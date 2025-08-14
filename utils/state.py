"""
State management for the multi-agent system.
Dynamic and extensible state that auto-adapts to new agents and tools.
"""

from typing import Dict, Any, Optional, Union, List, TypedDict
from dataclasses import dataclass, field
from langgraph.graph import MessagesState
import json


@dataclass
class AgentData:
    """Data structure for agent-specific information"""
    status: str = "idle"  # idle, working, completed, failed
    result: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_action: str = ""
    error: Optional[str] = None


@dataclass 
class ToolData:
    """Data structure for tool-specific information"""
    result: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_used: Optional[str] = None
    status: str = "unused"  # unused, success, failed
    error: Optional[str] = None


class MultiAgentState(MessagesState):
    """
    Enhanced state that extends MessagesState with dynamic capabilities.
    LangGraph will convert this to a dict, so we add helper functions.
    """
    
    # Core coordination fields that LangGraph will preserve
    current_task: str = ""
    task_status: str = "pending"  # pending, in_progress, completed, failed
    total_steps: int = 0
    
    # These will be stored as serialized data in the dict
    agent_data_json: str = "{}"
    tool_data_json: str = "{}"
    custom_data_json: str = "{}"
    execution_history_json: str = "[]"


# Helper functions to work with the state dict that LangGraph passes around
def register_agent(state: Dict[str, Any], agent_name: str, initial_status: str = "idle") -> None:
    """Register a new agent in the state dict"""
    agent_data = json.loads(state.get("agent_data_json", "{}"))
    if agent_name not in agent_data:
        agent_data[agent_name] = {
            "status": initial_status,
            "result": None,
            "metadata": {},
            "last_action": "",
            "error": None
        }
    state["agent_data_json"] = json.dumps(agent_data)


def update_agent_status(state: Dict[str, Any], agent_name: str, status: str, 
                       result: Any = None, metadata: Dict[str, Any] = None, 
                       action: str = "", error: str = None) -> None:
    """Update agent status and data in state dict"""
    register_agent(state, agent_name)
    agent_data = json.loads(state.get("agent_data_json", "{}"))
    
    agent = agent_data[agent_name]
    agent["status"] = status
    if result is not None:
        agent["result"] = result
    if metadata:
        agent["metadata"].update(metadata)
    if action:
        agent["last_action"] = action
    if error:
        agent["error"] = error
    
    state["agent_data_json"] = json.dumps(agent_data)


def register_tool(state: Dict[str, Any], tool_name: str) -> None:
    """Register a new tool in the state dict"""
    tool_data = json.loads(state.get("tool_data_json", "{}"))
    if tool_name not in tool_data:
        tool_data[tool_name] = {
            "result": None,
            "metadata": {},
            "last_used": None,
            "status": "unused",
            "error": None
        }
    state["tool_data_json"] = json.dumps(tool_data)


def update_tool_data(state: Dict[str, Any], tool_name: str, result: Any = None,
                    metadata: Dict[str, Any] = None, status: str = None,
                    error: str = None) -> None:
    """Update tool data and status in state dict"""
    register_tool(state, tool_name)
    tool_data = json.loads(state.get("tool_data_json", "{}"))
    
    tool = tool_data[tool_name]
    if result is not None:
        tool["result"] = result
    if metadata:
        tool["metadata"].update(metadata)
    if status:
        tool["status"] = status
    if error:
        tool["error"] = error
    tool["last_used"] = str(state.get("total_steps", 0))
    
    state["tool_data_json"] = json.dumps(tool_data)


def log_execution_step(state: Dict[str, Any], agent: str, action: str, 
                      details: Dict[str, Any] = None) -> None:
    """Log an execution step for tracking"""
    # Add timestamp
    from datetime import datetime
    
    step = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent,
        "action": action,
        "details": details or {}
    }
    
    # Handle both list-based and JSON-based execution history
    if "execution_history" in state and isinstance(state["execution_history"], list):
        # Direct list format (preferred)
        state["execution_history"].append(step)
    else:
        # JSON format (backward compatibility)
        execution_history = json.loads(state.get("execution_history_json", "[]"))
        execution_history.append(step)
        state["execution_history_json"] = json.dumps(execution_history)
        
        # Also ensure execution_history list exists
        if "execution_history" not in state:
            state["execution_history"] = []
        state["execution_history"].append(step)


def set_custom_data(state: Dict[str, Any], key: str, value: Any) -> None:
    """Set custom data that doesn't fit standard categories"""
    custom_data = json.loads(state.get("custom_data_json", "{}"))
    custom_data[key] = value
    state["custom_data_json"] = json.dumps(custom_data)


def get_custom_data(state: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Get custom data with optional default"""
    custom_data = json.loads(state.get("custom_data_json", "{}"))
    return custom_data.get(key, default)


def get_agent_result(state: Dict[str, Any], agent_name: str) -> Any:
    """Get result from specific agent"""
    agent_data = json.loads(state.get("agent_data_json", "{}"))
    return agent_data.get(agent_name, {}).get("result")


def get_tool_result(state: Dict[str, Any], tool_name: str) -> Any:
    """Get result from specific tool"""
    tool_data = json.loads(state.get("tool_data_json", "{}"))
    return tool_data.get(tool_name, {}).get("result")


def get_execution_summary(state: Dict[str, Any]) -> Dict[str, Any]:
    """Get summary of execution state"""
    agent_data = json.loads(state.get("agent_data_json", "{}"))
    tool_data = json.loads(state.get("tool_data_json", "{}"))
    execution_history = state.get("execution_history", [])
    
    return {
        "task_status": state.get("task_status", "unknown"),
        "total_steps": len(execution_history),
        "agents": agent_data,  # Full agent data
        "tools": tool_data,    # Full tool data
        "execution_steps": execution_history,  # Full execution history
        "agents_involved": list(agent_data.keys()),  # Backward compatibility
        "tools_used": [name for name, tool in tool_data.items() if tool.get("status") != "unused"],
        "current_task": state.get("current_task", "")
    }


# Backward compatibility functions
def get_weather_data(state: Dict[str, Any]) -> Any:
    """Backward compatibility for weather data"""
    return get_tool_result(state, "weather")


def set_weather_data(state: Dict[str, Any], value: Any) -> None:
    """Backward compatibility setter for weather data"""
    update_tool_data(state, "weather", result=value, status="success" if value else "unused")


def get_email_content(state: Dict[str, Any]) -> str:
    """Backward compatibility for email content"""
    return get_tool_result(state, "email") or ""


def set_email_content(state: Dict[str, Any], value: str) -> None:
    """Backward compatibility setter for email content"""
    update_tool_data(state, "email", result=value, status="success" if value else "unused")


def get_email_sent(state: Dict[str, Any]) -> bool:
    """Backward compatibility for email sent status"""
    tool_data = json.loads(state.get("tool_data_json", "{}"))
    email_tool = tool_data.get("email", {})
    return email_tool.get("metadata", {}).get("sent", False)


def set_email_sent(state: Dict[str, Any], value: bool) -> None:
    """Backward compatibility setter for email sent status"""
    register_tool(state, "email")
    tool_data = json.loads(state.get("tool_data_json", "{}"))
    if "email" not in tool_data:
        tool_data["email"] = {"metadata": {}}
    elif "metadata" not in tool_data["email"]:
        tool_data["email"]["metadata"] = {}
    
    tool_data["email"]["metadata"]["sent"] = value
    state["tool_data_json"] = json.dumps(tool_data)


def get_recipient_email(state: Dict[str, Any]) -> str:
    """Backward compatibility for recipient email"""
    tool_data = json.loads(state.get("tool_data_json", "{}"))
    email_tool = tool_data.get("email", {})
    return email_tool.get("metadata", {}).get("recipient", "")


def set_recipient_email(state: Dict[str, Any], value: str) -> None:
    """Backward compatibility setter for recipient email"""
    register_tool(state, "email")
    tool_data = json.loads(state.get("tool_data_json", "{}"))
    if "email" not in tool_data:
        tool_data["email"] = {"metadata": {}}
    elif "metadata" not in tool_data["email"]:
        tool_data["email"]["metadata"] = {}
    
    tool_data["email"]["metadata"]["recipient"] = value
    state["tool_data_json"] = json.dumps(tool_data)


def to_dict(state: Dict[str, Any]) -> Dict[str, Any]:
    """Convert state to dictionary for serialization"""
    return {
        "current_task": state.get("current_task", ""),
        "task_status": state.get("task_status", "pending"),
        "agent_data": json.loads(state.get("agent_data_json", "{}")),
        "tool_data": json.loads(state.get("tool_data_json", "{}")),
        "custom_data": json.loads(state.get("custom_data_json", "{}")),
        "execution_history": json.loads(state.get("execution_history_json", "[]")),
        "total_steps": state.get("total_steps", 0)
    }
