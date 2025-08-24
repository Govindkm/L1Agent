"""
Configuration management for the multi-agent email system.
Handles environment variables, model providers, and system settings.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import logging


class ModelProvider(Enum):
    """Supported model providers"""
    OPENAI = "openai"
    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"
    LITELLM = "litellm"


class LogLevel(Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO" 
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class ModelConfig:
    """Configuration for model providers"""
    provider: ModelProvider
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 30


@dataclass
class EmailConfig:
    """Email configuration"""
    smtp_server: str
    smtp_port: int
    username: str
    password: str
    use_tls: bool = True
    verify_ssl: bool = True


@dataclass
class ObservabilityConfig:
    """Observability and logging configuration"""
    log_level: LogLevel
    log_file: str
    enable_tracing: bool = True
    jaeger_endpoint: Optional[str] = None
    enable_metrics: bool = True


@dataclass
class SystemConfig:
    """Main system configuration"""
    model: ModelConfig
    email: EmailConfig
    observability: ObservabilityConfig
    mcp_servers: Dict[str, str]
    
    @classmethod
    def from_env(cls) -> 'SystemConfig':
        """Create configuration from environment variables"""
        
        # Model configuration
        provider_str = os.getenv("MODEL_PROVIDER", "ollama").lower()
        provider = ModelProvider(provider_str)
        
        model_config = ModelConfig(
            provider=provider,
            model=os.getenv("OLLAMA_MODEL" if provider == ModelProvider.OLLAMA else f"{provider_str.upper()}_MODEL", "qwen2.5:latest"),
            api_key=os.getenv("OPENAI_API_KEY") if provider == ModelProvider.OPENAI else None,
            base_url=os.getenv("OLLAMA_BASE_URL" if provider == ModelProvider.OLLAMA else f"{provider_str.upper()}_BASE_URL"),
            temperature=float(os.getenv("MODEL_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("MODEL_MAX_TOKENS", "2000")),
            timeout=int(os.getenv("MODEL_TIMEOUT", "30"))
        )
        
        # Email configuration
        email_config = EmailConfig(
            smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            username=os.getenv("EMAIL_USER", ""),
            password=os.getenv("EMAIL_PASSWORD", ""),
            use_tls=os.getenv("EMAIL_USE_TLS", "true").lower() == "true",
            verify_ssl=os.getenv("EMAIL_VERIFY_SSL", "true").lower() == "true"
        )
        
        # Observability configuration
        observability_config = ObservabilityConfig(
            log_level=LogLevel(os.getenv("LOG_LEVEL", "INFO")),
            log_file=os.getenv("LOG_FILE", "agent_logs.log"),
            enable_tracing=os.getenv("ENABLE_TRACING", "true").lower() == "true",
            jaeger_endpoint=os.getenv("JAEGER_ENDPOINT"),
            enable_metrics=os.getenv("ENABLE_METRICS", "true").lower() == "true"
        )
        
        # MCP servers configuration
        mcp_servers = {
            "github": os.getenv("GITHUB_MCP_SERVER", ""),
            "ado": os.getenv("ADO_MCP_SERVER", ""),
            "filesystem": os.getenv("FILESYSTEM_MCP_SERVER", "")
        }
        
        return cls(
            model=model_config,
            email=email_config,
            observability=observability_config,
            mcp_servers=mcp_servers
        )
    
    def validate(self) -> bool:
        """Validate configuration"""
        errors = []
        
        # Validate model configuration
        if self.model.provider == ModelProvider.OPENAI and not self.model.api_key:
            errors.append("OpenAI API key is required when using OpenAI provider")
        
        if self.model.provider == ModelProvider.OLLAMA and not self.model.base_url:
            errors.append("Ollama base URL is required when using Ollama provider")
        
        # Validate email configuration
        if not self.email.username or not self.email.password:
            errors.append("Email username and password are required")
        
        if errors:
            for error in errors:
                logging.error(f"Configuration error: {error}")
            return False
        
        return True


# Global configuration instance
_config: Optional[SystemConfig] = None


def get_config() -> SystemConfig:
    """Get the global configuration instance"""
    global _config
    if _config is None:
        _config = SystemConfig.from_env()
        if not _config.validate():
            raise ValueError("Invalid configuration")
    return _config


def reset_config():
    """Reset the global configuration (mainly for testing)"""
    global _config
    _config = None
