# A2A-MCP Framework Comprehensive Reference Guide

## Framework Overview

The A2A-MCP (Agent-to-Agent Model Context Protocol) framework is a sophisticated multi-agent system that enables specialized agents to collaborate through structured communication protocols. This reference guide provides complete architectural patterns and implementation details for building new orchestrator systems.

## 1. Core Architecture Components

### 1.1 Directory Structure
```
src/a2a_mcp/
├── agents/                    # Agent implementations
│   ├── parallel_orchestrator_agent.py
│   ├── langgraph_planner_agent.py
│   ├── adk_travel_agent.py
│   └── __main__.py
├── common/                    # Shared components
│   ├── base_agent.py         # Base agent class
│   ├── agent_executor.py     # A2A integration
│   ├── agent_runner.py       # Google ADK runner
│   ├── parallel_workflow.py  # NetworkX graphs
│   └── utils.py              # Utilities
├── mcp/                      # MCP server implementation
│   ├── server.py            # Main MCP server
│   ├── client.py            # MCP client utilities
│   └── remote_mcp_connector.py
└── __init__.py

agent_cards/                  # Agent registry cards
├── orchestrator_agent.json
├── planner_agent.json
├── air_ticketing_agent.json
├── hotel_booking_agent.json
└── car_rental_agent.json
```

### 1.2 Core Classes Hierarchy

```python
# Base Agent Class
class BaseAgent(BaseModel, ABC):
    agent_name: str
    description: str
    content_types: list[str]
    
    # Abstract methods for implementation
    async def stream(self, query, context_id, task_id) -> AsyncIterable[Dict[str, Any]]
    async def invoke(self, query, session_id) -> dict

# Orchestrator Pattern
class ParallelOrchestratorAgent(BaseAgent):
    - Coordinates multiple agents
    - Manages parallel workflow execution
    - Generates summaries using LLM
    - Handles user interaction states

# Task Agent Pattern
class TravelAgent(BaseAgent):
    - Uses Google ADK integration
    - Connects to MCP server via MCPToolset
    - Implements specific domain logic
```

## 2. Agent Implementation Patterns

### 2.1 Agent Card Structure
Every agent requires a JSON configuration card in `agent_cards/`:

```json
{
    "name": "Agent Name",
    "description": "Agent description",
    "url": "http://localhost:PORT/",
    "provider": null,
    "version": "1.0.0",
    "capabilities": {
        "streaming": "True",
        "pushNotifications": "True",
        "stateTransitionHistory": "False"
    },
    "auth_required": true,
    "auth_schemes": [
        {
            "type": "bearer",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    ],
    "defaultInputModes": ["text", "text/plain"],
    "defaultOutputModes": ["text", "text/plain"],
    "skills": [
        {
            "id": "skill_id",
            "name": "Skill Name",
            "description": "Skill description",
            "tags": ["tag1", "tag2"],
            "examples": ["Example usage"]
        }
    ]
}
```

### 2.2 Orchestrator Agent Pattern

```python
class YourOrchestratorAgent(BaseAgent):
    def __init__(self):
        init_api_key()  # Initialize Google API
        super().__init__(
            agent_name="Your Orchestrator Agent",
            description="Orchestrates your specific workflow",
            content_types=["text", "text/plain"]
        )
        self.graph = None
        self.results = []
        self.context = {}
        self.enable_parallel = True

    async def generate_summary(self) -> str:
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=YOUR_SUMMARY_PROMPT.replace("{data}", str(self.results)),
            config={"temperature": 0.0}
        )
        return response.text

    async def stream(self, query, context_id, task_id) -> AsyncIterable[Dict[str, Any]]:
        # Implement streaming workflow logic
        # 1. Process user input
        # 2. Coordinate with planner
        # 3. Execute tasks via task agents
        # 4. Generate final summary
```

### 2.3 Task Agent Pattern

```python
class YourTaskAgent(BaseAgent):
    def __init__(self, agent_name: str, description: str, instructions: str):
        init_api_key()
        super().__init__(
            agent_name=agent_name,
            description=description,
            content_types=['text', 'text/plain']
        )
        self.instructions = instructions
        self.agent = None

    async def init_agent(self):
        config = get_mcp_server_config()
        tools = await MCPToolset(
            connection_params=SseConnectionParams(url=config.url)
        ).get_tools()
        
        self.agent = Agent(
            name=self.agent_name,
            instruction=self.instructions,
            model='gemini-2.0-flash',
            tools=tools
        )

    async def stream(self, query, context_id, task_id) -> AsyncIterable[Dict[str, Any]]:
        if not self.agent:
            await self.init_agent()
        # Use Google ADK agent with MCP tools
```

## 3. Communication Protocols

### 3.1 A2A Protocol Integration

```python
class GenericAgentExecutor(AgentExecutor):
    def __init__(self, agent: BaseAgent):
        self.agent = agent

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        query = context.get_user_input()
        task = context.current_task or new_task(context.message)
        
        updater = TaskUpdater(event_queue, task.id, task.contextId)
        
        async for item in self.agent.stream(query, task.contextId, task.id):
            # Handle different event types
            if isinstance(event, TaskStatusUpdateEvent):
                await updater.update_status(event.status, event.message)
            elif isinstance(event, TaskArtifactUpdateEvent):
                await updater.add_artifact(event.parts, name=event.name)
```

### 3.2 MCP Server Communication

```python
# MCP Client Session Management
@asynccontextmanager
async def init_session(host, port, transport):
    if transport == 'sse':
        url = f'http://{host}:{port}/sse'
        async with sse_client(url) as (read_stream, write_stream):
            async with ClientSession(
                read_stream=read_stream, write_stream=write_stream
            ) as session:
                await session.initialize()
                yield session

# Tool Calling Pattern
async def call_mcp_tool(session: ClientSession, tool_name: str, arguments: dict):
    return await session.call_tool(name=tool_name, arguments=arguments)
```

## 4. Data and Configuration Management

### 4.1 Database Schema Pattern

```sql
-- Example domain-specific tables
CREATE TABLE your_domain_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    field1 TEXT NOT NULL,
    field2 TEXT NOT NULL,
    field3 REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.2 MCP Configuration (.mcp.json)

```json
{
  "mcpServers": {
    "server_name": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@package/mcp-server"],
      "env": {
        "API_KEY": "your_api_key",
        "CONFIG_VAR": "value"
      }
    }
  }
}
```

### 4.3 Environment Variables

```bash
# Required environment variables
GOOGLE_API_KEY=your_google_api_key_here
ENABLE_PARALLEL_EXECUTION=true

# Optional MCP-specific variables
SUPABASE_ACCESS_TOKEN=your_token
BRIGHTDATA_API_TOKEN=your_token
```

## 5. Integration Patterns

### 5.1 Google ADK Integration

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams
from google import genai

# Agent initialization with MCP tools
async def create_adk_agent(name: str, instructions: str, mcp_url: str):
    tools = await MCPToolset(
        connection_params=SseConnectionParams(url=mcp_url)
    ).get_tools()
    
    return Agent(
        name=name,
        instruction=instructions,
        model='gemini-2.0-flash',
        tools=tools,
        generate_content_config=genai_types.GenerateContentConfig(temperature=0.0)
    )
```

### 5.2 LangGraph Integration (Planner Pattern)

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class PlannerState(TypedDict):
    query: str
    plan: dict
    status: str

def create_planner_graph():
    workflow = StateGraph(PlannerState)
    workflow.add_node("parse_query", parse_query_node)
    workflow.add_node("generate_plan", generate_plan_node)
    workflow.add_edge("parse_query", "generate_plan")
    workflow.add_edge("generate_plan", END)
    workflow.set_entry_point("parse_query")
    return workflow.compile()
```

### 5.3 Parallel Workflow Management

```python
from a2a_mcp.common.parallel_workflow import ParallelWorkflowGraph, ParallelWorkflowNode

class WorkflowManager:
    def __init__(self):
        self.graph = ParallelWorkflowGraph()
    
    def add_task_node(self, task_id: str, task_description: str, agent_url: str):
        node = ParallelWorkflowNode(
            task=task_description,
            node_key=task_id,
            node_label=f"Task-{task_id}"
        )
        self.graph.add_node(task_id, node)
        self.graph.set_node_attributes(task_id, {
            "agent_url": agent_url,
            "status": "pending"
        })
```

## 6. Implementation Guide for Content and Growth Strategist

### 6.1 Required Components

1. **Content Strategist Orchestrator Agent** (Port 10201)
   - Coordinates content planning and growth strategy
   - Manages multi-step content workflows
   - Integrates with various content creation tools

2. **Content Planner Agent** (Port 10202)
   - Uses LangGraph for content strategy decomposition
   - Creates structured content calendars
   - Analyzes content performance requirements

3. **Specialized Task Agents**:
   - **Content Research Agent** (Port 10203)
   - **SEO Content Agent** (Port 10204)
   - **Social Media Agent** (Port 10205)
   - **Analytics Agent** (Port 10206)
   - **Newsletter Agent** (Port 10207)

### 6.2 Domain-Specific Database Schema

```sql
CREATE TABLE content_pieces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content_type TEXT NOT NULL,  -- blog, social, newsletter, etc.
    topic TEXT NOT NULL,
    target_audience TEXT NOT NULL,
    seo_keywords TEXT,
    status TEXT DEFAULT 'draft',
    publish_date DATE,
    performance_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE growth_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    measurement_date DATE NOT NULL,
    platform TEXT NOT NULL,
    content_id INTEGER,
    FOREIGN KEY (content_id) REFERENCES content_pieces (id)
);

CREATE TABLE content_calendar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id INTEGER NOT NULL,
    scheduled_date DATE NOT NULL,
    platform TEXT NOT NULL,
    status TEXT DEFAULT 'scheduled',
    FOREIGN KEY (content_id) REFERENCES content_pieces (id)
);
```

### 6.3 MCP Server Utilization Strategy

**Content Research Workflow**:
- **Brave Search**: Market research and trend analysis
- **Firecrawl**: Competitor content analysis
- **BrightData**: Social media sentiment analysis

**Content Creation Workflow**:
- **Context7**: Access to documentation and knowledge bases
- **NotionAI**: Content management and collaboration
- **Supabase**: Cloud-based content storage and versioning

**Performance Analysis Workflow**:
- **Upstash**: Real-time analytics caching
- **Puppeteer**: Automated performance testing
- **BrightData**: Social media metrics collection

### 6.4 Agent Card Templates

```json
{
    "name": "Content Strategist Orchestrator",
    "description": "Orchestrates content strategy and growth initiatives for AI solopreneurs",
    "url": "http://localhost:10201/",
    "skills": [
        {
            "id": "content_strategy",
            "name": "Content Strategy Planning",
            "description": "Creates comprehensive content strategies tailored for AI solopreneurs",
            "tags": ["content", "strategy", "planning", "AI", "solopreneur"],
            "examples": [
                "Create a 90-day content strategy for launching an AI product",
                "Develop content calendar for thought leadership in AI space",
                "Plan content funnel for AI consulting business"
            ]
        }
    ]
}
```

### 6.5 Sample Workflow Implementation

```python
class ContentStrategistOrchestrator(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_name="Content Strategist Orchestrator",
            description="AI-powered content strategy and growth orchestration",
            content_types=["text", "text/plain"]
        )
        self.content_calendar = []
        self.growth_metrics = {}
        self.strategy_context = {}

    async def collect_requirements(self, query: str) -> dict:
        """Interactive requirement collection for content strategy"""
        questions = [
            "What is your target audience?",
            "What are your primary content goals?",
            "What platforms do you want to focus on?",
            "What is your content creation capacity?",
            "What are your key performance indicators?"
        ]
        # Implement interactive Q&A flow
        
    async def coordinate_content_workflow(self, requirements: dict) -> list:
        """Coordinate between research, creation, and distribution agents"""
        tasks = [
            {"agent": "content_research", "task": "Research trending topics"},
            {"agent": "seo_content", "task": "Optimize for search visibility"},
            {"agent": "social_media", "task": "Adapt for social platforms"},
            {"agent": "analytics", "task": "Set up performance tracking"}
        ]
        return await self.execute_parallel_tasks(tasks)
```

## 7. Best Practices and Guidelines

### 7.1 Error Handling
- Implement comprehensive error handling for API quota limits
- Use retry patterns for external service calls
- Graceful degradation when MCP servers are unavailable

### 7.2 Performance Optimization
- Use parallel execution for independent tasks
- Implement caching for frequently accessed data
- Monitor resource usage and implement rate limiting

### 7.3 Security Considerations
- Store sensitive credentials in environment variables
- Use authentication schemes for agent communication
- Implement input validation and sanitization

### 7.4 Testing Patterns
- Create unit tests for individual agents
- Implement integration tests for agent communication
- Use mock MCP servers for testing

### 7.5 Deployment Guidelines
- Use separate ports for each agent (10200+ range for new domain)
- Implement health checks for all services
- Use process managers for production deployment

## 8. Common Pitfalls and Solutions

### 8.1 Google API Quota Management
**Problem**: Exceeding free tier limits
**Solution**: Implement quota monitoring and graceful handling

### 8.2 Agent Communication Failures
**Problem**: Network issues between agents
**Solution**: Implement retry logic and circuit breaker patterns

### 8.3 MCP Tool Discovery Issues
**Problem**: Tools not loading correctly
**Solution**: Validate MCP server configurations and connection parameters

### 8.4 State Management Complexity
**Problem**: Managing complex workflows with multiple agents
**Solution**: Use NetworkX graphs for workflow representation and state tracking

## 9. Extension Points

The framework is designed for extensibility:

1. **New Domain Implementation**: Follow the orchestrator + planner + task agents pattern
2. **Custom MCP Integration**: Add new MCP servers to .mcp.json configuration
3. **Advanced Workflows**: Extend parallel workflow graphs for complex orchestration
4. **Custom Authentication**: Implement domain-specific authentication schemes
5. **Performance Monitoring**: Add telemetry and monitoring capabilities

This reference guide provides the complete foundation for implementing sophisticated multi-agent systems using the A2A-MCP framework. The patterns established here ensure consistency, maintainability, and scalability across different domain implementations.