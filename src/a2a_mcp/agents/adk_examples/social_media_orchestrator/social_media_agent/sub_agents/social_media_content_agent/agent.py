"""
ABOUTME: Social Media Content Agent using Google ADK with Pydantic models for multi-platform content distribution
ABOUTME: Demonstrates cross-platform content optimization with platform-specific adaptations and engagement strategies
"""

import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime

# Load environment variables
load_dotenv()


# --- Define Social Platform Enum ---
class SocialPlatform(str, Enum):
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    THREADS = "threads"


# --- Define Content Format Enum ---
class ContentFormat(str, Enum):
    TEXT_POST = "text_post"
    IMAGE_POST = "image_post"
    VIDEO_POST = "video_post"
    CAROUSEL = "carousel"
    STORY = "story"
    THREAD = "thread"
    REEL = "reel"
    LIVE = "live"


# --- Define Engagement Strategy Enum ---
class EngagementStrategy(str, Enum):
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    INSPIRATIONAL = "inspirational"
    PROMOTIONAL = "promotional"
    COMMUNITY = "community"
    TRENDING = "trending"


# --- Define Platform Adaptation Schema ---
class PlatformAdaptation(BaseModel):
    platform: SocialPlatform = Field(description="Target social media platform")
    content: str = Field(description="Platform-optimized content")
    character_limit: Optional[int] = Field(description="Character limit for this platform")
    hashtags: List[str] = Field(description="Platform-specific hashtags", max_items=15)
    mentions: List[str] = Field(description="Relevant mentions for this platform", max_items=5)
    optimal_posting_time: str = Field(description="Best time to post on this platform")
    content_format: ContentFormat = Field(description="Recommended content format")
    engagement_tactics: List[str] = Field(description="Platform-specific engagement tactics", max_items=5)


# --- Define Visual Content Schema ---
class VisualContent(BaseModel):
    content_type: str = Field(description="Type of visual content (image, video, graphic)")
    description: str = Field(description="Description of visual content needed")
    dimensions: str = Field(description="Optimal dimensions for platform")
    style_guidelines: List[str] = Field(description="Visual style recommendations", max_items=5)
    text_overlay: Optional[str] = Field(description="Text to overlay on visual content")


# --- Define Cross-Promotion Schema ---
class CrossPromotion(BaseModel):
    primary_platform: SocialPlatform = Field(description="Main platform for content launch")
    secondary_platforms: List[SocialPlatform] = Field(description="Platforms for content amplification")
    adaptation_strategy: str = Field(description="How to adapt content across platforms")
    timing_sequence: List[str] = Field(description="Order and timing for cross-promotion")
    engagement_linking: str = Field(description="How to link engagement across platforms")


# --- Define Performance Prediction Schema ---
class PerformancePrediction(BaseModel):
    platform: SocialPlatform = Field(description="Platform for prediction")
    estimated_reach: str = Field(description="Predicted reach range")
    estimated_engagement: str = Field(description="Predicted engagement rate")
    best_metrics: List[str] = Field(description="Metrics likely to perform best", max_items=3)
    success_factors: List[str] = Field(description="Factors that will drive success", max_items=5)


# --- Define Social Media Content Schema ---
class SocialMediaContent(BaseModel):
    creation_date: str = Field(description="Content creation date", default_factory=lambda: datetime.now().isoformat())
    content_theme: str = Field(
        description="Main theme or topic of the content",
        min_length=5,
        max_length=100
    )
    core_message: str = Field(
        description="Central message or key takeaway",
        min_length=20,
        max_length=200
    )
    engagement_strategy: EngagementStrategy = Field(description="Primary engagement approach")
    platform_adaptations: List[PlatformAdaptation] = Field(
        description="Content adapted for each platform",
        min_items=1,
        max_items=7
    )
    visual_content: List[VisualContent] = Field(
        description="Visual content requirements",
        max_items=5
    )
    cross_promotion: CrossPromotion = Field(description="Cross-platform promotion strategy")
    target_audience: str = Field(description="Primary target audience for this content")
    content_objectives: List[str] = Field(
        description="Specific objectives for this content",
        max_items=5
    )
    call_to_action: str = Field(description="Primary call-to-action across platforms")
    trending_elements: List[str] = Field(
        description="Trending topics or elements to incorporate",
        max_items=5
    )
    performance_predictions: List[PerformancePrediction] = Field(
        description="Performance predictions by platform",
        max_items=7
    )
    content_calendar_notes: List[str] = Field(
        description="Notes for content calendar integration",
        max_items=3
    )
    repurposing_opportunities: List[str] = Field(
        description="Future content repurposing ideas",
        max_items=5
    )


# --- Create Social Media Content Agent ---
social_media_content_agent = LlmAgent(
    name="social_media_content_agent",
    model=os.getenv("GEMINI_MODEL"),
    instruction="""
        You are a Multi-Platform Social Media Content Strategist powered by Google ADK with session memory.
        Your task is to create and optimize content for maximum engagement across multiple social media platforms.

        CORE RESPONSIBILITIES:
        1. Develop core content themes that work across multiple platforms
        2. Adapt content for platform-specific audiences, formats, and algorithms
        3. Create cross-promotion strategies for amplified reach
        4. Optimize timing, hashtags, and engagement tactics per platform
        5. Predict performance and identify success factors
        6. Generate visual content requirements and specifications
        7. Integrate content into broader social media strategy

        SESSION AWARENESS:
        - Check session state for brand_voice, platform_preferences, and content_history
        - Reference successful content patterns and performance metrics
        - Use established hashtag strategies and audience insights
        - Consider content calendar and campaign coordination
        - Maintain brand consistency across platform adaptations

        PLATFORM OPTIMIZATION STRATEGIES:

        **LinkedIn**:
        - Professional tone, thought leadership focus
        - 1300-1900 character sweet spot
        - Industry hashtags + broad reach tags
        - Business hours posting (Tue-Thu 8AM-2PM)
        - Engagement: Questions, polls, professional insights

        **Twitter/X**:
        - Conversational, timely, reactive content
        - 71-100 characters for optimal engagement
        - 2-3 hashtags maximum
        - Peak times: 9AM-10AM, 7PM-9PM
        - Engagement: Threads, replies, trending topics

        **Instagram**:
        - Visual-first, aesthetic consistency
        - 125-150 characters in captions
        - 5-10 hashtags in comments
        - Peak times: 6AM-9AM, 7PM-9PM
        - Engagement: Stories, Reels, user-generated content

        **YouTube**:
        - Educational, entertaining long-form content
        - SEO-optimized titles and descriptions
        - Custom thumbnails, end screens
        - Consistent upload schedule
        - Engagement: Comments, community posts, premieres

        **TikTok**:
        - Trending audio, quick hooks, entertainment
        - 100-150 characters in descriptions
        - Trending hashtags + niche tags
        - Peak times: 6AM-10AM, 7PM-9PM
        - Engagement: Duets, challenges, trending formats

        **Facebook**:
        - Community-focused, longer-form content
        - 40-80 characters for link posts
        - Minimal hashtag usage
        - Peak times: 1PM-3PM, 7PM-9PM
        - Engagement: Groups, events, video content

        **Threads**:
        - Text-focused, conversation-driven
        - Similar to Twitter but more community-oriented
        - Minimal hashtags, authentic voice
        - Real-time engagement and responsiveness

        CONTENT ADAPTATION METHODOLOGY:
        1. **Core Message Preservation**: Maintain key insights across platforms
        2. **Format Optimization**: Adapt to platform content types
        3. **Audience Adjustment**: Tailor language and examples
        4. **Algorithm Alignment**: Optimize for platform discovery
        5. **Engagement Customization**: Platform-specific interaction strategies

        CROSS-PROMOTION STRATEGY:
        - Primary platform launch with full content
        - Secondary platform teasers driving traffic
        - Platform-specific adaptations maintaining brand voice
        - Strategic timing for maximum cumulative reach
        - Engagement bridging between platforms

        VISUAL CONTENT OPTIMIZATION:
        - Platform-specific dimension requirements
        - Brand consistency with platform adaptations
        - Mobile-first design principles
        - Accessibility considerations
        - Performance-driving visual elements

        ENGAGEMENT MAXIMIZATION:
        - Platform-specific best practices
        - Trending element integration
        - Community building tactics
        - Interactive content formats
        - Response and follow-up strategies

        PERFORMANCE PREDICTION:
        - Historical data pattern analysis
        - Platform algorithm considerations
        - Audience behavior insights
        - Trending topic leverage
        - Competitive landscape awareness

        MEMORY INTEGRATION:
        - Track content performance across platforms
        - Learn from successful adaptation strategies
        - Maintain brand voice consistency
        - Optimize timing and format selections
        - Build comprehensive content intelligence

        OUTPUT REQUIREMENTS:
        Your response MUST be valid JSON matching the SocialMediaContent schema.
        Provide platform-specific adaptations with optimization details.
        Include cross-promotion strategy and performance predictions.
        Focus on actionable content and engagement strategies.
        Do not include explanations outside the JSON structure.
    """,
    description="Multi-platform social media content optimization with cross-promotion and engagement strategies",
    output_schema=SocialMediaContent,
    output_key="content",
)
