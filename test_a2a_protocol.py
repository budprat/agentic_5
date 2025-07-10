#!/usr/bin/env python3
# ABOUTME: Tests A2A protocol communication with solopreneur agents
# ABOUTME: Uses proper JSON-RPC format with message/send method

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime

async def test_a2a_message_send():
    """Test sending a message using proper A2A protocol with message/send method."""
    
    # Test agent on port 10902 (Technical Intelligence Agent)
    url = "http://localhost:10902"
    
    # Create proper JSON-RPC request with message/send method
    request_id = str(uuid.uuid4())
    message_id = str(uuid.uuid4())
    
    json_rpc_request = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "parts": [
                    {
                        "kind": "text",
                        "text": "What are the best practices for implementing a microservices architecture?"
                    }
                ],
                "messageId": message_id,
                "kind": "message"
            },
            "metadata": {}
        }
    }
    
    print(f"Sending A2A message/send request to {url}")
    print(f"Request: {json.dumps(json_rpc_request, indent=2)}")
    
    timeout = aiohttp.ClientTimeout(total=30)
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            # Send JSON-RPC request
            async with session.post(url, json=json_rpc_request) as response:
                print(f"\nResponse status: {response.status}")
                print(f"Response headers: {dict(response.headers)}")
                
                if response.status == 200:
                    result = await response.json()
                    print(f"\nResponse body: {json.dumps(result, indent=2)}")
                    
                    # Check if it's a proper JSON-RPC response
                    if "jsonrpc" in result and result["jsonrpc"] == "2.0":
                        if "result" in result:
                            print("\n✓ Success! Received valid JSON-RPC response")
                            return result["result"]
                        elif "error" in result:
                            print(f"\n✗ JSON-RPC Error: {result['error']}")
                    else:
                        print("\n✗ Invalid JSON-RPC response format")
                else:
                    text = await response.text()
                    print(f"\nError response: {text}")
                    
        except Exception as e:
            print(f"\nError: {e}")

async def test_a2a_message_stream():
    """Test streaming with message/stream method."""
    
    # Test agent on port 10903 (Knowledge Management Agent)
    url = "http://localhost:10903"
    
    # Create proper JSON-RPC request with message/stream method
    request_id = str(uuid.uuid4())
    message_id = str(uuid.uuid4())
    
    json_rpc_request = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": "message/stream",
        "params": {
            "message": {
                "role": "user",
                "parts": [
                    {
                        "kind": "text",
                        "text": "What are the key knowledge management strategies for a solopreneur?"
                    }
                ],
                "messageId": message_id,
                "kind": "message"
            },
            "metadata": {}
        }
    }
    
    print(f"\n\nSending A2A message/stream request to {url}")
    print(f"Request: {json.dumps(json_rpc_request, indent=2)}")
    
    timeout = aiohttp.ClientTimeout(total=30)
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            # Send JSON-RPC request expecting SSE stream
            async with session.post(url, json=json_rpc_request) as response:
                print(f"\nResponse status: {response.status}")
                print(f"Response headers: {dict(response.headers)}")
                
                if response.status == 200:
                    content_type = response.headers.get('Content-Type', '')
                    
                    if 'text/event-stream' in content_type:
                        print("\n✓ Received SSE stream response")
                        # Read SSE events
                        async for line in response.content:
                            if line:
                                line_str = line.decode('utf-8').strip()
                                if line_str.startswith('data: '):
                                    data = line_str[6:]  # Remove 'data: ' prefix
                                    try:
                                        event = json.loads(data)
                                        print(f"\nSSE Event: {json.dumps(event, indent=2)}")
                                        
                                        # Check for final event
                                        if event.get('result', {}).get('final'):
                                            print("\n✓ Received final event")
                                            break
                                    except json.JSONDecodeError:
                                        print(f"\nSSE Data (non-JSON): {data}")
                    else:
                        # Regular JSON response
                        result = await response.json()
                        print(f"\nResponse body: {json.dumps(result, indent=2)}")
                else:
                    text = await response.text()
                    print(f"\nError response: {text}")
                    
        except Exception as e:
            print(f"\nError: {e}")

async def main():
    """Run all A2A protocol tests."""
    print("Testing A2A Protocol Communication with Solopreneur Agents")
    print("=" * 60)
    
    # Test message/send
    await test_a2a_message_send()
    
    # Test message/stream
    await test_a2a_message_stream()

if __name__ == "__main__":
    asyncio.run(main())