import os
import asyncio
import json
from typing import Dict, List, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
import sys

# Load environment variables
load_dotenv()

# Add parent directory to path to allow importing from clients
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the CombinedMCPClient from clients/multi_client.py
from clients.multi_client import CombinedMCPClient

# Tool tracker class to monitor which tools are being used
class ToolTracker:
    def __init__(self):
        self.tool_usage = {}
        self.last_used_tools = []
    
    def track_tool(self, tool_name, args=None):
        """Track when a tool is used"""
        if tool_name not in self.tool_usage:
            self.tool_usage[tool_name] = 0
        self.tool_usage[tool_name] += 1
        self.last_used_tools.append(tool_name)
        print(f"🔧 Tool called: {tool_name} with args: {args}")
    
    def get_used_tools(self):
        """Get summary of tools used"""
        return self.last_used_tools
    
    def clear(self):
        """Clear the last used tools for a new test"""
        self.last_used_tools = []

# Create a tracker instance
tracker = ToolTracker()

# Function to wrap tools with tracking
def wrap_tools_with_tracking(tools):
    """Wrap each tool with tracking functionality"""
    wrapped_tools = []
    
    for tool in tools:
        original_func = tool.func
        
        # Create a new function that wraps the original
        async def wrapped_func(*args, _original_func=original_func, _tool_name=tool.name, **kwargs):
            # Track the tool usage
            tracker.track_tool(_tool_name, args[1:] if len(args) > 1 else None)
            # Call the original function
            return await _original_func(*args, **kwargs)
        
        # Replace the original function with the wrapped one
        tool.func = wrapped_func
        wrapped_tools.append(tool)
    
    return wrapped_tools

async def test_combined_servers():
    """
    Test the combined functionality of all MCP servers (Math, Weather, GitHub)
    with tool usage tracking
    """
    print("=== Testing Combined MCP Servers With Tool Tracking ===")
    
    # Initialize the language model
    use_gemini = os.environ.get("USE_GEMINI", "false").lower() == "false"
    
    if use_gemini:
        print("Using Google Gemini model")
        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key=os.environ.get("GOOGLE_API_KEY"),
            temperature=0.3,
        )
    else:
        print("Using OpenAI GPT-4.1-nano model")
        model = ChatOpenAI(model="gpt-4.1-nano", api_key=os.environ.get("OPENAI_API_KEY"))
    
    # Connect to all MCP servers (SSE and stdio)
    async with CombinedMCPClient() as client:
        # Get all tools from all servers
        tools = client.get_tools()
        
        # Print all available tools
        print("\n📋 Available Tools:")
        for i, tool in enumerate(tools, 1):
            print(f"  {i}. {tool.name}: {tool.description}")
        
        # Wrap tools with tracking
        wrapped_tools = wrap_tools_with_tracking(tools)
        
        # Create the agent with the wrapped tools
        agent = create_react_agent(model, wrapped_tools)
        
        # Test cases combining different services
        test_cases = [
            # Math tests
            "What is 28 divided by 4?",
            
            # Weather tests
            "What's the weather in Tokyo?",
            
            # GitHub tests (these might be skipped if GitHub tools aren't available)
            "Summarize the last commit from nguyendinhsinh361/check-errror-ggsheet",
            "Summarize the all commit from nguyendinhsinh361/elevenlabs-mcp",
            
            # Combined tests (these use multiple services)
            # "If it's 75°F in New York and 60°F in London, what's the average temperature?",
            "If it's 75°F in New York and 60°F in London, what's the average temperature?. Please note average",
            "If there were 23 commits yesterday and 45 today, how many commits were there in total?"
        ]
        
        # Run all test cases
        for i, query in enumerate(test_cases, 1):
            print(f"\n{'='*50}")
            print(f"Test Case {i}: {query}")
            print(f"{'='*50}")
            
            # Clear tracker for new test
            tracker.clear()
            
            try:
                # Get the agent's response
                agent_response = await agent.ainvoke({"messages": [{"role": "user", "content": query}]})
                
                # Print the response
                response_message = agent_response["messages"][-1]
                print("\nResponse:", response_message.content)
                    
            except Exception as e:
                print(f"❌ Error during test: {e}")
    
    print("\n✅ Combined server tests completed")

if __name__ == "__main__":
    asyncio.run(test_combined_servers())