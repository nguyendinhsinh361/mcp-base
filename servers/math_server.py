from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv
load_dotenv()

# Create FastMCP instance
mcp = FastMCP("Math")

# Override the default server settings to set a new port
mcp.settings.port = 8001  # Use port 8001 instead of 8000
mcp.settings.host = os.environ.get("IP_HOST")


# Define MCP Tools
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    print(f"add - {a + b}")
    
    return a + b

@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract b from a"""
    print(f"subtract - {a - b}")
    
    return a - b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    print(f"multiply - {a * b}")
    return a * b

@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide a by b"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    print(f"divide - {a / b}")
    return a / b

if __name__ == "__main__":
    # Start MCP Server on Port 8001 with SSE transport
    print("Starting Math MCP Server on port 8001...")
    mcp.run(transport="sse")