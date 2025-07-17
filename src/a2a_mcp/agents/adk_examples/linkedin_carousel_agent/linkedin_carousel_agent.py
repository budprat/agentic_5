"""
ABOUTME: Test runner for LinkedIn Carousel Agent with memory session support
ABOUTME: Demonstrates stateful carousel generation with brand guidelines and performance tracking
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
    "brand_preferences": {
        "primary_colors": ["#0077B5", "#00A0DC", "#313335"],  # LinkedIn blues + dark
        "secondary_colors": ["#F3F6F8", "#E1E9EE", "#8B9DC3"],
        "font_family": "Inter, Arial, sans-serif",
        "design_style": "professional modern",
        "logo_position": "bottom-right",
        "company": "LinkedIn Domination Systems",
        "industry": "Digital Marketing & Content Creation"
    },
    "carousel_context": {
        "recent_topics": [],
        "performance_history": [],
        "successful_formats": [],
        "audience_preferences": ["entrepreneurs", "content creators", "marketing professionals"],
        "content_goals": ["thought leadership", "engagement", "lead generation"],
        "posting_schedule": "3x per week"
    },
    "target_metrics": {
        "engagement_rate": "8%+",
        "reach_goal": "50K+ impressions",
        "comments_target": "100+",
        "shares_target": "50+"
    }
}

# Create a NEW session
APP_NAME = "LinkedIn Carousel Agent"
USER_ID = "nu_carousel_domination"
SESSION_ID = str(uuid.uuid4())
stateful_session = session_service_stateful.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID,
    state=initial_state,
)

print("🎠 CREATED NEW CAROUSEL AGENT SESSION:")
print(f"\tSession ID: {SESSION_ID}")
print(f"\tUser: {initial_state['user_name']}")
print(f"\tCompany: {initial_state['brand_preferences']['company']}")
print(f"\tIndustry: {initial_state['brand_preferences']['industry']}")

# Create runner with the carousel agent
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service_stateful,
)

# Test carousel generation request
carousel_request = types.Content(
    role="user", 
    parts=[types.Part(text="""
        Create a LinkedIn carousel about "10 LinkedIn Algorithm Secrets That Tripled My Reach". 
        This should be educational content that teaches entrepreneurs and content creators 
        how to optimize their LinkedIn strategy. Include data-driven insights, actionable tips, 
        and make it highly engaging for maximum shares and comments.
        
        Target audience: Entrepreneurs, content creators, marketing professionals
        Goal: Establish thought leadership while driving engagement
        Style: Professional but approachable, data-backed insights
    """)]
)

print("\n🎨 GENERATING LINKEDIN CAROUSEL...")
print("=" * 60)

for event in runner.run(
    user_id=USER_ID,
    session_id=SESSION_ID,
    new_message=carousel_request,
):
    if event.is_final_response():
        if event.content and event.content.parts:
            print(f"🎠 Generated Carousel:\n{event.content.parts[0].text}")

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
print("🎯 Ready for carousel creation and performance optimization!")