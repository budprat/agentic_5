#!/usr/bin/env python3
# ABOUTME: Tests the complete AI Solopreneur Oracle System using A2A protocol
# ABOUTME: Sends queries to the master oracle and displays comprehensive results

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime

async def query_solopreneur_oracle(query: str):
    """Send a query to the Solopreneur Oracle using A2A protocol."""
    
    # Master Oracle on port 10901
    url = "http://localhost:10901"
    
    # Create proper A2A JSON-RPC request with message/stream method
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
                        "text": query
                    }
                ],
                "messageId": message_id,
                "kind": "message"
            },
            "metadata": {}
        }
    }
    
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"{'='*60}")
    print(f"Sending request to Solopreneur Oracle at {url}")
    
    timeout = aiohttp.ClientTimeout(total=120)  # 2 minute timeout for complex queries
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.post(url, json=json_rpc_request) as response:
                print(f"Response status: {response.status}")
                
                if response.status == 200:
                    content_type = response.headers.get('Content-Type', '')
                    
                    if 'text/event-stream' in content_type:
                        print("✓ Received SSE stream response")
                        
                        task_id = None
                        final_result = None
                        
                        # Read SSE events
                        async for line in response.content:
                            if line:
                                line_str = line.decode('utf-8').strip()
                                if line_str.startswith('data: '):
                                    data = line_str[6:]  # Remove 'data: ' prefix
                                    try:
                                        event = json.loads(data)
                                        
                                        if 'result' in event and isinstance(event['result'], dict):
                                            result = event['result']
                                            
                                            # Initial task submission
                                            if result.get('kind') == 'task':
                                                task_id = result.get('id')
                                                print(f"\nTask created: {task_id}")
                                                print(f"Status: {result.get('status', {}).get('state')}")
                                            
                                            # Status updates
                                            elif result.get('kind') == 'status-update':
                                                status = result.get('status', {})
                                                print(f"\nStatus update: {status.get('state')}")
                                                if result.get('final'):
                                                    print("✓ Task completed")
                                            
                                            # Final message with analysis
                                            elif result.get('kind') == 'streaming-response':
                                                if result.get('final'):
                                                    # This is the final synthesis
                                                    message = result.get('message', {})
                                                    parts = message.get('parts', [])
                                                    for part in parts:
                                                        if part.get('kind') == 'text':
                                                            final_result = part.get('text')
                                                            break
                                                else:
                                                    # Progress update
                                                    message = result.get('message', {})
                                                    parts = message.get('parts', [])
                                                    for part in parts:
                                                        if part.get('kind') == 'text':
                                                            print(f"Progress: {part.get('text')}")
                                                            
                                    except json.JSONDecodeError as e:
                                        print(f"Failed to parse SSE data: {e}")
                        
                        # Display final result
                        if final_result:
                            print(f"\n{'='*60}")
                            print("SOLOPRENEUR ORACLE ANALYSIS")
                            print(f"{'='*60}")
                            
                            try:
                                # Try to parse as JSON for structured display
                                analysis = json.loads(final_result)
                                
                                # Executive Summary
                                if 'executive_summary' in analysis:
                                    print(f"\n📋 EXECUTIVE SUMMARY:")
                                    print(f"   {analysis['executive_summary']}")
                                    print(f"   Confidence: {analysis.get('confidence_score', 0)*100:.0f}%")
                                
                                # Technical Assessment
                                if 'technical_assessment' in analysis:
                                    tech = analysis['technical_assessment']
                                    print(f"\n🔧 TECHNICAL ASSESSMENT:")
                                    print(f"   Feasibility: {tech.get('feasibility_score', 0)}%")
                                    print(f"   Complexity: {tech.get('implementation_complexity', 'N/A')}")
                                    print(f"   Architecture: {', '.join(tech.get('architecture_recommendations', []))}")
                                
                                # Personal Optimization
                                if 'personal_optimization' in analysis:
                                    personal = analysis['personal_optimization']
                                    print(f"\n🧠 PERSONAL OPTIMIZATION:")
                                    print(f"   Energy Impact: {personal.get('energy_impact', 'N/A')}")
                                    print(f"   Cognitive Load: {personal.get('cognitive_load', 'N/A')}")
                                    print(f"   Sustainability: {personal.get('sustainability_score', 0)}%")
                                
                                # Strategic Insights
                                if 'strategic_insights' in analysis:
                                    print(f"\n💡 KEY INSIGHTS:")
                                    for insight in analysis['strategic_insights'][:3]:  # Top 3
                                        print(f"   • {insight.get('insight', 'N/A')} (confidence: {insight.get('confidence', 0)*100:.0f}%)")
                                
                                # Action Plan
                                if 'action_plan' in analysis:
                                    plan = analysis['action_plan']
                                    print(f"\n📅 ACTION PLAN:")
                                    print(f"   Immediate: {', '.join(plan.get('immediate_actions', [])[:2])}")
                                    print(f"   Short-term: {', '.join(plan.get('short_term_goals', [])[:2])}")
                                    print(f"   Vision: {plan.get('long_term_vision', 'N/A')}")
                                
                            except json.JSONDecodeError:
                                # Display as plain text if not JSON
                                print(final_result)
                        else:
                            print("\n⚠️ No analysis result received")
                    else:
                        # Regular JSON response (error)
                        result = await response.json()
                        if 'error' in result:
                            print(f"\n❌ Error: {result['error'].get('message', 'Unknown error')}")
                        else:
                            print(f"\nUnexpected response: {json.dumps(result, indent=2)}")
                else:
                    text = await response.text()
                    print(f"\n❌ HTTP Error {response.status}: {text}")
                    
        except asyncio.TimeoutError:
            print("\n⏱️ Request timed out (120s)")
        except Exception as e:
            print(f"\n❌ Error: {e}")

async def main():
    """Run comprehensive system tests."""
    print("AI SOLOPRENEUR ORACLE SYSTEM TEST")
    print("=" * 60)
    print("Testing the complete 3-tier Oracle architecture")
    print("Master Oracle -> Domain Specialists -> Intelligence Synthesis")
    
    # Test queries covering different domains
    test_queries = [
        # Technical + Personal optimization query
        "How can I architect a scalable SaaS application while maintaining work-life balance as a solo developer?",
        
        # Learning + Knowledge management query
        # "What's the most efficient way to learn Kubernetes for deploying my AI applications?",
        
        # Integration + Technical query
        # "How should I integrate MCP tools with my existing development workflow for maximum productivity?",
    ]
    
    for query in test_queries:
        await query_solopreneur_oracle(query)
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())