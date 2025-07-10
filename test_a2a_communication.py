#!/usr/bin/env python3
# ABOUTME: Focused test for A2A agent-to-agent communication to verify TransferEncodingError fix
# ABOUTME: Tests the Oracle's ability to communicate with domain specialist agents via SSE

import asyncio
import aiohttp
import json
import time
from datetime import datetime

async def test_domain_agent_direct(port: int, domain: str, query: str):
    """Test direct communication with a domain agent."""
    print(f"\n🔍 Testing direct communication with {domain} agent on port {port}")
    
    url = f"http://localhost:{port}"
    payload = {
        "jsonrpc": "2.0",
        "id": "test-direct",
        "method": "message/stream",
        "params": {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": query}],
                "messageId": "test-msg-1",
                "kind": "message"
            },
            "metadata": {"test": True}
        }
    }
    
    start_time = time.time()
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    content_type = response.headers.get('Content-Type', '')
                    print(f"✅ Response received - Content-Type: {content_type}")
                    
                    if 'text/event-stream' in content_type:
                        final_content = None
                        event_count = 0
                        
                        async for line in response.content:
                            if line:
                                line_str = line.decode('utf-8').strip()
                                if line_str.startswith('data: '):
                                    event_count += 1
                                    data = line_str[6:]
                                    try:
                                        event = json.loads(data)
                                        if 'result' in event:
                                            result = event['result']
                                            kind = result.get('kind', '')
                                            
                                            if kind == 'streaming-response' and result.get('final'):
                                                message = result.get('message', {})
                                                parts = message.get('parts', [])
                                                text_parts = [p.get('text', '') for p in parts if p.get('kind') == 'text']
                                                final_content = '\n'.join(text_parts)
                                                print(f"✅ Final content received after {event_count} events")
                                                break
                                    except json.JSONDecodeError:
                                        pass
                        
                        elapsed = time.time() - start_time
                        if final_content:
                            print(f"✅ SUCCESS: Response received in {elapsed:.2f}s")
                            print(f"   Content preview: {final_content[:100]}...")
                            return True
                        else:
                            print(f"❌ FAILED: No final content received after {elapsed:.2f}s")
                            return False
                    else:
                        print(f"❌ FAILED: Unexpected response type")
                        return False
                else:
                    print(f"❌ FAILED: HTTP {response.status}")
                    return False
                    
    except asyncio.TimeoutError:
        elapsed = time.time() - start_time
        print(f"❌ FAILED: Timeout after {elapsed:.2f}s")
        return False
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ FAILED: {type(e).__name__}: {e} (after {elapsed:.2f}s)")
        return False

async def test_oracle_to_domain_communication():
    """Test Oracle's ability to communicate with domain agents."""
    print("\n🤖 Testing Oracle → Domain Agent Communication")
    
    # First test a simple query to the Oracle
    oracle_url = "http://localhost:10901"
    test_query = "What are the best practices for implementing a microservices architecture?"
    
    payload = {
        "jsonrpc": "2.0",
        "id": "test-oracle",
        "method": "message/stream",
        "params": {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": test_query}],
                "messageId": "test-oracle-msg",
                "kind": "message"
            },
            "metadata": {}
        }
    }
    
    print(f"\n📤 Sending query to Oracle: '{test_query}'")
    start_time = time.time()
    
    try:
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(oracle_url, json=payload) as response:
                if response.status == 200:
                    content_type = response.headers.get('Content-Type', '')
                    print(f"✅ Oracle responded - Content-Type: {content_type}")
                    
                    if 'text/event-stream' in content_type:
                        final_analysis = None
                        status_updates = []
                        domain_mentions = []
                        
                        async for line in response.content:
                            if line:
                                line_str = line.decode('utf-8').strip()
                                if line_str.startswith('data: '):
                                    data = line_str[6:]
                                    try:
                                        event = json.loads(data)
                                        if 'result' in event:
                                            result = event['result']
                                            kind = result.get('kind', '')
                                            
                                            # Track status updates
                                            if kind == 'status-update':
                                                status = result.get('status', {}).get('state', '')
                                                status_updates.append(status)
                                            
                                            # Track streaming responses
                                            elif kind == 'streaming-response':
                                                message = result.get('message', {})
                                                parts = message.get('parts', [])
                                                for part in parts:
                                                    if part.get('kind') == 'text':
                                                        text = part.get('text', '')
                                                        # Check for domain agent mentions
                                                        for domain in ['Technical', 'Personal', 'Knowledge', 'Learning', 'Integration']:
                                                            if domain in text:
                                                                domain_mentions.append(domain)
                                                        
                                                        # Check if this is the final analysis
                                                        if result.get('final'):
                                                            final_analysis = text
                                                            
                                    except json.JSONDecodeError:
                                        pass
                        
                        elapsed = time.time() - start_time
                        print(f"\n📊 Analysis completed in {elapsed:.2f}s")
                        print(f"   Status updates: {len(status_updates)}")
                        print(f"   Domains mentioned: {list(set(domain_mentions))}")
                        
                        if final_analysis:
                            # Check if it's a proper JSON analysis
                            try:
                                analysis_data = json.loads(final_analysis)
                                if 'executive_summary' in analysis_data:
                                    print(f"✅ SUCCESS: Received structured analysis")
                                    print(f"   Executive Summary: {analysis_data['executive_summary'][:100]}...")
                                    print(f"   Confidence Score: {analysis_data.get('confidence_score', 'N/A')}")
                                    return True
                            except:
                                print(f"✅ Received text analysis (not JSON)")
                                return True
                        else:
                            print(f"❌ FAILED: No final analysis received")
                            return False
                else:
                    print(f"❌ FAILED: Oracle returned HTTP {response.status}")
                    return False
                    
    except asyncio.TimeoutError:
        elapsed = time.time() - start_time
        print(f"❌ FAILED: Timeout after {elapsed:.2f}s")
        return False
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ FAILED: {type(e).__name__}: {e} (after {elapsed:.2f}s)")
        return False

async def main():
    """Run focused A2A communication tests."""
    print("=" * 60)
    print("🔬 A2A Agent-to-Agent Communication Test")
    print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = []
    
    # Test 1: Direct communication with domain agents
    print("\n📋 Test 1: Direct Domain Agent Communication")
    print("-" * 40)
    
    domain_tests = [
        (10902, "Technical Intelligence", "What are microservices best practices?"),
        (10904, "Personal Optimization", "How to optimize developer productivity?"),
        (10905, "Learning Enhancement", "Best way to learn Kubernetes?")
    ]
    
    for port, domain, query in domain_tests:
        result = await test_domain_agent_direct(port, domain, query)
        results.append(("Direct: " + domain, result))
        await asyncio.sleep(1)  # Brief pause between tests
    
    # Test 2: Oracle orchestration
    print("\n📋 Test 2: Oracle Multi-Domain Orchestration")
    print("-" * 40)
    
    result = await test_oracle_to_domain_communication()
    results.append(("Oracle Orchestration", result))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} passed ({(passed/total)*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! A2A communication is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the logs for details.")

if __name__ == "__main__":
    asyncio.run(main())