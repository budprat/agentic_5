# type: ignore

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
from a2a.server.tasks import InMemoryPushNotifier, InMemoryTaskStore
from a2a.types import AgentCard
from a2a_mcp.common import prompts
from a2a_mcp.common.agent_executor import GenericAgentExecutor
from a2a_mcp.common.auth import AuthScheme, create_auth_middleware
from a2a_mcp.agents.adk_travel_agent import TravelAgent
from a2a_mcp.agents.langgraph_planner_agent import LangraphPlannerAgent
from a2a_mcp.agents.orchestrator_agent import OrchestratorAgent
from a2a_mcp.agents.parallel_orchestrator_agent import ParallelOrchestratorAgent


logger = logging.getLogger(__name__)


def get_agent(agent_card: AgentCard):
    """Get the agent, given an agent card."""
    try:
        if agent_card.name == 'Orchestrator Agent':
            # Use parallel orchestrator if ENABLE_PARALLEL env var is set
            if os.getenv('ENABLE_PARALLEL_EXECUTION', 'true').lower() == 'true':
                logger.info("Using Parallel Orchestrator Agent")
                return ParallelOrchestratorAgent()
            else:
                return OrchestratorAgent()
        elif agent_card.name == 'Langraph Planner Agent':
            return LangraphPlannerAgent()
        elif agent_card.name == 'Air Ticketing Agent':
            return TravelAgent(
                agent_name='AirTicketingAgent',
                description='Book air tickets given a criteria',
                instructions=prompts.AIRFARE_COT_INSTRUCTIONS,
            )
        elif agent_card.name == 'Hotel Booking Agent':
            return TravelAgent(
                agent_name='HotelBookingAgent',
                description='Book hotels given a criteria',
                instructions=prompts.HOTELS_COT_INSTRUCTIONS,
            )
        elif agent_card.name == 'Car Rental Agent':
            return TravelAgent(
                agent_name='CarRentalBookingAgent',
                description='Book rental cars given a criteria',
                instructions=prompts.CARS_COT_INSTRUCTIONS,
            )
            # return LangraphCarRentalAgent()
    except Exception as e:
        raise e


@click.command()
@click.option('--host', 'host', default='localhost')
@click.option('--port', 'port', default=10101)
@click.option('--agent-card', 'agent_card')
def main(host, port, agent_card):
    """Starts an Agent server."""
    try:
        if not agent_card:
            raise ValueError('Agent card is required')
        with Path.open(agent_card) as file:
            data = json.load(file)
        agent_card = AgentCard(**data)

        client = httpx.AsyncClient()
        request_handler = DefaultRequestHandler(
            agent_executor=GenericAgentExecutor(agent=get_agent(agent_card)),
            task_store=InMemoryTaskStore(),
            push_notifier=InMemoryPushNotifier(client),
        )

        server = A2AStarletteApplication(
            agent_card=agent_card, http_handler=request_handler
        )
        
        # Add authentication middleware if configured
        if hasattr(agent_card, 'auth_required') and agent_card.auth_required:
            auth_schemes = []
            if hasattr(agent_card, 'auth_schemes'):
                for scheme in agent_card.auth_schemes:
                    auth_schemes.append(AuthScheme(**scheme))
            
            if auth_schemes:
                app = server.build()
                # Add authentication middleware to the app
                app.add_middleware(create_auth_middleware(auth_schemes))
                logger.info(f'Authentication enabled with schemes: {[s.type for s in auth_schemes]}')
            else:
                app = server.build()
                logger.warning('auth_required is True but no auth_schemes configured')
        else:
            app = server.build()
            logger.info('Running without authentication')

        logger.info(f'Starting server on {host}:{port}')

        uvicorn.run(app, host=host, port=port)
    except FileNotFoundError:
        logger.error(f"Error: File '{agent_card}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        logger.error(f"Error: File '{agent_card}' contains invalid JSON.")
        sys.exit(1)
    except Exception as e:
        logger.error(f'An error occurred during server startup: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()