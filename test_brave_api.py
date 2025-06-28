#!/usr/bin/env python3
"""Test Brave Search API directly."""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_brave_api():
    """Test the Brave Search API."""
    
    api_key = os.getenv('BRAVE_API_KEY')
    if not api_key:
        print("❌ BRAVE_API_KEY not found in environment")
        return
    
    url = "https://api.search.brave.com/res/v1/news/search"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": api_key
    }
    params = {
        "q": "AAPL stock news latest",
        "count": 5,
        "freshness": "week"
    }
    
    print("Testing Brave Search API...")
    print(f"URL: {url}")
    print(f"Query: {params['q']}")
    print("-" * 50)
    
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers, params=params) as response:
                print(f"Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print("✅ Success!")
                    print(f"Found {len(data.get('results', []))} results")
                    
                    # Print first result
                    if data.get('results'):
                        first = data['results'][0]
                        print(f"\nFirst result:")
                        print(f"Title: {first.get('title')}")
                        print(f"URL: {first.get('url')}")
                else:
                    error_text = await response.text()
                    print(f"❌ Error {response.status}: {error_text}")
                    
    except asyncio.TimeoutError:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    print("Brave Search API Test")
    print("=" * 50)
    asyncio.run(test_brave_api())