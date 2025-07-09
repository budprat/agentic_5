#!/bin/bash
# Startup script for complete 56-agent Solopreneur Oracle system

echo "🚀 Starting AI Solopreneur Oracle System (56 agents)..."
echo "=================================================="

# Source configuration if exists
if [ -f solopreneur_config.env ]; then
    source solopreneur_config.env
fi

# Check prerequisites
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ Error: GOOGLE_API_KEY not set"
    echo "Please set: export GOOGLE_API_KEY='your-api-key'"
    exit 1
fi

# Create logs directory
mkdir -p logs

# Start MCP Server if not running
if ! lsof -i:10100 > /dev/null 2>&1; then
    echo "📡 Starting MCP Server..."
    uv run a2a-mcp --run mcp-server --transport sse --host localhost --port 10100 > logs/mcp_server.log 2>&1 &
    MCP_PID=$!
    sleep 3
    echo "✅ MCP Server started (PID: $MCP_PID)"
    echo $MCP_PID > .mcp_pid
else
    echo "✅ MCP Server already running"
fi

# Function to start agent
start_agent() {
    local card_file=$1
    local port=$2
    local tier=$3
    
    echo "  Starting: $(basename $card_file .json) (Port $port, Tier $tier)..."
    uv run src/a2a_mcp/agents/ --agent-card $card_file --port $port > logs/agent_$port.log 2>&1 &
    echo $! >> .agent_pids
}

# Clear previous PIDs
> .agent_pids

echo ""
echo "🎯 TIER 1: Starting Oracle Master..."
start_agent "agent_cards/tier1/solopreneuroracle_master_agent.json" 10901 1

echo ""
echo "🔮 TIER 2: Starting Domain Specialists..."
for card in agent_cards/tier2/*.json; do
    port=$(grep -o '"url": "http://localhost:[0-9]*' $card | grep -o '[0-9]*$')
    start_agent "$card" "$port" 2
done

echo ""
echo "⚡ TIER 3: Starting Intelligence Modules..."
echo "  Technical Intelligence (10910-10919)..."
for port in {10910..10919}; do
    card=$(find agent_cards/tier3 -name "*.json" -exec grep -l "\"url\": \"http://localhost:$port" {} \; 2>/dev/null | head -1)
    [ -f "$card" ] && start_agent "$card" "$port" 3
done

echo "  Knowledge Systems (10920-10929)..."
for port in {10920..10929}; do
    card=$(find agent_cards/tier3 -name "*.json" -exec grep -l "\"url\": \"http://localhost:$port" {} \; 2>/dev/null | head -1)
    [ -f "$card" ] && start_agent "$card" "$port" 3
done

echo "  Personal Systems (10930-10939)..."
for port in {10930..10939}; do
    card=$(find agent_cards/tier3 -name "*.json" -exec grep -l "\"url\": \"http://localhost:$port" {} \; 2>/dev/null | head -1)
    [ -f "$card" ] && start_agent "$card" "$port" 3
done

echo "  Learning Systems (10940-10949)..."
for port in {10940..10949}; do
    card=$(find agent_cards/tier3 -name "*.json" -exec grep -l "\"url\": \"http://localhost:$port" {} \; 2>/dev/null | head -1)
    [ -f "$card" ] && start_agent "$card" "$port" 3
done

echo "  Integration Layer (10950-10959)..."
for port in {10950..10959}; do
    card=$(find agent_cards/tier3 -name "*.json" -exec grep -l "\"url\": \"http://localhost:$port" {} \; 2>/dev/null | head -1)
    [ -f "$card" ] && start_agent "$card" "$port" 3
done

# Wait for all agents to start
sleep 5

# Count running agents
AGENT_COUNT=$(wc -l < .agent_pids 2>/dev/null || echo 0)

echo ""
echo "✅ Solopreneur Oracle System Started!"
echo "====================================="
echo "Total Agents Started: $AGENT_COUNT / 56"
echo ""
echo "🌐 Access Points:"
echo "  Oracle Master: http://localhost:10901"
echo "  MCP Server: http://localhost:10100"
echo ""
echo "📊 Status Check: ./check_solopreneur_status.sh"
echo "🛑 Stop All: ./stop_solopreneur_agents.sh"
echo ""
echo "📝 Logs are in the 'logs/' directory"