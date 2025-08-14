#!/usr/bin/env python3
"""
Getting Started Script for L1Agent Library
==========================================

This script helps developers verify their setup and learn the basics.
"""

import sys
import os
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🤖 {title}")
    print('='*60)

def print_step(step_num, title, description=""):
    """Print a formatted step"""
    print(f"\n📋 Step {step_num}: {title}")
    if description:
        print(f"   {description}")

def check_dependencies():
    """Check if all required dependencies are installed"""
    print_step(1, "Checking Dependencies")
    
    required_packages = [
        "langchain", "langchain_core", "langchain_openai", 
        "langchain_ollama", "langgraph"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - Missing!")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("\n✅ All dependencies are installed!")
    return True

def check_model_setup():
    """Check model configuration"""
    print_step(2, "Checking Model Setup")
    
    # Check Ollama
    try:
        import subprocess
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            models = result.stdout.strip().split('\n')[1:]  # Skip header
            if models and models[0]:
                print("   ✅ Ollama is available with models:")
                for model in models[:3]:  # Show first 3 models
                    if model.strip():
                        print(f"      • {model.split()[0]}")
                return "ollama"
            else:
                print("   ⚠️  Ollama is running but no models found")
                print("      Try: ollama pull llama3")
        else:
            print("   ❌ Ollama command failed")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("   ❌ Ollama not found or not running")
        print("      Install: curl -fsSL https://ollama.ai/install.sh | sh")
        print("      Start: ollama serve")
    
    # Check OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("   ✅ OpenAI API key found")
        return "openai"
    else:
        print("   ⚠️  No OpenAI API key found")
        print("      Set: export OPENAI_API_KEY='your-key'")
    
    return None

def test_basic_functionality():
    """Test basic library functionality"""
    print_step(3, "Testing Basic Functionality")
    
    try:
        # Test imports
        from utils.state import register_agent, update_agent_status, get_execution_summary
        from config.model_config import get_model_config
        print("   ✅ Core imports successful")
        
        # Test state management
        test_state = {
            "messages": [],
            "agent_data_json": "{}",
            "tool_data_json": "{}",
            "execution_history": [],
            "task_status": "active"
        }
        
        register_agent(test_state, "test_agent", "working")
        update_agent_status(test_state, "test_agent", "completed", result="success")
        
        summary = get_execution_summary(test_state)
        if "test_agent" in summary.get("agents", {}):
            print("   ✅ State management working")
        else:
            print("   ❌ State management failed")
            return False
        
        # Test model config
        config = get_model_config()
        print(f"   ✅ Model config: {config.provider.value} - {config.model_name}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Basic functionality test failed: {e}")
        return False

def test_simple_agent():
    """Test a simple agent"""
    print_step(4, "Testing Simple Agent")
    
    try:
        from examples.calculator_agent import CalculatorAgent
        from langchain_core.messages import HumanMessage
        
        # Create test state
        test_state = {
            "messages": [HumanMessage(content="What is 5 + 3?")],
            "agent_data_json": "{}",
            "tool_data_json": "{}",
            "execution_history": [],
            "task_status": "active"
        }
        
        # Test agent (with timeout)
        print("   🧮 Testing calculator agent...")
        agent = CalculatorAgent()
        
        # Note: This might fail if no model is available, which is OK for setup check
        try:
            result = agent.process(test_state)
            if result and result.goto == "__end__":
                print("   ✅ Calculator agent working!")
                if result.update and "messages" in result.update:
                    response = result.update["messages"][0].content
                    print(f"      Response: {response[:100]}...")
                return True
            else:
                print("   ⚠️  Calculator agent returned unexpected result")
                return False
                
        except Exception as e:
            if "api key" in str(e).lower() or "not found" in str(e).lower():
                print("   ⚠️  Agent test skipped (no model available)")
                print(f"      This is OK - setup Ollama or OpenAI to test agents")
                return True
            else:
                print(f"   ❌ Agent test failed: {e}")
                return False
        
    except Exception as e:
        print(f"   ❌ Agent import failed: {e}")
        return False

def show_next_steps():
    """Show next steps for developers"""
    print_step(5, "Next Steps")
    
    print("   🎯 You're ready to start building agents!")
    print()
    print("   📚 Quick Start Options:")
    print("      • Run interactive calculator:")
    print("        python examples/interactive_calculator.py")
    print()
    print("      • Try a single calculation:")
    print("        python examples/interactive_calculator.py -e '25 + 17'")
    print()
    print("      • Test the full system:")
    print("        python -c \"from system import MultiAgentSystem; s=MultiAgentSystem(); print('OK')\"")
    print()
    print("   📖 Documentation:")
    print("      • Main README: README.md")
    print("      • Developer Guide: DEVELOPER_GUIDE.md")
    print("      • Quick Reference: QUICK_REFERENCE.md")
    print()
    print("   🔧 Development:")
    print("      • Create your first agent: See examples/calculator_agent.py")
    print("      • Run tests: python -m pytest tests/")
    print("      • Check logs: tail -f agent_logs.log")

def main():
    """Main setup verification"""
    print_header("L1Agent Library Setup Verification")
    print("This script will verify your setup and guide you through getting started.")
    
    # Run checks
    deps_ok = check_dependencies()
    if not deps_ok:
        print("\n❌ Please install missing dependencies first.")
        return False
    
    model_provider = check_model_setup()
    if not model_provider:
        print("\n⚠️  No AI models available. Setup Ollama or OpenAI to test agents.")
    else:
        # Configure the available model
        if model_provider == "ollama":
            try:
                from config.model_config import configure_ollama_model
                configure_ollama_model("llama3:latest")
                print("   ✅ Configured Ollama model")
            except Exception as e:
                print(f"   ⚠️  Model configuration issue: {e}")
        elif model_provider == "openai":
            try:
                from config.model_config import configure_openai_model
                configure_openai_model("gpt-4o-mini")
                print("   ✅ Configured OpenAI model")
            except Exception as e:
                print(f"   ⚠️  Model configuration issue: {e}")
    
    basic_ok = test_basic_functionality()
    if not basic_ok:
        print("\n❌ Basic functionality test failed.")
        return False
    
    agent_ok = test_simple_agent()
    
    # Summary
    print_header("Setup Summary")
    
    status_items = [
        ("Dependencies", "✅" if deps_ok else "❌"),
        ("Model Provider", "✅" if model_provider else "⚠️"),
        ("Basic Functions", "✅" if basic_ok else "❌"),
        ("Agent Test", "✅" if agent_ok else "⚠️")
    ]
    
    for item, status in status_items:
        print(f"   {status} {item}")
    
    if all([deps_ok, basic_ok]):
        print("\n🎉 Setup verification complete!")
        show_next_steps()
        return True
    else:
        print("\n⚠️  Some issues found. Check the output above.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Setup verification interrupted.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
