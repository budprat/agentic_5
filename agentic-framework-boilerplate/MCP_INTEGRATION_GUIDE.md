# MCP Integration Guide

## Overview

The Model Context Protocol (MCP) serves as the backbone of the A2A-MCP system, providing agent discovery, tool provision, and resource management capabilities. This guide details how MCP integration enables seamless communication between agents and centralized service management.

## MCP Architecture Components

### MCP Server (`src/a2a_mcp/mcp/server.py`)
- **Central Registry**: Maintains catalog of all available agents
- **Tool Provider**: Exposes database access via `query_travel_data` tool
- **Resource Manager**: Serves agent cards and metadata via MCP resources
- **Discovery Engine**: Uses embedding-based similarity matching for agent selection

### MCP Client Integration
- **Tool Discovery**: Agents dynamically load available tools on startup
- **Resource Access**: Agents retrieve metadata and configurations
- **Database Connectivity**: Standardized database access across all agents

## Agent Discovery System

### Embedding-Based Agent Matching

The MCP server uses advanced embedding technology to match queries with the most suitable agents:

```python
# Agent card embedding generation at server startup
def generate_embeddings(text: str) -> list[float]:
    """Generate embeddings for agent card content."""
    result = genai.embed_content(
        model=MODEL,
        content=text,
        task_type='retrieval_document'
    )
    return result['embedding']

# Load and embed all agent cards
df = pd.read_csv('agent_registry.csv')
df['card_embeddings'] = df.apply(
    lambda row: generate_embeddings(json.dumps(row['agent_card'])), 
    axis=1
)
```

### Query-to-Agent Matching Process

```python
async def find_best_agent(query: str) -> dict:
    """Find the best agent for a given query using embedding similarity."""
    
    # Generate query embedding
    query_embedding = genai.embed_content(
        model=MODEL,
        content=query,
        task_type='retrieval_query'
    )
    
    # Calculate cosine similarity with all agent cards
    similarities = np.dot(
        np.stack(df['card_embeddings']), 
        query_embedding['embedding']
    )
    
    # Find best match
    best_match_index = np.argmax(similarities)
    best_agent = df.iloc[best_match_index]
    
    return {
        'agent_card': best_agent['agent_card'],
        'similarity_score': similarities[best_match_index],
        'confidence': 'high' if similarities[best_match_index] > 0.8 else 'medium'
    }
```

### Agent Discovery Examples

**Query**: "Book business class flights from NYC to Tokyo"
```python
# Embedding analysis finds best match
{
    'agent_card': {
        'name': 'Air Ticketing Agent',
        'description': 'Specializes in booking flights and air travel arrangements',
        'skills': ['flight booking', 'airline search', 'itinerary planning'],
        'port': 10103
    },
    'similarity_score': 0.94,
    'confidence': 'high'
}
```

**Query**: "Find luxury hotel in downtown Tokyo"
```python
# Embedding analysis finds best match
{
    'agent_card': {
        'name': 'Hotel Booking Agent', 
        'description': 'Specializes in booking hotels and accommodations',
        'skills': ['hotel booking', 'accommodation search', 'room selection'],
        'port': 10104
    },
    'similarity_score': 0.91,
    'confidence': 'high'
}
```

## MCP Tool System

### Database Tool Implementation

The MCP server provides a unified database access tool:

```python
@server.call_tool()
async def query_travel_data(query: str) -> list[dict]:
    """Execute SQL queries on the travel database."""
    
    # Validate query for security
    if not is_safe_query(query):
        raise ValueError("Unsafe query detected")
    
    # Execute query
    try:
        conn = sqlite3.connect('travel_agency.db')
        cursor = conn.cursor()
        cursor.execute(query)
        
        # Format results
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        results = [dict(zip(columns, row)) for row in rows]
        
        conn.close()
        return results
        
    except Exception as e:
        logger.error(f"Database query failed: {e}")
        raise RuntimeError(f"Query execution error: {str(e)}")
```

### Tool Security and Validation

```python
def is_safe_query(query: str) -> bool:
    """Validate SQL query for security."""
    
    # Allowed operations
    allowed_operations = ['SELECT']
    
    # Blocked operations  
    blocked_operations = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE']
    
    query_upper = query.upper().strip()
    
    # Check if query starts with allowed operation
    if not any(query_upper.startswith(op) for op in allowed_operations):
        return False
    
    # Check for blocked operations
    if any(op in query_upper for op in blocked_operations):
        return False
    
    # Additional security checks
    dangerous_patterns = [
        '--',          # SQL comments
        ';',           # Query termination (multiple queries)
        'UNION',       # Union injections
        'EXEC',        # Stored procedure execution
        'xp_',         # Extended stored procedures
    ]
    
    for pattern in dangerous_patterns:
        if pattern in query_upper:
            return False
    
    return True
```

## Agent Tool Discovery and Loading

### Client-Side Tool Integration

Each agent loads MCP tools dynamically during initialization:

```python
# TravelAgent tool initialization
async def init_agent(self):
    """Initialize agent with MCP tools."""
    logger.info(f'Initializing {self.agent_name} with MCP tools')
    
    # Get MCP server configuration
    config = get_mcp_server_config()
    logger.info(f'MCP Server url={config.url}')
    
    # Connect to MCP server and load tools
    tools = await MCPToolset(
        connection_params=SseConnectionParams(url=config.url)
    ).get_tools()
    
    # Log available tools
    for tool in tools:
        logger.info(f'Loaded tool: {tool.name}')
    
    # Create Google ADK agent with MCP tools
    generate_content_config = genai_types.GenerateContentConfig(
        temperature=0.0,
        response_mime_type="application/json"
    )
    
    self.agent = Agent(
        name=self.agent_name,
        instruction=self.instructions,
        model='gemini-2.0-flash',
        disallow_transfer_to_parent=True,
        disallow_transfer_to_peers=True,
        generate_content_config=generate_content_config,
        tools=tools,  # MCP tools integrated into ADK agent
    )
```

### Tool Usage in Agents

```python
# Example tool usage in agent workflow
async def search_flights(self, criteria: dict) -> list[dict]:
    """Search for flights using MCP database tool."""
    
    # Build SQL query from criteria
    query = f"""
    SELECT carrier, flight_number, departure_time, arrival_time, price
    FROM flights 
    WHERE from_airport = '{criteria['origin']}'
    AND to_airport = '{criteria['destination']}'
    AND ticket_class = '{criteria['class']}'
    ORDER BY price ASC
    """
    
    # Execute via MCP tool
    try:
        results = await self.session.call_tool(
            name='query_travel_data',
            arguments={'query': query}
        )
        return results.content
    except Exception as e:
        logger.error(f"Flight search failed: {e}")
        return []
```

## MCP Resource Management

### Agent Card Resources

The MCP server exposes agent metadata via resources:

```python
@server.list_resources()
async def list_resources() -> list[Resource]:
    """List all available agent card resources."""
    
    resources = []
    for agent_file in glob.glob('agent_cards/*.json'):
        with open(agent_file, 'r') as f:
            agent_card = json.load(f)
            
        resources.append(Resource(
            uri=f"agent-card://{agent_card['name']}",
            name=agent_card['name'],
            description=agent_card.get('description', ''),
            mimeType="application/json"
        ))
    
    return resources

@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read agent card resource by URI."""
    
    if not uri.startswith("agent-card://"):
        raise ValueError(f"Unsupported resource URI: {uri}")
    
    agent_name = uri.replace("agent-card://", "")
    agent_file = f"agent_cards/{agent_name.lower().replace(' ', '_')}_agent.json"
    
    try:
        with open(agent_file, 'r') as f:
            return f.read()
    except FileNotFoundError:
        raise ValueError(f"Agent card not found: {agent_name}")
```

### Resource Access Examples

```python
# Orchestrator accessing agent metadata
async def get_agent_capabilities(self, agent_name: str) -> dict:
    """Retrieve agent capabilities from MCP resources."""
    
    resource_uri = f"agent-card://{agent_name}"
    resource_content = await self.mcp_client.read_resource(resource_uri)
    agent_card = json.loads(resource_content)
    
    return {
        'name': agent_card['name'],
        'description': agent_card['description'],
        'skills': agent_card.get('skills', []),
        'port': agent_card.get('port'),
        'auth_required': agent_card.get('auth_required', False)
    }
```

## MCP Configuration and Setup

### Server Configuration

```python
# MCP server configuration
MCP_CONFIG = {
    'transport': 'sse',
    'host': 'localhost', 
    'port': 10100,
    'model': 'models/text-embedding-004',
    'database_path': 'travel_agency.db',
    'agent_cards_dir': 'agent_cards/',
    'max_query_length': 1000,
    'enable_embeddings': True,
    'cache_embeddings': True
}
```

### Client Configuration

```python
# MCP client configuration for agents
def get_mcp_server_config() -> MCPConfig:
    """Get MCP server connection configuration."""
    return MCPConfig(
        url=f"http://localhost:10100/sse",
        timeout=30,
        retry_attempts=3,
        enable_caching=True
    )
```

### Environment Setup

```bash
# MCP server environment variables
export MCP_SERVER_HOST=localhost
export MCP_SERVER_PORT=10100
export MCP_DATABASE_PATH=travel_agency.db
export MCP_EMBEDDINGS_MODEL=models/text-embedding-004
export MCP_ENABLE_SECURITY=true
```

## Advanced MCP Features

### Remote MCP Server Integration

```python
# Support for connecting to external MCP servers
REMOTE_MCP_SERVERS = [
    {
        'name': 'external_tools',
        'url': 'http://external-mcp-server:8080/sse',
        'capabilities': ['weather', 'currency', 'translation']
    },
    {
        'name': 'third_party_booking',
        'url': 'https://partner-api.example.com/mcp',
        'capabilities': ['flight_booking', 'hotel_booking'],
        'auth_required': True
    }
]

async def connect_remote_servers(self):
    """Connect to external MCP servers for additional capabilities."""
    for server_config in REMOTE_MCP_SERVERS:
        try:
            remote_tools = await MCPToolset(
                connection_params=SseConnectionParams(url=server_config['url'])
            ).get_tools()
            
            logger.info(f"Connected to {server_config['name']}: {len(remote_tools)} tools loaded")
            self.external_tools.extend(remote_tools)
            
        except Exception as e:
            logger.warning(f"Failed to connect to {server_config['name']}: {e}")
```

### Caching and Performance Optimization

```python
# Embedding cache for improved performance
class EmbeddingCache:
    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size
        self.access_times = {}
    
    def get_embedding(self, text: str) -> Optional[list[float]]:
        """Get cached embedding or None if not found."""
        if text in self.cache:
            self.access_times[text] = time.time()
            return self.cache[text]
        return None
    
    def set_embedding(self, text: str, embedding: list[float]):
        """Cache embedding with LRU eviction."""
        if len(self.cache) >= self.max_size:
            # Remove least recently used
            oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
        
        self.cache[text] = embedding
        self.access_times[text] = time.time()

# Global embedding cache instance
embedding_cache = EmbeddingCache(max_size=1000)
```

### MCP Health Monitoring

```python
# MCP server health monitoring
async def check_mcp_health(self) -> dict:
    """Check MCP server health and performance."""
    
    start_time = time.time()
    
    try:
        # Test agent discovery
        test_query = "test flight booking"
        agent_result = await self.find_best_agent(test_query)
        discovery_time = time.time() - start_time
        
        # Test tool availability
        tools = await self.list_tools()
        tool_count = len(tools)
        
        # Test database connectivity
        db_start = time.time()
        test_result = await self.query_travel_data("SELECT COUNT(*) FROM flights")
        db_time = time.time() - db_start
        
        return {
            'status': 'healthy',
            'discovery_latency': f"{discovery_time:.3f}s",
            'available_tools': tool_count,
            'database_latency': f"{db_time:.3f}s",
            'cached_embeddings': len(embedding_cache.cache),
            'uptime': self.get_uptime()
        }
        
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
```

## Error Handling and Resilience

### Connection Resilience

```python
# Robust MCP connection handling
class ResilientMCPClient:
    def __init__(self, config: MCPConfig):
        self.config = config
        self.client = None
        self.retry_count = 0
        self.max_retries = 3
    
    async def connect_with_retry(self):
        """Connect to MCP server with automatic retry."""
        for attempt in range(self.max_retries):
            try:
                self.client = await MCPToolset(
                    connection_params=SseConnectionParams(url=self.config.url)
                ).get_tools()
                logger.info(f"MCP connection established on attempt {attempt + 1}")
                return self.client
                
            except Exception as e:
                logger.warning(f"MCP connection attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise ConnectionError(f"Failed to connect to MCP server after {self.max_retries} attempts")
```

### Graceful Degradation

```python
# Fallback mechanisms when MCP is unavailable
async def execute_with_fallback(self, query: str) -> dict:
    """Execute query with MCP fallback strategies."""
    
    try:
        # Primary: Use MCP for agent discovery and tool execution
        agent = await self.find_best_agent(query)
        result = await self.execute_with_agent(agent, query)
        return result
        
    except MCPConnectionError:
        logger.warning("MCP server unavailable, using fallback strategy")
        
        # Fallback: Use static agent mapping
        agent = self.get_fallback_agent(query)
        result = await self.execute_with_local_tools(agent, query)
        return result
        
    except Exception as e:
        logger.error(f"Both primary and fallback strategies failed: {e}")
        return {
            'error': 'Service temporarily unavailable',
            'suggestion': 'Please try again later'
        }
```

This comprehensive MCP integration guide demonstrates how the Model Context Protocol serves as the foundation for agent coordination, tool discovery, and resource management in the A2A-MCP system, enabling scalable and efficient multi-agent travel booking workflows.