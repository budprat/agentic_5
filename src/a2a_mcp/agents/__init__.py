# ABOUTME: Framework V2.0 agent exports for easy importing
# ABOUTME: Provides access to universal agent templates and specialized orchestrators

"""Framework V2.0 Agent Templates

This module exports the core Framework V2.0 agent classes:
- ADKServiceAgent: Universal template for all service agents
- MasterOrchestratorTemplate: Sophisticated multi-agent orchestration
- StandardizedAgentBase: Advanced base class with quality framework (via common)
"""

# Import from common module where these actually exist
from ..common.adk_service_agent import ADKServiceAgent
from ..common.master_orchestrator_template import MasterOrchestratorTemplate
from ..common.standardized_agent_base import StandardizedAgentBase

__all__ = [
    'ADKServiceAgent',              # Framework V2.0 universal service template
    'MasterOrchestratorTemplate',   # Framework V2.0 orchestration template  
    'StandardizedAgentBase'         # Advanced base with quality + A2A
]