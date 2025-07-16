#!/usr/bin/env python3
"""
Interactive test script for Google ADK agents
Allows you to chat with different agent types interactively
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from typing import Optional

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
from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LlmAgent
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import BaseModel, Field


def print_menu():
    """Print the main menu"""
    print("\n" + "="*50)
    print("🤖 Google ADK Interactive Agent Tester")
    print("="*50)
    print("\nAvailable Agents:")
    print("1. Simple Chat Agent")
    print("2. Sequential Agent (Research + Writing)")
    print("3. Parallel Agent (Multiple perspectives)")
    print("4. Structured Output Agent (JSON responses)")
    print("5. Code Assistant Agent")
    print("6. Custom Agent (define your own)")
    print("0. Exit")
    print("-"*50)


async def chat_with_agent(agent, agent_name: str):
    """Interactive chat loop with an agent"""
    print(f"\n🚀 Starting chat with {agent_name}")
    print("Type 'exit' to return to menu, 'clear' to clear history")
    print("-"*50)
    
    # Create session service and runner
    session_service = InMemorySessionService()
    runner = Runner(
        agent=agent,
        app_name="interactive_test",
        session_service=session_service
    )
    
    # Create session
    session = session_service.create_session(
        app_name="interactive_test",
        user_id="interactive_user",
        session_id=f"session_{agent_name}"
    )
    
    while True:
        # Get user input
        user_input = input("\n👤 You: ").strip()
        
        if user_input.lower() == 'exit':
            print("👋 Returning to menu...")
            break
        elif user_input.lower() == 'clear':
            # Create new session to clear history
            session = session_service.create_session(
                app_name="interactive_test",
                user_id="interactive_user",
                session_id=f"session_{agent_name}_new"
            )
            print("🧹 History cleared!")
            continue
        elif not user_input:
            continue
        
        # Create message
        content = types.Content(role='user', parts=[types.Part(text=user_input)])
        
        # Run the agent
        print(f"\n🤖 {agent_name}: ", end="", flush=True)
        
        response_text = ""
        try:
            async for event in runner.run_async(
                user_id="interactive_user",
                session_id=session.id,
                new_message=content
            ):
                if event.is_final_response():
                    if event.content and event.content.parts:
                        response_text = '\n'.join([p.text for p in event.content.parts if p.text])
                        print(response_text)
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


def create_simple_agent():
    """Create a simple chat agent"""
    return Agent(
        name="simple_chat",
        model="gemini-2.0-flash",
        description="A helpful chat assistant",
        instruction="""You are a helpful, friendly assistant. 
        Keep your responses concise and engaging.
        Use emojis occasionally to make the conversation more friendly."""
    )


def create_sequential_agent():
    """Create a sequential agent with research and writing sub-agents"""
    research_agent = Agent(
        name="researcher",
        model="gemini-2.0-flash",
        description="Research specialist",
        instruction="""You are a research specialist. 
        When given a topic, provide key facts, insights, and relevant information.
        Be thorough but concise."""
    )
    
    writer_agent = Agent(
        name="writer",
        model="gemini-2.0-flash",
        description="Content writer",
        instruction="""You are a creative writer. 
        Take the research provided and craft it into engaging, well-structured content.
        Make it interesting and easy to read."""
    )
    
    return SequentialAgent(
        name="research_writer",
        sub_agents=[research_agent, writer_agent],
        description="Research and writing team"
    )


def create_parallel_agent():
    """Create a parallel agent with multiple perspectives"""
    optimist_agent = Agent(
        name="optimist",
        model="gemini-2.0-flash",
        description="Optimistic perspective",
        instruction="You see the positive side of things. Provide an optimistic viewpoint."
    )
    
    realist_agent = Agent(
        name="realist",
        model="gemini-2.0-flash",
        description="Realistic perspective",
        instruction="You provide balanced, practical perspectives based on facts."
    )
    
    critic_agent = Agent(
        name="critic",
        model="gemini-2.0-flash",
        description="Critical perspective",
        instruction="You analyze potential issues and challenges. Be constructive."
    )
    
    return ParallelAgent(
        name="perspective_team",
        sub_agents=[optimist_agent, realist_agent, critic_agent],
        description="Multi-perspective analysis team"
    )


def create_structured_agent():
    """Create an agent that returns structured JSON output"""
    
    class AnalysisResult(BaseModel):
        summary: str = Field(description="Brief summary of the topic")
        key_points: list[str] = Field(description="Main points to remember")
        pros: list[str] = Field(description="Positive aspects")
        cons: list[str] = Field(description="Negative aspects")
        recommendation: str = Field(description="Final recommendation")
    
    return LlmAgent(
        name="structured_analyst",
        model="gemini-2.0-flash",
        instruction="""You are an analytical assistant. 
        Analyze topics and provide structured insights.
        Always provide balanced analysis with pros and cons.""",
        output_schema=AnalysisResult,
        output_key="analysis"
    )


def create_code_agent():
    """Create a code assistant agent"""
    return Agent(
        name="code_assistant",
        model="gemini-2.0-flash",
        description="Programming assistant",
        instruction="""You are an expert programming assistant.
        Help with coding questions, debugging, and best practices.
        Provide code examples when relevant.
        Support multiple languages but specialize in Python."""
    )


async def create_custom_agent():
    """Allow user to create a custom agent"""
    print("\n🛠️  Create Your Custom Agent")
    print("-"*50)
    
    name = input("Agent name: ").strip() or "custom_agent"
    description = input("Agent description: ").strip() or "A custom agent"
    
    print("\nEnter agent instructions (press Enter twice to finish):")
    instruction_lines = []
    while True:
        line = input()
        if line == "":
            if instruction_lines and instruction_lines[-1] == "":
                break
            instruction_lines.append("")
        else:
            instruction_lines.append(line)
    
    instruction = "\n".join(instruction_lines[:-1]) if instruction_lines else "You are a helpful assistant."
    
    model = input("\nModel (default: gemini-2.0-flash): ").strip() or "gemini-2.0-flash"
    
    return Agent(
        name=name,
        model=model,
        description=description,
        instruction=instruction
    )


async def main():
    """Main interactive loop"""
    print("🔧 Initializing ADK Interactive Tester...")
    print(f"✅ Using Python: {sys.executable}")
    print("✅ GOOGLE_API_KEY loaded from .env")
    
    while True:
        print_menu()
        
        try:
            choice = input("\nSelect an option (0-6): ").strip()
            
            if choice == '0':
                print("\n👋 Goodbye!")
                break
            
            elif choice == '1':
                agent = create_simple_agent()
                await chat_with_agent(agent, "Simple Chat Agent")
            
            elif choice == '2':
                agent = create_sequential_agent()
                print("\n💡 Tip: This agent will research then write about your topic")
                await chat_with_agent(agent, "Sequential Agent")
            
            elif choice == '3':
                agent = create_parallel_agent()
                print("\n💡 Tip: This agent provides multiple perspectives on your topic")
                await chat_with_agent(agent, "Parallel Agent")
            
            elif choice == '4':
                agent = create_structured_agent()
                print("\n💡 Tip: This agent returns structured JSON analysis")
                await chat_with_agent(agent, "Structured Agent")
            
            elif choice == '5':
                agent = create_code_agent()
                print("\n💡 Tip: Ask coding questions or for help with programming")
                await chat_with_agent(agent, "Code Assistant")
            
            elif choice == '6':
                agent = await create_custom_agent()
                await chat_with_agent(agent, "Custom Agent")
            
            else:
                print("❌ Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Returning to menu...")
            continue
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Returning to menu...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")