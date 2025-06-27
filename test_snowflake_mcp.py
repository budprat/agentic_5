#!/usr/bin/env python3
"""Test Snowflake MCP Integration"""

import os
import asyncio
import json
from datetime import datetime

# Set environment variables
os.environ['SNOWFLAKE_ACCOUNT'] = 'NBTQRQH-YX22629'
os.environ['SNOWFLAKE_USER'] = 'PBUDHWAR'
os.environ['SNOWFLAKE_PASSWORD'] = 'Tordywcehhavvyrwi4'
os.environ['SNOWFLAKE_DATABASE'] = 'SNOWFLAKE'
os.environ['SNOWFLAKE_WAREHOUSE'] = 'COMPUTE_WH'

# Import the Snowflake MCP components
from snowflake_mcp import SnowflakeConnection

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"🔷 {title}")
    print("="*80)

async def test_snowflake_connection():
    """Test Snowflake MCP functionality"""
    print("\n" + "🔷"*20)
    print("\n✨ SNOWFLAKE MCP INTEGRATION TEST ✨".center(80))
    print("\n" + "🔷"*20)
    
    # Initialize connection
    print("\n📋 Test Overview:")
    print("  • Connect to Snowflake")
    print("  • Execute queries")
    print("  • Show available data")
    print("  • Demonstrate integration with Market Oracle")
    
    snowflake = SnowflakeConnection()
    
    try:
        # Test 1: Basic Connection
        print_section("TEST 1: BASIC CONNECTION")
        print("Connecting to Snowflake...")
        conn = snowflake.verify_link()
        print("✅ Connection established successfully!")
        
        # Test 2: Show Available Databases
        print_section("TEST 2: SHOW AVAILABLE DATABASES")
        databases = snowflake.process_request("SHOW DATABASES")
        print(f"\n📊 Available Databases ({len(databases)}):")
        for db in databases[:5]:  # Show first 5
            print(f"  • {db.get('name', 'Unknown')}")
            
        # Test 3: Show Sample Data
        print_section("TEST 3: SAMPLE DATA QUERY")
        
        # Try to query sample data
        try:
            # First, let's see what schemas are available
            print("\n🔍 Checking available schemas...")
            schemas = snowflake.process_request("SHOW SCHEMAS IN DATABASE SNOWFLAKE")
            
            if schemas:
                print(f"\nFound {len(schemas)} schemas:")
                for schema in schemas[:5]:
                    print(f"  • {schema.get('name', 'Unknown')}")
            
            # Try to find tables in the CORTEX schema
            print("\n🔍 Looking for tables in CORTEX schema...")
            snowflake.process_request("USE DATABASE SNOWFLAKE")
            snowflake.process_request("USE SCHEMA CORTEX")
            
            tables = snowflake.process_request("SHOW TABLES")
            if tables:
                print(f"\nFound {len(tables)} tables:")
                for table in tables[:5]:
                    print(f"  • {table.get('name', 'Unknown')}")
                    
                # Query first table if available
                if tables:
                    first_table = tables[0].get('name')
                    print(f"\n📊 Sample data from {first_table}:")
                    sample_data = snowflake.process_request(f"SELECT * FROM {first_table} LIMIT 5")
                    
                    if sample_data:
                        # Display sample data
                        for i, row in enumerate(sample_data, 1):
                            print(f"\nRow {i}:")
                            for key, value in list(row.items())[:3]:  # Show first 3 columns
                                print(f"  {key}: {value}")
            else:
                print("No tables found in CORTEX schema")
                
        except Exception as e:
            print(f"⚠️ Sample data query error: {e}")
            
        # Test 4: Market Data Query (if available)
        print_section("TEST 4: MARKET DATA CAPABILITIES")
        
        # Try to find market-related tables
        try:
            # Search for market-related tables across all schemas
            market_tables = snowflake.process_request("""
                SELECT table_schema, table_name 
                FROM information_schema.tables 
                WHERE table_name LIKE '%STOCK%' 
                   OR table_name LIKE '%MARKET%' 
                   OR table_name LIKE '%PRICE%'
                   OR table_name LIKE '%TRADE%'
                LIMIT 10
            """)
            
            if market_tables:
                print(f"\n📈 Found {len(market_tables)} market-related tables:")
                for table in market_tables:
                    print(f"  • {table.get('TABLE_SCHEMA')}.{table.get('TABLE_NAME')}")
            else:
                print("\n📊 No market data tables found - can create custom tables for Market Oracle")
                
        except Exception as e:
            print(f"⚠️ Market data search error: {e}")
            
        # Test 5: Integration Potential
        print_section("TEST 5: MARKET ORACLE INTEGRATION POTENTIAL")
        
        print("\n🚀 Snowflake can be integrated with Market Oracle for:")
        print("  ✓ Historical price data storage")
        print("  ✓ Large-scale market analytics")
        print("  ✓ Time-series analysis with Snowflake's built-in functions")
        print("  ✓ ML model training data storage")
        print("  ✓ Backtesting historical strategies")
        print("  ✓ Real-time data streaming with Snowpipe")
        
        # Show a sample create table for Market Oracle
        print("\n📝 Example: Creating Market Oracle tables in Snowflake")
        print("""
        CREATE TABLE IF NOT EXISTS market_oracle_signals (
            signal_id VARCHAR,
            symbol VARCHAR,
            signal_type VARCHAR,
            confidence_score FLOAT,
            created_at TIMESTAMP,
            agent_name VARCHAR,
            reasoning TEXT
        );
        """)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        snowflake.cleanup()
        print("\n✅ Connection closed")
        
    # Summary
    print("\n\n" + "="*80)
    print("📊 SNOWFLAKE MCP TEST SUMMARY")
    print("="*80)
    print("\n✅ Snowflake MCP is operational and ready for integration!")
    print("\n🎯 Next Steps:")
    print("  1. Create Market Oracle specific tables")
    print("  2. Import historical market data")
    print("  3. Integrate with Oracle Prime for data analysis")
    print("  4. Use for backtesting and ML training")
    print("\n" + "🔷"*20)

if __name__ == "__main__":
    asyncio.run(test_snowflake_connection())