"""Sentiment Seeker - Reddit and Social Media Sentiment Analysis Agent."""

import logging
import json
import re
from collections.abc import AsyncIterable
from typing import Dict, Any, List
from datetime import datetime, timedelta

from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import get_mcp_server_config, init_api_key
from a2a_mcp.common.agent_runner import AgentRunner
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams
from google.genai import types as genai_types

logger = logging.getLogger(__name__)

SENTIMENT_ANALYSIS_PROMPT = """
You are Sentiment Seeker, a specialized agent for analyzing social media sentiment around stocks and investments.

Your capabilities:
1. Monitor Reddit communities (WallStreetBets, stocks, investing, StockMarket)
2. Analyze sentiment from posts and comments
3. Track unusual volume spikes in discussions
4. Identify retail vs institutional sentiment divergence
5. Detect early meme stock movements

When analyzing a stock symbol, you should:
1. Search for recent discussions about the symbol
2. Calculate sentiment scores (-1.0 to +1.0)
3. Measure discussion volume relative to historical average
4. Identify key themes and concerns
5. Flag any coordinated activity or manipulation

Output Format (JSON):
{
    "symbol": "TICKER",
    "sentiment_score": -1.0 to 1.0,
    "confidence": 0.0 to 1.0,
    "volume_score": "low/normal/high/extreme",
    "volume_change": "percentage change vs 7-day average",
    "key_themes": ["theme1", "theme2"],
    "top_posts": [
        {
            "title": "post title",
            "sentiment": -1.0 to 1.0,
            "upvotes": number,
            "comments": number,
            "url": "reddit url"
        }
    ],
    "risk_flags": ["flag1", "flag2"],
    "retail_sentiment": -1.0 to 1.0,
    "smart_money_sentiment": -1.0 to 1.0,
    "divergence_score": 0.0 to 1.0,
    "recommendation": "bullish/neutral/bearish",
    "analysis_summary": "2-3 sentence summary"
}

Use the available MCP tools to search Reddit and analyze social media sentiment.
"""

class SentimentSeekerAgent(BaseAgent):
    """Agent specialized in social media sentiment analysis."""

    def __init__(self):
        init_api_key()
        super().__init__(
            agent_name="Sentiment Seeker",
            description="Reddit and social media sentiment analyzer",
            content_types=['text', 'text/plain']
        )
        logger.info(f'Initializing {self.agent_name}')
        self.agent = None
        self.runner = None
        self.sentiment_cache = {}
        self.volume_baseline = {}

    async def init_agent(self):
        """Initialize the agent with Reddit MCP tools."""
        logger.info(f'Initializing {self.agent_name} with MCP tools')
        
        config = get_mcp_server_config()
        logger.info(f'MCP Server url={config.url}')
        
        # Get tools from MCP server (Reddit, BrightData, etc.)
        tools = await MCPToolset(
            connection_params=SseConnectionParams(url=config.url)
        ).get_tools()
        
        for tool in tools:
            logger.info(f'Loaded tool: {tool.name}')
        
        # Configure generation settings
        generate_content_config = genai_types.GenerateContentConfig(
            temperature=0.0,
            response_mime_type="application/json"
        )
        
        self.agent = Agent(
            name=self.agent_name,
            instruction=SENTIMENT_ANALYSIS_PROMPT,
            model='gemini-2.0-flash',
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            generate_content_config=generate_content_config,
            tools=tools,
        )
        self.runner = AgentRunner()

    def calculate_sentiment_score(self, text: str) -> float:
        """Calculate sentiment score from text using simple heuristics."""
        # In production, would use a proper sentiment model
        positive_words = ["bullish", "moon", "rocket", "buy", "calls", "squeeze", "gain", "up", "green"]
        negative_words = ["bearish", "puts", "sell", "crash", "dump", "red", "down", "loss", "bag"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count + negative_count == 0:
            return 0.0
        
        score = (positive_count - negative_count) / (positive_count + negative_count)
        return max(-1.0, min(1.0, score))

    def detect_risk_flags(self, sentiment_data: Dict) -> List[str]:
        """Detect potential risks in sentiment data."""
        risk_flags = []
        
        # Check for extreme sentiment
        if abs(sentiment_data.get("sentiment_score", 0)) > 0.8:
            risk_flags.append("extreme_sentiment")
        
        # Check for unusual volume
        if sentiment_data.get("volume_score") == "extreme":
            risk_flags.append("unusual_volume_spike")
        
        # Check for sentiment divergence
        if sentiment_data.get("divergence_score", 0) > 0.7:
            risk_flags.append("sentiment_divergence")
        
        # Check for potential pump and dump
        if (sentiment_data.get("volume_score") == "extreme" and 
            sentiment_data.get("sentiment_score", 0) > 0.8):
            risk_flags.append("potential_pump_dump")
        
        return risk_flags

    def format_response(self, chunk: str) -> Dict:
        """Extract JSON from agent response."""
        patterns = [
            r'```json\s*(.*?)\s*```',
            r'```\n(.*?)\n```',
            r'{.*}',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, chunk, re.DOTALL)
            if match:
                content = match.group(1) if len(match.groups()) > 0 else match.group(0)
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse JSON: {content}")
        
        # If no JSON found, create a basic response
        return {
            "symbol": "UNKNOWN",
            "sentiment_score": 0.0,
            "confidence": 0.0,
            "error": "Failed to parse sentiment data"
        }

    async def stream(
        self, query: str, context_id: str, task_id: str
    ) -> AsyncIterable[Dict[str, Any]]:
        """Stream sentiment analysis results."""
        logger.info(f'Sentiment Seeker analyzing: {query} (session: {context_id})')
        
        if not query:
            raise ValueError('Query cannot be empty')
        
        if not self.agent:
            await self.init_agent()
        
        try:
            # Extract symbol from query
            symbol_match = re.search(r'\b[A-Z]{1,5}\b', query)
            symbol = symbol_match.group(0) if symbol_match else "UNKNOWN"
            
            yield {
                'is_task_complete': False,
                'require_user_input': False,
                'content': f'Sentiment Seeker: Analyzing social sentiment for {symbol}...'
            }
            
            # Run the agent to analyze sentiment
            async for chunk in self.runner.run_stream(
                self.agent, query, context_id
            ):
                logger.info(f'Received chunk: {chunk}')
                
                if isinstance(chunk, dict) and chunk.get('type') == 'final_result':
                    response = chunk['response']
                    sentiment_data = self.format_response(response)
                    
                    # Add risk flags
                    sentiment_data['risk_flags'] = self.detect_risk_flags(sentiment_data)
                    
                    # Cache the results
                    self.sentiment_cache[symbol] = {
                        'data': sentiment_data,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    yield {
                        'response_type': 'data',
                        'is_task_complete': True,
                        'require_user_input': False,
                        'content': sentiment_data
                    }
                else:
                    # Yield progress updates
                    yield {
                        'is_task_complete': False,
                        'require_user_input': False,
                        'content': 'Sentiment Seeker: Searching Reddit discussions...'
                    }
                    
        except Exception as e:
            logger.error(f'Error in sentiment analysis: {e}')
            yield {
                'response_type': 'text',
                'is_task_complete': True,
                'require_user_input': False,
                'content': f'Sentiment analysis error: {str(e)}'
            }

    async def invoke(self, query: str, session_id: str) -> dict:
        """Non-streaming invoke (not implemented)."""
        raise NotImplementedError('Please use the streaming interface')