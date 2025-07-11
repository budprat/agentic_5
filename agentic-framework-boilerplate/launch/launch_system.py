#!/usr/bin/env python3
# ABOUTME: Simplified launcher that validates environment, starts MCP server, and manages agents
# ABOUTME: Includes process management and health monitoring for the A2A framework

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
from typing import Dict, List, Optional, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration constants
DEFAULT_MCP_HOST = "localhost"
DEFAULT_MCP_PORT = 8080
DEFAULT_MCP_TRANSPORT = "stdio"
AGENT_CARDS_DIR = "agent_cards"
HEALTH_CHECK_INTERVAL = 30  # seconds
MAX_STARTUP_RETRIES = 3
STARTUP_RETRY_DELAY = 5  # seconds

class SystemLauncher:
    """Manages the startup and monitoring of the A2A MCP system."""
    
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.agent_configs: List[Dict] = []
        self.mcp_server_ready = False
        self.shutdown_requested = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}. Initiating shutdown...")
        self.shutdown_requested = True
        self.shutdown()
    
    def validate_environment(self) -> Tuple[bool, List[str]]:
        """Validate the environment setup.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check for GOOGLE_API_KEY
        if not os.environ.get('GOOGLE_API_KEY'):
            errors.append("GOOGLE_API_KEY environment variable is not set")
        
        # Check if agent cards directory exists
        agent_cards_path = Path(AGENT_CARDS_DIR)
        if not agent_cards_path.exists():
            errors.append(f"Agent cards directory not found: {AGENT_CARDS_DIR}")
        elif not agent_cards_path.is_dir():
            errors.append(f"Agent cards path is not a directory: {AGENT_CARDS_DIR}")
        
        # Check Python version
        if sys.version_info < (3, 8):
            errors.append(f"Python 3.8+ required, found {sys.version}")
        
        # Check if src module is importable
        try:
            import a2a_mcp
        except ImportError:
            errors.append("Cannot import a2a_mcp module. Ensure you're in the project root.")
        
        return (len(errors) == 0, errors)
    
    def load_agent_configs(self) -> List[Dict]:
        """Load all agent configurations from agent cards."""
        configs = []
        agent_cards_path = Path(AGENT_CARDS_DIR)
        
        def load_cards_from_dir(directory: Path):
            """Recursively load agent cards from directory."""
            for item in directory.iterdir():
                if item.is_file() and item.suffix == '.json':
                    try:
                        with open(item, 'r') as f:
                            config = json.load(f)
                            config['_file_path'] = str(item)
                            configs.append(config)
                            logger.info(f"Loaded agent card: {item.name}")
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse {item}: {e}")
                    except Exception as e:
                        logger.error(f"Error loading {item}: {e}")
                elif item.is_dir():
                    load_cards_from_dir(item)
        
        load_cards_from_dir(agent_cards_path)
        
        # Sort by tier if available (tier 1 first)
        configs.sort(key=lambda x: x.get('tier', 999))
        
        return configs
    
    def start_mcp_server(self) -> bool:
        """Start the MCP server process.
        
        Returns:
            True if server started successfully, False otherwise.
        """
        logger.info("Starting MCP server...")
        
        try:
            # Prepare the command
            cmd = [
                sys.executable,
                "-m",
                "a2a_mcp.mcp",
                "--host", DEFAULT_MCP_HOST,
                "--port", str(DEFAULT_MCP_PORT),
                "--transport", DEFAULT_MCP_TRANSPORT
            ]
            
            # Set environment variables
            env = os.environ.copy()
            env['AGENT_CARDS_DIR'] = AGENT_CARDS_DIR
            env['PYTHONPATH'] = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/src:" + env.get('PYTHONPATH', '')
            
            # Start the process
            process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes['mcp_server'] = process
            
            # Wait for server to be ready
            for retry in range(MAX_STARTUP_RETRIES):
                time.sleep(STARTUP_RETRY_DELAY)
                if self._check_mcp_health():
                    logger.info("MCP server started successfully")
                    self.mcp_server_ready = True
                    return True
                logger.info(f"Waiting for MCP server... (attempt {retry + 1}/{MAX_STARTUP_RETRIES})")
            
            # If failed, try to get error output
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                if stderr:
                    logger.error(f"MCP server error: {stderr}")
            
            logger.error("MCP server failed to start within timeout")
            return False
            
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            return False
    
    def start_agent(self, config: Dict) -> bool:
        """Start an individual agent based on its configuration.
        
        Args:
            config: Agent configuration dictionary
            
        Returns:
            True if agent started successfully, False otherwise.
        """
        agent_name = config.get('name', 'Unknown')
        logger.info(f"Starting agent: {agent_name}")
        
        try:
            # Get the agent card file path
            agent_card_path = config.get('_file_path')
            if not agent_card_path:
                logger.error(f"No file path found for agent {agent_name}")
                return False
            
            # Build the command using the actual agent module interface
            cmd = [
                sys.executable,
                "-m",
                "a2a_mcp.agents",
                "--agent-card", agent_card_path
            ]
            
            # If agent has a specific port, add it
            if 'port' in config:
                cmd.extend(["--port", str(config['port'])])
            
            # Set up environment
            env = os.environ.copy()
            env['PYTHONPATH'] = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/src:" + env.get('PYTHONPATH', '')
            
            process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes[f'agent_{agent_name}'] = process
            
            # Brief delay to check if process started
            time.sleep(2)
            if process.poll() is None:
                logger.info(f"Agent {agent_name} started successfully")
                return True
            else:
                # Try to get error output
                stdout, stderr = process.communicate(timeout=1)
                logger.error(f"Agent {agent_name} failed to start")
                if stderr:
                    logger.error(f"Error output: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start agent {agent_name}: {e}")
            return False
    
    def _check_mcp_health(self) -> bool:
        """Check if MCP server is healthy.
        
        Returns:
            True if healthy, False otherwise.
        """
        try:
            # In a real implementation, this would make an HTTP/gRPC call
            # For now, just check if the process is running
            if 'mcp_server' in self.processes:
                process = self.processes['mcp_server']
                return process.poll() is None
            return False
        except Exception as e:
            logger.error(f"Error checking MCP health: {e}")
            return False
    
    def check_system_health(self) -> Dict[str, any]:
        """Check health of all system components.
        
        Returns:
            Dictionary with health status of each component.
        """
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'overall': 'healthy',
            'components': {}
        }
        
        # Check MCP server
        mcp_healthy = self._check_mcp_health()
        health_status['components']['mcp_server'] = {
            'status': 'healthy' if mcp_healthy else 'unhealthy',
            'running': mcp_healthy
        }
        
        # Check each agent
        for name, process in self.processes.items():
            if name.startswith('agent_'):
                agent_name = name.replace('agent_', '')
                is_running = process.poll() is None
                health_status['components'][name] = {
                    'status': 'healthy' if is_running else 'unhealthy',
                    'running': is_running,
                    'pid': process.pid if is_running else None
                }
        
        # Determine overall health
        if any(comp['status'] == 'unhealthy' for comp in health_status['components'].values()):
            health_status['overall'] = 'unhealthy'
        
        return health_status
    
    async def monitor_health(self):
        """Continuously monitor system health."""
        while not self.shutdown_requested:
            health_status = self.check_system_health()
            
            if health_status['overall'] == 'unhealthy':
                logger.warning(f"System health check failed: {health_status}")
                
                # Attempt to restart failed components
                for component, status in health_status['components'].items():
                    if not status['running']:
                        logger.info(f"Attempting to restart {component}...")
                        # In a real implementation, we would restart the component
            
            await asyncio.sleep(HEALTH_CHECK_INTERVAL)
    
    def launch(self):
        """Main launch sequence."""
        logger.info("Starting A2A MCP Framework...")
        
        # Step 1: Validate environment
        is_valid, errors = self.validate_environment()
        if not is_valid:
            logger.error("Environment validation failed:")
            for error in errors:
                logger.error(f"  - {error}")
            return False
        
        logger.info("Environment validation passed")
        
        # Step 2: Load agent configurations
        self.agent_configs = self.load_agent_configs()
        logger.info(f"Loaded {len(self.agent_configs)} agent configurations")
        
        # Step 3: Start MCP server
        if not self.start_mcp_server():
            logger.error("Failed to start MCP server. Aborting launch.")
            self.shutdown()
            return False
        
        # Step 4: Start agents
        started_agents = 0
        for config in self.agent_configs:
            if self.start_agent(config):
                started_agents += 1
            else:
                logger.warning(f"Failed to start agent: {config.get('name', 'Unknown')}")
        
        logger.info(f"Started {started_agents}/{len(self.agent_configs)} agents")
        
        # Step 5: Start health monitoring
        logger.info("Starting health monitoring...")
        try:
            asyncio.run(self.monitor_health())
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        
        return True
    
    def shutdown(self):
        """Shutdown all processes gracefully."""
        logger.info("Shutting down system...")
        
        # Stop all processes in reverse order
        for name in reversed(list(self.processes.keys())):
            process = self.processes[name]
            if process.poll() is None:
                logger.info(f"Stopping {name}...")
                process.terminate()
                
                # Give process time to terminate gracefully
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning(f"{name} did not terminate gracefully, forcing kill")
                    process.kill()
        
        logger.info("All processes stopped")
    
    def print_status(self):
        """Print current system status."""
        health = self.check_system_health()
        
        print("\n=== A2A MCP System Status ===")
        print(f"Time: {health['timestamp']}")
        print(f"Overall Status: {health['overall']}")
        print("\nComponents:")
        
        for component, status in health['components'].items():
            status_icon = "" if status['running'] else "L"
            print(f"  {status_icon} {component}: {status['status']}")
            if status.get('pid'):
                print(f"      PID: {status['pid']}")
        
        print(f"\nTotal Agents: {len(self.agent_configs)}")
        print("=" * 30 + "\n")


def main():
    """Main entry point."""
    launcher = SystemLauncher()
    
    try:
        # Print initial status
        print("A2A MCP Framework Launcher")
        print("=" * 30)
        
        # Launch the system
        success = launcher.launch()
        
        if success:
            logger.info("System launched successfully")
            launcher.print_status()
        else:
            logger.error("System launch failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Unexpected error during launch: {e}")
        launcher.shutdown()
        sys.exit(1)
    finally:
        launcher.shutdown()


if __name__ == "__main__":
    main()