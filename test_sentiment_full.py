#!/usr/bin/env python3
"""Test Sentiment Seeker full streaming functionality."""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from src.a2a_mcp.agents.market_oracle.sentiment_seeker_agent_brightdata import SentimentSeekerAgentBrightData

async def test_sentiment_streaming():
    """Test full Sentiment Seeker streaming."""
    print("\n🔍 Testing Sentiment Seeker Full Streaming")
    print("="*60)
    
    try:
        agent = SentimentSeekerAgentBrightData()
        print("✅ Agent initialized")
        
        # Test streaming
        context_id = "test-sentiment-seeker"
        task_id = f"task-{datetime.now().timestamp()}"
        
        print("\n📊 Streaming sentiment analysis for AAPL...")
        print("-" * 60)
        
        response_count = 0
        async for chunk in agent.stream("Analyze AAPL sentiment", context_id, task_id):
            response_count += 1
            
            if isinstance(chunk, dict):
                content = chunk.get('content', '')
                if content:
                    print(f"📍 {content}")
                
                # Check if task is complete
                if chunk.get('is_task_complete', False):
                    print("\n✅ Analysis complete!")
                    
                    # If response_type is 'data', show the analysis
                    if chunk.get('response_type') == 'data' and isinstance(content, dict):
                        print("\n📊 Final Analysis:")
                        print(f"Symbol: {content.get('symbol', 'N/A')}")
                        print(f"Sentiment Score: {content.get('sentiment_score', 'N/A')}")
                        print(f"Confidence: {content.get('confidence', 'N/A')}")
                        print(f"Volume Score: {content.get('volume_score', 'N/A')}")
                        print(f"Recommendation: {content.get('recommendation', 'N/A')}")
                        print(f"Posts Analyzed: {content.get('posts_analyzed', 'N/A')}")
            else:
                print(f"📝 {chunk}")
        
        print(f"\n✅ Received {response_count} streaming responses")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_sentiment_streaming())