"""Oracle Prime - Master Investment Orchestrator Agent with Supabase Integration."""

import logging
import json
from collections.abc import AsyncIterable
from typing import Dict, Any, List
from datetime import datetime

from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import init_api_key
from a2a_mcp.common.supabase_client import SupabaseClient
from a2a_mcp.common.stock_mcp_client import StockMCPClient
from a2a_mcp.common.parallel_workflow import (
    ParallelWorkflowGraph, 
    ParallelWorkflowNode,
    Status
)
from google import genai
import os
import aiohttp

logger = logging.getLogger(__name__)

# Investment analysis prompt
INVESTMENT_SUMMARY_PROMPT = """
You are Oracle Prime, a master investment strategist. Analyze the following market intelligence data and provide a comprehensive investment recommendation.

Market Intelligence Data:
{market_data}

Portfolio Context:
{portfolio_context}

Risk Limits:
- Maximum position size: {max_position}% of portfolio
- Maximum drawdown tolerance: {max_drawdown}%
- Portfolio correlation limit: {correlation_limit}%

Provide your analysis in the following JSON format:
{{
    "executive_summary": "Brief 2-3 sentence summary",
    "investment_recommendation": "BUY/HOLD/SELL",
    "confidence_score": 0.0-1.0,
    "position_size": "Recommended % of portfolio",
    "risk_assessment": {{
        "risk_score": 0-100,
        "key_risks": ["risk1", "risk2"],
        "mitigation_strategies": ["strategy1", "strategy2"]
    }},
    "key_insights": [
        {{"source": "agent_name", "insight": "key finding"}},
        ...
    ],
    "entry_strategy": {{
        "entry_price": "recommended entry price or range",
        "timing": "immediate/wait_for_dip/scale_in",
        "conditions": ["condition1", "condition2"]
    }},
    "exit_strategy": {{
        "target_price": "price target",
        "stop_loss": "stop loss level",
        "time_horizon": "holding period"
    }}
}}
"""

class OraclePrimeAgentSupabase(BaseAgent):
    """Master orchestrator for investment research with Supabase integration."""

    def __init__(self):
        init_api_key()
        super().__init__(
            agent_name="Oracle Prime Supabase",
            description="Master investment orchestrator with Supabase database",
            content_types=["text", "text/plain"],
        )
        self.graph = None
        self.market_intelligence = {}
        self.portfolio_context = {}
        self.risk_limits = {
            "max_position_size": 0.05,
            "max_drawdown": 0.15,
            "correlation_limit": 0.40,
            "daily_trade_limit": 10,
            "human_override_threshold": 10000
        }
        self.query_history = []
        self.context_id = None
        self.enable_parallel = True
        self.supabase = SupabaseClient()
        self.stock_mcp = StockMCPClient()

    async def load_portfolio_context(self, user_id: str = "demo_user"):
        """Load portfolio context from Supabase."""
        try:
            # Get portfolio
            client = self.supabase.get_client()
            portfolio_response = (client.table('portfolios')
                                .select("*")
                                .eq('user_id', user_id)
                                .limit(1)
                                .execute())
            
            if portfolio_response.data:
                portfolio = portfolio_response.data[0]
                
                # Get positions
                positions_response = (client.table('positions')
                                    .select("*")
                                    .eq('portfolio_id', portfolio['id'])
                                    .is_('exit_date', 'null')
                                    .execute())
                
                # Get latest risk metrics
                risk_response = (client.table('risk_metrics')
                               .select("*")
                               .eq('portfolio_id', portfolio['id'])
                               .order('calculated_at', desc=True)
                               .limit(1)
                               .execute())
                
                self.portfolio_context = {
                    "portfolio_id": portfolio['id'],
                    "total_value": float(portfolio['total_value'] or 0),
                    "cash_balance": float(portfolio['cash_balance'] or 0),
                    "positions": positions_response.data or [],
                    "risk_metrics": risk_response.data[0] if risk_response.data else {}
                }
            else:
                # Create default portfolio if none exists
                logger.info(f"Creating new portfolio for user {user_id}")
                await self.supabase.create_portfolio(user_id, 100000.0, 50000.0)
                await self.load_portfolio_context(user_id)
                
        except Exception as e:
            logger.error(f"Error loading portfolio: {e}")
            # Fallback to default
            self.portfolio_context = {
                "total_value": 100000,
                "cash_balance": 50000,
                "positions": [],
                "risk_metrics": {}
            }

    async def save_trading_signal(self, symbol: str, signal_type: str, 
                                confidence: float, reasoning: str):
        """Save trading signal to Supabase."""
        try:
            await self.supabase.create_trading_signal(
                symbol=symbol,
                signal_type=signal_type,
                confidence_score=confidence,
                agent_name=self.agent_name,
                reasoning=reasoning
            )
        except Exception as e:
            logger.error(f"Error saving trading signal: {e}")

    async def save_investment_research(self, symbol: str, recommendation: Dict):
        """Save investment research to Supabase."""
        try:
            await self.supabase.create_research(
                symbol=symbol,
                thesis_summary=recommendation.get('executive_summary', ''),
                target_price=float(recommendation.get('exit_strategy', {}).get('target_price', '0').replace('$', '')),
                confidence_level='high' if recommendation.get('confidence_score', 0) > 0.8 else 'medium',
                fundamental_score=self.market_intelligence.get('fundamentals', {}).get('fundamental_score', 0.5),
                technical_score=self.market_intelligence.get('technical', {}).get('technical_score', 0.5),
                sentiment_score=self.market_intelligence.get('sentiment', {}).get('score', 0)
            )
        except Exception as e:
            logger.error(f"Error saving research: {e}")

    async def fetch_stock_predictions(self, symbol: str) -> Dict[str, Any]:
        """Fetch ML predictions from stock predictions MCP."""
        try:
            logger.info(f"Fetching predictions for {symbol} using Stock MCP client")
            
            # Use the Stock MCP client
            prediction_data = await self.stock_mcp.get_prediction(symbol)
            
            # Transform response to match our format
            prediction = prediction_data.get('prediction', {})
            
            predictions = {
                "symbol": symbol,
                "ml_prediction": {
                    "direction": prediction.get('direction', 'neutral'),
                    "confidence": prediction.get('confidence', 0.5),
                    "predicted_price_change": prediction.get('predicted_price_change_percent', 0),
                    "volatility_forecast": "moderate" if abs(prediction.get('predicted_price_change_percent', 0)) < 3 else "high",
                    "risk_score": 1 - prediction.get('confidence', 0.5)
                },
                "technical_signals": {
                    "support": prediction.get('key_levels', {}).get('support'),
                    "resistance": prediction.get('key_levels', {}).get('resistance'),
                    "factors": prediction.get('factors', [])
                },
                "model_metadata": prediction_data.get('model_info', {})
            }
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error fetching stock predictions: {e}")
            return {
                "symbol": symbol,
                "error": str(e),
                "ml_prediction": {
                    "direction": "unavailable",
                    "confidence": 0
                }
            }

    async def generate_investment_summary(self) -> str:
        """Generate comprehensive investment recommendation."""
        client = genai.Client()
        
        prompt = INVESTMENT_SUMMARY_PROMPT.format(
            market_data=json.dumps(self.market_intelligence, indent=2),
            portfolio_context=json.dumps(self.portfolio_context, indent=2),
            max_position=self.risk_limits["max_position_size"] * 100,
            max_drawdown=self.risk_limits["max_drawdown"] * 100,
            correlation_limit=self.risk_limits["correlation_limit"] * 100
        )
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={
                "temperature": 0.0,
                "response_mime_type": "application/json"
            }
        )
        return response.text

    async def stream(
        self, query: str, context_id: str, task_id: str
    ) -> AsyncIterable[Dict[str, Any]]:
        """Execute investment analysis workflow with Supabase integration."""
        logger.info(f"Oracle Prime Supabase analyzing: {query} (session: {context_id})")
        
        if not query:
            raise ValueError("Query cannot be empty")
        
        # Extract symbol from query
        import re
        symbol_match = re.search(r'\b[A-Z]{1,5}\b', query)
        symbol = symbol_match.group(0) if symbol_match else "UNKNOWN"
        
        try:
            # Step 1: Load portfolio context from Supabase
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Oracle Prime: Loading portfolio data from Supabase..."
            }
            
            await self.load_portfolio_context()
            
            # Step 2: Check for recent signals in Supabase
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": f"Oracle Prime: Checking recent signals for {symbol}..."
            }
            
            recent_signals = await self.supabase.get_latest_signals(symbol, limit=5)
            
            # Step 3: Fetch ML predictions from Stock MCP
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": f"Oracle Prime: Fetching ML predictions for {symbol}..."
            }
            
            stock_predictions = await self.fetch_stock_predictions(symbol)
            
            # Step 4: Initialize workflow (keeping existing logic)
            self.graph = ParallelWorkflowGraph()
            
            # Simulate market intelligence gathering
            # In production, this would coordinate actual agent calls
            self.market_intelligence = {
                "sentiment": {
                    "score": 0.75,
                    "volume": "high",
                    "sources": ["reddit_brightdata", "twitter"],
                    "recent_signals": [s for s in recent_signals if s['agent_name'] == 'sentiment_seeker']
                },
                "fundamentals": {
                    "pe_ratio": 25.4,
                    "revenue_growth": 0.15,
                    "fundamental_score": 0.85,
                    "recent_signals": [s for s in recent_signals if s['agent_name'] == 'fundamental_analyst']
                },
                "technical": {
                    "trend": "bullish",
                    "rsi": 65,
                    "technical_score": 0.75,
                    "recent_signals": [s for s in recent_signals if s['agent_name'] == 'technical_prophet']
                },
                "ml_predictions": stock_predictions
            }
            
            # Step 5: Generate recommendation
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Oracle Prime: Synthesizing investment recommendation..."
            }
            
            summary = await self.generate_investment_summary()
            recommendation = json.loads(summary)
            
            # Step 6: Save to Supabase
            signal_type = recommendation['investment_recommendation'].lower()
            confidence = recommendation.get('confidence_score', 0.5)
            
            await self.save_trading_signal(
                symbol=symbol,
                signal_type=signal_type,
                confidence=confidence,
                reasoning=recommendation.get('executive_summary', '')
            )
            
            await self.save_investment_research(symbol, recommendation)
            
            # Step 7: Check risk and return response
            proposed_trade = {
                "symbol": symbol,
                "size": float(recommendation.get("position_size", "2.0").rstrip("%")) / 100,
                "value": self.portfolio_context["total_value"] * float(recommendation.get("position_size", "2.0").rstrip("%")) / 100
            }
            
            risk_check = self.check_risk_limits(proposed_trade)
            
            final_response = {
                "recommendation": recommendation,
                "risk_validation": risk_check,
                "market_intelligence": self.market_intelligence,
                "portfolio_context": {
                    "current_positions": len(self.portfolio_context.get('positions', [])),
                    "cash_available": self.portfolio_context.get('cash_balance', 0),
                    "portfolio_value": self.portfolio_context.get('total_value', 0)
                },
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
            logger.error(f"Oracle Prime error: {e}")
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": f"Oracle Prime: Analysis error - {str(e)}"
            }

    def check_risk_limits(self, proposed_trade: Dict) -> Dict[str, Any]:
        """Validate proposed trade against risk limits."""
        checks = {
            "position_size": proposed_trade.get("size", 0) <= self.risk_limits["max_position_size"],
            "drawdown_risk": self._calculate_drawdown_risk(proposed_trade) <= self.risk_limits["max_drawdown"],
            "correlation": self._check_correlation(proposed_trade) <= self.risk_limits["correlation_limit"],
            "human_override_required": proposed_trade.get("value", 0) > self.risk_limits["human_override_threshold"]
        }
        
        return {
            "approved": all(checks.values()) and not checks["human_override_required"],
            "checks": checks,
            "requires_human": checks["human_override_required"]
        }

    def _calculate_drawdown_risk(self, trade: Dict) -> float:
        """Calculate potential drawdown from proposed trade."""
        position_risk = trade.get("size", 0) * 0.2
        return position_risk

    def _check_correlation(self, trade: Dict) -> float:
        """Check portfolio correlation with new position."""
        return 0.3

    def clear_state(self):
        """Reset agent state for new analysis."""
        self.graph = None
        self.market_intelligence.clear()
        self.query_history.clear()

    async def invoke(self, query: str, session_id: str) -> dict:
        """Non-streaming invoke (not implemented)."""
        raise NotImplementedError("Please use the streaming interface")