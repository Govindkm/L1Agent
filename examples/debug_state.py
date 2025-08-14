#!/usr/bin/env python3
"""
Debug Test: Check why dynamic state tracking isn't working
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.messages import HumanMessage
from config.model_config import configure_ollama_model
from utils.state import register_agent, update_agent_status, log_execution_step, get_execution_summary
from examples.calculator_agent import CalculatorAgent

def debug_state_tracking():
    """Debug why state tracking shows 0 agents/tools"""
    
    print("🔍 DEBUG: State Tracking")
    print("=" * 40)
    
    # Configure model
    configure_ollama_model("llama3:latest")
    
    # Create state
    state = {
        "messages": [HumanMessage(content="What is 5 + 3?")],
        "agent_data_json": "{}",
        "tool_data_json": "{}",
        "execution_history": [],
        "task_status": "active"
    }
    
    print("📊 Initial state:")
    summary = get_execution_summary(state)
    print(f"  Agents: {len(summary.get('agents', {}))}")
    print(f"  Tools: {len(summary.get('tools', {}))}")
    print(f"  Steps: {len(summary.get('execution_steps', []))}")
    
    # Manually call state functions
    print("\n🔧 Manually registering agent...")
    register_agent(state, "calculator_agent", "active")
    
    print("📊 After manual registration:")
    summary = get_execution_summary(state)
    print(f"  Agents: {len(summary.get('agents', {}))}")
    print(f"  Tools: {len(summary.get('tools', {}))}")
    print(f"  Steps: {len(summary.get('execution_steps', []))}")
    
    # Check what's in the state
    print(f"\n🔍 Raw state inspection:")
    print(f"  agent_data_json: {state['agent_data_json']}")
    print(f"  tool_data_json: {state['tool_data_json']}")
    print(f"  execution_history length: {len(state['execution_history'])}")
    
    # Try running the calculator agent
    print("\n🧮 Running calculator agent...")
    calc_agent = CalculatorAgent()
    result = calc_agent.process(state)
    
    print(f"\n📊 After calculator execution:")
    summary = get_execution_summary(state)
    print(f"  Agents: {len(summary.get('agents', {}))}")
    print(f"  Tools: {len(summary.get('tools', {}))}")
    print(f"  Steps: {len(summary.get('execution_steps', []))}")
    
    print(f"\n🔍 Final raw state:")
    print(f"  agent_data_json: {state['agent_data_json']}")
    print(f"  tool_data_json: {state['tool_data_json']}")
    print(f"  execution_history length: {len(state['execution_history'])}")
    
    if state['execution_history']:
        print("  Execution history entries:")
        for i, entry in enumerate(state['execution_history']):
            print(f"    {i+1}: {entry}")

if __name__ == "__main__":
    debug_state_tracking()
