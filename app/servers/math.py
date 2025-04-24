"""
Math MCP Server implementation.
Provides basic math operations.
"""
from app.servers.base import BaseMCPServer
from app.core import settings, ToolError

class MathServer(BaseMCPServer):
    """MCP server for math operations"""
    
    def __init__(self):
        """Initialize the Math server with default port"""
        super().__init__("Math", port=settings.math_port)
        self._register_tools()
    
    def _register_tools(self) -> None:
        """Register all math tools with the MCP server"""
        
        @self.mcp.tool()
        def add(a: int, b: int) -> int:
            """
            Add two numbers together. 
            Use this when you need to find the sum of two values.
            Example: add(5, 3) returns 8
            """
            self.logger.info(f"add - {a + b}")
            return a + b
        
        @self.mcp.tool()
        def subtract(a: int, b: int) -> int:
            """Subtract b from a"""
            self.logger.info(f"subtract - {a - b}")
            return a - b
        
        @self.mcp.tool()
        def multiply(a: int, b: int) -> int:
            """Multiply two numbers"""
            self.logger.info(f"multiply - {a * b}")
            return a * b
        
        @self.mcp.tool()
        def divide(a: float, b: float) -> float:
            """
            Divide a by b and return the result.
            Use this when you need to:
            - Find the average of numbers (divide the sum by the count)
            - Calculate ratios or proportions
            - Perform division operations
            Example: To find the average of 10 and 20, first add them (30) then divide(30, 2) to get 15
            """
            if b == 0:
                error_msg = "Cannot divide by zero"
                self.logger.error(error_msg)
                raise ToolError("divide", error_msg)
            
            self.logger.info(f"divide - {a / b}")
            return a / b