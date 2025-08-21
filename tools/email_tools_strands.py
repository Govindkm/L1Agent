"""
Email tools for the multi-agent system.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from strands.tools import tool
from langchain_core.messages import SystemMessage

from utils.observer import log_thinking
from config.settings import get_settings
from config.model_config import get_model


@tool
def generate_email_content(topic: str, recipient_name: str = "there", style: str = "professional") -> str:
    """
    Generate email content on a given topic.
    
    Args:
        topic: The main topic or subject for the email
        recipient_name: Name of the recipient (default: "there")
        style: Email style - professional, casual, or friendly (default: professional)
        
    Returns:
        Generated email content
    """
    log_thinking(
        "EmailAgent",
        f"User wants an email about '{topic}' for {recipient_name} in {style} style",
        "Generating email content using LLM"
    )
    
    style_prompts = {
        "professional": "Write a professional and formal email",
        "casual": "Write a casual and relaxed email", 
        "friendly": "Write a friendly and warm email"
    }
    
    prompt = f"""
{style_prompts.get(style, style_prompts['professional'])} about {topic}.
The recipient's name is {recipient_name}.
Include an appropriate subject line and a well-structured email body.
Keep it concise but informative.

Format the response as:
Subject: [subject line]

[email body]
    """
    
    try:
        model = get_model()
        response = model.invoke([SystemMessage(content=prompt)])
        email_content = response.content
        
        log_thinking(
            "EmailAgent",
            f"Successfully generated {style} email about {topic}",
            "Returning formatted email content"
        )
        return email_content
        
    except Exception as e:
        error_msg = f"Error generating email content: {str(e)}"
        log_thinking("EmailAgent", f"LLM error: {str(e)}", "Return error message")
        return error_msg


@tool 
def send_email(recipient: str, subject: str, body: str) -> str:
    """
    Send an email to a recipient.
    
    Args:
        recipient: Email address of the recipient
        subject: Email subject line
        body: Email body content
        
    Returns:
        Success or failure message
    """
    log_thinking(
        "EmailAgent",
        f"User wants to send email to {recipient} with subject '{subject}'",
        "Preparing to send email via SMTP"
    )
    
    settings = get_settings()
    
    if not settings.email_user or not settings.email_password:
        error_msg = "Email credentials not configured. Please set EMAIL_USER and EMAIL_PASSWORD in .env file"
        log_thinking("EmailAgent", "Email credentials missing", "Return configuration error")
        return error_msg
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = settings.email_user
        msg['To'] = recipient
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(body, 'plain'))
        
        # Gmail SMTP configuration
        server = smtplib.SMTP(settings.smtp_server, settings.smtp_port)
        server.starttls()  # Enable encryption
        server.login(settings.email_user, settings.email_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(settings.email_user, recipient, text)
        server.quit()
        
        success_msg = f"Email successfully sent to {recipient}!"
        log_thinking("EmailAgent", f"Email sent successfully to {recipient}", "SMTP transaction completed")
        return success_msg
        
    except Exception as e:
        error_msg = f"Failed to send email: {str(e)}"
        log_thinking("EmailAgent", f"SMTP error: {str(e)}", "Return error message")
        return error_msg
