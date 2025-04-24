"""
Weather MCP Server implementation.
Provides weather information tools.
"""
from app.servers.base import BaseMCPServer
from app.core import settings

class WeatherServer(BaseMCPServer):
    """MCP server for weather operations"""
    
    def __init__(self):
        """Initialize the Weather server with default port"""
        super().__init__("Weather", port=settings.weather_port)
        self._register_tools()
    
    def _register_tools(self) -> None:
        """Register all weather tools with the MCP server"""
        
        @self.mcp.tool()
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
            
            result = weather_data.get(location, f"Weather data not available for {location}")
            self.logger.info(f"get_weather({location}) - {result}")
            return result
        
        @self.mcp.tool()
        async def get_forecast(location: str, days: int = 3) -> str:
            """Get weather forecast for a location for the next N days."""
            # In a real implementation, you would call a weather API here
            forecast = f"{days}-day forecast for {location}: "
            
            # Dummy forecast data
            if location.lower() in ["new york", "nyc"]:
                forecast += "Sunny followed by partly cloudy conditions"
            elif location.lower() in ["london"]:
                forecast += "Rainy with occasional breaks"
            else:
                forecast += "Mixed conditions expected"
            
            self.logger.info(f"get_forecast({location}, {days}) - {forecast}")
            return forecast