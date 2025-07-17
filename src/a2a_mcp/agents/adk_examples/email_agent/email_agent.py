"""
ABOUTME: Test runner for Advanced Email Agent with memory session support
ABOUTME: Demonstrates stateful email generation with user preferences and context
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
    "user_preferences": {
        "email_style": "professional but personable",
        "signature": "Best regards,\nNU",
        "company": "LinkedIn Domination Systems",
        "role": "CEO & Content Strategist",
        "industry": "Digital Marketing & Content Creation",
        "tone_preference": "confident and authoritative",
        "common_contacts": ["clients", "partners", "team members", "influencers"],
        "priorities": ["LinkedIn growth", "content excellence", "relationship building"]
    },
    "email_context": {
        "recent_topics": [],
        "follow_ups_needed": [],
        "templates_used": []
    }
}

# Create a NEW session
APP_NAME = "Advanced Email Agent"
USER_ID = "nu_linkedin_domination"
SESSION_ID = str(uuid.uuid4())
stateful_session = session_service_stateful.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID,
    state=initial_state,
)

print("🚀 CREATED NEW EMAIL AGENT SESSION:")
print(f"\tSession ID: {SESSION_ID}")
print(f"\tUser: {initial_state['user_name']}")
print(f"\tCompany: {initial_state['user_preferences']['company']}")

# Create runner with the email agent
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service_stateful,
)

# Test email generation request
email_request = types.Content(
    role="user", 
    parts=[types.Part(text="""
        Create a professional follow-up email to a potential LinkedIn collaboration partner. 
        We discussed creating co-authored content about LinkedIn algorithm optimization. 
        They mentioned they have 50K+ followers and are interested in cross-promotion.
        The email should propose specific next steps and include a clear call-to-action.
    """)]
)

print("\n📧 GENERATING EMAIL...")
print("=" * 50)

for event in runner.run(
    user_id=USER_ID,
    session_id=SESSION_ID,
    new_message=email_request,
):
    if event.is_final_response():
        if event.content and event.content.parts:
            print(f"📨 Generated Email:\n{event.content.parts[0].text}")

# Get session for state exploration
print("\n" + "=" * 50)
print("🔍 SESSION STATE EXPLORATION")
print("=" * 50)

session = session_service_stateful.get_session(
    app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
)

# Log final Session state
print("📊 Final Session State:")
for key, value in session.state.items():
    if isinstance(value, dict):
        print(f"\n{key}:")
        for sub_key, sub_value in value.items():
            print(f"  {sub_key}: {sub_value}")
    else:
        print(f"{key}: {value}")

print(f"\n✅ Session ID for future use: {SESSION_ID}")