"""
ABOUTME: Test runner for Blog Post Generator Agent with memory session support
ABOUTME: Demonstrates long-form content creation with SEO optimization and engagement strategies
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
    "content_strategy": {
        "primary_topics": ["LinkedIn optimization", "Content strategy", "Growth automation", "Algorithm insights"],
        "content_pillars": ["Education", "Case studies", "Industry analysis", "How-to guides"],
        "target_keywords": ["linkedin algorithm", "content strategy", "linkedin growth", "social media optimization"],
        "content_goals": ["Thought leadership", "Lead generation", "SEO ranking", "Audience education"],
        "publishing_frequency": "2x per week"
    },
    "brand_voice": {
        "tone": "Professional but approachable, data-driven, actionable",
        "personality": "Expert teacher who simplifies complex topics",
        "writing_style": "Clear, direct, evidence-based",
        "expertise_areas": ["LinkedIn algorithm", "Content systems", "Growth strategies"],
        "unique_angles": ["Technical insights", "Data-driven approach", "Systematic methods"]
    },
    "blog_performance": {
        "top_performing_topics": ["LinkedIn algorithm updates", "Content planning systems", "Growth case studies"],
        "successful_formats": ["Step-by-step guides", "Data analysis", "Behind-the-scenes"],
        "engagement_drivers": ["Actionable tips", "Real examples", "Industry insights"],
        "average_metrics": {"word_count": 2500, "read_time": 12, "engagement_rate": "8%"}
    },
    "audience_insights": {
        "primary_readers": "Entrepreneurs, content creators, marketing professionals",
        "experience_level": "Intermediate to advanced",
        "main_challenges": ["Consistent content creation", "LinkedIn growth", "Algorithm understanding"],
        "preferred_content": ["In-depth tutorials", "Real case studies", "Industry analysis"],
        "reading_behavior": ["Mobile-first", "Scannable content", "Actionable takeaways"]
    },
    "seo_strategy": {
        "target_keywords": {
            "primary": ["linkedin algorithm 2024", "linkedin content strategy", "linkedin growth tips"],
            "secondary": ["social media marketing", "content creation", "linkedin optimization"]
        },
        "current_rankings": {"linkedin algorithm": "position 15", "content strategy": "position 8"},
        "content_gaps": ["Video content strategy", "LinkedIn automation tools", "B2B content marketing"],
        "competitor_analysis": ["Neil Patel", "Gary Vaynerchuk", "Mari Smith"]
    }
}

# Create a NEW session
APP_NAME = "Blog Post Generator Agent"
USER_ID = "nu_blog_content_creation"
SESSION_ID = str(uuid.uuid4())
stateful_session = session_service_stateful.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID,
    state=initial_state,
)

print("📝 CREATED NEW BLOG POST GENERATOR SESSION:")
print(f"\tSession ID: {SESSION_ID}")
print(f"\tUser: {initial_state['user_name']}")
print(f"\tContent Focus: {', '.join(initial_state['content_strategy']['primary_topics'])}")
print(f"\tTarget Audience: {initial_state['audience_insights']['primary_readers']}")

# Create runner with the blog post generator agent
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service_stateful,
)

# Test blog post generation request
blog_request = types.Content(
    role="user", 
    parts=[types.Part(text="""
        Create a comprehensive blog post on the topic: "The Complete Guide to LinkedIn Algorithm Optimization in 2024"
        
        Content Requirements:
        - Target audience: Entrepreneurs, content creators, marketing professionals
        - Goal: Establish thought leadership while providing actionable value
        - Length: 2000-3000 words (comprehensive guide format)
        - Tone: Professional but approachable, data-driven with practical examples
        
        Key Topics to Cover:
        1. How the LinkedIn algorithm actually works (technical but accessible explanation)
        2. Recent algorithm updates and their impact on content visibility
        3. Step-by-step optimization strategies for different content types
        4. Common mistakes that hurt algorithm performance
        5. Advanced tactics used by top LinkedIn creators
        6. Measuring and tracking algorithm optimization success
        
        SEO Requirements:
        - Primary keyword: "LinkedIn algorithm optimization"
        - Target long-tail keywords: "how linkedin algorithm works 2024", "linkedin content strategy"
        - Focus on ranking for competitive LinkedIn marketing terms
        
        Engagement Goals:
        - Drive newsletter signups through valuable content upgrade
        - Encourage social sharing and comments
        - Position as the definitive guide on LinkedIn algorithm
        - Generate leads for LinkedIn optimization services
        
        Content Style:
        - Include real data and case studies where possible
        - Provide actionable steps readers can implement immediately
        - Use examples from successful LinkedIn creators
        - Include troubleshooting sections for common issues
        
        Please create a complete blog post structure with SEO optimization, engagement strategies, and conversion opportunities integrated throughout.
    """)]
)

print("\n📄 GENERATING COMPREHENSIVE BLOG POST...")
print("=" * 60)

for event in runner.run(
    user_id=USER_ID,
    session_id=SESSION_ID,
    new_message=blog_request,
):
    if event.is_final_response():
        if event.content and event.content.parts:
            print(f"📝 Blog Post Structure:\n{event.content.parts[0].text}")

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
print("🎯 Ready for comprehensive blog content creation and optimization!")