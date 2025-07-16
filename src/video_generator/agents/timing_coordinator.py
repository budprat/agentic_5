# ABOUTME: Timing Coordinator agent that optimizes video pacing and manages duration constraints
# ABOUTME: Specializes in platform-specific timing, audio-visual synchronization, and rhythm optimization

"""
Timing Coordinator Agent Implementation

This module implements the Timing Coordinator agent responsible for:
- Optimizing video pacing and rhythm
- Managing platform duration constraints
- Synchronizing audio-visual elements
- Creating timing breakdowns
- Ensuring optimal viewer engagement through pacing
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple, ClassVar
from datetime import datetime, timezone
import json
import time
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.common.a2a_connection_pool import A2AConnectionPool as ConnectionPool
from a2a_mcp.common.quality_framework import QualityThresholdFramework

# Define minimal required types inline
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
from a2a_mcp.common.quality_framework import QualityThresholdFramework
from a2a_mcp.common.observability import get_logger, trace_span, record_metric


class PacingStyle(Enum):
    """Video pacing styles."""
    STEADY = "steady"           # Consistent rhythm
    ACCELERATING = "accelerating"  # Building momentum
    VARIED = "varied"           # Dynamic changes
    RAPID = "rapid"             # Fast-paced throughout
    RELAXED = "relaxed"         # Slow and contemplative
    PULSING = "pulsing"         # Rhythmic beats


@dataclass
class TimingSegment:
    """Timing segment with synchronization data."""
    segment_id: str
    start_time: float
    end_time: float
    duration: float
    content_type: str
    beat_markers: List[float] = field(default_factory=list)
    emphasis_points: List[float] = field(default_factory=list)
    audio_sync_points: List[Dict[str, Any]] = field(default_factory=list)
    visual_sync_points: List[Dict[str, Any]] = field(default_factory=list)
    pacing_intensity: float = 1.0  # 0.5 = slow, 1.0 = normal, 2.0 = fast
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TimingPlan:
    """Complete timing plan for video."""
    total_duration: float
    platform: str
    segments: List[TimingSegment]
    pacing_style: PacingStyle
    beats_per_minute: float
    key_moments: List[Dict[str, Any]]
    synchronization_map: Dict[str, List[float]]
    platform_constraints: Dict[str, Any]
    optimization_notes: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class TimingCoordinator(StandardizedAgentBase):
    """
    Timing Coordinator Agent
    
    Optimizes video timing with:
    - Platform-specific duration management
    - Audio-visual synchronization
    - Pacing optimization
    - Rhythm and beat matching
    - Engagement curve optimization
    """
    
    # Platform timing constraints
    PLATFORM_CONSTRAINTS: ClassVar[Dict[str, Dict[str, Any]]] = {
        "youtube": {
            "min_duration": 60,
            "max_duration": 1200,
            "optimal_duration": 480,  # 8 minutes
            "attention_curve": "gradual_build",
            "chapter_min_duration": 30,
            "allows_variable_pacing": True,
            "key_moment_intervals": 60  # Every minute
        },
        "tiktok": {
            "min_duration": 15,
            "max_duration": 60,
            "optimal_duration": 30,
            "attention_curve": "immediate_hook",
            "chapter_min_duration": None,
            "allows_variable_pacing": False,
            "key_moment_intervals": 5  # Every 5 seconds
        },
        "instagram_reels": {
            "min_duration": 15,
            "max_duration": 90,
            "optimal_duration": 45,
            "attention_curve": "quick_peaks",
            "chapter_min_duration": None,
            "allows_variable_pacing": True,
            "key_moment_intervals": 10  # Every 10 seconds
        }
    }
    
    # Pacing templates
    PACING_TEMPLATES: ClassVar[Dict[PacingStyle, Dict[str, Any]]] = {
        PacingStyle.STEADY: {
            "intensity_curve": lambda t, d: 1.0,  # Constant
            "beat_pattern": "regular",
            "transition_speed": "consistent"
        },
        PacingStyle.ACCELERATING: {
            "intensity_curve": lambda t, d: 0.7 + (0.8 * t / d),  # Linear increase
            "beat_pattern": "increasing",
            "transition_speed": "quickening"
        },
        PacingStyle.VARIED: {
            "intensity_curve": lambda t, d: 1.0 + 0.5 * np.sin(4 * np.pi * t / d),  # Sinusoidal
            "beat_pattern": "dynamic",
            "transition_speed": "variable"
        },
        PacingStyle.RAPID: {
            "intensity_curve": lambda t, d: 1.5,  # High constant
            "beat_pattern": "fast",
            "transition_speed": "quick"
        },
        PacingStyle.RELAXED: {
            "intensity_curve": lambda t, d: 0.7,  # Low constant
            "beat_pattern": "slow",
            "transition_speed": "gentle"
        },
        PacingStyle.PULSING: {
            "intensity_curve": lambda t, d: 1.0 + 0.3 * np.sign(np.sin(8 * np.pi * t / d)),  # Square wave
            "beat_pattern": "rhythmic",
            "transition_speed": "beat_matched"
        }
    }
    
    def __init__(
        self,
        agent_id: str = "timing_coordinator",
        connection_pool: ConnectionPool = None,
        quality_framework: QualityThresholdFramework = None,
        config: Dict[str, Any] = None
    ):
        """Initialize Timing Coordinator agent."""
        config = config or {}
        
        # Set default configuration
        config.setdefault("port", 10214)
        config.setdefault("model", "gemini-2.0-flash-exp")
        config.setdefault("quality_domain", "BUSINESS")
        
        # Initialize base class with proper parameters
        super().__init__(
            agent_name="timing_coordinator",
            description="Optimizes video timing, pacing, and rhythm for maximum engagement",
            instructions="""You are a Timing Coordinator specializing in video pacing and rhythm.
            Optimize the timing of video content to maintain engagement and meet platform constraints.
            Ensure perfect synchronization between audio and visual elements.""",
            quality_config={
                "domain": config.get("quality_domain", "GENERIC"),
                "enabled": True,
                "thresholds": {
                    "timing_accuracy": 0.90,
                    "engagement_potential": 0.85
                }
            },
            use_config_manager=False  # Disable config manager for now
        )
        
        # Store additional attributes
        self.agent_id = agent_id
        self.config = config
        self.connection_pool = connection_pool
        self.quality_framework = quality_framework or self.quality_framework
        
        # System prompt
        self.system_prompt = """You are a Timing Coordinator specializing in video pacing and rhythm. Optimize the timing of video content to maintain engagement, meet platform constraints, and create compelling viewing experiences. Ensure perfect synchronization between audio and visual elements while managing pacing for maximum impact."""
    
    async def _execute_agent_logic(self, context: TaskContext) -> TaskResult:
        """Execute timing coordination logic."""
        start_time = time.time()
        
        try:
            # Extract parameters
            script = context.parameters.get("script", {})
            storyboard = context.parameters.get("storyboard", {})
            platform = context.parameters.get("platform", "youtube")
            target_duration = context.parameters.get("target_duration")
            music_bpm = context.parameters.get("music_bpm")
            style_preference = context.parameters.get("pacing_style", "varied")
            
            # Create timing plan
            timing_plan = await self.create_timing_plan(
                script=script,
                storyboard=storyboard,
                platform=platform,
                target_duration=target_duration,
                music_bpm=music_bpm,
                style_preference=style_preference
            )
            
            # Optimize timing
            optimized_plan = await self.optimize_timing(timing_plan)
            
            # Calculate quality scores
            quality_scores = await self._calculate_quality_scores(optimized_plan)
            
            # Create artifacts
            artifacts = [
                ArtifactData(
                    artifact_id=f"timing_plan_{int(time.time())}",
                    artifact_type="timing_plan",
                    content=self._serialize_timing_plan(optimized_plan),
                    metadata={
                        "platform": platform,
                        "total_duration": optimized_plan.total_duration,
                        "segment_count": len(optimized_plan.segments)
                    }
                ),
                ArtifactData(
                    artifact_id=f"sync_map_{int(time.time())}",
                    artifact_type="synchronization_map",
                    content=json.dumps(self._create_sync_map(optimized_plan)),
                    metadata={"sync_point_count": sum(len(points) for points in optimized_plan.synchronization_map.values())}
                )
            ]
            
            return TaskResult(
                status=ExecutionStatus.COMPLETED,
                confidence_score=quality_scores["overall"],
                artifacts=artifacts,
                metadata={
                    "duration": time.time() - start_time,
                    "quality_scores": quality_scores,
                    "timing_stats": {
                        "total_duration": optimized_plan.total_duration,
                        "avg_segment_duration": optimized_plan.total_duration / len(optimized_plan.segments),
                        "pacing_changes": self._count_pacing_changes(optimized_plan),
                        "sync_accuracy": quality_scores.get("sync_accuracy", 0.9)
                    }
                }
            )
            
        except Exception as e:
            self.logger.error(f"Timing coordination failed: {str(e)}", exc_info=True)
            return TaskResult(
                status=ExecutionStatus.FAILED,
                confidence_score=0.0,
                artifacts=[],
                metadata={"error": str(e), "duration": time.time() - start_time}
            )
    
    async def create_timing_plan(
        self,
        script: Dict[str, Any],
        storyboard: Dict[str, Any],
        platform: str,
        target_duration: Optional[float],
        music_bpm: Optional[float],
        style_preference: str
    ) -> TimingPlan:
        """Create comprehensive timing plan."""
        # Get platform constraints
        constraints = self.PLATFORM_CONSTRAINTS.get(platform, self.PLATFORM_CONSTRAINTS["youtube"])
        
        # Determine target duration
        if not target_duration:
            target_duration = constraints["optimal_duration"]
        else:
            # Clamp to platform limits
            target_duration = max(constraints["min_duration"], 
                                min(constraints["max_duration"], target_duration))
        
        # Determine pacing style
        pacing_style = self._determine_pacing_style(style_preference, platform)
        
        # Calculate base rhythm
        if not music_bpm:
            music_bpm = self._calculate_base_bpm(pacing_style)
        
        # Create timing segments
        segments = await self._create_timing_segments(
            script, storyboard, target_duration, constraints, pacing_style
        )
        
        # Identify key moments
        key_moments = self._identify_key_moments(segments, constraints)
        
        # Create synchronization map
        sync_map = await self._create_synchronization_map(segments, music_bpm)
        
        # Generate optimization notes
        optimization_notes = self._generate_optimization_notes(
            segments, target_duration, constraints
        )
        
        return TimingPlan(
            total_duration=sum(s.duration for s in segments),
            platform=platform,
            segments=segments,
            pacing_style=pacing_style,
            beats_per_minute=music_bpm,
            key_moments=key_moments,
            synchronization_map=sync_map,
            platform_constraints=constraints,
            optimization_notes=optimization_notes,
            metadata={
                "created_at": datetime.now(timezone.utc).isoformat(),
                "target_duration": target_duration
            }
        )
    
    def _determine_pacing_style(self, preference: str, platform: str) -> PacingStyle:
        """Determine appropriate pacing style."""
        style_map = {
            "steady": PacingStyle.STEADY,
            "accelerating": PacingStyle.ACCELERATING,
            "varied": PacingStyle.VARIED,
            "rapid": PacingStyle.RAPID,
            "relaxed": PacingStyle.RELAXED,
            "pulsing": PacingStyle.PULSING
        }
        
        # Platform overrides
        if platform == "tiktok":
            # TikTok needs rapid or pulsing
            if preference not in ["rapid", "pulsing"]:
                return PacingStyle.RAPID
        
        return style_map.get(preference, PacingStyle.VARIED)
    
    def _calculate_base_bpm(self, pacing_style: PacingStyle) -> float:
        """Calculate base BPM for pacing style."""
        bpm_map = {
            PacingStyle.STEADY: 120,
            PacingStyle.ACCELERATING: 110,  # Starts slower
            PacingStyle.VARIED: 125,
            PacingStyle.RAPID: 140,
            PacingStyle.RELAXED: 90,
            PacingStyle.PULSING: 128  # EDM standard
        }
        
        return bpm_map.get(pacing_style, 120)
    
    async def _create_timing_segments(
        self,
        script: Dict[str, Any],
        storyboard: Dict[str, Any],
        target_duration: float,
        constraints: Dict[str, Any],
        pacing_style: PacingStyle
    ) -> List[TimingSegment]:
        """Create timing segments from script and storyboard."""
        segments = []
        
        # Get content segments from script
        script_segments = script.get("segments", [])
        scenes = storyboard.get("scenes", [])
        
        if not script_segments and not scenes:
            # Create default segments
            return self._create_default_segments(target_duration, constraints, pacing_style)
        
        # Merge script and storyboard timing
        current_time = 0.0
        pacing_template = self.PACING_TEMPLATES[pacing_style]
        
        for i, script_seg in enumerate(script_segments):
            # Calculate segment duration
            base_duration = script_seg.get("duration", 5.0)
            
            # Apply pacing intensity
            intensity = pacing_template["intensity_curve"](current_time, target_duration)
            adjusted_duration = base_duration / intensity  # Higher intensity = shorter duration
            
            # Create timing segment
            segment = TimingSegment(
                segment_id=f"seg_{i}",
                start_time=current_time,
                end_time=current_time + adjusted_duration,
                duration=adjusted_duration,
                content_type=script_seg.get("type", "narration"),
                pacing_intensity=intensity,
                metadata={"script_index": i}
            )
            
            # Add beat markers
            segment.beat_markers = self._calculate_beat_markers(
                segment, constraints.get("key_moment_intervals", 10)
            )
            
            # Add emphasis points based on content
            segment.emphasis_points = self._identify_emphasis_points(script_seg)
            
            segments.append(segment)
            current_time += adjusted_duration
        
        # Adjust to match target duration
        segments = self._adjust_segment_durations(segments, target_duration)
        
        return segments
    
    def _create_default_segments(
        self,
        duration: float,
        constraints: Dict[str, Any],
        pacing_style: PacingStyle
    ) -> List[TimingSegment]:
        """Create default timing segments."""
        segments = []
        
        # Standard video structure
        structure = [
            {"name": "intro", "ratio": 0.1, "type": "hook"},
            {"name": "main_1", "ratio": 0.3, "type": "content"},
            {"name": "main_2", "ratio": 0.3, "type": "content"},
            {"name": "main_3", "ratio": 0.2, "type": "content"},
            {"name": "outro", "ratio": 0.1, "type": "cta"}
        ]
        
        current_time = 0.0
        pacing_template = self.PACING_TEMPLATES[pacing_style]
        
        for i, section in enumerate(structure):
            seg_duration = duration * section["ratio"]
            intensity = pacing_template["intensity_curve"](current_time, duration)
            
            segment = TimingSegment(
                segment_id=f"seg_{i}_{section['name']}",
                start_time=current_time,
                end_time=current_time + seg_duration,
                duration=seg_duration,
                content_type=section["type"],
                pacing_intensity=intensity
            )
            
            segments.append(segment)
            current_time += seg_duration
        
        return segments
    
    def _calculate_beat_markers(self, segment: TimingSegment, interval: float) -> List[float]:
        """Calculate beat markers for segment."""
        markers = []
        current = segment.start_time
        
        while current < segment.end_time:
            markers.append(current)
            current += interval / segment.pacing_intensity  # Adjust for pacing
        
        return markers
    
    def _identify_emphasis_points(self, script_segment: Dict[str, Any]) -> List[float]:
        """Identify emphasis points in content."""
        emphasis_points = []
        
        # Look for emphasis indicators in content
        content = script_segment.get("content", "").lower()
        emphasis_words = ["important", "key", "remember", "crucial", "amazing", "incredible"]
        
        # Simple heuristic - in production would use NLP
        if any(word in content for word in emphasis_words):
            # Add emphasis at segment midpoint
            timing = script_segment.get("timing", {})
            start = timing.get("start", 0)
            end = timing.get("end", 5)
            emphasis_points.append((start + end) / 2)
        
        return emphasis_points
    
    def _adjust_segment_durations(
        self,
        segments: List[TimingSegment],
        target_duration: float
    ) -> List[TimingSegment]:
        """Adjust segment durations to match target."""
        if not segments:
            return segments
        
        current_total = sum(s.duration for s in segments)
        if abs(current_total - target_duration) < 0.1:
            return segments  # Close enough
        
        # Calculate scaling factor
        scale_factor = target_duration / current_total
        
        # Adjust each segment proportionally
        current_time = 0.0
        for segment in segments:
            new_duration = segment.duration * scale_factor
            segment.start_time = current_time
            segment.end_time = current_time + new_duration
            segment.duration = new_duration
            
            # Recalculate beat markers
            segment.beat_markers = [
                current_time + (marker - segment.start_time) * scale_factor
                for marker in segment.beat_markers
            ]
            
            current_time += new_duration
        
        return segments
    
    def _identify_key_moments(
        self,
        segments: List[TimingSegment],
        constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify key moments in the video."""
        key_moments = []
        
        # Add platform-specific key moments
        interval = constraints.get("key_moment_intervals", 30)
        current_time = 0
        
        while current_time < segments[-1].end_time if segments else 0:
            # Find which segment contains this time
            segment = next((s for s in segments if s.start_time <= current_time < s.end_time), None)
            
            if segment:
                key_moments.append({
                    "time": current_time,
                    "type": "checkpoint",
                    "segment_id": segment.segment_id,
                    "description": f"Key moment at {int(current_time)}s"
                })
            
            current_time += interval
        
        # Add emphasis points as key moments
        for segment in segments:
            for emphasis_time in segment.emphasis_points:
                key_moments.append({
                    "time": emphasis_time,
                    "type": "emphasis",
                    "segment_id": segment.segment_id,
                    "description": "Content emphasis point"
                })
        
        # Sort by time
        key_moments.sort(key=lambda x: x["time"])
        
        return key_moments
    
    async def _create_synchronization_map(
        self,
        segments: List[TimingSegment],
        bpm: float
    ) -> Dict[str, List[float]]:
        """Create audio-visual synchronization map."""
        sync_map = {
            "beats": [],
            "measures": [],
            "sections": [],
            "transitions": []
        }
        
        # Calculate beat timing
        beat_duration = 60.0 / bpm  # Duration of one beat in seconds
        measure_duration = beat_duration * 4  # 4/4 time
        
        # Generate beat grid
        total_duration = segments[-1].end_time if segments else 0
        current_beat = 0.0
        
        while current_beat < total_duration:
            sync_map["beats"].append(current_beat)
            
            # Add measure markers
            if len(sync_map["beats"]) % 4 == 1:
                sync_map["measures"].append(current_beat)
            
            # Add section markers (every 8 measures)
            if len(sync_map["measures"]) % 8 == 1:
                sync_map["sections"].append(current_beat)
            
            current_beat += beat_duration
        
        # Add transition points
        for i in range(1, len(segments)):
            sync_map["transitions"].append(segments[i].start_time)
        
        return sync_map
    
    def _generate_optimization_notes(
        self,
        segments: List[TimingSegment],
        target_duration: float,
        constraints: Dict[str, Any]
    ) -> List[str]:
        """Generate timing optimization notes."""
        notes = []
        
        # Check duration compliance
        actual_duration = segments[-1].end_time if segments else 0
        if actual_duration < constraints["min_duration"]:
            notes.append(f"Duration too short ({actual_duration:.1f}s < {constraints['min_duration']}s minimum)")
        elif actual_duration > constraints["max_duration"]:
            notes.append(f"Duration too long ({actual_duration:.1f}s > {constraints['max_duration']}s maximum)")
        else:
            notes.append(f"Duration within platform limits ({actual_duration:.1f}s)")
        
        # Check pacing variety
        intensity_values = [s.pacing_intensity for s in segments]
        if len(set(intensity_values)) == 1:
            notes.append("Consider adding pacing variety for better engagement")
        
        # Check segment durations
        short_segments = [s for s in segments if s.duration < 2.0]
        if short_segments:
            notes.append(f"{len(short_segments)} segments under 2 seconds - may feel rushed")
        
        # Platform-specific notes
        if constraints.get("attention_curve") == "immediate_hook":
            if segments and segments[0].duration > 3.0:
                notes.append("Opening hook should be under 3 seconds for this platform")
        
        return notes
    
    async def optimize_timing(self, timing_plan: TimingPlan) -> TimingPlan:
        """Optimize timing plan for maximum engagement."""
        # Clone the plan for modification
        optimized = TimingPlan(
            total_duration=timing_plan.total_duration,
            platform=timing_plan.platform,
            segments=list(timing_plan.segments),  # Shallow copy
            pacing_style=timing_plan.pacing_style,
            beats_per_minute=timing_plan.beats_per_minute,
            key_moments=list(timing_plan.key_moments),
            synchronization_map=dict(timing_plan.synchronization_map),
            platform_constraints=timing_plan.platform_constraints,
            optimization_notes=list(timing_plan.optimization_notes),
            metadata=dict(timing_plan.metadata)
        )
        
        # Apply platform-specific optimizations
        optimized = await self._apply_platform_optimizations(optimized)
        
        # Optimize pacing flow
        optimized = self._optimize_pacing_flow(optimized)
        
        # Align with music beats
        optimized = self._align_to_beats(optimized)
        
        # Add synchronization points
        optimized = await self._add_sync_points(optimized)
        
        return optimized
    
    async def _apply_platform_optimizations(self, plan: TimingPlan) -> TimingPlan:
        """Apply platform-specific timing optimizations."""
        constraints = plan.platform_constraints
        
        if plan.platform == "tiktok":
            # Ensure strong hook in first 3 seconds
            if plan.segments and plan.segments[0].duration > 3.0:
                # Compress first segment
                excess = plan.segments[0].duration - 3.0
                plan.segments[0].duration = 3.0
                plan.segments[0].end_time = plan.segments[0].start_time + 3.0
                
                # Redistribute time to other segments
                if len(plan.segments) > 1:
                    per_segment = excess / (len(plan.segments) - 1)
                    for i in range(1, len(plan.segments)):
                        plan.segments[i].duration += per_segment
                        plan.segments[i].start_time = plan.segments[i-1].end_time
                        plan.segments[i].end_time = plan.segments[i].start_time + plan.segments[i].duration
        
        elif plan.platform == "youtube":
            # Ensure minimum chapter duration
            min_chapter = constraints.get("chapter_min_duration", 30)
            
            # Merge short segments
            i = 0
            while i < len(plan.segments) - 1:
                if plan.segments[i].duration < min_chapter:
                    # Merge with next segment
                    plan.segments[i].duration += plan.segments[i+1].duration
                    plan.segments[i].end_time = plan.segments[i+1].end_time
                    plan.segments.pop(i+1)
                else:
                    i += 1
        
        return plan
    
    def _optimize_pacing_flow(self, plan: TimingPlan) -> TimingPlan:
        """Optimize pacing flow for engagement."""
        if len(plan.segments) < 2:
            return plan
        
        # Apply pacing template more strictly
        template = self.PACING_TEMPLATES[plan.pacing_style]
        total_duration = plan.total_duration
        
        for segment in plan.segments:
            # Recalculate intensity based on position
            mid_time = (segment.start_time + segment.end_time) / 2
            segment.pacing_intensity = template["intensity_curve"](mid_time, total_duration)
        
        # Smooth transitions between segments
        for i in range(1, len(plan.segments)):
            prev_intensity = plan.segments[i-1].pacing_intensity
            curr_intensity = plan.segments[i].pacing_intensity
            
            # Limit intensity jumps
            max_jump = 0.3
            if abs(curr_intensity - prev_intensity) > max_jump:
                # Smooth the transition
                plan.segments[i].pacing_intensity = prev_intensity + max_jump * np.sign(curr_intensity - prev_intensity)
        
        return plan
    
    def _align_to_beats(self, plan: TimingPlan) -> TimingPlan:
        """Align segment transitions to musical beats."""
        if not plan.synchronization_map.get("beats"):
            return plan
        
        beats = plan.synchronization_map["beats"]
        beat_duration = 60.0 / plan.beats_per_minute
        
        for i, segment in enumerate(plan.segments):
            if i == 0:
                continue  # Don't adjust start
            
            # Find nearest beat to segment start
            nearest_beat = min(beats, key=lambda b: abs(b - segment.start_time))
            
            # Only adjust if within reasonable range (half a beat)
            if abs(nearest_beat - segment.start_time) < beat_duration / 2:
                # Adjust segment timing
                adjustment = nearest_beat - segment.start_time
                segment.start_time = nearest_beat
                segment.duration += adjustment
                
                # Adjust previous segment
                if i > 0:
                    plan.segments[i-1].end_time = nearest_beat
                    plan.segments[i-1].duration -= adjustment
        
        return plan
    
    async def _add_sync_points(self, plan: TimingPlan) -> TimingPlan:
        """Add audio-visual synchronization points."""
        for segment in plan.segments:
            # Audio sync points (on beats)
            beat_times = [b for b in plan.synchronization_map["beats"] 
                         if segment.start_time <= b < segment.end_time]
            
            # Add audio sync points for important beats
            for i, beat_time in enumerate(beat_times):
                if i % 4 == 0:  # Every measure
                    segment.audio_sync_points.append({
                        "time": beat_time,
                        "type": "measure_start",
                        "strength": "strong"
                    })
                elif i % 2 == 0:  # Every half measure
                    segment.audio_sync_points.append({
                        "time": beat_time,
                        "type": "beat",
                        "strength": "medium"
                    })
            
            # Visual sync points (for transitions and emphasis)
            if segment.emphasis_points:
                for emphasis_time in segment.emphasis_points:
                    # Find nearest beat
                    nearest_beat = min(beat_times, key=lambda b: abs(b - emphasis_time)) if beat_times else emphasis_time
                    
                    segment.visual_sync_points.append({
                        "time": nearest_beat,
                        "type": "emphasis",
                        "action": "visual_accent"
                    })
            
            # Add transition sync points
            segment.visual_sync_points.append({
                "time": segment.start_time,
                "type": "transition_in",
                "action": "fade_in" if segment.start_time == 0 else "cut"
            })
        
        return plan
    
    async def _calculate_quality_scores(self, timing_plan: TimingPlan) -> Dict[str, float]:
        """Calculate quality scores for timing plan."""
        scores = {
            "pacing_quality": self._score_pacing_quality(timing_plan),
            "sync_accuracy": self._score_sync_accuracy(timing_plan),
            "platform_fit": self._score_platform_fit(timing_plan),
            "engagement_curve": self._score_engagement_curve(timing_plan),
            "rhythm_consistency": self._score_rhythm_consistency(timing_plan)
        }
        
        scores["overall"] = sum(scores.values()) / len(scores)
        return scores
    
    def _score_pacing_quality(self, plan: TimingPlan) -> float:
        """Score pacing quality and variety."""
        if len(plan.segments) < 2:
            return 0.7
        
        # Check intensity variety
        intensities = [s.pacing_intensity for s in plan.segments]
        intensity_range = max(intensities) - min(intensities)
        
        # Good pacing has some variety
        variety_score = min(intensity_range / 0.5, 1.0)  # 0.5 range is ideal
        
        # Check for smooth transitions
        transition_score = 1.0
        for i in range(1, len(plan.segments)):
            jump = abs(plan.segments[i].pacing_intensity - plan.segments[i-1].pacing_intensity)
            if jump > 0.5:
                transition_score -= 0.1
        
        transition_score = max(0.5, transition_score)
        
        return (variety_score + transition_score) / 2
    
    def _score_sync_accuracy(self, plan: TimingPlan) -> float:
        """Score synchronization accuracy."""
        if not plan.synchronization_map.get("beats"):
            return 0.7
        
        beat_duration = 60.0 / plan.beats_per_minute
        sync_errors = []
        
        # Check segment boundaries against beats
        for segment in plan.segments:
            # Find nearest beat to segment start
            beats = plan.synchronization_map["beats"]
            if beats:
                nearest_beat = min(beats, key=lambda b: abs(b - segment.start_time))
                error = abs(nearest_beat - segment.start_time) / beat_duration
                sync_errors.append(error)
        
        # Calculate average sync error
        avg_error = sum(sync_errors) / len(sync_errors) if sync_errors else 0
        
        # Convert to score (0 error = 1.0 score)
        return max(0.5, 1.0 - avg_error)
    
    def _score_platform_fit(self, plan: TimingPlan) -> float:
        """Score how well timing fits platform requirements."""
        constraints = plan.platform_constraints
        score = 1.0
        
        # Check duration compliance
        if plan.total_duration < constraints["min_duration"]:
            score -= 0.3
        elif plan.total_duration > constraints["max_duration"]:
            score -= 0.3
        
        # Check attention curve compliance
        if constraints["attention_curve"] == "immediate_hook":
            if plan.segments and plan.segments[0].duration > 3.0:
                score -= 0.2
        
        # Check pacing style compatibility
        if plan.platform == "tiktok" and plan.pacing_style in [PacingStyle.RELAXED, PacingStyle.STEADY]:
            score -= 0.2  # TikTok needs dynamic pacing
        
        return max(0.3, score)
    
    def _score_engagement_curve(self, plan: TimingPlan) -> float:
        """Score engagement curve optimization."""
        if not plan.key_moments:
            return 0.6
        
        # Check key moment distribution
        moment_times = [m["time"] for m in plan.key_moments]
        
        # Ideal: evenly distributed key moments
        if len(moment_times) > 1:
            intervals = [moment_times[i+1] - moment_times[i] for i in range(len(moment_times)-1)]
            avg_interval = sum(intervals) / len(intervals)
            
            # Calculate variance
            variance = sum((i - avg_interval) ** 2 for i in intervals) / len(intervals)
            std_dev = variance ** 0.5
            
            # Lower variance is better
            consistency_score = max(0.5, 1.0 - (std_dev / avg_interval))
        else:
            consistency_score = 0.7
        
        # Check emphasis point placement
        emphasis_count = sum(len(s.emphasis_points) for s in plan.segments)
        emphasis_score = min(emphasis_count / 5, 1.0)  # 5 emphasis points is good
        
        return (consistency_score + emphasis_score) / 2
    
    def _score_rhythm_consistency(self, plan: TimingPlan) -> float:
        """Score rhythm and beat consistency."""
        if not plan.segments:
            return 0.5
        
        # Check beat marker consistency
        beat_intervals = []
        for segment in plan.segments:
            if len(segment.beat_markers) > 1:
                for i in range(1, len(segment.beat_markers)):
                    interval = segment.beat_markers[i] - segment.beat_markers[i-1]
                    beat_intervals.append(interval)
        
        if not beat_intervals:
            return 0.7
        
        # Calculate consistency
        avg_interval = sum(beat_intervals) / len(beat_intervals)
        deviations = [abs(i - avg_interval) / avg_interval for i in beat_intervals]
        avg_deviation = sum(deviations) / len(deviations)
        
        # Lower deviation is better
        return max(0.5, 1.0 - avg_deviation)
    
    def _count_pacing_changes(self, plan: TimingPlan) -> int:
        """Count significant pacing changes."""
        if len(plan.segments) < 2:
            return 0
        
        changes = 0
        for i in range(1, len(plan.segments)):
            intensity_change = abs(plan.segments[i].pacing_intensity - plan.segments[i-1].pacing_intensity)
            if intensity_change > 0.3:  # Significant change
                changes += 1
        
        return changes
    
    def _serialize_timing_plan(self, plan: TimingPlan) -> str:
        """Serialize timing plan to JSON."""
        return json.dumps({
            "total_duration": plan.total_duration,
            "platform": plan.platform,
            "pacing_style": plan.pacing_style.value,
            "beats_per_minute": plan.beats_per_minute,
            "segments": [
                {
                    "segment_id": s.segment_id,
                    "start_time": s.start_time,
                    "end_time": s.end_time,
                    "duration": s.duration,
                    "content_type": s.content_type,
                    "pacing_intensity": s.pacing_intensity,
                    "beat_markers": s.beat_markers,
                    "emphasis_points": s.emphasis_points,
                    "audio_sync_points": s.audio_sync_points,
                    "visual_sync_points": s.visual_sync_points,
                    "metadata": s.metadata
                }
                for s in plan.segments
            ],
            "key_moments": plan.key_moments,
            "synchronization_map": {
                k: v[:10] + ["..."] if len(v) > 10 else v  # Truncate long lists
                for k, v in plan.synchronization_map.items()
            },
            "platform_constraints": plan.platform_constraints,
            "optimization_notes": plan.optimization_notes,
            "metadata": plan.metadata
        }, indent=2)
    
    def _create_sync_map(self, plan: TimingPlan) -> Dict[str, Any]:
        """Create detailed synchronization map."""
        return {
            "beat_grid": {
                "bpm": plan.beats_per_minute,
                "beat_count": len(plan.synchronization_map.get("beats", [])),
                "measure_count": len(plan.synchronization_map.get("measures", [])),
                "section_count": len(plan.synchronization_map.get("sections", []))
            },
            "segment_sync": [
                {
                    "segment_id": s.segment_id,
                    "audio_sync_count": len(s.audio_sync_points),
                    "visual_sync_count": len(s.visual_sync_points),
                    "beat_aligned": any(
                        abs(s.start_time - beat) < 0.1 
                        for beat in plan.synchronization_map.get("beats", [])
                    )
                }
                for s in plan.segments
            ],
            "key_moment_sync": [
                {
                    "time": km["time"],
                    "nearest_beat": min(
                        plan.synchronization_map.get("beats", [km["time"]]),
                        key=lambda b: abs(b - km["time"])
                    ),
                    "beat_aligned": any(
                        abs(km["time"] - beat) < 0.1 
                        for beat in plan.synchronization_map.get("beats", [])
                    )
                }
                for km in plan.key_moments
            ],
            "optimization_summary": {
                "total_sync_points": sum(
                    len(s.audio_sync_points) + len(s.visual_sync_points) 
                    for s in plan.segments
                ),
                "beat_aligned_transitions": sum(
                    1 for s in plan.segments
                    if any(abs(s.start_time - beat) < 0.1 
                          for beat in plan.synchronization_map.get("beats", []))
                ),
                "pacing_changes": self._count_pacing_changes(plan)
            }
        }
    
    async def optimize(self, context: TaskContext) -> TaskResult:
        """Optimize timing for maximum impact."""
        # This is the main entry point when called by orchestrator
        return await self._execute_agent_logic(context)
