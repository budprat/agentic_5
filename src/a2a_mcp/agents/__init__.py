# ABOUTME: Framework V2.0 agent exports for easy importing
# ABOUTME: Provides access to universal agent templates and specialized orchestrators

"""Framework V2.0 Agent Templates

This module exports the core Framework V2.0 agent classes:
- ADKServiceAgent: Universal template for all service agents
- MasterOrchestratorTemplate: Sophisticated multi-agent orchestration
- StandardizedAgentBase: Advanced base class with quality framework (via common)
"""

from .adk_service_agent import ADKServiceAgent
from .master_orchestrator_template import MasterOrchestratorTemplate

# Import StandardizedAgentBase from common module
from ..common.standardized_agent_base import StandardizedAgentBase

__all__ = [
    'ADKServiceAgent',              # Framework V2.0 universal service template
    'MasterOrchestratorTemplate',   # Framework V2.0 orchestration template  
    'StandardizedAgentBase'         # Advanced base with quality + A2A
]