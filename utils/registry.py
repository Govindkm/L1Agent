"""
Dynamic agent and tool registry for automatic extension of the multi-agent system.
"""

from typing import Dict, Type, Any, List, Protocol, runtime_checkable
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import inspect


@runtime_checkable
class AgentProtocol(Protocol):
    """Protocol that all agents must implement"""
    
    def process(self, state: Any) -> Any:
        """Process method that all agents must have"""
        ...


@runtime_checkable  
class ToolProtocol(Protocol):
    """Protocol that all tools must implement"""
    
    def __call__(self, *args, **kwargs) -> Any:
        """Tools must be callable"""
        ...


@dataclass
class AgentRegistration:
    """Registration information for an agent"""
    name: str
    agent_class: Type
    description: str
    capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    routing_keywords: List[str] = field(default_factory=list)


@dataclass
class ToolRegistration:
    """Registration information for a tool"""
    name: str
    tool_func: callable
    description: str
    agent_compatibility: List[str] = field(default_factory=list)
    required_config: List[str] = field(default_factory=list)


class DynamicRegistry:
    """
    Registry for dynamically managing agents and tools.
    Allows automatic system extension without code modifications.
    """
    
    def __init__(self):
        self.agents: Dict[str, AgentRegistration] = {}
        self.tools: Dict[str, ToolRegistration] = {}
        self._agent_instances: Dict[str, Any] = {}
        
    def register_agent(self, name: str, agent_class: Type, description: str = "",
                      capabilities: List[str] = None, dependencies: List[str] = None,
                      routing_keywords: List[str] = None) -> None:
        """Register a new agent class"""
        
        # Validate agent implements required protocol
        if not hasattr(agent_class, 'process'):
            raise ValueError(f"Agent {name} must implement 'process' method")
        
        registration = AgentRegistration(
            name=name,
            agent_class=agent_class,
            description=description,
            capabilities=capabilities or [],
            dependencies=dependencies or [],
            routing_keywords=routing_keywords or []
        )
        
        self.agents[name] = registration
        print(f"✅ Registered agent: {name}")
    
    def register_tool(self, name: str, tool_func: callable, description: str = "",
                     agent_compatibility: List[str] = None,
                     required_config: List[str] = None) -> None:
        """Register a new tool function"""
        
        # Validate tool is callable
        if not callable(tool_func):
            raise ValueError(f"Tool {name} must be callable")
        
        registration = ToolRegistration(
            name=name,
            tool_func=tool_func,
            description=description,
            agent_compatibility=agent_compatibility or [],
            required_config=required_config or []
        )
        
        self.tools[name] = registration
        print(f"✅ Registered tool: {name}")
    
    def get_agent_instance(self, name: str) -> Any:
        """Get or create agent instance"""
        if name not in self._agent_instances:
            if name not in self.agents:
                raise ValueError(f"Agent {name} not registered")
            
            agent_class = self.agents[name].agent_class
            self._agent_instances[name] = agent_class()
        
        return self._agent_instances[name]
    
    def get_tool(self, name: str) -> callable:
        """Get tool function"""
        if name not in self.tools:
            raise ValueError(f"Tool {name} not registered")
        
        return self.tools[name].tool_func
    
    def get_routing_map(self) -> Dict[str, List[str]]:
        """Get keyword-to-agent routing map"""
        routing_map = {}
        for agent_name, registration in self.agents.items():
            for keyword in registration.routing_keywords:
                if keyword not in routing_map:
                    routing_map[keyword] = []
                routing_map[keyword].append(agent_name)
        return routing_map
    
    def suggest_agent(self, user_input: str) -> List[str]:
        """Suggest which agents could handle the user input"""
        user_input_lower = user_input.lower()
        suggestions = []
        
        for agent_name, registration in self.agents.items():
            # Check if any routing keywords match
            if any(keyword in user_input_lower for keyword in registration.routing_keywords):
                suggestions.append(agent_name)
        
        return suggestions
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        return {
            "total_agents": len(self.agents),
            "total_tools": len(self.tools),
            "agents": {
                name: {
                    "description": reg.description,
                    "capabilities": reg.capabilities,
                    "routing_keywords": reg.routing_keywords,
                    "dependencies": reg.dependencies
                }
                for name, reg in self.agents.items()
            },
            "tools": {
                name: {
                    "description": reg.description,
                    "agent_compatibility": reg.agent_compatibility,
                    "required_config": reg.required_config
                }
                for name, reg in self.tools.items()
            },
            "routing_map": self.get_routing_map()
        }
    
    def validate_system(self) -> Dict[str, Any]:
        """Validate all registered components"""
        validation_results = {
            "valid_agents": [],
            "invalid_agents": [],
            "valid_tools": [],
            "invalid_tools": [],
            "missing_dependencies": [],
            "warnings": []
        }
        
        # Validate agents
        for name, registration in self.agents.items():
            try:
                # Check if agent can be instantiated
                instance = registration.agent_class()
                if hasattr(instance, 'process'):
                    validation_results["valid_agents"].append(name)
                else:
                    validation_results["invalid_agents"].append(f"{name}: missing process method")
            except Exception as e:
                validation_results["invalid_agents"].append(f"{name}: {str(e)}")
        
        # Validate tools
        for name, registration in self.tools.items():
            try:
                if callable(registration.tool_func):
                    validation_results["valid_tools"].append(name)
                else:
                    validation_results["invalid_tools"].append(f"{name}: not callable")
            except Exception as e:
                validation_results["invalid_tools"].append(f"{name}: {str(e)}")
        
        # Check dependencies
        for name, registration in self.agents.items():
            for dep in registration.dependencies:
                if dep not in self.tools and dep not in self.agents:
                    validation_results["missing_dependencies"].append(f"{name} requires {dep}")
        
        return validation_results
    
    def auto_discover_agents_and_tools(self, module_paths: List[str] = None) -> None:
        """
        Auto-discover agents and tools from specified modules.
        This enables dynamic loading without manual registration.
        """
        if module_paths is None:
            module_paths = ["agents", "tools"]
        
        import importlib
        import pkgutil
        
        for module_path in module_paths:
            try:
                module = importlib.import_module(module_path)
                
                # Walk through all classes/functions in the module
                for name, obj in inspect.getmembers(module):
                    # Auto-register agents (classes ending with 'Agent')
                    if (inspect.isclass(obj) and 
                        name.endswith('Agent') and 
                        hasattr(obj, 'process') and
                        name not in ['BaseAgent', 'AgentProtocol']):
                        
                        self.register_agent(
                            name=name.lower().replace('agent', '_agent'),
                            agent_class=obj,
                            description=f"Auto-discovered agent: {name}"
                        )
                    
                    # Auto-register tools (functions decorated with @tool or named with specific patterns)
                    elif (callable(obj) and 
                          not inspect.isclass(obj) and
                          (name.startswith('get_') or name.startswith('send_') or name.startswith('generate_'))):
                        
                        self.register_tool(
                            name=name,
                            tool_func=obj,
                            description=f"Auto-discovered tool: {name}"
                        )
                        
            except ImportError as e:
                print(f"⚠️ Could not import {module_path}: {e}")


# Global registry instance
_global_registry: DynamicRegistry = None


def get_registry() -> DynamicRegistry:
    """Get the global registry instance"""
    global _global_registry
    if _global_registry is None:
        _global_registry = DynamicRegistry()
    return _global_registry


def initialize_default_registry() -> DynamicRegistry:
    """Initialize registry with default agents and tools"""
    registry = get_registry()
    
    # Import existing agents
    try:
        from agents.orchestrator_agent import OrchestratorAgent
        from agents.weather_agent import WeatherAgent
        from agents.email_agent import EmailAgent
        
        # Register existing agents
        registry.register_agent(
            "orchestrator",
            OrchestratorAgent,
            "Main coordinator that routes requests to appropriate agents",
            capabilities=["routing", "analysis", "coordination"],
            routing_keywords=["help", "what", "how", "general"]
        )
        
        registry.register_agent(
            "weather_agent", 
            WeatherAgent,
            "Handles weather-related queries and forecasts",
            capabilities=["weather_lookup", "forecast", "climate_data"],
            routing_keywords=["weather", "temperature", "forecast", "climate", "rain", "sunny", "cloudy"]
        )
        
        registry.register_agent(
            "email_agent",
            EmailAgent, 
            "Generates and sends emails",
            capabilities=["email_generation", "email_sending", "content_creation"],
            routing_keywords=["email", "send", "write", "compose", "message", "mail"]
        )
        
    except ImportError as e:
        print(f"⚠️ Could not import default agents: {e}")
    
    # Import existing tools
    try:
        from tools.weather_tools import get_weather_data
        from tools.email_tools import generate_email_content, send_email
        
        # Register existing tools
        registry.register_tool(
            "get_weather_data",
            get_weather_data,
            "Retrieves current weather data for a city",
            agent_compatibility=["weather_agent"]
        )
        
        registry.register_tool(
            "generate_email_content",
            generate_email_content,
            "Generates professional email content",
            agent_compatibility=["email_agent"]
        )
        
        registry.register_tool(
            "send_email",
            send_email,
            "Sends emails via SMTP",
            agent_compatibility=["email_agent"],
            required_config=["email_user", "email_password", "smtp_server"]
        )
        
    except ImportError as e:
        print(f"⚠️ Could not import default tools: {e}")
    
    return registry


if __name__ == "__main__":
    # Demo the registry system
    registry = initialize_default_registry()
    
    print("\n🔧 DYNAMIC REGISTRY SYSTEM DEMO")
    print("=" * 50)
    
    system_info = registry.get_system_info()
    print(f"📊 System Overview:")
    print(f"   Agents: {system_info['total_agents']}")
    print(f"   Tools: {system_info['total_tools']}")
    
    print(f"\n🤖 Registered Agents:")
    for name, info in system_info['agents'].items():
        print(f"   • {name}: {info['description']}")
        print(f"     Keywords: {', '.join(info['routing_keywords'])}")
    
    print(f"\n🛠️ Registered Tools:")
    for name, info in system_info['tools'].items():
        print(f"   • {name}: {info['description']}")
    
    # Test agent suggestion
    test_queries = [
        "What's the weather in Paris?",
        "Send an email to my boss",
        "Help me with something"
    ]
    
    print(f"\n🎯 Agent Suggestions:")
    for query in test_queries:
        suggestions = registry.suggest_agent(query)
        print(f"   '{query}' → {suggestions}")
    
    # Validate system
    validation = registry.validate_system()
    print(f"\n✅ System Validation:")
    print(f"   Valid agents: {len(validation['valid_agents'])}")
    print(f"   Valid tools: {len(validation['valid_tools'])}")
    if validation['invalid_agents']:
        print(f"   ❌ Invalid agents: {validation['invalid_agents']}")
    if validation['missing_dependencies']:
        print(f"   ⚠️ Missing dependencies: {validation['missing_dependencies']}")
