"""
ABOUTME: Test runner for Lead Qualification Agent with memory session support
ABOUTME: Demonstrates lead scoring, BANT qualification, and personalized follow-up strategies
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
    "business_info": {
        "company": "LinkedIn Domination Systems",
        "services": ["LinkedIn optimization", "Content strategy", "Growth automation"],
        "target_market": "Entrepreneurs, content creators, marketing professionals",
        "pricing_range": "$2K-$25K",
        "sales_cycle": "2-6 weeks",
        "unique_advantages": ["Technical expertise", "Proven systems", "Data-driven results"]
    },
    "ideal_customer_profile": {
        "company_size": ["startup", "small", "medium"],
        "budget_range": ["5k_to_10k", "10k_to_25k", "25k_to_50k"],
        "pain_points": ["Low LinkedIn engagement", "Inconsistent content", "No growth strategy"],
        "decision_makers": ["CEO", "CMO", "Marketing Director", "Growth Lead"],
        "industry_focus": ["SaaS", "Consulting", "Education", "Professional Services"]
    },
    "sales_process": {
        "qualification_criteria": {
            "min_budget": 5000,
            "min_team_size": 5,
            "growth_goals": "required",
            "timeline": "within_6_months"
        },
        "typical_objections": ["Budget constraints", "Time investment", "Internal resources"],
        "success_factors": ["Champion identified", "Clear ROI", "Urgent need"],
        "follow_up_sequence": ["Value-first content", "Case studies", "Social proof", "Demo"]
    },
    "qualification_history": {
        "recent_leads": [],
        "conversion_patterns": [],
        "successful_strategies": [],
        "common_blockers": []
    }
}

# Create a NEW session
APP_NAME = "Lead Qualification Agent"
USER_ID = "nu_sales_optimization"
SESSION_ID = str(uuid.uuid4())
stateful_session = session_service_stateful.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID,
    state=initial_state,
)

print("🎯 CREATED NEW LEAD QUALIFICATION SESSION:")
print(f"\tSession ID: {SESSION_ID}")
print(f"\tUser: {initial_state['user_name']}")
print(f"\tCompany: {initial_state['business_info']['company']}")
print(f"\tTarget Market: {initial_state['business_info']['target_market']}")

# Create runner with the lead qualification agent
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service_stateful,
)

# Test lead qualification request
qualification_request = types.Content(
    role="user", 
    parts=[types.Part(text="""
        Qualify this lead for our LinkedIn optimization services:
        
        Lead Information:
        - Name: Sarah Chen
        - Title: VP of Marketing at TechFlow Solutions
        - Company: B2B SaaS startup, 50 employees, Series A funded
        - Industry: Project management software for remote teams
        - LinkedIn: 5K followers, posts inconsistently
        
        Interaction Context:
        - Connected on LinkedIn after she commented on my algorithm post
        - She mentioned struggling with LinkedIn growth despite having good content
        - Company just raised $8M Series A, focused on rapid growth
        - She's been tasked with building thought leadership for the CEO
        - Timeline: Wants to see results within 3 months for upcoming product launch
        - Previous experience: Tried hiring freelance creators but got inconsistent results
        
        Pain Points Mentioned:
        - Low engagement despite quality content (averaging 50 likes per post)
        - CEO posts get even less engagement (20-30 likes)
        - No clear content strategy or posting schedule
        - Struggling to convert LinkedIn traffic to demo bookings
        - Team doesn't understand LinkedIn algorithm
        
        Budget Context:
        - Just raised funding, has budget allocated for growth
        - Mentioned willingness to invest in "the right solution"
        - Previously spent $5K/month on failed freelancer experiment
        - Looking for proven system rather than one-off content creation
        
        Decision Making:
        - She has budget authority for marketing tools and services
        - CEO is involved in content decisions but trusts her recommendations
        - Reports directly to CEO, no other marketing leadership
        - Company culture: data-driven, fast-moving, results-oriented
        
        Please provide a complete qualification assessment with lead score, next steps, and personalized follow-up strategy.
    """)]
)

print("\n📋 QUALIFYING LEAD...")
print("=" * 60)

for event in runner.run(
    user_id=USER_ID,
    session_id=SESSION_ID,
    new_message=qualification_request,
):
    if event.is_final_response():
        if event.content and event.content.parts:
            print(f"🎯 Lead Qualification:\n{event.content.parts[0].text}")

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
print("🎯 Ready for lead qualification and sales pipeline optimization!")