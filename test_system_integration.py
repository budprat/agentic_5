#!/usr/bin/env python3
# ABOUTME: Test the complete AI Solopreneur Oracle System integration
# ABOUTME: Uses A2A JSON-RPC protocol to communicate with agents

import asyncio
import httpx
import json
import uuid
from datetime import datetime

async def test_oracle_agent():
    """Test communication with the oracle agent."""
    print("=" * 60)
    print("AI Solopreneur Oracle System Integration Test")
    print("=" * 60)
    
    # Test query
    query = "What are the best practices for building a SaaS product as a solo developer?"
    
    # Create A2A JSON-RPC request
    request_id = str(uuid.uuid4())
    message_id = str(uuid.uuid4())
    
    payload = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": "message/stream",
        "params": {
            "message": {
                "role": "user",
                "parts": [
                    {
                        "kind": "text",
                        "text": query
                    }
                ],
                "messageId": message_id,
                "kind": "message"
            },
            "metadata": {}
        }
    }
    
    print(f"\n📤 Sending query to Oracle: {query}")
    print(f"Request ID: {request_id}")
    
    try:
        # Send request to oracle
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:10901/invoke",
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ Oracle Response:")
                print("-" * 40)
                
                if 'result' in result:
                    content = result['result'].get('content', 'No content')
                    print(content)
                elif 'error' in result:
                    print(f"❌ Error: {result['error']}")
                else:
                    print(f"Raw response: {json.dumps(result, indent=2)}")
            else:
                print(f"\n❌ HTTP Error {response.status_code}: {response.text}")
                
    except Exception as e:
        print(f"\n❌ Error communicating with oracle: {e}")
        return False
    
    # Test domain agent endpoints
    print("\n\n🔍 Testing Domain Agent Connections:")
    print("-" * 40)
    
    domain_agents = [
        ("Technical Intelligence", 10902),
        ("Knowledge Management", 10903),
        ("Personal Optimization", 10904),
        ("Learning Enhancement", 10905),
        ("Integration Synthesis", 10906)
    ]
    
    for agent_name, port in domain_agents:
        try:
            async with httpx.AsyncClient() as client:
                # Try health check
                health_response = await client.get(
                    f"http://localhost:{port}/health",
                    timeout=5.0
                )
                
                if health_response.status_code == 200:
                    print(f"✅ {agent_name} Agent (port {port}): ONLINE")
                else:
                    print(f"⚠️  {agent_name} Agent (port {port}): HTTP {health_response.status_code}")
        except Exception as e:
            print(f"❌ {agent_name} Agent (port {port}): {type(e).__name__}")
    
    print("\n✨ Integration test complete!")
    return True

async def test_cross_domain_query():
    """Test a cross-domain query that should engage multiple agents."""
    print("\n\n🌐 Testing Cross-Domain Query:")
    print("=" * 60)
    
    query = """I want to build an AI-powered learning platform. 
    Please analyze:
    1. Technical architecture recommendations
    2. Knowledge management strategies
    3. Learning optimization features
    4. Personal productivity integration
    """
    
    request_id = str(uuid.uuid4())
    message_id = str(uuid.uuid4())
    
    payload = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": "message/stream",
        "params": {
            "message": {
                "role": "user",
                "parts": [
                    {
                        "kind": "text",
                        "text": query
                    }
                ],
                "messageId": message_id,
                "kind": "message"
            },
            "metadata": {
                "cross_domain": True,
                "domains": ["technical", "knowledge", "learning", "personal"]
            }
        }
    }
    
    print("📤 Sending cross-domain query...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:10901/invoke",
                json=payload,
                timeout=60.0  # Longer timeout for complex query
            )
            
            if response.status_code == 200:
                result = response.json()
                print("\n✅ Cross-Domain Analysis:")
                print("-" * 40)
                
                if 'result' in result:
                    content = result['result'].get('content', 'No content')
                    print(content)
                else:
                    print(f"Raw response: {json.dumps(result, indent=2)}")
            else:
                print(f"\n❌ HTTP Error {response.status_code}: {response.text}")
                
    except Exception as e:
        print(f"\n❌ Error in cross-domain query: {e}")

async def main():
    """Run all integration tests."""
    print(f"🚀 Starting AI Solopreneur Oracle System Tests")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests
    await test_oracle_agent()
    await test_cross_domain_query()
    
    print("\n\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())