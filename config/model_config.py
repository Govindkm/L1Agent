"""
Model configuration and selection for the multi-agent system.
Supports both OpenAI and Ollama models.
"""

import os
from typing import Literal, Optional, Union
from enum import Enum
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.language_models import BaseChatModel
from strands.models.ollama import OllamaModel
from strands.models.openai import OpenAIModel
from strands.models import Model

# Load environment variables
load_dotenv()


class ModelProvider(Enum):
    """Supported model providers"""
    OPENAI = "openai"
    OLLAMA = "ollama"


class ModelConfig:
    """Configuration for model selection and initialization"""
    
    def __init__(
        self,
        provider: Union[ModelProvider, str] = ModelProvider.OPENAI,
        model_name: Optional[str] = None,
        temperature: float = 0.1,
        openai_api_key: Optional[str] = None,
        ollama_base_url: str = "http://localhost:11434"
    ):
        if isinstance(provider, str):
            provider = ModelProvider(provider.lower())
        
        self.provider = provider
        self.temperature = temperature
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.ollama_base_url = ollama_base_url
        
        # Set default model names based on provider
        if model_name is None:
            if provider == ModelProvider.OPENAI:
                self.model_name = "gpt-4o-mini"
            else:  # OLLAMA
                self.model_name = "llama3.2:latest"
        else:
            self.model_name = model_name
    
    def create_model(self) -> BaseChatModel:
        """Create and return the configured model instance"""
        if self.provider == ModelProvider.OPENAI:
            if not self.openai_api_key:
                raise ValueError(
                    "OpenAI API key is required for OpenAI models. "
                    "Set OPENAI_API_KEY environment variable or pass it to ModelConfig."
                )
            return ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                api_key=self.openai_api_key
            )
        
        elif self.provider == ModelProvider.OLLAMA:
            return ChatOllama(
                model=self.model_name,
                temperature=self.temperature,
                base_url=self.ollama_base_url
            )
        
        else:
            raise ValueError(f"Unsupported model provider: {self.provider}")
    
    def create_strands_model(self) -> Model:
        """Create and return the configured Strands model instance"""
        if self.provider == ModelProvider.OPENAI:
            return OpenAIModel(
                model_id=self.model_name,
                client_args={
                    "api_key": self.openai_api_key,
                },
                params={
                    "temperature": self.temperature,
                    "max_tokens": 2048
                }
            )
        
        elif self.provider == ModelProvider.OLLAMA:
            return OllamaModel(
                host=self.ollama_base_url,
                model_id=self.model_name,
            )
        
        else:
            raise ValueError(f"Unsupported model provider: {self.provider}")

    def __str__(self) -> str:
        return f"ModelConfig(provider={self.provider.value}, model={self.model_name})"


# Global model configuration
_global_model_config: Optional[ModelConfig] = None


def set_model_config(config: ModelConfig) -> None:
    """Set the global model configuration"""
    global _global_model_config
    _global_model_config = config


def get_model_config() -> ModelConfig:
    """Get the current global model configuration"""
    global _global_model_config
    if _global_model_config is None:
        # Read provider from environment variables
        provider_env = os.getenv("MODEL_PROVIDER", "openai").lower()
        model_name_env = os.getenv("OLLAMA_MODEL") if provider_env == "ollama" else None
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        _global_model_config = ModelConfig(
            provider=provider_env,
            model_name=model_name_env,
            ollama_base_url=ollama_base_url
        )
    return _global_model_config


def get_model() -> BaseChatModel:
    """Get the configured model instance"""
    config = get_model_config()
    return config.create_model()

def get_strands_model() -> Model:
    """Get the configured Strands model instance"""
    config = get_model_config()
    return config.create_strands_model()

def configure_openai_model(
    model_name: str = "gpt-4o-mini",
    temperature: float = 0.1,
    api_key: Optional[str] = None
) -> ModelConfig:
    """Configure and set OpenAI model"""
    config = ModelConfig(
        provider=ModelProvider.OPENAI,
        model_name=model_name,
        temperature=temperature,
        openai_api_key=api_key
    )
    set_model_config(config)
    return config


def configure_ollama_model(
    model_name: str = "llama3.2:latest",
    temperature: float = 0.1,
    base_url: str = "http://localhost:11434"
) -> ModelConfig:
    """Configure and set Ollama model"""
    config = ModelConfig(
        provider=ModelProvider.OLLAMA,
        model_name=model_name,
        temperature=temperature,
        ollama_base_url=base_url
    )
    set_model_config(config)
    return config


def list_available_models() -> dict:
    """List available models for each provider"""
    return {
        "openai": [
            "gpt-4o",
            "gpt-4o-mini", 
            "gpt-4-turbo",
            "gpt-3.5-turbo"
        ],
        "ollama": [
            "llama3.2:latest",
            "llama3.2:3b",
            "llama3.1:latest", 
            "llama3.1:8b",
            "llama3.1:70b",
            "mistral:latest",
            "mistral:7b",
            "codellama:latest",
            "codellama:7b",
            "phi3:latest",
            "gemma2:latest"
        ]
    }


def model_selection_prompt() -> str:
    """Return a formatted prompt for model selection"""
    models = list_available_models()
    
    prompt = """
🤖 AVAILABLE MODELS:

OpenAI Models (requires API key):
"""
    for model in models["openai"]:
        prompt += f"  • {model}\n"
    
    prompt += """
Ollama Models (requires local Ollama installation):
"""
    for model in models["ollama"]:
        prompt += f"  • {model}\n"
    
    prompt += """
Usage Examples:
- configure_openai_model("gpt-4o-mini")
- configure_ollama_model("llama3.2:latest")
"""
    
    return prompt


if __name__ == "__main__":
    # Demo the model configuration
    print("🤖 Model Configuration Demo")
    print("=" * 40)
    
    print(model_selection_prompt())
    
    # Test configurations (without actually creating models)
    print("\n📋 Configuration Examples:")
    
    openai_config = ModelConfig(provider="openai", model_name="gpt-4o-mini")
    print(f"OpenAI: {openai_config}")
    
    ollama_config = ModelConfig(provider="ollama", model_name="llama3.2:latest")
    print(f"Ollama: {ollama_config}")
