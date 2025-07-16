# ABOUTME: Video Orchestrator agent that coordinates multi-agent video script and storyboard generation
# ABOUTME: Extends StandardizedAgentBase with format detection, workflow planning, and quality validation

"""
Video Orchestrator Agent Implementation

This module implements the central orchestrator for video generation:
- Format detection for different platforms
- Workflow planning and execution
- Parallel task coordination
- Quality validation
- Progress tracking
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple, Callable, ClassVar
from datetime import datetime, timezone
import json
import time
from dataclasses import dataclass, field
try:
    import google.generativeai as genai
except ImportError:
    from google import genai

from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.common.enhanced_workflow import WorkflowState, NodeState
from a2a_mcp.common.a2a_connection_pool import A2AConnectionPool as ConnectionPool

# Define minimal required types
from dataclasses import dataclass as _dataclass
from typing import Dict as _Dict, Any as _Any, Optional as _Optional

@_dataclass
class TaskContext:
    task_id: str
    session_id: str
    context_id: str
    workflow_id: _Optional[str] = None
    metadata: _Dict[str, _Any] = field(default_factory=dict)

@_dataclass
class TaskResult:
    task_id: str
    status: str
    result: _Optional[_Any] = None
    error: _Optional[str] = None
    metadata: _Dict[str, _Any] = field(default_factory=dict)

@_dataclass
class ArtifactData:
    artifact_type: str
    content: _Any
    metadata: _Dict[str, _Any] = field(default_factory=dict)

@_dataclass  
class QualityMetrics:
    overall_score: float = 1.0
    passed_threshold: bool = True
    issues: List[str] = field(default_factory=list)

class ExecutionStatus:
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
from a2a_mcp.common.parallel_workflow import ParallelWorkflowGraph
# Connection pool will be created if needed
from a2a_mcp.common.quality_framework import QualityThresholdFramework
from a2a_mcp.common.observability import get_logger, trace_span, record_metric


@dataclass
class VideoFormat:
    """Video format configuration."""
    name: str
    min_duration: int
    max_duration: int
    structure: List[str]
    requirements: List[str]


@dataclass
class WorkflowPlan:
    """Workflow execution plan."""
    execution_plan: Dict[str, Any]
    parallel_tasks: List[Dict[str, Any]]
    sequential_tasks: List[Dict[str, Any]]
    dependencies: Dict[str, List[str]]
    platform_workflows: Dict[str, Any] = field(default_factory=dict)


class VideoOrchestrator(StandardizedAgentBase):
    """
    Video Production Orchestrator Agent
    
    Coordinates multi-agent video content generation with:
    - Platform-specific format detection
    - Intelligent workflow planning
    - Parallel execution optimization
    - Quality validation gates
    - Real-time progress tracking
    """
    
    # Platform format configurations
    FORMATS: ClassVar[Dict[str, VideoFormat]] = {
        "youtube": VideoFormat(
            name="youtube",
            min_duration=60,
            max_duration=1200,
            structure=["hook", "intro", "main_content", "outro", "cta"],
            requirements=["chapters", "description", "tags"]
        ),
        "tiktok": VideoFormat(
            name="tiktok",
            min_duration=15,
            max_duration=60,
            structure=["hook", "story", "loop"],
            requirements=["trending_audio", "hashtags", "effects"]
        ),
        "instagram_reels": VideoFormat(
            name="instagram_reels",
            min_duration=15,
            max_duration=90,
            structure=["hook", "value", "cta"],
            requirements=["cover_frame", "music", "hashtags"]
        )
    }
    
    def __init__(
        self,
        agent_id: str,
        connection_pool: ConnectionPool,
        quality_framework: QualityThresholdFramework,
        config: Dict[str, Any] = None,
        gemini_client: Any = None,
        event_handler: Callable = None,
        enable_caching: bool = False
    ):
        """Initialize Video Orchestrator with configuration."""
        config = config or {}
        
        # Set default configuration
        config.setdefault("port", 10106)
        config.setdefault("model", "gemini-2.0-flash-exp")
        config.setdefault("quality_domain", "BUSINESS")
        config.setdefault("planning_mode", "enhanced")
        config.setdefault("enable_parallel", True)
        
        # Quality thresholds
        config.setdefault("quality_thresholds", {
            "script_coherence": 0.85,
            "visual_feasibility": 0.80,
            "engagement_potential": 0.75,
            "platform_compliance": 0.90
        })
        
        super().__init__(
            agent_id=agent_id,
            name="Video Production Orchestrator",
            port=config["port"],
            connection_pool=connection_pool,
            quality_framework=quality_framework,
            config=config
        )
        
        self.gemini_client = gemini_client
        self.event_handler = event_handler
        self.enable_caching = enable_caching
        self.quality_domain = config.get("quality_domain", "BUSINESS")
        
        # Cache for templates
        self._cache = {} if enable_caching else None
        
        # Active workflows
        self._active_workflows = {}
        
        # System prompt
        self.system_prompt = """You are a Video Production Orchestrator responsible for transforming ideas into production-ready video scripts and storyboards. Analyze the request to determine format, style, and requirements, then coordinate specialized agents to create comprehensive video production materials. Ensure all outputs are practical, engaging, and optimized for the target platform."""
    
    async def _execute_agent_logic(self, context: TaskContext) -> TaskResult:
        """Execute orchestrator logic for video generation."""
        start_time = time.time()
        
        try:
            # Extract request parameters
            request = context.parameters
            platforms = request.get("platforms", ["youtube"])
            
            # Detect formats for each platform
            format_configs = {}
            for platform in platforms:
                format_config = await self.detect_format({**request, "platforms": [platform]})
                format_configs[platform] = format_config
            
            # Plan workflow
            workflow_plan = await self.plan_workflow(request)
            
            # Execute workflow
            results = await self._execute_workflow(workflow_plan, context)
            
            # Validate quality
            validation_result = await self.validate_quality(results)
            
            # Create final result
            artifacts = self._create_artifacts(results, format_configs)
            
            return TaskResult(
                status=ExecutionStatus.COMPLETED if validation_result["passed"] else ExecutionStatus.PARTIAL,
                confidence_score=validation_result["overall_score"],
                artifacts=artifacts,
                metadata={
                    "duration": time.time() - start_time,
                    "platforms": platforms,
                    "quality_validation": validation_result,
                    "workflow_plan": workflow_plan.execution_plan
                }
            )
            
        except Exception as e:
            self.logger.error(f"Orchestration failed: {str(e)}", exc_info=True)
            return TaskResult(
                status=ExecutionStatus.FAILED,
                confidence_score=0.0,
                artifacts=[],
                metadata={"error": str(e), "duration": time.time() - start_time}
            )
    
    async def detect_format(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Detect and configure format based on platform requirements."""
        platform = request["platforms"][0] if request.get("platforms") else "youtube"
        
        if platform not in self.FORMATS:
            # Default to YouTube for unknown platforms
            platform = "youtube"
        
        format_config = self.FORMATS[platform]
        
        return {
            "format": platform,
            "duration_range": (format_config.min_duration, format_config.max_duration),
            "structure": format_config.structure,
            "requirements": format_config.requirements,
            "style_adaptation": self._get_style_adaptation(platform, request.get("style", "educational"))
        }
    
    def _get_style_adaptation(self, platform: str, style: str) -> Dict[str, Any]:
        """Get platform-specific style adaptations."""
        adaptations = {
            "youtube": {
                "educational": {"pacing": "moderate", "detail": "high", "examples": True},
                "entertainment": {"pacing": "varied", "detail": "medium", "storytelling": True},
                "tutorial": {"pacing": "clear", "detail": "step-by-step", "visuals": "screen-recording"}
            },
            "tiktok": {
                "educational": {"pacing": "rapid", "detail": "bite-sized", "hook_duration": 3},
                "entertainment": {"pacing": "energetic", "detail": "minimal", "effects": True},
                "viral": {"pacing": "immediate", "detail": "punchy", "trend_integration": True}
            },
            "instagram_reels": {
                "educational": {"pacing": "quick", "detail": "visual", "text_overlay": True},
                "tutorial": {"pacing": "fast", "detail": "key-points", "music_sync": True},
                "marketing": {"pacing": "dynamic", "detail": "benefits", "cta_emphasis": True}
            }
        }
        
        return adaptations.get(platform, {}).get(style, {})
    
    async def plan_workflow(self, request: Dict[str, Any]) -> WorkflowPlan:
        """Plan workflow execution based on request requirements."""
        platforms = request.get("platforms", ["youtube"])
        is_multi_platform = len(platforms) > 1
        
        # Define task dependencies
        dependencies = {
            "hook_creator": [],
            "scene_designer": [],
            "script_writer": ["hook_creator"],
            "timing_coordinator": ["script_writer"],
            "shot_describer": ["scene_designer"],
            "transition_planner": ["scene_designer", "timing_coordinator"],
            "cta_generator": ["script_writer"]
        }
        
        # Define parallel tasks (can run simultaneously)
        parallel_tasks = [
            {"agent": "hook_creator", "action": "generate", "priority": 1},
            {"agent": "scene_designer", "action": "research", "priority": 1}
        ]
        
        # Define sequential tasks (must run in order)
        sequential_tasks = [
            {"agent": "script_writer", "action": "write", "priority": 2},
            {"agent": "timing_coordinator", "action": "optimize", "priority": 3},
            {"agent": "shot_describer", "action": "describe", "priority": 3},
            {"agent": "transition_planner", "action": "plan", "priority": 4},
            {"agent": "cta_generator", "action": "generate", "priority": 4}
        ]
        
        # Create platform-specific workflows if multi-platform
        platform_workflows = {}
        if is_multi_platform:
            for platform in platforms:
                platform_workflows[platform] = {
                    "format_config": await self.detect_format({**request, "platforms": [platform]}),
                    "adaptations": self._get_platform_adaptations(platform)
                }
        
        execution_plan = {
            "strategy": "parallel_optimized" if self.config.get("enable_parallel") else "sequential",
            "phases": [
                {"phase": 1, "tasks": parallel_tasks, "type": "parallel"},
                {"phase": 2, "tasks": sequential_tasks[:2], "type": "sequential"},
                {"phase": 3, "tasks": sequential_tasks[2:], "type": "parallel"}
            ],
            "estimated_duration": self._estimate_duration(platforms, request.get("style"))
        }
        
        return WorkflowPlan(
            execution_plan=execution_plan,
            parallel_tasks=parallel_tasks,
            sequential_tasks=sequential_tasks,
            dependencies=dependencies,
            platform_workflows=platform_workflows
        )
    
    def _get_platform_adaptations(self, platform: str) -> Dict[str, Any]:
        """Get platform-specific workflow adaptations."""
        return {
            "youtube": {"focus": "depth", "optimize_for": "retention"},
            "tiktok": {"focus": "hook", "optimize_for": "virality"},
            "instagram_reels": {"focus": "visual", "optimize_for": "engagement"}
        }.get(platform, {})
    
    def _estimate_duration(self, platforms: List[str], style: str) -> int:
        """Estimate workflow duration in seconds."""
        base_duration = 30
        platform_multiplier = len(platforms) * 0.7  # Parallel processing benefit
        style_complexity = {"educational": 1.2, "tutorial": 1.1, "entertainment": 1.0}.get(style, 1.0)
        
        return int(base_duration * platform_multiplier * style_complexity)
    
    async def _execute_workflow(self, workflow_plan: WorkflowPlan, context: TaskContext) -> Dict[str, Any]:
        """Execute the planned workflow."""
        results = {}
        
        # Execute phases according to plan
        for phase in workflow_plan.execution_plan["phases"]:
            if phase["type"] == "parallel":
                phase_results = await self.execute_parallel_tasks(phase["tasks"])
            else:
                phase_results = await self.execute_sequential_tasks(phase["tasks"])
            
            results.update(phase_results)
            
            # Emit progress
            await self.emit_progress("phase_completed", {
                "phase": phase["phase"],
                "completed_tasks": len(phase["tasks"])
            })
        
        return results
    
    async def execute_parallel_tasks(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute tasks in parallel for performance optimization."""
        async def execute_task(task):
            agent_name = task["agent"]
            action = task["action"]
            
            # Simulate agent communication (in real implementation, use A2A protocol)
            result = await self._communicate_with_agent(agent_name, action)
            return agent_name, result
        
        # Execute all tasks concurrently
        task_coroutines = [execute_task(task) for task in tasks]
        task_results = await asyncio.gather(*task_coroutines, return_exceptions=True)
        
        # Process results
        results = {}
        for agent_name, result in task_results:
            if isinstance(result, Exception):
                self.logger.error(f"Task failed for {agent_name}: {result}")
                results[agent_name] = {"status": "failed", "error": str(result)}
            else:
                results[agent_name] = result
        
        return results
    
    async def execute_sequential_tasks(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute tasks sequentially when dependencies exist."""
        results = {}
        
        for task in tasks:
            agent_name = task["agent"]
            action = task["action"]
            
            try:
                result = await self._communicate_with_agent(agent_name, action)
                results[agent_name] = result
            except Exception as e:
                self.logger.error(f"Sequential task failed for {agent_name}: {e}")
                results[agent_name] = {"status": "failed", "error": str(e)}
                # Continue with other tasks despite failure
        
        return results
    
    async def _communicate_with_agent(self, agent_name: str, action: str) -> Dict[str, Any]:
        """Communicate with other agents (placeholder for A2A protocol)."""
        # In real implementation, this would use A2AProtocolClient
        # For now, simulate agent responses
        await asyncio.sleep(0.5)  # Simulate network delay
        
        return {
            "status": "completed",
            "result": f"Result from {agent_name} for action {action}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def validate_quality(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Validate output quality against thresholds."""
        thresholds = self.config.get("quality_thresholds", {})
        quality_scores = output.get("quality_scores", {})
        
        # If no quality scores provided, calculate them
        if not quality_scores:
            quality_scores = await self._calculate_quality_scores(output)
        
        # Check each metric against threshold
        failed_metrics = []
        for metric, threshold in thresholds.items():
            score = quality_scores.get(metric, 0.0)
            if score < threshold:
                failed_metrics.append({
                    "metric": metric,
                    "score": score,
                    "threshold": threshold,
                    "gap": threshold - score
                })
        
        # Calculate overall score
        overall_score = sum(quality_scores.values()) / len(quality_scores) if quality_scores else 0.0
        
        return {
            "passed": len(failed_metrics) == 0,
            "overall_score": overall_score,
            "failed_metrics": failed_metrics,
            "scores": quality_scores,
            "thresholds": thresholds
        }
    
    async def _calculate_quality_scores(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate quality scores for output."""
        # Placeholder implementation - in real system would use ML models
        return {
            "script_coherence": 0.88,
            "visual_feasibility": 0.82,
            "engagement_potential": 0.79,
            "platform_compliance": 0.92
        }
    
    def _create_artifacts(self, results: Dict[str, Any], format_configs: Dict[str, Any]) -> List[ArtifactData]:
        """Create artifacts from workflow results."""
        artifacts = []
        
        # Script artifact
        if "script_writer" in results:
            artifacts.append(ArtifactData(
                artifact_id=f"script_{int(time.time())}",
                artifact_type="script",
                content=json.dumps(results["script_writer"]),
                metadata={"format": "video_script", "version": "1.0"}
            ))
        
        # Storyboard artifact
        if "scene_designer" in results:
            artifacts.append(ArtifactData(
                artifact_id=f"storyboard_{int(time.time())}",
                artifact_type="storyboard",
                content=json.dumps(results["scene_designer"]),
                metadata={"format": "visual_storyboard", "version": "1.0"}
            ))
        
        # Platform-specific artifacts
        for platform, config in format_configs.items():
            artifacts.append(ArtifactData(
                artifact_id=f"{platform}_config_{int(time.time())}",
                artifact_type="platform_config",
                content=json.dumps(config),
                metadata={"platform": platform}
            ))
        
        return artifacts
    
    async def emit_progress(self, event_type: str, data: Dict[str, Any]):
        """Emit progress event to handler if configured."""
        if self.event_handler:
            event = {
                "type": event_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": data
            }
            await self.event_handler(event)
    
    async def get_hook_template(self, params: Dict[str, Any]) -> Tuple[Any, bool]:
        """Get hook template with caching support."""
        if not self.enable_caching:
            template = await self._generate_hook_template(params)
            return template, False
        
        # Check cache
        cache_key = f"{params['style']}_{params['platform']}"
        if cache_key in self._cache:
            return self._cache[cache_key], True
        
        # Generate and cache
        template = await self._generate_hook_template(params)
        self._cache[cache_key] = template
        return template, False
    
    async def _generate_hook_template(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate hook template based on parameters."""
        # Placeholder - would use Gemini API in real implementation
        return {
            "template": f"Hook for {params['style']} on {params['platform']}",
            "duration": 5,
            "elements": ["attention_grabber", "value_proposition"]
        }
    
    def calculate_timeout(self, platform: str, operation: str) -> int:
        """Calculate adaptive timeout based on platform and operation."""
        base_timeouts = {
            "script_generation": {"youtube": 30, "tiktok": 10, "instagram_reels": 15},
            "full_workflow": {"youtube": 90, "tiktok": 30, "instagram_reels": 45},
            "quality_validation": {"youtube": 10, "tiktok": 5, "instagram_reels": 7}
        }
        
        operation_timeouts = base_timeouts.get(operation, {"youtube": 20, "tiktok": 10, "instagram_reels": 15})
        return operation_timeouts.get(platform, 20)
    
    async def execute_task_with_retry(self, task: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
        """Execute task with retry logic for resilience."""
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                # Add timeout to task
                timeout = task.get("timeout", 30)
                result = await asyncio.wait_for(
                    self._communicate_with_agent(task["agent"], task["action"]),
                    timeout=timeout
                )
                
                return {
                    "status": "completed",
                    "result": result,
                    "retry_count": retry_count
                }
                
            except asyncio.TimeoutError:
                last_error = "Task timed out"
                retry_count += 1
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                
            except Exception as e:
                last_error = str(e)
                retry_count += 1
                await asyncio.sleep(2 ** retry_count)
        
        return {
            "status": "failed",
            "error": last_error,
            "retry_count": retry_count
        }
    
    # Service management methods
    async def initialize(self):
        """Initialize orchestrator service."""
        self.logger.info(f"Initializing Video Orchestrator on port {self.port}")
        # Initialize Gemini client if not provided
        if not self.gemini_client and self.config.get("gemini_api_key"):
            genai.configure(api_key=self.config["gemini_api_key"])
            self.gemini_client = genai.GenerativeModel(self.config.get("model", "gemini-2.0-flash-exp"))
    
    async def start_service(self):
        """Start orchestrator service."""
        await self.initialize()
        # In real implementation, would start HTTP server
        self.logger.info("Video Orchestrator service started")
    
    async def stop_service(self):
        """Stop orchestrator service."""
        # Cleanup active workflows
        for workflow_id in list(self._active_workflows.keys()):
            await self._cleanup_workflow(workflow_id)
        self.logger.info("Video Orchestrator service stopped")
    
    async def _cleanup_workflow(self, workflow_id: str):
        """Cleanup workflow resources."""
        if workflow_id in self._active_workflows:
            del self._active_workflows[workflow_id]
    
    # Request management
    async def submit_request(self, request: Dict[str, Any]) -> str:
        """Submit video generation request."""
        request_id = f"req_{int(time.time() * 1000)}"
        self._active_workflows[request_id] = {
            "status": "submitted",
            "request": request,
            "submitted_at": datetime.now(timezone.utc)
        }
        
        # Start async processing
        asyncio.create_task(self._process_request(request_id, request))
        
        return request_id
    
    async def _process_request(self, request_id: str, request: Dict[str, Any]):
        """Process video generation request asynchronously."""
        try:
            self._active_workflows[request_id]["status"] = "processing"
            
            # Create task context
            context = TaskContext(
                session_id=request_id,
                request_type="video_generation",
                parameters=request,
                metadata={"timestamp": datetime.now(timezone.utc).isoformat()}
            )
            
            # Execute workflow
            result = await self._execute_agent_logic(context)
            
            # Update workflow status
            self._active_workflows[request_id].update({
                "status": "completed",
                "result": result,
                "completed_at": datetime.now(timezone.utc)
            })
            
        except Exception as e:
            self.logger.error(f"Request processing failed: {e}")
            self._active_workflows[request_id].update({
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.now(timezone.utc)
            })
    
    async def get_request_status(self, request_id: str) -> Dict[str, Any]:
        """Get status of video generation request."""
        if request_id not in self._active_workflows:
            return {"state": "not_found", "error": "Request ID not found"}
        
        workflow = self._active_workflows[request_id]
        state = workflow["status"]
        
        response = {
            "state": state,
            "submitted_at": workflow["submitted_at"].isoformat()
        }
        
        if state == "completed":
            result = workflow["result"]
            response.update({
                "artifacts": [a.dict() for a in result.artifacts],
                "metrics": {
                    "total_duration": result.metadata.get("duration", 0),
                    "quality_score": result.confidence_score
                }
            })
        elif state == "failed":
            response["error"] = workflow.get("error", "Unknown error")
        
        return response

# Alias for backward compatibility
VideoOrchestratorV2 = VideoOrchestrator
