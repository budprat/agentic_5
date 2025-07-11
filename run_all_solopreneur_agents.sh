#!/bin/bash
# Startup script for limited Solopreneur Oracle system (Tier 3: AWIE, scheduler, trends only)

echo "🚀 Starting AI Solopreneur Oracle System (LIMITED Tier 3: AWIE, scheduler, trends only)..."
echo "===================================================================================="

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
    # Use direct execution of __main__.py
    python src/a2a_mcp/agents/__main__.py --agent-card $card_file --port $port > logs/agent_$port.log 2>&1 &
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
echo "⚡ TIER 3: Starting LIMITED Intelligence Modules (AWIE, scheduler, trends only)..."

# AI Research Analyzer (trends) - Port 10910  
echo "  Starting AI Research Analyzer (trends)..."
start_agent "agent_cards/tier3/ai_research_analyzer.json" 10910 3

# Recovery Scheduler - Port 10935
echo "  Starting Recovery Scheduler..."
start_agent "agent_cards/tier3/recovery_scheduler.json" 10935 3

# Spaced Repetition Scheduler - Port 10944
echo "  Starting Spaced Repetition Scheduler..."
start_agent "agent_cards/tier3/spaced_repetition_scheduler.json" 10944 3

# AWIE Scheduler Agent - Port 10980 (requires special handling)
echo "  Starting AWIE Scheduler Agent..."
python -c "
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))

async def run_awie():
    try:
        from a2a_mcp.agents.tier3.awie_scheduler_agent import AWIESchedulerAgent
        agent = AWIESchedulerAgent()
        print('✅ AWIE Scheduler Agent started on port 10980')
        while True:
            await asyncio.sleep(10)
    except Exception as e:
        print(f'❌ AWIE Scheduler failed: {e}')

asyncio.run(run_awie())
" > logs/awie_scheduler.log 2>&1 &
echo $! >> .agent_pids

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