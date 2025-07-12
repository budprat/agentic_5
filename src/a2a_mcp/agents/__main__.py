# ABOUTME: Main entry point for starting A2A agent servers from agent cards
# ABOUTME: Simplified version with example domain agents and core server setup

import json
import logging
import os
import sys
from pathlib import Path

import click
import httpx
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard

logger = logging.getLogger(__name__)

# Import with fallbacks for missing modules
try:
    from a2a_mcp.common.agent_executor import GenericAgentExecutor
except ImportError:
    # Fallback to a2a's executor if our common one doesn't exist
    from a2a.agent_executor import GenericAgentExecutor

try:
    from a2a_mcp.common.auth import AuthScheme, create_auth_middleware
except ImportError:
    # Create simple fallback auth classes
    logger.warning("Auth module not available, using fallback")
    
    class AuthScheme:
        def __init__(self, **kwargs):
            self.type = kwargs.get('type', 'none')
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    def create_auth_middleware(auth_schemes):
        """Simple no-op auth middleware for fallback"""
        async def middleware(request, call_next):
            return await call_next(request)
        return middleware

# Import base agent for fallback
from a2a_mcp.common.base_agent import BaseAgent

# Try to import example domain agents with fallback to simple implementations
try:
    from a2a_mcp.agents.example_domain.master_oracle import MasterOracleAgent
except ImportError:
    logger.warning("MasterOracleAgent not available, using fallback implementation")
    # Create a simple fallback implementation
    class MasterOracleAgent(BaseAgent):
        def __init__(self, agent_id: str = "master_oracle"):
            super().__init__(
                agent_name=agent_id,
                description="Master Oracle Agent - Fallback Implementation",
                content_types=["application/json"]
            )

try:
    from a2a_mcp.agents.example_domain.domain_specialist import ResearchSpecialistAgent
except ImportError:
    logger.warning("ResearchSpecialistAgent not available, using fallback implementation")
    class ResearchSpecialistAgent(BaseAgent):
        def __init__(self, agent_id: str = "research_specialist", config: dict = None):
            super().__init__(
                agent_name=agent_id,
                description="Research Specialist Agent - Fallback Implementation",
                content_types=["application/json"]
            )

try:
    from a2a_mcp.agents.example_domain.service_agent import ServiceAgent
except ImportError:
    logger.warning("ServiceAgent not available, using fallback implementation")
    class ServiceAgent(BaseAgent):
        def __init__(self, agent_id: str = "service_agent", config: dict = None):
            super().__init__(
                agent_name=agent_id,
                description="Service Agent - Fallback Implementation", 
                content_types=["application/json"]
            )


def get_agent(agent_card: AgentCard):
    """
    Get the appropriate agent instance based on the agent card.
    
    This simplified version supports:
    - Master Oracle (Tier 1): Main orchestrator
    - Research Specialist (Tier 2): Domain-specific research
    - Service Agent (Tier 3): Basic service tasks
    - Example Agent: Generic example implementation
    """
    agent_name = agent_card.name.lower()
    
    try:
        # Tier 1: Master Oracle
        if 'oracle' in agent_name or agent_name == 'masteroracle':
            logger.info("Creating Master Oracle Agent")
            return MasterOracleAgent(agent_id="master_oracle")
        
        # Tier 2: Domain Specialists
        elif 'research' in agent_name or 'specialist' in agent_name:
            logger.info("Creating Research Specialist Agent")
            config = {
                'research_config': {
                    'max_search_results': 5,
                    'preferred_sources': ['github', 'official_docs'],
                }
            }
            return ResearchSpecialistAgent(
                agent_id="research_specialist",
                config=config
            )
        
        # Tier 3: Service Agents
        elif 'service' in agent_name:
            logger.info("Creating Service Agent")
            config = {
                'service_type': agent_card.metadata.get('service_type', 'general'),
                'capabilities': agent_card.capabilities
            }
            return ServiceAgent(
                agent_id="service_agent",
                config=config
            )
        
        # Default: Example Agent
        else:
            logger.info(f"Creating Example Agent for: {agent_card.name}")
            # Return a basic agent implementation
            # In production, this would be a proper ExampleAgent class
            return MasterOracleAgent(agent_id=f"example_{agent_card.name.lower()}")
            
    except Exception as e:
        logger.error(f"Failed to create agent for {agent_card.name}: {str(e)}")
        raise


@click.command()
@click.option('--host', 'host', default='localhost', help='Host to bind the server to')
@click.option('--port', 'port', default=10101, type=int, help='Port to bind the server to')
@click.option('--agent-card', 'agent_card', required=True, help='Path to agent card JSON file')
def main(host, port, agent_card):
    """
    Start an A2A agent server.
    
    This server:
    1. Loads an agent card configuration
    2. Creates the appropriate agent instance
    3. Sets up the A2A server with authentication (if configured)
    4. Starts serving agent requests
    
    Example:
        python -m a2a_mcp.agents --agent-card agent_cards/example_agent.json
    """
    try:
        # Validate agent card path
        if not agent_card:
            raise ValueError('Agent card path is required')
        
        # Load agent card
        agent_card_path = Path(agent_card)
        if not agent_card_path.exists():
            raise FileNotFoundError(f"Agent card not found: {agent_card}")
            
        with agent_card_path.open() as file:
            data = json.load(file)
        
        # Create AgentCard instance
        agent_card_obj = AgentCard(**data)
        
        # Override port if specified in agent card
        if hasattr(agent_card_obj, 'port') and agent_card_obj.port:
            port = agent_card_obj.port
            logger.info(f"Using port {port} from agent card")
        
        # Create HTTP client for agent communication
        client = httpx.AsyncClient()
        
        # Create the agent executor with the appropriate agent
        agent_executor = GenericAgentExecutor(agent=get_agent(agent_card_obj))
        
        # Create request handler with agent executor and task store
        request_handler = DefaultRequestHandler(
            agent_executor=agent_executor,
            task_store=InMemoryTaskStore()
        )
        
        # Create A2A server application
        server = A2AStarletteApplication(
            agent_card=agent_card_obj,
            http_handler=request_handler
        )
        
        # Build the application
        app = server.build()
        
        # Add authentication middleware if configured
        if hasattr(agent_card_obj, 'auth_required') and agent_card_obj.auth_required:
            auth_schemes = []
            
            # Extract auth schemes from agent card
            if hasattr(agent_card_obj, 'auth_schemes'):
                for scheme in agent_card_obj.auth_schemes:
                    auth_schemes.append(AuthScheme(**scheme))
            
            if auth_schemes:
                # Add authentication middleware
                app.add_middleware(create_auth_middleware(auth_schemes))
                logger.info(f'Authentication enabled with schemes: {[s.type for s in auth_schemes]}')
            else:
                logger.warning('auth_required is True but no auth_schemes configured')
        else:
            logger.info('Running without authentication')
        
        # Log startup information
        logger.info(f'Starting {agent_card_obj.name} server on {host}:{port}')
        logger.info(f'Agent type: {agent_card_obj.type}')
        logger.info(f'Capabilities: {agent_card_obj.capabilities}')
        
        # Start the server
        uvicorn.run(app, host=host, port=port)
        
    except FileNotFoundError:
        logger.error(f"Error: Agent card file '{agent_card}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Error: Agent card file '{agent_card}' contains invalid JSON: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f'An error occurred during server startup: {e}')
        logger.exception("Full traceback:")
        sys.exit(1)


if __name__ == '__main__':
    # Set up basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the main function
    main()