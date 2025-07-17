"""
ABOUTME: Competitor Analysis Agent using Google ADK with Pydantic models for strategic intelligence
ABOUTME: Demonstrates comprehensive competitor research with actionable insights and opportunity identification
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


# --- Define Competitor Tier Enum ---
class CompetitorTier(str, Enum):
    DIRECT = "direct"
    INDIRECT = "indirect"
    ASPIRATIONAL = "aspirational"
    EMERGING = "emerging"


# --- Define Content Category Enum ---
class ContentCategory(str, Enum):
    EDUCATIONAL = "educational"
    PROMOTIONAL = "promotional"
    THOUGHT_LEADERSHIP = "thought_leadership"


# --- Define Engagement Metrics Schema ---
class EngagementMetrics(BaseModel):
    average_likes: float = Field(description="Average likes per post")
    average_comments: float = Field(description="Average comments per post")
    average_shares: float = Field(description="Average shares per post")
    engagement_rate: float = Field(description="Overall engagement rate percentage")
    best_performing_post_likes: int = Field(description="Highest performing post likes")
    posting_frequency: str = Field(description="How often they post (e.g., '3x per week')")


# --- Define Content Strategy Schema ---
class ContentStrategy(BaseModel):
    primary_topics: List[str] = Field(description="Main content themes they focus on")
    content_mix: Dict[str, float] = Field(description="Percentage breakdown of content types")
    posting_times: List[str] = Field(description="Optimal posting times they use")
    hashtag_strategy: List[str] = Field(description="Common hashtags they use")
    content_length: str = Field(description="Typical post length (short/medium/long)")


# --- Define SWOT Analysis Schema ---
class SWOTAnalysis(BaseModel):
    strengths: List[str] = Field(description="Competitor's key strengths", max_items=5)
    weaknesses: List[str] = Field(description="Identified weaknesses and gaps", max_items=5)
    opportunities: List[str] = Field(description="Opportunities they're missing", max_items=5)
    threats: List[str] = Field(description="Threats they pose to your strategy", max_items=5)


# --- Define Competitive Gap Schema ---
class CompetitiveGap(BaseModel):
    gap_type: str = Field(description="Type of gap (content, audience, strategy, etc.)")
    description: str = Field(description="Detailed description of the gap")
    opportunity_size: str = Field(description="Size of opportunity (small/medium/large)")
    difficulty: str = Field(description="Difficulty to exploit (easy/medium/hard)")
    recommended_action: str = Field(description="Specific action to take advantage")


# --- Define Competitor Profile Schema ---
class CompetitorProfile(BaseModel):
    name: str = Field(description="Competitor name or handle")
    tier: CompetitorTier = Field(description="Competitor classification")
    follower_count: int = Field(description="Current follower count")
    industry_focus: str = Field(description="Primary industry or niche")
    unique_value_proposition: str = Field(description="What makes them unique")
    target_audience: str = Field(description="Their primary audience")


# --- Define Competitor Analysis Schema ---
class CompetitorAnalysis(BaseModel):
    analysis_date: str = Field(description="Date of analysis", default_factory=lambda: datetime.now().isoformat())
    competitor_profile: CompetitorProfile = Field(description="Basic competitor information")
    engagement_metrics: EngagementMetrics = Field(description="Performance metrics analysis")
    content_strategy: ContentStrategy = Field(description="Content strategy breakdown")
    swot_analysis: SWOTAnalysis = Field(description="Strengths, weaknesses, opportunities, threats")
    competitive_gaps: List[CompetitiveGap] = Field(
        description="Identified gaps and opportunities",
        max_items=5
    )
    key_insights: List[str] = Field(
        description="Key takeaways from the analysis",
        max_items=5
    )
    recommended_actions: List[str] = Field(
        description="Specific actions to outperform this competitor",
        max_items=5
    )
    threat_level: str = Field(description="Threat assessment (low/medium/high)")
    opportunity_score: float = Field(
        description="Opportunity score from 1-10",
        ge=1.0,
        le=10.0
    )


# --- Create Competitor Analysis Agent ---
competitor_analysis_agent = LlmAgent(
    name="competitor_analysis_agent",
    model=os.getenv("GEMINI_MODEL"),
    instruction="""
        You are a Strategic Competitor Intelligence Analyst powered by Google ADK with session memory.
        Your task is to conduct comprehensive competitor analysis that provides actionable insights for competitive advantage.

        CORE RESPONSIBILITIES:
        1. Analyze competitor profiles across multiple dimensions
        2. Identify content strategies, engagement patterns, and audience insights
        3. Conduct thorough SWOT analysis with strategic implications
        4. Discover competitive gaps and untapped opportunities
        5. Provide specific, actionable recommendations for competitive advantage
        6. Track competitive landscape changes over time
        7. Build intelligence database for strategic decision-making

        SESSION AWARENESS:
        - Check session state for user_industry, competitive_landscape, and analysis_history
        - Reference previous competitor analyses for trend identification
        - Use established competitive benchmarks and performance standards
        - Consider user's competitive positioning and strategic goals
        - Maintain competitive intelligence database across sessions

        ANALYSIS FRAMEWORK:
        1. **Profile Analysis**: Basic metrics, positioning, audience
        2. **Content Intelligence**: Strategy, themes, performance patterns
        3. **Engagement Analysis**: Metrics, audience interaction, growth trends
        4. **Strategic Assessment**: SWOT analysis with competitive implications
        5. **Gap Identification**: Missed opportunities and strategic weaknesses
        6. **Actionable Insights**: Specific recommendations for advantage

        CONTENT STRATEGY ANALYSIS:
        - Content mix and themes
        - Posting frequency and timing optimization
        - Engagement tactics and community building
        - Hashtag and SEO strategies
        - Visual content and brand consistency
        - Thought leadership positioning

        SWOT METHODOLOGY:
        - **Strengths**: What they do exceptionally well
        - **Weaknesses**: Gaps in strategy, content, or execution
        - **Opportunities**: Market gaps they haven't addressed
        - **Threats**: How they could impact your market position

        GAP IDENTIFICATION FOCUS:
        - Content gaps: Topics they're not covering
        - Audience gaps: Segments they're not serving
        - Format gaps: Content types they're missing
        - Engagement gaps: Community building weaknesses
        - Strategic gaps: Positioning opportunities

        COMPETITIVE INTELLIGENCE PRIORITIES:
        - Quantifiable metrics and performance data
        - Strategic positioning and differentiation
        - Content performance patterns and successful formats
        - Audience engagement and community building tactics
        - Innovation in content, strategy, or technology
        - Partnership and collaboration strategies

        ACTIONABLE RECOMMENDATIONS:
        - Specific tactics to exploit identified gaps
        - Content strategies to outperform competitors
        - Audience engagement techniques to differentiate
        - Positioning strategies for competitive advantage
        - Innovation opportunities in underserved areas

        MEMORY INTEGRATION:
        - Track competitive landscape evolution over time
        - Learn from successful competitive strategies
        - Build comprehensive competitor intelligence database
        - Identify industry trends and shifts in competitive dynamics
        - Maintain strategic context for long-term planning

        OUTPUT REQUIREMENTS:
        Your response MUST be valid JSON matching the CompetitorAnalysis schema.
        Provide specific, quantifiable insights where possible.
        Focus on actionable intelligence that drives strategic advantage.
        Include opportunity scoring and threat assessment.
        Do not include explanations outside the JSON structure.
    """,
    description="Strategic competitor analysis with actionable intelligence and opportunity identification",
    output_schema=CompetitorAnalysis,
    output_key="analysis",
)