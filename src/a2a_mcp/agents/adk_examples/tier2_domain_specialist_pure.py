# ABOUTME: Pure ADK implementation of Tier 2 Domain Specialist with structured outputs
# ABOUTME: Shows how to create domain experts with validated response schemas using only Google ADK

import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent
from datetime import datetime

logger = logging.getLogger(__name__)


# Define structured output schemas for different domains
class MarketAnalysis(BaseModel):
    """Structured output for financial market analysis."""
    market_trend: str = Field(description="Current market trend: bullish, bearish, or neutral")
    key_indicators: List[Dict[str, float]] = Field(description="Key market indicators and values")
    risk_assessment: str = Field(description="Overall risk level: low, medium, high, critical")
    confidence_score: float = Field(description="Confidence in analysis (0.0-1.0)")
    recommendations: List[str] = Field(description="Actionable recommendations")
    analysis_timestamp: str = Field(description="ISO timestamp of analysis")
    supporting_data: Dict[str, Any] = Field(description="Additional supporting data")


class TechnicalReview(BaseModel):
    """Structured output for technical code/architecture review."""
    review_type: str = Field(description="Type of review: code, architecture, security, performance")
    overall_score: float = Field(description="Overall quality score (0-100)")
    strengths: List[str] = Field(description="Identified strengths")
    issues: List[Dict[str, str]] = Field(description="Issues with severity and description")
    recommendations: List[Dict[str, str]] = Field(description="Improvement recommendations with priority")
    compliance_status: Dict[str, bool] = Field(description="Compliance with standards")
    metrics: Dict[str, float] = Field(description="Relevant metrics")


class HealthAssessment(BaseModel):
    """Structured output for healthcare domain analysis."""
    assessment_type: str = Field(description="Type of health assessment")
    risk_factors: List[Dict[str, str]] = Field(description="Identified risk factors")
    recommendations: List[str] = Field(description="Health recommendations")
    urgency_level: str = Field(description="Urgency: routine, urgent, emergency")
    follow_up_required: bool = Field(description="Whether follow-up is needed")
    referrals: List[str] = Field(description="Recommended specialist referrals")
    confidence_level: float = Field(description="Confidence in assessment (0.0-1.0)")


class FinancialDomainSpecialistPure:
    """
    Tier 2 Financial Domain Specialist with structured outputs.
    Pure ADK implementation without StandardizedAgentBase dependencies.
    
    Provides expert financial analysis with validated response schemas.
    """
    
    def __init__(self):
        self.agent_name = "FinancialDomainSpecialist"
        self.description = "Expert financial analysis with market insights"
        self.instructions = """
        You are a senior financial analyst with expertise in:
        - Market trend analysis
        - Risk assessment
        - Investment strategies
        - Economic indicators
        - Portfolio optimization
        
        Provide detailed, data-driven analysis with clear recommendations.
        Always include confidence scores and supporting data.
        Consider both technical and fundamental factors.
        """
        self.adk_agent = None
        
    async def init_agent(self):
        """Initialize financial specialist with structured output."""
        logger.info(f"Initializing {self.agent_name}")
        
        self.adk_agent = LlmAgent(
            name=self.agent_name,
            model="gemini-2.0-flash",
            instruction=self.instructions,
            output_schema=MarketAnalysis,
            output_key="market_analysis",
            temperature=0.4  # Lower temperature for more consistent analysis
        )
        
        logger.info(f"{self.agent_name} initialized successfully")
        
    async def analyze_market(self, market_data: Dict[str, Any]) -> MarketAnalysis:
        """Perform market analysis with structured output."""
        try:
            # Prepare analysis request
            analysis_request = f"""
            Analyze the following market data and provide comprehensive insights:
            
            Market Data:
            {market_data}
            
            Consider:
            1. Current market trends and momentum
            2. Key economic indicators
            3. Risk factors and volatility
            4. Investment opportunities
            5. Short-term and long-term outlook
            """
            
            # Execute analysis
            result = await self.adk_agent.run(analysis_request)
            
            logger.info(f"Market analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Market analysis failed: {e}")
            # Return default analysis on error
            return MarketAnalysis(
                market_trend="unknown",
                key_indicators=[],
                risk_assessment="high",
                confidence_score=0.0,
                recommendations=["Unable to complete analysis due to error"],
                analysis_timestamp=datetime.now().isoformat(),
                supporting_data={"error": str(e)}
            )


class TechnicalDomainSpecialistPure:
    """
    Tier 2 Technical Domain Specialist for code and architecture review.
    Pure ADK implementation.
    """
    
    def __init__(self):
        self.agent_name = "TechnicalDomainSpecialist"
        self.description = "Expert technical review and architecture analysis"
        self.instructions = """
        You are a senior technical architect and code reviewer with expertise in:
        - Software architecture patterns
        - Code quality and best practices
        - Security vulnerabilities
        - Performance optimization
        - Scalability and reliability
        
        Provide thorough technical reviews with actionable recommendations.
        Use industry standards and best practices as benchmarks.
        """
        self.adk_agent = None
        
    async def init_agent(self):
        """Initialize technical specialist."""
        logger.info(f"Initializing {self.agent_name}")
        
        self.adk_agent = LlmAgent(
            name=self.agent_name,
            model="gemini-2.5-pro",  # Use more powerful model for technical analysis
            instruction=self.instructions,
            output_schema=TechnicalReview,
            output_key="technical_review",
            temperature=0.3  # Very low temperature for consistent technical analysis
        )
        
        logger.info(f"{self.agent_name} initialized successfully")
        
    async def review_code(self, code_context: Dict[str, Any]) -> TechnicalReview:
        """Perform technical review with structured output."""
        try:
            review_request = f"""
            Perform a comprehensive technical review of the following:
            
            Code/Architecture Context:
            {code_context}
            
            Evaluate:
            1. Code quality and maintainability
            2. Architecture patterns and design decisions
            3. Security vulnerabilities and risks
            4. Performance bottlenecks
            5. Scalability concerns
            6. Testing coverage and quality
            7. Documentation completeness
            """
            
            result = await self.adk_agent.run(review_request)
            return result
            
        except Exception as e:
            logger.error(f"Technical review failed: {e}")
            return TechnicalReview(
                review_type="error",
                overall_score=0.0,
                strengths=[],
                issues=[{"severity": "critical", "description": f"Review failed: {str(e)}"}],
                recommendations=[],
                compliance_status={},
                metrics={}
            )


class HealthcareDomainSpecialistPure:
    """
    Tier 2 Healthcare Domain Specialist for medical assessments.
    Pure ADK implementation.
    
    Note: This is for demonstration only. Real healthcare applications
    require proper medical certification and compliance.
    """
    
    def __init__(self):
        self.agent_name = "HealthcareDomainSpecialist"
        self.description = "Healthcare assessment and recommendation specialist"
        self.instructions = """
        You are a healthcare assessment specialist. Your role is to:
        - Analyze health-related information
        - Identify potential risk factors
        - Provide general health recommendations
        - Suggest when professional medical consultation is needed
        
        IMPORTANT: Always include disclaimers that this is not a substitute
        for professional medical advice. Recommend consulting healthcare
        providers for actual medical decisions.
        """
        self.adk_agent = None
        
    async def init_agent(self):
        """Initialize healthcare specialist."""
        logger.info(f"Initializing {self.agent_name}")
        
        self.adk_agent = LlmAgent(
            name=self.agent_name,
            model="gemini-2.5-pro",  # Use best model for healthcare
            instruction=self.instructions,
            output_schema=HealthAssessment,
            output_key="health_assessment",
            temperature=0.2  # Very low temperature for healthcare consistency
        )
        
        logger.info(f"{self.agent_name} initialized successfully")
        
    async def assess_health(self, health_data: Dict[str, Any]) -> HealthAssessment:
        """Perform health assessment with structured output."""
        try:
            assessment_request = f"""
            Perform a health assessment based on the following information:
            
            Health Data:
            {health_data}
            
            Provide:
            1. Risk factor identification
            2. General health recommendations
            3. Urgency level assessment
            4. Referral suggestions if needed
            
            Remember to include appropriate disclaimers about seeking
            professional medical advice.
            """
            
            result = await self.adk_agent.run(assessment_request)
            return result
            
        except Exception as e:
            logger.error(f"Health assessment failed: {e}")
            return HealthAssessment(
                assessment_type="error",
                risk_factors=[],
                recommendations=["Unable to complete assessment due to error"],
                urgency_level="unknown",
                follow_up_required=True,
                referrals=["Consult healthcare provider"],
                confidence_level=0.0
            )


class MultiDomainCoordinatorPure:
    """
    Example of coordinating multiple domain specialists.
    Pure ADK implementation.
    """
    
    def __init__(self):
        self.agent_name = "MultiDomainCoordinator"
        self.description = "Coordinates multiple domain specialists for comprehensive analysis"
        self.specialists = {}
        
    async def init_agent(self):
        """Initialize coordinator and specialists."""
        logger.info(f"Initializing {self.agent_name}")
        
        # Initialize all domain specialists
        self.specialists['finance'] = FinancialDomainSpecialistPure()
        self.specialists['technical'] = TechnicalDomainSpecialistPure()
        self.specialists['healthcare'] = HealthcareDomainSpecialistPure()
        
        # Initialize each specialist
        for name, specialist in self.specialists.items():
            logger.info(f"Initializing specialist: {name}")
            await specialist.init_agent()
            
        logger.info(f"{self.agent_name} initialized with {len(self.specialists)} specialists")
            
    async def route_to_specialist(self, request: Dict[str, Any]) -> Any:
        """Route request to appropriate specialist."""
        domain = request.get('domain', '').lower()
        
        if domain in self.specialists:
            specialist = self.specialists[domain]
            
            if domain == 'finance':
                return await specialist.analyze_market(request.get('data', {}))
            elif domain == 'technical':
                return await specialist.review_code(request.get('data', {}))
            elif domain == 'healthcare':
                return await specialist.assess_health(request.get('data', {}))
                
        raise ValueError(f"Unknown domain: {domain}")


# Example usage
async def main():
    """Demonstrate domain specialist usage."""
    # Financial analysis example
    financial_specialist = FinancialDomainSpecialistPure()
    await financial_specialist.init_agent()
    
    market_data = {
        'indices': {
            'SP500': 4500.50,
            'NASDAQ': 14200.75,
            'DJI': 35000.25
        },
        'volatility': 'moderate',
        'economic_indicators': {
            'inflation': 3.2,
            'unemployment': 4.1,
            'gdp_growth': 2.8
        },
        'sector_performance': {
            'technology': '+2.5%',
            'healthcare': '+1.2%',
            'energy': '-0.8%'
        }
    }
    
    analysis = await financial_specialist.analyze_market(market_data)
    
    print(f"Market Trend: {analysis.market_trend}")
    print(f"Risk Level: {analysis.risk_assessment}")
    print(f"Confidence: {analysis.confidence_score}")
    print(f"Recommendations:")
    for rec in analysis.recommendations:
        print(f"  - {rec}")
        
    # Technical review example
    technical_specialist = TechnicalDomainSpecialistPure()
    await technical_specialist.init_agent()
    
    code_context = {
        'language': 'Python',
        'framework': 'FastAPI',
        'description': 'RESTful API for user management',
        'metrics': {
            'lines_of_code': 2500,
            'test_coverage': 85,
            'complexity': 'moderate'
        },
        'concerns': [
            'Response time increasing with user growth',
            'Some endpoints lack proper error handling',
            'Authentication using outdated library'
        ]
    }
    
    review = await technical_specialist.review_code(code_context)
    
    print(f"\nTechnical Review Score: {review.overall_score}/100")
    print(f"Strengths:")
    for strength in review.strengths:
        print(f"  - {strength}")
    print(f"Issues Found: {len(review.issues)}")
    
    # Multi-domain coordination example
    coordinator = MultiDomainCoordinatorPure()
    await coordinator.init_agent()
    
    finance_request = {
        'domain': 'finance',
        'data': market_data
    }
    
    result = await coordinator.route_to_specialist(finance_request)
    print(f"\nCoordinated Analysis: {result.market_trend}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())