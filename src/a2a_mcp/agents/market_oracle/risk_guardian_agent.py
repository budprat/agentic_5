"""Risk Guardian - Portfolio Risk Management Agent."""

import logging
import json
from collections.abc import AsyncIterable
from typing import Dict, Any, List
from datetime import datetime, timedelta
import math

from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import init_api_key
from a2a_mcp.common.supabase_client import SupabaseClient
from google import genai

logger = logging.getLogger(__name__)

RISK_ASSESSMENT_PROMPT = """
You are Risk Guardian, an AI risk management specialist focused on portfolio protection.

Analyze the following portfolio and proposed trade:

Portfolio Data:
{portfolio_data}

Proposed Trade:
{proposed_trade}

Current Risk Metrics:
{risk_metrics}

Market Conditions:
{market_conditions}

Generate a comprehensive risk assessment in JSON format:
{{
    "risk_score": 0-100,
    "risk_level": "low/medium/high/critical",
    "approval_status": "approved/rejected/needs_review",
    "portfolio_metrics": {{
        "var_95": "Value at Risk (95% confidence)",
        "expected_shortfall": "Expected shortfall amount",
        "sharpe_ratio": "Risk-adjusted return metric",
        "max_drawdown": "Maximum potential loss %",
        "beta": "Market correlation",
        "portfolio_volatility": "Annual volatility %"
    }},
    "position_risks": {{
        "concentration_risk": "single position exposure",
        "correlation_risk": "portfolio correlation score",
        "liquidity_risk": "ease of exit score",
        "market_risk": "systematic risk exposure"
    }},
    "stress_tests": {{
        "market_crash_10": "portfolio value if market drops 10%",
        "market_crash_20": "portfolio value if market drops 20%",
        "black_swan_event": "portfolio value in extreme scenario"
    }},
    "risk_mitigation": {{
        "recommended_hedges": ["hedge1", "hedge2"],
        "position_adjustments": ["adjustment1", "adjustment2"],
        "stop_loss_levels": {{"symbol": "price"}},
        "diversification_suggestions": ["suggestion1", "suggestion2"]
    }},
    "human_override_required": true/false,
    "reasoning": "Detailed risk analysis explanation"
}}
"""

class RiskGuardianAgent(BaseAgent):
    """Portfolio risk management agent with Supabase integration."""

    def __init__(self):
        init_api_key()
        super().__init__(
            agent_name="Risk Guardian",
            description="Portfolio risk management with Supabase integration",
            content_types=["text", "text/plain"],
        )
        self.supabase = SupabaseClient()
        self.model = genai.Client()
        self.risk_thresholds = {
            "max_var_95": 0.15,  # 15% VaR limit
            "max_sharpe_degradation": 0.2,  # 20% Sharpe ratio degradation
            "max_concentration": 0.25,  # 25% single position limit
            "min_liquidity_ratio": 0.3,  # 30% minimum liquid assets
            "max_correlation": 0.7  # 70% portfolio correlation limit
        }

    async def load_portfolio_risk_metrics(self, portfolio_id: str) -> Dict[str, Any]:
        """Load current risk metrics from Supabase."""
        try:
            client = self.supabase.get_client()
            
            # Get latest risk metrics
            risk_response = client.table('risk_metrics').select("*").eq(
                'portfolio_id', portfolio_id
            ).order('calculated_at', desc=True).limit(1).execute()
            
            if risk_response.data:
                return risk_response.data[0]
            
            # Return default metrics if none exist
            return {
                "var_95": 0.10,
                "sharpe_ratio": 1.5,
                "max_drawdown": 0.08,
                "correlation_score": 0.45
            }
            
        except Exception as e:
            logger.error(f"Error loading risk metrics: {e}")
            return {}

    async def calculate_portfolio_metrics(self, portfolio: Dict[str, Any], 
                                        proposed_trade: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate updated portfolio metrics with proposed trade."""
        positions = portfolio.get('positions', [])
        cash = portfolio.get('cash_balance', 0)
        total_value = portfolio.get('total_value', 100000)
        
        # Calculate current allocation
        position_values = {}
        for pos in positions:
            value = pos['quantity'] * pos['current_price']
            position_values[pos['symbol']] = value
        
        # Add proposed trade
        if proposed_trade:
            symbol = proposed_trade['symbol']
            trade_value = proposed_trade.get('value', 0)
            if symbol in position_values:
                position_values[symbol] += trade_value
            else:
                position_values[symbol] = trade_value
        
        # Calculate concentration
        max_position = max(position_values.values()) if position_values else 0
        concentration = max_position / total_value if total_value > 0 else 0
        
        # Calculate diversification (simplified Herfindahl index)
        herfindahl = sum((v/total_value)**2 for v in position_values.values())
        diversification_score = 1 - herfindahl
        
        # Estimate portfolio volatility (simplified)
        # In production, use historical correlations and individual volatilities
        num_positions = len(position_values)
        base_volatility = 0.20  # 20% annual volatility baseline
        portfolio_volatility = base_volatility / math.sqrt(max(num_positions, 1))
        
        # Calculate VaR (simplified normal distribution assumption)
        var_95 = total_value * portfolio_volatility * 1.645 / math.sqrt(252)  # Daily VaR
        
        # Estimate Sharpe ratio (simplified)
        expected_return = 0.08  # 8% expected annual return
        risk_free_rate = 0.02  # 2% risk-free rate
        sharpe_ratio = (expected_return - risk_free_rate) / portfolio_volatility
        
        return {
            "concentration": concentration,
            "diversification_score": diversification_score,
            "portfolio_volatility": portfolio_volatility,
            "var_95": var_95 / total_value,  # As percentage
            "sharpe_ratio": sharpe_ratio,
            "liquid_ratio": cash / total_value,
            "position_count": num_positions
        }

    async def run_stress_tests(self, portfolio: Dict[str, Any], 
                             scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run stress test scenarios on portfolio."""
        results = {}
        total_value = portfolio.get('total_value', 100000)
        
        # Market crash scenarios
        for crash_pct in [0.10, 0.20, 0.30]:
            scenario_value = total_value * (1 - crash_pct)
            results[f"market_crash_{int(crash_pct*100)}"] = {
                "portfolio_value": scenario_value,
                "loss": total_value - scenario_value,
                "loss_percentage": crash_pct
            }
        
        # Black swan event (50% drawdown)
        black_swan_value = total_value * 0.5
        results["black_swan_event"] = {
            "portfolio_value": black_swan_value,
            "loss": total_value - black_swan_value,
            "loss_percentage": 0.5
        }
        
        return results

    async def stream(
        self, query: str, context_id: str, task_id: str
    ) -> AsyncIterable[Dict[str, Any]]:
        """Execute risk assessment workflow with Supabase integration."""
        logger.info(f"Risk Guardian analyzing: {query}")
        
        try:
            # Parse query for portfolio and trade info
            import re
            symbol_match = re.search(r'\b[A-Z]{1,5}\b', query)
            symbol = symbol_match.group(0) if symbol_match else "AAPL"
            
            # Step 1: Load portfolio from Supabase
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Risk Guardian: Loading portfolio data from Supabase..."
            }
            
            # Get portfolio data
            client = self.supabase.get_client()
            portfolio_response = client.table('portfolios').select(
                "*, positions(*)"
            ).eq('user_id', 'demo_user').limit(1).execute()
            
            if not portfolio_response.data:
                raise ValueError("No portfolio found")
            
            portfolio = portfolio_response.data[0]
            portfolio_id = portfolio['id']
            
            # Step 2: Load current risk metrics
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Risk Guardian: Analyzing current risk profile..."
            }
            
            current_risk_metrics = await self.load_portfolio_risk_metrics(portfolio_id)
            
            # Step 3: Analyze proposed trade
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": f"Risk Guardian: Evaluating risk impact of {symbol} trade..."
            }
            
            # Simulate proposed trade
            proposed_trade = {
                "symbol": symbol,
                "action": "buy",
                "quantity": 100,
                "price": 150.00,
                "value": 15000.00
            }
            
            # Step 4: Calculate updated metrics
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Risk Guardian: Calculating portfolio metrics..."
            }
            
            updated_metrics = await self.calculate_portfolio_metrics(portfolio, proposed_trade)
            
            # Step 5: Run stress tests
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Risk Guardian: Running stress test scenarios..."
            }
            
            stress_results = await self.run_stress_tests(portfolio, [])
            
            # Step 6: Generate comprehensive risk assessment
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Risk Guardian: Generating risk assessment report..."
            }
            
            # Prepare data for Gemini analysis
            portfolio_data = {
                "total_value": float(portfolio.get('total_value', 0)),
                "cash_balance": float(portfolio.get('cash_balance', 0)),
                "positions": len(portfolio.get('positions', [])),
                "current_metrics": updated_metrics
            }
            
            market_conditions = {
                "vix_level": 18.5,  # Simulated
                "market_trend": "bullish",
                "sector_rotation": "technology to value"
            }
            
            prompt = RISK_ASSESSMENT_PROMPT.format(
                portfolio_data=json.dumps(portfolio_data, indent=2),
                proposed_trade=json.dumps(proposed_trade, indent=2),
                risk_metrics=json.dumps(current_risk_metrics, indent=2),
                market_conditions=json.dumps(market_conditions, indent=2)
            )
            
            response = self.model.models.generate_content(
                model=os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-001'),
                contents=prompt,
                config={"temperature": 0.0, "response_mime_type": "application/json"}
            )
            
            risk_assessment = json.loads(response.text)
            
            # Step 7: Save to Supabase
            # Save updated risk metrics
            new_metrics = {
                'portfolio_id': portfolio_id,
                'var_95': updated_metrics['var_95'],
                'sharpe_ratio': updated_metrics['sharpe_ratio'],
                'max_drawdown': stress_results['market_crash_20']['loss_percentage'],
                'correlation_score': updated_metrics.get('correlation_score', 0.5)
            }
            
            client.table('risk_metrics').insert(new_metrics).execute()
            
            # Save risk assessment as trading signal
            await self.supabase.create_trading_signal(
                symbol=symbol,
                signal_type='hold' if risk_assessment['risk_score'] > 70 else 'buy',
                confidence_score=1 - (risk_assessment['risk_score'] / 100),
                agent_name=self.agent_name,
                reasoning=f"Risk Score: {risk_assessment['risk_score']}/100 - {risk_assessment['reasoning']}"
            )
            
            # Return final assessment
            final_response = {
                "risk_assessment": risk_assessment,
                "portfolio_metrics": updated_metrics,
                "stress_test_results": stress_results,
                "risk_thresholds": self.risk_thresholds,
                "compliance_checks": {
                    "concentration_ok": updated_metrics['concentration'] <= self.risk_thresholds['max_concentration'],
                    "var_ok": updated_metrics['var_95'] <= self.risk_thresholds['max_var_95'],
                    "liquidity_ok": updated_metrics['liquid_ratio'] >= self.risk_thresholds['min_liquidity_ratio']
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
            logger.error(f"Risk Guardian error: {e}")
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": f"Risk Guardian: Risk assessment error - {str(e)}"
            }

    async def invoke(self, query: str, session_id: str) -> dict:
        """Non-streaming invoke (not implemented)."""
        raise NotImplementedError("Please use the streaming interface")