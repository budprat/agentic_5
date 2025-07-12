"""Configuration loader for remote MCP servers."""

import json
import os
from pathlib import Path
from typing import Dict, Any
from mcp.server.fastmcp.utilities.logging import get_logger

logger = get_logger(__name__)


def load_mcp_config() -> Dict[str, Any]:
    """Load MCP configuration from .mcp.json file.
    
    Returns:
        Dictionary containing MCP server configurations
    """
    config_path = Path('.mcp.json')
    
    if not config_path.exists():
        logger.warning('.mcp.json not found, using empty configuration')
        return {}
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config.get('mcpServers', {})
    except Exception as e:
        logger.error(f'Error loading .mcp.json: {e}')
        return {}


def transform_config_for_remote_connector(mcp_config: Dict[str, Any]) -> Dict[str, Any]:
    """Transform .mcp.json format to remote connector format.
    
    Args:
        mcp_config: Dictionary from .mcp.json
        
    Returns:
        Transformed configuration for remote connector
    """
    transformed = {}
    
    for name, config in mcp_config.items():
        # Skip if no type specified
        if 'type' not in config:
            continue
            
        server_config = {
            'transport': config['type'],  # 'stdio' or 'sse'
            'description': f'Remote MCP server: {name}'
        }
        
        if config['type'] == 'stdio':
            server_config['command'] = config.get('command', 'npx')
            server_config['args'] = config.get('args', [])
            server_config['env'] = config.get('env', {})
        elif config['type'] == 'sse':
            # For SSE, we need URL which might be in args or env
            if 'url' in config:
                server_config['url'] = config['url']
            else:
                # Try to construct URL from args if possible
                logger.warning(f'SSE server {name} has no URL specified')
                continue
        
        transformed[name] = server_config
    
    return transformed


def get_remote_mcp_servers() -> Dict[str, Any]:
    """Get all remote MCP server configurations ready for use.
    
    Returns:
        Dictionary of remote MCP server configurations
    """
    mcp_config = load_mcp_config()
    return transform_config_for_remote_connector(mcp_config)


def filter_enabled_servers(servers: Dict[str, Any]) -> Dict[str, Any]:
    """Filter servers that have required credentials configured.
    
    Args:
        servers: Dictionary of server configurations
        
    Returns:
        Filtered dictionary with only enabled servers
    """
    enabled = {}
    
    for name, config in servers.items():
        # Check if required environment variables are set
        if 'env' in config:
            all_vars_set = True
            for key, value in config['env'].items():
                # Skip if value is a placeholder
                if value and value.startswith('your-') or value == '':
                    logger.info(f'Server {name} skipped - {key} not configured')
                    all_vars_set = False
                    break
            
            if not all_vars_set:
                continue
        
        enabled[name] = config
    
    return enabled