"""
Weather agent - Specialized agent for handling weather-related queries.
"""

from typing import Literal
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.types import Command

from agents.base_agent import BaseAgent
from utils.state import MultiAgentState, register_agent, update_agent_status, log_execution_step, register_tool, update_tool_data
from config.model_config import get_model
from tools.weather_tools import get_weather_data


class WeatherAgent(BaseAgent):
    """
    Weather agent that handles weather-related queries using tools.
    """
    
    def __init__(self):
        super().__init__("WeatherAgent")
    
    def process(self, state: MultiAgentState) -> Command[Literal["__end__"]]:
        """
        Process weather-related requests
        """
        # Register this agent in the dynamic state
        register_agent(state, "weather_agent", "working")
        log_execution_step(state, "weather_agent", "started_processing")
        
        self.log_thinking(
            "Received weather task from orchestrator",
            "Analyzing request to extract city name"
        )
        
        messages = state["messages"]
        latest_message = messages[-1] if messages else None
        
        if not latest_message:
            update_agent_status(state, "weather_agent", "failed", error="No message to process")
            return Command(goto="__end__")
        
        # Extract city from the user's message
        city_extraction_prompt = f"""
        Extract the city name from this request: "{latest_message.content}"
        If no city is mentioned, ask the user to specify a city.
        
        Respond with just the city name, or if no city is found, respond with "NO_CITY_FOUND".
        """
        
        try:
            model = get_model()
            city_response = model.invoke([SystemMessage(content=city_extraction_prompt)])
            city = city_response.content.strip()
            
            if city == "NO_CITY_FOUND" or not city:
                self.log_thinking(
                    "No city found in request",
                    "Asking user to specify city"
                )
                response_text = "I'd be happy to help you with weather information! Could you please specify which city you'd like to know about?"
                response = AIMessage(
                    content=response_text,
                    name="weather_agent"
                )
                
                # Update dynamic state
                update_agent_status(state, "weather_agent", "completed", result=response_text, 
                                        action="requested_city_clarification")
                log_execution_step(state, "weather_agent", "requested_clarification", {"reason": "no_city_found"})
                
            else:
                self.log_thinking(
                    f"Extracted city: {city}",
                    "Calling weather API tool"
                )
                
                # Register and use the weather tool in dynamic state
                register_tool(state, "weather")
                weather_info = get_weather_data(city)
                
                # Update tool data
                update_tool_data(state, "weather", result=weather_info, 
                                     metadata={"city": city, "query_type": "current_weather"},
                                     status="success")
                
                response_text = f"Here's the current weather information:\n\n{weather_info}"
                response = AIMessage(
                    content=response_text,
                    name="weather_agent"
                )
                
                # Update agent status
                update_agent_status(state, "weather_agent", "completed", result=weather_info,
                                        action=f"retrieved_weather_for_{city}")
                log_execution_step(state, "weather_agent", "retrieved_weather", {
                    "city": city, 
                    "tool": "weather",
                    "success": True
                })
            
            return Command(
                goto="__end__",
                update={
                    "messages": [response],
                    "task_status": "completed"
                }
            )
            
        except Exception as e:
            self.log_thinking(f"Error processing request: {str(e)}", "Returning error message")
            
            # Update state with error information
            update_agent_status(state, "weather_agent", "failed", error=str(e),
                                    action="error_occurred")
            # Check if tool was registered before updating its status
            try:
                update_tool_data(state, "weather", status="failed", error=str(e))
            except:
                pass  # Tool might not have been registered yet
            
            log_execution_step(state, "weather_agent", "error", {"error": str(e)})
            
            error_response = AIMessage(
                content=f"I encountered an error while getting weather information: {str(e)}",
                name="weather_agent"
            )
            return Command(
                goto="__end__",
                update={"messages": [error_response], "task_status": "failed"}
            )
