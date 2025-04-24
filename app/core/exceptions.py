"""
Custom exceptions for MCP Project.
"""

class MCPError(Exception):
    """Base exception for all MCP-related errors"""
    pass

class ServerError(MCPError):
    """Raised when there's an error with MCP servers"""
    pass

class ClientError(MCPError):
    """Raised when there's an error with MCP clients"""
    pass

class ConfigurationError(MCPError):
    """Raised when there's an issue with configuration"""
    pass

class ToolError(MCPError):
    """Raised when there's an error with a specific tool"""
    
    def __init__(self, tool_name: str, message: str):
        self.tool_name = tool_name
        self.message = message
        super().__init__(f"Error in tool '{tool_name}': {message}")