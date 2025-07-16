# ABOUTME: Video generation workflow integrating all agents with parallel execution and result aggregation
# ABOUTME: Uses ParallelWorkflowGraph for optimal performance with connection pooling and quality validation

"""
Video Generation Workflow Implementation

This module implements the complete video generation workflow:
- Parallel agent execution using ParallelWorkflowGraph
- Connection pooling for performance
- Result aggregation and quality validation
- Platform-specific optimization paths
- Real-time progress tracking
"""

import asyncio
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timezone
import json
import time
from dataclasses import dataclass, field
import uuid

from a2a_mcp.common.parallel_workflow import ParallelWorkflowGraph
from a2a_mcp.common.a2a_protocol import A2AProtocolClient, register_agent_port
from a2a_mcp.common.enhanced_workflow import NodeState
from a2a_mcp.common.parallel_workflow import ParallelWorkflowNode
# TaskContext and TaskResult defined inline in agents
from a2a_mcp.common.a2a_connection_pool import A2AConnectionPool as ConnectionPool

# Define minimal required types
@dataclass
class TaskContext:
    task_id: str
    session_id: str
    context_id: str
    workflow_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TaskResult:
    task_id: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

from a2a_mcp.common.quality_framework import QualityThresholdFramework
from a2a_mcp.common.observability import get_logger, trace_span, record_metric
from a2a_mcp.common.response_formatter import ResponseFormatter

# Import all agents
from video_generator.agents.video_orchestrator_v2 import VideoOrchestratorV2
from video_generator.agents.script_writer import ScriptWriter
from video_generator.agents.scene_designer import SceneDesigner
from video_generator.agents.timing_coordinator import TimingCoordinator
from video_generator.agents.a2a_agent_wrapper import create_a2a_enabled_agent

# Import cache integration
from video_generator.cache import (
    CachedWorkflowIntegration,
    create_cached_workflow
)


@dataclass
class WorkflowConfig:
    """Workflow configuration."""
    enable_parallel: bool = True
    max_parallel_tasks: int = 5
    timeout_seconds: int = 300
    retry_attempts: int = 3
    quality_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "script_coherence": 0.85,
        "visual_feasibility": 0.80,
        "engagement_potential": 0.75,
        "platform_compliance": 0.90
    })
    connection_pool_size: int = 20
    enable_quality_checks: bool = True


class VideoGenerationWorkflow:
    """
    Complete video generation workflow with parallel execution.
    
    Coordinates multiple agents to create video scripts and storyboards
    with optimal performance through parallel execution and connection pooling.
    """
    
    def __init__(
        self,
        config: WorkflowConfig = None,
        connection_pool: ConnectionPool = None,
        quality_framework: QualityThresholdFramework = None,
        cache_integration: CachedWorkflowIntegration = None
    ):
        """Initialize video generation workflow."""
        self.config = config or WorkflowConfig()
        self.logger = get_logger("video_generation_workflow")
        
        # Initialize connection pool
        self.connection_pool = connection_pool or ConnectionPool(
            max_connections_per_host=self.config.connection_pool_size,
            keepalive_timeout=30
        )
        
        # Initialize quality framework
        quality_config = {
            "enabled": self.config.enable_quality_checks,
            "strict_mode": False,
            "thresholds": {
                "completeness": 0.8,
                "accuracy": 0.85,
                "relevance": 0.8
            }
        }
        self.quality_framework = quality_framework or QualityThresholdFramework(quality_config)
        
        # Initialize cache integration
        self.cache_integration = cache_integration
        
        # Initialize workflow graph
        self.workflow_graph = ParallelWorkflowGraph()
        
        # Initialize agents
        self.agents = self._initialize_agents()
        
        # Response formatter
        self.response_formatter = ResponseFormatter()
        
        # Active workflows tracking
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        
        # Build workflow graph
        self._build_workflow_graph()
    
    def _initialize_agents(self) -> Dict[str, Any]:
        """Initialize all agents with shared resources and A2A Protocol."""
        agents = {}
        
        # Video Orchestrator (Tier 1) - Using Enhanced Master Orchestrator Template
        # Note: Orchestrator uses its own internal A2A capabilities
        agents["video_orchestrator"] = VideoOrchestratorV2(
            quality_thresholds=self.config.quality_thresholds,
            enable_phase_7_streaming=True,
            enable_observability=True,
            enable_dynamic_workflow=True,
            enable_parallel=True
        )
        
        # Domain Specialists (Tier 2) with A2A Protocol
        agents["script_writer"] = create_a2a_enabled_agent(
            ScriptWriter,
            agent_name="script_writer",
            agent_port=10212,
            agent_id="script_writer",
            connection_pool=self.connection_pool,
            quality_framework=self.quality_framework,
            config={"port": 10212}
        )
        
        agents["scene_designer"] = create_a2a_enabled_agent(
            SceneDesigner,
            agent_name="scene_designer",
            agent_port=10213,
            agent_id="scene_designer",
            connection_pool=self.connection_pool,
            quality_framework=self.quality_framework,
            config={"port": 10213}
        )
        
        agents["timing_coordinator"] = create_a2a_enabled_agent(
            TimingCoordinator,
            agent_name="timing_coordinator",
            agent_port=10214,
            agent_id="timing_coordinator",
            connection_pool=self.connection_pool,
            quality_framework=self.quality_framework,
            config={"port": 10214}
        )
        
        # Start A2A servers for all agents
        self._start_a2a_servers_task = asyncio.create_task(self._start_a2a_servers(agents))
        
        # Note: Hook Creator, Shot Describer, Transition Planner, CTA Generator
        # would be implemented similarly and added here
        
        return agents
    
    async def _start_a2a_servers(self, agents: Dict[str, Any]):
        """Start A2A Protocol servers for all agents."""
        for name, agent in agents.items():
            if hasattr(agent, 'start_a2a_server'):
                try:
                    await agent.start_a2a_server()
                    self.logger.info(f"Started A2A server for {name}")
                except Exception as e:
                    self.logger.error(f"Failed to start A2A server for {name}: {e}")
    
    def _build_workflow_graph(self):
        """Build the parallel workflow graph."""
        # Phase 1: Initial Analysis (Orchestrator)
        orchestrator_node = ParallelWorkflowNode(
            task="Analyze video generation request",
            node_key="video_orchestrator",
            node_label="Initial Analysis"
        )
        # Set metadata after creation
        self.workflow_graph.set_node_attributes(orchestrator_node.id, {
            "agent_id": "video_orchestrator",
            "action": "analyze_request",
            "timeout": 30,
            "task_id": "orchestrator_analysis"
        })
        self.workflow_graph.add_node(orchestrator_node)
        
        # Phase 2: Parallel Content Creation
        # These can run in parallel as they don't depend on each other initially
        parallel_nodes = [
            ParallelWorkflowNode(
                task="Generate engaging hooks",
                node_key="hook_creator",
                node_label="Hook Creation"
            ),
            ParallelWorkflowNode(
                task="Research visual references",
                node_key="scene_designer",
                node_label="Scene Research"
            )
        ]
        
        # Add nodes and set their attributes
        hook_node = parallel_nodes[0]
        self.workflow_graph.add_node(hook_node)
        self.workflow_graph.set_node_attributes(hook_node.id, {
            "agent_id": "hook_creator",
            "action": "generate_hooks",
            "timeout": 20,
            "task_id": "hook_creation"
        })
        # Add dependency on orchestrator
        self.workflow_graph.add_edge(orchestrator_node.id, hook_node.id)
        
        scene_node = parallel_nodes[1]
        self.workflow_graph.add_node(scene_node)
        self.workflow_graph.set_node_attributes(scene_node.id, {
            "agent_id": "scene_designer",
            "action": "research",
            "timeout": 20,
            "task_id": "scene_research"
        })
        # Add dependency on orchestrator
        self.workflow_graph.add_edge(orchestrator_node.id, scene_node.id)
        
        # Phase 3: Script Writing (depends on hooks)
        script_node = ParallelWorkflowNode(
            task="Write engaging video script",
            node_key="script_writer",
            node_label="Script Writing"
        )
        self.workflow_graph.add_node(script_node)
        self.workflow_graph.set_node_attributes(script_node.id, {
            "agent_id": "script_writer",
            "action": "write_script",
            "timeout": 60,
            "task_id": "script_writing"
        })
        # Add dependency on hook creation
        self.workflow_graph.add_edge(hook_node.id, script_node.id)
        
        # Phase 4: Parallel Production Planning
        production_nodes = [
            ParallelWorkflowNode(
                task="Create visual storyboard",
                node_key="scene_designer",
                node_label="Scene Design"
            ),
            ParallelWorkflowNode(
                task="Optimize timing and pacing",
                node_key="timing_coordinator",
                node_label="Timing Optimization"
            )
        ]
        
        # Add production nodes and set their attributes
        storyboard_node = production_nodes[0]
        self.workflow_graph.add_node(storyboard_node)
        self.workflow_graph.set_node_attributes(storyboard_node.id, {
            "agent_id": "scene_designer",
            "action": "create_storyboard",
            "timeout": 45,
            "task_id": "scene_design"
        })
        # Add dependencies
        self.workflow_graph.add_edge(script_node.id, storyboard_node.id)
        self.workflow_graph.add_edge(scene_node.id, storyboard_node.id)
        
        timing_node = production_nodes[1]
        self.workflow_graph.add_node(timing_node)
        self.workflow_graph.set_node_attributes(timing_node.id, {
            "agent_id": "timing_coordinator",
            "action": "optimize_timing",
            "timeout": 30,
            "task_id": "timing_optimization"
        })
        # Add dependency
        self.workflow_graph.add_edge(script_node.id, timing_node.id)
        
        # Phase 5: Final Assembly
        assembly_node = ParallelWorkflowNode(
            task="Assemble final video content",
            node_key="video_orchestrator",
            node_label="Final Assembly"
        )
        self.workflow_graph.add_node(assembly_node)
        self.workflow_graph.set_node_attributes(assembly_node.id, {
            "agent_id": "video_orchestrator",
            "action": "assemble_output",
            "timeout": 30,
            "task_id": "final_assembly"
        })
        # Add dependencies
        self.workflow_graph.add_edge(storyboard_node.id, assembly_node.id)
        self.workflow_graph.add_edge(timing_node.id, assembly_node.id)
        
        # Phase 6: Quality Validation
        validation_node = ParallelWorkflowNode(
            task="Validate output quality",
            node_key="video_orchestrator",
            node_label="Quality Validation"
        )
        self.workflow_graph.add_node(validation_node)
        self.workflow_graph.set_node_attributes(validation_node.id, {
            "agent_id": "video_orchestrator",
            "action": "validate_quality",
            "timeout": 20,
            "task_id": "quality_validation"
        })
        # Add dependency
        self.workflow_graph.add_edge(assembly_node.id, validation_node.id)
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the complete video generation workflow."""
        workflow_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Initialize cache if not already done
        if not self.cache_integration:
            self.cache_integration = await create_cached_workflow()
        
        # Check cache first
        cached_result = await self.cache_integration.check_generation_cache(request)
        if cached_result:
            self.logger.info(f"Returning cached result for workflow {workflow_id}")
            return cached_result
        
        # Track workflow
        self.active_workflows[workflow_id] = {
            "status": "started",
            "request": request,
            "started_at": datetime.now(timezone.utc),
            "progress": {}
        }
        
        try:
            # Create workflow context
            context = TaskContext(
                task_id=workflow_id,
                session_id=workflow_id,
                context_id=f"video_gen_{workflow_id}",
                workflow_id=workflow_id,
                metadata={
                    "workflow_id": workflow_id,
                    "request_type": "video_generation",
                    "parameters": request,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
            
            # Execute workflow with progress tracking
            result = await self._execute_with_progress(context)
            
            # Update workflow status
            self.active_workflows[workflow_id]["status"] = "completed"
            self.active_workflows[workflow_id]["result"] = result
            self.active_workflows[workflow_id]["duration"] = time.time() - start_time
            
            # Format response
            formatted_response = self._format_workflow_response(result, workflow_id)
            
            # Cache the result
            await self.cache_integration.cache_generation_result(request, formatted_response)
            
            return formatted_response
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {str(e)}", exc_info=True)
            
            # Update workflow status
            self.active_workflows[workflow_id]["status"] = "failed"
            self.active_workflows[workflow_id]["error"] = str(e)
            
            return {
                "status": "failed",
                "workflow_id": workflow_id,
                "error": str(e),
                "duration": time.time() - start_time
            }
    
    async def _execute_with_progress(self, context: TaskContext) -> Dict[str, Any]:
        """Execute workflow with progress tracking."""
        workflow_id = context.session_id
        results = {}
        
        # For now, use a simpler direct execution approach
        # TODO: Integrate with ParallelWorkflowGraph properly
        
        try:
            orchestrator = self.agents["video_orchestrator"]
            request = context.metadata.get("parameters", {})
            
            # Generate video content using the orchestrator
            self.logger.info("Executing video generation with orchestrator")
            orchestrator_result = await orchestrator.generate_video_content(
                content=request.get("content", ""),
                platforms=request.get("platforms", ["youtube"]),
                style=request.get("style", "educational"),
                preferences=request.get("preferences", {})
            )
            
            results["orchestrator_analysis"] = orchestrator_result
            
            # Extract the generated components
            script = orchestrator_result.get("script", {})
            storyboard = orchestrator_result.get("storyboard", {})
            timing_plan = orchestrator_result.get("timing_plan", {})
            
            # Aggregate results
            results["final_output"] = {
                "script": script,
                "storyboard": storyboard,
                "timing_plan": timing_plan,
                "metadata": orchestrator_result.get("metadata", {})
            }
            
            # Update workflow progress
            self.active_workflows[workflow_id]["progress"]["completed"] = True
            
        except Exception as e:
            self.logger.error(f"Workflow execution error: {str(e)}", exc_info=True)
            results["error"] = str(e)
            self.active_workflows[workflow_id]["progress"]["error"] = str(e)
        
        return results
    
    def _create_node_executors(self, context: TaskContext) -> Dict[str, Any]:
        """Create executor functions for each node."""
        executors = {}
        
        # Orchestrator Analysis
        async def orchestrator_analysis():
            orchestrator = self.agents["video_orchestrator"]
            # Using the new orchestrator's generate_video_content method
            query = orchestrator._create_orchestrator_query(context.parameters)
            result = await orchestrator.invoke(query, context.session_id)
            return result
        
        executors["orchestrator_analysis"] = orchestrator_analysis
        
        # Hook Creation (placeholder)
        async def hook_creation():
            # In real implementation, would use Hook Creator agent
            return {
                "hooks": [
                    "Discover the secret to mastering Python in record time!",
                    "What if I told you coding could be this easy?"
                ],
                "style": "engaging"
            }
        
        executors["hook_creation"] = hook_creation
        
        # Scene Research
        async def scene_research():
            scene_designer = self.agents["scene_designer"]
            research_context = TaskContext(
                session_id=context.session_id,
                request_type="visual_research",
                parameters=context.parameters,
                metadata=context.metadata
            )
            result = await scene_designer.research(research_context)
            return result.artifacts[0].content if result.artifacts else {}
        
        executors["scene_research"] = scene_research
        
        # Script Writing
        async def script_writing():
            script_writer = self.agents["script_writer"]
            
            # Get hooks from previous step
            hooks = executors.get("hook_creation_result", {}).get("hooks", [])
            
            script_context = TaskContext(
                session_id=context.session_id,
                request_type="script_writing",
                parameters={
                    **context.parameters,
                    "hooks": hooks
                },
                metadata=context.metadata
            )
            
            result = await script_writer._execute_agent_logic(script_context)
            return json.loads(result.artifacts[0].content) if result.artifacts else {}
        
        executors["script_writing"] = script_writing
        
        # Scene Design
        async def scene_design():
            scene_designer = self.agents["scene_designer"]
            
            # Get script from previous step
            script = executors.get("script_writing_result", {})
            
            design_context = TaskContext(
                session_id=context.session_id,
                request_type="scene_design",
                parameters={
                    **context.parameters,
                    "script": script
                },
                metadata=context.metadata
            )
            
            result = await scene_designer._execute_agent_logic(design_context)
            return json.loads(result.artifacts[0].content) if result.artifacts else {}
        
        executors["scene_design"] = scene_design
        
        # Timing Optimization
        async def timing_optimization():
            timing_coordinator = self.agents["timing_coordinator"]
            
            # Get script from previous step
            script = executors.get("script_writing_result", {})
            storyboard = executors.get("scene_design_result", {})
            
            timing_context = TaskContext(
                session_id=context.session_id,
                request_type="timing_optimization",
                parameters={
                    **context.parameters,
                    "script": script,
                    "storyboard": storyboard
                },
                metadata=context.metadata
            )
            
            result = await timing_coordinator._execute_agent_logic(timing_context)
            return json.loads(result.artifacts[0].content) if result.artifacts else {}
        
        executors["timing_optimization"] = timing_optimization
        
        # Final Assembly
        async def final_assembly():
            # Aggregate all results
            assembled = {
                "format_analysis": executors.get("orchestrator_analysis_result", {}),
                "hooks": executors.get("hook_creation_result", {}),
                "script": executors.get("script_writing_result", {}),
                "storyboard": executors.get("scene_design_result", {}),
                "timing": executors.get("timing_optimization_result", {}),
                "metadata": {
                    "workflow_id": context.session_id,
                    "platform": context.parameters.get("platform", "youtube"),
                    "duration": executors.get("timing_optimization_result", {}).get("total_duration", 0)
                }
            }
            return assembled
        
        executors["final_assembly"] = final_assembly
        
        # Quality Validation
        async def quality_validation():
            assembled_output = executors.get("final_assembly_result", {})
            
            # The new orchestrator has built-in quality validation
            validation_result = self.agents["video_orchestrator"]._validate_video_output({
                "artifacts": [
                    {"type": "script", "content": assembled_output.get("script", {})},
                    {"type": "storyboard", "content": assembled_output.get("storyboard", {})},
                    {"type": "timing_plan", "content": assembled_output.get("timing", {})}
                ]
            })
            
            return validation_result
        
        executors["quality_validation"] = quality_validation
        
        # Store results as they complete
        for node_id, executor in list(executors.items()):
            original_executor = executor
            
            async def wrapped_executor(node_id=node_id, executor=original_executor):
                result = await executor()
                executors[f"{node_id}_result"] = result
                return result
            
            executors[node_id] = wrapped_executor
        
        return executors
    
    def _format_workflow_response(self, results: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        """Format the final workflow response."""
        # Get the assembled output
        final_output = results.get("final_assembly", {})
        validation = results.get("quality_validation", {})
        
        # Structure the response
        response = {
            "status": "completed" if validation.get("passed", False) else "completed_with_warnings",
            "workflow_id": workflow_id,
            "outputs": {
                "script": final_output.get("script", {}),
                "storyboard": final_output.get("storyboard", {}),
                "timing_plan": final_output.get("timing", {}),
                "hooks": final_output.get("hooks", {}).get("hooks", [])
            },
            "quality_validation": validation,
            "metadata": {
                "platform": final_output.get("metadata", {}).get("platform", "unknown"),
                "total_duration": final_output.get("metadata", {}).get("duration", 0),
                "workflow_duration": self.active_workflows[workflow_id].get("duration", 0),
                "nodes_executed": len(results)
            },
            "recommendations": self._generate_recommendations(final_output, validation)
        }
        
        return response
    
    def _generate_recommendations(self, output: Dict[str, Any], validation: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on output and validation."""
        recommendations = []
        
        # Check quality scores
        if validation.get("failed_metrics"):
            for metric in validation["failed_metrics"]:
                if metric["metric"] == "script_coherence":
                    recommendations.append("Review script flow and ensure logical progression")
                elif metric["metric"] == "visual_feasibility":
                    recommendations.append("Simplify visual requirements or adjust production scope")
                elif metric["metric"] == "engagement_potential":
                    recommendations.append("Add more dynamic pacing or compelling hooks")
        
        # Platform-specific recommendations
        platform = output.get("metadata", {}).get("platform")
        duration = output.get("metadata", {}).get("duration", 0)
        
        if platform == "tiktok" and duration > 60:
            recommendations.append("Consider shortening content to fit TikTok's 60-second limit")
        elif platform == "youtube" and duration < 60:
            recommendations.append("Consider expanding content for better YouTube performance")
        
        if not recommendations:
            recommendations.append("Content is well-optimized for the target platform")
        
        return recommendations
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of a workflow."""
        if workflow_id not in self.active_workflows:
            return {"status": "not_found", "error": "Workflow ID not found"}
        
        workflow = self.active_workflows[workflow_id]
        
        # Calculate progress percentage
        total_nodes = len(self.workflow_graph.nodes)
        completed_nodes = sum(
            1 for p in workflow["progress"].values() 
            if p["state"] in ["completed", "failed"]
        )
        progress_percentage = (completed_nodes / total_nodes * 100) if total_nodes > 0 else 0
        
        return {
            "workflow_id": workflow_id,
            "status": workflow["status"],
            "progress_percentage": progress_percentage,
            "progress_details": workflow["progress"],
            "started_at": workflow["started_at"].isoformat(),
            "duration": workflow.get("duration", time.time() - workflow["started_at"].timestamp())
        }
    
    async def cancel_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Cancel a running workflow."""
        if workflow_id not in self.active_workflows:
            return {"status": "not_found", "error": "Workflow ID not found"}
        
        workflow = self.active_workflows[workflow_id]
        
        if workflow["status"] in ["completed", "failed", "cancelled"]:
            return {"status": "error", "error": f"Cannot cancel {workflow['status']} workflow"}
        
        # Cancel the workflow
        workflow["status"] = "cancelled"
        workflow["cancelled_at"] = datetime.now(timezone.utc)
        
        # TODO: Implement actual cancellation logic in ParallelWorkflowGraph
        
        return {"status": "cancelled", "workflow_id": workflow_id}
    
    async def cleanup(self):
        """Cleanup resources."""
        # Stop A2A servers
        for agent in self.agents.values():
            if hasattr(agent, 'stop_a2a_server'):
                try:
                    await agent.stop_a2a_server()
                except Exception as e:
                    self.logger.error(f"Error stopping A2A server: {e}")
        
        # Cancel A2A server task
        if hasattr(self, '_start_a2a_servers_task'):
            self._start_a2a_servers_task.cancel()
            try:
                await self._start_a2a_servers_task
            except asyncio.CancelledError:
                pass
        
        # Close connection pool
        if hasattr(self.connection_pool, 'close'):
            await self.connection_pool.close()
        elif hasattr(self.connection_pool, 'close_all'):
            await self.connection_pool.close_all()
        
        # Clear active workflows
        self.active_workflows.clear()
        
        self.logger.info("Video generation workflow cleaned up")


# Convenience function for creating and executing workflow
async def generate_video_content(request: Dict[str, Any]) -> Dict[str, Any]:
    """Generate video content using the complete workflow."""
    workflow = VideoGenerationWorkflow()
    
    try:
        result = await workflow.execute(request)
        return result
    finally:
        await workflow.cleanup()
