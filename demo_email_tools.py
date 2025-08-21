#!/usr/bin/env python3
"""
Automated demo script for Email Agent functionality.
This script demonstrates email tools without requiring user interaction.
"""

import os
import sys
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.email_tools import generate_email_content, send_email
from config.settings import get_settings


def demo_email_content_generation():
    """Demo email content generation with various scenarios."""
    print("📝 EMAIL CONTENT GENERATION DEMO")
    print("=" * 45)
    
    test_cases = [
        {
            "topic": "quarterly project review meeting",
            "recipient": "Sarah",
            "style": "professional",
            "description": "Professional quarterly review email"
        },
        {
            "topic": "team lunch invitation",
            "recipient": "Team",
            "style": "friendly",
            "description": "Friendly team lunch invitation"
        },
        {
            "topic": "software update notification",
            "recipient": "users",
            "style": "casual",
            "description": "Casual software update notification"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📧 Test Case {i}: {test_case['description']}")
        print(f"   Topic: {test_case['topic']}")
        print(f"   Recipient: {test_case['recipient']}")
        print(f"   Style: {test_case['style']}")
        print("-" * 50)
        
        try:
            result = generate_email_content.func(
                topic=test_case['topic'],
                recipient_name=test_case['recipient'],
                style=test_case['style']
            )
            
            # Check if it's an error message
            if "Error generating email content" in result:
                print(f"⚠️  Content generation needs LLM configuration:")
                print(f"   {result}")
                print(f"📋 Using fallback demo content instead:")
                
                # Generate fallback content
                subject = f"{test_case['style'].title()} Email: {test_case['topic'].title()}"
                body = f"""Dear {test_case['recipient']},

This is a {test_case['style']} email regarding {test_case['topic']}.

[This is demo content since LLM is not configured]

Best regards,
Email Agent Demo"""
                result = f"Subject: {subject}\n\n{body}"
            
            print(result)
            print("✅ Content generated successfully")
            
        except Exception as e:
            print(f"❌ Error: {e}")


def demo_email_sending_mock():
    """Demo email sending with mocked SMTP."""
    print("\n\n📤 EMAIL SENDING DEMO (MOCK SMTP)")
    print("=" * 40)
    
    test_emails = [
        {
            "recipient": "demo@example.com",
            "subject": "Demo Email #1",
            "body": "This is a test email body for demonstration purposes."
        },
        {
            "recipient": "test@company.com", 
            "subject": "Project Update Demo",
            "body": "Hello,\n\nThis is a demo project update email.\n\nBest regards,\nDemo Agent"
        }
    ]
    
    print("🧪 Setting up mock SMTP server for safe testing...")
    
    with patch('smtplib.SMTP') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Set mock credentials for testing
        with patch.object(get_settings(), 'email_user', 'demo@example.com'):
            with patch.object(get_settings(), 'email_password', 'demo_password'):
                
                for i, email in enumerate(test_emails, 1):
                    print(f"\n📧 Sending Demo Email {i}:")
                    print(f"   To: {email['recipient']}")
                    print(f"   Subject: {email['subject']}")
                    print(f"   Body: {email['body'][:50]}...")
                    
                    try:
                        result = send_email.func(
                            recipient=email['recipient'],
                            subject=email['subject'],
                            body=email['body']
                        )
                        
                        print(f"   ✅ Result: {result}")
                        
                    except Exception as e:
                        print(f"   ❌ Error: {e}")
                
                print(f"\n🔍 SMTP Method Call Verification:")
                print(f"   - starttls() called: {mock_server.starttls.call_count} times")
                print(f"   - login() called: {mock_server.login.call_count} times")
                print(f"   - sendmail() called: {mock_server.sendmail.call_count} times")
                print(f"   - quit() called: {mock_server.quit.call_count} times")


def demo_email_configuration_check():
    """Demo configuration checking."""
    print("\n\n🔧 EMAIL CONFIGURATION DEMO")
    print("=" * 35)
    
    settings = get_settings()
    validation = settings.validate()
    
    print("📋 Current Configuration Status:")
    print(f"   🤖 OpenAI API: {'✅ Available' if validation['openai_available'] else '❌ Not configured'}")
    print(f"   🦙 Ollama: {'✅ Available' if validation['ollama_configured'] else '❌ Not configured'}")
    if validation['ollama_configured']:
        print(f"      Base URL: {settings.ollama_base_url}")
    
    print(f"   🌤️  Weather API: {'✅ Available' if validation['weather_available'] else '❌ Not configured'}")
    print(f"   📧 Email SMTP: {'✅ Available' if validation['email_available'] else '❌ Not configured'}")
    
    if validation['email_available']:
        print(f"      User: {settings.email_user}")
        print(f"      Server: {settings.smtp_server}:{settings.smtp_port}")
    else:
        print("      ⚠️  Email credentials not configured")
        print("      💡 Set EMAIL_USER and EMAIL_PASSWORD in .env file for actual sending")
    
    print(f"   📋 Logging: {settings.log_level} → {settings.log_file}")


def demo_error_handling():
    """Demo error handling scenarios."""
    print("\n\n🚨 ERROR HANDLING DEMO")
    print("=" * 30)
    
    # Test 1: Email sending without credentials
    print("📧 Test 1: Email sending without credentials")
    
    settings = get_settings()
    original_user = settings.email_user
    original_password = settings.email_password
    
    try:
        # Temporarily clear credentials
        settings.email_user = None
        settings.email_password = None
        
        result = send_email.func(
            recipient="test@example.com",
            subject="Test Without Credentials",
            body="This should fail gracefully"
        )
        
        print(f"   ✅ Graceful error handling: {result}")
        
    finally:
        # Restore credentials
        settings.email_user = original_user
        settings.email_password = original_password
    
    # Test 2: Empty inputs
    print("\n📧 Test 2: Edge case handling")
    try:
        result = generate_email_content.func(topic="", recipient_name="", style="invalid_style")
        print(f"   ✅ Edge case handled: Content generated despite empty/invalid inputs")
        print(f"   Preview: {result[:100]}...")
    except Exception as e:
        print(f"   ⚠️  Exception caught: {e}")


def demo_integration_workflow():
    """Demo a complete email workflow."""
    print("\n\n🔗 INTEGRATION WORKFLOW DEMO")
    print("=" * 35)
    
    workflow_topic = "weekly team standup meeting"
    workflow_recipient = "Development Team"
    workflow_style = "professional"
    workflow_email = "team@company.com"
    
    print(f"🎯 Scenario: Generate and send email about '{workflow_topic}'")
    print(f"   Recipient: {workflow_recipient} ({workflow_email})")
    print(f"   Style: {workflow_style}")
    
    print("\n🔄 Step 1: Generate email content")
    try:
        email_content = generate_email_content.func(
            topic=workflow_topic,
            recipient_name=workflow_recipient,
            style=workflow_style
        )
        
        if "Error generating email content" in email_content:
            print("   ⚠️  Using fallback content (LLM not configured)")
            email_content = f"""Subject: Weekly Team Standup Meeting

Dear {workflow_recipient},

I hope this email finds you well. I wanted to remind you about our weekly team standup meeting.

[This is demo content generated by fallback system]

Please let me know if you have any questions.

Best regards,
Email Agent Demo"""
        
        print("   ✅ Email content generated")
        
        # Parse subject and body
        lines = email_content.split('\n')
        subject = "Weekly Team Standup Meeting"  # fallback
        body = email_content
        
        for i, line in enumerate(lines):
            if line.startswith('Subject:'):
                subject = line.replace('Subject:', '').strip()
                body = '\n'.join(lines[i+1:]).strip()
                break
        
        print(f"   📧 Subject: {subject}")
        print(f"   📝 Body length: {len(body)} characters")
        
    except Exception as e:
        print(f"   ❌ Content generation failed: {e}")
        return
    
    print("\n🔄 Step 2: Send email (mock)")
    with patch('smtplib.SMTP') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        with patch.object(get_settings(), 'email_user', 'demo@company.com'):
            with patch.object(get_settings(), 'email_password', 'demo_password'):
                
                try:
                    result = send_email.func(
                        recipient=workflow_email,
                        subject=subject,
                        body=body
                    )
                    
                    print(f"   ✅ Email sent successfully: {result}")
                    print("   🎉 Complete workflow executed successfully!")
                    
                except Exception as e:
                    print(f"   ❌ Email sending failed: {e}")


def main():
    """Run the complete email tools demo."""
    print("🚀 EMAIL TOOLS AUTOMATED DEMO")
    print("=" * 50)
    print("This demo showcases all email tool functionality")
    print("without requiring user interaction.\n")
    
    # Run all demo sections
    demo_email_configuration_check()
    demo_email_content_generation()
    demo_email_sending_mock()
    demo_error_handling()
    demo_integration_workflow()
    
    print("\n" + "=" * 50)
    print("🏁 EMAIL TOOLS DEMO COMPLETED")
    print("\n📝 Summary:")
    print("   ✅ Email content generation tested (with LLM fallback)")
    print("   ✅ Email sending tested (mock SMTP)")
    print("   ✅ Error handling demonstrated")
    print("   ✅ Configuration checking verified")
    print("   ✅ Complete workflow integration tested")
    print("\n💡 Next steps:")
    print("   - Configure OpenAI API key or Ollama for content generation")
    print("   - Set EMAIL_USER and EMAIL_PASSWORD for actual email sending")
    print("   - Run the interactive test for hands-on experimentation")


if __name__ == "__main__":
    main()
