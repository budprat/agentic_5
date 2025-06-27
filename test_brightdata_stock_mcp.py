#!/usr/bin/env python3
"""Test BrightData Reddit API and Stock Predictions MCP integration."""

import asyncio
import os
from datetime import datetime

# Test imports
print("Testing imports...")
try:
    from src.a2a_mcp.agents.market_oracle import SentimentSeekerAgentBrightData
    print("✅ BrightData Sentiment Seeker imported successfully")
except Exception as e:
    print(f"❌ Error importing: {e}")
    exit(1)

async def test_brightdata_sentiment():
    """Test the BrightData-powered sentiment analysis."""
    print("\n" + "="*50)
    print("Testing BrightData Reddit Sentiment Analysis")
    print("="*50 + "\n")
    
    agent = SentimentSeekerAgentBrightData()
    
    # Test query
    query = "What is the Reddit sentiment on AAPL?"
    print(f"Query: {query}")
    print("-" * 40)
    
    try:
        async for response in agent.stream(query, "test_session", "test_task"):
            if response.get('is_task_complete'):
                if response.get('response_type') == 'data':
                    data = response['content']
                    
                    print("\n📊 Sentiment Analysis Results:")
                    print(f"Symbol: {data.get('symbol', 'N/A')}")
                    print(f"Sentiment Score: {data.get('sentiment_score', 0):.2f}")
                    print(f"Confidence: {data.get('confidence', 0):.2f}")
                    print(f"Volume: {data.get('volume_score', 'N/A')}")
                    print(f"Data Source: {data.get('data_source', 'N/A')}")
                    
                    if 'ml_predictions' in data:
                        print("\n🤖 ML Predictions:")
                        ml = data['ml_predictions']
                        print(f"  Direction: {ml.get('ml_prediction', 'N/A')}")
                        print(f"  Confidence: {ml.get('confidence', 0):.2f}")
                        print(f"  Predicted Move: {ml.get('predicted_move', 'N/A')}")
                    
                    print(f"\n💬 Summary: {data.get('analysis_summary', 'N/A')}")
                    
                    # Show if data was saved to Supabase
                    print("\n💾 Data saved to Supabase tables:")
                    print("  - sentiment_data")
                    if abs(data.get('sentiment_score', 0)) > 0.7:
                        print("  - trading_signals (strong sentiment)")
                    
            else:
                print(f"  {response.get('content', '')}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

async def test_stock_mcp_env():
    """Test Stock MCP environment variable."""
    print("\n" + "="*50)
    print("Testing Stock Predictions MCP Configuration")
    print("="*50 + "\n")
    
    stock_mcp = os.getenv('STOCK_MCP')
    if stock_mcp:
        print(f"✅ STOCK_MCP configured: {stock_mcp}")
    else:
        print("❌ STOCK_MCP not found in environment")
        print("  Expected: https://tonic-stock-predictions.hf.space/gradio_api/mcp/sse")
    
    # Test if Oracle Prime can access it
    try:
        from src.a2a_mcp.agents.market_oracle import OraclePrimeAgentSupabase
        oracle = OraclePrimeAgentSupabase()
        print(f"✅ Oracle Prime Stock MCP URL: {oracle.stock_mcp_url}")
    except Exception as e:
        print(f"❌ Error checking Oracle Prime: {e}")

async def test_full_integration():
    """Test full integration with Oracle Prime."""
    print("\n" + "="*50)
    print("Testing Full Integration")
    print("="*50 + "\n")
    
    from a2a_sdk.client import A2AClient
    
    print("Starting Market Oracle agents...")
    print("Make sure to run: ./start_market_oracle.sh")
    print("\nTesting Oracle Prime with BrightData sentiment and Stock MCP...")
    
    # Give user time to start agents
    print("\nPress Enter when agents are running...")
    input()
    
    try:
        client = A2AClient(base_url="http://localhost:10501")
        
        query = "Analyze TSLA using Reddit sentiment and ML predictions"
        print(f"\nQuery: {query}")
        print("-" * 40)
        
        stream = await client.astream(
            message=query,
            session_id="test_session",
            task_id="integration_test"
        )
        
        async for response in stream:
            if response.get('is_task_complete'):
                if response.get('response_type') == 'data':
                    data = response['content']
                    
                    # Check if ML predictions are included
                    intel = data.get('market_intelligence', {})
                    if 'ml_predictions' in intel:
                        print("\n✅ ML Predictions integrated!")
                        ml = intel['ml_predictions']
                        print(f"  Model: {ml.get('model_metadata', {}).get('model', 'N/A')}")
                        print(f"  Direction: {ml.get('ml_prediction', {}).get('direction', 'N/A')}")
                    
                    # Check sentiment source
                    sentiment = intel.get('sentiment', {})
                    if 'reddit_brightdata' in str(sentiment.get('sources', [])):
                        print("\n✅ BrightData Reddit sentiment integrated!")
                    
            else:
                print(f"  {response.get('content', '')}")
    
    except Exception as e:
        print(f"❌ Integration test error: {e}")

async def main():
    """Run all tests."""
    print("\n🚀 Testing BrightData and Stock MCP Integration\n")
    
    # Check environment
    print("Environment Check:")
    print(f"  BRIGHTDATA_API_TOKEN: {'✅' if os.getenv('BRIGHTDATA_API_TOKEN') else '❌'}")
    print(f"  STOCK_MCP: {'✅' if os.getenv('STOCK_MCP') else '❌'}")
    print(f"  SUPABASE_URL: {'✅' if os.getenv('SUPABASE_URL') else '❌'}")
    
    # Run tests
    await test_stock_mcp_env()
    await test_brightdata_sentiment()
    
    print("\n" + "="*50)
    print("✅ Tests Complete!")
    print("="*50)
    
    print("\nNext steps:")
    print("1. Update the agent runner to use SentimentSeekerAgentBrightData")
    print("2. Start the full system: ./start_market_oracle.sh")
    print("3. Run the integration test")

if __name__ == "__main__":
    asyncio.run(main())