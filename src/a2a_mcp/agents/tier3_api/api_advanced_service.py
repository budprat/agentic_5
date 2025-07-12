# ABOUTME: Advanced API Service - Tier 3 Advanced Service Agent for api operations
# ABOUTME: Uses StandardizedAgentBase for full framework capabilities with advanced service logic

from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.common.quality_framework import QualityDomain
from typing import Dict, Any, AsyncIterable


class ApiServiceAgent(StandardizedAgentBase):
    """
    Advanced API Service - Advanced service agent for api operations.
    
    Framework V2.0 Tier 3 agent using StandardizedAgentBase for complex service logic
    with full framework features including quality validation and advanced error handling.
    """
    
    def __init__(self):
        # Api-specific service instructions
        instructions = f"""
You are an advanced Advanced API Service, providing sophisticated api service operations.

Your capabilities include:
- Complex api service orchestration
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
            agent_name="Advanced API Service",
            description=f"Advanced service agent for complex api operations",
            instructions=instructions,
            quality_config={"domain": QualityDomain.SERVICE},
            mcp_tools_enabled=True,
            a2a_enabled=True
        )
    
    async def _execute_agent_logic(
        self, query: str, context_id: str, task_id: str
    ) -> AsyncIterable[Dict[str, Any]]:
        """Execute advanced api service logic with full framework capabilities."""
        
        # Progress indicator
        yield {
            'is_task_complete': False,
            'require_user_input': False,
            'content': f'{self.agent_name}: Initializing api service operation...'
        }
        
        # Initialize Google ADK agent if needed
        if not self.agent:
            await self.init_agent()
        
        # Enhanced service query with validation requirements
        service_query = f"""
        Api Service Request: {query}
        
        Execute this api service operation with:
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
                final_response = {
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': response,
                    'agent_name': self.agent_name,
                    'service_type': 'advanced',
                    'domain': 'api'
                }
                
                yield final_response
                break
            else:
                # Intermediate progress with enhanced detail
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': f'{self.agent_name}: Processing api service operation...'
                }


# Port assignment for api advanced service: 10301
if __name__ == "__main__":
    import asyncio
    
    async def main():
        agent = ApiServiceAgent()
        
        # Example usage
        query = "Execute complex api workflow with quality validation"
        context_id = "example_session"
        task_id = "example_task"
        
        async for result in agent.stream(query, context_id, task_id):
            print(f"Result: {result}")
    
    asyncio.run(main())
