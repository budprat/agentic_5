# Master Architect V2.0 Implementation Plan for A2A-MCP Framework

## Executive Summary

This document provides a comprehensive implementation plan for integrating the Master Architect V2.0 Enhanced system into the existing A2A-MCP framework. The plan maintains 100% compatibility with current patterns while adding universal agent building capabilities, hybrid routing, research pipelines, and visual workflow design.

**Version**: 2.0-A2A-MCP-ADAPTED  
**Framework**: A2A-MCP Compatible  
**Date**: January 2025  
**Status**: Ready for Implementation

---

## 🔍 A2A-MCP Framework Analysis

### Current Framework Strengths
Based on analysis of your existing codebase:

1. **Solid Foundation**: 
   - `BaseAgent` class with streaming and invoke patterns
   - `ParallelWorkflowGraph` with NetworkX for complex orchestration
   - Agent cards system with skills, examples, and endpoints
   - Google ADK integration via `adk_travel_agent.py` pattern

2. **Proven MCP Integration**:
   - Multiple MCP servers: brightdata, brave, supabase, snowflake, etc.
   - `MCPToolset` with `SseConnectionParams` for tool discovery
   - `get_mcp_server_config()` utility for server discovery

3. **Working Agent Ecosystem**:
   - Market Oracle agents demonstrate specialized domain expertise
   - Orchestrator agents coordinate multi-agent workflows
   - A2A protocol enables agent-to-agent communication

4. **Cloud Deployment Ready**:
   - Google Cloud deployment tutorial with ADK patterns
   - Agent cards define deployment endpoints and capabilities
   - Authentication and security patterns established

### Integration Strategy

The Master Architect V2.0 will be implemented as **extensions** to your existing framework, not replacements:

- **Extends** your `BaseAgent` class hierarchy
- **Leverages** your existing MCP server infrastructure  
- **Follows** your agent cards and skills patterns
- **Uses** your `ParallelWorkflowGraph` for orchestration
- **Maintains** your Google ADK deployment approach

---

## 🏗️ Adapted Architecture

```
A2A-MCP Master Architect Integration Architecture
════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────┐
│                MASTER ARCHITECT LAYER                    │
├─────────────────────────────────────────────────────────┤
│ • MasterArchitectAgent (extends BaseAgent)              │
│ • HybridRouterAgent (extends BaseAgent)                 │
│ • AgentBuilderAgent (extends BaseAgent)                 │
└────────────────┬────────────────────────────────────────┘
                 │
┌─────────────────────────────────────────────────────────┐
│              24 UNIVERSAL AGENTS LAYER                   │
├─────────────────────────────────────────────────────────┤
│ • GoalPlannerAgent (BaseAgent + ADK pattern)            │
│ • ReasoningEngineAgent (BaseAgent + ADK pattern)        │
│ • MemoryRecallAgent (BaseAgent + ADK pattern)           │
│ • ... (21 more universal agents)                        │
└────────────────┬────────────────────────────────────────┘
                 │
┌─────────────────────────────────────────────────────────┐
│            ENHANCED ORCHESTRATION LAYER                  │
├─────────────────────────────────────────────────────────┤
│ • MasterArchitectWorkflowGraph (extends your existing)  │
│ • HybridRouter (quick vs deep path routing)             │
│ • ResearchPipelineAgent (uses your MCP servers)         │
└────────────────┬────────────────────────────────────────┘
                 │
┌─────────────────────────────────────────────────────────┐
│               YOUR EXISTING FRAMEWORK                    │
├─────────────────────────────────────────────────────────┤
│ • ParallelWorkflowGraph (your NetworkX orchestration)   │
│ • MCP Servers (brightdata, brave, supabase, etc.)       │
│ • Agent Cards System (skills-based JSON configs)        │
│ • Google ADK Integration (adk_travel_agent pattern)     │
│ • Market Oracle Agents (your existing specialists)      │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Implementation Directory Structure

### New Directories (Following Your Conventions)

```
src/a2a_mcp/agents/
├── master_architect/                   # NEW - Main architect system
│   ├── __init__.py
│   ├── master_architect_agent.py       # Main orchestrator (extends BaseAgent)
│   ├── hybrid_router_agent.py          # Routing intelligence
│   ├── agent_builder_agent.py          # Agent creation system
│   ├── research_pipeline_agent.py      # Deep research capabilities
│   └── visual_builder_agent.py         # Drag-drop workflow designer
│
├── universal_agents/                   # NEW - 24 universal agents
│   ├── __init__.py
│   ├── goal_planner_agent.py           # Strategic planning specialist
│   ├── reasoning_engine_agent.py       # Logic and analysis expert
│   ├── memory_recall_agent.py          # Context and history manager
│   ├── research_analyst_agent.py       # Information gathering
│   ├── data_scientist_agent.py         # Analytics and ML specialist
│   ├── code_architect_agent.py         # Software development expert
│   ├── content_creator_agent.py        # Writing and content generation
│   ├── visual_designer_agent.py        # UI/UX and graphics
│   ├── project_manager_agent.py        # Coordination and timelines
│   ├── interaction_manager_agent.py    # User experience optimization
│   ├── quality_assurance_agent.py      # Testing and validation
│   ├── security_specialist_agent.py    # Security and compliance
│   ├── performance_optimizer_agent.py  # Speed and efficiency
│   ├── integration_specialist_agent.py # API and system integration
│   ├── deployment_engineer_agent.py    # Infrastructure and DevOps
│   ├── documentation_agent.py          # Technical writing
│   ├── user_profiling_agent.py         # User behavior analysis
│   ├── scheduler_habit_agent.py        # Time and routine management
│   ├── notification_agent.py           # Communication management
│   ├── personalization_agent.py        # Customization and preferences
│   ├── feedback_loop_agent.py          # Continuous improvement
│   ├── error_handling_agent.py         # Resilience and recovery
│   ├── monetization_agent.py           # Business model optimization
│   └── collaboration_router_agent.py   # Multi-agent coordination
│
├── enhanced_workflows/                 # NEW - Advanced workflow patterns
│   ├── __init__.py
│   ├── master_architect_workflow.py    # Enhanced parallel workflow
│   ├── research_workflow.py            # Deep research orchestration
│   └── visual_workflow.py              # Visual builder backend
│
├── market_oracle/                      # EXISTING - Your proven agents
│   ├── oracle_prime_agent.py           # Your existing orchestrator
│   ├── sentiment_seeker_agent.py       # Your existing specialist
│   └── ... (all your existing agents)
│
└── ... (all your existing agent directories)

agent_cards/                            # EXISTING + NEW cards
├── master_architect_agent.json         # NEW
├── hybrid_router_agent.json            # NEW
├── goal_planner_agent.json             # NEW
├── ... (cards for all 24 universal agents)
├── oracle_prime_agent.json             # EXISTING
└── ... (all your existing agent cards)
```

---

## 🔧 Core Implementation Components

### 1. Master Architect Agent (Extends Your BaseAgent)

```python
# src/a2a_mcp/agents/master_architect/master_architect_agent.py
"""Master Architect Agent - Universal agent builder with hybrid routing."""

import logging
import json
from collections.abc import AsyncIterable
from typing import Dict, Any, List

from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import init_api_key, get_mcp_server_config
from a2a_mcp.common.parallel_workflow import ParallelWorkflowGraph, ParallelWorkflowNode
from a2a_mcp.agents.master_architect.hybrid_router_agent import HybridRouterAgent
from a2a_mcp.agents.master_architect.agent_builder_agent import AgentBuilderAgent
from google import genai

logger = logging.getLogger(__name__)

class MasterArchitectAgent(BaseAgent):
    """Universal agent builder with hybrid routing capabilities."""

    def __init__(self):
        init_api_key()  # Your existing utility
        super().__init__(
            agent_name="Master Architect",
            description="Universal agent builder with hybrid routing and research capabilities",
            content_types=["text", "text/plain"],
        )
        
        # Core components
        self.hybrid_router = HybridRouterAgent()
        self.agent_builder = AgentBuilderAgent()
        self.graph = ParallelWorkflowGraph()  # Your existing class
        
        # State management
        self.universal_agents = self._load_universal_agents()
        self.results = []
        self.context_data = {}
        self.query_history = []
        
    async def stream(self, query: str, context_id: str, task_id: str) -> AsyncIterable[Dict[str, Any]]:
        """Main entry point following your BaseAgent pattern."""
        logger.info(f"MasterArchitect processing: {query[:100]}...")
        
        try:
            # Step 1: Route the request (quick vs deep)
            routing_decision = await self.hybrid_router.route_request(query)
            
            yield {
                "type": "routing_decision",
                "decision": routing_decision.to_dict(),
                "estimated_time": routing_decision.estimated_time
            }
            
            # Step 2: Execute based on route type
            if routing_decision.route_type == "quick":
                async for result in self._execute_quick_route(query, context_id, task_id, routing_decision):
                    yield result
            elif routing_decision.route_type == "deep":
                async for result in self._execute_deep_route(query, context_id, task_id, routing_decision):
                    yield result
            elif routing_decision.route_type == "build":
                async for result in self._execute_build_route(query, context_id, task_id, routing_decision):
                    yield result
            
            # Step 3: Generate final summary
            summary = await self._generate_summary()
            yield {
                "type": "final_summary",
                "summary": summary,
                "artifacts": self._collect_artifacts()
            }
            
        except Exception as e:
            logger.error(f"MasterArchitect error: {e}")
            yield {
                "type": "error",
                "error": str(e),
                "stage": "execution"
            }

    async def _execute_quick_route(self, query: str, context_id: str, task_id: str, routing_decision) -> AsyncIterable[Dict[str, Any]]:
        """Quick route using your existing parallel workflow."""
        yield {"type": "route_start", "route": "quick", "agents": len(routing_decision.selected_agents)}
        
        # Create workflow nodes following your pattern
        nodes = []
        for agent_def in routing_decision.selected_agents:
            node = ParallelWorkflowNode(
                id=agent_def.id,
                agent_card=agent_def.to_agent_card(),  # Convert to your agent card format
                query=query
            )
            nodes.append(node)
        
        # Execute using your existing parallel workflow
        async for chunk in self.graph.execute_parallel_nodes(nodes, context_id):
            yield {
                "type": "agent_result",
                "node_id": chunk.get("node_id"),
                "content": chunk.get("content"),
                "status": chunk.get("status")
            }
            
        yield {"type": "route_complete", "route": "quick"}

    async def _execute_deep_route(self, query: str, context_id: str, task_id: str, routing_decision) -> AsyncIterable[Dict[str, Any]]:
        """Deep route with research pipeline."""
        yield {"type": "route_start", "route": "deep", "phases": ["research", "analysis", "synthesis"]}
        
        # Phase 1: Research using your MCP servers
        research_agent = self._get_research_pipeline_agent()
        research_results = await research_agent.conduct_research(query)
        
        yield {
            "type": "research_complete",
            "sources": len(research_results.sources),
            "insights": research_results.key_insights
        }
        
        # Phase 2: First-principles analysis
        analysis_results = await self._conduct_first_principles_analysis(query, research_results)
        
        yield {
            "type": "analysis_complete",
            "principles": analysis_results.principles,
            "frameworks": analysis_results.recommended_frameworks
        }
        
        # Phase 3: Agent synthesis
        synthesis_results = await self._synthesize_agent_solution(query, research_results, analysis_results)
        
        yield {
            "type": "synthesis_complete",
            "agent_design": synthesis_results.agent_design,
            "implementation": synthesis_results.implementation_plan
        }
        
        yield {"type": "route_complete", "route": "deep"}

    def _load_universal_agents(self) -> Dict[int, 'UniversalAgentDefinition']:
        """Load 24 universal agents following your agent card pattern."""
        # This will load agent definitions that follow your skills-based format
        pass

    async def _generate_summary(self) -> str:
        """Generate summary using your existing LLM pattern."""
        client = genai.Client()
        # Use your existing prompt pattern from parallel_orchestrator_agent.py
        pass
```

### 2. Agent Cards for Universal Agents (Following Your Format)

```json
// agent_cards/goal_planner_agent.json
{
    "name": "Goal Planner Agent",
    "description": "Strategic planning and goal decomposition specialist",
    "url": "http://localhost:10601/",
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
            "id": "goal_decomposition",
            "name": "Goal Decomposition",
            "description": "Break down complex objectives into actionable tasks",
            "tags": ["planning", "strategy", "decomposition", "roadmap"],
            "examples": [
                "Create a 6-month product roadmap for an AI platform",
                "Plan a machine learning project from research to deployment",
                "Design a comprehensive marketing campaign strategy"
            ]
        },
        {
            "id": "timeline_creation",
            "name": "Timeline & Milestone Planning",
            "description": "Create realistic timelines with dependencies and milestones",
            "tags": ["timeline", "milestones", "dependencies", "scheduling"],
            "examples": [
                "Build project timeline with critical path analysis",
                "Create quarterly OKRs with measurable outcomes",
                "Plan resource allocation across multiple initiatives"
            ]
        },
        {
            "id": "risk_assessment",
            "name": "Strategic Risk Assessment",
            "description": "Identify potential risks and mitigation strategies",
            "tags": ["risk", "mitigation", "contingency", "planning"],
            "examples": [
                "Assess risks for new product launch",
                "Create contingency plans for project delays",
                "Identify resource bottlenecks and alternatives"
            ]
        }
    ]
}
```

### 3. Universal Agent Implementation (Following Your ADK Pattern)

```python
# src/a2a_mcp/agents/universal_agents/goal_planner_agent.py
"""Goal Planner Agent - Strategic planning and goal decomposition specialist."""

import logging
from collections.abc import AsyncIterable
from typing import Dict, Any

from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import init_api_key, get_mcp_server_config
from a2a_mcp.common.agent_runner import AgentRunner
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams
from google.genai import types as genai_types

logger = logging.getLogger(__name__)

GOAL_PLANNER_PROMPT = """
You are a Goal Planner Agent, a specialized strategic planning and goal decomposition expert.

Your capabilities:
1. Break down complex objectives into actionable tasks
2. Create realistic timelines with dependencies and milestones  
3. Prioritize tasks based on impact and resource constraints
4. Identify potential risks and mitigation strategies
5. Align tactical activities with strategic objectives

When planning goals, you should:
1. Understand the high-level objective and context
2. Decompose into logical phases and sub-goals
3. Create realistic timelines considering dependencies
4. Identify resource requirements and constraints
5. Plan risk mitigation and contingency strategies
6. Define measurable outcomes and success criteria

Output Format:
Provide structured plans with clear phases, timelines, dependencies, and success metrics.
Use markdown formatting for readability.
"""

class GoalPlannerAgent(BaseAgent):
    """Goal Planner Agent following your ADK integration pattern."""

    def __init__(self):
        init_api_key()  # Your existing utility
        super().__init__(
            agent_name="Goal Planner Agent",
            description="Strategic planning and goal decomposition specialist",
            content_types=["text", "text/plain"],
        )
        self.agent = None
        self.runner = None

    async def init_agent(self):
        """Initialize ADK agent following your adk_travel_agent.py pattern."""
        logger.info(f"Initializing {self.agent_name}")
        
        # Get MCP server config using your utility
        config = get_mcp_server_config()
        logger.info(f"MCP Server url={config.url}")
        
        # Load tools from MCP server
        tools = await MCPToolset(
            connection_params=SseConnectionParams(url=config.url)
        ).get_tools()

        for tool in tools:
            logger.info(f"Loaded tool: {tool.name}")
            
        # Create ADK agent following your pattern
        generate_content_config = genai_types.GenerateContentConfig(temperature=0.1)
        
        self.agent = Agent(
            name="goal_planner",
            instruction=GOAL_PLANNER_PROMPT,
            model='gemini-2.0-flash',
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            generate_content_config=generate_content_config,
            tools=tools,
        )
        
        # Initialize runner using your pattern
        self.runner = AgentRunner()

    async def stream(self, query: str, context_id: str, task_id: str) -> AsyncIterable[Dict[str, Any]]:
        """Stream responses following your BaseAgent pattern."""
        logger.info(f"GoalPlannerAgent stream for session {context_id} {task_id} - {query}")

        if not query:
            raise ValueError("Query cannot be empty")

        if not self.agent:
            await self.init_agent()
            
        # Stream results using your runner pattern
        async for chunk in self.runner.run_stream(self.agent, query, context_id):
            yield {
                "type": "agent_response",
                "agent": self.agent_name,
                "content": chunk.content if hasattr(chunk, 'content') else str(chunk),
                "chunk_type": chunk.type if hasattr(chunk, 'type') else 'text'
            }

    async def invoke(self, query: str, session_id: str) -> dict:
        """Non-streaming invoke method following your pattern."""
        logger.info(f"GoalPlannerAgent invoke for session {session_id}")
        
        # Collect all streaming results
        results = []
        async for chunk in self.stream(query, session_id, "invoke"):
            results.append(chunk)
            
        return {
            "agent": self.agent_name,
            "results": results,
            "session_id": session_id
        }
```

### 4. Hybrid Router Agent (Extends Your Routing Logic)

```python
# src/a2a_mcp/agents/master_architect/hybrid_router_agent.py
"""Hybrid Router Agent - Intelligent routing for quick vs deep vs build paths."""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum

from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import init_api_key

logger = logging.getLogger(__name__)

class RouteType(Enum):
    QUICK = "quick"     # 30 seconds, 1-3 agents, simple tasks
    DEEP = "deep"       # 5-10 minutes, research + first principles
    BUILD = "build"     # Agent building and complex workflows

@dataclass
class RoutingDecision:
    route_type: RouteType
    selected_agents: List['UniversalAgentDefinition']
    complexity_score: float
    confidence: float
    estimated_time: str
    reasoning: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "route_type": self.route_type.value,
            "selected_agents": [agent.to_dict() for agent in self.selected_agents],
            "complexity_score": self.complexity_score,
            "confidence": self.confidence,
            "estimated_time": self.estimated_time,
            "reasoning": self.reasoning
        }

class HybridRouterAgent(BaseAgent):
    """Intelligent routing engine for Master Architect."""

    def __init__(self):
        init_api_key()
        super().__init__(
            agent_name="Hybrid Router",
            description="Intelligent routing for quick vs deep execution paths",
            content_types=["text", "text/plain"],
        )
        
        # Load agent definitions and routing rules
        self.universal_agents = self._load_universal_agents()
        self.routing_keywords = self._load_routing_keywords()
        
    async def route_request(self, query: str) -> RoutingDecision:
        """Route request to appropriate execution path."""
        
        # Step 1: Keyword analysis
        keyword_matches = self._analyze_keywords(query)
        
        # Step 2: Complexity assessment
        complexity_score = self._assess_complexity(query, keyword_matches)
        
        # Step 3: Agent selection
        selected_agents = self._select_agents(keyword_matches, complexity_score)
        
        # Step 4: Route decision
        if self._is_build_request(query):
            return RoutingDecision(
                route_type=RouteType.BUILD,
                selected_agents=selected_agents,
                complexity_score=complexity_score,
                confidence=0.9,
                estimated_time="10-30 minutes",
                reasoning="Agent building or complex workflow creation detected"
            )
        elif complexity_score < 0.3 and len(selected_agents) <= 3:
            return RoutingDecision(
                route_type=RouteType.QUICK,
                selected_agents=selected_agents,
                complexity_score=complexity_score,
                confidence=0.8,
                estimated_time="30 seconds",
                reasoning=f"Simple task with {len(selected_agents)} specific agents"
            )
        else:
            return RoutingDecision(
                route_type=RouteType.DEEP,
                selected_agents=selected_agents,
                complexity_score=complexity_score,
                confidence=0.7,
                estimated_time="5-10 minutes",
                reasoning="Complex task requiring research and first-principles analysis"
            )

    def _analyze_keywords(self, query: str) -> Dict[str, float]:
        """Analyze query for agent-specific keywords."""
        keywords = {}
        query_lower = query.lower()
        
        for agent_id, agent_def in self.universal_agents.items():
            score = 0.0
            for keyword in agent_def.keywords:
                if keyword in query_lower:
                    score += 1.0
            keywords[agent_id] = score / len(agent_def.keywords) if agent_def.keywords else 0.0
            
        return keywords

    def _assess_complexity(self, query: str, keyword_matches: Dict[str, float]) -> float:
        """Assess complexity of the request."""
        complexity_indicators = [
            "complex", "comprehensive", "full", "complete", "enterprise",
            "production", "scalable", "robust", "advanced", "sophisticated",
            "integrate", "architecture", "framework", "system", "platform"
        ]
        
        query_lower = query.lower()
        complexity_score = sum(1 for indicator in complexity_indicators if indicator in query_lower)
        
        # Normalize to 0-1 scale
        return min(complexity_score / len(complexity_indicators), 1.0)

    def _is_build_request(self, query: str) -> bool:
        """Check if this is an agent building request."""
        build_keywords = [
            "create agent", "build agent", "design agent", "implement agent",
            "agent for", "agent that", "create workflow", "build workflow",
            "design system", "implement system"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in build_keywords)

    def _select_agents(self, keyword_matches: Dict[str, float], complexity_score: float) -> List['UniversalAgentDefinition']:
        """Select appropriate agents based on matches and complexity."""
        # Sort agents by keyword match score
        sorted_agents = sorted(
            keyword_matches.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Select top agents based on complexity
        if complexity_score < 0.3:
            # Simple task - select top 1-3 agents
            selected_count = min(3, len([a for a in sorted_agents if a[1] > 0]))
        else:
            # Complex task - select more agents
            selected_count = min(8, len([a for a in sorted_agents if a[1] > 0]))
            
        selected_agent_ids = [agent_id for agent_id, score in sorted_agents[:selected_count] if score > 0]
        
        return [self.universal_agents[agent_id] for agent_id in selected_agent_ids]

    def _load_universal_agents(self) -> Dict[int, 'UniversalAgentDefinition']:
        """Load universal agent definitions."""
        # This will be implemented to load from your agent cards
        pass

    def _load_routing_keywords(self) -> Dict[str, List[str]]:
        """Load routing keyword mappings."""
        # This will be implemented to load routing rules
        pass
```

### 5. Research Pipeline Agent (Uses Your MCP Servers)

```python
# src/a2a_mcp/agents/master_architect/research_pipeline_agent.py
"""Research Pipeline Agent - Deep research using existing MCP servers."""

import logging
from typing import Dict, Any, List
from dataclasses import dataclass

from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import init_api_key, get_mcp_server_config
from a2a_mcp.mcp.client import MCPClient

logger = logging.getLogger(__name__)

@dataclass
class ResearchResults:
    sources: List[Dict[str, Any]]
    key_insights: List[str]
    code_patterns: List[Dict[str, Any]]
    citations: List[str]
    
class ResearchPipelineAgent(BaseAgent):
    """Deep research pipeline using your existing MCP servers."""

    def __init__(self):
        init_api_key()
        super().__init__(
            agent_name="Research Pipeline",
            description="Deep research with web crawling, code analysis, and citation tracking",
            content_types=["text", "text/plain"],
        )
        
        # Your existing MCP servers
        self.mcp_servers = {
            "brightdata": "brightdata",
            "brave": "brave", 
            "puppeteer": "puppeteer",
            "context7": "context7"
        }

    async def conduct_research(self, query: str) -> ResearchResults:
        """Conduct comprehensive research using your MCP infrastructure."""
        
        # Stage 1: Web search using your Brave MCP
        search_results = await self._web_search(query)
        
        # Stage 2: Deep content scraping using your BrightData MCP
        content_results = await self._scrape_content(search_results)
        
        # Stage 3: Code pattern discovery using your Context7 MCP
        code_patterns = await self._discover_code_patterns(query)
        
        # Stage 4: Synthesis and citation tracking
        insights = await self._synthesize_insights(content_results, code_patterns)
        citations = await self._format_citations(search_results, content_results)
        
        return ResearchResults(
            sources=search_results + content_results,
            key_insights=insights,
            code_patterns=code_patterns,
            citations=citations
        )

    async def _web_search(self, query: str) -> List[Dict[str, Any]]:
        """Search web using your Brave MCP server."""
        try:
            # Use your existing MCP client pattern
            mcp_client = MCPClient(server_name="brave")
            
            results = await mcp_client.call_tool(
                tool_name="brave_web_search",
                arguments={
                    "query": query,
                    "count": 10
                }
            )
            
            logger.info(f"Brave search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return []

    async def _scrape_content(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Scrape content using your BrightData MCP server."""
        content_results = []
        
        for result in search_results[:5]:  # Limit to top 5 results
            try:
                url = result.get("url")
                if not url:
                    continue
                    
                # Use your existing MCP client pattern
                mcp_client = MCPClient(server_name="brightdata")
                
                content = await mcp_client.call_tool(
                    tool_name="scrape_as_markdown",
                    arguments={"url": url}
                )
                
                content_results.append({
                    "url": url,
                    "title": result.get("title", ""),
                    "content": content,
                    "source": "brightdata_scrape"
                })
                
            except Exception as e:
                logger.error(f"Content scraping error for {url}: {e}")
                continue
                
        logger.info(f"Scraped {len(content_results)} pages")
        return content_results

    async def _discover_code_patterns(self, query: str) -> List[Dict[str, Any]]:
        """Discover code patterns using your Context7 MCP server."""
        try:
            # Use your existing MCP client pattern
            mcp_client = MCPClient(server_name="context7")
            
            # First resolve library ID
            library_result = await mcp_client.call_tool(
                tool_name="resolve-library-id",
                arguments={"libraryName": query}
            )
            
            if library_result:
                # Get documentation and code examples
                docs_result = await mcp_client.call_tool(
                    tool_name="get-library-docs",
                    arguments={
                        "context7CompatibleLibraryID": library_result["library_id"],
                        "tokens": 5000
                    }
                )
                
                return [{
                    "library": library_result["library_id"],
                    "documentation": docs_result,
                    "source": "context7"
                }]
                
        except Exception as e:
            logger.error(f"Code pattern discovery error: {e}")
            
        return []

    async def _synthesize_insights(self, content_results: List[Dict[str, Any]], code_patterns: List[Dict[str, Any]]) -> List[str]:
        """Synthesize key insights from research results."""
        insights = []
        
        # Extract insights from content
        for content in content_results:
            # Use your existing LLM pattern for insight extraction
            # This would follow your genai.Client() pattern from existing agents
            pass
            
        # Extract insights from code patterns
        for pattern in code_patterns:
            # Extract technical insights and best practices
            pass
            
        return insights

    async def _format_citations(self, search_results: List[Dict[str, Any]], content_results: List[Dict[str, Any]]) -> List[str]:
        """Format citations in APA style."""
        citations = []
        
        for result in search_results + content_results:
            citation = f"{result.get('title', 'Unknown')}. Retrieved from {result.get('url', '')}"
            citations.append(citation)
            
        return citations
```

---

## 📋 Implementation Phases

### Phase 1: Foundation Setup (Weeks 1-2)

**Week 1: Core Structure**
- [ ] Create `src/a2a_mcp/agents/master_architect/` directory
- [ ] Create `src/a2a_mcp/agents/universal_agents/` directory  
- [ ] Implement `MasterArchitectAgent` extending your `BaseAgent`
- [ ] Create agent cards for Master Architect and Router agents
- [ ] Set up basic routing logic

**Week 2: Hybrid Router**
- [ ] Implement `HybridRouterAgent` with routing logic
- [ ] Create routing decision classes and enums
- [ ] Add complexity assessment algorithms
- [ ] Test quick vs deep route detection

### Phase 2: Universal Agents (Weeks 3-4)

**Week 3: Core Universal Agents (1-12)**
- [ ] Implement Goal Planner Agent following your ADK pattern
- [ ] Implement Reasoning Engine Agent
- [ ] Implement Memory & Recall Agent
- [ ] Implement Research Analyst Agent
- [ ] Implement Data Scientist Agent
- [ ] Implement Code Architect Agent
- [ ] Create agent cards for all 12 agents
- [ ] Test individual agent functionality

**Week 4: Interaction Universal Agents (13-24)**
- [ ] Implement Content Creator Agent
- [ ] Implement Visual Designer Agent
- [ ] Implement Project Manager Agent
- [ ] Implement Interaction Manager Agent
- [ ] Implement Quality Assurance Agent
- [ ] Implement Security Specialist Agent
- [ ] Implement remaining 6 universal agents
- [ ] Create complete agent card library

### Phase 3: Research Pipeline (Weeks 5-6)

**Week 5: MCP Integration**
- [ ] Implement `ResearchPipelineAgent` using your MCP servers
- [ ] Add web search via your Brave MCP
- [ ] Add content scraping via your BrightData MCP
- [ ] Add code discovery via your Context7 MCP
- [ ] Test MCP integration with existing servers

**Week 6: Research Synthesis**
- [ ] Implement research result synthesis
- [ ] Add citation tracking and formatting
- [ ] Create research workflow orchestration
- [ ] Add research result caching
- [ ] Test end-to-end research pipeline

### Phase 4: Enhanced Workflows (Weeks 7-8)

**Week 7: Master Architect Workflow**
- [ ] Extend your `ParallelWorkflowGraph` for Master Architect
- [ ] Implement quick route execution using your parallel pattern
- [ ] Implement deep route execution with research
- [ ] Add workflow state management
- [ ] Test workflow orchestration

**Week 8: Advanced Features**
- [ ] Implement Agent Builder functionality
- [ ] Add visual workflow design capabilities  
- [ ] Create export system for multiple formats
- [ ] Add workflow validation and testing
- [ ] Test complete system integration

### Phase 5: Visual Builder & Export (Weeks 9-10)

**Week 9: Visual Builder Backend**
- [ ] Implement Visual Builder Agent
- [ ] Create REST API for workflow design
- [ ] Add drag-drop workflow conversion
- [ ] Implement real-time workflow preview
- [ ] Test visual builder backend

**Week 10: Export System**
- [ ] Implement multi-format exporters (ADK, LangGraph, Docker, API)
- [ ] Create deployment script generators using your Cloud tutorial
- [ ] Add artifact generation (tests, docs, examples)
- [ ] Test export functionality for all formats
- [ ] Validate deployed agents work correctly

### Phase 6: Testing & Production (Weeks 11-12)

**Week 11: Comprehensive Testing**
- [ ] Unit tests for all components
- [ ] Integration tests with your existing agents
- [ ] End-to-end workflow tests
- [ ] Performance testing and optimization
- [ ] Security audit and validation

**Week 12: Production Deployment**
- [ ] Deploy to Google Cloud using your existing patterns
- [ ] Set up monitoring and logging
- [ ] Create comprehensive documentation
- [ ] Conduct user acceptance testing
- [ ] Production launch and monitoring

---

## 🚀 Deployment Integration

### Google Cloud Deployment (Following Your Tutorial)

The Master Architect system will deploy using your existing Google Cloud ADK patterns:

```bash
# Deploy Master Architect Agent
cd src/a2a_mcp/agents/master_architect
adk deploy cloud_run \
--project="Agents Cloud" \
--region="asia-south2-c" \
--service_name="master-architect-agent" \
--with_ui \
./

# Deploy Universal Agents
cd ../universal_agents
for agent in goal_planner reasoning_engine memory_recall; do
    adk deploy cloud_run \
    --project="Agents Cloud" \
    --region="asia-south2-c" \
    --service_name="${agent}-agent" \
    ./${agent}_agent
done
```

### Agent Card Updates

Master Architect agent cards will follow your established format:

```json
{
    "name": "Master Architect",
    "description": "Universal agent builder with hybrid routing",
    "url": "https://master-architect-agent-xxx-asia-south2.run.app/",
    "capabilities": {
        "streaming": "True",
        "pushNotifications": "True"
    },
    "skills": [
        {
            "id": "universal_agent_building",
            "name": "Universal Agent Building",
            "description": "Create specialized agents for any domain or task",
            "examples": [
                "Build a customer service chatbot",
                "Create a data analysis agent",
                "Design a content creation agent"
            ]
        }
    ]
}
```

---

## ✅ Success Criteria

### Technical Metrics
- [ ] **Route Performance**: Quick route <30 seconds, Deep route <10 minutes
- [ ] **Agent Quality**: 95%+ requirement coverage for generated agents
- [ ] **Integration**: 100% compatibility with existing A2A-MCP framework
- [ ] **Scalability**: Support 100+ concurrent agent building requests
- [ ] **Reliability**: 99.9% uptime for deployed Master Architect system

### Functional Metrics
- [ ] **Universal Coverage**: 24 universal agents covering all major domains
- [ ] **Export Compatibility**: 5+ export formats (ADK, LangGraph, Docker, API, Visual)
- [ ] **MCP Integration**: Seamless use of all existing MCP servers
- [ ] **Workflow Complexity**: Handle simple to enterprise-level agent requirements
- [ ] **Research Quality**: High-quality research results with proper citations

### User Experience Metrics
- [ ] **Ease of Use**: Non-technical users can build basic agents
- [ ] **Expert Flexibility**: Technical users have full customization control
- [ ] **Visual Interface**: Intuitive drag-drop workflow designer
- [ ] **Documentation**: Comprehensive guides and examples
- [ ] **Support**: Clear error messages and troubleshooting guides

---

## 🔧 Configuration & Usage

### Master Configuration

```python
# config/master_architect_config.py
MASTER_ARCHITECT_CONFIG = {
    "version": "2.0-a2a-mcp-adapted",
    "framework": "a2a-mcp",
    
    # Routing Configuration
    "routing": {
        "quick_route": {
            "max_agents": 3,
            "max_complexity": 0.3,
            "timeout": 30
        },
        "deep_route": {
            "enable_research": True,
            "research_depth": 3,
            "timeout": 600
        }
    },
    
    # Agent System
    "agents": {
        "universal_agent_count": 24,
        "base_class": "BaseAgent",  # Your existing base class
        "adk_integration": True,
        "mcp_integration": True
    },
    
    # MCP Servers (Your Existing)
    "mcp_servers": {
        "brightdata": "brightdata",
        "brave": "brave",
        "supabase": "supabase", 
        "snowflake": "snowflake",
        "puppeteer": "puppeteer",
        "context7": "context7"
    },
    
    # Deployment (Your Existing Patterns)
    "deployment": {
        "cloud_provider": "google_cloud",
        "project": "Agents Cloud",
        "region": "asia-south2-c",
        "deployment_method": "adk_deploy"
    }
}
```

### Usage Examples

```python
# Example 1: Quick Route Agent Building
from src.a2a_mcp.agents.master_architect.master_architect_agent import MasterArchitectAgent

architect = MasterArchitectAgent()

# Simple agent request - will route to quick path
response = await architect.stream(
    query="Create a customer service chatbot that handles basic FAQs",
    context_id="quick-demo-001",
    task_id="build-001"
)
# Expected: 30 seconds, uses Interaction Manager + Content Creator agents

# Example 2: Complex Agent Building - will route to deep path
response = await architect.stream(
    query="""Build a comprehensive financial analysis system that:
    - Analyzes market trends from multiple data sources
    - Provides risk assessment and portfolio optimization
    - Handles real-time trading signals
    - Ensures regulatory compliance
    - Scales to enterprise level""",
    context_id="deep-demo-001", 
    task_id="build-002"
)
# Expected: 5-10 minutes, full research + first principles + multi-agent synthesis

# Example 3: Using Individual Universal Agents
from src.a2a_mcp.agents.universal_agents.goal_planner_agent import GoalPlannerAgent

planner = GoalPlannerAgent()
plan = await planner.stream(
    query="Create a 6-month roadmap for launching an AI-powered mobile app",
    context_id="planning-001",
    task_id="plan-001"
)
```

---

## 📚 Documentation Plan

### Developer Documentation
- [ ] **Architecture Guide**: Complete system overview and design patterns
- [ ] **API Reference**: Full API documentation for all agents and components
- [ ] **Integration Guide**: How to integrate with existing A2A-MCP agents
- [ ] **Extension Guide**: How to add new universal agents and capabilities
- [ ] **Deployment Guide**: Cloud deployment using your established patterns

### User Documentation  
- [ ] **Quick Start Guide**: Get started with Master Architect in 10 minutes
- [ ] **Agent Building Tutorial**: Step-by-step agent creation examples
- [ ] **Visual Builder Guide**: Using the drag-drop interface
- [ ] **Best Practices**: Guidelines for effective agent design
- [ ] **Troubleshooting**: Common issues and solutions

### Code Documentation
- [ ] **Inline Documentation**: Comprehensive docstrings following your patterns
- [ ] **Code Examples**: Working examples for each component
- [ ] **Test Documentation**: How to run and extend the test suite
- [ ] **Configuration Reference**: All configuration options and defaults

---

## 🎯 Next Steps

1. **Immediate Actions**:
   - Review and approve this implementation plan
   - Set up development environment and project structure
   - Begin Phase 1 implementation with foundation components

2. **Resource Requirements**:
   - Development team familiar with your A2A-MCP patterns
   - Access to your existing Google Cloud and MCP infrastructure
   - Testing environment matching your production setup

3. **Risk Mitigation**:
   - Maintain backward compatibility with all existing agents
   - Implement comprehensive testing at each phase
   - Regular integration testing with your current system

4. **Success Validation**:
   - Deploy and test in your existing environment
   - Validate with your Market Oracle and Travel agents
   - Confirm Google Cloud deployment using your tutorial

---

**This implementation plan creates the most comprehensive agent building framework while maintaining 100% compatibility with your existing A2A-MCP system. The Master Architect V2.0 becomes a powerful extension that leverages all your existing infrastructure, patterns, and deployment methods.**

**Status**: Ready for Implementation 🚀  
**Framework**: A2A-MCP Compatible  
**Next Action**: Begin Phase 1 - Foundation Setup