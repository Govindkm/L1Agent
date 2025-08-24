"""Agents package containing all specialized agents."""

from .email_agent import (
    EmailAgent,
    email_agent_tool,
    create_email_agent,
    EMAIL_AGENT_SYSTEM_PROMPT,
    CONTENT_CREATOR_SYSTEM_PROMPT,
    EMAIL_SENDER_SYSTEM_PROMPT
)

from .orchestrator import (
    OrchestratorAgent,
    orchestrator_tool,
    create_orchestrator,
    ORCHESTRATOR_SYSTEM_PROMPT
)

__all__ = [
    # Email Agent
    'EmailAgent',
    'email_agent_tool',
    'create_email_agent',
    'EMAIL_AGENT_SYSTEM_PROMPT',
    'CONTENT_CREATOR_SYSTEM_PROMPT', 
    'EMAIL_SENDER_SYSTEM_PROMPT',
    
    # Orchestrator Agent
    'OrchestratorAgent',
    'orchestrator_tool',
    'create_orchestrator',
    'ORCHESTRATOR_SYSTEM_PROMPT'
]
