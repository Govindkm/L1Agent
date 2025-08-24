"""
Example: Basic email operations using the multi-agent system
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src import create_email_agent, get_observer


def basic_email_examples():
    """Demonstrate basic email functionality"""
    
    # Initialize observer for tracking
    observer = get_observer()
    
    # Create email agent
    email_agent = create_email_agent("ExampleEmailAgent")
    
    print("=== Multi-Agent Email System - Basic Examples ===\n")
    
    # Example 1: Create email content
    print("1. Creating email content for a meeting request...")
    
    content_request = """
    Create a professional meeting request email with these details:
    - Recipient: John Smith
    - Topic: Q1 Project Review Meeting
    - Purpose: meeting_request
    - Context: Need to review project milestones and discuss next quarter planning
    - Tone: professional
    """
    
    try:
        content_response = email_agent(content_request)
        print("✓ Email content created successfully!")
        print(f"Response: {content_response[:200]}...\n")
    except Exception as e:
        print(f"✗ Failed to create email content: {e}\n")
    
    # Example 2: Validate email addresses
    print("2. Validating email addresses...")
    
    validation_request = """
    Validate these email addresses:
    test@example.com, invalid-email, user@company.com, another.invalid@, valid@test.org
    """
    
    try:
        validation_response = email_agent(validation_request)
        print("✓ Email validation completed!")
        print(f"Response: {validation_response[:200]}...\n")
    except Exception as e:
        print(f"✗ Failed to validate emails: {e}\n")
    
    # Example 3: Create follow-up email
    print("3. Creating a follow-up email...")
    
    followup_request = """
    Create a follow-up email with these specifications:
    - Recipient: Sarah Johnson
    - Topic: Client Meeting Follow-up
    - Purpose: follow_up
    - Context: Following up on yesterday's client presentation, need to send the proposal document and schedule next meeting
    - Tone: professional but friendly
    """
    
    try:
        followup_response = email_agent(followup_request)
        print("✓ Follow-up email created successfully!")
        print(f"Response: {followup_response[:200]}...\n")
    except Exception as e:
        print(f"✗ Failed to create follow-up email: {e}\n")
    
    print("=== Examples completed ===")


def test_email_sending():
    """Test email sending (configure email settings in .env first)"""
    
    email_agent = create_email_agent("TestEmailAgent")
    
    print("=== Testing Email Sending ===\n")
    print("Note: Make sure your email configuration is set in .env file")
    
    # Test email send (you may want to change the recipient)
    send_request = """
    Send a test email with these details:
    - Recipients: your-email@example.com
    - Subject: Multi-Agent System Test Email
    - Body: This is a test email from the Multi-Agent Email System. The system is working correctly!
    - Format: plain text
    """
    
    try:
        send_response = email_agent(send_request)
        print("✓ Email sent successfully!")
        print(f"Response: {send_response}")
    except Exception as e:
        print(f"✗ Failed to send email: {e}")
        print("Make sure your email configuration in .env file is correct")


if __name__ == "__main__":
    # Run basic examples
    basic_email_examples()
    
    # Uncomment to test email sending (configure .env first)
    # test_email_sending()
