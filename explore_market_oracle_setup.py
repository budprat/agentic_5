#!/usr/bin/env python3
"""Explore the Market Oracle setup in Snowflake"""

import asyncio
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

async def explore_market_oracle():
    """Show what's available in Market Oracle"""
    server_params = StdioServerParameters(
        command="python",
        args=["snowflake_mcp.py"],
        env={}
    )
    
    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                await session.call_tool(
                    name="execute_query",
                    arguments={"query": "USE DATABASE MARKETS"}
                )
                
                logger.info("🏦 Market Oracle Database Structure")
                logger.info("=" * 60)
                
                # Show all schemas
                logger.info("\n📁 Schemas:")
                result = await session.call_tool(
                    name="execute_query",
                    arguments={"query": "SHOW SCHEMAS"}
                )
                if hasattr(result, 'content') and len(result.content) > 0:
                    text = result.content[0].text
                    if "MARKET_DATA" in text:
                        logger.info("✓ MARKET_DATA - Store price history and company info")
                        logger.info("✓ TECHNICAL_ANALYSIS - Calculate and store indicators")
                        logger.info("✓ SENTIMENT - Track social and news sentiment")
                        logger.info("✓ PORTFOLIO - Manage portfolios and positions")
                        logger.info("✓ RISK_MANAGEMENT - Track risk metrics")
                
                # Show tables in each schema
                schemas = ['MARKET_DATA', 'TECHNICAL_ANALYSIS', 'SENTIMENT', 'PORTFOLIO', 'RISK_MANAGEMENT']
                
                for schema in schemas:
                    logger.info(f"\n📊 Tables in {schema}:")
                    result = await session.call_tool(
                        name="execute_query",
                        arguments={"query": f"SHOW TABLES IN SCHEMA {schema}"}
                    )
                    if hasattr(result, 'content') and len(result.content) > 0:
                        text = result.content[0].text
                        lines = text.split('\n')
                        for line in lines:
                            if 'rows in' in line and 'Results' in line:
                                continue
                            if line.strip() and '[{' in line:
                                # Parse the table info
                                import json
                                try:
                                    tables = eval(line.strip())
                                    for table in tables:
                                        logger.info(f"  - {table['name']}")
                                except:
                                    pass
                
                # Show sample data
                logger.info("\n📈 Sample Companies in Database:")
                result = await session.call_tool(
                    name="execute_query",
                    arguments={"query": "SELECT * FROM MARKET_DATA.COMPANY_INFO"}
                )
                if hasattr(result, 'content') and len(result.content) > 0:
                    text = result.content[0].text
                    lines = text.split('\n')
                    for line in lines:
                        if '[{' in line:
                            import json
                            try:
                                companies = eval(line.strip())
                                for company in companies:
                                    logger.info(f"  - {company['symbol']}: {company['name']} ({company['sector']})")
                            except:
                                pass
                
                # Show capabilities
                logger.info("\n🚀 Market Oracle Capabilities with Snowflake MCP:")
                logger.info("-" * 60)
                logger.info("""
1. **Real-time Data Ingestion**
   - Use execute_query to INSERT price data from APIs
   - Store data from Alpha Vantage, Polygon, Yahoo Finance
   
2. **Technical Analysis**
   - Calculate indicators using SQL window functions
   - Store RSI, MACD, Moving Averages
   
3. **Sentiment Tracking**
   - Store Reddit sentiment scores
   - Track news sentiment over time
   
4. **Portfolio Analytics**
   - Track multiple portfolios
   - Calculate P&L and risk metrics
   
5. **Market Intelligence Queries**
   - Find correlations between assets
   - Identify trend patterns
   - Alert on unusual market movements

Example queries the Market Oracle agents can run:
- "What's the 30-day price trend for AAPL?"
- "Show me stocks with RSI < 30 (oversold)"
- "What's the sentiment score for crypto today?"
- "Calculate my portfolio's Sharpe ratio"
                """)
                
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(explore_market_oracle())