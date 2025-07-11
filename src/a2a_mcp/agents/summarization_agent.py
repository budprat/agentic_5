# ABOUTME: Example SummarizationAgent implementation for the A2A MCP framework
# ABOUTME: Demonstrates text processing and summarization capabilities

import asyncio
from typing import Dict, Any, Optional

from a2a_mcp.core.agent import Agent, AgentCapability
from a2a_mcp.core.protocol import A2AMessage, MessageType, MessageStatus
from a2a_mcp.common.utils import logger, generate_id


class SummarizationAgent(Agent):
    """
    Example agent that performs text summarization
    """
    
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            agent_type="summarization",
            capabilities={
                AgentCapability.TEXT_PROCESSING,
                AgentCapability.SUMMARIZATION
            },
            metadata={
                "version": "1.0.0",
                "description": "Text summarization and processing agent"
            }
        )
    
    async def process_request(self, message: A2AMessage) -> A2AMessage:
        """Process incoming summarization requests"""
        try:
            action = message.content.get("action")
            
            if action == "summarize":
                return await self._handle_summarize_request(message)
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
    
    async def _handle_summarize_request(self, message: A2AMessage) -> A2AMessage:
        """Handle text summarization requests"""
        text = message.content.get("text")
        max_length = message.content.get("max_length", 100)
        
        if not text:
            return self._create_error_response(
                message,
                "Text field is required for summarization"
            )
        
        # Perform summarization
        summary = await self._summarize_text(text, max_length)
        
        # Calculate metrics
        original_length = len(text.split())
        summary_length = len(summary.split())
        compression_ratio = original_length / summary_length if summary_length > 0 else 0
        
        # Create response
        return A2AMessage(
            message_id=generate_id("msg"),
            sender_id=self.agent_id,
            receiver_id=message.sender_id,
            message_type=MessageType.RESPONSE,
            content={
                "summary": summary,
                "metrics": {
                    "original_length": original_length,
                    "summary_length": summary_length,
                    "compression_ratio": compression_ratio
                }
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
    
    async def _summarize_text(self, text: str, max_length: int) -> str:
        """
        Perform text summarization (mock implementation)
        
        In a real implementation, this would use NLP models like
        BERT, GPT, or specialized summarization models
        """
        # Simulate processing delay
        await asyncio.sleep(0.3)
        
        # Simple mock summarization
        words = text.split()
        
        if len(words) <= max_length:
            return text
        
        # Take first and last portions of text
        start_words = max_length // 2
        end_words = max_length - start_words
        
        summary_parts = []
        if start_words > 0:
            summary_parts.extend(words[:start_words])
        if end_words > 0:
            summary_parts.append("...")
            summary_parts.extend(words[-end_words:])
        
        return " ".join(summary_parts)
    
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