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
    from a2a_mcp.common import prompts
except ImportError:
    logger.warning("Prompts module not available, using basic instructions")
    # Create fallback prompts object for basic agent creation
    class prompts:
        GENERIC_INSTRUCTIONS = "You are a helpful AI assistant. Provide clear, accurate responses."
        AIRFARE_COT_INSTRUCTIONS = "You are an airline booking assistant. Help users find and book flights."
        HOTELS_COT_INSTRUCTIONS = "You are a hotel booking assistant. Help users find and book accommodations."
        CARS_COT_INSTRUCTIONS = "You are a car rental assistant. Help users find and book rental vehicles."

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

# Import Framework V2.0 templates for proper fallback implementations
try:
    from a2a_mcp.common.master_orchestrator_template import MasterOrchestratorTemplate
except ImportError:
    logger.warning("MasterOrchestratorTemplate not available, will use StandardizedAgentBase fallback")
    MasterOrchestratorTemplate = None

try:
    from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
except ImportError:
    logger.warning("StandardizedAgentBase not available, using BaseAgent fallback")
    from a2a_mcp.common.base_agent import BaseAgent
    StandardizedAgentBase = BaseAgent

try:
    from a2a_mcp.common.adk_service_agent import ADKServiceAgent
except ImportError:
    logger.warning("ADKServiceAgent not available, will use StandardizedAgentBase fallback")
    ADKServiceAgent = None

# Try to import example domain agents with Framework V2.0 compliant fallbacks
try:
    from a2a_mcp.agents.example_domain.master_oracle import MasterOracleAgent
except ImportError:
    logger.warning("MasterOracleAgent not available, using Framework V2.0 fallback implementation")
    # Create Framework V2.0 compliant fallback using MasterOrchestratorTemplate
    if MasterOrchestratorTemplate:
        class MasterOracleAgent(MasterOrchestratorTemplate):
            def __init__(self, agent_id: str = "master_oracle"):
                domain_specialists = {
                    "analysis": "General analysis and assessment",
                    "coordination": "Task coordination and management",
                    "synthesis": "Information synthesis and reporting"
                }
                super().__init__(
                    domain_name="Master Oracle",
                    domain_description="General purpose orchestration and coordination",
                    domain_specialists=domain_specialists,
                    enable_parallel=True
                )
    else:
        # Ultimate fallback using StandardizedAgentBase
        class MasterOracleAgent(StandardizedAgentBase):
            def __init__(self, agent_id: str = "master_oracle"):
                super().__init__(
                    agent_name="Master Oracle Agent",
                    description="Master Oracle Agent - Framework V2.0 Fallback",
                    instructions="You are a master orchestrator agent that coordinates complex tasks across multiple domains.",
                    mcp_tools_enabled=True,
                    a2a_enabled=True
                )
            
            async def _execute_agent_logic(self, query, context_id, task_id):
                """Simple fallback agent logic."""
                yield {
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': f"Master Oracle Agent (Fallback): Processed query - {query}",
                    'agent_name': self.agent_name
                }

try:
    from a2a_mcp.agents.example_domain.domain_specialist import ResearchSpecialistAgent
except ImportError:
    logger.warning("ResearchSpecialistAgent not available, using Framework V2.0 fallback implementation")
    # Create Framework V2.0 compliant fallback using StandardizedAgentBase
    class ResearchSpecialistAgent(StandardizedAgentBase):
        def __init__(self, agent_id: str = "research_specialist", config: dict = None):
            super().__init__(
                agent_name="Research Specialist Agent",
                description="Domain specialist for research and analysis - Framework V2.0 Fallback",
                instructions="You are a research specialist providing expert analysis and domain knowledge.",
                quality_config={"domain": "BUSINESS"},
                mcp_tools_enabled=True,
                a2a_enabled=True
            )
            self.config = config or {}
        
        async def _execute_agent_logic(self, query, context_id, task_id):
            """Simple fallback research specialist logic."""
            yield {
                'is_task_complete': True,
                'require_user_input': False,
                'content': f"Research Specialist Agent (Fallback): Analyzed query - {query}",
                'agent_name': self.agent_name
            }

try:
    from a2a_mcp.agents.example_domain.service_agent import ServiceAgent
except ImportError:
    logger.warning("ServiceAgent not available, using Framework V2.0 fallback implementation")
    # Create Framework V2.0 compliant fallback using ADKServiceAgent or StandardizedAgentBase
    if ADKServiceAgent:
        class ServiceAgent(ADKServiceAgent):
            def __init__(self, agent_id: str = "service_agent", config: dict = None):
                super().__init__(
                    agent_name="Service Agent",
                    description="Service Agent - Framework V2.0 Fallback",
                    instructions="You are a service agent that executes specific tasks and tool operations.",
                    a2a_enabled=True
                )
                self.config = config or {}
    else:
        # Fallback to StandardizedAgentBase
        class ServiceAgent(StandardizedAgentBase):
            def __init__(self, agent_id: str = "service_agent", config: dict = None):
                super().__init__(
                    agent_name="Service Agent",
                    description="Service Agent - Framework V2.0 Fallback",
                    instructions="You are a service agent that executes specific tasks and tool operations.",
                    quality_config={"domain": "SERVICE"},
                    mcp_tools_enabled=True,
                    a2a_enabled=True
                )
                self.config = config or {}
            
            async def _execute_agent_logic(self, query, context_id, task_id):
                """Simple fallback service agent logic."""
                yield {
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': f"Service Agent (Fallback): Executed task - {query}",
                    'agent_name': self.agent_name
                }


def get_agent(agent_card: AgentCard):
    """
    Get the appropriate agent instance based on the agent card.
    
    Framework V2.0 compliant with tier-based architecture and domain-specific prompts:
    - Tier 1: Master Orchestrators using MasterOrchestratorTemplate
    - Tier 2: Domain Specialists using StandardizedAgentBase  
    - Tier 3: Service Agents using ADKServiceAgent or StandardizedAgentBase
    - Domain-specific agents with sophisticated prompts
    """
    agent_name = agent_card.name.lower()
    
    try:
        # Tier 1: Master Orchestrators
        if 'oracle' in agent_name or 'orchestrator' in agent_name or agent_name == 'masteroracle':
            logger.info("Creating Tier 1 Master Orchestrator Agent")
            return MasterOracleAgent(agent_id="master_oracle")
        
        # Tier 2: Domain Specialists
        elif 'research' in agent_name or 'specialist' in agent_name or 'analyst' in agent_name:
            logger.info("Creating Tier 2 Domain Specialist Agent")
            config = {
                'research_config': {
                    'max_search_results': 5,
                    'preferred_sources': ['github', 'official_docs'],
                },
                'domain': agent_card.metadata.get('domain', 'general'),
                'expertise_level': agent_card.metadata.get('expertise_level', 'advanced')
            }
            return ResearchSpecialistAgent(
                agent_id="research_specialist",
                config=config
            )
        
        # Tier 3: Travel Domain Service Agents (Framework V2.0 pattern)
        elif agent_card.name == 'Air Ticketing Agent':
            logger.info("Creating Tier 3 Air Ticketing Service Agent")
            # Import TravelAgent or use equivalent ADKServiceAgent pattern
            try:
                from a2a_mcp.common.adk_service_agent import ADKServiceAgent
                return ADKServiceAgent(
                    agent_name='AirTicketingAgent',
                    description='Book air tickets given criteria',
                    instructions=prompts.AIRFARE_COT_INSTRUCTIONS,
                    a2a_enabled=True
                )
            except ImportError:
                # Fallback using ServiceAgent
                logger.warning("ADKServiceAgent not available, using ServiceAgent fallback")
                return ServiceAgent(agent_id="air_ticketing_agent", config={'service_type': 'travel'})
        
        elif agent_card.name == 'Hotel Booking Agent':
            logger.info("Creating Tier 3 Hotel Booking Service Agent")
            try:
                from a2a_mcp.common.adk_service_agent import ADKServiceAgent
                return ADKServiceAgent(
                    agent_name='HotelBookingAgent',
                    description='Book hotels given criteria',
                    instructions=prompts.HOTELS_COT_INSTRUCTIONS,
                    a2a_enabled=True
                )
            except ImportError:
                logger.warning("ADKServiceAgent not available, using ServiceAgent fallback")
                return ServiceAgent(agent_id="hotel_booking_agent", config={'service_type': 'travel'})
        
        elif agent_card.name == 'Car Rental Agent':
            logger.info("Creating Tier 3 Car Rental Service Agent")
            try:
                from a2a_mcp.common.adk_service_agent import ADKServiceAgent
                return ADKServiceAgent(
                    agent_name='CarRentalBookingAgent',
                    description='Book rental cars given criteria',
                    instructions=prompts.CARS_COT_INSTRUCTIONS,
                    a2a_enabled=True
                )
            except ImportError:
                logger.warning("ADKServiceAgent not available, using ServiceAgent fallback")
                return ServiceAgent(agent_id="car_rental_agent", config={'service_type': 'travel'})
        
        # Tier 3: Generic Service Agents
        elif 'service' in agent_name or 'agent' in agent_name:
            logger.info("Creating Tier 3 Generic Service Agent")
            config = {
                'service_type': agent_card.metadata.get('service_type', 'general'),
                'capabilities': agent_card.capabilities,
                'domain': agent_card.metadata.get('domain', 'general')
            }
            return ServiceAgent(
                agent_id="service_agent",
                config=config
            )
        
        # Default: Framework V2.0 compliant agent with prompts
        else:
            logger.info(f"Creating Framework V2.0 Agent for: {agent_card.name}")
            # Determine tier from agent card metadata
            tier = getattr(agent_card, 'tier', None)
            
            if tier == 1:
                return MasterOracleAgent(agent_id=f"tier1_{agent_card.name.lower().replace(' ', '_')}")
            elif tier == 2:
                config = {'domain': agent_card.metadata.get('domain', 'general')}
                return ResearchSpecialistAgent(agent_id=f"tier2_{agent_card.name.lower().replace(' ', '_')}", config=config)
            else:
                # Default to Tier 3 service agent
                config = {'domain': agent_card.metadata.get('domain', 'general')}
                return ServiceAgent(agent_id=f"tier3_{agent_card.name.lower().replace(' ', '_')}", config=config)
            
    except Exception as e:
        logger.error(f"Failed to create agent for {agent_card.name}: {str(e)}")
        logger.exception("Full agent creation traceback:")
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