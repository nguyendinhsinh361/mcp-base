"""
Base client classes for MCP Project.
"""
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from langchain_core.tools import BaseTool

from app.core import logger, ClientError

class BaseMCPClient(ABC):
    """Abstract base class for MCP clients"""
    
    def __init__(self, name: str):
        """
        Initialize a base MCP client
        
        Args:
            name: The client name
        """
        self.name = name
        self.logger = logger.getChild(f"client.{name.lower()}")
        self.tools = []
    
    @abstractmethod
    async def __aenter__(self):
        """Async context manager entry point"""
        pass
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit point"""
        pass
    
    @abstractmethod
    def get_tools(self) -> List[BaseTool]:
        """
        Get all tools from the client
        
        Returns:
            List[BaseTool]: List of LangChain tools
        """
        pass