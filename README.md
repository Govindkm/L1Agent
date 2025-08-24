# Multi-Agent Email System with Strands Framework

A comprehensive multi-agent system built with [Strands Agents](https://strandsagents.com) that orchestrates specialized agents to handle email operations, content creation, and external service integrations using MCP (Model Context Protocol) tools.

## 🚀 Features

### Core Capabilities
- **AI-Powered Orchestration**: Central orchestrator agent that coordinates multiple specialized agents using AI decision-making
- **Email Management**: Complete email handling with content creation and sending capabilities
- **Multi-Recipient Support**: Send emails to single or multiple recipients with CC/BCC support
- **Content Generation**: Professional email content creation for various purposes (meetings, follow-ups, project updates)
- **Email Validation**: Built-in email address validation

### External Integrations (MCP)
- **GitHub Integration**: Repository management, issue tracking, pull request handling
- **Azure DevOps Integration**: Work item management, project operations
- **File System Operations**: Read, write, and manage files through MCP tools
- **Extensible MCP Support**: Easy to add new MCP servers for additional integrations

### Observability & Monitoring
- **Distributed Tracing**: Full request tracing with OpenTelemetry
- **Metrics Collection**: Agent performance and usage metrics
- **Structured Logging**: JSON-formatted logs with contextual information
- **Agent Behavior Tracking**: Monitor agent thinking and decision-making processes

### Model Provider Flexibility
- **Multiple Providers**: Support for OpenAI, Ollama, Anthropic, and LiteLLM
- **Easy Provider Switching**: Change providers through configuration
- **Custom Provider Support**: Add new providers with minimal code changes

## 📋 Prerequisites

- Python 3.10 or higher
- Model provider setup:
  - **Ollama**: Install and run Ollama locally
  - **OpenAI**: API key required
  - **Anthropic**: API key required (optional)

## 🛠 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd L1Agent
   ```

2. **Run the setup script**:
   ```bash
   python setup.py
   ```

3. **Configure environment**:
   - Edit the `.env` file with your configuration
   - Set your preferred model provider
   - Add API keys if using OpenAI/Anthropic
   - Configure email settings

## ⚙️ Configuration

### Environment Variables (.env file)

```bash
# Model Provider Configuration
MODEL_PROVIDER=ollama  # or "openai", "anthropic", "litellm"

# OpenAI Configuration (if using OpenAI)
OPENAI_API_KEY=your_openai_api_key_here

# Ollama Configuration (if using Ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=agent_logs.log

# Observability
ENABLE_TRACING=true
ENABLE_METRICS=true

# MCP Servers (optional)
GITHUB_MCP_SERVER=
ADO_MCP_SERVER=
```

### Model Providers

#### Using Ollama (Recommended for local development)
1. Install Ollama: https://ollama.ai/
2. Start Ollama: `ollama serve`
3. Pull a model: `ollama pull llama3.2`
4. Set `MODEL_PROVIDER=ollama` in `.env`

#### Using OpenAI
1. Get API key from https://platform.openai.com/
2. Set `MODEL_PROVIDER=openai` in `.env`
3. Add your API key: `OPENAI_API_KEY=your_key_here`

## 🎯 Usage

### Command Line Interface

```bash
# Interactive mode
python main.py interactive

# Process single request
python main.py process -r "Send a meeting request email to team@company.com"

# Run demonstrations
python main.py demo

# Show system status
python main.py status
```

### Example Requests in Interactive Mode

```bash
# Email operations
"Send a meeting request email to john@company.com about project review"
"Create a follow-up email for the client meeting"
"Validate these emails: user1@test.com, user2@test.com"

# Multi-recipient emails
"Send project update to team@company.com with CC to manager@company.com"

# Complex workflows
"Create and send a welcome email for new team member joining next week"
```

### Programmatic Usage

```python
from src import create_orchestrator, create_email_agent

# Create agents
orchestrator = create_orchestrator()
email_agent = create_email_agent()

# Use orchestrator for complex requests
response = orchestrator(
    "Send a project update email to the team about Q1 milestones",
    session_id="my_session"
)

# Use email agent directly
email_response = email_agent(
    "Create a meeting request email for project review"
)
```

## 📁 Project Structure

```
L1Agent/
├── src/                          # Source code
│   ├── agents/                   # Specialized agents
│   │   ├── email_agent.py        # Email handling agent
│   │   └── orchestrator.py       # Main orchestrator
│   ├── tools/                    # Agent tools
│   │   └── email_tools.py        # Email-specific tools
│   ├── providers/                # Model provider abstractions
│   │   └── model_providers.py    # Provider implementations
│   ├── observability/            # Monitoring and tracing
│   │   └── agent_observer.py     # Observability system
│   ├── mcp_clients/              # MCP integrations
│   │   └── mcp_integrations.py   # External service clients
│   └── __init__.py               # Package exports
├── config/                       # Configuration management
│   ├── settings.py               # Configuration classes
│   └── __init__.py
├── examples/                     # Usage examples
│   ├── basic_email_example.py    # Basic email operations
│   ├── orchestrator_example.py   # Orchestrator workflows
│   ├── mcp_integration_example.py # MCP integrations
│   └── observability_example.py  # Monitoring features
├── main.py                       # CLI application entry point
├── setup.py                      # Installation script
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
└── README.md                     # This file
```

## 🔧 Architecture

### Multi-Agent System Design

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Request  │────▶│   Orchestrator   │────▶│  Specialized    │
└─────────────────┘    │     Agent        │    │    Agents       │
                       │                  │    │                 │
                       │ • Route requests │    │ • Email Agent   │
                       │ • Coordinate     │    │ • MCP Clients   │
                       │ • Combine results│    │ • Custom Agents │
                       └──────────────────┘    └─────────────────┘
                               │
                               ▼
                       ┌──────────────────┐
                       │   Observability  │
                       │                  │
                       │ • Traces         │
                       │ • Metrics        │
                       │ • Logs           │
                       └──────────────────┘
```

### Agent Specialization

- **Orchestrator Agent**: Routes requests and coordinates workflows
- **Email Agent**: Handles email content creation and sending
- **MCP Clients**: Interface with external services (GitHub, Azure DevOps, etc.)

### Observability System

- **Tracing**: Track request flows across agents
- **Metrics**: Monitor performance and usage
- **Logging**: Structured logging with context
- **Agent Monitoring**: Track agent decisions and behavior

## 🔌 MCP Integration

The system supports Model Context Protocol (MCP) for external integrations:

### Available MCP Clients

- **GitHub**: Repository operations, issue management, PR handling
- **Azure DevOps**: Work item management, project operations  
- **File System**: File read/write/list operations

### Adding New MCP Clients

1. Create client class extending `BaseMCPClient`
2. Implement connection and tool methods
3. Register with `MCPClientManager`
4. Configure server endpoint in `.env`

## 📊 Observability Features

### Monitoring Agent Behavior

The system provides comprehensive observability:

```python
from src import get_observer

observer = get_observer()

# Agent execution tracing
with observer.trace_agent_execution("my_agent", "operation"):
    # Your agent logic here
    pass

# Log agent thoughts
observer.log_agent_thought("agent_name", "thinking process", context)

# Log decisions
observer.log_agent_decision("agent_name", "decision", "reasoning")
```

### Metrics Dashboard

Key metrics tracked:
- Agent invocation counts
- Operation durations
- Error rates
- Email send success/failure rates
- Tool usage statistics

## 🎨 Examples

### Basic Email Operations

```bash
python examples/basic_email_example.py
```

### Orchestrator Workflows

```bash
python examples/orchestrator_example.py
```

### MCP Integrations

```bash
python examples/mcp_integration_example.py
```

### Observability Demo

```bash
python examples/observability_example.py
```

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure dependencies are installed with `pip install -r requirements.txt`

2. **Model Provider Issues**: 
   - For Ollama: Ensure Ollama is running (`ollama serve`)
   - For OpenAI: Check API key in `.env` file

3. **Email Sending Fails**: 
   - Verify SMTP settings in `.env`
   - Use app passwords for Gmail (not regular password)

4. **MCP Integration Issues**: 
   - MCP servers need to be running and accessible
   - Check server endpoints in configuration

### Debug Mode

Enable detailed logging:
```bash
export LOG_LEVEL=DEBUG
python main.py interactive
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and examples
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🔗 Links

- [Strands Agents Documentation](https://strandsagents.com)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Ollama](https://ollama.ai/)
- [OpenAI API](https://platform.openai.com/)

## 📞 Support

For questions and support:
- Check the examples in the `examples/` directory
- Review the configuration in `.env.example`
- Run the demo: `python main.py demo`
