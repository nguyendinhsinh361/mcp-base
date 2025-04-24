"""
Tool usage tracking utilities for MCP Project.
"""
from typing import List, Dict, Any, Optional, Callable
from langchain_core.tools import BaseTool
import functools

from app.core import logger

class ToolTracker:
    """Track tool usage within the MCP system"""
    
    def __init__(self, name: str = "default"):
        """
        Initialize a tool tracker
        
        Args:
            name: The tracker instance name
        """
        self.name = name
        self.tool_usage = {}
        self.last_used_tools = []
        self.logger = logger.getChild(f"tracker.{name}")
    
    def track_tool(self, tool_name: str, args: Optional[Any] = None) -> None:
        """
        Track when a tool is used
        
        Args:
            tool_name: The name of the tool that was used
            args: The arguments passed to the tool
        """
        if tool_name not in self.tool_usage:
            self.tool_usage[tool_name] = 0
        self.tool_usage[tool_name] += 1
        self.last_used_tools.append(tool_name)
        self.logger.info(f"Tool called: {tool_name} with args: {args}")
    
    def get_used_tools(self) -> List[str]:
        """
        Get list of tools used in sequence
        
        Returns:
            List[str]: Sequence of tool names used
        """
        return self.last_used_tools
    
    def get_tool_usage_stats(self) -> Dict[str, int]:
        """
        Get statistics about tool usage
        
        Returns:
            Dict[str, int]: Dictionary mapping tool names to usage counts
        """
        return self.tool_usage
    
    def clear(self) -> None:
        """Clear the tracking data for a new session"""
        self.last_used_tools = []
        # Keep the total usage stats
    
    def reset(self) -> None:
        """Completely reset all tracking data"""
        self.tool_usage = {}
        self.last_used_tools = []
    
    def wrap_tools(self, tools: List[BaseTool]) -> List[BaseTool]:
        """
        Wrap all tools with tracking functionality
        
        Args:
            tools: List of tools to wrap
            
        Returns:
            List[BaseTool]: Wrapped tools
        """
        wrapped_tools = []
        
        for tool in tools:
            # Store the original function
            original_func = tool.func
            tool_name = tool.name
            
            # Create the wrapper function
            @functools.wraps(original_func)
            async def wrapped_func(*args, _original_func=original_func, _tool_name=tool_name, **kwargs):
                # Track the tool usage
                self.track_tool(_tool_name, args[1:] if len(args) > 1 else None)
                # Call the original function
                return await _original_func(*args, **kwargs)
            
            # Replace the function with the wrapped one
            tool.func = wrapped_func
            wrapped_tools.append(tool)
        
        self.logger.info(f"Wrapped {len(wrapped_tools)} tools with tracking")
        return wrapped_tools

# Create a default tracker instance
default_tracker = ToolTracker()