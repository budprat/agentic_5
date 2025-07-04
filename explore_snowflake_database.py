#!/usr/bin/env python3
"""Explore the SNOWFLAKE system database"""

import asyncio
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

async def explore_snowflake_database():
    """Explore SNOWFLAKE system database"""
    server_params = StdioServerParameters(
        command="python",
        args=["snowflake_mcp.py"],
        env={}
    )
    
    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                logger.info("🔍 Exploring SNOWFLAKE System Database")
                logger.info("=" * 70)
                
                # Switch to SNOWFLAKE database
                await session.call_tool(
                    name="execute_query",
                    arguments={"query": "USE DATABASE SNOWFLAKE"}
                )
                
                # Show all schemas
                logger.info("\n📁 Schemas in SNOWFLAKE database:")
                logger.info("-" * 70)
                result = await session.call_tool(
                    name="execute_query",
                    arguments={"query": "SHOW SCHEMAS"}
                )
                
                if hasattr(result, 'content') and len(result.content) > 0:
                    text = result.content[0].text
                    lines = text.split('\n')
                    for line in lines:
                        if '[{' in line:
                            try:
                                schemas = eval(line.strip())
                                for schema in schemas:
                                    logger.info(f"• {schema['name']:<30} - {schema.get('comment', 'No description')}")
                            except:
                                pass
                
                # Explore key schemas
                logger.info("\n📊 Key System Schemas:")
                logger.info("-" * 70)
                
                # 1. ACCOUNT_USAGE Schema
                logger.info("\n1️⃣ ACCOUNT_USAGE Schema - Historical account activity")
                await session.call_tool(
                    name="execute_query",
                    arguments={"query": "USE SCHEMA ACCOUNT_USAGE"}
                )
                
                # Show some key tables
                result = await session.call_tool(
                    name="execute_query",
                    arguments={"query": "SHOW TABLES LIKE '%HISTORY' LIMIT 10"}
                )
                if hasattr(result, 'content') and len(result.content) > 0:
                    logger.info("   Key history tables:")
                    text = result.content[0].text
                    if '[{' in text:
                        try:
                            tables = eval(text.split('[{')[1].split('}]')[0] + '}]')
                            for table in tables[:5]:
                                logger.info(f"   - {table['name']}")
                        except:
                            pass
                
                # 2. INFORMATION_SCHEMA
                logger.info("\n2️⃣ INFORMATION_SCHEMA - Database metadata")
                result = await session.call_tool(
                    name="execute_query",
                    arguments={"query": "SELECT COUNT(*) as view_count FROM SNOWFLAKE.INFORMATION_SCHEMA.VIEWS"}
                )
                if hasattr(result, 'content') and len(result.content) > 0:
                    logger.info("   Contains metadata views for database objects")
                
                # 3. Query examples
                logger.info("\n💡 Useful Queries with SNOWFLAKE Database:")
                logger.info("-" * 70)
                
                # Query history
                logger.info("\n📝 Recent Query History:")
                result = await session.call_tool(
                    name="execute_query",
                    arguments={
                        "query": """
                        SELECT 
                            QUERY_TEXT,
                            DATABASE_NAME,
                            EXECUTION_TIME,
                            ROWS_PRODUCED
                        FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
                        WHERE USER_NAME = CURRENT_USER()
                            AND START_TIME > DATEADD(hour, -1, CURRENT_TIMESTAMP())
                        ORDER BY START_TIME DESC
                        LIMIT 5
                        """
                    }
                )
                if hasattr(result, 'content') and len(result.content) > 0:
                    logger.info("   (Shows last 5 queries from past hour)")
                
                # Storage usage
                logger.info("\n💾 Storage Usage by Database:")
                result = await session.call_tool(
                    name="execute_query",
                    arguments={
                        "query": """
                        SELECT 
                            DATABASE_NAME,
                            ROUND(SUM(ACTIVE_BYTES)/(1024*1024*1024), 2) as GB_USED
                        FROM SNOWFLAKE.ACCOUNT_USAGE.TABLE_STORAGE_METRICS
                        WHERE DELETED IS NULL
                        GROUP BY DATABASE_NAME
                        ORDER BY GB_USED DESC
                        """
                    }
                )
                if hasattr(result, 'content') and len(result.content) > 0:
                    text = result.content[0].text
                    if '[{' in text:
                        try:
                            storage = eval(text.split('[{')[1].split('}]')[0] + '}]')
                            for db in storage:
                                logger.info(f"   - {db['DATABASE_NAME']}: {db['GB_USED']} GB")
                        except:
                            pass
                
                # Credit usage
                logger.info("\n💰 Compute Credit Usage (Last 7 days):")
                result = await session.call_tool(
                    name="execute_query",
                    arguments={
                        "query": """
                        SELECT 
                            DATE(START_TIME) as USAGE_DATE,
                            WAREHOUSE_NAME,
                            SUM(CREDITS_USED) as CREDITS
                        FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
                        WHERE START_TIME > DATEADD(day, -7, CURRENT_TIMESTAMP())
                        GROUP BY 1, 2
                        ORDER BY 1 DESC, 3 DESC
                        LIMIT 10
                        """
                    }
                )
                if hasattr(result, 'content') and len(result.content) > 0:
                    logger.info("   (Shows compute usage by warehouse)")
                
                logger.info("\n🎯 Use Cases for SNOWFLAKE Database:")
                logger.info("-" * 70)
                logger.info("""
1. **Performance Monitoring**
   - Track slow queries and optimize them
   - Monitor warehouse credit consumption
   - Analyze query patterns

2. **Security Auditing**
   - Review login history
   - Track data access patterns
   - Monitor user activity

3. **Cost Management**
   - Track storage costs by database
   - Monitor compute credit usage
   - Identify expensive queries

4. **Data Governance**
   - Track table modifications
   - Monitor data sharing activity
   - Audit user permissions

5. **System Health**
   - Check failed queries
   - Monitor system performance
   - Track error patterns

Example queries for Market Oracle:
- Find most expensive queries for optimization
- Track data ingestion patterns
- Monitor which tables are accessed most
- Analyze query performance over time
                """)
                
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(explore_snowflake_database())