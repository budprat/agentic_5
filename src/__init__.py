"""Convience methods to start servers."""

try:
    import click
    from dotenv import load_dotenv
    from a2a_mcp.mcp import server
    CLICK_AVAILABLE = True
except ImportError:
    CLICK_AVAILABLE = False
    # Allow imports to work even without click for testing
    pass


if CLICK_AVAILABLE:
    @click.command()
    @click.option('--run', 'command', default='mcp-server', help='Command to run')
    @click.option(
        '--host',
        'host',
        default='localhost',
        help='Host on which the server is started or the client connects to',
    )
    @click.option(
        '--port',
        'port',
        default=10100,
        help='Port on which the server is started or the client connects to',
    )
    @click.option(
        '--transport',
        'transport',
        default='stdio',
        help='MCP Transport',
    )
    def main(command, host, port, transport) -> None:
        # Load environment variables
        load_dotenv()
        
        # TODO: Add other servers, perhaps dynamic port allocation
        if command == 'mcp-server':
            server.serve(host, port, transport)
        else:
            raise ValueError(f'Unknown run option: {command}')
else:
    def main(*args, **kwargs):
        print("Click not available. Install with: pip install click python-dotenv")