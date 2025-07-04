#!/usr/bin/env python3
"""
Diagnose Cortex/AI feature availability in Snowflake
"""

import os
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

def diagnose_cortex():
    """Comprehensive diagnosis of Cortex availability"""
    
    # Get credentials
    account = os.getenv('SNOWFLAKE_ACCOUNT')
    user = os.getenv('SNOWFLAKE_USER')
    password = os.getenv('SNOWFLAKE_PASSWORD')
    warehouse = os.getenv('SNOWFLAKE_WAREHOUSE')
    
    print("🔍 Snowflake Cortex/AI Diagnostics")
    print("=" * 70)
    print(f"Account: {account}")
    print(f"User: {user}")
    print(f"Warehouse: {warehouse}")
    print("=" * 70)
    
    # Try with ACCOUNTADMIN first
    conn = snowflake.connector.connect(
        account=account,
        user=user,
        password=password,
        role='ACCOUNTADMIN'
    )
    
    cursor = conn.cursor()
    
    try:
        # 1. Check warehouse access
        print("\n1️⃣ Checking warehouse access...")
        cursor.execute("SHOW WAREHOUSES")
        warehouses = cursor.fetchall()
        print("Available warehouses:")
        for wh in warehouses:
            print(f"  - {wh[0]} (state: {wh[2]})")
        
        # Use warehouse
        try:
            cursor.execute(f"USE WAREHOUSE {warehouse}")
            print(f"✅ Using warehouse: {warehouse}")
        except Exception as e:
            print(f"❌ Cannot use warehouse {warehouse}: {e}")
            # Try to find any available warehouse
            for wh in warehouses:
                try:
                    cursor.execute(f"USE WAREHOUSE {wh[0]}")
                    print(f"✅ Switched to warehouse: {wh[0]}")
                    break
                except:
                    continue
        
        # 2. Check Cortex-specific settings
        print("\n2️⃣ Checking Cortex/AI related parameters...")
        params_to_check = [
            'ENABLE_CORTEX_SERVICE',
            'CORTEX_ENABLED_REGIONS',
            'AI_ENABLED',
            'ML_ENABLED'
        ]
        
        for param in params_to_check:
            try:
                cursor.execute(f"SHOW PARAMETERS LIKE '{param}' IN ACCOUNT")
                result = cursor.fetchall()
                if result:
                    print(f"  - {param}: {result[0][1] if len(result[0]) > 1 else 'Not found'}")
            except:
                pass
        
        # 3. Check available features
        print("\n3️⃣ Checking feature availability...")
        cursor.execute("SELECT SYSTEM$BEHAVIOR_CHANGE_BUNDLE_STATUS('2024_01')")
        bundle_status = cursor.fetchone()
        print(f"Behavior bundle status: {bundle_status[0] if bundle_status else 'Unknown'}")
        
        # 4. Direct Cortex test with proper setup
        print("\n4️⃣ Testing Cortex functions with proper setup...")
        cursor.execute("USE DATABASE SNOWFLAKE")
        
        # Check both CORTEX and ML schemas
        for schema in ['CORTEX', 'ML']:
            print(f"\nChecking {schema} schema...")
            try:
                cursor.execute(f"USE SCHEMA {schema}")
                cursor.execute("SHOW FUNCTIONS")
                functions = cursor.fetchall()
                ai_functions = [f for f in functions if any(x in f[1].upper() for x in ['COMPLETE', 'SENTIMENT', 'AI', 'LLM'])]
                if ai_functions:
                    print(f"✅ Found {len(ai_functions)} AI-related functions in {schema}:")
                    for func in ai_functions[:5]:
                        print(f"   - {func[1]}")
            except Exception as e:
                print(f"❌ Cannot access {schema} schema: {str(e)[:100]}")
        
        # 5. Test with different function paths
        print("\n5️⃣ Testing function calls...")
        test_queries = [
            "SELECT SNOWFLAKE.CORTEX.COMPLETE('llama2-7b-chat', 'Hello')",
            "SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-7b', 'Hello')",
            "SELECT SNOWFLAKE.ML.COMPLETE('mistral-7b', 'Hello')",
            "SELECT COMPLETE('mistral-7b', 'Hello')",
            "SELECT AI_COMPLETE('Hello')",
        ]
        
        for query in test_queries:
            try:
                print(f"\nTrying: {query[:60]}...")
                cursor.execute(query)
                result = cursor.fetchone()
                print(f"✅ SUCCESS! Result: {str(result[0])[:100] if result else 'Empty'}")
                break
            except Exception as e:
                error_msg = str(e)
                if "not available in region" in error_msg:
                    print("❌ Model not available in your region")
                elif "unknown function" in error_msg:
                    print("❌ Function not found")
                elif "Remote service error" in error_msg:
                    print("❌ Remote service error (might need activation)")
                else:
                    print(f"❌ Error: {error_msg[:100]}...")
        
        # 6. Check region-specific information
        print("\n6️⃣ Region information...")
        cursor.execute("SELECT CURRENT_REGION()")
        region = cursor.fetchone()
        print(f"Current region: {region[0] if region else 'Unknown'}")
        
        if region and 'ME_CENTRAL' in region[0]:
            print("\n⚠️  You are in Middle East Central region (GCP_ME_CENTRAL2)")
            print("   Cortex LLM features might have limited availability in this region.")
            print("   Consider using a different region where Cortex is fully supported:")
            print("   - US regions: US_WEST_2, US_EAST_1")
            print("   - Europe: EU_WEST_1, EU_CENTRAL_1")
            print("   - Asia: AP_SOUTHEAST_1")
        
    except Exception as e:
        print(f"\n❌ Diagnostic error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()
    
    print("\n" + "=" * 70)
    print("📊 DIAGNOSIS SUMMARY")
    print("=" * 70)
    print("\n⚠️  Based on the diagnostics:")
    print("1. Your Snowflake account is in GCP_ME_CENTRAL2 region")
    print("2. Cortex LLM features appear to have limited availability")
    print("3. The functions exist but return service errors")
    print("\n💡 Recommendations:")
    print("1. Contact Snowflake support to enable Cortex in your region")
    print("2. Consider using a Snowflake account in a supported region")
    print("3. Check with your account team about Cortex availability")

if __name__ == "__main__":
    diagnose_cortex()