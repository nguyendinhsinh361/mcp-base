# MCP Project

A clean implementation of Model Context Protocol (MCP) servers and clients using both SSE and StdioServer approaches.

## Project Structure

```
mcp_project/
│
├── .env                  # Environment variables
├── requirements.txt      # Dependencies
├── README.md             # This file
│
├── servers/              # Server implementations
│   ├── math_server.py    # Math server using SSE
│   ├── weather_server.py # Weather server using SSE
│   └── github_server.py  # Info on Github server using stdio (Docker)
│
├── clients/              # Client implementations 
│   ├── sse_client.py     # Single SSE client
│   ├── multi_sse_client.py # Multi-server SSE client
│   └── stdio_client.py   # StdioServer client (Docker)
│
├── tests/                # Test suite
│   ├── test_math.py      # Math server tests
│   ├── test_weather.py   # Weather server tests
│   ├── test_github.py    # GitHub server tests
│   ├── test_combined.py  # Combined servers test
│   └── run_all_tests.py  # Test runner
│
└── utils/                # Helper utilities
    └── __init__.py       # Empty init file
```

## Getting Started

### 1. Set Up Environment

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root with the following keys:

```
OPENAI_API_KEY="your-openai-api-key"
ANTHROPIC_API_KEY="your-anthropic-api-key"
GOOGLE_API_KEY="your-google-api-key"  # Required for Gemini model
GROQ_API_KEY="your-groq-api-key"
GITHUB_PERSONAL_ACCESS_TOKEN="your-github-personal-access-token"
USE_GEMINI="true"  # Set to "true" to use Gemini, "false" to use OpenAI
```

### 3. Running SSE Servers

Start each server in a separate terminal:

```bash
# Start Math Server (Port 8001)
python servers/math_server.py

# Start Weather Server (Port 8000)
python servers/weather_server.py
```

### 4. Running Combined Client

After setting up all servers (including the GitHub Docker server), you can run the combined client:

```bash
# Combined client with all servers (Math, Weather, and GitHub)
python clients/multi_sse_client.py
```

This client connects to both SSE-based servers (Math and Weather) and the GitHub server via stdio transport simultaneously, giving you access to all tools in a single interface.

## Running Tests

The project includes a comprehensive test suite for all server types:

```bash
# Run all tests from the project root directory
python -m tests.run_all_tests

# Run specific tests
python -m tests.run_all_tests --tests math weather
python -m tests.run_all_tests --tests github
python -m tests.run_all_tests --tests combined

# Run individual test files
python -m tests.test_math
python -m tests.test_weather
python -m tests.test_github
python -m tests.test_combined
```

Make sure all servers are running before executing the tests:
1. Math server on port 8001
2. Weather server on port 8000
3. GitHub server via Docker (for github and combined tests)

### 5. Setting Up GitHub Server (Docker)

For the GitHub server:

1. Install Docker
2. Clone the MCP servers repository:
   ```bash
   git clone https://github.com/modelcontextprotocol/servers.git
   cd servers
   ```
3. Build the Docker image:
   ```bash
   docker build -t mcp/github -f src/github/Dockerfile .
   ```

### 6. Running StdioServer Client (GitHub)

After building the Docker image:

```bash
# Run the GitHub client
python clients/stdio_client.py
```

## Key Concepts

### SSE (Server-Sent Events)

- Used for real-time communication over HTTP
- Servers run as web services on specific ports
- Clients connect via HTTP to the server endpoints
- Multiple servers can run simultaneously on different ports

### StdioServer (stdio)

- Used for communication via standard input/output
- Commonly used with Docker containers or external processes
- Useful for integrating with existing tools and services
- In this project, used for the GitHub MCP server

## Understanding the Code

### Servers
- Create a FastMCP instance with a name
- Define tools as Python functions with decorators
- Specify transport type when running the server

### Clients
- Connect to servers using appropriate client classes
- Load tools from the servers
- Create a ReAct agent using the loaded tools
- Submit questions to the agent

## Resources

- [LangChain MCP Adapters](https://github.com/langchain-ai/langchain-mcp-adapters)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [Model Context Protocol](https://modelcontextprotocol.github.io/)
- [MCP GitHub Server](https://github.com/modelcontextprotocol/servers/blob/main/src/github/README.md)