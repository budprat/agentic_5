#!/usr/bin/env python3
"""ABOUTME: Background launcher for Solopreneur Oracle system using nohup-style execution.
ABOUTME: Starts the complete system in background with proper logging and PID management."""

import os
import subprocess
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_requirements():
    """Check if system is ready to launch"""
    # Check environment
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ Error: GOOGLE_API_KEY environment variable is required")
        return False
    
    # Check if main launcher exists
    if not Path("launch_solopreneur_system.py").exists():
        print("❌ Error: Main launcher script not found")
        return False
    
    return True

def cleanup_existing():
    """Stop any existing system before starting new one"""
    pid_file = Path(".solopreneur_pids.json")
    if pid_file.exists():
        print("🧹 Stopping existing system...")
        try:
            subprocess.run([sys.executable, "stop_solopreneur_system.py"], 
                         capture_output=True, check=False)
            time.sleep(3)
        except:
            pass

def start_background():
    """Start the system in background using nohup"""
    print("🚀 Starting Solopreneur Oracle System in Background...")
    print("=" * 55)
    
    # Ensure logs directory exists
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Start main launcher in background
    log_file = log_dir / "system_background.log"
    
    try:
        process = subprocess.Popen([
            sys.executable, "launch_solopreneur_system.py"
        ],
        stdout=open(log_file, 'w'),
        stderr=subprocess.STDOUT,
        start_new_session=True  # Detach from parent
        )
        
        # Save main launcher PID for management
        with open(".main_launcher_pid", 'w') as f:
            f.write(str(process.pid))
        
        print(f"✅ System launched in background (PID: {process.pid})")
        print(f"📄 Logs: {log_file}")
        print("🔍 Status: ./status_solopreneur_system.py")
        print("🛑 Stop: ./stop_solopreneur_system.py")
        print()
        
        # Wait a moment to check if startup was successful
        time.sleep(5)
        
        if process.poll() is None:
            print("✅ Background startup successful")
            print("💡 System is initializing - check logs for progress")
        else:
            print("❌ Background startup may have failed - check logs")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to start background system: {e}")
        return False

def main():
    """Main entry point"""
    print("🧠 SOLOPRENEUR ORACLE BACKGROUND LAUNCHER")
    print("🎯 Starts complete system with nohup-style execution")
    print("=" * 55)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Cleanup existing
    cleanup_existing()
    
    # Start in background
    if start_background():
        print("🎉 Solopreneur Oracle System running in background!")
    else:
        print("❌ Failed to start system in background")
        sys.exit(1)

if __name__ == "__main__":
    main()