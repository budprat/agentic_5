# ABOUTME: Example of A2A agent with Vertex AI Memory Bank integration
# ABOUTME: Shows how to add memory capabilities to agents

import os
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.memory import VertexAIMemoryBankService, Session, Event
from a2a_mcp.memory.memory_integration import MemoryIntegration


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryEnabledAgent(StandardizedAgentBase):
    """Example agent with memory capabilities"""
    
    def __init__(self, agent_engine_id: str):
        """Initialize agent with memory service
        
        Args:
            agent_engine_id: Vertex AI Agent Engine ID for Memory Bank
        """
        super().__init__(
            agent_name="MemoryEnabledAgent",
            description="An agent that remembers past conversations",
            instructions="""You are a helpful assistant with memory capabilities.
            You can remember information from past conversations and use it to provide
            better, more personalized responses. Always check your memory for relevant
            context before answering questions."""
        )
        
        # Initialize memory integration
        self.memory_integration = MemoryIntegration(
            agent_engine_id=agent_engine_id
        )
        
        # Track current session
        self.current_session = None
        
    async def initialize_session(self, user_id: str) -> Session:
        """Initialize a new conversation session"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session = self.memory_integration.create_session(
            session_id=session_id,
            app_name=self.agent_name,
            user_id=user_id,
            initial_state={
                "start_time": datetime.now().isoformat(),
                "agent_version": "1.0"
            }
        )
        
        logger.info(f"Initialized session: {session_id}")
        return self.current_session
        
    async def process_message(self, message: str, user_id: str) -> str:
        """Process user message with memory context
        
        Args:
            message: User's input message
            user_id: User identifier
            
        Returns:
            Agent's response
        """
        # Initialize session if needed
        if not self.current_session:
            await self.initialize_session(user_id)
            
        # Add user message to session
        self.memory_integration.add_user_message(self.current_session, message)
        
        # Search memory for relevant context
        memory_context = await self.memory_integration.search_memory(
            query=message,
            user_id=user_id,
            limit=3
        )
        
        # Build enhanced prompt with memory
        enhanced_prompt = f"""Based on the following memory context:
{memory_context}

Please respond to the user's message: {message}

If the memory contains relevant information, use it to provide a more personalized response."""

        # Process with your agent logic (simplified for example)
        response = await self._generate_response(enhanced_prompt)
        
        # Add response to session
        self.memory_integration.add_agent_response(
            self.current_session,
            response,
            self.agent_name
        )
        
        # Update any important state
        if "remember" in message.lower():
            self.memory_integration.update_state(
                self.current_session,
                "user_asked_to_remember",
                True
            )
            
        return response
        
    async def _generate_response(self, prompt: str) -> str:
        """Generate response using agent's capabilities"""
        # This would use your actual agent implementation
        # For example, using Google ADK/Gemini
        return f"I understand your request. Based on our past conversations, I can help you with that."
        
    async def end_conversation(self) -> None:
        """End conversation and save to memory"""
        if self.current_session:
            # Add ending metadata
            self.memory_integration.update_state(
                self.current_session,
                "end_time",
                datetime.now().isoformat()
            )
            
            # Save session to long-term memory
            await self.memory_integration.save_session_to_memory(
                self.current_session
            )
            
            logger.info(f"Conversation saved to memory: {self.current_session.id}")
            self.current_session = None


async def main():
    """Example usage of memory-enabled agent"""
    
    # Set up environment
    os.environ["GOOGLE_CLOUD_PROJECT"] = "your-project-id"
    os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
    
    # Agent Engine ID from Vertex AI
    agent_engine_id = "your-agent-engine-id"
    
    # Create agent
    agent = MemoryEnabledAgent(agent_engine_id)
    
    # Simulate conversation
    user_id = "user123"
    
    # First conversation
    response1 = await agent.process_message(
        "Hi, I'm planning a trip to Paris next month.",
        user_id
    )
    print(f"Agent: {response1}")
    
    response2 = await agent.process_message(
        "Please remember that I prefer boutique hotels over chain hotels.",
        user_id
    )
    print(f"Agent: {response2}")
    
    # End first conversation
    await agent.end_conversation()
    
    # Start new conversation (agent should remember previous info)
    response3 = await agent.process_message(
        "Can you help me find a hotel for my trip?",
        user_id
    )
    print(f"Agent: {response3}")
    # Agent should mention Paris and boutique hotels preference
    
    # End second conversation
    await agent.end_conversation()


if __name__ == "__main__":
    asyncio.run(main())