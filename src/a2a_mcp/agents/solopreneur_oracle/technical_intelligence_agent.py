"""Technical Intelligence Agent - Domain Specialist for AI developers and entrepreneurs."""

from a2a_mcp.agents.solopreneur_oracle.base_solopreneur_agent import UnifiedSolopreneurAgent
from a2a_mcp.common import prompts

class TechnicalIntelligenceAgent(UnifiedSolopreneurAgent):
    """
    Technical Intelligence Specialist for evaluating technical feasibility, 
    architectural decisions, and implementation strategies.
    
    Port: 10902 (Tier 2 - Domain Specialist)
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Technical Intelligence Agent",
            description="Analyzes technical feasibility, architectural decisions, and implementation strategies for AI developers and entrepreneurs",
            instructions=prompts.TECHNICAL_INTELLIGENCE_COT_INSTRUCTIONS,
            port=10902
        )