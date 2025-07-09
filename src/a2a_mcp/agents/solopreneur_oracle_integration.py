"""Integration code for __main__.py - adds all 56 solopreneur agents."""

import logging

logger = logging.getLogger(__name__)

def add_solopreneur_agents_to_get_agent(get_agent_func):
    """Decorator to add all 56 solopreneur agents to get_agent function."""
    try:
        from a2a_mcp.agents.solopreneur_oracle.agent_registry import SOLOPRENEUR_AGENTS, create_agent
        
        def wrapped_get_agent(agent_card):
            # Check if it's a solopreneur agent
            if agent_card.name in SOLOPRENEUR_AGENTS:
                logger.info(f"Creating Solopreneur agent: {agent_card.name}")
                return create_agent(agent_card.name)
            
            # Otherwise use original function
            return get_agent_func(agent_card)
        
        # Log successful integration
        agent_count = len(SOLOPRENEUR_AGENTS)
        logger.info(f"Successfully integrated {agent_count} Solopreneur agents into agent factory")
        
        return wrapped_get_agent
    
    except ImportError as e:
        logger.warning(f"Could not import Solopreneur agents: {e}")
        # Return original function if import fails
        return get_agent_func