#!/usr/bin/env python3
"""Test Snowflake MCP server connection with actual database connection"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import snowflake.connector
except ImportError:
    print("❌ snowflake-connector-python not installed")
    sys.exit(1)

def test_snowflake_connection():
    """Test actual Snowflake database connection"""
    print("🔍 Testing Snowflake Connection...")
    
    # Get credentials from environment
    config = {
        "user": os.getenv("SNOWFLAKE_USER"),
        "password": os.getenv("SNOWFLAKE_PASSWORD"),
        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        "database": os.getenv("SNOWFLAKE_DATABASE"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
    }
    
    # Check if all required credentials exist
    missing = [k for k, v in config.items() if not v]
    if missing:
        print(f"❌ Missing credentials: {', '.join(missing)}")
        return False
    
    print(f"  Account: {config['account']}")
    print(f"  User: {config['user']}")
    print(f"  Database: {config['database']}")
    print(f"  Warehouse: {config['warehouse']}")
    
    try:
        # Attempt connection
        print("\n📡 Connecting to Snowflake...")
        conn = snowflake.connector.connect(
            **config,
            client_session_keep_alive=True,
            network_timeout=15,
            login_timeout=15
        )
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_VERSION(), CURRENT_TIMESTAMP()")
        result = cursor.fetchone()
        
        print(f"✅ Connection successful!")
        print(f"  Snowflake version: {result[0]}")
        print(f"  Server time: {result[1]}")
        
        # List available databases
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        print(f"\n📊 Available databases: {len(databases)}")
        for db in databases[:5]:  # Show first 5
            print(f"  - {db[1]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_snowflake_connection()
    sys.exit(0 if success else 1)