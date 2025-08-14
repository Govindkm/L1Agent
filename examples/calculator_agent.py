"""
Example: Calculator Agent - Demonstrates how easy it is to add new agents
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


def calculate_expression(expression: str) -> str:
    """
    Simple calculator tool that safely evaluates mathematical expressions.
    
    Args:
        expression: Mathematical expression to evaluate
        
    Returns:
        Result of the calculation or error message
    """
    try:
        # Clean the expression - only allow numbers, operators, parentheses, and whitespace
        cleaned = re.sub(r'[^0-9+\-*/().\s]', '', expression)
        
        # Basic safety check - no double operators or empty expression
        if not cleaned or re.search(r'[+\-*/]{2,}', cleaned):
            return "Invalid mathematical expression"
        
        # Evaluate safely
        result = eval(cleaned)
        return f"The result is: {result}"
        
    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception as e:
        return f"Error: Could not calculate - {str(e)}"


class CalculatorAgent(BaseAgent):
    """
    Calculator agent that handles mathematical calculations.
    
    This demonstrates how easy it is to add new agents to the system!
    """
    
    def __init__(self):
        super().__init__("CalculatorAgent")
    
    def process(self, state: MultiAgentState) -> Command[Literal["__end__"]]:
        """
        Process mathematical calculation requests
        """
        # Register this agent in the dynamic state
        register_agent(state, "calculator_agent", "working")
        log_execution_step(state, "calculator_agent", "started_processing")
        
        self.log_thinking(
            "Received calculation task from orchestrator",
            "Analyzing request to extract mathematical expression"
        )
        
        messages = state["messages"]
        latest_message = messages[-1] if messages else None
        
        if not latest_message:
            update_agent_status(state, "calculator_agent", "failed", error="No message to process")
            return Command(goto="__end__")
        
        # Extract mathematical expression from the user's message
        expression_extraction_prompt = f"""
        Extract the mathematical expression from this request: "{latest_message.content}"
        
        Look for numbers, operators (+, -, *, /), and parentheses.
        If you find a mathematical expression, respond with just that expression.
        If no mathematical expression is found, respond with "NO_MATH_FOUND".
        
        Examples:
        "What is 5 + 3?" → "5 + 3"
        "Calculate 10 * (2 + 3)" → "10 * (2 + 3)"
        "Hello there" → "NO_MATH_FOUND"
        """
        
        try:
            model = get_model()
            expression_response = model.invoke([SystemMessage(content=expression_extraction_prompt)])
            expression = expression_response.content.strip()
            
            if expression == "NO_MATH_FOUND" or not expression:
                self.log_thinking(
                    "No mathematical expression found in request",
                    "Asking user to provide a mathematical expression"
                )
                response_text = "I'd be happy to help with calculations! Could you please provide a mathematical expression? For example: '5 + 3' or '10 * (2 + 3)'"
                response = AIMessage(
                    content=response_text,
                    name="calculator_agent"
                )
                
                # Update dynamic state
                update_agent_status(state, "calculator_agent", "completed", result=response_text,
                                        action="requested_math_expression")
                log_execution_step(state, "calculator_agent", "requested_clarification", 
                                       {"reason": "no_expression_found"})
                
            else:
                self.log_thinking(
                    f"Extracted expression: {expression}",
                    "Performing calculation"
                )
                
                # Register and use the calculator tool in dynamic state
                register_tool(state, "calculator")
                calculation_result = calculate_expression(expression)
                
                # Update tool data
                update_tool_data(state, "calculator", result=calculation_result,
                                     metadata={"expression": expression, "query_type": "calculation"},
                                     status="success")
                
                response_text = f"Here's your calculation result:\n\n{expression} = {calculation_result}"
                response = AIMessage(
                    content=response_text,
                    name="calculator_agent"
                )
                
                # Update agent status
                update_agent_status(state, "calculator_agent", "completed", result=calculation_result,
                                        action=f"calculated_{expression}")
                log_execution_step(state, "calculator_agent", "performed_calculation", {
                    "expression": expression,
                    "result": calculation_result,
                    "tool": "calculator",
                    "success": True
                })
            
            return Command(
                goto="__end__",
                update={
                    "messages": [response],
                    "task_status": "completed"
                }
            )
            
        except Exception as e:
            self.log_thinking(f"Error processing calculation: {str(e)}", "Returning error message")
            
            # Update state with error information
            update_agent_status(state, "calculator_agent", "failed", error=str(e),
                                    action="error_occurred")
            try:
                update_tool_data(state, "calculator", status="failed", error=str(e))
            except:
                pass  # Tool might not have been registered yet
            
            log_execution_step(state, "calculator_agent", "error", {"error": str(e)})
            
            error_response = AIMessage(
                content=f"I encountered an error while performing the calculation: {str(e)}",
                name="calculator_agent"
            )
            return Command(
                goto="__end__",
                update={"messages": [error_response], "task_status": "failed"}
            )


# Example of how to register and test this new agent
if __name__ == "__main__":
    # Simple test of the calculator agent
    def test_calculator_agent():
        """Test the calculator agent with a simple calculation"""
        
        # Configure Ollama model for this example (no API key needed)
        print("🔧 Configuring Ollama model...")
        try:
            configure_ollama_model("llama3:latest")
            print("✅ Ollama configured successfully!")
        except Exception as e:
            print(f"⚠️  Ollama configuration issue: {e}")
            print("💡 Make sure Ollama is installed and running: 'ollama serve'")
            print("💡 And that llama3.2 is available: 'ollama pull llama3.2'")
        
        # Create a simple state for testing
        initial_state = {
            "messages": [HumanMessage(content="What is 15 + 25?")],
            "agent_data_json": "{}",
            "tool_data_json": "{}",
            "execution_history": [],
            "task_status": "active"
        }
        
        # Create the agent
        calc_agent = CalculatorAgent()
        
        print("\n🧮 Testing Calculator Agent")
        print("=" * 50)
        print(f"Query: What is 15 + 25?")
        print()
        
        try:
            # Process the calculation
            result = calc_agent.process(initial_state)
            
            print(f"✨ Result Command: goto={result.goto}")
            if result.update and "messages" in result.update:
                response_msg = result.update["messages"][0]
                print(f"🤖 Agent Response: {response_msg.content}")
        
        except Exception as e:
            print(f"❌ Error during processing: {e}")
            print("💡 This might be because Ollama is not running or the model is not available")
            print("   Try: ollama serve (in another terminal)")
            print("   Try: ollama pull llama3.2")
            import traceback
            traceback.print_exc()
            return None
        
        print("\n" + "=" * 50)
        print("✅ Test completed!")
        
        # Show final state
        summary = get_execution_summary(initial_state)
        print("\n📊 Execution Summary:")
        print(f"   • Agents: {len(summary.get('agents', {}))}")
        print(f"   • Tools: {len(summary.get('tools', {}))}")
        print(f"   • Steps: {len(summary.get('execution_steps', []))}")
        
        if summary.get('agents'):
            print("   • Agent statuses:")
            for agent, info in summary['agents'].items():
                print(f"     - {agent}: {info.get('status', 'unknown')}")
        
        if summary.get('tools'):
            print("   • Tool results:")
            for tool, info in summary['tools'].items():
                status = info.get('status', 'unknown')
                result = info.get('result', 'No result')
                print(f"     - {tool}: {status} -> {result}")
        
        return result
    
    # Run the test
    test_result = test_calculator_agent()
    
    print("\n" + "=" * 50)
    print("🚀 Calculator Agent Example Complete!")
    print("\n💡 This demonstrates how the new dynamic state system")
    print("   automatically handles new agents without code changes!")
    print("\n🔧 Key features showcased:")
    print("   • Dynamic agent registration")
    print("   • Tool integration")
    print("   • State tracking and logging") 
    print("   • Error handling")
    print("\n� To integrate with the main system:")
    print("   • Add to utils/registry.py")
    print("   • Include in orchestrator routing")
    print("   • Deploy and enjoy!")
