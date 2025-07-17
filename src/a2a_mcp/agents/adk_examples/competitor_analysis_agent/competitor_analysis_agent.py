"""
ABOUTME: Test runner for Competitor Analysis Agent with memory session support
ABOUTME: Demonstrates strategic competitor intelligence with actionable insights and gap identification
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
    "competitive_landscape": {
        "primary_competitors": ["Gary Vaynerchuk", "Neil Patel", "Mari Smith", "Jeff Bullas"],
        "competitive_positioning": "LinkedIn algorithm optimization expert",
        "unique_advantages": ["Technical expertise", "Data-driven approach", "System automation"],
        "target_metrics": {
            "follower_growth": "1000+/month",
            "engagement_rate": "8%+",
            "thought_leadership": "Top 1% in LinkedIn optimization"
        }
    },
    "analysis_history": {
        "completed_analyses": [],
        "key_learnings": [],
        "competitive_gaps_identified": [],
        "successful_strategies_copied": []
    },
    "strategic_goals": {
        "short_term": ["Increase engagement rate", "Grow thought leadership"],
        "long_term": ["Dominate LinkedIn education space", "Build course business"],
        "differentiation": "Technical + actionable insights"
    }
}

# Create a NEW session
APP_NAME = "Competitor Analysis Agent"
USER_ID = "nu_competitive_intelligence"
SESSION_ID = str(uuid.uuid4())
stateful_session = session_service_stateful.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID,
    state=initial_state,
)

print("🔍 CREATED NEW COMPETITOR ANALYSIS SESSION:")
print(f"\tSession ID: {SESSION_ID}")
print(f"\tUser: {initial_state['user_name']}")
print(f"\tIndustry: {initial_state['user_industry']}")
print(f"\tPositioning: {initial_state['competitive_landscape']['competitive_positioning']}")

# Create runner with the competitor analysis agent
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service_stateful,
)

# Test competitor analysis request
competitor_request = types.Content(
    role="user", 
    parts=[types.Part(text="""
        Analyze Justin Welsh as a competitor in the LinkedIn content space. 
        
        Key details:
        - ~500K LinkedIn followers
        - Focus: Solopreneur education and LinkedIn growth
        - Posts daily, mix of personal stories and business advice  
        - Strong engagement rates (typically 1K+ likes per post)
        - Monetizes through courses and newsletter
        - Known for simple, actionable advice
        - Uses a lot of personal anecdotes and data from his own journey
        
        I want to understand:
        1. His content strategy and what makes him successful
        2. Gaps in his approach that I could exploit
        3. Specific tactics I could adapt or improve upon
        4. How to differentiate from his style while learning from his success
        
        My goal is to build a competitive strategy for LinkedIn domination focused on algorithm optimization and technical insights.
    """)]
)

print("\n📊 ANALYZING COMPETITOR...")
print("=" * 60)

for event in runner.run(
    user_id=USER_ID,
    session_id=SESSION_ID,
    new_message=competitor_request,
):
    if event.is_final_response():
        if event.content and event.content.parts:
            print(f"🎯 Competitor Analysis:\n{event.content.parts[0].text}")

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
print("🎯 Ready for competitive intelligence and strategic planning!")