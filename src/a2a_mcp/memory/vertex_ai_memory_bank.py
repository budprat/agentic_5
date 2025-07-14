# ABOUTME: Vertex AI Memory Bank implementation for persistent agent memory
# ABOUTME: Integrates with Google Cloud Agent Engine for managed memory service

import os
import logging
from typing import List, Optional
from google.auth import default
from google.cloud import aiplatform_v1beta1
from google.cloud.aiplatform_v1beta1 import Agent, Memory

from .base import BaseMemoryService, Session, SearchMemoryResponse, MemoryResult


logger = logging.getLogger(__name__)


class VertexAIMemoryBankService(BaseMemoryService):
    """Memory service using Vertex AI Memory Bank in Agent Engine"""
    
    def __init__(
        self,
        project: Optional[str] = None,
        location: Optional[str] = None,
        agent_engine_id: Optional[str] = None
    ):
        """Initialize Vertex AI Memory Bank Service
        
        Args:
            project: GCP project ID (defaults to env var)
            location: GCP location (defaults to env var) 
            agent_engine_id: Agent Engine ID for Memory Bank
        """
        self.project = project or os.environ.get("GOOGLE_CLOUD_PROJECT")
        self.location = location or os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        self.agent_engine_id = agent_engine_id
        
        if not self.project:
            raise ValueError(
                "Project ID must be provided or set via GOOGLE_CLOUD_PROJECT env var"
            )
            
        if not self.agent_engine_id:
            raise ValueError("agent_engine_id is required for Memory Bank service")
            
        # Initialize the agent client
        self.agent_client = aiplatform_v1beta1.AgentServiceClient()
        self.agent_name = f"projects/{self.project}/locations/{self.location}/agents/{self.agent_engine_id}"
        
        logger.info(
            f"Initialized VertexAI Memory Bank with agent: {self.agent_name}"
        )
        
    async def add_session_to_memory(self, session: Session) -> None:
        """Add session content to Vertex AI Memory Bank
        
        Args:
            session: Session to ingest into memory
        """
        try:
            # Extract conversation content
            conversation_content = self.extract_conversation_content(session)
            
            if not conversation_content.strip():
                logger.warning(f"Session {session.id} has no content to add to memory")
                return
                
            # Extract metadata
            metadata = self.extract_session_metadata(session)
            
            # Create memory entry
            memory = Memory(
                content=conversation_content,
                metadata=metadata
            )
            
            # Add to Memory Bank
            request = aiplatform_v1beta1.AddMemoryRequest(
                parent=self.agent_name,
                memory=memory
            )
            
            response = self.agent_client.add_memory(request=request)
            
            logger.info(
                f"Added session {session.id} to Memory Bank: {response.name}"
            )
            
        except Exception as e:
            logger.error(f"Error adding session to memory: {e}")
            raise
            
    async def search_memory(
        self,
        query: str,
        app_name: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 10
    ) -> SearchMemoryResponse:
        """Search Memory Bank for relevant memories
        
        Args:
            query: Search query text
            app_name: Optional filter by app name
            user_id: Optional filter by user ID  
            limit: Maximum number of results
            
        Returns:
            SearchMemoryResponse with matching memories
        """
        try:
            # Build search request
            request = aiplatform_v1beta1.SearchMemoryRequest(
                parent=self.agent_name,
                query=query,
                page_size=limit
            )
            
            # Add filters if provided
            filters = []
            if app_name:
                filters.append(f"metadata.app_name = '{app_name}'")
            if user_id:
                filters.append(f"metadata.user_id = '{user_id}'")
                
            if filters:
                request.filter = " AND ".join(filters)
                
            # Execute search
            response = self.agent_client.search_memory(request=request)
            
            # Convert results
            memories = []
            for result in response.memories:
                memory_result = MemoryResult(
                    session_id=result.metadata.get("session_id", "unknown"),
                    content=result.content,
                    relevance_score=result.score,
                    timestamp=result.create_time,
                    metadata=dict(result.metadata)
                )
                memories.append(memory_result)
                
            return SearchMemoryResponse(
                memories=memories,
                total_count=len(memories),
                query=query
            )
            
        except Exception as e:
            logger.error(f"Error searching memory: {e}")
            # Return empty results on error
            return SearchMemoryResponse(
                memories=[],
                total_count=0,
                query=query
            )
            
    def _convert_state_to_metadata(self, state: dict) -> dict:
        """Convert session state to Memory Bank metadata format
        
        Memory Bank metadata must be flat key-value pairs
        """
        metadata = {}
        
        for key, value in state.items():
            # Convert complex values to strings
            if isinstance(value, (str, int, float, bool)):
                metadata[f"state.{key}"] = str(value)
            elif isinstance(value, (list, dict)):
                # Serialize complex types
                import json
                metadata[f"state.{key}"] = json.dumps(value)[:500]  # Limit length
                
        return metadata