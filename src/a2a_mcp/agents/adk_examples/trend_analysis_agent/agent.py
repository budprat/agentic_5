"""
ABOUTME: Trend Analysis Agent using Google ADK with Pydantic models for content opportunity identification
ABOUTME: Demonstrates trend analysis with momentum scoring and strategic content recommendations
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


# --- Define Trend Status Enum ---
class TrendStatus(str, Enum):
    EMERGING = "emerging"
    GROWING = "growing"
    PEAK = "peak"
    DECLINING = "declining"
    RESURGENT = "resurgent"


# --- Define Opportunity Level Enum ---
class OpportunityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# --- Define Content Angle Enum ---
class ContentAngle(str, Enum):
    EDUCATIONAL = "educational"
    OPINION = "opinion"
    CASE_STUDY = "case_study"
    PREDICTION = "prediction"


# --- Define Trend Source Schema ---
class TrendSource(BaseModel):
    source_name: str = Field(description="Name of the trend source", max_length=100)
    source_type: str = Field(description="Type of source (social, news, research, etc.)", max_length=50)
    credibility_score: float = Field(description="Source credibility from 1-10", ge=1.0, le=10.0)
    data_points: int = Field(description="Number of data points from this source")


# --- Define Keyword Analysis Schema ---
class KeywordAnalysis(BaseModel):
    primary_keyword: str = Field(description="Main keyword for the trend", max_length=100)
    related_keywords: List[str] = Field(description="Related keywords and variations", max_items=5)
    search_volume: str = Field(description="Estimated monthly search volume", max_length=50)
    competition_level: str = Field(description="Keyword competition (low/medium/high)", max_length=20)
    trending_hashtags: List[str] = Field(description="Trending hashtags related to topic", max_items=5)


# --- Define Content Opportunity Schema ---
class ContentOpportunity(BaseModel):
    angle: ContentAngle = Field(description="Content angle to pursue")
    title_suggestions: List[str] = Field(description="Suggested content titles", max_items=3)
    target_platforms: List[str] = Field(description="Best platforms for this content", max_items=3)
    estimated_reach: str = Field(description="Estimated potential reach", max_length=50)
    content_format: str = Field(description="Recommended content format", max_length=50)
    urgency_level: str = Field(description="How quickly to act (low/medium/high)", max_length=20)


# --- Define Market Sentiment Schema ---
class MarketSentiment(BaseModel):
    overall_sentiment: str = Field(description="Overall market sentiment (positive/negative/neutral)", max_length=20)
    sentiment_score: float = Field(description="Sentiment score from -1 to 1", ge=-1.0, le=1.0)
    key_drivers: List[str] = Field(description="Main factors driving sentiment", max_items=3)
    audience_emotions: List[str] = Field(description="Primary emotions in audience", max_items=3)


# --- Define Trend Metrics Schema ---
class TrendMetrics(BaseModel):
    momentum_score: float = Field(
        description="Trend momentum from 1-10",
        ge=1.0,
        le=10.0
    )
    velocity: str = Field(description="Speed of trend growth (slow/moderate/fast/explosive)", max_length=30)
    saturation_level: float = Field(
        description="Market saturation percentage",
        ge=0.0,
        le=100.0
    )
    estimated_lifespan: str = Field(description="Predicted trend duration", max_length=50)
    peak_timing: str = Field(description="When trend is expected to peak", max_length=50)


# --- Define Trend Analysis Schema ---
class TrendAnalysis(BaseModel):
    analysis_date: str = Field(description="Date of analysis", default_factory=lambda: datetime.now().isoformat())
    trend_topic: str = Field(
        description="Main trend topic or theme",
        min_length=5,
        max_length=100
    )
    trend_status: TrendStatus = Field(description="Current trend lifecycle stage")
    trend_metrics: TrendMetrics = Field(description="Quantitative trend measurements")
    opportunity_level: OpportunityLevel = Field(description="Overall opportunity assessment")
    keyword_analysis: KeywordAnalysis = Field(description="Keyword and search trend data")
    market_sentiment: MarketSentiment = Field(description="Market sentiment analysis")
    content_opportunities: List[ContentOpportunity] = Field(
        description="Specific content opportunities identified",
        max_items=3
    )
    trend_sources: List[TrendSource] = Field(
        description="Sources used for trend analysis",
        max_items=3
    )
    risk_factors: List[str] = Field(
        description="Potential risks or challenges",
        max_items=3
    )
    competitive_landscape: List[str] = Field(
        description="Key players already in this trend space",
        max_items=5
    )
    recommended_actions: List[str] = Field(
        description="Specific immediate actions to take",
        max_items=3
    )
    success_metrics: List[str] = Field(
        description="How to measure success in this trend",
        max_items=3
    )


# --- Create Trend Analysis Agent ---
root_agent = LlmAgent(
    name="trend_analysis_agent",
    model=os.getenv("GEMINI_MODEL"),
    instruction="""
        You are a Strategic Trend Intelligence Analyst powered by Google ADK with session memory.
        Your task is to identify, analyze, and quantify content opportunities from emerging and growing trends.

        CORE RESPONSIBILITIES:
        1. Identify and validate trending topics across multiple data sources
        2. Analyze trend momentum, velocity, and lifecycle positioning
        3. Assess market sentiment and audience emotional drivers
        4. Quantify content opportunity potential with specific recommendations
        5. Provide strategic timing guidance for maximum impact
        6. Track trend evolution and competitive landscape changes
        7. Generate actionable content strategies with success metrics

        SESSION AWARENESS:
        - Check session state for user_industry, content_preferences, and trend_history
        - Reference previous trend analyses for pattern recognition
        - Use established content performance benchmarks
        - Consider user's audience demographics and engagement patterns
        - Maintain trend intelligence database for strategic planning

        TREND ANALYSIS FRAMEWORK:
        1. **Trend Validation**: Multi-source verification and credibility assessment
        2. **Momentum Analysis**: Growth velocity and trajectory evaluation
        3. **Opportunity Sizing**: Market potential and content gap analysis
        4. **Competitive Assessment**: Player analysis and differentiation opportunities
        5. **Timing Strategy**: Optimal entry points and content calendar integration
        6. **Risk Evaluation**: Potential challenges and mitigation strategies

        MOMENTUM SCORING METHODOLOGY:
        - **1-3**: Early emerging trends with potential
        - **4-6**: Growing trends with increasing momentum
        - **7-8**: Strong momentum with immediate opportunity
        - **9-10**: Peak momentum requiring urgent action

        OPPORTUNITY ASSESSMENT CRITERIA:
        - **CRITICAL**: Massive opportunity requiring immediate action
        - **HIGH**: Strong opportunity with significant potential
        - **MEDIUM**: Solid opportunity worth pursuing
        - **LOW**: Limited opportunity or high risk

        CONTENT STRATEGY DEVELOPMENT:
        - Multiple content angles for comprehensive coverage
        - Platform-specific optimization recommendations
        - Timing strategies for maximum reach and engagement
        - Format recommendations based on trend characteristics
        - Audience targeting and messaging guidance

        TREND LIFECYCLE UNDERSTANDING:
        - **EMERGING**: Early signals, low competition, high risk/reward
        - **GROWING**: Increasing momentum, moderate competition
        - **PEAK**: Maximum attention, high competition, declining opportunity
        - **DECLINING**: Waning interest, opportunity for contrarian content
        - **RESURGENT**: Renewed interest, potential for nostalgia or updated angles

        COMPETITIVE INTELLIGENCE:
        - Identify key players and their strategies
        - Find content gaps and differentiation opportunities
        - Assess saturation levels and entry barriers
        - Recommend unique positioning strategies

        RISK ASSESSMENT FACTORS:
        - Trend sustainability and longevity
        - Competitive saturation levels
        - Audience fatigue potential
        - Platform algorithm changes
        - Controversial or sensitive aspects

        MEMORY INTEGRATION:
        - Track trend evolution and accuracy of predictions
        - Learn from successful content strategies
        - Build comprehensive trend intelligence database
        - Identify pattern recognition for future trend prediction
        - Maintain competitive landscape awareness

        OUTPUT REQUIREMENTS:
        Your response MUST be valid JSON matching the TrendAnalysis schema.
        Provide specific, quantifiable insights with clear action items.
        Include momentum scoring and opportunity assessment.
        Focus on actionable intelligence for immediate content strategy.
        Do not include explanations outside the JSON structure.
    """,
    description="Strategic trend analysis with momentum scoring and content opportunity identification",
    output_schema=TrendAnalysis,
    output_key="analysis",
)