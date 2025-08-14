"""
Observability utilities for tracking agent behavior.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Configure logging
def setup_logging(log_level: str = "INFO", log_file: str = "agent_logs.log"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


class AgentObserver:
    """Observer class to track agent thinking and actions"""
    
    def __init__(self):
        self.observations: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
    
    def log_agent_thinking(self, agent_name: str, thought: str, action: Optional[str] = None):
        """Log what an agent is thinking and planning to do"""
        observation = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "thought": thought,
            "action": action
        }
        self.observations.append(observation)
        self.logger.info(f"[{agent_name}] THINKING: {thought}")
        if action:
            self.logger.info(f"[{agent_name}] ACTION: {action}")
    
    def get_observations(self) -> List[Dict]:
        """Get all logged observations"""
        return self.observations.copy()
    
    def clear_observations(self):
        """Clear all observations"""
        self.observations.clear()
    
    def print_observations(self):
        """Print all observations in a formatted way"""
        print("\n" + "="*80)
        print("AGENT THINKING AND ACTIONS LOG")
        print("="*80)
        for obs in self.observations:
            print(f"\n[{obs['timestamp']}] Agent: {obs['agent']}")
            print(f"💭 Thinking: {obs['thought']}")
            if obs['action']:
                print(f"🎯 Action: {obs['action']}")
        print("="*80 + "\n")
    
    def get_agent_summary(self, agent_name: str) -> List[Dict]:
        """Get observations for a specific agent"""
        return [obs for obs in self.observations if obs['agent'] == agent_name]
    
    def export_observations(self, format: str = "json") -> str:
        """Export observations in specified format"""
        if format.lower() == "json":
            import json
            return json.dumps(self.observations, indent=2)
        elif format.lower() == "csv":
            import csv
            import io
            output = io.StringIO()
            if self.observations:
                fieldnames = self.observations[0].keys()
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.observations)
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Global observer instance
_global_observer: Optional[AgentObserver] = None


def get_observer() -> AgentObserver:
    """Get the global observer instance"""
    global _global_observer
    if _global_observer is None:
        _global_observer = AgentObserver()
    return _global_observer


def log_thinking(agent_name: str, thought: str, action: Optional[str] = None):
    """Convenience function to log agent thinking"""
    observer = get_observer()
    observer.log_agent_thinking(agent_name, thought, action)


def clear_logs():
    """Clear all observation logs"""
    observer = get_observer()
    observer.clear_observations()


def print_logs():
    """Print all observation logs"""
    observer = get_observer()
    observer.print_observations()
