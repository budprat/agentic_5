#!/usr/bin/env python3
"""Test Stock MCP and BrightData integrations without running all agents."""

import asyncio
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('integration_test.log')
    ]
)

logger = logging.getLogger(__name__)

async def test_stock_mcp_detailed():
    """Detailed test of Stock MCP integration."""
    print("\n" + "="*70)
    print("🤖 STOCK MCP INTEGRATION TEST")
    print("="*70)
    
    try:
        from src.a2a_mcp.common.stock_mcp_client import StockMCPClient
        
        async with StockMCPClient() as client:
            print(f"MCP URL: {client.mcp_url}")
            
            # Test single prediction
            print("\n1️⃣ Single Symbol Prediction Test")
            symbol = "TSLA"
            prediction = await client.get_prediction(symbol)
            
            if 'error' not in prediction:
                print(f"\n✅ Prediction for {symbol}:")
                pred = prediction['prediction']
                print(f"  Direction: {pred['direction']}")
                print(f"  Confidence: {pred['confidence']:.1%}")
                print(f"  Expected Change: {pred['predicted_price_change_percent']:+.2f}%")
                print(f"  Timeframe: {pred['timeframe']}")
                print(f"  Key Factors:")
                for factor in pred.get('factors', [])[:3]:
                    print(f"    - {factor}")
                print(f"  Support Level: ${pred['key_levels']['support']:.2f}")
                print(f"  Resistance Level: ${pred['key_levels']['resistance']:.2f}")
                
                model = prediction.get('model_info', {})
                print(f"\n  Model Info:")
                print(f"    Name: {model.get('name', 'Unknown')}")
                print(f"    Accuracy: {model.get('accuracy_score', 0):.1%}")
            else:
                print(f"❌ Error: {prediction['error']}")
            
            # Test batch predictions
            print("\n2️⃣ Batch Prediction Test")
            symbols = ["AAPL", "NVDA", "GOOGL", "MSFT", "AMZN"]
            print(f"Getting predictions for: {', '.join(symbols)}")
            
            batch_results = await client.get_batch_predictions(symbols)
            
            print("\nBatch Results Summary:")
            print("-" * 50)
            print(f"{'Symbol':<8} {'Direction':<10} {'Confidence':<12} {'Change':<10}")
            print("-" * 50)
            
            for symbol, result in batch_results.items():
                if 'error' not in result:
                    pred = result['prediction']
                    print(f"{symbol:<8} {pred['direction']:<10} "
                          f"{pred['confidence']:<12.1%} "
                          f"{pred['predicted_price_change_percent']:>+9.2f}%")
                else:
                    print(f"{symbol:<8} {'ERROR':<10} {'-':<12} {'-':<10}")
                    
    except Exception as e:
        logger.error(f"Stock MCP test error: {e}")
        import traceback
        traceback.print_exc()

async def test_brightdata_integration():
    """Test BrightData integration with caching."""
    print("\n" + "="*70)
    print("📊 BRIGHTDATA INTEGRATION TEST")
    print("="*70)
    
    try:
        from src.a2a_mcp.agents.market_oracle.sentiment_seeker_agent_brightdata import SentimentSeekerAgentBrightData
        
        agent = SentimentSeekerAgentBrightData()
        
        # Test 1: Direct API call
        print("\n1️⃣ Testing BrightData API Call")
        print("  Note: This will use cached data if available")
        
        symbol = "TSLA"
        reddit_data = await agent.fetch_reddit_data(symbol)
        
        if 'error' in reddit_data:
            print(f"  ⚠️  API returned error or timeout, using fallback data")
            print(f"  Error: {reddit_data['error']}")
        else:
            posts = reddit_data.get('posts', [])
            print(f"  ✅ Retrieved {len(posts)} posts for {symbol}")
            
            if posts:
                print("\n  Sample Posts:")
                for i, post in enumerate(posts[:3], 1):
                    print(f"  {i}. {post.get('title', 'No title')}")
                    print(f"     Upvotes: {post.get('upvotes', 0)}")
                    print(f"     Comments: {post.get('num_comments', 0)}")
                    print(f"     Subreddit: r/{post.get('subreddit', 'unknown')}")
        
        # Test 2: Cache functionality
        print("\n2️⃣ Testing Cache System")
        from src.a2a_mcp.common.brightdata_cache import BrightDataCache
        
        cache = BrightDataCache()
        
        # Try to get cached data
        cached = await cache.get(symbol)
        if cached:
            print(f"  ✅ Found cached data for {symbol}")
            print(f"     Posts in cache: {len(cached.get('posts', []))}")
        else:
            print(f"  ℹ️  No cached data for {symbol}")
        
        # Test 3: Full sentiment analysis
        print("\n3️⃣ Testing Full Sentiment Analysis")
        
        query = f"Analyze Reddit sentiment for {symbol}"
        results = []
        
        async for response in agent.stream(query, "test_session", "test_task"):
            if response.get('is_task_complete'):
                if response.get('response_type') == 'data':
                    results = response['content']
                    break
            else:
                print(f"  ⏳ {response.get('content', '')}")
        
        if results:
            print("\n  ✅ Sentiment Analysis Results:")
            print(f"     Symbol: {results.get('symbol', 'N/A')}")
            print(f"     Sentiment Score: {results.get('sentiment_score', 0):.2f}")
            print(f"     Confidence: {results.get('confidence', 0):.2f}")
            print(f"     Volume: {results.get('volume_score', 'N/A')}")
            print(f"     Recommendation: {results.get('recommendation', 'N/A')}")
            
            if 'ml_predictions' in results:
                ml = results['ml_predictions']
                print(f"\n     ML Predictions:")
                print(f"       Direction: {ml.get('ml_prediction', 'N/A')}")
                print(f"       Confidence: {ml.get('confidence', 0):.2f}")
                print(f"       Expected Move: {ml.get('predicted_move', 'N/A')}")
                
    except Exception as e:
        logger.error(f"BrightData test error: {e}")
        import traceback
        traceback.print_exc()

async def test_supabase_operations():
    """Test Supabase database operations."""
    print("\n" + "="*70)
    print("🗄️  SUPABASE OPERATIONS TEST")
    print("="*70)
    
    try:
        from src.a2a_mcp.common.supabase_client import SupabaseClient
        
        client = SupabaseClient()
        
        # Test 1: Create test data
        print("\n1️⃣ Creating Test Data")
        
        # Create sentiment data
        await client.create_sentiment_data(
            symbol="TEST",
            source="integration_test",
            sentiment_score=0.75,
            volume_score=100
        )
        print("  ✅ Created sentiment data")
        
        # Create trading signal
        await client.create_trading_signal(
            symbol="TEST",
            signal_type="buy",
            confidence_score=0.85,
            agent_name="Integration Test",
            reasoning="Test signal for integration testing"
        )
        print("  ✅ Created trading signal")
        
        # Test 2: Query data
        print("\n2️⃣ Querying Data")
        
        # Get latest signals
        signals = await client.get_latest_signals("TEST", limit=5)
        print(f"  ✅ Found {len(signals)} signals for TEST")
        
        if signals:
            latest = signals[0]
            print(f"     Latest: {latest['signal_type']} "
                  f"(confidence: {latest['confidence_score']:.2f})")
        
        # Get sentiment data
        db = client.get_client()
        sentiment_response = (db.table('sentiment_data')
                            .select("*")
                            .eq('symbol', 'TEST')
                            .order('timestamp', desc=True)
                            .limit(5)
                            .execute())
        
        print(f"  ✅ Found {len(sentiment_response.data)} sentiment records for TEST")
        
        # Test 3: Portfolio operations
        print("\n3️⃣ Testing Portfolio Operations")
        
        # Check if test portfolio exists
        portfolio_response = (db.table('portfolios')
                            .select("*")
                            .eq('user_id', 'test_user')
                            .limit(1)
                            .execute())
        
        if not portfolio_response.data:
            # Create test portfolio
            await client.create_portfolio("test_user", 100000.0, 50000.0)
            print("  ✅ Created test portfolio")
        else:
            print("  ✅ Test portfolio exists")
            portfolio = portfolio_response.data[0]
            print(f"     Total Value: ${portfolio['total_value']:,.2f}")
            print(f"     Cash Balance: ${portfolio['cash_balance']:,.2f}")
            
    except Exception as e:
        logger.error(f"Supabase test error: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run integration tests."""
    print("\n" + "="*70)
    print("🧪 MARKET ORACLE INTEGRATION TESTS")
    print("="*70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test Stock MCP
    await test_stock_mcp_detailed()
    
    # Test BrightData
    await test_brightdata_integration()
    
    # Test Supabase
    await test_supabase_operations()
    
    print("\n" + "="*70)
    print("✅ INTEGRATION TESTS COMPLETE")
    print("="*70)
    print("\nCheck integration_test.log for detailed logs")

if __name__ == "__main__":
    asyncio.run(main())