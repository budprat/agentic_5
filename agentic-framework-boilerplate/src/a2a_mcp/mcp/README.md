# Agent-to-Agent MCP Server

The MCP (Model Context Protocol) server provides tools for agent discovery and system health monitoring. It's built using FastMCP and designed to be easily extensible for domain-specific applications.

## Features

### Core Tools

1. **find_agent** - Finds the most relevant agent based on natural language queries
2. **list_available_agents** - Lists all available agents with their basic information
3. **check_system_health** - Monitors the health status of the MCP server and components
4. **get_server_config** - Returns current server configuration

### Resources

- `resource://agent_cards/list` - List of all agent card URIs
- `resource://agent_cards/{card_name}` - Individual agent card data

## Running the Server

### Command Line

```bash
# Run with stdio transport (default)
python -m a2a_mcp.mcp

# Run with SSE transport
python -m a2a_mcp.mcp --transport sse --host 0.0.0.0 --port 8080

# Specify custom agent cards directory
python -m a2a_mcp.mcp --agent-cards-dir /path/to/agents
```

### Environment Variables

- `MCP_HOST` - Server host (default: localhost)
- `MCP_PORT` - Server port (default: 8080)
- `MCP_TRANSPORT` - Transport mechanism (default: stdio)
- `AGENT_CARDS_DIR` - Directory containing agent cards (default: agent_cards)
- `SYSTEM_DB` - Path to system database (default: system.db)
- `GOOGLE_API_KEY` - API key for Google Generative AI embeddings (optional)

## Agent Card Structure

Agent cards are JSON files that describe agent capabilities and configuration:

```json
{
  "name": "AgentName",
  "type": "general|specialist",
  "description": "Agent description",
  "version": "1.0.0",
  "capabilities": ["capability1", "capability2"],
  "required_tools": ["tool1", "tool2"],
  "configuration": {
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2000
  },
  "metadata": {
    "author": "Author Name",
    "created": "2024-01-01",
    "tags": ["tag1", "tag2"]
  }
}
```

## Extending the Server

### Adding Custom Tools

Add new tools by decorating functions with `@mcp.tool()`:

```python
@mcp.tool(
    name='custom_tool',
    description='Description of what this tool does.'
)
def custom_tool(param1: str, param2: int) -> str:
    """Implement your custom logic here."""
    result = process_data(param1, param2)
    return json.dumps(result)
```

### Adding Custom Resources

Add resources using `@mcp.resource()`:

```python
@mcp.resource('resource://custom/data', mime_type='application/json')
def get_custom_data() -> dict:
    """Return custom resource data."""
    return {'data': 'custom_value'}
```

### Integration Points

The server provides several extension points:

1. **Custom Embeddings** - Override `generate_embeddings()` for different embedding models
2. **Database Integration** - Extend with custom database connections
3. **Domain Tools** - Add domain-specific tools for your use case
4. **Authentication** - Add authentication middleware if needed

## Embedding Fallback

The server includes a fallback mechanism for embeddings when Google Generative AI is not available. This uses a simple hash-based approach for demonstration purposes. In production, you should implement a proper embedding service.

## Health Monitoring

The health check monitors:
- Agent card loading status
- Embedding service availability
- Overall system health

Access health status using the `check_system_health` tool.

## Example Usage

### Finding an Agent

```python
# Client code
result = mcp_client.call_tool(
    "find_agent",
    {"query": "I need help with data analysis and visualization"}
)
```

### Listing Agents

```python
# Client code
agents = mcp_client.call_tool("list_available_agents", {})
```

## Troubleshooting

1. **No agents loaded** - Check that agent card JSON files exist in the configured directory
2. **Embedding errors** - Ensure GOOGLE_API_KEY is set or implement custom embedding logic
3. **Connection issues** - Verify host/port settings and transport configuration