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


def main():
    """Main entry point for the A2A MCP Framework CLI."""
    import sys
    from pathlib import Path
    
    # Add the agents module to path for easy access
    agents_path = Path(__file__).parent / "agents"
    if agents_path.exists():
        sys.path.insert(0, str(agents_path))
    
    # Import and run the main agents entry point
    try:
        from a2a_mcp.agents.__main__ import main as agents_main
        agents_main()
    except ImportError:
        print("A2A MCP Framework - Available modules:")
        print("  - agents: Multi-agent system components")
        print("  - common: Shared utilities and base classes")
        print("  - mcp: Model Context Protocol server")
        print("  - core: Core abstractions and protocols")
        print("\nUse 'start-mcp' command to launch MCP server")
        print("Use 'launch-system' command to launch multi-agent system")


if __name__ == "__main__":
    main()