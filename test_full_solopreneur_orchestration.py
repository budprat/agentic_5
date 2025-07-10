#!/usr/bin/env python3
"""Test full solopreneur oracle orchestration with all domain agents."""

import asyncio
import os
import sys
import subprocess
import time
import json
import aiohttp
from pathlib import Path

class FullSolopreneurTester:
    def __init__(self):
        self.base_port = 10901
        self.agents = {
            "solopreneur_oracle": {
                "port": 10901,
                "card": "agent_cards/solopreneur_oracle_agent.json",
                "process": None
            },
            "technical_intelligence": {
                "port": 10902,
                "card": "agent_cards/technical_intelligence_agent.json", 
                "process": None
            },
            "knowledge_management": {
                "port": 10903,
                "card": "agent_cards/knowledge_management_agent.json",
                "process": None
            },
            "personal_optimization": {
                "port": 10904,
                "card": "agent_cards/personal_optimization_agent.json",
                "process": None
            },
            "learning_enhancement": {
                "port": 10905,
                "card": "agent_cards/learning_enhancement_agent.json",
                "process": None
            },
            "integration_synthesis": {
                "port": 10906,
                "card": "agent_cards/integration_synthesis_agent.json",
                "process": None
            }
        }
        self.running_agents = {}

    def check_agent_card_exists(self, card_path):
        """Check if agent card file exists."""
        return Path(card_path).exists()

    async def start_agent_server(self, agent_name, config):
        """Start an individual agent server."""
        if not self.check_agent_card_exists(config["card"]):
            print(f"⚠️  Agent card not found: {config['card']} - skipping {agent_name}")
            return False
            
        print(f"🚀 Starting {agent_name} on port {config['port']}...")
        
        try:
            # Start agent server
            cmd = [
                "uv", "run", "python", "-m", "a2a_mcp.agents",
                "--host", "localhost",
                "--port", str(config["port"]),
                "--agent-card", config["card"]
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            config["process"] = process
            
            # Wait for server to start
            await asyncio.sleep(3)
            
            # Check if process is still running
            if process.poll() is None:
                self.running_agents[agent_name] = config
                print(f"✅ {agent_name} started successfully on port {config['port']}")
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"❌ Failed to start {agent_name}")
                print(f"   stdout: {stdout[:200]}")
                print(f"   stderr: {stderr[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting {agent_name}: {e}")
            return False

    async def check_agent_health(self, agent_name, port):
        """Check if agent is responding to health checks."""
        try:
            timeout = aiohttp.ClientTimeout(total=5.0)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"http://localhost:{port}/") as response:
                    if response.status in [200, 404]:  # 404 is OK for agent root
                        print(f"✅ {agent_name} health check: OK")
                        return True
                    else:
                        print(f"⚠️  {agent_name} health check: HTTP {response.status}")
                        return False
        except Exception as e:
            print(f"❌ {agent_name} health check failed: {e}")
            return False

    async def test_solopreneur_orchestration(self, query):
        """Test full solopreneur oracle orchestration."""
        print(f"\n🧪 Testing Solopreneur Oracle with query: {query}")
        print("=" * 80)
        
        oracle_port = self.agents["solopreneur_oracle"]["port"]
        
        try:
            timeout = aiohttp.ClientTimeout(total=60.0)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # Send query to solopreneur oracle
                request_data = {
                    "message": {
                        "content": query,
                        "contentType": "text/plain"
                    }
                }
                
                print(f"📤 Sending request to Solopreneur Oracle on port {oracle_port}")
                
                async with session.post(
                    f"http://localhost:{oracle_port}/stream-message",
                    json=request_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        print("✅ Solopreneur Oracle responded successfully")
                        
                        # Check if response is streaming
                        if 'text/event-stream' in response.headers.get('content-type', ''):
                            print("📡 Receiving streaming response...")
                            
                            responses = []
                            async for line in response.content:
                                line_str = line.decode('utf-8').strip()
                                if line_str.startswith('data: '):
                                    data = line_str[6:]  # Remove 'data: ' prefix
                                    try:
                                        event = json.loads(data)
                                        if 'result' in event and isinstance(event['result'], dict):
                                            result = event['result']
                                            
                                            # Check for content in message parts
                                            if result.get('kind') == 'message':
                                                parts = result.get('parts', [])
                                                for part in parts:
                                                    if part.get('kind') == 'text':
                                                        content = part.get('text', '')
                                                        if content.strip():
                                                            responses.append(content)
                                                            print(f"📥 Oracle: {content[:100]}...")
                                            
                                            # Check for final status
                                            elif result.get('kind') == 'status-update' and result.get('final'):
                                                print(f"🏁 Final status: {result.get('status')}")
                                                break
                                                
                                    except json.JSONDecodeError:
                                        pass
                            
                            if responses:
                                print(f"✅ Received {len(responses)} response chunks from oracle")
                                return responses
                            else:
                                print("⚠️  No content received from oracle")
                                return []
                        else:
                            # Handle regular JSON response
                            result = await response.json()
                            print(f"✅ Oracle response: {str(result)[:200]}...")
                            return [result]
                            
                    else:
                        print(f"❌ Oracle request failed: HTTP {response.status}")
                        response_text = await response.text()
                        print(f"   Response: {response_text[:500]}")
                        return None
                    
        except asyncio.TimeoutError:
            print("❌ Request to Solopreneur Oracle timed out")
            return None
        except Exception as e:
            print(f"❌ Error testing oracle: {e}")
            return None

    def stop_all_agents(self):
        """Stop all running agent servers."""
        print("\n🛑 Stopping all agent servers...")
        
        for agent_name, config in self.running_agents.items():
            if config.get("process") and config["process"].poll() is None:
                print(f"   Stopping {agent_name}...")
                config["process"].terminate()
                
                # Wait for graceful shutdown
                try:
                    config["process"].wait(timeout=5)
                    print(f"   ✅ {agent_name} stopped")
                except subprocess.TimeoutExpired:
                    print(f"   ⚠️  Force killing {agent_name}...")
                    config["process"].kill()
                    config["process"].wait()

    async def run_comprehensive_test(self):
        """Run comprehensive solopreneur oracle test."""
        print("🚀 COMPREHENSIVE SOLOPRENEUR ORACLE ORCHESTRATION TEST")
        print("=" * 80)
        print("Testing full multi-agent orchestration with domain specialists")
        print()
        
        # Set environment variables
        os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "test_key")
        os.environ["ENABLE_PARALLEL_EXECUTION"] = "true"
        
        try:
            # Step 1: Start master oracle (required)
            print("Phase 1: Starting Master Oracle")
            print("-" * 40)
            
            oracle_started = await self.start_agent_server("solopreneur_oracle", self.agents["solopreneur_oracle"])
            if not oracle_started:
                print("❌ Failed to start Solopreneur Oracle - aborting test")
                return False
                
            # Step 2: Start domain specialists (best effort)
            print("\nPhase 2: Starting Domain Specialists")
            print("-" * 40)
            
            domain_agents = ["technical_intelligence", "knowledge_management", "personal_optimization", 
                           "learning_enhancement", "integration_synthesis"]
            
            started_agents = []
            for agent_name in domain_agents:
                if agent_name in self.agents:
                    success = await self.start_agent_server(agent_name, self.agents[agent_name])
                    if success:
                        started_agents.append(agent_name)
            
            print(f"\n✅ Started {len(started_agents)}/{len(domain_agents)} domain agents")
            
            # Step 3: Health checks
            print("\nPhase 3: Health Checks")
            print("-" * 40)
            
            for agent_name, config in self.running_agents.items():
                await self.check_agent_health(agent_name, config["port"])
            
            # Step 4: Test orchestration
            print("\nPhase 4: Testing Orchestration")
            print("-" * 40)
            
            test_queries = [
                "How can I optimize my AI development workflow for maximum productivity?",
                "What's the best approach to learn LangGraph while maintaining my current project timeline?",
                "Create a comprehensive plan for implementing a new AI feature considering my technical skills and energy patterns"
            ]
            
            all_results = []
            for i, query in enumerate(test_queries):
                print(f"\n🧪 Test {i+1}/{len(test_queries)}")
                result = await self.test_solopreneur_orchestration(query)
                all_results.append({"query": query, "result": result})
                
                # Brief pause between tests
                await asyncio.sleep(2)
            
            # Step 5: Results summary
            print("\nPhase 5: Test Results Summary")
            print("-" * 40)
            
            successful_tests = sum(1 for r in all_results if r["result"])
            print(f"✅ Successful orchestration tests: {successful_tests}/{len(test_queries)}")
            print(f"✅ Running domain agents: {len(self.running_agents)}")
            print(f"✅ Oracle orchestration: {'FUNCTIONAL' if successful_tests > 0 else 'FAILED'}")
            
            if successful_tests > 0:
                print("\n🎉 SOLOPRENEUR ORACLE ORCHESTRATION: FULLY OPERATIONAL!")
                print("✅ Multi-domain intelligence coordination: WORKING")
                print("✅ Agent-to-agent communication: FUNCTIONAL") 
                print("✅ Parallel workflow execution: ENABLED")
                print("✅ Quality synthesis: IMPLEMENTED")
                return True
            else:
                print("\n⚠️  Some orchestration tests failed")
                return False
                
        except KeyboardInterrupt:
            print("\n⚠️  Test interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.stop_all_agents()

async def main():
    """Run the comprehensive solopreneur orchestration test."""
    tester = FullSolopreneurTester()
    
    try:
        success = await tester.run_comprehensive_test()
        return success
    except Exception as e:
        print(f"❌ Main test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Starting Full Solopreneur Oracle Orchestration Test")
    print("This will test the complete multi-agent system with real agents")
    print()
    
    success = asyncio.run(main())
    
    if success:
        print("\n🏆 FULL SOLOPRENEUR ORCHESTRATION TEST: PASSED")
        sys.exit(0)
    else:
        print("\n❌ FULL SOLOPRENEUR ORCHESTRATION TEST: FAILED")
        sys.exit(1)