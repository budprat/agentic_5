# ABOUTME: Script Writer agent that creates engaging video scripts with dialogue, narration, and story structure
# ABOUTME: Specializes in tone adaptation, platform-specific writing styles, and content quality scoring

"""
Script Writer Agent Implementation

This module implements the Script Writer agent responsible for:
- Creating engaging dialogue and narration
- Adapting tone and style to target audience
- Platform-specific script optimization
- Story structure and pacing
- Integration with Video Orchestrator
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


class WritingStyle(Enum):
    """Supported writing styles."""
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    MARKETING = "marketing"
    STORYTELLING = "storytelling"
    TUTORIAL = "tutorial"
    VIRAL = "viral"


@dataclass
class ScriptSegment:
    """Individual script segment."""
    type: str  # dialogue, narration, sound_effect, visual_cue
    content: str
    duration: float
    speaker: Optional[str] = None
    emotion: Optional[str] = None
    timing: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VideoScript:
    """Complete video script structure."""
    title: str
    segments: List[ScriptSegment]
    total_duration: float
    style: WritingStyle
    platform: str
    hooks: List[str]
    ctas: List[str]
    keywords: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class ScriptWriter(StandardizedAgentBase):
    """
    Video Script Writer Agent
    
    Creates engaging scripts with:
    - Platform-optimized content structure
    - Adaptive writing styles
    - Emotional storytelling
    - Clear dialogue and narration
    - Integrated production cues
    """
    
    # Writing style configurations
    STYLE_CONFIGS: ClassVar[Dict[WritingStyle, Dict[str, Any]]] = {
        WritingStyle.EDUCATIONAL: {
            "tone": "clear, structured, informative",
            "vocabulary": "accessible",
            "pacing": "moderate",
            "structure": ["introduction", "key_concepts", "examples", "summary"],
            "techniques": ["analogies", "step_by_step", "repetition"]
        },
        WritingStyle.ENTERTAINMENT: {
            "tone": "engaging, dynamic, emotional",
            "vocabulary": "conversational",
            "pacing": "varied",
            "structure": ["hook", "setup", "conflict", "resolution"],
            "techniques": ["humor", "surprise", "cliffhangers"]
        },
        WritingStyle.MARKETING: {
            "tone": "persuasive, benefit-focused",
            "vocabulary": "action-oriented",
            "pacing": "urgent",
            "structure": ["problem", "solution", "benefits", "cta"],
            "techniques": ["social_proof", "urgency", "emotion"]
        },
        WritingStyle.STORYTELLING: {
            "tone": "narrative-driven, character-focused",
            "vocabulary": "descriptive",
            "pacing": "dramatic",
            "structure": ["setup", "rising_action", "climax", "resolution"],
            "techniques": ["character_development", "plot_twists", "imagery"]
        },
        WritingStyle.TUTORIAL: {
            "tone": "instructional, encouraging",
            "vocabulary": "technical_but_clear",
            "pacing": "steady",
            "structure": ["objective", "prerequisites", "steps", "verification"],
            "techniques": ["demonstration", "practice", "troubleshooting"]
        },
        WritingStyle.VIRAL: {
            "tone": "energetic, surprising",
            "vocabulary": "trendy",
            "pacing": "rapid",
            "structure": ["instant_hook", "payoff", "share_trigger"],
            "techniques": ["pattern_interrupt", "relatable", "shareable"]
        }
    }
    
    # Platform-specific adaptations
    PLATFORM_ADAPTATIONS: ClassVar[Dict[str, Dict[str, Any]]] = {
        "youtube": {
            "opening_duration": 15,
            "chapter_breaks": True,
            "detail_level": "comprehensive",
            "cta_placement": ["middle", "end"],
            "optimal_segments": 10
        },
        "tiktok": {
            "opening_duration": 3,
            "chapter_breaks": False,
            "detail_level": "concise",
            "cta_placement": ["end"],
            "optimal_segments": 3
        },
        "instagram_reels": {
            "opening_duration": 5,
            "chapter_breaks": False,
            "detail_level": "visual_focused",
            "cta_placement": ["end"],
            "optimal_segments": 5
        }
    }
    
    def __init__(
        self,
        agent_id: str = "script_writer",
        connection_pool: ConnectionPool = None,
        quality_framework: QualityThresholdFramework = None,
        config: Dict[str, Any] = None
    ):
        """Initialize Script Writer agent."""
        config = config or {}
        
        # Set default configuration
        config.setdefault("port", 10212)
        config.setdefault("model", "gemini-2.0-flash-exp")
        config.setdefault("quality_domain", "BUSINESS")
        config.setdefault("temperature", 0.8)
        
        # Initialize base class with proper parameters
        super().__init__(
            agent_name="script_writer",
            description="Creates engaging video scripts with dialogue, narration, and story structure",
            instructions="""You are an expert video script writer who creates engaging content.
            Adapt tone and style to target audience and platform requirements.
            Focus on storytelling, pacing, and viewer engagement.""",
            quality_config={
                "domain": config.get("quality_domain", "GENERIC"),
                "enabled": True,
                "thresholds": {
                    "script_coherence": 0.85,
                    "engagement_potential": 0.80
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
        self.system_prompt = """You are a Video Script Writer specializing in creating engaging scripts for various video formats. Write compelling dialogue and narration that captures attention, delivers value, and drives action. Adapt your writing style to match the target audience and platform while maintaining clarity and impact. Include cues for visuals, sound effects, and music."""
    
    async def _execute_agent_logic(self, context: TaskContext) -> TaskResult:
        """Execute script writing logic."""
        start_time = time.time()
        
        try:
            # Extract parameters
            content = context.parameters.get("content", "")
            platform = context.parameters.get("platform", "youtube")
            style = context.parameters.get("style", "educational")
            preferences = context.parameters.get("preferences", {})
            hooks = context.parameters.get("hooks", [])
            duration_target = context.parameters.get("duration_target", 60)
            
            # Determine writing style
            writing_style = self._determine_writing_style(style)
            
            # Generate script
            script = await self.generate_script(
                content=content,
                platform=platform,
                writing_style=writing_style,
                preferences=preferences,
                hooks=hooks,
                duration_target=duration_target
            )
            
            # Calculate quality scores
            quality_scores = await self._calculate_quality_scores(script)
            
            # Create artifacts
            artifacts = [
                ArtifactData(
                    artifact_id=f"script_{int(time.time())}",
                    artifact_type="video_script",
                    content=self._serialize_script(script),
                    metadata={
                        "platform": platform,
                        "style": style,
                        "duration": script.total_duration,
                        "segment_count": len(script.segments)
                    }
                )
            ]
            
            return TaskResult(
                status=ExecutionStatus.COMPLETED,
                confidence_score=quality_scores["overall"],
                artifacts=artifacts,
                metadata={
                    "duration": time.time() - start_time,
                    "quality_scores": quality_scores,
                    "script_stats": {
                        "word_count": self._count_words(script),
                        "segment_count": len(script.segments),
                        "dialogue_ratio": self._calculate_dialogue_ratio(script)
                    }
                }
            )
            
        except Exception as e:
            self.logger.error(f"Script generation failed: {str(e)}", exc_info=True)
            return TaskResult(
                status=ExecutionStatus.FAILED,
                confidence_score=0.0,
                artifacts=[],
                metadata={"error": str(e), "duration": time.time() - start_time}
            )
    
    def _determine_writing_style(self, style_str: str) -> WritingStyle:
        """Determine writing style from string input."""
        style_map = {
            "educational": WritingStyle.EDUCATIONAL,
            "entertainment": WritingStyle.ENTERTAINMENT,
            "marketing": WritingStyle.MARKETING,
            "storytelling": WritingStyle.STORYTELLING,
            "tutorial": WritingStyle.TUTORIAL,
            "viral": WritingStyle.VIRAL
        }
        return style_map.get(style_str.lower(), WritingStyle.EDUCATIONAL)
    
    async def generate_script(
        self,
        content: str,
        platform: str,
        writing_style: WritingStyle,
        preferences: Dict[str, Any],
        hooks: List[str],
        duration_target: int
    ) -> VideoScript:
        """Generate complete video script."""
        # Get style and platform configurations
        style_config = self.STYLE_CONFIGS[writing_style]
        platform_config = self.PLATFORM_ADAPTATIONS.get(platform, self.PLATFORM_ADAPTATIONS["youtube"])
        
        # Build script structure
        structure = await self._build_script_structure(
            content, writing_style, platform_config, duration_target
        )
        
        # Generate script segments
        segments = []
        current_time = 0.0
        
        for section in structure:
            section_segments = await self._generate_section(
                section=section,
                content=content,
                style_config=style_config,
                preferences=preferences,
                current_time=current_time
            )
            segments.extend(section_segments)
            current_time = sum(s.duration for s in segments)
        
        # Add hooks at the beginning
        if hooks:
            hook_segment = await self._create_hook_segment(hooks[0], platform_config)
            segments.insert(0, hook_segment)
        
        # Add CTAs
        cta_segments = await self._create_cta_segments(platform_config, content)
        segments.extend(cta_segments)
        
        # Calculate total duration
        total_duration = sum(s.duration for s in segments)
        
        # Extract keywords
        keywords = await self._extract_keywords(content, segments)
        
        return VideoScript(
            title=await self._generate_title(content, writing_style),
            segments=segments,
            total_duration=total_duration,
            style=writing_style,
            platform=platform,
            hooks=hooks,
            ctas=[s.content for s in cta_segments],
            keywords=keywords,
            metadata={
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "target_duration": duration_target,
                "actual_duration": total_duration
            }
        )
    
    async def _build_script_structure(
        self,
        content: str,
        style: WritingStyle,
        platform_config: Dict[str, Any],
        duration_target: int
    ) -> List[Dict[str, Any]]:
        """Build script structure based on style and platform."""
        style_config = self.STYLE_CONFIGS[style]
        structure = style_config["structure"]
        
        # Allocate time to each section
        section_count = len(structure)
        base_duration = duration_target / section_count
        
        # Adjust for platform-specific needs
        sections = []
        for i, section_type in enumerate(structure):
            duration = base_duration
            
            # First section gets less time on short-form platforms
            if i == 0 and platform_config["opening_duration"] < 10:
                duration = platform_config["opening_duration"]
            
            sections.append({
                "type": section_type,
                "duration": duration,
                "content_focus": self._get_section_focus(section_type, content)
            })
        
        return sections
    
    def _get_section_focus(self, section_type: str, content: str) -> str:
        """Determine content focus for each section type."""
        section_focuses = {
            "introduction": "Set context and expectations",
            "hook": "Grab attention immediately",
            "key_concepts": "Present main ideas clearly",
            "examples": "Illustrate with concrete cases",
            "summary": "Reinforce key takeaways",
            "setup": "Establish situation and characters",
            "conflict": "Create tension or problem",
            "resolution": "Provide satisfying conclusion",
            "problem": "Identify pain points",
            "solution": "Present your offering",
            "benefits": "Highlight value propositions",
            "cta": "Drive specific action"
        }
        return section_focuses.get(section_type, "Develop content")
    
    async def _generate_section(
        self,
        section: Dict[str, Any],
        content: str,
        style_config: Dict[str, Any],
        preferences: Dict[str, Any],
        current_time: float
    ) -> List[ScriptSegment]:
        """Generate script segments for a section."""
        if not self.model:
            # Fallback without Gemini API
            return self._generate_section_fallback(section, current_time)
        
        # Build prompt for Gemini
        prompt = f"""
        Generate script segments for a video section.
        
        Content: {content}
        Section Type: {section['type']}
        Section Focus: {section['content_focus']}
        Duration: {section['duration']} seconds
        Tone: {style_config['tone']}
        Vocabulary: {style_config['vocabulary']}
        Audience: {preferences.get('audience', 'general')}
        
        Create a mix of:
        - Narration (voiceover)
        - Visual cues (what viewers see)
        - Sound effects (if applicable)
        - Music cues (mood/energy)
        
        Format each segment as:
        [TYPE] (DURATION): CONTENT
        
        Make it engaging and appropriate for the platform.
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            return self._parse_generated_segments(response.text, current_time)
        except Exception as e:
            self.logger.error(f"Gemini generation failed: {e}")
            return self._generate_section_fallback(section, current_time)
    
    def _generate_section_fallback(
        self,
        section: Dict[str, Any],
        current_time: float
    ) -> List[ScriptSegment]:
        """Generate section segments without API."""
        segments = []
        
        # Create a basic segment for the section
        segment = ScriptSegment(
            type="narration",
            content=f"{section['type'].replace('_', ' ').title()}: {section['content_focus']}",
            duration=section['duration'],
            timing={"start": current_time, "end": current_time + section['duration']}
        )
        segments.append(segment)
        
        return segments
    
    def _parse_generated_segments(self, generated_text: str, start_time: float) -> List[ScriptSegment]:
        """Parse Gemini-generated text into script segments."""
        segments = []
        current_time = start_time
        
        lines = generated_text.strip().split('\n')
        for line in lines:
            if not line.strip():
                continue
            
            # Parse format: [TYPE] (DURATION): CONTENT
            if line.startswith('[') and ']' in line and '(' in line and ')' in line:
                try:
                    type_end = line.index(']')
                    segment_type = line[1:type_end].lower()
                    
                    duration_start = line.index('(') + 1
                    duration_end = line.index(')')
                    duration = float(line[duration_start:duration_end])
                    
                    content_start = line.index(':') + 1
                    content = line[content_start:].strip()
                    
                    segment = ScriptSegment(
                        type=segment_type,
                        content=content,
                        duration=duration,
                        timing={
                            "start": current_time,
                            "end": current_time + duration
                        }
                    )
                    segments.append(segment)
                    current_time += duration
                    
                except (ValueError, IndexError) as e:
                    self.logger.warning(f"Failed to parse segment: {line}")
                    continue
        
        return segments
    
    async def _create_hook_segment(self, hook_text: str, platform_config: Dict[str, Any]) -> ScriptSegment:
        """Create hook segment for the beginning."""
        duration = platform_config["opening_duration"]
        
        return ScriptSegment(
            type="narration",
            content=hook_text,
            duration=duration,
            emotion="energetic",
            timing={"start": 0, "end": duration},
            metadata={"priority": "high", "purpose": "hook"}
        )
    
    async def _create_cta_segments(
        self,
        platform_config: Dict[str, Any],
        content: str
    ) -> List[ScriptSegment]:
        """Create call-to-action segments."""
        segments = []
        
        for placement in platform_config["cta_placement"]:
            cta_content = self._generate_cta_content(platform_config, content, placement)
            
            segment = ScriptSegment(
                type="narration",
                content=cta_content,
                duration=5.0,  # Standard CTA duration
                emotion="encouraging",
                metadata={"purpose": "cta", "placement": placement}
            )
            segments.append(segment)
        
        return segments
    
    def _generate_cta_content(self, platform_config: Dict[str, Any], content: str, placement: str) -> str:
        """Generate CTA content based on platform and placement."""
        platform_ctas = {
            "youtube": {
                "middle": "If you're finding this helpful, hit that like button!",
                "end": "Subscribe for more content like this and ring the notification bell!"
            },
            "tiktok": {
                "end": "Follow for more tips! Share if this helped you!"
            },
            "instagram_reels": {
                "end": "Save this for later and follow for daily tips!"
            }
        }
        
        platform = next((p for p in ["youtube", "tiktok", "instagram_reels"] 
                        if p in str(platform_config)), "youtube")
        
        return platform_ctas.get(platform, {}).get(placement, "Thanks for watching!")
    
    async def _generate_title(self, content: str, style: WritingStyle) -> str:
        """Generate engaging video title."""
        if self.model:
            prompt = f"Generate a catchy video title for: {content}. Style: {style.value}. Maximum 60 characters."
            try:
                response = await self.model.generate_content_async(prompt)
                return response.text.strip().strip('"')
            except:
                pass
        
        # Fallback title
        return f"{content[:50]}..." if len(content) > 50 else content
    
    async def _extract_keywords(self, content: str, segments: List[ScriptSegment]) -> List[str]:
        """Extract keywords from content and script."""
        # Simple keyword extraction - in production would use NLP
        words = content.lower().split()
        
        # Filter common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        keywords = [w for w in words if len(w) > 3 and w not in common_words]
        
        # Take top 10 most relevant
        return list(set(keywords))[:10]
    
    async def _calculate_quality_scores(self, script: VideoScript) -> Dict[str, float]:
        """Calculate quality scores for the script."""
        scores = {
            "coherence": await self._score_coherence(script),
            "engagement": await self._score_engagement(script),
            "clarity": await self._score_clarity(script),
            "pacing": await self._score_pacing(script),
            "platform_fit": await self._score_platform_fit(script)
        }
        
        scores["overall"] = sum(scores.values()) / len(scores)
        return scores
    
    async def _score_coherence(self, script: VideoScript) -> float:
        """Score script coherence and flow."""
        # Check logical flow between segments
        if len(script.segments) < 2:
            return 0.5
        
        # Basic coherence check - in production would use NLP
        score = 0.85  # Base score
        
        # Check for smooth transitions
        for i in range(1, len(script.segments)):
            if script.segments[i].timing["start"] != script.segments[i-1].timing["end"]:
                score -= 0.05
        
        return max(0.0, min(1.0, score))
    
    async def _score_engagement(self, script: VideoScript) -> float:
        """Score potential engagement level."""
        score = 0.7  # Base score
        
        # Boost for strong hooks
        if script.hooks and len(script.hooks) > 0:
            score += 0.1
        
        # Check for varied content types
        content_types = set(s.type for s in script.segments)
        if len(content_types) > 2:
            score += 0.1
        
        # Check for emotional variety
        emotions = set(s.emotion for s in script.segments if s.emotion)
        if len(emotions) > 1:
            score += 0.1
        
        return min(1.0, score)
    
    async def _score_clarity(self, script: VideoScript) -> float:
        """Score script clarity and comprehension."""
        # Simple clarity metrics
        total_words = self._count_words(script)
        avg_words_per_segment = total_words / len(script.segments) if script.segments else 0
        
        # Ideal is 20-40 words per segment
        if 20 <= avg_words_per_segment <= 40:
            return 0.9
        elif 15 <= avg_words_per_segment <= 50:
            return 0.8
        else:
            return 0.7
    
    async def _score_pacing(self, script: VideoScript) -> float:
        """Score script pacing appropriateness."""
        # Check if duration matches target
        if not script.metadata.get("target_duration"):
            return 0.8
        
        target = script.metadata["target_duration"]
        actual = script.total_duration
        
        # Within 10% is excellent
        deviation = abs(actual - target) / target
        if deviation <= 0.1:
            return 0.95
        elif deviation <= 0.2:
            return 0.85
        elif deviation <= 0.3:
            return 0.75
        else:
            return 0.65
    
    async def _score_platform_fit(self, script: VideoScript) -> float:
        """Score how well script fits platform requirements."""
        platform_config = self.PLATFORM_ADAPTATIONS.get(script.platform)
        if not platform_config:
            return 0.7
        
        score = 0.8  # Base score
        
        # Check segment count
        optimal_segments = platform_config["optimal_segments"]
        segment_deviation = abs(len(script.segments) - optimal_segments) / optimal_segments
        score -= segment_deviation * 0.2
        
        # Check opening duration
        if script.segments and script.segments[0].duration <= platform_config["opening_duration"]:
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _count_words(self, script: VideoScript) -> int:
        """Count total words in script."""
        total = 0
        for segment in script.segments:
            if segment.type in ["narration", "dialogue"]:
                total += len(segment.content.split())
        return total
    
    def _calculate_dialogue_ratio(self, script: VideoScript) -> float:
        """Calculate ratio of dialogue to total content."""
        dialogue_segments = [s for s in script.segments if s.type == "dialogue"]
        if not script.segments:
            return 0.0
        return len(dialogue_segments) / len(script.segments)
    
    def _serialize_script(self, script: VideoScript) -> str:
        """Serialize script to JSON format."""
        return json.dumps({
            "title": script.title,
            "platform": script.platform,
            "style": script.style.value,
            "total_duration": script.total_duration,
            "segments": [
                {
                    "type": s.type,
                    "content": s.content,
                    "duration": s.duration,
                    "speaker": s.speaker,
                    "emotion": s.emotion,
                    "timing": s.timing,
                    "metadata": s.metadata
                }
                for s in script.segments
            ],
            "hooks": script.hooks,
            "ctas": script.ctas,
            "keywords": script.keywords,
            "metadata": script.metadata
        }, indent=2)
    
    # A2A Protocol Implementation
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming script writing request."""
        context = TaskContext(
            session_id=request.get("session_id", f"session_{int(time.time())}"),
            request_type="script_writing",
            parameters=request,
            metadata={"timestamp": datetime.now(timezone.utc).isoformat()}
        )
        
        result = await self._execute_agent_logic(context)
        
        return {
            "status": result.status.value,
            "confidence": result.confidence_score,
            "artifacts": [a.dict() for a in result.artifacts],
            "metadata": result.metadata
        }
