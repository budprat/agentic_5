#!/bin/bash

# Market Oracle Startup Script
# This script verifies configuration and starts all agents

echo "=================================="
echo "Market Oracle Startup"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Please copy .env.market_oracle.example to .env and configure your API keys"
    exit 1
fi

# Load environment variables
source .env

# Function to check if a variable is set
check_var() {
    if [ -z "${!1}" ]; then
        echo -e "${RED}✗ $1 is not set${NC}"
        return 1
    else
        echo -e "${GREEN}✓ $1 is configured${NC}"
        return 0
    fi
}

echo -e "\n${YELLOW}Checking Core Configuration...${NC}"
check_var "GOOGLE_API_KEY"

echo -e "\n${YELLOW}Checking Agent-Specific APIs...${NC}"
echo "Sentiment Seeker (Reddit):"
check_var "REDDIT_CLIENT_ID"
check_var "REDDIT_CLIENT_SECRET"

echo -e "\nFundamental Analyst (BrightData):"
check_var "BRIGHTDATA_API_TOKEN"

echo -e "\nTechnical Prophet (HuggingFace):"
check_var "HUGGINGFACE_API_KEY"

echo -e "\nRisk Guardian (Snowflake):"
check_var "SNOWFLAKE_ACCOUNT"
check_var "SNOWFLAKE_USER"
check_var "SNOWFLAKE_PASSWORD"

echo -e "\nTrend Correlator (Google Trends):"
check_var "GOOGLE_TRENDS_API_KEY"

echo -e "\nReport Synthesizer (Notion):"
check_var "NOTION_API_KEY"

echo -e "\nAudio Briefer (ElevenLabs):"
check_var "ELEVENLABS_API_KEY"

# Check Supabase configuration
echo -e "\n${YELLOW}Checking Supabase Configuration...${NC}"
check_var "SUPABASE_URL"
check_var "SUPABASE_ANON_KEY"
check_var "SUPABASE_SERVICE_ROLE_KEY"

# Test Supabase connection
echo -e "\n${YELLOW}Testing Supabase Connection...${NC}"
if .venv/bin/python -c "import os; from src.a2a_mcp.common.supabase_client import SupabaseClient; client = SupabaseClient.get_client(); print('Connected')" 2>/dev/null; then
    echo -e "${GREEN}✓ Supabase connection successful${NC}"
else
    echo -e "${RED}✗ Failed to connect to Supabase${NC}"
    echo "Please check your Supabase credentials in .env"
    exit 1
fi

# Check if MCP server is already running
echo -e "\n${YELLOW}Checking MCP Server...${NC}"
if lsof -Pi :10100 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${GREEN}✓ MCP Server already running on port 10100${NC}"
else
    echo "Starting MCP Server..."
    uv run a2a-mcp --run mcp-server --transport sse --host localhost --port 10100 > logs/mcp-server.log 2>&1 &
    MCP_PID=$!
    sleep 5
    
    if lsof -Pi :10100 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${GREEN}✓ MCP Server started (PID: $MCP_PID)${NC}"
    else
        echo -e "${RED}✗ Failed to start MCP Server${NC}"
        exit 1
    fi
fi

# Function to start an agent
start_agent() {
    local agent_name=$1
    local agent_card=$2
    local port=$3
    
    echo -e "\n${YELLOW}Starting $agent_name on port $port...${NC}"
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${GREEN}✓ $agent_name already running${NC}"
    else
        uv run src/a2a_mcp/agents/ --agent-card agent_cards/$agent_card --port $port > logs/$agent_card.log 2>&1 &
        sleep 2
        
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
            echo -e "${GREEN}✓ $agent_name started${NC}"
        else
            echo -e "${RED}✗ Failed to start $agent_name${NC}"
        fi
    fi
}

# Start all agents
echo -e "\n${YELLOW}Starting Market Oracle Agents...${NC}"

start_agent "Oracle Prime" "oracle_prime_agent.json" 10501
start_agent "Sentiment Seeker" "sentiment_seeker_agent.json" 10502
start_agent "Fundamental Analyst" "fundamental_analyst_agent.json" 10503
start_agent "Technical Prophet" "technical_prophet_agent.json" 10504
start_agent "Risk Guardian" "risk_guardian_agent.json" 10505
start_agent "Trend Correlator" "trend_correlator_agent.json" 10506
start_agent "Report Synthesizer" "report_synthesizer_agent.json" 10507
start_agent "Audio Briefer" "audio_briefer_agent.json" 10508

echo -e "\n${GREEN}=================================="
echo "Market Oracle is running!"
echo "==================================${NC}"
echo ""
echo "Access points:"
echo "  - MCP Server: http://localhost:10100"
echo "  - Oracle Prime: http://localhost:10501"
echo "  - Sentiment Seeker: http://localhost:10502"
echo "  - Fundamental Analyst: http://localhost:10503"
echo "  - Technical Prophet: http://localhost:10504"
echo "  - Risk Guardian: http://localhost:10505"
echo "  - Trend Correlator: http://localhost:10506"
echo "  - Report Synthesizer: http://localhost:10507"
echo "  - Audio Briefer: http://localhost:10508"
echo ""
echo "Logs are available in the logs/ directory"
echo ""
echo "To test the system, run:"
echo "  python demo_market_oracle.py"
echo ""
echo "To stop all services, run:"
echo "  pkill -f 'a2a-mcp'"