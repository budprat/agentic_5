# Google ADK Agent Examples

This directory contains comprehensive examples of integrating Google ADK (Agent Development Kit) with the A2A-MCP framework.

## Overview

The examples demonstrate how to build production-ready multi-agent systems using Google ADK's powerful agent patterns within A2A's 3-tier architecture.

## Examples Structure

### Tier 1: Orchestrator Agents
- **ContentCreationOrchestrator** (`tier1_sequential_orchestrator.py`): Sequential workflow orchestration with state management
- **HybridOrchestrationPattern** (`advanced_orchestration_patterns.py`): Combines Sequential, Parallel, and Loop patterns
- **DynamicRoutingOrchestrator**: Routes tasks based on input characteristics
- **AdaptiveWorkflowOrchestrator**: Modifies execution path based on intermediate results

### Tier 2: Domain Specialists
- **FinancialDomainSpecialist** (`tier2_domain_specialist.py`): Financial analysis with structured outputs
- **TechnicalDomainSpecialist**: Code and architecture review specialist
- **HealthcareDomainSpecialist**: Healthcare assessment specialist (demo)
- **MultiDomainCoordinator**: Coordinates multiple domain specialists

### Tier 3: Service Agents
- **DataProcessingServiceAgent** (`tier3_service_agent.py`): Data transformation and validation
- **APIIntegrationServiceAgent**: External API integration
- **FileOperationsServiceAgent**: File I/O operations
- **ComputationServiceAgent**: Complex calculations using code execution

### Complete System Example
- **InvestmentAnalysisSystem** (`complete_system_example.py`): Full multi-tier system for investment analysis

## Key Patterns Demonstrated

### 1. ADK Agent Types
- **Agent**: Basic agent with tools and instructions
- **LlmAgent**: Agent with structured output using Pydantic schemas
- **SequentialAgent**: Execute sub-agents in sequence
- **ParallelAgent**: Execute sub-agents concurrently
- **LoopAgent**: Iterative refinement with quality checks

### 2. Tool Integration
- MCP tools via `MCPToolset`
- Built-in tools (grounding, code_execution)
- Custom tools for domain-specific operations
- AgentTool wrapper for sub-agent integration

### 3. A2A Framework Integration
- Inherit from `StandardizedAgentBase`
- Quality validation with `QualityFramework`
- Inter-agent communication via `A2AProtocolClient`
- Consistent error handling and logging

### 4. Advanced Workflows
- Hybrid orchestration (Sequential + Parallel + Loop)
- Dynamic routing based on input analysis
- Adaptive workflows that modify execution
- State management across agent stages

## Usage Examples

### Basic Sequential Orchestrator
```python
from a2a_mcp.agents.adk_examples import ContentCreationOrchestrator

# Create orchestrator
orchestrator = ContentCreationOrchestrator()
await orchestrator.init_agent()

# Execute workflow
result = await orchestrator.execute_workflow({
    'topic': 'Multi-Agent Systems',
    'content_type': 'blog_post',
    'target_audience': 'developers'
})
```

### Domain Specialist with Structured Output
```python
from a2a_mcp.agents.adk_examples import FinancialDomainSpecialist

# Create specialist
specialist = FinancialDomainSpecialist()
await specialist.init_agent()

# Analyze market data
market_data = {
    'indices': {'SP500': 4500, 'NASDAQ': 14200},
    'volatility': 'moderate',
    'economic_indicators': {'inflation': 3.2}
}
analysis = await specialist.analyze_market(market_data)
```

### Service Agent with Tools
```python
from a2a_mcp.agents.adk_examples import DataProcessingServiceAgent

# Create service agent
service = DataProcessingServiceAgent()
await service.init_agent()

# Process data
result = await service.process_data({
    'type': 'transform',
    'data': json_data,
    'requirements': 'Convert JSON to CSV'
})
```

### Complete System
```python
from a2a_mcp.agents.adk_examples import InvestmentAnalysisSystem

# Initialize system
system = InvestmentAnalysisSystem()
await system.initialize()

# Analyze investment
result = await system.analyze_investment(
    ticker="AAPL",
    context={'risk_tolerance': 'moderate'}
)
```

## Best Practices

### 1. Agent Design
- Keep agents focused on single responsibilities
- Use appropriate models for each tier (see GEMINI_MODELS.md)
- Implement comprehensive error handling
- Add callbacks for monitoring and debugging

### 2. Tool Usage
- Remember: Only ONE built-in tool per agent
- Combine MCP tools with custom tools as needed
- Use code_execution for computations
- Use grounding for real-time data

### 3. Orchestration
- Use SequentialAgent for ordered workflows
- Use ParallelAgent for independent tasks
- Use LoopAgent for iterative refinement
- Combine patterns for complex workflows

### 4. Quality Assurance
- Enable quality validation for critical agents
- Use structured outputs (LlmAgent) for data consistency
- Implement callbacks for stage validation
- Add comprehensive logging

## Integration with A2A Framework

All examples follow A2A framework patterns:

1. **StandardizedAgentBase**: Provides consistent foundation
2. **Quality Framework**: Validates responses
3. **A2A Protocol**: Enables inter-agent communication
4. **MCP Integration**: Extends agent capabilities
5. **Observability**: Built-in metrics and logging

## Testing

Each example includes test scenarios. Run tests with:

```bash
pytest tests/agents/test_adk_examples.py
```

## Deployment

See the main implementation plan (`docs/GOOGLE_ADK_IMPLEMENTATION_PLAN.md`) for deployment guidelines using Docker and Kubernetes.

## Next Steps

1. Choose appropriate patterns for your use case
2. Extend examples with domain-specific logic
3. Add custom tools as needed
4. Implement proper error handling
5. Deploy using A2A framework infrastructure

For questions or issues, refer to the framework documentation or contact the development team.