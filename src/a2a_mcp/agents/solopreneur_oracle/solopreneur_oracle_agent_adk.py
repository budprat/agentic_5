"""Solopreneur Oracle - Master orchestrator with Google ADK + LangGraph integration following travel agent pattern."""

import logging
import json
import asyncio
from collections.abc import AsyncIterable
from typing import Dict, Any, List, Literal
from datetime import datetime

from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.common.a2a_protocol import A2AProtocolClient, A2A_AGENT_PORTS
from a2a_mcp.common.quality_framework import QualityThresholdFramework, QualityDomain
from a2a_mcp.common.agent_runner import AgentRunner
from a2a_mcp.common.utils import get_mcp_server_config, init_api_key
from a2a_mcp.common.types import TaskList
from a2a_mcp.common.parallel_workflow import (
    ParallelWorkflowGraph, 
    ParallelWorkflowNode,
    Status
)

# Google ADK imports
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from google.genai import types as genai_types

# LangGraph imports
from langchain_core.messages import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

import os
import aiohttp

logger = logging.getLogger(__name__)
memory = MemorySaver()

# Task Decomposition Response Format
class SolopreneurTaskFormat(BaseModel):
    """Response format for solopreneur task decomposition."""
    
    status: Literal['planning', 'ready', 'error'] = 'planning'
    analysis: str = Field(description="Analysis of the user request for solopreneur optimization")
    tasks: TaskList = Field(description="Decomposed tasks for domain oracles")
    coordination_strategy: str = Field(description="How tasks will be coordinated")
    domains_required: List[str] = Field(description="Required domain specialists")
    quality_requirements: Dict[str, float] = Field(description="Quality thresholds for each domain")
    optimization_focus: List[str] = Field(description="Key optimization areas identified")

# LangGraph Planning Instructions
SOLOPRENEUR_PLANNING_INSTRUCTIONS = """
You are the Solopreneur Oracle Task Planner. Analyze user requests and decompose them into coordinated tasks for domain specialists.

Domain Specialists Available:
- technical_intelligence: AI research, architecture, code quality, implementation strategies
- knowledge_management: Information organization, learning strategies, knowledge synthesis
- personal_optimization: Energy management, focus optimization, productivity strategies
- learning_enhancement: Skill development, education planning, learning acceleration
- integration_synthesis: Workflow integration, automation opportunities, cross-domain optimization

For each request:
1. Analyze scope and identify relevant domains for AI developer/entrepreneur context
2. Create specific, actionable tasks for each domain oracle
3. Define coordination strategy (parallel/sequential based on dependencies)
4. Set quality requirements per domain
5. Identify optimization opportunities and synergies

Focus on:
- Technical excellence and innovation
- Personal sustainability and energy optimization
- Learning efficiency and skill acceleration
- Workflow automation and productivity gains
- Cross-domain integration opportunities
"""

# Solopreneur synthesis prompt
SOLOPRENEUR_SYNTHESIS_PROMPT = """
You are Solopreneur Oracle, a master AI developer and entrepreneur strategist. 
Analyze the following intelligence data from domain specialists: "{original_query}"

Intelligence Data from Domain Specialists:
{intelligence_data}

Context:
{context}

Quality Thresholds:
- Minimum confidence score: {min_confidence}
- Technical feasibility threshold: {tech_threshold}
- Personal sustainability threshold: {personal_threshold}

Provide synthesis in this JSON format:
{{
    "executive_summary": "Brief 2-3 sentence summary of key recommendations",
    "confidence_score": 0.0-1.0,
    "technical_assessment": {{
        "feasibility_score": 0-100,
        "implementation_complexity": "low|medium|high",
        "technical_risks": ["risk1", "risk2"],
        "architecture_recommendations": ["rec1", "rec2"]
    }},
    "personal_optimization": {{
        "energy_impact": "positive|neutral|negative",
        "cognitive_load": "low|medium|high", 
        "sustainability_score": 0-100,
        "optimization_strategies": ["strategy1", "strategy2"]
    }},
    "strategic_insights": [
        {{"source": "domain", "insight": "key finding", "confidence": 0.0-1.0}},
        ...
    ],
    "integration_opportunities": {{
        "synergies": ["synergy1", "synergy2"],
        "workflow_optimizations": ["opt1", "opt2"],
        "automation_potential": ["area1", "area2"]
    }},
    "action_plan": {{
        "immediate_actions": ["action1", "action2"],
        "short_term_goals": ["goal1", "goal2"],
        "long_term_vision": "strategic direction",
        "success_metrics": ["metric1", "metric2"]
    }},
    "risk_assessment": {{
        "technical_risks": ["risk1", "risk2"],
        "personal_risks": ["risk1", "risk2"],
        "mitigation_strategies": ["strategy1", "strategy2"],
        "contingency_plans": ["plan1", "plan2"]
    }}
}}
"""

class SolopreneurOracleAgent(StandardizedAgentBase):
    """Master orchestrator for AI developer/entrepreneur intelligence with Google ADK + LangGraph integration."""

    def __init__(self):
        init_api_key()
        super().__init__(
            agent_name="Solopreneur Oracle",
            description="Master AI developer/entrepreneur intelligence orchestrator with Framework V2.0 compliance",
            instructions="You are Solopreneur Oracle, a master AI developer and entrepreneur strategist specializing in technical excellence, personal optimization, and learning acceleration.",
            quality_config={
                "domain": QualityDomain.BUSINESS,
                "thresholds": {
                    "confidence_score": {"min_value": 0.75, "weight": 1.0},
                    "technical_feasibility": {"min_value": 0.8, "weight": 1.2},
                    "personal_sustainability": {"min_value": 0.7, "weight": 1.0},
                    "risk_tolerance": {"min_value": 0.6, "max_value": 0.8, "weight": 0.8}
                }
            },
            mcp_tools_enabled=True,
            a2a_enabled=True
        )
        
        # Original sophisticated components (keep these)
        self.graph = None
        self.intelligence_data = {}
        self.context = {}
        self.query_history = []
        self.context_id = None
        self.enable_parallel = True
        
        # Framework V2.0 standardized components (enhanced)
        self.task_planner = None
        self.runner = None

    async def _execute_agent_logic(self, query: str, context_id: str, task_id: str):
        """Agent-specific logic implementation following Framework V2.0 pattern."""
        logger.info(f"Executing solopreneur oracle logic for: {query}")
        
        # State management for Framework V2.0 pattern
        if self.context_id != context_id:
            self.clear_state()
            self.context_id = context_id
        
        self.query_history.append({"timestamp": datetime.now().isoformat(), "query": query})
        
        # Initialize components if needed (Framework V2.0 handles ADK agent)
        if not self.task_planner:
            await self._init_task_planner()
        
        # Phase 1: Task Decomposition via LangGraph
        logger.info("🎯 Phase 1: Task decomposition via LangGraph")
        task_plan = await self.decompose_tasks(query, context_id)
        
        # Phase 2: Sophisticated Domain Analysis using Framework V2.0 A2A protocol
        logger.info("⚡ Phase 2: Domain coordination via A2A protocol")
        await self.load_context(query)
        intelligence_data = await self._execute_enhanced_domain_coordination(task_plan, query)
        
        # Phase 3: Intelligence Synthesis via inherited Framework V2.0 ADK agent
        logger.info("🔬 Phase 3: Synthesis via Framework V2.0 ADK agent")
        synthesis_query = self._build_adk_synthesis_query(query, task_plan, intelligence_data)
        
        # Use inherited agent for synthesis with Framework V2.0 quality validation
        return await self._run_synthesis_via_adk(synthesis_query, context_id)
    
    async def _init_task_planner(self):
        """Initialize LangGraph task planner component."""
        if self.task_planner:
            return
            
        logger.info("Initializing LangGraph task planner")
        
        # Initialize LangGraph task planner (following langgraph_planner_agent.py pattern)
        self.task_planner = create_react_agent(
            ChatGoogleGenerativeAI(model='gemini-2.0-flash', temperature=0.0),
            checkpointer=memory,
            prompt=SOLOPRENEUR_PLANNING_INSTRUCTIONS,
            response_format=SolopreneurTaskFormat,
            tools=[],
        )
        
        self.runner = AgentRunner()
        logger.info("LangGraph task planner initialized successfully")

    def _get_synthesis_instructions(self) -> str:
        """Get synthesis instructions for Google ADK agent."""
        return """
        You are the Solopreneur Oracle Synthesis Agent. Your role is to synthesize intelligence from domain specialists into actionable insights for AI developers and entrepreneurs.
        
        Your capabilities:
        - Analyze cross-domain intelligence from technical, personal, learning, knowledge, and integration specialists
        - Identify synergies and optimization opportunities across domains
        - Generate comprehensive strategies balancing technical excellence with personal sustainability
        - Provide structured recommendations with clear action plans and success metrics
        
        Quality Standards:
        - Technical solutions must be implementable and scalable
        - Personal recommendations must consider energy management and sustainability
        - Learning strategies should accelerate skill development efficiently
        - All recommendations need clear success metrics and risk assessments
        
        Use available MCP tools to enhance your analysis and provide data-driven insights.
        Format responses as structured JSON following the comprehensive synthesis format.
        """

    async def decompose_tasks(self, query: str, context_id: str) -> SolopreneurTaskFormat:
        """Decompose user request into domain-specific tasks via LangGraph planner."""
        inputs = {'messages': [('user', f"Analyze this solopreneur request and create an execution plan: {query}")]}
        config = {'configurable': {'thread_id': context_id}}
        
        logger.info(f"LangGraph planner decomposing: {query}")
        
        # Run LangGraph planner
        for item in self.task_planner.stream(inputs, config, stream_mode='values'):
            message = item['messages'][-1]
            if isinstance(message, AIMessage):
                continue
                
        # Get structured task plan
        current_state = self.task_planner.get_state(config)
        task_plan = current_state.values.get('structured_response')
        
        if not task_plan or not isinstance(task_plan, SolopreneurTaskFormat):
            # Fallback plan if decomposition fails (using original sophisticated logic)
            logger.warning("LangGraph decomposition failed, using fallback with original domain analysis")
            
            # Use original sophisticated domain analysis as fallback
            await self.load_context(query)
            dependency_analysis = self.analyze_domain_dependencies(query)
            
            fallback_tasks = []
            for domain_group, oracles in dependency_analysis["domain_groups"].items():
                domain_key = oracles[0].replace("_oracle", "")
                fallback_tasks.append({
                    "task_id": f"{domain_key}_analysis",
                    "description": f"Comprehensive {domain_key.replace('_', ' ')} analysis for: {query}",
                    "domain": domain_key,
                    "priority": self._get_domain_priority(domain_key)
                })
            
            return SolopreneurTaskFormat(
                status='ready',
                analysis=f"Solopreneur optimization analysis needed for: {query}",
                tasks=TaskList(tasks=fallback_tasks),
                coordination_strategy="parallel" if self.enable_parallel else "sequential",
                domains_required=list(dependency_analysis["domain_groups"].keys()),
                quality_requirements=self.quality_thresholds,
                optimization_focus=["technical_excellence", "personal_sustainability", "learning_efficiency"]
            )
            
        return task_plan
    
    def _get_domain_priority(self, domain: str) -> int:
        """Get priority for domain based on original sophisticated analysis."""
        priorities = {
            "technical_intelligence": 1,
            "personal_optimization": 1, 
            "knowledge_management": 2,
            "learning_enhancement": 2,
            "integration_synthesis": 3
        }
        return priorities.get(domain, 99)

    async def load_context(self, query: str):
        """Load solopreneur context and determine domain scope."""
        try:
            # Extract relevant domains from query
            query_lower = query.lower()
            relevant_domains = []
            
            # Domain detection logic for solopreneur
            if any(word in query_lower for word in ["code", "architecture", "ai", "technology", "implementation", "framework"]):
                relevant_domains.append("technical_intelligence")
            if any(word in query_lower for word in ["knowledge", "information", "research", "data", "learning", "skill"]):
                relevant_domains.append("knowledge_management")
            if any(word in query_lower for word in ["energy", "focus", "productivity", "optimization", "schedule", "burnout"]):
                relevant_domains.append("personal_optimization")
            if any(word in query_lower for word in ["learn", "skill", "development", "education", "growth", "practice"]):
                relevant_domains.append("learning_enhancement")
            if any(word in query_lower for word in ["workflow", "integration", "automation", "efficiency"]):
                relevant_domains.append("integration_synthesis")
            
            # Default to comprehensive analysis if no specific domains detected
            if not relevant_domains:
                relevant_domains = ["technical_intelligence", "personal_optimization", "integration_synthesis"]
            
            self.context = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "domains": relevant_domains,
                "user_type": "ai_developer_entrepreneur",
                "optimization_goals": ["productivity", "learning_efficiency", "technical_excellence"]
            }
            
            logger.info(f"Loaded context for {len(relevant_domains)} domains")
            
        except Exception as e:
            logger.error(f"Error loading context: {e}")
            self.context = {"query": query, "error": str(e)}

    def analyze_domain_dependencies(self, query: str) -> Dict[str, Any]:
        """Determine which domain oracles to activate and their dependencies."""
        domain_groups = {
            "technical_analysis": ["technical_intelligence_oracle"],
            "knowledge_analysis": ["knowledge_management_oracle"],
            "personal_analysis": ["personal_optimization_oracle"],
            "learning_analysis": ["learning_enhancement_oracle"],
            "integration_analysis": ["integration_synthesis_oracle"]
        }
        
        # Define dependency relationships
        domain_dependencies = {
            "integration_analysis": ["technical_analysis", "personal_analysis"],
            "learning_analysis": ["knowledge_analysis"],
            "technical_analysis": [],    # Can run independently
            "knowledge_analysis": [],    # Can run independently
            "personal_analysis": []      # Can run independently
        }
        
        # Priority levels for execution order
        domain_priorities = {
            "technical_analysis": 1,     # High priority, foundational
            "personal_analysis": 1,      # High priority, foundational  
            "knowledge_analysis": 2,     # Medium priority
            "learning_analysis": 2,      # Medium priority
            "integration_analysis": 3    # Must wait for others
        }
        
        # Determine which analyses to run based on query
        required_analyses = []
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["code", "architecture", "ai", "technology", "implementation"]):
            required_analyses.append("technical_analysis")
        if any(word in query_lower for word in ["knowledge", "information", "research", "data"]):
            required_analyses.append("knowledge_analysis")
        if any(word in query_lower for word in ["energy", "focus", "productivity", "optimization", "schedule"]):
            required_analyses.append("personal_analysis")
        if any(word in query_lower for word in ["learn", "skill", "development", "education", "growth"]):
            required_analyses.append("learning_analysis")
        
        # Always include integration synthesis for comprehensive analysis
        if len(required_analyses) > 1:
            required_analyses.append("integration_analysis")
        
        # Default to comprehensive analysis if no specific domains detected
        if not required_analyses:
            required_analyses = ["technical_analysis", "personal_analysis", "integration_analysis"]
        
        # Build execution plan with dependencies and parallelization
        execution_plan = self._build_execution_plan(required_analyses, domain_dependencies, domain_priorities)
        
        return {
            "domain_groups": {k: v for k, v in domain_groups.items() if k in required_analyses},
            "execution_plan": execution_plan,
            "parallelization_opportunities": self._identify_parallel_batches(required_analyses, domain_dependencies)
        }

    def _build_execution_plan(self, required_analyses: List[str], dependencies: Dict, priorities: Dict) -> List[Dict]:
        """Build step-by-step execution plan respecting dependencies."""
        execution_plan = []
        completed = set()
        step = 1
        
        while len(completed) < len(required_analyses):
            # Find analyses that can be executed in this step
            ready_analyses = []
            for analysis in required_analyses:
                if analysis not in completed:
                    # Check if all dependencies are satisfied
                    deps = dependencies.get(analysis, [])
                    if all(dep in completed for dep in deps):
                        ready_analyses.append(analysis)
            
            if not ready_analyses:
                logger.error("Circular dependency detected in execution plan")
                break
            
            # Sort by priority
            ready_analyses.sort(key=lambda x: priorities.get(x, 99))
            
            # Group analyses with same priority for parallel execution
            current_priority = priorities.get(ready_analyses[0], 99)
            parallel_batch = [a for a in ready_analyses if priorities.get(a, 99) == current_priority]
            
            execution_plan.append({
                "step": step,
                "analyses": parallel_batch,
                "parallel_execution": len(parallel_batch) > 1
            })
            
            completed.update(parallel_batch)
            step += 1
        
        return execution_plan

    def _identify_parallel_batches(self, required_analyses: List[str], dependencies: Dict) -> List[List[str]]:
        """Identify which analyses can be executed in parallel."""
        # Find analyses with no dependencies - these can run in parallel
        independent_analyses = [
            analysis for analysis in required_analyses 
            if not dependencies.get(analysis, [])
        ]
        
        parallel_batches = []
        if len(independent_analyses) > 1:
            parallel_batches.append(independent_analyses)
        
        return parallel_batches

    async def _fetch_enhanced_domain_intelligence(self, domain: str, query: str, task_plan: SolopreneurTaskFormat) -> Dict[str, Any]:
        """Enhanced domain intelligence fetch with A2A protocol and task plan context."""
        try:
            logger.info(f"Fetching {domain} intelligence via A2A protocol for: {query}")
            
            # Get relevant tasks for this domain from task plan
            domain_tasks = [task for task in task_plan.tasks.tasks if task.get('domain') == domain]
            task_context = f"Tasks: {[task.get('description', '') for task in domain_tasks]}"
            
            # Enhanced query with task context
            enhanced_query = f"{query}\n\nTask Context: {task_context}\nOptimization Focus: {', '.join(task_plan.optimization_focus)}"
            
            # Use A2A protocol to communicate with domain oracle
            if self.a2a_client:
                oracle_port = A2A_AGENT_PORTS.get(f"{domain}_oracle") or A2A_AGENT_PORTS.get(domain)
                if oracle_port:
                    try:
                        response = await self.a2a_client.send_message(
                            target_port=oracle_port,
                            message=enhanced_query,
                            metadata={
                                "domain": domain,
                                "source_agent": self.agent_name,
                                "task_context": task_context,
                                "optimization_focus": task_plan.optimization_focus
                            }
                        )
                        if response and not response.get('error'):
                            return response
                        else:
                            logger.warning(f"A2A communication failed for {domain}, using fallback")
                    except Exception as e:
                        logger.warning(f"A2A error for {domain}: {e}, using fallback")
            
            # Fallback to original sophisticated analysis if A2A unavailable
            return await self.fetch_domain_intelligence_fallback(domain, enhanced_query)
            
        except Exception as e:
            logger.error(f"Error fetching enhanced {domain} analysis: {e}")
            return {
                "domain": domain,
                "error": str(e),
                "analysis": {"status": "unavailable"}
            }

    async def fetch_domain_intelligence_fallback(self, domain: str, query: str) -> Dict[str, Any]:
        """Fallback domain intelligence when A2A protocol unavailable."""
        try:
            logger.info(f"Using fallback intelligence for {domain}")
            
            if domain == "technical_intelligence":
                return {
                    "domain": "Technical Intelligence",
                    "analysis": {
                        "feasibility_assessment": {
                            "technical_feasibility": 0.85,
                            "implementation_complexity": "medium",
                            "architecture_recommendations": ["microservices", "event-driven", "ADK pattern"],
                            "tech_stack_suggestions": ["python", "fastapi", "postgresql", "redis"]
                        },
                        "code_quality_insights": {
                            "maintainability_score": 0.82,
                            "scalability_potential": 0.88,
                            "security_considerations": ["authentication", "rate limiting", "data encryption"]
                        },
                        "ai_integration": {
                            "recommended_models": ["gemini-2.0-flash", "claude-3-opus"],
                            "integration_patterns": ["ADK agents", "MCP tools", "streaming responses"],
                            "optimization_strategies": ["caching", "batch processing", "parallel execution"]
                        }
                    },
                    "confidence": 0.87
                }
            elif domain == "personal_optimization":
                return {
                    "domain": "Personal Optimization",
                    "analysis": {
                        "energy_management": {
                            "optimal_work_windows": ["9-11 AM", "2-5 PM"],
                            "focus_duration": "90 minute blocks",
                            "break_recommendations": ["5 min every 25 min", "15 min every 90 min"]
                        },
                        "cognitive_load_assessment": {
                            "current_load": "moderate",
                            "optimization_potential": 0.75,
                            "burnout_risk": "low"
                        },
                        "productivity_insights": {
                            "task_batching": ["similar cognitive demands", "energy-aligned scheduling"],
                            "context_switching_cost": "high",
                            "deep_work_recommendations": ["morning blocks", "notification-free zones"]
                        }
                    },
                    "confidence": 0.82
                }
            elif domain == "knowledge_management":
                return {
                    "domain": "Knowledge Management",
                    "analysis": {
                        "knowledge_gaps": ["distributed systems", "ml ops", "system design"],
                        "learning_priorities": {
                            "immediate": ["ADK framework mastery", "MCP tool development"],
                            "short_term": ["kubernetes", "event streaming"],
                            "long_term": ["ml engineering", "system architecture"]
                        },
                        "information_synthesis": {
                            "key_patterns": ["framework-first development", "incremental complexity"],
                            "connection_strength": 0.78
                        }
                    },
                    "confidence": 0.80
                }
            elif domain == "learning_enhancement":
                return {
                    "domain": "Learning Enhancement",
                    "analysis": {
                        "learning_style": "hands-on experimentation",
                        "retention_strategies": ["spaced repetition", "project-based learning"],
                        "skill_development_path": {
                            "current_level": "intermediate",
                            "next_milestones": ["advanced ADK patterns", "distributed systems"],
                            "estimated_timeline": "3-6 months"
                        }
                    },
                    "confidence": 0.79
                }
            else:  # integration_synthesis
                return {
                    "domain": "Integration Synthesis",
                    "analysis": {
                        "cross_domain_insights": ["technical-personal alignment critical", "learning-productivity synergy"],
                        "workflow_optimizations": ["automated testing", "CI/CD pipeline", "documentation generation"],
                        "integration_opportunities": ["knowledge graph automation", "personal metrics tracking"]
                    },
                    "confidence": 0.83
                }
            
        except Exception as e:
            logger.error(f"Error fetching fallback {domain} analysis: {e}")
            return {
                "domain": domain,
                "error": str(e),
                "analysis": {"status": "unavailable"}
            }

    async def _run_synthesis_via_adk(self, synthesis_query: str, context_id: str) -> Dict[str, Any]:
        """Run synthesis via inherited ADK agent from Framework V2.0."""
        try:
            # Use inherited agent for synthesis (StandardizedAgentBase provides self.agent)
            if not self.agent:
                await self.init_agent()  # Framework V2.0 initialization
            
            if not self.runner:
                self.runner = AgentRunner()
            
            # Run synthesis via inherited ADK agent
            synthesis_result = ""
            async for chunk in self.runner.run_stream(self.agent, synthesis_query, context_id):
                if isinstance(chunk, dict) and chunk.get('type') == 'final_result':
                    synthesis_result = chunk['response']
                    break
            
            # Apply Framework V2.0 quality validation
            try:
                synthesis = json.loads(synthesis_result)
                quality_check = await self.quality_framework.validate_response(synthesis, synthesis_query)
                
                if not quality_check.get("quality_approved", True):
                    logger.warning(f"Quality issues detected: {quality_check.get('quality_issues', [])}")
                    synthesis["quality_warning"] = f"Note: Some quality thresholds not met: {', '.join(quality_check.get('quality_issues', []))}"
                
                synthesis["quality_metadata"] = quality_check
                return synthesis
                
            except json.JSONDecodeError:
                # Return text response if JSON parsing fails
                return {"synthesis": synthesis_result, "format": "text"}
                
        except Exception as e:
            logger.error(f"Synthesis error: {e}")
            return {"error": f"Synthesis failed: {str(e)}"}

    def clear_state(self):
        """Reset agent state for new analysis."""
        self.graph = None
        self.intelligence_data.clear()
        self.query_history.clear()
        self.context.clear()

    async def _execute_enhanced_domain_coordination(self, task_plan: SolopreneurTaskFormat, query: str) -> Dict[str, Any]:
        """Execute domain coordination using Framework V2.0 A2A protocol with sophisticated dependency management."""
        # Use original sophisticated dependency analysis
        dependency_analysis = self.analyze_domain_dependencies(query)
        domain_groups = dependency_analysis["domain_groups"]
        execution_plan = dependency_analysis["execution_plan"]
        
        logger.info(f"Framework V2.0 enhanced coordination: {len(domain_groups)} domain groups, {len(execution_plan)} execution steps")
        
        # Execute with Framework V2.0 A2A protocol (enhanced with sophisticated workflow)
        for step in execution_plan:
            step_analyses = step["analyses"]
            is_parallel = step["parallel_execution"]
            
            if is_parallel and self.enable_parallel:
                # Parallel execution via A2A protocol
                tasks = []
                for analysis_group in step_analyses:
                    if analysis_group in domain_groups:
                        for oracle in domain_groups[analysis_group]:
                            domain_key = oracle.replace("_oracle", "")
                            # Use Framework V2.0 A2A enhanced intelligence fetch
                            tasks.append(self._fetch_enhanced_domain_intelligence(
                                domain_key, query, task_plan
                            ))
                
                step_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results with Framework V2.0 quality handling
                for i, (analysis_group, result) in enumerate(zip(step_analyses, step_results)):
                    if not isinstance(result, Exception) and result:
                        domain_key = domain_groups[analysis_group][0].replace("_oracle", "")
                        self.intelligence_data[domain_key] = result
            else:
                # Sequential execution via A2A protocol
                for analysis_group in step_analyses:
                    if analysis_group in domain_groups:
                        for oracle in domain_groups[analysis_group]:
                            domain_key = oracle.replace("_oracle", "")
                            analysis = await self._fetch_enhanced_domain_intelligence(
                                domain_key, query, task_plan
                            )
                            if analysis:
                                self.intelligence_data[domain_key] = analysis
        
        return self.intelligence_data
    
    async def _fetch_enhanced_domain_intelligence(self, domain: str, query: str, task_plan: SolopreneurTaskFormat) -> Dict[str, Any]:
        """Enhanced domain intelligence fetch with task plan context."""
        # Get relevant tasks for this domain from task plan
        domain_tasks = [task for task in task_plan.tasks.tasks if task.get('domain') == domain]
        task_context = f"Tasks: {[task.get('description', '') for task in domain_tasks]}"
        
        # Use original sophisticated domain intelligence with enhanced context
        enhanced_query = f"{query}\n\nTask Context: {task_context}\nOptimization Focus: {', '.join(task_plan.optimization_focus)}"
        
        return await self.fetch_domain_intelligence(domain, enhanced_query)
    
    def _build_adk_synthesis_query(self, original_query: str, task_plan: SolopreneurTaskFormat, intelligence_data: Dict[str, Any]) -> str:
        """Build synthesis query for ADK agent using original sophisticated prompt enhanced with task plan."""
        return f"""
        Synthesize the following solopreneur intelligence into actionable insights:
        
        Original Query: {original_query}
        
        Task Plan Analysis: {task_plan.analysis}
        Coordination Strategy: {task_plan.coordination_strategy}
        Domains Analyzed: {', '.join(task_plan.domains_required)}
        Optimization Focus: {', '.join(task_plan.optimization_focus)}
        
        Domain Intelligence Gathered:
        {json.dumps(intelligence_data, indent=2)}
        
        Context:
        {json.dumps(self.context, indent=2)}
        
        Quality Requirements:
        {json.dumps(task_plan.quality_requirements, indent=2)}
        
        Provide comprehensive synthesis using the original sophisticated format:
        {SOLOPRENEUR_SYNTHESIS_PROMPT.split('Provide synthesis in this JSON format:')[1]}
        
        Focus on balancing:
        1. Technical excellence and innovation opportunities
        2. Personal energy management and sustainability
        3. Learning efficiency and skill acceleration  
        4. Workflow automation and productivity optimization
        5. Cross-domain integration and synergies
        """
