# ABOUTME: Comprehensive test suite for Video Orchestrator agent with TDD approach and real API integration
# ABOUTME: Tests format detection, workflow planning, quality validation, and parallel execution coordination

"""
Test Suite for Video Orchestrator Agent

This module tests:
- Format detection for different platforms
- Workflow planning and execution
- Quality validation thresholds
- Parallel execution coordination
- Agent communication
- Error handling and resilience
"""

import pytest
import asyncio
from typing import Dict, Any, List
import json
from datetime import datetime

from src.video_generator.agents.video_orchestrator import VideoOrchestrator
from src.a2a_mcp.common.models import (
    TaskContext,
    TaskResult,
    ArtifactData,
    QualityMetrics
)


class TestVideoOrchestrator:
    """Test suite for Video Orchestrator agent."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, connection_pool, quality_framework):
        """Test Video Orchestrator can be initialized with proper configuration."""
        orchestrator = VideoOrchestrator(
            agent_id="video_orchestrator",
            connection_pool=connection_pool,
            quality_framework=quality_framework,
            config={
                "port": 10106,
                "model": "gemini-2.0-flash-exp",
                "quality_domain": "BUSINESS"
            }
        )
        
        assert orchestrator.agent_id == "video_orchestrator"
        assert orchestrator.port == 10106
        assert orchestrator.quality_domain == "BUSINESS"
    
    @pytest.mark.asyncio
    async def test_format_detection_youtube(self, connection_pool, quality_framework, video_request_samples):
        """Test format detection for YouTube videos."""
        orchestrator = VideoOrchestrator(
            agent_id="video_orchestrator",
            connection_pool=connection_pool,
            quality_framework=quality_framework
        )
        
        request = video_request_samples["youtube_educational"]
        result = await orchestrator.detect_format(request)
        
        assert result["format"] == "youtube"
        assert result["duration_range"] == (60, 1200)
        assert "chapters" in result["requirements"]
        assert result["structure"] == ["hook", "intro", "main_content", "outro", "cta"]
    
    @pytest.mark.asyncio
    async def test_format_detection_tiktok(self, connection_pool, quality_framework, video_request_samples):
        """Test format detection for TikTok videos."""
        orchestrator = VideoOrchestrator(
            agent_id="video_orchestrator",
            connection_pool=connection_pool,
            quality_framework=quality_framework
        )
        
        request = video_request_samples["tiktok_viral"]
        result = await orchestrator.detect_format(request)
        
        assert result["format"] == "tiktok"
        assert result["duration_range"] == (15, 60)
        assert "trending_audio" in result["requirements"]
        assert result["structure"] == ["hook", "story", "loop"]
    
    @pytest.mark.asyncio
    async def test_format_detection_reels(self, connection_pool, quality_framework, video_request_samples):
        """Test format detection for Instagram Reels."""
        orchestrator = VideoOrchestrator(
            agent_id="video_orchestrator",
            connection_pool=connection_pool,
            quality_framework=quality_framework
        )
        
        request = video_request_samples["reels_tutorial"]
        result = await orchestrator.detect_format(request)
        
        assert result["format"] == "instagram_reels"
        assert result["duration_range"] == (15, 90)
        assert "cover_frame" in result["requirements"]
        assert result["structure"] == ["hook", "value", "cta"]
    
    @pytest.mark.asyncio
    async def test_workflow_planning_single_platform(self, connection_pool, quality_framework, video_request_samples):
        """Test workflow planning for single platform request."""
        orchestrator = VideoOrchestrator(
            agent_id="video_orchestrator",
            connection_pool=connection_pool,
            quality_framework=quality_framework
        )
        
        request = video_request_samples["youtube_educational"]
        workflow = await orchestrator.plan_workflow(request)
        
        # Check workflow structure
        assert "execution_plan" in workflow
        assert "parallel_tasks" in workflow
        assert "sequential_tasks" in workflow
        assert "dependencies" in workflow
        
        # Verify parallel tasks include hook creation and research
        parallel_tasks = workflow["parallel_tasks"]
        assert any(task["agent"] == "hook_creator" for task in parallel_tasks)
        assert any(task["agent"] == "scene_designer" for task in parallel_tasks)
        
        # Verify sequential dependencies
        assert workflow["dependencies"]["script_writer"] == ["hook_creator"]
        assert workflow["dependencies"]["timing_coordinator"] == ["script_writer"]
    
    @pytest.mark.asyncio
    async def test_workflow_planning_multi_platform(self, connection_pool, quality_framework, video_request_samples):
        """Test workflow planning for multi-platform request."""
        orchestrator = VideoOrchestrator(
            agent_id="video_orchestrator",
            connection_pool=connection_pool,
            quality_framework=quality_framework
        )
        
        request = video_request_samples["multi_platform"]
        workflow = await orchestrator.plan_workflow(request)
        
        # Should have platform-specific branches
        assert "platform_workflows" in workflow
        assert len(workflow["platform_workflows"]) == 3
        assert all(platform in workflow["platform_workflows"] 
                  for platform in ["youtube", "tiktok", "instagram_reels"])
    
    @pytest.mark.asyncio
    async def test_quality_validation_thresholds(self, connection_pool, quality_framework, quality_thresholds):
        """Test quality validation against thresholds."""
        orchestrator = VideoOrchestrator(
            agent_id="video_orchestrator",
            connection_pool=connection_pool,
            quality_framework=quality_framework,
            config={"quality_thresholds": quality_thresholds}
        )
        
        # Test passing quality scores
        good_output = {
            "script": "Well-structured content...",
            "storyboard": {"scenes": [1, 2, 3]},
            "quality_scores": {
                "script_coherence": 0.90,
                "visual_feasibility": 0.85,
                "engagement_potential": 0.80,
                "platform_compliance": 0.95
            }
        }
        
        validation_result = await orchestrator.validate_quality(good_output)
        assert validation_result["passed"] == True
        assert validation_result["overall_score"] >= 0.85
        
        # Test failing quality scores
        poor_output = {
            "script": "Poorly structured...",
            "storyboard": {"scenes": []},
            "quality_scores": {
                "script_coherence": 0.70,  # Below threshold
                "visual_feasibility": 0.75,  # Below threshold
                "engagement_potential": 0.60,  # Below threshold
                "platform_compliance": 0.85
            }
        }
        
        validation_result = await orchestrator.validate_quality(poor_output)
        assert validation_result["passed"] == False
        assert len(validation_result["failed_metrics"]) == 3
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_execute_workflow_real_api(self, connection_pool, quality_framework, video_request_samples, real_gemini_client):
        """Test executing a real workflow with Gemini API."""
        orchestrator = VideoOrchestrator(
            agent_id="video_orchestrator",
            connection_pool=connection_pool,
            quality_framework=quality_framework,
            gemini_client=real_gemini_client
        )
        
        # Initialize orchestrator service
        await orchestrator.initialize()
        
        # Create task context
        context = TaskContext(
            session_id="test_session_001",
            request_type="video_generation",
            parameters=video_request_samples["tiktok_viral"],
            metadata={
                "test_run": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Execute workflow
        result = await orchestrator.execute(context)
        
        # Verify result structure
        assert isinstance(result, TaskResult)
        assert result.status in ["completed", "partial"]
        assert result.confidence_score > 0.7
        
        # Check artifacts
        assert len(result.artifacts) > 0
        script_artifact = next((a for a in result.artifacts if a.artifact_type == "script"), None)
        assert script_artifact is not None
        assert len(script_artifact.content) > 0
        
        # Verify quality validation was performed
        assert "quality_validation" in result.metadata
        assert result.metadata["quality_validation"]["passed"] == True
    
    @pytest.mark.asyncio
    async def test_parallel_execution_performance(self, connection_pool, quality_framework, performance_tracker):
        """Test parallel execution improves performance."""
        orchestrator = VideoOrchestrator(
            agent_id="video_orchestrator",
            connection_pool=connection_pool,
            quality_framework=quality_framework
        )
        
        # Measure sequential execution
        seq_timer = performance_tracker.start("sequential_execution")
        await orchestrator.execute_sequential_tasks([
            {"agent": "hook_creator", "action": "generate"},
            {"agent": "script_writer", "action": "write"},
            {"agent": "scene_designer", "action": "design"}
        ])
        performance_tracker.end(seq_timer)
        
        # Measure parallel execution
        par_timer = performance_tracker.start("parallel_execution")
        await orchestrator.execute_parallel_tasks([
            {"agent": "hook_creator", "action": "generate"},
            {"agent": "scene_designer", "action": "research"}
        ])
        performance_tracker.end(par_timer)
        
        # Get performance report
        report = performance_tracker.get_report()
        
        # Parallel should be faster
        seq_duration = next(m["duration"] for m in report["operations"] 
                           if m["operation"] == "sequential_execution")
        par_duration = next(m["duration"] for m in report["operations"] 
                           if m["operation"] == "parallel_execution")
        
        # Parallel execution should show improvement
        improvement = (seq_duration - par_duration) / seq_duration
        assert improvement > 0.3  # At least 30% improvement
    
    @pytest.mark.asyncio
    async def test_error_handling_agent_failure(self, connection_pool, quality_framework):
        """Test orchestrator handles agent failures gracefully."""
        orchestrator = VideoOrchestrator(
            agent_id="video_orchestrator",
            connection_pool=connection_pool,
            quality_framework=quality_framework
        )
        
        # Simulate agent failure
        failing_task = {
            "agent": "nonexistent_agent",
            "action": "generate",
            "timeout": 5
        }
        
        result = await orchestrator.execute_task_with_retry(failing_task)
        
        assert result["status"] == "failed"
        assert "error" in result
        assert result["retry_count"] >= 1
    
    @pytest.mark.asyncio
    async def test_adaptive_timeout_handling(self, connection_pool, quality_framework):
        """Test adaptive timeout based on platform requirements."""
        orchestrator = VideoOrchestrator(
            agent_id="video_orchestrator",
            connection_pool=connection_pool,
            quality_framework=quality_framework
        )
        
        # YouTube should have longer timeout
        youtube_timeout = orchestrator.calculate_timeout("youtube", "script_generation")
        assert youtube_timeout >= 30
        
        # TikTok should have shorter timeout
        tiktok_timeout = orchestrator.calculate_timeout("tiktok", "script_generation")
        assert tiktok_timeout <= 15
        
        # Complex tasks should have longer timeouts
        complex_timeout = orchestrator.calculate_timeout("youtube", "full_workflow")
        assert complex_timeout >= 60
    
    @pytest.mark.asyncio
    async def test_progress_tracking_events(self, connection_pool, quality_framework):
        """Test progress tracking and event emission."""
        events_captured = []
        
        async def event_handler(event):
            events_captured.append(event)
        
        orchestrator = VideoOrchestrator(
            agent_id="video_orchestrator",
            connection_pool=connection_pool,
            quality_framework=quality_framework,
            event_handler=event_handler
        )
        
        # Execute a workflow step
        await orchestrator.emit_progress("workflow_started", {"stage": "initialization"})
        await orchestrator.emit_progress("task_completed", {"agent": "hook_creator"})
        await orchestrator.emit_progress("workflow_completed", {"duration": 45.2})
        
        # Verify events were captured
        assert len(events_captured) == 3
        assert events_captured[0]["type"] == "workflow_started"
        assert events_captured[1]["type"] == "task_completed"
        assert events_captured[2]["type"] == "workflow_completed"
    
    @pytest.mark.asyncio
    async def test_caching_hook_templates(self, connection_pool, quality_framework):
        """Test caching of hook templates for performance."""
        orchestrator = VideoOrchestrator(
            agent_id="video_orchestrator",
            connection_pool=connection_pool,
            quality_framework=quality_framework,
            enable_caching=True
        )
        
        # First request should be cache miss
        hook_params = {"style": "educational", "platform": "youtube"}
        result1, cache_hit1 = await orchestrator.get_hook_template(hook_params)
        assert cache_hit1 == False
        
        # Second request should be cache hit
        result2, cache_hit2 = await orchestrator.get_hook_template(hook_params)
        assert cache_hit2 == True
        assert result1 == result2  # Should return same result
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_integration_workflow(self, connection_pool, quality_framework, video_request_samples, cleanup_agents):
        """Test full integration workflow with all components."""
        orchestrator = VideoOrchestrator(
            agent_id="video_orchestrator",
            connection_pool=connection_pool,
            quality_framework=quality_framework
        )
        
        # Start orchestrator service
        await orchestrator.start_service()
        
        try:
            # Submit video generation request
            request = video_request_samples["youtube_educational"]
            request_id = await orchestrator.submit_request(request)
            
            # Poll for completion
            max_wait = 120  # 2 minutes
            poll_interval = 5
            elapsed = 0
            
            while elapsed < max_wait:
                status = await orchestrator.get_request_status(request_id)
                
                if status["state"] == "completed":
                    break
                elif status["state"] == "failed":
                    pytest.fail(f"Request failed: {status.get('error')}")
                
                await asyncio.sleep(poll_interval)
                elapsed += poll_interval
            
            # Verify results
            assert status["state"] == "completed"
            assert "artifacts" in status
            assert len(status["artifacts"]) > 0
            
            # Check performance metrics
            assert status["metrics"]["total_duration"] < 120  # Under 2 minutes
            assert status["metrics"]["quality_score"] > 0.85
            
        finally:
            await orchestrator.stop_service()