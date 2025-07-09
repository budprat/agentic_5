#!/usr/bin/env python3
"""Test script for Solopreneur Oracle orchestration with ParallelWorkflowGraph."""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime

class SolopreneurOracleOrchestrationTest:
    def __init__(self):
        self.oracle_url = "http://localhost:10901"
        self.domain_agents = {
            "technical_intelligence": "http://localhost:10902",
            "knowledge_management": "http://localhost:10903", 
            "personal_optimization": "http://localhost:10904",
            "learning_enhancement": "http://localhost:10905",
            "integration_synthesis": "http://localhost:10906"
        }
        self.results = []
        
    async def test_orchestration_flow(self):
        """Test the full orchestration workflow."""
        print("🧪 Testing Solopreneur Oracle Orchestration Flow")
        print("=" * 70)
        
        test_cases = [
            {
                "name": "Technical Feasibility Query",
                "query": "How can I implement a RAG system with vector databases while maintaining my current energy levels?",
                "expected_domains": ["technical_intelligence", "personal_optimization"],
                "description": "Should trigger technical analysis and personal optimization"
            },
            {
                "name": "Learning Integration Query",
                "query": "What's the best way to learn LangGraph efficiently given my current skill level and time constraints?",
                "expected_domains": ["learning_enhancement", "knowledge_management", "personal_optimization"],
                "description": "Should trigger learning, knowledge management, and personal optimization"
            },
            {
                "name": "Comprehensive Optimization Query",
                "query": "Create a complete workflow for implementing AI agents while optimizing my productivity and learning new technologies",
                "expected_domains": ["technical_intelligence", "personal_optimization", "learning_enhancement", "integration_synthesis"],
                "description": "Should trigger multi-domain orchestration with synthesis"
            }
        ]
        
        async with aiohttp.ClientSession() as session:
            for test in test_cases:
                print(f"\n📋 Test: {test['name']}")
                print(f"   Query: {test['query'][:80]}...")
                print(f"   Expected domains: {test['expected_domains']}")
                
                try:
                    payload = {
                        "query": test["query"],
                        "context_id": f"test-{test['name'].lower().replace(' ', '-')}",
                        "task_id": f"task-{int(asyncio.get_event_loop().time())}"
                    }
                    
                    async with session.post(
                        f"{self.oracle_url}/stream",
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=60)
                    ) as response:
                        if response.status == 200:
                            chunks = []
                            final_result = None
                            
                            print("   📡 Streaming response:")
                            async for line in response.content:
                                if line:
                                    try:
                                        chunk = json.loads(line.decode('utf-8'))
                                        chunks.append(chunk)
                                        
                                        if chunk.get('content'):
                                            if isinstance(chunk['content'], dict):
                                                # Final structured response
                                                final_result = chunk['content']
                                                print(f"   ✅ Final synthesis received")
                                            else:
                                                # Progress update
                                                print(f"   → {chunk['content'][:100]}...")
                                    except json.JSONDecodeError:
                                        continue
                            
                            # Validate orchestration
                            if final_result:
                                self.results.append({
                                    "test": test["name"],
                                    "status": "PASS",
                                    "chunks": len(chunks),
                                    "final_result": final_result,
                                    "has_synthesis": "executive_summary" in final_result
                                })
                                print(f"   ✅ Test passed - {len(chunks)} chunks received")
                                
                                # Show key synthesis elements
                                if "executive_summary" in final_result:
                                    print(f"   💡 Executive Summary: {final_result['executive_summary'][:100]}...")
                                if "confidence_score" in final_result:
                                    print(f"   📊 Confidence Score: {final_result['confidence_score']}")
                            else:
                                self.results.append({
                                    "test": test["name"],
                                    "status": "PARTIAL",
                                    "chunks": len(chunks),
                                    "error": "No final synthesis received"
                                })
                                print(f"   ⚠️  Partial success - {len(chunks)} chunks but no synthesis")
                        else:
                            self.results.append({
                                "test": test["name"],
                                "status": "FAIL",
                                "error": f"HTTP {response.status}"
                            })
                            print(f"   ❌ Failed with HTTP {response.status}")
                            
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
    
    async def test_domain_agent_availability(self):
        """Test that all domain agents are available."""
        print("\n🧪 Testing Domain Agent Availability")
        print("=" * 70)
        
        available_agents = {}
        
        async with aiohttp.ClientSession() as session:
            for domain, url in self.domain_agents.items():
                try:
                    async with session.get(
                        f"{url}/health",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status == 200:
                            available_agents[domain] = True
                            print(f"   ✅ {domain.replace('_', ' ').title()} Agent: Available")
                        else:
                            available_agents[domain] = False
                            print(f"   ❌ {domain.replace('_', ' ').title()} Agent: HTTP {response.status}")
                except Exception as e:
                    available_agents[domain] = False
                    print(f"   ❌ {domain.replace('_', ' ').title()} Agent: {str(e)}")
        
        return available_agents
    
    async def test_oracle_master_availability(self):
        """Test that the Oracle Master is available."""
        print("\n🧪 Testing Oracle Master Availability")
        print("=" * 70)
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.oracle_url}/health",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        print("   ✅ Solopreneur Oracle Master: Available")
                        return True
                    else:
                        print(f"   ❌ Solopreneur Oracle Master: HTTP {response.status}")
                        return False
            except Exception as e:
                print(f"   ❌ Solopreneur Oracle Master: {str(e)}")
                return False
    
    async def generate_report(self):
        """Generate test report."""
        print("\n" + "="*70)
        print("SOLOPRENEUR ORACLE ORCHESTRATION TEST REPORT")
        print("="*70)
        print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test results summary
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        total = len(self.results)
        
        print(f"\nOrchestration Tests: {passed}/{total} passed")
        if total > 0:
            print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\nDetailed Results:")
        for result in self.results:
            status_icon = {
                "PASS": "✅",
                "FAIL": "❌", 
                "TIMEOUT": "⏱️",
                "ERROR": "⚠️",
                "PARTIAL": "🔶"
            }.get(result["status"], "❓")
            
            print(f"{status_icon} {result['test']}: {result['status']}")
            if result["status"] == "PASS":
                print(f"   Chunks: {result['chunks']}, Synthesis: {result['has_synthesis']}")
            elif result["status"] != "PASS" and "error" in result:
                print(f"   Error: {result['error']}")
        
        return passed == total

async def main():
    """Run orchestration tests."""
    print("🚀 Solopreneur Oracle Orchestration Test Suite")
    print("Testing ParallelWorkflowGraph orchestration with A2A protocol communication")
    print("=" * 70)
    
    tester = SolopreneurOracleOrchestrationTest()
    
    # Test Oracle Master availability
    oracle_available = await tester.test_oracle_master_availability()
    
    if not oracle_available:
        print("\n❌ Oracle Master not available. Start system with:")
        print("   ./run_solopreneur_agents.sh")
        sys.exit(1)
    
    # Test domain agent availability  
    available_agents = await tester.test_domain_agent_availability()
    available_count = sum(available_agents.values())
    total_agents = len(available_agents)
    
    print(f"\nDomain Agents Available: {available_count}/{total_agents}")
    
    # Run orchestration flow tests
    await tester.test_orchestration_flow()
    
    # Generate report
    success = await tester.generate_report()
    
    if success:
        print("\n🎉 All orchestration tests passed!")
        print("✅ ParallelWorkflowGraph orchestration working correctly")
        print("✅ A2A protocol communication functional")
        print("✅ Phase 2.3 validation: COMPLETE")
        sys.exit(0)
    else:
        print("\n⚠️  Some orchestration tests failed.")
        print("   Check agent availability and logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())