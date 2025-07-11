# ABOUTME: Service agent for example domain - demonstrates tool-focused tier 3 agent pattern
# ABOUTME: Uses MCP tools for web scraping and data extraction with service-level reliability

"""
Service Agent - Example Domain
Tier 3 agent focused on web data extraction using MCP tools.
Demonstrates the tool-focused agent pattern for service-level operations.
"""

from typing import Dict, Any, List, Optional, AsyncIterable
from datetime import datetime
import json
import asyncio

from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.common.a2a_protocol import A2AProtocolClient
import logging

logger = logging.getLogger(__name__)


class ServiceAgent(StandardizedAgentBase):
    """
    Service-level agent for web data extraction and processing.
    
    This tier 3 agent demonstrates:
    - Tool-focused operations using MCP tools
    - Service-level error handling and retries
    - Simple data extraction and formatting
    - Basic validation and response formatting
    """
    
    def __init__(self, agent_id: str = "service_agent"):
        """Initialize the service agent with MCP client configuration."""
        # Define service agent instructions
        instructions = """
        You are a Service Agent specialized in web data extraction and processing.
        Your capabilities include:
        1. Scraping content from URLs
        2. Searching the web for information
        3. Extracting structured data from web pages
        
        Focus on reliability and proper error handling.
        Present extracted data in a clean, structured format.
        """
        
        super().__init__(
            agent_name=agent_id,
            description="Service Agent - Web scraping and data extraction specialist",
            instructions=instructions,
            quality_config={
                "min_confidence_score": 0.6,
                "require_sources": False,
                "max_response_length": 20000
            },
            mcp_tools_enabled=True
        )
        
        # Service-level configuration
        self.max_retries = 2
        self.timeout_seconds = 30
        self.operation_cache = {}
    
    def _parse_query(self, query: str) -> tuple[str, Dict[str, Any]]:
        """Parse query to extract operation and parameters."""
        query_lower = query.lower()
        params = {}
        
        # Check for URL patterns
        import re
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, query)
        
        if urls and 'scrape' in query_lower:
            return 'scrape_url', {'url': urls[0]}
        elif urls and 'extract' in query_lower:
            return 'extract_data', {'urls': urls}
        elif 'search' in query_lower or 'find' in query_lower:
            # Remove command words to get search query
            search_query = re.sub(r'\b(search|find|web)\b', '', query, flags=re.IGNORECASE).strip()
            return 'search_web', {'query': search_query}
        else:
            return 'search_web', {'query': query}
        
    async def _execute_agent_logic(
        self, query: str, context_id: str, task_id: str
    ) -> AsyncIterable[Dict[str, Any]]:
        """
        Process web data extraction requests.
        """
        # Parse query to determine operation
        operation, params = self._parse_query(query)
        
        # Yield initial status
        yield {
            "is_task_complete": False,
            "require_user_input": False,
            "content": f"Processing {operation} request..."
        }
        
        try:
            # Initialize agent if needed
            if not self.agent:
                await self.init_agent()
            
            # Execute operation
            if operation == "scrape_url":
                result = await self._scrape_url(params.get('url', ''))
            elif operation == "search_web":
                result = await self._search_web(params.get('query', query))
            elif operation == "extract_data":
                result = await self._extract_structured_data(params.get('urls', []))
            else:
                # Default to web search
                result = await self._search_web(query)
            
            # Cache result
            cache_key = f"{operation}_{task_id}"
            self.operation_cache[cache_key] = result
            
            # Yield final result
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": result
            }
            
        except Exception as e:
            logger.error(f"Service agent error: {str(e)}")
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": {
                    "error": f"Operation failed: {str(e)}",
                    "operation": operation,
                    "query": query
                }
            }
    
    async def _scrape_url(self, url: str) -> Dict[str, Any]:
        """Scrape content from a URL using MCP tools."""
        if not url:
            return {"error": "URL is required"}
        
        # Try with firecrawl first (more powerful)
        for attempt in range(self.max_retries):
            try:
                # Find firecrawl scrape tool
                scrape_tool = next((t for t in self.tools if t.name == 'mcp__firecrawl__firecrawl_scrape'), None)
                if scrape_tool:
                    result = await self.agent.run_tool(
                        scrape_tool,
                        {
                            "url": url,
                            "formats": ["markdown"],
                            "onlyMainContent": True
                        }
                    )
                    
                    if result and result.get("data"):
                        return {
                            "url": url,
                            "content": result.get("data", {}).get("markdown", ""),
                            "title": result.get("data", {}).get("metadata", {}).get("title", ""),
                            "scraped_at": datetime.utcnow().isoformat(),
                            "tool_used": "firecrawl",
                            "attempt": attempt + 1
                        }
                    
            except Exception as e:
                logger.warning(f"Firecrawl attempt {attempt + 1} failed: {str(e)}")
        
        # Fallback to brightdata
        try:
            brightdata_tool = next((t for t in self.tools if t.name == 'mcp__brightdata__scrape_as_markdown'), None)
            if brightdata_tool:
                result = await self.agent.run_tool(
                    brightdata_tool,
                    {"url": url}
                )
                
                return {
                    "url": url,
                    "content": result.get("data", "") if result else "",
                    "scraped_at": datetime.utcnow().isoformat(),
                    "tool_used": "brightdata",
                    "fallback": True
                }
            
        except Exception as e:
            logger.error(f"Brightdata fallback failed: {str(e)}")
        
        return {
            "error": f"Failed to scrape URL after {self.max_retries} attempts",
            "url": url
        }
    
    async def _search_web(self, query: str) -> Dict[str, Any]:
        """Search the web and return results."""
        if not query:
            return {"error": "Search query is required"}
        
        limit = 5
        
        try:
            # Use firecrawl search for better results
            search_tool = next((t for t in self.tools if t.name == 'mcp__firecrawl__firecrawl_search'), None)
            if search_tool:
                result = await self.agent.run_tool(
                    search_tool,
                    {
                        "query": query,
                        "limit": limit,
                        "scrapeOptions": {
                            "formats": ["markdown"],
                            "onlyMainContent": True
                        }
                    }
                )
            else:
                result = None
            
            # Format search results
            search_results = []
            if result and result.get("data"):
                for item in result.get("data", []):
                    search_results.append({
                        "url": item.get("url"),
                        "title": item.get("title"),
                        "description": item.get("description"),
                        "content_preview": (item.get("markdown", "")[:500] + "...") if item.get("markdown") else ""
                    })
            
            return {
                "query": query,
                "results": search_results,
                "total_results": len(search_results),
                "tool_used": "firecrawl_search",
                "limit": limit
            }
            
        except Exception as e:
            # Fallback to brightdata search
            try:
                brightdata_search = next((t for t in self.tools if t.name == 'mcp__brightdata__search_engine'), None)
                if brightdata_search:
                    result = await self.agent.run_tool(
                        brightdata_search,
                        {"query": query}
                    )
                    
                    return {
                        "query": query,
                        "results": result.get("data", [])[:limit] if result else [],
                        "tool_used": "brightdata_search",
                        "fallback": True
                    }
            except Exception as fallback_error:
                logger.error(f"Brightdata search failed: {str(fallback_error)}")
            
            return {
                "error": f"Search failed",
                "query": query
            }
    
    async def _extract_structured_data(self, urls: List[str]) -> Dict[str, Any]:
        """Extract structured data from URLs."""
        if not urls:
            return {"error": "URLs are required for extraction"}
        
        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "key_points": {"type": "array", "items": {"type": "string"}}
            }
        }
        
        prompt = "Extract the main information from this content"
        
        try:
            extract_tool = next((t for t in self.tools if t.name == 'mcp__firecrawl__firecrawl_extract'), None)
            if extract_tool:
                result = await self.agent.run_tool(
                    extract_tool,
                    {
                        "urls": urls[:5],  # Limit to 5 URLs for service tier
                        "prompt": prompt,
                        "schema": schema
                    }
                )
                
                return {
                    "extracted_data": result.get("data", []) if result else [],
                    "urls_processed": len(urls[:5]),
                    "tool_used": "firecrawl_extract",
                    "schema_used": True
                }
            else:
                return {
                    "error": "Extract tool not available",
                    "urls": urls
                }
            
        except Exception as e:
            return {
                "error": f"Data extraction failed: {str(e)}",
                "urls": urls
            }
    
    def get_agent_temperature(self) -> float:
        """Use low temperature for consistent extraction."""
        return 0.2
    
    def get_response_mime_type(self) -> str:
        """Return structured JSON for extracted data."""
        return "application/json"
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return service agent capabilities."""
        return {
            "agent_type": "service_agent",
            "tier": 3,
            "capabilities": [
                "web_scraping",
                "data_extraction",
                "content_parsing",
                "basic_search"
            ],
            "mcp_tools_used": [
                "firecrawl_scrape",
                "firecrawl_search",
                "firecrawl_extract",
                "brightdata_scrape_as_markdown",
                "brightdata_search_engine"
            ],
            "max_retries": self.max_retries,
            "timeout_seconds": self.timeout_seconds
        }


# Example usage:
# This service agent handles basic web scraping and data extraction tasks.
# It can be used standalone or as part of a larger agent system.
#
# Example queries:
# - "Scrape the content from https://example.com"
# - "Search the web for Python tutorial"
# - "Extract data from https://example.com/article"
#
# The agent automatically uses MCP tools (Firecrawl, Brightdata) with fallback
# mechanisms to ensure reliable data extraction.