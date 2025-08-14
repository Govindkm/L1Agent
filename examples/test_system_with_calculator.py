#!/usr/bin/env python3
"""
Comprehensive Test: Calculator Agent Integration with Main System
================================================================

This test demonstrates:
1. Full system integration with calculator agent
2. Dynamic state logging and tracking  
3. Agent thinking and action visibility
4. Tool usage tracking
5. Complete execution flow
"""

import sys
import os
# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

# Import system components
from config.model_config import configure_ollama_model, get_model
from utils.state import (
    MultiAgentState, 
    register_agent, 
    update_agent_status, 
    register_tool, 
    update_tool_data, 
    log_execution_step,
    get_execution_summary,
    to_dict
)
from utils import setup_logging, get_observer
from examples.calculator_agent import CalculatorAgent

class SystemTester:
    """Test the full system with calculator agent integration"""
    
    def __init__(self):
        """Initialize the test system"""
        # Configure Ollama model
        print("🔧 Configuring Ollama model...")
        configure_ollama_model("llama3:latest")
        print("✅ Model configured successfully!")
        
        # Setup logging
        setup_logging(log_level="INFO")
        self.observer = get_observer()
        
        # Initialize calculator agent
        self.calculator_agent = CalculatorAgent()
        
        # Build graph
        self.graph = self._build_test_graph()
    
    def _build_test_graph(self) -> StateGraph:
        """Build a test graph with calculator agent"""
        print("🏗️  Building test graph...")
        
        builder = StateGraph(MultiAgentState)
        
        # Add calculator node
        builder.add_node("calculator", self.calculator_agent.process)
        
        # Simple flow: START -> calculator -> END
        builder.add_edge(START, "calculator") 
        builder.add_edge("calculator", END)
        
        graph = builder.compile()
        print("✅ Test graph built successfully!")
        
        return graph
    
    def test_calculator_integration(self, expression: str) -> Dict[str, Any]:
        """Test calculator agent with full logging"""
        print(f"\n{'='*60}")
        print(f"🧮 Testing Calculator Integration")
        print(f"📝 Expression: {expression}")
        print('='*60)
        
        # Clear previous observations
        self.observer.clear_observations()
        
        # Create initial state with proper structure
        initial_state = {
            "messages": [HumanMessage(content=expression)],
            "current_task": f"calculate_{expression}",
            "task_status": "active",
            "agent_data_json": "{}",
            "tool_data_json": "{}", 
            "custom_data_json": "{}",
            "execution_history": []
        }
        
        print("🚀 Starting execution...")
        
        try:
            # Run the graph
            final_state = self.graph.invoke(initial_state)
            
            print("\n📊 EXECUTION RESULTS:")
            print("-" * 40)
            
            # Show final messages
            if final_state.get("messages"):
                for i, msg in enumerate(final_state["messages"]):
                    if isinstance(msg, AIMessage):
                        print(f"🤖 Agent Response {i+1}:")
                        print(f"   {msg.content}")
                        print()
            
            # Show execution summary
            summary = get_execution_summary(final_state)
            print("📈 EXECUTION SUMMARY:")
            print("-" * 40)
            print(f"• Total Agents: {len(summary.get('agents', {}))}")
            print(f"• Total Tools: {len(summary.get('tools', {}))}")
            print(f"• Execution Steps: {len(summary.get('execution_steps', []))}")
            
            # Show agent details
            if summary.get('agents'):
                print("\n🤖 AGENT STATUS:")
                for agent_name, agent_info in summary['agents'].items():
                    status = agent_info.get('status', 'unknown')
                    result = agent_info.get('result', 'No result')
                    action = agent_info.get('action', 'No action')
                    print(f"  • {agent_name}:")
                    print(f"    - Status: {status}")
                    print(f"    - Action: {action}")
                    print(f"    - Result: {result}")
            
            # Show tool details  
            if summary.get('tools'):
                print("\n🔧 TOOL USAGE:")
                for tool_name, tool_info in summary['tools'].items():
                    status = tool_info.get('status', 'unknown')
                    result = tool_info.get('result', 'No result')
                    metadata = tool_info.get('metadata', {})
                    print(f"  • {tool_name}:")
                    print(f"    - Status: {status}")
                    print(f"    - Result: {result}")
                    if metadata:
                        print(f"    - Expression: {metadata.get('expression', 'N/A')}")
            
            # Show execution steps
            if summary.get('execution_steps'):
                print("\n📝 EXECUTION TIMELINE:")
                for step in summary['execution_steps']:
                    timestamp = step.get('timestamp', 'Unknown time')
                    agent = step.get('agent', 'Unknown agent')
                    action = step.get('action', 'Unknown action')
                    details = step.get('details', {})
                    print(f"  • {timestamp} - {agent}: {action}")
                    if details:
                        for key, value in details.items():
                            print(f"    {key}: {value}")
            
            # Show observer logs
            print("\n👁️  OBSERVER LOGS:")
            print("-" * 40)
            observations = self.observer.get_observations()
            for obs in observations:
                print(f"🕐 {obs['timestamp']}")
                print(f"🤖 {obs['agent']}: {obs['thought']}")
                if obs.get('action'):
                    print(f"🎯 Action: {obs['action']}")
                print()
            
            print(f"{'='*60}")
            print("✅ Test completed successfully!")
            
            return final_state
            
        except Exception as e:
            print(f"\n❌ Error during execution: {e}")
            import traceback
            traceback.print_exc()
            return {}

def main():
    """Run comprehensive system tests"""
    print("🚀 CALCULATOR AGENT SYSTEM INTEGRATION TEST")
    print("=" * 60)
    
    # Initialize tester
    tester = SystemTester()
    
    # Test different scenarios
    test_cases = [
        "Calculate 25 * 4 + 10",
        "What is (100 - 25) / 5?", 
        "Compute 2^3 * 5",  # This might challenge the expression parser
        "Hello world",  # Non-math query
    ]
    
    results = []
    
    for test_case in test_cases:
        result = tester.test_calculator_integration(test_case)
        results.append(result)
        
        # Brief pause between tests
        print("\n" + "⏱️ " * 20)
        print("Moving to next test...\n")
    
    print("🎉 ALL TESTS COMPLETED!")
    print("=" * 60)
    print("📊 SUMMARY:")
    print(f"✅ Total test cases: {len(test_cases)}")
    print(f"✅ Successful executions: {len([r for r in results if r])}")
    print("\n💡 Key Features Demonstrated:")
    print("   • Dynamic state management")
    print("   • Agent registration and tracking")
    print("   • Tool integration and logging")
    print("   • Execution timeline tracking")
    print("   • Observer pattern logging")
    print("   • Error handling and recovery")
    print("   • Full system integration")

if __name__ == "__main__":
    main()
