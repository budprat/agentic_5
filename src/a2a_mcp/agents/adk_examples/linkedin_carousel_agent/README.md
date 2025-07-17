# LinkedIn Carousel Agent

A specialized carousel generation agent built with Google ADK and Pydantic models for creating high-engagement LinkedIn visual content.

## Features

### 🎨 **Comprehensive Design Models**
- **CarouselSlide**: Individual slide structure with visual elements
- **DesignTheme**: Professional design themes (professional, modern, minimalist, bold, creative, corporate)
- **ContentType**: Content categories (educational, tips, process, statistics, story, comparison)
- **BrandGuidelines**: Consistent brand application across carousels

### 🎠 **Carousel Generation Capabilities**
- Multi-slide narrative flow optimization (3-10 slides)
- LinkedIn algorithm signal optimization
- Brand-consistent visual design
- Engagement hook generation
- Strategic hashtag recommendations
- Mobile-optimized readability

### 🎯 **Content Types Supported**
- **Educational**: How-to tutorials and frameworks
- **Tips**: Quick wins and actionable advice
- **Process**: Step-by-step workflows
- **Statistics**: Data-driven insights presentation
- **Story**: Personal experiences and case studies
- **Comparison**: Before/after and pros/cons analysis

### 🔧 **Technical Features**
- **Visual Element Positioning**: Strategic placement of icons, charts, images
- **Color Scheme Management**: Brand-consistent color application
- **Slide Flow Optimization**: Logical narrative progression
- **Mobile-First Design**: Optimized for LinkedIn mobile viewing
- **Performance Tracking**: Session-based optimization learning

## Usage Examples

### Basic Usage
```python
from linkedin_carousel_agent.agent import root_agent

# Generate a carousel
result = root_agent.run("Create a carousel about LinkedIn growth strategies")

# Access structured output
carousel_data = result.carousel
print(f"Title: {carousel_data.title}")
print(f"Slides: {len(carousel_data.slides)}")
print(f"Theme: {carousel_data.design_theme}")
```

### Memory-Enabled Session Usage
```python
import uuid
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from linkedin_carousel_agent.agent import root_agent

load_dotenv()

# Create session service
session_service = InMemorySessionService()

# Initialize brand context
initial_state = {
    "user_name": "Your Name",
    "brand_preferences": {
        "primary_colors": ["#0077B5", "#00A0DC", "#313335"],
        "secondary_colors": ["#F3F6F8", "#E1E9EE", "#8B9DC3"],
        "font_family": "Inter, Arial, sans-serif",
        "design_style": "professional modern",
        "company": "Your Company",
        "industry": "Your Industry"
    },
    "carousel_context": {
        "recent_topics": [],
        "performance_history": [],
        "successful_formats": [],
        "audience_preferences": ["your", "target", "audience"],
        "content_goals": ["thought leadership", "engagement", "lead generation"]
    }
}

# Create session and run
SESSION_ID = str(uuid.uuid4())
session = session_service.create_session(
    app_name="LinkedIn Carousel Agent",
    user_id="your_user_id",
    session_id=SESSION_ID,
    state=initial_state
)

runner = Runner(
    agent=root_agent,
    app_name="LinkedIn Carousel Agent",
    session_service=session_service
)

# Generate branded carousel
carousel_request = types.Content(
    role="user",
    parts=[types.Part(text="Create a carousel about LinkedIn algorithm optimization with 7 actionable tips")]
)

for event in runner.run(
    user_id="your_user_id",
    session_id=SESSION_ID,
    new_message=carousel_request
):
    if event.is_final_response():
        print(f"Generated Carousel: {event.content.parts[0].text}")
```

## Schema Structure

```python
class LinkedInCarousel(BaseModel):
    title: str                              # 10-100 chars
    description: str                        # 50-300 chars for LinkedIn post
    content_type: ContentType               # educational/tips/process/etc
    design_theme: DesignTheme              # professional/modern/minimalist/etc
    slides: List[CarouselSlide]            # 3-10 slides
    hashtags: List[str]                    # Max 10 relevant hashtags
    call_to_action: str                    # Clear CTA
    target_audience: str                   # Primary audience
    engagement_hooks: List[str]            # Max 5 engagement elements
    brand_guidelines: Optional[BrandGuidelines]  # Brand consistency
```

## LinkedIn Algorithm Optimization

### Engagement Signals
- **Dwell Time**: Scannable slides (3-5 seconds each)
- **Comments**: Thought-provoking questions and discussion starters
- **Shares**: Quotable insights and actionable takeaways
- **Early Engagement**: Hook optimization for first-hour performance

### Design Best Practices
- **Mobile-First**: Optimized for mobile LinkedIn viewing
- **High Contrast**: Ensures readability across devices
- **Visual Hierarchy**: Clear information flow and emphasis
- **Brand Consistency**: Maintains professional brand image

## Model Configuration

- **Model**: Environment-driven via `GEMINI_MODEL`
- **Agent Type**: `LlmAgent`
- **Output Schema**: `LinkedInCarousel`
- **Output Key**: `carousel`

## Benefits

1. **Algorithm Optimization**: Built for LinkedIn's engagement signals
2. **Brand Consistency**: Maintains visual identity across content
3. **Performance Learning**: Session-based optimization improvement
4. **Mobile-Optimized**: Designed for mobile-first consumption
5. **Engagement Focus**: Every element optimized for interaction
6. **Scalable Creation**: Rapid carousel generation with quality control

This agent is specifically designed for LinkedIn content domination through high-engagement visual storytelling.