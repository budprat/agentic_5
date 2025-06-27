#!/usr/bin/env python3
"""Test BrightData API with exact curl configuration."""

import asyncio
import aiohttp
import json

async def test_brightdata_api():
    """Test the exact BrightData API configuration."""
    
    # Exact configuration from curl command
    url = "https://api.brightdata.com/datasets/v3/trigger?dataset_id=gd_lvz8ah06191smkebj4&include_errors=true&type=discover_new&discover_by=keyword"
    
    headers = {
        "Authorization": "Bearer 9e9ece35cc8225d8b9e866772aea59acb0f9c810904b4616a513be83dc0d7a28",
        "Content-Type": "application/json"
    }
    
    # Test with TSLA as in the example - limited to 10 posts
    data = [{"keyword": "TSLA", "date": "Today", "sort_by": "Hot", "num_of_posts": 10}]
    
    print("Testing BrightData API with configuration:")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    print("-" * 50)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                print(f"Status: {response.status}")
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        response_json = json.loads(response_text)
                        print("✅ Success! Response:")
                        print(json.dumps(response_json, indent=2))
                    except:
                        print("Response (non-JSON):", response_text)
                else:
                    print(f"❌ Error {response.status}:")
                    print(response_text)
                    
    except Exception as e:
        print(f"❌ Exception: {e}")

async def test_with_different_symbols():
    """Test with multiple stock symbols."""
    print("\n" + "="*50)
    print("Testing multiple symbols")
    print("="*50 + "\n")
    
    symbols = ["AAPL", "NVDA", "GOOGL"]
    
    for symbol in symbols:
        print(f"\nTesting {symbol}...")
        
        url = "https://api.brightdata.com/datasets/v3/trigger?dataset_id=gd_lvz8ah06191smkebj4&include_errors=true&type=discover_new&discover_by=keyword"
        headers = {
            "Authorization": "Bearer 9e9ece35cc8225d8b9e866772aea59acb0f9c810904b4616a513be83dc0d7a28",
            "Content-Type": "application/json"
        }
        data = [{"keyword": symbol, "date": "Today", "sort_by": "Hot", "num_of_posts": 10}]
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ {symbol}: Success - {result}")
                    else:
                        print(f"❌ {symbol}: Error {response.status}")
        except Exception as e:
            print(f"❌ {symbol}: Exception - {e}")
        
        await asyncio.sleep(1)  # Avoid rate limiting

if __name__ == "__main__":
    print("BrightData API Test")
    print("=" * 50)
    asyncio.run(test_brightdata_api())
    asyncio.run(test_with_different_symbols())