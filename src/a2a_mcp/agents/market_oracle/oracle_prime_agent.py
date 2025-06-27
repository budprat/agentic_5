"""Oracle Prime - Master Investment Orchestrator Agent."""

import logging
import json
from collections.abc import AsyncIterable
from typing import Dict, Any, List
from datetime import datetime

from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import init_api_key
from a2a_mcp.common.parallel_workflow import (
    ParallelWorkflowGraph, 
    ParallelWorkflowNode,
    Status
)
from google import genai

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

class OraclePrimeAgent(BaseAgent):
    """Master orchestrator for investment research and trading decisions."""

    def __init__(self):
        init_api_key()
        super().__init__(
            agent_name="Oracle Prime",
            description="Master investment orchestrator with risk management",
            content_types=["text", "text/plain"],
        )
        self.graph = None
        self.market_intelligence = {}
        self.portfolio_context = {
            "total_value": 100000,
            "cash_balance": 50000,
            "positions": [],
            "risk_metrics": {}
        }
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

    def analyze_agent_dependencies(self, query: str) -> Dict[str, List[str]]:
        """Determine which agents to activate and their dependencies."""
        agent_groups = {
            "sentiment_analysis": ["sentiment_seeker"],
            "fundamental_analysis": ["fundamental_analyst"],
            "technical_analysis": ["technical_prophet"],
            "trend_analysis": ["trend_correlator"],
            "risk_assessment": ["risk_guardian"],
            "documentation": ["report_synthesizer"],
            "audio_update": ["audio_briefer"]
        }
        
        # Determine which analyses to run based on query
        required_analyses = []
        query_lower = query.lower()
        
        # Always include risk assessment for any trading decision
        if any(word in query_lower for word in ["buy", "sell", "trade", "invest", "position"]):
            required_analyses.extend(["sentiment_analysis", "fundamental_analysis", 
                                     "technical_analysis", "risk_assessment"])
        
        if "trend" in query_lower or "google" in query_lower:
            required_analyses.append("trend_analysis")
        
        if "report" in query_lower or "document" in query_lower:
            required_analyses.append("documentation")
            
        if "audio" in query_lower or "brief" in query_lower:
            required_analyses.append("audio_update")
        
        # Default to comprehensive analysis if no specific request
        if not required_analyses:
            required_analyses = ["sentiment_analysis", "fundamental_analysis", 
                               "technical_analysis", "trend_analysis", "risk_assessment"]
        
        return {group: agents for group, agents in agent_groups.items() 
                if group in required_analyses}

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
        # Simplified calculation - in production would use VaR
        position_risk = trade.get("size", 0) * 0.2  # Assume 20% max loss
        return position_risk

    def _check_correlation(self, trade: Dict) -> float:
        """Check portfolio correlation with new position."""
        # Simplified - in production would calculate actual correlation matrix
        return 0.3  # Placeholder

    def clear_state(self):
        """Reset agent state for new analysis."""
        self.graph = None
        self.market_intelligence.clear()
        self.query_history.clear()

    async def stream(
        self, query: str, context_id: str, task_id: str
    ) -> AsyncIterable[Dict[str, Any]]:
        """Execute investment analysis workflow."""
        logger.info(f"Oracle Prime analyzing: {query} (session: {context_id})")
        
        if not query:
            raise ValueError("Query cannot be empty")
        
        if self.context_id != context_id:
            self.clear_state()
            self.context_id = context_id
        
        self.query_history.append({"timestamp": datetime.now().isoformat(), "query": query})
        
        try:
            # Step 1: Initialize workflow graph
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Oracle Prime: Initializing market analysis workflow..."
            }
            
            self.graph = ParallelWorkflowGraph()
            
            # Step 2: Determine required analyses
            agent_groups = self.analyze_agent_dependencies(query)
            logger.info(f"Activating agent groups: {list(agent_groups.keys())}")
            
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": f"Oracle Prime: Coordinating {len(agent_groups)} analysis modules..."
            }
            
            # Step 3: Create workflow nodes for each agent group
            nodes = {}
            for group_name, agents in agent_groups.items():
                for agent_name in agents:
                    node = ParallelWorkflowNode(
                        task=f"Run {agent_name} analysis",
                        node_key=agent_name,
                        node_label=agent_name.replace("_", " ").title()
                    )
                    self.graph.add_node(node)
                    nodes[agent_name] = node
                    
                    # Set initial status
                    self.graph.set_node_attributes(
                        node.id, 
                        {"status": Status.PENDING, "agent_name": agent_name}
                    )
            
            # Step 4: Execute parallel analyses (simulated for now)
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Oracle Prime: Executing parallel market analysis..."
            }
            
            # Simulate agent responses (in production, would make actual A2A calls)
            self.market_intelligence = {
                "sentiment": {
                    "score": 0.75,
                    "volume": "high",
                    "sources": ["reddit", "twitter"],
                    "key_mentions": 1250
                },
                "fundamentals": {
                    "pe_ratio": 25.4,
                    "revenue_growth": 0.15,
                    "earnings_surprise": 0.08,
                    "analyst_rating": "buy"
                },
                "technical": {
                    "trend": "bullish",
                    "rsi": 65,
                    "support": 150.0,
                    "resistance": 165.0,
                    "price_prediction": {"1_day": 158.5, "1_week": 162.0}
                },
                "risk_metrics": {
                    "var_95": 5000,
                    "sharpe_ratio": 1.85,
                    "correlation": 0.35,
                    "risk_score": 45
                }
            }
            
            # Step 5: Generate investment recommendation
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Oracle Prime: Synthesizing investment recommendation..."
            }
            
            summary = await self.generate_investment_summary()
            recommendation = json.loads(summary)
            
            # Step 6: Check risk limits
            proposed_trade = {
                "symbol": query.split()[-1] if len(query.split()) > 1 else "UNKNOWN",
                "size": float(recommendation.get("position_size", "2.0").rstrip("%")) / 100,
                "value": self.portfolio_context["total_value"] * float(recommendation.get("position_size", "2.0").rstrip("%")) / 100
            }
            
            risk_check = self.check_risk_limits(proposed_trade)
            
            # Step 7: Format final response
            final_response = {
                "recommendation": recommendation,
                "risk_validation": risk_check,
                "market_intelligence": self.market_intelligence,
                "timestamp": datetime.now().isoformat()
            }
            
            if risk_check["requires_human"]:
                yield {
                    "is_task_complete": False,
                    "require_user_input": True,
                    "content": f"Oracle Prime: Trade value (${proposed_trade['value']:,.2f}) exceeds automatic approval limit. Please confirm to proceed with this {recommendation['investment_recommendation']} recommendation."
                }
            else:
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

    async def invoke(self, query: str, session_id: str) -> dict:
        """Non-streaming invoke (not implemented - use stream)."""
        raise NotImplementedError("Please use the streaming interface")