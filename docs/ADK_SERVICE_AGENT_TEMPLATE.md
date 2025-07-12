# ADK Service Agent Template Guide

## 🎯 **Overview**

The `ADKServiceAgent` is the **production-ready template** for creating domain-specific service agents in the A2A-MCP framework. It demonstrates the canonical pattern for integrating Google ADK with MCP tools and A2A protocols.

## 🏗️ **Architecture Position**

**Tier 3: Service Agents** - Direct tool execution for domain-specific tasks

```
┌─────────────────────┐
│ Tier 1: Orchestrator│ ← orchestrator_agent.py
└─────────┬───────────┘
          │
    ┌─────▼─────┬─────────────┐
    │ Tier 2:   │ Tier 2:     │ ← langgraph_planner_agent.py
    │ Domain    │ Specialist  │
    │ Planner   │ Agents      │
    └─────┬─────┴─────────────┘
          │
    ┌─────▼─────┬─────────────┬─────────────┐
    │ Tier 3:   │ Tier 3:     │ Tier 3:     │ ← **ADKServiceAgent**
    │ Travel    │ Finance     │ Support     │
    │ Service   │ Service     │ Service     │
    └───────────┴─────────────┴─────────────┘
```

## 🔧 **Key Features**

### **Production-Ready Patterns**
- ✅ Google ADK integration with streaming responses
- ✅ MCP tool discovery and dynamic loading
- ✅ A2A protocol compatibility
- ✅ Session management and state handling
- ✅ Comprehensive error handling and logging
- ✅ Intelligent response parsing and formatting

### **Domain Agnostic Design**
- ✅ Fully parameterized (name, description, instructions)
- ✅ Configurable content types and temperature
- ✅ No hardcoded domain logic
- ✅ Clean separation of infrastructure vs business logic

## 📝 **Usage Examples**

### **Travel Domain**
```python
from adk_service_agent import ADKServiceAgent

travel_agent = ADKServiceAgent(
    agent_name='AirTicketingAgent',
    description='Book air tickets given criteria',
    instructions=\"\"\"
    You are an expert air travel booking agent. When given travel criteria:
    1. Search for available flights using MCP tools
    2. Compare options by price, duration, and convenience
    3. Present recommendations with reasoning
    4. Handle booking requests with confirmation details
    \"\"\"
)
```

### **Finance Domain**
```python
finance_agent = ADKServiceAgent(
    agent_name='TradingAgent', 
    description='Execute trading strategies and analysis',
    instructions=\"\"\"
    You are a quantitative trading agent. Your capabilities:
    1. Analyze market data using MCP financial tools
    2. Execute trading strategies based on technical indicators
    3. Provide risk assessment and portfolio recommendations
    4. Generate trading reports with performance metrics
    \"\"\"
)
```

### **Customer Support Domain**
```python
support_agent = ADKServiceAgent(
    agent_name='CustomerSupportAgent',
    description='Handle customer inquiries and support tickets',
    instructions=\"\"\"
    You are a customer support specialist. Your role:
    1. Understand customer issues and classify them appropriately
    2. Access customer data and order history via MCP tools
    3. Provide helpful solutions and escalate when necessary
    4. Maintain empathetic and professional communication
    \"\"\"
)
```

### **Healthcare Domain**
```python
healthcare_agent = ADKServiceAgent(
    agent_name='MedicalRecordsAgent',
    description='Manage patient records and appointment scheduling',
    instructions=\"\"\"
    You are a medical records specialist. Your responsibilities:
    1. Access and update patient records using secure MCP tools
    2. Schedule appointments based on availability and urgency
    3. Handle insurance verification and billing inquiries
    4. Maintain strict HIPAA compliance in all interactions
    \"\"\"
)
```

## 🛠️ **Implementation Patterns**

### **1. Agent Initialization**
```python
# Lazy initialization pattern
if not self.agent:
    await self.init_agent()
```

### **2. MCP Tool Integration**
```python
# Dynamic tool discovery
config = get_mcp_server_config()
tools = await MCPToolset(
    connection_params=SseServerParams(url=config.url)
).get_tools()

# ADK agent with integrated tools
self.agent = Agent(
    name=self.agent_name,
    instruction=self.instructions,
    tools=tools  # MCP tools available to agent
)
```

### **3. Streaming Response Handling**
```python
# A2A compatible streaming
async for chunk in self.runner.run_stream(agent, query, context_id):
    if chunk.get('type') == 'final_result':
        yield self.get_agent_response(chunk['response'])
    else:
        yield {'content': 'Processing...', 'is_task_complete': False}
```

### **4. Response Format Standardization**
```python
# Intelligent response parsing
def format_response(self, chunk):
    patterns = [
        r'```json\s*(.*?)\s*```',  # JSON blocks
        r'```\n(.*?)\n```',        # Code blocks
    ]
    # Parse and return appropriate format
```

## 🔧 **Configuration Options**

### **Constructor Parameters**
```python
ADKServiceAgent(
    agent_name: str,              # Agent identifier
    description: str,             # Capability description  
    instructions: str,            # Domain-specific prompts
    content_types: List[str],     # Supported content types
    temperature: float = 0.0      # LLM temperature
)
```

### **Environment Variables**
```bash
GEMINI_MODEL=gemini-2.0-flash    # ADK model selection
GOOGLE_API_KEY=your_key          # Google API authentication
MCP_SERVER_HOST=localhost        # MCP server location
MCP_SERVER_PORT=10100           # MCP server port
```

## 📊 **Response Formats**

### **Text Response**
```python
{
    'response_type': 'text',
    'is_task_complete': True,
    'require_user_input': False,
    'content': 'Task completed successfully'
}
```

### **Data Response**
```python
{
    'response_type': 'data', 
    'is_task_complete': True,
    'require_user_input': False,
    'content': {
        'result': 'structured_data',
        'metadata': {...}
    }
}
```

### **Interactive Response**
```python
{
    'response_type': 'text',
    'is_task_complete': False,
    'require_user_input': True,
    'content': 'What is your preferred departure time?'
}
```

## 🎯 **Best Practices**

### **Instructions Design**
1. **Be Specific**: Clear, actionable instructions for the domain
2. **Include Context**: Explain the agent's role and capabilities
3. **Define Workflows**: Step-by-step process for common tasks
4. **Handle Edge Cases**: Instructions for error scenarios

### **MCP Tool Integration**
1. **Tool Discovery**: Let the agent discover available tools dynamically
2. **Error Handling**: Graceful degradation when tools are unavailable
3. **Logging**: Log tool usage for debugging and monitoring
4. **Security**: Validate tool outputs before processing

### **Performance Optimization**
1. **Lazy Loading**: Initialize ADK agent only when needed
2. **Connection Pooling**: Reuse MCP connections across requests
3. **Response Caching**: Cache responses for repeated queries
4. **Streaming**: Use streaming for long-running operations

## 🔍 **Debugging and Monitoring**

### **Logging Levels**
```python
logger.info(f'Initializing {self.agent_name}')          # Lifecycle
logger.info(f'Loaded MCP tool: {tool.name}')            # Tool discovery
logger.info(f'Received chunk: {chunk}')                 # Response streaming
logger.error(f'Error in get_agent_response: {e}')       # Error handling
```

### **Health Checks**
```python
# Verify agent initialization
assert self.agent is not None
assert self.runner is not None

# Verify MCP connectivity
config = get_mcp_server_config()
assert config.url is not None
```

## 🚀 **Deployment Considerations**

### **Google Cloud Deployment**
- Use with Google ADK `adk deploy cloud_run`
- Configure environment variables in Cloud Run
- Set up MCP server endpoints for tool access

### **Local Development**
- Run MCP server locally on port 10100
- Set GOOGLE_API_KEY for ADK access
- Use development model endpoints

### **Production Monitoring**
- Monitor agent response times and error rates
- Track MCP tool usage and performance
- Set up alerting for agent failures

This template provides the foundation for building production-ready, domain-specific service agents that integrate seamlessly with the A2A-MCP framework architecture.