"""
Base agent class for the multi-agent system.
"""

from abc import ABC, abstractmethod
from typing import Literal
from langgraph.types import Command

from utils.state import MultiAgentState
from utils.observer import log_thinking


class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def process(self, state: MultiAgentState) -> Command[Literal["__end__"]]:
        """Process the agent's task and return a command"""
        pass
    
    def log_thinking(self, thought: str, action: str = None):
        """Log agent thinking and actions"""
        log_thinking(self.name, thought, action)
