# ABOUTME: Example A2A agent with full memory continuity capabilities
# ABOUTME: Shows how to load sessions and maintain context across conversations

from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.memory.memory_aware_agent_mixin import MemoryAwareAgentMixin


class ContinuityAgent(StandardizedAgentBase, MemoryAwareAgentMixin):
    """Agent that remembers across sessions"""
    
    def __init__(self, agent_engine_id: str):
        # Initialize base agent
        super().__init__(
            agent_name="ContinuityAgent",
            description="An agent with conversation continuity",
            instructions="""You are a helpful assistant with perfect memory.
            You remember all past conversations and can reference them naturally.
            Always check context for relevant past interactions."""
        )
        
        # Initialize memory capabilities
        self.initialize_memory(agent_engine_id)
        
    async def process_with_continuity(
        self,
        message: str,
        user_id: str,
        session_id: Optional[str] = None
    ) -> str:
        """Process message with full conversation continuity"""
        
        # Start or resume session with context
        session, context = await self.start_or_resume_session(
            user_id=user_id,
            session_id=session_id,
            load_context=True
        )
        
        self.current_session = session
        
        # Log context info
        if context["has_previous_sessions"]:
            print(f"User has {len(context['recent_sessions'])} previous sessions")
            if context["user_preferences"]:
                print(f"Known preferences: {context['user_preferences']}")
                
        # Add user message to session
        from a2a_mcp.memory.base import Event
        session.events.append(Event(
            type="user_message",
            content=message
        ))
        
        # Get contextual prompt
        enhanced_prompt = await self.get_contextual_prompt(message, user_id)
        
        # Process with your agent logic
        # This would use your actual LLM/processing
        response = f"I understand. {enhanced_prompt}"
        
        # Add response to session
        session.events.append(Event(
            type="agent_response",
            content=response
        ))
        
        return response
        
    async def end_conversation(self):
        """Save session when conversation ends"""
        await self.save_current_session()


# Usage example
import asyncio
import os
from typing import Optional


async def demo_continuity():
    """Demonstrate conversation continuity"""
    
    agent_engine_id = "your-agent-engine-id"
    agent = ContinuityAgent(agent_engine_id)
    
    user_id = "demo_user"
    
    print("=== First Conversation ===")
    
    # First conversation
    response1 = await agent.process_with_continuity(
        "I'm John and I love Italian food",
        user_id
    )
    print(f"Agent: {response1}")
    
    response2 = await agent.process_with_continuity(
        "I'm also learning Python",
        user_id
    )
    print(f"Agent: {response2}")
    
    # Save conversation
    await agent.end_conversation()
    
    print("\n=== New Conversation (Later) ===")
    
    # New conversation - agent should remember
    response3 = await agent.process_with_continuity(
        "Do you remember my name?",
        user_id
    )
    print(f"Agent: {response3}")
    # Should reference "John" from previous conversation
    
    response4 = await agent.process_with_continuity(
        "What kind of food do I like?",
        user_id
    )
    print(f"Agent: {response4}")
    # Should reference "Italian food" from previous conversation
    
    await agent.end_conversation()


if __name__ == "__main__":
    os.environ["GOOGLE_CLOUD_PROJECT"] = "your-project-id"
    os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
    
    asyncio.run(demo_continuity())