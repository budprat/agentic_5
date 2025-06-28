"""News Hawk - Real-time Market News Analysis via Brave Search."""

import os
import logging
import json
from typing import AsyncIterable, Dict, Any, List
from datetime import datetime, timedelta
from dotenv import load_dotenv

from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import init_api_key
from a2a_mcp.common.supabase_client import SupabaseClient
from google import genai
import aiohttp

logger = logging.getLogger(__name__)

NEWS_ANALYSIS_PROMPT = """
You are News Hawk, a financial news analyst specializing in market-moving events.

Analyze the following news articles for {symbol}:

News Data:
{news_data}

Focus on:
1. Market-moving events and their potential impact
2. Company-specific developments (earnings, products, leadership)
3. Sector and industry trends affecting the stock
4. Regulatory or legal developments
5. Merger & acquisition activity
6. Analyst upgrades/downgrades

Provide a structured analysis with:
- Key headlines and their significance
- Bullish vs bearish news sentiment
- Potential short-term and long-term impacts
- News volume and media attention level
- Any conflicting narratives or uncertainties

Rate the overall news sentiment from -10 (very bearish) to +10 (very bullish).
"""

class NewsHawkAgent(BaseAgent):
    """Real-time market news analysis using Brave Search."""
    
    def __init__(self):
        load_dotenv()
        init_api_key()
        super().__init__(
            agent_name="News Hawk",
            description="Real-time market news analysis via Brave Search",
            content_types=['text', 'text/plain']
        )
        self.supabase = SupabaseClient()
        self.model = genai.Client()
        self.brave_api_key = os.getenv('BRAVE_API_KEY')
        
    async def search_news(self, query: str, count: int = 10) -> List[Dict[str, Any]]:
        """Search for news using Brave Search API."""
        try:
            if not self.brave_api_key:
                logger.error("Brave API key not found")
                return []
            
            url = "https://api.search.brave.com/res/v1/news/search"
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": self.brave_api_key
            }
            params = {
                "q": f"{query} stock news latest",
                "count": count,
                "freshness": "week"  # Get news from the last week
            }
            
            timeout = aiohttp.ClientTimeout(total=30)  # 30 second timeout
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get('results', [])
                        
                        news_items = []
                        for item in results:
                            news_items.append({
                                'title': item.get('title', ''),
                                'url': item.get('url', ''),
                                'description': item.get('description', ''),
                                'age': item.get('age', ''),
                                'source': item.get('meta_url', {}).get('hostname', '')
                            })
                        
                        return news_items
                    else:
                        logger.error(f"Brave API error: {response.status}")
                        return []
            
        except Exception as e:
            logger.error(f"Error searching news: {e}")
            return []
    
    async def analyze_news_sentiment(self, news_items: List[Dict[str, Any]], symbol: str) -> Dict[str, Any]:
        """Analyze news sentiment using Gemini."""
        try:
            # Format news for analysis
            news_text = "\n\n".join([
                f"Title: {item['title']}\nDescription: {item.get('description', 'N/A')}"
                for item in news_items
            ])
            
            # Generate analysis
            prompt = NEWS_ANALYSIS_PROMPT.format(
                symbol=symbol,
                news_data=news_text
            )
            
            response = await self.model.aio.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )
            
            return {
                'analysis': response.text,
                'news_count': len(news_items),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing news sentiment: {e}")
            return {
                'analysis': f"Error analyzing news: {str(e)}",
                'news_count': 0,
                'timestamp': datetime.now().isoformat()
            }
    
    async def save_news_analysis(self, symbol: str, analysis: Dict[str, Any], news_items: List[Dict[str, Any]]):
        """Save news analysis to Supabase."""
        try:
            # Extract sentiment score from analysis
            sentiment_score = 0
            analysis_text = analysis.get('analysis', '')
            
            # Simple extraction of sentiment score
            if 'sentiment' in analysis_text.lower():
                import re
                score_match = re.search(r'sentiment[:\s]+(-?\d+)', analysis_text.lower())
                if score_match:
                    sentiment_score = int(score_match.group(1))
            
            # Save to database
            data = {
                'symbol': symbol,
                'agent_name': 'News Hawk',
                'analysis_type': 'sentiment',  # Use 'sentiment' to match save_agent_analysis
                'sentiment_score': sentiment_score,
                'volume_score': len(news_items),  # Use news count as volume score
                'news_count': len(news_items),
                'key_insights': {
                    'headlines': [item['title'] for item in news_items[:5]],
                    'analysis': analysis_text[:1000],  # First 1000 chars
                    'sources': len(set(item.get('url', '').split('/')[2] for item in news_items if item.get('url')))
                },
                'raw_data': {
                    'news_items': news_items[:10],  # Save first 10 items
                    'full_analysis': analysis
                }
            }
            
            # Save using the generic agent analysis method
            await self.supabase.save_agent_analysis(data)
            logger.info(f"Saved news analysis for {symbol}")
            
        except Exception as e:
            logger.error(f"Error saving news analysis: {e}")
    
    async def stream(self, request: str) -> AsyncIterable[str]:
        """Stream news analysis for the requested symbol."""
        try:
            # Extract symbol from request
            symbol = self.extract_symbol(request)
            if not symbol:
                yield "Please specify a stock symbol to analyze."
                return
            
            yield f"🦅 News Hawk analyzing latest news for {symbol}...\n\n"
            
            # Search for recent news
            yield "📰 Searching for latest market news...\n"
            news_items = await self.search_news(f"{symbol} stock", count=15)
            
            if not news_items:
                yield "❌ No recent news found. The market might be quiet.\n"
                return
            
            yield f"✅ Found {len(news_items)} recent news articles\n\n"
            
            # Show top headlines
            yield "📋 Top Headlines:\n"
            for i, item in enumerate(news_items[:5], 1):
                yield f"{i}. {item['title']}\n"
            yield "\n"
            
            # Analyze sentiment
            yield "🔍 Analyzing news sentiment and impact...\n"
            analysis = await self.analyze_news_sentiment(news_items, symbol)
            
            # Stream the analysis
            yield "\n📊 News Analysis:\n"
            yield "=" * 50 + "\n"
            yield analysis['analysis']
            yield "\n" + "=" * 50 + "\n"
            
            # Save to database
            await self.save_news_analysis(symbol, analysis, news_items)
            
            yield f"\n✅ News analysis complete and saved to database"
            
        except Exception as e:
            logger.error(f"Error in news analysis stream: {e}")
            yield f"\n❌ Error: {str(e)}"
    
    def extract_symbol(self, request: str) -> str:
        """Extract stock symbol from request."""
        # Simple extraction - look for uppercase symbols
        import re
        matches = re.findall(r'\b[A-Z]{1,5}\b', request)
        
        # Filter out common words
        common_words = {'I', 'A', 'THE', 'AND', 'OR', 'FOR', 'TO', 'IN', 'OF', 'GET', 'NEWS'}
        symbols = [m for m in matches if m not in common_words]
        
        return symbols[0] if symbols else None
    
    async def invoke(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle structured requests."""
        symbol = request.get('symbol', '').upper()
        
        if not symbol:
            return {
                'error': 'No symbol provided',
                'message': 'Please provide a stock symbol to analyze'
            }
        
        # Search for news
        news_items = await self.search_news(f"{symbol} stock", count=10)
        
        if not news_items:
            return {
                'symbol': symbol,
                'news_count': 0,
                'message': 'No recent news found',
                'analysis': None
            }
        
        # Analyze news
        analysis = await self.analyze_news_sentiment(news_items, symbol)
        
        # Save to database
        await self.save_news_analysis(symbol, analysis, news_items)
        
        return {
            'symbol': symbol,
            'news_count': len(news_items),
            'top_headlines': [item['title'] for item in news_items[:5]],
            'analysis': analysis['analysis'],
            'timestamp': datetime.now().isoformat()
        }