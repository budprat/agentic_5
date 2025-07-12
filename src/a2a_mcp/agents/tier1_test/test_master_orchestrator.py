# ABOUTME: Test Orchestrator - Tier 1 Master Orchestrator for test domain
# ABOUTME: Uses MasterOrchestratorTemplate for sophisticated multi-agent coordination

from a2a_mcp.common.master_orchestrator_template import MasterOrchestratorTemplate
from a2a_mcp.common.quality_framework import QualityDomain


class TestMasterOrchestrator(MasterOrchestratorTemplate):
    """
    Test Orchestrator - Master Orchestrator for test domain.
    
    Framework V2.0 Tier 1 agent using MasterOrchestratorTemplate for sophisticated
    orchestration patterns with LangGraph integration and parallel workflow management.
    """
    
    def __init__(self):
        # Define domain specialists for test
        domain_specialists = {
            "analysis_specialist": "Test analysis and strategic assessment",
            "execution_specialist": "Test implementation and operations",
            "optimization_specialist": "Test optimization and improvement"
        }
        
        # Test-specific planning instructions
        planning_instructions = f"""
You are the Test Orchestrator Task Planner. Analyze test requests and decompose them into coordinated tasks.

Domain Specialists Available:
- analysis_specialist: Test analysis and strategic assessment
- execution_specialist: Test implementation and operations  
- optimization_specialist: Test optimization and improvement

For each test request:
1. Analyze scope and identify relevant specialists
2. Create specific, actionable tasks for each domain specialist
3. Define coordination strategy (parallel/sequential based on dependencies)
4. Set quality requirements per domain
5. Identify optimization opportunities and synergies

Focus on test-specific best practices and industry standards.
"""
        
        # Test-specific synthesis prompt
        synthesis_prompt = f"""
You are the Test Orchestrator Synthesis Agent. Synthesize test intelligence into actionable insights.

Your test capabilities:
- Cross-specialist intelligence analysis
- Test strategy optimization
- Implementation planning with test best practices
- Risk assessment and mitigation strategies

Provide structured test recommendations with clear action plans and success metrics.
"""
        
        super().__init__(
            domain_name="Test Orchestrator",
            domain_description="test strategy and operations coordination",
            domain_specialists=domain_specialists,
            quality_domain=QualityDomain.BUSINESS,  # Adjust based on domain
            planning_instructions=planning_instructions,
            synthesis_prompt=synthesis_prompt,
            enable_parallel=True
        )


# Port assignment for test domain: 10110
if __name__ == "__main__":
    import asyncio
    from a2a_mcp.common.agent_runner import AgentRunner
    
    async def main():
        agent = TestMasterOrchestrator()
        runner = AgentRunner()
        
        # Example usage
        query = "Develop a comprehensive test strategy"
        context_id = "example_session"
        task_id = "example_task"
        
        async for result in agent.stream(query, context_id, task_id):
            print(f"Result: {result}")
    
    asyncio.run(main())
