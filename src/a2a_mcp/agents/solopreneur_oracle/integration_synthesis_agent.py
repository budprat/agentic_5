"""Integration Synthesis Agent - Domain Specialist for cross-domain connections and workflow optimization."""

from a2a_mcp.agents.solopreneur_oracle.base_solopreneur_agent import UnifiedSolopreneurAgent
from a2a_mcp.common import prompts

class IntegrationSynthesisAgent(UnifiedSolopreneurAgent):
    """
    Integration Synthesis Specialist for identifying cross-domain connections, 
    workflow optimization, and holistic strategy integration.
    
    Port: 10906 (Tier 2 - Domain Specialist)
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Integration Synthesis Agent",
            description="Identifies cross-domain connections, workflow optimization, and holistic strategy integration for AI developers and entrepreneurs",
            instructions=prompts.INTEGRATION_SYNTHESIS_COT_INSTRUCTIONS,
            port=10906
        )