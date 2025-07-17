"""
ABOUTME: Test runner for Social Media Content Agent with memory session support  
ABOUTME: Demonstrates multi-platform content optimization with cross-promotion and engagement strategies
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
    "brand_voice": {
        "personality": "Confident expert with approachable teaching style",
        "tone": "Professional but personable, data-driven, actionable",
        "values": ["Authenticity", "Results-driven", "Continuous learning"],
        "voice_characteristics": ["Direct", "Insightful", "Practical", "Encouraging"],
        "content_themes": ["LinkedIn optimization", "Content strategy", "Growth systems"]
    },
    "platform_preferences": {
        "primary_platforms": ["LinkedIn", "Twitter", "YouTube"],
        "secondary_platforms": ["Instagram", "Threads"],
        "content_distribution": {
            "LinkedIn": "40%",
            "Twitter": "25%", 
            "YouTube": "20%",
            "Instagram": "10%",
            "Threads": "5%"
        },
        "posting_frequency": {
            "LinkedIn": "Daily",
            "Twitter": "3x daily",
            "YouTube": "2x weekly",
            "Instagram": "3x weekly",
            "Threads": "Daily"
        }
    },
    "content_history": {
        "top_performing_content": [],
        "successful_hashtags": ["#LinkedInTips", "#ContentStrategy", "#GrowthHacking"],
        "audience_preferences": ["How-to content", "Data insights", "Behind-the-scenes"],
        "engagement_patterns": {
            "best_times": {"LinkedIn": "9AM-11AM", "Twitter": "8AM-10AM"},
            "top_formats": ["Carousels", "Threads", "Video tutorials"]
        }
    },
    "audience_insights": {
        "primary_demographics": "Entrepreneurs, content creators, marketing professionals aged 25-45",
        "pain_points": ["Inconsistent content", "Low engagement", "No clear strategy"],
        "goals": ["LinkedIn growth", "Thought leadership", "Lead generation"],
        "platform_behavior": {
            "LinkedIn": "Professional development focus",
            "Twitter": "Quick tips and industry news",
            "YouTube": "In-depth tutorials and walkthroughs"
        }
    },
    "business_objectives": {
        "primary_goals": ["Thought leadership", "Lead generation", "Community building"],
        "success_metrics": ["Engagement rate 8%+", "Monthly leads 500+", "Follower growth 1000+/month"],
        "content_objectives": ["Educate", "Inspire", "Convert"],
        "brand_positioning": "The go-to expert for LinkedIn algorithm optimization"
    }
}

# Create a NEW session
APP_NAME = "Social Media Content Agent"
USER_ID = "nu_social_content_optimization"
SESSION_ID = str(uuid.uuid4())
stateful_session = session_service_stateful.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID,
    state=initial_state,
)

print("📱 CREATED NEW SOCIAL MEDIA CONTENT SESSION:")
print(f"\tSession ID: {SESSION_ID}")
print(f"\tUser: {initial_state['user_name']}")
print(f"\tBrand Voice: {initial_state['brand_voice']['personality']}")
print(f"\tPrimary Platforms: {', '.join(initial_state['platform_preferences']['primary_platforms'])}")

# Create runner with the social media content agent
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service_stateful,
)

# Test social media content request
content_request = types.Content(
    role="user", 
    parts=[types.Part(text="""
        Create multi-platform social media content around the topic: "5 LinkedIn Algorithm Updates That Changed Everything in 2024"
        
        Content Context:
        - This should be educational content that establishes thought leadership
        - Target audience: Entrepreneurs, content creators, marketing professionals
        - Goal: Drive engagement and position me as the LinkedIn algorithm expert
        - Include recent algorithm changes like creator mode benefits, video prioritization, etc.
        
        Platform Requirements:
        - LinkedIn (primary): Professional carousel or long-form post
        - Twitter: Thread format with key insights
        - YouTube: Video script outline/description 
        - Instagram: Visual post with key takeaways
        - Threads: Conversational discussion starter
        
        Content Goals:
        - Educate audience about algorithm changes
        - Provide actionable insights they can implement
        - Generate comments and shares
        - Drive traffic to LinkedIn for deeper engagement
        - Establish authority on LinkedIn optimization
        
        Please create platform-specific adaptations with optimal timing, hashtags, and engagement strategies. Include cross-promotion plan and performance predictions.
    """)]
)

print("\n📲 GENERATING MULTI-PLATFORM CONTENT...")
print("=" * 60)

for event in runner.run(
    user_id=USER_ID,
    session_id=SESSION_ID,
    new_message=content_request,
):
    if event.is_final_response():
        if event.content and event.content.parts:
            print(f"📱 Social Media Content:\n{event.content.parts[0].text}")

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
            elif isinstance(sub_value, dict) and len(sub_value) > 3:
                print(f"  {sub_key}: {{...}} ({len(sub_value)} items)")
            else:
                print(f"  {sub_key}: {sub_value}")
    else:
        print(f"{key}: {value}")

print(f"\n✅ Session ID for future use: {SESSION_ID}")
print("🎯 Ready for multi-platform content creation and optimization!")