"""
StdIO Client implementation for MCP Project.
"""
from typing import Dict, List, Any, Optional
from langchain_core.tools import BaseTool
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.clients.base import BaseMCPClient
from app.core import settings, ClientError

class StdioClient(BaseMCPClient):
    """Client for stdio-based MCP servers (like GitHub)"""
    
    def __init__(self, name: str, command: str, args: List[str], env: Optional[Dict[str, str]] = None):
        """
        Initialize a stdio client
        
        Args:
            name: The client name
            command: The command to run
            args: Command arguments
            env: Environment variables
        """
        super().__init__(name)
        self.command = command
        self.args = args
        self.env = env or {}
        
        # StdIO specific variables
        self.stdio_client_ctx = None
        self.stdio_session = None
        self.stdio_read = None
        self.stdio_write = None
    
    async def __aenter__(self):
        """Initialize the stdio client and connect to the server"""
        try:
            self.logger.info(f"Starting {self.name} server process")
            
            # Set up the stdio client context
            server_params = StdioServerParameters(
                command=self.command,
                args=self.args,
                env=self.env
            )
            
            self.stdio_client_ctx = stdio_client(server_params)
            self.stdio_read, self.stdio_write = await self.stdio_client_ctx.__aenter__()
            
            # Create a client session
            self.stdio_session = ClientSession(self.stdio_read, self.stdio_write)
            await self.stdio_session.__aenter__()
            
            return self
        except Exception as e:
            self.logger.error(f"Failed to start {self.name} server process: {e}")
            await self._cleanup()
            raise ClientError(f"Failed to start {self.name} server process") from e
    
    async def _cleanup(self):
        """Clean up resources in reverse order"""
        if self.stdio_session:
            try:
                await self.stdio_session.__aexit__(None, None, None)
            except Exception as e:
                self.logger.error(f"Error closing stdio session: {e}")
            self.stdio_session = None
        
        if self.stdio_client_ctx:
            try:
                await self.stdio_client_ctx.__aexit__(None, None, None)
            except Exception as e:
                self.logger.error(f"Error closing stdio client: {e}")
            self.stdio_client_ctx = None
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up the client connection"""
        await self._cleanup()
    
    def get_tools(self) -> List[BaseTool]:
        """Get all tools from the stdio server"""
        if not self.stdio_session:
            raise ClientError(f"{self.name} client is not connected")
        
        from langchain_mcp_adapters.tools import load_mcp_tools
        try:
            self.logger.info(f"Loading tools from {self.name} server")
            self.tools = load_mcp_tools(self.stdio_session)
            self.logger.info(f"Loaded {len(self.tools)} tools from {self.name} server")
            return self.tools
        except Exception as e:
            self.logger.error(f"Failed to load tools from {self.name} server: {e}")
            raise ClientError(f"Failed to load tools from {self.name} server") from e


class GitHubClient(StdioClient):
    """Client for the GitHub MCP server via Docker"""
    
    def __init__(self):
        """Initialize the GitHub client with Docker parameters"""
        if not settings.github_token:
            raise ClientError("GitHub client requires GITHUB_PERSONAL_ACCESS_TOKEN to be set")
        
        command = "docker"
        args = [
            "run", 
            "--rm", 
            "-e", 
            f"GITHUB_PERSONAL_ACCESS_TOKEN={settings.github_token}", 
            "-i", 
            "mcp/github"
        ]
        
        super().__init__("GitHub", command, args)