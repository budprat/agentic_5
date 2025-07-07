"""Sentiment Seeker - Social Media Sentiment Analysis using BrightData."""

import os
import logging
import json
import re
import asyncio
import aiohttp
from collections.abc import AsyncIterable
from typing import Dict, Any, List
from datetime import datetime, timedelta
from dotenv import load_dotenv

from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import init_api_key
from a2a_mcp.common.supabase_client import SupabaseClient
from a2a_mcp.common.stock_mcp_client import StockMCPClient
from a2a_mcp.common.brightdata_cache import BrightDataCache, BrightDataParser
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
        load_dotenv()
        init_api_key()
        super().__init__(
            agent_name="Sentiment Seeker BrightData",
            description="Reddit sentiment analysis via BrightData API",
            content_types=['text', 'text/plain']
        )
        self.supabase = SupabaseClient()
        self.model = genai.Client()
        # BrightData API configuration
        self.brightdata_token = os.getenv('BRIGHTDATA_API_TOKEN')
        self.dataset_id = "gd_lvz8ah06191smkebj4"
        self.base_url = "https://api.brightdata.com/datasets/v3"
        # Initialize cache and parser
        self.cache = BrightDataCache()
        self.parser = BrightDataParser()
        self.stock_mcp = StockMCPClient()

    async def fetch_reddit_data(self, keyword: str) -> Dict[str, Any]:
        """Fetch Reddit data from BrightData API with caching."""
        try:
            # Check cache first
            cached_data = await self.cache.get(keyword)
            if cached_data:
                logger.info(f"Using cached data for {keyword}")
                return cached_data
            
            # Check if BrightData token is available
            if not self.brightdata_token:
                raise ValueError("BrightData API token not configured")
            # Prepare the request URL with parameters
            url = f"https://api.brightdata.com/datasets/v3/trigger?dataset_id={self.dataset_id}&include_errors=true&type=discover_new&discover_by=keyword"
            
            headers = {
                "Authorization": f"Bearer {self.brightdata_token}",
                "Content-Type": "application/json"
            }
            
            # Search data format matching the curl example with limited posts
            search_data = [
                {"keyword": keyword, "date": "Today", "sort_by": "Hot", "num_of_posts": 10}
            ]
            
            logger.info(f"Fetching Reddit data for {keyword} from BrightData...")
            logger.info(f"Request URL: {url}")
            logger.info(f"Request data: {search_data}")
            
            timeout = aiohttp.ClientTimeout(total=60)  # 1 minute timeout
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, headers=headers, json=search_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"BrightData request successful: {data}")
                        
                        # Check if we got a snapshot ID to poll for results
                        if 'snapshot_id' in data:
                            # Poll for results - BrightData needs time to process
                            await asyncio.sleep(5)  # Give BrightData time to start processing
                            results = await self.get_brightdata_results(data['snapshot_id'])
                            
                            # Parse and cache the results
                            if results and 'error' not in results:
                                parsed_results = self.parser.parse_reddit_posts(results)
                                await self.cache.set(keyword, parsed_results)
                                return parsed_results
                            return results
                        return data
                    else:
                        error_text = await response.text()
                        logger.error(f"BrightData API error: {response.status} - {error_text}")
                        return {"error": f"API error: {response.status}"}
                        
        except asyncio.TimeoutError:
            logger.error(f"BrightData API timeout for {keyword}")
            return {"error": "BrightData API timeout", "posts": []}
        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching Reddit data: {e}")
            return {"error": f"Network error: {str(e)}", "posts": []}
        except Exception as e:
            logger.error(f"Error fetching Reddit data: {e}")
            return {"error": str(e), "posts": []}

    async def get_brightdata_results(self, snapshot_id: str) -> Dict[str, Any]:
        """Get results from BrightData snapshot."""
        try:
            url = f"{self.base_url}/snapshot/{snapshot_id}"
            headers = {"Authorization": f"Bearer {self.brightdata_token}"}
            
            # Poll for results with retries - BrightData typically takes 8-10 seconds
            max_retries = 15  # Increased to allow for proper polling
            retry_delay = 2  # seconds
            
            for attempt in range(max_retries):
                timeout = aiohttp.ClientTimeout(total=30)  # 30 second timeout per request
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(url, headers=headers) as response:
                        logger.info(f"Polling attempt {attempt + 1}: Status {response.status}")
                        
                        if response.status == 200:
                            # Try to get text response for NDJSON format
                            text_response = await response.text()
                            
                            # Check if it's NDJSON (multiple JSON objects separated by newlines)
                            if text_response.strip() and '\n' in text_response and text_response.startswith('{'):
                                logger.info(f"Got NDJSON response with {text_response.count(chr(10)) + 1} lines")
                                return text_response  # Return raw text for parser
                            else:
                                # Try to parse as regular JSON
                                try:
                                    data = json.loads(text_response)
                                    # Check if data is ready
                                    if data.get('status') == 'ready' or data.get('data'):
                                        logger.info(f"Results ready: {data}")
                                        return data
                                    else:
                                        logger.info(f"Results not ready yet: {data}")
                                except json.JSONDecodeError:
                                    # If it's not JSON, it might be NDJSON without newlines
                                    if text_response.strip().startswith('{'):
                                        logger.info("Got response, treating as NDJSON")
                                        return text_response
                                    logger.error("Failed to parse response as JSON")
                                    return {"error": "Invalid JSON response"}
                        elif response.status == 202:
                            # Still processing - this is normal for the first few attempts
                            logger.info("Results still processing (202)...")
                        else:
                            logger.error(f"Unexpected status: {response.status}")
                            return {"error": f"Failed to get results: {response.status}"}
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
            
            return {"error": "Results not ready after maximum retries"}
            
        except Exception as e:
            logger.error(f"Error getting BrightData results: {e}")
            return {"error": str(e)}

    async def fetch_stock_predictions(self, symbol: str) -> Dict[str, Any]:
        """Fetch ML predictions from stock predictions MCP."""
        try:
            logger.info(f"Fetching stock predictions for {symbol}")
            
            # Use the Stock MCP client
            prediction_data = await self.stock_mcp.get_prediction(symbol)
            
            if 'error' in prediction_data:
                logger.warning(f"Stock MCP error: {prediction_data['error']}")
                
            # Format for our use
            prediction = prediction_data.get('prediction', {})
            return {
                "ml_prediction": prediction.get('direction', 'neutral'),
                "confidence": prediction.get('confidence', 0.5),
                "predicted_move": f"{prediction.get('predicted_price_change_percent', 0):+.1f}%",
                "timeframe": prediction.get('timeframe', '1 week'),
                "factors": prediction.get('factors', []),
                "support": prediction.get('key_levels', {}).get('support'),
                "resistance": prediction.get('key_levels', {}).get('resistance'),
                "model_accuracy": prediction_data.get('model_info', {}).get('accuracy_score', 0)
            }
            
        except Exception as e:
            logger.error(f"Error fetching stock predictions: {e}")
            return {
                "ml_prediction": "unavailable",
                "confidence": 0,
                "error": str(e)
            }

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
            title = post.get('title') or ''
            text = post.get('text') or ''
            combined_text = (title + ' ' + text).lower()
            positive_count += sum(1 for word in positive_words if word in combined_text)
            negative_count += sum(1 for word in negative_words if word in combined_text)
        
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
                logger.error(f"BrightData error: {reddit_data['error']}")
                yield f"❌ Error fetching Reddit data: {reddit_data['error']}\n"
                return
            
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
                model=os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-001'),
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