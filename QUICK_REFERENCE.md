# Quick Reference Guide 📚

Common patterns and code snippets for the L1Agent library.

## 🚀 Getting Started

### Basic Agent Template

```python
from typing import Literal
from langchain_core.messages import AIMessage
from langgraph.types import Command

from agents.base_agent import BaseAgent
from utils.state import register_agent, update_agent_status, log_execution_step
from config.model_config import get_model

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__("MyAgent")
    
    def process(self, state: MultiAgentState) -> Command[Literal["__end__"]]:
        # 1. Register agent
        register_agent(state, "my_agent", "working")
        log_execution_step(state, "my_agent", "started")
        
        # 2. Log thinking
        self.log_thinking("Processing user request", "Analyzing input")
        
        # 3. Get input
        user_input = state["messages"][-1].content
        
        # 4. Process with AI
        model = get_model()
        response = model.invoke(f"Process this: {user_input}")
        
        # 5. Update state
        update_agent_status(state, "my_agent", "completed", result=response.content)
        log_execution_step(state, "my_agent", "completed")
        
        # 6. Return result
        return Command(
            goto="__end__",
            update={"messages": [AIMessage(content=response.content, name="my_agent")]}
        )
```

## 🔧 Common Code Snippets

### Configure Models

```python
# Ollama (Local)
from config.model_config import configure_ollama_model
configure_ollama_model("llama3:latest")

# OpenAI (Cloud)
from config.model_config import configure_openai_model
configure_openai_model("gpt-4o-mini", api_key="your-key")
```

### State Management

```python
from utils.state import *

# Agent operations
register_agent(state, "agent_name", "status")
update_agent_status(state, "agent_name", "completed", result="data")

# Tool operations
register_tool(state, "tool_name")
update_tool_data(state, "tool_name", result="output", status="success")

# Execution tracking
log_execution_step(state, "agent_name", "action", {"key": "value"})

# Custom data
set_custom_data(state, "my_key", {"data": "value"})
data = get_custom_data(state, "my_key", default={})

# Get summary
summary = get_execution_summary(state)
```

### Error Handling

```python
try:
    result = risky_operation()
    update_agent_status(state, "agent", "completed", result=result)
except Exception as e:
    self.log_thinking(f"Error: {e}", "Handling gracefully")
    update_agent_status(state, "agent", "failed", error=str(e))
    return Command(goto="__end__", update={"messages": [error_response]})
```

### Testing Setup

```python
def create_test_state(message="test"):
    return {
        "messages": [HumanMessage(content=message)],
        "agent_data_json": "{}",
        "tool_data_json": "{}",
        "execution_history": [],
        "task_status": "active"
    }

# Test agent
agent = MyAgent()
result = agent.process(create_test_state("Hello"))
```

## 🎯 Quick Commands

### Run Examples

```bash
# Interactive calculator
python examples/interactive_calculator.py

# Single calculation
python examples/interactive_calculator.py -e "25 + 17"

# Batch tests
python examples/interactive_calculator.py --batch

# System test
python -c "from system import MultiAgentSystem; s=MultiAgentSystem(); print(s.process_request('Hello'))"
```

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Setup Ollama
ollama serve
ollama pull llama3

# Run tests
python -m pytest tests/

# Check logs
tail -f agent_logs.log
```

## 📊 State Structure

```python
state = {
    "messages": [HumanMessage, AIMessage, ...],        # LangChain messages
    "agent_data_json": "{}",                           # Agent status/results
    "tool_data_json": "{}",                            # Tool usage/results  
    "execution_history": [],                           # Timestamped steps
    "custom_data_json": "{}",                          # Your custom data
    "task_status": "active|completed|failed"           # Overall status
}
```

## 🔍 Debugging

```python
# Debug state
from utils.state import get_execution_summary
summary = get_execution_summary(state)
print(f"Agents: {summary['agents']}")
print(f"Tools: {summary['tools']}")
print(f"Steps: {len(summary['execution_steps'])}")

# Check logs
from utils import get_observer
observer = get_observer()
for obs in observer.get_observations():
    print(f"{obs['agent']}: {obs['thought']}")

# Check model
from config.model_config import get_model_config
config = get_model_config()
print(f"Using: {config.provider.value} - {config.model_name}")
```

## 🛠️ Useful Patterns

### Conditional Processing

```python
def process(self, state):
    user_input = state["messages"][-1].content.lower()
    
    if "weather" in user_input:
        return self.handle_weather(state)
    elif "email" in user_input:
        return self.handle_email(state)
    else:
        return self.handle_general(state)
```

### Multi-step Processing

```python
def process(self, state):
    # Step 1
    log_execution_step(state, "agent", "step_1")
    data = self.step_1(state)
    
    # Step 2
    log_execution_step(state, "agent", "step_2") 
    result = self.step_2(data)
    
    # Step 3
    log_execution_step(state, "agent", "step_3")
    final = self.step_3(result)
    
    return Command(goto="__end__", update={"messages": [final]})
```

### Tool Usage

```python
def process(self, state):
    # Register tool
    register_tool(state, "my_tool")
    
    # Use tool
    tool_result = self.use_tool(input_data)
    
    # Update tool state
    update_tool_data(state, "my_tool", 
                    result=tool_result,
                    metadata={"input": input_data},
                    status="success")
    
    return Command(goto="__end__")
```

### Caching

```python
def process(self, state):
    cache_key = f"cache_{hash(user_input)}"
    
    # Check cache
    cached = get_custom_data(state, cache_key)
    if cached and not self.is_expired(cached):
        return Command(goto="__end__", update={"messages": [cached["result"]]})
    
    # Process and cache
    result = expensive_operation()
    set_custom_data(state, cache_key, {
        "result": result,
        "timestamp": time.time()
    })
    
    return Command(goto="__end__", update={"messages": [result]})
```

## 📋 Checklists

### New Agent Checklist

- [ ] Inherit from `BaseAgent`
- [ ] Implement `process()` method
- [ ] Register agent with `register_agent()`
- [ ] Update status with `update_agent_status()`
- [ ] Log execution steps
- [ ] Handle errors gracefully
- [ ] Add thinking logs
- [ ] Write unit tests
- [ ] Add to registry (optional)

### Production Checklist

- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Performance optimized
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Resource limits set
- [ ] Monitoring enabled
- [ ] Health checks added

### Troubleshooting Checklist

- [ ] Check model configuration
- [ ] Verify Ollama is running
- [ ] Check import paths
- [ ] Review error logs
- [ ] Validate state structure
- [ ] Test with simple input
- [ ] Check resource usage

---

*Keep this guide handy for quick reference while developing with L1Agent!*
