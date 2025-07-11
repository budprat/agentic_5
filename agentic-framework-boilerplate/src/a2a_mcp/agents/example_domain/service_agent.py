# ABOUTME: Service agent for example domain - demonstrates tool-focused tier 3 agent pattern
# ABOUTME: Uses MCP tools for web scraping and data extraction with service-level reliability

"""
Service Agent - Example Domain
Tier 3 agent focused on web data extraction using MCP tools.
Demonstrates the tool-focused agent pattern for service-level operations.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from ...core.agent_interface import Agent, Message, AgentResponse
from ...core.mcp_client import MCPClient
from ...utils.logging import get_logger

logger = get_logger(__name__)


class ServiceAgent(Agent):
    """
    Service-level agent for web data extraction and processing.
    
    This tier 3 agent demonstrates:
    - Tool-focused operations using MCP clients
    - Service-level error handling and retries
    - Simple data extraction and formatting
    - Basic validation and response formatting
    """
    
    def __init__(self, agent_id: str = "service_agent"):
        """Initialize the service agent with MCP client configuration."""
        super().__init__(
            agent_id=agent_id,
            tier=3,
            quality_domain="service",
            capabilities=[
                "web_scraping",
                "data_extraction",
                "content_parsing",
                "basic_search"
            ]
        )
        
        # Initialize MCP clients for web operations
        self.mcp_clients = {
            "firecrawl": MCPClient("firecrawl"),
            "brightdata": MCPClient("brightdata")
        }
        
        # Service-level configuration
        self.max_retries = 2
        self.timeout_seconds = 30
        
    async def process(self, message: Message) -> AgentResponse:
        """
        Process incoming messages for web data extraction tasks.
        
        Supports operations:
        - scrape_url: Extract content from a single URL
        - search_web: Search and extract results
        - extract_data: Extract structured data from URLs
        """
        try:
            operation = message.metadata.get("operation", "scrape_url")
            
            if operation == "scrape_url":
                return await self._scrape_url(message)
            elif operation == "search_web":
                return await self._search_web(message)
            elif operation == "extract_data":
                return await self._extract_structured_data(message)
            else:
                return self._create_error_response(
                    f"Unknown operation: {operation}",
                    message
                )
                
        except Exception as e:
            logger.error(f"Service agent error: {str(e)}")
            return self._create_error_response(str(e), message)
    
    async def _scrape_url(self, message: Message) -> AgentResponse:
        """Scrape content from a URL using MCP tools."""
        url = message.metadata.get("url")
        if not url:
            return self._create_error_response("URL is required", message)
        
        # Try with firecrawl first (more powerful)
        for attempt in range(self.max_retries):
            try:
                result = await self.mcp_clients["firecrawl"].call_tool(
                    "firecrawl_scrape",
                    {
                        "url": url,
                        "formats": ["markdown"],
                        "onlyMainContent": True
                    }
                )
                
                if result.get("success"):
                    return AgentResponse(
                        agent_id=self.agent_id,
                        status="success",
                        data={
                            "url": url,
                            "content": result.get("data", {}).get("markdown", ""),
                            "title": result.get("data", {}).get("metadata", {}).get("title", ""),
                            "scraped_at": datetime.utcnow().isoformat()
                        },
                        metadata={
                            "tool_used": "firecrawl",
                            "attempt": attempt + 1
                        }
                    )
                    
            except Exception as e:
                logger.warning(f"Firecrawl attempt {attempt + 1} failed: {str(e)}")
        
        # Fallback to brightdata
        try:
            result = await self.mcp_clients["brightdata"].call_tool(
                "scrape_as_markdown",
                {"url": url}
            )
            
            return AgentResponse(
                agent_id=self.agent_id,
                status="success",
                data={
                    "url": url,
                    "content": result.get("data", ""),
                    "scraped_at": datetime.utcnow().isoformat()
                },
                metadata={
                    "tool_used": "brightdata",
                    "fallback": True
                }
            )
            
        except Exception as e:
            return self._create_error_response(
                f"Failed to scrape URL after {self.max_retries} attempts: {str(e)}",
                message
            )
    
    async def _search_web(self, message: Message) -> AgentResponse:
        """Search the web and return results."""
        query = message.content or message.metadata.get("query")
        if not query:
            return self._create_error_response("Search query is required", message)
        
        limit = message.metadata.get("limit", 5)
        
        try:
            # Use firecrawl search for better results
            result = await self.mcp_clients["firecrawl"].call_tool(
                "firecrawl_search",
                {
                    "query": query,
                    "limit": limit,
                    "scrapeOptions": {
                        "formats": ["markdown"],
                        "onlyMainContent": True
                    }
                }
            )
            
            # Format search results
            search_results = []
            for item in result.get("data", []):
                search_results.append({
                    "url": item.get("url"),
                    "title": item.get("title"),
                    "description": item.get("description"),
                    "content_preview": item.get("markdown", "")[:500] + "..."
                })
            
            return AgentResponse(
                agent_id=self.agent_id,
                status="success",
                data={
                    "query": query,
                    "results": search_results,
                    "total_results": len(search_results)
                },
                metadata={
                    "tool_used": "firecrawl_search",
                    "limit": limit
                }
            )
            
        except Exception as e:
            # Fallback to brightdata search
            try:
                result = await self.mcp_clients["brightdata"].call_tool(
                    "search_engine",
                    {"query": query}
                )
                
                return AgentResponse(
                    agent_id=self.agent_id,
                    status="success",
                    data={
                        "query": query,
                        "results": result.get("data", [])[:limit]
                    },
                    metadata={
                        "tool_used": "brightdata_search",
                        "fallback": True
                    }
                )
            except Exception as fallback_error:
                return self._create_error_response(
                    f"Search failed: {str(fallback_error)}",
                    message
                )
    
    async def _extract_structured_data(self, message: Message) -> AgentResponse:
        """Extract structured data from URLs."""
        urls = message.metadata.get("urls", [])
        if not urls:
            return self._create_error_response("URLs are required for extraction", message)
        
        schema = message.metadata.get("schema", {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "key_points": {"type": "array", "items": {"type": "string"}}
            }
        })
        
        prompt = message.metadata.get(
            "prompt",
            "Extract the main information from this content"
        )
        
        try:
            result = await self.mcp_clients["firecrawl"].call_tool(
                "firecrawl_extract",
                {
                    "urls": urls[:5],  # Limit to 5 URLs for service tier
                    "prompt": prompt,
                    "schema": schema
                }
            )
            
            return AgentResponse(
                agent_id=self.agent_id,
                status="success",
                data={
                    "extracted_data": result.get("data", []),
                    "urls_processed": len(urls[:5])
                },
                metadata={
                    "tool_used": "firecrawl_extract",
                    "schema_used": True
                }
            )
            
        except Exception as e:
            return self._create_error_response(
                f"Data extraction failed: {str(e)}",
                message
            )
    
    def _create_error_response(self, error_message: str, original_message: Message) -> AgentResponse:
        """Create a standardized error response."""
        return AgentResponse(
            agent_id=self.agent_id,
            status="error",
            error=error_message,
            metadata={
                "original_operation": original_message.metadata.get("operation"),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    async def validate_tools(self) -> Dict[str, bool]:
        """Validate that required MCP tools are available."""
        tool_status = {}
        
        for client_name, client in self.mcp_clients.items():
            try:
                # Check if client can list tools
                tools = await client.list_tools()
                tool_status[client_name] = len(tools) > 0
            except Exception as e:
                logger.error(f"Failed to validate {client_name}: {str(e)}")
                tool_status[client_name] = False
        
        return tool_status
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "agent_id": self.agent_id,
            "tier": self.tier,
            "quality_domain": self.quality_domain,
            "capabilities": self.capabilities,
            "mcp_clients": list(self.mcp_clients.keys()),
            "max_retries": self.max_retries,
            "timeout_seconds": self.timeout_seconds
        }