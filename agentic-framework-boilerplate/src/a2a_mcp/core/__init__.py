# ABOUTME: Core module for A2A MCP framework
# ABOUTME: Contains base classes and protocols for agent communication

from .agent import Agent, AgentCapability
from .protocol import (
    A2AMessage, MessageType, MessageStatus, ProtocolVersion,
    A2AProtocol, ProtocolError, MessageValidator
)
from .quality import (
    QualityFramework, QualityMetric, QualityReport, QualityIssue,
    QualityLevel, ValidationRule, MetricType
)

__all__ = [
    # Agent
    'Agent',
    'AgentCapability',
    
    # Protocol
    'A2AMessage',
    'MessageType',
    'MessageStatus',
    'ProtocolVersion',
    'A2AProtocol',
    'ProtocolError',
    'MessageValidator',
    
    # Quality
    'QualityFramework',
    'QualityMetric',
    'QualityReport',
    'QualityIssue',
    'QualityLevel',
    'ValidationRule',
    'MetricType',
]