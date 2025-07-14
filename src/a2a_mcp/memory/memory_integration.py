# ABOUTME: Memory integration helpers for A2A framework agents  
# ABOUTME: Provides session management and memory lifecycle operations

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from .base import Session, Event, BaseMemoryService
from .vertex_ai_memory_bank import VertexAIMemoryBankService


logger = logging.getLogger(__name__)


class MemoryIntegration:
    """Helper class for integrating memory into A2A agents"""
    
    def __init__(
        self,
        memory_service: Optional[BaseMemoryService] = None,
        agent_engine_id: Optional[str] = None
    ):
        """Initialize memory integration
        
        Args:
            memory_service: Pre-configured memory service instance
            agent_engine_id: Agent Engine ID for Vertex AI Memory Bank
        """
        self.memory_service = memory_service
        
        # Create default Vertex AI Memory Bank if not provided
        if not self.memory_service and agent_engine_id:
            self.memory_service = VertexAIMemoryBankService(
                agent_engine_id=agent_engine_id
            )
            
    def create_session(
        self,
        session_id: str,
        app_name: str,
        user_id: str,
        initial_state: Optional[Dict[str, Any]] = None
    ) -> Session:
        """Create a new session for tracking conversation"""
        return Session(
            id=session_id,
            app_name=app_name,
            user_id=user_id,
            state=initial_state or {}
        )
        
    def add_user_message(self, session: Session, message: str) -> None:
        """Add user message event to session"""
        event = Event(
            type="user_message",
            content=message,
            metadata={"role": "user"}
        )
        session.events.append(event)
        session.updated_at = datetime.now()
        
    def add_agent_response(self, session: Session, response: str, agent_name: str) -> None:
        """Add agent response event to session"""
        event = Event(
            type="agent_response", 
            content=response,
            metadata={"role": "assistant", "agent_name": agent_name}
        )
        session.events.append(event)
        session.updated_at = datetime.now()
        
    def add_tool_call(
        self,
        session: Session,
        tool_name: str,
        parameters: Dict[str, Any],
        result: Any
    ) -> None:
        """Add tool call event to session"""
        event = Event(
            type="tool_call",
            content=result,
            metadata={
                "tool_name": tool_name,
                "parameters": parameters
            }
        )
        session.events.append(event)
        session.updated_at = datetime.now()
        
    def update_state(self, session: Session, key: str, value: Any) -> None:
        """Update session state"""
        session.state[key] = value
        session.updated_at = datetime.now()
        
        # Also record as state change event
        event = Event(
            type="state_change",
            content={key: value},
            metadata={"operation": "update"}
        )
        session.events.append(event)
        
    async def save_session_to_memory(self, session: Session) -> None:
        """Save completed session to long-term memory"""
        if not self.memory_service:
            logger.warning("No memory service configured, session not saved")
            return
            
        try:
            await self.memory_service.add_session_to_memory(session)
            logger.info(f"Session {session.id} saved to memory")
        except Exception as e:
            logger.error(f"Failed to save session to memory: {e}")
            
    async def search_memory(
        self,
        query: str,
        app_name: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 5
    ) -> str:
        """Search memory and return formatted results"""
        if not self.memory_service:
            return "Memory service not configured"
            
        try:
            response = await self.memory_service.search_memory(
                query=query,
                app_name=app_name,
                user_id=user_id,
                limit=limit
            )
            
            if not response.memories:
                return f"No relevant memories found for: {query}"
                
            # Format results
            results = [f"Found {len(response.memories)} relevant memories:\n"]
            
            for i, memory in enumerate(response.memories, 1):
                results.append(f"\n{i}. [Score: {memory.relevance_score:.2f}]")
                results.append(f"   From session: {memory.session_id}")
                results.append(f"   Time: {memory.timestamp}")
                results.append(f"   Content: {memory.content[:200]}...")
                
            return "\n".join(results)
            
        except Exception as e:
            logger.error(f"Memory search failed: {e}")
            return f"Error searching memory: {str(e)}"