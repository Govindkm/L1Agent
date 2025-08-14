#!/usr/bin/env python3
"""
Interactive Calculator Demo Script
==================================

This script demonstrates how to use the interactive calculator.
It shows what the interactive mode would look like.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def show_interactive_demo():
    """Show what the interactive mode looks like"""
    print("🎯 INTERACTIVE CALCULATOR DEMO")
    print("=" * 60)
    print()
    print("This is what the interactive mode looks like:")
    print()
    print("🧮 INTERACTIVE CALCULATOR AGENT")
    print("=" * 50)
    print("Initializing system...")
    print("🔧 Configuring Ollama model...")
    print("✅ Model configured successfully!")
    print("✅ Calculator agent ready!")
    print()
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
    
    # Simulate some interactions
    interactions = [
        ("15 + 25", "Here's your calculation result:\n\n15 + 25 = The result is: 40"),
        ("What is 100 / 4?", "Here's your calculation result:\n\n100 / 4 = The result is: 25.0"),
        ("help", "[Shows help with examples]"),
        ("Hello there", "I'd be happy to help with calculations! Could you please provide a mathematical expression?"),
        ("quit", "👋 Thanks for using the Calculator Agent!")
    ]
    
    for user_input, response in interactions:
        print(f"🧮 Enter calculation: {user_input}")
        if user_input == "help":
            print(response)
        elif user_input == "quit":
            print(f"\n{response}")
            break
        else:
            print("🚀 Starting calculation...")
            print(f"🤖 Calculator Agent Response:\n   {response}")
            print("\n🧠 Agent Thinking Process:")
            print("1. 💭 Received calculation task from orchestrator")
            print("   🎯 Action: Analyzing request to extract mathematical expression")
            print("2. 💭 Extracted expression: [expression]")
            print("   🎯 Action: Performing calculation")
        print("\n" + "⏱️ " * 20)
        print()

def show_usage_examples():
    """Show different ways to use the calculator"""
    print("\n📚 HOW TO USE THE INTERACTIVE CALCULATOR")
    print("=" * 60)
    print()
    print("🔧 INSTALLATION & SETUP:")
    print("1. Make sure Ollama is installed and running:")
    print("   curl -fsSL https://ollama.ai/install.sh | sh")
    print("   ollama serve")
    print()
    print("2. Pull the required model:")
    print("   ollama pull llama3")
    print()
    print("3. Run the calculator:")
    print(f"   python {os.path.basename(__file__)}")
    print()
    
    print("🚀 USAGE MODES:")
    print()
    print("1. Interactive Mode (default):")
    print("   python examples/interactive_calculator.py")
    print("   # Enter calculations interactively")
    print()
    print("2. Single Expression Mode:")
    print("   python examples/interactive_calculator.py -e \"25 + 17\"")
    print("   python examples/interactive_calculator.py --expression \"What is 100 / 4?\"")
    print()
    print("3. Batch Test Mode:")
    print("   python examples/interactive_calculator.py --batch")
    print("   # Runs predefined test cases")
    print()
    
    print("💡 EXAMPLE CALCULATIONS:")
    print()
    examples = [
        "Basic: 15 + 25, 100 - 30, 6 * 7, 84 / 4",
        "Complex: (5 + 3) * 2, 100 / (2 + 3), 2 * 3 + 4 * 5",
        "Natural language: 'What is 25 plus 17?'",
        "Word problems: 'Calculate the sum of 8 and 12'"
    ]
    
    for example in examples:
        print(f"  • {example}")
    print()
    
    print("🎯 FEATURES:")
    print("  ✅ Natural language processing")
    print("  ✅ Mathematical expression parsing")
    print("  ✅ Real-time agent thinking display")
    print("  ✅ Execution tracking and logging")
    print("  ✅ Error handling and recovery")
    print("  ✅ Multiple input formats")
    print("  ✅ Local model (no API key required)")

def main():
    """Main demo function"""
    show_interactive_demo()
    show_usage_examples()
    
    print("\n🚀 READY TO TRY IT?")
    print("=" * 60)
    print("Run one of these commands:")
    print()
    print("# Interactive mode:")
    print("python examples/interactive_calculator.py")
    print()
    print("# Quick calculation:")
    print("python examples/interactive_calculator.py -e \"42 * 7 + 18\"")
    print()
    print("# Run tests:")
    print("python examples/interactive_calculator.py --batch")
    print()
    print("🎉 Happy calculating!")

if __name__ == "__main__":
    main()
