"""
Email agent - Specialized agent for handling email generation and sending.
"""

from typing import Literal
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.types import Command

from agents.base_agent import BaseAgent
from utils.state import MultiAgentState, register_agent, update_agent_status, log_execution_step, register_tool, update_tool_data
from config.model_config import get_model
from tools.email_tools import generate_email_content, send_email


class EmailAgent(BaseAgent):
    """
    Email agent that handles email generation and sending.
    """
    
    def __init__(self):
        super().__init__("EmailAgent")
    
    def process(self, state: MultiAgentState) -> Command[Literal["__end__"]]:
        """
        Process email-related requests
        """
        # Register this agent in the dynamic state
        register_agent(state, "email_agent", "working")
        log_execution_step(state, "email_agent", "started_processing")
        
        self.log_thinking(
            "Received email task from orchestrator",
            "Analyzing request to determine email action"
        )
        
        messages = state["messages"]
        latest_message = messages[-1] if messages else None
        
        if not latest_message:
            update_agent_status(state, "email_agent", "failed", error="No message to process")
            return Command(goto="__end__")
        
        user_input = latest_message.content.lower()
        
        try:
            # Register email tool
            register_tool(state, "email")
            
            if "send" in user_input:
                self.log_thinking(
                    "User wants to send an email",
                    "Parsing recipient and content details"
                )
                
                response_text = "I can help you send an email! However, for security reasons, email sending requires proper configuration. Please provide:\n1. Recipient email address\n2. Subject\n3. Message content\n\nFor now, I'll generate email content for you."
                response = AIMessage(
                    content=response_text,
                    name="email_agent"
                )
                
                # Update state for sending intent
                update_agent_status(state, "email_agent", "completed", result=response_text,
                                        action="requested_email_details")
                update_tool_data(state, "email", metadata={"action": "send_requested", "status": "pending_details"})
                log_execution_step(state, "email_agent", "send_requested", {"requires_configuration": True})
                
            else:
                self.log_thinking(
                    "User wants email content generation",
                    "Extracting topic and style preferences"
                )
                # Handle email content generation
                topic_extraction_prompt = f"""
                Extract the email topic/subject from this request: "{latest_message.content}"
                
                Respond with just the main topic or subject matter.
                """
                
                model = get_model()
                topic_response = model.invoke([SystemMessage(content=topic_extraction_prompt)])
                topic = topic_response.content.strip()
                
                self.log_thinking(f"Extracted topic: {topic}", "Generating email content")
                
                # Generate email content using the tool
                email_content = generate_email_content(topic)
                
                # Update tool data with generated content
                update_tool_data(state, "email", result=email_content,
                                     metadata={
                                         "topic": topic,
                                         "action": "content_generated",
                                         "recipient": "not_specified"
                                     },
                                     status="success")
                
                response_text = f"I've generated email content for you:\n\n{email_content}\n\nWould you like me to modify anything or help you send this email?"
                response = AIMessage(
                    content=response_text,
                    name="email_agent"
                )
                
                # Update agent status
                update_agent_status(state, "email_agent", "completed", result=email_content,
                                        action=f"generated_content_for_{topic}")
                log_execution_step(state, "email_agent", "content_generated", {
                    "topic": topic,
                    "tool": "email",
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
            self.log_thinking(f"Error processing email request: {str(e)}", "Returning error message")
            
            # Update state with error information
            update_agent_status(state, "email_agent", "failed", error=str(e),
                                    action="error_occurred")
            try:
                update_tool_data(state, "email", status="failed", error=str(e))
            except:
                pass  # Tool might not have been registered yet
            
            log_execution_step(state, "email_agent", "error", {"error": str(e)})
            
            error_response = AIMessage(
                content=f"I encountered an error while handling your email request: {str(e)}",
                name="email_agent"
            )
            return Command(
                goto="__end__",
                update={"messages": [error_response], "task_status": "failed"}
            )
