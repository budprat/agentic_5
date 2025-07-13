# ABOUTME: Lightweight Master Orchestrator using Enhanced Planner Agent for all planning tasks
# ABOUTME: Framework V2.0 orchestrator focused purely on execution coordination and agent management

"""
Lightweight Master Orchestrator Template - Framework V2.0

Streamlined orchestrator that delegates all planning, task decomposition, and analysis
to the Enhanced Planner Agent, focusing purely on execution coordination and agent management.

This creates clean separation of concerns:
- Enhanced Planner Agent = All planning intelligence
- Lightweight Orchestrator = Execution coordination only
"""

import logging
import json
import asyncio
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

# Google ADK imports
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from google.genai import types as genai_types

import os

logger = logging.getLogger(__name__)

class LightweightMasterOrchestrator(StandardizedAgentBase):
    """
    Lightweight Master Orchestrator that delegates planning to Enhanced Planner Agent.
    
    Responsibilities:
    - Agent lifecycle management
    - Task execution coordination  
    - Health monitoring
    - Resource management
    - A2A protocol coordination
    
    NOT responsible for:
    - Task decomposition (delegated to planner)
    - Risk assessment (delegated to planner)
    - Resource estimation (delegated to planner)
    - Plan validation (delegated to planner)
    """
    
    def __init__(
        self,
        domain_name: str,
        domain_description: str,
        domain_specialists: Dict[str, str],
        base_port: int = 14000,
        quality_domain: QualityDomain = QualityDomain.GENERIC,
        enable_parallel: bool = True,
        planning_mode: Literal['simple', 'sophisticated'] = 'sophisticated',
        enable_health_monitoring: bool = True
    ):
        """Initialize lightweight orchestrator with integrated planner."""
        init_api_key()
        
        agent_name = f"{domain_name} Lightweight Orchestrator"
        super().__init__(
            agent_name=agent_name,
            description=f"Lightweight orchestrator for {domain_name} domain focusing on execution coordination",
            content_types=['text', 'text/plain'],
        )
        
        # Core configuration
        self.domain_name = domain_name
        self.domain_description = domain_description
        self.domain_specialists = domain_specialists
        self.base_port = base_port
        self.enable_parallel = enable_parallel
        self.enable_health_monitoring = enable_health_monitoring
        
        # Initialize Enhanced Planner Agent for all planning tasks
        self.planner = EnhancedGenericPlannerAgent(
            domain=domain_name,
            agent_name=f"{domain_name} Strategic Planner",
            domain_specialists=domain_specialists,
            planning_mode=planning_mode,
            quality_domain=quality_domain,
            enable_quality_validation=True,
            enable_fallback_planning=True
        )
        
        # Execution tracking
        self.active_agents = {}
        self.execution_history = []
        self.current_execution_plan = None
        self.workflow_graph = None
        
        # Health monitoring
        self.health_status = {
            'orchestrator_ready': True,
            'planner_ready': True,
            'agents_ready': {},
            'last_health_check': None
        }
        
        logger.info(f"Lightweight {domain_name} Orchestrator initialized with Enhanced Planner")

    async def invoke(self, query: str, sessionId: str) -> str:
        """Main orchestration entry point - delegates planning to Enhanced Planner."""
        try:
            logger.info(f"Lightweight orchestrator processing: {query[:100]}...")
            
            # Step 1: Delegate all planning to Enhanced Planner Agent
            plan_response = await self._get_execution_plan(query, sessionId)
            
            if not plan_response or plan_response.get('response_type') != 'data':
                return self._format_error_response("Failed to generate execution plan")
            
            execution_plan = plan_response['content']
            self.current_execution_plan = execution_plan
            
            # Step 2: Execute the plan using orchestration capabilities
            execution_result = await self._execute_plan(execution_plan, sessionId)
            
            # Step 3: Monitor and coordinate execution
            final_result = await self._monitor_execution(execution_result, sessionId)
            
            return self._format_success_response(final_result)
            
        except Exception as e:
            logger.error(f"Orchestration error: {e}")
            return self._format_error_response(f"Orchestration failed: {str(e)}")

    async def stream(self, query: str, sessionId: str, task_id: str) -> AsyncIterable[dict[str, Any]]:
        """Stream orchestration progress with planning delegation."""
        try:
            yield {
                'response_type': 'text',
                'is_task_complete': False,
                'require_user_input': False,
                'content': f'🎯 Starting {self.domain_name} orchestration...',
                'stage': 'initialization'
            }
            
            # Step 1: Stream planning phase
            yield {
                'response_type': 'text',
                'is_task_complete': False,
                'require_user_input': False,
                'content': '📋 Delegating to Enhanced Planner for strategic analysis...',
                'stage': 'planning'
            }
            
            # Get execution plan from Enhanced Planner
            plan_response = await self._get_execution_plan(query, sessionId)
            
            if not plan_response or plan_response.get('response_type') != 'data':
                yield {
                    'response_type': 'text',
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': '❌ Planning phase failed',
                    'stage': 'error'
                }
                return
            
            execution_plan = plan_response['content']
            tasks = execution_plan.get('tasks', [])
            
            yield {
                'response_type': 'text',
                'is_task_complete': False,
                'require_user_input': False,
                'content': f'✅ Plan generated: {len(tasks)} tasks, {execution_plan.get("coordination_strategy")} execution',
                'stage': 'planning_complete'
            }
            
            # Step 2: Stream execution coordination
            yield {
                'response_type': 'text',
                'is_task_complete': False,
                'require_user_input': False,
                'content': '🚀 Beginning execution coordination...',
                'stage': 'execution_start'
            }
            
            # Execute tasks with progress streaming
            execution_result = await self._stream_execution(execution_plan, sessionId)
            
            # Stream execution progress
            async for progress in execution_result:
                yield progress
            
            # Final completion
            yield {
                'response_type': 'text',
                'is_task_complete': True,
                'require_user_input': False,
                'content': f'🎉 {self.domain_name} orchestration completed successfully',
                'stage': 'completion'
            }
            
        except Exception as e:
            logger.error(f"Stream orchestration error: {e}")
            yield {
                'response_type': 'text',
                'is_task_complete': True,
                'require_user_input': False,
                'content': f'❌ Orchestration failed: {str(e)}',
                'stage': 'error'
            }

    async def _get_execution_plan(self, query: str, sessionId: str) -> dict:
        """Delegate all planning to Enhanced Planner Agent."""
        try:
            # Use Enhanced Planner for all planning intelligence
            plan_response = self.planner.invoke(query, sessionId)
            
            # Additional orchestrator-specific enhancements
            if plan_response.get('response_type') == 'data':
                plan_content = plan_response['content']
                
                # Add orchestrator-specific metadata
                plan_content['orchestrator_metadata'] = {
                    'orchestrator_type': 'lightweight',
                    'domain': self.domain_name,
                    'parallel_enabled': self.enable_parallel,
                    'base_port': self.base_port,
                    'specialist_assignments': self._assign_specialists_to_tasks(plan_content.get('tasks', []))
                }
                
                # Enhance with agent lifecycle information
                plan_content['agent_lifecycle'] = self._plan_agent_lifecycle(plan_content.get('tasks', []))
            
            return plan_response
            
        except Exception as e:
            logger.error(f"Planning delegation error: {e}")
            return {'response_type': 'error', 'content': f'Planning failed: {str(e)}'}

    def _assign_specialists_to_tasks(self, tasks: List[dict]) -> Dict[str, str]:
        """Map tasks to specific specialist agents with port assignments."""
        assignments = {}
        port_offset = 0
        
        for task in tasks:
            task_id = task.get('id', 'unknown')
            suggested_specialist = task.get('agent_type', 'generalist')
            
            # Map to actual specialist from domain configuration
            if suggested_specialist in self.domain_specialists:
                specialist_name = suggested_specialist
            else:
                # Find best match from configured specialists
                specialist_name = self._match_specialist(suggested_specialist)
            
            assignments[task_id] = {
                'specialist': specialist_name,
                'port': self.base_port + port_offset,
                'description': self.domain_specialists.get(specialist_name, 'General specialist')
            }
            port_offset += 1
            
        return assignments

    def _match_specialist(self, suggested_type: str) -> str:
        """Match suggested specialist type to available domain specialists."""
        # Simple keyword matching - can be enhanced
        suggested_lower = suggested_type.lower()
        
        for specialist_key in self.domain_specialists.keys():
            if suggested_lower in specialist_key.lower() or specialist_key.lower() in suggested_lower:
                return specialist_key
        
        # Fallback to first available specialist
        return list(self.domain_specialists.keys())[0] if self.domain_specialists else 'generalist'

    def _plan_agent_lifecycle(self, tasks: List[dict]) -> Dict[str, Any]:
        """Plan agent lifecycle for task execution."""
        return {
            'agents_needed': len(set(task.get('agent_type', 'generalist') for task in tasks)),
            'startup_sequence': 'parallel' if self.enable_parallel else 'sequential',
            'health_check_interval': 30,  # seconds
            'max_retry_attempts': 3,
            'graceful_shutdown': True
        }

    async def _execute_plan(self, execution_plan: dict, sessionId: str) -> dict:
        """Execute the plan focusing on coordination, not planning."""
        try:
            tasks = execution_plan.get('tasks', [])
            coordination_strategy = execution_plan.get('coordination_strategy', 'sequential')
            
            # Initialize agents based on specialist assignments
            await self._initialize_execution_agents(execution_plan)
            
            # Execute based on coordination strategy
            if coordination_strategy == 'parallel':
                result = await self._execute_parallel(tasks, sessionId)
            elif coordination_strategy == 'hybrid':
                result = await self._execute_hybrid(tasks, sessionId)
            else:  # sequential
                result = await self._execute_sequential(tasks, sessionId)
            
            return {
                'execution_strategy': coordination_strategy,
                'tasks_completed': len([t for t in result.get('task_results', []) if t.get('status') == 'completed']),
                'total_tasks': len(tasks),
                'execution_time': result.get('total_time', 0),
                'results': result
            }
            
        except Exception as e:
            logger.error(f"Plan execution error: {e}")
            return {'error': str(e), 'status': 'failed'}

    async def _initialize_execution_agents(self, execution_plan: dict):
        """Initialize specialist agents for task execution."""
        specialist_assignments = execution_plan.get('orchestrator_metadata', {}).get('specialist_assignments', {})
        
        for task_id, assignment in specialist_assignments.items():
            specialist = assignment['specialist']
            port = assignment['port']
            
            if specialist not in self.active_agents:
                # Initialize agent (simulation - in real implementation would spawn actual agents)
                self.active_agents[specialist] = {
                    'port': port,
                    'status': 'initialized',
                    'tasks_assigned': [],
                    'health': 'healthy'
                }
                
                logger.info(f"Initialized {specialist} agent on port {port}")

    async def _execute_sequential(self, tasks: List[dict], sessionId: str) -> dict:
        """Execute tasks sequentially with coordination."""
        results = []
        start_time = datetime.now()
        
        for task in tasks:
            task_result = await self._execute_single_task(task, sessionId)
            results.append(task_result)
            
            # Health check between tasks
            if self.enable_health_monitoring:
                await self._perform_health_check()
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'strategy': 'sequential',
            'task_results': results,
            'total_time': execution_time,
            'health_checks_performed': len(tasks) if self.enable_health_monitoring else 0
        }

    async def _execute_parallel(self, tasks: List[dict], sessionId: str) -> dict:
        """Execute tasks in parallel with coordination."""
        start_time = datetime.now()
        
        # Create async tasks for parallel execution
        task_coroutines = [
            self._execute_single_task(task, sessionId) 
            for task in tasks
        ]
        
        # Execute in parallel
        results = await asyncio.gather(*task_coroutines, return_exceptions=True)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'strategy': 'parallel',
            'task_results': results,
            'total_time': execution_time,
            'parallel_efficiency': len(tasks) / max(execution_time, 1)
        }

    async def _execute_hybrid(self, tasks: List[dict], sessionId: str) -> dict:
        """Execute tasks using hybrid strategy (sequential + parallel batches)."""
        # Group tasks by dependencies for hybrid execution
        independent_tasks = [t for t in tasks if not t.get('dependencies', [])]
        dependent_tasks = [t for t in tasks if t.get('dependencies', [])]
        
        start_time = datetime.now()
        results = []
        
        # Execute independent tasks in parallel
        if independent_tasks:
            parallel_results = await self._execute_parallel(independent_tasks, sessionId)
            results.extend(parallel_results['task_results'])
        
        # Execute dependent tasks sequentially
        if dependent_tasks:
            sequential_results = await self._execute_sequential(dependent_tasks, sessionId)
            results.extend(sequential_results['task_results'])
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'strategy': 'hybrid',
            'task_results': results,
            'total_time': execution_time,
            'parallel_batch_size': len(independent_tasks),
            'sequential_batch_size': len(dependent_tasks)
        }

    async def _execute_single_task(self, task: dict, sessionId: str) -> dict:
        """Execute a single task using appropriate specialist."""
        try:
            task_id = task.get('id', 'unknown')
            task_description = task.get('description', '')
            
            # Simulate task execution (in real implementation, would delegate to specialist agent)
            await asyncio.sleep(0.1)  # Simulate execution time
            
            return {
                'task_id': task_id,
                'status': 'completed',
                'execution_time': 0.1,
                'description': task_description,
                'result': f"Simulated completion of: {task_description[:50]}..."
            }
            
        except Exception as e:
            return {
                'task_id': task.get('id', 'unknown'),
                'status': 'failed',
                'error': str(e),
                'execution_time': 0
            }

    async def _stream_execution(self, execution_plan: dict, sessionId: str):
        """Stream execution progress."""
        tasks = execution_plan.get('tasks', [])
        
        for i, task in enumerate(tasks, 1):
            yield {
                'response_type': 'text',
                'is_task_complete': False,
                'require_user_input': False,
                'content': f'⚡ Executing task {i}/{len(tasks)}: {task.get("description", "")[:60]}...',
                'stage': 'task_execution',
                'progress': i / len(tasks)
            }
            
            # Simulate task execution
            await asyncio.sleep(0.2)
            
            yield {
                'response_type': 'text',
                'is_task_complete': False,
                'require_user_input': False,
                'content': f'✅ Completed task {i}: {task.get("description", "")[:40]}...',
                'stage': 'task_complete',
                'progress': i / len(tasks)
            }

    async def _monitor_execution(self, execution_result: dict, sessionId: str) -> dict:
        """Monitor execution and provide final coordination."""
        if self.enable_health_monitoring:
            await self._perform_health_check()
        
        # Add orchestrator analysis to results
        execution_result['orchestrator_analysis'] = {
            'total_agents_used': len(self.active_agents),
            'execution_efficiency': self._calculate_execution_efficiency(execution_result),
            'recommendations': self._generate_execution_recommendations(execution_result)
        }
        
        return execution_result

    async def _perform_health_check(self):
        """Perform health check on orchestrator and agents."""
        self.health_status['last_health_check'] = datetime.now().isoformat()
        
        # Check agent health
        for agent_name, agent_info in self.active_agents.items():
            # Simulate health check
            agent_info['health'] = 'healthy'
            self.health_status['agents_ready'][agent_name] = True

    def _calculate_execution_efficiency(self, execution_result: dict) -> float:
        """Calculate execution efficiency score."""
        total_tasks = execution_result.get('total_tasks', 1)
        completed_tasks = execution_result.get('tasks_completed', 0)
        
        return round(completed_tasks / total_tasks, 2)

    def _generate_execution_recommendations(self, execution_result: dict) -> List[str]:
        """Generate recommendations for future executions."""
        recommendations = []
        
        efficiency = self._calculate_execution_efficiency(execution_result)
        
        if efficiency < 0.8:
            recommendations.append("Consider reviewing task complexity and resource allocation")
        
        if execution_result.get('execution_strategy') == 'sequential' and execution_result.get('total_tasks', 0) > 5:
            recommendations.append("Consider parallel execution for better performance")
        
        if not recommendations:
            recommendations.append("Execution performed optimally")
        
        return recommendations

    def _format_success_response(self, result: dict) -> str:
        """Format successful orchestration response."""
        return json.dumps({
            'status': 'completed',
            'domain': self.domain_name,
            'orchestrator_type': 'lightweight',
            'execution_summary': result.get('orchestrator_analysis', {}),
            'planner_integration': 'Enhanced Planner Agent used for all planning tasks',
            'result': result
        }, indent=2)

    def _format_error_response(self, error_message: str) -> str:
        """Format error response."""
        return json.dumps({
            'status': 'error',
            'domain': self.domain_name,
            'orchestrator_type': 'lightweight',
            'error': error_message,
            'timestamp': datetime.now().isoformat()
        }, indent=2)

    def get_orchestrator_status(self) -> dict:
        """Get current orchestrator status and capabilities."""
        return {
            'orchestrator_type': 'lightweight',
            'domain': self.domain_name,
            'planner_integration': {
                'planner_type': 'EnhancedGenericPlannerAgent',
                'planning_mode': self.planner.planning_mode,
                'capabilities_delegated': [
                    'Task decomposition',
                    'Risk assessment', 
                    'Resource estimation',
                    'Plan validation',
                    'Template application',
                    'Quality assessment'
                ]
            },
            'orchestrator_responsibilities': [
                'Agent lifecycle management',
                'Task execution coordination',
                'Health monitoring', 
                'Resource management',
                'A2A protocol coordination'
            ],
            'active_agents': len(self.active_agents),
            'health_status': self.health_status,
            'execution_history': len(self.execution_history)
        }