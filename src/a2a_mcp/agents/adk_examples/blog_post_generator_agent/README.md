# Blog Post Generator Agent

A comprehensive long-form content creation agent built with Google ADK and Pydantic models for SEO-optimized blog posts that drive traffic, engagement, and conversions.

## Features

### 📝 **Comprehensive Content Models**
- **BlogPost**: Complete blog structure with SEO and engagement optimization
- **BlogSection**: Individual content sections with structured information
- **SEOOptimization**: Keyword strategy, meta descriptions, and link opportunities
- **ContentEngagement**: Hooks, CTAs, and social sharing optimization
- **VisualContentSuggestion**: Strategic visual content placement and optimization

### 🎯 **Content Creation Capabilities**
- Long-form content structure (500-5000 words)
- SEO optimization with keyword integration
- Engagement strategy development
- Visual content planning and placement
- Conversion opportunity identification
- Content distribution strategy

### 📊 **Blog Categories Supported**
- **How-To**: Step-by-step instructional content
- **Tutorial**: Educational guides and walkthroughs
- **Case Study**: Real-world examples and results
- **Industry Analysis**: Market insights and trends
- **Opinion**: Thought leadership and perspectives
- **Listicle**: Numbered lists with valuable insights
- **Comparison**: Product/service/strategy comparisons

### 🔧 **Optimization Features**
- **SEO Strategy**: Primary/secondary keyword optimization
- **Meta Optimization**: Title tags and descriptions
- **Content Structure**: Proper heading hierarchy and flow
- **Engagement Elements**: Interactive components and CTAs
- **Visual Integration**: Strategic image and media placement
- **Conversion Tracking**: Lead generation and sales opportunities

## Usage Examples

### Basic Usage
```python
from blog_post_generator_agent.agent import root_agent

# Generate a blog post
result = root_agent.run("Create a comprehensive blog post about [Topic] for [Target Audience]")

# Access structured output
blog_data = result.blog_post
print(f"Title: {blog_data.title}")
print(f"Word Count: {blog_data.estimated_word_count}")
print(f"Sections: {len(blog_data.blog_sections)}")
```

### Memory-Enabled Session Usage
```python
import uuid
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from blog_post_generator_agent.agent import root_agent

load_dotenv()

# Create session service
session_service = InMemorySessionService()

# Initialize content strategy context
initial_state = {
    "user_name": "Your Name",
    "content_strategy": {
        "primary_topics": ["Topic 1", "Topic 2", "Topic 3"],
        "content_pillars": ["Education", "Case studies", "How-to guides"],
        "target_keywords": ["keyword1", "keyword2", "keyword3"],
        "content_goals": ["Thought leadership", "Lead generation", "SEO ranking"],
        "publishing_frequency": "2x per week"
    },
    "brand_voice": {
        "tone": "Professional but approachable",
        "personality": "Expert teacher",
        "writing_style": "Clear, direct, evidence-based",
        "expertise_areas": ["Area 1", "Area 2", "Area 3"],
        "unique_angles": ["Technical insights", "Data-driven approach"]
    },
    "blog_performance": {
        "top_performing_topics": ["Topic A", "Topic B", "Topic C"],
        "successful_formats": ["Step-by-step guides", "Case studies"],
        "engagement_drivers": ["Actionable tips", "Real examples"],
        "average_metrics": {"word_count": 2500, "read_time": 12}
    },
    "audience_insights": {
        "primary_readers": "Your target audience",
        "experience_level": "Intermediate to advanced",
        "main_challenges": ["Challenge 1", "Challenge 2"],
        "preferred_content": ["In-depth tutorials", "Case studies"],
        "reading_behavior": ["Mobile-first", "Scannable content"]
    }
}

# Create session and run
SESSION_ID = str(uuid.uuid4())
session = session_service.create_session(
    app_name="Blog Post Generator Agent",
    user_id="your_user_id",
    session_id=SESSION_ID,
    state=initial_state
)

runner = Runner(
    agent=root_agent,
    app_name="Blog Post Generator Agent",
    session_service=session_service
)

# Generate comprehensive blog post
blog_request = types.Content(
    role="user",
    parts=[types.Part(text="Create a comprehensive blog post about [Specific Topic] targeting [Specific Audience] with SEO optimization for [Target Keywords]")]
)

for event in runner.run(
    user_id="your_user_id",
    session_id=SESSION_ID,
    new_message=blog_request
):
    if event.is_final_response():
        print(f"Blog Post: {event.content.parts[0].text}")
```

## Schema Structure

```python
class BlogPost(BaseModel):
    creation_date: str                          # ISO timestamp
    title: str                                 # 30-100 chars SEO-optimized
    subtitle: Optional[str]                    # Max 150 chars optional
    category: BlogCategory                     # how_to/tutorial/case_study/etc
    content_tone: ContentTone                  # professional/conversational/etc
    target_audience: str                       # Primary audience description
    estimated_word_count: int                  # 500-5000 words
    estimated_read_time: int                   # Reading time in minutes
    introduction: str                          # 100-300 chars compelling intro
    blog_sections: List[BlogSection]           # 3-10 main content sections
    conclusion: str                            # 100-300 chars strong conclusion
    seo_optimization: SEOOptimization          # Complete SEO strategy
    content_engagement: ContentEngagement      # Engagement optimization
    visual_content: List[VisualContentSuggestion]  # Max 7 visual elements
    key_insights: List[str]                    # Max 5 main insights
    actionable_takeaways: List[str]            # Max 7 specific actions
    related_topics: List[str]                  # Max 5 future content ideas
    content_distribution_strategy: List[str]   # Max 5 promotion tactics
    conversion_opportunities: List[str]        # Max 3 conversion points
```

## SEO Optimization Strategy

### Keyword Integration
- **Primary Keyword**: Main target keyword (1-2% density)
- **Secondary Keywords**: Supporting keywords throughout content
- **Long-tail Keywords**: Specific phrases for niche targeting
- **LSI Keywords**: Related terms for semantic SEO

### Technical SEO
- **Title Tag**: Under 60 characters with primary keyword
- **Meta Description**: 120-160 characters with compelling copy
- **Header Structure**: Proper H1/H2/H3 hierarchy
- **Internal Links**: Strategic links to related content
- **External Links**: Authority links for credibility

### Content Structure
- **Scannable Format**: Headers, bullets, short paragraphs
- **Featured Snippets**: Structured content for Google snippets
- **Rich Media**: Images, videos, infographics for engagement
- **Mobile Optimization**: Mobile-first content design

## Content Engagement Strategy

### Reader Experience
- **Hook Introduction**: Compelling opening that addresses pain points
- **Value Proposition**: Clear benefits for reading the content
- **Logical Flow**: Structured progression through topics
- **Actionable Content**: Specific steps readers can implement

### Interaction Elements
- **Questions**: Thought-provoking questions throughout
- **CTAs**: Strategic calls-to-action for engagement
- **Social Sharing**: Optimized for platform sharing
- **Lead Magnets**: Content upgrades and resources

## Model Configuration

- **Model**: Environment-driven via `GEMINI_MODEL`
- **Agent Type**: `LlmAgent`
- **Output Schema**: `BlogPost`
- **Output Key**: `blog_post`

## Benefits

1. **SEO Optimization**: Comprehensive keyword strategy and technical SEO
2. **Engagement Focus**: Elements designed to keep readers engaged
3. **Conversion Integration**: Strategic lead generation opportunities
4. **Content Strategy**: Aligned with broader content marketing goals
5. **Distribution Ready**: Optimized for multiple promotion channels
6. **Performance Tracking**: Built-in metrics and success indicators

This agent provides comprehensive blog post creation with SEO optimization, engagement strategies, and conversion opportunities for maximum content marketing impact.