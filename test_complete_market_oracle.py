#!/usr/bin/env python3
"""Complete Market Oracle System Test with all enhancements."""

import asyncio
import logging
import sys
import json
from datetime import datetime
import subprocess
import time
import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('market_oracle_test.log')
    ]
)

logger = logging.getLogger(__name__)

# Agent configurations
AGENTS = {
    "Oracle Prime": {"port": 10501, "url": "http://localhost:10501/v1/agent/invoke"},
    "Fundamental Analyst": {"port": 10502, "url": "http://localhost:10502/v1/agent/invoke"},
    "Sentiment Seeker": {"port": 10503, "url": "http://localhost:10503/v1/agent/invoke"},
    "Technical Prophet": {"port": 10504, "url": "http://localhost:10504/v1/agent/invoke"},
    "Risk Guardian": {"port": 10505, "url": "http://localhost:10505/v1/agent/invoke"},
    "Trend Correlator": {"port": 10506, "url": "http://localhost:10506/v1/agent/invoke"},
    "Report Synthesizer": {"port": 10507, "url": "http://localhost:10507/v1/agent/invoke"},
    "Audio Briefer": {"port": 10508, "url": "http://localhost:10508/v1/agent/invoke"}
}

async def check_agent_health(agent_name: str, url: str) -> bool:
    """Check if an agent is healthy."""
    try:
        async with aiohttp.ClientSession() as session:
            # Try to get agent info
            info_url = url.replace('/invoke', '/info')
            async with session.get(info_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    logger.info(f"✅ {agent_name} is healthy")
                    return True
    except Exception as e:
        logger.error(f"❌ {agent_name} health check failed: {e}")
    return False

async def test_individual_agent(agent_name: str, url: str, query: str):
    """Test an individual agent."""
    print(f"\n{'='*70}")
    print(f"Testing {agent_name}")
    print('='*70)
    
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "query": query,
                "session_id": f"test_{agent_name.lower().replace(' ', '_')}"
            }
            
            logger.info(f"Sending query to {agent_name}: {query}")
            
            async with session.post(
                url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                
                if response.status == 200:
                    # Handle streaming response
                    async for line in response.content:
                        if line:
                            try:
                                line_str = line.decode('utf-8').strip()
                                if line_str.startswith('data: '):
                                    data = json.loads(line_str[6:])
                                    
                                    if data.get('is_task_complete'):
                                        print(f"\n✅ {agent_name} Response:")
                                        if data.get('response_type') == 'data':
                                            print(json.dumps(data['content'], indent=2))
                                        else:
                                            print(data.get('content', 'No content'))
                                        return True
                                    else:
                                        print(f"  ⏳ {data.get('content', '')}")
                                        
                            except json.JSONDecodeError:
                                continue
                else:
                    logger.error(f"Error from {agent_name}: {response.status}")
                    text = await response.text()
                    logger.error(f"Response: {text}")
                    
    except Exception as e:
        logger.error(f"Error testing {agent_name}: {e}")
        import traceback
        traceback.print_exc()
    
    return False

async def test_stock_mcp_integration():
    """Test Stock MCP integration."""
    print("\n" + "="*70)
    print("Testing Stock MCP Integration")
    print("="*70)
    
    try:
        from src.a2a_mcp.common.stock_mcp_client import StockMCPClient
        
        async with StockMCPClient() as client:
            # Test connection
            connected = await client.connect()
            print(f"Stock MCP Connection: {'✅ Connected' if connected else '❌ Failed'}")
            
            # Test predictions for multiple symbols
            symbols = ["AAPL", "TSLA", "NVDA"]
            for symbol in symbols:
                print(f"\nGetting prediction for {symbol}...")
                prediction = await client.get_prediction(symbol)
                
                if 'error' not in prediction:
                    pred_data = prediction['prediction']
                    print(f"  Direction: {pred_data['direction']}")
                    print(f"  Confidence: {pred_data['confidence']:.2%}")
                    print(f"  Expected Change: {pred_data['predicted_price_change_percent']:+.2f}%")
                    print(f"  Support: ${pred_data['key_levels']['support']:.2f}")
                    print(f"  Resistance: ${pred_data['key_levels']['resistance']:.2f}")
                else:
                    print(f"  ❌ Error: {prediction['error']}")
                    
    except Exception as e:
        logger.error(f"Stock MCP test error: {e}")

async def test_brightdata_cache():
    """Test BrightData caching."""
    print("\n" + "="*70)
    print("Testing BrightData Cache")
    print("="*70)
    
    try:
        from src.a2a_mcp.common.brightdata_cache import BrightDataCache, BrightDataParser
        
        cache = BrightDataCache()
        parser = BrightDataParser()
        
        # Test cache operations
        test_data = {
            "posts": [
                {
                    "title": "Test post about TSLA",
                    "upvotes": 100,
                    "num_comments": 50,
                    "subreddit": "wallstreetbets"
                }
            ]
        }
        
        # Save to cache
        await cache.set("TSLA", test_data)
        print("✅ Data cached for TSLA")
        
        # Retrieve from cache
        cached = await cache.get("TSLA")
        if cached:
            print("✅ Cache hit for TSLA")
            print(f"   Posts: {len(cached.get('posts', []))}")
        
        # Test parser
        raw_data = {
            "data": [
                {
                    "title": "TSLA to the moon!",
                    "score": 1500,
                    "num_comments": 200,
                    "subreddit": "stocks",
                    "author": "test_user",
                    "created_utc": "2024-01-01T00:00:00Z"
                }
            ]
        }
        
        parsed = parser.parse_reddit_posts(raw_data)
        print(f"\n✅ Parsed {parsed['total_posts']} posts")
        if parsed['posts']:
            post = parsed['posts'][0]
            print(f"   Title: {post['title']}")
            print(f"   Engagement Score: {post['engagement_score']}")
            
    except Exception as e:
        logger.error(f"Cache test error: {e}")

async def test_full_orchestration():
    """Test full orchestration with Oracle Prime."""
    print("\n" + "="*70)
    print("Testing Full Orchestration")
    print("="*70)
    
    queries = [
        "Analyze TSLA for investment opportunity",
        "What's the market sentiment for AAPL?",
        "Generate investment report for NVDA"
    ]
    
    for query in queries:
        print(f"\n📊 Query: {query}")
        success = await test_individual_agent("Oracle Prime", AGENTS["Oracle Prime"]["url"], query)
        if success:
            print("✅ Orchestration successful")
        else:
            print("❌ Orchestration failed")
        
        # Small delay between queries
        await asyncio.sleep(2)

async def verify_supabase_data():
    """Verify data is being saved to Supabase."""
    print("\n" + "="*70)
    print("Verifying Supabase Data")
    print("="*70)
    
    try:
        from src.a2a_mcp.common.supabase_client import SupabaseClient
        
        client = SupabaseClient()
        
        # Check trading signals
        signals = await client.get_latest_signals(limit=10)
        print(f"\n📊 Latest Trading Signals: {len(signals)}")
        for signal in signals[:3]:
            print(f"  - {signal['symbol']}: {signal['signal_type']} "
                  f"(confidence: {signal['confidence_score']:.2f}) "
                  f"by {signal['agent_name']}")
        
        # Check sentiment data
        db = client.get_client()
        sentiment_response = (db.table('sentiment_data')
                            .select("*")
                            .order('created_at', desc=True)
                            .limit(5)
                            .execute())
        
        print(f"\n😊 Latest Sentiment Data: {len(sentiment_response.data)}")
        for sentiment in sentiment_response.data[:3]:
            print(f"  - {sentiment['symbol']}: score={sentiment['sentiment_score']:.2f} "
                  f"from {sentiment['source']}")
        
        # Check research reports
        research_response = (db.table('investment_research')
                           .select("*")
                           .order('created_at', desc=True)
                           .limit(5)
                           .execute())
        
        print(f"\n📑 Latest Research Reports: {len(research_response.data)}")
        for research in research_response.data[:3]:
            print(f"  - {research['symbol']}: {research['thesis_summary'][:50]}...")
            
    except Exception as e:
        logger.error(f"Supabase verification error: {e}")

async def main():
    """Run complete Market Oracle system test."""
    print("\n" + "="*70)
    print("🔮 MARKET ORACLE COMPLETE SYSTEM TEST")
    print("="*70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Check all agents are running
    print("\n1️⃣ Checking Agent Health...")
    all_healthy = True
    for agent_name, config in AGENTS.items():
        healthy = await check_agent_health(agent_name, config['url'])
        if not healthy:
            all_healthy = False
    
    if not all_healthy:
        print("\n⚠️  Some agents are not running.")
        print("Please run: ./start_market_oracle.sh")
        return
    
    # Step 2: Test Stock MCP Integration
    print("\n2️⃣ Testing Stock MCP Integration...")
    await test_stock_mcp_integration()
    
    # Step 3: Test BrightData Cache
    print("\n3️⃣ Testing BrightData Cache...")
    await test_brightdata_cache()
    
    # Step 4: Test Individual Agents
    print("\n4️⃣ Testing Individual Agents...")
    
    test_cases = [
        ("Sentiment Seeker", "Analyze Reddit sentiment for TSLA"),
        ("Technical Prophet", "Perform technical analysis on AAPL"),
        ("Risk Guardian", "Assess portfolio risk for adding NVDA position"),
        ("Trend Correlator", "Find market trends related to MSFT"),
        ("Report Synthesizer", "Generate investment report for GOOGL"),
        ("Audio Briefer", "Create audio briefing for today's market outlook")
    ]
    
    for agent_name, query in test_cases:
        if agent_name in AGENTS:
            await test_individual_agent(agent_name, AGENTS[agent_name]['url'], query)
            await asyncio.sleep(2)
    
    # Step 5: Test Full Orchestration
    print("\n5️⃣ Testing Full Orchestration...")
    await test_full_orchestration()
    
    # Step 6: Verify Supabase Data
    print("\n6️⃣ Verifying Supabase Data...")
    await verify_supabase_data()
    
    print("\n" + "="*70)
    print("✅ COMPLETE SYSTEM TEST FINISHED")
    print("="*70)
    print("\nCheck market_oracle_test.log for detailed logs")

if __name__ == "__main__":
    asyncio.run(main())