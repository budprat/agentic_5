# ABOUTME: Mixin class to add memory capabilities to any A2A agent
# ABOUTME: Provides easy integration of session loading and context retrieval

import logging
from typing import Optional, Dict, Any
from .session_service import SessionService
from .vertex_ai_memory_bank import VertexAIMemoryBankService


logger = logging.getLogger(__name__)


class MemoryAwareAgentMixin:
    """Mixin to add memory capabilities to agents"""
    
    def initialize_memory(
        self,
        agent_engine_id: str,
        app_name: Optional[str] = None
    ):
        """Initialize memory services for the agent"""
        self.memory_service = VertexAIMemoryBankService(
            agent_engine_id=agent_engine_id
        )
        
        self.session_service = SessionService(
            memory_service=self.memory_service,
            app_name=app_name or self.agent_name
        )
        
        logger.info(f"Memory services initialized for {self.agent_name}")
        
    async def load_user_context(
        self,
        user_id: str,
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """Load user context from memory"""
        context = {
            "has_previous_sessions": False,
            "recent_sessions": [],
            "relevant_context": "",
            "user_preferences": {}
        }
        
        # Get recent sessions
        recent_sessions = await self.session_service.get_user_sessions(
            user_id=user_id,
            limit=5
        )
        
        if recent_sessions:
            context["has_previous_sessions"] = True
            context["recent_sessions"] = recent_sessions
            
            # Get relevant context if query provided
            if query:
                context["relevant_context"] = await self.session_service.get_conversation_context(
                    user_id=user_id,
                    query=query,
                    limit=3
                )
                
            # Extract user preferences from past sessions
            pref_results = await self.memory_service.search_memory(
                query="user preferences likes dislikes",
                user_id=user_id,
                limit=5
            )
            
            for memory in pref_results.memories:
                # Parse preferences from content
                if "prefer" in memory.content.lower():
                    context["user_preferences"]["extracted"] = memory.content[:200]
                    
        return context
        
    async def start_or_resume_session(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        load_context: bool = True
    ) -> tuple:
        """Start new or resume existing session with context"""
        
        # Load user context if requested
        context = {}
        if load_context:
            context = await self.load_user_context(user_id)
            
        # Get or create session
        session = await self.session_service.get_or_create_session(
            user_id=user_id,
            session_id=session_id
        )
        
        # Add context to session state
        session.state["loaded_context"] = context
        
        return session, context
        
    async def get_contextual_prompt(
        self,
        user_message: str,
        user_id: str
    ) -> str:
        """Build prompt with memory context"""
        
        # Get relevant context
        context = await self.session_service.get_conversation_context(
            user_id=user_id,
            query=user_message,
            limit=3
        )
        
        # Build enhanced prompt
        prompt_parts = []
        
        if context and "No previous relevant" not in context:
            prompt_parts.append("Based on our previous conversations:")
            prompt_parts.append(context)
            prompt_parts.append("\n---\n")
            
        prompt_parts.append(f"User message: {user_message}")
        
        return "\n".join(prompt_parts)
        
    async def save_current_session(self):
        """Save current session to memory"""
        if hasattr(self, 'current_session') and self.current_session:
            await self.session_service.save_session(self.current_session)
            logger.info(f"Session {self.current_session.id} saved to memory")