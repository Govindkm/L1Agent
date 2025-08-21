#!/usr/bin/env python3
"""
Quick test of email content generation with the updated model configuration.
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.email_tools import generate_email_content
from config.model_config import get_model_config

def test_email_generation_with_qwen():
    """Test email generation with qwen2.5 model"""
    print("🧪 TESTING EMAIL GENERATION WITH QWEN2.5")
    print("=" * 50)
    
    # Show current configuration
    config = get_model_config()
    print(f"🤖 Current Model: {config.model_name}")
    print(f"📡 Provider: {config.provider.value}")
    
    # Test cases
    test_cases = [
        {
            "topic": "project deadline extension request",
            "recipient": "Manager",
            "style": "professional"
        },
        {
            "topic": "team meeting reminder",
            "recipient": "Team",
            "style": "friendly"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📧 Test Case {i}: {test_case['topic']}")
        print(f"   Recipient: {test_case['recipient']}")
        print(f"   Style: {test_case['style']}")
        print("-" * 40)
        
        try:
            result = generate_email_content.func(
                topic=test_case['topic'],
                recipient_name=test_case['recipient'],
                style=test_case['style']
            )
            
            if "Error generating email content" not in result:
                print("✅ Email generation successful!")
                print("📄 Generated content:")
                print("-" * 30)
                print(result)
                print("-" * 30)
            else:
                print(f"❌ Error: {result}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_email_generation_with_qwen()
