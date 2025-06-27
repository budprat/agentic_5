#!/usr/bin/env python3
"""Test Market Oracle agents individually without full startup script."""

import asyncio
import subprocess
import time
import aiohttp
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_mcp_server():
    """Start the MCP server."""
    print("\n🚀 Starting MCP Server...")
    cmd = [
        ".venv/bin/python", "-m", "a2a_mcp", 
        "--run", "mcp-server", 
        "--transport", "sse", 
        "--host", "localhost", 
        "--port", "10100"
    ]
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    await asyncio.sleep(5)
    
    if process.poll() is None:
        print("✅ MCP Server started")
        return process
    else:
        print("❌ MCP Server failed to start")
        return None

async def start_agent(name, card_path, port):
    """Start an individual agent."""
    print(f"\n🤖 Starting {name} on port {port}...")
    
    cmd = [
        ".venv/bin/python", "-m", "a2a_mcp.agents",
        "--agent-card", card_path,
        "--port", str(port)
    ]
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for agent to start
    await asyncio.sleep(3)
    
    if process.poll() is None:
        # Test agent health
        try:
            async with aiohttp.ClientSession() as session:
                url = f"http://localhost:{port}/v1/agent/info"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        print(f"✅ {name} started and healthy")
                        return process
        except:
            pass
            
    print(f"❌ {name} failed to start")
    if process.poll() is None:
        process.terminate()
    return None

async def test_agent_query(name, port, query):
    """Test an agent with a query."""
    print(f"\n📊 Testing {name} with query: {query}")
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"http://localhost:{port}/v1/agent/invoke"
            payload = {
                "query": query,
                "session_id": f"test_{name.lower().replace(' ', '_')}"
            }
            
            async with session.post(
                url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                
                if response.status == 200:
                    # Handle streaming response
                    result_data = None
                    async for line in response.content:
                        if line:
                            try:
                                line_str = line.decode('utf-8').strip()
                                if line_str.startswith('data: '):
                                    data = json.loads(line_str[6:])
                                    
                                    if data.get('is_task_complete'):
                                        if data.get('response_type') == 'data':
                                            result_data = data['content']
                                        else:
                                            result_data = {"message": data.get('content', 'No content')}
                                        break
                                    else:
                                        print(f"  ⏳ {data.get('content', '')}")
                                        
                            except json.JSONDecodeError:
                                continue
                    
                    if result_data:
                        print(f"\n✅ {name} Response:")
                        print(json.dumps(result_data, indent=2)[:500] + "..." if len(json.dumps(result_data)) > 500 else "")
                        return True
                else:
                    print(f"❌ Error from {name}: {response.status}")
                    
    except Exception as e:
        print(f"❌ Error testing {name}: {e}")
    
    return False

async def main():
    """Test Market Oracle agents individually."""
    print("\n" + "="*80)
    print("🔮 MARKET ORACLE AGENT TESTING")
    print("="*80)
    
    processes = []
    
    try:
        # Start MCP Server
        mcp_process = await start_mcp_server()
        if mcp_process:
            processes.append(mcp_process)
        else:
            print("Cannot continue without MCP server")
            return
        
        # Define agents to test
        agents = [
            {
                "name": "Oracle Prime",
                "card": "agent_cards/oracle_prime_agent.json",
                "port": 10501,
                "query": "Analyze TSLA for investment opportunity"
            },
            {
                "name": "Sentiment Seeker",
                "card": "agent_cards/sentiment_seeker_agent.json",
                "port": 10503,
                "query": "Analyze Reddit sentiment for NVDA"
            },
            {
                "name": "Technical Prophet",
                "card": "agent_cards/technical_prophet_agent.json",
                "port": 10504,
                "query": "Perform technical analysis on AAPL"
            },
            {
                "name": "Risk Guardian",
                "card": "agent_cards/risk_guardian_agent.json",
                "port": 10505,
                "query": "Assess portfolio risk for adding MSFT position"
            }
        ]
        
        # Start and test each agent
        for agent in agents:
            process = await start_agent(agent["name"], agent["card"], agent["port"])
            if process:
                processes.append(process)
                await asyncio.sleep(2)
                
                # Test the agent
                success = await test_agent_query(agent["name"], agent["port"], agent["query"])
                if not success:
                    print(f"⚠️  {agent['name']} started but query failed")
            else:
                print(f"⚠️  Skipping {agent['name']} test")
        
        print("\n" + "="*80)
        print("✅ AGENT TESTING COMPLETE")
        print("="*80)
        
        # Keep running for a bit to see any output
        print("\nAgents running. Press Ctrl+C to stop...")
        await asyncio.sleep(10)
        
    except KeyboardInterrupt:
        print("\n\nShutting down agents...")
    finally:
        # Cleanup
        for process in processes:
            if process.poll() is None:
                process.terminate()
                process.wait()
        print("All agents stopped.")

if __name__ == "__main__":
    asyncio.run(main())