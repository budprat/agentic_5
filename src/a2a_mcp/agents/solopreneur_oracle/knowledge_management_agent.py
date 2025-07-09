"""Knowledge Management Agent - Domain Specialist for information organization and learning systems."""

from a2a_mcp.agents.solopreneur_oracle.base_solopreneur_agent import UnifiedSolopreneurAgent
from a2a_mcp.common import prompts

class KnowledgeManagementAgent(UnifiedSolopreneurAgent):
    """
    Knowledge Management Specialist for optimizing information organization, 
    learning systems, and knowledge synthesis.
    
    Port: 10903 (Tier 2 - Domain Specialist)
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Knowledge Management Agent",
            description="Optimizes information organization, learning systems, and knowledge synthesis for AI developers and entrepreneurs",
            instructions=prompts.KNOWLEDGE_MANAGEMENT_COT_INSTRUCTIONS,
            port=10903
        )