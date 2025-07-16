# ABOUTME: Advanced orchestration patterns combining Sequential, Parallel, and Loop agents
# ABOUTME: Shows complex multi-tier workflows using Google ADK patterns

import logging
from typing import List, Dict, Any, Optional
from google.adk.agents import SequentialAgent, ParallelAgent, LoopAgent, Agent
from google.adk.tools.agent_tool import AgentTool
from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from .tier2_domain_specialist import FinancialDomainSpecialist, TechnicalDomainSpecialist
from .tier3_service_agent import DataProcessingServiceAgent, APIIntegrationServiceAgent

logger = logging.getLogger(__name__)


class HybridOrchestrationPattern(StandardizedAgentBase):
    """
    Advanced orchestration pattern combining Sequential and Parallel execution.
    
    Pattern: Sequential stages with parallel execution within each stage.
    Use case: Multi-stage workflows where each stage has independent subtasks.
    """
    
    def __init__(self):
        super().__init__(
            agent_name="HybridOrchestrator",
            description="Combines sequential and parallel patterns for complex workflows",
            instructions="""
            You orchestrate multi-stage workflows with parallel execution within stages.
            
            Workflow pattern:
            Stage 1: Data Collection (Parallel)
            Stage 2: Analysis (Parallel) 
            Stage 3: Synthesis (Sequential)
            Stage 4: Quality Check (Loop)
            
            Optimize for efficiency while maintaining data consistency.
            """
        )
        
    async def init_agent(self):
        """Initialize hybrid orchestration pattern."""
        await super().init_agent()
        
        # Stage 1: Parallel data collection
        data_collection_agents = await self._create_data_collectors()
        stage1_parallel = ParallelAgent(
            name="DataCollectionStage",
            sub_agents=data_collection_agents,
            description="Collect data from multiple sources in parallel"
        )
        
        # Stage 2: Parallel analysis
        analysis_agents = await self._create_analysis_agents()
        stage2_parallel = ParallelAgent(
            name="AnalysisStage",
            sub_agents=analysis_agents,
            description="Analyze collected data in parallel"
        )
        
        # Stage 3: Sequential synthesis
        synthesis_agent = await self._create_synthesis_agent()
        
        # Stage 4: Loop-based quality check
        quality_loop = LoopAgent(
            name="QualityCheckLoop",
            max_iterations=3,
            sub_agents=[
                await self._create_quality_checker(),
                await self._create_quality_improver()
            ],
            description="Iteratively improve quality until standards are met"
        )
        
        # Main sequential pipeline
        self.adk_agent = SequentialAgent(
            name=self.agent_name,
            sub_agents=[
                stage1_parallel,
                stage2_parallel,
                synthesis_agent,
                quality_loop
            ],
            description=self.description
        )
        
    async def _create_data_collectors(self) -> List[Agent]:
        """Create parallel data collection agents."""
        return [
            Agent(
                name="MarketDataCollector",
                model="gemini-2.0-flash",
                instruction="Collect current market data from financial sources",
                tools=self.tools
            ),
            Agent(
                name="NewsDataCollector",
                model="gemini-2.0-flash",
                instruction="Collect relevant news and sentiment data",
                tools=self.tools
            ),
            Agent(
                name="HistoricalDataCollector",
                model="gemini-2.0-flash",
                instruction="Collect historical performance data",
                tools=self.tools
            )
        ]
        
    async def _create_analysis_agents(self) -> List[Agent]:
        """Create parallel analysis agents."""
        # Can use domain specialists
        financial_specialist = FinancialDomainSpecialist()
        await financial_specialist.init_agent()
        
        technical_specialist = TechnicalDomainSpecialist()
        await technical_specialist.init_agent()
        
        return [
            AgentTool(financial_specialist.adk_agent),
            AgentTool(technical_specialist.adk_agent),
            Agent(
                name="RiskAnalyzer",
                model="gemini-2.0-flash",
                instruction="Analyze risk factors and provide risk assessment",
                tools=[]
            )
        ]
        
    async def _create_synthesis_agent(self) -> Agent:
        """Create synthesis agent to combine analysis results."""
        return Agent(
            name="SynthesisAgent",
            model="gemini-2.0-flash",
            instruction="""
            Synthesize results from multiple analyses into a coherent report.
            Combine financial analysis, technical review, and risk assessment.
            Identify key insights and actionable recommendations.
            """,
            tools=[]
        )
        
    async def _create_quality_checker(self) -> Agent:
        """Create quality checking agent."""
        return Agent(
            name="QualityChecker",
            model="gemini-2.0-flash",
            instruction="""
            Check the synthesized report for:
            1. Completeness - all required sections present
            2. Accuracy - data and calculations correct
            3. Clarity - clear and understandable
            4. Actionability - concrete recommendations
            
            Output JSON with quality_score (0-100) and issues list.
            """,
            tools=[]
        )
        
    async def _create_quality_improver(self) -> Agent:
        """Create quality improvement agent."""
        return Agent(
            name="QualityImprover",
            model="gemini-2.0-flash",
            instruction="""
            Based on quality check results, improve the report:
            1. Fix identified issues
            2. Enhance clarity where needed
            3. Strengthen recommendations
            4. Add missing information
            
            Output improved report version.
            """,
            tools=[]
        )


class DynamicRoutingOrchestrator(StandardizedAgentBase):
    """
    Dynamic routing pattern that selects execution path based on input.
    
    Pattern: Conditional branching with different agent pipelines.
    Use case: Workflows that require different processing based on input type.
    """
    
    def __init__(self):
        super().__init__(
            agent_name="DynamicRoutingOrchestrator",
            description="Routes tasks dynamically based on input characteristics",
            instructions="""
            You are a dynamic routing orchestrator that:
            1. Analyzes incoming requests
            2. Determines the optimal processing path
            3. Routes to appropriate agent pipeline
            4. Handles results aggregation
            
            Support multiple domains: finance, technical, healthcare, general
            """
        )
        self.routing_pipelines = {}
        
    async def init_agent(self):
        """Initialize routing orchestrator with multiple pipelines."""
        await super().init_agent()
        
        # Create router agent
        self.router_agent = Agent(
            name="RouterAgent",
            model="gemini-2.0-flash",
            instruction="""
            Analyze the input request and determine:
            1. Domain (finance, technical, healthcare, general)
            2. Complexity (simple, moderate, complex)
            3. Priority (low, medium, high, critical)
            
            Output JSON with routing decision.
            """,
            tools=[]
        )
        
        # Initialize different pipelines
        await self._init_finance_pipeline()
        await self._init_technical_pipeline()
        await self._init_healthcare_pipeline()
        await self._init_general_pipeline()
        
    async def _init_finance_pipeline(self):
        """Initialize finance-specific pipeline."""
        # Simple finance tasks - single agent
        simple_finance = FinancialDomainSpecialist()
        await simple_finance.init_agent()
        
        # Complex finance tasks - multi-agent pipeline
        complex_finance = SequentialAgent(
            name="ComplexFinancePipeline",
            sub_agents=[
                DataProcessingServiceAgent(),  # Data prep
                simple_finance.adk_agent,      # Analysis
                Agent(                         # Report generation
                    name="FinanceReporter",
                    model="gemini-2.0-flash",
                    instruction="Generate comprehensive financial report",
                    tools=[]
                )
            ]
        )
        
        self.routing_pipelines['finance'] = {
            'simple': simple_finance,
            'complex': complex_finance
        }
        
    async def _init_technical_pipeline(self):
        """Initialize technical review pipeline."""
        # Parallel technical analysis
        technical_pipeline = ParallelAgent(
            name="TechnicalReviewPipeline",
            sub_agents=[
                Agent(
                    name="CodeAnalyzer",
                    model="gemini-2.0-flash",
                    instruction="Analyze code quality and patterns",
                    tools=self.tools
                ),
                Agent(
                    name="SecurityScanner",
                    model="gemini-2.0-flash",
                    instruction="Scan for security vulnerabilities",
                    tools=self.tools
                ),
                Agent(
                    name="PerformanceAnalyzer",
                    model="gemini-2.0-flash",
                    instruction="Analyze performance characteristics",
                    tools=self.tools
                )
            ]
        )
        
        self.routing_pipelines['technical'] = technical_pipeline
        
    async def _init_healthcare_pipeline(self):
        """Initialize healthcare pipeline (demonstration only)."""
        self.routing_pipelines['healthcare'] = Agent(
            name="HealthcareRouter",
            model="gemini-2.0-flash",
            instruction="Route to appropriate healthcare specialist (demo only)",
            tools=[]
        )
        
    async def _init_general_pipeline(self):
        """Initialize general-purpose pipeline."""
        self.routing_pipelines['general'] = Agent(
            name="GeneralProcessor",
            model="gemini-2.0-flash",
            instruction="Handle general requests with appropriate analysis",
            tools=self.tools
        )
        
    async def route_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Route request to appropriate pipeline."""
        # First, analyze request with router
        routing_decision = await self.router_agent.run(request)
        
        # Extract routing info
        domain = routing_decision.get('domain', 'general')
        complexity = routing_decision.get('complexity', 'simple')
        
        # Select appropriate pipeline
        if domain in self.routing_pipelines:
            pipeline = self.routing_pipelines[domain]
            
            # Handle complexity-based routing for finance
            if domain == 'finance' and isinstance(pipeline, dict):
                pipeline = pipeline.get(complexity, pipeline['simple'])
                
            # Execute pipeline
            result = await pipeline.run(request)
            
            return {
                'success': True,
                'domain': domain,
                'complexity': complexity,
                'result': result,
                'pipeline_used': pipeline.name if hasattr(pipeline, 'name') else 'unknown'
            }
            
        return {
            'success': False,
            'error': f"No pipeline available for domain: {domain}"
        }


class AdaptiveWorkflowOrchestrator(StandardizedAgentBase):
    """
    Adaptive workflow that modifies its execution based on intermediate results.
    
    Pattern: Dynamic pipeline modification during execution.
    Use case: Workflows that need to adapt based on discovered information.
    """
    
    def __init__(self):
        super().__init__(
            agent_name="AdaptiveWorkflowOrchestrator",
            description="Adapts workflow execution based on intermediate results",
            instructions="""
            You orchestrate adaptive workflows that:
            1. Start with initial analysis
            2. Adapt execution path based on findings
            3. Add or skip stages dynamically
            4. Optimize for efficiency and accuracy
            """
        )
        
    async def init_agent(self):
        """Initialize adaptive workflow orchestrator."""
        await super().init_agent()
        
        # Initial analysis agent
        self.initial_analyzer = Agent(
            name="InitialAnalyzer",
            model="gemini-2.0-flash",
            instruction="""
            Analyze the request and determine:
            1. Required depth of analysis (shallow, deep, comprehensive)
            2. Data availability (complete, partial, missing)
            3. Risk factors present (none, low, medium, high)
            4. Special requirements
            
            Output analysis results as JSON.
            """,
            tools=self.tools
        )
        
        # Pool of available agents for dynamic selection
        self.agent_pool = await self._create_agent_pool()
        
    async def _create_agent_pool(self) -> Dict[str, Agent]:
        """Create pool of agents for dynamic selection."""
        return {
            'data_enrichment': Agent(
                name="DataEnrichmentAgent",
                model="gemini-2.0-flash",
                instruction="Enrich incomplete data using available sources",
                tools=self.tools
            ),
            'deep_analysis': ParallelAgent(
                name="DeepAnalysisTeam",
                sub_agents=[
                    Agent(name="Analyst1", model="gemini-2.0-flash", 
                          instruction="Perform quantitative analysis", tools=[]),
                    Agent(name="Analyst2", model="gemini-2.0-flash",
                          instruction="Perform qualitative analysis", tools=[]),
                    Agent(name="Analyst3", model="gemini-2.0-flash",
                          instruction="Perform comparative analysis", tools=[])
                ]
            ),
            'risk_mitigation': LoopAgent(
                name="RiskMitigationLoop",
                max_iterations=5,
                sub_agents=[
                    Agent(name="RiskIdentifier", model="gemini-2.0-flash",
                          instruction="Identify and prioritize risks", tools=[]),
                    Agent(name="RiskMitigator", model="gemini-2.0-flash",
                          instruction="Propose and implement risk mitigations", tools=[])
                ]
            ),
            'validation': Agent(
                name="ValidationAgent",
                model="gemini-2.0-flash",
                instruction="Validate results against requirements and quality standards",
                tools=[]
            ),
            'optimization': Agent(
                name="OptimizationAgent",
                model="gemini-2.0-flash",
                instruction="Optimize results for performance and efficiency",
                tools=[]
            )
        }
        
    async def execute_adaptive_workflow(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute adaptive workflow based on analysis results."""
        # Step 1: Initial analysis
        analysis = await self.initial_analyzer.run(request)
        
        # Step 2: Build dynamic pipeline based on analysis
        pipeline_agents = []
        
        # Add data enrichment if needed
        if analysis.get('data_availability') == 'partial':
            pipeline_agents.append(self.agent_pool['data_enrichment'])
            
        # Add appropriate analysis depth
        if analysis.get('required_depth') in ['deep', 'comprehensive']:
            pipeline_agents.append(self.agent_pool['deep_analysis'])
            
        # Add risk mitigation if risks present
        if analysis.get('risk_factors') in ['medium', 'high']:
            pipeline_agents.append(self.agent_pool['risk_mitigation'])
            
        # Always add validation
        pipeline_agents.append(self.agent_pool['validation'])
        
        # Add optimization for comprehensive analysis
        if analysis.get('required_depth') == 'comprehensive':
            pipeline_agents.append(self.agent_pool['optimization'])
            
        # Step 3: Create and execute dynamic pipeline
        if len(pipeline_agents) > 1:
            dynamic_pipeline = SequentialAgent(
                name="DynamicPipeline",
                sub_agents=pipeline_agents,
                description="Dynamically constructed pipeline"
            )
            result = await dynamic_pipeline.run(request)
        elif len(pipeline_agents) == 1:
            result = await pipeline_agents[0].run(request)
        else:
            result = {"message": "No processing required based on analysis"}
            
        return {
            'success': True,
            'initial_analysis': analysis,
            'pipeline_length': len(pipeline_agents),
            'agents_used': [agent.name for agent in pipeline_agents],
            'result': result
        }


# Example usage demonstrating all patterns
async def demonstrate_advanced_patterns():
    """Demonstrate advanced orchestration patterns."""
    
    # 1. Hybrid orchestration (Sequential + Parallel + Loop)
    logger.info("=== Hybrid Orchestration Demo ===")
    hybrid = HybridOrchestrationPattern()
    await hybrid.init_agent()
    
    hybrid_request = {
        'task': 'comprehensive_market_analysis',
        'symbols': ['AAPL', 'GOOGL', 'MSFT'],
        'timeframe': '1Y',
        'include': ['technical', 'fundamental', 'sentiment']
    }
    
    # This would execute: Parallel data collection → Parallel analysis → 
    # Sequential synthesis → Loop quality check
    
    # 2. Dynamic routing based on input
    logger.info("=== Dynamic Routing Demo ===")
    router = DynamicRoutingOrchestrator()
    await router.init_agent()
    
    # Finance request
    finance_request = {
        'type': 'analysis',
        'domain_hint': 'finance',
        'data': {'portfolio': ['AAPL', 'GOOGL'], 'risk_tolerance': 'moderate'}
    }
    finance_result = await router.route_request(finance_request)
    
    # Technical request
    tech_request = {
        'type': 'review',
        'domain_hint': 'technical',
        'code_url': 'https://github.com/example/repo',
        'focus': ['security', 'performance']
    }
    tech_result = await router.route_request(tech_request)
    
    # 3. Adaptive workflow
    logger.info("=== Adaptive Workflow Demo ===")
    adaptive = AdaptiveWorkflowOrchestrator()
    await adaptive.init_agent()
    
    # Request that triggers adaptation
    adaptive_request = {
        'objective': 'market_opportunity_analysis',
        'data_completeness': 'partial',
        'risk_tolerance': 'low',
        'depth_required': 'comprehensive'
    }
    
    # This would dynamically build pipeline based on initial analysis
    adaptive_result = await adaptive.execute_adaptive_workflow(adaptive_request)
    
    logger.info(f"Adaptive pipeline used {len(adaptive_result['agents_used'])} agents")
    logger.info(f"Agents: {adaptive_result['agents_used']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demonstrate_advanced_patterns())