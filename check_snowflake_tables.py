#!/usr/bin/env python3
"""Check actual tables in SNOWFLAKE database"""

import asyncio
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

async def check_snowflake_tables():
    """Check what tables exist in SNOWFLAKE database"""
    server_params = StdioServerParameters(
        command="python",
        args=["snowflake_mcp.py"],
        env={}
    )
    
    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                # Use SNOWFLAKE database
                await session.call_tool(
                    name="execute_query",
                    arguments={"query": "USE DATABASE SNOWFLAKE"}
                )
                
                logger.info("📊 SNOWFLAKE System Database Contents")
                logger.info("=" * 60)
                
                # Check current schema
                result = await session.call_tool(
                    name="execute_query",
                    arguments={"query": "SELECT CURRENT_DATABASE(), CURRENT_SCHEMA()"}
                )
                if hasattr(result, 'content') and len(result.content) > 0:
                    logger.info(f"\nCurrent context: {result.content[0].text}")
                
                # Show all schemas with tables
                logger.info("\n📁 Schemas with Tables:")
                logger.info("-" * 60)
                
                schemas_to_check = ['LOCAL', 'TELEMETRY', 'CORTEX', 'INFORMATION_SCHEMA']
                
                for schema in schemas_to_check:
                    logger.info(f"\n🔍 Schema: {schema}")
                    
                    # Set schema
                    await session.call_tool(
                        name="execute_query",
                        arguments={"query": f"USE SCHEMA {schema}"}
                    )
                    
                    # Show tables
                    result = await session.call_tool(
                        name="execute_query",
                        arguments={"query": "SHOW TABLES"}
                    )
                    
                    if hasattr(result, 'content') and len(result.content) > 0:
                        text = result.content[0].text
                        if "0 rows" in text:
                            logger.info("  No tables")
                        elif '[{' in text:
                            try:
                                # Parse tables
                                import json
                                tables_str = text.split('[{')[1].split('}]')[0] + '}]'
                                tables = eval(tables_str)
                                for table in tables:
                                    logger.info(f"  - {table['name']:<40} ({table.get('rows', 0)} rows)")
                            except:
                                logger.info(f"  Tables found: {text[:100]}...")
                
                # Check LOCAL schema tables specifically
                logger.info("\n📋 LOCAL Schema Table Details:")
                logger.info("-" * 60)
                
                await session.call_tool(
                    name="execute_query",
                    arguments={"query": "USE SCHEMA LOCAL"}
                )
                
                # Check AI_OBSERVABILITY_EVENTS
                logger.info("\n1. AI_OBSERVABILITY_EVENTS - AI/ML model usage tracking")
                result = await session.call_tool(
                    name="execute_query",
                    arguments={"query": "SELECT COUNT(*) as event_count FROM AI_OBSERVABILITY_EVENTS"}
                )
                if hasattr(result, 'content') and len(result.content) > 0:
                    logger.info(f"   {result.content[0].text}")
                
                # Check CORTEX_ANALYST_REQUESTS_RAW
                logger.info("\n2. CORTEX_ANALYST_REQUESTS_RAW - Cortex AI requests")
                result = await session.call_tool(
                    name="execute_query",
                    arguments={"query": "SELECT COUNT(*) as request_count FROM CORTEX_ANALYST_REQUESTS_RAW"}
                )
                if hasattr(result, 'content') and len(result.content) > 0:
                    logger.info(f"   {result.content[0].text}")
                
                # Show sample telemetry event
                logger.info("\n📊 Sample Telemetry Data:")
                logger.info("-" * 60)
                
                await session.call_tool(
                    name="execute_query",
                    arguments={"query": "USE SCHEMA TELEMETRY"}
                )
                
                result = await session.call_tool(
                    name="execute_query",
                    arguments={
                        "query": """
                        SELECT 
                            EVENT_TYPE,
                            EVENT_TIMESTAMP,
                            RESOURCE_ATTRIBUTES
                        FROM EVENTS 
                        LIMIT 5
                        """
                    }
                )
                if hasattr(result, 'content') and len(result.content) > 0:
                    text = result.content[0].text
                    if "0 rows" in text:
                        logger.info("No telemetry events recorded yet")
                    else:
                        logger.info("Telemetry events are being tracked")
                
                logger.info("\n💡 What We Can Do with SNOWFLAKE Database:")
                logger.info("-" * 60)
                logger.info("""
1. **Monitor AI/ML Usage** (AI_OBSERVABILITY_EVENTS)
   - Track Cortex AI model calls
   - Monitor AI feature usage
   - Analyze AI performance metrics

2. **Analyze Cortex Requests** (CORTEX_ANALYST_REQUESTS_RAW)
   - Review natural language queries
   - Track query patterns
   - Optimize query performance

3. **System Telemetry** (TELEMETRY.EVENTS)
   - Monitor system health
   - Track resource usage
   - Debug issues

4. **Data Quality Monitoring** (DATA_QUALITY_MONITORING_RESULTS_RAW)
   - Track data quality metrics
   - Monitor data freshness
   - Alert on anomalies

For Market Oracle:
- Track AI model usage for predictions
- Monitor Cortex queries for market analysis
- Analyze system performance for real-time data processing
                """)
                
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_snowflake_tables())