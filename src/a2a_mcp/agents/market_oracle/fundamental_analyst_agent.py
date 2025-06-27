"""Fundamental Analyst - SEC Filings and Earnings Analysis Agent."""

import logging
import json
from collections.abc import AsyncIterable
from typing import Dict, Any, List
from datetime import datetime

from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import get_mcp_server_config, init_api_key
from a2a_mcp.common.agent_runner import AgentRunner
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams
from google.genai import types as genai_types

logger = logging.getLogger(__name__)

FUNDAMENTAL_ANALYSIS_PROMPT = """
You are Fundamental Analyst, a specialized agent for analyzing company financials and SEC filings.

Your capabilities:
1. Parse SEC filings (10-K, 10-Q, 8-K) using BrightData MCP
2. Extract key financial metrics and ratios
3. Analyze earnings reports and guidance
4. Compare metrics with industry peers
5. Identify fundamental strengths and weaknesses

When analyzing a company, focus on:
1. Revenue growth and trends
2. Profit margins and efficiency
3. Balance sheet strength
4. Cash flow generation
5. Competitive positioning

Output Format (JSON):
{
    "symbol": "TICKER",
    "company_name": "Full company name",
    "financial_metrics": {
        "revenue_ttm": number,
        "revenue_growth_yoy": percentage,
        "gross_margin": percentage,
        "operating_margin": percentage,
        "net_margin": percentage,
        "pe_ratio": number,
        "peg_ratio": number,
        "price_to_book": number,
        "debt_to_equity": number,
        "current_ratio": number,
        "roe": percentage,
        "free_cash_flow": number
    },
    "peer_comparison": {
        "pe_vs_industry": "above/inline/below",
        "growth_vs_peers": "above/inline/below",
        "margins_vs_peers": "above/inline/below",
        "percentile_rank": 0-100
    },
    "recent_filings": [
        {
            "type": "10-K/10-Q/8-K",
            "date": "YYYY-MM-DD",
            "key_points": ["point1", "point2"]
        }
    ],
    "earnings_analysis": {
        "last_earnings_date": "YYYY-MM-DD",
        "earnings_surprise": percentage,
        "guidance": "raised/maintained/lowered/none",
        "analyst_consensus": "strong_buy/buy/hold/sell/strong_sell"
    },
    "fundamental_score": 0.0 to 1.0,
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"],
    "investment_thesis": "2-3 sentence fundamental view"
}

Use BrightData MCP to scrape SEC filings and financial data. Use HuggingFace models for document analysis if needed.
"""

class FundamentalAnalystAgent(BaseAgent):
    """Agent specialized in fundamental analysis of companies."""

    def __init__(self):
        init_api_key()
        super().__init__(
            agent_name="Fundamental Analyst",
            description="SEC filings and earnings analyzer",
            content_types=['text', 'text/plain']
        )
        logger.info(f'Initializing {self.agent_name}')
        self.agent = None
        self.runner = None
        self.analysis_cache = {}
        self.industry_benchmarks = {
            "tech": {"pe_ratio": 25, "revenue_growth": 0.15, "net_margin": 0.20},
            "finance": {"pe_ratio": 12, "revenue_growth": 0.08, "net_margin": 0.25},
            "healthcare": {"pe_ratio": 18, "revenue_growth": 0.12, "net_margin": 0.15},
            "consumer": {"pe_ratio": 20, "revenue_growth": 0.10, "net_margin": 0.12}
        }

    async def init_agent(self):
        """Initialize the agent with MCP tools."""
        logger.info(f'Initializing {self.agent_name} with MCP tools')
        
        config = get_mcp_server_config()
        tools = await MCPToolset(
            connection_params=SseConnectionParams(url=config.url)
        ).get_tools()
        
        generate_content_config = genai_types.GenerateContentConfig(
            temperature=0.0,
            response_mime_type="application/json"
        )
        
        self.agent = Agent(
            name=self.agent_name,
            instruction=FUNDAMENTAL_ANALYSIS_PROMPT,
            model='gemini-2.0-flash',
            generate_content_config=generate_content_config,
            tools=tools,
        )
        self.runner = AgentRunner()

    def calculate_fundamental_score(self, metrics: Dict) -> float:
        """Calculate overall fundamental score based on key metrics."""
        score = 0.0
        weights = {
            "revenue_growth": 0.20,
            "margins": 0.20,
            "valuation": 0.20,
            "balance_sheet": 0.20,
            "cash_flow": 0.20
        }
        
        # Revenue growth score
        growth = metrics.get("revenue_growth_yoy", 0)
        if growth > 0.20:
            score += weights["revenue_growth"]
        elif growth > 0.10:
            score += weights["revenue_growth"] * 0.7
        elif growth > 0:
            score += weights["revenue_growth"] * 0.4
        
        # Margins score
        net_margin = metrics.get("net_margin", 0)
        if net_margin > 0.20:
            score += weights["margins"]
        elif net_margin > 0.10:
            score += weights["margins"] * 0.7
        elif net_margin > 0.05:
            score += weights["margins"] * 0.4
        
        # Valuation score
        pe_ratio = metrics.get("pe_ratio", 30)
        if 10 < pe_ratio < 20:
            score += weights["valuation"]
        elif 20 <= pe_ratio < 30:
            score += weights["valuation"] * 0.7
        elif pe_ratio <= 10 and pe_ratio > 0:
            score += weights["valuation"] * 0.5
        
        # Balance sheet score
        debt_to_equity = metrics.get("debt_to_equity", 1.0)
        if debt_to_equity < 0.5:
            score += weights["balance_sheet"]
        elif debt_to_equity < 1.0:
            score += weights["balance_sheet"] * 0.7
        elif debt_to_equity < 2.0:
            score += weights["balance_sheet"] * 0.4
        
        # Cash flow score (simplified)
        if metrics.get("free_cash_flow", 0) > 0:
            score += weights["cash_flow"] * 0.8
        
        return min(1.0, score)

    def format_response(self, chunk: str) -> Dict:
        """Extract JSON from agent response."""
        try:
            # Try to find JSON in the response
            import re
            json_match = re.search(r'{.*}', chunk, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
        
        # Return default structure if parsing fails
        return {
            "symbol": "UNKNOWN",
            "fundamental_score": 0.0,
            "error": "Failed to parse fundamental data"
        }

    async def stream(
        self, query: str, context_id: str, task_id: str
    ) -> AsyncIterable[Dict[str, Any]]:
        """Stream fundamental analysis results."""
        logger.info(f'Fundamental Analyst analyzing: {query} (session: {context_id})')
        
        if not query:
            raise ValueError('Query cannot be empty')
        
        if not self.agent:
            await self.init_agent()
        
        try:
            yield {
                'is_task_complete': False,
                'require_user_input': False,
                'content': 'Fundamental Analyst: Retrieving SEC filings and financial data...'
            }
            
            async for chunk in self.runner.run_stream(
                self.agent, query, context_id
            ):
                if isinstance(chunk, dict) and chunk.get('type') == 'final_result':
                    response = chunk['response']
                    fundamental_data = self.format_response(response)
                    
                    # Calculate fundamental score if not provided
                    if 'fundamental_score' not in fundamental_data and 'financial_metrics' in fundamental_data:
                        fundamental_data['fundamental_score'] = self.calculate_fundamental_score(
                            fundamental_data['financial_metrics']
                        )
                    
                    yield {
                        'response_type': 'data',
                        'is_task_complete': True,
                        'require_user_input': False,
                        'content': fundamental_data
                    }
                else:
                    yield {
                        'is_task_complete': False,
                        'require_user_input': False,
                        'content': 'Fundamental Analyst: Analyzing financial statements...'
                    }
                    
        except Exception as e:
            logger.error(f'Error in fundamental analysis: {e}')
            yield {
                'response_type': 'text',
                'is_task_complete': True,
                'require_user_input': False,
                'content': f'Fundamental analysis error: {str(e)}'
            }

    async def invoke(self, query: str, session_id: str) -> dict:
        """Non-streaming invoke (not implemented)."""
        raise NotImplementedError('Please use the streaming interface')