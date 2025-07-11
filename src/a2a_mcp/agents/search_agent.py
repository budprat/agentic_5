# ABOUTME: Example SearchAgent implementation for the A2A MCP framework
# ABOUTME: Demonstrates web search and data retrieval capabilities

import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional

from a2a_mcp.core.agent import Agent, AgentCapability
from a2a_mcp.core.protocol import A2AMessage, MessageType, MessageStatus
from a2a_mcp.common.utils import logger, generate_id


class SearchAgent(Agent):
    """
    Example agent that performs web searches and retrieves information
    """
    
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            agent_type="search",
            capabilities={
                AgentCapability.SEARCH,
                AgentCapability.WEB_SCRAPING
            },
            metadata={
                "version": "1.0.0",
                "description": "Web search and information retrieval agent"
            }
        )
    
    async def process_request(self, message: A2AMessage) -> A2AMessage:
        """Process incoming search requests"""
        try:
            action = message.content.get("action")
            
            if action == "search":
                return await self._handle_search_request(message)
            elif action == "get_capabilities":
                return await self._handle_capability_query(message)
            else:
                return self._create_error_response(
                    message,
                    f"Unknown action: {action}"
                )
        
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return self._create_error_response(message, str(e))
    
    async def _handle_search_request(self, message: A2AMessage) -> A2AMessage:
        """Handle web search requests"""
        query = message.content.get("query")
        limit = message.content.get("limit", 10)
        
        if not query:
            return self._create_error_response(
                message,
                "Search query is required"
            )
        
        # Perform the search
        results = await self._perform_web_search(query, limit)
        
        # Create response
        return A2AMessage(
            message_id=generate_id("msg"),
            sender_id=self.agent_id,
            receiver_id=message.sender_id,
            message_type=MessageType.RESPONSE,
            content={
                "results": results,
                "query": query,
                "count": len(results)
            },
            correlation_id=message.message_id,
            status=MessageStatus.COMPLETED
        )
    
    async def _handle_capability_query(self, message: A2AMessage) -> A2AMessage:
        """Handle capability query requests"""
        capabilities = [cap.value for cap in self.capabilities]
        
        return A2AMessage(
            message_id=generate_id("msg"),
            sender_id=self.agent_id,
            receiver_id=message.sender_id,
            message_type=MessageType.RESPONSE,
            content={
                "capabilities": capabilities,
                "agent_type": self.agent_type,
                "metadata": self.metadata
            },
            correlation_id=message.message_id,
            status=MessageStatus.COMPLETED
        )
    
    async def _perform_web_search(
        self,
        query: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Perform actual web search (mock implementation)
        
        In a real implementation, this would integrate with search APIs
        like Google, Bing, or DuckDuckGo
        """
        # Simulate search delay
        await asyncio.sleep(0.5)
        
        # Mock search results
        results = []
        for i in range(min(limit, 5)):
            results.append({
                "title": f"Result {i+1} for '{query}'",
                "url": f"http://example.com/result{i+1}",
                "snippet": f"This is a snippet for search result {i+1} "
                          f"related to the query '{query}'...",
                "timestamp": datetime.now().isoformat()
            })
        
        return results
    
    def _create_error_response(
        self,
        original_message: A2AMessage,
        error: str
    ) -> A2AMessage:
        """Create an error response message"""
        return A2AMessage(
            message_id=generate_id("msg"),
            sender_id=self.agent_id,
            receiver_id=original_message.sender_id,
            message_type=MessageType.RESPONSE,
            content={"error": error},
            correlation_id=original_message.message_id,
            status=MessageStatus.FAILED
        )