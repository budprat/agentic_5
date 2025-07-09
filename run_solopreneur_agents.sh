#!/bin/bash

# Solopreneur Oracle System Startup Script
# Launches all 6 solopreneur agents in the proper order

# Check if .env file exists
if [ -f .env ]; then
    # Load environment variables from .env file
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if GOOGLE_API_KEY is set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "Error: GOOGLE_API_KEY is not set!"
    echo "Please set it in the .env file or as an environment variable"
    echo "Example: export GOOGLE_API_KEY='your-api-key-here'"
    exit 1
fi

echo "🚀 Starting Solopreneur Oracle System..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Function to run a command in a new terminal
run_in_terminal() {
    local title=$1
    local command=$2
    
    # Try different terminal emulators
    if command -v gnome-terminal >/dev/null 2>&1; then
        gnome-terminal --title="$title" -- bash -c "$command; read -p 'Press enter to close...'"
    elif command -v xterm >/dev/null 2>&1; then
        xterm -title "$title" -e bash -c "$command; read -p 'Press enter to close...'"
    elif command -v konsole >/dev/null 2>&1; then
        konsole --title="$title" -e bash -c "$command; read -p 'Press enter to close...'"
    else
        # Fallback: run in background
        echo "Starting $title in background..."
        eval "$command" &
    fi
}

# Start MCP Server (required for all agents)
echo "📡 Starting MCP Server..."
run_in_terminal "MCP Server" "cd /home/solopreneur && python -m a2a_mcp.mcp.server --transport sse --host localhost --port 10100"

# Wait for MCP server to start
sleep 3

# Start Domain Specialists (Tier 2) - Order matters for dependencies
echo "🧠 Starting Domain Specialists (Tier 2)..."

echo "  🔧 Starting Technical Intelligence Agent (Port 10902)..."
run_in_terminal "Technical Intelligence Agent" "cd /home/solopreneur && python src/a2a_mcp/agents/__main__.py --agent-card agent_cards/technical_intelligence_agent.json --port 10902"

echo "  📚 Starting Knowledge Management Agent (Port 10903)..."
run_in_terminal "Knowledge Management Agent" "cd /home/solopreneur && python src/a2a_mcp/agents/__main__.py --agent-card agent_cards/knowledge_management_agent.json --port 10903"

echo "  ⚡ Starting Personal Optimization Agent (Port 10904)..."
run_in_terminal "Personal Optimization Agent" "cd /home/solopreneur && python src/a2a_mcp/agents/__main__.py --agent-card agent_cards/personal_optimization_agent.json --port 10904"

echo "  🎯 Starting Learning Enhancement Agent (Port 10905)..."
run_in_terminal "Learning Enhancement Agent" "cd /home/solopreneur && python src/a2a_mcp/agents/__main__.py --agent-card agent_cards/learning_enhancement_agent.json --port 10905"

echo "  🔗 Starting Integration Synthesis Agent (Port 10906)..."
run_in_terminal "Integration Synthesis Agent" "cd /home/solopreneur && python src/a2a_mcp/agents/__main__.py --agent-card agent_cards/integration_synthesis_agent.json --port 10906"

# Wait for domain specialists to start
sleep 5

# Start Master Oracle (Tier 1) - Must start after domain specialists
echo "🔮 Starting Master Oracle (Tier 1)..."
echo "  👑 Starting Solopreneur Oracle Agent (Port 10901)..."
run_in_terminal "Solopreneur Oracle Agent" "cd /home/solopreneur && python src/a2a_mcp/agents/__main__.py --agent-card agent_cards/solopreneur_oracle_agent.json --port 10901"

echo ""
echo "✅ All Solopreneur Oracle System services started!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Services running on:"
echo "  📡 MCP Server:                    http://localhost:10100"
echo "  👑 Solopreneur Oracle Agent:     http://localhost:10901"
echo "  🔧 Technical Intelligence Agent: http://localhost:10902"
echo "  📚 Knowledge Management Agent:   http://localhost:10903"
echo "  ⚡ Personal Optimization Agent:  http://localhost:10904"
echo "  🎯 Learning Enhancement Agent:   http://localhost:10905"
echo "  🔗 Integration Synthesis Agent:  http://localhost:10906"
echo ""
echo "🧪 Test the system:"
echo "  python test_solopreneur_integration.py"
echo ""
echo "🔥 Ready for AI developer/entrepreneur optimization!"