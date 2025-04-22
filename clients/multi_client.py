import os
import asyncio
from typing import Dict, List, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent

# Load environment variables
load_dotenv()

class CombinedMCPClient:
    """
    A wrapper class that combines SSE and stdio MCP clients
    to provide a unified set of tools from multiple servers.
    """
    
    def __init__(self):
        self.client = None
        self.stdio_session = None
        self.stdio_read = None
        self.stdio_write = None
        self.stdio_client_ctx = None
        self.combined_tools = []
        self.github_token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
        self.ip_host = os.environ.get("IP_HOST")
    
    async def __aenter__(self):
        # Initialize the SSE client for math and weather servers
        try:
            use_github = bool(self.github_token)
            server_config = {
                    "math": {
                        "url": f"http://{self.ip_host}:8001/sse",
                        "transport": "sse",
                    },
                    "weather": {
                        "url": f"http://{self.ip_host}:8000/sse",
                        "transport": "sse",
                    },
                    "github": {
                        "command": "docker",
                        "args": ["run", "--rm", "-e", f"GITHUB_PERSONAL_ACCESS_TOKEN={self.github_token}", "-i", "mcp/github"],
                        "transport": "stdio",
                        "env": {}
                    }
                }
            self.client = MultiServerMCPClient(
                server_config
            )
            
            await self.client.__aenter__()
            # Get SSE tools and add them to combined tools
            tools = self.client.get_tools()
            self.combined_tools.extend(tools)
            print("Tools loaded successfully")
            
        except Exception as e:
            print(f"Failed to connect to SSE servers: {e}")
            print("Make sure Math server (port 8001) and Weather server (port 8000) are running")
            
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Clean up in reverse order
        errors = []
        
        # Clean up stdio session
        if self.stdio_session:
            try:
                await self.stdio_session.__aexit__(exc_type, exc_val, exc_tb)
            except Exception as e:
                errors.append(f"Error closing stdio session: {e}")
            self.stdio_session = None
        
        # Clean up stdio client
        if self.stdio_client_ctx:
            try:
                await self.stdio_client_ctx.__aexit__(exc_type, exc_val, exc_tb)
            except Exception as e:
                errors.append(f"Error closing stdio client: {e}")
            self.stdio_client_ctx = None
        
        # Clean up Multiple client
        if self.client:
            try:
                await self.client.__aexit__(exc_type, exc_val, exc_tb)
            except Exception as e:
                errors.append(f"Error closing SSE client: {e}")
            self.client = None
        
        if errors:
            print("Errors during cleanup:")
            for error in errors:
                print(f"  - {error}")
    
    def get_tools(self):
        """Get all tools from both SSE and stdio clients"""
        # print(self.combined_tools)
        return self.combined_tools