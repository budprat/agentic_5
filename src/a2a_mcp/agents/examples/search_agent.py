# ABOUTME: Example search agent demonstrating web search capabilities
# ABOUTME: Shows how to build a simple agent extending StandardizedAgentBase

"""
Search Agent Example

A simple agent that demonstrates web search capabilities using MCP tools.
This shows the basic pattern for creating tool-based agents.
"""

from typing import Dict, Any, AsyncIterable
from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase


class SearchAgent(StandardizedAgentBase):
    """
    Example agent that performs web searches using MCP tools.
    
    Demonstrates:
    - Basic agent setup with StandardizedAgentBase
    - Using MCP tools for web operations
    - Simple query processing
    """
    
    def __init__(self):
        super().__init__(
            agent_name="search_agent",
            description="Web search and information retrieval agent",
            instructions="""You are a search agent that helps find information on the web.
            Use available search tools to find relevant information based on user queries.
            Present results in a clear, organized manner.""",
            quality_config={
                "domain": "GENERIC",
                "min_confidence_score": 0.7
            }
        )
    
    async def _execute_agent_logic(self, prompt: str) -> AsyncIterable[Dict[str, Any]]:
        """Execute search logic"""
        # Parse the query
        query = prompt.strip()
        
        if not query:
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": "Please provide a search query."
            }
            return
        
        # Use search tool if available
        tools = await self.agent.get_tools()
        search_tools = [t for t in tools if 'search' in t.name.lower()]
        
        if search_tools:
            # Execute search
            result = await self.agent.run_tool(
                search_tools[0].name,
                query=query,
                limit=5
            )
            
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": f"Search results for '{query}':\n\n{result}"
            }
        else:
            # Fallback without search tool
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": f"I would search for '{query}' but no search tools are available."
            }
    
    def get_agent_temperature(self) -> Optional[float]:
        """Low temperature for factual search results"""
        return 0.3
    
    def get_response_mime_type(self) -> Optional[str]:
        return "text/plain"