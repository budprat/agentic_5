# ABOUTME: Marketing Specialist - Tier 2 Domain Specialist for marketing expertise
# ABOUTME: Uses StandardizedAgentBase for comprehensive domain analysis and knowledge synthesis

from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.common.quality_framework import QualityDomain
from typing import Dict, Any, AsyncIterable


class MarketingSpecialist(StandardizedAgentBase):
    """
    Marketing Specialist - Domain specialist for marketing expertise.
    
    Framework V2.0 Tier 2 agent using StandardizedAgentBase with full framework
    capabilities including MCP tools, A2A communication, and quality validation.
    """
    
    def __init__(self):
        # Marketing-specific instructions
        instructions = f"""
You are a Marketing Specialist, a specialized expert in marketing with deep knowledge and analytical capabilities.

Your expertise includes:
- Marketing analysis and assessment
- Industry best practices and standards
- Strategic recommendations and planning
- Risk assessment and mitigation
- Performance optimization
- Quality assurance and validation

For each request:
1. Analyze the marketing context thoroughly
2. Apply your specialized knowledge and experience  
3. Use available MCP tools for data gathering and analysis
4. Provide expert recommendations with clear rationale
5. Include implementation guidance and success metrics

Maintain high professional standards and provide actionable insights.
"""
        
        super().__init__(
            agent_name="Marketing Specialist",
            description=f"Expert marketing specialist providing deep domain knowledge and analysis",
            instructions=instructions,
            quality_config={"domain": QualityDomain.BUSINESS},  # Adjust based on domain
            mcp_tools_enabled=True,
            a2a_enabled=True
        )
    
    async def _execute_agent_logic(
        self, query: str, context_id: str, task_id: str
    ) -> AsyncIterable[Dict[str, Any]]:
        """Execute marketing specialist logic with domain-specific processing."""
        
        # Progress indicator
        yield {
            'is_task_complete': False,
            'require_user_input': False,
            'content': f'{self.agent_name}: Analyzing marketing requirements...'
        }
        
        # Initialize Google ADK agent if needed
        if not self.agent:
            await self.init_agent()
        
        # Use inherited agent for marketing analysis
        from a2a_mcp.common.agent_runner import AgentRunner
        runner = AgentRunner()
        
        # Enhanced query with marketing context
        enhanced_query = f"""
        Marketing Analysis Request: {query}
        
        Please provide expert marketing analysis including:
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
                
                yield {
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': response,
                    'agent_name': self.agent_name,
                    'domain': 'marketing'
                }
                break
            else:
                # Intermediate progress  
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': f'{self.agent_name}: Processing marketing analysis...'
                }


# Port assignment for marketing specialist: 10250
if __name__ == "__main__":
    import asyncio
    
    async def main():
        agent = MarketingSpecialist()
        
        # Example usage
        query = "Analyze current marketing trends and provide strategic recommendations"
        context_id = "example_session"
        task_id = "example_task"
        
        async for result in agent.stream(query, context_id, task_id):
            print(f"Result: {result}")
    
    asyncio.run(main())
