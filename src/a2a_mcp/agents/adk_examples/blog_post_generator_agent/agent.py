"""
ABOUTME: Blog Post Generator Agent using Google ADK with Pydantic models for long-form content creation
ABOUTME: Demonstrates comprehensive blog structure with SEO optimization and engagement strategies
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


# --- Define Blog Category Enum ---
class BlogCategory(str, Enum):
    HOW_TO = "how_to"
    TUTORIAL = "tutorial"
    CASE_STUDY = "case_study"
    INDUSTRY_ANALYSIS = "industry_analysis"
    OPINION = "opinion"
    NEWS = "news"
    REVIEW = "review"
    LISTICLE = "listicle"
    COMPARISON = "comparison"


# --- Define Content Tone Enum ---
class ContentTone(str, Enum):
    PROFESSIONAL = "professional"
    CONVERSATIONAL = "conversational"
    EDUCATIONAL = "educational"
    PERSUASIVE = "persuasive"
    INSPIRATIONAL = "inspirational"
    AUTHORITATIVE = "authoritative"


# --- Define SEO Difficulty Enum ---
class SEODifficulty(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# --- Define Blog Section Schema ---
class BlogSection(BaseModel):
    section_title: str = Field(description="Section heading (H2 or H3)")
    content: str = Field(description="Section content with key points")
    section_type: str = Field(description="Type of section (introduction, main_point, example, conclusion)")
    word_count: int = Field(description="Estimated word count for this section")
    key_takeaways: List[str] = Field(description="Main takeaways from this section", max_items=3)


# --- Define SEO Optimization Schema ---
class SEOOptimization(BaseModel):
    primary_keyword: str = Field(description="Main target keyword")
    secondary_keywords: List[str] = Field(description="Supporting keywords", max_items=8)
    meta_description: str = Field(
        description="SEO meta description",
        min_length=120,
        max_length=160
    )
    title_tag: str = Field(
        description="SEO-optimized title tag",
        min_length=30,
        max_length=60
    )
    keyword_density: float = Field(description="Target keyword density percentage", ge=0.5, le=3.0)
    internal_link_opportunities: List[str] = Field(
        description="Suggested internal linking opportunities",
        max_items=5
    )
    external_authority_links: List[str] = Field(
        description="Suggested authoritative external links",
        max_items=3
    )


# --- Define Content Engagement Schema ---
class ContentEngagement(BaseModel):
    hook_introduction: str = Field(description="Compelling opening hook")
    call_to_action: str = Field(description="Primary call-to-action")
    engagement_elements: List[str] = Field(
        description="Elements to increase engagement (questions, polls, etc.)",
        max_items=5
    )
    social_sharing_optimizations: List[str] = Field(
        description="Elements optimized for social sharing",
        max_items=3
    )
    reader_value_propositions: List[str] = Field(
        description="Clear value propositions for readers",
        max_items=3
    )


# --- Define Visual Content Schema ---
class VisualContentSuggestion(BaseModel):
    content_type: str = Field(description="Type of visual (infographic, chart, image, video)")
    description: str = Field(description="Description of visual content needed")
    placement: str = Field(description="Where in the blog post to place this visual")
    alt_text: str = Field(description="SEO-optimized alt text for images")
    purpose: str = Field(description="Purpose of this visual element")


# --- Define Blog Post Schema ---
class BlogPost(BaseModel):
    creation_date: str = Field(description="Blog post creation date", default_factory=lambda: datetime.now().isoformat())
    title: str = Field(
        description="Blog post title - compelling and SEO-optimized",
        min_length=30,
        max_length=100
    )
    subtitle: Optional[str] = Field(
        description="Optional subtitle for additional context",
        max_length=150
    )
    category: BlogCategory = Field(description="Blog post category")
    content_tone: ContentTone = Field(description="Overall tone and style")
    target_audience: str = Field(description="Primary target audience for this post")
    estimated_word_count: int = Field(
        description="Total estimated word count",
        ge=500,
        le=5000
    )
    estimated_read_time: int = Field(description="Estimated reading time in minutes")
    introduction: str = Field(
        description="Compelling introduction paragraph",
        min_length=100,
        max_length=300
    )
    blog_sections: List[BlogSection] = Field(
        description="Main content sections",
        min_items=3,
        max_items=10
    )
    conclusion: str = Field(
        description="Strong conclusion that ties everything together",
        min_length=100,
        max_length=300
    )
    seo_optimization: SEOOptimization = Field(description="SEO strategy and optimization")
    content_engagement: ContentEngagement = Field(description="Engagement optimization strategy")
    visual_content: List[VisualContentSuggestion] = Field(
        description="Visual content recommendations",
        max_items=7
    )
    key_insights: List[str] = Field(
        description="Main insights readers will gain",
        max_items=5
    )
    actionable_takeaways: List[str] = Field(
        description="Specific actions readers can take",
        max_items=7
    )
    related_topics: List[str] = Field(
        description="Related topics for future content",
        max_items=5
    )
    content_distribution_strategy: List[str] = Field(
        description="How to distribute and promote this content",
        max_items=5
    )
    conversion_opportunities: List[str] = Field(
        description="Opportunities to convert readers to leads/customers",
        max_items=3
    )


# --- Create Blog Post Generator Agent ---
root_agent = LlmAgent(
    name="blog_post_generator_agent",
    model=os.getenv("GEMINI_MODEL"),
    instruction="""
        You are a Strategic Long-Form Content Creator powered by Google ADK with session memory.
        Your task is to create comprehensive, engaging blog posts that drive traffic, engagement, and conversions.

        CORE RESPONSIBILITIES:
        1. Develop compelling blog post structures with clear value propositions
        2. Create SEO-optimized content that ranks well in search engines
        3. Design engagement strategies that keep readers on page and drive actions
        4. Generate actionable, practical content that provides real value
        5. Optimize for both human readers and search algorithms
        6. Create content that supports broader content marketing strategy
        7. Integrate lead generation and conversion opportunities

        SESSION AWARENESS:
        - Check session state for content_strategy, brand_voice, and blog_performance
        - Reference successful blog post patterns and topics
        - Use established SEO keywords and content themes
        - Consider content calendar and campaign integration
        - Maintain brand consistency and thought leadership positioning

        BLOG STRUCTURE METHODOLOGY:
        1. **Hook Introduction**: Compelling opening that addresses reader pain point
        2. **Value Proposition**: Clear benefit statement for reading the post
        3. **Structured Content**: Logical flow with actionable insights
        4. **Supporting Evidence**: Data, examples, case studies for credibility
        5. **Actionable Takeaways**: Specific steps readers can implement
        6. **Strong Conclusion**: Reinforcement of value and next steps

        SEO OPTIMIZATION STRATEGY:
        - **Keyword Research**: Primary and secondary keyword integration
        - **Title Optimization**: Compelling titles under 60 characters
        - **Meta Descriptions**: Compelling descriptions 120-160 characters
        - **Header Structure**: Proper H1/H2/H3 hierarchy for readability
        - **Internal Linking**: Strategic links to related content
        - **External Authority**: Links to credible external sources

        CONTENT ENGAGEMENT TACTICS:
        - **Scannable Format**: Headers, bullet points, short paragraphs
        - **Interactive Elements**: Questions, challenges, actionable steps
        - **Visual Integration**: Strategic placement of supporting visuals
        - **Social Sharing**: Elements optimized for social media sharing
        - **Reader Journey**: Logical flow that maintains interest

        BLOG CATEGORY OPTIMIZATION:

        **How-To/Tutorial**:
        - Step-by-step structure with clear progression
        - Actionable instructions with expected outcomes
        - Troubleshooting and common mistakes sections
        - Visual aids for complex processes

        **Case Study**:
        - Problem/solution/results structure
        - Specific metrics and outcomes
        - Lessons learned and applications
        - Credible source attribution

        **Industry Analysis**:
        - Data-driven insights and trends
        - Expert perspectives and predictions
        - Implications for target audience
        - Strategic recommendations

        **Listicle**:
        - Clear numbering with valuable points
        - Consistent structure across items
        - Actionable insights for each point
        - Compelling introduction and conclusion

        CONVERSION OPTIMIZATION:
        - **Lead Magnets**: Content upgrades and resources
        - **Call-to-Actions**: Strategic placement throughout content
        - **Value Demonstration**: Showcase expertise and results
        - **Trust Building**: Social proof and credibility indicators

        CONTENT DISTRIBUTION INTEGRATION:
        - **Social Media**: Adaptable content for platform sharing
        - **Email Marketing**: Newsletter integration opportunities
        - **LinkedIn Articles**: Professional platform adaptation
        - **Video Content**: Script and talking points extraction

        MEMORY INTEGRATION:
        - Track successful content topics and formats
        - Learn from engagement patterns and reader feedback
        - Maintain content theme consistency
        - Optimize based on performance metrics
        - Build comprehensive content intelligence database

        OUTPUT REQUIREMENTS:
        Your response MUST be valid JSON matching the BlogPost schema.
        Provide comprehensive structure with actionable content sections.
        Include SEO optimization and engagement strategies.
        Focus on valuable, practical content that drives results.
        Do not include explanations outside the JSON structure.
    """,
    description="Comprehensive blog post generation with SEO optimization and engagement strategies",
    output_schema=BlogPost,
    output_key="blog_post",
)