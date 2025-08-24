#!/usr/bin/env python3
"""
Debug script to test model provider configurations
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.settings import get_config
from providers.model_providers import get_model_provider

# Load environment variables
load_dotenv()

def test_model_provider():
    """Test creating a model provider and agent"""
    
    try:
        # Get configuration
        config = get_config()
        print(f"✅ Configuration loaded successfully")
        print(f"   Provider: {config.model.provider}")
        print(f"   Model: {config.model.model}")
        print(f"   Base URL: {config.model.base_url}")
        
        # Get model provider
        provider = get_model_provider(config.model)
        print(f"✅ Model provider created: {provider.__class__.__name__}")
        
        # Get model info
        model_info = provider.get_model_info()
        print(f"✅ Model info: {model_info}")
        
        # Create model instance
        model = provider.create_model()
        print(f"✅ Model instance created: {model.__class__.__name__}")
        
        # Create agent with model
        agent = provider.create_agent(
            system_prompt="You are a helpful assistant. Respond briefly."
        )
        print(f"✅ Agent created successfully: {agent.__class__.__name__}")
        
        # Try a simple interaction
        print("\n🧪 Testing simple interaction...")
        response = agent("Say hello in one word")
        print(f"✅ Agent response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_environment_setup():
    """Test if environment variables are loaded correctly"""
    print("🔧 Environment Variables:")
    print(f"MODEL_PROVIDER: {os.getenv('MODEL_PROVIDER')}")
    print(f"OPENAI_API_KEY: {'***' if os.getenv('OPENAI_API_KEY') else 'Not set'}")
    print(f"OPENAI_BASE_URL: {os.getenv('OPENAI_BASE_URL')}")
    print(f"OPENAI_MODEL: {os.getenv('OPENAI_MODEL')}")
    print(f"OLLAMA_BASE_URL: {os.getenv('OLLAMA_BASE_URL')}")
    print(f"OLLAMA_MODEL: {os.getenv('OLLAMA_MODEL')}")
    print(f"EMAIL_USER: {os.getenv('EMAIL_USER')}")
    print(f"EMAIL_PASSWORD: {'***' if os.getenv('EMAIL_PASSWORD') else 'Not set'}")


if __name__ == "__main__":
    print("🚀 Debug Model Provider Configuration")
    print("=" * 50)
    
    test_environment_setup()
    
    print("\n" + "=" * 50)
    success = test_model_provider()
    
    if success:
        print(f"\n🎉 Model provider test successful!")
    else:
        print("\n😞 Model provider test failed")
        print("Check the configuration and ensure all dependencies are installed")
