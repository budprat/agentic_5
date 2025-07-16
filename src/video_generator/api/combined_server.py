# ABOUTME: Combined API server running both REST and WebSocket endpoints on different ports
# ABOUTME: Provides unified entry point for the complete video generation API service

"""
Combined Video Generation API Server

This module runs both REST and WebSocket APIs concurrently:
- REST API on port 8000
- WebSocket API on port 8001
"""

import asyncio
import uvicorn
from contextlib import asynccontextmanager
import signal
import sys

from a2a_mcp.common.observability import get_logger, init_observability
from a2a_mcp.common.metrics_collector import MetricsCollector


logger = get_logger("video_generation_api_server")


class APIServer:
    """Combined API server for video generation."""
    
    def __init__(self):
        self.rest_server = None
        self.websocket_server = None
        self.metrics_collector = MetricsCollector()
        
    async def start_rest_api(self):
        """Start REST API server."""
        from .rest_api import app
        
        config = uvicorn.Config(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True
        )
        self.rest_server = uvicorn.Server(config)
        
        logger.info("Starting REST API on port 8000")
        await self.rest_server.serve()
        
    async def start_websocket_api(self):
        """Start WebSocket API server."""
        from .websocket_api import app
        
        config = uvicorn.Config(
            app,
            host="0.0.0.0",
            port=8001,
            log_level="info",
            access_log=True
        )
        self.websocket_server = uvicorn.Server(config)
        
        logger.info("Starting WebSocket API on port 8001")
        await self.websocket_server.serve()
        
    async def start_metrics_server(self):
        """Start Prometheus metrics server."""
        logger.info("Starting metrics server on port 9090")
        await self.metrics_collector.start_metrics_server(port=9090)
        
    async def run(self):
        """Run all servers concurrently."""
        # Initialize observability
        init_observability(service_name="video_generation_api")
        
        # Create tasks for all servers
        tasks = [
            asyncio.create_task(self.start_rest_api()),
            asyncio.create_task(self.start_websocket_api()),
            asyncio.create_task(self.start_metrics_server())
        ]
        
        # Wait for all servers
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
            raise
            
    async def shutdown(self):
        """Gracefully shutdown all servers."""
        logger.info("Shutting down API servers")
        
        if self.rest_server:
            self.rest_server.should_exit = True
            
        if self.websocket_server:
            self.websocket_server.should_exit = True


# Global server instance
server = APIServer()


def signal_handler(sig, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {sig}")
    asyncio.create_task(server.shutdown())
    sys.exit(0)


async def main():
    """Main entry point."""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Print startup information
    print("=" * 60)
    print("Video Generation API Server")
    print("=" * 60)
    print("REST API:      http://localhost:8000")
    print("WebSocket API: ws://localhost:8001")
    print("Metrics:       http://localhost:9090/metrics")
    print("=" * 60)
    print("\nAPI Documentation:")
    print("REST API Docs:      http://localhost:8000/docs")
    print("WebSocket Demo:     http://localhost:8001/")
    print("=" * 60)
    
    # Run servers
    await server.run()


# Helper functions for test compatibility
async def run_rest_api():
    """Run REST API server (helper for tests)."""
    server = APIServer()
    await server.start_rest_api()

async def run_websocket_api():
    """Run WebSocket API server (helper for tests)."""
    server = APIServer()
    await server.start_websocket_api()


if __name__ == "__main__":
    asyncio.run(main())