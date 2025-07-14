# ABOUTME: Session service for managing conversation sessions with memory
# ABOUTME: Provides session persistence and retrieval using Vertex AI Memory Bank

import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from .base import Session, Event, BaseMemoryService
from .vertex_ai_memory_bank import VertexAIMemoryBankService


logger = logging.getLogger(__name__)


class SessionService:
    """Service for managing sessions with memory persistence"""
    
    def __init__(
        self,
        memory_service: BaseMemoryService,
        app_name: str
    ):
        self.memory_service = memory_service
        self.app_name = app_name
        self._active_sessions: Dict[str, Session] = {}
        
    async def create_session(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        initial_state: Optional[Dict[str, Any]] = None
    ) -> Session:
        """Create a new session"""
        if not session_id:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}"
            
        session = Session(
            id=session_id,
            app_name=self.app_name,
            user_id=user_id,
            state=initial_state or {}
        )
        
        self._active_sessions[session_id] = session
        logger.info(f"Created session: {session_id}")
        
        return session
        
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get active session by ID"""
        return self._active_sessions.get(session_id)
        
    async def get_or_create_session(
        self,
        user_id: str,
        session_id: Optional[str] = None
    ) -> Session:
        """Get existing session or create new one"""
        if session_id and session_id in self._active_sessions:
            return self._active_sessions[session_id]
            
        # Try to load from memory if session_id provided
        if session_id:
            loaded_session = await self.load_session_from_memory(session_id)
            if loaded_session:
                self._active_sessions[session_id] = loaded_session
                return loaded_session
                
        # Create new session
        return await self.create_session(user_id, session_id)
        
    async def load_session_from_memory(
        self,
        session_id: str
    ) -> Optional[Session]:
        """Load a session from memory bank"""
        try:
            # Search for specific session
            results = await self.memory_service.search_memory(
                query=f"session_id:{session_id}",
                app_name=self.app_name,
                limit=1
            )
            
            if results.memories:
                memory = results.memories[0]
                
                # Reconstruct session from memory metadata
                if "session_data" in memory.metadata:
                    session_data = json.loads(memory.metadata["session_data"])
                    
                    session = Session(
                        id=session_id,
                        app_name=self.app_name,
                        user_id=memory.metadata.get("user_id", "unknown"),
                        state=session_data.get("state", {}),
                        created_at=datetime.fromisoformat(session_data.get("created_at")),
                        updated_at=datetime.fromisoformat(session_data.get("updated_at"))
                    )
                    
                    # Reconstruct events
                    for event_data in session_data.get("events", []):
                        event = Event(
                            type=event_data["type"],
                            content=event_data["content"],
                            timestamp=datetime.fromisoformat(event_data["timestamp"]),
                            metadata=event_data.get("metadata", {})
                        )
                        session.events.append(event)
                        
                    logger.info(f"Loaded session from memory: {session_id}")
                    return session
                    
        except Exception as e:
            logger.error(f"Failed to load session from memory: {e}")
            
        return None
        
    async def get_user_sessions(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent sessions for a user"""
        results = await self.memory_service.search_memory(
            query=f"user sessions",
            app_name=self.app_name,
            user_id=user_id,
            limit=limit
        )
        
        sessions = []
        for memory in results.memories:
            sessions.append({
                "session_id": memory.metadata.get("session_id"),
                "timestamp": memory.timestamp,
                "summary": memory.content[:200] + "...",
                "event_count": memory.metadata.get("event_count", 0)
            })
            
        return sessions
        
    async def save_session(self, session: Session) -> None:
        """Save session to memory"""
        # Add session metadata for easier retrieval
        session_metadata = session.to_dict()
        
        # Store the full session data in metadata
        enhanced_session = Session(
            id=session.id,
            app_name=session.app_name,
            user_id=session.user_id,
            events=session.events,
            state=session.state,
            created_at=session.created_at,
            updated_at=session.updated_at
        )
        
        # Add metadata for search
        for event in enhanced_session.events:
            if "session_data" not in event.metadata:
                event.metadata["session_data"] = json.dumps(session_metadata)
                break
        else:
            # Add as new event if no suitable event found
            metadata_event = Event(
                type="session_metadata",
                content="Session metadata for retrieval",
                metadata={"session_data": json.dumps(session_metadata)}
            )
            enhanced_session.events.append(metadata_event)
            
        await self.memory_service.add_session_to_memory(enhanced_session)
        
        # Remove from active sessions
        if session.id in self._active_sessions:
            del self._active_sessions[session.id]
            
        logger.info(f"Saved session to memory: {session.id}")
        
    async def get_conversation_context(
        self,
        user_id: str,
        query: str,
        limit: int = 5
    ) -> str:
        """Get relevant conversation context for user"""
        results = await self.memory_service.search_memory(
            query=query,
            app_name=self.app_name,
            user_id=user_id,
            limit=limit
        )
        
        if not results.memories:
            return "No previous relevant conversations found."
            
        context_parts = ["Previous relevant conversations:\n"]
        
        for i, memory in enumerate(results.memories, 1):
            context_parts.append(f"\n{i}. Session: {memory.metadata.get('session_id', 'unknown')}")
            context_parts.append(f"   Time: {memory.timestamp}")
            context_parts.append(f"   Relevance: {memory.relevance_score:.2f}")
            context_parts.append(f"   Context: {memory.content[:300]}...")
            
        return "\n".join(context_parts)