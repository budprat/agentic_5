"""
ABOUTME: Research assistant agent package
ABOUTME: Exports the main research orchestrator and enhanced versions
"""

from .agent import research_orchestrator
from .a2a_enhanced_orchestrator import A2AEnhancedOrchestrator, create_enhanced_orchestrator

__all__ = [
    "research_orchestrator",
    "A2AEnhancedOrchestrator",
    "create_enhanced_orchestrator"
]