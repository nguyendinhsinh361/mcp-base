"""
Tests for the combined functionality of all MCP servers.
"""
import os
import asyncio
from typing import Dict, List, Any

from app.core import settings, logger
from app.clients import CombinedMCPClient
from app.utils import ToolTracker
from langgraph.prebuilt import create_react_agent

async def test_combined_servers():
    """
    Test the combined functionality of all MCP servers (Math, Weather, GitHub)
    with tool usage tracking
    """
    print("=== Testing Combined MCP Servers With Tool Tracking ===")
    
    # Initialize the language model
    model = settings.get_model_instance()
    
    # Create a tool tracker
    tracker = ToolTracker("test_combined")
    # Connect to all MCP servers
    async with CombinedMCPClient() as client:
        # Get all tools from all servers        
        tools = client.get_tools()
        
        
        # Print all available tools
        print("\n📋 Available Tools:")
        for i, tool in enumerate(tools, 1):
            print(f"  {i}. {tool.name}: {tool.description}")
        
        # Wrap tools with tracking
        wrapped_tools = tracker.wrap_tools(tools)
        
        # Create the agent with the wrapped tools
        agent = create_react_agent(model, wrapped_tools)
        
        # Test cases combining different services
        test_cases = [
            # Math tests
            # "What is 28 divided by 4?",
            
            # Weather tests
            # "What's the weather in Tokyo?",
            
            # GitHub tests (these might be skipped if GitHub tools aren't available)
            "Summarize the last commit from nguyendinhsinh361/check-errror-ggsheet",
            
            # Combined tests (these use multiple services)
            "If it's 75°F in New York and 60°F in London, what's the average temperature? Please note average.",
            # "If there were 23 commits yesterday and 45 today, how many commits were there in total?",
            # "What is your name ?",
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