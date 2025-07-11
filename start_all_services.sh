#!/bin/bash
# ABOUTME: Simple nohup-style launcher for all Solopreneur services
# ABOUTME: Starts MCP server, Oracle, and all domain agents in background using nohup pattern

echo "🚀 Starting All Solopreneur Services in Background..."

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Check prerequisites
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ Error: GOOGLE_API_KEY not set in .env file"
    exit 1
fi

# Create logs directory
mkdir -p logs

# Function to start service in background with nohup
start_service() {
    local name=$1
    local script=$2
    local log_file=$3
    
    echo "📡 Starting $name..."
    nohup python $script > $log_file 2>&1 &
    echo $! >> .service_pids
    echo "  ✅ $name started (PID: $!) - logs: $log_file"
}

# Clear previous service PIDs
> .service_pids

echo "=" * 50

# Start MCP Server
start_service "MCP Server" "start_mcp_server.py" "logs/mcp_server_background.log"
sleep 3

# Start Main System Launcher  
start_service "Solopreneur System" "start_solopreneur_background.py" "logs/system_launcher_background.log"
sleep 5

echo ""
echo "✅ All services started in background!"
echo "=" * 40
echo "📊 Status Check: ./status_solopreneur_system.py"
echo "🛑 Stop All: ./stop_solopreneur_system.py"
echo "📄 Logs: logs/ directory"
echo ""
echo "💡 Services are running independently in background"