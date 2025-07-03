#!/usr/bin/env python3
"""Explore MARKETS database for Market Oracle capabilities"""

import json
import asyncio
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

async def explore_markets_database():
    """Explore MARKETS database structure and data"""
    server_params = StdioServerParameters(
        command="python",
        args=["snowflake_mcp.py"],
        env={}
    )
    
    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                # Switch to MARKETS database
                logger.info("🏦 Switching to MARKETS database...")
                logger.info("=" * 60)
                
                await session.call_tool(
                    name="execute_query",
                    arguments={"query": "USE DATABASE MARKETS"}
                )
                
                # Query 1: Show schemas in MARKETS database
                logger.info("\n📂 Schemas in MARKETS database:")
                logger.info("-" * 60)
                
                result = await session.call_tool(
                    name="execute_query",
                    arguments={"query": "SHOW SCHEMAS"}
                )
                
                if hasattr(result, 'content') and len(result.content) > 0:
                    logger.info(result.content[0].text)
                
                # Query 2: Show all tables in MARKETS database
                logger.info("\n📊 Tables in MARKETS database:")
                logger.info("-" * 60)
                
                result = await session.call_tool(
                    name="execute_query",
                    arguments={"query": "SHOW TABLES IN DATABASE MARKETS"}
                )
                
                if hasattr(result, 'content') and len(result.content) > 0:
                    logger.info(result.content[0].text)
                
                # Query 3: Show views (if any)
                logger.info("\n👁️ Views in MARKETS database:")
                logger.info("-" * 60)
                
                result = await session.call_tool(
                    name="execute_query",
                    arguments={"query": "SHOW VIEWS IN DATABASE MARKETS"}
                )
                
                if hasattr(result, 'content') and len(result.content) > 0:
                    logger.info(result.content[0].text)
                
                # Query 4: Check for common market data tables
                logger.info("\n🔍 Looking for market data tables...")
                logger.info("-" * 60)
                
                # Try PUBLIC schema first
                await session.call_tool(
                    name="execute_query",
                    arguments={"query": "USE SCHEMA PUBLIC"}
                )
                
                # Check if we have any price/quote/trade tables
                common_table_patterns = [
                    "SHOW TABLES LIKE '%PRICE%'",
                    "SHOW TABLES LIKE '%QUOTE%'",
                    "SHOW TABLES LIKE '%TRADE%'",
                    "SHOW TABLES LIKE '%STOCK%'",
                    "SHOW TABLES LIKE '%MARKET%'",
                    "SHOW TABLES LIKE '%TICKER%'",
                    "SHOW TABLES LIKE '%PORTFOLIO%'"
                ]
                
                for pattern in common_table_patterns:
                    result = await session.call_tool(
                        name="execute_query",
                        arguments={"query": pattern}
                    )
                    
                    if hasattr(result, 'content') and len(result.content) > 0:
                        text = result.content[0].text
                        if "rows in" in text and not "0 rows in" in text:
                            logger.info(f"\nFound tables matching '{pattern}':")
                            logger.info(text)
                
                # Query 5: Sample data from any existing tables
                logger.info("\n📈 Market Oracle Capabilities with Snowflake:")
                logger.info("-" * 60)
                logger.info("""
Based on the MARKETS database, we can implement:

1. **Historical Price Data Storage**
   - Store OHLCV data for stocks, crypto, forex
   - Time-series data with minute/hour/day granularity
   
2. **Real-time Market Data Pipeline**
   - Ingest data from multiple sources (Alpha Vantage, Polygon, etc.)
   - Store in Snowflake for analysis
   
3. **Technical Indicators**
   - Calculate moving averages, RSI, MACD
   - Store pre-calculated indicators for fast retrieval
   
4. **Market Sentiment Data**
   - Store Reddit/news sentiment scores
   - Link sentiment to price movements
   
5. **Portfolio Analytics**
   - Track portfolio performance
   - Risk metrics calculation
   
6. **Market Correlations**
   - Cross-asset correlation analysis
   - Sector rotation patterns

Would you like me to create the schema and tables for Market Oracle?
                """)
                
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(explore_markets_database())