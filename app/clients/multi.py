"""
Multi-Server Client implementation for MCP Project.
Combines multiple MCP servers into a single client.
"""
from typing import Dict, List, Any, Optional
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from app.clients.base import BaseMCPClient
from app.core import settings, logger, ClientError

class CombinedMCPClient(BaseMCPClient):
    """
    A wrapper class that combines multiple MCP clients
    to provide a unified set of tools from multiple servers.
    """
    
    def __init__(self, servers: Optional[List[str]] = None):
        """
        Initialize a combined MCP client
        
        Args:
            servers: List of server names to connect to (default: all available)
        """
        super().__init__("Combined")
        self.client = None
        self.combined_tools = []
        self.servers = servers or ["math", "weather", "github"]
        
        # Filter out GitHub if no token is available
        if "github" in self.servers and not settings.github_token:
            self.logger.warning("GitHub server requires GITHUB_PERSONAL_ACCESS_TOKEN, which is not set")
            self.servers.remove("github")
            
        self.logger.info(f"Initializing Combined MCP Client with servers: {', '.join(self.servers)}")
    
    async def __aenter__(self):
        """Connect to all configured MCP servers"""
        try:
            # Build server configuration based on the requested servers
            server_config = {}
            
            for server in self.servers:
                if server in settings.server_config:
                    server_config[server] = settings.server_config[server]
            
            if not server_config:
                raise ClientError("No valid servers configured")
                
            # Initialize the MultiServerMCPClient
            self.client = MultiServerMCPClient(server_config) 
            await self.client.__aenter__()
            print(self)
            return self
        except Exception as e:
            self.logger.error(f"Failed to connect to MCP servers: {e}")
            if self.client:
                await self.client.__aexit__(None, None, None)
                self.client = None
            raise ClientError(f"Failed to connect to MCP servers") from e
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up all client connections"""
        if self.client:
            try:
                await self.client.__aexit__(exc_type, exc_val, exc_tb)
            except Exception as e:
                self.logger.error(f"Error closing Combined client: {e}")
            self.client = None
    
    def get_tools(self) -> List[BaseTool]:
        """Get tools from all connected servers"""
        if not self.client:
            raise ClientError("Combined client is not connected")
        
        try:
            self.combined_tools = self.client.get_tools()
            
            # Log information about loaded tools
            tool_counts = {}
            for tool in self.combined_tools:
                server_name = tool.name.split("_")[0] if "_" in tool.name else "unknown"
                if server_name not in tool_counts:
                    tool_counts[server_name] = 0
                tool_counts[server_name] += 1
                
            for server, count in tool_counts.items():
                self.logger.info(f"Loaded {count} tools from {server} server")
                
            self.logger.info(f"Total tools loaded: {len(self.combined_tools)}")
            return self.combined_tools
        except Exception as e:
            self.logger.error(f"Failed to get tools from servers: {e}")
            raise ClientError(f"Failed to get tools from servers") from e

async def create_agent(model=None):
    """
    Create a ReAct agent with tools from all servers
    
    Args:
        model: An optional language model instance
              (default: use the one from settings)
              
    Returns:
        A ReAct agent instance
    """
    from langgraph.prebuilt import create_react_agent
    
    # Use the provided model or get from settings
    if model is None:
        model = settings.get_model_instance()
        
    async with CombinedMCPClient() as client:
        tools = client.get_tools()
        agent = create_react_agent(model, tools)
        return agent