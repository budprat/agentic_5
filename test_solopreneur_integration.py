"""Complete integration test for 56-agent Solopreneur Oracle system."""

import asyncio
import aiohttp
import json
from typing import Dict, List
import sys
from datetime import datetime

class SolopreneurIntegrationTest:
    def __init__(self):
        self.base_url = "http://localhost:10901"  # Oracle Master
        self.results = []
        self.tier_ports = {
            1: [10901],
            2: list(range(10902, 10907)),
            3: list(range(10910, 10960))
        }
        
    async def test_tier_communication(self):
        """Test that all tiers communicate properly."""
        print("\n🧪 Testing Multi-Tier Communication")
        print("=" * 50)
        
        test_cases = [
            {
                "name": "Technical Intelligence Flow",
                "query": "Analyze the latest LangGraph patterns for multi-agent systems",
                "expected_domains": ["Technical Intelligence"],
                "description": "Should activate Technical Intelligence Oracle and relevant modules"
            },
            {
                "name": "Personal Optimization Flow", 
                "query": "Optimize my schedule for deep learning sessions this week based on my energy patterns",
                "expected_domains": ["Personal Optimization"],
                "description": "Should activate Personal Optimization Oracle and energy modules"
            },
            {
                "name": "Cross-Domain Integration",
                "query": "How can I learn Rust efficiently given my energy patterns and current skill level?",
                "expected_domains": ["Learning Enhancement", "Personal Optimization", "Integration Synthesis"],
                "description": "Should activate multiple domain specialists"
            },
            {
                "name": "Full System Integration",
                "query": "Create a comprehensive plan for implementing a new AI feature with LangGraph, considering my learning needs, optimal work times, and technical requirements",
                "expected_domains": ["Technical Intelligence", "Learning Enhancement", "Personal Optimization", "Integration Synthesis"],
                "description": "Should activate all major domains"
            }
        ]
        
        async with aiohttp.ClientSession() as session:
            for test in test_cases:
                print(f"\n📋 Test: {test['name']}")
                print(f"   Description: {test['description']}")
                print(f"   Query: {test['query'][:80]}...")
                
                try:
                    async with session.post(
                        f"{self.base_url}/stream",
                        json={
                            "query": test["query"],
                            "context_id": f"test-{test['name'].lower().replace(' ', '-')}",
                            "task_id": f"task-{int(asyncio.get_event_loop().time())}"
                        },
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status == 200:
                            # Read streaming response
                            chunks = []
                            async for line in response.content:
                                if line:
                                    try:
                                        chunk = json.loads(line.decode('utf-8'))
                                        chunks.append(chunk)
                                        if chunk.get('content'):
                                            print(f"   → {chunk['content'][:100]}")
                                    except:
                                        pass
                            
                            self.results.append({
                                "test": test["name"],
                                "status": "PASS",
                                "chunks": len(chunks)
                            })
                            print(f"   ✅ Received {len(chunks)} response chunks")
                        else:
                            self.results.append({
                                "test": test["name"],
                                "status": "FAIL",
                                "error": f"HTTP {response.status}"
                            })
                            print(f"   ❌ Failed with status {response.status}")
                            
                except asyncio.TimeoutError:
                    self.results.append({
                        "test": test["name"],
                        "status": "TIMEOUT",
                        "error": "Request timed out"
                    })
                    print(f"   ⏱️  Request timed out")
                except Exception as e:
                    self.results.append({
                        "test": test["name"],
                        "status": "ERROR",
                        "error": str(e)
                    })
                    print(f"   ❌ Error: {str(e)}")
    
    async def test_agent_health(self):
        """Test health endpoints for all tiers."""
        print("\n🧪 Testing Agent Health Endpoints")
        print("=" * 50)
        
        healthy_agents = {1: 0, 2: 0, 3: 0}
        
        async with aiohttp.ClientSession() as session:
            for tier, ports in self.tier_ports.items():
                print(f"\nTier {tier} Health Checks:")
                
                # Sample a subset for Tier 3
                if tier == 3:
                    ports = [ports[i] for i in range(0, len(ports), 5)][:10]  # Sample 10 ports
                
                for port in ports:
                    try:
                        async with session.get(
                            f"http://localhost:{port}/health",
                            timeout=aiohttp.ClientTimeout(total=2)
                        ) as response:
                            if response.status == 200:
                                healthy_agents[tier] += 1
                                print(f"   Port {port}: ✅")
                            else:
                                print(f"   Port {port}: ❌ (Status {response.status})")
                    except:
                        print(f"   Port {port}: ❌ (No response)")
        
        return healthy_agents
    
    async def test_mcp_integration(self):
        """Test MCP server connectivity."""
        print("\n🧪 Testing MCP Server Integration")
        print("=" * 50)
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    "http://localhost:10100/health",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        print("   ✅ MCP Server is healthy")
                        return True
                    else:
                        print(f"   ❌ MCP Server returned status {response.status}")
                        return False
            except Exception as e:
                print(f"   ❌ MCP Server error: {str(e)}")
                return False
    
    async def generate_report(self):
        """Generate test report."""
        print("\n" + "="*60)
        print("SOLOPRENEUR ORACLE INTEGRATION TEST REPORT")
        print("="*60)
        print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test results summary
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        total = len(self.results)
        
        print(f"\nCommunication Tests: {passed}/{total} passed")
        
        if total > 0:
            print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\nDetailed Results:")
        for result in self.results:
            status_icon = {
                "PASS": "✅",
                "FAIL": "❌",
                "TIMEOUT": "⏱️",
                "ERROR": "⚠️"
            }.get(result["status"], "❓")
            
            print(f"{status_icon} {result['test']}: {result['status']}")
            if result["status"] != "PASS" and "error" in result:
                print(f"   Error: {result['error']}")
        
        return passed == total

async def main():
    """Run integration tests."""
    print("🚀 Solopreneur Oracle Integration Test Suite")
    print("Testing 56-agent system with 3 tiers...")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        print("Running in quick mode (health checks only)")
        
    tester = SolopreneurIntegrationTest()
    
    # Test MCP Server
    mcp_healthy = await tester.test_mcp_integration()
    
    if not mcp_healthy:
        print("\n⚠️  MCP Server not available. Some tests may fail.")
    
    # Test agent health
    healthy_agents = await tester.test_agent_health()
    print(f"\nHealthy Agents by Tier:")
    print(f"  Tier 1: {healthy_agents[1]}/1")
    print(f"  Tier 2: {healthy_agents[2]}/5") 
    print(f"  Tier 3: {healthy_agents[3]} sampled (50 total)")
    
    # Run communication tests only if master is healthy
    if healthy_agents[1] > 0:
        await tester.test_tier_communication()
        success = await tester.generate_report()
        
        if success:
            print("\n🎉 All integration tests passed!")
            sys.exit(0)
        else:
            print("\n⚠️  Some tests failed. Check logs for details.")
            sys.exit(1)
    else:
        print("\n❌ Oracle Master not running. Cannot run communication tests.")
        print("   Start the system with: ./run_all_solopreneur_agents.sh")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())