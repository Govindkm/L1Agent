"""
Orchestrator agent - Main coordinator that routes requests to appropriate sub-agents.
"""

from typing import Literal
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.types import Command

from agents.base_agent import BaseAgent
from utils.state import MultiAgentState, register_agent, update_agent_status, log_execution_step
from config.model_config import get_model


class OrchestratorAgent(BaseAgent):
    """
    Main orchestrator agent that analyzes requests and delegates to appropriate sub-agents.
    """
    
    def __init__(self):
        super().__init__("Orchestrator")
    
    def process(self, state: MultiAgentState) -> Command[Literal["weather_agent", "email_agent", "__end__"]]:
        """
        Analyze user request and route to appropriate agent
        """
        # Register orchestrator in the dynamic state
        register_agent(state, "orchestrator", "working")
        log_execution_step(state, "orchestrator", "started_analysis")
        
        self.log_thinking("Analyzing user request to determine which sub-agents to involve")
        
        messages = state["messages"]
        latest_message = messages[-1] if messages else None
        
        if not latest_message:
            self.log_thinking("No messages found", "Ending conversation")
            update_agent_status(state, "orchestrator", "completed", action="no_messages_found")
            return Command(goto="__end__")
        
        user_input = latest_message.content.lower()
        
        # Analyze the user request to determine routing
        analysis_prompt = f"""
        Analyze this user request and determine what actions are needed:
        Request: "{latest_message.content}"
        
        Based on the request, determine if we need to:
        1. Get weather information (weather_agent)
        2. Generate or send email content (email_agent) 
        3. Both weather and email tasks
        4. Neither (just respond normally)
        
        Respond with a JSON object containing:
        {{
            "needs_weather": true/false,
            "needs_email": true/false,
            "reasoning": "explanation of your analysis",
            "next_agent": "weather_agent" or "email_agent" or "end"
        }}
        """
        
        try:
            model = get_model()
            analysis_response = model.invoke([
                SystemMessage(content=analysis_prompt),
                latest_message
            ])
            
            # Parse the response (in a real app, you'd use structured output)
            analysis_text = analysis_response.content
            self.log_thinking(f"Analysis result: {analysis_text}")
            
            # Simple routing logic based on keywords
            if any(word in user_input for word in ["weather", "temperature", "forecast", "climate"]):
                self.log_thinking(
                    "Detected weather-related request",
                    "Routing to weather_agent"
                )
                
                # Update state with routing decision
                update_agent_status(state, "orchestrator", "completed", 
                                        result="routed_to_weather_agent",
                                        action="routing_to_weather",
                                        metadata={"target_agent": "weather_agent", "reason": "weather_keywords_detected"})
                log_execution_step(state, "orchestrator", "routing_decision", {
                    "target": "weather_agent",
                    "keywords_detected": [word for word in ["weather", "temperature", "forecast", "climate"] if word in user_input]
                })
                
                return Command(
                    goto="weather_agent",
                    update={"current_task": "weather_lookup", "task_status": "in_progress"}
                )
                
            elif any(word in user_input for word in ["email", "send", "write", "compose", "message"]):
                self.log_thinking(
                    "Detected email-related request", 
                    "Routing to email_agent"
                )
                
                # Update state with routing decision
                update_agent_status(state, "orchestrator", "completed",
                                        result="routed_to_email_agent", 
                                        action="routing_to_email",
                                        metadata={"target_agent": "email_agent", "reason": "email_keywords_detected"})
                log_execution_step(state, "orchestrator", "routing_decision", {
                    "target": "email_agent", 
                    "keywords_detected": [word for word in ["email", "send", "write", "compose", "message"] if word in user_input]
                })
                
                return Command(
                    goto="email_agent",
                    update={"current_task": "email_task", "task_status": "in_progress"}
                )
            else:
                # Handle general queries
                self.log_thinking(
                    "General query detected - providing direct response",
                    "Preparing response message"
                )
                
                model = get_model()
                response = model.invoke([
                    SystemMessage(content="You are a helpful assistant. Respond to the user's query directly."),
                    latest_message
                ])
                
                # Update state for general response
                update_agent_status(state, "orchestrator", "completed",
                                        result=response.content,
                                        action="direct_response",
                                        metadata={"response_type": "general_query"})
                log_execution_step(state, "orchestrator", "direct_response", {
                    "bypassed_routing": True,
                    "reason": "no_specific_agent_needed"
                })
                
                return Command(
                    goto="__end__",
                    update={
                        "messages": [AIMessage(content=response.content, name="orchestrator")],
                        "task_status": "completed"
                    }
                )
        
        except Exception as e:
            self.log_thinking(f"Error in analysis: {str(e)}", "Ending with error")
            
            # Update state with error information
            update_agent_status(state, "orchestrator", "failed", error=str(e), action="error_occurred")
            log_execution_step(state, "orchestrator", "error", {"error": str(e)})
            
            error_response = AIMessage(
                content=f"I encountered an error while processing your request: {str(e)}", 
                name="orchestrator"
            )
            return Command(
                goto="__end__",
                update={"messages": [error_response], "task_status": "failed"}
            )
