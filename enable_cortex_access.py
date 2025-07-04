#!/usr/bin/env python3
"""
Enable Snowflake Cortex access by granting the CORTEX_USER database role.
Based on: https://medium.com/snowflake/snowflake-cortex-function-complete-guide-1-4b0a050517c0
"""

import os
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

def enable_cortex_access():
    """Grant CORTEX_USER database role to enable Cortex functions."""
    
    # Get credentials
    account = os.getenv('SNOWFLAKE_ACCOUNT')
    user = os.getenv('SNOWFLAKE_USER')
    password = os.getenv('SNOWFLAKE_PASSWORD')
    role = os.getenv('SNOWFLAKE_ROLE', 'ACCOUNTADMIN')
    warehouse = os.getenv('SNOWFLAKE_WAREHOUSE')
    
    if not all([account, user, password]):
        raise ValueError("Missing required Snowflake credentials in .env file")
    
    # Connect to Snowflake
    conn = snowflake.connector.connect(
        account=account,
        user=user,
        password=password,
        role=role,
        warehouse=warehouse
    )
    
    cursor = conn.cursor()
    
    try:
        print("Enabling Cortex access...")
        
        # Step 1: Switch to ACCOUNTADMIN role
        cursor.execute("USE ROLE ACCOUNTADMIN")
        print("✓ Using ACCOUNTADMIN role")
        
        # Step 2: Check if CORTEX_USER database role exists
        cursor.execute("SHOW DATABASE ROLES IN DATABASE SNOWFLAKE")
        db_roles = cursor.fetchall()
        cortex_role_exists = any('CORTEX_USER' in str(row) for row in db_roles)
        
        if not cortex_role_exists:
            print("⚠️  CORTEX_USER database role not found. This might indicate:")
            print("   - Cortex is not available in your Snowflake region")
            print("   - Your Snowflake account doesn't have Cortex enabled")
            return False
        
        print("✓ CORTEX_USER database role found")
        
        # Step 3: Grant CORTEX_USER to the main role
        target_role = os.getenv('SNOWFLAKE_CORTEX_ROLE', 'SYSADMIN')
        cursor.execute(f"GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE {target_role}")
        print(f"✓ Granted CORTEX_USER database role to {target_role}")
        
        # Step 4: Verify the grant
        cursor.execute(f"USE ROLE {target_role}")
        cursor.execute("SHOW DATABASE ROLES IN DATABASE SNOWFLAKE")
        roles_after = cursor.fetchall()
        
        if any('CORTEX_USER' in str(row) for row in roles_after):
            print(f"✓ Successfully verified CORTEX_USER access for role {target_role}")
            
            # Step 5: Test Cortex availability
            print("\nTesting Cortex function availability...")
            cursor.execute("USE DATABASE SNOWFLAKE")
            cursor.execute("USE SCHEMA CORTEX")
            cursor.execute(f"USE WAREHOUSE {warehouse}")  # Ensure warehouse is set
            
            # Try to list available functions
            cursor.execute("SHOW FUNCTIONS LIKE 'COMPLETE'")
            functions = cursor.fetchall()
            
            if functions:
                print("✓ Cortex COMPLETE function is available")
                print("\nAvailable Cortex models:")
                # Test which models are available
                test_models = ['llama3.1-8b', 'llama3.1-70b', 'llama3.1-405b', 
                             'mistral-7b', 'mixtral-8x7b', 'gemma-7b']
                
                for model in test_models:
                    try:
                        cursor.execute(f"""
                            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                                '{model}', 
                                'Hello'
                            ) as response
                        """)
                        result = cursor.fetchone()
                        if result:
                            print(f"  ✓ {model} - Available")
                    except Exception as e:
                        if "not available" in str(e).lower():
                            print(f"  ✗ {model} - Not available in this region")
                        else:
                            print(f"  ? {model} - Error: {str(e)[:50]}...")
            else:
                print("⚠️  Cortex functions not found. They might not be available in your region.")
                
        else:
            print("⚠️  Failed to verify CORTEX_USER access")
            return False
            
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def check_regional_availability():
    """Check which Cortex functions are available in the current region."""
    print("\nChecking regional availability of Cortex functions...")
    
    # Get credentials
    account = os.getenv('SNOWFLAKE_ACCOUNT')
    user = os.getenv('SNOWFLAKE_USER')
    password = os.getenv('SNOWFLAKE_PASSWORD')
    role = os.getenv('SNOWFLAKE_CORTEX_ROLE', 'SYSADMIN')
    warehouse = os.getenv('SNOWFLAKE_WAREHOUSE')
    
    conn = snowflake.connector.connect(
        account=account,
        user=user,
        password=password,
        role=role,
        warehouse=warehouse
    )
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("USE DATABASE SNOWFLAKE")
        cursor.execute("USE SCHEMA CORTEX")
        cursor.execute(f"USE WAREHOUSE {warehouse}")  # Ensure warehouse is set
        
        # Check LLM functions
        llm_functions = ['COMPLETE', 'EXTRACT_ANSWER', 'SENTIMENT', 'SUMMARIZE', 'TRANSLATE']
        print("\nLLM Functions:")
        for func in llm_functions:
            try:
                cursor.execute(f"SHOW FUNCTIONS LIKE '{func}'")
                if cursor.fetchall():
                    print(f"  ✓ {func} - Available")
                else:
                    print(f"  ✗ {func} - Not available")
            except:
                print(f"  ✗ {func} - Not available")
        
        # Check ML functions
        ml_functions = ['ANOMALY_DETECTION', 'CONTRIBUTION_EXPLORER', 'FORECASTING', 
                       'TOP_INSIGHTS', 'CLASSIFICATION']
        print("\nML Functions:")
        for func in ml_functions:
            try:
                cursor.execute(f"SHOW FUNCTIONS LIKE '{func}'")
                if cursor.fetchall():
                    print(f"  ✓ {func} - Available")
                else:
                    print(f"  ✗ {func} - Not available")
            except:
                print(f"  ✗ {func} - Not available")
                
    except Exception as e:
        print(f"Error checking availability: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Snowflake Cortex Setup Script")
    print("=" * 50)
    
    if enable_cortex_access():
        print("\n✅ Cortex access has been enabled successfully!")
        check_regional_availability()
        print("\nNext steps:")
        print("1. Update your Snowflake role in .env to use CORTEX_USER permissions")
        print("2. Run test_cortex_simple.py to verify everything works")
    else:
        print("\n❌ Failed to enable Cortex access")
        print("\nPossible reasons:")
        print("1. Cortex might not be available in your Snowflake region")
        print("2. Your account might not have Cortex features enabled")
        print("3. You might need to contact Snowflake support to enable Cortex")