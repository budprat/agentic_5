# ABOUTME: Scene Designer agent that creates visual sequences and storyboards for video production
# ABOUTME: Specializes in shot composition, visual transitions, and platform-specific feasibility validation

"""
Scene Designer Agent Implementation

This module implements the Scene Designer agent responsible for:
- Creating visual sequences and storyboards
- Designing shot compositions and camera angles
- Planning visual transitions
- Validating production feasibility
- Platform-specific visual optimization
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple, ClassVar
from datetime import datetime, timezone
import json
import time
from dataclasses import dataclass, field
from enum import Enum
try:
    import google.generativeai as genai
except ImportError:
    from google import genai

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


class ShotType(Enum):
    """Camera shot types."""
    WIDE = "wide"
    MEDIUM = "medium"
    CLOSE_UP = "close_up"
    EXTREME_CLOSE_UP = "extreme_close_up"
    OVERHEAD = "overhead"
    LOW_ANGLE = "low_angle"
    HIGH_ANGLE = "high_angle"
    DUTCH_ANGLE = "dutch_angle"
    POV = "pov"
    TRACKING = "tracking"


class TransitionType(Enum):
    """Scene transition types."""
    CUT = "cut"
    FADE = "fade"
    DISSOLVE = "dissolve"
    WIPE = "wipe"
    ZOOM = "zoom"
    PAN = "pan"
    MATCH_CUT = "match_cut"
    JUMP_CUT = "jump_cut"
    MORPH = "morph"
    GLITCH = "glitch"


@dataclass
class Shot:
    """Individual shot in a scene."""
    shot_number: int
    shot_type: ShotType
    duration: float
    description: str
    camera_movement: Optional[str] = None
    focal_point: Optional[str] = None
    lighting: Optional[str] = None
    props: List[str] = field(default_factory=list)
    effects: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Scene:
    """Scene in the storyboard."""
    scene_number: int
    title: str
    duration: float
    location: str
    time_of_day: str
    shots: List[Shot]
    mood: str
    color_palette: List[str]
    audio_notes: str
    transition_in: TransitionType
    transition_out: TransitionType
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Storyboard:
    """Complete storyboard structure."""
    title: str
    total_duration: float
    scenes: List[Scene]
    aspect_ratio: str
    visual_style: str
    platform: str
    production_notes: List[str]
    equipment_needed: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class SceneDesigner(StandardizedAgentBase):
    """
    Scene Designer Agent
    
    Creates comprehensive storyboards with:
    - Shot-by-shot visual planning
    - Camera angle optimization
    - Transition design
    - Production feasibility validation
    - Platform-specific adaptations
    """
    
    # Platform visual requirements
    PLATFORM_SPECS: ClassVar[Dict[str, Dict[str, Any]]] = {
        "youtube": {
            "aspect_ratio": "16:9",
            "min_shot_duration": 2.0,
            "max_shots_per_minute": 15,
            "supports_complex_transitions": True,
            "preferred_shots": [ShotType.WIDE, ShotType.MEDIUM, ShotType.CLOSE_UP],
            "visual_complexity": "high"
        },
        "tiktok": {
            "aspect_ratio": "9:16",
            "min_shot_duration": 0.5,
            "max_shots_per_minute": 30,
            "supports_complex_transitions": False,
            "preferred_shots": [ShotType.CLOSE_UP, ShotType.MEDIUM, ShotType.POV],
            "visual_complexity": "medium"
        },
        "instagram_reels": {
            "aspect_ratio": "9:16",
            "min_shot_duration": 1.0,
            "max_shots_per_minute": 20,
            "supports_complex_transitions": True,
            "preferred_shots": [ShotType.CLOSE_UP, ShotType.MEDIUM, ShotType.OVERHEAD],
            "visual_complexity": "medium"
        }
    }
    
    # Visual style templates
    VISUAL_STYLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        "cinematic": {
            "shot_preferences": [ShotType.WIDE, ShotType.TRACKING, ShotType.LOW_ANGLE],
            "transition_preferences": [TransitionType.FADE, TransitionType.DISSOLVE],
            "color_mood": "dramatic",
            "lighting": "high_contrast",
            "camera_movement": "smooth_controlled"
        },
        "documentary": {
            "shot_preferences": [ShotType.MEDIUM, ShotType.CLOSE_UP, ShotType.POV],
            "transition_preferences": [TransitionType.CUT, TransitionType.MATCH_CUT],
            "color_mood": "natural",
            "lighting": "available_light",
            "camera_movement": "handheld"
        },
        "vlog": {
            "shot_preferences": [ShotType.MEDIUM, ShotType.CLOSE_UP, ShotType.POV],
            "transition_preferences": [TransitionType.CUT, TransitionType.JUMP_CUT],
            "color_mood": "vibrant",
            "lighting": "soft_natural",
            "camera_movement": "handheld_stable"
        },
        "tutorial": {
            "shot_preferences": [ShotType.CLOSE_UP, ShotType.OVERHEAD, ShotType.MEDIUM],
            "transition_preferences": [TransitionType.CUT, TransitionType.ZOOM],
            "color_mood": "clear",
            "lighting": "even_bright",
            "camera_movement": "static_focused"
        },
        "artistic": {
            "shot_preferences": [ShotType.DUTCH_ANGLE, ShotType.EXTREME_CLOSE_UP, ShotType.OVERHEAD],
            "transition_preferences": [TransitionType.MORPH, TransitionType.GLITCH, TransitionType.DISSOLVE],
            "color_mood": "stylized",
            "lighting": "creative",
            "camera_movement": "dynamic"
        }
    }
    
    def __init__(
        self,
        agent_id: str = "scene_designer",
        connection_pool: ConnectionPool = None,
        quality_framework: QualityThresholdFramework = None,
        config: Dict[str, Any] = None
    ):
        """Initialize Scene Designer agent."""
        config = config or {}
        
        # Set default configuration
        config.setdefault("port", 10213)
        config.setdefault("model", "gemini-2.0-flash-exp")
        config.setdefault("quality_domain", "BUSINESS")
        config.setdefault("temperature", 0.9)
        
        # Initialize base class with proper parameters
        super().__init__(
            agent_name="scene_designer",
            description="Creates visual sequences and storyboards for video production",
            instructions="""You are an expert visual designer for video content.
            Create compelling shot compositions, camera angles, and visual transitions.
            Consider platform-specific requirements and production feasibility.""",
            quality_config={
                "domain": config.get("quality_domain", "GENERIC"),
                "enabled": True,
                "thresholds": {
                    "visual_feasibility": 0.80,
                    "platform_compliance": 0.90
                }
            },
            use_config_manager=False  # Disable config manager for now
        )
        
        # Store additional attributes
        self.agent_id = agent_id
        self.config = config
        self.connection_pool = connection_pool
        self.quality_framework = quality_framework or self.quality_framework
        
        # Initialize Gemini model
        if config.get("gemini_api_key"):
            genai.configure(api_key=config["gemini_api_key"])
            self.model = genai.GenerativeModel(
                config["model"],
                generation_config=genai.GenerationConfig(
                    temperature=config["temperature"],
                    max_output_tokens=8192
                )
            )
        else:
            self.model = None
        
        # System prompt
        self.system_prompt = """You are a Scene Designer specializing in visual storytelling for video production. Create detailed storyboards with shot compositions, camera angles, and visual transitions that enhance the narrative. Consider production feasibility, platform requirements, and visual impact. Your designs should be both creative and practical."""
    
    async def _execute_agent_logic(self, context: TaskContext) -> TaskResult:
        """Execute scene design logic."""
        start_time = time.time()
        
        try:
            # Extract parameters
            script_content = context.parameters.get("script", {})
            platform = context.parameters.get("platform", "youtube")
            visual_style = context.parameters.get("visual_style", "cinematic")
            duration_target = context.parameters.get("duration_target", 60)
            preferences = context.parameters.get("preferences", {})
            
            # Create storyboard
            storyboard = await self.create_storyboard(
                script_content=script_content,
                platform=platform,
                visual_style=visual_style,
                duration_target=duration_target,
                preferences=preferences
            )
            
            # Validate feasibility
            feasibility = await self.validate_feasibility(storyboard)
            
            # Calculate quality scores
            quality_scores = await self._calculate_quality_scores(storyboard, feasibility)
            
            # Create artifacts
            artifacts = [
                ArtifactData(
                    artifact_id=f"storyboard_{int(time.time())}",
                    artifact_type="storyboard",
                    content=self._serialize_storyboard(storyboard),
                    metadata={
                        "platform": platform,
                        "visual_style": visual_style,
                        "scene_count": len(storyboard.scenes),
                        "total_shots": sum(len(s.shots) for s in storyboard.scenes)
                    }
                ),
                ArtifactData(
                    artifact_id=f"production_guide_{int(time.time())}",
                    artifact_type="production_guide",
                    content=json.dumps(self._create_production_guide(storyboard, feasibility)),
                    metadata={"feasibility_score": feasibility["overall_score"]}
                )
            ]
            
            return TaskResult(
                status=ExecutionStatus.COMPLETED,
                confidence_score=quality_scores["overall"],
                artifacts=artifacts,
                metadata={
                    "duration": time.time() - start_time,
                    "quality_scores": quality_scores,
                    "feasibility": feasibility,
                    "storyboard_stats": {
                        "scene_count": len(storyboard.scenes),
                        "total_shots": sum(len(s.shots) for s in storyboard.scenes),
                        "avg_shot_duration": storyboard.total_duration / sum(len(s.shots) for s in storyboard.scenes)
                    }
                }
            )
            
        except Exception as e:
            self.logger.error(f"Scene design failed: {str(e)}", exc_info=True)
            return TaskResult(
                status=ExecutionStatus.FAILED,
                confidence_score=0.0,
                artifacts=[],
                metadata={"error": str(e), "duration": time.time() - start_time}
            )
    
    async def create_storyboard(
        self,
        script_content: Dict[str, Any],
        platform: str,
        visual_style: str,
        duration_target: float,
        preferences: Dict[str, Any]
    ) -> Storyboard:
        """Create complete storyboard from script."""
        # Get platform and style specifications
        platform_spec = self.PLATFORM_SPECS.get(platform, self.PLATFORM_SPECS["youtube"])
        style_spec = self.VISUAL_STYLES.get(visual_style, self.VISUAL_STYLES["cinematic"])
        
        # Parse script into visual scenes
        scenes = await self._create_scenes_from_script(
            script_content,
            platform_spec,
            style_spec,
            duration_target
        )
        
        # Add production details
        production_notes = self._generate_production_notes(scenes, platform_spec)
        equipment_needed = self._determine_equipment_needs(scenes, style_spec)
        
        # Calculate total duration
        total_duration = sum(scene.duration for scene in scenes)
        
        return Storyboard(
            title=script_content.get("title", "Untitled Video"),
            total_duration=total_duration,
            scenes=scenes,
            aspect_ratio=platform_spec["aspect_ratio"],
            visual_style=visual_style,
            platform=platform,
            production_notes=production_notes,
            equipment_needed=equipment_needed,
            metadata={
                "created_at": datetime.now(timezone.utc).isoformat(),
                "target_duration": duration_target,
                "preferences": preferences
            }
        )
    
    async def _create_scenes_from_script(
        self,
        script_content: Dict[str, Any],
        platform_spec: Dict[str, Any],
        style_spec: Dict[str, Any],
        duration_target: float
    ) -> List[Scene]:
        """Create scenes from script content."""
        scenes = []
        script_segments = script_content.get("segments", [])
        
        if not script_segments:
            # Create default scene structure
            return await self._create_default_scenes(duration_target, platform_spec, style_spec)
        
        # Group segments into scenes
        scene_groups = self._group_segments_into_scenes(script_segments)
        
        # Create scene for each group
        for i, group in enumerate(scene_groups):
            scene = await self._create_scene(
                scene_number=i + 1,
                segments=group,
                platform_spec=platform_spec,
                style_spec=style_spec
            )
            scenes.append(scene)
        
        return scenes
    
    def _group_segments_into_scenes(self, segments: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Group script segments into logical scenes."""
        if not segments:
            return []
        
        # Simple grouping by content type changes or timing gaps
        groups = []
        current_group = []
        
        for segment in segments:
            if not current_group:
                current_group.append(segment)
            else:
                # Check if this should start a new scene
                if self._should_start_new_scene(current_group[-1], segment):
                    groups.append(current_group)
                    current_group = [segment]
                else:
                    current_group.append(segment)
        
        if current_group:
            groups.append(current_group)
        
        return groups
    
    def _should_start_new_scene(self, prev_segment: Dict[str, Any], curr_segment: Dict[str, Any]) -> bool:
        """Determine if a new scene should start."""
        # New scene if significant time gap
        prev_end = prev_segment.get("timing", {}).get("end", 0)
        curr_start = curr_segment.get("timing", {}).get("start", 0)
        if curr_start - prev_end > 2.0:
            return True
        
        # New scene if content type changes significantly
        if prev_segment.get("type") != curr_segment.get("type"):
            return True
        
        return False
    
    async def _create_scene(
        self,
        scene_number: int,
        segments: List[Dict[str, Any]],
        platform_spec: Dict[str, Any],
        style_spec: Dict[str, Any]
    ) -> Scene:
        """Create a scene from segments."""
        # Calculate scene duration
        duration = sum(s.get("duration", 5.0) for s in segments)
        
        # Determine scene properties
        title = f"Scene {scene_number}"
        location = self._determine_location(segments)
        time_of_day = self._determine_time_of_day(segments)
        mood = self._determine_mood(segments, style_spec)
        
        # Create shots for the scene
        shots = await self._create_shots_for_scene(
            segments,
            duration,
            platform_spec,
            style_spec
        )
        
        # Determine transitions
        transition_in = self._select_transition(style_spec, "in", scene_number)
        transition_out = self._select_transition(style_spec, "out", scene_number)
        
        # Define color palette
        color_palette = self._generate_color_palette(mood, style_spec)
        
        # Audio notes
        audio_notes = self._generate_audio_notes(segments, mood)
        
        return Scene(
            scene_number=scene_number,
            title=title,
            duration=duration,
            location=location,
            time_of_day=time_of_day,
            shots=shots,
            mood=mood,
            color_palette=color_palette,
            audio_notes=audio_notes,
            transition_in=transition_in,
            transition_out=transition_out,
            metadata={"segment_count": len(segments)}
        )
    
    async def _create_shots_for_scene(
        self,
        segments: List[Dict[str, Any]],
        scene_duration: float,
        platform_spec: Dict[str, Any],
        style_spec: Dict[str, Any]
    ) -> List[Shot]:
        """Create shots for a scene."""
        shots = []
        
        # Calculate optimal shot count
        max_shots = int(scene_duration * platform_spec["max_shots_per_minute"] / 60)
        target_shots = min(max_shots, max(2, len(segments)))
        
        # Distribute duration among shots
        shot_duration = scene_duration / target_shots
        shot_duration = max(platform_spec["min_shot_duration"], shot_duration)
        
        # Create shots
        for i in range(target_shots):
            shot_type = self._select_shot_type(i, target_shots, platform_spec, style_spec)
            
            shot = Shot(
                shot_number=i + 1,
                shot_type=shot_type,
                duration=shot_duration,
                description=await self._generate_shot_description(
                    shot_type,
                    segments[min(i, len(segments)-1)] if segments else {},
                    style_spec
                ),
                camera_movement=self._determine_camera_movement(shot_type, style_spec),
                focal_point=self._determine_focal_point(segments, i),
                lighting=style_spec.get("lighting", "natural"),
                props=self._identify_props(segments, i),
                effects=self._determine_effects(platform_spec, style_spec)
            )
            shots.append(shot)
        
        return shots
    
    def _select_shot_type(
        self,
        shot_index: int,
        total_shots: int,
        platform_spec: Dict[str, Any],
        style_spec: Dict[str, Any]
    ) -> ShotType:
        """Select appropriate shot type."""
        preferred_shots = platform_spec.get("preferred_shots", [])
        style_preferences = style_spec.get("shot_preferences", [])
        
        # Combine preferences
        all_preferences = list(set(preferred_shots + style_preferences))
        
        if not all_preferences:
            all_preferences = list(ShotType)
        
        # Vary shots for visual interest
        return all_preferences[shot_index % len(all_preferences)]
    
    async def _generate_shot_description(
        self,
        shot_type: ShotType,
        segment: Dict[str, Any],
        style_spec: Dict[str, Any]
    ) -> str:
        """Generate shot description."""
        if self.model and segment.get("content"):
            prompt = f"""
            Create a visual shot description for:
            Shot Type: {shot_type.value}
            Content: {segment.get('content', '')}
            Visual Style: {style_spec.get('color_mood', 'natural')}
            
            Describe what the viewer sees in 1-2 sentences.
            """
            
            try:
                response = await self.model.generate_content_async(prompt)
                return response.text.strip()
            except:
                pass
        
        # Fallback description
        return f"{shot_type.value.replace('_', ' ').title()} shot of the main subject"
    
    def _determine_camera_movement(self, shot_type: ShotType, style_spec: Dict[str, Any]) -> str:
        """Determine camera movement for shot."""
        movement_style = style_spec.get("camera_movement", "static")
        
        movements = {
            "smooth_controlled": ["slow pan", "gentle tilt", "smooth dolly"],
            "handheld": ["handheld follow", "slight shake", "natural movement"],
            "handheld_stable": ["stabilized handheld", "smooth follow"],
            "static_focused": ["locked off", "static"],
            "dynamic": ["whip pan", "crash zoom", "rotating"]
        }
        
        movement_options = movements.get(movement_style, ["static"])
        
        # Some shots work better with specific movements
        if shot_type == ShotType.TRACKING:
            return "tracking movement"
        elif shot_type in [ShotType.WIDE, ShotType.EXTREME_CLOSE_UP]:
            return "static"
        
        return movement_options[0]
    
    def _select_transition(
        self,
        style_spec: Dict[str, Any],
        direction: str,
        scene_number: int
    ) -> TransitionType:
        """Select appropriate transition type."""
        preferences = style_spec.get("transition_preferences", [TransitionType.CUT])
        
        # First scene always fades in
        if direction == "in" and scene_number == 1:
            return TransitionType.FADE
        
        # Default to first preference
        return preferences[0] if preferences else TransitionType.CUT
    
    def _determine_location(self, segments: List[Dict[str, Any]]) -> str:
        """Determine scene location from segments."""
        # Simple heuristic - could be enhanced with NLP
        for segment in segments:
            content = segment.get("content", "").lower()
            if "indoor" in content or "room" in content or "office" in content:
                return "Interior"
            elif "outdoor" in content or "outside" in content or "park" in content:
                return "Exterior"
        
        return "Studio"
    
    def _determine_time_of_day(self, segments: List[Dict[str, Any]]) -> str:
        """Determine time of day for scene."""
        for segment in segments:
            content = segment.get("content", "").lower()
            if "morning" in content or "sunrise" in content:
                return "Morning"
            elif "evening" in content or "sunset" in content:
                return "Evening"
            elif "night" in content or "dark" in content:
                return "Night"
        
        return "Day"
    
    def _determine_mood(self, segments: List[Dict[str, Any]], style_spec: Dict[str, Any]) -> str:
        """Determine scene mood."""
        # Check segment emotions
        emotions = [s.get("emotion", "") for s in segments if s.get("emotion")]
        if emotions:
            return emotions[0]
        
        # Use style default
        return style_spec.get("color_mood", "neutral")
    
    def _generate_color_palette(self, mood: str, style_spec: Dict[str, Any]) -> List[str]:
        """Generate color palette for mood."""
        palettes = {
            "dramatic": ["#1a1a1a", "#8b0000", "#ffffff", "#4a4a4a"],
            "natural": ["#87ceeb", "#228b22", "#deb887", "#f5f5dc"],
            "vibrant": ["#ff6b6b", "#4ecdc4", "#45b7d1", "#f9ca24"],
            "clear": ["#ffffff", "#f0f0f0", "#333333", "#0066cc"],
            "stylized": ["#e056fd", "#f0932b", "#22a6b3", "#130f40"],
            "energetic": ["#ff4757", "#ffa502", "#32ff7e", "#7bed9f"],
            "neutral": ["#dfe6e9", "#b2bec3", "#636e72", "#2d3436"]
        }
        
        return palettes.get(mood, palettes["neutral"])
    
    def _generate_audio_notes(self, segments: List[Dict[str, Any]], mood: str) -> str:
        """Generate audio notes for scene."""
        audio_moods = {
            "dramatic": "Intense orchestral music, building tension",
            "natural": "Ambient nature sounds, subtle background music",
            "vibrant": "Upbeat energetic music, modern pop influences",
            "clear": "Minimal background music, clear voiceover focus",
            "stylized": "Electronic or experimental music, unique sound design",
            "energetic": "High-energy music, strong beat, motivational",
            "neutral": "Soft instrumental music, non-intrusive"
        }
        
        return audio_moods.get(mood, "Appropriate background music")
    
    def _determine_focal_point(self, segments: List[Dict[str, Any]], shot_index: int) -> str:
        """Determine focal point for shot."""
        if shot_index < len(segments):
            segment = segments[shot_index]
            if segment.get("type") == "dialogue" and segment.get("speaker"):
                return segment["speaker"]
        
        return "Main subject"
    
    def _identify_props(self, segments: List[Dict[str, Any]], shot_index: int) -> List[str]:
        """Identify props needed for shot."""
        # Basic prop identification - could be enhanced
        props = []
        
        if shot_index < len(segments):
            content = segments[shot_index].get("content", "").lower()
            
            # Common props based on content
            if "computer" in content or "laptop" in content:
                props.append("laptop")
            if "phone" in content:
                props.append("smartphone")
            if "book" in content:
                props.append("book")
            if "coffee" in content:
                props.append("coffee cup")
        
        return props
    
    def _determine_effects(self, platform_spec: Dict[str, Any], style_spec: Dict[str, Any]) -> List[str]:
        """Determine visual effects for shot."""
        effects = []
        
        # Platform-specific effects
        if platform_spec.get("visual_complexity") == "high":
            effects.extend(["color grading", "subtle vfx"])
        
        # Style-specific effects
        if "glitch" in [t.value for t in style_spec.get("transition_preferences", [])]:
            effects.append("glitch effects")
        
        return effects
    
    async def _create_default_scenes(
        self,
        duration_target: float,
        platform_spec: Dict[str, Any],
        style_spec: Dict[str, Any]
    ) -> List[Scene]:
        """Create default scene structure when no script provided."""
        # Create 3 basic scenes
        scenes_data = [
            {"title": "Opening", "duration_ratio": 0.2, "mood": "engaging"},
            {"title": "Main Content", "duration_ratio": 0.6, "mood": "informative"},
            {"title": "Closing", "duration_ratio": 0.2, "mood": "inspiring"}
        ]
        
        scenes = []
        for i, scene_data in enumerate(scenes_data):
            duration = duration_target * scene_data["duration_ratio"]
            
            scene = Scene(
                scene_number=i + 1,
                title=scene_data["title"],
                duration=duration,
                location="Studio",
                time_of_day="Day",
                shots=await self._create_shots_for_scene(
                    [],
                    duration,
                    platform_spec,
                    style_spec
                ),
                mood=scene_data["mood"],
                color_palette=self._generate_color_palette(scene_data["mood"], style_spec),
                audio_notes=self._generate_audio_notes([], scene_data["mood"]),
                transition_in=TransitionType.FADE if i == 0 else TransitionType.CUT,
                transition_out=TransitionType.FADE if i == 2 else TransitionType.CUT
            )
            scenes.append(scene)
        
        return scenes
    
    async def validate_feasibility(self, storyboard: Storyboard) -> Dict[str, Any]:
        """Validate production feasibility of storyboard."""
        checks = {
            "equipment_availability": self._check_equipment_feasibility(storyboard),
            "timing_feasibility": self._check_timing_feasibility(storyboard),
            "complexity_assessment": self._assess_complexity(storyboard),
            "platform_compliance": self._check_platform_compliance(storyboard),
            "budget_estimate": self._estimate_budget_category(storyboard)
        }
        
        # Calculate overall feasibility score
        scores = [check.get("score", 0.5) for check in checks.values()]
        overall_score = sum(scores) / len(scores)
        
        return {
            "overall_score": overall_score,
            "checks": checks,
            "is_feasible": overall_score >= 0.7,
            "recommendations": self._generate_feasibility_recommendations(checks)
        }
    
    def _check_equipment_feasibility(self, storyboard: Storyboard) -> Dict[str, Any]:
        """Check if required equipment is reasonable."""
        equipment = storyboard.equipment_needed
        
        # Basic equipment categories
        basic_equipment = ["camera", "tripod", "microphone", "lights"]
        advanced_equipment = ["drone", "gimbal", "crane", "dolly"]
        
        basic_count = sum(1 for e in equipment if any(b in e.lower() for b in basic_equipment))
        advanced_count = sum(1 for e in equipment if any(a in e.lower() for a in advanced_equipment))
        
        if advanced_count > 2:
            score = 0.6
            note = "Requires significant advanced equipment"
        elif advanced_count > 0:
            score = 0.8
            note = "Requires some advanced equipment"
        else:
            score = 0.95
            note = "Basic equipment sufficient"
        
        return {"score": score, "note": note, "equipment_list": equipment}
    
    def _check_timing_feasibility(self, storyboard: Storyboard) -> Dict[str, Any]:
        """Check if timing is realistic."""
        total_shots = sum(len(scene.shots) for scene in storyboard.scenes)
        avg_shot_duration = storyboard.total_duration / total_shots if total_shots > 0 else 0
        
        platform_spec = self.PLATFORM_SPECS.get(storyboard.platform, self.PLATFORM_SPECS["youtube"])
        min_duration = platform_spec["min_shot_duration"]
        
        if avg_shot_duration < min_duration:
            score = 0.5
            note = f"Shots too short ({avg_shot_duration:.1f}s avg, {min_duration}s min)"
        elif avg_shot_duration < min_duration * 1.5:
            score = 0.8
            note = "Tight timing but achievable"
        else:
            score = 0.95
            note = "Comfortable timing"
        
        return {"score": score, "note": note, "avg_shot_duration": avg_shot_duration}
    
    def _assess_complexity(self, storyboard: Storyboard) -> Dict[str, Any]:
        """Assess overall production complexity."""
        complexity_factors = {
            "location_changes": len(set(s.location for s in storyboard.scenes)),
            "unique_shots": len(set(shot.shot_type for s in storyboard.scenes for shot in s.shots)),
            "effects_required": sum(len(shot.effects) for s in storyboard.scenes for shot in s.shots),
            "props_needed": len(set(prop for s in storyboard.scenes for shot in s.shots for prop in shot.props))
        }
        
        complexity_score = sum([
            1 - min(complexity_factors["location_changes"] / 5, 1.0) * 0.3,
            1 - min(complexity_factors["unique_shots"] / 10, 1.0) * 0.2,
            1 - min(complexity_factors["effects_required"] / 20, 1.0) * 0.3,
            1 - min(complexity_factors["props_needed"] / 15, 1.0) * 0.2
        ])
        
        if complexity_score < 0.5:
            note = "Very complex production"
        elif complexity_score < 0.7:
            note = "Moderately complex production"
        else:
            note = "Straightforward production"
        
        return {"score": complexity_score, "note": note, "factors": complexity_factors}
    
    def _check_platform_compliance(self, storyboard: Storyboard) -> Dict[str, Any]:
        """Check compliance with platform specifications."""
        platform_spec = self.PLATFORM_SPECS.get(storyboard.platform)
        if not platform_spec:
            return {"score": 0.5, "note": "Unknown platform"}
        
        issues = []
        
        # Check aspect ratio
        if storyboard.aspect_ratio != platform_spec["aspect_ratio"]:
            issues.append(f"Wrong aspect ratio (using {storyboard.aspect_ratio}, need {platform_spec['aspect_ratio']})")
        
        # Check shot pacing
        total_shots = sum(len(s.shots) for s in storyboard.scenes)
        shots_per_minute = (total_shots / storyboard.total_duration) * 60
        if shots_per_minute > platform_spec["max_shots_per_minute"]:
            issues.append(f"Too many shots per minute ({shots_per_minute:.1f} vs {platform_spec['max_shots_per_minute']} max)")
        
        score = 1.0 - (len(issues) * 0.3)
        score = max(0.3, score)
        
        return {
            "score": score,
            "note": "Platform compliant" if not issues else f"{len(issues)} compliance issues",
            "issues": issues
        }
    
    def _estimate_budget_category(self, storyboard: Storyboard) -> Dict[str, Any]:
        """Estimate production budget category."""
        # Simple estimation based on complexity
        factors = {
            "equipment": len(storyboard.equipment_needed),
            "locations": len(set(s.location for s in storyboard.scenes)),
            "duration": storyboard.total_duration,
            "effects": sum(len(shot.effects) for s in storyboard.scenes for shot in s.shots)
        }
        
        # Score calculation (lower is more expensive)
        budget_score = 1.0
        budget_score -= min(factors["equipment"] / 20, 0.3)
        budget_score -= min(factors["locations"] / 5, 0.2)
        budget_score -= min(factors["duration"] / 600, 0.2)  # 10 minutes
        budget_score -= min(factors["effects"] / 30, 0.3)
        
        if budget_score > 0.8:
            category = "Low budget"
        elif budget_score > 0.6:
            category = "Moderate budget"
        elif budget_score > 0.4:
            category = "Significant budget"
        else:
            category = "High budget"
        
        return {"score": budget_score, "note": category, "factors": factors}
    
    def _generate_feasibility_recommendations(self, checks: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on feasibility checks."""
        recommendations = []
        
        for check_name, check_result in checks.items():
            if check_result["score"] < 0.7:
                if check_name == "equipment_availability":
                    recommendations.append("Consider renting specialized equipment or simplifying shots")
                elif check_name == "timing_feasibility":
                    recommendations.append("Extend shot durations or reduce shot count")
                elif check_name == "complexity_assessment":
                    recommendations.append("Simplify production by reducing locations or effects")
                elif check_name == "platform_compliance":
                    recommendations.append("Adjust storyboard to meet platform requirements")
                elif check_name == "budget_estimate":
                    recommendations.append("Consider scaling back scope or seeking additional resources")
        
        if not recommendations:
            recommendations.append("Production plan is well-balanced and feasible")
        
        return recommendations
    
    def _generate_production_notes(self, scenes: List[Scene], platform_spec: Dict[str, Any]) -> List[str]:
        """Generate production notes."""
        notes = []
        
        # Platform-specific notes
        notes.append(f"Shoot in {platform_spec['aspect_ratio']} aspect ratio")
        
        # Location notes
        unique_locations = set(s.location for s in scenes)
        notes.append(f"Locations needed: {', '.join(unique_locations)}")
        
        # Timing notes
        total_shots = sum(len(s.shots) for s in scenes)
        notes.append(f"Total shots to capture: {total_shots}")
        
        # Transition notes
        unique_transitions = set()
        for scene in scenes:
            unique_transitions.add(scene.transition_in)
            unique_transitions.add(scene.transition_out)
        
        if len(unique_transitions) > 2:
            notes.append("Multiple transition types - plan for post-production")
        
        return notes
    
    def _determine_equipment_needs(self, scenes: List[Scene], style_spec: Dict[str, Any]) -> List[str]:
        """Determine equipment needed for production."""
        equipment = ["Camera", "Tripod", "Microphone"]
        
        # Check for specific shot requirements
        shot_types = set()
        for scene in scenes:
            for shot in scene.shots:
                shot_types.add(shot.shot_type)
        
        # Add equipment based on shots
        if ShotType.TRACKING in shot_types:
            equipment.append("Gimbal or dolly")
        if ShotType.OVERHEAD in shot_types:
            equipment.append("Overhead rig or drone")
        if any(st in shot_types for st in [ShotType.LOW_ANGLE, ShotType.HIGH_ANGLE]):
            equipment.append("Adjustable tripod or crane")
        
        # Lighting needs
        if style_spec.get("lighting") != "available_light":
            equipment.extend(["LED panels", "Reflectors"])
        
        # Audio needs
        if any(s.audio_notes for s in scenes):
            equipment.append("External audio recorder")
        
        return equipment
    
    async def _calculate_quality_scores(
        self,
        storyboard: Storyboard,
        feasibility: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate quality scores for the storyboard."""
        scores = {
            "visual_coherence": self._score_visual_coherence(storyboard),
            "narrative_flow": self._score_narrative_flow(storyboard),
            "production_quality": feasibility["overall_score"],
            "creativity": self._score_creativity(storyboard),
            "platform_optimization": self._score_platform_optimization(storyboard)
        }
        
        scores["overall"] = sum(scores.values()) / len(scores)
        return scores
    
    def _score_visual_coherence(self, storyboard: Storyboard) -> float:
        """Score visual coherence of storyboard."""
        # Check consistency in visual style
        score = 0.9
        
        # Check color palette consistency
        color_sets = [set(s.color_palette) for s in storyboard.scenes]
        if len(color_sets) > 1:
            # Calculate overlap between consecutive scenes
            for i in range(1, len(color_sets)):
                overlap = len(color_sets[i-1] & color_sets[i]) / len(color_sets[i-1])
                if overlap < 0.5:
                    score -= 0.1
        
        return max(0.5, score)
    
    def _score_narrative_flow(self, storyboard: Storyboard) -> float:
        """Score narrative flow between scenes."""
        if len(storyboard.scenes) < 2:
            return 0.7
        
        score = 0.85
        
        # Check scene transitions
        for i in range(1, len(storyboard.scenes)):
            prev_scene = storyboard.scenes[i-1]
            curr_scene = storyboard.scenes[i]
            
            # Matching transitions
            if prev_scene.transition_out != curr_scene.transition_in:
                score -= 0.05
        
        return max(0.5, score)
    
    def _score_creativity(self, storyboard: Storyboard) -> float:
        """Score creativity and visual interest."""
        # Variety in shot types
        unique_shots = set()
        for scene in storyboard.scenes:
            for shot in scene.shots:
                unique_shots.add(shot.shot_type)
        
        shot_variety_score = min(len(unique_shots) / 5, 1.0)
        
        # Variety in transitions
        unique_transitions = set()
        for scene in storyboard.scenes:
            unique_transitions.add(scene.transition_in)
            unique_transitions.add(scene.transition_out)
        
        transition_variety_score = min(len(unique_transitions) / 3, 1.0)
        
        return (shot_variety_score + transition_variety_score) / 2
    
    def _score_platform_optimization(self, storyboard: Storyboard) -> float:
        """Score platform optimization."""
        platform_spec = self.PLATFORM_SPECS.get(storyboard.platform)
        if not platform_spec:
            return 0.5
        
        score = 0.9
        
        # Check if using preferred shots
        platform_preferred = set(platform_spec["preferred_shots"])
        used_shots = set()
        for scene in storyboard.scenes:
            for shot in scene.shots:
                used_shots.add(shot.shot_type)
        
        preference_match = len(platform_preferred & used_shots) / len(platform_preferred)
        score = 0.5 + (preference_match * 0.5)
        
        return score
    
    def _serialize_storyboard(self, storyboard: Storyboard) -> str:
        """Serialize storyboard to JSON."""
        return json.dumps({
            "title": storyboard.title,
            "total_duration": storyboard.total_duration,
            "aspect_ratio": storyboard.aspect_ratio,
            "visual_style": storyboard.visual_style,
            "platform": storyboard.platform,
            "scenes": [
                {
                    "scene_number": s.scene_number,
                    "title": s.title,
                    "duration": s.duration,
                    "location": s.location,
                    "time_of_day": s.time_of_day,
                    "mood": s.mood,
                    "color_palette": s.color_palette,
                    "audio_notes": s.audio_notes,
                    "transition_in": s.transition_in.value,
                    "transition_out": s.transition_out.value,
                    "shots": [
                        {
                            "shot_number": shot.shot_number,
                            "shot_type": shot.shot_type.value,
                            "duration": shot.duration,
                            "description": shot.description,
                            "camera_movement": shot.camera_movement,
                            "focal_point": shot.focal_point,
                            "lighting": shot.lighting,
                            "props": shot.props,
                            "effects": shot.effects
                        }
                        for shot in s.shots
                    ]
                }
                for s in storyboard.scenes
            ],
            "production_notes": storyboard.production_notes,
            "equipment_needed": storyboard.equipment_needed,
            "metadata": storyboard.metadata
        }, indent=2)
    
    def _create_production_guide(
        self,
        storyboard: Storyboard,
        feasibility: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create production guide from storyboard."""
        return {
            "overview": {
                "title": storyboard.title,
                "duration": storyboard.total_duration,
                "platform": storyboard.platform,
                "visual_style": storyboard.visual_style
            },
            "pre_production": {
                "equipment_checklist": storyboard.equipment_needed,
                "location_scouting": list(set(s.location for s in storyboard.scenes)),
                "props_needed": list(set(
                    prop for s in storyboard.scenes 
                    for shot in s.shots 
                    for prop in shot.props
                ))
            },
            "production_schedule": {
                "total_scenes": len(storyboard.scenes),
                "total_shots": sum(len(s.shots) for s in storyboard.scenes),
                "estimated_shoot_time": self._estimate_shoot_time(storyboard)
            },
            "post_production": {
                "transitions_needed": list(set(
                    s.transition_in.value for s in storyboard.scenes
                ).union(set(s.transition_out.value for s in storyboard.scenes))),
                "effects_required": list(set(
                    effect for s in storyboard.scenes 
                    for shot in s.shots 
                    for effect in shot.effects
                )),
                "color_grading_notes": self._generate_color_grading_notes(storyboard)
            },
            "feasibility_summary": feasibility,
            "recommendations": feasibility["recommendations"]
        }
    
    def _estimate_shoot_time(self, storyboard: Storyboard) -> str:
        """Estimate total shoot time."""
        total_shots = sum(len(s.shots) for s in storyboard.scenes)
        # Assume 15-30 minutes per shot including setup
        min_time = total_shots * 15
        max_time = total_shots * 30
        
        min_hours = min_time / 60
        max_hours = max_time / 60
        
        return f"{min_hours:.1f} - {max_hours:.1f} hours"
    
    def _generate_color_grading_notes(self, storyboard: Storyboard) -> List[str]:
        """Generate color grading notes."""
        notes = []
        
        # Overall style
        notes.append(f"Overall visual style: {storyboard.visual_style}")
        
        # Scene-specific moods
        unique_moods = set(s.mood for s in storyboard.scenes)
        notes.append(f"Moods to convey: {', '.join(unique_moods)}")
        
        # Color consistency
        notes.append("Maintain color consistency across scenes while respecting mood changes")
        
        return notes
    
    async def research(self, context: TaskContext) -> TaskResult:
        """Research visual references and trends."""
        # This method would be called during parallel execution
        # For now, return basic research data
        return TaskResult(
            status=ExecutionStatus.COMPLETED,
            confidence_score=0.85,
            artifacts=[
                ArtifactData(
                    artifact_id=f"visual_research_{int(time.time())}",
                    artifact_type="research",
                    content=json.dumps({
                        "trending_styles": ["minimalist", "neon", "retro"],
                        "color_trends": ["pastel", "high_contrast", "monochrome"],
                        "transition_trends": ["smooth", "glitch", "match_cut"]
                    }),
                    metadata={"source": "visual_research"}
                )
            ],
            metadata={"research_type": "visual_trends"}
        )
