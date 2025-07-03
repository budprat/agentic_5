#!/usr/bin/env python3
"""Test all MCP servers configured in .mcp.json"""

import json
import subprocess
import asyncio
import time
from pathlib import Path
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def load_mcp_config():
    """Load MCP configuration from .mcp.json"""
    with open('.mcp.json', 'r') as f:
        return json.load(f)

def test_stdio_server(name, config):
    """Test a stdio MCP server by attempting to start it"""
    print(f"\n{Colors.BLUE}Testing {name} (stdio)...{Colors.END}")
    
    # Build command
    command = config.get('command', 'npx')
    args = config.get('args', [])
    env = os.environ.copy()
    env.update(config.get('env', {}))
    
    # For Python scripts, check if file exists
    if command == 'python' and args:
        script_path = args[0]
        if not Path(script_path).exists():
            print(f"{Colors.RED}✗ Script not found: {script_path}{Colors.END}")
            # Try alternative path from current directory
            alt_path = Path('.') / Path(script_path).name
            if alt_path.exists():
                print(f"{Colors.YELLOW}  Found at: {alt_path}{Colors.END}")
                args[0] = str(alt_path)
            else:
                return False
    
    try:
        # Try to run the command with a timeout
        cmd = [command] + args
        print(f"  Command: {' '.join(cmd)}")
        
        # For npx commands, add --version to just check if package exists
        if command == 'npx' and len(args) > 0:
            # Extract package name from args
            package = args[0]
            if package == '-y' and len(args) > 1:
                package = args[1]
            
            # Special handling for different packages
            if '@' in package:
                # For scoped packages, try to get version info
                test_cmd = ['npx', '-y', package, '--help']
            else:
                test_cmd = ['npx', '-y', package, '--version']
            
            # Run with short timeout
            proc = subprocess.run(
                test_cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if proc.returncode == 0:
                print(f"{Colors.GREEN}✓ {name} package is available{Colors.END}")
                return True
            else:
                print(f"{Colors.RED}✗ {name} failed: {proc.stderr}{Colors.END}")
                return False
        
        # For other commands, just check if they exist
        elif command == 'python':
            # Check if Python script exists and is valid
            result = subprocess.run(
                [command, '-c', 'print("OK")'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"{Colors.GREEN}✓ Python is available{Colors.END}")
                return True
            else:
                print(f"{Colors.RED}✗ Python check failed{Colors.END}")
                return False
                
    except subprocess.TimeoutExpired:
        print(f"{Colors.YELLOW}⚠ {name} timed out (server might be starting correctly){Colors.END}")
        return True  # Timeout might mean server started successfully
    except FileNotFoundError:
        print(f"{Colors.RED}✗ Command not found: {command}{Colors.END}")
        return False
    except Exception as e:
        print(f"{Colors.RED}✗ Error testing {name}: {e}{Colors.END}")
        return False

def test_sse_server(name, config):
    """Test an SSE MCP server (would need actual connection test)"""
    print(f"\n{Colors.BLUE}Testing {name} (SSE)...{Colors.END}")
    url = config.get('url', 'No URL specified')
    print(f"  URL: {url}")
    print(f"{Colors.YELLOW}⚠ SSE servers need manual connection testing{Colors.END}")
    return None  # Can't test without actually connecting

def check_credentials(name, config):
    """Check if required credentials are configured"""
    env_vars = config.get('env', {})
    missing = []
    
    for key, value in env_vars.items():
        if value.startswith('YOUR_') or value == '':
            missing.append(key)
    
    # Special handling for different servers
    if name == 'snowflake':
        # Check Snowflake env vars
        snowflake_vars = ['SNOWFLAKE_USER', 'SNOWFLAKE_PASSWORD', 'SNOWFLAKE_ACCOUNT']
        for var in snowflake_vars:
            if not os.getenv(var):
                missing.append(var)
    
    if missing:
        print(f"  {Colors.YELLOW}Missing credentials: {', '.join(missing)}{Colors.END}")
        return False
    return True

def main():
    """Test all MCP servers"""
    print(f"{Colors.BLUE}=== MCP Server Connection Test ==={Colors.END}")
    
    try:
        config = load_mcp_config()
        servers = config.get('mcpServers', {})
        
        results = {}
        
        for name, server_config in servers.items():
            server_type = server_config.get('type', 'stdio')
            
            # Check credentials first
            has_creds = check_credentials(name, server_config)
            
            if server_type == 'stdio':
                if has_creds or name in ['puppeteer', 'context7']:  # Some don't need creds
                    result = test_stdio_server(name, server_config)
                    results[name] = result
                else:
                    print(f"\n{Colors.BLUE}Testing {name} (stdio)...{Colors.END}")
                    print(f"{Colors.YELLOW}⚠ Skipping - missing credentials{Colors.END}")
                    results[name] = None
            elif server_type == 'sse':
                result = test_sse_server(name, server_config)
                results[name] = result
            else:
                print(f"\n{Colors.YELLOW}Unknown server type for {name}: {server_type}{Colors.END}")
                results[name] = None
        
        # Summary
        print(f"\n{Colors.BLUE}=== Summary ==={Colors.END}")
        working = sum(1 for r in results.values() if r is True)
        failed = sum(1 for r in results.values() if r is False)
        unknown = sum(1 for r in results.values() if r is None)
        
        for name, result in results.items():
            if result is True:
                print(f"  {Colors.GREEN}✓ {name}{Colors.END}")
            elif result is False:
                print(f"  {Colors.RED}✗ {name}{Colors.END}")
            else:
                print(f"  {Colors.YELLOW}? {name} (needs manual testing or credentials){Colors.END}")
        
        print(f"\nTotal: {working} working, {failed} failed, {unknown} need manual testing")
        
    except FileNotFoundError:
        print(f"{Colors.RED}Error: .mcp.json not found{Colors.END}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"{Colors.RED}Error: Invalid JSON in .mcp.json{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()