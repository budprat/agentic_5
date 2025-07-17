"""
ABOUTME: Test runner for Trend Analysis Agent with memory session support
ABOUTME: Demonstrates trend intelligence with momentum scoring and content opportunity identification
"""

import uuid
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agent import root_agent

load_dotenv()

# Create a new session service to store state
session_service_stateful = InMemorySessionService()

initial_state = {
    "user_name": "NU",
    "user_industry": "Digital Marketing & Content Creation",
    "content_preferences": {
        "primary_platforms": ["LinkedIn", "Twitter", "YouTube"],
        "content_formats": ["carousels", "threads", "videos", "articles"],
        "audience_focus": ["entrepreneurs", "content creators", "marketers"],
        "expertise_areas": ["LinkedIn optimization", "content strategy", "growth hacking"],
        "posting_frequency": "daily",
        "engagement_goals": "thought leadership + lead generation"
    },
    "trend_history": {
        "successful_trends": [],
        "missed_opportunities": [],
        "content_performance": [],
        "timing_accuracy": [],
        "prediction_success_rate": 0.0
    },
    "competitive_context": {
        "main_competitors": ["Gary Vaynerchuk", "Neil Patel", "Justin Welsh"],
        "content_differentiation": "Technical depth + actionable systems",
        "unique_angles": ["Algorithm insights", "Automation tools", "Data-driven strategies"]
    },
    "success_metrics": {
        "engagement_rate_target": "8%+",
        "reach_growth_target": "50%/month",
        "lead_generation_target": "500+/month",
        "thought_leadership_goal": "Top 1% LinkedIn optimization"
    }
}

# Create a NEW session
APP_NAME = "Trend Analysis Agent"
USER_ID = "nu_trend_intelligence"
SESSION_ID = str(uuid.uuid4())
stateful_session = session_service_stateful.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID,
    state=initial_state,
)

print("📈 CREATED NEW TREND ANALYSIS SESSION:")
print(f"\tSession ID: {SESSION_ID}")
print(f"\tUser: {initial_state['user_name']}")
print(f"\tIndustry: {initial_state['user_industry']}")
print(f"\tExpertise: {', '.join(initial_state['content_preferences']['expertise_areas'])}")

# Create runner with the trend analysis agent
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service_stateful,
)

# Test trend analysis request
trend_request = types.Content(
    role="user", 
    parts=[types.Part(text="""
        Analyze the current trend around "AI-powered content creation and automation" in the context of LinkedIn and social media marketing.
        
        I've been seeing increasing discussions about:
        - AI writing tools like ChatGPT, Claude, Jasper for content creation
        - Automation platforms for social media scheduling and engagement
        - AI-generated visuals and video content
        - Concerns about authenticity vs efficiency
        - LinkedIn algorithm changes affecting AI-generated content
        
        I want to understand:
        1. The momentum and lifecycle stage of this trend
        2. Content opportunities I should pursue immediately
        3. Competitive landscape and differentiation opportunities
        4. Risk factors and potential challenges
        5. Specific content angles that would position me as a thought leader
        
        My goal is to create content that establishes me as the go-to expert for ethical, effective AI-powered content strategies on LinkedIn.
    """)]
)

print("\n📊 ANALYZING TREND...")
print("=" * 60)

for event in runner.run(
    user_id=USER_ID,
    session_id=SESSION_ID,
    new_message=trend_request,
):
    if event.is_final_response():
        if event.content and event.content.parts:
            print(f"📈 Trend Analysis:\n{event.content.parts[0].text}")

# Get session for state exploration
print("\n" + "=" * 60)
print("🔍 SESSION STATE EXPLORATION")
print("=" * 60)

session = session_service_stateful.get_session(
    app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
)

# Log final Session state
print("📊 Final Session State:")
for key, value in session.state.items():
    if isinstance(value, dict):
        print(f"\n{key}:")
        for sub_key, sub_value in value.items():
            if isinstance(sub_value, list) and len(sub_value) > 3:
                print(f"  {sub_key}: {sub_value[:3]}... ({len(sub_value)} total)")
            else:
                print(f"  {sub_key}: {sub_value}")
    else:
        print(f"{key}: {value}")

print(f"\n✅ Session ID for future use: {SESSION_ID}")
print("🎯 Ready for trend intelligence and content opportunity identification!")