"""
Generic Agent Registry Template for Framework V2.0 Domain Implementation.

This template provides the standard pattern for organizing domain agents in a tier-based architecture.
Domains should copy this template and customize it with their specific agents and capabilities.

Framework V2.0 Tier Architecture:
- Tier 1: Master Orchestrators (1 per domain) - ports 10x01
- Tier 2: Domain Specialists (3-6 per domain) - ports 10x02-10x09  
- Tier 3: Intelligence Modules (10-50 per domain) - ports 10x10-10x99

Port Allocation Convention:
- Domain range: 10x00-10x99 where x is domain identifier
- Example: Domain 1 = 10100-10199, Domain 2 = 10200-10299, etc.
"""

from typing import Dict, Any, Type
from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase

# Default instructions for agents without specific prompts
DEFAULT_TIER1_INSTRUCTIONS = """
You are a Master Orchestrator in Framework V2.0's tier-based architecture.
Your role is to:
1. Analyze incoming queries to determine which domain specialists to activate
2. Coordinate responses from multiple domain specialists (Tier 2)
3. Synthesize cross-domain insights into comprehensive recommendations
4. Ensure quality and coherence across all analyses
5. Provide executive-level summaries and action plans

Return structured responses with executive summaries, key insights, and actionable recommendations.
"""

DEFAULT_TIER2_INSTRUCTIONS = """
You are a domain specialist in Framework V2.0's tier-based architecture.
Analyze queries related to your domain and coordinate with relevant intelligence modules.
Provide structured insights and actionable recommendations.
"""

DEFAULT_TIER3_INSTRUCTIONS = """
You are a specialized intelligence module in Framework V2.0's tier-based architecture.
Perform focused analysis in your area of expertise.
Return structured data that can be synthesized by higher-tier agents.
"""

# Template agent definitions - domains should customize these
TEMPLATE_DOMAIN_AGENTS = {
    # TIER 1: Master Orchestrator (1 agent per domain)
    "Template Master Orchestrator": {
        "port": 10001,  # Change to your domain's base port + 01
        "tier": 1,
        "template": "MasterOrchestratorTemplate",  # Use this template for Tier 1
        "description": "Master orchestrator for [DOMAIN_NAME] intelligence",
        "instructions": DEFAULT_TIER1_INSTRUCTIONS,
        "quality_domain": "BUSINESS",  # Adjust: TECHNICAL, BUSINESS, CREATIVE, SERVICE
        "capabilities": ["orchestration", "synthesis", "coordination"]
    },
    
    # TIER 2: Domain Specialists (3-6 agents per domain)
    "Template Analysis Specialist": {
        "port": 10002,  # Change to your domain's base port + 02
        "tier": 2,
        "template": "StandardizedAgentBase",  # Use this template for Tier 2
        "description": "Analysis and research specialist for [DOMAIN_NAME]",
        "instructions": DEFAULT_TIER2_INSTRUCTIONS,
        "quality_domain": "TECHNICAL",
        "capabilities": ["analysis", "research", "assessment"]
    },
    "Template Implementation Specialist": {
        "port": 10003,  # Change to your domain's base port + 03
        "tier": 2,
        "template": "StandardizedAgentBase",  # Use this template for Tier 2
        "description": "Implementation and execution specialist for [DOMAIN_NAME]",
        "instructions": DEFAULT_TIER2_INSTRUCTIONS,
        "quality_domain": "TECHNICAL",
        "capabilities": ["implementation", "execution", "deployment"]
    },
    "Template Optimization Specialist": {
        "port": 10004,  # Change to your domain's base port + 04
        "tier": 2,
        "template": "StandardizedAgentBase",  # Use this template for Tier 2
        "description": "Optimization and improvement specialist for [DOMAIN_NAME]",
        "instructions": DEFAULT_TIER2_INSTRUCTIONS,
        "quality_domain": "BUSINESS",
        "capabilities": ["optimization", "improvement", "efficiency"]
    },
    
    # TIER 3: Intelligence Modules (10-50 agents per domain)
    # Core Intelligence Modules (10x10-10x19)
    "Template Data Analyzer": {
        "port": 10010,  # Change to your domain's base port + 10
        "tier": 3,
        "template": "ADKServiceAgent",  # Use ADKServiceAgent or StandardizedAgentBase for Tier 3
        "description": "Data analysis and pattern recognition for [DOMAIN_NAME]",
        "instructions": DEFAULT_TIER3_INSTRUCTIONS,
        "quality_domain": "TECHNICAL",
        "capabilities": ["data_analysis", "pattern_recognition"]
    },
    "Template Performance Monitor": {
        "port": 10011,  # Change to your domain's base port + 11
        "tier": 3,
        "template": "ADKServiceAgent",
        "description": "Performance monitoring and metrics for [DOMAIN_NAME]",
        "instructions": DEFAULT_TIER3_INSTRUCTIONS,
        "quality_domain": "TECHNICAL",
        "capabilities": ["monitoring", "metrics", "performance"]
    },
    "Template Quality Validator": {
        "port": 10012,  # Change to your domain's base port + 12
        "tier": 3,
        "template": "StandardizedAgentBase",  # More complex logic, use StandardizedAgentBase
        "description": "Quality validation and standards compliance for [DOMAIN_NAME]",
        "instructions": DEFAULT_TIER3_INSTRUCTIONS,
        "quality_domain": "SERVICE",
        "capabilities": ["validation", "compliance", "standards"]
    },
    
    # Specialized Intelligence Modules (10x20-10x29)
    "Template Integration Manager": {
        "port": 10020,  # Change to your domain's base port + 20
        "tier": 3,
        "template": "ADKServiceAgent",
        "description": "Integration and coordination management for [DOMAIN_NAME]",
        "instructions": DEFAULT_TIER3_INSTRUCTIONS,
        "quality_domain": "TECHNICAL",
        "capabilities": ["integration", "coordination", "workflow"]
    },
    "Template Knowledge Synthesizer": {
        "port": 10021,  # Change to your domain's base port + 21
        "tier": 3,
        "template": "StandardizedAgentBase",
        "description": "Knowledge synthesis and insight generation for [DOMAIN_NAME]",
        "instructions": DEFAULT_TIER3_INSTRUCTIONS,
        "quality_domain": "CREATIVE",
        "capabilities": ["synthesis", "insights", "knowledge_management"]
    },
    
    # Domain-Specific Modules (10x30-10x99) - Add your specific agents here
    # Example:
    # "Your Specific Agent": {
    #     "port": 10030,
    #     "tier": 3,
    #     "template": "ADKServiceAgent",  # or "StandardizedAgentBase"
    #     "description": "Your agent description",
    #     "instructions": "Your specific instructions...",
    #     "quality_domain": "TECHNICAL",  # or BUSINESS, CREATIVE, SERVICE
    #     "capabilities": ["capability1", "capability2"]
    # },
}

def create_agent(agent_name: str, base_agent_class: Type[StandardizedAgentBase] = None) -> StandardizedAgentBase:
    """
    Factory function to create any agent from the registry.
    
    Args:
        agent_name: Name of the agent to create
        base_agent_class: Optional custom base class (for domain-specific agents)
    
    Returns:
        Configured agent instance
    """
    if agent_name not in TEMPLATE_DOMAIN_AGENTS:
        raise ValueError(f"Unknown agent: {agent_name}. Available agents: {list(TEMPLATE_DOMAIN_AGENTS.keys())}")
    
    config = TEMPLATE_DOMAIN_AGENTS[agent_name]
    
    # Import the appropriate template based on tier and template specification
    template_name = config.get("template", "StandardizedAgentBase")
    
    if template_name == "MasterOrchestratorTemplate":
        from a2a_mcp.common.master_orchestrator_template import MasterOrchestratorTemplate
        # Note: MasterOrchestratorTemplate has different initialization
        # Domains should implement their own factory method for Tier 1 agents
        raise NotImplementedError("MasterOrchestratorTemplate requires custom initialization. See domain examples.")
    
    elif template_name == "ADKServiceAgent":
        from a2a_mcp.common.adk_service_agent import ADKServiceAgent
        agent_class = ADKServiceAgent
    
    else:  # StandardizedAgentBase (default)
        from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
        agent_class = StandardizedAgentBase
    
    # Use custom base class if provided
    if base_agent_class:
        agent_class = base_agent_class
    
    return agent_class(
        agent_name=agent_name,
        description=config.get("description", f"{agent_name} - Tier {config['tier']} agent"),
        instructions=config.get("instructions", DEFAULT_TIER3_INSTRUCTIONS),
        quality_config={"domain": config.get("quality_domain", "TECHNICAL")},
        mcp_tools_enabled=True,
        a2a_enabled=True
    )

def get_agents_by_tier(tier: int) -> Dict[str, Dict[str, Any]]:
    """Get all agents of a specific tier."""
    return {
        name: config 
        for name, config in TEMPLATE_DOMAIN_AGENTS.items() 
        if config["tier"] == tier
    }

def get_agents_by_template(template: str) -> Dict[str, Dict[str, Any]]:
    """Get all agents using a specific template."""
    return {
        name: config 
        for name, config in TEMPLATE_DOMAIN_AGENTS.items() 
        if config.get("template", "StandardizedAgentBase") == template
    }

def get_agents_by_capability(capability: str) -> Dict[str, Dict[str, Any]]:
    """Get all agents with a specific capability."""
    return {
        name: config 
        for name, config in TEMPLATE_DOMAIN_AGENTS.items() 
        if capability in config.get("capabilities", [])
    }

def get_port_range() -> Dict[str, int]:
    """Get the port range used by this domain."""
    ports = [config["port"] for config in TEMPLATE_DOMAIN_AGENTS.values()]
    return {
        "min_port": min(ports),
        "max_port": max(ports),
        "total_agents": len(ports)
    }

def get_agent_count() -> Dict[str, int]:
    """Get count of agents by tier."""
    tier_counts = {}
    template_counts = {}
    
    for config in TEMPLATE_DOMAIN_AGENTS.values():
        tier = config["tier"]
        template = config.get("template", "StandardizedAgentBase")
        
        tier_counts[f"tier_{tier}"] = tier_counts.get(f"tier_{tier}", 0) + 1
        template_counts[template] = template_counts.get(template, 0) + 1
    
    return {
        "total": len(TEMPLATE_DOMAIN_AGENTS),
        "by_tier": tier_counts,
        "by_template": template_counts
    }

def validate_agent_registry() -> list[str]:
    """
    Validate the agent registry for Framework V2.0 compliance.
    
    Returns:
        List of validation issues (empty if valid)
    """
    issues = []
    
    # Check tier distribution
    tier_counts = get_agent_count()["by_tier"]
    
    if tier_counts.get("tier_1", 0) != 1:
        issues.append("Domain must have exactly 1 Tier 1 agent (Master Orchestrator)")
    
    if tier_counts.get("tier_2", 0) < 2:
        issues.append("Domain should have at least 2 Tier 2 agents (Domain Specialists)")
    
    if tier_counts.get("tier_3", 0) < 5:
        issues.append("Domain should have at least 5 Tier 3 agents (Intelligence Modules)")
    
    # Check port assignments
    ports = [config["port"] for config in TEMPLATE_DOMAIN_AGENTS.values()]
    if len(ports) != len(set(ports)):
        issues.append("Duplicate port assignments detected")
    
    # Check template usage
    for name, config in TEMPLATE_DOMAIN_AGENTS.items():
        tier = config["tier"]
        template = config.get("template", "StandardizedAgentBase")
        
        if tier == 1 and template != "MasterOrchestratorTemplate":
            issues.append(f"Tier 1 agent '{name}' must use MasterOrchestratorTemplate")
        
        if tier == 2 and template not in ["StandardizedAgentBase"]:
            issues.append(f"Tier 2 agent '{name}' should use StandardizedAgentBase")
        
        if tier == 3 and template not in ["ADKServiceAgent", "StandardizedAgentBase"]:
            issues.append(f"Tier 3 agent '{name}' should use ADKServiceAgent or StandardizedAgentBase")
    
    return issues

def get_domain_summary() -> Dict[str, Any]:
    """Get a comprehensive summary of the domain architecture."""
    return {
        "domain_name": "Template Domain",  # Change this to your domain name
        "framework_version": "2.0",
        "agent_count": get_agent_count(),
        "port_range": get_port_range(),
        "validation_issues": validate_agent_registry(),
        "tier_architecture": {
            "tier_1": "Master Orchestration",
            "tier_2": "Domain Specialization", 
            "tier_3": "Intelligence Modules"
        },
        "templates_used": list(get_agent_count()["by_template"].keys())
    }


# Domain-specific customizations go here
# Example:
# 
# class YourDomainAgent(StandardizedAgentBase):
#     """Your domain-specific agent base class."""
#     
#     def __init__(self, agent_name: str, description: str, instructions: str, **kwargs):
#         super().__init__(
#             agent_name=agent_name,
#             description=description,
#             instructions=instructions,
#             quality_config={"domain": "YOUR_DOMAIN"},
#             **kwargs
#         )
#         # Add domain-specific initialization
#     
#     async def _execute_agent_logic(self, query: str, context_id: str, task_id: str):
#         """Domain-specific logic."""
#         # Implement your domain-specific processing
#         return {"content": f"Domain response for: {query}"}


if __name__ == "__main__":
    # Example usage and testing
    print("Framework V2.0 Agent Registry Template")
    print("="*50)
    
    # Show domain summary
    summary = get_domain_summary()
    print(f"Domain: {summary['domain_name']}")
    print(f"Framework Version: {summary['framework_version']}")
    print(f"Total Agents: {summary['agent_count']['total']}")
    
    print("\\nAgent Distribution:")
    for tier, count in summary['agent_count']['by_tier'].items():
        print(f"  {tier}: {count}")
    
    print("\\nTemplate Usage:")
    for template, count in summary['agent_count']['by_template'].items():
        print(f"  {template}: {count}")
    
    print(f"\\nPort Range: {summary['port_range']['min_port']}-{summary['port_range']['max_port']}")
    
    # Validation
    issues = summary['validation_issues']
    if issues:
        print("\\nValidation Issues:")
        for issue in issues:
            print(f"  ⚠️  {issue}")
    else:
        print("\\n✅ Registry is Framework V2.0 compliant!")
    
    print("\\nAvailable Agents:")
    for tier in [1, 2, 3]:
        agents = get_agents_by_tier(tier)
        if agents:
            print(f"\\n  Tier {tier}:")
            for name, config in agents.items():
                print(f"    • {name} (port {config['port']}) - {config['description']}")