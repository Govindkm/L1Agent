"""
Email tools for content creation and sending functionality.
Provides tools for generating email content and sending emails to single or multiple recipients.
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
import logging
from strands import tool
from config.settings import get_config
from observability import get_observer
import re


class EmailContentCreator:
    """Email content creation utilities"""
    
    def __init__(self):
        self.observer = get_observer()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def create_professional_email(self, purpose: str, recipient_context: str, tone: str = "professional") -> Dict[str, str]:
        """Create professional email content based on purpose and context"""
        
        templates = {
            "meeting_request": {
                "subject": "Meeting Request - {topic}",
                "greeting": "Dear {recipient},",
                "body": """
I hope this email finds you well.

I would like to schedule a meeting to discuss {topic}. This meeting would be beneficial for {reason}.

Proposed details:
- Duration: {duration}
- Preferred timing: {timing}
- Format: {format}

Please let me know your availability, and I'll send a calendar invitation accordingly.

Looking forward to hearing from you.
""",
                "closing": "Best regards,"
            },
            "follow_up": {
                "subject": "Follow-up: {topic}",
                "greeting": "Hi {recipient},",
                "body": """
I wanted to follow up on our previous conversation regarding {topic}.

{follow_up_content}

Please let me know if you need any additional information or if there's anything I can help with.
""",
                "closing": "Best regards,"
            },
            "project_update": {
                "subject": "Project Update - {project_name}",
                "greeting": "Hello {recipient},",
                "body": """
I'm writing to provide you with an update on the {project_name} project.

Current Status:
{status_update}

Next Steps:
{next_steps}

Please review and let me know if you have any questions or concerns.
""",
                "closing": "Regards,"
            },
            "general": {
                "subject": "Regarding {topic}",
                "greeting": "Hello {recipient},",
                "body": """
{content}

Please let me know if you need any additional information.
""",
                "closing": "Best regards,"
            }
        }
        
        return templates.get(purpose, templates["general"])
    
    def personalize_content(self, template: Dict[str, str], variables: Dict[str, str]) -> Dict[str, str]:
        """Personalize email template with provided variables"""
        
        personalized = {}
        for key, content in template.items():
            try:
                personalized[key] = content.format(**variables)
            except KeyError as e:
                self.logger.warning(f"Missing variable {e} for email personalization")
                personalized[key] = content
        
        return personalized


class EmailSender:
    """Email sending functionality with support for single and multiple recipients"""
    
    def __init__(self):
        self.config = get_config()
        self.observer = get_observer()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def send_email(self, 
                   to_emails: List[str], 
                   subject: str, 
                   body: str, 
                   cc_emails: Optional[List[str]] = None,
                   bcc_emails: Optional[List[str]] = None,
                   attachments: Optional[List[str]] = None,
                   is_html: bool = False) -> Dict[str, Any]:
        """Send email to single or multiple recipients"""
        
        try:
            with self.observer.trace_tool_execution("email_sender", 
                                                   to_count=len(to_emails),
                                                   cc_count=len(cc_emails or []),
                                                   bcc_count=len(bcc_emails or [])) as span:
                
                # Create message
                msg = MIMEMultipart()
                msg['From'] = self.config.email.username
                msg['To'] = ', '.join(to_emails)
                msg['Subject'] = subject
                
                if cc_emails:
                    msg['Cc'] = ', '.join(cc_emails)
                
                # Add body
                if is_html:
                    msg.attach(MIMEText(body, 'html'))
                else:
                    msg.attach(MIMEText(body, 'plain'))
                
                # Add attachments if provided
                if attachments:
                    for file_path in attachments:
                        try:
                            self._add_attachment(msg, file_path)
                        except Exception as e:
                            self.logger.warning(f"Failed to attach file {file_path}: {e}")
                
                # Combine all recipients
                all_recipients = to_emails.copy()
                if cc_emails:
                    all_recipients.extend(cc_emails)
                if bcc_emails:
                    all_recipients.extend(bcc_emails)
                
                # Send email with proper SSL handling
                context = ssl.create_default_context()
                
                # Use configuration to determine SSL verification behavior
                if not self.config.email.verify_ssl:
                    self.logger.warning("SSL verification disabled for email sending")
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                
                try:
                    with smtplib.SMTP(self.config.email.smtp_server, self.config.email.smtp_port) as server:
                        if self.config.email.use_tls:
                            server.starttls(context=context)
                        
                        server.login(self.config.email.username, self.config.email.password)
                        text = msg.as_string()
                        server.sendmail(self.config.email.username, all_recipients, text)
                        
                except ssl.SSLError as ssl_error:
                    self.logger.warning(f"SSL error occurred, trying with relaxed SSL verification: {ssl_error}")
                    # Fallback with relaxed SSL verification for development
                    context_relaxed = ssl.create_default_context()
                    context_relaxed.check_hostname = False
                    context_relaxed.verify_mode = ssl.CERT_NONE
                    
                    with smtplib.SMTP(self.config.email.smtp_server, self.config.email.smtp_port) as server:
                        if self.config.email.use_tls:
                            server.starttls(context=context_relaxed)
                        
                        server.login(self.config.email.username, self.config.email.password)
                        text = msg.as_string()
                        server.sendmail(self.config.email.username, all_recipients, text)
                
                # Log successful sending
                for recipient in all_recipients:
                    self.observer.log_email_event("sent", recipient, subject, "success", {
                        "body_length": len(body),
                        "is_html": is_html,
                        "has_attachments": bool(attachments)
                    })
                
                span.set_attribute("emails_sent", len(all_recipients))
                
                return {
                    "status": "success",
                    "message": f"Email sent successfully to {len(all_recipients)} recipients",
                    "recipients": all_recipients
                }
        
        except Exception as e:
            # Log failed sending
            for recipient in to_emails:
                self.observer.log_email_event("sent", recipient, subject, "error", {
                    "error": str(e)
                })
            
            self.logger.error(f"Failed to send email: {e}")
            return {
                "status": "error",
                "message": f"Failed to send email: {str(e)}",
                "error": str(e)
            }
    
    def _add_attachment(self, msg: MIMEMultipart, file_path: str):
        """Add attachment to email message"""
        with open(file_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {file_path.split("/")[-1]}'
        )
        msg.attach(part)
    
    def validate_email(self, email: str) -> bool:
        """Validate email address format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None


# Strands tools for email functionality
email_content_creator = EmailContentCreator()
email_sender = EmailSender()


@tool
def create_email_content(purpose: str, recipient_name: str, topic: str, 
                        additional_context: str = "", tone: str = "professional") -> str:
    """
    Create professional email content based on purpose, recipient, and topic.
    
    Args:
        purpose: Type of email (meeting_request, follow_up, project_update, general)
        recipient_name: Name of the email recipient
        topic: Main topic or subject of the email
        additional_context: Additional context or specific content for the email
        tone: Tone of the email (professional, friendly, formal)
    
    Returns:
        JSON string containing email subject and body
    """
    observer = get_observer()
    
    with observer.trace_tool_execution("create_email_content", 
                                     purpose=purpose,
                                     recipient_name=recipient_name,
                                     topic=topic) as span:
        
        observer.log_tool_usage("create_email_content", {
            "purpose": purpose,
            "recipient_name": recipient_name,
            "topic": topic,
            "additional_context": additional_context,
            "tone": tone
        })
        
        # Get appropriate template
        template = email_content_creator.create_professional_email(purpose, additional_context, tone)
        
        # Prepare variables for personalization
        variables = {
            "recipient": recipient_name,
            "topic": topic,
            "reason": additional_context,
            "duration": "30 minutes",
            "timing": "next week",
            "format": "in-person/virtual",
            "follow_up_content": additional_context,
            "project_name": topic,
            "status_update": additional_context,
            "next_steps": "Will be discussed in the meeting",
            "content": additional_context
        }
        
        # Personalize content
        personalized = email_content_creator.personalize_content(template, variables)
        
        # Construct full email
        full_email = f"{personalized['greeting']}\n\n{personalized['body']}\n\n{personalized['closing']}\n[Your Name]"
        
        result = {
            "subject": personalized['subject'],
            "body": full_email.strip(),
            "tone": tone,
            "purpose": purpose
        }
        
        observer.log_tool_usage("create_email_content", variables, result)
        span.set_attribute("email_created", True)
        
        import json
        return json.dumps(result, indent=2)


@tool
def send_email_tool(to_emails: str, subject: str, body: str, 
                   cc_emails: str = "", bcc_emails: str = "", 
                   is_html: bool = False) -> str:
    """
    Send email to single or multiple recipients with CC and BCC support.
    
    Args:
        to_emails: Comma-separated list of recipient email addresses
        subject: Email subject line
        body: Email body content
        cc_emails: Comma-separated list of CC email addresses (optional)
        bcc_emails: Comma-separated list of BCC email addresses (optional)
        is_html: Whether the email body is HTML formatted
    
    Returns:
        JSON string with send status and details
    """
    observer = get_observer()
    
    # Parse email lists
    to_list = [email.strip() for email in to_emails.split(',') if email.strip()]
    cc_list = [email.strip() for email in cc_emails.split(',') if cc_emails and email.strip()]
    bcc_list = [email.strip() for email in bcc_emails.split(',') if bcc_emails and email.strip()]
    
    # Validate email addresses
    invalid_emails = []
    for email_list in [to_list, cc_list, bcc_list]:
        for email in email_list:
            if not email_sender.validate_email(email):
                invalid_emails.append(email)
    
    if invalid_emails:
        error_result = {
            "status": "error",
            "message": f"Invalid email addresses: {', '.join(invalid_emails)}"
        }
        import json
        return json.dumps(error_result, indent=2)
    
    with observer.trace_tool_execution("send_email", 
                                     to_count=len(to_list),
                                     cc_count=len(cc_list),
                                     bcc_count=len(bcc_list)) as span:
        
        observer.log_tool_usage("send_email_tool", {
            "to_emails": to_list,
            "subject": subject[:50],
            "cc_emails": cc_list,
            "bcc_emails": bcc_list,
            "is_html": is_html
        })
        
        result = email_sender.send_email(
            to_emails=to_list,
            subject=subject,
            body=body,
            cc_emails=cc_list if cc_list else None,
            bcc_emails=bcc_list if bcc_list else None,
            is_html=is_html
        )
        
        observer.log_tool_usage("send_email_tool", {
            "to_emails": to_list,
            "subject": subject[:50]
        }, result)
        
        span.set_attribute("email_sent", result["status"] == "success")
        
        import json
        return json.dumps(result, indent=2)


@tool
def validate_email_addresses(emails: str) -> str:
    """
    Validate multiple email addresses.
    
    Args:
        emails: Comma-separated list of email addresses to validate
    
    Returns:
        JSON string with validation results
    """
    observer = get_observer()
    
    email_list = [email.strip() for email in emails.split(',') if email.strip()]
    
    with observer.trace_tool_execution("validate_emails", email_count=len(email_list)):
        
        valid_emails = []
        invalid_emails = []
        
        for email in email_list:
            if email_sender.validate_email(email):
                valid_emails.append(email)
            else:
                invalid_emails.append(email)
        
        result = {
            "valid_emails": valid_emails,
            "invalid_emails": invalid_emails,
            "total_count": len(email_list),
            "valid_count": len(valid_emails),
            "invalid_count": len(invalid_emails)
        }
        
        observer.log_tool_usage("validate_email_addresses", {
            "input_emails": email_list
        }, result)
        
        import json
        return json.dumps(result, indent=2)
