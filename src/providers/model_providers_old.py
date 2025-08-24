"""
Model provider abstraction layer for flexible LLM integration.
Supports OpenAI, Ollama, Anthropic, and LiteLLM providers through Strands Agents SDK.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from strands import Agent
from strands.models.openai import OpenAIModel
from strands.models.ollama import OllamaModel
from strands.models.anthropic import AnthropicModel
from strands.models.litellm import LiteLLMModel
from config.settings import ModelConfig, ModelProvider
import logging


class BaseModelProvider(ABC):
    """Abstract base class for model providers"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def create_model(self) -> Any:
        """Create a model instance for this provider"""
        pass
    
    def create_agent(self, system_prompt: str, tools: Optional[List[Any]] = None, **kwargs) -> Agent:
        """Create an agent with this model provider's model"""
        model = self.create_model()
        return Agent(
            model=model,
            system_prompt=system_prompt,
            tools=tools or [],
            **kwargs
        )
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model"""
        pass


class OpenAIProvider(BaseModelProvider):
    """OpenAI model provider"""
    
    def create_model(self) -> OpenAIModel:
        """Create an OpenAI model instance"""
        client_args = {}
        
        if self.config.api_key:
            client_args["api_key"] = self.config.api_key
        
        if self.config.base_url:
            client_args["base_url"] = self.config.base_url
        
        params = {}
        if self.config.temperature is not None:
            params["temperature"] = self.config.temperature
        if self.config.max_tokens is not None:
            params["max_tokens"] = self.config.max_tokens
        
        return OpenAIModel(
            client_args=client_args,
            model_id=self.config.model,
            params=params
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get OpenAI model information"""
        return {
            "provider": "openai",
            "model": self.config.model,
            "base_url": self.config.base_url,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }


class OllamaProvider(BaseModelProvider):
    """Ollama model provider for local models"""
    
    def create_model(self) -> OllamaModel:
        """Create an Ollama model instance"""
        return OllamaModel(
            host=self.config.base_url or "http://localhost:11434",
            model_id=self.config.model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            keep_alive="5m"  # Keep model loaded for 5 minutes
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Ollama model information"""
        return {
            "provider": "ollama",
            "model": self.config.model,
            "host": self.config.base_url or "http://localhost:11434",
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }


class AnthropicProvider(BaseModelProvider):
    """Anthropic (Claude) model provider"""
    
    def create_model(self) -> AnthropicModel:
        """Create an Anthropic model instance"""
        client_args = {}
        
        if self.config.api_key:
            client_args["api_key"] = self.config.api_key
        
        params = {}
        if self.config.temperature is not None:
            params["temperature"] = self.config.temperature
        
        return AnthropicModel(
            client_args=client_args,
            model_id=self.config.model or "claude-3-5-sonnet-20241022",
            max_tokens=self.config.max_tokens or 1024,
            params=params
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Anthropic model information"""
        return {
            "provider": "anthropic",
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }


class LiteLLMProvider(BaseModelProvider):
    """LiteLLM provider for unified access to multiple LLM providers"""
    
    def create_model(self) -> LiteLLMModel:
        """Create a LiteLLM model instance"""
        client_args = {}
        
        if self.config.api_key:
            client_args["api_key"] = self.config.api_key
        
        if self.config.base_url:
            client_args["base_url"] = self.config.base_url
        
        params = {}
        if self.config.temperature is not None:
            params["temperature"] = self.config.temperature
        if self.config.max_tokens is not None:
            params["max_tokens"] = self.config.max_tokens
        
        return LiteLLMModel(
            client_args=client_args,
            model_id=self.config.model,
            params=params
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get LiteLLM model information"""
        return {
            "provider": "litellm",
            "model": self.config.model,
            "base_url": self.config.base_url,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }


class ModelProviderFactory:
    """Factory class for creating model providers"""
    
    @staticmethod
    def create_provider(config: ModelConfig) -> BaseModelProvider:
        """Create a model provider based on configuration"""
        
        if config.provider == ModelProvider.OPENAI:
            return OpenAIProvider(config)
        elif config.provider == ModelProvider.OLLAMA:
            return OllamaProvider(config)
        elif config.provider == ModelProvider.ANTHROPIC:
            return AnthropicProvider(config)
        elif config.provider == ModelProvider.LITELLM:
            return LiteLLMProvider(config)
        else:
            raise ValueError(f"Unsupported provider: {config.provider}")
    
    @staticmethod
    def get_available_providers() -> List[str]:
        """Get list of available providers"""
        return [provider.value for provider in ModelProvider]


def get_model_provider(config: ModelConfig) -> BaseModelProvider:
    """Get a model provider instance"""
    return ModelProviderFactory.create_provider(config)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get OpenAI model information"""
        return {
            "provider": "openai",
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }


class OllamaProvider(BaseModelProvider):
    """Ollama model provider for local models"""
    
    def create_agent(self, system_prompt: str, tools: Optional[List[Any]] = None, **kwargs) -> Agent:
        """Create an agent using Ollama models"""
        
        # For Ollama with Strands, we might need to specify the model differently
        # This will depend on how Strands handles different providers
        return Agent(
            model=OllamaModel(),  # e.g., "ollama/llama3.2"
            system_prompt=system_prompt,
            tools=tools or [],
            **kwargs
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Ollama model information"""
        return {
            "provider": "ollama",
            "model": self.config.model,
            "base_url": self.config.base_url,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }


class AnthropicProvider(BaseModelProvider):
    """Anthropic (Claude) model provider"""
    
    def create_agent(self, system_prompt: str, tools: Optional[List[Any]] = None, **kwargs) -> Agent:
        """Create an agent using Anthropic models"""
        
        # Note: This would require strands to support Anthropic models
        # For now, we'll use a placeholder implementation
        try:
            return Agent(
                model=AnthropicModel(),  # e.g., "claude-3-sonnet-20240229"
                system_prompt=system_prompt,
                tools=tools or [],
                **kwargs
            )
        except Exception:
            # Fallback to LiteLLM if direct Anthropic support isn't available
            self.logger.warning("Direct Anthropic support not available, falling back to LiteLLM")
            return self._create_litellm_agent(system_prompt, tools, **kwargs)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Anthropic model information"""
        return {
            "provider": "anthropic",
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }
    
    def _create_litellm_agent(self, system_prompt: str, tools: Optional[List[Any]] = None, **kwargs) -> Agent:
        """Fallback to create agent using LiteLLM"""
        
        return Agent(
            model=f"claude-3-sonnet-20240229",  # Default Claude model
            system_prompt=system_prompt,
            tools=tools or [],
            **kwargs
        )


class LiteLLMProvider(BaseModelProvider):
    """LiteLLM provider for accessing multiple model providers through a unified API"""
    
    def create_agent(self, system_prompt: str, tools: Optional[List[Any]] = None, **kwargs) -> Agent:
        """Create an agent using LiteLLM"""
        
        return Agent(
            model=LiteLLMModel(),
            system_prompt=system_prompt,
            tools=tools or [],
            **kwargs
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get LiteLLM model information"""
        return {
            "provider": "litellm",
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "base_url": self.config.base_url
        }


class ModelProviderFactory:
    """Factory for creating model providers"""
    
    _providers = {
        ModelProvider.OPENAI: OpenAIProvider,
        ModelProvider.OLLAMA: OllamaProvider,
        ModelProvider.ANTHROPIC: AnthropicProvider,
        ModelProvider.LITELLM: LiteLLMProvider
    }
    
    @classmethod
    def create_provider(cls, config: ModelConfig) -> BaseModelProvider:
        """Create a model provider based on configuration"""
        
        provider_class = cls._providers.get(config.provider)
        if not provider_class:
            raise ValueError(f"Unsupported model provider: {config.provider}")
        
        return provider_class(config)
    
    @classmethod
    def register_provider(cls, provider_type: ModelProvider, provider_class: type):
        """Register a new model provider"""
        cls._providers[provider_type] = provider_class
    
    @classmethod
    def list_providers(cls) -> List[ModelProvider]:
        """List all available providers"""
        return list(cls._providers.keys())


def get_model_provider(config: ModelConfig) -> BaseModelProvider:
    """Convenience function to get a model provider"""
    return ModelProviderFactory.create_provider(config)
