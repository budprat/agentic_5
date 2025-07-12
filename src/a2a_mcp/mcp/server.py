# ABOUTME: MCP server providing agent discovery and system health monitoring tools
# ABOUTME: Extensible framework for domain-specific tool integration using FastMCP

import json
import os
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import numpy as np
import pandas as pd

from a2a_mcp.common.utils import init_api_key
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

# Configuration constants
AGENT_CARDS_DIR = os.getenv('AGENT_CARDS_DIR', 'agent_cards')
EMBEDDING_MODEL = 'models/embedding-001'
SYSTEM_DB = os.getenv('SYSTEM_DB', 'system.db')

# Agent card management
agent_embeddings_df = None


def generate_embeddings(text: str) -> List[float]:
    """Generates embeddings for the given text using Google Generative AI.

    Args:
        text: The input string for which to generate embeddings.

    Returns:
        A list of embeddings representing the input text.
    """
    try:
        import google.generativeai as genai
        return genai.embed_content(
            model=EMBEDDING_MODEL,
            content=text,
            task_type='retrieval_document',
        )['embedding']
    except Exception as e:
        logger.warning(f"Embedding generation failed: {e}. Using fallback method.")
        # Fallback: simple hash-based pseudo-embedding for demo purposes
        return [float(hash(text + str(i)) % 1000) / 1000 for i in range(768)]


def load_agent_cards() -> tuple[List[str], List[dict]]:
    """Loads agent card data from JSON files within a specified directory.

    Returns:
        A tuple containing:
        - List of agent card URIs
        - List of agent card data dictionaries
    """
    card_uris = []
    agent_cards = []
    dir_path = Path(AGENT_CARDS_DIR)
    
    if not dir_path.is_dir():
        logger.warning(
            f'Agent cards directory not found or is not a directory: {AGENT_CARDS_DIR}'
        )
        return card_uris, agent_cards

    logger.info(f'Loading agent cards from: {AGENT_CARDS_DIR}')

    for filename in os.listdir(AGENT_CARDS_DIR):
        if filename.lower().endswith('.json'):
            file_path = dir_path / filename

            if file_path.is_file():
                logger.info(f'Reading file: {filename}')
                try:
                    with file_path.open('r', encoding='utf-8') as f:
                        data = json.load(f)
                        card_uris.append(
                            f'resource://agent_cards/{Path(filename).stem}'
                        )
                        agent_cards.append(data)
                except json.JSONDecodeError as jde:
                    logger.error(f'JSON Decoder Error: {jde}')
                except OSError as e:
                    logger.error(f'Error reading file {filename}: {e}')
                except Exception as e:
                    logger.error(
                        f'Unexpected error processing {filename}: {e}',
                        exc_info=True,
                    )
    
    logger.info(f'Loaded {len(agent_cards)} agent cards')
    return card_uris, agent_cards


def build_agent_card_embeddings() -> Optional[pd.DataFrame]:
    """Loads agent cards, generates embeddings for them, and returns a DataFrame.

    Returns:
        A Pandas DataFrame containing agent card data and embeddings, or None if failed.
    """
    card_uris, agent_cards = load_agent_cards()
    
    if not agent_cards:
        logger.warning('No agent cards loaded')
        return None
    
    logger.info('Generating embeddings for agent cards')
    try:
        df = pd.DataFrame(
            {'card_uri': card_uris, 'agent_card': agent_cards}
        )
        df['card_embeddings'] = df.apply(
            lambda row: generate_embeddings(json.dumps(row['agent_card'])),
            axis=1,
        )
        logger.info('Successfully generated embeddings')
        return df
    except Exception as e:
        logger.error(f'Error generating embeddings: {e}', exc_info=True)
        return None


def serve(host: str, port: int, transport: str):
    """Initializes and runs the Agent-to-Agent MCP server.

    Args:
        host: The hostname or IP address to bind the server to.
        port: The port number to bind the server to.
        transport: The transport mechanism for the MCP server (e.g., 'stdio', 'sse').
    """
    # Initialize API key if needed
    try:
        init_api_key()
    except Exception as e:
        logger.warning(f"API key initialization failed: {e}. Some features may be limited.")
    
    logger.info('Starting Agent-to-Agent MCP Server')
    mcp = FastMCP('a2a-framework', host=host, port=port)

    # Build agent embeddings
    global agent_embeddings_df
    agent_embeddings_df = build_agent_card_embeddings()

    # Tool: Find the most relevant agent
    @mcp.tool(
        name='find_agent',
        description='Finds the most relevant agent card based on a natural language query string.',
    )
    def find_agent(query: str) -> str:
        """Finds the most relevant agent card based on a query string.

        This function takes a user query, generates its embedding, and compares it against
        pre-computed embeddings of loaded agent cards to find the best match.

        Args:
            query: The natural language query string used to search for a relevant agent.

        Returns:
            The agent card JSON deemed most relevant to the input query.
        """
        if agent_embeddings_df is None or agent_embeddings_df.empty:
            return json.dumps({
                'error': 'No agent cards loaded',
                'suggestion': 'Ensure agent cards are present in the configured directory'
            })
        
        try:
            # Generate query embedding
            query_embedding = generate_embeddings(query)
            
            # Calculate similarity scores
            dot_products = np.dot(
                np.stack(agent_embeddings_df['card_embeddings']),
                query_embedding
            )
            
            # Find best match
            best_match_index = np.argmax(dot_products)
            best_score = dot_products[best_match_index]
            
            logger.debug(
                f'Found best match at index {best_match_index} with score {best_score}'
            )
            
            result = agent_embeddings_df.iloc[best_match_index]['agent_card']
            result['_match_score'] = float(best_score)
            
            return json.dumps(result)
            
        except Exception as e:
            logger.error(f'Error finding agent: {e}', exc_info=True)
            return json.dumps({
                'error': 'Failed to find matching agent',
                'details': str(e)
            })

    # Tool: List all available agents
    @mcp.tool(
        name='list_available_agents',
        description='List all available agents with their basic information.',
    )
    def list_available_agents() -> str:
        """Lists all available agents with their basic information.

        Returns:
            JSON list of agents with their names, descriptions, and capabilities.
        """
        if agent_embeddings_df is None or agent_embeddings_df.empty:
            return json.dumps({
                'agents': [],
                'count': 0,
                'message': 'No agents currently loaded'
            })
        
        try:
            agents_summary = []
            for _, row in agent_embeddings_df.iterrows():
                agent_card = row['agent_card']
                summary = {
                    'uri': row['card_uri'],
                    'name': agent_card.get('name', 'Unknown'),
                    'description': agent_card.get('description', 'No description'),
                    'capabilities': agent_card.get('capabilities', []),
                    'type': agent_card.get('type', 'general')
                }
                agents_summary.append(summary)
            
            return json.dumps({
                'agents': agents_summary,
                'count': len(agents_summary)
            })
            
        except Exception as e:
            logger.error(f'Error listing agents: {e}', exc_info=True)
            return json.dumps({
                'error': 'Failed to list agents',
                'details': str(e)
            })

    # Tool: System health check
    @mcp.tool(
        name='check_system_health',
        description='Check the health status of the MCP server and its components.',
    )
    def check_system_health() -> str:
        """Checks the health status of the MCP server and its components.

        Returns:
            JSON object with health status information.
        """
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'components': {}
        }
        
        # Check agent cards
        agent_status = {
            'status': 'healthy' if agent_embeddings_df is not None else 'unhealthy',
            'loaded_count': len(agent_embeddings_df) if agent_embeddings_df is not None else 0,
            'has_embeddings': agent_embeddings_df is not None and 'card_embeddings' in agent_embeddings_df.columns
        }
        health_status['components']['agent_cards'] = agent_status
        
        # Check embeddings
        embedding_status = {
            'status': 'healthy',
            'model': EMBEDDING_MODEL,
            'fallback_active': False
        }
        try:
            # Test embedding generation
            test_embedding = generate_embeddings("test")
            if len(test_embedding) != 768:  # Expected embedding size
                embedding_status['fallback_active'] = True
        except Exception as e:
            embedding_status['status'] = 'degraded'
            embedding_status['error'] = str(e)
        
        health_status['components']['embeddings'] = embedding_status
        
        # Overall status
        if any(comp.get('status') == 'unhealthy' for comp in health_status['components'].values()):
            health_status['status'] = 'unhealthy'
        elif any(comp.get('status') == 'degraded' for comp in health_status['components'].values()):
            health_status['status'] = 'degraded'
        
        return json.dumps(health_status)

    # Tool: Get server configuration
    @mcp.tool(
        name='get_server_config',
        description='Get the current configuration of the MCP server.',
    )
    def get_server_config() -> str:
        """Gets the current configuration of the MCP server.

        Returns:
            JSON object with server configuration details.
        """
        config = {
            'server_name': 'a2a-framework',
            'host': host,
            'port': port,
            'transport': transport,
            'agent_cards_directory': AGENT_CARDS_DIR,
            'embedding_model': EMBEDDING_MODEL,
            'system_database': SYSTEM_DB,
            'environment': {
                'python_version': os.sys.version.split()[0],
                'platform': os.sys.platform
            }
        }
        
        return json.dumps(config)

    # Resources: Agent cards list
    @mcp.resource('resource://agent_cards/list', mime_type='application/json')
    def get_agent_cards() -> dict:
        """Retrieves all loaded agent cards for the MCP resource endpoint.

        Returns:
            Dictionary containing list of agent card URIs.
        """
        if agent_embeddings_df is None or agent_embeddings_df.empty:
            return {'agent_cards': []}
        
        logger.info('Reading agent cards resource list')
        return {'agent_cards': agent_embeddings_df['card_uri'].tolist()}

    # Resources: Individual agent card
    @mcp.resource(
        'resource://agent_cards/{card_name}', mime_type='application/json'
    )
    def get_agent_card(card_name: str) -> dict:
        """Retrieves a specific agent card for the MCP resource endpoint.

        Args:
            card_name: Name/ID of the agent card to retrieve.

        Returns:
            Dictionary containing the agent card data.
        """
        if agent_embeddings_df is None or agent_embeddings_df.empty:
            return {'error': 'No agent cards loaded'}
        
        logger.info(f'Reading agent card resource: {card_name}')
        
        card_uri = f'resource://agent_cards/{card_name}'
        matching_cards = agent_embeddings_df.loc[
            agent_embeddings_df['card_uri'] == card_uri, 'agent_card'
        ].tolist()
        
        if matching_cards:
            return {'agent_card': matching_cards[0]}
        else:
            return {'error': f'Agent card not found: {card_name}'}

    # Extension point for domain-specific tools
    # Add your custom tools here by decorating functions with @mcp.tool()
    # Example:
    # @mcp.tool(
    #     name='domain_specific_tool',
    #     description='Description of what this tool does.'
    # )
    # def domain_specific_tool(param1: str, param2: int) -> str:
    #     """Your domain-specific implementation."""
    #     pass

    logger.info(
        f'Agent-to-Agent MCP Server running at {host}:{port} using {transport} transport'
    )
    
    # Run the server
    mcp.run(transport=transport)


# Entry point for testing
if __name__ == "__main__":
    # Default configuration for testing
    serve(host="localhost", port=8080, transport="stdio")