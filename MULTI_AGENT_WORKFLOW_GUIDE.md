# Multi-Agent System Creation Workflow Guide

## Overview

This guide provides a step-by-step workflow for creating multi-agent systems using the A2A-MCP Framework V2.0. For comprehensive component documentation and orchestration patterns, see the [Framework Components and Orchestration Guide](./FRAMEWORK_COMPONENTS_AND_ORCHESTRATION_GUIDE.md).

## Workflow Summary

### Step 1: Define Domain and Requirements
```yaml
domain:
  name: "YourDomain"
  description: "What your system does"
  specialists:
    specialist_1: "Description of specialist 1's role"
    specialist_2: "Description of specialist 2's role"
  requirements:
    performance: "high|medium|low"
    quality_validation: true
    observability: true
    parallel_execution: true
```

### Step 2: Choose Architecture Pattern

#### Option A: Production-Ready System
```python
# Full enterprise architecture with all features
from a2a_mcp.common.master_orchestrator_template import EnhancedMasterOrchestratorTemplate
from a2a_mcp.common.quality_framework import QualityDomain
from a2a_mcp.common.observability import ObservabilityManager

# Initialize observability
observability = ObservabilityManager()
observability.init_tracing()

# Create orchestrator
orchestrator = EnhancedMasterOrchestratorTemplate(
    domain_name="YourDomain",
    domain_specialists=specialists,
    quality_domain=QualityDomain.ANALYSIS,
    enable_phase_7_streaming=True,
    enable_observability=True
)
```

#### Option B: Lightweight Prototype
```python
# Simplified architecture for quick development
from a2a_mcp.common.lightweight_orchestrator_template import LightweightMasterOrchestrator
from a2a_mcp.common.workflow import WorkflowGraph

orchestrator = LightweightMasterOrchestrator(
    domain_name="YourDomain",
    domain_specialists=specialists,
    planning_mode="simple"
)
```

### Step 3: Create Domain Specialists

```python
from a2a_mcp.common.generic_domain_agent import GenericDomainAgent
from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase

# For simple specialists
def create_specialists(domain_config):
    specialists = {}
    for name, description in domain_config["specialists"].items():
        specialist = GenericDomainAgent(
            domain=domain_config["name"],
            specialization=name,
            capabilities=[description],
            tools=get_tools_for_specialist(name)
        )
        specialists[name] = specialist
    return specialists

# For custom specialists
class CustomSpecialist(StandardizedAgentBase):
    def __init__(self, specialization: str):
        super().__init__(
            agent_name=f"{specialization} Specialist",
            description=f"Custom implementation for {specialization}"
        )
        # Add custom logic
```

### Step 4: Configure Workflow

```python
from a2a_mcp.common.enhanced_workflow import DynamicWorkflowGraph
from a2a_mcp.common.parallel_workflow import ParallelWorkflowGraph

# For dynamic workflows
workflow_manager = DynamicWorkflowGraph()

# For parallel execution
parallel_workflow = ParallelWorkflowGraph(
    parallel_threshold=3,  # Execute in parallel if 3+ independent tasks
    enable_progress_tracking=True
)
```

### Step 5: Set Up Communication

```python
from a2a_mcp.common.a2a_protocol import A2AProtocolClient
from a2a_mcp.common.connection_pool import ConnectionPool
from a2a_mcp.common.mcp_client import MCPClient

# Initialize connection pool for performance
connection_pool = ConnectionPool(
    max_connections=10,
    enable_http2=True
)

# A2A Protocol for inter-agent communication
a2a_client = A2AProtocolClient(connection_pool)

# MCP Client for tool servers
mcp_client = MCPClient(
    server_config=get_mcp_server_config()
)
```

### Step 6: Implement Quality & Monitoring

```python
from a2a_mcp.common.quality_framework import QualityThresholdFramework
from a2a_mcp.common.metrics_collector import MetricsCollector
from a2a_mcp.common.structured_logger import StructuredLogger

# Quality validation
quality_framework = QualityThresholdFramework()
quality_framework.configure_domain(QualityDomain.ANALYSIS)
quality_framework.set_thresholds({
    "completeness": 0.9,
    "accuracy": 0.95,
    "relevance": 0.85
})

# Metrics collection
metrics = MetricsCollector(
    namespace="a2a_mcp",
    subsystem="your_domain"
)

# Structured logging
logger = StructuredLogger("your_domain")
```

### Step 7: Create Configuration

```python
from a2a_mcp.common.config_manager import ConfigManager

# config/your_domain.yaml
config_content = """
domain:
  name: YourDomain
  version: "2.0"
  
specialists:
  analyst:
    description: "Analyzes data and provides insights"
    port: 14001
    tools:
      - data_analysis_tool
      - visualization_tool
  
  researcher:
    description: "Conducts research and gathers information"
    port: 14002
    tools:
      - web_search_tool
      - document_analysis_tool

workflow:
  default_strategy: "parallel"
  max_parallel_tasks: 5
  timeout_seconds: 300

quality:
  domain: "ANALYSIS"
  thresholds:
    completeness: 0.9
    accuracy: 0.95

observability:
  tracing:
    enabled: true
  metrics:
    enabled: true
  logging:
    level: "INFO"
"""

# Load configuration
config_manager = ConfigManager()
config = config_manager.load_config("your_domain.yaml")
```

### Step 8: Implement Main Execution Flow

```python
async def create_multi_agent_system(query: str, session_id: str):
    """Main entry point for multi-agent system execution."""
    
    # 1. Initialize system
    orchestrator = create_orchestrator(config)
    specialists = create_specialists(config)
    
    # 2. Start monitoring
    with metrics.track_agent_request("orchestrator"):
        
        # 3. Execute with streaming
        if config.get("streaming", {}).get("enabled", True):
            async for event in orchestrator.stream_with_artifacts(
                query, session_id, task_id=str(uuid.uuid4())
            ):
                # Handle streaming events
                if event["type"] == "planning":
                    logger.info("Planning phase", extra={"event": event})
                elif event["type"] == "execution":
                    logger.info("Execution update", extra={"event": event})
                elif event["type"] == "artifact":
                    process_artifact(event["artifact"])
        else:
            # Non-streaming execution
            result = await orchestrator.invoke(query, session_id)
            
        # 4. Validate quality
        quality_result = quality_framework.validate_output(result)
        
        # 5. Return results
        return {
            "result": result,
            "quality": quality_result,
            "metrics": metrics.get_metrics_summary()
        }
```

### Step 9: Deploy and Monitor

```python
# Start services
async def start_services():
    # 1. Start metrics server
    await metrics.start_metrics_server(port=9090)
    
    # 2. Start agent runners
    for specialist in specialists.values():
        runner = AgentRunner(specialist)
        await runner.start()
    
    # 3. Start orchestrator
    orchestrator_runner = AgentRunner(orchestrator)
    await orchestrator_runner.start()
    
    # 4. Health monitoring
    while True:
        health_status = await check_system_health()
        logger.info("System health", extra=health_status)
        await asyncio.sleep(30)
```

## Common Patterns

### Pattern 1: Sequential Analysis
```python
# For ordered, dependent tasks
workflow = WorkflowGraph()
workflow.add_node("research", "Research topic")
workflow.add_node("analyze", "Analyze findings") 
workflow.add_edge("research", "analyze")  # analyze depends on research
```

### Pattern 2: Parallel Processing
```python
# For independent tasks
parallel_tasks = [
    {"id": "task1", "description": "Analyze dataset A"},
    {"id": "task2", "description": "Analyze dataset B"},
    {"id": "task3", "description": "Analyze dataset C"}
]
results = await parallel_workflow.execute_parallel_tasks(parallel_tasks)
```

### Pattern 3: Hybrid Execution
```python
# Mix of sequential and parallel
plan = planner.create_sophisticated_plan(query)
# Planner determines optimal execution strategy
if plan["coordination_strategy"] == "hybrid":
    await orchestrator.execute_hybrid_plan(plan)
```

## Best Practices

1. **Start with Configuration**: Define your domain in YAML/JSON first
2. **Use Type Hints**: Leverage Python type hints for better IDE support
3. **Enable Observability Early**: Add tracing and metrics from the start
4. **Test Quality Thresholds**: Validate quality settings with sample data
5. **Monitor Performance**: Use connection pooling and parallel execution
6. **Handle Errors Gracefully**: Implement retry logic and fallbacks
7. **Document Specialists**: Clear descriptions help the planner assign tasks

## Example: Financial Analysis System

```python
# Complete example
async def create_financial_analysis_system():
    # Domain configuration
    domain_config = {
        "name": "FinancialAnalysis",
        "specialists": {
            "market_analyst": "Analyzes market trends and indicators",
            "risk_assessor": "Evaluates investment risks",
            "portfolio_optimizer": "Optimizes portfolio allocation",
            "report_generator": "Creates comprehensive reports"
        }
    }
    
    # Create orchestrator with all features
    orchestrator = EnhancedMasterOrchestratorTemplate(
        domain_name=domain_config["name"],
        domain_specialists=domain_config["specialists"],
        quality_domain=QualityDomain.ANALYSIS,
        enable_phase_7_streaming=True,
        enable_observability=True,
        quality_thresholds={
            "completeness": 0.95,
            "accuracy": 0.98,
            "relevance": 0.90
        }
    )
    
    # Execute analysis
    query = "Analyze tech sector performance and recommend portfolio adjustments"
    async for event in orchestrator.stream_with_artifacts(query, "session_123", "task_456"):
        if event["type"] == "artifact" and event["artifact"]["type"] == "analysis":
            print(f"Analysis: {event['artifact']['content']}")
        elif event["type"] == "completion":
            print(f"Final recommendations: {event['result']}")
```

## Troubleshooting

### Common Issues
1. **Agents Not Communicating**: Check A2A protocol configuration and ports
2. **Poor Performance**: Enable connection pooling and parallel execution
3. **Quality Validation Failures**: Adjust thresholds based on domain requirements
4. **Missing Traces**: Ensure OpenTelemetry is properly configured
5. **Configuration Errors**: Validate YAML syntax and required fields

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable trace details
orchestrator = EnhancedMasterOrchestratorTemplate(
    domain_name="Debug",
    debug_mode=True,
    trace_details=True
)
```

## Next Steps

1. Review example implementations in `examples/` directory
2. Customize specialists for your domain
3. Configure quality thresholds
4. Set up monitoring dashboards
5. Test with sample queries
6. Deploy to production

For detailed component documentation and orchestration patterns, see [FRAMEWORK_COMPONENTS_AND_ORCHESTRATION_GUIDE.md](./FRAMEWORK_COMPONENTS_AND_ORCHESTRATION_GUIDE.md).