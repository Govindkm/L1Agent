"""
General settings and configuration for the multi-agent system.
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class Settings:
    """Global settings for the multi-agent system"""
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    
    # Ollama Configuration  
    ollama_base_url: str = "http://localhost:11434"
    
    # Weather API Configuration
    weather_api_key: Optional[str] = None
    
    # Email Configuration
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    email_user: Optional[str] = None
    email_password: Optional[str] = None
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "agent_logs.log"
    
    def __post_init__(self):
        """Load settings from environment variables if not provided"""
        if self.openai_api_key is None:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if self.weather_api_key is None:
            self.weather_api_key = os.getenv("WEATHER_API_KEY")
        
        if self.email_user is None:
            self.email_user = os.getenv("EMAIL_USER")
        
        if self.email_password is None:
            self.email_password = os.getenv("EMAIL_PASSWORD")
        
        # Override with environment variables if they exist
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", self.ollama_base_url)
        self.smtp_server = os.getenv("SMTP_SERVER", self.smtp_server)
        self.smtp_port = int(os.getenv("SMTP_PORT", str(self.smtp_port)))
        self.log_level = os.getenv("LOG_LEVEL", self.log_level)
        self.log_file = os.getenv("LOG_FILE", self.log_file)
    
    def validate(self) -> dict:
        """Validate configuration and return status"""
        validation = {
            "openai_available": bool(self.openai_api_key),
            "weather_available": bool(self.weather_api_key),
            "email_available": bool(self.email_user and self.email_password),
            "ollama_configured": bool(self.ollama_base_url)
        }
        return validation
    
    def print_status(self):
        """Print configuration status"""
        validation = self.validate()
        
        print("🔧 SYSTEM CONFIGURATION STATUS")
        print("=" * 40)
        print(f"🤖 OpenAI API: {'✅ Configured' if validation['openai_available'] else '❌ Missing API key'}")
        print(f"🦙 Ollama: {'✅ Configured' if validation['ollama_configured'] else '❌ Not configured'}")
        print(f"   Base URL: {self.ollama_base_url}")
        print(f"🌤️ Weather API: {'✅ Configured' if validation['weather_available'] else '❌ Missing API key'}")
        print(f"📧 Email: {'✅ Configured' if validation['email_available'] else '❌ Missing credentials'}")
        print(f"📋 Logging: {self.log_level} → {self.log_file}")


# Global settings instance
_global_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance"""
    global _global_settings
    if _global_settings is None:
        _global_settings = Settings()
    return _global_settings


def reload_settings() -> Settings:
    """Reload settings from environment"""
    global _global_settings
    _global_settings = Settings()
    return _global_settings


if __name__ == "__main__":
    # Demo the settings
    settings = get_settings()
    settings.print_status()
