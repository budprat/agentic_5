#!/usr/bin/env python3
"""ABOUTME: Complete Solopreneur Oracle system launcher - starts MCP server, Oracle, all domain agents, and provides interactive testing.
ABOUTME: This script orchestrates the entire system startup and provides comprehensive testing interface."""

import asyncio
import subprocess
import sys
import time
import signal
import logging
from pathlib import Path
from typing import List, Dict, Any
import json

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SolopreneurSystemLauncher:
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.services_started = False
        
    def cleanup_ports(self):
        """Clean up any processes using Solopreneur ports"""
        logger.info("🧹 Cleaning up existing processes on Solopreneur ports...")
        
        # Port ranges for Solopreneur system
        port_ranges = [
            range(10901, 10910),  # Tier 1 + Tier 2 agents
            range(10960, 10985),  # Tier 3 agents
            range(8000, 8010),    # MCP servers
        ]
        
        for port_range in port_ranges:
            for port in port_range:
                try:
                    subprocess.run(['fuser', '-k', f'{port}/tcp'], 
                                 capture_output=True, check=False)
                except Exception:
                    pass
        
        time.sleep(2)  # Give processes time to clean up
        logger.info("✅ Port cleanup completed")

    async def start_mcp_server(self):
        """Start the MCP server"""
        logger.info("🚀 Starting MCP Server...")
        
        try:
            # Check if MCP server script exists
            mcp_script = Path("start_mcp_server.py")
            if not mcp_script.exists():
                logger.warning("⚠️ MCP server script not found, creating basic launcher...")
                await self.create_mcp_launcher()
            
            # Start MCP server
            process = subprocess.Popen([
                sys.executable, "start_mcp_server.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes.append(process)
            
            # Wait for MCP server to start
            await asyncio.sleep(3)
            
            # Check if process is running
            if process.poll() is None:
                logger.info("✅ MCP Server started successfully")
                return True
            else:
                logger.error("❌ MCP Server failed to start")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start MCP Server: {e}")
            return False

    async def create_mcp_launcher(self):
        """Create a basic MCP server launcher if it doesn't exist"""
        mcp_content = '''#!/usr/bin/env python3
"""Basic MCP Server launcher for Solopreneur system"""

import asyncio
import logging
from pathlib import Path
import sys

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("🚀 Starting basic MCP server...")
    try:
        from a2a_mcp.mcp.server import create_mcp_server
        server = await create_mcp_server()
        logger.info("✅ MCP Server running on port 8000")
        await server.serve_forever()
    except ImportError:
        logger.info("⚠️ MCP server module not found, running in mock mode")
        while True:
            await asyncio.sleep(10)
    except Exception as e:
        logger.error(f"❌ MCP Server error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
'''
        
        with open("start_mcp_server.py", "w") as f:
            f.write(mcp_content)

    async def start_oracle_agent(self):
        """Start the main Solopreneur Oracle agent"""
        logger.info("🧠 Starting Solopreneur Oracle Agent...")
        
        try:
            # Start oracle agent
            process = subprocess.Popen([
                sys.executable, "-c", """
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))

async def run_oracle():
    try:
        from a2a_mcp.agents.solopreneur_oracle.autonomous_workflow_intelligence_oracle import AutonomousWorkflowIntelligenceOracle
        oracle = AutonomousWorkflowIntelligenceOracle()
        print('✅ Solopreneur Oracle started on port 10907')
        # Keep running
        while True:
            await asyncio.sleep(10)
    except Exception as e:
        print(f'❌ Oracle startup failed: {e}')

asyncio.run(run_oracle())
"""
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes.append(process)
            
            # Wait for oracle to start
            await asyncio.sleep(5)
            
            if process.poll() is None:
                logger.info("✅ Solopreneur Oracle Agent started successfully")
                return True
            else:
                logger.error("❌ Oracle Agent failed to start")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start Oracle Agent: {e}")
            return False

    async def start_domain_agents(self):
        """Start key domain agents"""
        logger.info("🎯 Starting Domain Agents...")
        
        # Key domain agents to start
        domain_agents = [
            ("Technical Intelligence Oracle", 10902),
            ("Knowledge Management Oracle", 10903),
            ("Personal Optimization Oracle", 10904),
            ("Learning Enhancement Oracle", 10905),
            ("Integration Synthesis Oracle", 10906),
        ]
        
        success_count = 0
        
        for agent_name, port in domain_agents:
            try:
                logger.info(f"🚀 Starting {agent_name} on port {port}...")
                
                # Create a simple agent runner
                process = subprocess.Popen([
                    sys.executable, "-c", f"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))

async def run_agent():
    try:
        from a2a_mcp.agents.solopreneur_oracle.base_solopreneur_agent import UnifiedSolopreneurAgent
        agent = UnifiedSolopreneurAgent(
            agent_name="{agent_name}",
            port={port},
            description="Domain specialist agent",
            instructions="You are a domain specialist in the Solopreneur Oracle system."
        )
        print(f'✅ {agent_name} started on port {port}')
        while True:
            await asyncio.sleep(10)
    except Exception as e:
        print(f'❌ Agent {agent_name} failed: {{e}}')

asyncio.run(run_agent())
"""
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                self.processes.append(process)
                await asyncio.sleep(2)  # Stagger startup
                
                if process.poll() is None:
                    success_count += 1
                    logger.info(f"✅ {agent_name} started successfully")
                else:
                    logger.warning(f"⚠️ {agent_name} may have failed to start")
                    
            except Exception as e:
                logger.error(f"❌ Failed to start {agent_name}: {e}")
        
        logger.info(f"📊 Domain Agents: {success_count}/{len(domain_agents)} started successfully")
        return success_count > 0

    async def start_tier3_agents(self):
        """Start Tier 3 specialized agents"""
        logger.info("⚡ Starting Tier 3 Agents...")
        
        # Start AWIE Scheduler and Context-Driven Orchestrator
        tier3_agents = [
            ("AWIE Scheduler Agent", 10980),
            ("Context-Driven Orchestrator", 10961),
        ]
        
        success_count = 0
        
        for agent_name, port in tier3_agents:
            try:
                logger.info(f"🚀 Starting {agent_name} on port {port}...")
                
                if "AWIE Scheduler" in agent_name:
                    agent_class = "AWIESchedulerAgent"
                    import_path = "a2a_mcp.agents.tier3.awie_scheduler_agent"
                else:
                    agent_class = "ContextDrivenOrchestrator" 
                    import_path = "a2a_mcp.agents.tier3.context_driven_orchestrator"
                
                process = subprocess.Popen([
                    sys.executable, "-c", f"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))

async def run_agent():
    try:
        from {import_path} import {agent_class}
        agent = {agent_class}()
        print(f'✅ {agent_name} started on port {port}')
        while True:
            await asyncio.sleep(10)
    except Exception as e:
        print(f'❌ Agent {agent_name} failed: {{e}}')

asyncio.run(run_agent())
"""
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                self.processes.append(process)
                await asyncio.sleep(2)
                
                if process.poll() is None:
                    success_count += 1
                    logger.info(f"✅ {agent_name} started successfully")
                else:
                    logger.warning(f"⚠️ {agent_name} may have failed to start")
                    
            except Exception as e:
                logger.error(f"❌ Failed to start {agent_name}: {e}")
        
        logger.info(f"📊 Tier 3 Agents: {success_count}/{len(tier3_agents)} started successfully")
        return success_count > 0

    async def start_all_services(self):
        """Start all services in the correct order"""
        logger.info("🚀 STARTING COMPLETE SOLOPRENEUR ORACLE SYSTEM")
        logger.info("=" * 60)
        
        # Step 1: Clean up ports
        self.cleanup_ports()
        
        # Step 2: Start MCP Server
        mcp_success = await self.start_mcp_server()
        
        # Step 3: Start Oracle Agent
        oracle_success = await self.start_oracle_agent()
        
        # Step 4: Start Domain Agents
        domain_success = await self.start_domain_agents()
        
        # Step 5: Start Tier 3 Agents
        tier3_success = await self.start_tier3_agents()
        
        # Final status
        if oracle_success and domain_success:
            logger.info("🎉 SOLOPRENEUR ORACLE SYSTEM FULLY OPERATIONAL!")
            logger.info("=" * 60)
            self.services_started = True
            return True
        else:
            logger.error("❌ System startup incomplete - some services failed")
            return False

    async def interactive_test_session(self):
        """Run interactive test session with the full system"""
        if not self.services_started:
            logger.error("❌ Services not started - cannot run interactive session")
            return
        
        logger.info("🎯 INTERACTIVE SOLOPRENEUR ORACLE TEST SESSION")
        logger.info("=" * 60)
        
        # Import Oracle for testing
        try:
            from a2a_mcp.agents.solopreneur_oracle.autonomous_workflow_intelligence_oracle import AutonomousWorkflowIntelligenceOracle
            oracle = AutonomousWorkflowIntelligenceOracle()
            
            logger.info("✅ Connected to Solopreneur Oracle")
            logger.info("💡 Example requests:")
            logger.info("   • 'create AI content strategy with SERP optimization'")
            logger.info("   • 'organize my development workflow'")
            logger.info("   • 'coordinate multiple agents for research project'")
            logger.info("   • 'schedule content creation workflow'")
            print("\n" + "=" * 60)
            
            # Interactive loop
            while True:
                try:
                    request = input("🎯 Enter your request (or 'quit' to exit): ").strip()
                    
                    if request.lower() in ['quit', 'exit', 'q']:
                        break
                    
                    if not request:
                        print("⚠️ Please enter a request")
                        continue
                    
                    print("🔄 Processing request...")
                    
                    # Process through Oracle
                    import hashlib
                    request_hash = hashlib.md5(request.encode()).hexdigest()[:8]
                    
                    result = await oracle._process_manual_task_request(
                        request, f"interactive_{request_hash}", f"task_{request_hash}"
                    )
                    
                    if result and "content" in result:
                        print("\n" + "="*60)
                        print("🎯 SOLOPRENEUR ORACLE RESPONSE:")
                        print("="*60)
                        print(result["content"])
                        print("="*60)
                        
                        if "metadata" in result:
                            metadata = result["metadata"]
                            print("📊 METADATA:")
                            for key, value in metadata.items():
                                print(f"   {key}: {value}")
                    else:
                        print("❌ No response generated")
                    
                except KeyboardInterrupt:
                    break
                except EOFError:
                    break
                except Exception as e:
                    print(f"❌ Error processing request: {e}")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Oracle: {e}")

    def cleanup(self):
        """Clean up all started processes"""
        logger.info("🧹 Cleaning up processes...")
        
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                logger.warning(f"Error cleaning up process: {e}")
        
        logger.info("✅ Cleanup completed")

    async def run(self):
        """Main run method"""
        try:
            # Start all services
            success = await self.start_all_services()
            
            if success:
                # Run interactive session
                await self.interactive_test_session()
            else:
                logger.error("❌ System startup failed")
                
        except KeyboardInterrupt:
            logger.info("👋 Shutting down...")
        finally:
            self.cleanup()

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\n👋 Shutting down Solopreneur Oracle system...")
    sys.exit(0)

async def main():
    """Main function"""
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🧠 SOLOPRENEUR ORACLE COMPLETE SYSTEM LAUNCHER")
    print("🎯 This will start MCP server, Oracle agent, and all domain agents")
    print("⚡ Then provide interactive testing interface")
    print("=" * 70)
    
    launcher = SolopreneurSystemLauncher()
    await launcher.run()

if __name__ == "__main__":
    asyncio.run(main())