#!/usr/bin/env python3
"""
Test script to verify email sending functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables BEFORE importing our modules
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tools.email_tools import EmailSender
from config.settings import get_config

def test_email_connection():
    """Test email connection and sending"""
    
    print("🚀 Testing Email Connection")
    print("=" * 40)
    
    try:
        # Get configuration
        config = get_config()
        print(f"✅ Configuration loaded")
        print(f"   SMTP Server: {config.email.smtp_server}")
        print(f"   SMTP Port: {config.email.smtp_port}")
        print(f"   Username: {config.email.username}")
        print(f"   Use TLS: {config.email.use_tls}")
        print(f"   Verify SSL: {config.email.verify_ssl}")
        
        # Create email sender
        sender = EmailSender()
        print(f"✅ Email sender created")
        
        # Test email sending
        print("\n📧 Testing email sending...")
        result = sender.send_email(
            to_emails=[config.email.username],  # Send to self for testing
            subject="Test Email - Strands Email Agent",
            body="""Hello!

This is a test email from the Strands Email Agent system to verify that email sending functionality is working correctly.

Key features tested:
- SMTP connection with TLS
- SSL certificate handling
- Email composition and sending
- Configuration loading

If you receive this email, the system is working properly!

Best regards,
The Strands Email Agent System
""",
            is_html=False
        )
        
        print(f"Result: {result}")
        
        if result["status"] == "success":
            print("🎉 Email sent successfully!")
            return True
        else:
            print(f"❌ Email failed: {result['message']}")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_email_connection()
    
    if success:
        print("\n🎉 Email system working correctly!")
    else:
        print("\n😞 Email system has issues")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check Gmail app-specific password")
        print("2. Try setting EMAIL_VERIFY_SSL=false in .env")
        print("3. Ensure Gmail 'Less secure app access' is enabled (if using regular password)")
        print("4. Check firewall/network connectivity")
