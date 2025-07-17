"""
ABOUTME: Lead Qualification Agent using Google ADK with Pydantic models for sales pipeline optimization
ABOUTME: Demonstrates lead scoring, qualification criteria, and personalized follow-up recommendations
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


# --- Define Lead Status Enum ---
class LeadStatus(str, Enum):
    COLD = "cold"
    WARM = "warm"
    HOT = "hot"
    QUALIFIED = "qualified"
    DISQUALIFIED = "disqualified"


# --- Define Budget Range Enum ---
class BudgetRange(str, Enum):
    UNDER_1K = "under_1k"
    ONE_TO_5K = "1k_to_5k"
    FIVE_TO_10K = "5k_to_10k"
    TEN_TO_25K = "10k_to_25k"
    TWENTY_FIVE_TO_50K = "25k_to_50k"
    OVER_50K = "over_50k"
    UNKNOWN = "unknown"


# --- Define Company Size Enum ---
class CompanySize(str, Enum):
    STARTUP = "startup"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"


# --- Define Lead Source Enum ---
class LeadSource(str, Enum):
    LINKEDIN = "linkedin"
    WEBSITE = "website"
    REFERRAL = "referral"
    CONTENT = "content"
    EMAIL = "email"
    SOCIAL = "social"
    EVENT = "event"
    COLD_OUTREACH = "cold_outreach"


# --- Define Pain Point Schema ---
class PainPoint(BaseModel):
    category: str = Field(description="Pain point category (e.g., 'growth', 'efficiency', 'cost')")
    description: str = Field(description="Detailed description of the pain point")
    severity: str = Field(description="Pain severity (low/medium/high/critical)")
    impact: str = Field(description="Business impact if not solved")
    urgency: str = Field(description="Timeline urgency (low/medium/high)")


# --- Define Decision Maker Schema ---
class DecisionMaker(BaseModel):
    role: str = Field(description="Role/title of decision maker")
    influence_level: str = Field(description="Level of influence (low/medium/high)")
    contact_status: str = Field(description="Contact status (not_contacted/contacted/engaged)")
    relationship_strength: str = Field(description="Relationship strength (none/weak/moderate/strong)")


# --- Define Qualification Criteria Schema ---
class QualificationCriteria(BaseModel):
    budget_fit: bool = Field(description="Does budget align with offering")
    authority_confirmed: bool = Field(description="Decision maker identified and engaged")
    need_validated: bool = Field(description="Business need confirmed and quantified")
    timeline_realistic: bool = Field(description="Timeline aligns with sales cycle")
    competitive_advantage: bool = Field(description="Clear advantage over competitors")


# --- Define Follow Up Action Schema ---
class FollowUpAction(BaseModel):
    action_type: str = Field(description="Type of follow-up (email, call, content, demo, etc.)")
    priority: str = Field(description="Priority level (low/medium/high/urgent)")
    timeline: str = Field(description="When to execute (immediately/today/this_week/next_week)")
    message_template: str = Field(description="Suggested message or talking points")
    expected_outcome: str = Field(description="What you expect to achieve")


# --- Define Lead Qualification Schema ---
class LeadQualification(BaseModel):
    qualification_date: str = Field(description="Date of qualification", default_factory=lambda: datetime.now().isoformat())
    lead_name: str = Field(description="Lead's name or company name")
    lead_source: LeadSource = Field(description="How the lead was acquired")
    company_info: Dict[str, str] = Field(description="Company information (size, industry, etc.)")
    lead_score: int = Field(
        description="Lead score from 0-100",
        ge=0,
        le=100
    )
    qualification_status: LeadStatus = Field(description="Current lead status")
    qualification_criteria: QualificationCriteria = Field(description="BANT qualification assessment")
    pain_points: List[PainPoint] = Field(
        description="Identified pain points and challenges",
        max_items=5
    )
    decision_makers: List[DecisionMaker] = Field(
        description="Key decision makers and influencers",
        max_items=5
    )
    budget_range: BudgetRange = Field(description="Estimated budget range")
    decision_timeline: str = Field(description="Expected decision timeframe")
    competitive_situation: List[str] = Field(
        description="Known competitors in consideration",
        max_items=5
    )
    value_proposition_fit: str = Field(description="How well your solution fits their needs")
    objections_concerns: List[str] = Field(
        description="Identified objections or concerns",
        max_items=5
    )
    next_actions: List[FollowUpAction] = Field(
        description="Recommended next steps",
        max_items=5
    )
    personalization_data: Dict[str, str] = Field(
        description="Personal details for relationship building"
    )
    success_probability: float = Field(
        description="Probability of closing (0-100%)",
        ge=0.0,
        le=100.0
    )
    estimated_deal_value: Optional[str] = Field(
        default=None,
        description="Estimated deal value if closed"
    )
    notes: List[str] = Field(
        description="Additional qualification notes",
        max_items=3
    )


# --- Create Lead Qualification Agent ---
lead_qualification_agent = LlmAgent(
    name="lead_qualification_agent",
    model=os.getenv("GEMINI_MODEL"),
    instruction="""
        You are a Strategic Lead Qualification Specialist powered by Google ADK with session memory.
        Your task is to analyze prospects and provide comprehensive qualification assessments with actionable follow-up strategies.

        CORE RESPONSIBILITIES:
        1. Assess lead quality using BANT methodology (Budget, Authority, Need, Timeline)
        2. Score leads based on fit, urgency, and probability of conversion
        3. Identify key decision makers and relationship-building opportunities
        4. Analyze pain points and map solutions to business needs
        5. Develop personalized follow-up strategies with specific actions
        6. Track qualification progression and relationship development
        7. Optimize sales process based on qualification insights

        SESSION AWARENESS:
        - Check session state for sales_process, ideal_customer_profile, and qualification_history
        - Reference previous lead interactions and successful patterns
        - Use established scoring criteria and qualification benchmarks
        - Consider sales cycle length and typical decision processes
        - Maintain lead relationship intelligence across interactions

        LEAD SCORING METHODOLOGY:
        - **0-25**: Poor fit, major disqualifying factors
        - **26-50**: Moderate fit, some challenges or gaps
        - **51-75**: Good fit, minor objections to overcome
        - **76-90**: Excellent fit, high probability prospect
        - **91-100**: Perfect fit, priority prospect

        BANT QUALIFICATION FRAMEWORK:
        - **Budget**: Financial capacity and allocation priorities
        - **Authority**: Decision-making power and influence structure
        - **Need**: Business pain points and solution requirements
        - **Timeline**: Decision urgency and implementation schedule

        PAIN POINT ANALYSIS:
        - Categorize by business impact and urgency
        - Quantify cost of inaction where possible
        - Map pain points to solution capabilities
        - Identify emotional and logical drivers
        - Assess competitive advantage potential

        DECISION MAKER MAPPING:
        - Identify champions, influencers, and blockers
        - Assess relationship strength and engagement level
        - Develop multi-threaded relationship strategies
        - Consider buying committee dynamics
        - Plan stakeholder-specific messaging

        PERSONALIZATION STRATEGY:
        - Research personal and professional background
        - Identify shared connections and interests
        - Understand communication preferences
        - Note previous interactions and context
        - Tailor messaging to individual motivations

        FOLLOW-UP OPTIMIZATION:
        - Sequence actions for maximum impact
        - Balance persistence with respect
        - Provide value in every interaction
        - Use appropriate channels and timing
        - Set clear expectations and next steps

        COMPETITIVE INTELLIGENCE:
        - Identify known competitors in consideration
        - Assess your competitive advantages
        - Develop differentiation strategies
        - Anticipate and address competitive objections
        - Position unique value propositions

        MEMORY INTEGRATION:
        - Track lead progression and interaction history
        - Learn from successful qualification patterns
        - Maintain relationship context and preferences
        - Identify optimal timing and messaging strategies
        - Build comprehensive prospect intelligence

        OUTPUT REQUIREMENTS:
        Your response MUST be valid JSON matching the LeadQualification schema.
        Provide specific, actionable insights with clear scoring rationale.
        Include personalized follow-up strategies and timeline recommendations.
        Focus on qualification criteria and next steps for sales progression.
        Do not include explanations outside the JSON structure.
    """,
    description="Lead qualification and sales pipeline optimization with personalized follow-up strategies",
    output_schema=LeadQualification,
    output_key="qualification",
)
