# Interactive Calculator Agent 🧮

A user-friendly interface to interact with the calculator agent using natural language and mathematical expressions.

## Features ✨

- **Natural Language Processing**: Ask questions like "What is 25 plus 17?"
- **Mathematical Expression Parsing**: Handle complex expressions with parentheses
- **Real-time Agent Thinking**: See how the agent processes your requests
- **Multiple Input Formats**: Support for both mathematical notation and natural language
- **Local Model**: Uses Ollama (no API key required)
- **Interactive & Batch Modes**: Choose your preferred interaction style

## Quick Start 🚀

### Prerequisites

1. **Install Ollama**:
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ollama serve
   ```

2. **Pull the model**:
   ```bash
   ollama pull llama3
   ```

### Usage

#### Interactive Mode (Default)
```bash
python examples/interactive_calculator.py
```
Enter calculations interactively and see real-time responses.

#### Single Expression Mode
```bash
python examples/interactive_calculator.py -e "25 + 17"
python examples/interactive_calculator.py --expression "What is 100 / 4?"
```

#### Batch Test Mode
```bash
python examples/interactive_calculator.py --batch
```
Runs predefined test cases to demonstrate functionality.

## Example Calculations 💡

### Basic Operations
- `15 + 25`
- `100 - 30`
- `6 * 7`
- `84 / 4`

### Complex Expressions
- `(5 + 3) * 2`
- `100 / (2 + 3)`
- `2 * 3 + 4 * 5`

### Natural Language
- "What is 25 plus 17?"
- "Calculate the sum of 8 and 12"
- "Compute (2 + 3) times 4"

## Interactive Commands 🎯

While in interactive mode:
- Type any mathematical expression to calculate
- Type `help` for examples and guidance
- Type `quit`, `exit`, or `q` to stop
- Use Ctrl+C to interrupt

## Sample Session 📝

```
🧮 Enter calculation: What is 42 * 7 + 18?
🚀 Starting calculation...

🤖 Calculator Agent Response:
   Here's your calculation result:

42 * 7 + 18 = The result is: 312

🧠 Agent Thinking Process:
1. 💭 Received calculation task from orchestrator
   🎯 Action: Analyzing request to extract mathematical expression
2. 💭 Extracted expression: 42 * 7 + 18
   🎯 Action: Performing calculation

📊 Execution Summary:
• Agents involved: 1
• Tools used: 1
• Execution steps: 2
```

## Technical Details 🔧

### Architecture
- **Agent**: CalculatorAgent with natural language processing
- **Model**: Ollama llama3 (local execution)
- **State Management**: Dynamic state tracking
- **Logging**: Comprehensive execution logging

### Error Handling
- Invalid expressions are handled gracefully
- Non-mathematical queries receive helpful responses
- Network and model errors are caught and reported

### Logging
All interactions are logged to `agent_logs.log` with:
- Agent thinking process
- Mathematical expressions extracted
- Calculation results
- Execution timestamps

## Troubleshooting 🔍

### Common Issues

1. **"Model not found" error**:
   ```bash
   ollama pull llama3
   ```

2. **"Connection refused" error**:
   ```bash
   ollama serve
   ```

3. **Import errors**:
   - Ensure you're in the project root directory
   - Check that the virtual environment is activated

### Getting Help

- Use the `help` command in interactive mode
- Check the batch tests: `--batch`
- Review the log file: `agent_logs.log`

## Advanced Usage 🎓

### Custom Expressions
The calculator handles various mathematical operations:
- Basic arithmetic: `+`, `-`, `*`, `/`
- Parentheses for grouping: `(2 + 3) * 4`
- Order of operations: `2 + 3 * 4` = 14

### Integration with Main System
This calculator agent demonstrates how to:
- Add new agents to the dynamic state system
- Handle natural language processing
- Integrate with LangGraph workflows
- Implement comprehensive logging

## Contributing 🤝

This calculator agent serves as an example of how to extend the multi-agent system. To add your own agents:

1. Create a new agent class inheriting from `BaseAgent`
2. Implement the `process()` method
3. Use the dynamic state functions for tracking
4. Test with both unit tests and interactive interfaces

Happy calculating! 🎉
