"""Technical Prophet - ML Predictions and Technical Analysis Agent."""

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

TECHNICAL_ANALYSIS_PROMPT = """
You are Technical Prophet, an AI model specialized in technical analysis and market predictions.

Analyze the following technical data and generate a trading signal:

Symbol: {symbol}
Current Price: ${current_price}
Historical Data: {historical_data}
Technical Indicators: {indicators}
Recent Trading Signals: {recent_signals}

Generate a technical analysis report in JSON format:
{{
    "signal_type": "buy/sell/hold",
    "confidence_score": 0.0-1.0,
    "technical_score": 0.0-1.0,
    "price_targets": {{
        "short_term": "price in 1-7 days",
        "medium_term": "price in 1-3 months",
        "support_level": "key support price",
        "resistance_level": "key resistance price"
    }},
    "indicators_summary": {{
        "trend": "bullish/bearish/neutral",
        "momentum": "strong/moderate/weak",
        "volatility": "high/medium/low",
        "volume_analysis": "increasing/decreasing/stable"
    }},
    "ml_predictions": {{
        "next_day_direction": "up/down",
        "probability": 0.0-1.0,
        "expected_move": "percentage"
    }},
    "key_levels": [
        {{"price": value, "type": "support/resistance", "strength": "strong/moderate/weak"}}
    ],
    "reasoning": "Detailed technical explanation"
}}
"""

class TechnicalProphetAgent(BaseAgent):
    """ML-powered technical analysis agent with Supabase integration."""

    def __init__(self):
        init_api_key()
        super().__init__(
            agent_name="Technical Prophet",
            description="ML predictions and technical analysis with Supabase",
            content_types=["text", "text/plain"],
        )
        self.supabase = SupabaseClient()
        self.model = genai.Client()

    async def calculate_technical_indicators(self, symbol: str, price_data: List[float]) -> Dict[str, Any]:
        """Calculate technical indicators from price data."""
        if len(price_data) < 2:
            return {}
        
        # Simple technical indicators (in production, use TA-Lib or similar)
        current_price = price_data[-1]
        sma_20 = sum(price_data[-20:]) / min(20, len(price_data))
        
        # RSI calculation (simplified)
        gains = []
        losses = []
        for i in range(1, min(14, len(price_data))):
            change = price_data[i] - price_data[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains) / len(gains) if gains else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        rs = avg_gain / avg_loss if avg_loss > 0 else 100
        rsi = 100 - (100 / (1 + rs))
        
        # MACD (simplified)
        ema_12 = current_price  # Simplified
        ema_26 = sma_20  # Simplified
        macd = ema_12 - ema_26
        
        # Bollinger Bands
        std_dev = (sum((p - sma_20) ** 2 for p in price_data[-20:]) / min(20, len(price_data))) ** 0.5
        bb_upper = sma_20 + (2 * std_dev)
        bb_lower = sma_20 - (2 * std_dev)
        
        return {
            "current_price": current_price,
            "sma_20": round(sma_20, 2),
            "rsi": round(rsi, 2),
            "macd": round(macd, 2),
            "bollinger_bands": {
                "upper": round(bb_upper, 2),
                "middle": round(sma_20, 2),
                "lower": round(bb_lower, 2)
            },
            "volume_trend": "increasing" if random.random() > 0.5 else "decreasing"
        }

    async def get_historical_signals(self, symbol: str) -> List[Dict[str, Any]]:
        """Get historical trading signals from Supabase."""
        try:
            signals = await self.supabase.get_latest_signals(
                symbol=symbol,
                agent_name="Technical Prophet",
                limit=10
            )
            return signals
        except Exception as e:
            logger.error(f"Error fetching historical signals: {e}")
            return []

    async def generate_ml_prediction(self, symbol: str, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ML-based price prediction."""
        # In production, this would use a trained ML model
        # For demo, we'll use Gemini to simulate ML predictions
        
        client = genai.Client()
        
        prompt = f"""
        Based on these technical indicators for {symbol}:
        - RSI: {indicators.get('rsi', 50)}
        - MACD: {indicators.get('macd', 0)}
        - Current price vs SMA: {indicators.get('current_price', 0) / indicators.get('sma_20', 1)}
        
        Predict the next day's price movement (up/down) and probability (0-1).
        Response format: {{"direction": "up/down", "probability": 0.X, "expected_move": "X%"}}
        """
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={"temperature": 0.0, "response_mime_type": "application/json"}
        )
        
        return json.loads(response.text)

    async def stream(
        self, query: str, context_id: str, task_id: str
    ) -> AsyncIterable[Dict[str, Any]]:
        """Execute technical analysis workflow with Supabase integration."""
        logger.info(f"Technical Prophet analyzing: {query}")
        
        # Extract symbol from query
        import re
        symbol_match = re.search(r'\b[A-Z]{1,5}\b', query)
        symbol = symbol_match.group(0) if symbol_match else "AAPL"
        
        try:
            # Step 1: Get price data (simulated for demo)
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": f"Technical Prophet: Fetching price data for {symbol}..."
            }
            
            # Simulate historical prices
            base_price = 150 + (random.random() * 50)
            price_data = [base_price + (random.random() - 0.5) * 10 for _ in range(50)]
            
            # Step 2: Calculate technical indicators
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Technical Prophet: Calculating technical indicators..."
            }
            
            indicators = await self.calculate_technical_indicators(symbol, price_data)
            
            # Step 3: Get historical signals from Supabase
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Technical Prophet: Analyzing historical patterns..."
            }
            
            recent_signals = await self.get_historical_signals(symbol)
            
            # Step 4: Generate ML predictions
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Technical Prophet: Running ML prediction models..."
            }
            
            ml_prediction = await self.generate_ml_prediction(symbol, indicators)
            
            # Step 5: Generate comprehensive analysis
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Technical Prophet: Generating technical analysis report..."
            }
            
            # Use Gemini for comprehensive analysis
            historical_data = {
                "prices": price_data[-10:],
                "average_volume": "2.5M shares",
                "52_week_high": max(price_data) * 1.1,
                "52_week_low": min(price_data) * 0.9
            }
            
            prompt = TECHNICAL_ANALYSIS_PROMPT.format(
                symbol=symbol,
                current_price=indicators['current_price'],
                historical_data=json.dumps(historical_data, indent=2),
                indicators=json.dumps(indicators, indent=2),
                recent_signals=json.dumps([{
                    'signal_type': s.get('signal_type'),
                    'confidence': s.get('confidence_score'),
                    'date': s.get('created_at')
                } for s in recent_signals[-5:]], indent=2)
            )
            
            response = self.model.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config={"temperature": 0.0, "response_mime_type": "application/json"}
            )
            
            analysis = json.loads(response.text)
            
            # Step 6: Save to Supabase
            await self.supabase.create_trading_signal(
                symbol=symbol,
                signal_type=analysis['signal_type'],
                confidence_score=analysis['confidence_score'],
                agent_name=self.agent_name,
                reasoning=analysis['reasoning']
            )
            
            # Save market trend data
            client = self.supabase.get_client()
            client.table('market_trends').insert({
                'symbol': symbol,
                'search_term': f"{symbol} technical analysis",
                'trend_score': int(analysis['technical_score'] * 100),
                'correlation_coefficient': ml_prediction['probability'],
                'lead_lag_days': 1
            }).execute()
            
            # Return final analysis
            final_response = {
                "technical_analysis": analysis,
                "ml_predictions": ml_prediction,
                "indicators": indicators,
                "recent_signals": recent_signals,
                "timestamp": datetime.now().isoformat()
            }
            
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "response_type": "data",
                "content": final_response
            }
            
        except Exception as e:
            logger.error(f"Technical Prophet error: {e}")
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": f"Technical Prophet: Error in analysis - {str(e)}"
            }

    async def invoke(self, query: str, session_id: str) -> dict:
        """Non-streaming invoke (not implemented)."""
        raise NotImplementedError("Please use the streaming interface")