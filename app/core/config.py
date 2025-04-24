"""
Centralized configuration management for MCP Project.
Handles environment variables and server settings.
"""
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Configuration settings for the MCP project"""
    
    def __init__(self):
        # API Keys
        self.openai_api_key: str = os.environ.get("OPENAI_API_KEY", "")
        self.anthropic_api_key: str = os.environ.get("ANTHROPIC_API_KEY", "")
        self.google_api_key: str = os.environ.get("GOOGLE_API_KEY", "")
        self.groq_api_key: str = os.environ.get("GROQ_API_KEY", "")
        self.github_token: str = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN", "")
        
        # Model settings
        self.use_gemini: bool = os.environ.get("USE_GEMINI", False).lower() == False
        
        # Server settings
        self.ip_host: str = os.environ.get("IP_HOST", "localhost")
        self.weather_port: int = os.environ.get("WEATHER_PORT", 8000)
        self.math_port: int = os.environ.get("MATH_PORT", 8001)
        self.github_port: int = os.environ.get("GITHUB_PORT", 8002)
        
        # Server configurations for clients
        self._server_config = None
    
    @property
    def server_config(self) -> Dict[str, Dict[str, Any]]:
        """Get server configuration for multi-client"""
        if self._server_config is None:
            self._server_config = {
                "math": {
                    "url": f"http://{self.ip_host}:{self.math_port}/sse",
                    "transport": "sse",
                },
                "weather": {
                    "url": f"http://{self.ip_host}:{self.weather_port}/sse",
                    "transport": "sse",
                },
                "github": {
                    "url": f"http://{self.ip_host}:{self.github_port}/sse",
                    "transport": "sse",
                }
            }
            
            # Add GitHub server config if token is available
            # if self.github_token:
            #     self._server_config["github"] = {
            #         "command": "docker",
            #         "args": ["run", "--rm", "-e", f"GITHUB_PERSONAL_ACCESS_TOKEN={self.github_token}", "-i", "mcp/github"],
            #         "transport": "stdio",
            #         "env": {}
            #     }
                
        return self._server_config
    
    def validate(self) -> bool:
        """Validate that required configuration is present"""
        missing = []
        
        # Check for required API keys based on configuration
        if self.use_gemini and not self.google_api_key:
            missing.append("GOOGLE_API_KEY (required when USE_GEMINI=true)")
        elif not self.use_gemini and not self.openai_api_key:
            missing.append("OPENAI_API_KEY (required when USE_GEMINI=false)")
            
        if missing:
            print("Missing required environment variables:")
            for var in missing:
                print(f"  - {var}")
            return False
            
        return True
    
    def get_model_instance(self):
        """Get the appropriate language model instance based on configuration"""
        if self.use_gemini:
            print(11111, self.use_gemini)
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model="gemini-1.5-pro",
                google_api_key=self.google_api_key,
                temperature=0.3,
            )
        else:
            print(2222, self.use_gemini)
            
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model="gpt-4.1-nano", 
                api_key=self.openai_api_key,
                temperature=0.3
            )

# Create a global settings instance
settings = Settings()