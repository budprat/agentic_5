#!/usr/bin/env python3
"""Detailed testing of Market Oracle with real market data."""

import asyncio
import logging
import sys
import json
from datetime import datetime
import aiohttp

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('real_data_test.log')
    ]
)

logger = logging.getLogger(__name__)

# Real stock symbols for testing
REAL_STOCKS = {
    "TSLA": "Tesla Inc.",
    "AAPL": "Apple Inc.",
    "NVDA": "NVIDIA Corporation",
    "MSFT": "Microsoft Corporation",
    "GOOGL": "Alphabet Inc.",
    "AMZN": "Amazon.com Inc.",
    "META": "Meta Platforms Inc.",
    "AMD": "Advanced Micro Devices"
}

async def test_stock_mcp_real_data():
    """Test Stock MCP with real stock symbols."""
    print("\n" + "="*80)
    print("🔮 TESTING STOCK PREDICTIONS MCP WITH REAL DATA")
    print("="*80)
    
    from src.a2a_mcp.common.stock_mcp_client import StockMCPClient
    
    async with StockMCPClient() as client:
        print(f"\n📊 Testing {len(REAL_STOCKS)} Real Stocks")
        print("-" * 80)
        
        all_predictions = {}
        
        for symbol, name in REAL_STOCKS.items():
            print(f"\n🎯 {symbol} - {name}")
            
            try:
                # Get prediction
                prediction = await client.get_prediction(symbol)
                all_predictions[symbol] = prediction
                
                if 'error' not in prediction:
                    pred = prediction['prediction']
                    model = prediction.get('model_info', {})
                    
                    # Display detailed prediction
                    print(f"  📈 Prediction Details:")
                    print(f"     Direction: {pred['direction'].upper()}")
                    print(f"     Confidence: {pred['confidence']:.1%}")
                    print(f"     Expected Change: {pred['predicted_price_change_percent']:+.2f}%")
                    print(f"     Timeframe: {pred['timeframe']}")
                    
                    # Support/Resistance levels
                    print(f"\n  📊 Key Levels:")
                    print(f"     Support: ${pred['key_levels']['support']:.2f}")
                    print(f"     Resistance: ${pred['key_levels']['resistance']:.2f}")
                    print(f"     Range: ${pred['key_levels']['resistance'] - pred['key_levels']['support']:.2f}")
                    
                    # Factors
                    print(f"\n  🔍 Analysis Factors:")
                    for i, factor in enumerate(pred.get('factors', []), 1):
                        print(f"     {i}. {factor}")
                    
                    # Model info
                    print(f"\n  🤖 Model Info:")
                    print(f"     Model: {model.get('name', 'Unknown')}")
                    print(f"     Accuracy: {model.get('accuracy_score', 0):.1%}")
                    print(f"     Last Updated: {model.get('last_updated', 'N/A')}")
                    
                    # Trading signal
                    signal_strength = "Strong" if pred['confidence'] > 0.8 else "Moderate" if pred['confidence'] > 0.6 else "Weak"
                    print(f"\n  💡 Trading Signal: {signal_strength} {pred['direction'].upper()}")
                    
                else:
                    print(f"  ❌ Error: {prediction['error']}")
                    
            except Exception as e:
                logger.error(f"Error getting prediction for {symbol}: {e}")
                print(f"  ❌ Exception: {e}")
            
            # Small delay
            await asyncio.sleep(0.5)
        
        # Summary statistics
        print("\n" + "="*80)
        print("📊 PREDICTION SUMMARY")
        print("="*80)
        
        bullish = sum(1 for p in all_predictions.values() 
                     if 'error' not in p and p['prediction']['direction'] == 'bullish')
        bearish = sum(1 for p in all_predictions.values() 
                     if 'error' not in p and p['prediction']['direction'] == 'bearish')
        neutral = sum(1 for p in all_predictions.values() 
                     if 'error' not in p and p['prediction']['direction'] == 'neutral')
        
        print(f"Bullish: {bullish} stocks")
        print(f"Bearish: {bearish} stocks")
        print(f"Neutral: {neutral} stocks")
        
        # High confidence predictions
        high_confidence = [(s, p) for s, p in all_predictions.items() 
                          if 'error' not in p and p['prediction']['confidence'] > 0.75]
        
        if high_confidence:
            print(f"\n🎯 HIGH CONFIDENCE PREDICTIONS (>75%):")
            for symbol, pred in sorted(high_confidence, 
                                      key=lambda x: x[1]['prediction']['confidence'], 
                                      reverse=True):
                p = pred['prediction']
                print(f"  {symbol}: {p['direction']} ({p['confidence']:.1%}) - "
                      f"Expected: {p['predicted_price_change_percent']:+.2f}%")

async def test_brightdata_real_symbols():
    """Test BrightData with real stock symbols."""
    print("\n" + "="*80)
    print("📰 TESTING BRIGHTDATA REDDIT SENTIMENT WITH REAL STOCKS")
    print("="*80)
    
    from src.a2a_mcp.agents.market_oracle.sentiment_seeker_agent_brightdata import SentimentSeekerAgentBrightData
    
    agent = SentimentSeekerAgentBrightData()
    
    # Test popular stocks that likely have Reddit discussions
    test_symbols = ["TSLA", "NVDA", "GME", "AMC", "AAPL"]
    
    for symbol in test_symbols:
        print(f"\n🔍 Testing Reddit Sentiment for {symbol}")
        print("-" * 60)
        
        try:
            # Check cache first
            from src.a2a_mcp.common.brightdata_cache import BrightDataCache
            cache = BrightDataCache()
            cached = await cache.get(symbol)
            
            if cached:
                print(f"  ✅ Found cached data for {symbol}")
                print(f"     Posts: {len(cached.get('posts', []))}")
            else:
                print(f"  ℹ️  No cache, fetching from BrightData...")
            
            # Stream sentiment analysis
            query = f"Analyze Reddit sentiment for {symbol}"
            result = None
            
            async for response in agent.stream(query, f"test_{symbol}", f"task_{symbol}"):
                if response.get('is_task_complete'):
                    if response.get('response_type') == 'data':
                        result = response['content']
                        break
                else:
                    print(f"  ⏳ {response.get('content', '')}")
            
            if result:
                print(f"\n  📊 Sentiment Analysis Results:")
                print(f"     Symbol: {result.get('symbol', 'N/A')}")
                print(f"     Sentiment Score: {result.get('sentiment_score', 0):.2f} (-1 to +1)")
                print(f"     Confidence: {result.get('confidence', 0):.1%}")
                print(f"     Volume: {result.get('volume_score', 'N/A')}")
                print(f"     Posts Analyzed: {result.get('posts_analyzed', 0)}")
                
                # Sentiment breakdown
                if 'sentiment_breakdown' in result:
                    sb = result['sentiment_breakdown']
                    print(f"\n  📈 Sentiment Distribution:")
                    print(f"     Bullish: {sb.get('bullish_percentage', 0):.1f}%")
                    print(f"     Bearish: {sb.get('bearish_percentage', 0):.1f}%")
                    print(f"     Neutral: {sb.get('neutral_percentage', 0):.1f}%")
                
                # Key themes
                if 'key_themes' in result:
                    print(f"\n  🔑 Key Themes:")
                    for theme in result['key_themes'][:5]:
                        print(f"     - {theme}")
                
                # ML predictions integration
                if 'ml_predictions' in result:
                    ml = result['ml_predictions']
                    print(f"\n  🤖 ML Predictions:")
                    print(f"     Direction: {ml.get('ml_prediction', 'N/A')}")
                    print(f"     Confidence: {ml.get('confidence', 0):.1%}")
                    print(f"     Expected Move: {ml.get('predicted_move', 'N/A')}")
                
                # Risk flags
                if 'risk_flags' in result and result['risk_flags']:
                    print(f"\n  ⚠️  Risk Flags:")
                    for flag in result['risk_flags']:
                        print(f"     - {flag}")
                
                print(f"\n  💡 Recommendation: {result.get('recommendation', 'N/A').upper()}")
                print(f"  📝 Summary: {result.get('analysis_summary', 'N/A')}")
                
        except Exception as e:
            logger.error(f"Error testing {symbol}: {e}")
            print(f"  ❌ Error: {e}")
        
        # Delay between requests
        await asyncio.sleep(2)

async def test_supabase_real_data():
    """Test Supabase with real market data."""
    print("\n" + "="*80)
    print("🗄️  TESTING SUPABASE WITH REAL MARKET DATA")
    print("="*80)
    
    from src.a2a_mcp.common.supabase_client import SupabaseClient
    client = SupabaseClient()
    
    # Test creating real market signals
    print("\n1️⃣ Creating Real Trading Signals")
    
    test_signals = [
        {"symbol": "TSLA", "signal_type": "buy", "confidence": 0.85, "reasoning": "Strong technical breakout + positive sentiment"},
        {"symbol": "NVDA", "signal_type": "buy", "confidence": 0.78, "reasoning": "AI sector momentum + earnings beat"},
        {"symbol": "AAPL", "signal_type": "hold", "confidence": 0.65, "reasoning": "Mixed signals, waiting for clarity"},
        {"symbol": "META", "signal_type": "sell", "confidence": 0.72, "reasoning": "Regulatory concerns + valuation stretched"}
    ]
    
    for signal in test_signals:
        try:
            await client.create_trading_signal(
                symbol=signal['symbol'],
                signal_type=signal['signal_type'],
                confidence_score=signal['confidence'],
                agent_name="Market Oracle Test",
                reasoning=signal['reasoning']
            )
            print(f"  ✅ Created {signal['signal_type']} signal for {signal['symbol']} "
                  f"(confidence: {signal['confidence']:.0%})")
        except Exception as e:
            logger.error(f"Error creating signal: {e}")
    
    # Query latest signals
    print("\n2️⃣ Querying Latest Signals by Symbol")
    
    for symbol in ["TSLA", "NVDA", "AAPL"]:
        signals = await client.get_latest_signals(symbol, limit=5)
        print(f"\n  📊 {symbol} - Found {len(signals)} signals:")
        
        for sig in signals[:3]:
            print(f"     {sig['signal_type'].upper()} - Confidence: {sig['confidence_score']:.0%} "
                  f"- By: {sig['agent_name']} "
                  f"- Time: {sig['created_at']}")
    
    # Test portfolio operations
    print("\n3️⃣ Testing Portfolio Management")
    
    # Get or create test portfolio
    db = client.get_client()
    portfolio_response = (db.table('portfolios')
                        .select("*")
                        .eq('user_id', 'market_oracle_test')
                        .limit(1)
                        .execute())
    
    if portfolio_response.data:
        portfolio = portfolio_response.data[0]
        print(f"  ✅ Found existing portfolio:")
    else:
        portfolio_data = await client.create_portfolio('market_oracle_test', 1000000.0, 500000.0)
        portfolio = portfolio_data
        print(f"  ✅ Created new portfolio:")
    
    print(f"     ID: {portfolio['id']}")
    print(f"     Total Value: ${portfolio['total_value']:,.2f}")
    print(f"     Cash Balance: ${portfolio['cash_balance']:,.2f}")
    
    # Create test positions
    print("\n4️⃣ Creating Test Positions")
    
    test_positions = [
        {"symbol": "TSLA", "quantity": 100, "entry_price": 180.50},
        {"symbol": "NVDA", "quantity": 50, "entry_price": 485.25},
        {"symbol": "AAPL", "quantity": 200, "entry_price": 195.75}
    ]
    
    for pos in test_positions:
        try:
            await client.create_position(
                portfolio_id=portfolio['id'],
                symbol=pos['symbol'],
                quantity=pos['quantity'],
                entry_price=pos['entry_price']
            )
            position_value = pos['quantity'] * pos['entry_price']
            print(f"  ✅ Created position: {pos['quantity']} shares of {pos['symbol']} "
                  f"@ ${pos['entry_price']:.2f} = ${position_value:,.2f}")
        except Exception as e:
            if "duplicate key" in str(e):
                print(f"  ℹ️  Position for {pos['symbol']} already exists")
            else:
                logger.error(f"Error creating position: {e}")
    
    # Get all positions
    positions = await client.get_positions(portfolio['id'])
    print(f"\n  📊 Portfolio Positions: {len(positions)} total")
    
    total_position_value = 0
    for pos in positions:
        value = pos['quantity'] * pos['current_price']
        total_position_value += value
        pnl = (pos['current_price'] - pos['entry_price']) * pos['quantity']
        pnl_pct = ((pos['current_price'] - pos['entry_price']) / pos['entry_price']) * 100
        
        print(f"     {pos['symbol']}: {pos['quantity']} shares @ ${pos['current_price']:.2f} "
              f"= ${value:,.2f} (P&L: ${pnl:+,.2f} / {pnl_pct:+.1f}%)")
    
    print(f"\n  💰 Portfolio Summary:")
    print(f"     Total Positions Value: ${total_position_value:,.2f}")
    print(f"     Cash Balance: ${portfolio['cash_balance']:,.2f}")
    print(f"     Total Portfolio Value: ${total_position_value + portfolio['cash_balance']:,.2f}")

async def test_full_workflow():
    """Test complete workflow with real market scenario."""
    print("\n" + "="*80)
    print("🔄 TESTING COMPLETE MARKET ORACLE WORKFLOW")
    print("="*80)
    
    # Simulate a real investment decision workflow
    test_symbol = "TSLA"
    print(f"\n📊 Analyzing {test_symbol} for Investment Decision")
    print("-" * 80)
    
    # Step 1: Get ML Predictions
    print("\n1️⃣ Fetching ML Predictions...")
    from src.a2a_mcp.common.stock_mcp_client import StockMCPClient
    
    async with StockMCPClient() as stock_client:
        prediction = await stock_client.get_prediction(test_symbol)
        if 'error' not in prediction:
            pred = prediction['prediction']
            print(f"   Direction: {pred['direction']}")
            print(f"   Confidence: {pred['confidence']:.1%}")
            print(f"   Expected Move: {pred['predicted_price_change_percent']:+.2f}%")
    
    # Step 2: Get Reddit Sentiment
    print("\n2️⃣ Analyzing Reddit Sentiment...")
    from src.a2a_mcp.agents.market_oracle.sentiment_seeker_agent_brightdata import SentimentSeekerAgentBrightData
    
    sentiment_agent = SentimentSeekerAgentBrightData()
    sentiment_result = None
    
    async for response in sentiment_agent.stream(
        f"Analyze Reddit sentiment for {test_symbol}", 
        "workflow_test", 
        "workflow_task"
    ):
        if response.get('is_task_complete') and response.get('response_type') == 'data':
            sentiment_result = response['content']
            break
    
    if sentiment_result:
        print(f"   Sentiment Score: {sentiment_result.get('sentiment_score', 0):.2f}")
        print(f"   Volume: {sentiment_result.get('volume_score', 'N/A')}")
        print(f"   Recommendation: {sentiment_result.get('recommendation', 'N/A')}")
    
    # Step 3: Create comprehensive signal
    print("\n3️⃣ Generating Investment Signal...")
    
    # Combine ML and sentiment
    ml_bullish = pred['direction'] == 'bullish' if 'error' not in prediction else False
    sentiment_bullish = sentiment_result.get('sentiment_score', 0) > 0.3 if sentiment_result else False
    
    combined_confidence = (
        (pred['confidence'] if 'error' not in prediction else 0.5) * 0.6 +
        (sentiment_result.get('confidence', 0.5) if sentiment_result else 0.5) * 0.4
    )
    
    if ml_bullish and sentiment_bullish:
        signal_type = "buy"
        reasoning = "Both ML predictions and sentiment analysis are bullish"
    elif not ml_bullish and not sentiment_bullish:
        signal_type = "sell"
        reasoning = "Both ML predictions and sentiment analysis are bearish"
    else:
        signal_type = "hold"
        reasoning = "Mixed signals between ML predictions and sentiment"
    
    print(f"   Signal Type: {signal_type.upper()}")
    print(f"   Combined Confidence: {combined_confidence:.1%}")
    print(f"   Reasoning: {reasoning}")
    
    # Step 4: Save to Supabase
    print("\n4️⃣ Saving Analysis to Database...")
    from src.a2a_mcp.common.supabase_client import SupabaseClient
    
    client = SupabaseClient()
    
    # Save trading signal
    await client.create_trading_signal(
        symbol=test_symbol,
        signal_type=signal_type,
        confidence_score=combined_confidence,
        agent_name="Market Oracle Workflow",
        reasoning=reasoning
    )
    print("   ✅ Trading signal saved")
    
    # Save research
    await client.create_research(
        symbol=test_symbol,
        thesis_summary=f"{reasoning}. ML predicts {pred['predicted_price_change_percent']:+.2f}% move.",
        target_price=100.0 * (1 + pred['predicted_price_change_percent'] / 100),
        confidence_level='high' if combined_confidence > 0.7 else 'medium',
        fundamental_score=0.75,  # Placeholder
        technical_score=pred['confidence'] if 'error' not in prediction else 0.5,
        sentiment_score=sentiment_result.get('sentiment_score', 0) if sentiment_result else 0
    )
    print("   ✅ Investment research saved")
    
    print("\n✅ Complete workflow executed successfully!")

async def main():
    """Run all real data tests."""
    print("\n" + "="*80)
    print("🚀 MARKET ORACLE REAL DATA TESTING SUITE")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test 1: Stock MCP with real symbols
        await test_stock_mcp_real_data()
        
        # Test 2: BrightData with real symbols
        await test_brightdata_real_symbols()
        
        # Test 3: Supabase with real data
        await test_supabase_real_data()
        
        # Test 4: Complete workflow
        await test_full_workflow()
        
    except Exception as e:
        logger.error(f"Test suite error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("✅ REAL DATA TESTING COMPLETE")
    print("="*80)
    print("\nCheck real_data_test.log for detailed logs")

if __name__ == "__main__":
    asyncio.run(main())