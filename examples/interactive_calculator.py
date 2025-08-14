#!/usr/bin/env python3
"""
Interactive Calculator Agent Demo
=================================

A user-friendly interface to interact with the calculator agent.
Users can input mathematical expressions and see the agent's thinking process.
"""

import sys
import os
# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END

# Import system components
from config.model_config import configure_ollama_model, get_model
from utils.state import (
    MultiAgentState, 
    register_agent, 
    update_agent_status, 
    register_tool, 
    update_tool_data, 
    log_execution_step,
    get_execution_summary
)
from utils import setup_logging, get_observer
from examples.calculator_agent import CalculatorAgent

class InteractiveCalculator:
    """Interactive calculator interface using the calculator agent"""
    
    def __init__(self):
        """Initialize the interactive calculator"""
        print("🧮 INTERACTIVE CALCULATOR AGENT")
        print("=" * 50)
        print("Initializing system...")
        
        # Configure Ollama model
        print("🔧 Configuring Ollama model...")
        try:
            configure_ollama_model("llama3:latest")
            print("✅ Model configured successfully!")
        except Exception as e:
            print(f"❌ Model configuration failed: {e}")
            print("💡 Make sure Ollama is running: 'ollama serve'")
            sys.exit(1)
        
        # Setup logging
        setup_logging(log_level="INFO")
        self.observer = get_observer()
        
        # Initialize calculator agent
        self.calculator_agent = CalculatorAgent()
        
        # Build graph
        self.graph = self._build_calculator_graph()
        print("✅ Calculator agent ready!")
        print()
    
    def _build_calculator_graph(self) -> StateGraph:
        """Build a simple graph with just the calculator agent"""
        builder = StateGraph(MultiAgentState)
        
        # Add calculator node
        builder.add_node("calculator", self.calculator_agent.process)
        
        # Simple flow: START -> calculator -> END
        builder.add_edge(START, "calculator") 
        builder.add_edge("calculator", END)
        
        return builder.compile()
    
    def process_calculation(self, user_input: str) -> Dict[str, Any]:
        """Process a calculation request from the user"""
        print(f"\n{'='*60}")
        print(f"🧮 Processing: {user_input}")
        print('='*60)
        
        # Clear previous observations
        self.observer.clear_observations()
        
        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "current_task": f"calculate: {user_input}",
            "task_status": "active",
            "agent_data_json": "{}",
            "tool_data_json": "{}", 
            "custom_data_json": "{}",
            "execution_history": []
        }
        
        try:
            # Run the graph
            print("🚀 Starting calculation...")
            final_state = self.graph.invoke(initial_state)
            
            # Extract the response
            response_message = None
            if final_state.get("messages"):
                for msg in final_state["messages"]:
                    if isinstance(msg, AIMessage):
                        response_message = msg
                        break
            
            if response_message:
                print(f"\n🤖 Calculator Agent Response:")
                print(f"   {response_message.content}")
            else:
                print("\n❌ No response generated")
            
            # Show agent thinking process
            self._show_thinking_process()
            
            # Show execution summary
            self._show_execution_summary(final_state)
            
            return final_state
            
        except Exception as e:
            print(f"\n❌ Error during calculation: {e}")
            print("💡 This might be due to:")
            print("   • Ollama not running (try: ollama serve)")
            print("   • Model not available (try: ollama pull llama3)")
            print("   • Network connectivity issues")
            return {}
    
    def _show_thinking_process(self):
        """Display the agent's thinking process"""
        observations = self.observer.get_observations()
        
        if observations:
            print(f"\n🧠 Agent Thinking Process:")
            print("-" * 40)
            for i, obs in enumerate(observations, 1):
                print(f"{i}. 💭 {obs['thought']}")
                if obs.get('action'):
                    print(f"   🎯 Action: {obs['action']}")
        else:
            print("\n🤔 No thinking process recorded")
    
    def _show_execution_summary(self, state: Dict[str, Any]):
        """Show execution summary"""
        summary = get_execution_summary(state)
        
        print(f"\n📊 Execution Summary:")
        print("-" * 40)
        print(f"• Agents involved: {len(summary.get('agents', {}))}")
        print(f"• Tools used: {len(summary.get('tools', {}))}")
        print(f"• Execution steps: {len(summary.get('execution_steps', []))}")
        
        # Show detailed agent info
        if summary.get('agents'):
            for agent_name, agent_info in summary['agents'].items():
                status = agent_info.get('status', 'unknown')
                action = agent_info.get('last_action', 'No action')
                print(f"• {agent_name}: {status} - {action}")
        
        # Show tool results
        if summary.get('tools'):
            for tool_name, tool_info in summary['tools'].items():
                result = tool_info.get('result', 'No result')
                status = tool_info.get('status', 'unknown')
                print(f"• {tool_name}: {status} -> {result}")
    
    def run_interactive_mode(self):
        """Run in interactive mode, getting input from user"""
        print("🎯 INTERACTIVE MODE")
        print("=" * 50)
        print("Enter mathematical expressions to calculate.")
        print("Examples:")
        print("  • What is 25 + 17?")
        print("  • Calculate 100 / 4 + 15")
        print("  • (2 + 3) * (4 + 6)")
        print("  • Compute the square root of 144")
        print()
        print("Type 'quit', 'exit', or 'q' to stop.")
        print("Type 'help' for more examples.")
        print()
        
        while True:
            try:
                # Get user input
                user_input = input("🧮 Enter calculation: ").strip()
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Thanks for using the Calculator Agent!")
                    break
                
                if user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                if not user_input:
                    print("⚠️  Please enter a calculation or 'quit' to exit.")
                    continue
                
                # Process the calculation
                self.process_calculation(user_input)
                
                # Add separator for next round
                print("\n" + "⏱️ " * 20)
                
            except KeyboardInterrupt:
                print("\n\n👋 Calculator interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                print("Please try again or type 'quit' to exit.")
    
    def _show_help(self):
        """Show help with example calculations"""
        print("\n📚 CALCULATOR HELP")
        print("=" * 40)
        print("The calculator can handle various mathematical expressions:")
        print()
        print("🔢 Basic Operations:")
        print("  • Addition: 5 + 3, What is 10 plus 7?")
        print("  • Subtraction: 20 - 8, Calculate 50 minus 15")
        print("  • Multiplication: 6 * 4, What's 12 times 5?")
        print("  • Division: 100 / 4, Divide 50 by 2")
        print()
        print("🧮 Complex Expressions:")
        print("  • Parentheses: (2 + 3) * 4")
        print("  • Order of operations: 5 + 3 * 2")
        print("  • Mixed operations: (100 - 25) / 5 + 10")
        print()
        print("💬 Natural Language:")
        print("  • 'What is the result of 15 plus 25?'")
        print("  • 'Calculate the sum of 8 and 12'")
        print("  • 'Compute 3 times 7 plus 4'")
        print()
        print("⚠️  Note: For best results, use standard mathematical notation")
        print("   (+, -, *, /) rather than words when possible.")
        print()

def run_batch_tests():
    """Run some predefined test calculations"""
    print("🧪 BATCH TEST MODE")
    print("=" * 50)
    
    calc = InteractiveCalculator()
    
    test_cases = [
        "15 + 25",
        "What is 100 divided by 4?",
        "Calculate (5 + 3) * 2",
        "50 - 17 + 8",
        "What's the result of 2 * 3 * 4?",
        "Hello there"  # Non-math test
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}/{len(test_cases)}: {test_case}")
        calc.process_calculation(test_case)
        
        if i < len(test_cases):
            print("\n" + "⏱️ " * 20)
            print("Moving to next test...")
    
    print(f"\n🎉 Batch testing completed! ({len(test_cases)} tests)")

def main():
    """Main function to run the interactive calculator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Interactive Calculator Agent Demo')
    parser.add_argument('--batch', action='store_true', 
                       help='Run batch tests instead of interactive mode')
    parser.add_argument('--expression', '-e', type=str,
                       help='Calculate a single expression and exit')
    
    args = parser.parse_args()
    
    if args.batch:
        run_batch_tests()
    elif args.expression:
        calc = InteractiveCalculator()
        calc.process_calculation(args.expression)
    else:
        calc = InteractiveCalculator()
        calc.run_interactive_mode()

if __name__ == "__main__":
    main()
