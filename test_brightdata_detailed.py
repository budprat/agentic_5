#!/usr/bin/env python3
"""Detailed test of BrightData integration with full logging."""

import asyncio
import logging
import sys
from datetime import datetime

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('brightdata_test.log')
    ]
)

# Import our agent
from src.a2a_mcp.agents.market_oracle import SentimentSeekerAgentBrightData

async def test_sentiment_analysis():
    """Test sentiment analysis with detailed logging."""
    
    print("\n" + "="*70)
    print("DETAILED BRIGHTDATA SENTIMENT ANALYSIS TEST")
    print("="*70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Create agent
    agent = SentimentSeekerAgentBrightData()
    print(f"✅ Agent created: {agent.agent_name}")
    print(f"   BrightData Token: {agent.brightdata_token[:20]}...")
    print(f"   Dataset ID: {agent.dataset_id}")
    print(f"   Stock MCP URL: {agent.fetch_stock_predictions.__doc__}")
    
    # Test symbols
    symbols = ["TSLA", "AAPL", "NVDA"]
    
    for symbol in symbols:
        print(f"\n{'='*70}")
        print(f"Testing {symbol}")
        print('='*70)
        
        query = f"Analyze Reddit sentiment for {symbol}"
        print(f"Query: {query}")
        
        try:
            # Stream the analysis
            async for response in agent.stream(query, "test_session", f"test_{symbol}"):
                if response.get('is_task_complete'):
                    if response.get('response_type') == 'data':
                        data = response['content']
                        
                        print("\n📊 COMPLETE ANALYSIS RESULTS:")
                        print("-" * 50)
                        
                        # Basic info
                        print(f"Symbol: {data.get('symbol', 'N/A')}")
                        print(f"Data Source: {data.get('data_source', 'N/A')}")
                        print(f"Timestamp: {data.get('timestamp', 'N/A')}")
                        
                        # Sentiment scores
                        print(f"\n📈 SENTIMENT METRICS:")
                        print(f"  Overall Score: {data.get('sentiment_score', 0):.2f} (-1 to +1)")
                        print(f"  Confidence: {data.get('confidence', 0):.2f}")
                        print(f"  Volume: {data.get('volume_score', 'N/A')}")
                        print(f"  Posts Analyzed: {data.get('posts_analyzed', 0)}")
                        
                        # Volume metrics
                        if 'volume_metrics' in data:
                            vm = data['volume_metrics']
                            print(f"\n📊 VOLUME BREAKDOWN:")
                            print(f"  Total Posts: {vm.get('total_posts', 0)}")
                            print(f"  Total Comments: {vm.get('total_comments', 0)}")
                            print(f"  Total Upvotes: {vm.get('total_upvotes', 0)}")
                            print(f"  Engagement Rate: {vm.get('engagement_rate', 0):.2f}")
                        
                        # Sentiment breakdown
                        if 'sentiment_breakdown' in data:
                            sb = data['sentiment_breakdown']
                            print(f"\n🎯 SENTIMENT DISTRIBUTION:")
                            print(f"  Bullish: {sb.get('bullish_percentage', 0):.1f}%")
                            print(f"  Bearish: {sb.get('bearish_percentage', 0):.1f}%")
                            print(f"  Neutral: {sb.get('neutral_percentage', 0):.1f}%")
                        
                        # Key themes
                        if 'key_themes' in data:
                            print(f"\n🔑 KEY THEMES:")
                            for theme in data['key_themes'][:5]:
                                print(f"  - {theme}")
                        
                        # Top posts
                        if 'top_posts' in data and data['top_posts']:
                            print(f"\n📝 TOP POSTS:")
                            for i, post in enumerate(data['top_posts'][:3], 1):
                                print(f"  {i}. {post.get('title', 'N/A')}")
                                print(f"     Sentiment: {post.get('sentiment', 0):.2f}")
                                print(f"     Upvotes: {post.get('upvotes', 0)}")
                                print(f"     Comments: {post.get('comments', 0)}")
                                print(f"     Subreddit: r/{post.get('subreddit', 'N/A')}")
                        
                        # ML predictions
                        if 'ml_predictions' in data:
                            ml = data['ml_predictions']
                            print(f"\n🤖 ML PREDICTIONS:")
                            print(f"  Direction: {ml.get('ml_prediction', 'N/A')}")
                            print(f"  Confidence: {ml.get('confidence', 0):.2f}")
                            print(f"  Predicted Move: {ml.get('predicted_move', 'N/A')}")
                            print(f"  Timeframe: {ml.get('timeframe', 'N/A')}")
                        
                        # Risk flags
                        if 'risk_flags' in data and data['risk_flags']:
                            print(f"\n⚠️  RISK FLAGS:")
                            for flag in data['risk_flags']:
                                print(f"  - {flag}")
                        
                        # Recommendation
                        print(f"\n💡 RECOMMENDATION: {data.get('recommendation', 'N/A')}")
                        print(f"\n📝 SUMMARY:")
                        print(f"{data.get('analysis_summary', 'N/A')}")
                        
                        print("\n✅ Analysis complete for", symbol)
                        
                else:
                    # Progress update
                    print(f"  ⏳ {response.get('content', '')}")
            
        except Exception as e:
            print(f"\n❌ ERROR for {symbol}: {e}")
            import traceback
            traceback.print_exc()
        
        # Small delay between symbols
        await asyncio.sleep(2)
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
    print("\nCheck brightdata_test.log for detailed logs")

if __name__ == "__main__":
    asyncio.run(test_sentiment_analysis())