# L1Agent: Dynamic Multi-Agent System Library 🤖

A sophisticated multi-agent system built with LangGraph that supports dynamic agent creation, comprehensive observability, and extensible architecture. Create intelligent agents that can collaborate, think, and solve complex problems.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2.58-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🌟 Key Features

- **🔄 Dynamic Agent System**: Add new agents without modifying core code
- **🧠 AI Model Support**: OpenAI GPT models and Ollama local models
- **📊 Comprehensive Observability**: Track agent thinking, actions, and execution
- **🛠️ Extensible Architecture**: Modular design for easy customization
- **🔗 LangGraph Integration**: Powerful workflow orchestration
- **📝 Natural Language Processing**: Agents understand human language
- **🏗️ Production Ready**: Error handling, logging, and state management

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Architecture Overview](#architecture-overview)
- [Creating Your First Agent](#creating-your-first-agent)
- [Advanced Agent Development](#advanced-agent-development)
- [Working with the Dynamic State System](#working-with-the-dynamic-state-system)
- [Model Configuration](#model-configuration)
- [Observability and Logging](#observability-and-logging)
- [Examples](#examples)
- [API Reference](#api-reference)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/your-org/L1Agent.git
cd L1Agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup Model Provider

**Option A: OpenAI (Cloud)**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

**Option B: Ollama (Local)**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull a model
ollama pull llama3
```

### 3. Test the System

```python
from system import MultiAgentSystem
from config.model_config import configure_ollama_model

# Configure for local model
configure_ollama_model("llama3:latest")

# Initialize system
system = MultiAgentSystem()

# Process a request
result = system.process_request("What's the weather in San Francisco?")
print(result)
```

## 🏗️ Architecture Overview

```
L1Agent/
├── agents/           # Agent implementations
├── config/           # Configuration files
├── utils/            # Utilities and state management
├── examples/         # Example agents and demos
├── system.py         # Main system orchestrator
└── requirements.txt  # Dependencies
```

### Core Components

1. **Dynamic State System**: JSON-based state that automatically adapts to new agents
2. **Agent Registry**: Automatically discover and register new agents
3. **Observer Pattern**: Track agent thinking and execution
4. **Model Abstraction**: Support multiple AI providers
5. **LangGraph Integration**: Workflow orchestration and routing

## 🤖 Creating Your First Agent

### Step 1: Define Your Agent Class

```python
# agents/my_agent.py
from typing import Literal
from langchain_core.messages import AIMessage
from langgraph.types import Command

from agents.base_agent import BaseAgent
from utils.state import (
    MultiAgentState, 
    register_agent, 
    update_agent_status,
    log_execution_step
)
from config.model_config import get_model

class MyAgent(BaseAgent):
    """Custom agent that does amazing things"""
    
    def __init__(self):
        super().__init__("MyAgent")
    
    def process(self, state: MultiAgentState) -> Command[Literal["__end__"]]:
        """Process requests for this agent"""
        
        # Register agent in dynamic state
        register_agent(state, "my_agent", "working")
        log_execution_step(state, "my_agent", "started_processing")
        
        # Log thinking process
        self.log_thinking(
            "Received request from orchestrator",
            "Analyzing user requirements"
        )
        
        # Get user message
        messages = state["messages"]
        user_message = messages[-1].content if messages else ""
        
        try:
            # Use AI model to process
            model = get_model()
            response = model.invoke([
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ])
            
            # Log successful processing
            self.log_thinking(
                f"Processed request: {user_message}",
                "Generating response"
            )
            
            # Update agent status
            update_agent_status(state, "my_agent", "completed", 
                              result=response.content)
            log_execution_step(state, "my_agent", "completed_processing", {
                "input": user_message,
                "output": response.content
            })
            
            # Return response
            ai_message = AIMessage(content=response.content, name="my_agent")
            return Command(
                goto="__end__",
                update={"messages": [ai_message]}
            )
            
        except Exception as e:
            # Handle errors gracefully
            self.log_thinking(f"Error occurred: {str(e)}", "Returning error response")
            
            update_agent_status(state, "my_agent", "failed", error=str(e))
            log_execution_step(state, "my_agent", "error", {"error": str(e)})
            
            error_message = AIMessage(
                content=f"I encountered an error: {str(e)}",
                name="my_agent"
            )
            return Command(
                goto="__end__",
                update={"messages": [error_message]}
            )
```

### Step 2: Test Your Agent

```python
# test_my_agent.py
from langchain_core.messages import HumanMessage
from config.model_config import configure_ollama_model
from agents.my_agent import MyAgent

# Configure model
configure_ollama_model("llama3:latest")

# Create test state
state = {
    "messages": [HumanMessage(content="Hello, how are you?")],
    "agent_data_json": "{}",
    "tool_data_json": "{}",
    "execution_history": [],
    "task_status": "active"
}

# Test agent
agent = MyAgent()
result = agent.process(state)
print(f"Response: {result.update['messages'][0].content}")
```

### Step 3: Register with System (Optional)

```python
# utils/registry.py - Add to get_registry() function
def get_registry():
    registry = DynamicRegistry()
    
    # Register existing agents
    # ... existing registrations ...
    
    # Register your new agent
    registry.register_agent(
        "my_agent",
        MyAgent,
        "Custom agent that does amazing things",
        capabilities=["general_assistance", "custom_logic"],
        routing_keywords=["help", "assist", "custom"]
    )
    
    return registry
```

## 🔧 Advanced Agent Development

### Working with Tools

```python
from utils.state import register_tool, update_tool_data

class AdvancedAgent(BaseAgent):
    def process(self, state: MultiAgentState) -> Command:
        # Register tool usage
        register_tool(state, "my_tool")
        
        # Use tool
        tool_result = self.use_custom_tool(user_input)
        
        # Update tool data
        update_tool_data(state, "my_tool", 
                        result=tool_result,
                        metadata={"query_type": "advanced"},
                        status="success")
        
        return Command(goto="__end__")
    
    def use_custom_tool(self, input_data):
        """Custom tool implementation"""
        # Your tool logic here
        return "Tool result"
```

### Multi-Step Processing

```python
class MultiStepAgent(BaseAgent):
    def process(self, state: MultiAgentState) -> Command:
        register_agent(state, "multistep_agent", "working")
        
        # Step 1: Analysis
        log_execution_step(state, "multistep_agent", "step_1_analysis")
        analysis_result = self.analyze_input(state)
        
        # Step 2: Processing
        log_execution_step(state, "multistep_agent", "step_2_processing")
        processed_result = self.process_data(analysis_result)
        
        # Step 3: Finalization
        log_execution_step(state, "multistep_agent", "step_3_finalization")
        final_result = self.finalize_output(processed_result)
        
        update_agent_status(state, "multistep_agent", "completed", 
                          result=final_result)
        
        return Command(goto="__end__", update={"messages": [final_result]})
```

### Conditional Routing

```python
class RouterAgent(BaseAgent):
    def process(self, state: MultiAgentState) -> Command:
        user_input = state["messages"][-1].content
        
        if "weather" in user_input.lower():
            return Command(goto="weather_agent")
        elif "email" in user_input.lower():
            return Command(goto="email_agent")
        elif "calculate" in user_input.lower():
            return Command(goto="calculator_agent")
        else:
            return Command(goto="general_agent")
```

## 📊 Working with the Dynamic State System

The dynamic state system automatically adapts to new agents and tools without requiring code changes.

### State Functions

```python
from utils.state import (
    register_agent,
    update_agent_status,
    register_tool,
    update_tool_data,
    log_execution_step,
    get_execution_summary,
    set_custom_data,
    get_custom_data
)

# Agent registration
register_agent(state, "agent_name", "initial_status")

# Status updates
update_agent_status(state, "agent_name", "completed", 
                   result="success", action="processed_request")

# Tool management
register_tool(state, "tool_name")
update_tool_data(state, "tool_name", result="tool_output", status="success")

# Execution logging
log_execution_step(state, "agent_name", "action_name", {"key": "value"})

# Custom data
set_custom_data(state, "my_key", {"custom": "data"})
my_data = get_custom_data(state, "my_key")

# Get summary
summary = get_execution_summary(state)
print(f"Agents: {len(summary['agents'])}")
print(f"Tools: {len(summary['tools'])}")
print(f"Steps: {len(summary['execution_steps'])}")
```

### State Structure

```python
# The state is automatically managed as JSON
{
    "agent_data_json": "{...}",      # Agent status and results
    "tool_data_json": "{...}",       # Tool usage and results
    "execution_history": [...],      # Timestamped execution steps
    "custom_data_json": "{...}",     # Your custom data
    "messages": [...],               # LangChain messages
    "task_status": "active"          # Overall task status
}
```

## 🎛️ Model Configuration

### OpenAI Configuration

```python
from config.model_config import configure_openai_model

# Configure OpenAI
config = configure_openai_model(
    model_name="gpt-4o-mini",
    temperature=0.1,
    api_key="your-api-key"  # Optional if env var set
)
```

### Ollama Configuration

```python
from config.model_config import configure_ollama_model

# Configure Ollama
config = configure_ollama_model(
    model_name="llama3:latest",
    temperature=0.1,
    base_url="http://localhost:11434"
)
```

### Dynamic Model Switching

```python
from config.model_config import get_model, ModelProvider

# Get current model
model = get_model()

# Check provider
config = get_model_config()
if config.provider == ModelProvider.OLLAMA:
    print("Using local Ollama model")
else:
    print("Using OpenAI model")
```

## 👁️ Observability and Logging

### Agent Thinking Logs

```python
from utils import get_observer

class ObservableAgent(BaseAgent):
    def process(self, state: MultiAgentState) -> Command:
        # Log thinking process
        self.log_thinking(
            "Analyzing user request for sentiment",
            "Using NLP model to determine emotional tone"
        )
        
        # Process...
        
        self.log_thinking(
            "Sentiment analysis complete: positive",
            "Generating appropriate response"
        )
        
        return Command(goto="__end__")

# View observations
observer = get_observer()
observations = observer.get_observations()
for obs in observations:
    print(f"{obs['agent']}: {obs['thought']} -> {obs['action']}")
```

### Execution Tracking

```python
# All agent actions are automatically tracked
summary = get_execution_summary(state)

print("Execution Timeline:")
for step in summary['execution_steps']:
    print(f"{step['timestamp']}: {step['agent']} - {step['action']}")
    if step['details']:
        print(f"  Details: {step['details']}")
```

### Log Files

```python
from utils import setup_logging

# Configure logging
setup_logging(log_level="INFO", log_file="my_agents.log")

# Logs are written to:
# - Console (real-time)
# - Log file (persistent)
# - Observer (programmatic access)
```

## 📚 Examples

### Calculator Agent
```bash
# Interactive calculator
python examples/interactive_calculator.py

# Single calculation
python examples/interactive_calculator.py -e "25 * 4 + 10"

# Batch tests
python examples/interactive_calculator.py --batch
```

### Weather Agent
```python
# Test weather functionality
python -c "
from system import MultiAgentSystem
system = MultiAgentSystem()
result = system.process_request('What is the weather in London?')
print(result)
"
```

### Custom Agent Example
See `examples/calculator_agent.py` for a complete example of:
- Natural language processing
- Mathematical expression parsing
- Error handling
- State management
- Tool integration

## 📖 API Reference

### BaseAgent Class

```python
class BaseAgent:
    def __init__(self, name: str)
    def process(self, state: MultiAgentState) -> Command
    def log_thinking(self, thought: str, action: str = None)
```

### State Functions

```python
# Agent Management
register_agent(state, name, status)
update_agent_status(state, name, status, result=None, action=None, error=None)

# Tool Management  
register_tool(state, name)
update_tool_data(state, name, result=None, metadata=None, status=None)

# Execution Tracking
log_execution_step(state, agent, action, details=None)
get_execution_summary(state) -> Dict

# Custom Data
set_custom_data(state, key, value)
get_custom_data(state, key, default=None)
```

### Model Configuration

```python
# Configuration
configure_openai_model(model_name, temperature, api_key)
configure_ollama_model(model_name, temperature, base_url)

# Usage
get_model() -> BaseChatModel
get_model_config() -> ModelConfig
```

## 🎯 Best Practices

### 1. Agent Design

- **Single Responsibility**: Each agent should have a clear, focused purpose
- **Error Handling**: Always handle exceptions gracefully
- **State Management**: Use dynamic state functions consistently
- **Logging**: Log thinking process for observability

### 2. State Management

```python
# ✅ Good: Use state functions
register_agent(state, "my_agent", "working")
update_agent_status(state, "my_agent", "completed", result=data)

# ❌ Bad: Direct state manipulation
state["agent_data"] = {"my_agent": {"status": "completed"}}
```

### 3. Error Handling

```python
# ✅ Good: Comprehensive error handling
try:
    result = process_data()
    update_agent_status(state, "agent", "completed", result=result)
except Exception as e:
    self.log_thinking(f"Error: {e}", "Handling gracefully")
    update_agent_status(state, "agent", "failed", error=str(e))
    return Command(goto="__end__", update={"messages": [error_response]})
```

### 4. Testing

```python
# Create isolated test states
def create_test_state(message_content="test"):
    return {
        "messages": [HumanMessage(content=message_content)],
        "agent_data_json": "{}",
        "tool_data_json": "{}",
        "execution_history": [],
        "task_status": "active"
    }
```

### 5. Performance

- Use appropriate model sizes (e.g., gpt-4o-mini for simple tasks)
- Cache expensive operations
- Monitor token usage for cloud models
- Use local models for development and testing

## 🔧 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Ensure you're in the project root
cd L1Agent

# Activate virtual environment
source .venv/bin/activate

# Check Python path
python -c "import sys; print(sys.path)"
```

**2. Model Not Found**
```bash
# For Ollama
ollama list
ollama pull llama3

# For OpenAI
echo $OPENAI_API_KEY
```

**3. State Tracking Issues**
```python
# Debug state
from utils.state import get_execution_summary
summary = get_execution_summary(state)
print(f"Debug: {summary}")
```

**4. Agent Not Responding**
```python
# Check model configuration
from config.model_config import get_model_config
config = get_model_config()
print(f"Current model: {config}")
```

### Debug Mode

```python
# Enable debug logging
from utils import setup_logging
setup_logging(log_level="DEBUG")

# Check observer logs
from utils import get_observer
observer = get_observer()
observer.print_observations()
```

### Performance Monitoring

```python
import time
from utils.state import log_execution_step

start_time = time.time()
# ... agent processing ...
duration = time.time() - start_time

log_execution_step(state, "agent_name", "performance_metric", {
    "duration_seconds": duration,
    "tokens_used": token_count
})
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-agent`
3. **Add your agent**: Follow the patterns in `examples/`
4. **Add tests**: Create test files for your agent
5. **Update documentation**: Add examples and API docs
6. **Submit a pull request**

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Check code style
flake8 agents/ utils/ examples/

# Type checking
mypy agents/ utils/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check this README and example files
- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **Examples**: See the `examples/` directory

## 🔮 Roadmap

- [ ] Web UI for agent interaction
- [ ] Agent marketplace and templates
- [ ] Advanced workflow orchestration
- [ ] Multi-modal agent support
- [ ] Performance analytics dashboard
- [ ] Distributed agent execution

---

**Happy Agent Building!** 🚀

*Built with ❤️ using LangGraph, LangChain, and the power of AI agents*
