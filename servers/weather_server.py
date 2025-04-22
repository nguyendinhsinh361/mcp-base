from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv
load_dotenv()

# Create FastMCP instance
mcp = FastMCP("Weather")

mcp.settings.port = 8000
mcp.settings.host = os.environ.get("IP_HOST")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for a location."""
    # In a real implementation, you would call a weather API here
    weather_data = {
        "New York": "Sunny, 75°F",
        "London": "Rainy, 60°F",
        "Tokyo": "Cloudy, 70°F",
        "Paris": "Partly Cloudy, 65°F",
        "Sydney": "Clear, 80°F"
    }
    
    return weather_data.get(location, f"Weather data not available for {location}")

@mcp.tool()
async def get_forecast(location: str, days: int = 3) -> str:
    """Get weather forecast for a location for the next N days."""
    # In a real implementation, you would call a weather API here
    forecast = f"{days}-day forecast for {location}: "
    
    # Dummy forecast data
    if location.lower() in ["new york", "nyc"]:
        return forecast + "Sunny followed by partly cloudy conditions"
    elif location.lower() in ["london"]:
        return forecast + "Rainy with occasional breaks"
    else:
        return forecast + "Mixed conditions expected"

if __name__ == "__main__":
    # Start MCP Server on default Port 8000 with SSE transport
    print("Starting Weather MCP Server on port 8000...")
    mcp.run(transport="sse")