# MCP Server Patterns - Framework V2.0

## Overview

The A2A Framework V2.0 provides generic, reusable patterns for creating MCP servers with common integrations like APIs, databases, and custom tools. This eliminates the need to write boilerplate code for every new MCP server.

## Generic MCP Server Template

### Key Features

✅ **Reusable API Integration Patterns** - Common REST/GraphQL API patterns  
✅ **Database Query Tools** - Secure SQL database integrations  
✅ **Custom Tool Registration** - Easy custom tool creation  
✅ **Built-in Security** - Query validation, rate limiting, error handling  
✅ **Health Monitoring** - Automatic health checks for all integrations  
✅ **Extensible Architecture** - Add new tool types easily  

## Quick Start Examples

### Basic API Integration

```python
from a2a_mcp.common.generic_mcp_server_template import (
    GenericMCPServerTemplate, 
    APIConfig
)

# Create server
server = GenericMCPServerTemplate(
    server_name="my-api-server",
    description="Custom API integrations"
)

# Add Google Places API (like your example)
places_config = APIConfig(
    name="query_places_data",
    description="Query Google Places for location data",
    base_url="https://places.googleapis.com/v1/places:searchText",
    headers={
        'X-Goog-Api-Key': '',  # Set from env var
        'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress',
        'Content-Type': 'application/json'
    },
    auth_env_var='GOOGLE_PLACES_API_KEY',
    default_params={
        'languageCode': 'en',
        'maxResultCount': 10
    }
)

server.add_api_tool("google_places", places_config)
server.run()
```

### Database Integration

```python
from a2a_mcp.common.generic_mcp_server_template import (
    GenericMCPServerTemplate,
    DatabaseConfig
)

# Add travel database (like your example)
travel_db_config = DatabaseConfig(
    name="query_travel_data", 
    description="Query travel database for bookings and availability",
    connection_string="travel.db",
    db_type="sqlite",
    query_whitelist=[
        "SELECT * FROM airlines",
        "SELECT * FROM hotels",
        "SELECT * FROM car_rentals", 
        "SELECT * FROM bookings"
    ],
    max_results=1000
)

server.add_database_tool("travel_db", travel_db_config)
```

### Custom Tools

```python
def my_custom_logic(param1: str, param2: int) -> dict:
    """Your custom business logic."""
    return {
        'result': f'Processed {param1} with value {param2}',
        'timestamp': datetime.now().isoformat()
    }

server.add_custom_tool(
    name="custom_processor",
    description="Process data with custom business logic",
    handler_func=my_custom_logic,
    parameters={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "Input string"},
            "param2": {"type": "integer", "description": "Input number"}
        },
        "required": ["param1", "param2"]
    }
)
```

## Complete Travel Server Example

Here's exactly what you were looking for - the patterns from your original code:

```python
#!/usr/bin/env python3
import os
from a2a_mcp.common.generic_mcp_server_template import (
    GenericMCPServerTemplate,
    APIConfig, 
    DatabaseConfig
)

# Create travel services server
travel_server = GenericMCPServerTemplate(
    server_name="travel-services",
    description="Travel booking and search services",
    host="localhost",
    port=8080
)

# Google Places API tool (exactly like your example)
places_config = APIConfig(
    name="query_places_data",
    description="Query Google Places for location information", 
    base_url="https://places.googleapis.com/v1/places:searchText",
    headers={
        'X-Goog-Api-Key': '',  # Will be set from GOOGLE_PLACES_API_KEY
        'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress',
        'Content-Type': 'application/json'
    },
    auth_env_var='GOOGLE_PLACES_API_KEY',
    default_params={
        'languageCode': 'en',
        'maxResultCount': 10
    }
)
travel_server.add_api_tool("google_places", places_config)

# Travel database tool (exactly like your example) 
travel_db_config = DatabaseConfig(
    name="query_travel_data",
    description="Query travel database for airline, hotel, and car rental information",
    connection_string=os.getenv('SQLITE_DB', 'travel.db'),
    db_type="sqlite",
    query_whitelist=[
        "SELECT * FROM airlines",
        "SELECT * FROM hotels",
        "SELECT * FROM car_rentals", 
        "SELECT * FROM bookings"
    ],
    max_results=1000
)
travel_server.add_database_tool("travel_db", travel_db_config)

# Run the server
travel_server.run()
```

## Tool Handler Classes

For advanced use cases, you can create custom tool handlers:

```python
from a2a_mcp.common.generic_mcp_server_template import ToolHandler

class CustomAPIHandler(ToolHandler):
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "custom_api",
            "description": "Custom API integration",
            "parameters": {
                "type": "object", 
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        }
    
    def execute(self, **kwargs) -> Any:
        # Your custom logic here
        return {"result": "custom response"}

# Use custom handler
server.tool_handlers["custom"] = CustomAPIHandler()
```

## Enhanced MCP Server

Our enhanced `mcp/server.py` combines agent discovery with the generic patterns:

```python
# Automatic agent discovery + extensible tool patterns
from a2a_mcp.mcp.server import serve

# Set environment variables for integrations
os.environ['GOOGLE_PLACES_API_KEY'] = 'your-key'
os.environ['SQLITE_DB'] = 'travel.db'

# Runs enhanced server with:
# - Agent discovery and matching
# - Google Places API (if key set)
# - Travel database queries (if DB exists)
# - Health monitoring
# - Custom tool extensibility
serve(host="localhost", port=8080, transport="stdio")
```

## Pre-configured Tool Factories

Use these factory functions for common integrations:

```python
from a2a_mcp.common.generic_mcp_server_template import (
    create_google_places_tool,
    create_travel_database_tool,
    create_weather_api_tool
)

# Google Places
places_config = create_google_places_tool()
server.add_api_tool("places", places_config)

# Travel Database  
travel_config = create_travel_database_tool("travel.db")
server.add_database_tool("travel", travel_config)

# Weather API
weather_config = create_weather_api_tool()
server.add_api_tool("weather", weather_config)
```

## Security Features

### Database Query Validation

```python
# Automatic security validation:
# ✅ Only SELECT statements allowed
# ❌ Blocks DROP, DELETE, UPDATE, INSERT, ALTER
# ✅ Query whitelist support
# ✅ Result limit enforcement
# ✅ SQL injection protection

DatabaseConfig(
    name="secure_db",
    connection_string="app.db",
    db_type="sqlite",
    query_whitelist=[
        "SELECT * FROM users WHERE id = ",
        "SELECT name, email FROM customers"
    ],
    max_results=100  # Prevents large result sets
)
```

### API Security

```python
# Automatic API security:
# ✅ Environment variable auth
# ✅ Request timeout limits  
# ✅ Retry logic with backoff
# ✅ Error handling and logging
# ✅ Rate limiting ready

APIConfig(
    name="secure_api",
    base_url="https://api.example.com/v1",
    auth_env_var='API_KEY',  # Automatically applied
    timeout=30,              # Request timeout
    max_retries=3           # Retry failed requests
)
```

## Built-in Tools

Every server includes these tools automatically:

### `health_check`
Check health of server and all integrated services:
```json
{
  "server": "travel-services",
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "tools": {
    "google_places": {"type": "api", "status": "healthy"},
    "travel_db": {"type": "database", "status": "healthy"}
  }
}
```

### `list_tools`
List all available tools and capabilities:
```json
{
  "server": "travel-services", 
  "tools": [
    {
      "name": "query_places_data",
      "description": "Query Google Places API",
      "type": "APIToolHandler"
    }
  ]
}
```

## Migration from Original Code

### Before (Manual Implementation)
```python
@mcp.tool()
def query_places_data(query: str):
    """Manual implementation with lots of boilerplate."""
    logger.info(f'Search for places : {query}')
    api_key = os.getenv('GOOGLE_PLACES_API_KEY')
    if not api_key:
        return {'places': []}
    
    # ... lots of manual error handling code ...
    # ... manual request setup ...
    # ... manual retry logic ...
```

### After (Generic Template)
```python
# One-liner with all error handling, retries, auth, etc.
places_config = create_google_places_tool()
server.add_api_tool("google_places", places_config)
```

## Benefits

✅ **95% Less Boilerplate** - Generic patterns eliminate repetitive code  
✅ **Built-in Security** - Query validation, auth handling, error management  
✅ **Automatic Retries** - Network resilience built-in  
✅ **Health Monitoring** - Know when integrations fail  
✅ **Extensible** - Easy to add new tool types  
✅ **Consistent APIs** - Same patterns across all tools  
✅ **Error Handling** - Comprehensive error management  
✅ **Documentation** - Self-documenting tool definitions  

## Next Steps

1. **Use the enhanced `mcp/server.py`** for agent discovery + extensible tools
2. **Create domain-specific servers** using `GenericMCPServerTemplate`
3. **Add your API integrations** using `APIConfig` patterns
4. **Add database tools** using `DatabaseConfig` patterns
5. **Extend with custom tools** using `add_custom_tool()`

The generic template handles all the boilerplate, security, and error handling so you can focus on your business logic!