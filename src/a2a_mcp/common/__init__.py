"""ABOUTME: Common utilities and base classes for the A2A MCP framework.
ABOUTME: Contains standardized agents, protocols, and quality frameworks."""

# Import submodules to make them available
from . import types
from . import utils
from . import quality_framework
from . import base_agent
from . import a2a_protocol
from . import standardized_agent_base
from . import a2a_connection_pool
from . import response_formatter
from . import config_manager
from . import metrics_collector

# Import key classes for convenience
from .standardized_agent_base import StandardizedAgentBase
from .quality_framework import QualityDomain, QualityThresholdFramework
from .a2a_protocol import A2AProtocolClient
from .base_agent import BaseAgent
from .a2a_connection_pool import A2AConnectionPool, get_global_connection_pool
from .response_formatter import ResponseFormatter
from .utils import initialize_a2a_connection_pool, shutdown_a2a_connection_pool
from .config_manager import (
    ConfigManager, FrameworkConfig, AgentConfig,
    get_config_manager, get_config, get_agent_config, reload_config
)
from .metrics_collector import (
    MetricsCollector, get_metrics_collector,
    record_agent_request, record_a2a_message, get_metrics_summary
)

__all__ = [
    'types', 'utils', 'quality_framework', 'base_agent', 'a2a_protocol', 'standardized_agent_base',
    'a2a_connection_pool', 'response_formatter', 'config_manager', 'metrics_collector',
    'StandardizedAgentBase', 'QualityDomain', 'QualityThresholdFramework', 'A2AProtocolClient', 'BaseAgent',
    'A2AConnectionPool', 'get_global_connection_pool', 'ResponseFormatter',
    'initialize_a2a_connection_pool', 'shutdown_a2a_connection_pool',
    'ConfigManager', 'FrameworkConfig', 'AgentConfig',
    'get_config_manager', 'get_config', 'get_agent_config', 'reload_config',
    'MetricsCollector', 'get_metrics_collector',
    'record_agent_request', 'record_a2a_message', 'get_metrics_summary'
]