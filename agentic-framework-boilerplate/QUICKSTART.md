# Quick Start Guide

## Prerequisites
- Python 3.9+
- pip or uv package manager
- Unix-like environment (Linux/macOS)

## 1. Clone and Setup

```bash
# Clone the boilerplate
git clone <your-repo> my-agent-system
cd my-agent-system

# Create environment file
cp .env.template .env
# Edit .env with your settings
```

## 2. Start the System

```bash
# Make scripts executable
chmod +x start.sh stop.sh run_tests.sh

# Start all services
./start.sh

# The system will:
# - Create virtual environment
# - Install dependencies
# - Start MCP server on port 10099
# - Launch example agents
# - Begin health monitoring
```

## 3. Test the System

```bash
# In another terminal
cd examples
python simple_client.py

# Or run the test suite
./run_tests.sh
```

## 4. Create Your First Agent

```python
# src/a2a_mcp/agents/my_domain/my_agent.py
from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from typing import Dict, Any

class MyAgent(StandardizedAgentBase):
    def __init__(self):
        super().__init__(
            agent_name="my_agent",
            description="My custom agent",
            instructions="Process requests in my domain",
            quality_config={"domain": "GENERIC"},
            mcp_tools_enabled=True,
            a2a_enabled=True
        )
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        # Your logic here
        result = await self._process_with_llm(request.get("query", ""))
        return {
            "status": "success",
            "result": result,
            "confidence": 0.95
        }
```

## 5. Create Agent Card

```json
// agent_cards/tier2/my_agent.json
{
    "agent_id": "my_agent",
    "name": "My Custom Agent",
    "description": "Processes domain-specific requests",
    "tier": 2,
    "port": 10250,
    "host": "localhost",
    "version": "1.0.0",
    "status": "active",
    "capabilities": ["process", "analyze"],
    "dependencies": [],
    "mcp_enabled": true,
    "a2a_enabled": true,
    "quality_domain": "GENERIC",
    "instructions": "Process requests accurately and efficiently"
}
```

## 6. Add to Launch Script

Edit `launch/launch_system.py` to include your agent:

```python
# In start_tier2_agents()
agents_to_start = [
    ("search_agent", 10201),
    ("summarization_agent", 10202),
    ("my_agent", 10250),  # Add your agent
]
```

## 7. Restart System

```bash
./stop.sh
./start.sh
```

## Next Steps

- Read [ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design
- Explore example agents in `src/a2a_mcp/agents/example_domain/`
- Add custom MCP tools in `src/a2a_mcp/mcp/server.py`
- Configure quality rules for your domain
- Set up monitoring and logging

## Common Commands

```bash
# Stop all services
./stop.sh

# Run tests
./run_tests.sh

# Check agent health
curl http://localhost:10099/health

# View logs
tail -f logs/mcp_server.log
tail -f logs/agents/*.log
```

## Troubleshooting

1. **Port already in use**: Change ports in agent cards and .env
2. **Import errors**: Ensure virtual environment is activated
3. **Agent not responding**: Check logs and health endpoint
4. **MCP tools not available**: Verify MCP server is running

## Support

- Check [README.md](README.md) for detailed documentation
- Review [examples/](examples/) for usage patterns
- See [tests/](tests/) for testing approaches