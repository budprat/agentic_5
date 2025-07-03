#!/usr/bin/env python3
"""Check what databases exist in Snowflake"""

import json
import asyncio
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

async def check_snowflake_databases():
    """Check databases in Snowflake"""
    server_params = StdioServerParameters(
        command="python",
        args=["snowflake_mcp.py"],
        env={}
    )
    
    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                # Query 1: Show all databases
                logger.info("📊 Databases in Snowflake:")
                logger.info("-" * 50)
                
                result = await session.call_tool(
                    name="execute_query",
                    arguments={
                        "query": "SHOW DATABASES"
                    }
                )
                
                # Parse and display results
                if hasattr(result, 'content') and len(result.content) > 0:
                    text = result.content[0].text
                    # Extract the actual data from the result
                    lines = text.split('\n')
                    for line in lines:
                        if line.strip():
                            logger.info(line)
                
                # Query 2: Current database context
                logger.info("\n📍 Current Database Context:")
                logger.info("-" * 50)
                
                result2 = await session.call_tool(
                    name="execute_query",
                    arguments={
                        "query": "SELECT CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_WAREHOUSE()"
                    }
                )
                
                if hasattr(result2, 'content') and len(result2.content) > 0:
                    text = result2.content[0].text
                    lines = text.split('\n')
                    for line in lines:
                        if line.strip():
                            logger.info(line)
                
                # Query 3: Show tables in current database
                logger.info("\n📋 Tables in Current Database:")
                logger.info("-" * 50)
                
                result3 = await session.call_tool(
                    name="execute_query",
                    arguments={
                        "query": "SHOW TABLES"
                    }
                )
                
                if hasattr(result3, 'content') and len(result3.content) > 0:
                    text = result3.content[0].text
                    lines = text.split('\n')
                    for line in lines:
                        if line.strip():
                            logger.info(line)
                            
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_snowflake_databases())