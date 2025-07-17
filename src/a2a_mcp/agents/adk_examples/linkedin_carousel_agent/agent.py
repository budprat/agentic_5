"""
ABOUTME: LinkedIn Carousel Agent using Google ADK with Pydantic models for visual content generation
ABOUTME: Demonstrates structured carousel creation with brand consistency and engagement optimization
"""

import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

# Load environment variables
load_dotenv()


# --- Define Design Theme Enum ---
class DesignTheme(str, Enum):
    PROFESSIONAL = "professional"
    MODERN = "modern"
    MINIMALIST = "minimalist"
    BOLD = "bold"


# --- Define Content Type Enum ---
class ContentType(str, Enum):
    EDUCATIONAL = "educational"
    TIPS = "tips"
    PROCESS = "process"
    STATISTICS = "statistics"


# --- Define Slide Type Enum ---
class SlideType(str, Enum):
    TITLE = "title"
    CONTENT = "content"
    LIST = "list"
    QUOTE = "quote"
    STATISTIC = "statistic"
    CTA = "call_to_action"


# --- Define Visual Element Schema ---
class VisualElement(BaseModel):
    element_type: str = Field(description="Type of visual element (icon, chart, image, etc.)")
    description: str = Field(description="Description of the visual element")
    position: str = Field(description="Position on slide (top, center, bottom, left, right)")
    size: str = Field(description="Size of element (small, medium, large)")


# --- Define Carousel Slide Schema ---
class CarouselSlide(BaseModel):
    slide_number: int = Field(description="Slide number in sequence")
    slide_type: SlideType = Field(description="Type of slide content")
    title: str = Field(
        description="Slide title - concise and impactful",
        max_length=80
    )
    content: str = Field(
        description="Main slide content - bullet points or key message",
        max_length=300
    )
    visual_elements: List[VisualElement] = Field(
        default=[],
        description="Visual elements to include on this slide"
    )
    background_color: str = Field(
        default="#FFFFFF",
        description="Hex color code for slide background"
    )
    text_color: str = Field(
        default="#000000", 
        description="Hex color code for text"
    )


# --- Define Brand Guidelines Schema ---
class BrandGuidelines(BaseModel):
    primary_colors: List[str] = Field(description="Primary brand colors (hex codes)")
    secondary_colors: List[str] = Field(description="Secondary brand colors (hex codes)")
    font_family: str = Field(description="Primary font family")
    logo_position: str = Field(description="Logo placement on slides")


# --- Define LinkedIn Carousel Schema ---
class LinkedInCarousel(BaseModel):
    title: str = Field(
        description="Carousel title - engaging and descriptive",
        min_length=10,
        max_length=100
    )
    description: str = Field(
        description="Carousel description for LinkedIn post",
        min_length=50,
        max_length=300
    )
    content_type: ContentType = Field(description="Type of content being presented")
    design_theme: DesignTheme = Field(description="Visual design theme")
    slides: List[CarouselSlide] = Field(
        description="List of slides in the carousel",
        min_items=3,
        max_items=10
    )
    hashtags: List[str] = Field(
        description="Relevant hashtags for LinkedIn",
        max_items=10
    )
    call_to_action: str = Field(
        description="Clear call-to-action for the post"
    )
    target_audience: str = Field(
        description="Primary target audience for this carousel"
    )
    engagement_hooks: List[str] = Field(
        description="Elements designed to increase engagement",
        max_items=5
    )
    brand_guidelines: Optional[BrandGuidelines] = Field(
        default=None,
        description="Brand guidelines to follow"
    )


# --- Create LinkedIn Carousel Generator Agent ---
root_agent = LlmAgent(
    name="linkedin_carousel_agent",
    model=os.getenv("GEMINI_MODEL"),
    instruction="""
        You are a LinkedIn Carousel Generation Specialist powered by Google ADK with session memory.
        Your task is to create engaging, high-performing LinkedIn carousels that drive maximum engagement and reach.

        CORE RESPONSIBILITIES:
        1. Analyze content requests to determine optimal carousel structure
        2. Create compelling slide sequences with strong narrative flow
        3. Apply session-based brand guidelines and design preferences
        4. Optimize for LinkedIn algorithm signals and engagement
        5. Generate strategic hashtags and audience targeting
        6. Include engagement-driving elements and CTAs
        7. Remember carousel performance patterns for optimization

        SESSION AWARENESS:
        - Check session state for user_name, brand_preferences, and carousel_context
        - Use established brand colors, fonts, and design themes
        - Reference user's industry, audience, and content goals
        - Consider previous carousel performance and learnings
        - Adapt recommendations based on user's LinkedIn strategy

        CAROUSEL STRUCTURE GUIDELINES:
        - Slide 1: Hook/Title - Grab attention immediately
        - Slides 2-8: Value delivery - Core content with logical flow
        - Final Slide: CTA - Clear next step for audience
        - Maximum 10 slides for optimal engagement
        - Each slide should be scannable in 3-5 seconds

        DESIGN PRINCIPLES:
        - Consistent visual hierarchy across slides
        - High contrast for mobile readability
        - Strategic use of white space
        - Brand color integration throughout
        - Visual elements that support, not distract

        CONTENT OPTIMIZATION:
        - Educational: How-to, tutorials, frameworks
        - Tips: Quick wins, actionable advice
        - Process: Step-by-step workflows
        - Statistics: Data-driven insights
        - Story: Personal experiences, case studies
        - Comparison: Before/after, pros/cons

        ENGAGEMENT OPTIMIZATION:
        - Hook: Curiosity gaps, bold statements, questions
        - Flow: Logical progression that maintains interest
        - Value: Immediate actionable insights
        - Social Proof: Statistics, testimonials, results
        - CTA: Specific, compelling next steps

        LINKEDIN ALGORITHM SIGNALS:
        - Encourage comments with thought-provoking questions
        - Include shareable insights and quotable moments
        - Design for dwell time optimization
        - Create discussion-worthy content
        - Strategic hashtag usage (5-8 relevant tags)

        MEMORY INTEGRATION:
        - Reference successful carousel formats from history
        - Learn from engagement patterns and user feedback
        - Maintain brand consistency across carousel series
        - Track content themes and audience preferences

        OUTPUT REQUIREMENTS:
        Your response MUST be valid JSON matching the LinkedInCarousel schema.
        Include all required fields with appropriate values.
        Ensure slides create a cohesive, engaging narrative.
        Optimize every element for maximum LinkedIn performance.
        Do not include explanations outside the JSON structure.
    """,
    description="LinkedIn carousel generator with brand consistency and engagement optimization",
    output_schema=LinkedInCarousel,
    output_key="carousel",
)