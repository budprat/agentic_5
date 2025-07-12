# ABOUTME: Utility functions for the A2A MCP framework
# ABOUTME: Provides logging, configuration, and helper functions

import logging
import os
import uuid
import asyncio
from typing import Optional, Dict, Any, TypeVar, Callable
from pathlib import Path
import json
import yaml
from datetime import datetime, timezone
from functools import wraps
import time

from a2a_mcp.common.types import ServerConfig


logger = logging.getLogger(__name__)


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix.
    
    Args:
        prefix: Optional prefix for the ID
        
    Returns:
        Unique ID string
    """
    unique_id = str(uuid.uuid4())
    return f"{prefix}-{unique_id}" if prefix else unique_id


def utc_now() -> datetime:
    """Get current UTC datetime.
    
    Returns:
        Current datetime in UTC timezone
    """
    return datetime.now(timezone.utc)


def config_logging(level: Optional[str] = None):
    """Configure basic logging for the framework.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR). 
               Defaults to env var A2A_LOG_LEVEL or INFO.
    """
    log_level = level or os.getenv('A2A_LOG_LEVEL', 'INFO').upper()
    
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def config_logger(logger_instance: logging.Logger, level: Optional[str] = None):
    """Configure a specific logger instance.
    
    Args:
        logger_instance: The logger to configure
        level: Logging level for this logger
    """
    log_level = level or os.getenv('A2A_LOG_LEVEL', 'INFO').upper()
    logger_instance.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Avoid adding duplicate handlers
    if not logger_instance.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level, logging.INFO))
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        logger_instance.addHandler(console_handler)


def get_mcp_server_config() -> ServerConfig:
    """Get the MCP server configuration from environment or defaults.
    
    Returns:
        ServerConfig with host, port, transport, and URL settings
    """
    host = os.getenv('MCP_SERVER_HOST', 'localhost')
    port = int(os.getenv('MCP_SERVER_PORT', '10100'))
    transport = os.getenv('MCP_SERVER_TRANSPORT', 'sse')
    
    # Build URL based on transport type
    if transport == 'sse':
        url = f'http://{host}:{port}/sse'
    else:
        url = f'http://{host}:{port}'
    
    return ServerConfig(
        host=host,
        port=port,
        transport=transport,
        url=url,
    )


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML or JSON file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If file format is unsupported
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(path, 'r') as f:
        if path.suffix in ['.yaml', '.yml']:
            return yaml.safe_load(f)
        elif path.suffix == '.json':
            return json.load(f)
        else:
            raise ValueError(f"Unsupported config format: {path.suffix}")


def ensure_directory(directory: str) -> Path:
    """Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Path to directory
        
    Returns:
        Path object for the directory
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_agent_card_path(agent_id: str) -> str:
    """Get the path to an agent's card file.
    
    Args:
        agent_id: The agent's identifier
        
    Returns:
        Path to the agent card JSON file
    """
    base_dir = os.getenv('AGENT_CARDS_DIR', 'agent_cards')
    return os.path.join(base_dir, f"{agent_id}.json")


def format_agent_id(name: str) -> str:
    """Format an agent name into a valid agent ID.
    
    Args:
        name: Human-readable agent name
        
    Returns:
        Formatted agent ID (lowercase, underscores for spaces)
    """
    return name.lower().replace(' ', '_').replace('-', '_')


def parse_capability_string(capability: str) -> Dict[str, Any]:
    """Parse a capability string into structured format.
    
    Args:
        capability: Capability string (e.g., "search:web:google")
        
    Returns:
        Dictionary with parsed capability information
    """
    parts = capability.split(':')
    return {
        'category': parts[0] if len(parts) > 0 else 'general',
        'type': parts[1] if len(parts) > 1 else None,
        'provider': parts[2] if len(parts) > 2 else None,
        'full': capability
    }


def validate_agent_config(config: Dict[str, Any]) -> bool:
    """Validate an agent configuration dictionary.
    
    Args:
        config: Agent configuration to validate
        
    Returns:
        True if valid, raises ValueError if not
    """
    required_fields = ['agent_id', 'name', 'capabilities']
    
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required field: {field}")
    
    if not isinstance(config['capabilities'], list):
        raise ValueError("Capabilities must be a list")
    
    return True


async def initialize_a2a_connection_pool(**kwargs) -> None:
    """Initialize the global A2A connection pool.
    
    This should be called once at application startup to enable
    connection pooling for 60% performance improvement.
    
    Args:
        **kwargs: Configuration options for the connection pool
                  (see A2AConnectionPool for available options)
    """
    from a2a_mcp.common.a2a_connection_pool import initialize_global_pool
    
    logger.info("Initializing A2A connection pool for optimized performance")
    await initialize_global_pool(**kwargs)
    logger.info("A2A connection pool initialized successfully")


async def shutdown_a2a_connection_pool() -> None:
    """Shutdown the global A2A connection pool.
    
    This should be called at application shutdown to properly
    close all persistent connections.
    """
    from a2a_mcp.common.a2a_connection_pool import shutdown_global_pool
    
    logger.info("Shutting down A2A connection pool")
    await shutdown_global_pool()
    logger.info("A2A connection pool shutdown complete")