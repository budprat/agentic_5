# ABOUTME: Generic MCP client for Framework V2.0 multi-agent systems
# ABOUTME: Provides configurable MCP client with support for any domain tools and resources

import asyncio
import json
import os
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional, List

import click

from fastmcp.utilities.logging import get_logger
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client
from mcp.types import CallToolResult, ReadResourceResult

logger = get_logger(__name__)


class GenericMCPClient:
    """
    Generic MCP client for Framework V2.0.
    
    Provides a configurable interface for connecting to MCP servers and calling
    tools/resources. Domains can extend this class or use it directly.
    """
    
    def __init__(self, server_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the generic MCP client.
        
        Args:
            server_config: Optional server configuration override
        """
        self.server_config = server_config or {
            'host': 'localhost',
            'port': 10100,
            'transport': 'stdio',
            'command': 'uv',
            'args': ['run', 'a2a-mcp'],
            'env_vars': ['GOOGLE_API_KEY']
        }
        
        # Build environment with required variables
        self.env = {}
        for var in self.server_config.get('env_vars', []):
            value = os.getenv(var)
            if value:
                self.env[var] = value
    
    @asynccontextmanager
    async def init_session(self, host: str = None, port: int = None, transport: str = None):
        """
        Initializes and manages an MCP ClientSession based on the specified transport.

        This asynchronous context manager establishes a connection to an MCP server
        using either Server-Sent Events (SSE) or Standard I/O (STDIO) transport.
        It handles the setup and teardown of the connection and yields an active
        `ClientSession` object ready for communication.

        Args:
            host: The hostname or IP address of the MCP server (used for SSE).
            port: The port number of the MCP server (used for SSE).
            transport: The communication transport to use ('sse' or 'stdio').

        Yields:
            ClientSession: An initialized and ready-to-use MCP client session.

        Raises:
            ValueError: If an unsupported transport type is provided.
            Exception: Other potential exceptions during client initialization.
        """
        # Use provided values or fall back to server config
        host = host or self.server_config['host']
        port = port or self.server_config['port']
        transport = transport or self.server_config['transport']
        
        if transport == 'sse':
            url = f'http://{host}:{port}/sse'
            async with sse_client(url) as (read_stream, write_stream):
                async with ClientSession(
                    read_stream=read_stream, write_stream=write_stream
                ) as session:
                    logger.debug('SSE ClientSession created, initializing...')
                    await session.initialize()
                    logger.info('SSE ClientSession initialized successfully.')
                    yield session
                    
        elif transport == 'stdio':
            # Validate required environment variables
            missing_vars = []
            for var in self.server_config.get('env_vars', []):
                if not os.getenv(var):
                    missing_vars.append(var)
            
            if missing_vars:
                error_msg = f'Required environment variables not set: {", ".join(missing_vars)}'
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            stdio_params = StdioServerParameters(
                command=self.server_config.get('command', 'uv'),
                args=self.server_config.get('args', ['run', 'a2a-mcp']),
                env=self.env,
            )
            async with stdio_client(stdio_params) as (read_stream, write_stream):
                async with ClientSession(
                    read_stream=read_stream,
                    write_stream=write_stream,
                ) as session:
                    logger.debug('STDIO ClientSession created, initializing...')
                    await session.initialize()
                    logger.info('STDIO ClientSession initialized successfully.')
                    yield session
        else:
            logger.error(f'Unsupported transport type: {transport}')
            raise ValueError(
                f"Unsupported transport type: {transport}. Must be 'sse' or 'stdio'."
            )

    async def call_tool(self, session: ClientSession, tool_name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """
        Generic tool calling method.
        
        Args:
            session: The active ClientSession.
            tool_name: Name of the tool to call.
            arguments: Arguments to pass to the tool.
            
        Returns:
            The result of the tool call.
        """
        logger.info(f"Calling '{tool_name}' tool with arguments: {arguments}")
        return await session.call_tool(name=tool_name, arguments=arguments)

    async def read_resource(self, session: ClientSession, resource_uri: str) -> ReadResourceResult:
        """
        Generic resource reading method.
        
        Args:
            session: The active ClientSession.
            resource_uri: The URI of the resource to read.
            
        Returns:
            The result of the resource read operation.
        """
        logger.info(f'Reading resource: {resource_uri}')
        return await session.read_resource(resource_uri)

    async def list_tools(self, session: ClientSession) -> List[Dict[str, Any]]:
        """
        List available tools from the MCP server.
        
        Args:
            session: The active ClientSession.
            
        Returns:
            List of available tools with their schemas.
        """
        logger.info('Listing available tools from MCP server')
        try:
            tools_result = await session.list_tools()
            return [tool.model_dump() for tool in tools_result.tools]
        except Exception as e:
            logger.error(f'Failed to list tools: {e}')
            return []

    async def list_resources(self, session: ClientSession) -> List[Dict[str, Any]]:
        """
        List available resources from the MCP server.
        
        Args:
            session: The active ClientSession.
            
        Returns:
            List of available resources.
        """
        logger.info('Listing available resources from MCP server')
        try:
            resources_result = await session.list_resources()
            return [resource.model_dump() for resource in resources_result.resources]
        except Exception as e:
            logger.error(f'Failed to list resources: {e}')
            return []


# Legacy function wrappers for backward compatibility
async def init_session(host, port, transport):
    """Legacy function wrapper for backward compatibility."""
    client = GenericMCPClient()
    async with client.init_session(host, port, transport) as session:
        yield session


# Domain-specific tool functions (examples that domains can customize)
async def find_agent(session: ClientSession, query: str) -> CallToolResult:
    """
    Framework V2.0 agent discovery tool.
    
    Args:
        session: The active ClientSession.
        query: The natural language query to find agents.
        
    Returns:
        The result of the tool call.
    """
    logger.info(f"Calling 'find_agent' tool with query: '{query[:50]}...'")
    return await session.call_tool(
        name='find_agent',
        arguments={'query': query}
    )


async def query_database(session: ClientSession, query: str, database: str = "default") -> CallToolResult:
    """
    Generic database query tool.
    
    Args:
        session: The active ClientSession.
        query: SQL query to execute.
        database: Database name/identifier.
        
    Returns:
        The result of the tool call.
    """
    logger.info(f"Calling 'query_database' tool with query: '{query[:50]}...'")
    return await session.call_tool(
        name='query_database',
        arguments={'query': query, 'database': database}
    )


async def get_agent_cards(session: ClientSession, filter_criteria: Dict[str, Any] = None) -> ReadResourceResult:
    """
    Get agent cards resource with optional filtering.
    
    Args:
        session: The active ClientSession.
        filter_criteria: Optional criteria to filter agent cards.
        
    Returns:
        The result of the resource read operation.
    """
    resource_uri = 'resource://agent_cards/list'
    if filter_criteria:
        # Convert filter criteria to query parameters
        params = '&'.join([f'{k}={v}' for k, v in filter_criteria.items()])
        resource_uri += f'?{params}'
    
    logger.info(f'Reading agent cards resource: {resource_uri}')
    return await session.read_resource(resource_uri)


# Main function for testing and domain customization
async def main(host: str = 'localhost', port: int = 10100, transport: str = 'stdio', 
               tool_name: str = None, tool_args: Dict[str, Any] = None,
               resource_uri: str = None, list_capabilities: bool = False):
    """
    Main asynchronous function to connect to the MCP server and execute commands.

    This function demonstrates how to use the GenericMCPClient and can be
    customized by domains for their specific needs.

    Args:
        host: Server hostname.
        port: Server port.
        transport: Connection transport ('sse' or 'stdio').
        tool_name: Optional tool name to call.
        tool_args: Optional arguments for the tool.
        resource_uri: Optional resource URI to read.
        list_capabilities: Whether to list server capabilities.
    """
    logger.info('Starting Generic MCP Client for Framework V2.0')
    
    client = GenericMCPClient({
        'host': host,
        'port': port,
        'transport': transport,
        'env_vars': ['GOOGLE_API_KEY']  # Domains can customize this
    })
    
    async with client.init_session() as session:
        
        # List server capabilities if requested
        if list_capabilities:
            logger.info("=== MCP Server Capabilities ===")
            
            tools = await client.list_tools(session)
            logger.info(f"Available Tools ({len(tools)}):")
            for tool in tools:
                logger.info(f"  - {tool.get('name', 'unnamed')}: {tool.get('description', 'no description')}")
            
            resources = await client.list_resources(session)
            logger.info(f"Available Resources ({len(resources)}):")
            for resource in resources:
                logger.info(f"  - {resource.get('uri', 'unnamed')}: {resource.get('description', 'no description')}")
        
        # Call specific tool if requested
        if tool_name and tool_args:
            try:
                result = await client.call_tool(session, tool_name, tool_args)
                if hasattr(result, 'content') and result.content:
                    if hasattr(result.content[0], 'text'):
                        try:
                            data = json.loads(result.content[0].text)
                            logger.info("Tool Result:")
                            logger.info(json.dumps(data, indent=2))
                        except json.JSONDecodeError:
                            logger.info(f"Tool Result (raw): {result.content[0].text}")
                    else:
                        logger.info(f"Tool Result: {result.content}")
                else:
                    logger.info(f"Tool Result: {result}")
            except Exception as e:
                logger.error(f"Tool call failed: {e}")
        
        # Read specific resource if requested
        if resource_uri:
            try:
                result = await client.read_resource(session, resource_uri)
                if hasattr(result, 'contents') and result.contents:
                    try:
                        data = json.loads(result.contents[0].text)
                        logger.info("Resource Content:")
                        logger.info(json.dumps(data, indent=2))
                    except json.JSONDecodeError:
                        logger.info(f"Resource Content (raw): {result.contents[0].text}")
                else:
                    logger.info(f"Resource Result: {result}")
            except Exception as e:
                logger.error(f"Resource read failed: {e}")


# Enhanced CLI for Framework V2.0
@click.command()
@click.option('--host', default='localhost', help='MCP server hostname')
@click.option('--port', default=10100, help='MCP server port')
@click.option('--transport', default='stdio', type=click.Choice(['sse', 'stdio']), help='MCP transport method')
@click.option('--tool', help='Tool name to call')
@click.option('--tool-args', help='Tool arguments as JSON string')
@click.option('--resource', help='Resource URI to read')
@click.option('--list-capabilities', is_flag=True, help='List server tools and resources')
@click.option('--find-agent', help='Find agent using natural language query')
@click.option('--query-db', help='Execute database query')
def cli(host, port, transport, tool, tool_args, resource, list_capabilities, find_agent, query_db):
    """
    Generic MCP client for Framework V2.0 multi-agent systems.
    
    Examples:
        # List server capabilities
        python client.py --list-capabilities
        
        # Find an agent
        python client.py --find-agent "I need a finance specialist"
        
        # Call custom tool
        python client.py --tool my_tool --tool-args '{"param1": "value1"}'
        
        # Read resource
        python client.py --resource "resource://agent_cards/list"
    """
    
    # Parse tool arguments if provided
    parsed_tool_args = {}
    if tool_args:
        try:
            parsed_tool_args = json.loads(tool_args)
        except json.JSONDecodeError:
            click.echo(f"Error: Invalid JSON in tool-args: {tool_args}")
            return
    
    # Handle convenience options
    if find_agent:
        tool = 'find_agent'
        parsed_tool_args = {'query': find_agent}
    
    if query_db:
        tool = 'query_database'
        parsed_tool_args = {'query': query_db}
    
    # Run the main function
    asyncio.run(main(
        host=host, 
        port=port, 
        transport=transport,
        tool_name=tool,
        tool_args=parsed_tool_args if parsed_tool_args else None,
        resource_uri=resource,
        list_capabilities=list_capabilities
    ))


if __name__ == '__main__':
    cli()