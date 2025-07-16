# ABOUTME: Tests for Video Production Orchestrator agent
# ABOUTME: Validates video format detection, workflow planning, and coordination

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from src.video_generator.agents.video_orchestrator import VideoOrchestrator

class TestVideoOrchestrator:
    """Test suite for Video Production Orchestrator"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create VideoOrchestrator instance for testing"""
        return VideoOrchestrator(
            agent_name="video_orchestrator",
            description="Video Production Orchestrator",
            instructions="Coordinate video generation workflow",
            quality_config={
                "min_confidence": 0.7,
                "require_verification": True
            },
            mcp_tools_enabled=False,
            a2a_enabled=False,
            use_config_manager=False
        )
    
    @pytest.mark.asyncio
    async def test_format_detection_youtube(self, orchestrator):
        """Test YouTube format detection from request"""
        request = {
            "content": "Create a 10-minute tutorial about Python",
            "platform": "youtube"
        }
        
        result = await orchestrator.detect_format(request)
        
        assert result["format"] == "youtube"
        assert result["duration_range"] == (60, 1200)
        assert result["structure"] == ["hook", "intro", "main_content", "outro", "cta"]
    
    @pytest.mark.asyncio
    async def test_format_detection_tiktok(self, orchestrator):
        """Test TikTok format detection from request"""
        request = {
            "content": "Quick tip about productivity",
            "platform": "tiktok"
        }
        
        result = await orchestrator.detect_format(request)
        
        assert result["format"] == "tiktok"
        assert result["duration_range"] == (15, 60)
        assert result["structure"] == ["hook", "story", "loop"]
    
    @pytest.mark.asyncio
    async def test_workflow_planning(self, orchestrator):
        """Test workflow planning for video production"""
        request = {
            "content": "Create a video about AI",
            "platform": "youtube",
            "style": "educational"
        }
        
        plan = await orchestrator.plan_workflow(request)
        
        assert "agents" in plan
        assert "script_writer" in plan["agents"]
        assert "hook_creator" in plan["agents"]
        assert "scene_designer" in plan["agents"]
        assert "timing_coordinator" in plan["agents"]
        
        assert plan["parallel_tasks"] == ["hook_creation", "scene_research"]
        assert plan["estimated_time"] > 0
    
    @pytest.mark.asyncio
    async def test_quality_validation(self, orchestrator):
        """Test quality validation for generated content"""
        script = {
            "content": "This is a test script...",
            "coherence_score": 0.90,
            "engagement_score": 0.85
        }
        
        validation = await orchestrator.validate_quality(script)
        
        assert validation["passed"] == True
        assert validation["coherence"] >= 0.85
        assert validation["engagement"] >= 0.75
    
    @pytest.mark.asyncio
    async def test_error_handling(self, orchestrator):
        """Test error handling for invalid requests"""
        invalid_request = {
            "platform": "unknown_platform"
        }
        
        with pytest.raises(ValueError) as exc_info:
            await orchestrator.detect_format(invalid_request)
        
        assert "Unsupported platform" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_multi_format_generation(self, orchestrator):
        """Test generating content for multiple platforms"""
        request = {
            "content": "How to learn programming",
            "platforms": ["youtube", "tiktok", "instagram_reels"]
        }
        
        results = await orchestrator.generate_multi_format(request)
        
        assert len(results) == 3
        assert "youtube" in results
        assert "tiktok" in results
        assert "instagram_reels" in results
        
        # Verify each format has appropriate duration
        assert results["youtube"]["duration"] >= 60
        assert results["tiktok"]["duration"] <= 60
        assert results["instagram_reels"]["duration"] <= 90