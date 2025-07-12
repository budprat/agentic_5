# Launch System

This directory contains the launch system for the A2A MCP Framework.

## Files

- `launch_system.py` - Main launcher that validates environment, starts MCP server, and manages agents
- `test_launch.py` - Test script to verify launch system functionality
- `process_manager.py` - (To be implemented) Advanced process management
- `start_all.sh` - (To be implemented) Shell script wrapper

## Usage

### Prerequisites

1. Set the `GOOGLE_API_KEY` environment variable:
   ```bash
   export GOOGLE_API_KEY="your-api-key-here"
   ```

2. Ensure you're in the project root directory

3. Install dependencies (if not already done):
   ```bash
   pip install -r requirements.txt
   ```

### Running the System

```bash
# From project root
python launch/launch_system.py
```

### Testing

Run the test script to verify your setup:

```bash
python launch/test_launch.py
```

## Features

1. **Environment Validation**
   - Checks for required environment variables (GOOGLE_API_KEY)
   - Validates Python version (3.8+)
   - Ensures agent cards directory exists
   - Verifies module imports

2. **MCP Server Management**
   - Starts the MCP server on localhost:8080
   - Waits for server readiness
   - Provides agent discovery and health monitoring tools

3. **Agent Management**
   - Loads agent configurations from JSON files
   - Starts agents based on their tier (tier 1 first)
   - Uses ports specified in agent cards
   - Manages agent processes

4. **Health Monitoring**
   - Periodic health checks every 30 seconds
   - Monitors MCP server and all agent processes
   - Reports system status
   - (Future: Auto-restart failed components)

5. **Graceful Shutdown**
   - Handles SIGINT and SIGTERM signals
   - Stops all processes in reverse order
   - Ensures clean shutdown

## Agent Cards

The system loads agent configurations from JSON files in the `agent_cards/` directory:

```
agent_cards/
├── example_agent.json
├── tier1/
│   └── master_oracle.json
├── tier2/
│   └── domain_specialist.json
└── tier3/
    └── service_agent.json
```

Each agent card should specify:
- `name`: Agent name
- `type`: Agent type (orchestrator, specialist, service, etc.)
- `port`: (Optional) Specific port for the agent
- `tier`: (Optional) Agent tier for startup ordering

## Customization

To add new agents:
1. Create an agent card JSON file
2. Place it in the appropriate directory
3. Implement the agent class (see agents module)
4. The launcher will automatically discover and start it

## Troubleshooting

1. **API Key Error**: Ensure GOOGLE_API_KEY is set
2. **Import Error**: Run from project root, not from launch directory
3. **Port Conflicts**: Check if ports are already in use
4. **Agent Startup Failed**: Check agent logs for specific errors