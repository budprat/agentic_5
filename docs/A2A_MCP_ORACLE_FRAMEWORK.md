# A2A-MCP Framework V2.0 - Standardized Multi-Agent Architecture
## Production-Ready Framework with Unified Patterns and Best Practices

### Framework Overview

The **A2A-MCP Framework V2.0** provides **production-ready multi-agent implementations** with standardized patterns derived from comprehensive analysis of Oracle, Travel, and Research agent architectures. This framework establishes unified standards for Google ADK integration, A2A communication, quality validation, and tool ecosystem management.

**Key Evolution from V1.0:**
- **Unified Agent Standards**: Beyond Oracle-only to all agent types
- **Standardized Base Classes**: Common implementation patterns with enhanced templates
- **Domain-Specific Quality**: Configurable quality frameworks (5 domains: GENERIC, CREATIVE, ANALYTICAL, CODING, COMMUNICATION)
- **Tool Ecosystem Consolidation**: Unified FastMCP server architecture
- **Best Practices Integration**: Learnings from multi-agent analysis
- **7-Phase Enhancement Architecture**: Dynamic workflows, streaming, quality validation
- **Enterprise Observability**: OpenTelemetry, Prometheus, structured logging

**Production Standards:**
- **StandardizedAgentBase** with Google ADK + MCPToolset pattern
- **A2AProtocolClient** with unified communication protocol
- **QualityThresholdFramework** with domain-specific configurations
- **UnifiedMCPToolServer** with consolidated tool ecosystem

---

## 1. Unified Agent Architecture Standards

### 1.0 Framework V2.0 Tier-Based Agent Template Rules

**MANDATORY FRAMEWORK RULES - Established by NU for A2A_MCP_FRAMEWORK V2.0:**

**Tier 1 - Master Orchestrators:**
- **MUST** use `EnhancedMasterOrchestratorTemplate` for all sophisticated multi-agent orchestration
- **MAY** use `LightweightMasterOrchestrator` for simple orchestration with clean planning separation
- **Purpose:** Strategic planning, task decomposition, complex domain coordination
- **Use Cases:** Business oracles, domain master orchestrators, complex workflow coordination
- **Key Features:** 
  - EnhancedGenericPlannerAgent delegation for strategic planning (simple/sophisticated modes)
  - Dynamic WorkflowGraph with real-time state management
  - PHASE 7 streaming with artifact events
  - Context & history tracking with intelligent Q&A
  - Session state management with pause/resume
  - Comprehensive observability (OpenTelemetry, Prometheus)
  - LangGraph integration, parallel workflow management
- **Ports:** 10000-10099 range

**Tier 2 - Domain Specialists:** 
- **MUST** use `StandardizedAgentBase` as the primary template
- **Purpose:** Domain expertise, specialized analysis, knowledge synthesis  
- **Use Cases:** Technical intelligence, knowledge management, research specialists, domain experts
- **Key Features:** Google ADK integration, MCP tools, A2A communication, quality validation
- **Ports:** 10200-10899 range

**Tier 3 - Service/MCP Agents (Dual Template Approach):**

**Template Choice Guidelines:**
- **Use `ADKServiceAgent`** for:
  - MCP-focused database agents 
  - Simple service coordination
  - Direct tool integration tasks
  - Legacy compatibility requirements
  - Streamlined MCP tool workflows

- **Use `StandardizedAgentBase`** for:
  - Complex service logic requiring full framework features
  - Agents needing advanced quality validation
  - Services requiring centralized configuration management
  - Future-forward implementations with full V2.0 capabilities

**Both templates are valid and production-ready for Tier 3 agents.**
- **Purpose:** Task execution, tool operations, database queries, direct service delivery
- **Ports:** 10900-10999 range

### 1.0.1 Framework V2.0 Complete Boilerplate Templates

**All templates are available in `src/a2a_mcp/common/` for universal access:**

**Core Agent Templates:**
- `EnhancedMasterOrchestratorTemplate` - Tier 1 sophisticated orchestration with 7 enhancement phases
- `LightweightMasterOrchestrator` - Simplified orchestrator for clean separation of concerns  
- `StandardizedAgentBase` - Tier 2/3 universal agent base
- `ADKServiceAgent` - Tier 3 streamlined MCP service agents (for legacy compatibility)

**Domain Implementation Templates:**
- `generic_a2a_client.py` - A2A JSON-RPC client template for domain frontends
- `agent_registry_template.py` - Tier-based agent organization template

**Template Usage Pattern:**
1. Copy `agent_registry_template.py` → `your_domain_agent_registry.py`
2. Copy `generic_a2a_client.py` → `your_domain_client.py` 
3. Customize agent definitions, ports, and domain-specific logic
4. Use Framework V2.0 tier-based template rules for each agent

### 1.1 StandardizedAgentBase Pattern (Universal Base)

```python
# PRODUCTION STANDARD: All agents inherit from StandardizedAgentBase
from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.common.quality_framework import QualityDomain

class ProductionAgent(StandardizedAgentBase):
    """Production agent following unified standards."""
    
    def __init__(self, domain_type: str):
        super().__init__(
            agent_name="Production Agent",
            description="Standardized production agent",
            instructions="System instructions...",
            quality_config={"domain": domain_type},  # business|academic|service|generic
            mcp_tools_enabled=True,
            a2a_enabled=True
        )
    
    async def _execute_agent_logic(self, query, context_id, task_id):
        """Agent-specific logic implementation."""
        # 1. Standardized initialization and context loading
        # 2. Domain-specific analysis and processing
        # 3. Unified tool utilization via MCP
        # 4. A2A communication with other agents (if needed)
        # 5. Quality validation and response formatting
        pass
```

**Key Features**:
- **Graceful Degradation**: Fallback modes when MCP/A2A unavailable
- **Unified Error Handling**: Consistent exception management
- **Quality Integration**: Automatic quality threshold validation
- **Health Monitoring**: Built-in agent health checking

### 1.2 Agent Type Specializations

#### **Oracle Agents (Complex Multi-Intelligence)**
```python
class OracleAgent(StandardizedAgentBase):
    """Oracle agent with sophisticated orchestration capabilities."""
    
    def __init__(self, oracle_domain: str):
        super().__init__(
            agent_name=f"{oracle_domain} Oracle",
            description=f"Master {oracle_domain} intelligence orchestrator",
            instructions=f"You are a master {oracle_domain} oracle...",
            quality_config={
                "domain": "business",  # or "academic" for research oracles
                "thresholds": {
                    "confidence_score": 0.75,
                    "technical_feasibility": 0.8,
                    "domain_coverage": 2.0
                }
            }
        )
        self.domain_specialists = []
        self.orchestration_enabled = True
    
    async def _execute_agent_logic(self, query, context_id, task_id):
        # Oracle-specific multi-intelligence orchestration
        # 1. Domain dependency analysis
        # 2. Parallel coordination of specialists via A2A
        # 3. Sophisticated synthesis and quality validation
        pass
```

#### **Service Agents (Dual Template Options)**

**Option A: ADKServiceAgent (Tier 3 - MCP/Database Focus)**
```python
from a2a_mcp.common.adk_service_agent import ADKServiceAgent

class MCPServiceAgent(ADKServiceAgent):
    """MCP-focused service agent for direct tool integration."""
    
    def __init__(self, service_domain: str):
        super().__init__(
            agent_name=f"{service_domain} Service Agent",
            description=f"{service_domain} MCP tool coordination",
            instructions=f"You are a {service_domain} service agent focused on tool execution...",
            a2a_enabled=True,
            quality_domain=QualityDomain.SERVICE
        )
    
    # Inherits stream() method with built-in MCP tool integration
    # Optimized for database queries and direct service delivery
```

**Option B: StandardizedAgentBase (Tier 3 - Full Framework Features)**
```python
class AdvancedServiceAgent(StandardizedAgentBase):
    """Service agent with full framework capabilities."""
    
    def __init__(self, service_domain: str):
        super().__init__(
            agent_name=f"{service_domain} Agent",
            description=f"{service_domain} service coordination",
            instructions=f"You are a {service_domain} service agent...",
            quality_config={"domain": "service"}
        )
    
    async def _execute_agent_logic(self, query, context_id, task_id):
        # Service-specific tool coordination
        # 1. Service request processing
        # 2. Tool utilization and coordination
        # 3. Service quality validation
        pass
```

#### **Research Agents (Academic-Focused)**
```python
class ResearchAgent(StandardizedAgentBase):
    """Research agent with academic quality standards."""
    
    def __init__(self, research_domain: str):
        super().__init__(
            agent_name=f"{research_domain} Research Agent",
            description=f"{research_domain} research and analysis",
            instructions=f"You are a {research_domain} research specialist...",
            quality_config={"domain": "academic"}
        )
    
    async def _execute_agent_logic(self, query, context_id, task_id):
        # Research-specific analysis
        # 1. Academic rigor and methodology
        # 2. Evidence-based analysis
        # 3. Bias detection and validation
        pass
```

---

## 2. Unified Communication Protocol

### 2.1 A2A Protocol Standardization

```python
# PRODUCTION STANDARD: Unified A2A communication
from a2a_mcp.common.a2a_protocol import A2AProtocolClient, create_a2a_request

class StandardizedAgentBase:
    def __init__(self, ...):
        self.a2a_client = A2AProtocolClient(
            default_timeout=60,
            max_retries=3,
            retry_delay=1.0
        )
    
    async def communicate_with_agent(self, target_agent: str, message: str, metadata=None):
        """Unified inter-agent communication."""
        from a2a_mcp.common.a2a_protocol import get_agent_port
        
        target_port = get_agent_port(target_agent)
        response = await self.a2a_client.send_message(
            target_port, message, metadata
        )
        return response

# Standard port mapping for consistent agent communication
A2A_AGENT_PORTS = {
    "solopreneur_oracle": 10901,
    "technical_intelligence": 10902,
    "knowledge_management": 10903,
    "personal_optimization": 10904,
    "learning_enhancement": 10905,
    "integration_synthesis": 10906,
    "nexus_oracle": 12000,
    "travel_agent": 11000,
    # ... additional agents
}
```

**Communication Features**:
- **Retry Logic**: Exponential backoff with configurable attempts
- **Timeout Management**: Per-request and connection timeouts
- **Error Recovery**: Graceful handling of network failures
- **Health Monitoring**: Agent availability checking

### 2.2 Multi-Agent Orchestration Patterns

#### **Oracle Pattern: Master-Specialist Coordination**
```python
async def oracle_orchestration_pattern(self, query, specialists):
    """Master oracle coordinating multiple domain specialists."""
    
    # 1. Dependency analysis
    dependencies = await self.analyze_domain_dependencies(query)
    
    # 2. Parallel coordination
    results = {}
    for phase in dependencies["execution_plan"]:
        if phase["parallel_execution"]:
            # Parallel execution via A2A
            tasks = []
            for specialist in phase["specialists"]:
                task = self.communicate_with_agent(specialist, query)
                tasks.append(task)
            
            phase_results = await asyncio.gather(*tasks, return_exceptions=True)
            for specialist, result in zip(phase["specialists"], phase_results):
                if not isinstance(result, Exception):
                    results[specialist] = result
    
    # 3. Synthesis and quality validation
    synthesis = await self.generate_synthesis(query, results)
    validated_synthesis = await self.quality_framework.validate_response(synthesis, query)
    
    return validated_synthesis
```

---

## 3. Quality Framework Standards

### 3.1 Domain-Specific Quality Configurations

```python
# PRODUCTION STANDARD: Configurable quality frameworks
from a2a_mcp.common.quality_framework import QualityThresholdFramework, QualityDomain

# Business Domain (Solopreneur, Market Intelligence)
business_quality_config = {
    "domain": QualityDomain.BUSINESS,
    "enabled": True,
    "thresholds": {
        "confidence_score": {"min_value": 0.75, "weight": 1.0},
        "technical_feasibility": {"min_value": 0.8, "weight": 1.2},
        "personal_sustainability": {"min_value": 0.7, "weight": 1.0},
        "risk_tolerance": {"min_value": 0.6, "max_value": 0.8, "weight": 0.8}
    }
}

# Academic Domain (Research, Nexus Oracle)
academic_quality_config = {
    "domain": QualityDomain.ACADEMIC,
    "enabled": True,
    "thresholds": {
        "research_confidence": {"min_value": 0.7, "weight": 1.0},
        "domain_coverage": {"min_value": 2.0, "max_value": 10.0, "weight": 1.1},
        "evidence_quality": {"min_value": 0.75, "weight": 1.2},
        "bias_detection": {"min_value": 0.6, "weight": 1.0},
        "methodological_rigor": {"min_value": 0.7, "weight": 1.1}
    }
}

# Service Domain (Travel, Booking, Tools)
service_quality_config = {
    "domain": QualityDomain.SERVICE,
    "enabled": True,
    "thresholds": {
        "service_reliability": {"min_value": 0.95, "weight": 1.3},
        "response_accuracy": {"min_value": 0.8, "weight": 1.0},
        "user_satisfaction": {"min_value": 0.75, "weight": 1.0}
    }
}

# Generic Domain (Default for unspecified domains)
generic_quality_config = {
    "domain": QualityDomain.GENERIC,
    "enabled": True,
    "thresholds": {
        "completeness": {"min_value": 0.8, "weight": 1.0},
        "accuracy": {"min_value": 0.85, "weight": 1.0},
        "relevance": {"min_value": 0.8, "weight": 1.0}
    }
}

# Creative Domain (Content creation, design)
creative_quality_config = {
    "domain": QualityDomain.CREATIVE,
    "enabled": True,
    "thresholds": {
        "originality": {"min_value": 0.7, "weight": 1.2},
        "coherence": {"min_value": 0.8, "weight": 1.0},
        "engagement": {"min_value": 0.75, "weight": 1.1}
    }
}

# Analytical Domain (Data analysis, research)
analytical_quality_config = {
    "domain": QualityDomain.ANALYTICAL,
    "enabled": True,
    "thresholds": {
        "data_accuracy": {"min_value": 0.9, "weight": 1.3},
        "methodology_soundness": {"min_value": 0.85, "weight": 1.2},
        "conclusion_validity": {"min_value": 0.8, "weight": 1.1}
    }
}

# Coding Domain (Software development)
coding_quality_config = {
    "domain": QualityDomain.CODING,
    "enabled": True,
    "thresholds": {
        "code_correctness": {"min_value": 0.9, "weight": 1.3},
        "best_practices": {"min_value": 0.8, "weight": 1.0},
        "performance": {"min_value": 0.75, "weight": 0.9}
    }
}

# Communication Domain (Customer service, support)
communication_quality_config = {
    "domain": QualityDomain.COMMUNICATION,
    "enabled": True,
    "thresholds": {
        "clarity": {"min_value": 0.85, "weight": 1.2},
        "helpfulness": {"min_value": 0.8, "weight": 1.1},
        "tone_appropriateness": {"min_value": 0.8, "weight": 1.0}
    }
}
```

### 3.2 Quality Validation Integration

```python
class StandardizedAgentBase:
    async def _apply_quality_validation(self, response, original_query):
        """Unified quality validation across all agent types."""
        
        if not self.quality_framework.is_enabled():
            return response
        
        # Extract quality metrics from response
        quality_result = await self.quality_framework.validate_response(
            response.get("content", {}), original_query
        )
        
        # Apply domain-specific quality standards
        if quality_result.get("quality_approved", True):
            logger.info(f'Quality validation passed for {self.agent_name}')
        else:
            logger.warning(f'Quality issues: {quality_result.get("quality_issues", [])}')
            # Add quality warning to response
            response["quality_warning"] = f"Threshold validation: {', '.join(quality_result.get('quality_issues', []))}"
        
        response["quality_metadata"] = quality_result
        return response
```

---

## 4. Unified Tool Ecosystem

### 4.1 Consolidated FastMCP Server

```python
# PRODUCTION STANDARD: Unified tool ecosystem
from a2a_mcp.common.unified_mcp_tools import UnifiedMCPToolServer

# Single tool server for all agent types
unified_server = UnifiedMCPToolServer(host="localhost", port=10100)

# Tool categories automatically registered:
# - agent_discovery: find_agent, list_available_agents
# - travel: query_places_data, query_travel_data  
# - solopreneur: metrics, trends, scheduling, workflows
# - system: health checks, tool management

# Health monitoring and statistics
health_status = unified_server.get_server().tool_call("mcp_server_health")
```

### 4.2 Standardized Tool Integration

```python
class StandardizedAgentBase:
    async def init_agent(self):
        """Standardized MCP tool loading."""
        if self.mcp_tools_enabled:
            config = get_mcp_server_config()
            
            # Unified tool loading pattern
            self.tools = await MCPToolset(
                connection_params=SseServerParams(url=config.url)
            ).get_tools()
            
            logger.info(f'Loaded {len(self.tools)} MCP tools')
        
        # Initialize Google ADK agent with loaded tools
        self.agent = Agent(
            name=self.agent_name,
            instruction=self.instructions,
            model=self.get_model_name(),
            tools=self.tools,
            generate_content_config=self.get_generation_config()
        )
```

---

## 5. Workflow Evolution and Management

### 5.1 Workflow System Architecture

The framework includes three workflow systems with increasing sophistication:

#### Basic Workflow (`workflow.py`)
- **Purpose**: Foundation workflow orchestration for multi-agent task execution
- **Architecture**:
  ```python
  # Graph-based workflow management
  workflow = WorkflowGraph()
  workflow.add_node("research", agent="researcher")
  workflow.add_edge("research", "analyze")
  ```
- **Key Features**:
  - Graph-based workflow management using NetworkX
  - A2A agent integration with automatic agent discovery
  - State management (READY, RUNNING, COMPLETED, PAUSED, INITIALIZED)
  - Real-time streaming support via AsyncIterable patterns
  - Automatic pause/resume on input requirements

#### Enhanced Workflow (`enhanced_workflow.py`)
- **Purpose**: Framework V2.0 sophisticated workflow capabilities
- **Architecture**:
  ```python
  # Dynamic workflow with runtime modifications
  workflow = DynamicWorkflowGraph()
  node = WorkflowNode(
      task="Analyze market data",
      node_key="analyst",
      metadata={"priority": "high", "timeout": 3600}
  )
  workflow.add_node(node)
  # Can modify graph during execution
  workflow.add_edge(node.id, new_node.id)
  ```
- **Key Enhancements**:
  - Dynamic graph building with runtime node/edge manipulation
  - Comprehensive state tracking with timestamps
  - Dependency resolution and execution ordering
  - Workflow statistics and health monitoring
  - Cycle detection for graph validation
  - Multiple workflow states (PENDING, RUNNING, PAUSED, COMPLETED, FAILED, CANCELLED)

#### Parallel Workflow (`parallel_workflow.py`)
- **Purpose**: Parallel task execution for performance optimization
- **Architecture**:
  ```python
  # Automatic parallel detection
  workflow = ParallelWorkflowGraph()
  parallel_levels = workflow.identify_parallel_tasks()
  # Executes independent tasks concurrently
  async for result in workflow.run_workflow():
      process_result(result)
  ```
- **Key Features**:
  - Automatic detection of parallelizable tasks
  - Level-based execution (BFS traversal)
  - Configurable parallel threshold
  - Mixed sequential/parallel execution modes
  - Visual execution plan generation

### 5.2 Planning Architecture

#### EnhancedGenericPlannerAgent (`planner_agent.py`)
- **Purpose**: Sophisticated planning with quality validation
- **Planning Modes**:
  ```python
  # Simple mode for basic tasks
  planner = EnhancedGenericPlannerAgent(
      planning_mode="simple"
  )
  
  # Sophisticated mode for complex scenarios
  planner = EnhancedGenericPlannerAgent(
      planning_mode="sophisticated",
      enable_quality_validation=True
  )
  ```
- **Capabilities**:
  - Domain specialist awareness and assignment
  - Quality validation framework integration
  - Dependency analysis and critical path identification
  - Resource estimation (time, cost, computational units)
  - Risk assessment with mitigation strategies
  - Plan templates for common scenarios

### 5.3 Additional Components

#### Event Queue System (`event_queue.py`)
- **Purpose**: Event-driven architecture support
- **Features**:
  - Async event processing
  - Priority queuing
  - Dead letter handling
  - Integration with streaming architecture

#### Session Context (`session_context.py`)
- **Purpose**: Session isolation and management
- **Features**:
  - State tracking per session
  - Context propagation
  - Automatic cleanup
  - Multi-session support

#### Response Formatter (`response_formatter.py`)
- **Purpose**: Standardized response formatting
- **Features**:
  - Consistent structure across all agents
  - Interactive mode detection
  - Progress and error formatting
  - Quality metadata integration

---

## 6. Integration Patterns

### Pattern 1: Basic Multi-Agent System
```python
# 1. Configure domain
config = ConfigManager()
domain_config = config.get_domain_config("finance")

# 2. Create orchestrator
orchestrator = EnhancedMasterOrchestratorTemplate(
    domain_name=domain_config["name"],
    domain_specialists=domain_config["specialists"]
)

# 3. Create specialists
agents = {}
for name, desc in domain_config["specialists"].items():
    agents[name] = GenericDomainAgent(
        domain=domain_config["name"],
        specialization=name,
        capabilities=[desc]
    )

# 4. Execute
result = await orchestrator.invoke("Analyze tech stocks", session_id)
```

### Pattern 2: Parallel Execution System
```python
# Create planner
planner = EnhancedGenericPlannerAgent(
    domain="DataAnalysis",
    planning_mode="sophisticated"
)

# Get plan
plan = planner.invoke("Process customer data", session_id)

# Create parallel workflow
workflow = ParallelWorkflowGraph()
for task in plan["tasks"]:
    workflow.add_node(task)

# Execute in parallel
async for result in workflow.run_workflow():
    process_result(result)
```

### Pattern 3: Quality-Validated System
```python
# Configure quality
quality = QualityThresholdFramework()
quality.configure_domain(QualityDomain.ANALYSIS)

# Create orchestrator with quality
orchestrator = EnhancedMasterOrchestratorTemplate(
    domain_name="Research",
    quality_domain=QualityDomain.ANALYSIS,
    quality_thresholds={"completeness": 0.9, "accuracy": 0.95}
)

# Results include quality metadata
result = await orchestrator.invoke(query, session_id)
quality_score = result["quality_metadata"]["overall_score"]
```

---

## 7. Performance and Scalability

### 7.1 Parallel Execution Benefits
- Reduced total execution time for independent tasks
- Automatic detection of parallelizable work
- Configurable parallelism thresholds
- Efficiency metrics: `parallel_efficiency = tasks_count / execution_time`

### 7.2 Connection Pooling Impact
- 60% performance improvement in inter-agent communication
- HTTP/2 connection reuse
- Reduced connection overhead
- Automatic health checking

### 7.3 Resource Optimization
- Task batching for similar operations
- Intelligent specialist assignment
- Cost-aware execution planning
- Connection pool metrics tracking

### 7.4 Scalability Features
- Asynchronous execution throughout
- Minimal blocking operations
- Session-based isolation
- Event-driven architecture

---

## 8. Common Pitfalls to Avoid

1. **Over-Engineering**: Don't use all components if not needed
2. **Ignoring Quality**: Always enable quality validation in production
3. **Sequential Only**: Consider parallel execution for performance
4. **No Monitoring**: Production systems must have observability
5. **Hard-Coded Config**: Use ConfigManager for flexibility
6. **Ignoring Streaming**: Use PHASE 7 for real-time visibility
7. **No Connection Pooling**: Essential for production performance

---

## 9. Production Deployment Standards

### 9.1 Agent Factory Integration

```python
# PRODUCTION PATTERN: Unified agent factory
from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase

def create_standardized_agent(agent_type: str, agent_config: Dict) -> StandardizedAgentBase:
    """Factory for creating standardized agents."""
    
    agent_classes = {
        "oracle": OracleAgent,
        "service": ServiceAgent,
        "research": ResearchAgent,
        "travel": TravelAgent,
        "solopreneur": SolopreneurAgent
    }
    
    agent_class = agent_classes.get(agent_type)
    if not agent_class:
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    return agent_class(**agent_config)

# Integration with existing get_agent() function
def get_agent(agent_card: AgentCard):
    """Enhanced agent factory with standardized patterns."""
    
    # Determine agent type from card
    agent_type = determine_agent_type(agent_card)
    
    # Create standardized agent
    config = extract_agent_config(agent_card)
    agent = create_standardized_agent(agent_type, config)
    
    return agent
```

### 5.2 Enterprise Observability Architecture

The Framework V2.0 includes comprehensive observability features for production monitoring:

#### **5.2.1 OpenTelemetry Integration**

```python
# PRODUCTION STANDARD: Distributed tracing
from a2a_mcp.common.observability import trace_async, trace_span, get_tracer

class StandardizedAgentBase:
    @trace_async("agent_execution")
    async def execute(self, query: str, context_id: str, task_id: str):
        """Agent execution with distributed tracing."""
        with trace_span("query_processing", {"query_length": len(query)}):
            # Processing logic with automatic trace propagation
            pass
```

#### **5.2.2 Prometheus Metrics Collection**

```python
# PRODUCTION STANDARD: Performance metrics
from a2a_mcp.common.observability import record_metric, measure_performance

# Available metrics:
# - orchestration_requests_total: Total orchestration requests by domain/status
# - tasks_executed_total: Tasks by specialist and status  
# - orchestration_duration_seconds: Execution time histograms
# - active_sessions: Current active session gauge
# - artifacts_created_total: Artifact creation tracking
# - errors_total: Errors by component and type

@measure_performance("task_duration_seconds")
async def execute_task(self, task: dict):
    """Task execution with automatic performance tracking."""
    result = await self._process_task(task)
    record_metric('tasks_executed_total', 1, 
                  {'specialist': self.agent_name, 'status': 'completed'})
    return result
```

#### **5.2.3 Structured JSON Logging**

```python
# PRODUCTION STANDARD: Structured logging with trace correlation
from a2a_mcp.common.observability import get_logger

logger = get_logger(__name__)

# Structured logging with contextual fields
logger.info("Task execution completed",
            session_id=session_id,
            task_id=task_id,
            duration=execution_time,
            specialist=agent_name)
```

#### **5.2.4 Grafana Dashboard Integration**

Pre-built dashboards available at `src/a2a_mcp/common/dashboards/`:
- Orchestration performance monitoring
- Task execution analytics
- Error rate tracking
- Session management visualization
- Artifact lifecycle monitoring

#### **5.2.5 Health Monitoring Enhanced**

```python
class StandardizedAgentBase:
    def get_health_status(self) -> Dict[str, Any]:
        """Enhanced health status with observability metrics."""
        return {
            "agent_name": self.agent_name,
            "initialization_complete": self.initialization_complete,
            "mcp_tools_enabled": self.mcp_tools_enabled,
            "mcp_tools_loaded": len(self.tools),
            "a2a_enabled": self.a2a_client is not None,
            "quality_framework_enabled": self.quality_framework.is_enabled(),
            "observability": {
                "tracing_enabled": self.tracing_enabled,
                "metrics_enabled": self.metrics_enabled,
                "active_traces": self.get_active_trace_count(),
                "metrics_summary": self.get_metrics_summary()
            },
            "session_stats": self.get_session_statistics(),
            "timestamp": datetime.now().isoformat()
        }
```

For complete observability deployment guide, see: `docs/OBSERVABILITY_DEPLOYMENT.md`

---

## 10. PHASE 7: Workflow Streaming with Artifact Events

### 10.1 Real-Time Streaming Architecture

The Master Orchestrator Template now supports real-time streaming with artifact events:

```python
# PRODUCTION STANDARD: Streaming with artifact events
from a2a_mcp.common.master_orchestrator_template import MasterOrchestratorTemplate

class DomainOrchestrator(MasterOrchestratorTemplate):
    async def stream_with_artifacts(self, query: str, sessionId: str, task_id: str):
        """
        Enhanced streaming providing real-time visibility into:
        - Task execution progress with percentage tracking
        - Artifact creation events as they happen
        - Performance metrics in real-time
        - Partial results for long-running tasks
        - Live workflow graph updates
        """
        async for event in super().stream_with_artifacts(query, sessionId, task_id):
            yield event
```

### 10.2 Streaming Event Types

```python
# Event structure for streaming
{
    'response_type': 'progress' | 'artifact' | 'task_update' | 'workflow_state',
    'is_task_complete': bool,
    'require_user_input': bool,
    'content': str | dict,
    'stage': str,  # Current execution stage
    'progress': float,  # 0.0 to 1.0
    'task_info': {  # For task updates
        'task_id': str,
        'specialist': str,
        'status': str,
        'partial_result': Any
    },
    'artifact_info': {  # For artifact events
        'artifact_id': str,
        'type': str,
        'size': int,
        'metadata': dict
    },
    'workflow_update': {  # For workflow state
        'nodes_pending': int,
        'nodes_executing': int,
        'nodes_completed': int,
        'execution_path': List[str]
    },
    'metrics': {  # Real-time performance
        'tasks_per_second': float,
        'avg_task_duration': float,
        'memory_usage': int
    }
}
```

### 10.3 Integration with Observability

Streaming sessions are fully integrated with the observability stack:

```python
# Streaming with automatic observability
class EnhancedStreaming:
    @trace_async("streaming_session")
    async def stream_with_artifacts(self, query: str, sessionId: str):
        # Initialize streaming metrics
        streaming_session_id = f"{sessionId}_stream_{timestamp}"
        
        # Track streaming performance
        record_metric('streaming_sessions_active', 1)
        
        try:
            async for event in self._generate_stream_events():
                # Record event metrics
                record_metric('streaming_events_total', 1, 
                             {'event_type': event['response_type']})
                yield event
        finally:
            # Cleanup and record session metrics
            record_metric('streaming_duration_seconds', duration)
```

---

## 11. Migration from Legacy Patterns

### 11.1 Oracle Agent Migration

```python
# BEFORE: Legacy Oracle implementation
class LegacyOracleAgent(BaseAgent):
    def __init__(self):
        # Custom initialization
        # Hardcoded quality thresholds
        # Inconsistent MCP integration
        pass

# AFTER: Standardized Oracle implementation
class ModernOracleAgent(StandardizedAgentBase):
    def __init__(self, oracle_domain: str):
        super().__init__(
            agent_name=f"{oracle_domain} Oracle",
            description=f"Standardized {oracle_domain} oracle",
            instructions=f"You are a master {oracle_domain} oracle...",
            quality_config={"domain": "business"},
            mcp_tools_enabled=True,
            a2a_enabled=True
        )
    
    async def _execute_agent_logic(self, query, context_id, task_id):
        # Standardized oracle orchestration
        pass
```

### 11.2 Travel Agent Migration

```python
# BEFORE: Legacy Travel implementation
class LegacyTravelAgent(BaseAgent):
    def __init__(self):
        # Custom ADK initialization
        # Manual tool loading
        # No quality validation
        pass

# AFTER: Standardized Travel implementation  
class ModernTravelAgent(StandardizedAgentBase):
    def __init__(self):
        super().__init__(
            agent_name="Travel Agent",
            description="Standardized travel planning agent",
            instructions="You are a travel planning specialist...",
            quality_config={"domain": "service"}
        )
    
    async def _execute_agent_logic(self, query, context_id, task_id):
        # Standardized service coordination
        pass
```

---

## 12. Best Practices and Guidelines

### 12.1 Agent Development Guidelines

**DO:**
- ✅ Inherit from StandardizedAgentBase
- ✅ Use A2AProtocolClient for inter-agent communication
- ✅ Configure domain-appropriate quality thresholds
- ✅ Implement comprehensive error handling
- ✅ Use UnifiedMCPToolServer for tool access

**DON'T:**
- ❌ Create custom base agent classes
- ❌ Hardcode communication protocols
- ❌ Skip quality validation
- ❌ Ignore health monitoring
- ❌ Duplicate tool implementations

### 12.2 Quality Standards

**Business Domain Agents:**
- Focus on practical implementation success
- Emphasize risk management and sustainability
- Validate technical feasibility

**Academic Domain Agents:**
- Prioritize research rigor and evidence quality
- Implement bias detection mechanisms
- Ensure multi-disciplinary coverage

**Service Domain Agents:**
- Maximize reliability and accuracy
- Optimize for user satisfaction
- Implement comprehensive error handling

### 12.3 Performance Optimization

```python
# PRODUCTION PATTERN: Performance-optimized agent
class OptimizedAgent(StandardizedAgentBase):
    def __init__(self, ...):
        super().__init__(...)
        # Performance tuning
        self.cache_enabled = True
        self.parallel_threshold = 3  # Use parallel execution for 3+ tasks
        self.timeout_strategy = "adaptive"  # Adaptive timeouts based on load
    
    def get_agent_temperature(self) -> float:
        """Optimized temperature for consistent results."""
        return 0.1
    
    def get_model_name(self) -> str:
        """Performance-optimized model selection."""
        return 'gemini-2.0-flash'  # Fast and efficient
```

---

## 13. Framework Evolution Roadmap

### 13.1 Current Status (V2.0)
- ✅ Unified agent architecture standards
- ✅ Standardized communication protocol
- ✅ Configurable quality frameworks
- ✅ Consolidated tool ecosystem
- ✅ Production deployment patterns
- ✅ **ENHANCED MASTER ORCHESTRATOR CAPABILITIES**
  - ✅ PHASE 1-7: Complete implementation of all enhancement phases
  - ✅ Dynamic WorkflowGraph with state management
  - ✅ Context & history tracking with intelligent Q&A
  - ✅ Artifact management and result collection
  - ✅ Real-time streaming with artifact events
  - ✅ Session state management with pause/resume
- ✅ **ENTERPRISE OBSERVABILITY**
  - ✅ OpenTelemetry distributed tracing integration
  - ✅ Prometheus metrics collection
  - ✅ Structured JSON logging with trace correlation
  - ✅ Pre-built Grafana dashboards
  - ✅ Comprehensive health monitoring
- ✅ **SOLOPRENEUR ORACLE: FULL FRAMEWORK V2.0 COMPLIANCE ACHIEVED**
  - ✅ Complete StandardizedAgentBase inheritance with sophisticated orchestration preserved
  - ✅ A2AProtocolClient integration with graceful degradation fallbacks
  - ✅ QualityThresholdFramework with QualityDomain.BUSINESS configuration
  - ✅ Google ADK + LangGraph integration maintaining original sophistication
  - ✅ Production-ready Framework V2.0 reference implementation

### 13.2 Future Enhancements (V2.1+)
- **Advanced Orchestration**: Distributed workflow management across multiple nodes
- **Intelligent Caching**: Agent response caching and optimization
- **Dynamic Scaling**: Auto-scaling based on load patterns
- **Enhanced Security**: OAuth2/JWT authentication standards
- **Multi-Cloud Support**: AWS/GCP/Azure native integrations
- **GraphQL API**: Alternative to JSON-RPC for modern clients

---

## 14. Conclusion

The **A2A-MCP Framework V2.0** represents a significant evolution from Oracle-specific patterns to **universal multi-agent standards**. This framework provides:

1. **Architectural Consistency**: All agents follow standardized patterns
2. **Quality Assurance**: Domain-specific configurable quality frameworks
3. **Scalable Communication**: Unified A2A protocol with robust error handling
4. **Tool Consolidation**: Single FastMCP server with organized tool ecosystem
5. **Production Readiness**: Comprehensive health monitoring and observability

**Framework Benefits:**
- **Developer Productivity**: Consistent patterns reduce development time
- **System Reliability**: Standardized error handling and fallback mechanisms
- **Quality Assurance**: Automated quality validation across all agent types
- **Operational Excellence**: Unified monitoring and health checking
- **Future-Proof Architecture**: Extensible framework supporting new agent types

This unified framework establishes the foundation for **enterprise-grade multi-agent systems** that can scale from simple service agents to sophisticated oracle orchestrators while maintaining consistency, quality, and reliability across all implementations.