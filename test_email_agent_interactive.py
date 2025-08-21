#!/usr/bin/env python3
"""
Interactive test script for the Email Agent functionality.
This script allows you to test email tools with user input.
"""

import os
import sys
from unittest.mock import patch, MagicMock
from getpass import getpass

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.email_agent import EmailAgent
from tools.email_tools import generate_email_content, send_email
from config.settings import get_settings
from utils.state import MultiAgentState


def print_banner():
    """Print a nice banner for the interactive test."""
    print("=" * 60)
    print("📧 EMAIL AGENT INTERACTIVE TEST SUITE")
    print("=" * 60)
    print("This script will help you test the email agent functionality")
    print("interactively with your own inputs.\n")


def check_configuration():
    """Check and display current configuration status."""
    print("🔧 CHECKING CONFIGURATION")
    print("-" * 30)
    
    settings = get_settings()
    validation = settings.validate()
    
    print(f"🤖 OpenAI API: {'✅ Available' if validation['openai_available'] else '❌ Not configured'}")
    print(f"🦙 Ollama: {'✅ Available' if validation['ollama_configured'] else '❌ Not configured'}")
    print(f"📧 Email SMTP: {'✅ Available' if validation['email_available'] else '❌ Not configured'}")
    print(f"🌐 SMTP Server: {settings.smtp_server}:{settings.smtp_port}")
    
    return validation


def get_user_choice(prompt, options):
    """Get user choice from a list of options."""
    print(f"\n{prompt}")
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    
    while True:
        try:
            choice = int(input(f"Choose (1-{len(options)}): ")) - 1
            if 0 <= choice < len(options):
                return choice
            else:
                print(f"Please enter a number between 1 and {len(options)}")
        except ValueError:
            print("Please enter a valid number")


def test_email_content_generation_interactive():
    """Test email content generation with user input."""
    print("\n📝 EMAIL CONTENT GENERATION TEST")
    print("-" * 40)
    
    # Get user inputs
    topic = input("📌 Enter email topic/subject: ").strip()
    if not topic:
        topic = "project status update"
        print(f"Using default topic: {topic}")
    
    recipient_name = input("👤 Enter recipient name (or press Enter for 'there'): ").strip()
    if not recipient_name:
        recipient_name = "there"
    
    style_options = ["professional", "casual", "friendly"]
    style_choice = get_user_choice("🎨 Choose email style:", style_options)
    style = style_options[style_choice]
    
    print(f"\n🚀 Generating {style} email about '{topic}' for {recipient_name}...")
    
    try:
        # Test the email generation tool directly
        result = generate_email_content.func(
            topic=topic,
            recipient_name=recipient_name,
            style=style
        )
        
        print(f"\n✅ EMAIL GENERATED SUCCESSFULLY!")
        print("=" * 50)
        print(result)
        print("=" * 50)
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error generating email: {e}")
        
        # Offer manual content creation for testing send functionality
        print("\n💡 Would you like to create manual email content for testing send functionality?")
        create_manual = input("Enter 'y' to create manual content or any other key to skip: ").lower()
        
        if create_manual == 'y':
            subject = input("📧 Enter email subject: ").strip()
            if not subject:
                subject = f"Test Email: {topic}"
            
            body = input("📝 Enter email body (or press Enter for default): ").strip()
            if not body:
                body = f"Dear {recipient_name},\n\nThis is a test email regarding {topic}.\n\nBest regards,\nTest User"
            
            manual_content = f"Subject: {subject}\n\n{body}"
            print(f"\n✅ MANUAL EMAIL CREATED:")
            print("=" * 50)
            print(manual_content)
            print("=" * 50)
            return manual_content
        
        return None


def test_email_sending_interactive(email_content=None):
    """Test email sending with user input."""
    print("\n📤 EMAIL SENDING TEST")
    print("-" * 25)
    
    # Parse content if provided
    subject = "Test Email"
    body = "This is a test email body."
    
    if email_content:
        lines = email_content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('Subject:'):
                subject = line.replace('Subject:', '').strip()
                body = '\n'.join(lines[i+1:]).strip()
                break
    
    print(f"📧 Current subject: {subject}")
    print(f"📝 Current body preview: {body[:100]}{'...' if len(body) > 100 else ''}")
    
    # Get sending options
    send_options = ["Test with mock SMTP (safe - no actual email sent)", 
                   "Send actual email (requires email credentials)",
                   "Skip email sending test"]
    
    send_choice = get_user_choice("🚀 Choose sending option:", send_options)
    
    if send_choice == 2:  # Skip
        print("⏭️  Skipping email sending test")
        return
    
    # Get recipient email
    recipient = input("📬 Enter recipient email address: ").strip()
    if not recipient:
        recipient = "test@example.com"
        print(f"Using default recipient: {recipient}")
    
    if send_choice == 0:  # Mock SMTP
        print(f"\n🧪 Testing email send with MOCK SMTP...")
        test_mock_email_send(recipient, subject, body)
    
    elif send_choice == 1:  # Actual email
        print(f"\n📧 Testing ACTUAL email send...")
        test_actual_email_send(recipient, subject, body)


def test_mock_email_send(recipient, subject, body):
    """Test email sending with mocked SMTP."""
    print("🔧 Setting up mock SMTP server...")
    
    with patch('smtplib.SMTP') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Mock credentials for testing
        with patch.object(get_settings(), 'email_user', 'test@example.com'):
            with patch.object(get_settings(), 'email_password', 'test_password'):
                try:
                    result = send_email.func(
                        recipient=recipient,
                        subject=subject,
                        body=body
                    )
                    
                    print(f"✅ Mock send result: {result}")
                    print("🔍 SMTP method calls:")
                    print(f"  - starttls() called: {mock_server.starttls.called}")
                    print(f"  - login() called: {mock_server.login.called}")
                    print(f"  - sendmail() called: {mock_server.sendmail.called}")
                    print(f"  - quit() called: {mock_server.quit.called}")
                    
                except Exception as e:
                    print(f"❌ Mock send failed: {e}")


def test_actual_email_send(recipient, subject, body):
    """Test actual email sending with user-provided credentials."""
    print("⚠️  ACTUAL EMAIL SENDING - This will send a real email!")
    confirm = input("Are you sure you want to proceed? (yes/no): ").lower()
    
    if confirm != 'yes':
        print("📛 Actual email sending cancelled")
        return
    
    # Get email credentials
    print("\n🔐 Enter your email credentials:")
    email_user = input("📧 Your email address: ").strip()
    if not email_user:
        print("❌ Email address is required")
        return
    
    email_password = getpass("🔑 Your email password (app password recommended): ")
    if not email_password:
        print("❌ Email password is required")
        return
    
    # Temporarily set credentials
    settings = get_settings()
    original_user = settings.email_user
    original_password = settings.email_password
    
    try:
        settings.email_user = email_user
        settings.email_password = email_password
        
        print(f"\n📤 Sending email to {recipient}...")
        result = send_email.func(
            recipient=recipient,
            subject=subject,
            body=body
        )
        
        print(f"📧 Send result: {result}")
        
    except Exception as e:
        print(f"❌ Actual send failed: {e}")
    
    finally:
        # Restore original settings
        settings.email_user = original_user
        settings.email_password = original_password


def test_email_agent_integration():
    """Test the full Email Agent integration."""
    print("\n🤖 EMAIL AGENT INTEGRATION TEST")
    print("-" * 35)
    
    try:
        # Initialize the email agent
        state = MultiAgentState()
        email_agent = EmailAgent()
        
        print("✅ Email Agent initialized successfully")
        print(f"🔧 Agent Name: {email_agent.name}")
        # print(f"🎯 Agent Role: {email_agent.role}")
        print(f"🛠️  Available Tools: {len(email_agent.tools)} tools")
        
        for tool in email_agent.tools:
            print(f"   - {tool.name}: {tool.description[:60]}...")
        
        # Test agent thinking process
        print(f"\n🧠 Testing agent reasoning...")
        user_request = input("💭 Enter a request for the email agent (or press Enter for default): ").strip()
        if not user_request:
            user_request = "Generate a professional email about project deadline extension"
        
        print(f"🎯 Processing request: '{user_request}'")
        
        # You could add more agent-specific testing here
        print("✅ Agent integration test completed")
        
    except Exception as e:
        print(f"❌ Agent integration test failed: {e}")


def main():
    """Main interactive test function."""
    print_banner()
    
    # Check configuration
    validation = check_configuration()
    
    # Main test menu
    while True:
        print("\n🎯 TEST MENU")
        print("-" * 15)
        test_options = [
            "Test Email Content Generation",
            "Test Email Sending (Mock)",
            "Test Email Sending (Actual)",
            "Test Email Agent Integration",
            "Run All Tests",
            "Exit"
        ]
        
        choice = get_user_choice("Choose a test to run:", test_options)
        
        if choice == 0:  # Email content generation
            email_content = test_email_content_generation_interactive()
            if email_content:
                use_for_send = input("\n🔄 Use this content to test email sending? (y/n): ").lower()
                if use_for_send == 'y':
                    test_email_sending_interactive(email_content)
        
        elif choice == 1:  # Mock email sending
            test_email_sending_interactive()
        
        elif choice == 2:  # Actual email sending
            print("⚠️  This will send actual emails!")
            test_email_sending_interactive()
        
        elif choice == 3:  # Agent integration
            test_email_agent_integration()
        
        elif choice == 4:  # Run all tests
            print("\n🚀 RUNNING ALL TESTS")
            print("=" * 25)
            email_content = test_email_content_generation_interactive()
            if email_content:
                test_email_sending_interactive(email_content)
            test_email_agent_integration()
        
        elif choice == 5:  # Exit
            print("\n👋 Thanks for testing the Email Agent!")
            print("=" * 40)
            break
        
        # Ask if user wants to continue
        print("\n" + "="*40)
        continue_testing = input("🔄 Continue testing? (y/n): ").lower()
        if continue_testing != 'y':
            print("\n👋 Thanks for testing the Email Agent!")
            break


if __name__ == "__main__":
    main()
