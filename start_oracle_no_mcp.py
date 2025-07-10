#!/usr/bin/env python3
# ABOUTME: Start solopreneur oracle agent without requiring MCP tools
# ABOUTME: Direct startup bypassing MCP initialization

import asyncio
import logging
import os
import sys
from aiohttp import web
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import after path setup
from a2a_mcp.agents.solopreneur_oracle.solopreneur_oracle_agent import SolopreneurOracleAgent

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    """Start the oracle agent without MCP tools."""
    logger.info("Starting Solopreneur Oracle Agent on port 10901 (without MCP tools)")
    
    # Validate environment
    try:
        from a2a_mcp.agents.solopreneur_oracle.base_solopreneur_agent import validate_environment
        validate_environment()
        logger.info("✓ Environment validation passed")
    except ValueError as e:
        logger.error(f"✗ Environment validation failed: {e}")
        return
    except ImportError:
        # Fallback validation
        if not os.environ.get('GOOGLE_API_KEY'):
            logger.error("✗ GOOGLE_API_KEY is required but not set")
            return
        logger.info("✓ Basic environment validation passed")
    
    # Create agent
    agent = SolopreneurOracleAgent()
    
    # Create web app
    app = web.Application()
    
    # Health check endpoint
    async def health_check(request):
        return web.json_response({"status": "healthy", "agent": agent.agent_name})
    
    # A2A endpoint for agent communication
    async def handle_a2a_request(request):
        try:
            data = await request.json()
            logger.info(f"Received A2A request: {data.get('method', 'unknown')}")
            
            # Handle A2A JSON-RPC protocol
            if data.get('method') == 'message/stream':
                params = data.get('params', {})
                message = params.get('message', {})
                text = message.get('parts', [{}])[0].get('text', '')
                
                # Process the query
                response = {
                    "jsonrpc": "2.0",
                    "id": data.get('id'),
                    "result": {
                        "content": f"Oracle Response: Processing query about '{text}' (MCP tools disabled for testing)",
                        "role": "assistant"
                    }
                }
                
                return web.json_response(response)
            else:
                return web.json_response({
                    "jsonrpc": "2.0",
                    "id": data.get('id'),
                    "error": {"code": -32601, "message": "Method not found"}
                })
                
        except Exception as e:
            logger.error(f"Error handling A2A request: {e}")
            return web.json_response({
                "jsonrpc": "2.0",
                "id": data.get('id', 'unknown'),
                "error": {"code": -32603, "message": str(e)}
            })
    
    # Register routes
    app.router.add_get('/health', health_check)
    app.router.add_post('/invoke', handle_a2a_request)
    
    # Start server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 10901)
    await site.start()
    
    logger.info("Oracle agent running on http://localhost:10901")
    logger.info("Health check: http://localhost:10901/health")
    logger.info("A2A endpoint: http://localhost:10901/invoke")
    
    # Keep running
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())