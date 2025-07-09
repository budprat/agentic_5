"""Patch to add solopreneur tools to MCP server."""

import logging

logger = logging.getLogger(__name__)

def apply_solopreneur_patch(server_module):
    """Apply solopreneur tools to existing server."""
    # Import at the module level
    import importlib
    import sys
    
    try:
        # Add import to server module
        if 'a2a_mcp.mcp.solopreneur_mcp_tools' not in sys.modules:
            solopreneur_tools = importlib.import_module('a2a_mcp.mcp.solopreneur_mcp_tools')
        
        # Get the server instance
        server = server_module.server
        
        # Initialize solopreneur tools
        from a2a_mcp.mcp.solopreneur_mcp_tools import init_solopreneur_tools
        init_solopreneur_tools(server)
        
        logger.info("✅ Solopreneur MCP tools integrated successfully!")
        return server
    
    except ImportError as e:
        logger.warning(f"Could not import solopreneur tools: {e}")
        return server_module.server
    except Exception as e:
        logger.error(f"Error applying solopreneur patch: {e}")
        return server_module.server