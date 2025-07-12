# ABOUTME: Export example domain agents for easy importing
# ABOUTME: Provides MasterOracleAgent, ResearchSpecialistAgent, and ServiceAgent

"""
Example Domain Agents

This module provides example implementations of the three-tier agent hierarchy:
- Tier 1: MasterOracleAgent - Orchestrates and coordinates other agents
- Tier 2: ResearchSpecialistAgent - Domain-specific research and analysis
- Tier 3: ServiceAgent - Tool-focused service operations
"""

from .master_oracle import MasterOracleAgent
from .domain_specialist import ResearchSpecialistAgent
from .service_agent import ServiceAgent

__all__ = [
    'MasterOracleAgent',
    'ResearchSpecialistAgent', 
    'ServiceAgent'
]