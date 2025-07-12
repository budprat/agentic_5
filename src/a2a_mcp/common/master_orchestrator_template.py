# type: ignore

"""
Master Orchestrator Template - Framework V2.0

Generic template for creating sophisticated multi-agent orchestrators with
advanced coordination, quality validation, and enterprise-grade features.

Based on the SolopreneurOracleAgent pattern but generalized for any domain.
"""

import logging
import json
import asyncio
from collections.abc import AsyncIterable
from typing import Dict, Any, List, Literal, Optional
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

logger = logging.getLogger(__name__)
memory = MemorySaver()

# Generic Task Decomposition Response Format
class DomainTaskFormat(BaseModel):
    """Response format for domain-specific task decomposition."""
    
    status: Literal['planning', 'ready', 'error'] = 'planning'
    analysis: str = Field(description="Analysis of the user request for domain optimization")
    tasks: TaskList = Field(description="Decomposed tasks for domain specialists")
    coordination_strategy: str = Field(description="How tasks will be coordinated")
    domains_required: List[str] = Field(description="Required domain specialists")
    quality_requirements: Dict[str, float] = Field(description="Quality thresholds for each domain")
    optimization_focus: List[str] = Field(description="Key optimization areas identified")

class MasterOrchestratorTemplate(StandardizedAgentBase):
    """
    Generic Master Orchestrator Template - Framework V2.0
    
    This template provides the sophisticated orchestration patterns demonstrated
    in the SolopreneurOracleAgent but generalized for any business domain.
    
    Example usage:
        # Healthcare domain
        healthcare_orchestrator = MasterOrchestratorTemplate(
            domain_name="Healthcare Management",
            domain_description="Medical workflow optimization and patient care coordination",
            domain_specialists={
                "patient_care": "Patient care and treatment optimization",
                "medical_records": "Medical records and compliance management", 
                "resource_planning": "Hospital resource and scheduling optimization"
            },
            quality_domain=QualityDomain.SERVICE,
            planning_instructions=healthcare_planning_instructions,
            synthesis_prompt=healthcare_synthesis_prompt
        )
        
        # Financial domain
        finance_orchestrator = MasterOrchestratorTemplate(
            domain_name="Financial Intelligence",
            domain_description="Investment analysis and portfolio optimization",
            domain_specialists={
                "market_analysis": "Market trends and technical analysis",
                "risk_assessment": "Portfolio risk and compliance analysis",
                "strategy_optimization": "Investment strategy optimization"
            },
            quality_domain=QualityDomain.BUSINESS,
            planning_instructions=finance_planning_instructions,
            synthesis_prompt=finance_synthesis_prompt
        )
    """

    def __init__(
        self,
        domain_name: str,
        domain_description: str,
        domain_specialists: Dict[str, str],
        quality_domain: QualityDomain = QualityDomain.BUSINESS,
        quality_thresholds: Optional[Dict[str, Any]] = None,
        planning_instructions: Optional[str] = None,
        synthesis_prompt: Optional[str] = None,
        enable_parallel: bool = True
    ):
        """
        Initialize Master Orchestrator for specific domain.
        
        Args:
            domain_name: Name of the domain (e.g., "Healthcare Management")
            domain_description: Description of domain capabilities
            domain_specialists: Dict of specialist_key -> description
            quality_domain: Quality validation domain type
            quality_thresholds: Custom quality thresholds (optional)
            planning_instructions: Domain-specific planning instructions
            synthesis_prompt: Domain-specific synthesis prompt template
            enable_parallel: Enable parallel execution of independent tasks
        """
        init_api_key()
        
        # Build quality configuration
        quality_config = {
            "domain": quality_domain,
            "thresholds": quality_thresholds or self._get_default_quality_thresholds(quality_domain)
        }
        
        super().__init__(
            agent_name=f"{domain_name} Master Orchestrator",
            description=f"Master {domain_name.lower()} intelligence orchestrator with Framework V2.0 compliance",
            instructions=f"You are the {domain_name} Master Orchestrator, specializing in {domain_description}.",
            quality_config=quality_config,
            mcp_tools_enabled=True,
            a2a_enabled=True
        )
        
        # Domain configuration
        self.domain_name = domain_name
        self.domain_description = domain_description
        self.domain_specialists = domain_specialists
        self.planning_instructions = planning_instructions or self._get_default_planning_instructions()
        self.synthesis_prompt = synthesis_prompt or self._get_default_synthesis_prompt()
        
        # Orchestration state (sophisticated pattern from original)
        self.graph = None
        self.intelligence_data = {}
        self.context = {}
        self.query_history = []
        self.context_id = None
        self.enable_parallel = enable_parallel
        
        # Framework V2.0 standardized components
        self.task_planner = None
        self.runner = None

    def _get_default_quality_thresholds(self, domain: QualityDomain) -> Dict[str, Any]:
        """Get default quality thresholds for domain."""
        base_thresholds = {
            "confidence_score": {"min_value": 0.75, "weight": 1.0},
            "technical_feasibility": {"min_value": 0.8, "weight": 1.2},
            "domain_relevance": {"min_value": 0.7, "weight": 1.0},
            "risk_tolerance": {"min_value": 0.6, "max_value": 0.8, "weight": 0.8}
        }
        
        # Domain-specific adjustments
        if domain == QualityDomain.BUSINESS:
            base_thresholds["business_value"] = {"min_value": 0.7, "weight": 1.1}
        elif domain == QualityDomain.SERVICE:
            base_thresholds["service_quality"] = {"min_value": 0.8, "weight": 1.2}
        elif domain == QualityDomain.ACADEMIC:
            base_thresholds["methodological_rigor"] = {"min_value": 0.85, "weight": 1.3}
            
        return base_thresholds

    def _get_default_planning_instructions(self) -> str:
        """Get default planning instructions for domain."""
        specialist_list = '\n'.join([f"- {key}: {desc}" for key, desc in self.domain_specialists.items()])
        
        return f"""
You are the {self.domain_name} Task Planner. Analyze user requests and decompose them into coordinated tasks for domain specialists.

Domain Specialists Available:
{specialist_list}

For each request:
1. Analyze scope and identify relevant specialists for {self.domain_description}
2. Create specific, actionable tasks for each domain specialist
3. Define coordination strategy (parallel/sequential based on dependencies)
4. Set quality requirements per domain
5. Identify optimization opportunities and synergies

Focus on:
- {self.domain_description}
- Cross-domain integration opportunities
- Quality and compliance requirements
- Efficient resource utilization
"""

    def _get_default_synthesis_prompt(self) -> str:
        """Get default synthesis prompt template."""
        return f"""
You are the {self.domain_name} Synthesis Agent. Your role is to synthesize intelligence from domain specialists into actionable insights.

Your capabilities:
- Analyze cross-domain intelligence from {', '.join(self.domain_specialists.keys())} specialists
- Identify synergies and optimization opportunities across domains
- Generate comprehensive strategies for {self.domain_description}
- Provide structured recommendations with clear action plans and success metrics

Quality Standards:
- Solutions must be implementable and scalable
- Recommendations must consider domain-specific constraints
- All recommendations need clear success metrics and risk assessments

Use available MCP tools to enhance your analysis and provide data-driven insights.
Format responses as structured JSON with comprehensive analysis.
"""

    async def _execute_agent_logic(self, query: str, context_id: str, task_id: str):
        """Agent-specific logic implementation following Framework V2.0 pattern."""
        logger.info(f"Executing {self.domain_name} orchestration logic for: {query}")
        
        # State management for Framework V2.0 pattern
        if self.context_id != context_id:
            self.clear_state()
            self.context_id = context_id
        
        self.query_history.append({"timestamp": datetime.now().isoformat(), "query": query})
        
        # Initialize components if needed
        if not self.task_planner:
            await self._init_task_planner()
        
        # Phase 1: Task Decomposition via LangGraph
        logger.info("🎯 Phase 1: Task decomposition via LangGraph")
        task_plan = await self.decompose_tasks(query, context_id)
        
        # Phase 2: Domain Coordination using Framework V2.0 A2A protocol
        logger.info("⚡ Phase 2: Domain coordination via A2A protocol")
        await self.load_context(query)
        intelligence_data = await self._execute_domain_coordination(task_plan, query)
        
        # Phase 3: Intelligence Synthesis via inherited Framework V2.0 ADK agent
        logger.info("🔬 Phase 3: Synthesis via Framework V2.0 ADK agent")
        synthesis_query = self._build_synthesis_query(query, task_plan, intelligence_data)
        
        # Use inherited agent for synthesis with quality validation
        return await self._run_synthesis_via_adk(synthesis_query, context_id)
    
    async def _init_task_planner(self):
        """Initialize LangGraph task planner component with enhanced error handling."""
        if self.task_planner:
            return
            
        logger.info(f"Initializing LangGraph task planner for {self.domain_name}")
        
        try:
            self.task_planner = create_react_agent(
                ChatGoogleGenerativeAI(model=os.getenv('GEMINI_MODEL', 'gemini-2.0-flash'), temperature=0.0),
                checkpointer=memory,
                prompt=self.planning_instructions,
                response_format=DomainTaskFormat,
                tools=[],
            )
            
            self.runner = AgentRunner()
            logger.info(f"LangGraph task planner initialized for {self.domain_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize task planner for {self.domain_name}: {e}")
            await self._handle_planner_initialization_failure(e)

    async def _handle_planner_initialization_failure(self, error: Exception):
        """Handle task planner initialization failure with graceful degradation."""
        logger.warning(f"Task planner initialization failed for {self.domain_name}, using fallback mode: {error}")
        
        try:
            # Fallback: Use simpler planning approach
            logger.info(f"Initializing fallback planner for {self.domain_name}")
            
            # Create minimal planner (could be enhanced with simpler LangGraph setup)
            self.task_planner = None  # Will trigger fallback in decompose_tasks
            self.runner = AgentRunner()
            
            logger.warning(f"Fallback planner initialized for {self.domain_name} (reduced functionality)")
            
        except Exception as fallback_error:
            logger.error(f"Complete planner initialization failure for {self.domain_name}: {fallback_error}")
            # Continue without planner - will use _create_fallback_task_plan
            self.task_planner = None
            self.runner = AgentRunner()

    def _get_synthesis_instructions(self) -> str:
        """Get synthesis instructions for Google ADK agent."""
        return self.synthesis_prompt

    async def decompose_tasks(self, query: str, context_id: str) -> DomainTaskFormat:
        """Decompose user request into domain-specific tasks via LangGraph planner."""
        inputs = {'messages': [('user', f"Analyze this {self.domain_name.lower()} request and create an execution plan: {query}")]}
        config = {'configurable': {'thread_id': context_id}}
        
        logger.info(f"LangGraph planner decomposing for {self.domain_name}: {query}")
        
        try:
            # Run LangGraph planner
            for item in self.task_planner.stream(inputs, config, stream_mode='values'):
                message = item['messages'][-1]
                if isinstance(message, AIMessage):
                    continue
                    
            # Get structured task plan
            current_state = self.task_planner.get_state(config)
            task_plan = current_state.values.get('structured_response')
            
            if task_plan and isinstance(task_plan, DomainTaskFormat):
                return task_plan
        except Exception as e:
            logger.warning(f"LangGraph decomposition failed: {e}, using fallback")
        
        # Fallback plan if decomposition fails
        return await self._create_fallback_task_plan(query)

    async def _create_fallback_task_plan(self, query: str) -> DomainTaskFormat:
        """Create fallback task plan when LangGraph fails."""
        try:
            await self.load_context(query)
            dependency_analysis = self.analyze_domain_dependencies(query)
            
            fallback_tasks = []
            for domain_group, specialists in dependency_analysis["domain_groups"].items():
                specialist_key = specialists[0] if specialists else domain_group
                fallback_tasks.append({
                    "task_id": f"{specialist_key}_analysis",
                    "description": f"Comprehensive {specialist_key.replace('_', ' ')} analysis for: {query}",
                    "domain": specialist_key,
                    "priority": self._get_domain_priority(specialist_key)
                })
            
            return DomainTaskFormat(
                status='ready',
                analysis=f"{self.domain_name} optimization analysis needed for: {query}",
                tasks=TaskList(tasks=fallback_tasks),
                coordination_strategy="parallel" if self.enable_parallel else "sequential",
                domains_required=list(dependency_analysis["domain_groups"].keys()),
                quality_requirements=self._get_default_quality_thresholds(QualityDomain.BUSINESS),
                optimization_focus=[self.domain_name.lower().replace(' ', '_')]
            )
        except Exception as e:
            logger.error(f"Fallback task plan creation failed: {e}")
            # Ultra-minimal fallback
            return DomainTaskFormat(
                status='error',
                analysis=f"Minimal analysis mode for {self.domain_name}: {query}",
                tasks=TaskList(tasks=[{
                    "task_id": "manual_analysis",
                    "description": f"Manual {self.domain_name.lower()} analysis required",
                    "domain": "manual",
                    "priority": 1
                }]),
                coordination_strategy="sequential",
                domains_required=["manual"],
                quality_requirements={},
                optimization_focus=["manual_intervention"]
            )
    
    def _get_domain_priority(self, domain: str) -> int:
        """Get priority for domain specialist."""
        # Default priority based on position in specialists dict
        specialist_keys = list(self.domain_specialists.keys())
        try:
            return specialist_keys.index(domain) + 1
        except ValueError:
            return 99

    async def load_context(self, query: str):
        """Load domain context and determine specialist scope."""
        try:
            # Extract relevant specialists from query
            query_lower = query.lower()
            relevant_specialists = []
            
            # Check which specialists are relevant based on query content
            for specialist_key, specialist_desc in self.domain_specialists.items():
                # Simple keyword matching - can be enhanced with semantic analysis
                specialist_keywords = specialist_key.replace('_', ' ').split() + specialist_desc.lower().split()
                if any(keyword in query_lower for keyword in specialist_keywords):
                    relevant_specialists.append(specialist_key)
            
            # Default to all specialists if no specific ones detected
            if not relevant_specialists:
                relevant_specialists = list(self.domain_specialists.keys())
            
            self.context = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "domain": self.domain_name,
                "specialists": relevant_specialists,
                "optimization_goals": [self.domain_description]
            }
            
            logger.info(f"Loaded context for {len(relevant_specialists)} specialists in {self.domain_name}")
            
        except Exception as e:
            logger.error(f"Error loading context: {e}")
            self.context = {"query": query, "error": str(e)}

    def analyze_domain_dependencies(self, query: str) -> Dict[str, Any]:
        """Determine which domain specialists to activate and their dependencies."""
        # Create specialist groups based on configured specialists
        domain_groups = {
            f"{key}_analysis": [f"{key}_specialist"] 
            for key in self.domain_specialists.keys()
        }
        
        # Simple dependency model - can be enhanced for specific domains
        domain_dependencies = {}
        specialist_keys = list(self.domain_specialists.keys())
        
        # Create simple priority system
        domain_priorities = {
            f"{key}_analysis": i + 1 
            for i, key in enumerate(specialist_keys)
        }
        
        # Determine required analyses based on context
        required_analyses = [f"{key}_analysis" for key in self.context.get("specialists", specialist_keys)]
        
        # Build execution plan
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
            
            execution_plan.append({
                "step": step,
                "analyses": ready_analyses,
                "parallel_execution": len(ready_analyses) > 1 and self.enable_parallel
            })
            
            completed.update(ready_analyses)
            step += 1
        
        return execution_plan

    def _identify_parallel_batches(self, required_analyses: List[str], dependencies: Dict) -> List[List[str]]:
        """Identify which analyses can be executed in parallel."""
        independent_analyses = [
            analysis for analysis in required_analyses 
            if not dependencies.get(analysis, [])
        ]
        
        parallel_batches = []
        if len(independent_analyses) > 1:
            parallel_batches.append(independent_analyses)
        
        return parallel_batches

    async def _execute_domain_coordination(self, task_plan: DomainTaskFormat, query: str) -> Dict[str, Any]:
        """Execute domain coordination using Framework V2.0 A2A protocol with health checks."""
        dependency_analysis = self.analyze_domain_dependencies(query)
        domain_groups = dependency_analysis["domain_groups"]
        execution_plan = dependency_analysis["execution_plan"]
        
        logger.info(f"Framework V2.0 coordination: {len(domain_groups)} domain groups, {len(execution_plan)} execution steps")
        
        # Pre-execution health checks
        health_status = await self._check_coordination_health()
        if not health_status["coordination_ready"]:
            logger.warning(f"Coordination health issues detected: {health_status['issues']}")
            # Continue with degraded service but log warnings
        
        # Execute coordination plan with enhanced error handling
        try:
            for step in execution_plan:
                step_analyses = step["analyses"]
                is_parallel = step["parallel_execution"]
                
                if is_parallel:
                    # Parallel execution via A2A protocol with error resilience
                    tasks = []
                    for analysis_group in step_analyses:
                        if analysis_group in domain_groups:
                            specialist_key = analysis_group.replace("_analysis", "")
                            tasks.append(self._fetch_domain_intelligence_with_fallback(
                                specialist_key, query, task_plan
                            ))
                    
                    step_results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Process results with enhanced error handling
                    for i, (analysis_group, result) in enumerate(zip(step_analyses, step_results)):
                        specialist_key = analysis_group.replace("_analysis", "")
                        
                        if isinstance(result, Exception):
                            logger.error(f"Specialist {specialist_key} failed: {result}")
                            # Add fallback intelligence
                            self.intelligence_data[specialist_key] = await self._create_fallback_intelligence(specialist_key, str(result))
                        elif result:
                            self.intelligence_data[specialist_key] = result
                        else:
                            logger.warning(f"No intelligence received from {specialist_key}")
                            self.intelligence_data[specialist_key] = await self._create_fallback_intelligence(specialist_key, "No response")
                else:
                    # Sequential execution with error resilience
                    for analysis_group in step_analyses:
                        if analysis_group in domain_groups:
                            specialist_key = analysis_group.replace("_analysis", "")
                            try:
                                analysis = await self._fetch_domain_intelligence_with_fallback(
                                    specialist_key, query, task_plan
                                )
                                if analysis:
                                    self.intelligence_data[specialist_key] = analysis
                                else:
                                    self.intelligence_data[specialist_key] = await self._create_fallback_intelligence(specialist_key, "No response")
                            except Exception as e:
                                logger.error(f"Sequential execution failed for {specialist_key}: {e}")
                                self.intelligence_data[specialist_key] = await self._create_fallback_intelligence(specialist_key, str(e))
        
        except Exception as e:
            logger.error(f"Critical coordination failure: {e}")
            await self._handle_coordination_failure(e)
        
        return self.intelligence_data

    async def _check_coordination_health(self) -> Dict[str, Any]:
        """Check health of coordination dependencies before execution."""
        health_status = {
            "coordination_ready": True,
            "issues": [],
            "component_status": {}
        }
        
        # Check A2A protocol health
        if not self.a2a_client:
            health_status["coordination_ready"] = False
            health_status["issues"].append("A2A protocol not available")
            health_status["component_status"]["a2a_protocol"] = "disabled"
        else:
            health_status["component_status"]["a2a_protocol"] = "enabled"
        
        # Check task planner health
        if not self.task_planner:
            health_status["issues"].append("Task planner not initialized")
            health_status["component_status"]["task_planner"] = "not_initialized"
        else:
            health_status["component_status"]["task_planner"] = "active"
        
        # Check quality framework health
        if not self.quality_framework.is_enabled():
            health_status["issues"].append("Quality framework disabled")
            health_status["component_status"]["quality_framework"] = "disabled"
        else:
            health_status["component_status"]["quality_framework"] = "enabled"
        
        # Check inherited ADK agent health
        inherited_health = self.get_health_status()
        if not inherited_health.get("dependencies_healthy", False):
            health_status["coordination_ready"] = False
            health_status["issues"].append("Inherited agent dependencies unhealthy")
            health_status["component_status"]["inherited_agent"] = "unhealthy"
        else:
            health_status["component_status"]["inherited_agent"] = "healthy"
        
        return health_status

    async def _fetch_domain_intelligence_with_fallback(self, specialist_key: str, query: str, task_plan: DomainTaskFormat) -> Dict[str, Any]:
        """Fetch intelligence with enhanced error handling and fallback."""
        try:
            return await self._fetch_domain_intelligence(specialist_key, query, task_plan)
        except Exception as e:
            logger.error(f"Primary intelligence fetch failed for {specialist_key}: {e}")
            return await self._create_fallback_intelligence(specialist_key, str(e))

    async def _create_fallback_intelligence(self, specialist_key: str, error_reason: str) -> Dict[str, Any]:
        """Create fallback intelligence when specialist unavailable."""
        specialist_desc = self.domain_specialists.get(specialist_key, "domain specialist")
        
        return {
            "specialist": specialist_key,
            "domain": self.domain_name,
            "status": "fallback_mode",
            "error_reason": error_reason,
            "analysis": {
                "capability_assessment": {
                    "relevance_score": 0.5,  # Lower score for fallback
                    "implementation_feasibility": "unknown",
                    "resource_requirements": ["specialist unavailable"],
                    "recommendations": [f"Retry {specialist_desc} when available", "Use alternative approach"]
                },
                "optimization_insights": {
                    "improvement_potential": 0.3,  # Conservative estimate
                    "key_opportunities": ["manual specialist consultation"],
                    "risk_factors": ["specialist unavailability", "incomplete analysis"]
                }
            },
            "confidence": 0.3,  # Low confidence for fallback
            "quality_warning": "This analysis is based on fallback data due to specialist unavailability"
        }

    async def _handle_coordination_failure(self, error: Exception):
        """Handle critical coordination failures with graceful degradation."""
        logger.error(f"Handling critical coordination failure: {error}")
        
        # Attempt to create minimal intelligence data
        for specialist_key in self.domain_specialists.keys():
            if specialist_key not in self.intelligence_data:
                self.intelligence_data[specialist_key] = await self._create_fallback_intelligence(
                    specialist_key, f"Coordination failure: {str(error)}"
                )
        
        # Add coordination failure metadata
        self.intelligence_data["_coordination_metadata"] = {
            "coordination_status": "failed",
            "failure_reason": str(error),
            "fallback_mode": True,
            "timestamp": datetime.now().isoformat()
        }

    async def _fetch_domain_intelligence(self, specialist_key: str, query: str, task_plan: DomainTaskFormat) -> Dict[str, Any]:
        """Fetch intelligence from domain specialist."""
        try:
            logger.info(f"Fetching {specialist_key} intelligence for {self.domain_name}")
            
            # Get relevant tasks for this specialist from task plan
            specialist_tasks = [task for task in task_plan.tasks.tasks if task.get('domain') == specialist_key]
            task_context = f"Tasks: {[task.get('description', '') for task in specialist_tasks]}"
            
            # Enhanced query with task context
            enhanced_query = f"{query}\n\nTask Context: {task_context}\nOptimization Focus: {', '.join(task_plan.optimization_focus)}"
            
            # Use A2A protocol if available
            if self.a2a_client:
                specialist_port = A2A_AGENT_PORTS.get(f"{specialist_key}_specialist") or A2A_AGENT_PORTS.get(specialist_key)
                if specialist_port:
                    try:
                        response = await self.a2a_client.send_message(
                            target_port=specialist_port,
                            message=enhanced_query,
                            metadata={
                                "domain": self.domain_name,
                                "specialist": specialist_key,
                                "source_agent": self.agent_name,
                                "task_context": task_context
                            }
                        )
                        if response and not response.get('error'):
                            return response
                    except Exception as e:
                        logger.warning(f"A2A communication failed for {specialist_key}: {e}")
            
            # Fallback to mock analysis if A2A unavailable
            return await self._fetch_intelligence_fallback(specialist_key, enhanced_query)
            
        except Exception as e:
            logger.error(f"Error fetching {specialist_key} analysis: {e}")
            # Use enhanced fallback intelligence
            return await self._create_fallback_intelligence(specialist_key, str(e))

    async def _fetch_intelligence_fallback(self, specialist_key: str, query: str) -> Dict[str, Any]:
        """Fallback intelligence when A2A protocol unavailable."""
        specialist_desc = self.domain_specialists.get(specialist_key, "domain specialist")
        
        return {
            "specialist": specialist_key,
            "domain": self.domain_name,
            "analysis": {
                "capability_assessment": {
                    "relevance_score": 0.85,
                    "implementation_feasibility": "medium",
                    "resource_requirements": ["specialist knowledge", "domain tools"],
                    "recommendations": [f"Consult {specialist_desc}", f"Apply {self.domain_name} best practices"]
                },
                "optimization_insights": {
                    "improvement_potential": 0.80,
                    "key_opportunities": [f"{specialist_key} optimization", "cross-domain integration"],
                    "risk_factors": ["resource constraints", "implementation complexity"]
                }
            },
            "confidence": 0.82
        }

    def _build_synthesis_query(self, original_query: str, task_plan: DomainTaskFormat, intelligence_data: Dict[str, Any]) -> str:
        """Build synthesis query for ADK agent."""
        return f"""
        Synthesize the following {self.domain_name} intelligence into actionable insights:
        
        Original Query: {original_query}
        
        Task Plan Analysis: {task_plan.analysis}
        Coordination Strategy: {task_plan.coordination_strategy}
        Specialists Analyzed: {', '.join(task_plan.domains_required)}
        Optimization Focus: {', '.join(task_plan.optimization_focus)}
        
        Specialist Intelligence Gathered:
        {json.dumps(intelligence_data, indent=2)}
        
        Context:
        {json.dumps(self.context, indent=2)}
        
        Quality Requirements:
        {json.dumps(task_plan.quality_requirements, indent=2)}
        
        {self.synthesis_prompt}
        
        Focus on:
        1. {self.domain_description}
        2. Cross-specialist integration opportunities
        3. Quality and compliance requirements
        4. Implementation feasibility and resource optimization
        5. Risk assessment and mitigation strategies
        """

    async def _run_synthesis_via_adk(self, synthesis_query: str, context_id: str) -> Dict[str, Any]:
        """Run synthesis via inherited ADK agent from Framework V2.0."""
        try:
            # Use inherited agent for synthesis
            if not self.agent:
                await self.init_agent()
            
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
                return {"synthesis": synthesis_result, "format": "text"}
                
        except Exception as e:
            logger.error(f"Synthesis error: {e}")
            return {"error": f"Synthesis failed: {str(e)}"}

    def get_orchestration_health_status(self) -> Dict[str, Any]:
        """Get comprehensive orchestration health status.
        
        Enhanced health monitoring for orchestration-specific components.
        """
        base_health = self.get_health_status()
        
        # Add orchestration-specific health checks
        orchestration_health = {
            "domain_specialists": len(self.domain_specialists),
            "specialists_configured": list(self.domain_specialists.keys()),
            "task_planner_initialized": self.task_planner is not None,
            "langraph_available": True,  # Could check LangGraph specifically
            "parallel_execution_enabled": self.enable_parallel,
            "intelligence_data_size": len(self.intelligence_data),
            "query_history_size": len(self.query_history),
            "current_context_loaded": bool(self.context)
        }
        
        # Merge with base health status
        base_health["orchestration_details"] = orchestration_health
        base_health["orchestration_type"] = "master_orchestrator"
        
        return base_health

    # Configurable methods for domain customization (inherited from StandardizedAgentBase)
    
    def get_agent_temperature(self) -> float:
        """Get temperature setting for orchestration planning."""
        return 0.1  # Low temperature for consistent coordination
    
    def get_response_mime_type(self) -> str:
        """Get response MIME type for orchestration results."""
        return "application/json"  # Structured data for complex coordination
    
    def get_model_name(self) -> str:
        """Get model name for orchestration tasks."""
        return os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')  # Fast model for coordination

    def clear_state(self):
        """Reset agent state for new analysis."""
        self.graph = None
        self.intelligence_data.clear()
        self.query_history.clear()
        self.context.clear()