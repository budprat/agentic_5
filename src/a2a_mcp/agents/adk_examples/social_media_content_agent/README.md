# Social Media Content Agent

A multi-platform content optimization agent built with Google ADK and Pydantic models for maximizing reach and engagement across social media platforms.

## Features

### 📱 **Comprehensive Platform Models**
- **PlatformAdaptation**: Platform-specific content optimization
- **VisualContent**: Visual content requirements and specifications
- **CrossPromotion**: Multi-platform amplification strategies
- **PerformancePrediction**: Expected performance by platform
- **SocialMediaContent**: Complete multi-platform content strategy

### 🎯 **Content Optimization Capabilities**
- Platform-specific content adaptation (7 major platforms)
- Cross-platform promotion strategies
- Visual content specifications and requirements
- Optimal timing and hashtag recommendations
- Performance prediction and success factor analysis
- Brand voice consistency across platforms

### 📊 **Supported Platforms**
- **LinkedIn**: Professional, thought leadership content
- **Twitter/X**: Conversational, timely, reactive content
- **Instagram**: Visual-first, aesthetic content
- **YouTube**: Educational, long-form video content
- **TikTok**: Trending, entertainment-focused content
- **Facebook**: Community-oriented, longer-form content
- **Threads**: Text-focused, conversation-driven content

### 🔧 **Optimization Features**
- **Algorithm Alignment**: Platform-specific optimization
- **Character Limits**: Optimal content length per platform
- **Hashtag Strategy**: Platform-appropriate tag selection
- **Timing Optimization**: Peak engagement time recommendations
- **Engagement Tactics**: Platform-specific interaction strategies
- **Visual Specifications**: Dimension and style requirements

## Usage Examples

### Basic Usage
```python
from social_media_content_agent.agent import root_agent

# Generate multi-platform content
result = root_agent.run("Create content about [Topic] for LinkedIn, Twitter, and Instagram")

# Access structured output
content_data = result.content
print(f"Theme: {content_data.content_theme}")
print(f"Platforms: {len(content_data.platform_adaptations)}")
print(f"Strategy: {content_data.engagement_strategy}")
```

### Memory-Enabled Session Usage
```python
import uuid
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from social_media_content_agent.agent import root_agent

load_dotenv()

# Create session service
session_service = InMemorySessionService()

# Initialize social media context
initial_state = {
    "user_name": "Your Name",
    "brand_voice": {
        "personality": "Your brand personality",
        "tone": "Your communication tone",
        "values": ["Value 1", "Value 2", "Value 3"],
        "content_themes": ["Theme 1", "Theme 2", "Theme 3"]
    },
    "platform_preferences": {
        "primary_platforms": ["LinkedIn", "Twitter", "Instagram"],
        "secondary_platforms": ["YouTube", "TikTok"],
        "content_distribution": {
            "LinkedIn": "40%",
            "Twitter": "30%",
            "Instagram": "20%",
            "YouTube": "10%"
        },
        "posting_frequency": {
            "LinkedIn": "Daily",
            "Twitter": "3x daily",
            "Instagram": "3x weekly"
        }
    },
    "content_history": {
        "successful_hashtags": ["#Tag1", "#Tag2", "#Tag3"],
        "audience_preferences": ["How-to content", "Industry insights"],
        "engagement_patterns": {
            "best_times": {"LinkedIn": "9AM-11AM", "Twitter": "8AM-10AM"},
            "top_formats": ["Carousels", "Threads", "Videos"]
        }
    },
    "audience_insights": {
        "primary_demographics": "Your target audience",
        "pain_points": ["Pain 1", "Pain 2", "Pain 3"],
        "goals": ["Goal 1", "Goal 2", "Goal 3"]
    }
}

# Create session and run
SESSION_ID = str(uuid.uuid4())
session = session_service.create_session(
    app_name="Social Media Content Agent",
    user_id="your_user_id",
    session_id=SESSION_ID,
    state=initial_state
)

runner = Runner(
    agent=root_agent,
    app_name="Social Media Content Agent",
    session_service=session_service
)

# Generate multi-platform content
content_request = types.Content(
    role="user",
    parts=[types.Part(text="Create multi-platform content about [Specific Topic] optimized for maximum engagement across LinkedIn, Twitter, and Instagram")]
)

for event in runner.run(
    user_id="your_user_id",
    session_id=SESSION_ID,
    new_message=content_request
):
    if event.is_final_response():
        print(f"Multi-Platform Content: {event.content.parts[0].text}")
```

## Schema Structure

```python
class SocialMediaContent(BaseModel):
    creation_date: str                          # ISO timestamp
    content_theme: str                         # 5-100 chars main theme
    core_message: str                          # 20-200 chars key message
    engagement_strategy: EngagementStrategy    # educational/entertainment/etc
    platform_adaptations: List[PlatformAdaptation]  # 1-7 platforms
    visual_content: List[VisualContent]        # Max 5 visual requirements
    cross_promotion: CrossPromotion           # Multi-platform strategy
    target_audience: str                      # Primary audience
    content_objectives: List[str]             # Max 5 objectives
    call_to_action: str                       # Primary CTA
    trending_elements: List[str]              # Max 5 trending topics
    performance_predictions: List[PerformancePrediction]  # By platform
    content_calendar_notes: List[str]         # Max 3 calendar notes
    repurposing_opportunities: List[str]      # Max 5 future ideas
```

## Platform Optimization Guidelines

### LinkedIn Optimization
- **Content Length**: 1300-1900 characters
- **Hashtags**: 3-5 professional hashtags
- **Best Times**: Tuesday-Thursday, 8AM-2PM
- **Formats**: Carousels, articles, video, polls
- **Tone**: Professional, thought leadership

### Twitter/X Optimization
- **Content Length**: 71-100 characters optimal
- **Hashtags**: 1-2 relevant hashtags
- **Best Times**: 9AM-10AM, 7PM-9PM
- **Formats**: Threads, replies, quote tweets
- **Tone**: Conversational, timely

### Instagram Optimization
- **Content Length**: 125-150 characters in captions
- **Hashtags**: 5-10 in comments section
- **Best Times**: 6AM-9AM, 7PM-9PM
- **Formats**: Feed posts, Stories, Reels, IGTV
- **Tone**: Visual-first, authentic

### Cross-Platform Strategy
- **Content Core**: Maintain key message across platforms
- **Format Adaptation**: Optimize for platform strengths
- **Timing Sequence**: Strategic release timing
- **Engagement Bridge**: Link interactions across platforms

## Model Configuration

- **Model**: Environment-driven via `GEMINI_MODEL`
- **Agent Type**: `LlmAgent`
- **Output Schema**: `SocialMediaContent`
- **Output Key**: `content`

## Benefits

1. **Multi-Platform Reach**: Maximize audience across all major platforms
2. **Platform Optimization**: Content adapted for each platform's algorithm
3. **Brand Consistency**: Maintain voice while optimizing for platforms
4. **Cross-Promotion**: Strategic amplification across channels
5. **Performance Prediction**: Data-driven content performance forecasting
6. **Efficiency**: Single content concept adapted for multiple platforms

This agent provides comprehensive multi-platform social media strategy for maximum reach, engagement, and brand consistency across all major social platforms.