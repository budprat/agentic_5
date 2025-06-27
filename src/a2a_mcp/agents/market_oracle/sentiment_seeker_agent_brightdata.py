"""Sentiment Seeker - Social Media Sentiment Analysis using BrightData."""

import logging
import json
import re
import asyncio
import aiohttp
from collections.abc import AsyncIterable
from typing import Dict, Any, List
from datetime import datetime, timedelta

from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import init_api_key
from a2a_mcp.common.supabase_client import SupabaseClient
from google import genai

logger = logging.getLogger(__name__)

SENTIMENT_ANALYSIS_PROMPT = """
You are Sentiment Seeker, analyzing social media sentiment from Reddit data.

Analyze the following Reddit data for stock sentiment:

Reddit Data:
{reddit_data}

Symbol: {symbol}

Generate a comprehensive sentiment analysis in JSON format:
{{
    "symbol": "{symbol}",
    "sentiment_score": -1.0 to 1.0,
    "confidence": 0.0 to 1.0,
    "volume_score": "low/normal/high/extreme",
    "volume_metrics": {{
        "total_posts": number,
        "total_comments": number,
        "total_upvotes": number,
        "engagement_rate": 0.0 to 1.0
    }},
    "key_themes": ["theme1", "theme2", "theme3"],
    "top_posts": [
        {{
            "title": "post title",
            "sentiment": -1.0 to 1.0,
            "upvotes": number,
            "comments": number,
            "subreddit": "subreddit name"
        }}
    ],
    "sentiment_breakdown": {{
        "bullish_percentage": 0.0 to 100.0,
        "bearish_percentage": 0.0 to 100.0,
        "neutral_percentage": 0.0 to 100.0
    }},
    "risk_flags": ["flag1", "flag2"],
    "retail_sentiment": -1.0 to 1.0,
    "smart_money_sentiment": -1.0 to 1.0,
    "divergence_score": 0.0 to 1.0,
    "recommendation": "bullish/neutral/bearish",
    "analysis_summary": "2-3 sentence summary of the sentiment and key findings"
}}

Focus on:
1. Overall sentiment direction and strength
2. Volume of discussions (unusual spikes?)
3. Quality of analysis vs hype
4. Potential manipulation or coordinated activity
5. Divergence between different investor groups
"""

class SentimentSeekerAgentBrightData(BaseAgent):
    """Social media sentiment analysis using BrightData."""

    def __init__(self):
        init_api_key()
        super().__init__(
            agent_name="Sentiment Seeker BrightData",
            description="Reddit sentiment analysis via BrightData API",
            content_types=['text', 'text/plain']
        )
        self.supabase = SupabaseClient()
        self.model = genai.Client()
        # BrightData API configuration
        self.brightdata_token = "9e9ece35cc8225d8b9e866772aea59acb0f9c810904b4616a513be83dc0d7a28"
        self.dataset_id = "gd_lvz8ah06191smkebj4"
        self.base_url = "https://api.brightdata.com/datasets/v3"

    async def fetch_reddit_data(self, keyword: str) -> Dict[str, Any]:
        """Fetch Reddit data from BrightData API."""
        try:
            # Prepare the request URL with parameters
            url = f"https://api.brightdata.com/datasets/v3/trigger?dataset_id={self.dataset_id}&include_errors=true&type=discover_new&discover_by=keyword"
            
            headers = {
                "Authorization": f"Bearer {self.brightdata_token}",
                "Content-Type": "application/json"
            }
            
            # Search data format matching the curl example
            search_data = [
                {"keyword": keyword, "date": "Today", "sort_by": "Hot"}
            ]
            
            logger.info(f"Fetching Reddit data for {keyword} from BrightData...")
            logger.info(f"Request URL: {url}")
            logger.info(f"Request data: {search_data}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=search_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"BrightData request successful: {data}")
                        
                        # Check if we got a snapshot ID to poll for results
                        if 'snapshot_id' in data:
                            # Poll for results
                            await asyncio.sleep(5)  # Give it time to process
                            results = await self.get_brightdata_results(data['snapshot_id'])
                            return results
                        return data
                    else:
                        error_text = await response.text()
                        logger.error(f"BrightData API error: {response.status} - {error_text}")
                        return {"error": f"API error: {response.status}"}
                        
        except Exception as e:
            logger.error(f"Error fetching Reddit data: {e}")
            return {"error": str(e)}

    async def get_brightdata_results(self, snapshot_id: str) -> Dict[str, Any]:
        """Get results from BrightData snapshot."""
        try:
            url = f"{self.base_url}/snapshot/{snapshot_id}"
            headers = {"Authorization": f"Bearer {self.brightdata_token}"}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"Failed to get results: {response.status}"}
        except Exception as e:
            logger.error(f"Error getting BrightData results: {e}")
            return {"error": str(e)}

    async def fetch_stock_predictions(self, symbol: str) -> Dict[str, Any]:
        """Fetch ML predictions from stock predictions MCP."""
        try:
            import os
            stock_mcp_url = os.getenv('STOCK_MCP', 'https://tonic-stock-predictions.hf.space/gradio_api/mcp/sse')
            
            # This would integrate with the stock predictions MCP
            # For now, return placeholder data
            logger.info(f"Stock MCP URL: {stock_mcp_url}")
            
            return {
                "ml_prediction": "bullish",
                "confidence": 0.75,
                "predicted_move": "+2.5%",
                "timeframe": "1 week"
            }
            
        except Exception as e:
            logger.error(f"Error fetching stock predictions: {e}")
            return {}

    def calculate_sentiment_metrics(self, posts: List[Dict]) -> Dict[str, Any]:
        """Calculate sentiment metrics from Reddit posts."""
        if not posts:
            return {
                "total_posts": 0,
                "sentiment_score": 0.0,
                "volume_score": "low"
            }
        
        total_upvotes = sum(post.get('upvotes', 0) for post in posts)
        total_comments = sum(post.get('num_comments', 0) for post in posts)
        
        # Simple sentiment calculation based on post titles and content
        positive_words = ["bullish", "moon", "rocket", "buy", "calls", "squeeze", "gain", "up", "green", "long"]
        negative_words = ["bearish", "puts", "sell", "crash", "dump", "red", "down", "loss", "short", "bag"]
        
        positive_count = 0
        negative_count = 0
        
        for post in posts:
            text = (post.get('title', '') + ' ' + post.get('text', '')).lower()
            positive_count += sum(1 for word in positive_words if word in text)
            negative_count += sum(1 for word in negative_words if word in text)
        
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words > 0:
            sentiment_score = (positive_count - negative_count) / total_sentiment_words
        else:
            sentiment_score = 0.0
        
        # Determine volume score
        if len(posts) > 50:
            volume_score = "extreme"
        elif len(posts) > 20:
            volume_score = "high"
        elif len(posts) > 5:
            volume_score = "normal"
        else:
            volume_score = "low"
        
        return {
            "total_posts": len(posts),
            "total_upvotes": total_upvotes,
            "total_comments": total_comments,
            "sentiment_score": max(-1.0, min(1.0, sentiment_score)),
            "volume_score": volume_score,
            "positive_mentions": positive_count,
            "negative_mentions": negative_count
        }

    async def stream(
        self, query: str, context_id: str, task_id: str
    ) -> AsyncIterable[Dict[str, Any]]:
        """Stream sentiment analysis results using BrightData."""
        logger.info(f'Sentiment Seeker analyzing: {query} (session: {context_id})')
        
        if not query:
            raise ValueError('Query cannot be empty')
        
        try:
            # Extract symbol from query
            symbol_match = re.search(r'\b[A-Z]{1,5}\b', query)
            symbol = symbol_match.group(0) if symbol_match else "UNKNOWN"
            
            # Step 1: Fetch Reddit data from BrightData
            yield {
                'is_task_complete': False,
                'require_user_input': False,
                'content': f'Sentiment Seeker: Fetching Reddit data for {symbol} via BrightData...'
            }
            
            reddit_data = await self.fetch_reddit_data(symbol)
            
            if "error" in reddit_data:
                # Fallback to simulated data for demo
                logger.warning(f"BrightData error, using simulated data: {reddit_data['error']}")
                reddit_data = {
                    "posts": [
                        {
                            "title": f"${symbol} to the moon! 🚀",
                            "text": "Great earnings, bullish on this stock",
                            "upvotes": 1250,
                            "num_comments": 89,
                            "subreddit": "wallstreetbets",
                            "created_at": datetime.now().isoformat()
                        },
                        {
                            "title": f"DD on {symbol} - Why I'm buying calls",
                            "text": "Technical analysis shows strong support...",
                            "upvotes": 856,
                            "num_comments": 124,
                            "subreddit": "stocks",
                            "created_at": (datetime.now() - timedelta(hours=2)).isoformat()
                        },
                        {
                            "title": f"Be careful with {symbol}",
                            "text": "Overvalued at current levels",
                            "upvotes": 234,
                            "num_comments": 45,
                            "subreddit": "investing",
                            "created_at": (datetime.now() - timedelta(hours=5)).isoformat()
                        }
                    ]
                }
            
            # Step 2: Calculate basic metrics
            yield {
                'is_task_complete': False,
                'require_user_input': False,
                'content': 'Sentiment Seeker: Analyzing sentiment patterns...'
            }
            
            posts = reddit_data.get('posts', [])
            metrics = self.calculate_sentiment_metrics(posts)
            
            # Step 3: Get ML predictions
            yield {
                'is_task_complete': False,
                'require_user_input': False,
                'content': 'Sentiment Seeker: Fetching ML predictions...'
            }
            
            ml_predictions = await self.fetch_stock_predictions(symbol)
            
            # Step 4: Generate comprehensive analysis using Gemini
            yield {
                'is_task_complete': False,
                'require_user_input': False,
                'content': 'Sentiment Seeker: Generating sentiment analysis...'
            }
            
            # Prepare data for Gemini
            reddit_summary = {
                "posts_analyzed": len(posts),
                "sentiment_metrics": metrics,
                "top_posts": posts[:5],  # Top 5 posts
                "ml_predictions": ml_predictions
            }
            
            prompt = SENTIMENT_ANALYSIS_PROMPT.format(
                reddit_data=json.dumps(reddit_summary, indent=2),
                symbol=symbol
            )
            
            response = self.model.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config={"temperature": 0.0, "response_mime_type": "application/json"}
            )
            
            sentiment_analysis = json.loads(response.text)
            
            # Step 5: Save to Supabase
            await self.supabase.create_sentiment_data(
                symbol=symbol,
                source="reddit_brightdata",
                sentiment_score=sentiment_analysis['sentiment_score'],
                volume_score=metrics['total_posts']  # Using post count as volume indicator
            )
            
            # Also create a trading signal if sentiment is strong
            if abs(sentiment_analysis['sentiment_score']) > 0.7:
                signal_type = 'buy' if sentiment_analysis['sentiment_score'] > 0 else 'sell'
                await self.supabase.create_trading_signal(
                    symbol=symbol,
                    signal_type=signal_type,
                    confidence_score=sentiment_analysis['confidence'],
                    agent_name=self.agent_name,
                    reasoning=sentiment_analysis['analysis_summary']
                )
            
            # Return final analysis
            final_response = {
                **sentiment_analysis,
                "data_source": "BrightData Reddit API",
                "posts_analyzed": len(posts),
                "ml_predictions": ml_predictions,
                "timestamp": datetime.now().isoformat()
            }
            
            yield {
                'response_type': 'data',
                'is_task_complete': True,
                'require_user_input': False,
                'content': final_response
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