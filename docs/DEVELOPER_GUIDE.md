# A2A-MCP Framework V2.0 Developer Guide

## Overview

This guide provides comprehensive instructions for developing multi-agent systems using the A2A-MCP Framework V2.0. The framework has evolved with enterprise-grade features including quality validation, observability, and sophisticated orchestration patterns.

## V2.0 Architecture Overview

### Core Components
- **StandardizedAgentBase**: Universal base class with quality validation and observability
- **Master Orchestrator Templates**: 3 options for different complexity levels
- **Enhanced Workflows**: Dynamic graph management and parallel execution
- **Quality Framework**: Domain-specific validation with configurable thresholds
- **Observability Stack**: OpenTelemetry, Prometheus, and structured logging

### Essential Documentation
Before starting development, review:
- [Framework Components & Orchestration Guide](./FRAMEWORK_COMPONENTS_AND_ORCHESTRATION_GUIDE.md)
- [Multi-Agent Workflow Guide](./MULTI_AGENT_WORKFLOW_GUIDE.md)

## Quick Start: Creating Your First Agent

### Option 1: Using Generic Domain Agent (Fastest)

```python
from a2a_mcp.common.generic_domain_agent import GenericDomainAgent
from a2a_mcp.common.quality_framework import QualityDomain

# Create a specialist in seconds
agent = GenericDomainAgent(
    domain="Finance",
    specialization="market_analyst",
    capabilities=["Analyze market trends", "Evaluate stocks", "Generate reports"],
    quality_domain=QualityDomain.ANALYSIS,
    tools=["web_search", "data_analysis", "chart_generation"]
)
```

### Option 2: Custom Agent with V2.0 Features

```python
from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.common.quality_framework import QualityDomain
from a2a_mcp.common.observability import trace_async
from typing import Dict, Any

class CustomFinanceAgent(StandardizedAgentBase):
    def __init__(self):
        super().__init__(
            agent_name="Custom Finance Specialist",
            description="Advanced financial analysis with quality validation",
            instructions=self._get_custom_instructions(),
            content_types=['text', 'application/json'],
            quality_config={
                "domain": QualityDomain.ANALYSIS,
                "thresholds": {
                    "completeness": 0.9,
                    "accuracy": 0.95,
                    "relevance": 0.85
                }
            },
            mcp_tools_enabled=True,
            a2a_enabled=True,
            enable_observability=True  # V2.0 feature
        )
    
    @trace_async  # Automatic distributed tracing
    async def process_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process request with automatic quality validation and tracing."""
        try:
            # Extract request details
            action = message.get("action")
            data = message.get("data", {})
            
            # Process based on action
            if action == "analyze_market":
                result = await self._analyze_market(data)
            elif action == "evaluate_portfolio":
                result = await self._evaluate_portfolio(data)
            else:
                result = {"error": "Unknown action", "status": "failed"}
            
            # V2.0: Automatic response formatting and quality validation
            return self.format_response(result)
            
        except Exception as e:
            self.logger.error(f"Processing error: {e}", extra={"trace_id": self.get_trace_id()})
            return self.format_error_response(str(e))
    
    async def _analyze_market(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market with quality checks."""
        # Use MCP tools
        market_data = await self.use_mcp_tool("market_data_fetch", data)
        
        # Process with LLM
        analysis = await self._process_with_llm(
            f"Analyze market data: {market_data}",
            quality_check=True  # V2.0: Inline quality validation
        )
        
        return {
            "analysis": analysis,
            "confidence": 0.92,
            "data_points": len(market_data)
        }
```

## Creating Multi-Agent Systems

### Step 1: Choose Your Orchestrator

#### For Production Systems
```python
from a2a_mcp.common.master_orchestrator_template import EnhancedMasterOrchestratorTemplate
from a2a_mcp.common.quality_framework import QualityDomain

orchestrator = EnhancedMasterOrchestratorTemplate(
    domain_name="FinancialAnalysis",
    domain_description="Comprehensive financial analysis platform",
    domain_specialists={
        "market_analyst": "Analyzes market trends and indicators",
        "risk_assessor": "Evaluates investment risks",
        "portfolio_manager": "Optimizes portfolio allocation"
    },
    quality_domain=QualityDomain.ANALYSIS,
    enable_phase_7_streaming=True,  # Real-time execution visibility
    enable_observability=True,
    quality_thresholds={
        "completeness": 0.95,
        "accuracy": 0.98,
        "relevance": 0.90
    }
)
```

#### For Prototypes
```python
from a2a_mcp.common.lightweight_orchestrator_template import LightweightMasterOrchestrator

orchestrator = LightweightMasterOrchestrator(
    domain_name="SimpleAnalysis",
    domain_description="Quick analysis system",
    domain_specialists={"analyst": "General analysis"},
    planning_mode="simple"
)
```

### Step 2: Configure Workflows

#### Dynamic Workflow (V2.0)
```python
from a2a_mcp.common.enhanced_workflow import DynamicWorkflowGraph
from a2a_mcp.common.workflow import WorkflowNode

# Create dynamic workflow
workflow = DynamicWorkflowGraph()

# Add nodes with metadata
analysis_node = WorkflowNode(
    task="Market analysis",
    node_key="market_analyst",
    metadata={
        "priority": "high",
        "timeout": 3600,
        "quality_threshold": 0.9
    }
)
workflow.add_node(analysis_node)

# Add dependencies dynamically
risk_node = WorkflowNode(
    task="Risk assessment",
    node_key="risk_assessor",
    dependencies=[analysis_node.id]
)
workflow.add_node(risk_node)

# Execute with progress tracking
async for event in workflow.stream_execution():
    print(f"Progress: {event['progress']}% - {event['message']}")
```

#### Parallel Workflow (V2.0)
```python
from a2a_mcp.common.parallel_workflow import ParallelWorkflowGraph

# Automatic parallel detection
parallel_workflow = ParallelWorkflowGraph(
    parallel_threshold=3,  # Execute if 3+ independent tasks
    enable_progress_tracking=True
)

# Add independent tasks
for task in independent_tasks:
    parallel_workflow.add_node(task)

# Execute with automatic parallelization
results = await parallel_workflow.execute_parallel()
```

## Quality Framework Integration

### Configuring Quality Domains

```python
from a2a_mcp.common.quality_framework import QualityThresholdFramework, QualityDomain

# Initialize quality framework
quality = QualityThresholdFramework()

# Configure for your domain
quality.configure_domain(QualityDomain.ANALYSIS)
quality.set_thresholds({
    "completeness": 0.9,
    "accuracy": 0.95,
    "relevance": 0.85,
    "coherence": 0.88
})

# Validate outputs
validation_result = quality.validate_output(agent_response)
if validation_result["passed"]:
    print(f"Quality score: {validation_result['overall_score']}")
else:
    print(f"Failed metrics: {validation_result['failed_metrics']}")
```

### Available Quality Domains
- **GENERIC**: General purpose validation
- **CREATIVE**: Creative content generation
- **ANALYTICAL**: Data analysis and research
- **CODING**: Code generation and review
- **COMMUNICATION**: Customer interaction

## Observability Implementation

### Setting Up Tracing

```python
from a2a_mcp.common.observability import ObservabilityManager, trace_async

# Initialize observability (done automatically with StandardizedAgentBase)
obs_manager = ObservabilityManager()

# Manual tracing for custom methods
@trace_async
async def complex_operation(self, data):
    # Automatically traced with span creation
    result = await self.process_data(data)
    
    # Add custom span attributes
    span = obs_manager.get_current_span()
    if span:
        span.set_attribute("data.size", len(data))
        span.set_attribute("result.confidence", result["confidence"])
    
    return result
```

### Metrics Collection

```python
from a2a_mcp.common.metrics_collector import get_metrics_collector

metrics = get_metrics_collector()

# Track agent requests
with metrics.track_agent_request("my_agent"):
    result = await agent.process(request)

# Record custom metrics
metrics.record_quality_validation(
    domain="Finance",
    status="passed",
    scores={"accuracy": 0.96, "completeness": 0.94}
)

# Get metrics summary
summary = metrics.get_metrics_summary()
print(f"Total requests: {summary['agent_metrics']['my_agent']['total_requests']}")
```

### Structured Logging

```python
from a2a_mcp.common.structured_logger import StructuredLogger

logger = StructuredLogger("my_agent")

# Logs include trace context automatically
logger.info("Processing request", extra={
    "request_id": request_id,
    "action": action,
    "user_id": user_id
})

# Error logging with context
logger.error("Processing failed", extra={
    "error_type": "validation",
    "details": validation_errors
}, exc_info=True)
```

## PHASE 7 Streaming Implementation

### Real-time Execution Visibility

```python
# Enable PHASE 7 streaming in orchestrator
async for event in orchestrator.stream_with_artifacts(
    query="Analyze tech sector performance",
    session_id=session_id,
    task_id=task_id
):
    if event["type"] == "planning":
        print(f"Planning: {event['content']}")
    elif event["type"] == "task_start":
        print(f"Starting: {event['task']['description']}")
    elif event["type"] == "artifact":
        # Real-time artifact streaming
        artifact = event["artifact"]
        print(f"Artifact: {artifact['type']} - {artifact['title']}")
    elif event["type"] == "progress":
        print(f"Progress: {event['percentage']}%")
    elif event["type"] == "completion":
        print(f"Completed: {event['result']}")
```

## Connection Pooling for Performance

```python
from a2a_mcp.common.connection_pool import ConnectionPool

# Initialize connection pool (60% performance improvement)
pool = ConnectionPool(
    max_connections=20,
    max_keepalive_connections=10,
    keepalive_expiry=30.0,
    enable_http2=True
)

# Use with A2A protocol
from a2a_mcp.common.a2a_protocol import A2AProtocolClient
a2a_client = A2AProtocolClient(connection_pool=pool)

# Monitor pool performance
pool_stats = pool.get_statistics()
print(f"Reuse rate: {pool_stats['connection_reuse_rate']}%")
```

## Testing Your Agents

### Unit Testing with V2.0 Features

```python
import pytest
from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.common.quality_framework import QualityDomain

@pytest.fixture
async def test_agent():
    agent = CustomFinanceAgent()
    await agent.initialize()
    yield agent
    await agent.cleanup()

async def test_agent_quality_validation(test_agent):
    """Test that agent responses meet quality thresholds."""
    response = await test_agent.process_request({
        "action": "analyze_market",
        "data": {"symbol": "AAPL"}
    })
    
    # Check response format
    assert response["response_type"] in ["data", "structured"]
    assert response["is_task_complete"] == True
    
    # Check quality metadata
    assert "quality_metadata" in response
    assert response["quality_metadata"]["overall_score"] >= 0.9

async def test_agent_observability(test_agent):
    """Test that agent creates proper traces."""
    with test_agent.tracer.start_as_current_span("test_span") as span:
        response = await test_agent.process_request({
            "action": "analyze_market",
            "data": {"symbol": "GOOGL"}
        })
        
        # Verify span attributes
        assert span.get_attribute("agent.name") == "Custom Finance Specialist"
        assert span.get_attribute("request.action") == "analyze_market"
```

## Deployment Best Practices

### Environment Configuration

```bash
# .env file for V2.0 features
# API Keys
GEMINI_API_KEY=your_key_here

# Observability
ENABLE_OBSERVABILITY=true
OTEL_SERVICE_NAME=my-agent-system
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
TRACING_ENABLED=true
METRICS_ENABLED=true
JSON_LOGS=true

# Quality Framework
DEFAULT_QUALITY_DOMAIN=ANALYSIS
MIN_QUALITY_SCORE=0.85

# Performance
CONNECTION_POOL_SIZE=20
ENABLE_HTTP2=true
REQUEST_TIMEOUT=30

# A2A Protocol
A2A_BASE_PORT=10000
A2A_REGISTRY_PORT=10099
```

### Production Deployment

1. **Start Observability Stack**
```bash
docker-compose -f docker-compose.observability.yml up -d
```

2. **Configure Quality Thresholds**
```yaml
# configs/quality.yaml
domains:
  analysis:
    thresholds:
      completeness: 0.95
      accuracy: 0.98
      relevance: 0.90
  creative:
    thresholds:
      originality: 0.85
      coherence: 0.90
```

3. **Enable All V2.0 Features**
```python
orchestrator = EnhancedMasterOrchestratorTemplate(
    domain_name="Production",
    enable_phase_7_streaming=True,
    enable_observability=True,
    enable_quality_validation=True,
    enable_connection_pooling=True,
    quality_thresholds=production_thresholds
)
```

## Common Patterns and Examples

### Pattern 1: Research System
```python
# See examples/research_system.py
research_orchestrator = create_research_system(
    specialists=["researcher", "fact_checker", "summarizer"],
    quality_domain=QualityDomain.ANALYTICAL
)
```

### Pattern 2: Customer Service
```python
# See examples/customer_service.py
service_orchestrator = create_service_system(
    specialists=["classifier", "resolver", "escalation"],
    quality_domain=QualityDomain.COMMUNICATION
)
```

### Pattern 3: Code Generation
```python
# See examples/code_generation.py
code_orchestrator = create_coding_system(
    specialists=["architect", "developer", "reviewer"],
    quality_domain=QualityDomain.CODING
)
```

## Troubleshooting

### Common Issues

1. **Quality Validation Failures**
   - Check domain configuration matches use case
   - Adjust thresholds based on requirements
   - Review agent instructions for clarity

2. **Performance Issues**
   - Enable connection pooling
   - Use parallel workflows for independent tasks
   - Check trace data for bottlenecks

3. **Observability Not Working**
   - Verify OTEL endpoint is accessible
   - Check environment variables are set
   - Ensure observability is enabled in agent config

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable trace details
agent = CustomAgent(debug_mode=True, trace_details=True)

# Check quality validation details
quality.set_debug_mode(True)
```

## Next Steps

1. Review the [Framework Components Guide](./FRAMEWORK_COMPONENTS_AND_ORCHESTRATION_GUIDE.md) for detailed component documentation
2. Follow the [Multi-Agent Workflow Guide](./MULTI_AGENT_WORKFLOW_GUIDE.md) for system creation patterns
3. Explore examples in the `examples/` directory
4. Set up monitoring dashboards using provided Grafana templates
5. Join the community for support and best practices

## Conclusion

The A2A-MCP Framework V2.0 provides everything needed to build production-grade multi-agent systems with enterprise features. Start simple with templates and progressively add sophistication as your requirements grow.