"""
Quick test script to verify system components are working
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all core components can be imported"""
    print("Testing imports...")
    
    try:
        from config import get_config, ModelProvider
        print("✓ Configuration system")
    except ImportError as e:
        print(f"✗ Configuration system: {e}")
        return False
    
    try:
        from src.providers import get_model_provider
        print("✓ Model providers")
    except ImportError as e:
        print(f"✗ Model providers: {e}")
        return False
    
    try:
        from src.observability import get_observer
        print("✓ Observability system")
    except ImportError as e:
        print(f"✗ Observability system: {e}")
        return False
    
    try:
        from src.tools import create_email_content
        print("✓ Email tools")
    except ImportError as e:
        print(f"✗ Email tools: {e}")
        return False
    
    try:
        from src.agents import create_email_agent, create_orchestrator
        print("✓ Agent system")
    except ImportError as e:
        print(f"✗ Agent system: {e}")
        return False
    
    try:
        from src.mcp_clients import get_mcp_manager
        print("✓ MCP clients")
    except ImportError as e:
        print(f"✗ MCP clients: {e}")
        return False
    
    return True


def test_configuration():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from config import get_config
        config = get_config()
        print(f"✓ Model provider: {config.model.provider.value}")
        print(f"✓ Model: {config.model.model}")
        print(f"✓ Email configured: {bool(config.email.username)}")
        return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False


def test_observability():
    """Test observability system"""
    print("\nTesting observability...")
    
    try:
        from src.observability import get_observer
        observer = get_observer()
        
        # Test basic logging
        observer.log_agent_thought("test_agent", "Testing observability system")
        observer.log_orchestration_event("test_event", {"test": True})
        
        print("✓ Observer initialized")
        print("✓ Logging functions working")
        return True
    except Exception as e:
        print(f"✗ Observability error: {e}")
        return False


def test_mcp_manager():
    """Test MCP client manager"""
    print("\nTesting MCP manager...")
    
    try:
        from src.mcp_clients import get_mcp_manager
        mcp_manager = get_mcp_manager()
        
        print(f"✓ MCP manager initialized")
        print(f"✓ Available clients: {list(mcp_manager.clients.keys())}")
        return True
    except Exception as e:
        print(f"✗ MCP manager error: {e}")
        return False


def test_basic_functionality():
    """Test basic system functionality without external dependencies"""
    print("\nTesting basic functionality...")
    
    try:
        # Test email content creation (mock)
        from src.tools.email_tools import EmailContentCreator
        creator = EmailContentCreator()
        
        template = creator.create_professional_email("general", "test context")
        print("✓ Email content creator working")
        
        # Test observability wrapper
        from src.observability import make_observable
        print("✓ Observability wrapper available")
        
        return True
    except Exception as e:
        print(f"✗ Basic functionality error: {e}")
        return False


def main():
    """Run all tests"""
    print("Multi-Agent Email System - Component Test")
    print("="*50)
    
    tests = [
        test_imports,
        test_configuration, 
        test_observability,
        test_mcp_manager,
        test_basic_functionality
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "="*50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The system is ready to use.")
        print("\nNext steps:")
        print("1. Configure your .env file")
        print("2. Run: python main.py demo")
        print("3. Try: python main.py interactive")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
