#!/usr/bin/env python3
"""Test fixed BrightData integration with NDJSON parser."""

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
        logging.FileHandler('brightdata_fixed_test.log')
    ]
)

logger = logging.getLogger(__name__)

async def test_brightdata_fixed():
    """Test BrightData with fixed NDJSON parser."""
    print("\n" + "="*80)
    print("🔧 TESTING FIXED BRIGHTDATA INTEGRATION")
    print("="*80)
    
    from src.a2a_mcp.agents.market_oracle.sentiment_seeker_agent_brightdata import SentimentSeekerAgentBrightData
    
    agent = SentimentSeekerAgentBrightData()
    
    # Test symbols
    test_symbols = ["TSLA", "NVDA", "AAPL"]
    
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}")
        print("-" * 60)
        
        try:
            # Clear cache first to force fresh API call
            from src.a2a_mcp.common.brightdata_cache import BrightDataCache
            cache = BrightDataCache()
            
            # Direct API test
            print(f"1️⃣ Fetching Reddit data for {symbol}...")
            reddit_data = await agent.fetch_reddit_data(symbol)
            
            if isinstance(reddit_data, str):
                print(f"  ✅ Got NDJSON response: {len(reddit_data)} bytes")
                print(f"  📝 Number of lines: {reddit_data.count(chr(10)) + 1}")
                
                # Parse with fixed parser
                from src.a2a_mcp.common.brightdata_cache import BrightDataParser
                parser = BrightDataParser()
                parsed = parser.parse_reddit_posts(reddit_data)
                
                print(f"  ✅ Parsed {parsed['total_posts']} posts")
                
                # Show top posts
                if parsed['posts']:
                    print("\n  📌 Top Reddit Posts:")
                    for i, post in enumerate(parsed['posts'][:3], 1):
                        print(f"\n  {i}. {post['title']}")
                        print(f"     Subreddit: r/{post['subreddit']}")
                        print(f"     Author: u/{post['author']}")
                        print(f"     Upvotes: {post['upvotes']:,}")
                        print(f"     Comments: {post['num_comments']:,}")
                        print(f"     Engagement Score: {post['engagement_score']:,}")
                        print(f"     Date: {post['created_at']}")
                        if post['text']:
                            preview = post['text'][:100] + "..." if len(post['text']) > 100 else post['text']
                            print(f"     Text: {preview}")
                
                # Test caching
                await cache.set(symbol, parsed)
                print(f"\n  💾 Data cached for {symbol}")
                
            elif 'error' in reddit_data:
                print(f"  ❌ Error: {reddit_data['error']}")
                print("  ⚠️  Using fallback data")
            else:
                print(f"  ℹ️  Got structured response: {type(reddit_data)}")
            
            # Test full sentiment analysis
            print(f"\n2️⃣ Running full sentiment analysis...")
            
            query = f"Analyze Reddit sentiment for {symbol}"
            result = None
            
            async for response in agent.stream(query, f"test_{symbol}", f"task_{symbol}"):
                if not response.get('is_task_complete'):
                    print(f"  ⏳ {response.get('content', '')}")
                else:
                    if response.get('response_type') == 'data':
                        result = response['content']
                        break
            
            if result:
                print(f"\n  ✅ Sentiment Analysis Complete:")
                print(f"     Sentiment Score: {result.get('sentiment_score', 0):.2f}")
                print(f"     Confidence: {result.get('confidence', 0):.1%}")
                print(f"     Volume: {result.get('volume_score', 'N/A')}")
                print(f"     Recommendation: {result.get('recommendation', 'N/A')}")
                
                if result.get('posts_analyzed', 0) > 0:
                    print(f"     Posts Analyzed: {result.get('posts_analyzed')}")
                    print(f"     Data Source: {result.get('data_source', 'N/A')}")
                
        except Exception as e:
            logger.error(f"Error testing {symbol}: {e}")
            print(f"  ❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
        
        await asyncio.sleep(2)
    
    print("\n" + "="*80)
    print("✅ BRIGHTDATA TESTING COMPLETE")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_brightdata_fixed())