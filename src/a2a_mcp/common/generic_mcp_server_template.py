# ABOUTME: Generic MCP server template with reusable tool patterns for common integrations
# ABOUTME: Framework V2.0 extensible template for APIs, databases, search, and third-party services

"""
Generic MCP Server Template - Framework V2.0

This template provides reusable patterns for common MCP tool integrations:
- API integrations (REST, GraphQL)
- Database queries (SQL, NoSQL) 
- Search services (Google Places, Travel data)
- Third-party service wrappers
- File system operations
- Data processing pipelines

Usage:
    from a2a_mcp.common.generic_mcp_server_template import GenericMCPServerTemplate
    
    # Create domain-specific server
    travel_server = GenericMCPServerTemplate(
        server_name="travel-services",
        description="Travel booking and search services",
        host="localhost",
        port=8080
    )
    
    # Add domain tools
    travel_server.add_api_tool("google_places", PLACES_API_CONFIG)
    travel_server.add_database_tool("travel_db", SQLITE_CONFIG)
    travel_server.run()
"""

import json
import os
import sqlite3
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod

import requests
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.logging import get_logger

# Initialize logger
logger = get_logger(__name__)


@dataclass
class APIConfig:
    """Configuration for API tool integration."""
    name: str
    description: str
    base_url: str
    headers: Dict[str, str]
    auth_env_var: Optional[str] = None
    default_params: Optional[Dict[str, Any]] = None
    timeout: int = 30
    max_retries: int = 3


@dataclass 
class DatabaseConfig:
    """Configuration for database tool integration."""
    name: str
    description: str
    connection_string: str
    db_type: str  # 'sqlite', 'postgres', 'mysql', etc.
    query_whitelist: Optional[List[str]] = None  # Allowed query patterns
    max_results: int = 1000


class ToolHandler(ABC):
    """Abstract base class for MCP tool handlers."""
    
    @abstractmethod
    def get_tool_definition(self) -> Dict[str, Any]:
        """Return tool definition for MCP registration."""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters."""
        pass


class APIToolHandler(ToolHandler):
    """Generic API tool handler."""
    
    def __init__(self, config: APIConfig):
        self.config = config
        self.session = requests.Session()
        
        # Set up authentication
        if config.auth_env_var:
            auth_key = os.getenv(config.auth_env_var)
            if auth_key:
                # Common auth patterns
                if 'api-key' in config.headers.get('Authorization', '').lower():
                    config.headers['Authorization'] = f"Bearer {auth_key}"
                elif 'x-api-key' in config.headers:
                    config.headers['X-API-Key'] = auth_key
                elif 'x-goog-api-key' in config.headers:
                    config.headers['X-Goog-Api-Key'] = auth_key
        
        self.session.headers.update(config.headers)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": self.config.name,
            "description": self.config.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": f"Query string for {self.config.name} API"
                    },
                    "params": {
                        "type": "object", 
                        "description": "Additional API parameters",
                        "default": {}
                    }
                },
                "required": ["query"]
            }
        }
    
    def execute(self, query: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute API call with error handling and retries."""
        logger.info(f'API call to {self.config.name}: {query}')
        
        # Check authentication
        auth_key = None
        if self.config.auth_env_var:
            auth_key = os.getenv(self.config.auth_env_var)
            if not auth_key:
                logger.warning(f'{self.config.auth_env_var} not set')
                return {'error': f'API key not configured for {self.config.name}'}
        
        # Prepare request parameters
        request_params = {**(self.config.default_params or {}), **(params or {})}
        
        # Build request based on common patterns
        if 'textQuery' in str(self.config.default_params):
            # Google Places style
            payload = {**request_params, 'textQuery': query}
            method = 'POST'
            kwargs = {'json': payload}
        elif 'q' in str(self.config.default_params):
            # Search API style
            request_params['q'] = query
            method = 'GET'
            kwargs = {'params': request_params}
        else:
            # Generic query parameter
            request_params['query'] = query  
            method = 'GET'
            kwargs = {'params': request_params}
        
        # Execute with retries
        for attempt in range(self.config.max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=self.config.base_url,
                    timeout=self.config.timeout,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.HTTPError as e:
                logger.warning(f'HTTP error on attempt {attempt + 1}: {e}')
                if attempt == self.config.max_retries - 1:
                    return {'error': f'HTTP error: {e}', 'response': response.text if 'response' in locals() else ''}
                    
            except requests.exceptions.ConnectionError as e:
                logger.warning(f'Connection error on attempt {attempt + 1}: {e}')
                if attempt == self.config.max_retries - 1:
                    return {'error': f'Connection error: {e}'}
                    
            except requests.exceptions.Timeout as e:
                logger.warning(f'Timeout on attempt {attempt + 1}: {e}')
                if attempt == self.config.max_retries - 1:
                    return {'error': f'Request timeout: {e}'}
                    
            except requests.exceptions.RequestException as e:
                logger.error(f'Request error on attempt {attempt + 1}: {e}')
                if attempt == self.config.max_retries - 1:
                    return {'error': f'Request failed: {e}'}
                    
            except json.JSONDecodeError as e:
                logger.error(f'JSON decode error: {e}')
                return {'error': 'Invalid JSON response', 'raw_response': response.text if 'response' in locals() else ''}
        
        return {'error': 'Max retries exceeded'}


class DatabaseToolHandler(ToolHandler):
    """Generic database tool handler with security controls."""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": self.config.name,
            "description": self.config.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": f"SQL query for {self.config.name} database. Must start with SELECT."
                    }
                },
                "required": ["query"]
            }
        }
    
    def _validate_query(self, query: str) -> bool:
        """Validate query for security."""
        query_upper = query.strip().upper()
        
        # Basic security checks
        if not query_upper.startswith('SELECT'):
            logger.warning(f'Non-SELECT query rejected: {query}')
            return False
            
        # Check for dangerous operations
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
        if any(keyword in query_upper for keyword in dangerous_keywords):
            logger.warning(f'Dangerous query rejected: {query}')
            return False
            
        # Check whitelist if configured
        if self.config.query_whitelist:
            if not any(pattern.upper() in query_upper for pattern in self.config.query_whitelist):
                logger.warning(f'Query not in whitelist: {query}')
                return False
        
        return True
    
    def execute(self, query: str) -> Dict[str, Any]:
        """Execute database query with security validation."""
        logger.info(f'Database query on {self.config.name}: {query}')
        
        # Validate query
        if not self._validate_query(query):
            return {'error': 'Query validation failed'}
        
        try:
            if self.config.db_type == 'sqlite':
                return self._execute_sqlite(query)
            else:
                return {'error': f'Database type {self.config.db_type} not yet implemented'}
                
        except Exception as e:
            logger.error(f'Database error: {e}')
            logger.error(traceback.format_exc())
            
            # Provide helpful error messages (matching original pattern)
            if 'no such column' in str(e).lower():
                return {
                    'error': f'Please check your query, {e}. Use the table schema to regenerate the query'
                }
            elif 'no such table' in str(e).lower():
                return {'error': f'Table not found: {e}'}
            else:
                return {'error': str(e)}
    
    def _execute_sqlite(self, query: str) -> Dict[str, Any]:
        """Execute SQLite query."""
        with sqlite3.connect(self.config.connection_string) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query)
            
            # Limit results for safety
            rows = cursor.fetchmany(self.config.max_results)
            
            result = {
                'results': [dict(row) for row in rows],
                'count': len(rows),
                'limited': len(rows) == self.config.max_results
            }
            
            return result


class GenericMCPServerTemplate:
    """Generic MCP server template with extensible tool patterns."""
    
    def __init__(
        self,
        server_name: str,
        description: str = "Generic MCP server",
        host: str = "localhost", 
        port: int = 8080,
        transport: str = "stdio"
    ):
        self.server_name = server_name
        self.description = description
        self.host = host
        self.port = port
        self.transport = transport
        
        self.mcp = FastMCP(server_name, host=host, port=port)
        self.tool_handlers: Dict[str, ToolHandler] = {}
        
        # Add default system tools
        self._add_system_tools()
        
        logger.info(f'Initialized {server_name} MCP server template')
    
    def _add_system_tools(self):
        """Add default system monitoring tools."""
        
        @self.mcp.tool(
            name='health_check',
            description='Check the health status of the MCP server and all integrated services.'
        )
        def health_check() -> str:
            """Check health of server and all tool handlers."""
            health_status = {
                'server': self.server_name,
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'tools': {}
            }
            
            # Check each tool handler
            for name, handler in self.tool_handlers.items():
                try:
                    # Basic connectivity test
                    if isinstance(handler, APIToolHandler):
                        # Test API connectivity (lightweight check)
                        health_status['tools'][name] = {
                            'type': 'api',
                            'status': 'healthy',
                            'base_url': handler.config.base_url
                        }
                    elif isinstance(handler, DatabaseToolHandler):
                        # Test database connectivity
                        test_result = handler.execute("SELECT 1 as test")
                        health_status['tools'][name] = {
                            'type': 'database',
                            'status': 'healthy' if 'error' not in test_result else 'unhealthy',
                            'db_type': handler.config.db_type
                        }
                    else:
                        health_status['tools'][name] = {
                            'type': 'unknown',
                            'status': 'unknown'
                        }
                        
                except Exception as e:
                    health_status['tools'][name] = {
                        'status': 'unhealthy',
                        'error': str(e)
                    }
            
            # Overall status
            if any(tool.get('status') == 'unhealthy' for tool in health_status['tools'].values()):
                health_status['status'] = 'degraded'
            
            return json.dumps(health_status)
        
        @self.mcp.tool(
            name='list_tools',
            description='List all available tools and their capabilities.'
        )
        def list_tools() -> str:
            """List all registered tools."""
            tools_info = {
                'server': self.server_name,
                'description': self.description,
                'tools': []
            }
            
            for name, handler in self.tool_handlers.items():
                tool_def = handler.get_tool_definition()
                tools_info['tools'].append({
                    'name': name,
                    'description': tool_def.get('description', 'No description'),
                    'type': type(handler).__name__,
                    'parameters': tool_def.get('parameters', {})
                })
            
            return json.dumps(tools_info)
    
    def add_api_tool(self, name: str, config: APIConfig) -> 'GenericMCPServerTemplate':
        """Add an API integration tool."""
        handler = APIToolHandler(config)
        self.tool_handlers[name] = handler
        
        # Register with MCP
        tool_def = handler.get_tool_definition()
        
        @self.mcp.tool(
            name=tool_def['name'],
            description=tool_def['description']
        )
        def api_tool_wrapper(query: str, params: Optional[Dict] = None) -> str:
            result = handler.execute(query=query, params=params)
            return json.dumps(result)
        
        logger.info(f'Added API tool: {name}')
        return self
    
    def add_database_tool(self, name: str, config: DatabaseConfig) -> 'GenericMCPServerTemplate':
        """Add a database integration tool."""
        handler = DatabaseToolHandler(config)
        self.tool_handlers[name] = handler
        
        # Register with MCP
        tool_def = handler.get_tool_definition()
        
        @self.mcp.tool(
            name=tool_def['name'],
            description=tool_def['description']
        )
        def db_tool_wrapper(query: str) -> str:
            result = handler.execute(query=query)
            return json.dumps(result)
        
        logger.info(f'Added database tool: {name}')
        return self
    
    def add_custom_tool(
        self,
        name: str,
        description: str,
        handler_func: Callable,
        parameters: Dict[str, Any]
    ) -> 'GenericMCPServerTemplate':
        """Add a custom tool with user-defined handler."""
        
        @self.mcp.tool(name=name, description=description)
        def custom_tool_wrapper(**kwargs) -> str:
            try:
                result = handler_func(**kwargs)
                if isinstance(result, (dict, list)):
                    return json.dumps(result)
                return str(result)
            except Exception as e:
                logger.error(f'Custom tool {name} error: {e}')
                return json.dumps({'error': str(e)})
        
        logger.info(f'Added custom tool: {name}')
        return self
    
    def run(self):
        """Start the MCP server."""
        logger.info(
            f'{self.server_name} MCP server running at {self.host}:{self.port} '
            f'using {self.transport} transport'
        )
        logger.info(f'Registered {len(self.tool_handlers)} tool handlers')
        
        # Run the server
        self.mcp.run(transport=self.transport)


# Pre-configured tool factories for common use cases

def create_google_places_tool() -> APIConfig:
    """Create Google Places API tool configuration."""
    return APIConfig(
        name="query_places_data",
        description="Query Google Places API for location information",
        base_url="https://places.googleapis.com/v1/places:searchText",
        headers={
            'X-Goog-Api-Key': '',  # Will be set from env var
            'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress',
            'Content-Type': 'application/json'
        },
        auth_env_var='GOOGLE_PLACES_API_KEY',
        default_params={
            'languageCode': 'en',
            'maxResultCount': 10
        }
    )


def create_travel_database_tool(db_path: str) -> DatabaseConfig:
    """Create travel database tool configuration."""
    return DatabaseConfig(
        name="query_travel_data",
        description="Query travel database for airline, hotel, and car rental information",
        connection_string=db_path,
        db_type="sqlite",
        query_whitelist=[
            "SELECT * FROM airlines",
            "SELECT * FROM hotels", 
            "SELECT * FROM car_rentals",
            "SELECT * FROM bookings"
        ],
        max_results=100
    )


def create_weather_api_tool() -> APIConfig:
    """Create weather API tool configuration."""
    return APIConfig(
        name="query_weather_data",
        description="Query weather information for locations",
        base_url="https://api.openweathermap.org/data/2.5/weather",
        headers={'Content-Type': 'application/json'},
        auth_env_var='OPENWEATHER_API_KEY',
        default_params={
            'units': 'metric'
        }
    )


# Example usage and testing
if __name__ == "__main__":
    # Example: Create a travel services MCP server
    travel_server = GenericMCPServerTemplate(
        server_name="travel-services",
        description="Travel booking and search services MCP server",
        host="localhost",
        port=8080
    )
    
    # Add Google Places integration
    places_config = create_google_places_tool()
    travel_server.add_api_tool("google_places", places_config)
    
    # Add travel database
    travel_db_path = os.getenv('TRAVEL_DB', 'travel.db')
    travel_db_config = create_travel_database_tool(travel_db_path)
    travel_server.add_database_tool("travel_db", travel_db_config)
    
    # Add custom tool example
    def get_server_time() -> Dict[str, str]:
        return {
            'timestamp': datetime.now().isoformat(),
            'timezone': 'UTC'
        }
    
    travel_server.add_custom_tool(
        name="get_time",
        description="Get current server timestamp",
        handler_func=get_server_time,
        parameters={}
    )
    
    # Run the server
    travel_server.run()