#!/bin/bash
# ABOUTME: Main startup script that validates environment, sources config, and launches the A2A framework
# ABOUTME: Provides user-friendly output and error handling for system initialization

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Banner
echo "============================================"
echo "   A2A MCP Framework Launcher"
echo "   Agentic Framework Boilerplate"
echo "============================================"
echo ""

# Step 1: Check Python version
print_info "Checking Python version..."
if ! command_exists python3; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_error "Python $REQUIRED_VERSION or higher is required. Found: Python $PYTHON_VERSION"
    exit 1
fi
print_success "Python $PYTHON_VERSION detected"

# Step 2: Source environment variables
print_info "Loading environment configuration..."

# Check for .env file in configs directory
ENV_FILE="$PROJECT_ROOT/configs/.env"
ENV_TEMPLATE="$PROJECT_ROOT/configs/.env.template"

if [ -f "$ENV_FILE" ]; then
    print_info "Loading environment from $ENV_FILE"
    set -a  # Mark variables for export
    source "$ENV_FILE"
    set +a
    print_success "Environment variables loaded"
else
    print_warning "No .env file found at $ENV_FILE"
    if [ -f "$ENV_TEMPLATE" ]; then
        print_info "Template file exists at: $ENV_TEMPLATE"
        print_info "To create your .env file, run:"
        echo "    cp $ENV_TEMPLATE $ENV_FILE"
        echo "    # Then edit $ENV_FILE with your values"
    fi
fi

# Step 3: Validate prerequisites
print_info "Validating prerequisites..."

# Check for required environment variables
MISSING_VARS=()

if [ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "your_google_api_key_here" ]; then
    MISSING_VARS+=("GOOGLE_API_KEY")
fi

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    print_error "Missing required environment variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "    - $var"
    done
    echo ""
    print_info "Please set these variables in your .env file or export them:"
    for var in "${MISSING_VARS[@]}"; do
        echo "    export $var=your_value_here"
    done
    exit 1
fi

# Check if agent_cards directory exists
AGENT_CARDS_DIR="$PROJECT_ROOT/agent_cards"
if [ ! -d "$AGENT_CARDS_DIR" ]; then
    print_error "Agent cards directory not found: $AGENT_CARDS_DIR"
    print_info "Please ensure the agent_cards directory exists with agent configuration files."
    exit 1
fi

# Count agent cards
AGENT_COUNT=$(find "$AGENT_CARDS_DIR" -name "*.json" -type f | wc -l)
if [ "$AGENT_COUNT" -eq 0 ]; then
    print_warning "No agent configuration files (*.json) found in $AGENT_CARDS_DIR"
else
    print_success "Found $AGENT_COUNT agent configuration(s)"
fi

# Check if src/a2a_mcp module exists
if [ ! -d "$PROJECT_ROOT/src/a2a_mcp" ]; then
    print_error "A2A MCP module not found at: $PROJECT_ROOT/src/a2a_mcp"
    print_info "Please ensure you're running from the project root directory."
    exit 1
fi

print_success "All prerequisites validated"

# Step 4: Set up Python path
export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"
print_info "Python path configured: $PYTHONPATH"

# Step 5: Create logs directory if it doesn't exist
LOG_DIR="$PROJECT_ROOT/logs"
if [ ! -d "$LOG_DIR" ]; then
    print_info "Creating logs directory..."
    mkdir -p "$LOG_DIR"
fi

# Step 6: Launch the system
print_info "Starting A2A MCP Framework..."
echo ""

# Change to project root
cd "$PROJECT_ROOT"

# Set default MCP configuration if not provided
export MCP_SERVER_HOST="${MCP_SERVER_HOST:-localhost}"
export MCP_SERVER_PORT="${MCP_SERVER_PORT:-8080}"
export AGENT_CARDS_DIR="${AGENT_CARDS_DIR:-agent_cards}"

print_info "MCP Server Configuration:"
echo "    Host: $MCP_SERVER_HOST"
echo "    Port: $MCP_SERVER_PORT"
echo "    Agent Cards: $AGENT_CARDS_DIR"
echo ""

# Launch with proper error handling
python3 "$SCRIPT_DIR/launch_system.py" 2>&1 | tee "$LOG_DIR/startup_$(date +%Y%m%d_%H%M%S).log"

# Check exit status
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    print_success "System launched successfully!"
else
    print_error "System launch failed. Check the logs for details."
    exit 1
fi