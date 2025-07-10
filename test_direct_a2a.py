#!/usr/bin/env python3
# ABOUTME: Direct test of A2A protocol without going through agent layer
# ABOUTME: Tests raw JSON-RPC communication to understand the issue

import asyncio
import aiohttp
import json
import uuid

async def test_agent_card():
    """Test if agent cards are accessible."""
    url = "http://localhost:10902/.well-known/agent.json"
    
    print(f"Testing agent card at {url}")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✓ Agent card retrieved: {data.get('name', 'Unknown')}")
                    print(f"  Description: {data.get('description', 'N/A')}")
                    print(f"  Capabilities: {data.get('capabilities', {})}")
                    return True
                else:
                    print(f"✗ Failed to get agent card: HTTP {response.status}")
                    return False
        except Exception as e:
            print(f"✗ Error getting agent card: {e}")
            return False

async def test_simple_message():
    """Test with simplest possible message."""
    url = "http://localhost:10902"
    
    # Minimal A2A JSON-RPC request
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "parts": [
                    {
                        "kind": "text",
                        "text": "Hello"
                    }
                ],
                "messageId": str(uuid.uuid4()),
                "kind": "message"
            }
        }
    }
    
    print(f"\nTesting simple message to {url}")
    print(f"Request: {json.dumps(request, indent=2)}")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=request) as response:
                print(f"\nResponse status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"Response: {json.dumps(data, indent=2)}")
                    
                    if "error" in data:
                        # Check error details
                        error = data["error"]
                        print(f"\n❌ Error details:")
                        print(f"  Code: {error.get('code')}")
                        print(f"  Message: {error.get('message')}")
                        
                        # Check if there's additional error data
                        if "data" in error:
                            print(f"  Data: {error['data']}")
                else:
                    text = await response.text()
                    print(f"Error response: {text}")
                    
        except Exception as e:
            print(f"Exception: {e}")
            import traceback
            traceback.print_exc()

async def check_agent_health():
    """Check if agent is responding to basic requests."""
    ports = {
        "Technical Intelligence": 10902,
        "Knowledge Management": 10903,
        "Personal Optimization": 10904,
        "Learning Enhancement": 10905,
        "Integration Synthesis": 10906,
        "Solopreneur Oracle": 10901
    }
    
    print("\nChecking agent health...")
    for name, port in ports.items():
        url = f"http://localhost:{port}"
        try:
            async with aiohttp.ClientSession() as session:
                # Try a simple GET to see if server responds
                async with session.get(url) as response:
                    if response.status == 405:  # Method not allowed is expected
                        print(f"✓ {name} (port {port}): Responding")
                    else:
                        print(f"? {name} (port {port}): Unexpected status {response.status}")
        except Exception as e:
            print(f"✗ {name} (port {port}): Not responding - {e}")

async def main():
    """Run all tests."""
    print("Direct A2A Protocol Testing")
    print("=" * 60)
    
    # First check agent health
    await check_agent_health()
    
    # Test agent card
    print("\n" + "=" * 60)
    await test_agent_card()
    
    # Test simple message
    print("\n" + "=" * 60)
    await test_simple_message()

if __name__ == "__main__":
    asyncio.run(main())