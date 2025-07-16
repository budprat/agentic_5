#!/usr/bin/env python3
"""
Simple interactive chat with Google ADK agent
Just run and start chatting!
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API key
google_api_key = os.getenv('GOOGLE_API_KEY')
if not google_api_key:
    print("❌ Error: GOOGLE_API_KEY not found in environment")
    sys.exit(1)

os.environ['GOOGLE_API_KEY'] = google_api_key

# Import ADK components
from google.adk import Runner
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.genai import types


async def main():
    """Simple chat loop"""
    print("🤖 Google ADK Chat Assistant")
    print("="*50)
    print("Type 'exit' to quit, 'clear' to clear history")
    print("="*50)
    
    # Create a simple agent
    agent = Agent(
        name="assistant",
        model="gemini-2.0-flash",
        description="A helpful AI assistant",
        instruction="""You are a helpful, friendly, and knowledgeable AI assistant. 
        Provide clear, concise, and accurate responses.
        Be conversational and engaging while remaining professional.
        If you don't know something, say so honestly."""
    )
    
    # Create session service and runner
    session_service = InMemorySessionService()
    runner = Runner(
        agent=agent,
        app_name="chat_app",
        session_service=session_service
    )
    
    # Create session
    session = session_service.create_session(
        app_name="chat_app",
        user_id="user",
        session_id="chat_session"
    )
    
    print("\n💬 Chat started! I'm ready to help.\n")
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if user_input.lower() == 'exit':
                print("\n👋 Goodbye!")
                break
            elif user_input.lower() == 'clear':
                # Create new session to clear history
                session = session_service.create_session(
                    app_name="chat_app",
                    user_id="user",
                    session_id=f"chat_session_{os.urandom(4).hex()}"
                )
                print("\n🧹 History cleared!\n")
                continue
            elif not user_input:
                continue
            
            # Create message
            content = types.Content(role='user', parts=[types.Part(text=user_input)])
            
            # Run the agent
            print("\nAssistant: ", end="", flush=True)
            
            response_text = ""
            async for event in runner.run_async(
                user_id="user",
                session_id=session.id,
                new_message=content
            ):
                if event.is_final_response():
                    if event.content and event.content.parts:
                        response_text = '\n'.join([p.text for p in event.content.parts if p.text])
                        print(response_text)
            
            print()  # Add blank line for readability
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")


if __name__ == "__main__":
    asyncio.run(main())