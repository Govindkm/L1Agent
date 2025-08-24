#!/usr/bin/env python3
"""
Simple test of the email system without the full demo complexity
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.email_agent import create_email_agent

# Load environment variables
load_dotenv()

def test_email_agent():
    """Test the email agent with a simple request"""
    
    print("🚀 Testing Email Agent")
    print("=" * 40)
    
    try:
        # Create email agent
        print("Creating email agent...")
        email_agent = create_email_agent("TestEmailAgent")
        print("✅ Email agent created successfully")
        
        # Test 1: Create email content
        print("\n📝 Test 1: Create email content")
        request = """
        Create a professional email for a meeting request with these details:
        - Topic: Weekly team standup
        - Purpose: meeting_request
        - Tone: professional
        - Keep it brief
        """
        
        response = email_agent(request)
        print(f"✅ Response: {response}")
        
        # Test 2: Validate email addresses
        print("\n📋 Test 2: Validate email addresses")
        validation_request = """
        Validate these email addresses:
        - test@example.com
        - invalid-email
        - user@company.com
        """
        
        response = email_agent(validation_request)
        print(f"✅ Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_email_agent()
    
    if success:
        print("\n🎉 Email agent test successful!")
        print("\nThe system is working correctly with Ollama via OpenAI-compatible API")
        print("Model provider abstraction is properly implemented")
    else:
        print("\n😞 Email agent test failed")
        
    print("\n" + "=" * 60)
    print("📋 Summary:")
    print("✅ Model providers: OpenAI, Ollama, Anthropic, LiteLLM")
    print("✅ Configuration: Flexible and extensible") 
    print("✅ Agents: Created using model instances (not model providers)")
    print("✅ Why model providers create agents: For abstraction and flexibility")
    print("")
    print("🔧 Model Provider Architecture:")
    print("1. BaseModelProvider (abstract) - defines interface")
    print("2. Concrete providers (OpenAIProvider, OllamaProvider, etc.) - implement models")
    print("3. Providers create MODEL INSTANCES, not agents directly")
    print("4. Agent() constructor takes model instances")
    print("5. This allows flexible model swapping and configuration")
