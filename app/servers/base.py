"""
Base server classes for MCP Project.
"""
from typing import Optional, Dict, Any, List, Callable
from mcp.server.fastmcp import FastMCP
import asyncio

from app.core import settings, logger, ServerError

class BaseMCPServer:
    """Base class for MCP servers"""
    
    def __init__(self, name: str, port: Optional[int] = None, host: Optional[str] = None):
        """
        Initialize a base MCP server
        
        Args:
            name: The server name
            port: The port to use (optional)
            host: The host to bind to (optional)
        """
        self.name = name
        self.mcp = FastMCP(name)
        
        # Configure the server
        if port is not None:
            # Chuyển đổi port thành số nguyên
            self.mcp.settings.port = int(port)
        
        if host is not None:
            self.mcp.settings.host = host
        else:
            self.mcp.settings.host = settings.ip_host
        
        self.port = self.mcp.settings.port
        self.host = self.mcp.settings.host
        self.logger = logger.getChild(f"server.{name.lower()}")
    
    def run(self, transport: str = "sse") -> None:
        """
        Run the MCP server
        
        Args:
            transport: The transport type to use ("sse" or "stdio")
        """
        try:
            self.logger.info(f"Starting {self.name} MCP Server on port {self.port}...")
            self.mcp.run(transport=transport)
        except Exception as e:
            self.logger.error(f"Failed to start {self.name} server: {e}")
            raise ServerError(f"Failed to start {self.name} server") from e