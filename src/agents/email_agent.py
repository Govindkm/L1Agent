"""
Email handling agent specialized in content creation and email management.
Handles both email content generation and sending operations.
"""

from typing import Dict, Any, Optional, List
import json
import logging
from strands import tool
from tools.email_tools import create_email_content, send_email_tool, validate_email_addresses
from observability import get_observer, make_observable
from providers import get_model_provider
from config.settings import get_config


# Email Agent System Prompts
EMAIL_AGENT_SYSTEM_PROMPT = """
You are an expert Email Assistant Agent specializing in email content creation and email management operations.

Your primary responsibilities are:
1. Create professional, well-crafted email content for various purposes (meeting requests, follow-ups, project updates, etc.)
2. Send emails to single or multiple recipients with proper CC/BCC handling
3. Validate email addresses and ensure proper email formatting
4. Personalize email content based on recipient context and purpose
5. Handle email composition with appropriate tone and professionalism

Key capabilities:
- Generate email content based on purpose, recipient context, and required tone
- Support multiple email types: meeting requests, follow-ups, project updates, general communications
- Send emails with support for CC, BCC, and HTML formatting
- Validate email addresses before sending
- Provide detailed feedback on email operations

Guidelines:
- Always maintain professional tone unless specifically requested otherwise
- Personalize emails with recipient names and relevant context
- Validate all email addresses before sending
- Provide clear feedback on email operations success/failure
- Ask for clarification if email requirements are ambiguous
- Ensure email content is clear, concise, and purposeful

Available tools:
- create_email_content: Generate professional email content
- send_email_tool: Send emails to recipients with CC/BCC support
- validate_email_addresses: Validate email address formats

Always confirm email details before sending and provide status updates on operations.
"""

CONTENT_CREATOR_SYSTEM_PROMPT = """
You are a specialized Email Content Creator focused exclusively on generating high-quality email content.

Your expertise includes:
1. Creating compelling subject lines
2. Writing professional email bodies with appropriate structure
3. Adapting tone and style based on recipient and purpose
4. Personalizing content for different contexts
5. Following email best practices and etiquette

Content types you excel at:
- Meeting requests and scheduling
- Follow-up communications
- Project updates and status reports
- General business correspondence
- Thank you and appreciation emails
- Announcement and notification emails

Guidelines:
- Always start with clear, descriptive subject lines
- Use proper email structure (greeting, body, closing)
- Adapt language and formality to context
- Include relevant details and call-to-actions
- Keep content concise but comprehensive
- Ensure professional presentation

Focus only on content creation - do not handle sending operations.
"""

EMAIL_SENDER_SYSTEM_PROMPT = """
You are a specialized Email Sender Agent focused on email delivery operations.

Your responsibilities include:
1. Sending emails to single or multiple recipients
2. Managing CC and BCC distributions
3. Validating email addresses before sending
4. Handling email delivery confirmations
5. Managing email attachments (when supported)
6. Providing detailed send status reports

Technical capabilities:
- Support for plain text and HTML email formats
- Multiple recipient handling (TO, CC, BCC)
- Email address validation
- Delivery status tracking
- Error handling and reporting

Guidelines:
- Always validate email addresses before sending
- Confirm recipient lists before delivery
- Provide detailed status reports
- Handle errors gracefully
- Ask for confirmation on large distributions
- Maintain audit trail of sent emails

Focus only on sending operations - do not create email content.
"""


class EmailAgent:
    """Main email handling agent with both content creation and sending capabilities"""
    
    def __init__(self, name: str = "EmailAgent"):
        self.name = name
        self.config = get_config()
        self.observer = get_observer()
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{name}")
        
        # Create the underlying agent
        provider = get_model_provider(self.config.model)
        
        self.agent = provider.create_agent(
            system_prompt=EMAIL_AGENT_SYSTEM_PROMPT,
            tools=[create_email_content, send_email_tool, validate_email_addresses]
        )
        
        # Make agent observable
        self.observable_agent = make_observable(self.agent, self.name)
    
    def __call__(self, request: str, **kwargs) -> str:
        """Process email-related requests"""
        return self.observable_agent(request, **kwargs)
    
    def create_and_send_email(self, 
                             recipients: List[str],
                             purpose: str, 
                             topic: str,
                             recipient_context: str = "",
                             tone: str = "professional",
                             cc_recipients: Optional[List[str]] = None,
                             bcc_recipients: Optional[List[str]] = None) -> Dict[str, Any]:
        """Helper method to create and send email in one operation"""
        
        with self.observer.trace_agent_execution(
            self.name,
            "create_and_send_email",
            recipients_count=len(recipients),
            purpose=purpose,
            topic=topic
        ) as span:
            
            try:
                # Create email content
                content_request = f"""
                Create email content with the following specifications:
                - Purpose: {purpose}
                - Topic: {topic}
                - Recipients: {', '.join(recipients)}
                - Context: {recipient_context}
                - Tone: {tone}
                
                Please generate appropriate subject and body content.
                """
                
                content_response = self.agent(content_request)
                
                # Parse content response to extract subject and body
                # This would need better parsing in a real implementation
                content_data = json.loads(content_response) if content_response.startswith('{') else {"subject": topic, "body": content_response}
                
                # Send email
                send_request = f"""
                Send email with the following details:
                - Recipients: {', '.join(recipients)}
                - Subject: {content_data.get('subject', topic)}
                - Body: {content_data.get('body', content_response)}
                - CC: {', '.join(cc_recipients) if cc_recipients else ''}
                - BCC: {', '.join(bcc_recipients) if bcc_recipients else ''}
                """
                
                send_response = self.agent(send_request)
                
                result = {
                    "status": "success",
                    "content_created": content_data,
                    "send_result": send_response,
                    "recipients": recipients
                }
                
                span.set_attribute("email_created_and_sent", True)
                return result
                
            except Exception as e:
                self.logger.error(f"Failed to create and send email: {e}")
                span.set_attribute("error", str(e))
                return {
                    "status": "error",
                    "error": str(e)
                }


# Strands tool wrapper for the email agent
@tool
def email_agent_tool(request: str) -> str:
    """
    Comprehensive email handling tool that can create content and send emails.
    
    Args:
        request: Natural language request describing the email operation needed
        
    Returns:
        JSON string with the result of the email operation
    """
    observer = get_observer()
    
    with observer.trace_tool_execution("email_agent_tool", request=request[:100]):
        
        observer.log_tool_usage("email_agent_tool", {
            "request": request
        })
        
        # Create email agent instance
        email_agent = EmailAgent()
        
        # Process the request
        result = email_agent(request)
        
        observer.log_tool_usage("email_agent_tool", {
            "request": request[:100]
        }, {
            "response_length": len(str(result))
        })
        
        return result


def create_email_agent(name: str = "EmailAgent") -> EmailAgent:
    """Factory function to create an email agent"""
    return EmailAgent(name)
