#!/usr/bin/env python3
"""
A2A MCP Framework V2.0 - Agent Boilerplate Generator

Generates boilerplate code for new agents following the established tier-based template rules:
- Tier 1: MasterOrchestratorTemplate 
- Tier 2: GenericDomainAgent
- Tier 3: ADKServiceAgent or StandardizedAgentBase (user choice)

Usage:
    python scripts/generate_agent.py --tier 1 --name "Healthcare Orchestrator" --domain healthcare
    python scripts/generate_agent.py --tier 2 --name "Financial Analyst" --domain finance
    python scripts/generate_agent.py --tier 3 --name "Database Service" --template adk
"""

import argparse
import json
import os
from pathlib import Path
from typing import Dict, Any


class AgentBoilerplateGenerator:
    """Framework V2.0 compliant agent boilerplate generator."""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.templates_path = self.base_path / "templates"
        self.agents_path = self.base_path / "src" / "a2a_mcp" / "agents"
        self.cards_path = self.base_path / "agent_cards"
        
    def generate_tier1_orchestrator(self, name: str, domain: str, port: int) -> Dict[str, str]:
        """Generate Tier 1 Master Orchestrator using MasterOrchestratorTemplate."""
        class_name = f"{domain.title()}MasterOrchestrator"
        filename = f"{domain.lower()}_master_orchestrator.py"
        
        code = f'''# ABOUTME: {name} - Tier 1 Master Orchestrator for {domain} domain
# ABOUTME: Uses MasterOrchestratorTemplate for sophisticated multi-agent coordination

from a2a_mcp.common.master_orchestrator_template import MasterOrchestratorTemplate
from a2a_mcp.common.quality_framework import QualityDomain


class {class_name}(MasterOrchestratorTemplate):
    """
    {name} - Master Orchestrator for {domain} domain.
    
    Framework V2.0 Tier 1 agent using MasterOrchestratorTemplate for sophisticated
    orchestration patterns with LangGraph integration and parallel workflow management.
    """
    
    def __init__(self):
        # Define domain specialists for {domain}
        domain_specialists = {{
            "analysis_specialist": "{domain.title()} analysis and strategic assessment",
            "execution_specialist": "{domain.title()} implementation and operations",
            "optimization_specialist": "{domain.title()} optimization and improvement"
        }}
        
        # {domain.title()}-specific planning instructions
        planning_instructions = f"""
You are the {name} Task Planner. Analyze {domain} requests and decompose them into coordinated tasks.

Domain Specialists Available:
- analysis_specialist: {domain.title()} analysis and strategic assessment
- execution_specialist: {domain.title()} implementation and operations  
- optimization_specialist: {domain.title()} optimization and improvement

For each {domain} request:
1. Analyze scope and identify relevant specialists
2. Create specific, actionable tasks for each domain specialist
3. Define coordination strategy (parallel/sequential based on dependencies)
4. Set quality requirements per domain
5. Identify optimization opportunities and synergies

Focus on {domain}-specific best practices and industry standards.
"""
        
        # {domain.title()}-specific synthesis prompt
        synthesis_prompt = f"""
You are the {name} Synthesis Agent. Synthesize {domain} intelligence into actionable insights.

Your {domain} capabilities:
- Cross-specialist intelligence analysis
- {domain.title()} strategy optimization
- Implementation planning with {domain} best practices
- Risk assessment and mitigation strategies

Provide structured {domain} recommendations with clear action plans and success metrics.
"""
        
        super().__init__(
            domain_name="{name}",
            domain_description="{domain} strategy and operations coordination",
            domain_specialists=domain_specialists,
            quality_domain=QualityDomain.BUSINESS,  # Adjust based on domain
            planning_instructions=planning_instructions,
            synthesis_prompt=synthesis_prompt,
            enable_parallel=True
        )


# Port assignment for {domain} domain: {port}
if __name__ == "__main__":
    import asyncio
    from a2a_mcp.common.agent_runner import AgentRunner
    
    async def main():
        agent = {class_name}()
        runner = AgentRunner()
        
        # Example usage
        query = "Develop a comprehensive {domain} strategy"
        context_id = "example_session"
        task_id = "example_task"
        
        async for result in agent.stream(query, context_id, task_id):
            print(f"Result: {{result}}")
    
    asyncio.run(main())
'''
        
        agent_card = {
            "name": name,
            "type": "orchestrator", 
            "tier": 1,
            "port": port,
            "description": f"Master orchestrator for {domain} domain coordination and strategy",
            "version": "2.0.0",
            "capabilities": [
                "strategic_planning",
                "task_decomposition", 
                "agent_coordination",
                f"{domain}_expertise"
            ],
            "metadata": {
                "author": "Framework Team",
                "domain": domain,
                "tier": 1,
                "template": "MasterOrchestratorTemplate"
            }
        }
        
        return {
            "code": code,
            "filename": filename,
            "agent_card": agent_card,
            "card_filename": f"{domain.lower()}_orchestrator.json"
        }
    
    def generate_tier2_specialist(self, name: str, domain: str, port: int) -> Dict[str, str]:
        """Generate Tier 2 Domain Specialist using GenericDomainAgent."""
        class_name = f"{domain.title()}Specialist"
        filename = f"{domain.lower()}_specialist.py"
        
        code = f'''# ABOUTME: {name} - Tier 2 Domain Specialist for {domain} expertise
# ABOUTME: Uses GenericDomainAgent for comprehensive domain analysis and knowledge synthesis

from a2a_mcp.common.standardized_agent_base import GenericDomainAgent
from a2a_mcp.common.quality_framework import QualityDomain
from typing import Dict, Any, AsyncIterable


class {class_name}(GenericDomainAgent):
    """
    {name} - Domain specialist for {domain} expertise.
    
    Framework V2.0 Tier 2 agent using GenericDomainAgent with full framework
    capabilities including MCP tools, A2A communication, and quality validation.
    """
    
    def __init__(self):
        # {domain.title()}-specific instructions
        instructions = f"""
You are a {name}, a specialized expert in {domain} with deep knowledge and analytical capabilities.

Your expertise includes:
- {domain.title()} analysis and assessment
- Industry best practices and standards
- Strategic recommendations and planning
- Risk assessment and mitigation
- Performance optimization
- Quality assurance and validation

For each request:
1. Analyze the {domain} context thoroughly
2. Apply your specialized knowledge and experience  
3. Use available MCP tools for data gathering and analysis
4. Provide expert recommendations with clear rationale
5. Include implementation guidance and success metrics

Maintain high professional standards and provide actionable insights.
"""
        
        super().__init__(
            agent_name="{name}",
            description=f"Expert {domain} specialist providing deep domain knowledge and analysis",
            instructions=instructions,
            quality_config={{"domain": QualityDomain.BUSINESS}},  # Adjust based on domain
            mcp_tools_enabled=True,
            a2a_enabled=True
        )
    
    async def _execute_agent_logic(
        self, query: str, context_id: str, task_id: str
    ) -> AsyncIterable[Dict[str, Any]]:
        """Execute {domain} specialist logic with domain-specific processing."""
        
        # Progress indicator
        yield {{
            'is_task_complete': False,
            'require_user_input': False,
            'content': f'{{self.agent_name}}: Analyzing {domain} requirements...'
        }}
        
        # Initialize Google ADK agent if needed
        if not self.agent:
            await self.init_agent()
        
        # Use inherited agent for {domain} analysis
        from a2a_mcp.common.agent_runner import AgentRunner
        runner = AgentRunner()
        
        # Enhanced query with {domain} context
        enhanced_query = f"""
        {domain.title()} Analysis Request: {{query}}
        
        Please provide expert {domain} analysis including:
        1. Current situation assessment
        2. Key considerations and factors
        3. Recommended approach or solution
        4. Implementation steps
        5. Success metrics and validation criteria
        6. Risk factors and mitigation strategies
        """
        
        # Stream response from ADK agent
        async for chunk in runner.run_stream(self.agent, enhanced_query, context_id):
            if isinstance(chunk, dict) and chunk.get('type') == 'final_result':
                # Format final response
                response = self.format_response(chunk['response'])
                
                yield {{
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': response,
                    'agent_name': self.agent_name,
                    'domain': '{domain}'
                }}
                break
            else:
                # Intermediate progress  
                yield {{
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': f'{{self.agent_name}}: Processing {domain} analysis...'
                }}


# Port assignment for {domain} specialist: {port}
if __name__ == "__main__":
    import asyncio
    
    async def main():
        agent = {class_name}()
        
        # Example usage
        query = "Analyze current {domain} trends and provide strategic recommendations"
        context_id = "example_session"
        task_id = "example_task"
        
        async for result in agent.stream(query, context_id, task_id):
            print(f"Result: {{result}}")
    
    asyncio.run(main())
'''
        
        agent_card = {
            "name": name,
            "type": "specialist",
            "tier": 2, 
            "port": port,
            "description": f"Domain specialist providing expert {domain} knowledge and analysis",
            "version": "2.0.0",
            "capabilities": [
                f"{domain}_expertise",
                "domain_analysis",
                "strategic_planning",
                "risk_assessment"
            ],
            "metadata": {
                "author": "Framework Team",
                "domain": domain,
                "tier": 2,
                "template": "GenericDomainAgent"
            }
        }
        
        return {
            "code": code,
            "filename": filename,
            "agent_card": agent_card,
            "card_filename": f"{domain.lower()}_specialist.json"
        }
    
    def generate_tier3_service(self, name: str, domain: str, port: int, template: str) -> Dict[str, str]:
        """Generate Tier 3 Service Agent using ADKServiceAgent or StandardizedAgentBase."""
        
        if template == "adk":
            return self._generate_adk_service_agent(name, domain, port)
        else:
            return self._generate_standardized_service_agent(name, domain, port)
    
    def _generate_adk_service_agent(self, name: str, domain: str, port: int) -> Dict[str, str]:
        """Generate Tier 3 service using ADKServiceAgent template."""
        class_name = f"{domain.title()}ServiceAgent"
        filename = f"{domain.lower()}_service_agent.py"
        
        code = f'''# ABOUTME: {name} - Tier 3 Service Agent for {domain} tool operations  
# ABOUTME: Uses ADKServiceAgent for streamlined MCP tool integration and database queries

from a2a_mcp.common.adk_service_agent import ADKServiceAgent
from a2a_mcp.common.quality_framework import QualityDomain


class {class_name}(ADKServiceAgent):
    """
    {name} - Service agent for {domain} tool operations.
    
    Framework V2.0 Tier 3 agent using ADKServiceAgent template for efficient
    MCP tool integration and database operations.
    """
    
    def __init__(self):
        # {domain.title()}-specific service instructions
        instructions = f"""
You are a {name}, specialized in executing {domain} service operations and tool coordination.

Your responsibilities:
- Execute specific {domain} tasks efficiently
- Coordinate with MCP tools for data access and processing
- Perform database queries and data operations
- Handle API integrations and service calls
- Process and format results appropriately
- Report status and handle errors gracefully

For each task:
1. Understand the specific {domain} operation required
2. Use appropriate MCP tools and services
3. Execute the operation efficiently
4. Validate results and handle errors
5. Return formatted results with clear status

Focus on reliable execution and clear communication of results.
"""
        
        super().__init__(
            agent_name="{name}",
            description=f"Service agent for {domain} tool operations and data processing",
            instructions=instructions,
            temperature=0.1,  # Low temperature for consistent service execution
            a2a_enabled=True,
            quality_domain=QualityDomain.SERVICE
        )


# Port assignment for {domain} service: {port}
if __name__ == "__main__":
    import asyncio
    
    async def main():
        agent = {class_name}()
        
        # Example usage
        query = "Execute {domain} data query and format results"
        context_id = "example_session"
        task_id = "example_task"
        
        async for result in agent.stream(query, context_id, task_id):
            print(f"Result: {{result}}")
    
    asyncio.run(main())
'''
        
        agent_card = {
            "name": name,
            "type": "service",
            "tier": 3,
            "port": port,
            "description": f"Service agent for {domain} tool operations and data processing",
            "version": "2.0.0",
            "capabilities": [
                "tool_operation",
                "data_processing",
                f"{domain}_services",
                "api_integration"
            ],
            "metadata": {
                "author": "Framework Team", 
                "domain": domain,
                "tier": 3,
                "template": "ADKServiceAgent"
            }
        }
        
        return {
            "code": code,
            "filename": filename,
            "agent_card": agent_card,
            "card_filename": f"{domain.lower()}_service.json"
        }
    
    def _generate_standardized_service_agent(self, name: str, domain: str, port: int) -> Dict[str, str]:
        """Generate Tier 3 service using StandardizedAgentBase template."""
        class_name = f"{domain.title()}ServiceAgent"
        filename = f"{domain.lower()}_advanced_service.py"
        
        code = f'''# ABOUTME: {name} - Tier 3 Advanced Service Agent for {domain} operations
# ABOUTME: Uses StandardizedAgentBase for full framework capabilities with advanced service logic

from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.common.quality_framework import QualityDomain
from typing import Dict, Any, AsyncIterable


class {class_name}(StandardizedAgentBase):
    """
    {name} - Advanced service agent for {domain} operations.
    
    Framework V2.0 Tier 3 agent using StandardizedAgentBase for complex service logic
    with full framework features including quality validation and advanced error handling.
    """
    
    def __init__(self):
        # {domain.title()}-specific service instructions
        instructions = f"""
You are an advanced {name}, providing sophisticated {domain} service operations.

Your capabilities include:
- Complex {domain} service orchestration
- Advanced data processing and analysis
- Multi-step workflow execution
- Quality validation and assurance
- Error handling and recovery
- Performance optimization

For each service request:
1. Analyze the complexity and requirements
2. Plan the optimal execution approach
3. Execute with quality validation at each step
4. Handle errors gracefully with fallback strategies
5. Provide comprehensive results and status reporting

Maintain high service quality and reliability standards.
"""
        
        super().__init__(
            agent_name="{name}",
            description=f"Advanced service agent for complex {domain} operations",
            instructions=instructions,
            quality_config={{"domain": QualityDomain.SERVICE}},
            mcp_tools_enabled=True,
            a2a_enabled=True
        )
    
    async def _execute_agent_logic(
        self, query: str, context_id: str, task_id: str
    ) -> AsyncIterable[Dict[str, Any]]:
        """Execute advanced {domain} service logic with full framework capabilities."""
        
        # Progress indicator
        yield {{
            'is_task_complete': False,
            'require_user_input': False,
            'content': f'{{self.agent_name}}: Initializing {domain} service operation...'
        }}
        
        # Initialize Google ADK agent if needed
        if not self.agent:
            await self.init_agent()
        
        # Enhanced service query with validation requirements
        service_query = f"""
        {domain.title()} Service Request: {{query}}
        
        Execute this {domain} service operation with:
        1. Comprehensive analysis of requirements
        2. Optimal execution strategy
        3. Quality validation at each step
        4. Error handling and recovery procedures
        5. Complete results with status reporting
        6. Performance metrics and optimization insights
        """
        
        # Use inherited agent for advanced service execution
        from a2a_mcp.common.agent_runner import AgentRunner
        runner = AgentRunner()
        
        # Stream response with enhanced processing
        async for chunk in runner.run_stream(self.agent, service_query, context_id):
            if isinstance(chunk, dict) and chunk.get('type') == 'final_result':
                # Format and validate final response
                response = self.format_response(chunk['response'])
                
                # Apply framework V2.0 quality validation
                final_response = {{
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': response,
                    'agent_name': self.agent_name,
                    'service_type': 'advanced',
                    'domain': '{domain}'
                }}
                
                yield final_response
                break
            else:
                # Intermediate progress with enhanced detail
                yield {{
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': f'{{self.agent_name}}: Processing {domain} service operation...'
                }}


# Port assignment for {domain} advanced service: {port}
if __name__ == "__main__":
    import asyncio
    
    async def main():
        agent = {class_name}()
        
        # Example usage
        query = "Execute complex {domain} workflow with quality validation"
        context_id = "example_session"
        task_id = "example_task"
        
        async for result in agent.stream(query, context_id, task_id):
            print(f"Result: {{result}}")
    
    asyncio.run(main())
'''
        
        agent_card = {
            "name": name,
            "type": "service",
            "tier": 3,
            "port": port,
            "description": f"Advanced service agent for complex {domain} operations",
            "version": "2.0.0", 
            "capabilities": [
                "advanced_processing",
                "quality_validation",
                f"{domain}_services",
                "workflow_orchestration"
            ],
            "metadata": {
                "author": "Framework Team",
                "domain": domain,
                "tier": 3,
                "template": "StandardizedAgentBase"
            }
        }
        
        return {
            "code": code,
            "filename": filename,
            "agent_card": agent_card,
            "card_filename": f"{domain.lower()}_advanced_service.json"
        }
    
    def write_files(self, generated: Dict[str, str], tier: int, domain: str):
        """Write generated code and agent card to appropriate directories."""
        
        # Ensure directories exist
        tier_dir = self.agents_path / f"tier{tier}_{domain}"
        tier_dir.mkdir(parents=True, exist_ok=True)
        
        card_tier_dir = self.cards_path / f"tier{tier}"
        card_tier_dir.mkdir(parents=True, exist_ok=True)
        
        # Write agent code
        code_path = tier_dir / generated["filename"]
        with open(code_path, 'w') as f:
            f.write(generated["code"])
        
        # Write agent card
        card_path = card_tier_dir / generated["card_filename"]
        with open(card_path, 'w') as f:
            json.dump(generated["agent_card"], f, indent=2)
        
        print(f"✅ Generated agent files:")
        print(f"   Code: {code_path}")
        print(f"   Card: {card_path}")
        
        # Provide usage instructions
        print(f"\n📝 Usage Instructions:")
        print(f"   1. Review and customize the generated code")
        print(f"   2. Update agent card configuration as needed")
        print(f"   3. Add to your agent registry")
        print(f"   4. Test with: python {code_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate A2A MCP Framework V2.0 agent boilerplate",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate Tier 1 Master Orchestrator
  python scripts/generate_agent.py --tier 1 --name "Healthcare Orchestrator" --domain healthcare --port 10100

  # Generate Tier 2 Domain Specialist  
  python scripts/generate_agent.py --tier 2 --name "Financial Analyst" --domain finance --port 10200

  # Generate Tier 3 Service Agent (ADK template)
  python scripts/generate_agent.py --tier 3 --name "Database Service" --domain data --port 10300 --template adk

  # Generate Tier 3 Service Agent (StandardizedAgentBase template)  
  python scripts/generate_agent.py --tier 3 --name "Advanced API Service" --domain api --port 10301 --template standard
        """
    )
    
    parser.add_argument('--tier', type=int, choices=[1, 2, 3], required=True,
                        help='Agent tier (1=Orchestrator, 2=Specialist, 3=Service)')
    parser.add_argument('--name', type=str, required=True,
                        help='Human-readable agent name')
    parser.add_argument('--domain', type=str, required=True,
                        help='Domain/category for the agent (e.g., healthcare, finance)')
    parser.add_argument('--port', type=int, required=True,
                        help='Port number for the agent')
    parser.add_argument('--template', type=str, choices=['adk', 'standard'], default='adk',
                        help='Tier 3 template choice: adk=ADKServiceAgent, standard=StandardizedAgentBase')
    
    args = parser.parse_args()
    
    generator = AgentBoilerplateGenerator()
    
    print(f"🚀 Generating Framework V2.0 Tier {args.tier} agent...")
    print(f"   Name: {args.name}")
    print(f"   Domain: {args.domain}")
    print(f"   Port: {args.port}")
    
    if args.tier == 1:
        generated = generator.generate_tier1_orchestrator(args.name, args.domain, args.port)
        print(f"   Template: MasterOrchestratorTemplate")
    elif args.tier == 2:
        generated = generator.generate_tier2_specialist(args.name, args.domain, args.port)
        print(f"   Template: GenericDomainAgent")
    elif args.tier == 3:
        template_name = "ADKServiceAgent" if args.template == "adk" else "StandardizedAgentBase"
        generated = generator.generate_tier3_service(args.name, args.domain, args.port, args.template)
        print(f"   Template: {template_name}")
    
    generator.write_files(generated, args.tier, args.domain)
    
    print(f"\n🎉 Framework V2.0 agent boilerplate generated successfully!")


if __name__ == "__main__":
    main()