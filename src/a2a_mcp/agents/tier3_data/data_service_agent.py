# ABOUTME: Database Query Service - Tier 3 Service Agent for data tool operations  
# ABOUTME: Uses ADKServiceAgent for streamlined MCP tool integration and database queries

from a2a_mcp.common.adk_service_agent import ADKServiceAgent
from a2a_mcp.common.quality_framework import QualityDomain


class DataServiceAgent(ADKServiceAgent):
    """
    Database Query Service - Service agent for data tool operations.
    
    Framework V2.0 Tier 3 agent using ADKServiceAgent template for efficient
    MCP tool integration and database operations.
    """
    
    def __init__(self):
        # Data-specific service instructions
        instructions = f"""
You are a Database Query Service, specialized in executing data service operations and tool coordination.

Your responsibilities:
- Execute specific data tasks efficiently
- Coordinate with MCP tools for data access and processing
- Perform database queries and data operations
- Handle API integrations and service calls
- Process and format results appropriately
- Report status and handle errors gracefully

For each task:
1. Understand the specific data operation required
2. Use appropriate MCP tools and services
3. Execute the operation efficiently
4. Validate results and handle errors
5. Return formatted results with clear status

Focus on reliable execution and clear communication of results.
"""
        
        super().__init__(
            agent_name="Database Query Service",
            description=f"Service agent for data tool operations and data processing",
            instructions=instructions,
            temperature=0.1,  # Low temperature for consistent service execution
            a2a_enabled=True,
            quality_domain=QualityDomain.SERVICE
        )


# Port assignment for data service: 10300
if __name__ == "__main__":
    import asyncio
    
    async def main():
        agent = DataServiceAgent()
        
        # Example usage
        query = "Execute data data query and format results"
        context_id = "example_session"
        task_id = "example_task"
        
        async for result in agent.stream(query, context_id, task_id):
            print(f"Result: {result}")
    
    asyncio.run(main())
