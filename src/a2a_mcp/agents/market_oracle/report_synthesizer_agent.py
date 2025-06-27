"""Report Synthesizer - Documentation Generation Agent."""

import logging
import json
from collections.abc import AsyncIterable
from typing import Dict, Any, List
from datetime import datetime
import base64

from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import init_api_key
from a2a_mcp.common.supabase_client import SupabaseClient
from google import genai

logger = logging.getLogger(__name__)

REPORT_GENERATION_PROMPT = """
You are Report Synthesizer, an AI specialist in creating comprehensive investment reports.

Generate a professional investment report based on the following data:

Investment Analysis Data:
{analysis_data}

Portfolio Context:
{portfolio_context}

Recent Trading Activity:
{recent_activity}

Market Conditions:
{market_conditions}

Generate a structured investment report in JSON format:
{{
    "report_metadata": {{
        "title": "Investment Analysis Report - [Symbol]",
        "date": "YYYY-MM-DD",
        "report_type": "comprehensive/summary/alert",
        "urgency": "high/medium/low"
    }},
    "executive_summary": {{
        "key_recommendation": "BUY/HOLD/SELL",
        "confidence_level": "high/medium/low",
        "investment_thesis": "2-3 sentence summary",
        "risk_reward_profile": "favorable/balanced/unfavorable"
    }},
    "market_analysis": {{
        "technical_summary": "Technical analysis findings",
        "fundamental_summary": "Fundamental analysis findings",
        "sentiment_summary": "Market sentiment analysis",
        "trend_summary": "Search trend correlations"
    }},
    "risk_assessment": {{
        "primary_risks": ["risk1", "risk2", "risk3"],
        "risk_mitigation": ["strategy1", "strategy2"],
        "portfolio_impact": "Expected impact on portfolio",
        "downside_scenarios": ["scenario1", "scenario2"]
    }},
    "recommendation_details": {{
        "action_items": [
            {{"priority": "high/medium/low", "action": "specific action", "timeline": "immediate/short-term/long-term"}}
        ],
        "position_sizing": "Recommended allocation",
        "entry_strategy": "How to enter position",
        "exit_criteria": "When to exit position"
    }},
    "supporting_data": {{
        "key_metrics": {{"metric": "value"}},
        "confidence_factors": ["factor1", "factor2"],
        "data_quality_score": 0.0-1.0
    }},
    "disclaimer": "Standard investment disclaimer",
    "next_review_date": "YYYY-MM-DD"
}}
"""

MARKDOWN_TEMPLATE = """# {title}

**Date:** {date}  
**Report Type:** {report_type}  
**Urgency:** {urgency}

## Executive Summary

**Recommendation:** {recommendation}  
**Confidence:** {confidence}  

{investment_thesis}

**Risk/Reward Profile:** {risk_reward}

## Market Analysis

### Technical Analysis
{technical_summary}

### Fundamental Analysis
{fundamental_summary}

### Sentiment Analysis
{sentiment_summary}

### Trend Analysis
{trend_summary}

## Risk Assessment

### Primary Risks
{risks}

### Risk Mitigation Strategies
{mitigation}

### Portfolio Impact
{portfolio_impact}

## Recommendations

### Action Items
{action_items}

### Position Sizing
{position_sizing}

### Entry Strategy
{entry_strategy}

### Exit Criteria
{exit_criteria}

## Key Metrics
{metrics}

---

*{disclaimer}*

**Next Review Date:** {next_review}
"""

class ReportSynthesizerAgent(BaseAgent):
    """Documentation generation agent with Supabase integration."""

    def __init__(self):
        init_api_key()
        super().__init__(
            agent_name="Report Synthesizer",
            description="Investment report generation with Supabase integration",
            content_types=["text", "text/plain"],
        )
        self.supabase = SupabaseClient()
        self.model = genai.Client()

    async def gather_analysis_data(self, symbol: str) -> Dict[str, Any]:
        """Gather all analysis data from Supabase."""
        try:
            client = self.supabase.get_client()
            
            # Get latest trading signals
            signals = await self.supabase.get_latest_signals(symbol, limit=20)
            
            # Get investment research
            research_response = client.table('investment_research').select("*").eq(
                'symbol', symbol
            ).order('created_at', desc=True).limit(1).execute()
            
            # Get sentiment data
            sentiment_response = client.table('sentiment_data').select("*").eq(
                'symbol', symbol
            ).order('timestamp', desc=True).limit(10).execute()
            
            # Get market trends
            trends_response = client.table('market_trends').select("*").eq(
                'symbol', symbol
            ).order('timestamp', desc=True).limit(10).execute()
            
            # Aggregate by agent
            agent_data = {}
            for signal in signals:
                agent_name = signal.get('agent_name', 'unknown')
                if agent_name not in agent_data:
                    agent_data[agent_name] = []
                agent_data[agent_name].append(signal)
            
            return {
                "trading_signals": signals,
                "agent_analyses": agent_data,
                "research": research_response.data[0] if research_response.data else {},
                "sentiment_data": sentiment_response.data,
                "trend_data": trends_response.data,
                "data_completeness": len(agent_data) / 5  # Out of 5 analysis agents
            }
            
        except Exception as e:
            logger.error(f"Error gathering analysis data: {e}")
            return {}

    async def generate_markdown_report(self, report_data: Dict[str, Any]) -> str:
        """Convert JSON report to formatted Markdown."""
        meta = report_data.get('report_metadata', {})
        exec_summary = report_data.get('executive_summary', {})
        market = report_data.get('market_analysis', {})
        risk = report_data.get('risk_assessment', {})
        rec = report_data.get('recommendation_details', {})
        support = report_data.get('supporting_data', {})
        
        # Format action items
        action_items = "\n".join([
            f"- **[{item['priority'].upper()}]** {item['action']} ({item['timeline']})"
            for item in rec.get('action_items', [])
        ])
        
        # Format risks
        risks = "\n".join([f"- {risk}" for risk in risk.get('primary_risks', [])])
        mitigation = "\n".join([f"- {strategy}" for strategy in risk.get('risk_mitigation', [])])
        
        # Format metrics
        metrics = "\n".join([
            f"- **{k}:** {v}" for k, v in support.get('key_metrics', {}).items()
        ])
        
        return MARKDOWN_TEMPLATE.format(
            title=meta.get('title', 'Investment Report'),
            date=meta.get('date', datetime.now().strftime('%Y-%m-%d')),
            report_type=meta.get('report_type', 'comprehensive'),
            urgency=meta.get('urgency', 'medium'),
            recommendation=exec_summary.get('key_recommendation', 'HOLD'),
            confidence=exec_summary.get('confidence_level', 'medium'),
            investment_thesis=exec_summary.get('investment_thesis', ''),
            risk_reward=exec_summary.get('risk_reward_profile', 'balanced'),
            technical_summary=market.get('technical_summary', ''),
            fundamental_summary=market.get('fundamental_summary', ''),
            sentiment_summary=market.get('sentiment_summary', ''),
            trend_summary=market.get('trend_summary', ''),
            risks=risks,
            mitigation=mitigation,
            portfolio_impact=risk.get('portfolio_impact', ''),
            action_items=action_items,
            position_sizing=rec.get('position_sizing', ''),
            entry_strategy=rec.get('entry_strategy', ''),
            exit_criteria=rec.get('exit_criteria', ''),
            metrics=metrics,
            disclaimer=report_data.get('disclaimer', 'This report is for informational purposes only.'),
            next_review=report_data.get('next_review_date', '')
        )

    async def stream(
        self, query: str, context_id: str, task_id: str
    ) -> AsyncIterable[Dict[str, Any]]:
        """Execute report generation workflow with Supabase integration."""
        logger.info(f"Report Synthesizer generating report: {query}")
        
        # Extract symbol from query
        import re
        symbol_match = re.search(r'\b[A-Z]{1,5}\b', query)
        symbol = symbol_match.group(0) if symbol_match else "AAPL"
        
        try:
            # Step 1: Gather all analysis data
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": f"Report Synthesizer: Gathering analysis data for {symbol}..."
            }
            
            analysis_data = await self.gather_analysis_data(symbol)
            
            # Step 2: Load portfolio context
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Report Synthesizer: Loading portfolio context..."
            }
            
            client = self.supabase.get_client()
            portfolio_response = client.table('portfolios').select(
                "*, positions(*)"
            ).eq('user_id', 'demo_user').limit(1).execute()
            
            portfolio_context = {}
            if portfolio_response.data:
                portfolio = portfolio_response.data[0]
                portfolio_context = {
                    "total_value": float(portfolio.get('total_value', 0)),
                    "cash_balance": float(portfolio.get('cash_balance', 0)),
                    "positions": len(portfolio.get('positions', [])),
                    "exposure_to_symbol": any(p['symbol'] == symbol for p in portfolio.get('positions', []))
                }
            
            # Step 3: Get recent activity
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Report Synthesizer: Analyzing recent trading activity..."
            }
            
            # Get recent trades (last 7 days)
            recent_signals = [s for s in analysis_data.get('trading_signals', [])
                            if s.get('created_at', '') > (datetime.now() - timedelta(days=7)).isoformat()]
            
            recent_activity = {
                "signal_count": len(recent_signals),
                "buy_signals": len([s for s in recent_signals if s.get('signal_type') == 'buy']),
                "sell_signals": len([s for s in recent_signals if s.get('signal_type') == 'sell']),
                "average_confidence": sum(s.get('confidence_score', 0) for s in recent_signals) / max(len(recent_signals), 1)
            }
            
            # Step 4: Determine market conditions
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Report Synthesizer: Assessing market conditions..."
            }
            
            market_conditions = {
                "overall_sentiment": "bullish" if recent_activity['buy_signals'] > recent_activity['sell_signals'] else "bearish",
                "volatility": "high" if len(recent_signals) > 10 else "moderate",
                "data_quality": analysis_data.get('data_completeness', 0),
                "last_update": datetime.now().isoformat()
            }
            
            # Step 5: Generate comprehensive report
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Report Synthesizer: Generating comprehensive report..."
            }
            
            prompt = REPORT_GENERATION_PROMPT.format(
                analysis_data=json.dumps(analysis_data, indent=2, default=str),
                portfolio_context=json.dumps(portfolio_context, indent=2),
                recent_activity=json.dumps(recent_activity, indent=2),
                market_conditions=json.dumps(market_conditions, indent=2)
            )
            
            response = self.model.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config={"temperature": 0.0, "response_mime_type": "application/json"}
            )
            
            report_data = json.loads(response.text)
            
            # Step 6: Generate Markdown version
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Report Synthesizer: Formatting report..."
            }
            
            markdown_report = await self.generate_markdown_report(report_data)
            
            # Step 7: Save to Supabase
            # Save research report
            research_entry = {
                'symbol': symbol,
                'thesis_summary': report_data['executive_summary']['investment_thesis'],
                'target_price': 0,  # Would be extracted from analysis
                'confidence_level': report_data['executive_summary']['confidence_level'],
                'fundamental_score': analysis_data.get('research', {}).get('fundamental_score', 0.5),
                'technical_score': analysis_data.get('research', {}).get('technical_score', 0.5),
                'sentiment_score': sum(s.get('sentiment_score', 0) for s in analysis_data.get('sentiment_data', [])) / max(len(analysis_data.get('sentiment_data', [])), 1)
            }
            
            client.table('investment_research').insert(research_entry).execute()
            
            # Return final report
            final_response = {
                "report": report_data,
                "markdown": markdown_report,
                "metadata": {
                    "symbol": symbol,
                    "generated_at": datetime.now().isoformat(),
                    "data_sources": len(analysis_data.get('agent_analyses', {})),
                    "confidence_score": analysis_data.get('data_completeness', 0),
                    "report_id": f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                },
                "download_formats": {
                    "markdown": base64.b64encode(markdown_report.encode()).decode(),
                    "json": base64.b64encode(json.dumps(report_data, indent=2).encode()).decode()
                }
            }
            
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "response_type": "data",
                "content": final_response
            }
            
        except Exception as e:
            logger.error(f"Report Synthesizer error: {e}")
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": f"Report Synthesizer: Error generating report - {str(e)}"
            }

    async def invoke(self, query: str, session_id: str) -> dict:
        """Non-streaming invoke (not implemented)."""
        raise NotImplementedError("Please use the streaming interface")