"""
SSE Client implementation for MCP Project.
"""
from typing import Dict, List, Any, Optional
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from app.clients.base import BaseMCPClient
from app.core import settings, ClientError

class SSEClient(BaseMCPClient):
    """Client for SSE-based MCP servers"""
    
    def __init__(self, name: str, url: str):
        """
        Initialize an SSE client
        
        Args:
            name: The client name
            url: The SSE endpoint URL
        """
        super().__init__(name)
        self.url = url
        self.client = None
    
    async def __aenter__(self):
        """Initialize the MCP client and connect to the server"""
        try:
            self.logger.info(f"Connecting to {self.name} server at {self.url}")
            self.client = MultiServerMCPClient(
                server_url=self.url,
                transport="sse"
            )
            await self.client.__aenter__()
            return self
        except Exception as e:
            self.logger.error(f"Failed to connect to {self.name} server: {e}")
            raise ClientError(f"Failed to connect to {self.name} server") from e
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up the client connection"""
        if self.client:
            try:
                await self.client.__aexit__(exc_type, exc_val, exc_tb)
            except Exception as e:
                self.logger.error(f"Error closing {self.name} client: {e}")
            self.client = None
    
    def get_tools(self) -> List[BaseTool]:
        """Get all tools from the SSE server"""
        if not self.client:
            raise ClientError(f"{self.name} client is not connected")
        
        from langchain_mcp_adapters.tools import load_mcp_tools
        try:
            self.logger.info(f"Loading tools from {self.name} server")
            self.tools = load_mcp_tools(self.client)
            self.logger.info(f"Loaded {len(self.tools)} tools from {self.name} server")
            return self.tools
        except Exception as e:
            self.logger.error(f"Failed to load tools from {self.name} server: {e}")
            raise ClientError(f"Failed to load tools from {self.name} server") from e


class MathClient(SSEClient):
    """Client for the Math MCP server"""
    
    def __init__(self):
        """Initialize the Math client with the default URL"""
        url = f"http://{settings.ip_host}:{settings.math_port}/sse"
        super().__init__("Math", url)


class WeatherClient(SSEClient):
    """Client for the Weather MCP server"""
    
    def __init__(self):
        """Initialize the Weather client with the default URL"""
        url = f"http://{settings.ip_host}:{settings.weather_port}/sse"
        super().__init__("Weather", url)
        