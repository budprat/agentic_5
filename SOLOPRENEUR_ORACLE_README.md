# AI Solopreneur Oracle System

A comprehensive 56-agent multi-tier system built on the A2A-MCP framework, designed specifically for AI developers and entrepreneurs.

## System Overview

The Solopreneur Oracle implements a sophisticated 3-tier architecture:

### Tier 1: Oracle Master (1 agent)
- **Port 10901**: SolopreneurOracle Master Agent
  - Orchestrates all domain specialists
  - Synthesizes cross-domain insights
  - Provides executive-level recommendations

### Tier 2: Domain Specialists (5 agents)
- **Port 10902**: Technical Intelligence Oracle
- **Port 10903**: Knowledge Management Oracle  
- **Port 10904**: Personal Optimization Oracle
- **Port 10905**: Learning Enhancement Oracle
- **Port 10906**: Integration Synthesis Oracle

### Tier 3: Intelligence Modules (50 agents)
- **Ports 10910-10919**: Technical Intelligence (10 modules)
- **Ports 10920-10929**: Knowledge Systems (10 modules)
- **Ports 10930-10939**: Personal Systems (10 modules)
- **Ports 10940-10949**: Learning Systems (10 modules)
- **Ports 10950-10959**: Integration Layer (10 modules)

## Quick Start

### 1. Prerequisites
```bash
# Required
export GOOGLE_API_KEY="your-gemini-api-key"

# Optional (copy and edit config template)
cp solopreneur_config.env.template solopreneur_config.env
# Edit solopreneur_config.env with your settings
```

### 2. Initialize Database
```bash
# Create database
sqlite3 databases/solopreneur.db < databases/solopreneur_database_schema.sql

# Initialize sample data (if available)
python init_solopreneur_data.py
```

### 3. Start the System
```bash
# Start all 56 agents
./run_all_solopreneur_agents.sh

# Check system status
./check_solopreneur_status.sh

# View logs
tail -f logs/agent_10901.log  # Oracle Master
tail -f logs/mcp_server.log   # MCP Server
```

### 4. Test the System
```bash
# Run integration tests
python test_solopreneur_integration.py

# Quick health check only
python test_solopreneur_integration.py --quick

# Test with client
python clients/solopreneur_client.py
```

### 5. Stop the System
```bash
./stop_solopreneur_agents.sh
```

## Architecture Details

### File Structure
```
/home/solopreneur/
├── src/a2a_mcp/agents/solopreneur_oracle/
│   ├── __init__.py                      # Module initialization
│   ├── base_solopreneur_agent.py       # Base class for all agents
│   ├── agent_registry.py               # Registry of all 56 agents
│   └── solopreneur_oracle_agent.py     # Original oracle implementation
├── agent_cards/
│   ├── tier1/                          # 1 Master Oracle card
│   ├── tier2/                          # 5 Domain Specialist cards
│   └── tier3/                          # 50 Intelligence Module cards
├── databases/
│   └── solopreneur_database_schema.sql # Database schema
├── clients/
│   └── solopreneur_client.py          # Client implementation
└── logs/                               # Agent logs directory
```

### Key Components

#### UnifiedSolopreneurAgent
Base class that powers all 56 agents with tier-specific behavior:
- Tier 1: Multi-domain orchestration
- Tier 2: Domain coordination with modules
- Tier 3: Specialized analysis

#### Agent Registry
Central registry (`agent_registry.py`) containing:
- Agent definitions with ports and descriptions
- Instructions for each agent
- Factory function for agent creation

#### MCP Integration
- Tools defined in `solopreneur_mcp_tools.py`
- Database queries, external APIs, analysis tools
- Integrated via `server_solopreneur_patch.py`

## Usage Examples

### Technical Intelligence Query
```python
query = "Analyze the latest LangGraph patterns for multi-agent systems"
# Activates: Technical Intelligence Oracle + AI Research Analyzer
```

### Personal Optimization Query
```python
query = "Optimize my daily schedule based on energy patterns"
# Activates: Personal Optimization Oracle + Energy Pattern Analyzer
```

### Cross-Domain Query
```python
query = "How can I learn Rust efficiently given my energy patterns?"
# Activates: Learning + Personal + Integration domains
```

## Monitoring & Debugging

### Check Agent Status
```bash
# Full system check
./check_solopreneur_status.sh

# Check specific tier
curl http://localhost:10901/health  # Tier 1
curl http://localhost:10902/health  # Tier 2 example
curl http://localhost:10910/health  # Tier 3 example
```

### View Logs
```bash
# All logs are in logs/ directory
ls -la logs/

# Monitor specific agent
tail -f logs/agent_10901.log

# Search for errors
grep ERROR logs/*.log
```

### Debug Tips
1. Check MCP server is running first
2. Verify GOOGLE_API_KEY is set
3. Ensure database exists
4. Check agent cards are in correct locations
5. Monitor logs for startup errors

## Performance Tuning

### Configuration Options
```bash
# In solopreneur_config.env
export MAX_CONCURRENT_AGENTS="10"     # Limit concurrent agents
export AGENT_STARTUP_DELAY="0.1"      # Delay between starts
export ENABLE_PARALLEL_EXECUTION="true" # Enable parallel processing
```

### Resource Management
- Each agent runs in its own process
- Typical memory: ~100MB per agent
- CPU: Minimal when idle, spikes during processing
- Network: Requires ports 10100, 10901-10959

## Troubleshooting

### Common Issues

1. **"GOOGLE_API_KEY not set"**
   ```bash
   export GOOGLE_API_KEY="your-key"
   ```

2. **"Port already in use"**
   ```bash
   # Check what's using the port
   lsof -i:10901
   ```

3. **"Database not found"**
   ```bash
   # Create database
   mkdir -p databases
   sqlite3 databases/solopreneur.db < databases/solopreneur_database_schema.sql
   ```

4. **"Agent not responding"**
   - Check logs: `logs/agent_PORT.log`
   - Verify agent card exists
   - Check Python dependencies

## Development

### Adding New Agents
1. Add to `agent_registry.py`
2. Assign appropriate port in range
3. Define instructions
4. Regenerate agent cards

### Extending Functionality
1. Add new MCP tools in `solopreneur_mcp_tools.py`
2. Update agent instructions
3. Modify tier-specific behavior in base class

## License

Part of the A2A-MCP framework. See main project license.