# 🤖 L1Agent Library Overview

## 📁 Project Structure

```
L1Agent/
├── README.md                           # Main documentation
├── DEVELOPER_GUIDE.md                  # Advanced patterns & best practices
├── QUICK_REFERENCE.md                  # Code snippets & checklists
├── LIBRARY_OVERVIEW.md                 # This file - complete overview
├── getting_started.py                  # Setup verification script
├── requirements.txt                    # Python dependencies
├── system.py                          # Main orchestrator system
├── config/
│   └── model_config.py                # Model configuration
├── utils/
│   ├── state.py                       # Dynamic state management
│   ├── tools.py                       # Tool definitions
│   └── observer.py                    # Agent thinking & logging
├── agents/
│   ├── base_agent.py                  # Base agent class
│   ├── calculator_agent.py            # Calculator implementation
│   ├── orchestrator_agent.py          # Main orchestration logic
│   ├── weather_agent.py               # Weather information (demo)
│   └── email_agent.py                 # Email functionality (demo)
└── examples/
    └── interactive_calculator.py      # Interactive calculator demo
```

## 🚀 Quick Start

### 1. Installation
```bash
# Clone and setup
git clone <your-repo>
cd L1Agent
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Install Ollama (for local models)
# Visit: https://ollama.ai/download
ollama pull llama3:latest
```

### 2. Verification
```bash
python getting_started.py
```

### 3. Try Examples
```bash
# Interactive mode
python examples/interactive_calculator.py

# Single calculation
python examples/interactive_calculator.py -e "25 * 4 + 10"

# Batch mode
python examples/interactive_calculator.py -b
```

## 🏗️ Core Components

### 1. **Dynamic State Management** (`utils/state.py`)
- JSON-based state storage for unlimited extensibility
- Automatic agent/tool registration
- Execution timeline tracking
- No static schemas - add agents dynamically

```python
from utils.state import register_agent, update_agent_status, log_execution_step

# Register new agent automatically
register_agent(state, "MyNewAgent", "processing", {"custom": "data"})

# Track execution
log_execution_step(state, "MyNewAgent", "thinking", "Analyzing user request")
```

### 2. **Multi-Agent Orchestration** (`system.py`)
- LangGraph-based workflow orchestration
- Command-driven agent communication
- Automatic state management
- Built-in observability

```python
from system import MultiAgentSystem

system = MultiAgentSystem()
result = system.process_request("Calculate 15 * 8 + 42")
```

### 3. **Base Agent Framework** (`agents/base_agent.py`)
- Standardized agent interface
- Automatic state integration
- Built-in thinking/action logging
- LangChain tool integration

```python
from agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__("MyAgent", "Handles my tasks")
    
    def process(self, state):
        # Your agent logic here
        pass
```

### 4. **Model Configuration** (`config/model_config.py`)
- Multi-provider support (OpenAI, Ollama)
- Environment-based configuration
- Easy model switching
- Local and cloud deployment ready

```python
# Supports both OpenAI and Ollama
# Set MODEL_PROVIDER=openai or MODEL_PROVIDER=ollama
# Automatically configures based on environment
```

### 5. **Observability System** (`utils/observer.py`)
- Real-time agent thinking logs
- Action tracking
- Execution timeline
- Debug-friendly output

```python
# Automatic logging in all agents
self.observer.log_thinking("Analyzing user request")
self.observer.log_action("Extracting mathematical expression")
```

## 📋 File Descriptions

| File | Purpose | Key Features |
|------|---------|--------------|
| `README.md` | Main documentation | Installation, quick start, architecture |
| `DEVELOPER_GUIDE.md` | Advanced patterns | Real-world examples, best practices |
| `QUICK_REFERENCE.md` | Developer reference | Code snippets, common patterns |
| `getting_started.py` | Setup verification | Automated setup checking |
| `system.py` | Main orchestrator | LangGraph workflows, state management |
| `utils/state.py` | Dynamic state | JSON-based extensible state system |
| `utils/observer.py` | Observability | Agent thinking and action logging |
| `agents/base_agent.py` | Agent framework | Standardized agent interface |
| `examples/interactive_calculator.py` | Demo application | Interactive calculator with CLI |

## 🎯 Usage Patterns

### Creating New Agents
```python
from agents.base_agent import BaseAgent

class DataAgent(BaseAgent):
    def __init__(self):
        super().__init__("DataAgent", "Processes data requests")
    
    def process(self, state):
        self.observer.log_thinking("Processing data request")
        # Your logic here
        return Command(goto="orchestrator")
```

### Adding Tools
```python
from utils.tools import create_calculator_tool

def my_tool(input: str) -> str:
    """Custom tool description"""
    return f"Processed: {input}"

# Tools automatically integrate with agents
```

### State Management
```python
from utils.state import get_state_value, set_state_value

# Dynamic state access
user_data = get_state_value(state, "user_preferences", {})
set_state_value(state, "processing_status", "complete")
```

## 🔧 Development Workflow

1. **Start with Examples**: Run `examples/interactive_calculator.py`
2. **Create New Agent**: Copy `agents/calculator_agent.py` as template
3. **Add to System**: Register in `system.py`
4. **Test Integration**: Use `getting_started.py` to verify
5. **Deploy**: Set environment variables and run

## 📊 Key Benefits

- ✅ **Dynamic Extensibility**: Add agents without code changes
- ✅ **Production Ready**: Complete error handling and logging
- ✅ **Multi-Model Support**: OpenAI, Ollama, and more
- ✅ **Developer Friendly**: Comprehensive documentation
- ✅ **Observable**: Real-time agent thinking and actions
- ✅ **Modular**: Clean separation of concerns
- ✅ **Interactive**: CLI tools for testing and debugging

## 🌟 Next Steps

1. **Read Documentation**: Start with `README.md`
2. **Follow Developer Guide**: Advanced patterns in `DEVELOPER_GUIDE.md`
3. **Try Examples**: Interactive calculator and more
4. **Create Your Agent**: Use provided templates
5. **Contribute**: Add new agents and tools
6. **Deploy**: Production-ready architecture

## 📚 Documentation Hierarchy

1. **LIBRARY_OVERVIEW.md** (this file) - Complete project overview
2. **README.md** - Main library documentation and getting started
3. **DEVELOPER_GUIDE.md** - Advanced patterns and production practices  
4. **QUICK_REFERENCE.md** - Code snippets and quick lookups
5. **getting_started.py** - Automated setup verification and guidance

---

🤖 **L1Agent**: Building the future of multi-agent systems, one agent at a time.
