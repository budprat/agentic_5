#!/usr/bin/env python3
"""Test network-dependent agents separately."""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from src.a2a_mcp.agents.market_oracle.news_hawk_agent import NewsHawkAgent
from src.a2a_mcp.agents.market_oracle.sentiment_seeker_agent_brightdata import SentimentSeekerAgentBrightData

async def test_news_hawk():
    """Test News Hawk agent."""
    print("\n" + "="*60)
    print("🦅 Testing News Hawk Agent")
    print("="*60)
    
    try:
        agent = NewsHawkAgent()
        print("✅ Agent initialized")
        
        # Test the Brave API directly
        print("\n📰 Testing Brave Search API...")
        news_items = await agent.search_news("AAPL stock", count=5)
        
        if news_items:
            print(f"✅ Found {len(news_items)} news articles")
            for i, item in enumerate(news_items[:3], 1):
                print(f"\n{i}. {item['title']}")
                print(f"   Source: {item.get('source', 'Unknown')}")
        else:
            print("❌ No news found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

async def test_sentiment_seeker():
    """Test Sentiment Seeker agent."""
    print("\n" + "="*60)
    print("🔍 Testing Sentiment Seeker Agent")
    print("="*60)
    
    try:
        agent = SentimentSeekerAgentBrightData()
        print("✅ Agent initialized")
        
        # Test the BrightData API directly
        print("\n📊 Testing BrightData Reddit API...")
        reddit_data = await agent.fetch_reddit_data("AAPL")
        
        if "error" not in reddit_data:
            print(f"✅ BrightData request successful")
            if "snapshot_id" in reddit_data:
                print(f"📸 Snapshot ID: {reddit_data['snapshot_id']}")
            elif "posts" in reddit_data:
                print(f"✅ Found {len(reddit_data['posts'])} posts")
        else:
            print(f"❌ Error: {reddit_data['error']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Test both network agents."""
    print("🌐 Network Agents Test Suite")
    print(f"📅 {datetime.now()}")
    
    # Test News Hawk
    await test_news_hawk()
    
    # Test Sentiment Seeker
    await test_sentiment_seeker()
    
    print("\n" + "="*60)
    print("✅ Test completed")

if __name__ == "__main__":
    asyncio.run(main())