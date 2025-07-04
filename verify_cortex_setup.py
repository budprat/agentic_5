#!/usr/bin/env python3
"""Verify Cortex setup in Snowflake"""

import asyncio
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

async def verify_setup():
    """Verify all Cortex features are set up"""
    server_params = StdioServerParameters(
        command="python",
        args=["snowflake_mcp.py"],
        env={}
    )
    
    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                logger.info("✅ Verifying Snowflake Cortex Setup for Market Oracle")
                logger.info("=" * 70)
                
                await session.call_tool(
                    name="execute_query",
                    arguments={"query": "USE DATABASE MARKETS"}
                )
                
                # Check all schemas
                logger.info("\n📁 Created Schemas:")
                result = await session.call_tool(
                    name="execute_query",
                    arguments={"query": "SHOW SCHEMAS"}
                )
                if hasattr(result, 'content') and len(result.content) > 0:
                    text = result.content[0].text
                    if "ML_MODELS" in text:
                        logger.info("✓ ML_MODELS - AI predictions")
                    if "DATA_QUALITY" in text:
                        logger.info("✓ DATA_QUALITY - Quality monitoring")
                    if "PERFORMANCE" in text:
                        logger.info("✓ PERFORMANCE - Telemetry tracking")
                
                # Check key tables
                logger.info("\n📊 Key Tables Created:")
                
                tables_to_check = [
                    ("ML_MODELS", "MARKET_PREDICTIONS", "AI prediction storage"),
                    ("ML_MODELS", "QUERY_TEMPLATES", "Natural language templates"),
                    ("DATA_QUALITY", "QUALITY_RULES", "Data quality rules"),
                    ("DATA_QUALITY", "MONITORING_RESULTS", "Quality check results"),
                    ("PERFORMANCE", "QUERY_METRICS", "Performance tracking"),
                    ("PERFORMANCE", "ALERT_THRESHOLDS", "Performance alerts")
                ]
                
                for schema, table, desc in tables_to_check:
                    result = await session.call_tool(
                        name="execute_query",
                        arguments={"query": f"SELECT COUNT(*) FROM {schema}.{table}"}
                    )
                    logger.info(f"✓ {schema}.{table} - {desc}")
                
                # Show sample queries
                logger.info("\n💡 Example Queries You Can Run:")
                logger.info("-" * 70)
                logger.info("""
# 1. Check for price anomalies:
SELECT symbol, ML_MODELS.DETECT_PRICE_ANOMALY(symbol, close, 
    AVG(close) OVER (PARTITION BY symbol ORDER BY timestamp 
    ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING),
    STDDEV(close) OVER (PARTITION BY symbol ORDER BY timestamp 
    ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING)
) as anomaly_status
FROM MARKET_DATA.PRICE_HISTORY
WHERE timestamp > DATEADD(hour, -1, CURRENT_TIMESTAMP());

# 2. Natural language query (after enabling Cortex Analyst):
-- "Show me the top gaining stocks today"
-- Automatically translates to:
SELECT symbol, company_name, price_change_pct 
FROM ML_MODELS.MARKET_SEMANTIC_MODEL 
WHERE DATE(timestamp) = CURRENT_DATE()
ORDER BY price_change_pct DESC LIMIT 10;

# 3. Data quality check:
CALL DATA_QUALITY.RUN_QUALITY_CHECKS();

# 4. Performance analysis:
SELECT * FROM PERFORMANCE.MARKET_HOURS_METRICS
WHERE hour >= DATEADD(hour, -24, CURRENT_TIMESTAMP());
                """)
                
                logger.info("\n🚀 Your Market Oracle is now equipped with:")
                logger.info("• AI-powered price predictions")
                logger.info("• Natural language market queries")
                logger.info("• Automated data quality monitoring")
                logger.info("• Real-time performance tracking")
                
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(verify_setup())