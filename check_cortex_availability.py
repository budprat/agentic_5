#!/usr/bin/env python3
"""
Check Cortex availability and proper setup in Snowflake
"""

import os
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

def check_cortex():
    """Comprehensive check for Cortex availability"""
    
    # Get credentials
    account = os.getenv('SNOWFLAKE_ACCOUNT')
    user = os.getenv('SNOWFLAKE_USER')
    password = os.getenv('SNOWFLAKE_PASSWORD')
    warehouse = os.getenv('SNOWFLAKE_WAREHOUSE')
    
    conn = snowflake.connector.connect(
        account=account,
        user=user,
        password=password,
        role='ACCOUNTADMIN',
        warehouse=warehouse
    )
    
    cursor = conn.cursor()
    
    try:
        print("🔍 Checking Cortex Availability")
        print("=" * 70)
        
        # 1. Check account edition
        print("\n1️⃣ Checking Snowflake Edition...")
        cursor.execute("SELECT CURRENT_ACCOUNT(), CURRENT_REGION()")
        account_info = cursor.fetchone()
        print(f"Account: {account_info[0]}")
        print(f"Region: {account_info[1]}")
        
        # 2. Check available databases
        print("\n2️⃣ Checking SNOWFLAKE database schemas...")
        cursor.execute("USE DATABASE SNOWFLAKE")
        cursor.execute("SHOW SCHEMAS")
        schemas = cursor.fetchall()
        print("Available schemas in SNOWFLAKE database:")
        for schema in schemas:
            print(f"  - {schema[1]}")  # Schema name is in column 1
        
        # 3. Check if ML functions exist
        print("\n3️⃣ Checking for ML/AI functions...")
        cursor.execute("USE WAREHOUSE " + warehouse)
        
        # Try different approaches to find Cortex functions
        print("\nChecking in SNOWFLAKE.ML schema...")
        try:
            cursor.execute("USE SCHEMA SNOWFLAKE.ML")
            cursor.execute("SHOW FUNCTIONS")
            functions = cursor.fetchall()
            ml_functions = [f for f in functions if 'COMPLETE' in str(f) or 'SENTIMENT' in str(f)]
            if ml_functions:
                print("✅ Found ML functions in SNOWFLAKE.ML schema")
                for func in ml_functions[:5]:  # Show first 5
                    print(f"  - {func[1]}")
        except Exception as e:
            print(f"❌ SNOWFLAKE.ML schema not accessible: {e}")
        
        # 4. Try direct Cortex function call
        print("\n4️⃣ Testing direct Cortex function calls...")
        test_queries = [
            ("SNOWFLAKE.CORTEX.COMPLETE", "SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-7b', 'Hello') as response"),
            ("SNOWFLAKE.CORTEX.SENTIMENT", "SELECT SNOWFLAKE.CORTEX.SENTIMENT('Great product!') as sentiment"),
            ("SNOWFLAKE.ML.COMPLETE", "SELECT SNOWFLAKE.ML.COMPLETE('mistral-7b', 'Hello') as response"),
        ]
        
        for func_name, query in test_queries:
            try:
                print(f"\nTrying {func_name}...")
                cursor.execute(query)
                result = cursor.fetchone()
                print(f"✅ {func_name} works! Response: {str(result[0])[:100]}...")
                break
            except Exception as e:
                error_msg = str(e)
                if "unknown function" in error_msg.lower():
                    print(f"❌ {func_name} not found")
                elif "not available" in error_msg.lower():
                    print(f"⚠️  {func_name} exists but model not available in region")
                else:
                    print(f"❌ {func_name} error: {error_msg[:100]}...")
        
        # 5. Check available models
        print("\n5️⃣ Checking available LLM models...")
        models = ['mistral-7b', 'llama2-7b-chat', 'gemma-7b', 'mixtral-8x7b', 
                  'llama3-8b', 'llama3-70b', 'llama3.1-8b', 'llama3.1-70b']
        
        working_models = []
        for model in models:
            try:
                cursor.execute(f"""
                    SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', 'test') as response
                """)
                result = cursor.fetchone()
                if result:
                    working_models.append(model)
                    print(f"✅ {model} - Available")
            except Exception as e:
                if "not available" in str(e).lower():
                    print(f"❌ {model} - Not available in this region")
                elif "unknown function" in str(e).lower():
                    # Try with ML schema
                    try:
                        cursor.execute(f"""
                            SELECT SNOWFLAKE.ML.COMPLETE('{model}', 'test') as response
                        """)
                        result = cursor.fetchone()
                        if result:
                            working_models.append(f"{model} (via ML schema)")
                            print(f"✅ {model} - Available via SNOWFLAKE.ML")
                    except:
                        print(f"❌ {model} - Not found")
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 SUMMARY")
        print("=" * 70)
        
        if working_models:
            print(f"✅ Cortex is available with {len(working_models)} models:")
            for model in working_models:
                print(f"   - {model}")
            print("\n💡 To use Cortex, make sure to:")
            print("   1. Grant CORTEX_USER database role to your role")
            print("   2. Use the correct schema (SNOWFLAKE.CORTEX or SNOWFLAKE.ML)")
            print("   3. Select an available model from the list above")
        else:
            print("❌ Cortex functions are not available")
            print("\nPossible reasons:")
            print("1. Your Snowflake edition might not include Cortex")
            print("2. Cortex might not be available in your region")
            print("3. You might need to enable Cortex through Snowflake support")
            print("\n💡 Contact Snowflake support to enable Cortex LLM features")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_cortex()