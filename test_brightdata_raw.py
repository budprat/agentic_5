#!/usr/bin/env python3
"""Test BrightData API raw response to debug JSON parsing issue."""

import os
import asyncio
import aiohttp
import json
from dotenv import load_dotenv

async def test_brightdata_raw():
    """Test BrightData API and capture raw response."""
    load_dotenv()
    
    # Test configuration
    token = os.getenv('BRIGHTDATA_API_TOKEN')
    dataset_id = "gd_lvz8ah06191smkebj4"
    
    # Step 1: Trigger data collection
    print("1️⃣ Triggering BrightData collection...")
    
    trigger_url = f"https://api.brightdata.com/datasets/v3/trigger?dataset_id={dataset_id}&include_errors=true&type=discover_new&discover_by=keyword"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = [{"keyword": "TSLA", "date": "Today", "sort_by": "Hot", "num_of_posts": 10}]
    
    async with aiohttp.ClientSession() as session:
        async with session.post(trigger_url, headers=headers, json=data) as response:
            print(f"Trigger Status: {response.status}")
            trigger_text = await response.text()
            print(f"Trigger Response: {trigger_text}")
            
            try:
                trigger_data = json.loads(trigger_text)
                snapshot_id = trigger_data.get('snapshot_id')
                print(f"Snapshot ID: {snapshot_id}")
            except Exception as e:
                print(f"Error parsing trigger response: {e}")
                return
    
    if not snapshot_id:
        print("No snapshot ID received")
        return
    
    # Step 2: Poll for results
    print("\n2️⃣ Polling for results...")
    
    result_url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    await asyncio.sleep(15)  # Initial wait
    
    for attempt in range(10):
        print(f"\nAttempt {attempt + 1}...")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(result_url, headers=headers) as response:
                print(f"Status: {response.status}")
                
                # Get raw response
                raw_response = await response.read()
                print(f"Raw response length: {len(raw_response)} bytes")
                
                # Try to decode as text
                try:
                    text_response = raw_response.decode('utf-8')
                    print(f"Text response preview (first 500 chars):")
                    print(text_response[:500])
                    
                    # Save full response for analysis
                    with open('brightdata_raw_response.txt', 'w') as f:
                        f.write(text_response)
                    print("\nFull response saved to brightdata_raw_response.txt")
                    
                    # Try different parsing strategies
                    print("\n3️⃣ Trying different parsing strategies...")
                    
                    # Strategy 1: Direct JSON parse
                    try:
                        data = json.loads(text_response)
                        print("✅ Strategy 1 (direct parse): Success!")
                        print(f"Data type: {type(data)}")
                        if isinstance(data, dict):
                            print(f"Keys: {list(data.keys())}")
                            if response.status == 200 and data.get('status') != 'running':
                                print("\n🎉 Got final results!")
                                return
                    except json.JSONDecodeError as e:
                        print(f"❌ Strategy 1 failed: {e}")
                    
                    # Strategy 2: Parse line by line
                    lines = text_response.strip().split('\n')
                    print(f"\nFound {len(lines)} lines")
                    
                    for i, line in enumerate(lines[:3]):  # First 3 lines
                        print(f"\nLine {i+1} preview: {line[:100]}...")
                        try:
                            line_data = json.loads(line)
                            print(f"  ✅ Line {i+1} is valid JSON")
                        except:
                            print(f"  ❌ Line {i+1} is not valid JSON")
                    
                    # Strategy 3: Find JSON boundaries
                    print("\n4️⃣ Looking for JSON boundaries...")
                    
                    # Find all potential JSON start/end points
                    json_starts = [i for i, char in enumerate(text_response) if char == '{']
                    json_ends = [i for i, char in enumerate(text_response) if char == '}']
                    
                    print(f"Found {len(json_starts)} '{' and {len(json_ends)} '}'")
                    
                    if response.status == 200 and 'data' in text_response:
                        print("\n✅ Got 200 response with data!")
                        return
                        
                except Exception as e:
                    print(f"Error processing response: {e}")
        
        if attempt < 9:
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(test_brightdata_raw())