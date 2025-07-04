#!/usr/bin/env python3
"""
Test the AI_COMPLETE function that was found in SNOWFLAKE.ML schema
"""

import os
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

def test_ai_complete():
    """Test the AI_COMPLETE function with different approaches"""
    
    # Get credentials
    account = os.getenv('SNOWFLAKE_ACCOUNT')
    user = os.getenv('SNOWFLAKE_USER')
    password = os.getenv('SNOWFLAKE_PASSWORD')
    warehouse = os.getenv('SNOWFLAKE_WAREHOUSE')
    
    conn = snowflake.connector.connect(
        account=account,
        user=user,
        password=password,
        role='SYSADMIN',  # Use SYSADMIN with CORTEX_USER granted
        warehouse=warehouse
    )
    
    cursor = conn.cursor()
    
    try:
        print("🧪 Testing AI_COMPLETE Function")
        print("=" * 70)
        
        # Set up environment
        cursor.execute(f"USE WAREHOUSE {warehouse}")
        cursor.execute("USE DATABASE SNOWFLAKE")
        cursor.execute("USE SCHEMA ML")
        
        # 1. Check function signature
        print("\n1️⃣ Checking AI_COMPLETE function signature...")
        cursor.execute("DESC FUNCTION AI_COMPLETE(VARCHAR)")
        desc = cursor.fetchall()
        print("Function signature:")
        for row in desc:
            print(f"  {row}")
        
        # 2. Try different ways to call AI_COMPLETE
        print("\n2️⃣ Testing different AI_COMPLETE call patterns...")
        
        test_patterns = [
            # Pattern 1: Simple prompt
            ("Simple prompt", "SELECT AI_COMPLETE('What is 2+2?') as response"),
            
            # Pattern 2: With model specification
            ("With model", "SELECT AI_COMPLETE('mistral-7b', 'What is 2+2?') as response"),
            
            # Pattern 3: Using SNOWFLAKE.ML prefix
            ("With full path", "SELECT SNOWFLAKE.ML.AI_COMPLETE('What is 2+2?') as response"),
            
            # Pattern 4: With JSON options
            ("With options", """
                SELECT AI_COMPLETE(
                    'What is the capital of France?',
                    {'model': 'mistral-7b', 'temperature': 0.7}
                ) as response
            """),
        ]
        
        for pattern_name, query in test_patterns:
            print(f"\nTrying: {pattern_name}")
            print(f"Query: {query.strip()}")
            try:
                cursor.execute(query)
                result = cursor.fetchone()
                if result and result[0]:
                    print(f"✅ Success! Response: {str(result[0])[:200]}...")
                    
                    # If successful, try more detailed test
                    print("\n3️⃣ Testing with market analysis prompt...")
                    cursor.execute("""
                        SELECT AI_COMPLETE(
                            'Provide a brief analysis of the current AI market trends in 2024.'
                        ) as analysis
                    """)
                    analysis = cursor.fetchone()
                    if analysis and analysis[0]:
                        print("✅ Market analysis successful!")
                        print(f"Response preview: {str(analysis[0])[:300]}...")
                    
                    return True
                else:
                    print("❌ No response returned")
            except Exception as e:
                print(f"❌ Error: {str(e)[:200]}...")
        
        # If we get here, nothing worked
        print("\n❌ Could not successfully call AI_COMPLETE function")
        print("\nTrying to get more information about available functions...")
        
        # List all functions in ML schema
        cursor.execute("SHOW FUNCTIONS IN SCHEMA SNOWFLAKE.ML")
        functions = cursor.fetchall()
        print("\nAll functions in SNOWFLAKE.ML:")
        for func in functions:
            if 'AI' in func[1] or 'COMPLETE' in func[1] or 'LLM' in func[1]:
                print(f"  - {func[1]} ({func[8]})")  # Function name and description
        
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    if test_ai_complete():
        print("\n✅ AI_COMPLETE function is working!")
        print("\n💡 Next steps:")
        print("1. Update your code to use AI_COMPLETE instead of CORTEX.COMPLETE")
        print("2. Check the function signature for proper parameter format")
        print("3. Test with different prompts and options")
    else:
        print("\n❌ AI_COMPLETE function is not working properly")
        print("\n💡 Recommendations:")
        print("1. Contact Snowflake support to enable Cortex LLM features")
        print("2. Check if your account has the necessary privileges")
        print("3. Verify your Snowflake edition supports AI features")