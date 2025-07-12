# ABOUTME: Healthcare Master Orchestrator - Tier 1 Master Orchestrator for healthcare domain
# ABOUTME: Uses MasterOrchestratorTemplate for sophisticated multi-agent coordination

from a2a_mcp.common.master_orchestrator_template import MasterOrchestratorTemplate
from a2a_mcp.common.quality_framework import QualityDomain


class HealthcareMasterOrchestrator(MasterOrchestratorTemplate):
    """
    Healthcare Master Orchestrator - Master Orchestrator for healthcare domain.
    
    Framework V2.0 Tier 1 agent using MasterOrchestratorTemplate for sophisticated
    orchestration patterns with LangGraph integration and parallel workflow management.
    """
    
    def __init__(self):
        # Define domain specialists for healthcare
        domain_specialists = {
            "analysis_specialist": "Healthcare analysis and strategic assessment",
            "execution_specialist": "Healthcare implementation and operations",
            "optimization_specialist": "Healthcare optimization and improvement"
        }
        
        # Healthcare-specific planning instructions
        planning_instructions = f"""
You are the Healthcare Master Orchestrator Task Planner. Analyze healthcare requests and decompose them into coordinated tasks.

Domain Specialists Available:
- analysis_specialist: Healthcare analysis and strategic assessment
- execution_specialist: Healthcare implementation and operations  
- optimization_specialist: Healthcare optimization and improvement

For each healthcare request:
1. Analyze scope and identify relevant specialists
2. Create specific, actionable tasks for each domain specialist
3. Define coordination strategy (parallel/sequential based on dependencies)
4. Set quality requirements per domain
5. Identify optimization opportunities and synergies

Focus on healthcare-specific best practices and industry standards.
"""
        
        # Healthcare-specific synthesis prompt
        synthesis_prompt = f"""
You are the Healthcare Master Orchestrator Synthesis Agent. Synthesize healthcare intelligence into actionable insights.

Your healthcare capabilities:
- Cross-specialist intelligence analysis
- Healthcare strategy optimization
- Implementation planning with healthcare best practices
- Risk assessment and mitigation strategies

Provide structured healthcare recommendations with clear action plans and success metrics.
"""
        
        super().__init__(
            domain_name="Healthcare Master Orchestrator",
            domain_description="healthcare strategy and operations coordination",
            domain_specialists=domain_specialists,
            quality_domain=QualityDomain.BUSINESS,  # Adjust based on domain
            planning_instructions=planning_instructions,
            synthesis_prompt=synthesis_prompt,
            enable_parallel=True
        )


# Port assignment for healthcare domain: 10100
if __name__ == "__main__":
    import asyncio
    from a2a_mcp.common.agent_runner import AgentRunner
    
    async def main():
        agent = HealthcareMasterOrchestrator()
        runner = AgentRunner()
        
        # Example usage
        query = "Develop a comprehensive healthcare strategy"
        context_id = "example_session"
        task_id = "example_task"
        
        async for result in agent.stream(query, context_id, task_id):
            print(f"Result: {result}")
    
    asyncio.run(main())
