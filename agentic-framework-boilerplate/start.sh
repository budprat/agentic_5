#!/bin/bash
# ABOUTME: Main startup script for the A2A MCP Framework
# ABOUTME: Launches MCP server and agent system with proper environment setup

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
MCP_PORT=${MCP_PORT:-10100}
LOG_DIR=${LOG_DIR:-"logs"}
VENV_PATH=${VENV_PATH:-".venv"}

# Functions
print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}   A2A MCP Framework Startup Script${NC}"
    echo -e "${BLUE}============================================${NC}"
    echo ""
}

check_python() {
    echo -e "${YELLOW}Checking Python installation...${NC}"
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error: Python 3 is not installed${NC}"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓ Python ${PYTHON_VERSION} found${NC}"
}

setup_venv() {
    echo -e "${YELLOW}Setting up virtual environment...${NC}"
    
    if [ ! -d "$VENV_PATH" ]; then
        echo "Creating virtual environment..."
        python3 -m venv "$VENV_PATH"
    fi
    
    # Activate virtual environment
    source "$VENV_PATH/bin/activate"
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
}

install_dependencies() {
    echo -e "${YELLOW}Installing dependencies...${NC}"
    
    # Upgrade pip
    pip install --upgrade pip > /dev/null 2>&1
    
    # Install from pyproject.toml if it exists, otherwise use requirements.txt
    if [ -f "pyproject.toml" ]; then
        echo "Installing from pyproject.toml..."
        pip install -e . > /dev/null 2>&1
    elif [ -f "requirements.txt" ]; then
        echo "Installing from requirements.txt..."
        pip install -r requirements.txt > /dev/null 2>&1
    else
        echo -e "${RED}Error: No pyproject.toml or requirements.txt found${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Dependencies installed${NC}"
}

setup_directories() {
    echo -e "${YELLOW}Setting up directories...${NC}"
    
    # Create necessary directories
    mkdir -p "$LOG_DIR"
    mkdir -p "cache"
    mkdir -p "agent_cards"
    
    echo -e "${GREEN}✓ Directories created${NC}"
}

check_environment() {
    echo -e "${YELLOW}Checking environment variables...${NC}"
    
    # Check for .env file
    if [ -f ".env" ]; then
        echo "Loading environment variables from .env..."
        export $(cat .env | grep -v '^#' | xargs)
    else
        echo -e "${YELLOW}Warning: No .env file found${NC}"
        echo "Using default configuration..."
    fi
    
    # Display configuration
    echo ""
    echo "Configuration:"
    echo "  MCP Server Port: $MCP_PORT"
    echo "  Log Directory: $LOG_DIR"
    echo ""
}

cleanup_old_processes() {
    echo -e "${YELLOW}Cleaning up old processes...${NC}"
    
    # Kill any existing MCP server processes
    if pgrep -f "python.*mcp.*server" > /dev/null; then
        echo "Stopping existing MCP server..."
        pkill -f "python.*mcp.*server" || true
        sleep 2
    fi
    
    # Kill any existing agent processes
    if pgrep -f "python.*a2a_mcp.*agent" > /dev/null; then
        echo "Stopping existing agents..."
        pkill -f "python.*a2a_mcp.*agent" || true
        sleep 2
    fi
    
    echo -e "${GREEN}✓ Cleanup complete${NC}"
}

start_mcp_server() {
    echo -e "${YELLOW}Starting MCP server...${NC}"
    
    # Start MCP server in background
    nohup python -m a2a_mcp.mcp.server > "$LOG_DIR/mcp_server.log" 2>&1 &
    MCP_PID=$!
    
    # Wait for server to start
    sleep 3
    
    # Check if server is running
    if kill -0 $MCP_PID 2>/dev/null; then
        echo -e "${GREEN}✓ MCP server started (PID: $MCP_PID)${NC}"
        echo $MCP_PID > mcp_server.pid
    else
        echo -e "${RED}Error: Failed to start MCP server${NC}"
        echo "Check logs at: $LOG_DIR/mcp_server.log"
        exit 1
    fi
}

start_example_agents() {
    echo -e "${YELLOW}Starting example agents...${NC}"
    
    # Start example agents if they exist
    if [ -d "src/a2a_mcp/agents/example_domain" ]; then
        echo "Starting example domain agents..."
        
        # Start master oracle
        nohup python -m a2a_mcp.agents.example_domain.master_oracle > "$LOG_DIR/master_oracle.log" 2>&1 &
        echo $! > master_oracle.pid
        
        # Start domain specialist
        nohup python -m a2a_mcp.agents.example_domain.domain_specialist > "$LOG_DIR/domain_specialist.log" 2>&1 &
        echo $! > domain_specialist.pid
        
        # Start service agent
        nohup python -m a2a_mcp.agents.example_domain.service_agent > "$LOG_DIR/service_agent.log" 2>&1 &
        echo $! > service_agent.pid
        
        sleep 2
        echo -e "${GREEN}✓ Example agents started${NC}"
    else
        echo "No example agents found to start"
    fi
}

show_status() {
    echo ""
    echo -e "${BLUE}System Status:${NC}"
    echo "=============="
    
    # Check MCP server
    if [ -f "mcp_server.pid" ] && kill -0 $(cat mcp_server.pid) 2>/dev/null; then
        echo -e "MCP Server: ${GREEN}Running${NC} (PID: $(cat mcp_server.pid))"
    else
        echo -e "MCP Server: ${RED}Not Running${NC}"
    fi
    
    # Check agents
    for pidfile in *.pid; do
        if [ -f "$pidfile" ] && [ "$pidfile" != "mcp_server.pid" ]; then
            agent_name=$(basename "$pidfile" .pid)
            if kill -0 $(cat "$pidfile") 2>/dev/null; then
                echo -e "$agent_name: ${GREEN}Running${NC} (PID: $(cat $pidfile))"
            else
                echo -e "$agent_name: ${RED}Not Running${NC}"
            fi
        fi
    done
    
    echo ""
    echo "Logs are available in: $LOG_DIR/"
    echo ""
    echo -e "${YELLOW}To stop all services, run: ./stop.sh${NC}"
}

# Main execution
main() {
    print_header
    check_python
    setup_venv
    install_dependencies
    setup_directories
    check_environment
    cleanup_old_processes
    start_mcp_server
    start_example_agents
    show_status
    
    echo -e "${GREEN}✓ A2A MCP Framework started successfully!${NC}"
}

# Run main function
main