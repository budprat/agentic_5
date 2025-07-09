"""Personal Optimization Agent - Domain Specialist for productivity and energy management."""

from a2a_mcp.agents.solopreneur_oracle.base_solopreneur_agent import UnifiedSolopreneurAgent
from a2a_mcp.common import prompts

class PersonalOptimizationAgent(UnifiedSolopreneurAgent):
    """
    Personal Optimization Specialist for enhancing productivity, energy management, 
    and sustainable performance.
    
    Port: 10904 (Tier 2 - Domain Specialist)
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Personal Optimization Agent",
            description="Enhances productivity, energy management, and sustainable performance for AI developers and entrepreneurs",
            instructions=prompts.PERSONAL_OPTIMIZATION_COT_INSTRUCTIONS,
            port=10904
        )