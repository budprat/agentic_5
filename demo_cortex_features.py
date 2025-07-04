#!/usr/bin/env python3
"""Demonstrate Snowflake Cortex features for Market Oracle"""

import asyncio
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
import logging
from datetime import datetime, timedelta
import random

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

async def demo_cortex_features():
    """Demonstrate all implemented Cortex features"""
    server_params = StdioServerParameters(
        command="python",
        args=["snowflake_mcp.py"],
        env={}
    )
    
    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                logger.info("🎯 Demonstrating Snowflake Cortex Features")
                logger.info("=" * 70)
                
                await session.call_tool(
                    name="execute_query",
                    arguments={"query": "USE DATABASE MARKETS"}
                )
                
                # 1. AI-POWERED PREDICTIONS DEMO
                logger.info("\n1️⃣ AI-Powered Market Predictions Demo")
                logger.info("-" * 70)
                
                # Insert sample prediction
                prediction_query = f"""
                INSERT INTO ML_MODELS.MARKET_PREDICTIONS 
                (prediction_id, symbol, prediction_date, target_date, prediction_type, 
                 predicted_value, confidence_score, model_name, features_used)
                VALUES 
                ('pred_001', 'AAPL', CURRENT_TIMESTAMP(), 
                 DATEADD(day, 1, CURRENT_TIMESTAMP()), 'price',
                 185.50, 0.87, 'CORTEX_LSTM_V1',
                 PARSE_JSON('{{"rsi": 45, "volume_trend": "increasing", "sentiment": 0.72}}'))
                """
                await session.call_tool(
                    name="execute_query",
                    arguments={"query": prediction_query}
                )
                logger.info("✓ Created sample AI prediction for AAPL")
                
                # Test anomaly detection
                logger.info("\n🔍 Testing Anomaly Detection:")
                anomaly_test = """
                SELECT 
                    'AAPL' as symbol,
                    180.0 as current_price,
                    175.0 as avg_price,
                    3.0 as std_dev,
                    ML_MODELS.DETECT_PRICE_ANOMALY('AAPL', 180.0, 175.0, 3.0) as anomaly_status
                UNION ALL
                SELECT 
                    'MSFT', 400.0, 380.0, 5.0,
                    ML_MODELS.DETECT_PRICE_ANOMALY('MSFT', 400.0, 380.0, 5.0)
                """
                result = await session.call_tool(
                    name="execute_query",
                    arguments={"query": anomaly_test}
                )
                if hasattr(result, 'content') and len(result.content) > 0:
                    logger.info(f"Anomaly detection results:\n{result.content[0].text}")
                
                # 2. NATURAL LANGUAGE QUERIES DEMO
                logger.info("\n2️⃣ Natural Language Market Queries Demo")
                logger.info("-" * 70)
                
                # First, insert some sample price data
                logger.info("📊 Inserting sample market data...")
                for symbol in ['AAPL', 'MSFT', 'GOOGL']:
                    for i in range(10):
                        timestamp = datetime.now() - timedelta(hours=i)
                        price = 150 + random.uniform(-5, 5) if symbol == 'AAPL' else 380 + random.uniform(-10, 10)
                        volume = random.randint(1000000, 5000000)
                        
                        insert_price = f"""
                        INSERT INTO MARKET_DATA.PRICE_HISTORY 
                        (symbol, timestamp, open, high, low, close, volume, source, asset_type)
                        VALUES 
                        ('{symbol}', '{timestamp}', {price-1}, {price+1}, {price-2}, {price}, {volume}, 
                         'DEMO', 'stock')
                        """
                        await session.call_tool(
                            name="execute_query",
                            arguments={"query": insert_price}
                        )
                
                logger.info("✓ Sample data inserted")
                
                # Show available query templates
                logger.info("\n📋 Available Natural Language Query Templates:")
                templates_query = "SELECT template_id, example_question FROM ML_MODELS.QUERY_TEMPLATES"
                result = await session.call_tool(
                    name="execute_query",
                    arguments={"query": templates_query}
                )
                if hasattr(result, 'content') and len(result.content) > 0:
                    logger.info(result.content[0].text)
                
                # 3. DATA QUALITY MONITORING DEMO
                logger.info("\n3️⃣ Data Quality Monitoring Demo")
                logger.info("-" * 70)
                
                # Run quality check on price data
                quality_check = """
                SELECT 
                    'Price Completeness Check' as check_name,
                    COUNT(*) as total_records,
                    SUM(CASE WHEN close IS NULL THEN 1 ELSE 0 END) as null_prices,
                    SUM(CASE WHEN close <= 0 THEN 1 ELSE 0 END) as invalid_prices
                FROM MARKET_DATA.PRICE_HISTORY
                WHERE timestamp > DATEADD(hour, -24, CURRENT_TIMESTAMP())
                """
                result = await session.call_tool(
                    name="execute_query",
                    arguments={"query": quality_check}
                )
                if hasattr(result, 'content') and len(result.content) > 0:
                    logger.info(f"Data quality results:\n{result.content[0].text}")
                
                # Insert quality check result
                check_result = """
                INSERT INTO DATA_QUALITY.MONITORING_RESULTS
                (check_id, rule_id, check_timestamp, records_checked, records_failed, 
                 failure_rate, status)
                VALUES
                ('check_001', 'price_not_null', CURRENT_TIMESTAMP(), 100, 0, 0.0, 'passed')
                """
                await session.call_tool(
                    name="execute_query",
                    arguments={"query": check_result}
                )
                logger.info("✓ Quality monitoring result recorded")
                
                # 4. PERFORMANCE TRACKING DEMO
                logger.info("\n4️⃣ Performance Telemetry Demo")
                logger.info("-" * 70)
                
                # Record query performance
                perf_record = """
                INSERT INTO PERFORMANCE.QUERY_METRICS
                (query_id, query_type, query_text, execution_time_ms, 
                 rows_processed, bytes_scanned, warehouse_size, user_name, success)
                VALUES
                ('qry_001', 'analysis', 'SELECT AVG(close) FROM PRICE_HISTORY', 
                 125, 1000, 50000, 'SMALL', CURRENT_USER(), TRUE),
                ('qry_002', 'data_ingestion', 'INSERT INTO PRICE_HISTORY...', 
                 45, 100, 10000, 'SMALL', CURRENT_USER(), TRUE),
                ('qry_003', 'prediction', 'ML MODEL PREDICTION', 
                 2500, 5000, 500000, 'MEDIUM', CURRENT_USER(), TRUE)
                """
                await session.call_tool(
                    name="execute_query",
                    arguments={"query": perf_record}
                )
                logger.info("✓ Performance metrics recorded")
                
                # Show performance summary
                perf_summary = """
                SELECT 
                    query_type,
                    COUNT(*) as query_count,
                    AVG(execution_time_ms) as avg_ms,
                    MAX(execution_time_ms) as max_ms
                FROM PERFORMANCE.QUERY_METRICS
                GROUP BY query_type
                """
                result = await session.call_tool(
                    name="execute_query",
                    arguments={"query": perf_summary}
                )
                if hasattr(result, 'content') and len(result.content) > 0:
                    logger.info(f"\nPerformance Summary:\n{result.content[0].text}")
                
                # INTEGRATION EXAMPLE
                logger.info("\n🔗 Complete Integration Example")
                logger.info("-" * 70)
                logger.info("""
How Market Oracle agents use these features:

1. **Technical Prophet Agent**:
   - Stores predictions in MARKET_PREDICTIONS
   - Uses anomaly detection for alerts
   
2. **Oracle Prime Agent**:
   - Processes natural language queries
   - "Show me tech stocks up more than 5%" → SQL query
   
3. **Data Quality Agent** (new):
   - Runs hourly quality checks
   - Alerts on data feed issues
   
4. **Performance Monitor** (new):
   - Tracks query latency during market hours
   - Optimizes slow queries automatically

Example workflow:
User: "What tech stocks look bullish today?"
→ Cortex Analyst interprets query
→ Checks quality of recent data
→ Runs optimized SQL query
→ Returns results with confidence scores
                """)
                
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(demo_cortex_features())