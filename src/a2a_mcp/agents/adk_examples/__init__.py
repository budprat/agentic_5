# ABOUTME: ADK examples package initialization
# ABOUTME: Exports key classes and patterns for Google ADK integration

from .tier1_sequential_orchestrator import ContentCreationOrchestrator
from .tier2_domain_specialist import (
    FinancialDomainSpecialist,
    TechnicalDomainSpecialist, 
    HealthcareDomainSpecialist,
    MultiDomainCoordinator
)
from .tier3_service_agent import (
    DataProcessingServiceAgent,
    APIIntegrationServiceAgent,
    FileOperationsServiceAgent,
    ComputationServiceAgent,
    ServiceCoordinator
)
from .advanced_orchestration_patterns import (
    HybridOrchestrationPattern,
    DynamicRoutingOrchestrator,
    AdaptiveWorkflowOrchestrator
)
from .complete_system_example import InvestmentAnalysisSystem

__all__ = [
    # Tier 1 Orchestrators
    'ContentCreationOrchestrator',
    
    # Tier 2 Domain Specialists
    'FinancialDomainSpecialist',
    'TechnicalDomainSpecialist',
    'HealthcareDomainSpecialist', 
    'MultiDomainCoordinator',
    
    # Tier 3 Service Agents
    'DataProcessingServiceAgent',
    'APIIntegrationServiceAgent',
    'FileOperationsServiceAgent',
    'ComputationServiceAgent',
    'ServiceCoordinator',
    
    # Advanced Patterns
    'HybridOrchestrationPattern',
    'DynamicRoutingOrchestrator',
    'AdaptiveWorkflowOrchestrator',
    
    # Complete Example
    'InvestmentAnalysisSystem'
]