# ABOUTME: Complete example system using Google ADK agents across all tiers
# ABOUTME: Demonstrates a full multi-agent system for investment analysis

import logging
import asyncio
from typing import Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field

# ADK imports
from google.adk.agents import SequentialAgent, ParallelAgent, LoopAgent, Agent, LlmAgent
from google.adk.tools import grounding, code_execution
from google.adk.tools.agent_tool import AgentTool

# A2A Framework imports
from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.common.quality_framework import QualityDomain
from a2a_mcp.common.a2a_protocol import A2AProtocolClient

logger = logging.getLogger(__name__)


# Structured output schemas
class InvestmentRecommendation(BaseModel):
    """Final investment recommendation structure."""
    ticker: str = Field(description="Stock ticker symbol")
    recommendation: str = Field(description="BUY, HOLD, or SELL")
    confidence: float = Field(description="Confidence score 0-1")
    target_price: float = Field(description="12-month target price")
    risk_level: str = Field(description="LOW, MEDIUM, HIGH")
    rationale: str = Field(description="Investment rationale")
    key_factors: List[str] = Field(description="Key decision factors")


class MarketSentiment(BaseModel):
    """Market sentiment analysis structure."""
    overall_sentiment: str = Field(description="BULLISH, BEARISH, NEUTRAL")
    sentiment_score: float = Field(description="Sentiment score -1 to 1")
    key_themes: List[str] = Field(description="Major market themes")
    risk_indicators: List[str] = Field(description="Risk indicators")


class CompanyFinancials(BaseModel):
    """Company financial analysis structure."""
    revenue_growth: float = Field(description="Year-over-year revenue growth %")
    profit_margin: float = Field(description="Net profit margin %")
    debt_to_equity: float = Field(description="Debt-to-equity ratio")
    pe_ratio: float = Field(description="Price-to-earnings ratio")
    financial_health: str = Field(description="STRONG, MODERATE, WEAK")


# Complete Investment Analysis System
class InvestmentAnalysisSystem:
    """
    Complete multi-agent system for investment analysis.
    
    Architecture:
    - Tier 1: Master Investment Orchestrator (Sequential + Parallel)
    - Tier 2: Domain Specialists (Financial, Market, Risk)
    - Tier 3: Service Agents (Data, News, Computation)
    
    Workflow:
    1. Data Collection (Parallel)
    2. Analysis (Parallel with specialists)
    3. Risk Assessment (Sequential)
    4. Recommendation Generation (Loop for quality)
    5. Final Report Assembly
    """
    
    def __init__(self):
        self.orchestrator = None
        self.specialists = {}
        self.service_agents = {}
        self.a2a_client = A2AProtocolClient()
        
    async def initialize(self):
        """Initialize the complete system."""
        logger.info("Initializing Investment Analysis System")
        
        # Initialize Tier 3 Service Agents
        await self._init_service_agents()
        
        # Initialize Tier 2 Domain Specialists
        await self._init_domain_specialists()
        
        # Initialize Tier 1 Master Orchestrator
        await self._init_orchestrator()
        
        logger.info("System initialization complete")
        
    async def _init_service_agents(self):
        """Initialize Tier 3 service agents."""
        # Market Data Service
        self.service_agents['market_data'] = Agent(
            name="MarketDataService",
            model="gemini-1.5-flash-8b",  # Lightweight for simple data tasks
            instruction="""
            You are a market data service agent. Fetch and format:
            - Current stock prices and volume
            - Historical price data
            - Market indicators (VIX, sector performance)
            - Trading patterns and technical indicators
            
            Use the grounding tool to get real-time data.
            Output structured JSON with all requested data.
            """,
            tools=[grounding]  # Using grounding for real-time data
        )
        
        # News Aggregation Service
        self.service_agents['news_service'] = Agent(
            name="NewsAggregationService",
            model="gemini-1.5-flash-8b",
            instruction="""
            You are a news aggregation service. Collect and summarize:
            - Recent company news and press releases
            - Industry news and trends
            - Analyst reports and ratings
            - Social media sentiment
            
            Focus on information from the last 30 days.
            Output structured news summary with sources.
            """,
            tools=[grounding]
        )
        
        # Financial Computation Service
        self.service_agents['computation'] = Agent(
            name="FinancialComputationService",
            model="gemini-2.0-flash",
            instruction="""
            You are a financial computation service. Calculate:
            - Financial ratios (PE, PEG, ROE, etc.)
            - Growth rates and trends
            - Risk metrics (beta, volatility)
            - Valuation models (DCF, comparables)
            
            Use code execution for complex calculations.
            Ensure accuracy in all computations.
            """,
            tools=[code_execution]  # For financial calculations
        )
        
    async def _init_domain_specialists(self):
        """Initialize Tier 2 domain specialists."""
        # Financial Analysis Specialist
        self.specialists['financial'] = LlmAgent(
            name="FinancialAnalysisSpecialist",
            model="gemini-2.0-flash",
            instruction="""
            You are a senior financial analyst specializing in fundamental analysis.
            
            Analyze company financials including:
            - Revenue trends and growth drivers
            - Profitability and margin analysis
            - Balance sheet strength
            - Cash flow analysis
            - Competitive positioning
            
            Provide expert insights on financial health and valuation.
            """,
            output_schema=CompanyFinancials,
            output_key="financial_analysis"
        )
        
        # Market Sentiment Specialist
        self.specialists['sentiment'] = LlmAgent(
            name="MarketSentimentSpecialist",
            model="gemini-2.0-flash",
            instruction="""
            You are a market sentiment analysis expert.
            
            Analyze market sentiment based on:
            - News sentiment and media coverage
            - Analyst recommendations
            - Social media trends
            - Market momentum indicators
            - Insider trading patterns
            
            Provide nuanced sentiment analysis with supporting evidence.
            """,
            output_schema=MarketSentiment,
            output_key="sentiment_analysis"
        )
        
        # Risk Assessment Specialist
        self.specialists['risk'] = Agent(
            name="RiskAssessmentSpecialist",
            model="gemini-2.5-pro",  # Best model for risk analysis
            instruction="""
            You are a risk management specialist.
            
            Assess investment risks including:
            - Market risk and volatility
            - Company-specific risks
            - Industry and sector risks
            - Regulatory and compliance risks
            - Macroeconomic risks
            
            Provide comprehensive risk assessment with mitigation strategies.
            Output detailed risk analysis in JSON format.
            """,
            tools=[]
        )
        
    async def _init_orchestrator(self):
        """Initialize Tier 1 master orchestrator."""
        # Stage 1: Parallel Data Collection
        data_collection = ParallelAgent(
            name="DataCollectionStage",
            sub_agents=[
                self.service_agents['market_data'],
                self.service_agents['news_service'],
                self.service_agents['computation']
            ],
            description="Collect all required data in parallel"
        )
        
        # Stage 2: Parallel Domain Analysis
        domain_analysis = ParallelAgent(
            name="DomainAnalysisStage",
            sub_agents=[
                AgentTool(self.specialists['financial']),
                AgentTool(self.specialists['sentiment']),
                self.specialists['risk']
            ],
            description="Perform specialized analysis in parallel"
        )
        
        # Stage 3: Integration and Synthesis
        synthesis_agent = Agent(
            name="AnalysisSynthesizer",
            model="gemini-2.0-flash",
            instruction="""
            You are an investment analysis synthesizer.
            
            Integrate results from:
            - Financial analysis
            - Market sentiment
            - Risk assessment
            
            Create a coherent investment thesis considering all factors.
            Identify key investment drivers and concerns.
            """,
            tools=[]
        )
        
        # Stage 4: Recommendation Generation with Quality Loop
        recommendation_agent = LlmAgent(
            name="RecommendationGenerator",
            model="gemini-2.5-pro",
            instruction="""
            You are a senior investment advisor.
            
            Based on the comprehensive analysis, generate investment recommendation:
            - Clear BUY/HOLD/SELL recommendation
            - 12-month price target with rationale
            - Risk-adjusted position sizing
            - Key catalysts and risks
            - Investment timeline
            
            Ensure recommendations are actionable and well-supported.
            """,
            output_schema=InvestmentRecommendation,
            output_key="recommendation"
        )
        
        quality_checker = Agent(
            name="QualityValidator",
            model="gemini-2.0-flash",
            instruction="""
            Validate investment recommendations for:
            - Logical consistency
            - Supporting evidence
            - Risk/reward balance
            - Regulatory compliance
            
            Output validation score (0-100) and any issues found.
            """,
            tools=[]
        )
        
        recommendation_loop = LoopAgent(
            name="RecommendationQualityLoop",
            max_iterations=3,
            sub_agents=[recommendation_agent, quality_checker],
            description="Iteratively improve recommendation quality"
        )
        
        # Stage 5: Final Report Assembly
        report_generator = Agent(
            name="InvestmentReportGenerator",
            model="gemini-2.0-flash",
            instruction="""
            Create a professional investment report including:
            - Executive summary
            - Investment recommendation
            - Detailed analysis sections
            - Risk disclosures
            - Supporting data and charts
            
            Format for institutional investors.
            """,
            tools=[]
        )
        
        # Master Orchestrator Pipeline
        self.orchestrator = SequentialAgent(
            name="InvestmentAnalysisOrchestrator",
            sub_agents=[
                data_collection,
                domain_analysis,
                synthesis_agent,
                recommendation_loop,
                report_generator
            ],
            description="Complete investment analysis workflow",
            before_agent_callback=self._orchestrator_callback,
            after_agent_callback=self._orchestrator_callback
        )
        
    async def _orchestrator_callback(self, agent_name: str, data: Any) -> Any:
        """Callback for orchestrator stages."""
        logger.info(f"Orchestrator stage: {agent_name}")
        
        # Can add stage-specific logic here
        if agent_name == "DataCollectionStage":
            logger.info("Data collection complete, validating data quality")
        elif agent_name == "DomainAnalysisStage":
            logger.info("Domain analysis complete, checking for conflicts")
        elif agent_name == "RecommendationQualityLoop":
            logger.info("Generating final recommendation")
            
        return data
        
    async def analyze_investment(self, ticker: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze an investment opportunity.
        
        Args:
            ticker: Stock ticker symbol
            context: Additional context (portfolio, risk tolerance, etc.)
            
        Returns:
            Complete investment analysis and recommendation
        """
        try:
            # Prepare analysis request
            request = {
                'ticker': ticker,
                'analysis_date': datetime.now().isoformat(),
                'context': context or {},
                'requirements': {
                    'depth': 'comprehensive',
                    'include_technicals': True,
                    'include_comparables': True,
                    'risk_assessment': 'detailed'
                }
            }
            
            # Execute orchestrated analysis
            logger.info(f"Starting investment analysis for {ticker}")
            result = await self.orchestrator.run(request)
            
            # Send result to other agents if A2A is enabled
            if context and context.get('notify_portfolio_manager'):
                await self.a2a_client.send_message(
                    target_agent_port=context['portfolio_manager_port'],
                    message=f"Investment analysis complete for {ticker}",
                    metadata={'ticker': ticker, 'recommendation': result.get('recommendation')}
                )
            
            return {
                'success': True,
                'ticker': ticker,
                'analysis': result,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Investment analysis failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'ticker': ticker
            }
            
    async def batch_analysis(self, tickers: List[str]) -> Dict[str, Any]:
        """Analyze multiple investments in parallel."""
        # Create parallel analysis tasks
        tasks = [self.analyze_investment(ticker) for ticker in tickers]
        
        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        successful = [r for r in results if isinstance(r, dict) and r.get('success')]
        failed = [r for r in results if isinstance(r, Exception) or not r.get('success')]
        
        return {
            'total': len(tickers),
            'successful': len(successful),
            'failed': len(failed),
            'results': successful,
            'errors': failed
        }


# Example usage
async def main():
    """Demonstrate the complete investment analysis system."""
    # Initialize system
    system = InvestmentAnalysisSystem()
    await system.initialize()
    
    # Single stock analysis
    logger.info("=== Single Stock Analysis ===")
    result = await system.analyze_investment(
        ticker="AAPL",
        context={
            'portfolio_size': 100000,
            'risk_tolerance': 'moderate',
            'investment_horizon': '12 months',
            'existing_positions': ['MSFT', 'GOOGL']
        }
    )
    
    if result['success']:
        analysis = result['analysis']
        logger.info(f"Analysis complete for {result['ticker']}")
        # In real implementation, would extract recommendation details
        
    # Batch analysis for portfolio review
    logger.info("\n=== Batch Portfolio Analysis ===")
    portfolio_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    batch_results = await system.batch_analysis(portfolio_tickers)
    
    logger.info(f"Analyzed {batch_results['successful']} stocks successfully")
    logger.info(f"Failed analyses: {batch_results['failed']}")
    
    # Example of using A2A to notify portfolio manager
    if result['success']:
        # This would send results to portfolio management agent
        # await system.a2a_client.send_message(...)
        pass


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the example
    asyncio.run(main())