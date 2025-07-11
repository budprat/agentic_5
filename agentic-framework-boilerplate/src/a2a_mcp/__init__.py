# ABOUTME: Main package initialization for A2A MCP framework
# ABOUTME: Exports key classes and modules for easy access

"""
A2A MCP Framework - Agent-to-Agent Model Context Protocol

A framework for building and coordinating AI agents that can communicate
and collaborate using a standardized protocol.
"""

__version__ = "0.1.0"

# Core abstractions
from a2a_mcp.core.agent import Agent, AgentCapability
from a2a_mcp.core.protocol import (
    A2AMessage,
    A2AProtocol,
    MessageType,
    MessageStatus,
    ProtocolVersion,
    ProtocolError
)
from a2a_mcp.core.quality import (
    QualityFramework,
    QualityMetric,
    QualityReport,
    QualityLevel,
    ValidationRule
)

# Common implementations
from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.common.a2a_protocol import A2AProtocolClient
from a2a_mcp.common.quality_framework import QualityThresholdFramework

__all__ = [
    # Version
    "__version__",
    
    # Core abstractions
    "Agent",
    "AgentCapability",
    "A2AMessage",
    "A2AProtocol",
    "MessageType",
    "MessageStatus", 
    "ProtocolVersion",
    "ProtocolError",
    "QualityFramework",
    "QualityMetric",
    "QualityReport",
    "QualityLevel",
    "ValidationRule",
    
    # Common implementations
    "BaseAgent",
    "StandardizedAgentBase",
    "A2AProtocolClient",
    "QualityThresholdFramework",
]