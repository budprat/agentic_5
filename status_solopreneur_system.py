#!/usr/bin/env python3
"""ABOUTME: Comprehensive status checker for Solopreneur Oracle system.
ABOUTME: Provides detailed health status of MCP server, all agents, and system components."""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
import subprocess
import requests

def load_process_info():
    """Load process information from PID files"""
    processes = {}
    
    # Load from JSON PID file (new format)
    json_pid_file = Path(".solopreneur_pids.json")
    if json_pid_file.exists():
        try:
            with open(json_pid_file) as f:
                data = json.load(f)
                for name, info in data.items():
                    processes[name] = {
                        'pid': info['pid'],
                        'config': info.get('config', {}),
                        'started': info.get('started', 'Unknown'),
                        'type': 'managed'
                    }
        except Exception as e:
            print(f"Warning: Could not read JSON PID file: {e}")
    
    return processes

def check_process_running(pid):
    """Check if a process is actually running"""
    try:
        os.kill(pid, 0)  # Signal 0 just checks if process exists
        return True
    except OSError:
        return False

def check_port_health(port, timeout=2):
    """Check if a service on a port is responding"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=timeout)
        return response.status_code == 200
    except:
        # Try just connecting to the port
        try:
            response = requests.get(f"http://localhost:{port}", timeout=timeout)
            return True  # Any response means service is up
        except:
            return False

def get_port_processes():
    """Get processes listening on Solopreneur ports"""
    port_info = {}
    
    # All Solopreneur ports
    ports = [10100]  # MCP Server
    ports.extend(range(10901, 10908))  # Tier 1 + Tier 2
    ports.extend(range(10910, 10981))  # Tier 3
    
    for port in ports:
        try:
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"], 
                capture_output=True, text=True
            )
            
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                port_info[port] = [int(pid) for pid in pids if pid.isdigit()]
        except (FileNotFoundError, ValueError):
            continue
    
    return port_info

def format_uptime(started_str):
    """Calculate and format uptime"""
    try:
        started = datetime.fromisoformat(started_str.replace('Z', '+00:00'))
        uptime = datetime.now() - started.replace(tzinfo=None)
        
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    except:
        return "Unknown"

def check_system_health():
    """Perform comprehensive system health check"""
    print("🔍 SOLOPRENEUR ORACLE SYSTEM STATUS")
    print("=" * 50)
    
    # Load tracked processes
    processes = load_process_info()
    port_processes = get_port_processes()
    
    # Check main launcher
    main_pid_file = Path(".main_launcher_pid")
    main_launcher_running = False
    if main_pid_file.exists():
        try:
            with open(main_pid_file) as f:
                main_pid = int(f.read().strip())
                main_launcher_running = check_process_running(main_pid)
                print(f"🧠 Main Launcher (PID {main_pid}): {'✅ Running' if main_launcher_running else '❌ Not Running'}")
        except:
            print("🧠 Main Launcher: ❌ PID file corrupted")
    else:
        print("🧠 Main Launcher: ❌ Not tracked")
    
    print()
    
    # Check MCP Server
    print("📡 MCP SERVER STATUS")
    print("-" * 20)
    mcp_port = 10100
    mcp_health = check_port_health(mcp_port)
    mcp_process = mcp_port in port_processes
    
    print(f"Port {mcp_port}: {'✅ Responding' if mcp_health else '❌ Not Responding'}")
    if mcp_process:
        pids = port_processes[mcp_port]
        print(f"Processes: {', '.join(map(str, pids))}")
    else:
        print("Processes: None")
    
    print()
    
    # Check tracked processes
    if processes:
        print("🤖 TRACKED AGENTS STATUS")
        print("-" * 25)
        
        running_count = 0
        total_count = len(processes)
        
        # Group by tiers
        tier_stats = {"tier1": 0, "tier2": 0, "tier3": 0, "mcp": 0}
        
        for name, info in processes.items():
            pid = info['pid']
            config = info.get('config', {})
            port = config.get('port', 'N/A')
            started = info.get('started', 'Unknown')
            
            # Check if process is running
            process_running = check_process_running(pid)
            
            # Check port health if applicable
            port_healthy = False
            if isinstance(port, int):
                port_healthy = check_port_health(port)
            
            # Determine status
            if process_running and (port == 'N/A' or port_healthy):
                status = "✅ Healthy"
                running_count += 1
            elif process_running:
                status = "⚠️ Running (Port Issues)"
            else:
                status = "❌ Dead"
            
            # Categorize by tier
            if isinstance(port, int):
                if port == 10100:
                    tier_stats["mcp"] += 1 if process_running else 0
                elif 10901 <= port <= 10907:
                    tier_stats["tier1" if port == 10901 else "tier2"] += 1 if process_running else 0
                elif 10910 <= port <= 10980:
                    tier_stats["tier3"] += 1 if process_running else 0
            
            # Format output
            uptime = format_uptime(started)
            print(f"{name:30} (PID {pid:6}, Port {port:5}): {status:20} | Uptime: {uptime}")
    
    else:
        print("🤖 TRACKED AGENTS: None found")
    
    print()
    
    # Check port usage summary
    print("🌐 PORT USAGE SUMMARY")
    print("-" * 21)
    
    tier_ranges = [
        ("MCP Server", [10100]),
        ("Tier 1 (Master)", [10901]),
        ("Tier 2 (Domain)", list(range(10902, 10908))),
        ("Tier 3 (Intelligence)", list(range(10910, 10981)))
    ]
    
    for tier_name, ports in tier_ranges:
        active_ports = [p for p in ports if p in port_processes]
        total_ports = len(ports)
        active_count = len(active_ports)
        
        print(f"{tier_name:20}: {active_count:2}/{total_ports:2} ports active")
        
        if active_count > 0 and active_count <= 5:  # Show details for small ranges
            for port in active_ports:
                health = "✅" if check_port_health(port) else "⚠️"
                print(f"  {health} Port {port}")
    
    print()
    
    # Overall system status
    print("📊 SYSTEM SUMMARY")
    print("-" * 16)
    
    if processes:
        health_percentage = (running_count / total_count) * 100
        print(f"Tracked Agents: {running_count}/{total_count} running ({health_percentage:.1f}%)")
    
    total_active_ports = len(port_processes)
    print(f"Active Ports: {total_active_ports}")
    print(f"MCP Server: {'✅ Running' if mcp_health else '❌ Down'}")
    
    # Overall health assessment
    if mcp_health and (not processes or running_count >= total_count * 0.8):
        print("\n🎉 Status: ✅ SYSTEM HEALTHY")
    elif mcp_health and running_count > 0:
        print("\n⚠️ Status: 🟡 SYSTEM DEGRADED")
    else:
        print("\n❌ Status: 🔴 SYSTEM DOWN")
    
    print()
    
    # Show recent logs if available
    log_files = list(Path("logs").glob("*.log")) if Path("logs").exists() else []
    if log_files:
        print("📄 RECENT LOG FILES")
        print("-" * 18)
        for log_file in sorted(log_files, key=lambda f: f.stat().st_mtime, reverse=True)[:5]:
            size = log_file.stat().st_size
            modified = datetime.fromtimestamp(log_file.stat().st_mtime)
            print(f"{log_file.name:25} | {size:8} bytes | {modified.strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main status check function"""
    try:
        check_system_health()
    except KeyboardInterrupt:
        print("\n👋 Status check interrupted")
    except Exception as e:
        print(f"❌ Error during status check: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()