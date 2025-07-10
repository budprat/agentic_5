"""Solopreneur Oracle agents for AI developer/entrepreneur intelligence."""

from .base_solopreneur_agent import UnifiedSolopreneurAgent
from .agent_registry import SOLOPRENEUR_AGENTS, create_agent, get_agents_by_tier, get_agent_count

# Import the Framework V2.0 compliant oracle agent if it exists
try:
    from .solopreneur_oracle_agent_adk import SolopreneurOracleAgent
except ImportError:
    # Use UnifiedSolopreneurAgent for the master oracle
    class SolopreneurOracleAgent(UnifiedSolopreneurAgent):
        def __init__(self):
            config = SOLOPRENEUR_AGENTS["SolopreneurOracle Master Agent"]
            super().__init__(
                agent_name="SolopreneurOracle Master Agent",
                description=config["description"],
                instructions=config["instructions"],
                port=config["port"]
            )

__all__ = [
    'UnifiedSolopreneurAgent',
    'SolopreneurOracleAgent', 
    'SOLOPRENEUR_AGENTS',
    'create_agent',
    'get_agents_by_tier',
    'get_agent_count'
]