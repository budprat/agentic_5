# Hybrid Framework Implementation Guide: A2A-MCP + Google ADK

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Core Design Principles](#core-design-principles)
4. [Step-by-Step Implementation Guide](#step-by-step-implementation-guide)
5. [Component Integration Patterns](#component-integration-patterns)
6. [Code Templates](#code-templates)
7. [MCP Integration Strategies](#mcp-integration-strategies)
8. [Best Practices](#best-practices)
9. [Common Patterns and Anti-Patterns](#common-patterns-and-anti-patterns)
10. [Testing and Validation](#testing-and-validation)
11. [Deployment Considerations](#deployment-considerations)
12. [Example: Building a New Multi-Agent System](#example-building-a-new-multi-agent-system)

---

## Executive Summary

The Hybrid Framework combines **A2A-MCP Framework V2.0** with **Google ADK (Agent Development Kit)** to create production-ready multi-agent systems with enterprise-grade features. This guide provides a template for building future multi-agent systems using this proven architecture.

### Key Benefits
- **Best of Both Worlds**: Google ADK's powerful LLM agents + A2A-MCP's enterprise features
- **Production Ready**: Built-in quality validation, observability, and error handling
- **Scalable**: Connection pooling, parallel execution, and distributed architecture
- **Maintainable**: Clear separation of concerns and standardized patterns

### When to Use This Framework
- Building complex multi-agent systems requiring coordination
- Need enterprise features (observability, quality validation, metrics)
- Require inter-agent communication and orchestration
- Want to leverage MCP tools and external services
- Need production-grade reliability and monitoring

---

## Architecture Overview

### Visual Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Hybrid Multi-Agent System                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              A2A-MCP Enhanced Orchestrator               │    │
│  │                                                           │    │
│  │  Inherits: StandardizedAgentBase                        │    │
│  │  ┌─────────────────────────────────────────────────┐   │    │
│  │  │  A2A-MCP Features:                              │   │    │
│  │  │  • Quality Framework (domain-specific)          │   │    │
│  │  │  • Observability (OpenTelemetry)               │   │    │
│  │  │  • A2A Protocol (inter-agent communication)    │   │    │
│  │  │  • Connection Pool (resilient networking)      │   │    │
│  │  │  • Metrics Collection (performance tracking)   │   │    │
│  │  │  • Response Formatting (standardized output)   │   │    │
│  │  └─────────────────────────────────────────────────┘   │    │
│  │                                                           │    │
│  │  Contains: self.adk_agent = orchestrator_agent          │    │
│  │  ┌─────────────────────────────────────────────────┐   │    │
│  │  │  Google ADK Features:                           │   │    │
│  │  │  • LlmAgent (Gemini/GPT-4 models)              │   │    │
│  │  │  • MCPToolset (external tool integration)      │   │    │
│  │  │  • Runner (execution management)               │   │    │
│  │  │  • Sessions (state management)                 │   │    │
│  │  │  • Callbacks (progress tracking)               │   │    │
│  │  └─────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                               │                                   │
│                               │ Coordinates                       │
│                               ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Specialist Agents                      │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │    │
│  │  │   Agent 1   │  │   Agent 2   │  │   Agent 3   │     │    │
│  │  │ Port: 14001 │  │ Port: 14002 │  │ Port: 14003 │     │    │
│  │  │             │  │             │  │             │     │    │
│  │  │ A2A + ADK   │  │ A2A + ADK   │  │ A2A + ADK   │     │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Component Hierarchy

1. **Orchestrator Layer**
   - Inherits from `StandardizedAgentBase`
   - Wraps Google ADK `LlmAgent`
   - Manages specialist agents
   - Handles quality validation
   - Provides observability

2. **Specialist Agent Layer**
   - Task-specific agents
   - Can inherit from `StandardizedAgentBase`
   - Communicate via A2A Protocol
   - Independent execution
   - Domain expertise

3. **Infrastructure Layer**
   - Connection pooling
   - Metrics collection
   - Response formatting
   - Error handling
   - MCP tool integration

---

## Core Design Principles

### 1. Composition Over Inheritance
```python
# Good: Wrap ADK agent, don't extend it
class A2AEnhancedOrchestrator(StandardizedAgentBase):
    def __init__(self):
        self.adk_agent = google_adk_orchestrator  # Composition

# Bad: Direct inheritance from ADK
class MyOrchestrator(LlmAgent):  # Avoid this
    pass
```

### 2. Separation of Concerns
- **A2A-MCP Layer**: Quality, observability, inter-agent communication
- **Google ADK Layer**: LLM interaction, tool execution, state management
- **Business Logic**: Domain-specific functionality

### 3. Async-First Design
```python
# All major operations should be async
async def coordinate_agents(self, task: str) -> Dict[str, Any]:
    # Parallel execution when possible
    results = await asyncio.gather(
        self.agent1.execute(task),
        self.agent2.execute(task),
        self.agent3.execute(task)
    )
```

### 4. Fail-Safe Defaults
- Quality validation enabled by default
- Automatic retries with backoff
- Graceful degradation
- Comprehensive error handling

---

## Step-by-Step Implementation Guide

### Step 1: Define Your Multi-Agent System Architecture

```python
# 1. Identify your agents and their relationships
"""
System: Customer Support Assistant
Orchestrator: support_orchestrator
Specialists:
  - ticket_analyzer_agent (analyzes support tickets)
  - knowledge_base_agent (searches documentation)
  - solution_generator_agent (creates responses)
  - escalation_agent (handles complex cases)
"""

# 2. Define quality domains
from a2a_mcp.common.quality_framework import QualityDomain

QUALITY_DOMAINS = {
    "support": QualityDomain.GENERAL,  # Or create custom domain
    "technical": QualityDomain.ACADEMIC,  # For technical accuracy
}

# 3. Plan communication patterns
"""
Parallel: ticket_analyzer + knowledge_base
Sequential: analyzer -> solution_generator
Conditional: escalation if confidence < 0.7
"""
```

### Step 2: Create Google ADK Base Agents

```python
# agents/orchestrator/agent.py
import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

# Create orchestrator agent
support_orchestrator = LlmAgent(
    name="support_orchestrator",
    model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
    instruction="""You are a customer support orchestrator that:
    - Analyzes support tickets
    - Coordinates specialist agents
    - Ensures high-quality responses
    - Handles escalations when needed
    """,
    tools=[
        # Add MCP tools as needed
        MCPToolset(
            connection_params=StdioServerParameters(
                command="npx",
                args=["-y", "@firecrawl/mcp-server"],
                env={"FIRECRAWL_API_KEY": os.getenv("FIRECRAWL_API_KEY")},
            )
        ),
    ],
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    description="Orchestrates customer support workflow"
)
```

### Step 3: Create A2A-Enhanced Orchestrator

```python
# agents/orchestrator/a2a_enhanced_orchestrator.py
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.common.quality_framework import QualityDomain
from a2a_mcp.common.metrics_collector import MetricsCollector
from a2a_mcp.common.observability import trace_async
from a2a_mcp.common.response_formatter import ResponseFormatter
from a2a_mcp.common.a2a_protocol import A2AProtocolClient
from a2a_mcp.common.a2a_connection_pool import A2AConnectionPool

from .agent import support_orchestrator

class A2ASupportOrchestrator(StandardizedAgentBase):
    """Enhanced support orchestrator with A2A-MCP features."""
    
    def __init__(self):
        # Initialize with A2A features
        super().__init__(
            agent_name="A2A Support Orchestrator",
            description="Enhanced customer support orchestration",
            instructions="""You orchestrate customer support with:
            - Quality validation for all responses
            - Distributed agent coordination
            - Performance tracking
            - Escalation management
            """,
            quality_config={
                "domain": QualityDomain.GENERAL,
                "enabled": True,
                "thresholds": {
                    "accuracy": {"min_value": 0.85, "weight": 1.2},
                    "completeness": {"min_value": 0.9, "weight": 1.1},
                    "relevance": {"min_value": 0.8, "weight": 1.0},
                    "clarity": {"min_value": 0.85, "weight": 0.9}
                }
            },
            mcp_tools_enabled=True,
            a2a_enabled=True
        )
        
        # Wrap Google ADK agent
        self.adk_agent = support_orchestrator
        
        # Initialize metrics
        self.metrics = MetricsCollector(
            namespace="support_orchestrator",
            subsystem="ticket_processing"
        )
        
        # Agent configuration
        self.specialist_agents = {
            "ticket_analyzer": {"port": 14001, "timeout": 30},
            "knowledge_base": {"port": 14002, "timeout": 45},
            "solution_generator": {"port": 14003, "timeout": 60},
            "escalation": {"port": 14004, "timeout": 30}
        }
        
        # Initialize connection pool
        self._init_task = asyncio.create_task(self._initialize_connections())
    
    async def _initialize_connections(self):
        """Initialize A2A connection pool."""
        self.connection_pool = await A2AConnectionPool.create({
            "max_connections": 20,
            "health_check_interval": 30,
            "connection_timeout": 30,
            "retry_attempts": 3
        })
        
        self.a2a_client = A2AProtocolClient(
            agent_id=self.agent_id,
            connection_pool=self.connection_pool
        )
    
    @trace_async("process_support_ticket")
    async def process_ticket(
        self, 
        ticket: Dict[str, Any],
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """
        Process a support ticket through the multi-agent system.
        
        Args:
            ticket: Support ticket data
            priority: Ticket priority (low, normal, high, urgent)
            
        Returns:
            Processing result with solution and metadata
        """
        start_time = datetime.now()
        
        # Step 1: Analyze ticket (parallel with knowledge search)
        analysis_task = self._analyze_ticket(ticket)
        knowledge_task = self._search_knowledge(ticket)
        
        analysis, knowledge = await asyncio.gather(
            analysis_task,
            knowledge_task,
            return_exceptions=True
        )
        
        # Handle errors
        if isinstance(analysis, Exception):
            self.logger.error(f"Ticket analysis failed: {analysis}")
            analysis = {"error": str(analysis)}
        
        if isinstance(knowledge, Exception):
            self.logger.error(f"Knowledge search failed: {knowledge}")
            knowledge = {"articles": []}
        
        # Step 2: Generate solution
        solution = await self._generate_solution(
            ticket=ticket,
            analysis=analysis,
            knowledge=knowledge
        )
        
        # Step 3: Validate quality
        quality_result = await self._validate_solution_quality(solution)
        
        # Step 4: Check if escalation needed
        if self._needs_escalation(quality_result, priority):
            escalation_result = await self._escalate_ticket(
                ticket=ticket,
                solution=solution,
                reason=quality_result.get("issues", [])
            )
            solution["escalated"] = True
            solution["escalation"] = escalation_result
        
        # Record metrics
        duration = (datetime.now() - start_time).total_seconds()
        self.metrics.record_histogram(
            "ticket_processing_duration",
            duration,
            labels={"priority": priority}
        )
        
        # Format response
        return ResponseFormatter.format_response(
            content={
                "ticket_id": ticket.get("id"),
                "solution": solution,
                "analysis": analysis,
                "knowledge_used": len(knowledge.get("articles", [])),
                "quality_validation": quality_result,
                "processing_time": duration
            },
            metadata={
                "orchestrator": self.agent_name,
                "priority": priority,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    async def _analyze_ticket(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze ticket using specialist agent."""
        return await self.a2a_client.send_request(
            agent_port=self.specialist_agents["ticket_analyzer"]["port"],
            action="analyze",
            data=ticket,
            timeout=self.specialist_agents["ticket_analyzer"]["timeout"]
        )
    
    async def _search_knowledge(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        """Search knowledge base for relevant articles."""
        return await self.a2a_client.send_request(
            agent_port=self.specialist_agents["knowledge_base"]["port"],
            action="search",
            data={
                "query": ticket.get("subject", "") + " " + ticket.get("description", ""),
                "limit": 5
            },
            timeout=self.specialist_agents["knowledge_base"]["timeout"]
        )
    
    async def _generate_solution(
        self,
        ticket: Dict[str, Any],
        analysis: Dict[str, Any],
        knowledge: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate solution using all available information."""
        return await self.a2a_client.send_request(
            agent_port=self.specialist_agents["solution_generator"]["port"],
            action="generate",
            data={
                "ticket": ticket,
                "analysis": analysis,
                "knowledge_articles": knowledge.get("articles", [])
            },
            timeout=self.specialist_agents["solution_generator"]["timeout"]
        )
    
    async def _validate_solution_quality(self, solution: Dict[str, Any]) -> Dict[str, Any]:
        """Validate solution quality."""
        quality_metrics = {
            "accuracy": self._calculate_accuracy(solution),
            "completeness": self._calculate_completeness(solution),
            "relevance": self._calculate_relevance(solution),
            "clarity": self._calculate_clarity(solution)
        }
        
        return await self.quality_framework.validate_response(
            quality_metrics,
            "support_solution"
        )
    
    def _needs_escalation(self, quality_result: Dict[str, Any], priority: str) -> bool:
        """Determine if ticket needs escalation."""
        # Escalate if quality is low or priority is high
        quality_score = quality_result.get("overall_score", 0)
        quality_approved = quality_result.get("quality_approved", False)
        
        if priority in ["high", "urgent"] and quality_score < 0.9:
            return True
        
        if not quality_approved:
            return True
        
        return False
    
    async def _escalate_ticket(
        self,
        ticket: Dict[str, Any],
        solution: Dict[str, Any],
        reason: List[str]
    ) -> Dict[str, Any]:
        """Escalate ticket to senior support."""
        return await self.a2a_client.send_request(
            agent_port=self.specialist_agents["escalation"]["port"],
            action="escalate",
            data={
                "ticket": ticket,
                "attempted_solution": solution,
                "escalation_reason": reason
            },
            timeout=self.specialist_agents["escalation"]["timeout"]
        )
    
    # Quality calculation methods (simplified examples)
    def _calculate_accuracy(self, solution: Dict[str, Any]) -> float:
        """Calculate solution accuracy score."""
        # Implement domain-specific accuracy calculation
        return 0.85  # Placeholder
    
    def _calculate_completeness(self, solution: Dict[str, Any]) -> float:
        """Calculate solution completeness score."""
        # Check if all required elements are present
        required_elements = ["resolution_steps", "explanation", "references"]
        present = sum(1 for elem in required_elements if elem in solution)
        return present / len(required_elements)
    
    def _calculate_relevance(self, solution: Dict[str, Any]) -> float:
        """Calculate solution relevance score."""
        # Implement relevance scoring
        return 0.9  # Placeholder
    
    def _calculate_clarity(self, solution: Dict[str, Any]) -> float:
        """Calculate solution clarity score."""
        # Could use readability metrics
        return 0.85  # Placeholder
```

### Step 4: Create Specialist Agents

```python
# agents/ticket_analyzer/a2a_enhanced_agent.py
class A2ATicketAnalyzerAgent(StandardizedAgentBase):
    """Analyzes support tickets for intent, urgency, and category."""
    
    def __init__(self):
        super().__init__(
            agent_name="A2A Ticket Analyzer",
            description="Analyzes support tickets",
            quality_config={
                "domain": QualityDomain.GENERAL,
                "thresholds": {
                    "classification_accuracy": {"min_value": 0.9, "weight": 1.3},
                    "intent_detection": {"min_value": 0.85, "weight": 1.2}
                }
            }
        )
        
        # Wrap ADK agent
        self.adk_agent = ticket_analyzer_agent
    
    @trace_async("analyze_ticket")
    async def analyze(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze support ticket."""
        # Use ADK agent for analysis
        result = await self._execute_adk_agent(ticket)
        
        # Extract structured information
        analysis = {
            "category": self._extract_category(result),
            "intent": self._extract_intent(result),
            "urgency": self._calculate_urgency(result),
            "sentiment": self._analyze_sentiment(result),
            "key_issues": self._extract_key_issues(result)
        }
        
        # Validate quality
        quality = await self.quality_framework.validate_response(
            {
                "classification_accuracy": analysis.get("confidence", 0.8),
                "intent_detection": 0.9  # From intent detection confidence
            },
            "ticket_analysis"
        )
        
        return ResponseFormatter.format_response(
            content=analysis,
            metadata={"quality": quality}
        )
```

### Step 5: Create Main Entry Point

```python
# main.py
import asyncio
import os
from typing import Dict, Any
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from agents.orchestrator.a2a_enhanced_orchestrator import A2ASupportOrchestrator

async def main():
    """Main entry point for the support system."""
    # Initialize orchestrator
    orchestrator = A2ASupportOrchestrator()
    
    # Wait for connections to initialize
    await orchestrator._init_task
    
    # Example: Process a support ticket
    ticket = {
        "id": "TICKET-12345",
        "subject": "Cannot access my account",
        "description": "I'm getting an error when trying to log in...",
        "customer_id": "CUST-789",
        "created_at": "2024-01-15T10:30:00Z"
    }
    
    # Process ticket
    result = await orchestrator.process_ticket(
        ticket=ticket,
        priority="high"
    )
    
    print("Support Ticket Processing Result:")
    print(f"Solution: {result['content']['solution']}")
    print(f"Quality Score: {result['content']['quality_validation']['overall_score']}")
    print(f"Processing Time: {result['content']['processing_time']}s")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Component Integration Patterns

### Pattern 1: Quality-First Agent Design

```python
class QualityFirstAgent(StandardizedAgentBase):
    """Agent that prioritizes quality validation."""
    
    def __init__(self, domain: QualityDomain, thresholds: Dict[str, Any]):
        super().__init__(
            agent_name="Quality-First Agent",
            quality_config={
                "domain": domain,
                "enabled": True,
                "thresholds": thresholds,
                "fail_fast": True  # Stop if quality check fails
            }
        )
    
    async def execute_with_validation(self, task: Any) -> Dict[str, Any]:
        """Execute task with mandatory quality validation."""
        result = await self._perform_task(task)
        
        # Calculate quality metrics
        metrics = self._calculate_quality_metrics(result)
        
        # Validate
        validation = await self.quality_framework.validate_response(
            metrics, 
            "task_execution"
        )
        
        if not validation["quality_approved"]:
            # Retry with improvements
            result = await self._improve_and_retry(result, validation["issues"])
        
        return result
```

### Pattern 2: Multi-Source Aggregation

```python
class MultiSourceAggregator(StandardizedAgentBase):
    """Agent that aggregates data from multiple sources."""
    
    async def aggregate_from_sources(self, query: str) -> Dict[str, Any]:
        """Aggregate data from multiple sources in parallel."""
        # Define sources
        sources = [
            self._search_source_a(query),
            self._search_source_b(query),
            self._search_source_c(query)
        ]
        
        # Parallel execution
        results = await asyncio.gather(*sources, return_exceptions=True)
        
        # Handle errors gracefully
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.warning(f"Source {i} failed: {result}")
            else:
                valid_results.append(result)
        
        # Deduplicate and rank
        aggregated = self._deduplicate_results(valid_results)
        ranked = self._rank_by_quality(aggregated)
        
        return ranked
```

### Pattern 3: Streaming with Progress

```python
class StreamingAgent(StandardizedAgentBase):
    """Agent that streams results with progress updates."""
    
    async def stream_with_progress(self, task: Any):
        """Stream results with progress tracking."""
        total_steps = 5
        
        async for step in self._execute_steps(task):
            progress = (step["number"] / total_steps) * 100
            
            yield {
                "type": "progress",
                "progress": progress,
                "message": step["message"],
                "partial_result": step.get("result")
            }
        
        # Final result
        yield {
            "type": "completion",
            "result": await self._finalize_results(),
            "metadata": {
                "total_steps": total_steps,
                "execution_time": self._get_execution_time()
            }
        }
```

### Pattern 4: Circuit Breaker for Resilience

```python
class ResilientAgent(StandardizedAgentBase):
    """Agent with circuit breaker pattern."""
    
    def __init__(self):
        super().__init__(agent_name="Resilient Agent")
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60,
            expected_exception=AgentException
        )
    
    @circuit_breaker
    async def execute_with_circuit_breaker(self, task: Any) -> Dict[str, Any]:
        """Execute with circuit breaker protection."""
        try:
            return await self._execute_task(task)
        except Exception as e:
            # Record failure
            self.metrics.inc_counter("task_failures", labels={"error": str(e)})
            raise
```

---

## Code Templates

### Template 1: Basic A2A-Enhanced Agent

```python
# template_basic_agent.py
from typing import Dict, Any, Optional, List
from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.common.quality_framework import QualityDomain
from a2a_mcp.common.observability import trace_async
from a2a_mcp.common.response_formatter import ResponseFormatter

class A2AEnhancedAgent(StandardizedAgentBase):
    """
    Template for creating an A2A-enhanced agent.
    
    Replace:
    - AGENT_NAME: Your agent's name
    - DOMAIN: Quality domain (ACADEMIC, MEDICAL, LEGAL, GENERAL)
    - QUALITY_METRICS: Domain-specific quality metrics
    """
    
    def __init__(self):
        super().__init__(
            agent_name="AGENT_NAME",
            description="Agent description",
            instructions="Detailed agent instructions",
            quality_config={
                "domain": QualityDomain.DOMAIN,
                "enabled": True,
                "thresholds": {
                    "metric1": {"min_value": 0.8, "weight": 1.0},
                    "metric2": {"min_value": 0.85, "weight": 1.1},
                    # Add more metrics as needed
                }
            },
            mcp_tools_enabled=True,  # Enable if using MCP tools
            a2a_enabled=True  # Enable for inter-agent communication
        )
        
        # Wrap Google ADK agent if needed
        # self.adk_agent = your_adk_agent
        
        # Initialize any additional components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize agent-specific components."""
        # Add initialization logic
        pass
    
    @trace_async("main_operation")
    async def perform_task(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main task execution method.
        
        Args:
            input_data: Task input data
            
        Returns:
            Formatted response with results
        """
        try:
            # Step 1: Validate input
            self._validate_input(input_data)
            
            # Step 2: Execute main logic
            result = await self._execute_core_logic(input_data)
            
            # Step 3: Calculate quality metrics
            quality_metrics = self._calculate_quality_metrics(result)
            
            # Step 4: Validate quality
            quality_validation = await self.quality_framework.validate_response(
                quality_metrics,
                "task_name"
            )
            
            # Step 5: Format and return response
            return ResponseFormatter.format_response(
                content=result,
                metadata={
                    "quality": quality_validation,
                    "agent": self.agent_name
                }
            )
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            return ResponseFormatter.format_error(
                error=str(e),
                context={"input": input_data}
            )
    
    def _validate_input(self, input_data: Dict[str, Any]):
        """Validate input data."""
        # Add validation logic
        required_fields = ["field1", "field2"]
        for field in required_fields:
            if field not in input_data:
                raise ValueError(f"Missing required field: {field}")
    
    async def _execute_core_logic(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the main agent logic."""
        # Implement your core functionality
        return {"result": "processed"}
    
    def _calculate_quality_metrics(self, result: Dict[str, Any]) -> Dict[str, float]:
        """Calculate quality metrics for the result."""
        return {
            "metric1": 0.85,
            "metric2": 0.90
        }
```

### Template 2: Orchestrator with Specialist Coordination

```python
# template_orchestrator.py
class A2AOrchestrator(StandardizedAgentBase):
    """Template for orchestrator that coordinates multiple agents."""
    
    def __init__(self):
        super().__init__(
            agent_name="Orchestrator",
            quality_config={
                "domain": QualityDomain.GENERAL,
                "thresholds": {
                    "coordination_efficiency": {"min_value": 0.8, "weight": 1.0},
                    "result_quality": {"min_value": 0.85, "weight": 1.2}
                }
            }
        )
        
        # Define specialist agents
        self.specialists = {
            "specialist_1": {"port": 14001, "timeout": 30},
            "specialist_2": {"port": 14002, "timeout": 45},
            "specialist_3": {"port": 14003, "timeout": 60}
        }
        
        # Initialize connection pool
        self._init_task = asyncio.create_task(self._initialize_connections())
    
    async def orchestrate_workflow(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate multi-agent workflow."""
        # Pattern 1: Parallel execution
        parallel_results = await self._execute_parallel_tasks(task)
        
        # Pattern 2: Sequential execution with context passing
        sequential_result = await self._execute_sequential_tasks(
            task, 
            parallel_results
        )
        
        # Pattern 3: Conditional execution
        if self._needs_additional_processing(sequential_result):
            final_result = await self._execute_conditional_task(sequential_result)
        else:
            final_result = sequential_result
        
        return final_result
    
    async def _execute_parallel_tasks(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute tasks in parallel."""
        parallel_tasks = [
            self.a2a_client.send_request(
                agent_port=self.specialists["specialist_1"]["port"],
                action="analyze",
                data=task
            ),
            self.a2a_client.send_request(
                agent_port=self.specialists["specialist_2"]["port"],
                action="process",
                data=task
            )
        ]
        
        return await asyncio.gather(*parallel_tasks, return_exceptions=True)
    
    async def _execute_sequential_tasks(
        self, 
        task: Dict[str, Any], 
        context: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute tasks sequentially with context."""
        # First task uses parallel results as context
        result_1 = await self.a2a_client.send_request(
            agent_port=self.specialists["specialist_3"]["port"],
            action="synthesize",
            data={
                "original_task": task,
                "context": context
            }
        )
        
        # Second task builds on first
        result_2 = await self.a2a_client.send_request(
            agent_port=self.specialists["specialist_1"]["port"],
            action="refine",
            data=result_1
        )
        
        return result_2
```

### Template 3: Agent with MCP Tools

```python
# template_mcp_agent.py
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

# First create the Google ADK agent with MCP tools
mcp_agent = LlmAgent(
    name="mcp_enhanced_agent",
    model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
    instruction="Agent with MCP tool access",
    tools=[
        # Firecrawl for web scraping
        MCPToolset(
            connection_params=StdioServerParameters(
                command="npx",
                args=["-y", "@firecrawl/mcp-server"],
                env={"FIRECRAWL_API_KEY": os.getenv("FIRECRAWL_API_KEY")},
            )
        ),
        # Add more MCP tools as needed
    ]
)

# Then wrap with A2A enhancements
class A2AMCPAgent(StandardizedAgentBase):
    """Agent with MCP tool integration."""
    
    def __init__(self):
        super().__init__(
            agent_name="A2A MCP Agent",
            mcp_tools_enabled=True
        )
        self.adk_agent = mcp_agent
    
    async def scrape_and_analyze(self, url: str) -> Dict[str, Any]:
        """Scrape URL and analyze content."""
        # Use ADK agent with MCP tools
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        
        runner = Runner(
            agent=self.adk_agent,
            app_name="MCP Scraper",
            session_service=InMemorySessionService()
        )
        
        # Execute with MCP tools
        results = []
        async for event in runner.run_async(
            user_id="scraper",
            session_id=f"scrape_{datetime.now().timestamp()}",
            new_message={
                "role": "user", 
                "content": f"Scrape and analyze: {url}"
            }
        ):
            if event.is_final_response():
                results.append(event.content)
        
        # Process and validate results
        return self._process_scraped_content(results)
```

---

## MCP Integration Strategies

### Available MCP Servers

1. **Firecrawl** - Web scraping and content extraction
2. **Brightdata** - Advanced web data collection
3. **Context7** - Documentation and context retrieval
4. **Scholarly** - Academic paper search
5. **Puppeteer** - Browser automation
6. **Playwright** - Cross-browser automation

### Integration Patterns

#### Pattern 1: Direct MCP Tool Usage

```python
# In Google ADK agent definition
tools=[
    MCPToolset(
        connection_params=StdioServerParameters(
            command="npx",
            args=["-y", "@firecrawl/mcp-server"],
            env={"FIRECRAWL_API_KEY": os.getenv("FIRECRAWL_API_KEY")},
        )
    ),
    MCPToolset(
        connection_params=StdioServerParameters(
            command="npx",
            args=["-y", "@brightdata/mcp-server"],
            env={"BRIGHTDATA_API_KEY": os.getenv("BRIGHTDATA_API_KEY")},
        )
    )
]
```

#### Pattern 2: Conditional MCP Tool Selection

```python
async def select_appropriate_mcp_tool(self, task_type: str) -> str:
    """Select the best MCP tool for the task."""
    tool_mapping = {
        "web_scraping": "firecrawl",
        "academic_search": "scholarly",
        "documentation": "context7",
        "browser_automation": "playwright",
        "data_collection": "brightdata"
    }
    
    return tool_mapping.get(task_type, "firecrawl")
```

#### Pattern 3: MCP Tool Fallback Chain

```python
async def scrape_with_fallback(self, url: str) -> Dict[str, Any]:
    """Try multiple MCP tools with fallback."""
    tools_priority = ["firecrawl", "brightdata", "playwright"]
    
    for tool in tools_priority:
        try:
            result = await self._scrape_with_tool(url, tool)
            if result and result.get("content"):
                return result
        except Exception as e:
            self.logger.warning(f"{tool} failed: {e}")
            continue
    
    raise Exception("All scraping tools failed")
```

---

## Best Practices

### 1. Agent Design

✅ **DO:**
- Keep agents focused on a single responsibility
- Use composition over inheritance
- Implement proper error handling
- Add comprehensive logging
- Use async/await consistently

❌ **DON'T:**
- Create monolithic agents that do everything
- Ignore quality validation
- Use synchronous operations in async contexts
- Hardcode configuration values
- Skip error handling

### 2. Quality Configuration

```python
# Good: Domain-specific quality metrics
quality_config={
    "domain": QualityDomain.ACADEMIC,
    "thresholds": {
        "citation_completeness": {"min_value": 0.85, "weight": 1.3},
        "methodology_rigor": {"min_value": 0.9, "weight": 1.2},
        "statistical_validity": {"min_value": 0.8, "weight": 1.1}
    }
}

# Bad: Generic metrics for specialized domain
quality_config={
    "domain": QualityDomain.ACADEMIC,
    "thresholds": {
        "quality": {"min_value": 0.7, "weight": 1.0}
    }
}
```

### 3. Connection Management

```python
# Good: Proper initialization and cleanup
class WellManagedAgent(StandardizedAgentBase):
    def __init__(self):
        super().__init__(agent_name="Well Managed")
        self._init_task = asyncio.create_task(self._initialize())
    
    async def _initialize(self):
        """Initialize connections."""
        self.connection_pool = await A2AConnectionPool.create({
            "max_connections": 10
        })
    
    async def cleanup(self):
        """Clean up resources."""
        if hasattr(self, 'connection_pool'):
            await self.connection_pool.close()

# Bad: No cleanup
class PoorlyManagedAgent(StandardizedAgentBase):
    def __init__(self):
        super().__init__(agent_name="Poorly Managed")
        # Creates connections but never cleans up
        self.connection_pool = A2AConnectionPool.create({})
```

### 4. Error Handling and Retries

```python
# Good: Comprehensive error handling with retries
async def execute_with_retry(self, task: Any, max_retries: int = 3) -> Dict[str, Any]:
    """Execute task with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            result = await self._execute_task(task)
            return result
        except TemporaryError as e:
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                self.logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s")
                await asyncio.sleep(wait_time)
            else:
                raise
        except PermanentError as e:
            # Don't retry permanent errors
            self.logger.error(f"Permanent error: {e}")
            raise
```

### 5. Metrics and Monitoring

```python
# Good: Comprehensive metrics
class MetricsAwareAgent(StandardizedAgentBase):
    def __init__(self):
        super().__init__(agent_name="Metrics Aware")
        self._setup_metrics()
    
    def _setup_metrics(self):
        """Set up agent-specific metrics."""
        self.task_counter = self.metrics.create_counter(
            'tasks_processed_total',
            'Total tasks processed',
            ['task_type', 'status']
        )
        
        self.task_duration = self.metrics.create_histogram(
            'task_duration_seconds',
            'Task processing duration',
            ['task_type'],
            buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
        )
        
        self.quality_gauge = self.metrics.create_gauge(
            'quality_score',
            'Current quality score',
            ['metric_type']
        )
```

---

## Common Patterns and Anti-Patterns

### Pattern: Response Extraction

```python
def extract_structured_content(self, response: str) -> Dict[str, Any]:
    """Extract structured content from LLM responses."""
    extracted = {
        "raw_response": response,
        "code_blocks": [],
        "json_blocks": [],
        "plain_text": response
    }
    
    # Pattern definitions
    patterns = {
        "code": r'```\n(.*?)\n```',
        "json": r'```json\s*(.*?)\s*```',
        "python": r'```python\s*(.*?)\s*```',
    }
    
    # Extract each pattern type
    for pattern_type, pattern in patterns.items():
        matches = re.findall(pattern, response, re.DOTALL)
        
        for match in matches:
            if pattern_type == "json":
                try:
                    parsed = json.loads(match)
                    extracted["json_blocks"].append(parsed)
                except json.JSONDecodeError:
                    extracted["code_blocks"].append({
                        "type": "json_invalid",
                        "content": match
                    })
            else:
                extracted["code_blocks"].append({
                    "type": pattern_type,
                    "content": match
                })
    
    return extracted
```

### Anti-Pattern: Blocking Operations

```python
# Bad: Blocking operation in async context
async def bad_async_method(self):
    # This blocks the event loop!
    time.sleep(5)  # ❌
    
    # This blocks with I/O
    with open('large_file.txt', 'r') as f:  # ❌
        data = f.read()

# Good: Non-blocking alternatives
async def good_async_method(self):
    # Non-blocking sleep
    await asyncio.sleep(5)  # ✅
    
    # Non-blocking file I/O
    async with aiofiles.open('large_file.txt', 'r') as f:  # ✅
        data = await f.read()
```

### Pattern: Graceful Degradation

```python
async def search_with_degradation(self, query: str) -> Dict[str, Any]:
    """Search with graceful degradation across sources."""
    results = {
        "primary": None,
        "secondary": None,
        "fallback": None,
        "source_used": None
    }
    
    # Try primary source
    try:
        results["primary"] = await self._search_primary(query)
        results["source_used"] = "primary"
        return results["primary"]
    except Exception as e:
        self.logger.warning(f"Primary search failed: {e}")
    
    # Try secondary source
    try:
        results["secondary"] = await self._search_secondary(query)
        results["source_used"] = "secondary"
        return results["secondary"]
    except Exception as e:
        self.logger.warning(f"Secondary search failed: {e}")
    
    # Use cached/fallback data
    results["fallback"] = await self._get_cached_results(query)
    results["source_used"] = "cache"
    
    return results["fallback"] or {"error": "All sources failed"}
```

---

## Testing and Validation

### Unit Testing Template

```python
# test_agent.py
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from agents.my_agent import MyA2AAgent

class TestMyA2AAgent:
    """Test suite for MyA2AAgent."""
    
    @pytest.fixture
    async def agent(self):
        """Create agent instance for testing."""
        agent = MyA2AAgent()
        # Wait for initialization
        await agent._init_task
        yield agent
        # Cleanup
        await agent.cleanup()
    
    @pytest.mark.asyncio
    async def test_quality_validation(self, agent):
        """Test quality validation logic."""
        # Mock quality framework
        agent.quality_framework.validate_response = AsyncMock(
            return_value={
                "quality_approved": True,
                "overall_score": 0.85
            }
        )
        
        # Execute task
        result = await agent.perform_task({"test": "data"})
        
        # Assertions
        assert result["status"] == "success"
        assert "quality" in result["metadata"]
        agent.quality_framework.validate_response.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling(self, agent):
        """Test error handling."""
        # Force an error
        agent._execute_core_logic = AsyncMock(
            side_effect=Exception("Test error")
        )
        
        # Should handle gracefully
        result = await agent.perform_task({"test": "data"})
        
        assert result["status"] == "error"
        assert "Test error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_parallel_execution(self, agent):
        """Test parallel task execution."""
        # Mock parallel tasks
        async def mock_task(delay):
            await asyncio.sleep(delay)
            return f"Result after {delay}s"
        
        # Execute in parallel
        start = asyncio.get_event_loop().time()
        results = await asyncio.gather(
            mock_task(0.1),
            mock_task(0.1),
            mock_task(0.1)
        )
        duration = asyncio.get_event_loop().time() - start
        
        # Should complete in ~0.1s, not 0.3s
        assert duration < 0.2
        assert len(results) == 3
```

### Integration Testing

```python
# test_integration.py
class TestMultiAgentIntegration:
    """Test multi-agent system integration."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_coordination(self):
        """Test orchestrator coordinating multiple agents."""
        # Start specialist agents
        agents = await start_test_agents([
            ("analyzer", 14001),
            ("processor", 14002),
            ("validator", 14003)
        ])
        
        # Create orchestrator
        orchestrator = TestOrchestrator()
        await orchestrator._init_task
        
        # Execute workflow
        result = await orchestrator.coordinate_workflow({
            "task": "integration_test",
            "data": {"test": True}
        })
        
        # Verify coordination
        assert result["status"] == "success"
        assert len(result["agent_results"]) == 3
        
        # Cleanup
        await stop_test_agents(agents)
        await orchestrator.cleanup()
```

### Performance Testing

```python
# test_performance.py
@pytest.mark.performance
async def test_agent_throughput():
    """Test agent throughput under load."""
    agent = HighPerformanceAgent()
    await agent._init_task
    
    # Generate test tasks
    tasks = [{"id": i, "data": f"test_{i}"} for i in range(100)]
    
    # Measure throughput
    start = time.time()
    results = await asyncio.gather(*[
        agent.process_task(task) for task in tasks
    ])
    duration = time.time() - start
    
    throughput = len(results) / duration
    
    # Assert minimum throughput
    assert throughput > 10  # At least 10 tasks/second
    assert all(r["status"] == "success" for r in results)
    
    await agent.cleanup()
```

---

## Deployment Considerations

### 1. Environment Configuration

```python
# config.py
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class AgentConfig:
    """Agent configuration."""
    # A2A-MCP settings
    a2a_enabled: bool = True
    connection_pool_size: int = 20
    health_check_interval: int = 30
    
    # Quality settings
    quality_domain: str = "GENERAL"
    quality_threshold: float = 0.7
    
    # Model settings
    llm_model: str = os.getenv("LLM_MODEL", "gemini-2.0-flash")
    temperature: float = 0.7
    
    # MCP settings
    mcp_tools_enabled: bool = True
    firecrawl_api_key: Optional[str] = os.getenv("FIRECRAWL_API_KEY")
    brightdata_api_key: Optional[str] = os.getenv("BRIGHTDATA_API_KEY")
    
    # Observability
    enable_tracing: bool = True
    trace_endpoint: str = os.getenv("TRACE_ENDPOINT", "http://localhost:4318")
    
    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Create config from environment variables."""
        return cls(
            a2a_enabled=os.getenv("A2A_ENABLED", "true").lower() == "true",
            connection_pool_size=int(os.getenv("CONNECTION_POOL_SIZE", "20")),
            quality_threshold=float(os.getenv("QUALITY_THRESHOLD", "0.7"))
        )
```

### 2. Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for MCP servers
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV A2A_ENABLED=true
ENV QUALITY_THRESHOLD=0.7

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')"

# Run
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 3. Kubernetes Deployment

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hybrid-agent-system
  labels:
    app: hybrid-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: hybrid-agent
  template:
    metadata:
      labels:
        app: hybrid-agent
    spec:
      containers:
      - name: orchestrator
        image: hybrid-agent:latest
        ports:
        - containerPort: 8080
        env:
        - name: AGENT_ROLE
          value: "orchestrator"
        - name: A2A_ENABLED
          value: "true"
        - name: CONNECTION_POOL_SIZE
          value: "50"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
      - name: specialist-1
        image: hybrid-agent:latest
        ports:
        - containerPort: 14001
        env:
        - name: AGENT_ROLE
          value: "specialist"
        - name: AGENT_PORT
          value: "14001"
---
apiVersion: v1
kind: Service
metadata:
  name: hybrid-agent-service
spec:
  selector:
    app: hybrid-agent
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: LoadBalancer
```

### 4. Monitoring and Observability

```python
# observability_setup.py
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import start_http_server

def setup_observability(config: AgentConfig):
    """Set up observability for the agent system."""
    if config.enable_tracing:
        # Set up OpenTelemetry
        trace.set_tracer_provider(TracerProvider())
        tracer_provider = trace.get_tracer_provider()
        
        # Configure OTLP exporter
        otlp_exporter = OTLPSpanExporter(
            endpoint=config.trace_endpoint,
            insecure=True
        )
        
        # Add batch processor
        span_processor = BatchSpanProcessor(otlp_exporter)
        tracer_provider.add_span_processor(span_processor)
    
    # Start Prometheus metrics server
    start_http_server(9090)
    
    return trace.get_tracer(__name__)
```

---

## Example: Building a New Multi-Agent System

Let's build a complete example: **Document Analysis System**

### Step 1: System Design

```python
"""
Document Analysis System
- Orchestrator: document_analysis_orchestrator
- Specialists:
  - text_extractor_agent: Extracts text from various formats
  - entity_recognition_agent: Identifies entities (people, places, organizations)
  - sentiment_analyzer_agent: Analyzes sentiment and tone
  - summarizer_agent: Creates concise summaries
  - classifier_agent: Categorizes documents
"""
```

### Step 2: Create Orchestrator

```python
# document_orchestrator.py
from typing import Dict, Any, List
import asyncio
from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.common.quality_framework import QualityDomain
from a2a_mcp.common.observability import trace_async

class DocumentAnalysisOrchestrator(StandardizedAgentBase):
    """Orchestrates document analysis workflow."""
    
    def __init__(self):
        super().__init__(
            agent_name="Document Analysis Orchestrator",
            description="Coordinates document analysis specialists",
            quality_config={
                "domain": QualityDomain.GENERAL,
                "thresholds": {
                    "extraction_quality": {"min_value": 0.9, "weight": 1.2},
                    "entity_accuracy": {"min_value": 0.85, "weight": 1.1},
                    "summary_coherence": {"min_value": 0.8, "weight": 1.0}
                }
            }
        )
        
        self.specialists = {
            "text_extractor": {"port": 14001, "timeout": 30},
            "entity_recognizer": {"port": 14002, "timeout": 20},
            "sentiment_analyzer": {"port": 14003, "timeout": 15},
            "summarizer": {"port": 14004, "timeout": 45},
            "classifier": {"port": 14005, "timeout": 20}
        }
    
    @trace_async("analyze_document")
    async def analyze_document(
        self, 
        document_path: str,
        analysis_options: Dict[str, bool] = None
    ) -> Dict[str, Any]:
        """
        Analyze a document using specialist agents.
        
        Args:
            document_path: Path to the document
            analysis_options: Which analyses to perform
            
        Returns:
            Complete analysis results
        """
        # Default options
        options = {
            "extract_entities": True,
            "analyze_sentiment": True,
            "generate_summary": True,
            "classify_document": True,
            **(analysis_options or {})
        }
        
        # Step 1: Extract text
        text_content = await self._extract_text(document_path)
        
        # Step 2: Parallel analysis
        analysis_tasks = []
        
        if options["extract_entities"]:
            analysis_tasks.append(self._extract_entities(text_content))
        
        if options["analyze_sentiment"]:
            analysis_tasks.append(self._analyze_sentiment(text_content))
        
        if options["classify_document"]:
            analysis_tasks.append(self._classify_document(text_content))
        
        # Execute parallel tasks
        parallel_results = await asyncio.gather(
            *analysis_tasks, 
            return_exceptions=True
        )
        
        # Step 3: Generate summary (may use other results)
        summary = None
        if options["generate_summary"]:
            context = {
                "entities": parallel_results[0] if options["extract_entities"] else None,
                "sentiment": parallel_results[1] if options["analyze_sentiment"] else None
            }
            summary = await self._generate_summary(text_content, context)
        
        # Compile results
        return {
            "document_path": document_path,
            "text_content": text_content,
            "entities": parallel_results[0] if options["extract_entities"] else None,
            "sentiment": parallel_results[1] if options["analyze_sentiment"] else None,
            "classification": parallel_results[2] if options["classify_document"] else None,
            "summary": summary,
            "analysis_options": options
        }
```

### Step 3: Create Specialist Agent

```python
# entity_recognition_agent.py
from typing import Dict, Any, List
from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.common.quality_framework import QualityDomain

class EntityRecognitionAgent(StandardizedAgentBase):
    """Extracts named entities from text."""
    
    def __init__(self):
        super().__init__(
            agent_name="Entity Recognition Agent",
            description="Identifies people, places, organizations in text",
            quality_config={
                "domain": QualityDomain.GENERAL,
                "thresholds": {
                    "precision": {"min_value": 0.85, "weight": 1.2},
                    "recall": {"min_value": 0.8, "weight": 1.1},
                    "f1_score": {"min_value": 0.82, "weight": 1.0}
                }
            }
        )
        
        # Initialize NER model (example with spaCy)
        import spacy
        self.nlp = spacy.load("en_core_web_sm")
    
    async def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract named entities from text."""
        # Process text
        doc = self.nlp(text)
        
        # Extract entities by type
        entities = {
            "PERSON": [],
            "ORG": [],
            "GPE": [],  # Geopolitical entities
            "DATE": [],
            "MONEY": [],
            "PRODUCT": []
        }
        
        for ent in doc.ents:
            if ent.label_ in entities:
                entities[ent.label_].append({
                    "text": ent.text,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "confidence": 0.85  # Model-specific confidence
                })
        
        # Calculate quality metrics
        total_entities = sum(len(v) for v in entities.values())
        quality_metrics = {
            "precision": 0.87,  # Would be calculated from validation set
            "recall": 0.83,
            "f1_score": 0.85
        }
        
        # Validate quality
        quality_result = await self.quality_framework.validate_response(
            quality_metrics,
            "entity_extraction"
        )
        
        return {
            "entities": entities,
            "total_count": total_entities,
            "quality": quality_result,
            "model": "spacy_en_core_web_sm"
        }
```

### Step 4: Deploy the System

```python
# deploy.py
import asyncio
from agents.orchestrator import DocumentAnalysisOrchestrator
from agents.specialists import (
    TextExtractorAgent,
    EntityRecognitionAgent,
    SentimentAnalyzerAgent,
    SummarizerAgent,
    ClassifierAgent
)

async def start_document_analysis_system():
    """Start the complete document analysis system."""
    # Start specialist agents on their ports
    specialists = [
        TextExtractorAgent(port=14001),
        EntityRecognitionAgent(port=14002),
        SentimentAnalyzerAgent(port=14003),
        SummarizerAgent(port=14004),
        ClassifierAgent(port=14005)
    ]
    
    # Start each specialist
    specialist_tasks = []
    for agent in specialists:
        task = asyncio.create_task(agent.start_server())
        specialist_tasks.append(task)
    
    # Start orchestrator
    orchestrator = DocumentAnalysisOrchestrator()
    await orchestrator._init_task
    
    # Example usage
    result = await orchestrator.analyze_document(
        document_path="/path/to/document.pdf",
        analysis_options={
            "extract_entities": True,
            "analyze_sentiment": True,
            "generate_summary": True,
            "classify_document": True
        }
    )
    
    print("Analysis Complete:")
    print(f"Entities found: {result['entities']['total_count']}")
    print(f"Sentiment: {result['sentiment']['overall']}")
    print(f"Classification: {result['classification']['category']}")
    print(f"Summary: {result['summary']['text'][:200]}...")
    
    # Keep system running
    await asyncio.gather(*specialist_tasks)

if __name__ == "__main__":
    asyncio.run(start_document_analysis_system())
```

---

## Conclusion

The Hybrid Framework (A2A-MCP + Google ADK) provides a powerful foundation for building production-ready multi-agent systems. By following this guide, you can:

1. **Leverage Best of Both Worlds**: Google ADK's LLM capabilities with A2A-MCP's enterprise features
2. **Build Scalable Systems**: From simple two-agent systems to complex orchestrations
3. **Ensure Quality**: Built-in validation and monitoring
4. **Deploy with Confidence**: Production-ready patterns and practices

### Next Steps

1. Start with the basic templates
2. Customize quality metrics for your domain
3. Add specialized agents as needed
4. Deploy with proper monitoring
5. Iterate based on performance metrics

### Resources

- A2A-MCP Framework documentation
- Google ADK documentation
- Example implementations in `/src/a2a_mcp/agents/adk_examples/`
- Test suites for reference patterns

Remember: The key to success is starting simple and iterating based on real-world performance and user feedback.