"""
Modular Multi-Agent System with LangGraph
========================================

A sophisticated multi-agent system built with LangGraph that supports:
- Multiple model providers (OpenAI, Ollama)
- Modular agent architecture
- Comprehensive observability
- Tool integration for weather and email
"""

from typing import Optional, Union
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START

# Import modular components
from config import ModelConfig, get_model, Settings, get_settings
from config.model_config import configure_openai_model, configure_ollama_model, list_available_models
from utils import setup_logging, get_observer, clear_logs, print_logs
from utils.state import MultiAgentState
from agents import OrchestratorAgent, WeatherAgent, EmailAgent


class MultiAgentSystem:
    """
    Main multi-agent system class that orchestrates all components.
    """
    
    def __init__(self, model_config: Optional[ModelConfig] = None):
        """
        Initialize the multi-agent system.
        
        Args:
            model_config: Optional model configuration. If None, uses default.
        """
        # Setup configuration
        self.settings = get_settings()
        if model_config:
            from config.model_config import set_model_config
            set_model_config(model_config)
        
        # Setup logging
        setup_logging(self.settings.log_level, self.settings.log_file)
        
        # Get observer for tracking
        self.observer = get_observer()
        
        # Initialize agents
        self.orchestrator = OrchestratorAgent()
        self.weather_agent = WeatherAgent()
        self.email_agent = EmailAgent()
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build and compile the LangGraph workflow"""
        self.observer.log_agent_thinking("System", "Initializing multi-agent system", "Building LangGraph workflow")
        
        # Create the state graph
        builder = StateGraph(MultiAgentState)
        
        # Add agent nodes
        builder.add_node("orchestrator", self.orchestrator.process)
        builder.add_node("weather_agent", self.weather_agent.process) 
        builder.add_node("email_agent", self.email_agent.process)
        
        # Add edges - all conversations start with orchestrator
        builder.add_edge(START, "orchestrator")
        
        # Compile the graph
        graph = builder.compile()
        
        self.observer.log_agent_thinking("System", "Multi-agent system initialized successfully", "Ready to process requests")
        return graph
    
    def process_request(self, user_input: str) -> dict:
        """
        Process a user request through the multi-agent system.
        
        Args:
            user_input: The user's request or question
            
        Returns:
            The final state after processing
        """
        print(f"\n🤖 Multi-Agent System Starting...")
        print(f"📝 User Input: {user_input}")
        
        # Clear previous observations for this request
        self.observer.clear_observations()
        
        # Prepare initial state using our MultiAgentState class
        initial_state = MultiAgentState(
            messages=[HumanMessage(content=user_input)],
            current_task="",
            task_status="pending",
            agent_data_json="{}",
            tool_data_json="{}",
            custom_data_json="{}",
            execution_history_json="[]",
            total_steps=0
        )
        
        try:
            # Run the graph
            self.observer.log_agent_thinking("System", f"Processing user request: {user_input}", "Starting workflow execution")
            
            result = self.graph.invoke(initial_state)
            
            # Display results
            print(f"\n📋 Final Response:")
            final_message = result["messages"][-1]
            print(f"🤖 {final_message.name}: {final_message.content}")
            
            print(f"\n📊 Task Status: {result.get('task_status', 'unknown')}")
            
            # Show agent thinking and actions
            self.observer.print_observations()
            
            return result
            
        except Exception as e:
            self.observer.log_agent_thinking("System", f"System error: {str(e)}", "Execution failed")
            print(f"\n❌ Error: {str(e)}")
            self.observer.print_observations()
            return None
    
    def get_system_status(self) -> dict:
        """Get the current system configuration status"""
        return {
            "model_config": str(get_model()),
            "settings_validation": self.settings.validate(),
            "total_observations": len(self.observer.get_observations())
        }
    
    def print_system_info(self):
        """Print comprehensive system information"""
        print("🤖 MULTI-AGENT SYSTEM STATUS")
        print("=" * 50)
        
        # Configuration status
        self.settings.print_status()
        
        # Model info
        try:
            model = get_model()
            print(f"\n🧠 Current Model: {type(model).__name__}")
            if hasattr(model, 'model_name'):
                print(f"   Model Name: {model.model_name}")
        except Exception as e:
            print(f"\n🧠 Model: ❌ Error - {e}")
        
        # Available models
        print(f"\n📋 Available Models:")
        models = list_available_models()
        for provider, model_list in models.items():
            print(f"   {provider.upper()}: {', '.join(model_list[:3])}{'...' if len(model_list) > 3 else ''}")


def create_system_with_openai(
    model_name: str = "gpt-4o-mini", 
    temperature: float = 0.1,
    api_key: Optional[str] = None
) -> MultiAgentSystem:
    """
    Create a multi-agent system configured for OpenAI models.
    
    Args:
        model_name: OpenAI model name
        temperature: Model temperature
        api_key: OpenAI API key (optional, will use environment variable)
        
    Returns:
        Configured MultiAgentSystem instance
    """
    config = configure_openai_model(model_name, temperature, api_key)
    return MultiAgentSystem(config)


def create_system_with_ollama(
    model_name: str = "llama3.2:latest",
    temperature: float = 0.1,
    base_url: str = "http://localhost:11434"
) -> MultiAgentSystem:
    """
    Create a multi-agent system configured for Ollama models.
    
    Args:
        model_name: Ollama model name
        temperature: Model temperature
        base_url: Ollama server URL
        
    Returns:
        Configured MultiAgentSystem instance
    """
    config = configure_ollama_model(model_name, temperature, base_url)
    return MultiAgentSystem(config)


def run_interactive_demo():
    """Run an interactive demonstration of the system"""
    print("🚀 MULTI-AGENT SYSTEM INTERACTIVE DEMO")
    print("=" * 60)
    
    # Show available models
    print("\n📋 Available Models:")
    models = list_available_models()
    print("OpenAI:", ", ".join(models["openai"][:3]))
    print("Ollama:", ", ".join(models["ollama"][:3]))
    
    print("\n🔧 Configuration Options:")
    print("1. OpenAI (requires API key)")
    print("2. Ollama (requires local installation)")
    print("3. Default (tries OpenAI first, then shows demo)")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    try:
        if choice == "1":
            model_name = input("Enter OpenAI model name (default: gpt-4o-mini): ").strip() or "gpt-4o-mini"
            system = create_system_with_openai(model_name)
        elif choice == "2":
            model_name = input("Enter Ollama model name (default: llama3.2:latest): ").strip() or "llama3.2:latest"
            system = create_system_with_ollama(model_name)
        else:
            system = MultiAgentSystem()
        
        # Show system status
        system.print_system_info()
        
        # Interactive loop
        print("\n💬 Chat with the multi-agent system (type 'quit' to exit):")
        while True:
            user_input = input("\n👤 You: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if user_input:
                system.process_request(user_input)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Try running with default configuration or check your setup.")


# Example usage and testing
if __name__ == "__main__":
    print("🤖 LANGGRAPH MULTI-AGENT SYSTEM")
    print("=" * 50)
    print("This modular system supports:")
    print("✅ Multiple model providers (OpenAI, Ollama)")
    print("✅ Modular agent architecture")
    print("✅ Comprehensive observability")
    print("✅ Weather and email tools")
    print("✅ Configurable settings")
    
    # Run interactive demo
    run_interactive_demo()
