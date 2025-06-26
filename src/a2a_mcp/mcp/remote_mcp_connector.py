"""Remote MCP Server Connector for connecting to external MCP servers."""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.types import (
    CallToolRequest,
    ReadResourceResult,
    Tool,
    Resource,
    ServerCapabilities
)

logger = logging.getLogger(__name__)


@dataclass
class RemoteMCPServer:
    """Configuration for a remote MCP server."""
    name: str
    transport: str  # 'sse', 'stdio', or 'websocket'
    url: Optional[str] = None  # For SSE/WebSocket
    command: Optional[str] = None  # For stdio
    args: Optional[List[str]] = None  # For stdio
    env: Optional[Dict[str, str]] = None  # Environment variables
    description: Optional[str] = None
    
    def __post_init__(self):
        if self.transport == 'sse' and not self.url:
            raise ValueError("SSE transport requires a URL")
        if self.transport == 'stdio' and not self.command:
            raise ValueError("Stdio transport requires a command")


class RemoteMCPConnector:
    """Manages connections to multiple remote MCP servers."""
    
    def __init__(self):
        self.servers: Dict[str, RemoteMCPServer] = {}
        self.sessions: Dict[str, ClientSession] = {}
        self.tools_cache: Dict[str, List[Tool]] = {}
        self.resources_cache: Dict[str, List[Resource]] = {}
    
    def register_server(self, server: RemoteMCPServer):
        """Register a remote MCP server."""
        self.servers[server.name] = server
        logger.info(f"Registered remote MCP server: {server.name}")
    
    def register_servers_from_config(self, config: Dict[str, Any]):
        """Register multiple servers from a configuration dictionary."""
        for name, server_config in config.items():
            server = RemoteMCPServer(
                name=name,
                transport=server_config.get('transport', 'sse'),
                url=server_config.get('url'),
                command=server_config.get('command'),
                args=server_config.get('args'),
                env=server_config.get('env'),
                description=server_config.get('description')
            )
            self.register_server(server)
    
    @asynccontextmanager
    async def connect_server(self, server_name: str):
        """Connect to a specific remote MCP server."""
        if server_name not in self.servers:
            raise ValueError(f"Server '{server_name}' not registered")
        
        server = self.servers[server_name]
        
        if server.transport == 'sse':
            async with sse_client(server.url) as (read_stream, write_stream):
                async with ClientSession(
                    read_stream=read_stream,
                    write_stream=write_stream
                ) as session:
                    logger.info(f"Connected to SSE server: {server_name}")
                    await session.initialize()
                    self.sessions[server_name] = session
                    
                    # Cache available tools and resources
                    await self._cache_server_capabilities(server_name, session)
                    
                    yield session
        
        elif server.transport == 'stdio':
            stdio_params = StdioServerParameters(
                command=server.command,
                args=server.args or [],
                env=server.env or {}
            )
            async with stdio_client(stdio_params) as (read_stream, write_stream):
                async with ClientSession(
                    read_stream=read_stream,
                    write_stream=write_stream
                ) as session:
                    logger.info(f"Connected to stdio server: {server_name}")
                    await session.initialize()
                    self.sessions[server_name] = session
                    
                    # Cache available tools and resources
                    await self._cache_server_capabilities(server_name, session)
                    
                    yield session
        
        else:
            raise ValueError(f"Unsupported transport: {server.transport}")
        
        # Clean up after disconnect
        if server_name in self.sessions:
            del self.sessions[server_name]
        if server_name in self.tools_cache:
            del self.tools_cache[server_name]
        if server_name in self.resources_cache:
            del self.resources_cache[server_name]
    
    async def _cache_server_capabilities(self, server_name: str, session: ClientSession):
        """Cache the tools and resources available from a server."""
        try:
            # Get server capabilities
            result = await session.initialize()
            
            # Cache tools
            if hasattr(result, 'capabilities') and hasattr(result.capabilities, 'tools'):
                tools = result.capabilities.tools
                self.tools_cache[server_name] = tools if tools else []
                logger.info(f"Cached {len(self.tools_cache[server_name])} tools from {server_name}")
            
            # Cache resources
            if hasattr(result, 'capabilities') and hasattr(result.capabilities, 'resources'):
                resources = result.capabilities.resources
                self.resources_cache[server_name] = resources if resources else []
                logger.info(f"Cached {len(self.resources_cache[server_name])} resources from {server_name}")
                
        except Exception as e:
            logger.error(f"Error caching capabilities for {server_name}: {e}")
    
    async def call_remote_tool(
        self, 
        server_name: str, 
        tool_name: str, 
        arguments: Dict[str, Any]
    ) -> Any:
        """Call a tool on a specific remote server."""
        async with self.connect_server(server_name) as session:
            logger.info(f"Calling tool '{tool_name}' on server '{server_name}'")
            result = await session.call_tool(
                name=tool_name,
                arguments=arguments
            )
            return result
    
    async def read_remote_resource(
        self, 
        server_name: str, 
        resource_uri: str
    ) -> ReadResourceResult:
        """Read a resource from a specific remote server."""
        async with self.connect_server(server_name) as session:
            logger.info(f"Reading resource '{resource_uri}' from server '{server_name}'")
            result = await session.read_resource(resource_uri)
            return result
    
    def get_available_tools(self, server_name: Optional[str] = None) -> Dict[str, List[Tool]]:
        """Get available tools from one or all servers."""
        if server_name:
            return {server_name: self.tools_cache.get(server_name, [])}
        return self.tools_cache.copy()
    
    def get_available_resources(self, server_name: Optional[str] = None) -> Dict[str, List[Resource]]:
        """Get available resources from one or all servers."""
        if server_name:
            return {server_name: self.resources_cache.get(server_name, [])}
        return self.resources_cache.copy()
    
    async def discover_tool_across_servers(self, tool_name: str) -> List[str]:
        """Find which servers provide a specific tool."""
        servers_with_tool = []
        
        for server_name in self.servers:
            try:
                async with self.connect_server(server_name) as session:
                    tools = self.tools_cache.get(server_name, [])
                    if any(tool.name == tool_name for tool in tools):
                        servers_with_tool.append(server_name)
            except Exception as e:
                logger.error(f"Error checking server {server_name}: {e}")
        
        return servers_with_tool
    
    async def aggregate_tools_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """Aggregate tools from all servers organized by category/functionality."""
        categorized_tools = {}
        
        for server_name in self.servers:
            try:
                async with self.connect_server(server_name) as session:
                    tools = self.tools_cache.get(server_name, [])
                    
                    for tool in tools:
                        # Categorize based on tool name or description
                        category = self._categorize_tool(tool)
                        
                        if category not in categorized_tools:
                            categorized_tools[category] = []
                        
                        categorized_tools[category].append({
                            'server': server_name,
                            'tool': tool.model_dump() if hasattr(tool, 'model_dump') else tool
                        })
            except Exception as e:
                logger.error(f"Error aggregating from server {server_name}: {e}")
        
        return categorized_tools
    
    def _categorize_tool(self, tool: Tool) -> str:
        """Categorize a tool based on its name or description."""
        tool_name = tool.name.lower()
        
        # Simple categorization logic - can be enhanced
        if any(keyword in tool_name for keyword in ['search', 'find', 'query']):
            return 'search'
        elif any(keyword in tool_name for keyword in ['create', 'write', 'update', 'delete']):
            return 'data_modification'
        elif any(keyword in tool_name for keyword in ['read', 'get', 'fetch', 'retrieve']):
            return 'data_access'
        elif any(keyword in tool_name for keyword in ['analyze', 'process', 'compute']):
            return 'analysis'
        else:
            return 'other'


class RemoteMCPRegistry:
    """Registry for managing multiple remote MCP connectors."""
    
    def __init__(self):
        self.connector = RemoteMCPConnector()
        self._load_servers_from_config()
    
    def _load_servers_from_config(self):
        """Load remote MCP servers from configuration."""
        try:
            from a2a_mcp.mcp.config_loader import get_remote_mcp_servers, filter_enabled_servers
            
            # Load servers from .mcp.json
            servers = get_remote_mcp_servers()
            
            # Filter to only enabled servers
            enabled_servers = filter_enabled_servers(servers)
            
            if enabled_servers:
                logger.info(f"Loading {len(enabled_servers)} remote MCP servers from configuration")
                self.connector.register_servers_from_config(enabled_servers)
            else:
                logger.info("No enabled remote MCP servers found in configuration")
                
        except Exception as e:
            logger.error(f"Error loading servers from config: {e}")
            # Fall back to manual configuration if needed
            self._load_default_servers()
    
    def _load_default_servers(self):
        """Load default remote MCP servers configuration as fallback."""
        # Example configurations for testing
        default_servers = {
            "filesystem": {
                "transport": "stdio",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
                "description": "Filesystem MCP server for file access"
            }
        }
        
        try:
            self.connector.register_servers_from_config(default_servers)
        except Exception as e:
            logger.error(f"Error registering default servers: {e}")
    
    async def get_all_available_tools(self) -> Dict[str, Any]:
        """Get all available tools from all registered servers."""
        all_tools = {}
        
        for server_name in self.connector.servers:
            try:
                async with self.connector.connect_server(server_name) as session:
                    tools = self.connector.get_available_tools(server_name)
                    all_tools[server_name] = tools
            except Exception as e:
                logger.error(f"Error getting tools from {server_name}: {e}")
                all_tools[server_name] = {"error": str(e)}
        
        return all_tools
    
    async def execute_cross_server_workflow(
        self, 
        workflow: List[Dict[str, Any]]
    ) -> List[Any]:
        """Execute a workflow that spans multiple MCP servers."""
        results = []
        context = {}  # Shared context between steps
        
        for step in workflow:
            server_name = step.get('server')
            action = step.get('action')
            
            if action == 'tool':
                tool_name = step.get('tool_name')
                arguments = step.get('arguments', {})
                
                # Substitute context variables
                for key, value in arguments.items():
                    if isinstance(value, str) and value.startswith('{{') and value.endswith('}}'):
                        context_key = value[2:-2]
                        arguments[key] = context.get(context_key, value)
                
                result = await self.connector.call_remote_tool(
                    server_name, tool_name, arguments
                )
                
                # Store result in context
                if step.get('store_as'):
                    context[step['store_as']] = result
                
                results.append(result)
            
            elif action == 'resource':
                resource_uri = step.get('resource_uri')
                result = await self.connector.read_remote_resource(
                    server_name, resource_uri
                )
                
                # Store result in context
                if step.get('store_as'):
                    context[step['store_as']] = result
                
                results.append(result)
        
        return results


# Example usage
async def example_usage():
    """Example of using the remote MCP connector."""
    # Create registry
    registry = RemoteMCPRegistry()
    
    # Register a custom server
    custom_server = RemoteMCPServer(
        name="my_custom_mcp",
        transport="sse",
        url="http://localhost:8080/sse",
        description="My custom MCP server"
    )
    registry.connector.register_server(custom_server)
    
    # Get all available tools
    all_tools = await registry.get_all_available_tools()
    print("Available tools:", json.dumps(all_tools, indent=2))
    
    # Execute a cross-server workflow
    workflow = [
        {
            "server": "github",
            "action": "tool",
            "tool_name": "list_repositories",
            "arguments": {"organization": "anthropics"},
            "store_as": "repos"
        },
        {
            "server": "slack",
            "action": "tool",
            "tool_name": "post_message",
            "arguments": {
                "channel": "#general",
                "message": "Found {{repos}} repositories"
            }
        }
    ]
    
    results = await registry.execute_cross_server_workflow(workflow)
    print("Workflow results:", results)


if __name__ == "__main__":
    asyncio.run(example_usage())