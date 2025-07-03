#!/usr/bin/env python3
"""Create Market Oracle schema and tables in Snowflake"""

import asyncio
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

async def create_market_oracle_schema():
    """Create complete Market Oracle schema in Snowflake"""
    server_params = StdioServerParameters(
        command="python",
        args=["snowflake_mcp.py"],
        env={}
    )
    
    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                logger.info("🏗️ Creating Market Oracle Schema in MARKETS database...")
                logger.info("=" * 60)
                
                # Use MARKETS database
                await session.call_tool(
                    name="execute_query",
                    arguments={"query": "USE DATABASE MARKETS"}
                )
                
                # Create schemas
                logger.info("\n📁 Creating schemas...")
                schemas = [
                    "CREATE SCHEMA IF NOT EXISTS MARKET_DATA",
                    "CREATE SCHEMA IF NOT EXISTS TECHNICAL_ANALYSIS", 
                    "CREATE SCHEMA IF NOT EXISTS SENTIMENT",
                    "CREATE SCHEMA IF NOT EXISTS PORTFOLIO",
                    "CREATE SCHEMA IF NOT EXISTS RISK_MANAGEMENT"
                ]
                
                for schema_sql in schemas:
                    result = await session.call_tool(
                        name="execute_query",
                        arguments={"query": schema_sql}
                    )
                    logger.info(f"✓ {schema_sql.split()[3]}")
                
                # Create Market Data tables
                logger.info("\n📊 Creating Market Data tables...")
                
                # Price data table
                price_table = """
                CREATE TABLE IF NOT EXISTS MARKET_DATA.PRICE_HISTORY (
                    symbol VARCHAR(20) NOT NULL,
                    timestamp TIMESTAMP_NTZ NOT NULL,
                    open DECIMAL(20,6),
                    high DECIMAL(20,6),
                    low DECIMAL(20,6),
                    close DECIMAL(20,6),
                    volume DECIMAL(20,2),
                    source VARCHAR(50),
                    asset_type VARCHAR(20), -- 'stock', 'crypto', 'forex', 'commodity'
                    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                    PRIMARY KEY (symbol, timestamp)
                )
                """
                await session.call_tool(
                    name="execute_query",
                    arguments={"query": price_table}
                )
                logger.info("✓ PRICE_HISTORY table")
                
                # Company info table
                company_table = """
                CREATE TABLE IF NOT EXISTS MARKET_DATA.COMPANY_INFO (
                    symbol VARCHAR(20) PRIMARY KEY,
                    name VARCHAR(255),
                    sector VARCHAR(100),
                    industry VARCHAR(100),
                    market_cap DECIMAL(20,2),
                    country VARCHAR(50),
                    exchange VARCHAR(50),
                    ipo_date DATE,
                    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
                )
                """
                await session.call_tool(
                    name="execute_query",
                    arguments={"query": company_table}
                )
                logger.info("✓ COMPANY_INFO table")
                
                # Technical indicators table
                logger.info("\n📈 Creating Technical Analysis tables...")
                
                indicators_table = """
                CREATE TABLE IF NOT EXISTS TECHNICAL_ANALYSIS.INDICATORS (
                    symbol VARCHAR(20) NOT NULL,
                    timestamp TIMESTAMP_NTZ NOT NULL,
                    indicator_name VARCHAR(50) NOT NULL,
                    timeframe VARCHAR(10), -- '1m', '5m', '1h', '1d'
                    value DECIMAL(20,6),
                    signal VARCHAR(20), -- 'buy', 'sell', 'neutral'
                    parameters VARIANT, -- JSON for indicator settings
                    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                    PRIMARY KEY (symbol, timestamp, indicator_name, timeframe)
                )
                """
                await session.call_tool(
                    name="execute_query",
                    arguments={"query": indicators_table}
                )
                logger.info("✓ INDICATORS table")
                
                # Sentiment data tables
                logger.info("\n💭 Creating Sentiment tables...")
                
                sentiment_table = """
                CREATE TABLE IF NOT EXISTS SENTIMENT.SOCIAL_SENTIMENT (
                    symbol VARCHAR(20) NOT NULL,
                    timestamp TIMESTAMP_NTZ NOT NULL,
                    source VARCHAR(50), -- 'reddit', 'twitter', 'news'
                    sentiment_score DECIMAL(5,4), -- -1 to 1
                    volume INT, -- number of mentions
                    bullish_count INT,
                    bearish_count INT,
                    neutral_count INT,
                    top_keywords VARIANT, -- JSON array
                    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                    PRIMARY KEY (symbol, timestamp, source)
                )
                """
                await session.call_tool(
                    name="execute_query",
                    arguments={"query": sentiment_table}
                )
                logger.info("✓ SOCIAL_SENTIMENT table")
                
                # News sentiment table
                news_table = """
                CREATE TABLE IF NOT EXISTS SENTIMENT.NEWS_ARTICLES (
                    article_id VARCHAR(255) PRIMARY KEY,
                    symbol VARCHAR(20),
                    published_at TIMESTAMP_NTZ,
                    title TEXT,
                    summary TEXT,
                    url VARCHAR(1000),
                    source VARCHAR(100),
                    sentiment_score DECIMAL(5,4),
                    relevance_score DECIMAL(5,4),
                    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
                )
                """
                await session.call_tool(
                    name="execute_query",
                    arguments={"query": news_table}
                )
                logger.info("✓ NEWS_ARTICLES table")
                
                # Portfolio tables
                logger.info("\n💼 Creating Portfolio tables...")
                
                portfolio_table = """
                CREATE TABLE IF NOT EXISTS PORTFOLIO.PORTFOLIOS (
                    portfolio_id VARCHAR(100) PRIMARY KEY,
                    name VARCHAR(255),
                    strategy VARCHAR(100),
                    initial_capital DECIMAL(20,2),
                    current_value DECIMAL(20,2),
                    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
                )
                """
                await session.call_tool(
                    name="execute_query",
                    arguments={"query": portfolio_table}
                )
                logger.info("✓ PORTFOLIOS table")
                
                positions_table = """
                CREATE TABLE IF NOT EXISTS PORTFOLIO.POSITIONS (
                    position_id VARCHAR(100) PRIMARY KEY,
                    portfolio_id VARCHAR(100),
                    symbol VARCHAR(20),
                    quantity DECIMAL(20,6),
                    entry_price DECIMAL(20,6),
                    current_price DECIMAL(20,6),
                    entry_date TIMESTAMP_NTZ,
                    exit_date TIMESTAMP_NTZ,
                    status VARCHAR(20), -- 'open', 'closed'
                    pnl DECIMAL(20,2),
                    pnl_percent DECIMAL(10,4),
                    FOREIGN KEY (portfolio_id) REFERENCES PORTFOLIO.PORTFOLIOS(portfolio_id)
                )
                """
                await session.call_tool(
                    name="execute_query",
                    arguments={"query": positions_table}
                )
                logger.info("✓ POSITIONS table")
                
                # Risk management tables
                logger.info("\n⚠️ Creating Risk Management tables...")
                
                risk_metrics_table = """
                CREATE TABLE IF NOT EXISTS RISK_MANAGEMENT.RISK_METRICS (
                    portfolio_id VARCHAR(100),
                    date DATE,
                    var_95 DECIMAL(20,6), -- Value at Risk
                    sharpe_ratio DECIMAL(10,4),
                    max_drawdown DECIMAL(10,4),
                    beta DECIMAL(10,4),
                    volatility DECIMAL(10,4),
                    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                    PRIMARY KEY (portfolio_id, date)
                )
                """
                await session.call_tool(
                    name="execute_query",
                    arguments={"query": risk_metrics_table}
                )
                logger.info("✓ RISK_METRICS table")
                
                # Create views
                logger.info("\n👁️ Creating useful views...")
                
                latest_prices_view = """
                CREATE OR REPLACE VIEW MARKET_DATA.LATEST_PRICES AS
                SELECT 
                    symbol,
                    timestamp,
                    close as price,
                    volume,
                    asset_type
                FROM MARKET_DATA.PRICE_HISTORY
                QUALIFY ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY timestamp DESC) = 1
                """
                await session.call_tool(
                    name="execute_query",
                    arguments={"query": latest_prices_view}
                )
                logger.info("✓ LATEST_PRICES view")
                
                # Create sample data
                logger.info("\n📝 Inserting sample data...")
                
                # Insert sample companies
                sample_companies = """
                INSERT INTO MARKET_DATA.COMPANY_INFO (symbol, name, sector, industry, market_cap, exchange)
                SELECT * FROM VALUES
                    ('AAPL', 'Apple Inc.', 'Technology', 'Consumer Electronics', 3000000000000, 'NASDAQ'),
                    ('MSFT', 'Microsoft Corporation', 'Technology', 'Software', 2800000000000, 'NASDAQ'),
                    ('GOOGL', 'Alphabet Inc.', 'Technology', 'Internet Services', 1800000000000, 'NASDAQ'),
                    ('BTC-USD', 'Bitcoin', 'Cryptocurrency', 'Digital Currency', 800000000000, 'CRYPTO'),
                    ('ETH-USD', 'Ethereum', 'Cryptocurrency', 'Smart Contracts', 300000000000, 'CRYPTO')
                """
                await session.call_tool(
                    name="execute_query",
                    arguments={"query": sample_companies}
                )
                logger.info("✓ Sample companies inserted")
                
                logger.info("\n✅ Market Oracle schema created successfully!")
                logger.info("\n📊 Available for Market Oracle agents:")
                logger.info("- Price data ingestion and storage")
                logger.info("- Technical indicator calculations")
                logger.info("- Sentiment analysis tracking")
                logger.info("- Portfolio management")
                logger.info("- Risk metrics computation")
                
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_market_oracle_schema())