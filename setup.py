#!/usr/bin/env python3
"""
Setup script for the Multi-Agent Email System
Installs dependencies and configures the environment
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"{'='*50}")
    print(f"RUNNING: {description}")
    print(f"COMMAND: {command}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✓ SUCCESS")
        if result.stdout:
            print("OUTPUT:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ FAILED: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"✗ Python 3.10+ is required. Current version: {version.major}.{version.minor}")
        return False
    
    print(f"✓ Python version {version.major}.{version.minor} is compatible")
    return True


def install_dependencies():
    """Install Python dependencies"""
    print("Installing dependencies...")
    
    # Install from requirements.txt
    if run_command("pip install -r requirements.txt", "Installing Python packages"):
        print("✓ Dependencies installed successfully")
        return True
    else:
        print("✗ Failed to install dependencies")
        print("You may need to install packages manually:")
        print("  pip install strands-agents strands-agents-tools")
        print("  pip install python-dotenv click rich")
        return False


def setup_environment():
    """Setup environment configuration"""
    print("Setting up environment configuration...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print("✓ Created .env file from .env.example")
        else:
            create_default_env()
            print("✓ Created default .env file")
        
        print("\n" + "!"*60)
        print("IMPORTANT: Please edit the .env file with your configuration:")
        print("  - Set your model provider (openai or ollama)")
        print("  - Add API keys if using OpenAI")
        print("  - Configure email settings")
        print("!"*60 + "\n")
    else:
        print("✓ .env file already exists")


def create_default_env():
    """Create a default .env file"""
    default_env = """# Model Provider Configuration
# Choose between "openai" or "ollama"
MODEL_PROVIDER=ollama

# OpenAI API Configuration
# OPENAI_API_KEY=your_openai_api_key_here

# Ollama Configuration (for local models)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=agent_logs.log

# Observability Configuration
ENABLE_TRACING=true
ENABLE_METRICS=true
# JAEGER_ENDPOINT=http://localhost:14268

# MCP Server Configuration (optional)
# GITHUB_MCP_SERVER=
# ADO_MCP_SERVER=
# FILESYSTEM_MCP_SERVER=
"""
    
    with open(".env", "w") as f:
        f.write(default_env)


def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    
    directories = [
        "logs",
        "data",
        "temp"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")


def test_installation():
    """Test the installation"""
    print("Testing installation...")
    
    try:
        # Test imports
        sys.path.insert(0, 'src')
        from src import get_config, create_email_agent
        print("✓ Core imports successful")
        
        # Test configuration
        config = get_config()
        print(f"✓ Configuration loaded (provider: {config.model.provider.value})")
        
        # Test agent creation (basic)
        try:
            agent = create_email_agent("TestAgent")
            print("✓ Agent creation successful")
        except Exception as e:
            print(f"⚠ Agent creation failed: {e}")
            print("  This may be due to missing model provider configuration")
        
        return True
        
    except Exception as e:
        print(f"✗ Installation test failed: {e}")
        return False


def show_next_steps():
    """Show next steps after setup"""
    print("\n" + "="*60)
    print("SETUP COMPLETED!")
    print("="*60)
    
    print("\nNext steps:")
    print("1. Edit the .env file with your configuration")
    print("2. If using Ollama, make sure it's running:")
    print("   ollama serve")
    print("3. If using OpenAI, add your API key to .env")
    print("4. Test the system:")
    print("   python main.py demo")
    print("5. Start interactive mode:")
    print("   python main.py interactive")
    
    print("\nExample commands:")
    print("   python examples/basic_email_example.py")
    print("   python examples/orchestrator_example.py")
    print("   python examples/observability_example.py")
    
    print("\nDocumentation:")
    print("   Check README.md for detailed usage instructions")
    print("   See examples/ directory for more examples")


def main():
    """Main setup function"""
    print("Multi-Agent Email System - Setup Script")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("⚠ Some dependencies may not be installed correctly")
        print("You may need to install them manually or check your internet connection")
    
    # Setup environment
    setup_environment()
    
    # Create directories
    create_directories()
    
    # Test installation
    if test_installation():
        print("✓ Installation test passed")
    else:
        print("⚠ Some components may not work correctly")
        print("Check the error messages above and your configuration")
    
    # Show next steps
    show_next_steps()


if __name__ == "__main__":
    main()
