#!/usr/bin/env python3
# ABOUTME: Quick check to verify Oracle agent is responding to A2A requests
# ABOUTME: Tests the root "/" endpoint with proper A2A JSON-RPC format

import asyncio
import aiohttp
import json

async def check_oracle():
    """Check if Oracle is responding to A2A requests."""
    url = "http://localhost:10901"
    
    # Simple A2A request
    payload = {
        "jsonrpc": "2.0",
        "id": "health-check",
        "method": "message/send",  # Try non-streaming first
        "params": {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": "ping"}],
                "messageId": "health-check-msg",
                "kind": "message"
            },
            "metadata": {}
        }
    }
    
    print(f"Checking Oracle at {url}")
    
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload) as response:
                print(f"Status: {response.status}")
                print(f"Headers: {dict(response.headers)}")
                
                if response.status == 200:
                    content_type = response.headers.get('Content-Type', '')
                    print(f"Content-Type: {content_type}")
                    
                    # Read response
                    text = await response.text()
                    print(f"\nResponse:\n{text[:500]}...")
                    
                    # Try to parse as JSON
                    try:
                        data = json.loads(text)
                        print(f"\nParsed response: {json.dumps(data, indent=2)[:500]}...")
                    except:
                        pass
                        
                    return True
                else:
                    error_text = await response.text()
                    print(f"Error response: {error_text}")
                    return False
                    
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(check_oracle())
    print(f"\nResult: {'SUCCESS' if result else 'FAILED'}")