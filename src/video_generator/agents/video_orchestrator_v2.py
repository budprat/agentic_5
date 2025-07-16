# ABOUTME: Video Orchestrator using Enhanced Master Orchestrator Template for proper delegation
# ABOUTME: Framework V2.0 compliant orchestrator with enhanced planner delegation and all 7 phases

"""
Video Orchestrator V2 - Enhanced Master Orchestrator Implementation

This module implements the Video Orchestrator using the Enhanced Master Orchestrator Template
following Framework V2.0 architecture:
- Delegates planning to Enhanced Planner Agent
- Focuses on orchestration and execution coordination
- Implements all 7 enhancement phases
- Supports real-time streaming with artifacts
"""

import asyncio
from typing import Dict, Any, List, Optional, AsyncIterable
from datetime import datetime
import json
import uuid

from a2a_mcp.common.enhanced_master_orchestrator_template import EnhancedMasterOrchestratorTemplate
from a2a_mcp.common.quality_framework import QualityDomain
from a2a_mcp.common.enhanced_workflow import WorkflowNode, WorkflowState, NodeState
from a2a_mcp.common.observability import get_logger, trace_span, record_metric


class VideoOrchestratorV2(EnhancedMasterOrchestratorTemplate):
    """
    Video Production Orchestrator V2 - Enhanced Implementation
    
    This orchestrator uses the Enhanced Master Orchestrator Template to:
    - Delegate all planning to Enhanced Planner Agent
    - Focus on execution coordination
    - Support all 7 enhancement phases
    - Provide real-time streaming with artifacts
    
    Key improvements over V1:
    - Proper separation of concerns (planning vs orchestration)
    - Enhanced planner capabilities for complex video workflows
    - Real-time progress tracking with PHASE 7 streaming
    - Better quality validation integration
    """
    
    def __init__(
        self,
        quality_domain: QualityDomain = QualityDomain.BUSINESS,
        quality_thresholds: Optional[Dict[str, float]] = None,
        enable_phase_7_streaming: bool = True,
        enable_observability: bool = True,
        enable_dynamic_workflow: bool = True,
        enable_parallel: bool = True
    ):
        """
        Initialize Video Orchestrator V2 with enhanced capabilities.
        
        Args:
            quality_domain: Quality validation domain (BUSINESS for production content)
            quality_thresholds: Custom quality thresholds for video generation
            enable_phase_7_streaming: Enable real-time streaming with artifacts
            enable_observability: Enable OpenTelemetry tracing and metrics
            enable_dynamic_workflow: Enable dynamic workflow graph capabilities
            enable_parallel: Enable parallel execution of independent tasks
        """
        # Define video generation domain and specialists
        domain_name = "Video Content Generation"
        domain_description = """
        Advanced video content generation system that creates production-ready scripts 
        and storyboards for multiple platforms including YouTube, TikTok, and Instagram Reels.
        Specializes in format detection, content adaptation, visual planning, and timing optimization.
        """
        
        # Define video generation specialists
        domain_specialists = {
            "script_writer": "Creates engaging video scripts with platform-specific adaptations, dialogue, narration, and story structure",
            "scene_designer": "Designs visual sequences, storyboards, shot compositions, and validates production feasibility",
            "timing_coordinator": "Optimizes video pacing, manages duration constraints, and synchronizes audio-visual elements",
            "hook_creator": "Generates attention-grabbing openings optimized for each platform's audience",
            "shot_describer": "Provides detailed camera angles, movements, and technical shot specifications",
            "transition_planner": "Plans smooth scene transitions and visual flow between segments",
            "cta_generator": "Creates compelling calls-to-action tailored to platform and audience"
        }
        
        # Default quality thresholds for video generation
        if not quality_thresholds:
            quality_thresholds = {
                "script_coherence": 0.85,
                "visual_feasibility": 0.80,
                "engagement_potential": 0.75,
                "platform_compliance": 0.90,
                "timing_accuracy": 0.85,
                "production_quality": 0.80
            }
        
        # Planning instructions specific to video generation
        planning_instructions = """
        When planning video generation tasks:
        
        1. FORMAT DETECTION PHASE:
           - First analyze the target platforms (YouTube, TikTok, Instagram Reels)
           - Identify duration constraints and format requirements
           - Determine optimal content structure for each platform
        
        2. PARALLEL CONTENT CREATION:
           - Hook creation and scene research can run in parallel
           - These tasks are independent and benefit from concurrent execution
        
        3. SCRIPT WRITING PHASE:
           - Depends on hooks from hook creator
           - Must adapt tone, pacing, and style to platform requirements
           - Incorporate audience preferences and content goals
        
        4. PRODUCTION PLANNING:
           - Scene design and timing coordination can run in parallel after script
           - Both need script as input but are independent of each other
        
        5. FINAL ASSEMBLY:
           - Aggregate all outputs into cohesive production plan
           - Validate quality across all dimensions
           - Ensure platform compliance
        
        Always prioritize parallel execution where possible for performance optimization.
        Target total generation time should be under 2 minutes for all platforms.
        """
        
        # Synthesis prompt for final output
        synthesis_prompt = """
        Create a comprehensive video production package that includes:
        
        1. FINAL SCRIPT:
           - Platform-optimized versions
           - Clear scene breakdowns
           - Dialogue and narration with timing
        
        2. VISUAL STORYBOARD:
           - Shot-by-shot breakdown
           - Camera angles and movements
           - Visual effects and transitions
        
        3. TIMING PLAN:
           - Precise segment durations
           - Audio-visual sync points
           - Pacing recommendations
        
        4. PRODUCTION GUIDE:
           - Equipment requirements
           - Shooting schedule
           - Post-production notes
        
        Ensure all outputs are production-ready and validated for quality.
        """
        
        # Initialize parent with video generation configuration
        super().__init__(
            domain_name=domain_name,
            domain_description=domain_description,
            domain_specialists=domain_specialists,
            quality_domain=quality_domain,
            quality_thresholds=quality_thresholds,
            planning_instructions=planning_instructions,
            synthesis_prompt=synthesis_prompt,
            enable_parallel=enable_parallel,
            enable_dynamic_workflow=enable_dynamic_workflow,
            enable_phase_7_streaming=enable_phase_7_streaming,
            enable_observability=enable_observability
        )
        
        # Video-specific configurations
        self.platform_configs = {
            "youtube": {
                "min_duration": 60,
                "max_duration": 1200,
                "optimal_duration": 480,
                "aspect_ratio": "16:9",
                "features": ["chapters", "end_screens", "cards"]
            },
            "tiktok": {
                "min_duration": 15,
                "max_duration": 60,
                "optimal_duration": 30,
                "aspect_ratio": "9:16",
                "features": ["effects", "music", "captions"]
            },
            "instagram_reels": {
                "min_duration": 15,
                "max_duration": 90,
                "optimal_duration": 45,
                "aspect_ratio": "9:16",
                "features": ["music", "effects", "stickers"]
            }
        }
        
        self.logger = get_logger(self.__class__.__name__)
    
    async def generate_video_content(
        self,
        request: Dict[str, Any],
        session_id: str,
        stream: bool = True
    ) -> Any:
        """
        Generate video content for specified platforms.
        
        This is the main entry point that leverages the enhanced orchestrator's
        planning and execution capabilities.
        
        Args:
            request: Video generation request containing:
                - content: The topic or content to create video about
                - platforms: List of target platforms
                - style: Video style (educational, entertainment, etc.)
                - preferences: Additional preferences
            session_id: Unique session identifier
            stream: Whether to use streaming mode (recommended)
        
        Returns:
            If streaming: AsyncIterable of events
            If not streaming: Final result dictionary
        """
        # Validate and enhance request with platform-specific info
        enhanced_request = self._enhance_request(request)
        
        # Create query for the orchestrator
        query = self._create_orchestrator_query(enhanced_request)
        
        if stream and self.enable_phase_7_streaming:
            # Use PHASE 7 streaming with artifacts
            task_id = str(uuid.uuid4())
            return self.stream_with_artifacts(query, session_id, task_id)
        else:
            # Non-streaming execution
            return await self.invoke(query, session_id)
    
    def _enhance_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance request with platform-specific configurations."""
        enhanced = request.copy()
        
        # Add platform configurations
        platforms = request.get("platforms", ["youtube"])
        enhanced["platform_configs"] = {
            platform: self.platform_configs.get(platform, {})
            for platform in platforms
        }
        
        # Add quality requirements
        enhanced["quality_requirements"] = {
            "min_script_coherence": self.quality_config["thresholds"].get("script_coherence", 0.85),
            "min_visual_feasibility": self.quality_config["thresholds"].get("visual_feasibility", 0.80),
            "min_engagement_potential": self.quality_config["thresholds"].get("engagement_potential", 0.75)
        }
        
        return enhanced
    
    def _create_orchestrator_query(self, request: Dict[str, Any]) -> str:
        """Create a detailed query for the orchestrator."""
        platforms = request.get("platforms", ["youtube"])
        content = request.get("content", "")
        style = request.get("style", "educational")
        
        query = f"""
        Create a comprehensive video production package for the following:
        
        CONTENT: {content}
        PLATFORMS: {', '.join(platforms)}
        STYLE: {style}
        
        Requirements:
        1. Generate platform-optimized scripts with appropriate hooks and CTAs
        2. Create detailed storyboards with shot compositions and transitions
        3. Develop timing plans with audio-visual synchronization
        4. Ensure all content meets quality thresholds
        5. Provide production-ready outputs
        
        Platform Constraints:
        {json.dumps(request.get("platform_configs", {}), indent=2)}
        
        Additional Preferences:
        {json.dumps(request.get("preferences", {}), indent=2)}
        """
        
        return query.strip()
    
    async def process_streaming_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process streaming events with video-specific handling.
        
        Override to add custom processing for video generation events.
        """
        event_type = event.get("type", "")
        
        # Add video-specific metadata to events
        if event_type == "artifact" and "artifact" in event:
            artifact = event["artifact"]
            artifact_type = artifact.get("type", "")
            
            # Enhance script artifacts
            if artifact_type == "script":
                artifact["metadata"] = artifact.get("metadata", {})
                artifact["metadata"]["word_count"] = self._count_words(artifact.get("content", ""))
                artifact["metadata"]["estimated_duration"] = self._estimate_duration(artifact.get("content", ""))
            
            # Enhance storyboard artifacts
            elif artifact_type == "storyboard":
                artifact["metadata"] = artifact.get("metadata", {})
                artifact["metadata"]["scene_count"] = self._count_scenes(artifact.get("content", ""))
                artifact["metadata"]["shot_count"] = self._count_shots(artifact.get("content", ""))
        
        return event
    
    def _count_words(self, content: str) -> int:
        """Count words in script content."""
        try:
            if isinstance(content, str):
                return len(content.split())
            elif isinstance(content, dict):
                # Handle structured script format
                text = json.dumps(content)
                return len(text.split())
        except:
            return 0
    
    def _estimate_duration(self, content: str) -> float:
        """Estimate video duration from script content."""
        word_count = self._count_words(content)
        # Average speaking rate: 150 words per minute
        return word_count / 150 * 60  # seconds
    
    def _count_scenes(self, content: str) -> int:
        """Count scenes in storyboard content."""
        try:
            if isinstance(content, str):
                data = json.loads(content)
            else:
                data = content
            
            return len(data.get("scenes", []))
        except:
            return 0
    
    def _count_shots(self, content: str) -> int:
        """Count total shots in storyboard content."""
        try:
            if isinstance(content, str):
                data = json.loads(content)
            else:
                data = content
            
            total_shots = 0
            for scene in data.get("scenes", []):
                total_shots += len(scene.get("shots", []))
            
            return total_shots
        except:
            return 0
    
    # Override specific phase methods if needed
    
    async def _phase_2_enhanced_planner_delegation(self, query: str, session_id: str) -> Dict[str, Any]:
        """
        PHASE 2: Enhanced planner delegation with video-specific context.
        
        Override to add video generation context to planning.
        """
        # Add video-specific context to the query
        enhanced_query = f"""
        {query}
        
        IMPORTANT: This is a video generation task that requires:
        - Parallel execution of hook creation and scene research
        - Sequential dependency from hooks to script writing
        - Parallel execution of scene design and timing coordination after script
        - Quality validation at each stage
        - Platform-specific optimizations
        """
        
        # Call parent implementation with enhanced query
        return await super()._phase_2_enhanced_planner_delegation(enhanced_query, session_id)
    
    def _validate_video_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate video generation output meets quality standards.
        
        This is called automatically by the quality framework but can be
        customized for video-specific validation.
        """
        validation_results = {
            "passed": True,
            "issues": [],
            "scores": {}
        }
        
        # Check for required artifacts
        required_artifacts = ["script", "storyboard", "timing_plan"]
        artifacts = output.get("artifacts", [])
        artifact_types = [a.get("type") for a in artifacts]
        
        for required in required_artifacts:
            if required not in artifact_types:
                validation_results["passed"] = False
                validation_results["issues"].append(f"Missing required artifact: {required}")
        
        # Validate script quality
        script_artifact = next((a for a in artifacts if a.get("type") == "script"), None)
        if script_artifact:
            script_score = self._validate_script_quality(script_artifact)
            validation_results["scores"]["script"] = script_score
            
            if script_score < self.quality_config["thresholds"].get("script_coherence", 0.85):
                validation_results["passed"] = False
                validation_results["issues"].append(f"Script quality below threshold: {script_score}")
        
        # Validate storyboard feasibility
        storyboard_artifact = next((a for a in artifacts if a.get("type") == "storyboard"), None)
        if storyboard_artifact:
            feasibility_score = self._validate_storyboard_feasibility(storyboard_artifact)
            validation_results["scores"]["storyboard"] = feasibility_score
            
            if feasibility_score < self.quality_config["thresholds"].get("visual_feasibility", 0.80):
                validation_results["passed"] = False
                validation_results["issues"].append(f"Storyboard feasibility below threshold: {feasibility_score}")
        
        return validation_results
    
    def _validate_script_quality(self, script_artifact: Dict[str, Any]) -> float:
        """Validate script quality score."""
        # Simplified validation - in production would use more sophisticated analysis
        content = script_artifact.get("content", "")
        
        # Check basic quality indicators
        score = 1.0
        
        # Has content
        if not content:
            return 0.0
        
        # Has reasonable length
        word_count = self._count_words(content)
        if word_count < 50:
            score *= 0.5
        elif word_count > 5000:
            score *= 0.8
        
        # Has structure (if JSON)
        try:
            if isinstance(content, str) and content.startswith("{"):
                data = json.loads(content)
                if "segments" not in data:
                    score *= 0.7
        except:
            pass
        
        return score
    
    def _validate_storyboard_feasibility(self, storyboard_artifact: Dict[str, Any]) -> float:
        """Validate storyboard production feasibility."""
        # Simplified validation
        content = storyboard_artifact.get("content", "")
        
        try:
            if isinstance(content, str):
                data = json.loads(content)
            else:
                data = content
            
            # Check basic feasibility
            scene_count = len(data.get("scenes", []))
            
            if scene_count == 0:
                return 0.0
            elif scene_count > 50:
                return 0.6  # Too many scenes
            else:
                return 0.9
        except:
            return 0.5
    
    def get_specialist_config(self, specialist_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific video generation specialist.
        
        This can be used to configure individual agents with specific settings.
        """
        configs = {
            "script_writer": {
                "temperature": 0.8,
                "writing_styles": ["educational", "entertainment", "marketing", "viral"],
                "platform_adaptations": True
            },
            "scene_designer": {
                "temperature": 0.9,
                "shot_types": ["wide", "medium", "close_up", "overhead", "tracking"],
                "feasibility_checking": True
            },
            "timing_coordinator": {
                "temperature": 0.7,
                "pacing_styles": ["steady", "accelerating", "varied", "rapid"],
                "beat_synchronization": True
            }
        }
        
        return configs.get(specialist_name, {})


# Convenience function for creating video orchestrator
def create_video_orchestrator(
    enable_streaming: bool = True,
    quality_thresholds: Optional[Dict[str, float]] = None
) -> VideoOrchestratorV2:
    """
    Create a properly configured Video Orchestrator V2.
    
    Args:
        enable_streaming: Enable real-time streaming with artifacts
        quality_thresholds: Custom quality thresholds
    
    Returns:
        Configured VideoOrchestratorV2 instance
    """
    return VideoOrchestratorV2(
        quality_domain=QualityDomain.BUSINESS,
        quality_thresholds=quality_thresholds,
        enable_phase_7_streaming=enable_streaming,
        enable_observability=True,
        enable_dynamic_workflow=True,
        enable_parallel=True
    )
