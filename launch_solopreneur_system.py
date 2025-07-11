#!/usr/bin/env python3
"""ABOUTME: Production-grade Solopreneur Oracle system launcher with comprehensive process management.
ABOUTME: Launches MCP server, Oracle, and all 76 domain agents with health monitoring and auto-restart capabilities."""

import asyncio
import json
import logging
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure comprehensive logging
class ColoredFormatter(logging.Formatter):
    """Colored log formatter for better visual output"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green 
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)

# Setup logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Console handler with colors
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(ColoredFormatter(
    '%(asctime)s - %(levelname)s - %(message)s'
))

# File handler for detailed logs
file_handler = logging.FileHandler(log_dir / "system_launcher.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))

# Configure root logger
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[console_handler, file_handler]
)
logger = logging.getLogger(__name__)

class ProcessManager:
    """Manages agent processes with health monitoring and auto-restart"""
    
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.process_configs: Dict[str, Dict] = {}
        self.pid_file = Path(".solopreneur_pids.json")
        self.shutdown_requested = False
        
    def add_process(self, name: str, process: subprocess.Popen, config: Dict):
        """Add a process to be managed"""
        self.processes[name] = process
        self.process_configs[name] = config
        logger.info(f"✅ Added process {name} (PID: {process.pid})")
        
    def save_pids(self):
        """Save process PIDs to file for external monitoring"""
        pid_data = {
            name: {
                "pid": proc.pid,
                "config": config,
                "started": datetime.now().isoformat()
            }
            for name, proc in self.processes.items()
            if proc.poll() is None
        }
        
        with open(self.pid_file, 'w') as f:
            json.dump(pid_data, f, indent=2)
            
    def is_process_healthy(self, name: str, process: subprocess.Popen) -> bool:
        """Check if a process is healthy"""
        if process.poll() is not None:
            return False
            
        # For processes with ports, try HTTP health check
        config = self.process_configs.get(name, {})
        port = config.get('port')
        
        if port:
            try:
                response = requests.get(f"http://localhost:{port}/health", timeout=2)
                return response.status_code == 200
            except:
                # If no health endpoint, just check if process is running
                return True
        
        return True
    
    async def health_monitor(self):
        """Continuously monitor process health and restart if needed"""
        logger.info("🔍 Starting health monitoring...")
        
        while not self.shutdown_requested:
            dead_processes = []
            
            for name, process in self.processes.items():
                if not self.is_process_healthy(name, process):
                    logger.warning(f"⚠️ Process {name} unhealthy (PID: {process.pid})")
                    dead_processes.append(name)
            
            # Restart unhealthy processes
            for name in dead_processes:
                if not self.shutdown_requested:
                    await self.restart_process(name)
            
            # Update PID file
            self.save_pids()
            
            # Sleep before next check
            await asyncio.sleep(30)  # Check every 30 seconds
    
    async def restart_process(self, name: str):
        """Restart a failed process"""
        logger.info(f"🔄 Restarting process {name}...")
        
        # Clean up dead process
        if name in self.processes:
            try:
                self.processes[name].terminate()
                self.processes[name].wait(timeout=5)
            except:
                pass
            del self.processes[name]
        
        # Restart using saved config
        config = self.process_configs.get(name, {})
        if config:
            # Give it a moment before restart
            await asyncio.sleep(5)
            
            try:
                process = await self._start_process_from_config(name, config)
                if process:
                    self.processes[name] = process
                    logger.info(f"✅ Successfully restarted {name}")
                else:
                    logger.error(f"❌ Failed to restart {name}")
            except Exception as e:
                logger.error(f"❌ Error restarting {name}: {e}")
    
    async def _start_process_from_config(self, name: str, config: Dict) -> Optional[subprocess.Popen]:
        """Start a process from its saved configuration"""
        try:
            if config['type'] == 'mcp_server':
                return subprocess.Popen(
                    [sys.executable, "start_mcp_server.py"],
                    stdout=open(log_dir / f"{name}.log", 'a'),
                    stderr=subprocess.STDOUT,
                    preexec_fn=os.setsid
                )
            elif config['type'] == 'agent':
                # Use python module execution for consistency
                agent_name = config.get('name', f"agent_port_{config['port']}")
                log_name = agent_name.lower().replace(' ', '_').replace('-', '_')
                
                return subprocess.Popen([
                    sys.executable, "src/a2a_mcp/agents/__main__.py",
                    "--agent-card", config['card_file'],
                    "--port", str(config['port'])
                ], 
                stdout=open(log_dir / f"{log_name}.log", 'a'),
                stderr=subprocess.STDOUT,
                preexec_fn=os.setsid,
                cwd=str(Path.cwd())
                )
        except Exception as e:
            logger.error(f"Failed to start {name}: {e}")
            return None
    
    def shutdown_all(self):
        """Shutdown all managed processes gracefully"""
        logger.info("🛑 Shutting down all processes...")
        self.shutdown_requested = True
        
        # Send SIGTERM to all processes
        for name, process in self.processes.items():
            try:
                if process.poll() is None:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    logger.info(f"📤 Sent SIGTERM to {name}")
            except Exception as e:
                logger.warning(f"Error terminating {name}: {e}")
        
        # Wait for graceful shutdown
        time.sleep(5)
        
        # Force kill if needed
        for name, process in self.processes.items():
            try:
                if process.poll() is None:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    logger.info(f"💀 Force killed {name}")
            except Exception as e:
                logger.warning(f"Error force killing {name}: {e}")
        
        # Clean up PID file
        if self.pid_file.exists():
            self.pid_file.unlink()
            
        logger.info("✅ All processes shutdown complete")

class SolopreneurSystemLauncher:
    """Comprehensive system launcher for Solopreneur Oracle ecosystem"""
    
    def __init__(self):
        self.process_manager = ProcessManager()
        self.startup_success = False
        
        # Agent configuration mapping
        self.agent_tiers = {
            "tier1": {
                "name": "Oracle Master",
                "agents": [
                    {"name": "SolopreneurOracle Master", "port": 10901, "card": "agent_cards/solopreneur_oracle_agent.json"}
                ]
            },
            "tier2": {
                "name": "Domain Specialists", 
                "agents": [
                    {"name": "Technical Intelligence Oracle", "port": 10902, "card": "agent_cards/tier2/technical_intelligence_agent.json"},
                    {"name": "Knowledge Management Oracle", "port": 10903, "card": "agent_cards/tier2/knowledge_management_agent.json"},
                    {"name": "Personal Optimization Oracle", "port": 10904, "card": "agent_cards/tier2/personal_optimization_agent.json"},
                    {"name": "Learning Enhancement Oracle", "port": 10905, "card": "agent_cards/tier2/learning_enhancement_agent.json"},
                    {"name": "Integration Synthesis Oracle", "port": 10906, "card": "agent_cards/tier2/integration_synthesis_agent.json"},
                    {"name": "Autonomous Workflow Intelligence Oracle", "port": 10907, "card": "agent_cards/tier2/autonomous_workflow_intelligence_oracle.json"}
                ]
            },
            "tier3": {
                "name": "Intelligence Modules (Limited: AWIE, scheduler, trends only)",
                "port_ranges": [
                    {"ports": [10910], "category": "AI Research Analyzer"},  # trends
                    {"ports": [10935], "category": "Recovery Scheduler"},     # scheduler
                    {"ports": [10944], "category": "Spaced Repetition Scheduler"},  # scheduler
                    {"ports": [10980], "category": "AWIE Scheduler"}         # awie
                ]
            }
        }
    
    def validate_environment(self) -> bool:
        """Validate required environment variables and dependencies"""
        logger.info("🔍 Validating environment...")
        
        required_vars = ['GOOGLE_API_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {missing_vars}")
            return False
        
        # Check if agent cards directory exists
        if not Path("agent_cards").exists():
            logger.error("❌ agent_cards directory not found")
            return False
        
        # Check UV installation
        try:
            subprocess.run(["uv", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("❌ UV package manager not found. Please install UV.")
            return False
        
        logger.info("✅ Environment validation passed")
        return True
    
    def cleanup_existing_processes(self):
        """Clean up any existing processes on Solopreneur ports"""
        logger.info("🧹 Cleaning up existing processes...")
        
        # Define all port ranges
        all_ports = [10100]  # MCP Server
        all_ports.extend(range(10901, 10908))  # Tier 1 + Tier 2
        all_ports.extend(range(10910, 10981))  # Tier 3
        
        killed_count = 0
        for port in all_ports:
            try:
                # Use lsof to find processes using the port
                result = subprocess.run(
                    ["lsof", "-ti", f":{port}"], 
                    capture_output=True, text=True
                )
                
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        try:
                            os.kill(int(pid), signal.SIGTERM)
                            killed_count += 1
                            logger.debug(f"Killed process {pid} on port {port}")
                        except (ProcessLookupError, ValueError):
                            pass
            except FileNotFoundError:
                # lsof not available, try fuser
                try:
                    subprocess.run(
                        ["fuser", "-k", f"{port}/tcp"], 
                        capture_output=True, check=False
                    )
                except FileNotFoundError:
                    logger.warning("Neither lsof nor fuser available for port cleanup")
                    break
        
        if killed_count > 0:
            logger.info(f"🗑️ Cleaned up {killed_count} existing processes")
            time.sleep(3)  # Wait for cleanup
        
        logger.info("✅ Port cleanup completed")
    
    async def start_mcp_server(self) -> bool:
        """Start the MCP server with process management"""
        logger.info("📡 Starting MCP Server...")
        
        try:
            process = subprocess.Popen(
                [sys.executable, "start_mcp_server.py"],
                stdout=open(log_dir / "mcp_server.log", 'w'),
                stderr=subprocess.STDOUT,
                preexec_fn=os.setsid
            )
            
            # Wait for server to start
            for i in range(10):  # Wait up to 10 seconds
                if process.poll() is not None:
                    logger.error("❌ MCP Server failed to start")
                    return False
                
                try:
                    response = requests.get("http://localhost:10100/health", timeout=2)
                    if response.status_code == 200:
                        break
                except:
                    pass
                
                await asyncio.sleep(1)
            else:
                logger.warning("⚠️ MCP Server health check failed, but process is running")
            
            # Add to process manager
            self.process_manager.add_process("mcp_server", process, {
                "type": "mcp_server",
                "port": 10100
            })
            
            logger.info("✅ MCP Server started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start MCP Server: {e}")
            return False
    
    def find_agent_card(self, port: int, category: str = "") -> Optional[str]:
        """Find agent card file for a given port"""
        # Special handling for specific tier 3 agents we want to run
        specific_mappings = {
            10910: "agent_cards/tier3/ai_research_analyzer.json",     # trends
            10935: "agent_cards/tier3/recovery_scheduler.json",      # scheduler
            10944: "agent_cards/tier3/spaced_repetition_scheduler.json",  # scheduler
            10980: None  # AWIE Scheduler - uses direct class import
        }
        
        if port in specific_mappings:
            card_file = specific_mappings[port]
            if card_file and Path(card_file).exists():
                return card_file
            elif port == 10980:
                return "awie_direct"  # Special marker for AWIE
        
        # Look for card with matching port in URL
        for card_file in Path("agent_cards").rglob("*.json"):
            try:
                with open(card_file) as f:
                    data = json.load(f)
                    if "url" in data and f"localhost:{port}" in data["url"]:
                        return str(card_file)
            except:
                continue
        
        return None
    
    def get_agent_name_from_card(self, card_file: str, port: int, category: str) -> str:
        """Extract meaningful agent name from card file"""
        try:
            with open(card_file) as f:
                data = json.load(f)
                agent_name = data.get('name', '')
                if agent_name:
                    return agent_name
        except:
            pass
        
        # Fallback to meaningful name based on file or category
        card_name = Path(card_file).stem
        if card_name and card_name != 'agent':
            # Clean up the card name
            cleaned = card_name.replace('_', ' ').replace('-', ' ').title()
            return cleaned
        
        # Final fallback
        return f"{category} Agent {port}"
    
    async def start_agent_tier(self, tier_name: str) -> int:
        """Start all agents in a specific tier"""
        tier_config = self.agent_tiers.get(tier_name, {})
        logger.info(f"🚀 Starting {tier_config.get('name', tier_name)}...")
        
        started_count = 0
        
        if tier_name in ["tier1", "tier2"] and "agents" in tier_config:
            # Start specific agents
            for agent in tier_config["agents"]:
                success = await self.start_single_agent(
                    agent["name"], agent["port"], agent["card"]
                )
                if success:
                    started_count += 1
                    
                # Stagger startup to avoid resource conflicts
                await asyncio.sleep(2)
        
        elif tier_name == "tier3" and "port_ranges" in tier_config:
            # Start tier 3 agents by port ranges
            for range_config in tier_config["port_ranges"]:
                category = range_config["category"]
                
                if "start" in range_config and "end" in range_config:
                    ports = range(range_config["start"], range_config["end"] + 1)
                elif "ports" in range_config:
                    ports = range_config["ports"]
                else:
                    continue
                
                logger.info(f"  Starting {category} ({min(ports)}-{max(ports)})...")
                
                for port in ports:
                    card_file = self.find_agent_card(port, category)
                    if card_file:
                        # Create meaningful agent name from card file or category
                        if card_file == "awie_direct":
                            agent_name = "AWIE Scheduler Agent"
                            success = await self.start_awie_scheduler_agent(agent_name, port)
                        else:
                            agent_name = self.get_agent_name_from_card(card_file, port, category)
                            success = await self.start_single_agent(agent_name, port, card_file)
                        
                        if success:
                            started_count += 1
                    else:
                        logger.debug(f"No agent card found for port {port}")
                    
                    await asyncio.sleep(1)  # Quick stagger for tier 3
        
        logger.info(f"📊 {tier_config.get('name', tier_name)}: {started_count} agents started")
        return started_count
    
    async def start_single_agent(self, name: str, port: int, card_file: str) -> bool:
        """Start a single agent with error handling"""
        # Special handling for AWIE Scheduler Agent
        if "AWIE Scheduler" in name and port == 10980:
            return await self.start_awie_scheduler_agent(name, port)
        
        if not Path(card_file).exists():
            logger.warning(f"⚠️ Agent card not found: {card_file}")
            return False
        
        try:
            # Use direct execution of __main__.py
            process = subprocess.Popen([
                sys.executable, "src/a2a_mcp/agents/__main__.py",
                "--agent-card", card_file,
                "--port", str(port)
            ], 
            stdout=open(log_dir / f"{name.lower().replace(' ', '_')}.log", 'w'),
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid,
            cwd=str(Path.cwd())
            )
            
            # Quick health check
            await asyncio.sleep(1)
            if process.poll() is not None:
                logger.warning(f"⚠️ Agent {name} failed to start")
                return False
            
            # Create clean agent identifier
            agent_id = name.lower().replace(' ', '_').replace('-', '_')
            
            # Add to process manager
            self.process_manager.add_process(agent_id, process, {
                "type": "agent",
                "port": port,
                "card_file": card_file,
                "name": name
            })
            
            logger.debug(f"✅ Started {name} on port {port}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start {name}: {e}")
            return False
    
    async def start_awie_scheduler_agent(self, name: str, port: int) -> bool:
        """Start AWIE Scheduler Agent using direct class import"""
        try:
            process = subprocess.Popen([
                sys.executable, "-c", f"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))

async def run_agent():
    try:
        from a2a_mcp.agents.tier3.awie_scheduler_agent import AWIESchedulerAgent
        agent = AWIESchedulerAgent()
        print(f'✅ {name} started on port {port}')
        while True:
            await asyncio.sleep(10)
    except Exception as e:
        print(f'❌ Agent {name} failed: {{e}}')

asyncio.run(run_agent())
"""
            ], 
            stdout=open(log_dir / f"{name.lower().replace(' ', '_')}.log", 'w'),
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid,
            cwd=str(Path.cwd())
            )
            
            # Quick health check
            await asyncio.sleep(2)
            if process.poll() is not None:
                logger.warning(f"⚠️ AWIE Scheduler Agent failed to start")
                return False
            
            # Add to process manager
            agent_id = name.lower().replace(' ', '_').replace('-', '_')
            self.process_manager.add_process(agent_id, process, {
                "type": "awie_agent",
                "port": port,
                "name": name
            })
            
            logger.debug(f"✅ Started AWIE Scheduler Agent on port {port}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start AWIE Scheduler Agent: {e}")
            return False
    
    async def start_all_services(self) -> bool:
        """Start all services in the correct order"""
        logger.info("🚀 STARTING COMPLETE SOLOPRENEUR ORACLE SYSTEM")
        logger.info("=" * 60)
        
        # Step 1: Environment validation
        if not self.validate_environment():
            return False
        
        # Step 2: Cleanup existing processes
        self.cleanup_existing_processes()
        
        # Step 3: Start MCP Server
        if not await self.start_mcp_server():
            logger.error("❌ Cannot continue without MCP Server")
            return False
        
        # Step 4: Start Tier 1 (Oracle Master)
        tier1_count = await self.start_agent_tier("tier1")
        
        # Step 5: Start Tier 2 (Domain Specialists)
        tier2_count = await self.start_agent_tier("tier2")
        
        # Step 6: Start Tier 3 (Intelligence Modules)
        tier3_count = await self.start_agent_tier("tier3")
        
        total_agents = tier1_count + tier2_count + tier3_count
        
        # Final status
        if tier1_count >= 1 and tier2_count >= 3:  # Minimum viable system
            logger.info("🎉 SOLOPRENEUR ORACLE SYSTEM OPERATIONAL!")
            logger.info(f"📊 Total Agents Running: {total_agents}")
            logger.info(f"📊 Tier 3 Limited Mode: AWIE, scheduler, and trends agents only ({tier3_count} agents)")
            logger.info("=" * 60)
            self.startup_success = True
            return True
        else:
            logger.error("❌ Insufficient agents started - system not operational")
            return False
    
    async def run_system(self):
        """Main system runner with health monitoring"""
        try:
            # Start all services
            if await self.start_all_services():
                logger.info("🔍 System operational - starting health monitoring")
                logger.info("💡 Press Ctrl+C to shutdown system")
                
                # Start health monitoring
                health_task = asyncio.create_task(self.process_manager.health_monitor())
                
                # Keep system running
                try:
                    await health_task
                except asyncio.CancelledError:
                    pass
            else:
                logger.error("❌ System startup failed")
                
        except KeyboardInterrupt:
            logger.info("👋 Shutdown requested...")
        finally:
            self.process_manager.shutdown_all()

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"📡 Received signal {signum}, initiating shutdown...")
    # The main loop will handle cleanup
    sys.exit(0)

def main():
    """Main entry point"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🧠 SOLOPRENEUR ORACLE SYSTEM LAUNCHER")
    print("🎯 Production-grade launcher with process management")
    print("⚡ MCP Server + Oracle + 76 Domain Agents")
    print("=" * 70)
    
    launcher = SolopreneurSystemLauncher()
    
    try:
        asyncio.run(launcher.run_system())
    except KeyboardInterrupt:
        logger.info("👋 Shutdown complete")
    except Exception as e:
        logger.error(f"❌ System error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()