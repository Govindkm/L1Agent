#!/usr/bin/env python3
"""
Test script to verify model configuration is reading from .env file
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.model_config import get_model_config, get_model
from dotenv import load_dotenv

def test_model_config():
    """Test if model configuration reads from .env correctly"""
    print("🧪 MODEL CONFIGURATION TEST")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check environment variables
    print("📋 Environment Variables:")
    print(f"   MODEL_PROVIDER: {os.getenv('MODEL_PROVIDER', 'Not set')}")
    print(f"   OLLAMA_MODEL: {os.getenv('OLLAMA_MODEL', 'Not set')}")
    print(f"   OLLAMA_BASE_URL: {os.getenv('OLLAMA_BASE_URL', 'Not set')}")
    print(f"   OPENAI_API_KEY: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}")
    
    # Get model configuration
    print("\n🤖 Model Configuration:")
    try:
        config = get_model_config()
        print(f"   Provider: {config.provider.value}")
        print(f"   Model Name: {config.model_name}")
        print(f"   Temperature: {config.temperature}")
        
        if config.provider.value == "ollama":
            print(f"   Ollama Base URL: {config.ollama_base_url}")
        elif config.provider.value == "openai":
            print(f"   OpenAI API Key: {'Available' if config.openai_api_key else 'Missing'}")
        
        print("✅ Configuration loaded successfully")
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    # Try to create model instance
    print("\n🚀 Model Instance Creation:")
    try:
        model = get_model()
        print(f"   Model type: {type(model).__name__}")
        print(f"   Model info: {model}")
        print("✅ Model instance created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Model creation error: {e}")
        return False

def test_ollama_connection():
    """Test if Ollama is running and accessible"""
    print("\n\n🦙 OLLAMA CONNECTION TEST")
    print("=" * 30)
    
    import requests
    
    ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    
    try:
        # Test if Ollama is running
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            print(f"✅ Ollama is running at {ollama_url}")
            print(f"📋 Available models:")
            if 'models' in models:
                for model in models['models']:
                    print(f"   - {model.get('name', 'Unknown')}")
            else:
                print("   No models found")
            return True
        else:
            print(f"⚠️  Ollama responded with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print(f"💡 Make sure Ollama is running with: ollama serve")
        return False

if __name__ == "__main__":
    config_success = test_model_config()
    ollama_success = test_ollama_connection()
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    print(f"   Model Config: {'✅ Success' if config_success else '❌ Failed'}")
    print(f"   Ollama Connection: {'✅ Success' if ollama_success else '❌ Failed'}")
    
    if not config_success:
        print("\n🔧 Troubleshooting:")
        print("   1. Check if .env file exists in project root")
        print("   2. Verify MODEL_PROVIDER is set to 'ollama' in .env")
        print("   3. Check OLLAMA_MODEL and OLLAMA_BASE_URL values")
    
    if not ollama_success:
        print("\n🦙 Ollama Setup:")
        print("   1. Install Ollama from https://ollama.ai")
        print("   2. Start Ollama server: ollama serve")
        print("   3. Pull the model: ollama pull gpt-oss")
