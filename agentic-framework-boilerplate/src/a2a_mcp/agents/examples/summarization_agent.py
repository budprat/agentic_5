# ABOUTME: Example summarization agent for text processing tasks
# ABOUTME: Demonstrates quality validation and text analysis patterns

"""
Summarization Agent Example

A simple agent that demonstrates text summarization and processing.
Shows how to implement quality validation for agent outputs.
"""

from typing import Dict, Any, AsyncIterable, Optional
from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase


class SummarizationAgent(StandardizedAgentBase):
    """
    Example agent that performs text summarization.
    
    Demonstrates:
    - Text processing with quality checks
    - Length validation
    - Structured output generation
    """
    
    def __init__(self):
        super().__init__(
            agent_name="summarization_agent",
            description="Text summarization and processing agent",
            instructions="""You are a summarization expert. Your task is to:
            1. Create concise summaries of provided text
            2. Preserve key information and main points
            3. Maintain clarity and readability
            4. Provide compression metrics""",
            quality_config={
                "domain": "GENERIC",
                "min_confidence_score": 0.8,
                "max_response_time_ms": 10000
            }
        )
    
    async def _execute_agent_logic(self, prompt: str) -> AsyncIterable[Dict[str, Any]]:
        """Execute summarization logic"""
        # Extract text to summarize
        if not prompt or len(prompt.strip()) < 50:
            yield {
                "is_task_complete": True,
                "require_user_input": True,
                "content": "Please provide text with at least 50 characters to summarize."
            }
            return
        
        text = prompt.strip()
        original_length = len(text.split())
        
        # Generate summary using LLM
        summary_prompt = f"""Summarize the following text concisely while preserving key information:

{text}

Provide:
1. A brief summary (max 3-5 sentences)
2. Key points as bullet items
3. Compression ratio"""
        
        # Process with quality validation
        result = await self._process_with_llm(summary_prompt)
        
        # Validate quality
        is_valid = await self._validate_with_quality_framework({
            "summary": result,
            "original_length": original_length,
            "confidence": 0.85
        })
        
        if is_valid:
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": result
            }
        else:
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": "Summary generated but did not meet quality thresholds. Please try with clearer text."
            }
    
    def get_agent_temperature(self) -> Optional[float]:
        """Medium temperature for balanced summarization"""
        return 0.5
    
    def get_response_mime_type(self) -> Optional[str]:
        return "text/plain"