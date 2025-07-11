"""ABOUTME: Common utilities and base classes for the A2A MCP framework.
ABOUTME: Contains standardized agents, protocols, and quality frameworks."""

# Import submodules to make them available
from . import types
from . import utils
from . import quality_framework
from . import base_agent
from . import a2a_protocol
from . import standardized_agent_base

# Import key classes for convenience
from .standardized_agent_base import StandardizedAgentBase
from .quality_framework import QualityDomain, QualityThresholdFramework
from .a2a_protocol import A2AProtocolClient
from .base_agent import BaseAgent

__all__ = [
    'types', 'utils', 'quality_framework', 'base_agent', 'a2a_protocol', 'standardized_agent_base',
    'StandardizedAgentBase', 'QualityDomain', 'QualityThresholdFramework', 'A2AProtocolClient', 'BaseAgent'
]