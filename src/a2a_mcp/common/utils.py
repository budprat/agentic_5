# ABOUTME: Common utility functions for the A2A MCP framework
# ABOUTME: Provides helper functions for logging, async operations, and data handling

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union
from uuid import uuid4

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    import structlog
except ImportError:
    structlog = None

try:
    import yaml
except ImportError:
    yaml = None

from a2a_mcp.common.types import ServerConfig

# Type variables for generic functions
T = TypeVar('T')
AsyncFunc = TypeVar('AsyncFunc', bound=Callable[..., Any])

logger = logging.getLogger(__name__)


# Original utility functions
def init_api_key():
    """Initialize the API key for Google Generative AI."""
    if not genai:
        logger.warning('google.generativeai not installed, skipping API key init')
        return
        
    if not os.getenv('GOOGLE_API_KEY'):
        logger.error('GOOGLE_API_KEY is not set')
        raise ValueError('GOOGLE_API_KEY is not set')

    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))


def config_logging():
    """Configure basic logging."""
    log_level = (
        os.getenv('A2A_LOG_LEVEL') or os.getenv('FASTMCP_LOG_LEVEL') or 'INFO'
    ).upper()
    logging.basicConfig(level=getattr(logging, log_level, logging.INFO))


def config_logger(logger):
    """Logger specific config, avoiding clutter in enabling all loggging."""
    # TODO: replace with env
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def get_mcp_server_config() -> ServerConfig:
    """Get the MCP server configuration."""
    return ServerConfig(
        host='localhost',
        port=10100,
        transport='sse',
        url='http://localhost:10100/sse',
    )


# Enhanced Logging Configuration
def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    structured: bool = True
) -> logging.Logger:
    """
    Set up structured logging for the application
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional path to log file
        structured: Whether to use structured logging
        
    Returns:
        Configured logger instance
    """
    # Configure stdlib logging
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers
    )
    
    if structured and structlog:
        # Configure structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        return structlog.get_logger()
    else:
        return logging.getLogger(__name__)


# ID Generation
def generate_id(prefix: str = "") -> str:
    """
    Generate a unique ID with optional prefix
    
    Args:
        prefix: Optional prefix for the ID
        
    Returns:
        Unique ID string
    """
    base_id = str(uuid4())
    return f"{prefix}-{base_id}" if prefix else base_id


# Time Utilities
def utc_now() -> datetime:
    """Get current UTC timestamp"""
    return datetime.now(timezone.utc)


def timestamp_str() -> str:
    """Get current timestamp as ISO format string"""
    return utc_now().isoformat()


# Async Utilities
async def run_with_timeout(
    coro: Callable[..., T],
    timeout: float,
    *args,
    **kwargs
) -> Optional[T]:
    """
    Run a coroutine with a timeout
    
    Args:
        coro: Coroutine to run
        timeout: Timeout in seconds
        *args: Positional arguments for coroutine
        **kwargs: Keyword arguments for coroutine
        
    Returns:
        Result of coroutine or None if timeout
    """
    try:
        return await asyncio.wait_for(
            coro(*args, **kwargs),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        return None


def retry_async(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for retrying async functions
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries
        backoff: Backoff multiplier for delay
        exceptions: Tuple of exceptions to catch
    """
    def decorator(func: AsyncFunc) -> AsyncFunc:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        raise last_exception
            
            raise last_exception
        
        return wrapper
    return decorator


# Data Utilities
def safe_json_loads(
    data: Union[str, bytes],
    default: Any = None
) -> Any:
    """
    Safely load JSON data with fallback
    
    Args:
        data: JSON string or bytes
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(
    obj: Any,
    indent: Optional[int] = None,
    default: Optional[Callable] = None
) -> str:
    """
    Safely dump object to JSON string
    
    Args:
        obj: Object to serialize
        indent: Indentation for pretty printing
        default: Function to handle non-serializable objects
        
    Returns:
        JSON string
    """
    def json_default(o):
        if hasattr(o, 'to_dict'):
            return o.to_dict()
        elif hasattr(o, '__dict__'):
            return o.__dict__
        elif isinstance(o, datetime):
            return o.isoformat()
        elif default:
            return default(o)
        else:
            return str(o)
    
    return json.dumps(obj, indent=indent, default=json_default)


# Configuration Utilities
def load_yaml_config(path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load YAML configuration file
    
    Args:
        path: Path to YAML file
        
    Returns:
        Parsed configuration dictionary
    """
    if not yaml:
        raise ImportError("PyYAML is not installed. Please install it to use YAML configuration.")
    
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    
    with open(path, 'r') as f:
        return yaml.safe_load(f) or {}


def merge_configs(
    base: Dict[str, Any],
    override: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Deep merge configuration dictionaries
    
    Args:
        base: Base configuration
        override: Override configuration
        
    Returns:
        Merged configuration
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    
    return result


# Validation Utilities
def validate_required_fields(
    data: Dict[str, Any],
    required: List[str]
) -> Optional[str]:
    """
    Validate that required fields are present in data
    
    Args:
        data: Data dictionary to validate
        required: List of required field names
        
    Returns:
        Error message if validation fails, None if valid
    """
    missing = [field for field in required if field not in data or data[field] is None]
    
    if missing:
        return f"Missing required fields: {', '.join(missing)}"
    
    return None


# Performance Utilities
class Timer:
    """Context manager for timing operations"""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.duration = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        self.duration = self.end_time - self.start_time
        return False
    
    def __str__(self):
        return f"{self.name} took {self.duration:.4f} seconds"


# Error Handling Utilities
class A2AError(Exception):
    """Base exception for A2A framework errors"""
    pass


class ValidationError(A2AError):
    """Raised when validation fails"""
    pass


class CommunicationError(A2AError):
    """Raised when agent communication fails"""
    pass


class TimeoutError(A2AError):
    """Raised when operation times out"""
    pass


# Batch Processing Utilities
async def process_in_batches(
    items: List[T],
    batch_size: int,
    processor: Callable[[List[T]], Any],
    delay_between_batches: float = 0.0
) -> List[Any]:
    """
    Process items in batches with optional delay
    
    Args:
        items: List of items to process
        batch_size: Size of each batch
        processor: Async function to process a batch
        delay_between_batches: Delay in seconds between batches
        
    Returns:
        List of results from all batches
    """
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        result = await processor(batch)
        results.append(result)
        
        if delay_between_batches > 0 and i + batch_size < len(items):
            await asyncio.sleep(delay_between_batches)
    
    return results


# State Management Utilities
class StateManager:
    """Simple state management for agents"""
    
    def __init__(self):
        self._state: Dict[str, Any] = {}
        self._state_history: List[Dict[str, Any]] = []
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get state value"""
        return self._state.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set state value"""
        self._state[key] = value
        self._state_history.append({
            'timestamp': timestamp_str(),
            'key': key,
            'value': value,
            'action': 'set'
        })
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple state values"""
        self._state.update(updates)
        self._state_history.append({
            'timestamp': timestamp_str(),
            'updates': updates,
            'action': 'update'
        })
    
    def clear(self) -> None:
        """Clear all state"""
        self._state.clear()
        self._state_history.append({
            'timestamp': timestamp_str(),
            'action': 'clear'
        })
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get state change history"""
        return self._state_history.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """Export current state as dictionary"""
        return self._state.copy()


# Rate Limiting Utilities
class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, calls_per_second: float):
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second
        self.last_call_time = 0.0
    
    async def acquire(self) -> None:
        """Wait if necessary to respect rate limit"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.min_interval:
            wait_time = self.min_interval - time_since_last_call
            await asyncio.sleep(wait_time)
        
        self.last_call_time = time.time()


# Export commonly used utilities
__all__ = [
    # Original functions
    'init_api_key',
    'config_logging',
    'config_logger',
    'get_mcp_server_config',
    
    # Enhanced functions
    'setup_logging',
    'generate_id',
    'utc_now',
    'timestamp_str',
    'run_with_timeout',
    'retry_async',
    'safe_json_loads',
    'safe_json_dumps',
    'load_yaml_config',
    'merge_configs',
    'validate_required_fields',
    'process_in_batches',
    
    # Classes
    'Timer',
    'StateManager',
    'RateLimiter',
    
    # Exceptions
    'A2AError',
    'ValidationError',
    'CommunicationError',
    'TimeoutError',
]