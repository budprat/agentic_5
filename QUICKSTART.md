# Quick Start Guide

## Prerequisites
- Python 3.9+
- pip or uv package manager
- Unix-like environment (Linux/macOS)

## 1. Clone and Setup

```bash
# Clone the A2A-MCP Framework V2.0
git clone <your-repo> my-agent-system
cd my-agent-system

# Create environment file
cp .env.template .env
# Edit .env with your settings (API keys, ports, etc.)

# Optional: Enable V2.0 observability features
# Set ENABLE_OBSERVABILITY=true in .env
# Set OTEL_EXPORTER_OTLP_ENDPOINT for tracing
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

## 4. Create Your First Agent (Framework V2.0)

### Option A: Using Generic Domain Agent (Recommended for Quick Start)
```python
# src/a2a_mcp/agents/my_domain/my_agent.py
from a2a_mcp.common.generic_domain_agent import GenericDomainAgent

# Quick domain specialist creation
agent = GenericDomainAgent(
    domain="Finance",
    specialization="market_analyst",
    capabilities=["Analyze market trends", "Evaluate stocks"]
)
```

### Option B: Custom Agent with V2.0 Features
```python
# src/a2a_mcp/agents/my_domain/my_agent.py
from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.common.quality_framework import QualityDomain
from typing import Dict, Any

class MyAgent(StandardizedAgentBase):
    def __init__(self):
        super().__init__(
            agent_name="my_agent",
            description="My custom agent with V2.0 features",
            instructions="Process requests with quality validation",
            quality_config={
                "domain": QualityDomain.ANALYSIS,
                "thresholds": {"completeness": 0.9, "accuracy": 0.95}
            },
            mcp_tools_enabled=True,
            a2a_enabled=True,
            enable_observability=True  # V2.0 feature
        )
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        # V2.0: Automatic quality validation and observability
        result = await self._process_with_llm(request.get("query", ""))
        return self.format_response(result)  # V2.0: Standardized formatting
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

### Essential Documentation (V2.0)
- **[Framework Components Guide](docs/FRAMEWORK_COMPONENTS_AND_ORCHESTRATION_GUIDE.md)** - Complete component reference
- **[Multi-Agent Workflow Guide](docs/MULTI_AGENT_WORKFLOW_GUIDE.md)** - Step-by-step system creation
- **[A2A MCP Oracle Framework](docs/A2A_MCP_ORACLE_FRAMEWORK.md)** - Full framework reference

### Quick Start Options
1. **Simple System**: Use `LightweightMasterOrchestrator` + `GenericDomainAgent`
2. **Production System**: Use `EnhancedMasterOrchestratorTemplate` with all 7 phases
3. **Custom Domain**: Follow the Domain Customization Guide

### V2.0 Features to Explore
- **PHASE 7 Streaming**: Real-time execution visibility
- **Quality Framework**: Domain-specific validation
- **Observability**: OpenTelemetry tracing & Prometheus metrics
- **Parallel Workflows**: Automatic parallel execution
- **Connection Pooling**: 60% performance improvement

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