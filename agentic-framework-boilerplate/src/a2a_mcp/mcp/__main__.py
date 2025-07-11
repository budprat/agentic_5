# ABOUTME: Entry point for running the MCP server as a module
# ABOUTME: Supports command-line arguments for server configuration

import argparse
import os
from .server import serve


def main():
    """Main entry point for the MCP server."""
    parser = argparse.ArgumentParser(
        description='Agent-to-Agent Framework MCP Server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with stdio transport (default)
  python -m a2a_mcp.mcp
  
  # Run with SSE transport on specific host/port
  python -m a2a_mcp.mcp --transport sse --host 0.0.0.0 --port 8080
  
  # Specify custom agent cards directory
  python -m a2a_mcp.mcp --agent-cards-dir /path/to/agents
"""
    )
    
    parser.add_argument(
        '--host',
        default=os.getenv('MCP_HOST', 'localhost'),
        help='Host to bind the server to (default: localhost)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=int(os.getenv('MCP_PORT', '8080')),
        help='Port to bind the server to (default: 8080)'
    )
    
    parser.add_argument(
        '--transport',
        choices=['stdio', 'sse'],
        default=os.getenv('MCP_TRANSPORT', 'stdio'),
        help='Transport mechanism to use (default: stdio)'
    )
    
    parser.add_argument(
        '--agent-cards-dir',
        default=os.getenv('AGENT_CARDS_DIR', 'agent_cards'),
        help='Directory containing agent card JSON files (default: agent_cards)'
    )
    
    parser.add_argument(
        '--system-db',
        default=os.getenv('SYSTEM_DB', 'system.db'),
        help='Path to system database (default: system.db)'
    )
    
    args = parser.parse_args()
    
    # Set environment variables from command line arguments
    os.environ['AGENT_CARDS_DIR'] = args.agent_cards_dir
    os.environ['SYSTEM_DB'] = args.system_db
    
    # Start the server
    print(f"Starting MCP server with {args.transport} transport on {args.host}:{args.port}")
    print(f"Agent cards directory: {args.agent_cards_dir}")
    
    serve(host=args.host, port=args.port, transport=args.transport)


if __name__ == '__main__':
    main()