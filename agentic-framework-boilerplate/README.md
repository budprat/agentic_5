# A2A MCP Framework - Agentic Framework Boilerplate

A production-ready framework for building sophisticated multi-agent systems with seamless tool integration via the Model Context Protocol (MCP).

## 🚀 Overview

The A2A MCP Framework provides a structured approach to building collaborative AI agent systems that can work together to solve complex problems. Built with enterprise-grade quality standards, this framework enables developers to create scalable agent systems that integrate with any MCP-compatible tools.

## ✨ Key Features

### 🏗️ Tiered Agent Architecture
- **Tier 1 (Master Agents)**: High-level orchestration and planning
- **Tier 2 (Domain Specialists)**: Specialized knowledge and task execution
- **Tier 3 (Service Agents)**: Direct tool integration and atomic operations

### 🔗 Agent-to-Agent (A2A) Protocol
- Standardized JSON-RPC based communication
- Asynchronous message passing with SSE support
- Built-in error handling and retry mechanisms
- Full context preservation across interactions

### 🛠️ Model Context Protocol (MCP) Integration
- Connect to any MCP-compatible tool server
- Dynamic tool discovery and registration
- Unified interface for diverse tool ecosystems
- Support for custom MCP implementations

### 📊 Quality & Reliability
- Comprehensive test coverage
- Built-in performance monitoring
- Graceful error recovery
- Structured logging and debugging

## 🚦 Quick Start

### Prerequisites
- Python 3.9+
- Git

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd agentic-framework-boilerplate

# Run the setup script
./start.sh
```

The setup script will:
- Create a virtual environment
- Install all dependencies
- Set up necessary directories
- Start the MCP server
- Launch example agents

### Basic Usage

```python
# Example: Using the client to interact with agents
python examples/simple_client.py

# Or run in interactive chat mode
python examples/simple_client.py chat
```

## 📁 Project Structure

```
agentic-framework-boilerplate/
├── src/
│   └── a2a_mcp/
│       ├── common/          # Shared utilities and base classes
│       ├── agents/          # Agent implementations
│       │   ├── example_domain/  # Domain-specific example agents
│       │   └── examples/        # Simple example agents
│       ├── clients/         # Client implementations
│       └── mcp/            # MCP server and integration
├── tests/                   # Test suite
├── examples/               # Example implementations
├── agent_cards/            # Agent capability definitions
├── configs/                # Configuration files
└── docs/                   # Documentation
```

## 🔧 Configuration

1. Copy `.env.template` to `.env`:
```bash
cp .env.template .env
```

2. Update the configuration values as needed:
```env
# Logging level
A2A_LOG_LEVEL=INFO

# MCP Server settings
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=10100

# Add your API keys if needed
# OPENAI_API_KEY=your_key_here
```

## 🧪 Testing

Run the test suite with coverage:

```bash
./run_tests.sh
```

## 🏭 Creating Your Own Agents

### 1. Define an Agent Card

Create a JSON file in `agent_cards/`:

```json
{
  "agent_id": "my_agent",
  "name": "My Custom Agent",
  "description": "Description of what your agent does",
  "capabilities": ["capability1", "capability2"],
  "tier": 2,
  "dependencies": {
    "tier_3_agents": ["tool_agent_1", "tool_agent_2"]
  }
}
```

### 2. Implement the Agent

Create your agent class extending `BaseAgent`:

```python
from a2a_mcp.common.base_agent import BaseAgent

class MyCustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="my_agent",
            name="My Custom Agent",
            description="What this agent does",
            capabilities=["capability1", "capability2"]
        )
    
    async def process_request(self, message: dict) -> dict:
        # Your agent logic here
        action = message.get("action")
        
        if action == "my_action":
            # Process the action
            return {"result": "success", "data": {...}}
        
        return {"error": "Unknown action"}
```

### 3. Register and Run

Add your agent to the system and start it:

```python
# In your launch script
agent = MyCustomAgent()
await agent.start(port=10201)
```

## 🔌 MCP Tool Integration

The framework supports any MCP-compatible tool. To add a new tool:

1. Ensure the MCP server is configured to access your tool
2. Tools are automatically available to all agents
3. Use the tool through the MCP client interface

Example:
```python
# Tools are accessed through the MCP integration
result = await self.mcp_client.call_tool(
    "tool_name",
    parameters={"param": "value"}
)
```

## 📚 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Quick Start Guide](docs/QUICK_START.md)
- [API Reference](docs/README.md)

## 📦 Example Agents

The framework includes several example agents to help you get started:

### Simple Examples (`src/a2a_mcp/agents/examples/`)
- **SearchAgent**: Demonstrates web search capabilities using MCP tools
- **SummarizationAgent**: Shows text processing with quality validation
- **DataValidationAgent**: Illustrates data validation with custom rules

### Domain Examples (`src/a2a_mcp/agents/example_domain/`)
- **MasterOracleAgent**: Tier 1 orchestrator showing A2A coordination
- **ResearchSpecialistAgent**: Tier 2 domain expert with quality checks
- **ServiceAgent**: Tier 3 service agent with tool integration

## 🛑 Stopping the System

To gracefully shut down all agents and the MCP server:

```bash
./stop.sh
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

Built with the Model Context Protocol (MCP) by Anthropic and inspired by modern agent architectures.