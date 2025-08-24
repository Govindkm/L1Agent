#!/usr/bin/env python3
"""
Debug configuration loading
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.settings import get_config, ModelProvider

# Load environment variables
load_dotenv()

def debug_configuration():
    """Debug configuration loading"""
    
    print("🔧 Environment Variables (Raw):")
    print(f"MODEL_PROVIDER: {os.getenv('MODEL_PROVIDER')}")
    print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")
    print(f"OPENAI_BASE_URL: {os.getenv('OPENAI_BASE_URL')}")
    print(f"OPENAI_MODEL: {os.getenv('OPENAI_MODEL')}")
    print(f"OLLAMA_BASE_URL: {os.getenv('OLLAMA_BASE_URL')}")
    print(f"OLLAMA_MODEL: {os.getenv('OLLAMA_MODEL')}")
    print(f"EMAIL_USER: {os.getenv('EMAIL_USER')}")
    print(f"EMAIL_PASSWORD: {'***' if os.getenv('EMAIL_PASSWORD') else 'Not set'}")
    
    print("\n" + "="*50)
    
    try:
        print("📋 Loading Configuration...")
        config = get_config()
        
        print(f"✅ Configuration loaded successfully")
        print(f"Provider Enum: {config.model.provider}")
        print(f"Provider Value: {config.model.provider.value}")
        print(f"Model: {config.model.model}")
        print(f"API Key: {'***' if config.model.api_key else 'None'}")
        print(f"Base URL: {config.model.base_url}")
        print(f"Temperature: {config.model.temperature}")
        print(f"Max Tokens: {config.model.max_tokens}")
        
        print(f"\nEmail Config:")
        print(f"Username: {config.email.username}")
        print(f"Password: {'***' if config.email.password else 'None'}")
        
        print(f"\n🔍 Validation Check:")
        # Check individual conditions
        if config.model.provider == ModelProvider.OPENAI:
            print(f"✅ Using OpenAI provider")
            if config.model.api_key:
                print(f"✅ OpenAI API key present")
            else:
                print(f"❌ OpenAI API key missing")
        
        if config.model.provider == ModelProvider.OLLAMA:
            print(f"🔧 Using Ollama provider")
            if config.model.base_url:
                print(f"✅ Ollama base URL present")
            else:
                print(f"❌ Ollama base URL missing")
        
        # Email validation
        if config.email.username and config.email.password:
            print(f"✅ Email credentials present")
        else:
            print(f"❌ Email credentials missing")
        
        print(f"\n🎯 Full Validation Result:")
        is_valid = config.validate()
        print(f"Valid: {is_valid}")
        
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_configuration()
