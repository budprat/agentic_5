"""
ABOUTME: Research Assistant Orchestrator package initialization
ABOUTME: Exports the A2A-enhanced research orchestrator and sub-agents
"""

from .research_assistant_agent.a2a_enhanced_orchestrator import A2AEnhancedOrchestrator
from .research_assistant_agent.agent import research_orchestrator

__all__ = ["A2AEnhancedOrchestrator", "research_orchestrator"]