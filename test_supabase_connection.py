#!/usr/bin/env python3
"""Test Supabase connection and Market Oracle integration."""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test imports
try:
    from src.a2a_mcp.common.supabase_client import SupabaseClient
    print("✅ Supabase client imported successfully")
except Exception as e:
    print(f"❌ Error importing Supabase client: {e}")
    exit(1)

async def test_supabase_connection():
    """Test basic Supabase connectivity."""
    print("\n" + "="*50)
    print("Testing Supabase Connection")
    print("="*50 + "\n")
    
    try:
        # Get client
        client = SupabaseClient.get_client()
        print("✅ Connected to Supabase")
        
        # Test 1: Read portfolios
        print("\n📊 Testing Portfolio Access...")
        portfolios = client.table('portfolios').select("*").execute()
        print(f"Found {len(portfolios.data)} portfolios:")
        for p in portfolios.data:
            print(f"  - User: {p['user_id']}, Balance: ${p['cash_balance']:,.2f}")
        
        # Test 2: Read trading signals
        print("\n📈 Testing Trading Signals...")
        signals = client.table('trading_signals').select("*").order('created_at', desc=True).limit(5).execute()
        print(f"Latest {len(signals.data)} signals:")
        for s in signals.data:
            print(f"  - {s['symbol']}: {s['signal_type']} (confidence: {s['confidence_score']})")
        
        # Test 3: Read sentiment data
        print("\n💭 Testing Sentiment Data...")
        sentiment = client.table('sentiment_data').select("*").order('timestamp', desc=True).limit(5).execute()
        print(f"Latest {len(sentiment.data)} sentiment entries:")
        for s in sentiment.data:
            print(f"  - {s['symbol']} ({s['source']}): {s['sentiment_score']}")
        
        # Test 4: Create a test signal
        print("\n✍️ Testing Write Operations...")
        new_signal = client.table('trading_signals').insert({
            'symbol': 'TEST',
            'signal_type': 'buy',
            'confidence_score': 0.99,
            'agent_name': 'test_script',
            'reasoning': 'Testing Supabase integration'
        }).execute()
        
        if new_signal.data:
            print("✅ Successfully created test signal")
            signal_id = new_signal.data[0]['id']
            
            # Clean up test data
            client.table('trading_signals').delete().eq('id', signal_id).execute()
            print("✅ Cleaned up test data")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Supabase connection error: {e}")
        return False

async def test_oracle_prime_supabase():
    """Test Oracle Prime agent with Supabase."""
    print("\n" + "="*50)
    print("Testing Oracle Prime with Supabase")
    print("="*50 + "\n")
    
    try:
        from src.a2a_mcp.agents.market_oracle.oracle_prime_agent_supabase import OraclePrimeAgentSupabase
        
        # Initialize Oracle Prime
        oracle = OraclePrimeAgentSupabase()
        print("✅ Oracle Prime initialized")
        
        # Test loading portfolio context
        await oracle.load_portfolio_context("demo_user")
        print(f"✅ Portfolio loaded: ${oracle.portfolio_context.get('total_value', 0):,.2f}")
        print(f"   Cash: ${oracle.portfolio_context.get('cash_balance', 0):,.2f}")
        print(f"   Positions: {len(oracle.portfolio_context.get('positions', []))}")
        
        # Test analysis with Supabase
        print("\n🤖 Running investment analysis...")
        query = "Should I invest in AAPL?"
        
        async for response in oracle.stream(query, "test_session", "test_task"):
            if response.get('is_task_complete'):
                if response.get('response_type') == 'data':
                    data = response['content']
                    
                    print("\n📊 Analysis Complete!")
                    if 'recommendation' in data:
                        rec = data['recommendation']
                        print(f"Recommendation: {rec.get('investment_recommendation')}")
                        print(f"Confidence: {rec.get('confidence_score')}")
                        print(f"Summary: {rec.get('executive_summary')}")
                    
                    if 'recent_signals' in data:
                        print(f"\nRecent signals from database: {len(data['recent_signals'])}")
                    
                    print("\n✅ Supabase integration working correctly!")
            else:
                print(f"  {response.get('content', '...')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Oracle Prime test error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def create_sample_portfolio_if_needed():
    """Ensure we have a demo portfolio."""
    try:
        client = SupabaseClient.get_client()
        
        # Check if demo portfolio exists
        existing = client.table('portfolios').select("*").eq('user_id', 'demo_user').execute()
        
        if not existing.data:
            print("\n📝 Creating demo portfolio...")
            
            # Create portfolio
            portfolio = client.table('portfolios').insert({
                'user_id': 'demo_user',
                'total_value': 100000.00,
                'cash_balance': 50000.00
            }).execute()
            
            if portfolio.data:
                portfolio_id = portfolio.data[0]['id']
                
                # Add some positions
                positions = [
                    {'portfolio_id': portfolio_id, 'symbol': 'AAPL', 'quantity': 100, 
                     'entry_price': 150.00, 'current_price': 175.00, 'profit_loss': 2500.00},
                    {'portfolio_id': portfolio_id, 'symbol': 'TSLA', 'quantity': 50,
                     'entry_price': 200.00, 'current_price': 180.00, 'profit_loss': -1000.00}
                ]
                
                client.table('positions').insert(positions).execute()
                print("✅ Demo portfolio created with sample positions")
        
    except Exception as e:
        print(f"Error creating demo portfolio: {e}")

async def main():
    """Run all tests."""
    print("\n🚀 Market Oracle Supabase Integration Test\n")
    
    # Check environment
    print("Environment Check:")
    print(f"  SUPABASE_URL: {'✅' if os.getenv('SUPABASE_URL') else '❌'}")
    print(f"  SUPABASE_ANON_KEY: {'✅' if os.getenv('SUPABASE_ANON_KEY') else '❌'}")
    print(f"  SUPABASE_SERVICE_ROLE_KEY: {'✅' if os.getenv('SUPABASE_SERVICE_ROLE_KEY') else '❌'}")
    print(f"  GOOGLE_API_KEY: {'✅' if os.getenv('GOOGLE_API_KEY') else '❌'}")
    
    # Test Supabase connection
    if await test_supabase_connection():
        # Ensure demo portfolio exists
        await create_sample_portfolio_if_needed()
        
        # Test Oracle Prime
        await test_oracle_prime_supabase()
    
    print("\n✅ All tests completed!")
    print("\nNext steps:")
    print("1. Start the MCP server: ./start_market_oracle.sh")
    print("2. Run the full demo: python demo_market_oracle.py")
    print("3. Access Supabase dashboard to monitor data")

if __name__ == "__main__":
    asyncio.run(main())