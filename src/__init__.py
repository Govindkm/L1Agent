"""
Multi-Agent Email System with Strands Framework

A comprehensive system that orchestrates multiple agents to handle email operations,
content creation, and external service integrations using MCP tools.
"""

from .agents import (
    EmailAgent,
    OrchestratorAgent,
    create_email_agent,
    create_orchestrator
)

from .tools import (
    create_email_content,
    send_email_tool,
    validate_email_addresses
)

from .providers import (
    get_model_provider,
    ModelProviderFactory
)

from .observability import (
    get_observer,
    make_observable
)

from .mcp_clients import (
    get_mcp_manager,
    GitHubMCPClient,
    AzureDevOpsMCPClient
)

from config import (
    get_config,
    SystemConfig,
    ModelProvider
)

__version__ = "1.0.0"

__all__ = [
    # Core agents
    'EmailAgent',
    'OrchestratorAgent',
    'create_email_agent',
    'create_orchestrator',
    
    # Tools
    'create_email_content',
    'send_email_tool',
    'validate_email_addresses',
    
    # Providers
    'get_model_provider',
    'ModelProviderFactory',
    
    # Observability
    'get_observer',
    'make_observable',
    
    # MCP clients
    'get_mcp_manager',
    'GitHubMCPClient',
    'AzureDevOpsMCPClient',
    
    # Configuration
    'get_config',
    'SystemConfig',
    'ModelProvider',
    
    # Version
    '__version__'
]
