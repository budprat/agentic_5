#!/usr/bin/env python3
"""Test BrightData polling mechanism."""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_brightdata_polling():
    """Test the complete BrightData flow."""
    
    token = os.getenv('BRIGHTDATA_API_TOKEN')
    dataset_id = "gd_lvz8ah06191smkebj4"
    
    # Step 1: Trigger the search
    print("Step 1: Triggering BrightData search...")
    url = f"https://api.brightdata.com/datasets/v3/trigger?dataset_id={dataset_id}&include_errors=true&type=discover_new&discover_by=keyword"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = [{"keyword": "AAPL", "date": "Today", "sort_by": "Hot", "num_of_posts": 5}]
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Trigger successful: {result}")
                
                if 'snapshot_id' in result:
                    snapshot_id = result['snapshot_id']
                    print(f"📸 Snapshot ID: {snapshot_id}")
                    
                    # Step 2: Poll for results
                    print("\nStep 2: Polling for results...")
                    await poll_results(snapshot_id, token)
                else:
                    print("❌ No snapshot_id in response")
            else:
                print(f"❌ Trigger failed: {response.status}")
                print(await response.text())

async def poll_results(snapshot_id: str, token: str):
    """Poll BrightData for results."""
    
    # Try the snapshot endpoint
    url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    for attempt in range(10):
        print(f"\nAttempt {attempt + 1}/10...")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                print(f"Status: {response.status}")
                
                if response.status == 200:
                    text = await response.text()
                    print(f"Response length: {len(text)} bytes")
                    
                    # Check if it's NDJSON
                    if '\n' in text and text.startswith('{'):
                        lines = text.strip().split('\n')
                        print(f"✅ Got NDJSON with {len(lines)} lines")
                        
                        # Parse first few lines
                        for i, line in enumerate(lines[:3]):
                            try:
                                obj = json.loads(line)
                                print(f"\nLine {i+1}:")
                                print(f"  URL: {obj.get('url', 'N/A')}")
                                print(f"  Title: {obj.get('title', 'N/A')[:50]}...")
                                print(f"  Subreddit: {obj.get('subreddit', 'N/A')}")
                            except:
                                print(f"Failed to parse line {i+1}")
                        
                        return
                    else:
                        # Try to parse as JSON
                        try:
                            data = json.loads(text)
                            print(f"JSON response: {json.dumps(data, indent=2)[:200]}...")
                            
                            if data.get('status') == 'ready':
                                print("✅ Results are ready!")
                                return
                        except:
                            print("Not valid JSON")
                
                elif response.status == 202:
                    print("⏳ Still processing...")
                else:
                    print(f"❌ Error: {response.status}")
                    print(await response.text())
        
        if attempt < 9:
            await asyncio.sleep(2)
    
    print("\n❌ Results not ready after all attempts")

if __name__ == "__main__":
    asyncio.run(test_brightdata_polling())