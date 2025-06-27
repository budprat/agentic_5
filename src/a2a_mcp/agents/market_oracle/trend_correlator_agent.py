"""Trend Correlator - Google Trends Analysis Agent."""

import logging
import json
from collections.abc import AsyncIterable
from typing import Dict, Any, List
from datetime import datetime, timedelta
import random

from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import init_api_key
from a2a_mcp.common.supabase_client import SupabaseClient
from google import genai

logger = logging.getLogger(__name__)

TREND_ANALYSIS_PROMPT = """
You are Trend Correlator, an AI specialist in analyzing search trends and their correlation with market movements.

Analyze the following trend data and market information:

Symbol: {symbol}
Company/Product: {company_info}
Search Trends Data: {trends_data}
Historical Correlations: {historical_correlations}
Market Context: {market_context}

Generate a comprehensive trend analysis in JSON format:
{{
    "trend_score": 0-100,
    "trend_direction": "increasing/decreasing/stable",
    "correlation_strength": 0.0-1.0,
    "lead_lag_analysis": {{
        "trend_leads_price": true/false,
        "lead_time_days": "number of days trends lead price",
        "confidence": 0.0-1.0
    }},
    "key_search_terms": [
        {{"term": "search term", "volume": "relative volume", "growth_rate": "% change"}}
    ],
    "sentiment_indicators": {{
        "product_interest": "high/medium/low",
        "brand_sentiment": "positive/neutral/negative",
        "competitor_comparison": "gaining/losing market interest"
    }},
    "predictive_signals": {{
        "short_term_outlook": "bullish/bearish/neutral",
        "trend_momentum": "accelerating/decelerating/stable",
        "breakout_probability": 0.0-1.0
    }},
    "correlated_events": [
        {{"event": "description", "impact": "high/medium/low", "date": "YYYY-MM-DD"}}
    ],
    "investment_implications": "Detailed analysis of what trends mean for investment",
    "confidence_level": 0.0-1.0
}}
"""

class TrendCorrelatorAgent(BaseAgent):
    """Google Trends analysis agent with Supabase integration."""

    def __init__(self):
        init_api_key()
        super().__init__(
            agent_name="Trend Correlator",
            description="Search trend analysis with Supabase integration",
            content_types=["text", "text/plain"],
        )
        self.supabase = SupabaseClient()
        self.model = genai.Client()

    async def get_simulated_trends_data(self, symbol: str, 
                                      search_terms: List[str]) -> Dict[str, Any]:
        """Simulate Google Trends data for demo purposes."""
        # In production, this would use actual Google Trends API
        trends_data = {}
        
        for term in search_terms:
            # Generate realistic trend data
            base_volume = random.randint(40, 80)
            trend_points = []
            
            for i in range(30):  # 30 days of data
                # Add some realistic variation
                noise = random.randint(-10, 15)
                growth = i * 0.5 if random.random() > 0.5 else -i * 0.3
                value = min(100, max(0, base_volume + noise + growth))
                
                trend_points.append({
                    "date": (datetime.now() - timedelta(days=30-i)).strftime("%Y-%m-%d"),
                    "value": value
                })
            
            # Calculate growth rate
            start_avg = sum(p['value'] for p in trend_points[:7]) / 7
            end_avg = sum(p['value'] for p in trend_points[-7:]) / 7
            growth_rate = ((end_avg - start_avg) / start_avg) * 100 if start_avg > 0 else 0
            
            trends_data[term] = {
                "data_points": trend_points,
                "current_volume": trend_points[-1]['value'],
                "growth_rate": round(growth_rate, 2),
                "peak_volume": max(p['value'] for p in trend_points),
                "average_volume": sum(p['value'] for p in trend_points) / len(trend_points)
            }
        
        return trends_data

    async def get_historical_correlations(self, symbol: str) -> List[Dict[str, Any]]:
        """Get historical trend correlations from Supabase."""
        try:
            client = self.supabase.get_client()
            
            # Get market trends data
            trends_response = client.table('market_trends').select("*").eq(
                'symbol', symbol
            ).order('timestamp', desc=True).limit(20).execute()
            
            if trends_response.data:
                return trends_response.data
            
            return []
            
        except Exception as e:
            logger.error(f"Error fetching historical correlations: {e}")
            return []

    async def calculate_correlation(self, trends_data: Dict[str, Any], 
                                  price_movements: List[float]) -> float:
        """Calculate correlation between trends and price movements."""
        # Simplified correlation calculation
        # In production, use proper statistical methods
        
        if not trends_data or not price_movements:
            return 0.0
        
        # Get average trend growth
        avg_growth = sum(t.get('growth_rate', 0) for t in trends_data.values()) / len(trends_data)
        
        # Simulate price growth (in production, use actual price data)
        price_growth = 5.0 if avg_growth > 10 else -3.0 if avg_growth < -10 else 1.0
        
        # Calculate correlation coefficient (simplified)
        if avg_growth > 0 and price_growth > 0:
            correlation = min(0.9, 0.5 + (avg_growth / 100))
        elif avg_growth < 0 and price_growth < 0:
            correlation = min(0.9, 0.5 + abs(avg_growth / 100))
        else:
            correlation = max(0.1, 0.3 - abs(avg_growth / 100))
        
        return round(correlation, 3)

    async def stream(
        self, query: str, context_id: str, task_id: str
    ) -> AsyncIterable[Dict[str, Any]]:
        """Execute trend analysis workflow with Supabase integration."""
        logger.info(f"Trend Correlator analyzing: {query}")
        
        # Extract symbol and company info from query
        import re
        symbol_match = re.search(r'\b[A-Z]{1,5}\b', query)
        symbol = symbol_match.group(0) if symbol_match else "AAPL"
        
        # Map symbols to company names for search terms
        company_map = {
            "AAPL": {"name": "Apple", "products": ["iPhone", "MacBook", "Apple Watch"]},
            "TSLA": {"name": "Tesla", "products": ["Model 3", "Model Y", "Cybertruck"]},
            "GOOGL": {"name": "Google", "products": ["Google Search", "Android", "YouTube"]},
            "MSFT": {"name": "Microsoft", "products": ["Windows", "Office", "Azure"]},
            "AMZN": {"name": "Amazon", "products": ["Prime", "AWS", "Alexa"]}
        }
        
        company_info = company_map.get(symbol, {"name": symbol, "products": [symbol]})
        
        try:
            # Step 1: Generate search terms
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": f"Trend Correlator: Generating search terms for {symbol}..."
            }
            
            search_terms = [
                company_info["name"],
                f"{company_info['name']} stock",
                f"buy {company_info['name']}",
                f"{company_info['name']} news"
            ] + company_info["products"][:2]
            
            # Step 2: Fetch trends data
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Trend Correlator: Analyzing Google Trends data..."
            }
            
            trends_data = await self.get_simulated_trends_data(symbol, search_terms)
            
            # Step 3: Get historical correlations from Supabase
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Trend Correlator: Loading historical correlations..."
            }
            
            historical_correlations = await self.get_historical_correlations(symbol)
            
            # Step 4: Calculate correlation metrics
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Trend Correlator: Calculating trend-price correlations..."
            }
            
            # Simulate price movements (in production, get from market data)
            price_movements = [random.uniform(-2, 3) for _ in range(30)]
            correlation_coefficient = await self.calculate_correlation(trends_data, price_movements)
            
            # Step 5: Generate comprehensive analysis
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Trend Correlator: Generating trend analysis report..."
            }
            
            # Prepare data for Gemini analysis
            market_context = {
                "current_price": 150.00 + random.uniform(-5, 5),
                "market_cap": "$2.5T",
                "sector": "Technology",
                "recent_news": "Product launch announced"
            }
            
            historical_data = {
                "avg_correlation": sum(h.get('correlation_coefficient', 0) for h in historical_correlations) / max(len(historical_correlations), 1),
                "trend_accuracy": 0.75,  # Simulated
                "lead_time_days": 3 if correlation_coefficient > 0.5 else 0
            }
            
            prompt = TREND_ANALYSIS_PROMPT.format(
                symbol=symbol,
                company_info=json.dumps(company_info, indent=2),
                trends_data=json.dumps({k: {
                    'current_volume': v['current_volume'],
                    'growth_rate': v['growth_rate'],
                    'peak_volume': v['peak_volume']
                } for k, v in trends_data.items()}, indent=2),
                historical_correlations=json.dumps(historical_data, indent=2),
                market_context=json.dumps(market_context, indent=2)
            )
            
            response = self.model.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config={"temperature": 0.0, "response_mime_type": "application/json"}
            )
            
            trend_analysis = json.loads(response.text)
            
            # Step 6: Save to Supabase
            # Save trend analysis
            for term, data in trends_data.items():
                client = self.supabase.get_client()
                client.table('market_trends').insert({
                    'symbol': symbol,
                    'search_term': term,
                    'trend_score': data['current_volume'],
                    'correlation_coefficient': correlation_coefficient,
                    'lead_lag_days': trend_analysis['lead_lag_analysis']['lead_time_days']
                }).execute()
            
            # Save as trading signal if strong correlation
            if trend_analysis['correlation_strength'] > 0.7:
                signal_type = 'buy' if trend_analysis['trend_direction'] == 'increasing' else 'sell'
                await self.supabase.create_trading_signal(
                    symbol=symbol,
                    signal_type=signal_type,
                    confidence_score=trend_analysis['confidence_level'],
                    agent_name=self.agent_name,
                    reasoning=f"Strong trend correlation ({trend_analysis['correlation_strength']}) - {trend_analysis['investment_implications']}"
                )
            
            # Return final analysis
            final_response = {
                "trend_analysis": trend_analysis,
                "search_terms_analyzed": list(trends_data.keys()),
                "trends_data": trends_data,
                "correlation_metrics": {
                    "current_correlation": correlation_coefficient,
                    "historical_average": historical_data['avg_correlation'],
                    "trend_strength": trend_analysis['trend_score']
                },
                "investment_signal": {
                    "action": "buy" if trend_analysis['predictive_signals']['short_term_outlook'] == 'bullish' else "hold",
                    "confidence": trend_analysis['confidence_level'],
                    "reasoning": trend_analysis['investment_implications']
                },
                "timestamp": datetime.now().isoformat()
            }
            
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "response_type": "data",
                "content": final_response
            }
            
        except Exception as e:
            logger.error(f"Trend Correlator error: {e}")
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": f"Trend Correlator: Analysis error - {str(e)}"
            }

    async def invoke(self, query: str, session_id: str) -> dict:
        """Non-streaming invoke (not implemented)."""
        raise NotImplementedError("Please use the streaming interface")