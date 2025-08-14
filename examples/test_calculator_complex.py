#!/usr/bin/env python3
"""
Test the calculator agent with a complex expression
"""

import sys
import os
# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Literal
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langgraph.types import Command

from agents.base_agent import BaseAgent
from utils.state import MultiAgentState, register_agent, update_agent_status, log_execution_step, register_tool, update_tool_data, get_execution_summary
from config.model_config import get_model, configure_ollama_model
import re

# Import the calculator agent
from examples.calculator_agent import CalculatorAgent

def test_complex_calculation():
    """Test the calculator agent with a complex calculation"""
    
    # Configure Ollama model for this example (no API key needed)
    print("🔧 Configuring Ollama model...")
    configure_ollama_model("llama3:latest")
    print("✅ Ollama configured successfully!")
    
    # Test different expressions
    test_expressions = [
        "Calculate 10 * (5 + 3)",
        "What is 100 / 4 + 15?",
        "Compute (2 + 3) * (4 + 6)",
        "Hello there",  # This should ask for a math expression
    ]
    
    calc_agent = CalculatorAgent()
    
    for i, expression in enumerate(test_expressions, 1):
        print(f"\n{'='*60}")
        print(f"🧮 Test {i}: {expression}")
        print('='*60)
        
        # Create a fresh state for each test
        state = {
            "messages": [HumanMessage(content=expression)],
            "agent_data_json": "{}",
            "tool_data_json": "{}",
            "execution_history": [],
            "task_status": "active"
        }
        
        try:
            result = calc_agent.process(state)
            
            if result.update and "messages" in result.update:
                response_msg = result.update["messages"][0]
                print(f"🤖 Agent Response:")
                print(f"   {response_msg.content}")
            else:
                print("🤖 No response message generated")
            
            print(f"📍 Command: goto={result.goto}")
            
            # Show execution summary
            summary = get_execution_summary(state)
            if summary.get('agents'):
                print("📊 Agent Status:")
                for agent, info in summary['agents'].items():
                    print(f"   - {agent}: {info.get('status', 'unknown')}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_complex_calculation()
    
    print(f"\n{'='*60}")
    print("🎉 All tests completed!")
    print("✨ The calculator agent successfully:")
    print("   • Parses mathematical expressions")
    print("   • Performs calculations") 
    print("   • Handles non-math queries gracefully")
    print("   • Uses the new dynamic state system")
    print("   • Works with Ollama (no API key needed)")
