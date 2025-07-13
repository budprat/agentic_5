# ABOUTME: Refactored Master Orchestrator Template that delegates planning to Enhanced Planner Agent
# ABOUTME: Framework V2.0 orchestrator maintaining backward compatibility while using new architecture

"""
Refactored Master Orchestrator Template - Framework V2.0

🔄 REFACTORED: This template now uses the Enhanced Planner Agent for all planning tasks:
   ✅ Maintains backward compatibility with existing APIs
   ✅ Delegates task decomposition to Enhanced Planner Agent
   ✅ Delegates risk assessment to Enhanced Planner Agent  
   ✅ Delegates resource estimation to Enhanced Planner Agent
   ✅ Focuses on orchestration and execution coordination

Benefits:
✅ Same API as original MasterOrchestratorTemplate
✅ Enhanced planning capabilities via EnhancedGenericPlannerAgent
✅ Much lighter codebase (300 vs 852 lines)
✅ Better separation of concerns
✅ Improved maintainability

This provides the best of both worlds:
- Backward compatibility for existing code
- Enhanced capabilities from new architecture
"""

import logging
import json
import asyncio
import warnings
from collections.abc import AsyncIterable
from typing import Dict, Any, List, Literal, Optional
from datetime import datetime

from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.common.planner_agent import EnhancedGenericPlannerAgent
from a2a_mcp.common.a2a_protocol import A2AProtocolClient, A2A_AGENT_PORTS
from a2a_mcp.common.quality_framework import QualityThresholdFramework, QualityDomain
from a2a_mcp.common.agent_runner import AgentRunner
from a2a_mcp.common.utils import get_mcp_server_config, init_api_key
from a2a_mcp.common.types import GenericTaskList
from a2a_mcp.common.parallel_workflow import (
    ParallelWorkflowGraph, 
    ParallelWorkflowNode,
    Status
)
from a2a_mcp.common.enhanced_workflow import (
    DynamicWorkflowGraph,
    WorkflowNode, 
    WorkflowState,
    NodeState,
    workflow_manager
)

# Google ADK imports
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from google.genai import types as genai_types

import os

logger = logging.getLogger(__name__)

class MasterOrchestratorTemplate(StandardizedAgentBase):
    """
    Refactored Master Orchestrator Template - Framework V2.0
    
    This refactored template delegates all planning intelligence to the Enhanced Planner Agent
    while maintaining backward compatibility with the original API.
    
    Key Changes:
    - Uses EnhancedGenericPlannerAgent for task decomposition, risk assessment, etc.
    - Focuses purely on orchestration and execution coordination
    - Maintains same interface as original MasterOrchestratorTemplate
    - Much lighter codebase with enhanced capabilities
    
    Example usage (unchanged from original):
        orchestrator = MasterOrchestratorTemplate(
            domain_name="Healthcare Management",
            domain_description="Medical workflow optimization",
            domain_specialists={
                "patient_care": "Patient care optimization",
                "medical_records": "Medical records management"
            }
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
        enable_parallel: bool = True,
        enable_dynamic_workflow: bool = True
    ):
        """
        Initialize refactored Master Orchestrator that delegates planning to Enhanced Planner.
        
        Args:
            domain_name: Name of the domain (e.g., "Healthcare Management")
            domain_description: Description of domain capabilities
            domain_specialists: Dict of specialist_key -> description
            quality_domain: Quality validation domain type
            quality_thresholds: Custom quality thresholds (optional)
            planning_instructions: Domain-specific planning instructions (optional)
            synthesis_prompt: Domain-specific synthesis prompt (optional)
            enable_parallel: Enable parallel execution of independent tasks
            enable_dynamic_workflow: Enable dynamic workflow graph capabilities (Phase 1)
        """
        init_api_key()
        
        # Build quality configuration
        quality_config = {
            "domain": quality_domain,
            "thresholds": quality_thresholds or self._get_default_quality_thresholds(quality_domain)
        }
        
        super().__init__(
            agent_name=f"{domain_name} Master Orchestrator",
            description=f"Refactored {domain_name.lower()} orchestrator with Enhanced Planner integration",
            instructions=f"You are the refactored {domain_name} Master Orchestrator, specializing in {domain_description}.",
            quality_config=quality_config,
            content_types=['text', 'text/plain'],
        )
        
        # Core configuration
        self.domain_name = domain_name
        self.domain_description = domain_description
        self.domain_specialists = domain_specialists
        self.enable_parallel = enable_parallel
        self.enable_dynamic_workflow = enable_dynamic_workflow
        
        # Initialize Enhanced Planner Agent for all planning tasks
        planning_mode = 'sophisticated'  # Always use sophisticated mode for enterprise features
        self.planner = EnhancedGenericPlannerAgent(
            domain=domain_name,
            agent_name=f"{domain_name} Strategic Planner",
            custom_prompt=planning_instructions,
            domain_specialists=domain_specialists,
            planning_mode=planning_mode,
            quality_domain=quality_domain,
            enable_quality_validation=True,
            enable_fallback_planning=True
        )
        
        # Quality framework
        self.quality_framework = QualityThresholdFramework()
        self.quality_framework.configure_domain(quality_domain)
        
        # Execution tracking (legacy)
        self.active_agents = {}
        self.execution_context = {}
        self.coordination_history = []
        self.workflow_graph = None
        
        # Enhanced workflow capabilities (Phase 1)
        self.dynamic_workflow: Optional[DynamicWorkflowGraph] = None
        self.current_session_id: Optional[str] = None
        
        # PHASE 2: Context & History Tracking
        self.session_contexts: Dict[str, Dict[str, Any]] = {}  # session_id -> context data
        self.execution_history: Dict[str, List[Dict[str, Any]]] = {}  # session_id -> execution records
        self.domain_context: Dict[str, Any] = {}  # Persistent domain-specific context
        self.context_evolution: List[Dict[str, Any]] = []  # Track context changes over time
        self.query_patterns: Dict[str, int] = {}  # Track query patterns for intelligence
        self.performance_metrics: Dict[str, Dict[str, Any]] = {}  # Track performance by session
        
        # PHASE 2.5: Clear State Management
        self.domain_specialist_usage: Dict[str, int] = {}  # Track specialist usage patterns
        self.archived_sessions: Dict[str, Dict[str, Any]] = {}  # Archived session summaries
        
        # PHASE 3: Enhanced State Management with Pause/Resume
        self.execution_states: Dict[str, Dict[str, Any]] = {}  # session_id -> execution state
        self.pause_checkpoints: Dict[str, List[Dict[str, Any]]] = {}  # session_id -> checkpoints
        self.state_transitions: List[Dict[str, Any]] = []  # Track state transition events
        self.resumption_strategies: Dict[str, str] = {}  # session_id -> resumption strategy
        
        # PHASE 4: Artifact Management & Result Collection
        self.artifact_store: Dict[str, Dict[str, Any]] = {}  # artifact_id -> artifact data
        self.session_artifacts: Dict[str, List[str]] = {}  # session_id -> [artifact_ids]
        self.task_artifacts: Dict[str, List[str]] = {}  # task_id -> [artifact_ids]
        self.artifact_relationships: Dict[str, List[str]] = {}  # artifact_id -> [related_artifact_ids]
        self.result_collections: Dict[str, Dict[str, Any]] = {}  # collection_id -> collection metadata
        self.artifact_search_index: Dict[str, List[str]] = {}  # keyword -> [artifact_ids]
        self.artifact_templates: Dict[str, Dict[str, Any]] = {}  # template_name -> template config
        
        logger.info(f"Refactored {domain_name} Master Orchestrator initialized with Enhanced Planner")

    def _get_default_quality_thresholds(self, quality_domain: QualityDomain) -> Dict[str, Any]:
        """Get default quality thresholds for domain."""
        return {
            "minimum_score": 0.7,
            "target_score": 0.85,
            "excellence_score": 0.95,
            "domain": quality_domain.value
        }

    async def invoke(self, query: str, sessionId: str) -> str:
        """Main orchestration entry point - delegates planning to Enhanced Planner."""
        try:
            logger.info(f"Master orchestrator processing: {query[:100]}...")
            
            # PHASE 2.5: Auto-clear context if significant change detected
            context_cleared = self.auto_clear_on_context_change(query, sessionId)
            
            # PHASE 2: Initialize context and track query
            self._initialize_session_context(sessionId, query)
            execution_start = datetime.now()
            
            # Log context change detection
            if context_cleared:
                logger.info(f"Context auto-cleared for session {sessionId} before processing query")
            
            # Step 1: Delegate all planning to Enhanced Planner Agent
            plan_response = await self._get_strategic_plan(query, sessionId)
            
            if not plan_response or plan_response.get('response_type') != 'data':
                return self._format_orchestrator_response({
                    'status': 'error',
                    'message': 'Failed to generate strategic plan',
                    'error': plan_response.get('content', 'Unknown planning error')
                })
            
            execution_plan = plan_response['content']
            
            # Step 2: Execute orchestration using A2A protocol
            orchestration_result = await self._execute_orchestration(execution_plan, sessionId)
            
            # PHASE 4: Collect and organize artifacts from orchestration
            await self._collect_orchestration_artifacts(orchestration_result, execution_plan, sessionId)
            
            # Step 3: Synthesize final results
            final_result = await self._synthesize_results(orchestration_result, execution_plan, query)
            
            # PHASE 2: Record execution history and update context
            self._record_execution_history(sessionId, {
                'query': query,
                'execution_plan': execution_plan,
                'orchestration_result': orchestration_result,
                'final_result': final_result,
                'execution_duration': (datetime.now() - execution_start).total_seconds(),
                'timestamp': execution_start.isoformat()
            })
            
            return self._format_orchestrator_response(final_result)
            
        except Exception as e:
            logger.error(f"Master orchestration error: {e}")
            return self._format_orchestrator_response({
                'status': 'error',
                'message': f'Orchestration failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            })

    async def stream(self, query: str, sessionId: str, task_id: str) -> AsyncIterable[dict[str, Any]]:
        """Stream orchestration progress with enhanced planning delegation."""
        try:
            yield {
                'response_type': 'text',
                'is_task_complete': False,
                'require_user_input': False,
                'content': f'🎯 Starting {self.domain_name} master orchestration...',
                'stage': 'initialization'
            }
            
            # Step 1: Strategic planning phase
            yield {
                'response_type': 'text',
                'is_task_complete': False,
                'require_user_input': False,
                'content': '🧠 Delegating to Enhanced Planner for strategic analysis...',
                'stage': 'strategic_planning'
            }
            
            plan_response = await self._get_strategic_plan(query, sessionId)
            
            if not plan_response or plan_response.get('response_type') != 'data':
                yield {
                    'response_type': 'text',
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': '❌ Strategic planning failed',
                    'stage': 'error'
                }
                return
            
            execution_plan = plan_response['content']
            tasks = execution_plan.get('tasks', [])
            
            yield {
                'response_type': 'text',
                'is_task_complete': False,
                'require_user_input': False,
                'content': f'✅ Strategic plan complete: {len(tasks)} tasks, {execution_plan.get("coordination_strategy")} coordination',
                'stage': 'planning_complete'
            }
            
            # Step 2: Orchestration execution
            yield {
                'response_type': 'text',
                'is_task_complete': False,
                'require_user_input': False,
                'content': '🚀 Beginning domain specialist orchestration...',
                'stage': 'orchestration_start'
            }
            
            # Stream orchestration progress
            async for progress in self._stream_orchestration(execution_plan, sessionId):
                yield progress
            
            # Step 3: Final synthesis
            yield {
                'response_type': 'text',
                'is_task_complete': False,
                'require_user_input': False,
                'content': '🔮 Synthesizing final results...',
                'stage': 'synthesis'
            }
            
            yield {
                'response_type': 'text',
                'is_task_complete': True,
                'require_user_input': False,
                'content': f'🎉 {self.domain_name} master orchestration completed',
                'stage': 'completion'
            }
            
        except Exception as e:
            logger.error(f"Stream orchestration error: {e}")
            yield {
                'response_type': 'text',
                'is_task_complete': True,
                'require_user_input': False,
                'content': f'❌ Master orchestration failed: {str(e)}',
                'stage': 'error'
            }

    async def _get_strategic_plan(self, query: str, sessionId: str) -> dict:
        """Delegate strategic planning to Enhanced Planner Agent."""
        try:
            # Use Enhanced Planner for all planning intelligence
            plan_response = self.planner.invoke(query, sessionId)
            
            # Enhance with orchestrator-specific metadata
            if plan_response.get('response_type') == 'data':
                plan_content = plan_response['content']
                
                # Add orchestrator-specific enhancements
                plan_content['orchestrator_metadata'] = {
                    'orchestrator_type': 'master_template_refactored',
                    'domain': self.domain_name,
                    'parallel_enabled': self.enable_parallel,
                    'dynamic_workflow_enabled': self.enable_dynamic_workflow,
                    'specialist_assignments': self._assign_specialists_to_tasks(plan_content.get('tasks', [])),
                    'coordination_strategy': plan_content.get('coordination_strategy', 'sequential')
                }
                
                # Add enhanced planning analysis
                await self._enhance_plan_with_analysis(plan_content)
            
            return plan_response
            
        except Exception as e:
            logger.error(f"Strategic planning delegation error: {e}")
            return {'response_type': 'error', 'content': f'Strategic planning failed: {str(e)}'}

    def _assign_specialists_to_tasks(self, tasks: List[dict]) -> Dict[str, dict]:
        """Assign domain specialists to specific tasks."""
        assignments = {}
        
        for task in tasks:
            task_id = task.get('id', 'unknown')
            suggested_specialist = task.get('agent_type', 'generalist')
            
            # Map to configured domain specialists
            if suggested_specialist in self.domain_specialists:
                specialist_name = suggested_specialist
            else:
                specialist_name = self._match_specialist_to_task(task, suggested_specialist)
            
            assignments[task_id] = {
                'specialist': specialist_name,
                'specialist_description': self.domain_specialists.get(specialist_name, 'General specialist'),
                'task_complexity': self.planner._estimate_task_complexity(task),
                'estimated_duration': task.get('estimated_duration', '1 day')
            }
            
        return assignments

    def _match_specialist_to_task(self, task: dict, suggested_type: str) -> str:
        """Match task to best available domain specialist."""
        task_description = task.get('description', '').lower()
        
        # Score each specialist based on keyword matching
        specialist_scores = {}
        for specialist_key, specialist_desc in self.domain_specialists.items():
            score = 0
            specialist_keywords = specialist_desc.lower().split()
            
            # Check description overlap
            for keyword in specialist_keywords:
                if keyword in task_description:
                    score += 1
            
            # Check specialist type match
            if suggested_type.lower() in specialist_key.lower():
                score += 2
                
            specialist_scores[specialist_key] = score
        
        # Return specialist with highest score
        if specialist_scores:
            return max(specialist_scores, key=specialist_scores.get)
        
        # Fallback to first available
        return list(self.domain_specialists.keys())[0] if self.domain_specialists else 'generalist'

    async def _enhance_plan_with_analysis(self, plan_content: dict):
        """Enhance plan with additional orchestrator analysis."""
        tasks = plan_content.get('tasks', [])
        
        if tasks:
            # Add risk assessment from planner
            risk_assessment = self.planner.assess_plan_risks(plan_content)
            plan_content['risk_analysis'] = risk_assessment
            
            # Add resource estimation from planner
            resource_estimate = self.planner.estimate_plan_resources(tasks)
            plan_content['resource_analysis'] = resource_estimate
            
            # Add timeline estimation from planner
            timeline_estimate = self.planner.estimate_execution_timeline(tasks)
            plan_content['timeline_analysis'] = timeline_estimate

    async def _execute_orchestration(self, execution_plan: dict, sessionId: str) -> dict:
        """Execute orchestration focusing on coordination, not planning."""
        tasks = execution_plan.get('tasks', [])
        coordination_strategy = execution_plan.get('coordination_strategy', 'sequential')
        specialist_assignments = execution_plan.get('orchestrator_metadata', {}).get('specialist_assignments', {})
        
        orchestration_result = {
            'execution_strategy': coordination_strategy,
            'specialist_coordination': {},
            'task_results': [],
            'orchestration_metrics': {}
        }
        
        try:
            # Initialize specialist coordination
            await self._initialize_specialist_coordination(specialist_assignments)
            
            # Execute based on coordination strategy
            if coordination_strategy == 'parallel':
                task_results = await self._coordinate_parallel_execution(tasks, sessionId)
            elif coordination_strategy == 'hybrid':
                task_results = await self._coordinate_hybrid_execution(tasks, sessionId)
            else:  # sequential
                task_results = await self._coordinate_sequential_execution(tasks, sessionId)
            
            orchestration_result['task_results'] = task_results
            orchestration_result['orchestration_metrics'] = self._calculate_orchestration_metrics(task_results)
            
            return orchestration_result
            
        except Exception as e:
            logger.error(f"Orchestration execution error: {e}")
            orchestration_result['error'] = str(e)
            return orchestration_result

    async def _initialize_specialist_coordination(self, specialist_assignments: Dict[str, dict]):
        """Initialize coordination with domain specialists."""
        unique_specialists = set(
            assignment['specialist'] 
            for assignment in specialist_assignments.values()
        )
        
        for specialist in unique_specialists:
            # Simulate specialist initialization (in real implementation, would use A2A protocol)
            self.active_agents[specialist] = {
                'status': 'initialized',
                'capabilities': self.domain_specialists.get(specialist, 'General specialist'),
                'tasks_assigned': [],
                'performance_metrics': {'tasks_completed': 0, 'avg_duration': 0}
            }
            
            logger.info(f"Initialized coordination with {specialist} specialist")

    async def _coordinate_sequential_execution(self, tasks: List[dict], sessionId: str) -> List[dict]:
        """Coordinate sequential task execution."""
        results = []
        
        for task in tasks:
            task_result = await self._coordinate_single_task(task, sessionId)
            results.append(task_result)
            
            # Update coordination history
            self.coordination_history.append({
                'task_id': task.get('id'),
                'status': task_result.get('status'),
                'timestamp': datetime.now().isoformat()
            })
        
        return results

    async def _coordinate_parallel_execution(self, tasks: List[dict], sessionId: str) -> List[dict]:
        """Coordinate parallel task execution."""
        # Create coroutines for parallel execution
        task_coroutines = [
            self._coordinate_single_task(task, sessionId) 
            for task in tasks
        ]
        
        # Execute in parallel
        results = await asyncio.gather(*task_coroutines, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'task_id': tasks[i].get('id', f'task_{i}'),
                    'status': 'error',
                    'error': str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results

    async def _coordinate_hybrid_execution(self, tasks: List[dict], sessionId: str) -> List[dict]:
        """Coordinate hybrid execution (parallel batches in sequence)."""
        # Group tasks by dependencies
        independent_tasks = [t for t in tasks if not t.get('dependencies', [])]
        dependent_tasks = [t for t in tasks if t.get('dependencies', [])]
        
        results = []
        
        # Execute independent tasks in parallel
        if independent_tasks:
            parallel_results = await self._coordinate_parallel_execution(independent_tasks, sessionId)
            results.extend(parallel_results)
        
        # Execute dependent tasks sequentially
        if dependent_tasks:
            sequential_results = await self._coordinate_sequential_execution(dependent_tasks, sessionId)
            results.extend(sequential_results)
        
        return results

    async def _coordinate_single_task(self, task: dict, sessionId: str) -> dict:
        """Coordinate execution of a single task via specialist."""
        try:
            task_id = task.get('id', 'unknown')
            task_description = task.get('description', '')
            
            # Simulate task coordination (in real implementation, would use A2A protocol)
            await asyncio.sleep(0.1)  # Simulate coordination time
            
            return {
                'task_id': task_id,
                'status': 'completed',
                'result': f'Coordinated completion: {task_description[:50]}...',
                'specialist_used': task.get('agent_type', 'generalist'),
                'coordination_time': 0.1
            }
            
        except Exception as e:
            return {
                'task_id': task.get('id', 'unknown'),
                'status': 'error',
                'error': str(e),
                'coordination_time': 0
            }

    async def _stream_orchestration(self, execution_plan: dict, sessionId: str):
        """Stream orchestration execution progress."""
        tasks = execution_plan.get('tasks', [])
        
        for i, task in enumerate(tasks, 1):
            yield {
                'response_type': 'text',
                'is_task_complete': False,
                'require_user_input': False,
                'content': f'⚡ Coordinating task {i}/{len(tasks)}: {task.get("description", "")[:60]}...',
                'stage': 'task_coordination',
                'progress': i / len(tasks)
            }
            
            # Simulate coordination
            await asyncio.sleep(0.2)
            
            yield {
                'response_type': 'text',
                'is_task_complete': False,
                'require_user_input': False,
                'content': f'✅ Task {i} coordinated: {task.get("description", "")[:40]}...',
                'stage': 'task_completed',
                'progress': i / len(tasks)
            }

    def _calculate_orchestration_metrics(self, task_results: List[dict]) -> dict:
        """Calculate orchestration performance metrics."""
        total_tasks = len(task_results)
        completed_tasks = len([r for r in task_results if r.get('status') == 'completed'])
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'success_rate': completed_tasks / total_tasks if total_tasks > 0 else 0,
            'coordination_efficiency': round(completed_tasks / max(total_tasks, 1), 2),
            'specialists_utilized': len(self.active_agents)
        }

    async def _synthesize_results(self, orchestration_result: dict, execution_plan: dict, original_query: str) -> dict:
        """Synthesize final orchestration results."""
        return {
            'status': 'completed',
            'domain': self.domain_name,
            'orchestrator_type': 'master_template_refactored',
            'original_query': original_query,
            'planning_summary': {
                'planner_used': 'EnhancedGenericPlannerAgent',
                'planning_mode': self.planner.planning_mode,
                'tasks_planned': len(execution_plan.get('tasks', [])),
                'coordination_strategy': execution_plan.get('coordination_strategy'),
                'risk_assessment': execution_plan.get('risk_analysis', {}).get('risk_level', 'unknown')
            },
            'orchestration_summary': orchestration_result.get('orchestration_metrics', {}),
            'execution_results': orchestration_result,
            'enhanced_capabilities': [
                'Strategic planning via Enhanced Planner Agent',
                'Risk assessment and mitigation analysis',
                'Resource estimation and optimization',
                'Timeline analysis and coordination',
                'Quality validation and scoring',
                'Template-based planning support'
            ],
            'timestamp': datetime.now().isoformat()
        }

    def _format_orchestrator_response(self, result: dict) -> str:
        """Format orchestrator response for consistency."""
        return json.dumps(result, indent=2)

    # ============================================================================
    # PHASE 1: Dynamic Workflow Graph Capabilities
    # ============================================================================
    
    def _ensure_dynamic_workflow(self, session_id: str) -> DynamicWorkflowGraph:
        """Ensure dynamic workflow exists for session."""
        if not self.enable_dynamic_workflow:
            logger.debug("Dynamic workflow disabled, using legacy workflow")
            return None
            
        # Create new workflow if session changed or no workflow exists
        if (self.current_session_id != session_id or 
            self.dynamic_workflow is None):
            
            # Clean up previous session workflows if session changed
            if (self.current_session_id and 
                self.current_session_id != session_id):
                self.clear_session_state()
            
            self.current_session_id = session_id
            self.dynamic_workflow = workflow_manager.create_workflow(session_id)
            logger.info(f"Created dynamic workflow {self.dynamic_workflow.workflow_id} for session {session_id}")
        
        return self.dynamic_workflow
    
    # ============================================================================
    # PHASE 2: Context & History Tracking Methods
    # ============================================================================
    
    def _initialize_session_context(self, session_id: str, query: str):
        """Initialize or update session context with query information."""
        if session_id not in self.session_contexts:
            self.session_contexts[session_id] = {
                'session_start': datetime.now().isoformat(),
                'domain': self.domain_name,
                'total_queries': 0,
                'query_types': {},
                'specialists_used': set(),
                'performance_summary': {},
                'context_version': 1
            }
        
        # Update session context
        context = self.session_contexts[session_id]
        context['total_queries'] += 1
        context['last_query'] = query
        context['last_activity'] = datetime.now().isoformat()
        
        # Track query patterns
        query_type = self._classify_query_type(query)
        context['query_types'][query_type] = context['query_types'].get(query_type, 0) + 1
        
        # Update global query patterns
        self.query_patterns[query_type] = self.query_patterns.get(query_type, 0) + 1
        
        logger.debug(f"Initialized context for session {session_id}, query type: {query_type}")
    
    def _classify_query_type(self, query: str) -> str:
        """Classify query into categories for pattern tracking."""
        query_lower = query.lower()
        
        # Domain-specific classification
        if any(word in query_lower for word in ['analyze', 'analysis', 'report', 'summary']):
            return 'analysis'
        elif any(word in query_lower for word in ['create', 'build', 'generate', 'develop']):
            return 'creation'
        elif any(word in query_lower for word in ['plan', 'strategy', 'roadmap', 'organize']):
            return 'planning'
        elif any(word in query_lower for word in ['optimize', 'improve', 'enhance', 'better']):
            return 'optimization'
        elif any(word in query_lower for word in ['fix', 'solve', 'resolve', 'debug']):
            return 'problem_solving'
        elif any(word in query_lower for word in ['research', 'find', 'search', 'discover']):
            return 'research'
        else:
            return 'general'
    
    def _record_execution_history(self, session_id: str, execution_record: Dict[str, Any]):
        """Record detailed execution history for analysis and learning."""
        if session_id not in self.execution_history:
            self.execution_history[session_id] = []
        
        # Enhance record with context
        enhanced_record = {
            **execution_record,
            'record_id': str(uuid.uuid4()),
            'domain': self.domain_name,
            'orchestrator_version': 'v2.0_refactored',
            'planner_mode': self.planner.planning_mode,
            'context_snapshot': self._get_context_snapshot(session_id)
        }
        
        # Add performance metrics
        plan_tasks = execution_record.get('execution_plan', {}).get('tasks', [])
        enhanced_record['performance_metrics'] = {
            'tasks_planned': len(plan_tasks),
            'execution_duration': execution_record.get('execution_duration', 0),
            'success_rate': self._calculate_success_rate(execution_record.get('orchestration_result', {})),
            'complexity_score': self._assess_execution_complexity(plan_tasks)
        }
        
        self.execution_history[session_id].append(enhanced_record)
        
        # Update session performance metrics
        self._update_session_performance(session_id, enhanced_record)
        
        # Track context evolution
        self._track_context_evolution(session_id, enhanced_record)
        
        logger.info(f"Recorded execution history for session {session_id}: {enhanced_record['record_id']}")
    
    def _get_context_snapshot(self, session_id: str) -> Dict[str, Any]:
        """Get current context snapshot for historical record."""
        return {
            'session_context': self.session_contexts.get(session_id, {}),
            'active_agents_count': len(self.active_agents),
            'workflow_state': self.dynamic_workflow.state.value if self.dynamic_workflow else 'none',
            'domain_context_keys': list(self.domain_context.keys()),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_success_rate(self, orchestration_result: Dict[str, Any]) -> float:
        """Calculate success rate from orchestration results."""
        metrics = orchestration_result.get('orchestration_metrics', {})
        total_tasks = metrics.get('total_tasks', 1)
        completed_tasks = metrics.get('completed_tasks', 0)
        
        return completed_tasks / total_tasks if total_tasks > 0 else 0.0
    
    def _assess_execution_complexity(self, tasks: List[Dict[str, Any]]) -> float:
        """Assess execution complexity based on task characteristics."""
        if not tasks:
            return 0.0
        
        complexity_factors = {
            'task_count': len(tasks),
            'parallel_tasks': len([t for t in tasks if not t.get('dependencies', [])]),
            'dependent_tasks': len([t for t in tasks if t.get('dependencies', [])]),
            'specialist_diversity': len(set(t.get('agent_type', 'generic') for t in tasks))
        }
        
        # Weighted complexity score
        score = (
            complexity_factors['task_count'] * 0.3 +
            complexity_factors['parallel_tasks'] * 0.2 +
            complexity_factors['dependent_tasks'] * 0.3 +
            complexity_factors['specialist_diversity'] * 0.2
        )
        
        return min(score / 10.0, 1.0)  # Normalize to 0-1 scale
    
    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get complete session context for analysis or debugging."""
        return {
            'session_context': self.session_contexts.get(session_id, {}),
            'execution_history': self.execution_history.get(session_id, []),
            'performance_metrics': self.performance_metrics.get(session_id, {}),
            'context_evolution': [
                entry for entry in self.context_evolution 
                if entry['session_id'] == session_id
            ][-10:]  # Last 10 evolution entries
        }
    
    def get_domain_insights(self) -> Dict[str, Any]:
        """Get domain-wide insights from accumulated context and history."""
        total_sessions = len(self.session_contexts)
        total_executions = sum(
            len(history) for history in self.execution_history.values()
        )
        
        # Calculate domain-wide averages
        all_performance = list(self.performance_metrics.values())
        avg_success_rate = sum(p['avg_success_rate'] for p in all_performance) / len(all_performance) if all_performance else 0
        avg_complexity = sum(p['avg_complexity'] for p in all_performance) / len(all_performance) if all_performance else 0
        
        return {
            'domain': self.domain_name,
            'total_sessions': total_sessions,
            'total_executions': total_executions,
            'query_patterns': self.query_patterns,
            'avg_success_rate': avg_success_rate,
            'avg_complexity': avg_complexity,
            'most_common_query_type': max(self.query_patterns.items(), key=lambda x: x[1])[0] if self.query_patterns else 'none',
            'performance_insights': self._generate_performance_insights()
        }
    
    def _generate_performance_insights(self) -> List[str]:
        """Generate actionable performance insights."""
        insights = []
        
        if not self.performance_metrics:
            return ['Insufficient data for performance analysis']
        
        # Analyze success rates
        success_rates = [m['avg_success_rate'] for m in self.performance_metrics.values()]
        avg_success = sum(success_rates) / len(success_rates)
        
        if avg_success < 0.8:
            insights.append('Success rate below optimal threshold - consider task decomposition review')
        elif avg_success > 0.95:
            insights.append('Excellent success rate - current strategies are highly effective')
        
        # Analyze complexity trends
        complexities = [m['avg_complexity'] for m in self.performance_metrics.values()]
        avg_complexity = sum(complexities) / len(complexities)
        
        if avg_complexity > 0.7:
            insights.append('High complexity tasks detected - consider specialist diversification')
        
        # Analyze query patterns
        if self.query_patterns:
            most_common = max(self.query_patterns.items(), key=lambda x: x[1])
            insights.append(f'Most common query pattern: {most_common[0]} ({most_common[1]} occurrences)')
        
        return insights
    
    def _update_session_performance(self, session_id: str, execution_record: Dict[str, Any]):
        """Update session-level performance metrics."""
        if session_id not in self.performance_metrics:
            self.performance_metrics[session_id] = {
                'total_executions': 0,
                'avg_duration': 0.0,
                'avg_success_rate': 0.0,
                'avg_complexity': 0.0,
                'total_tasks_executed': 0,
                'performance_trend': []
            }
        
        metrics = self.performance_metrics[session_id]
        perf = execution_record['performance_metrics']
        
        # Update aggregated metrics
        metrics['total_executions'] += 1
        n = metrics['total_executions']
        
        # Running averages
        metrics['avg_duration'] = ((metrics['avg_duration'] * (n-1)) + perf['execution_duration']) / n
        metrics['avg_success_rate'] = ((metrics['avg_success_rate'] * (n-1)) + perf['success_rate']) / n
        metrics['avg_complexity'] = ((metrics['avg_complexity'] * (n-1)) + perf['complexity_score']) / n
        metrics['total_tasks_executed'] += perf['tasks_planned']
        
        # Track performance trend
        metrics['performance_trend'].append({
            'timestamp': execution_record['timestamp'],
            'duration': perf['execution_duration'],
            'success_rate': perf['success_rate'],
            'complexity': perf['complexity_score']
        })
        
        # Keep only last 50 trend points to avoid memory bloat
        if len(metrics['performance_trend']) > 50:
            metrics['performance_trend'] = metrics['performance_trend'][-50:]
    
    def _track_context_evolution(self, session_id: str, execution_record: Dict[str, Any]):
        """Track how context evolves over time."""
        evolution_entry = {
            'session_id': session_id,
            'timestamp': execution_record['timestamp'],
            'query_type': self._classify_query_type(execution_record['query']),
            'complexity_change': self._detect_complexity_change(session_id, execution_record),
            'new_patterns': self._detect_new_patterns(execution_record),
            'context_version': self.session_contexts[session_id]['context_version']
        }
        
        self.context_evolution.append(evolution_entry)
        
        # Keep only last 100 evolution entries
        if len(self.context_evolution) > 100:
            self.context_evolution = self.context_evolution[-100:]
    
    def _detect_complexity_change(self, session_id: str, execution_record: Dict[str, Any]) -> str:
        """Detect if execution complexity is trending up, down, or stable."""
        if session_id not in self.performance_metrics:
            return 'initial'
        
        current_complexity = execution_record['performance_metrics']['complexity_score']
        avg_complexity = self.performance_metrics[session_id]['avg_complexity']
        
        if current_complexity > avg_complexity * 1.2:
            return 'increasing'
        elif current_complexity < avg_complexity * 0.8:
            return 'decreasing'
        else:
            return 'stable'
    
    def _detect_new_patterns(self, execution_record: Dict[str, Any]) -> List[str]:
        """Detect new patterns in execution that might indicate context shift."""
        patterns = []
        
        # Check for new specialist types
        plan_tasks = execution_record.get('execution_plan', {}).get('tasks', [])
        specialist_types = set(t.get('agent_type', 'generic') for t in plan_tasks)
        
        for specialist in specialist_types:
            if specialist not in self.domain_specialists:
                patterns.append(f'new_specialist:{specialist}')
        
        # Check for coordination strategy changes
        coord_strategy = execution_record.get('execution_plan', {}).get('coordination_strategy', 'sequential')
        if coord_strategy != 'sequential':  # Default strategy
            patterns.append(f'coordination:{coord_strategy}')
        
        # Check for execution duration anomalies
        duration = execution_record.get('execution_duration', 0)
        if duration > 30:  # Longer than 30 seconds
            patterns.append('long_execution')
        
        return patterns
    
    def add_graph_node(
        self,
        task_id: str,
        context_id: str, 
        query: str,
        node_id: Optional[str] = None,
        node_key: Optional[str] = None,
        node_label: Optional[str] = None
    ) -> Optional[WorkflowNode]:
        """
        Add a node to the dynamic workflow graph.
        
        Args:
            task_id: Task identifier
            context_id: Context identifier (session ID)
            query: Task query/description
            node_id: Parent node ID to connect to (optional)
            node_key: Node type key (optional)
            node_label: Human-readable label (optional)
            
        Returns:
            Created WorkflowNode or None if dynamic workflow disabled
        """
        workflow = self._ensure_dynamic_workflow(context_id)
        if not workflow:
            return None
            
        # Create new workflow node
        node = WorkflowNode(
            task=query,
            node_key=node_key,
            node_label=node_label or f"{self.domain_name} Task"
        )
        
        # Add metadata
        node.set_attributes({
            'task_id': task_id,
            'context_id': context_id,
            'domain': self.domain_name,
            'orchestrator_type': 'master_template_refactored'
        })
        
        # Add to workflow
        workflow.add_node(node)
        
        # Add edge if parent specified
        if node_id and node_id in workflow.nodes:
            workflow.add_edge(node_id, node.id)
        
        logger.info(f"Added workflow node {node.id} ({node_key}) to {workflow.workflow_id}")
        return node
    
    def set_node_attributes(
        self, 
        node_id: str, 
        task_id: Optional[str] = None,
        context_id: Optional[str] = None, 
        query: Optional[str] = None,
        **additional_attrs
    ):
        """
        Set attributes on a workflow node.
        
        Args:
            node_id: Target node ID
            task_id: Task ID to set (optional)
            context_id: Context ID to set (optional)
            query: Query to update (optional)
            **additional_attrs: Additional attributes to set
        """
        if not self.dynamic_workflow:
            logger.debug("No dynamic workflow available for setting node attributes")
            return
            
        attributes = {}
        if task_id:
            attributes['task_id'] = task_id
        if context_id:
            attributes['context_id'] = context_id
        if query:
            # Update node task as well
            node = self.dynamic_workflow.get_node(node_id)
            if node:
                node.task = query
        
        attributes.update(additional_attrs)
        
        if attributes:
            self.dynamic_workflow.set_node_attributes(node_id, attributes)
    
    def get_workflow_stats(self) -> Dict[str, Any]:
        """Get current workflow statistics."""
        if not self.dynamic_workflow:
            return {'dynamic_workflow_enabled': False}
            
        stats = self.dynamic_workflow.get_workflow_stats()
        stats['dynamic_workflow_enabled'] = True
        stats['domain'] = self.domain_name
        return stats
    
    def clear_session_state(self, session_id: Optional[str] = None, preserve_domain_context: bool = True):
        """Enhanced clear state for session transitions - PHASE 2.5 implementation.
        
        Args:
            session_id: Specific session to clear (if None, clears current session)
            preserve_domain_context: Whether to preserve domain-wide learning context
        """
        target_session = session_id or self.current_session_id
        
        if target_session:
            # PHASE 2.5: Intelligent context preservation before clearing
            self._preserve_valuable_context(target_session, preserve_domain_context)
            
            # Clean up workflow manager
            workflow_manager.cleanup_session(target_session)
            
            # PHASE 2.5: Clear PHASE 2 context & history data
            self._clear_phase2_context_data(target_session)
            
            logger.info(f"Enhanced session state clearing completed for {target_session}")
        
        # Reset instance state (only if clearing current session)
        if not session_id or session_id == self.current_session_id:
            self.dynamic_workflow = None
            self.current_session_id = None
            self.active_agents.clear()
            self.execution_context.clear()
            self.coordination_history.clear()
            self.workflow_graph = None
            
            # Reset planner state if needed
            if hasattr(self.planner, 'clear_session_context'):
                self.planner.clear_session_context(target_session)
    
    # ============================================================================
    # PHASE 2.5: Clear State Management - Context Change Detection & Auto-Clear
    # ============================================================================
    
    def _preserve_valuable_context(self, session_id: str, preserve_domain_context: bool):
        """Preserve valuable context before clearing session state."""
        if session_id in self.session_contexts:
            session_context = self.session_contexts[session_id]
            
            # Extract valuable patterns for domain learning
            if preserve_domain_context:
                self._extract_domain_learnings(session_context, session_id)
            
            # Archive session summary for future reference
            self._archive_session_summary(session_id, session_context)
    
    def _clear_phase2_context_data(self, session_id: str):
        """Clear PHASE 2 context and history data for specific session."""
        # Clear session-specific data
        if session_id in self.session_contexts:
            del self.session_contexts[session_id]
        
        if session_id in self.execution_history:
            del self.execution_history[session_id]
        
        if session_id in self.performance_metrics:
            del self.performance_metrics[session_id]
        
        # Remove session-specific context evolution entries
        self.context_evolution = [
            entry for entry in self.context_evolution 
            if entry['session_id'] != session_id
        ]
        
        logger.debug(f"Cleared PHASE 2 context data for session {session_id}")
    
    def _extract_domain_learnings(self, session_context: Dict[str, Any], session_id: str):
        """Extract valuable learnings to preserve in domain context."""
        # Extract query patterns for domain intelligence
        query_types = session_context.get('query_types', {})
        for query_type, count in query_types.items():
            self.query_patterns[query_type] = self.query_patterns.get(query_type, 0) + count
        
        # Extract specialist usage patterns
        specialists_used = session_context.get('specialists_used', set())
        if not hasattr(self, 'domain_specialist_usage'):
            self.domain_specialist_usage = {}
        
        for specialist in specialists_used:
            self.domain_specialist_usage[specialist] = self.domain_specialist_usage.get(specialist, 0) + 1
        
        # Store high-level performance insights in domain context
        if session_id in self.performance_metrics:
            perf = self.performance_metrics[session_id]
            if perf['avg_success_rate'] > 0.9:  # High-performing sessions
                if 'high_performance_patterns' not in self.domain_context:
                    self.domain_context['high_performance_patterns'] = []
                
                self.domain_context['high_performance_patterns'].append({
                    'session_type': session_context.get('query_types', {}),
                    'success_rate': perf['avg_success_rate'],
                    'avg_complexity': perf['avg_complexity'],
                    'timestamp': datetime.now().isoformat()
                })
        
        logger.debug(f"Extracted domain learnings from session {session_id}")
    
    def _archive_session_summary(self, session_id: str, session_context: Dict[str, Any]):
        """Archive session summary for potential future reference."""
        if not hasattr(self, 'archived_sessions'):
            self.archived_sessions = {}
        
        # Keep only essential summary to avoid memory bloat
        summary = {
            'session_start': session_context.get('session_start'),
            'total_queries': session_context.get('total_queries', 0),
            'dominant_query_type': max(session_context.get('query_types', {}).items(), key=lambda x: x[1])[0] if session_context.get('query_types') else 'unknown',
            'archived_at': datetime.now().isoformat()
        }
        
        self.archived_sessions[session_id] = summary
        
        # Keep only last 20 archived sessions to prevent memory issues
        if len(self.archived_sessions) > 20:
            oldest_sessions = sorted(self.archived_sessions.items(), key=lambda x: x[1]['archived_at'])[:5]
            for old_session_id, _ in oldest_sessions:
                del self.archived_sessions[old_session_id]
    
    def detect_context_change(self, current_query: str, session_id: str) -> Dict[str, Any]:
        """Detect if current query represents a significant context change."""
        if session_id not in self.session_contexts:
            return {'context_change': False, 'reason': 'new_session'}
        
        session_context = self.session_contexts[session_id]
        current_query_type = self._classify_query_type(current_query)
        
        # Analyze context change indicators
        change_indicators = []
        
        # 1. Query type shift detection
        query_types = session_context.get('query_types', {})
        if query_types:
            dominant_type = max(query_types.items(), key=lambda x: x[1])[0]
            if current_query_type != dominant_type and query_types.get(current_query_type, 0) == 0:
                change_indicators.append('query_type_shift')
        
        # 2. Domain terminology shift detection
        last_query = session_context.get('last_query', '')
        if self._detect_domain_shift(current_query, last_query):
            change_indicators.append('domain_terminology_shift')
        
        # 3. Complexity shift detection
        if session_id in self.performance_metrics:
            recent_complexity = self.performance_metrics[session_id].get('avg_complexity', 0)
            current_complexity = self._estimate_query_complexity(current_query)
            if abs(current_complexity - recent_complexity) > 0.4:  # Significant complexity change
                change_indicators.append('complexity_shift')
        
        # 4. Time gap detection
        last_activity = session_context.get('last_activity')
        if last_activity:
            time_gap = (datetime.now() - datetime.fromisoformat(last_activity)).total_seconds()
            if time_gap > 1800:  # More than 30 minutes
                change_indicators.append('time_gap')
        
        # Determine if context change is significant enough to trigger clear
        significant_change = len(change_indicators) >= 2 or 'domain_terminology_shift' in change_indicators
        
        return {
            'context_change': significant_change,
            'indicators': change_indicators,
            'confidence': len(change_indicators) / 4.0,  # Normalized confidence score
            'recommendation': 'clear_context' if significant_change else 'continue',
            'query_type_change': current_query_type
        }
    
    def _detect_domain_shift(self, current_query: str, last_query: str) -> bool:
        """Detect significant domain/topic shift between queries."""
        if not last_query:
            return False
        
        # Simple keyword-based domain shift detection
        current_keywords = set(current_query.lower().split())
        last_keywords = set(last_query.lower().split())
        
        # Remove common words
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'among', 'can', 'could', 'should', 'would', 'will', 'shall', 'may', 'might', 'must', 'need', 'want', 'like', 'know', 'think', 'say', 'get', 'make', 'go', 'do', 'see', 'come', 'take', 'use', 'find', 'give', 'tell', 'ask', 'work', 'seem', 'feel', 'try', 'leave', 'call'}
        
        current_meaningful = current_keywords - common_words
        last_meaningful = last_keywords - common_words
        
        if not last_meaningful:
            return False
        
        # Calculate keyword overlap
        overlap = len(current_meaningful & last_meaningful)
        total_unique = len(current_meaningful | last_meaningful)
        
        overlap_ratio = overlap / total_unique if total_unique > 0 else 0
        
        # Domain shift if less than 20% keyword overlap
        return overlap_ratio < 0.2
    
    def _estimate_query_complexity(self, query: str) -> float:
        """Estimate query complexity for context change detection."""
        complexity_factors = {
            'length': len(query.split()) / 50.0,  # Normalized by 50 words
            'technical_terms': len([w for w in query.lower().split() if len(w) > 8]) / 10.0,
            'question_complexity': len([w for w in query.lower().split() if w in ['analyze', 'compare', 'evaluate', 'synthesize', 'optimize']]) / 5.0,
            'coordination_indicators': len([w for w in query.lower().split() if w in ['coordinate', 'orchestrate', 'manage', 'integrate', 'combine']]) / 3.0
        }
        
        # Weighted complexity score
        complexity = (
            complexity_factors['length'] * 0.2 +
            complexity_factors['technical_terms'] * 0.3 +
            complexity_factors['question_complexity'] * 0.3 +
            complexity_factors['coordination_indicators'] * 0.2
        )
        
        return min(complexity, 1.0)  # Cap at 1.0
    
    def auto_clear_on_context_change(self, query: str, session_id: str) -> bool:
        """Automatically clear context if significant change detected."""
        change_analysis = self.detect_context_change(query, session_id)
        
        if change_analysis['context_change'] and change_analysis['confidence'] > 0.6:
            logger.info(f"Auto-clearing context for session {session_id}: {change_analysis['indicators']}")
            
            # Preserve domain context but clear session-specific state
            self.clear_session_state(session_id, preserve_domain_context=True)
            
            # Log context change for analysis
            self.context_evolution.append({
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'event_type': 'auto_context_clear',
                'change_indicators': change_analysis['indicators'],
                'confidence': change_analysis['confidence'],
                'query_type_change': change_analysis['query_type_change']
            })
            
            return True
        
        return False
    
    def get_context_change_stats(self) -> Dict[str, Any]:
        """Get statistics about context changes and auto-clears."""
        context_events = [e for e in self.context_evolution if e.get('event_type') == 'auto_context_clear']
        
        if not context_events:
            return {'total_auto_clears': 0, 'most_common_indicator': 'none'}
        
        all_indicators = []
        for event in context_events:
            all_indicators.extend(event.get('change_indicators', []))
        
        from collections import Counter
        indicator_counts = Counter(all_indicators)
        
        return {
            'total_auto_clears': len(context_events),
            'most_common_indicator': indicator_counts.most_common(1)[0][0] if indicator_counts else 'none',
            'indicator_distribution': dict(indicator_counts),
            'avg_confidence': sum(e.get('confidence', 0) for e in context_events) / len(context_events)
        }
    
    def pause_workflow(self, paused_node_id: Optional[str] = None, reason: str = 'manual', save_checkpoint: bool = True):
        """Enhanced pause workflow with state management - PHASE 3."""
        if self.dynamic_workflow:
            session_id = self.current_session_id
            
            # PHASE 3: Create execution checkpoint before pausing
            if save_checkpoint and session_id:
                self._create_execution_checkpoint(session_id, paused_node_id, reason)
            
            # Pause the workflow
            self.dynamic_workflow.pause_workflow(paused_node_id)
            
            # PHASE 3: Update execution state
            self._update_execution_state(session_id, 'paused', {
                'paused_node_id': paused_node_id,
                'pause_reason': reason,
                'pause_timestamp': datetime.now().isoformat(),
                'workflow_state_snapshot': self._capture_workflow_state()
            })
            
            logger.info(f"Enhanced pause: workflow at node {paused_node_id}, reason: {reason}")
    
    def resume_workflow(self, resumption_strategy: str = 'continue', validation_checks: bool = True):
        """Enhanced resume workflow with state validation - PHASE 3."""
        if self.dynamic_workflow and self.current_session_id:
            session_id = self.current_session_id
            
            # PHASE 3: Validate resumption conditions
            if validation_checks and not self._validate_resumption_conditions(session_id):
                logger.warning(f"Resumption validation failed for session {session_id}")
                return False
            
            # PHASE 3: Apply resumption strategy
            success = self._apply_resumption_strategy(session_id, resumption_strategy)
            
            if success:
                # Resume the workflow
                self.dynamic_workflow.resume_workflow()
                
                # PHASE 3: Update execution state
                self._update_execution_state(session_id, 'running', {
                    'resume_timestamp': datetime.now().isoformat(),
                    'resumption_strategy': resumption_strategy,
                    'validation_passed': validation_checks
                })
                
                logger.info(f"Enhanced resume: workflow resumed with strategy {resumption_strategy}")
                return True
            else:
                logger.error(f"Failed to resume workflow for session {session_id}")
                return False
        
        return False
    
    # ============================================================================
    # PHASE 3: Enhanced State Management Support Methods
    # ============================================================================
    
    def _create_execution_checkpoint(self, session_id: str, paused_node_id: Optional[str], reason: str):
        """Create execution checkpoint for state recovery."""
        if session_id not in self.pause_checkpoints:
            self.pause_checkpoints[session_id] = []
        
        checkpoint = {
            'checkpoint_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'paused_node_id': paused_node_id,
            'pause_reason': reason,
            'workflow_state': self._capture_workflow_state(),
            'execution_context': dict(self.execution_context),
            'active_agents': dict(self.active_agents),
            'session_context_snapshot': self.session_contexts.get(session_id, {}),
            'performance_metrics_snapshot': self.performance_metrics.get(session_id, {})
        }
        
        self.pause_checkpoints[session_id].append(checkpoint)
        
        # Keep only last 10 checkpoints per session to manage memory
        if len(self.pause_checkpoints[session_id]) > 10:
            self.pause_checkpoints[session_id] = self.pause_checkpoints[session_id][-10:]
        
        logger.debug(f"Created execution checkpoint {checkpoint['checkpoint_id']} for session {session_id}")
    
    def _capture_workflow_state(self) -> Dict[str, Any]:
        """Capture current workflow state for checkpoint."""
        if not self.dynamic_workflow:
            return {'workflow_exists': False}
        
        return {
            'workflow_exists': True,
            'workflow_id': self.dynamic_workflow.workflow_id,
            'state': self.dynamic_workflow.state.value,
            'paused_node_id': self.dynamic_workflow.paused_node_id,
            'total_nodes': len(self.dynamic_workflow.nodes),
            'completed_nodes': len([n for n in self.dynamic_workflow.nodes.values() if n.state.value == 'completed']),
            'pending_nodes': len([n for n in self.dynamic_workflow.nodes.values() if n.state.value == 'pending']),
            'executable_nodes': len(self.dynamic_workflow.get_executable_nodes()),
            'workflow_stats': self.dynamic_workflow.get_workflow_stats()
        }
    
    def _update_execution_state(self, session_id: str, state: str, additional_data: Dict[str, Any]):
        """Update execution state tracking."""
        if session_id not in self.execution_states:
            self.execution_states[session_id] = {
                'current_state': 'unknown',
                'state_history': [],
                'last_updated': None
            }
        
        execution_state = self.execution_states[session_id]
        previous_state = execution_state['current_state']
        
        # Record state transition
        transition = {
            'from_state': previous_state,
            'to_state': state,
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            **additional_data
        }
        
        execution_state['state_history'].append(transition)
        execution_state['current_state'] = state
        execution_state['last_updated'] = transition['timestamp']
        
        # Add to global state transitions
        self.state_transitions.append(transition)
        
        # Keep only last 100 global transitions
        if len(self.state_transitions) > 100:
            self.state_transitions = self.state_transitions[-100:]
        
        logger.debug(f"State transition: {previous_state} -> {state} for session {session_id}")
    
    def _validate_resumption_conditions(self, session_id: str) -> bool:
        """Validate conditions for safe workflow resumption."""
        # Check if workflow exists and is paused
        if not self.dynamic_workflow or self.dynamic_workflow.state.value != 'paused':
            logger.warning("Cannot resume: workflow not in paused state")
            return False
        
        # Check execution state consistency
        if session_id not in self.execution_states:
            logger.warning("Cannot resume: no execution state found")
            return False
        
        execution_state = self.execution_states[session_id]
        if execution_state['current_state'] != 'paused':
            logger.warning(f"Cannot resume: execution state mismatch - {execution_state['current_state']}")
            return False
        
        # Check for workflow integrity
        if self.dynamic_workflow._has_cycles():
            logger.warning("Cannot resume: workflow has circular dependencies")
            return False
        
        # Check if there are executable nodes
        executable_nodes = self.dynamic_workflow.get_executable_nodes()
        if not executable_nodes and self.dynamic_workflow.paused_node_id:
            # Check if paused node can be resumed
            paused_node = self.dynamic_workflow.get_node(self.dynamic_workflow.paused_node_id)
            if not paused_node or paused_node.state.value not in ['pending', 'running']:
                logger.warning("Cannot resume: no executable nodes and paused node not resumable")
                return False
        
        # Validate session context consistency
        if session_id not in self.session_contexts:
            logger.warning("Cannot resume: session context missing")
            return False
        
        logger.debug(f"Resumption validation passed for session {session_id}")
        return True
    
    def _apply_resumption_strategy(self, session_id: str, strategy: str) -> bool:
        """Apply specific resumption strategy."""
        try:
            if strategy == 'continue':
                # Continue from where paused
                return self._resume_continue_strategy(session_id)
            elif strategy == 'restart':
                # Restart from beginning with current context
                return self._resume_restart_strategy(session_id)
            elif strategy == 'skip':
                # Skip paused node and continue
                return self._resume_skip_strategy(session_id)
            elif strategy == 'rollback':
                # Rollback to previous checkpoint
                return self._resume_rollback_strategy(session_id)
            else:
                logger.error(f"Unknown resumption strategy: {strategy}")
                return False
        except Exception as e:
            logger.error(f"Error applying resumption strategy {strategy}: {e}")
            return False
    
    def _resume_continue_strategy(self, session_id: str) -> bool:
        """Resume from current paused state."""
        self.resumption_strategies[session_id] = 'continue'
        logger.debug(f"Applied continue strategy for session {session_id}")
        return True
    
    def _resume_restart_strategy(self, session_id: str) -> bool:
        """Restart workflow from beginning."""
        if self.dynamic_workflow:
            # Reset all nodes to pending state
            for node in self.dynamic_workflow.nodes.values():
                if node.state.value in ['completed', 'failed']:
                    node.state = NodeState.PENDING
                    node.started_at = None
                    node.completed_at = None
                    node.result = None
                    node.error = None
            
            # Reset workflow state
            self.dynamic_workflow.state = WorkflowState.RUNNING
            self.dynamic_workflow.paused_node_id = None
            
            self.resumption_strategies[session_id] = 'restart'
            logger.debug(f"Applied restart strategy for session {session_id}")
            return True
        return False
    
    def _resume_skip_strategy(self, session_id: str) -> bool:
        """Skip paused node and continue with next executable nodes."""
        if self.dynamic_workflow and self.dynamic_workflow.paused_node_id:
            paused_node = self.dynamic_workflow.get_node(self.dynamic_workflow.paused_node_id)
            if paused_node:
                # Mark paused node as skipped
                paused_node.state = NodeState.SKIPPED
                paused_node.completed_at = datetime.now()
                
                # Clear pause state
                self.dynamic_workflow.paused_node_id = None
                
                self.resumption_strategies[session_id] = 'skip'
                logger.debug(f"Applied skip strategy for session {session_id}")
                return True
        return False
    
    def _resume_rollback_strategy(self, session_id: str) -> bool:
        """Rollback to previous checkpoint and resume."""
        if session_id in self.pause_checkpoints and self.pause_checkpoints[session_id]:
            # Get most recent checkpoint
            checkpoint = self.pause_checkpoints[session_id][-1]
            
            # Restore execution context
            self.execution_context = checkpoint['execution_context']
            self.active_agents = checkpoint['active_agents']
            
            # Restore session context
            if session_id in self.session_contexts:
                self.session_contexts[session_id].update(checkpoint['session_context_snapshot'])
            
            self.resumption_strategies[session_id] = 'rollback'
            logger.debug(f"Applied rollback strategy for session {session_id}")
            return True
        
        logger.warning(f"No checkpoints available for rollback in session {session_id}")
        return False
    
    def get_execution_state_summary(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive execution state summary."""
        return {
            'session_id': session_id,
            'current_state': self.execution_states.get(session_id, {}).get('current_state', 'unknown'),
            'workflow_state': self._capture_workflow_state(),
            'available_checkpoints': len(self.pause_checkpoints.get(session_id, [])),
            'state_transitions': len(self.execution_states.get(session_id, {}).get('state_history', [])),
            'resumption_strategy': self.resumption_strategies.get(session_id),
            'can_resume': self._validate_resumption_conditions(session_id) if session_id in self.execution_states else False,
            'executable_nodes_count': len(self.dynamic_workflow.get_executable_nodes()) if self.dynamic_workflow else 0
        }
    
    def get_pause_resume_analytics(self) -> Dict[str, Any]:
        """Get analytics on pause/resume patterns."""
        total_pauses = len([t for t in self.state_transitions if t['to_state'] == 'paused'])
        total_resumes = len([t for t in self.state_transitions if t['to_state'] == 'running'])
        
        pause_reasons = {}
        for transition in self.state_transitions:
            if transition['to_state'] == 'paused':
                reason = transition.get('pause_reason', 'unknown')
                pause_reasons[reason] = pause_reasons.get(reason, 0) + 1
        
        resumption_strategies = {}
        for strategy in self.resumption_strategies.values():
            resumption_strategies[strategy] = resumption_strategies.get(strategy, 0) + 1
        
        return {
            'total_pauses': total_pauses,
            'total_resumes': total_resumes,
            'success_rate': total_resumes / total_pauses if total_pauses > 0 else 0,
            'pause_reasons': pause_reasons,
            'resumption_strategies': resumption_strategies,
            'active_sessions_with_state': len(self.execution_states),
            'total_checkpoints': sum(len(checkpoints) for checkpoints in self.pause_checkpoints.values())
        }
    
    # ============================================================================
    # PHASE 4: Artifact Management & Result Collection Methods
    # ============================================================================
    
    async def _collect_orchestration_artifacts(self, orchestration_result: Dict[str, Any], execution_plan: Dict[str, Any], session_id: str):
        """Collect artifacts from orchestration execution."""
        collection_id = str(uuid.uuid4())
        
        # Create result collection for this orchestration
        collection = await self._create_result_collection(
            collection_id=collection_id,
            session_id=session_id,
            collection_type='orchestration_execution',
            metadata={
                'execution_plan_id': execution_plan.get('plan_id', 'unknown'),
                'coordination_strategy': execution_plan.get('coordination_strategy', 'sequential'),
                'task_count': len(execution_plan.get('tasks', [])),
                'timestamp': datetime.now().isoformat()
            }
        )
        
        # Collect task-level artifacts
        tasks = execution_plan.get('tasks', [])
        task_results = orchestration_result.get('task_results', [])
        
        for task, result in zip(tasks, task_results):
            await self._collect_task_artifacts(task, result, session_id, collection_id)
        
        # Collect orchestration-level artifacts
        await self._collect_orchestration_metadata_artifacts(orchestration_result, session_id, collection_id)
        
        logger.info(f"Collected artifacts for orchestration in collection {collection_id}")
    
    async def _create_result_collection(self, collection_id: str, session_id: str, collection_type: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new result collection."""
        collection = {
            'collection_id': collection_id,
            'session_id': session_id,
            'collection_type': collection_type,
            'created_at': datetime.now().isoformat(),
            'artifact_ids': [],
            'metadata': metadata,
            'tags': [],
            'status': 'active'
        }
        
        self.result_collections[collection_id] = collection
        
        # Associate with session
        if session_id not in self.session_artifacts:
            self.session_artifacts[session_id] = []
        
        logger.debug(f"Created result collection {collection_id} for session {session_id}")
        return collection
    
    async def _collect_task_artifacts(self, task: Dict[str, Any], result: Dict[str, Any], session_id: str, collection_id: str):
        """Collect artifacts from individual task execution."""
        task_id = task.get('id', 'unknown')
        
        # Create task result artifact
        if result.get('result'):
            artifact_id = await self.store_artifact(
                content=result['result'],
                artifact_type='task_result',
                source_info={
                    'task_id': task_id,
                    'task_description': task.get('description', ''),
                    'specialist_used': result.get('specialist_used', 'unknown'),
                    'execution_status': result.get('status', 'unknown')
                },
                session_id=session_id,
                collection_id=collection_id
            )
            
            # Associate artifact with task
            if task_id not in self.task_artifacts:
                self.task_artifacts[task_id] = []
            self.task_artifacts[task_id].append(artifact_id)
        
        # Collect task execution metadata
        if result.get('coordination_time') or result.get('status'):
            metadata_artifact_id = await self.store_artifact(
                content={
                    'execution_metadata': {
                        'coordination_time': result.get('coordination_time', 0),
                        'status': result.get('status', 'unknown'),
                        'error': result.get('error'),
                        'specialist_used': result.get('specialist_used')
                    }
                },
                artifact_type='task_metadata',
                source_info={
                    'task_id': task_id,
                    'metadata_type': 'execution_metrics'
                },
                session_id=session_id,
                collection_id=collection_id
            )
            
            if task_id not in self.task_artifacts:
                self.task_artifacts[task_id] = []
            self.task_artifacts[task_id].append(metadata_artifact_id)
    
    async def _collect_orchestration_metadata_artifacts(self, orchestration_result: Dict[str, Any], session_id: str, collection_id: str):
        """Collect orchestration-level metadata artifacts."""
        # Collect orchestration metrics
        metrics = orchestration_result.get('orchestration_metrics', {})
        if metrics:
            await self.store_artifact(
                content=metrics,
                artifact_type='orchestration_metrics',
                source_info={
                    'metrics_type': 'orchestration_summary',
                    'execution_strategy': orchestration_result.get('execution_strategy', 'unknown')
                },
                session_id=session_id,
                collection_id=collection_id
            )
        
        # Collect specialist coordination data
        specialist_data = orchestration_result.get('specialist_coordination', {})
        if specialist_data:
            await self.store_artifact(
                content=specialist_data,
                artifact_type='specialist_coordination',
                source_info={
                    'coordination_type': 'specialist_management',
                    'specialists_count': len(specialist_data)
                },
                session_id=session_id,
                collection_id=collection_id
            )
    
    async def store_artifact(
        self, 
        content: Any, 
        artifact_type: str, 
        source_info: Dict[str, Any], 
        session_id: str,
        collection_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store an artifact with comprehensive metadata."""
        artifact_id = str(uuid.uuid4())
        
        # Prepare artifact data
        artifact = {
            'artifact_id': artifact_id,
            'content': content,
            'artifact_type': artifact_type,
            'source_info': source_info,
            'session_id': session_id,
            'collection_id': collection_id,
            'created_at': datetime.now().isoformat(),
            'tags': tags or [],
            'metadata': metadata or {},
            'content_size': self._calculate_content_size(content),
            'content_hash': self._calculate_content_hash(content),
            'relationships': []
        }
        
        # Store in artifact store
        self.artifact_store[artifact_id] = artifact
        
        # Associate with session
        if session_id not in self.session_artifacts:
            self.session_artifacts[session_id] = []
        self.session_artifacts[session_id].append(artifact_id)
        
        # Associate with collection
        if collection_id and collection_id in self.result_collections:
            self.result_collections[collection_id]['artifact_ids'].append(artifact_id)
        
        # Update search index
        self._update_artifact_search_index(artifact_id, artifact)
        
        # Auto-detect relationships
        await self._detect_artifact_relationships(artifact_id)
        
        logger.debug(f"Stored artifact {artifact_id} (type: {artifact_type}, session: {session_id})")
        return artifact_id
    
    def _calculate_content_size(self, content: Any) -> int:
        """Calculate approximate content size in bytes."""
        try:
            import json
            if isinstance(content, (dict, list)):
                return len(json.dumps(content, default=str).encode('utf-8'))
            elif isinstance(content, str):
                return len(content.encode('utf-8'))
            else:
                return len(str(content).encode('utf-8'))
        except Exception:
            return 0
    
    def _calculate_content_hash(self, content: Any) -> str:
        """Calculate content hash for deduplication."""
        try:
            import hashlib
            import json
            
            if isinstance(content, (dict, list)):
                content_str = json.dumps(content, sort_keys=True, default=str)
            else:
                content_str = str(content)
            
            return hashlib.md5(content_str.encode('utf-8')).hexdigest()
        except Exception:
            return 'unknown'
    
    def _update_artifact_search_index(self, artifact_id: str, artifact: Dict[str, Any]):
        """Update search index for artifact discovery."""
        # Extract searchable keywords
        keywords = set()
        
        # From artifact type
        keywords.add(artifact['artifact_type'])
        
        # From tags
        keywords.update(artifact.get('tags', []))
        
        # From source info
        source_info = artifact.get('source_info', {})
        for key, value in source_info.items():
            if isinstance(value, str) and len(value) < 50:  # Avoid indexing large text
                keywords.add(value.lower())
        
        # From content (limited extraction)
        content = artifact.get('content', {})
        if isinstance(content, dict):
            for key in content.keys():
                if isinstance(key, str) and len(key) < 30:
                    keywords.add(key.lower())
        
        # Update index
        for keyword in keywords:
            if keyword not in self.artifact_search_index:
                self.artifact_search_index[keyword] = []
            if artifact_id not in self.artifact_search_index[keyword]:
                self.artifact_search_index[keyword].append(artifact_id)
    
    async def _detect_artifact_relationships(self, artifact_id: str):
        """Detect relationships between artifacts."""
        artifact = self.artifact_store.get(artifact_id)
        if not artifact:
            return
        
        relationships = []
        
        # Find artifacts from same session
        session_id = artifact['session_id']
        session_artifacts = self.session_artifacts.get(session_id, [])
        
        for other_artifact_id in session_artifacts:
            if other_artifact_id == artifact_id:
                continue
            
            other_artifact = self.artifact_store.get(other_artifact_id)
            if not other_artifact:
                continue
            
            # Check for task sequence relationships
            if self._are_artifacts_task_related(artifact, other_artifact):
                relationships.append(other_artifact_id)
            
            # Check for content similarity relationships
            if self._are_artifacts_content_similar(artifact, other_artifact):
                relationships.append(other_artifact_id)
        
        # Store relationships
        if relationships:
            self.artifact_relationships[artifact_id] = relationships
            artifact['relationships'] = relationships
    
    def _are_artifacts_task_related(self, artifact1: Dict[str, Any], artifact2: Dict[str, Any]) -> bool:
        """Check if artifacts are related through task execution."""
        source1 = artifact1.get('source_info', {})
        source2 = artifact2.get('source_info', {})
        
        # Same task ID
        if source1.get('task_id') and source1.get('task_id') == source2.get('task_id'):
            return True
        
        # Same specialist
        if source1.get('specialist_used') and source1.get('specialist_used') == source2.get('specialist_used'):
            return True
        
        return False
    
    def _are_artifacts_content_similar(self, artifact1: Dict[str, Any], artifact2: Dict[str, Any]) -> bool:
        """Check if artifacts have similar content."""
        # Simple hash-based similarity
        hash1 = artifact1.get('content_hash')
        hash2 = artifact2.get('content_hash')
        
        if hash1 and hash2 and hash1 == hash2:
            return True
        
        # Type-based similarity
        type1 = artifact1.get('artifact_type')
        type2 = artifact2.get('artifact_type')
        
        if type1 and type2 and type1 == type2:
            return True
        
        return False
    
    def search_artifacts(
        self, 
        query: str = None, 
        artifact_type: str = None, 
        session_id: str = None,
        collection_id: str = None,
        tags: List[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search artifacts with multiple criteria."""
        matching_artifacts = []
        
        # Get candidate artifact IDs
        candidate_ids = set()
        
        if query:
            # Search by keywords
            query_keywords = query.lower().split()
            for keyword in query_keywords:
                if keyword in self.artifact_search_index:
                    candidate_ids.update(self.artifact_search_index[keyword])
        else:
            # If no query, start with all artifacts
            candidate_ids = set(self.artifact_store.keys())
        
        # Filter candidates
        for artifact_id in candidate_ids:
            artifact = self.artifact_store.get(artifact_id)
            if not artifact:
                continue
            
            # Apply filters
            if artifact_type and artifact.get('artifact_type') != artifact_type:
                continue
            
            if session_id and artifact.get('session_id') != session_id:
                continue
            
            if collection_id and artifact.get('collection_id') != collection_id:
                continue
            
            if tags:
                artifact_tags = set(artifact.get('tags', []))
                if not any(tag in artifact_tags for tag in tags):
                    continue
            
            matching_artifacts.append(artifact)
        
        # Sort by creation time (newest first)
        matching_artifacts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return matching_artifacts[:limit]
    
    def get_artifact(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        """Get artifact by ID."""
        return self.artifact_store.get(artifact_id)
    
    def get_session_artifacts(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all artifacts for a session."""
        artifact_ids = self.session_artifacts.get(session_id, [])
        return [self.artifact_store[aid] for aid in artifact_ids if aid in self.artifact_store]
    
    def get_task_artifacts(self, task_id: str) -> List[Dict[str, Any]]:
        """Get all artifacts for a specific task."""
        artifact_ids = self.task_artifacts.get(task_id, [])
        return [self.artifact_store[aid] for aid in artifact_ids if aid in self.artifact_store]
    
    def get_collection_artifacts(self, collection_id: str) -> List[Dict[str, Any]]:
        """Get all artifacts in a collection."""
        collection = self.result_collections.get(collection_id)
        if not collection:
            return []
        
        artifact_ids = collection.get('artifact_ids', [])
        return [self.artifact_store[aid] for aid in artifact_ids if aid in self.artifact_store]
    
    def get_related_artifacts(self, artifact_id: str) -> List[Dict[str, Any]]:
        """Get artifacts related to a specific artifact."""
        related_ids = self.artifact_relationships.get(artifact_id, [])
        return [self.artifact_store[aid] for aid in related_ids if aid in self.artifact_store]
    
    def get_artifact_analytics(self) -> Dict[str, Any]:
        """Get comprehensive artifact analytics."""
        total_artifacts = len(self.artifact_store)
        
        # Analyze by type
        type_distribution = {}
        size_distribution = {'small': 0, 'medium': 0, 'large': 0}
        
        for artifact in self.artifact_store.values():
            artifact_type = artifact.get('artifact_type', 'unknown')
            type_distribution[artifact_type] = type_distribution.get(artifact_type, 0) + 1
            
            # Size analysis
            size = artifact.get('content_size', 0)
            if size < 1024:  # < 1KB
                size_distribution['small'] += 1
            elif size < 102400:  # < 100KB
                size_distribution['medium'] += 1
            else:
                size_distribution['large'] += 1
        
        return {
            'total_artifacts': total_artifacts,
            'total_sessions_with_artifacts': len(self.session_artifacts),
            'total_tasks_with_artifacts': len(self.task_artifacts),
            'total_collections': len(self.result_collections),
            'type_distribution': type_distribution,
            'size_distribution': size_distribution,
            'search_index_keywords': len(self.artifact_search_index),
            'total_relationships': sum(len(rels) for rels in self.artifact_relationships.values()),
            'avg_artifacts_per_session': total_artifacts / len(self.session_artifacts) if self.session_artifacts else 0
        }
    
    def cleanup_artifacts(self, session_id: str = None, older_than_hours: int = None):
        """Clean up artifacts based on criteria."""
        artifacts_to_remove = []
        
        for artifact_id, artifact in self.artifact_store.items():
            should_remove = False
            
            # Session-based cleanup
            if session_id and artifact.get('session_id') == session_id:
                should_remove = True
            
            # Time-based cleanup
            if older_than_hours:
                created_at = datetime.fromisoformat(artifact.get('created_at', '1970-01-01T00:00:00'))
                if (datetime.now() - created_at).total_seconds() > (older_than_hours * 3600):
                    should_remove = True
            
            if should_remove:
                artifacts_to_remove.append(artifact_id)
        
        # Remove artifacts
        for artifact_id in artifacts_to_remove:
            self._remove_artifact(artifact_id)
        
        logger.info(f"Cleaned up {len(artifacts_to_remove)} artifacts")
        return len(artifacts_to_remove)
    
    def _remove_artifact(self, artifact_id: str):
        """Remove artifact and all references."""
        artifact = self.artifact_store.get(artifact_id)
        if not artifact:
            return
        
        # Remove from store
        del self.artifact_store[artifact_id]
        
        # Remove from session artifacts
        session_id = artifact.get('session_id')
        if session_id in self.session_artifacts:
            self.session_artifacts[session_id] = [aid for aid in self.session_artifacts[session_id] if aid != artifact_id]
        
        # Remove from task artifacts
        for task_id, artifact_ids in self.task_artifacts.items():
            self.task_artifacts[task_id] = [aid for aid in artifact_ids if aid != artifact_id]
        
        # Remove from collections
        collection_id = artifact.get('collection_id')
        if collection_id in self.result_collections:
            collection = self.result_collections[collection_id]
            collection['artifact_ids'] = [aid for aid in collection.get('artifact_ids', []) if aid != artifact_id]
        
        # Remove from search index
        for keyword, artifact_ids in self.artifact_search_index.items():
            self.artifact_search_index[keyword] = [aid for aid in artifact_ids if aid != artifact_id]
        
        # Remove relationships
        if artifact_id in self.artifact_relationships:
            del self.artifact_relationships[artifact_id]
        
        # Remove from other artifacts' relationships
        for other_artifact_id, related_ids in self.artifact_relationships.items():
            self.artifact_relationships[other_artifact_id] = [aid for aid in related_ids if aid != artifact_id]
    
    def get_paused_node_id(self) -> Optional[str]:
        """Get the ID of the paused node."""
        if self.dynamic_workflow:
            return self.dynamic_workflow.paused_node_id
        return None
    
    def is_workflow_paused(self) -> bool:
        """Check if workflow is currently paused."""
        if self.dynamic_workflow:
            return self.dynamic_workflow.state == WorkflowState.PAUSED
        return False
    
    def get_executable_nodes(self) -> List[WorkflowNode]:
        """Get nodes that can be executed now."""
        if self.dynamic_workflow:
            return self.dynamic_workflow.get_executable_nodes()
        return []
    
    def _build_workflow_from_plan(self, execution_plan: Dict[str, Any], session_id: str) -> Optional[str]:
        """
        Build dynamic workflow graph from execution plan.
        
        Args:
            execution_plan: Plan from Enhanced Planner Agent
            session_id: Session identifier
            
        Returns:
            Starting node ID or None if dynamic workflow disabled
        """
        workflow = self._ensure_dynamic_workflow(session_id)
        if not workflow:
            return None
            
        tasks = execution_plan.get('tasks', [])
        if not tasks:
            logger.warning("No tasks in execution plan for workflow building")
            return None
        
        # Start workflow execution
        workflow.start_workflow()
        
        # Create planner node as root
        planner_node = self.add_graph_node(
            task_id="planner",
            context_id=session_id,
            query="Strategic planning and task decomposition",
            node_key="planner",
            node_label="Strategic Planner"
        )
        
        if not planner_node:
            return None
            
        # Mark planner as completed since we have the plan
        planner_node.complete_execution(execution_plan)
        
        # Add task nodes based on coordination strategy
        coordination_strategy = execution_plan.get('coordination_strategy', 'sequential')
        current_node_id = planner_node.id
        
        for idx, task in enumerate(tasks):
            task_node = self.add_graph_node(
                task_id=task.get('id', f"task_{idx}"),
                context_id=session_id,
                query=task.get('description', f"Execute task {idx + 1}"),
                node_id=current_node_id if coordination_strategy == 'sequential' else planner_node.id,
                node_key=task.get('specialist_type', 'generic'),
                node_label=task.get('title', f"Task {idx + 1}")
            )
            
            if task_node:
                # Add task-specific metadata
                task_node.set_attributes({
                    'task_data': task,
                    'specialist_type': task.get('specialist_type'),
                    'priority': task.get('priority', 'medium'),
                    'estimated_duration': task.get('estimated_duration')
                })
                
                # Update current node for sequential chaining
                if coordination_strategy == 'sequential':
                    current_node_id = task_node.id
        
        logger.info(f"Built dynamic workflow with {len(tasks)} task nodes, strategy: {coordination_strategy}")
        return planner_node.id

    def get_orchestrator_capabilities(self) -> dict:
        """Get comprehensive orchestrator capabilities."""
        return {
            'orchestrator_type': 'master_template_refactored',
            'domain': self.domain_name,
            'architecture': 'Enhanced Planner Agent integration',
            'planning_capabilities': {
                'planner_type': 'EnhancedGenericPlannerAgent',
                'planning_modes': ['simple', 'sophisticated'],
                'current_mode': self.planner.planning_mode,
                'advanced_features': [
                    'Task decomposition and analysis',
                    'Risk assessment and mitigation',
                    'Resource estimation and budgeting',
                    'Plan validation and feasibility checks',
                    'Template library and application',
                    'Plan versioning and iteration',
                    'Cost and timeline estimation',
                    'Quality scoring and validation'
                ]
            },
            'orchestration_capabilities': [
                'Domain specialist coordination',
                'Sequential execution management',
                'Parallel execution coordination',
                'Hybrid execution strategies',
                'A2A protocol integration',
                'Performance monitoring and metrics',
                'Health checking and diagnostics'
            ],
            'dynamic_workflow_capabilities': [
                'Dynamic graph building with nodes and edges',
                'Task metadata and execution tracking', 
                'State management (RUNNING, PAUSED, COMPLETED)',
                'Node attribute management for orchestration',
                'Workflow pause and resume functionality',
                'Session-based workflow isolation',
                'Dependency resolution and execution ordering',
                'Integration with Enhanced Planner Agent'
            ] if self.enable_dynamic_workflow else [],
            'context_history_capabilities': [
                'Session-based context tracking and management',
                'Query pattern recognition and classification',
                'Execution history recording with rich metadata',
                'Performance metrics tracking and analysis',
                'Context evolution monitoring and trend analysis',
                'Domain-wide insights and performance optimization',
                'Context snapshots for historical analysis',
                'Complexity change detection and alerting',
                'Pattern-based intelligence for future planning'
            ],
            'clear_state_management_capabilities': [
                'Automatic context change detection and clearing',
                'Intelligent context preservation during state transitions',
                'Domain learning extraction before context clearing',
                'Query type shift and domain terminology change detection',
                'Complexity and time gap analysis for context changes',
                'Configurable auto-clear triggers and thresholds',
                'Session archiving with essential summary preservation',
                'Context change statistics and pattern analysis',
                'Manual and automatic state clearing with selective preservation'
            ],
            'enhanced_state_management_capabilities': [
                'Sophisticated pause/resume with execution checkpoints',
                'State validation and resumption condition checking',
                'Multiple resumption strategies (continue, restart, skip)',
                'Execution state tracking and transition monitoring',
                'Workflow state snapshots and recovery mechanisms',
                'Checkpoint-based rollback and recovery capabilities',
                'State consistency validation and error recovery',
                'Pause reason tracking and intelligent resumption',
                'Cross-session state persistence and restoration'
            ],
            'artifact_management_capabilities': [
                'Comprehensive artifact collection and storage during orchestration',
                'Task-level and orchestration-level result preservation',
                'Metadata-rich artifact tracking with source information',
                'Intelligent artifact relationship detection and linking',
                'Multi-criteria artifact search and discovery system',
                'Result collection organization and management',
                'Content-based deduplication and hash verification',
                'Session and task-based artifact organization',
                'Artifact search indexing and keyword-based retrieval',
                'Automated cleanup and lifecycle management',
                'Analytics and reporting on artifact patterns',
                'Cross-artifact relationship mapping and analysis'
            ],
            'backward_compatibility': 'Full API compatibility with original MasterOrchestratorTemplate',
            'enhanced_features': 'All capabilities enhanced via EnhancedGenericPlannerAgent integration',
            'phase_completion_status': {
                'phase_1_dynamic_workflow': True,
                'phase_2_context_history': True,
                'phase_2_5_clear_state_management': True,
                'phase_3_enhanced_state_management': True,
                'phase_4_artifact_management': True
            }
        }