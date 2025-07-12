# ABOUTME: Test Cleanup Orchestrator - Tier 1 Master Orchestrator for cleanup domain
# ABOUTME: Uses MasterOrchestratorTemplate for sophisticated multi-agent coordination

from a2a_mcp.common.master_orchestrator_template import MasterOrchestratorTemplate
from a2a_mcp.common.quality_framework import QualityDomain


class CleanupMasterOrchestrator(MasterOrchestratorTemplate):
    """
    Test Cleanup Orchestrator - Master Orchestrator for cleanup domain.
    
    Framework V2.0 Tier 1 agent using MasterOrchestratorTemplate for sophisticated
    orchestration patterns with LangGraph integration and parallel workflow management.
    """
    
    def __init__(self):
        # Define domain specialists for cleanup
        domain_specialists = {
            "analysis_specialist": "Cleanup analysis and strategic assessment",
            "execution_specialist": "Cleanup implementation and operations",
            "optimization_specialist": "Cleanup optimization and improvement"
        }
        
        # Cleanup-specific planning instructions
        planning_instructions = f"""
You are the Test Cleanup Orchestrator Task Planner. Analyze cleanup requests and decompose them into coordinated tasks.

Domain Specialists Available:
- analysis_specialist: Cleanup analysis and strategic assessment
- execution_specialist: Cleanup implementation and operations  
- optimization_specialist: Cleanup optimization and improvement

For each cleanup request:
1. Analyze scope and identify relevant specialists
2. Create specific, actionable tasks for each domain specialist
3. Define coordination strategy (parallel/sequential based on dependencies)
4. Set quality requirements per domain
5. Identify optimization opportunities and synergies

Focus on cleanup-specific best practices and industry standards.
"""
        
        # Cleanup-specific synthesis prompt
        synthesis_prompt = f"""
You are the Test Cleanup Orchestrator Synthesis Agent. Synthesize cleanup intelligence into actionable insights.

Your cleanup capabilities:
- Cross-specialist intelligence analysis
- Cleanup strategy optimization
- Implementation planning with cleanup best practices
- Risk assessment and mitigation strategies

Provide structured cleanup recommendations with clear action plans and success metrics.
"""
        
        super().__init__(
            domain_name="Test Cleanup Orchestrator",
            domain_description="cleanup strategy and operations coordination",
            domain_specialists=domain_specialists,
            quality_domain=QualityDomain.BUSINESS,  # Adjust based on domain
            planning_instructions=planning_instructions,
            synthesis_prompt=synthesis_prompt,
            enable_parallel=True
        )


# Port assignment for cleanup domain: 10120
if __name__ == "__main__":
    import asyncio
    from a2a_mcp.common.agent_runner import AgentRunner
    
    async def main():
        agent = CleanupMasterOrchestrator()
        runner = AgentRunner()
        
        # Example usage
        query = "Develop a comprehensive cleanup strategy"
        context_id = "example_session"
        task_id = "example_task"
        
        async for result in agent.stream(query, context_id, task_id):
            print(f"Result: {result}")
    
    asyncio.run(main())
