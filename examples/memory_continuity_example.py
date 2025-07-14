# ABOUTME: Example showing how to maintain conversation continuity across sessions
# ABOUTME: Demonstrates loading previous sessions and using context

import os
import asyncio
from datetime import datetime

from a2a_mcp.memory import VertexAIMemoryBankService
from a2a_mcp.memory.session_service import SessionService
from a2a_mcp.memory.memory_integration import MemoryIntegration


async def main():
    """Example of conversation continuity with memory"""
    
    # Initialize memory service
    agent_engine_id = "your-agent-engine-id"
    memory_service = VertexAIMemoryBankService(
        agent_engine_id=agent_engine_id
    )
    
    # Create session service
    session_service = SessionService(
        memory_service=memory_service,
        app_name="ContinuityExample"
    )
    
    user_id = "user123"
    
    # SCENARIO 1: First conversation
    print("=== First Conversation ===")
    session1 = await session_service.create_session(user_id)
    
    # Add some conversation
    session1.events.append(Event(
        type="user_message",
        content="I'm planning a trip to Tokyo in March"
    ))
    session1.events.append(Event(
        type="agent_response",
        content="Tokyo in March is beautiful! Cherry blossoms typically bloom then."
    ))
    session1.events.append(Event(
        type="user_message",
        content="I love sushi and ramen. Any recommendations?"
    ))
    session1.events.append(Event(
        type="agent_response",
        content="For sushi, try Tsukiji Outer Market. For ramen, Ichiran is great!"
    ))
    
    # Save session
    await session_service.save_session(session1)
    print(f"Saved session: {session1.id}")
    
    # SCENARIO 2: New conversation - loading context
    print("\n=== New Conversation (Next Day) ===")
    
    # Get user's previous sessions
    previous_sessions = await session_service.get_user_sessions(user_id)
    print(f"Found {len(previous_sessions)} previous sessions")
    
    # Get relevant context for new query
    context = await session_service.get_conversation_context(
        user_id=user_id,
        query="travel plans restaurants",
        limit=3
    )
    print(f"\nContext retrieved:\n{context}")
    
    # Create new session with context
    session2 = await session_service.create_session(user_id)
    
    # Use context in conversation
    session2.events.append(Event(
        type="user_message",
        content="What was that sushi place you mentioned?"
    ))
    
    # Agent can use the context to answer
    print("\nAgent can now reference the previous conversation about Tsukiji!")
    
    # SCENARIO 3: Resume specific session
    print("\n=== Resume Specific Session ===")
    
    # Load specific session by ID
    loaded_session = await session_service.load_session_from_memory(session1.id)
    if loaded_session:
        print(f"Loaded session: {loaded_session.id}")
        print(f"Events in session: {len(loaded_session.events)}")
        print(f"Last message: {loaded_session.events[-1].content}")
    
    # SCENARIO 4: Intelligent context loading
    print("\n=== Intelligent Context Loading ===")
    
    # Helper function for agents
    async def get_user_context_for_query(query: str) -> str:
        """Get relevant context before processing user query"""
        
        # Search for relevant past conversations
        context = await session_service.get_conversation_context(
            user_id=user_id,
            query=query,
            limit=5
        )
        
        # Get user's recent sessions summary
        recent_sessions = await session_service.get_user_sessions(
            user_id=user_id,
            limit=3
        )
        
        summary = f"User has {len(recent_sessions)} recent conversations.\n"
        summary += f"Most recent was at {recent_sessions[0]['timestamp']}\n\n"
        summary += context
        
        return summary
    
    # Example usage
    user_query = "Do you remember what month I'm traveling?"
    context = await get_user_context_for_query(user_query)
    print(f"\nContext for '{user_query}':")
    print(context)


# Import Event class
from a2a_mcp.memory.base import Event


if __name__ == "__main__":
    # Set up environment
    os.environ["GOOGLE_CLOUD_PROJECT"] = "your-project-id"
    os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
    
    asyncio.run(main())