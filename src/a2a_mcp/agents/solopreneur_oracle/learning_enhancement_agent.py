"""Learning Enhancement Agent - Domain Specialist for skill development and knowledge acquisition."""

from a2a_mcp.agents.solopreneur_oracle.base_solopreneur_agent import UnifiedSolopreneurAgent
from a2a_mcp.common import prompts

class LearningEnhancementAgent(UnifiedSolopreneurAgent):
    """
    Learning Enhancement Specialist for optimizing skill development, 
    knowledge acquisition, and learning velocity.
    
    Port: 10905 (Tier 2 - Domain Specialist)
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Learning Enhancement Agent",
            description="Optimizes skill development, knowledge acquisition, and learning velocity for AI developers and entrepreneurs",
            instructions=prompts.LEARNING_ENHANCEMENT_COT_INSTRUCTIONS,
            port=10905
        )