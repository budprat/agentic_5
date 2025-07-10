# type: ignore

import json
import os
import sqlite3
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

import google.generativeai as genai
import numpy as np
import pandas as pd
import requests

from a2a_mcp.common.utils import init_api_key
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.logging import get_logger


logger = get_logger(__name__)
AGENT_CARDS_DIR = 'agent_cards'
MODEL = 'models/embedding-001'
SQLLITE_DB = 'travel_agency.db'
PLACES_API_URL = 'https://places.googleapis.com/v1/places:searchText'

# Solopreneur database configuration
SOLOPRENEUR_DB = os.getenv('SOLOPRENEUR_DB', 'solopreneur.db')
NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')


def generate_embeddings(text):
    """Generates embeddings for the given text using Google Generative AI.

    Args:
        text: The input string for which to generate embeddings.

    Returns:
        A list of embeddings representing the input text.
    """
    return genai.embed_content(
        model=MODEL,
        content=text,
        task_type='retrieval_document',
    )['embedding']


def load_agent_cards():
    """Loads agent card data from JSON files within a specified directory.

    Returns:
        A list containing JSON data from an agent card file found in the specified directory.
        Returns an empty list if the directory is empty, contains no '.json' files,
        or if all '.json' files encounter errors during processing.
    """
    card_uris = []
    agent_cards = []
    dir_path = Path(AGENT_CARDS_DIR)
    if not dir_path.is_dir():
        logger.error(
            f'Agent cards directory not found or is not a directory: {AGENT_CARDS_DIR}'
        )
        return agent_cards

    logger.info(f'Loading agent cards from card repo: {AGENT_CARDS_DIR}')

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
                    logger.error(f'JSON Decoder Error {jde}')
                except OSError as e:
                    logger.error(f'Error reading file {filename}: {e}.')
                except Exception as e:
                    logger.error(
                        f'An unexpected error occurred processing {filename}: {e}',
                        exc_info=True,
                    )
    logger.info(
        f'Finished loading agent cards. Found {len(agent_cards)} cards.'
    )
    return card_uris, agent_cards


def build_agent_card_embeddings() -> pd.DataFrame:
    """Loads agent cards, generates embeddings for them, and returns a DataFrame.

    Returns:
        Optional[pd.DataFrame]: A Pandas DataFrame containing the original
        'agent_card' data and their corresponding 'Embeddings'. Returns None
        if no agent cards were loaded initially or if an exception occurred
        during the embedding generation process.
    """
    card_uris, agent_cards = load_agent_cards()
    logger.info('Generating Embeddings for agent cards')
    try:
        if agent_cards:
            df = pd.DataFrame(
                {'card_uri': card_uris, 'agent_card': agent_cards}
            )
            df['card_embeddings'] = df.apply(
                lambda row: generate_embeddings(json.dumps(row['agent_card'])),
                axis=1,
            )
            return df
        logger.info('Done generating embeddings for agent cards')
    except Exception as e:
        logger.error(f'An unexpected error occurred : {e}.', exc_info=True)
        return None


def serve(host, port, transport):  # noqa: PLR0915
    """Initializes and runs the Agent Cards MCP server.

    Args:
        host: The hostname or IP address to bind the server to.
        port: The port number to bind the server to.
        transport: The transport mechanism for the MCP server (e.g., 'stdio', 'sse').

    Raises:
        ValueError: If the 'GOOGLE_API_KEY' environment variable is not set.
    """
    init_api_key()
    logger.info('Starting Agent Cards MCP Server')
    mcp = FastMCP('agent-cards', host=host, port=port)

    df = build_agent_card_embeddings()

    @mcp.tool(
        name='find_agent',
        description='Finds the most relevant agent card based on a natural language query string.',
    )
    def find_agent(query: str) -> str:
        """Finds the most relevant agent card based on a query string.

        This function takes a user query, typically a natural language question or a task generated by an agent,
        generates its embedding, and compares it against the
        pre-computed embeddings of the loaded agent cards. It uses the dot
        product to measure similarity and identifies the agent card with the
        highest similarity score.

        Args:
            query: The natural language query string used to search for a
                   relevant agent.

        Returns:
            The json representing the agent card deemed most relevant
            to the input query based on embedding similarity.
        """
        query_embedding = genai.embed_content(
            model=MODEL, content=query, task_type='retrieval_query'
        )
        dot_products = np.dot(
            np.stack(df['card_embeddings']), query_embedding['embedding']
        )
        best_match_index = np.argmax(dot_products)
        logger.debug(
            f'Found best match at index {best_match_index} with score {dot_products[best_match_index]}'
        )
        return df.iloc[best_match_index]['agent_card']

    @mcp.tool()
    def query_places_data(query: str):
        """Query Google Places."""
        logger.info(f'Search for places : {query}')
        api_key = os.getenv('GOOGLE_PLACES_API_KEY')
        if not api_key:
            logger.info('GOOGLE_PLACES_API_KEY is not set')
            return {'places': []}

        headers = {
            'X-Goog-Api-Key': api_key,
            'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress',
            'Content-Type': 'application/json',
        }
        payload = {
            'textQuery': query,
            'languageCode': 'en',
            'maxResultCount': 10,
        }

        try:
            response = requests.post(
                PLACES_API_URL, headers=headers, json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            logger.info(f'HTTP error occurred: {http_err}')
            logger.info(f'Response content: {response.text}')
        except requests.exceptions.ConnectionError as conn_err:
            logger.info(f'Connection error occurred: {conn_err}')
        except requests.exceptions.Timeout as timeout_err:
            logger.info(f'Timeout error occurred: {timeout_err}')
        except requests.exceptions.RequestException as req_err:
            logger.info(
                f'An unexpected error occurred with the request: {req_err}'
            )
        except json.JSONDecodeError:
            logger.info(
                f'Failed to decode JSON response. Raw response: {response.text}'
            )

        return {'places': []}

    @mcp.tool()
    def query_travel_data(query: str) -> dict:
        """
        "name": "query_travel_data",
        "description": "Retrieves the most up-to-date, ariline, hotel and car rental availability. Helps with the booking.
        This tool should be used when a user asks for the airline ticket booking, hotel or accommodation booking, or car rental reservations.",
        "parameters": {
            "type": "object",
            "properties": {
            "query": {
                "type": "string",
                "description": "A SQL to run against the travel database."
            }
            },
            "required": ["query"]
        }
        """
        # The above is to influence gemini to pickup the tool.
        logger.info(f'Query sqllite : {query}')

        if not query or not query.strip().upper().startswith('SELECT'):
            raise ValueError(f'In correct query {query}')

        try:
            with sqlite3.connect(SQLLITE_DB) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                result = {'results': [dict(row) for row in rows]}
                return json.dumps(result)
        except Exception as e:
            logger.error(f'Exception running query {e}')
            logger.error(traceback.format_exc())
            if 'no such column' in e:
                return {
                    'error': f'Please check your query, {e}. Use the table schema to regenerate the query'
                }
            return {'error': {e}}

    # Solopreneur-specific tools for knowledge management and personal optimization
    @mcp.tool(
        name='query_solopreneur_metrics',
        description='Query personal optimization metrics from the database (energy, focus, productivity, stress).',
    )
    def query_solopreneur_metrics(
        metric_type: str,
        user_id: str = "default",
        time_range: str = "day",
        aggregation: str = "avg"
    ) -> str:
        """
        Query personal optimization metrics from the database.
        
        Args:
            metric_type: Type of metric ('energy', 'focus', 'productivity', 'stress')
            user_id: User identifier
            time_range: Time range ('day', 'week', 'month')
            aggregation: Aggregation method ('avg', 'max', 'min', 'sum')
        """
        logger.info(f'Query solopreneur metrics: {metric_type} for {time_range}')
        
        # Calculate date range
        end_date = datetime.now()
        if time_range == 'day':
            start_date = end_date - timedelta(days=1)
        elif time_range == 'week':
            start_date = end_date - timedelta(weeks=1)
        elif time_range == 'month':
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=7)
        
        try:
            with sqlite3.connect(SOLOPRENEUR_DB) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = f"""
                SELECT 
                    DATE(timestamp) as date,
                    {aggregation}(value) as {aggregation}_value,
                    COUNT(*) as data_points,
                    MIN(value) as min_value,
                    MAX(value) as max_value
                FROM personal_metrics
                WHERE user_id = ? 
                    AND metric_type = ?
                    AND timestamp BETWEEN ? AND ?
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
                """
                
                cursor.execute(query, (user_id, metric_type, start_date, end_date))
                rows = cursor.fetchall()
                
                results = {
                    'metric_type': metric_type,
                    'time_range': time_range,
                    'aggregation': aggregation,
                    'data': [dict(row) for row in rows],
                    'summary': {
                        'total_data_points': sum(row['data_points'] for row in rows),
                        'overall_avg': sum(row[f'{aggregation}_value'] * row['data_points'] for row in rows) / sum(row['data_points'] for row in rows) if rows else 0
                    }
                }
                
                return json.dumps(results)
        except Exception as e:
            logger.error(f'Error querying metrics: {e}')
            return json.dumps({'error': str(e)})

    @mcp.tool(
        name='analyze_energy_patterns',
        description='Analyze energy patterns to find optimal work windows and productivity schedules.',
    )
    def analyze_energy_patterns(
        user_id: str = "default",
        date: Optional[str] = None
    ) -> str:
        """
        Analyze energy patterns to find optimal work windows.
        
        Args:
            user_id: User identifier
            date: Specific date to analyze (YYYY-MM-DD) or None for today
        """
        logger.info(f'Analyze energy patterns for user: {user_id}')
        
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            with sqlite3.connect(SOLOPRENEUR_DB) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get energy patterns for the date
                cursor.execute("""
                SELECT hour, energy_level, cognitive_capacity, optimal_task_types
                FROM energy_patterns
                WHERE user_id = ? AND date = ?
                ORDER BY hour
                """, (user_id, date))
                
                patterns = cursor.fetchall()
                
                if not patterns:
                    # Get average patterns if no data for specific date
                    cursor.execute("""
                    SELECT 
                        hour,
                        AVG(energy_level) as energy_level,
                        AVG(cognitive_capacity) as cognitive_capacity,
                        GROUP_CONCAT(DISTINCT optimal_task_types) as optimal_task_types
                    FROM energy_patterns
                    WHERE user_id = ?
                    GROUP BY hour
                    ORDER BY hour
                    """, (user_id,))
                    patterns = cursor.fetchall()
                
                # Analyze patterns
                peak_hours = []
                low_hours = []
                deep_work_windows = []
                
                for row in patterns:
                    hour_data = dict(row)
                    if hour_data['energy_level'] >= 8:
                        peak_hours.append(hour_data['hour'])
                    elif hour_data['energy_level'] <= 4:
                        low_hours.append(hour_data['hour'])
                    
                    if hour_data['cognitive_capacity'] >= 8:
                        optimal_tasks = []
                        if hour_data['optimal_task_types']:
                            try:
                                optimal_tasks = json.loads(hour_data['optimal_task_types'])
                            except json.JSONDecodeError:
                                optimal_tasks = hour_data['optimal_task_types'].split(',')
                        
                        deep_work_windows.append({
                            'hour': hour_data['hour'],
                            'capacity': hour_data['cognitive_capacity'],
                            'optimal_tasks': optimal_tasks
                        })
                
                recommendations = []
                if peak_hours:
                    recommendations.append(f"Schedule complex tasks during peak hours: {', '.join(map(str, peak_hours))}")
                if low_hours:
                    recommendations.append(f"Reserve low-energy hours for routine tasks: {', '.join(map(str, low_hours))}")
                if deep_work_windows:
                    recommendations.append(f"Deep work windows available at: {', '.join([str(w['hour']) for w in deep_work_windows])}")
                
                return json.dumps({
                    'date': date,
                    'patterns': [dict(row) for row in patterns],
                    'analysis': {
                        'peak_energy_hours': peak_hours,
                        'low_energy_hours': low_hours,
                        'deep_work_windows': deep_work_windows,
                        'recommendations': recommendations
                    }
                })
                
        except Exception as e:
            logger.error(f'Error analyzing energy patterns: {e}')
            return json.dumps({'error': str(e)})

    @mcp.tool(
        name='track_learning_progress',
        description='Track and update learning progress for skills, including hours invested and milestone achievements.',
    )
    def track_learning_progress(
        skill_name: str,
        user_id: str = "default",
        hours_to_add: Optional[float] = None,
        new_level: Optional[int] = None
    ) -> str:
        """
        Track and update learning progress for a skill.
        
        Args:
            skill_name: Name of the skill
            user_id: User identifier
            hours_to_add: Optional hours to add to the skill
            new_level: Optional new level to set for the skill
        """
        logger.info(f'Track learning progress for skill: {skill_name}')
        
        try:
            with sqlite3.connect(SOLOPRENEUR_DB) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Update skill progress if data provided
                if hours_to_add is not None:
                    cursor.execute("""
                    UPDATE skill_progress 
                    SET hours_invested = hours_invested + ?,
                        last_practice_date = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND skill_name = ?
                    """, (hours_to_add, user_id, skill_name))
                
                if new_level is not None:
                    cursor.execute("""
                    UPDATE skill_progress 
                    SET current_level = ?
                    WHERE user_id = ? AND skill_name = ?
                    """, (new_level, user_id, skill_name))
                
                conn.commit()
                
                # Get current progress
                cursor.execute("""
                SELECT sp.*, 
                    COUNT(ls.id) as total_sessions,
                    AVG(ls.productivity_score) as avg_productivity
                FROM skill_progress sp
                LEFT JOIN learning_sessions ls ON sp.id = ls.skill_id
                WHERE sp.user_id = ? AND sp.skill_name = ?
                GROUP BY sp.id
                """, (user_id, skill_name))
                
                progress = cursor.fetchone()
                
                if not progress:
                    # Create new skill entry
                    cursor.execute("""
                    INSERT INTO skill_progress (user_id, skill_name, current_level, target_level, hours_invested)
                    VALUES (?, ?, 1, 5, 0)
                    """, (user_id, skill_name))
                    conn.commit()
                    
                    progress = cursor.execute("""
                    SELECT * FROM skill_progress 
                    WHERE user_id = ? AND skill_name = ?
                    """, (user_id, skill_name)).fetchone()
                
                # Calculate learning velocity
                hours = progress['hours_invested'] or 0
                current_level = progress['current_level'] or 1
                target_level = progress['target_level'] or 5
                
                velocity = 0
                trajectory = 'just_started'
                estimated_hours = float('inf')
                
                if hours > 0:
                    velocity = (current_level - 1) / hours
                    trajectory = 'improving' if velocity > 0 else 'stagnant'
                    remaining_levels = target_level - current_level
                    estimated_hours = remaining_levels / velocity if velocity > 0 else float('inf')
                
                learning_velocity = {
                    'velocity': velocity,
                    'trajectory': trajectory,
                    'estimated_hours_to_target': estimated_hours
                }
                
                # Generate recommendations
                recommendations = []
                if velocity < 0.01 and hours > 0:
                    recommendations.append("Consider more active learning methods or shorter, focused sessions")
                
                if progress['last_practice_date']:
                    try:
                        last_practice = datetime.fromisoformat(progress['last_practice_date'])
                        days_since = (datetime.now() - last_practice).days
                        if days_since > 7:
                            recommendations.append(f"It's been {days_since} days since last practice. Schedule a review session.")
                    except ValueError:
                        pass
                
                if current_level >= 3 and progress['total_sessions'] < 5:
                    recommendations.append("Consider working on a practical project to solidify your knowledge")
                
                return json.dumps({
                    'skill': skill_name,
                    'progress': dict(progress),
                    'learning_velocity': learning_velocity,
                    'recommendations': recommendations
                })
                
        except Exception as e:
            logger.error(f'Error tracking learning progress: {e}')
            return json.dumps({'error': str(e)})

    @mcp.tool(
        name='search_relevant_research',
        description='Search for relevant research papers and technical content using ArXiv and stored intelligence.',
    )
    def search_relevant_research(
        query: str,
        research_area: str,
        max_results: int = 20
    ) -> str:
        """
        Search for relevant research papers and technical content.
        
        Args:
            query: Search query
            research_area: Specific research area
            max_results: Maximum number of results
        """
        logger.info(f'Search relevant research: {query} in {research_area}')
        
        try:
            # Search stored technical intelligence first
            stored_results = []
            with sqlite3.connect(SOLOPRENEUR_DB) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                SELECT * FROM technical_intelligence
                WHERE research_area = ? 
                    AND (title LIKE ? OR summary LIKE ?)
                ORDER BY relevance_score DESC
                LIMIT ?
                """, (research_area, f'%{query}%', f'%{query}%', max_results))
                
                stored_results = [dict(row) for row in cursor.fetchall()]
            
            # Try to search ArXiv if available
            arxiv_results = []
            try:
                import arxiv
                client = arxiv.Client()
                search = arxiv.Search(
                    query=f"{query} AND cat:{research_area}",
                    max_results=min(max_results, 10),
                    sort_by=arxiv.SortCriterion.Relevance
                )
                
                for result in client.results(search):
                    arxiv_results.append({
                        'arxiv_id': result.entry_id.split('/')[-1],
                        'title': result.title,
                        'authors': [author.name for author in result.authors][:3],
                        'abstract': result.summary[:500],
                        'published': result.published.isoformat(),
                        'url': result.pdf_url,
                        'source': 'arxiv'
                    })
            except ImportError:
                logger.warning("ArXiv library not available, using stored results only")
            except Exception as e:
                logger.warning(f"ArXiv search failed: {e}")
            
            return json.dumps({
                'query': query,
                'research_area': research_area,
                'arxiv_results': arxiv_results,
                'stored_results': stored_results,
                'total_results': len(arxiv_results) + len(stored_results)
            })
            
        except Exception as e:
            logger.error(f'Error searching research: {e}')
            return json.dumps({'error': str(e)})

    @mcp.resource('resource://agent_cards/list', mime_type='application/json')
    def get_agent_cards() -> dict:
        """Retrieves all loaded agent cards as a json / dictionary for the MCP resource endpoint.

        This function serves as the handler for the MCP resource identified by
        the URI 'resource://agent_cards/list'.

        Returns:
            A json / dictionary structured as {'agent_cards': [...]}, where the value is a
            list containing all the loaded agent card dictionaries. Returns
            {'agent_cards': []} if the data cannot be retrieved.
        """
        resources = {}
        logger.info('Starting read resources')
        resources['agent_cards'] = df['card_uri'].to_list()
        return resources

    @mcp.resource(
        'resource://agent_cards/{card_name}', mime_type='application/json'
    )
    def get_agent_card(card_name: str) -> dict:
        """Retrieves an agent card as a json / dictionary for the MCP resource endpoint.

        This function serves as the handler for the MCP resource identified by
        the URI 'resource://agent_cards/{card_name}'.

        Returns:
            A json / dictionary
        """
        resources = {}
        logger.info(
            f'Starting read resource resource://agent_cards/{card_name}'
        )
        resources['agent_card'] = (
            df.loc[
                df['card_uri'] == f'resource://agent_cards/{card_name}',
                'agent_card',
            ]
        ).to_list()

        return resources

    logger.info(
        f'Agent cards MCP Server at {host}:{port} and transport {transport}'
    )
    mcp.run(transport=transport)