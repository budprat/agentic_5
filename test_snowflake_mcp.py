#!/usr/bin/env python3
"""Test Snowflake MCP server by sending MCP protocol messages"""

import json
import asyncio
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_snowflake_mcp():
    """Test the Snowflake MCP server"""
    # Configure the server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["snowflake_mcp.py"],
        env={}
    )
    
    try:
        # Start the MCP client
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                logger.info("Connected to Snowflake MCP server")
                
                # Initialize the session
                await session.initialize()
                logger.info("Session initialized")
                
                # List available tools
                tools = await session.list_tools()
                logger.info(f"Available tools: {len(tools.tools) if tools.tools else 0}")
                for tool in (tools.tools or []):
                    logger.info(f"  - {tool.name}: {tool.description}")
                
                # Test the execute_query tool if available
                if tools.tools and any(tool.name == "execute_query" for tool in tools.tools):
                    logger.info("\nTesting execute_query tool...")
                    
                    # Simple test query
                    result = await session.call_tool(
                        name="execute_query",
                        arguments={
                            "query": "SELECT CURRENT_VERSION() AS version, CURRENT_TIMESTAMP() AS timestamp"
                        }
                    )
                    
                    if hasattr(result, 'content') and len(result.content) > 0:
                        logger.info(f"Query result: {result.content[0].text if hasattr(result.content[0], 'text') else result.content}")
                    
                    # Test listing databases
                    result2 = await session.call_tool(
                        name="execute_query",
                        arguments={
                            "query": "SHOW DATABASES LIMIT 5"
                        }
                    )
                    
                    if hasattr(result2, 'content') and len(result2.content) > 0:
                        logger.info(f"Databases result: {result2.content[0].text if hasattr(result2.content[0], 'text') else result2.content}")
                else:
                    logger.warning("execute_query tool not found")
                
                logger.info("\nSnowflake MCP server test completed successfully!")
                
    except Exception as e:
        logger.error(f"Error testing Snowflake MCP: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_snowflake_mcp())