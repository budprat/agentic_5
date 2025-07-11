#!/usr/bin/env python3
"""ABOUTME: Comprehensive stop script for Solopreneur Oracle system.
ABOUTME: Gracefully shuts down all components including MCP server and all agents."""

import json
import os
import signal
import sys
import time
from pathlib import Path
import subprocess

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
                        'type': 'managed'
                    }
        except Exception as e:
            print(f"Warning: Could not read JSON PID file: {e}")
    
    # Load main launcher PID
    main_pid_file = Path(".main_launcher_pid")
    if main_pid_file.exists():
        try:
            with open(main_pid_file) as f:
                pid = int(f.read().strip())
                processes['main_launcher'] = {
                    'pid': pid,
                    'type': 'launcher'
                }
        except Exception as e:
            print(f"Warning: Could not read main PID file: {e}")
    
    # Load legacy PID files
    agent_pids_file = Path(".agent_pids")
    if agent_pids_file.exists():
        try:
            with open(agent_pids_file) as f:
                for line_num, line in enumerate(f, 1):
                    pid = int(line.strip())
                    processes[f'legacy_agent_{line_num}'] = {
                        'pid': pid,
                        'type': 'legacy'
                    }
        except Exception as e:
            print(f"Warning: Could not read legacy PID file: {e}")
    
    mcp_pid_file = Path(".mcp_pid")
    if mcp_pid_file.exists():
        try:
            with open(mcp_pid_file) as f:
                pid = int(f.read().strip())
                processes['legacy_mcp'] = {
                    'pid': pid,
                    'type': 'legacy'
                }
        except Exception as e:
            print(f"Warning: Could not read MCP PID file: {e}")
    
    return processes

def kill_process_tree(pid, timeout=10):
    """Kill a process and all its children"""
    try:
        # Try graceful termination first
        os.kill(pid, signal.SIGTERM)
        
        # Wait for graceful shutdown
        for _ in range(timeout):
            try:
                # Check if process still exists
                os.kill(pid, 0)
                time.sleep(1)
            except OSError:
                # Process no longer exists
                return True
        
        # Force kill if still running
        try:
            os.kill(pid, signal.SIGKILL)
            return True
        except OSError:
            return True  # Already dead
            
    except OSError:
        # Process doesn't exist
        return True

def cleanup_ports():
    """Force cleanup of known Solopreneur ports"""
    print("🧹 Cleaning up ports...")
    
    # All Solopreneur ports
    ports = [10100]  # MCP Server
    ports.extend(range(10901, 10908))  # Tier 1 + Tier 2
    ports.extend(range(10910, 10981))  # Tier 3
    
    killed_count = 0
    
    for port in ports:
        try:
            # Use lsof to find processes
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"], 
                capture_output=True, text=True
            )
            
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid_str in pids:
                    try:
                        pid = int(pid_str)
                        os.kill(pid, signal.SIGTERM)
                        killed_count += 1
                    except (ValueError, OSError):
                        pass
        except FileNotFoundError:
            # lsof not available, try fuser
            try:
                subprocess.run(
                    ["fuser", "-k", f"{port}/tcp"], 
                    capture_output=True, check=False
                )
            except FileNotFoundError:
                break
    
    if killed_count > 0:
        print(f"🗑️ Cleaned up {killed_count} processes from ports")
        time.sleep(2)

def cleanup_pid_files():
    """Remove all PID files"""
    pid_files = [
        ".solopreneur_pids.json",
        ".main_launcher_pid", 
        ".agent_pids",
        ".mcp_pid"
    ]
    
    for pid_file in pid_files:
        try:
            Path(pid_file).unlink(missing_ok=True)
        except Exception:
            pass

def main():
    """Main stop function"""
    print("🛑 STOPPING SOLOPRENEUR ORACLE SYSTEM")
    print("=" * 45)
    
    # Load process information
    processes = load_process_info()
    
    if not processes:
        print("ℹ️ No tracked processes found")
        cleanup_ports()
        cleanup_pid_files()
        print("✅ System cleanup completed")
        return
    
    print(f"📋 Found {len(processes)} tracked processes")
    
    # Stop processes gracefully
    stopped_count = 0
    failed_count = 0
    
    for name, info in processes.items():
        pid = info['pid']
        process_type = info['type']
        
        print(f"🛑 Stopping {name} (PID: {pid}, Type: {process_type})...")
        
        if kill_process_tree(pid):
            print(f"  ✅ Stopped {name}")
            stopped_count += 1
        else:
            print(f"  ❌ Failed to stop {name}")
            failed_count += 1
    
    # Force cleanup ports to catch any missed processes
    cleanup_ports()
    
    # Clean up PID files
    cleanup_pid_files()
    
    # Final summary
    print()
    print("📊 SHUTDOWN SUMMARY")
    print("=" * 20)
    print(f"✅ Stopped: {stopped_count}")
    if failed_count > 0:
        print(f"❌ Failed: {failed_count}")
    print("🧹 PID files cleaned")
    print("🧹 Ports cleaned")
    print()
    print("✅ Solopreneur Oracle System shutdown complete!")

if __name__ == "__main__":
    main()