# ABOUTME: Starlette application for A2A MCP Framework with WebSocket and HTTP support
# ABOUTME: Manages routes, middleware, and application lifecycle for production deployments

import logging
from typing import Dict, Any, Optional, List
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route, WebSocketRoute
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
import json

from .handlers import DefaultRequestHandler
from .task_store import InMemoryTaskStore
from .notifier import InMemoryPushNotifier

logger = logging.getLogger(__name__)


class A2AStarletteApplication:
    """Production-ready Starlette application for A2A MCP Framework.
    
    Features:
    - HTTP and WebSocket endpoints
    - Task management with persistence
    - Push notification support
    - CORS and security middleware
    - Health check endpoints
    - Graceful error handling
    """
    
    def __init__(
        self,
        agent_card: Optional[Any] = None,  # AgentCard type
        http_handler: Optional['DefaultRequestHandler'] = None,
        task_store: Optional['InMemoryTaskStore'] = None,
        push_notifier: Optional['InMemoryPushNotifier'] = None,
        cors_origins: Optional[List[str]] = None,
        trusted_hosts: Optional[List[str]] = None,
        debug: bool = False
    ):
        """Initialize the Starlette application.
        
        Args:
            agent_card: Agent configuration card
            http_handler: Request handler with agent executor
            task_store: Task persistence store (creates default if None)
            push_notifier: Push notification service (creates default if None)
            cors_origins: Allowed CORS origins (defaults to ["*"])
            trusted_hosts: Trusted host headers (defaults to ["*"])
            debug: Enable debug mode
        """
        self.agent_card = agent_card
        self.task_store = task_store or InMemoryTaskStore()
        self.push_notifier = push_notifier or InMemoryPushNotifier()
        self.debug = debug
        
        # Configure middleware
        middleware = [
            Middleware(
                CORSMiddleware,
                allow_origins=cors_origins or ["*"],
                allow_methods=["*"],
                allow_headers=["*"],
            )
        ]
        
        if trusted_hosts:
            middleware.append(
                Middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)
            )
        
        # Configure routes
        routes = [
            Route("/", self.index, methods=["GET"]),
            Route("/health", self.health_check, methods=["GET"]),
            Route("/api/v1/agent/execute", self.execute_agent, methods=["POST"]),
            Route("/api/v1/tasks/{task_id}", self.get_task, methods=["GET"]),
            Route("/api/v1/tasks", self.list_tasks, methods=["GET"]),
            WebSocketRoute("/ws/notifications", self.notification_websocket),
        ]
        
        # Create Starlette app
        self.app = Starlette(
            debug=debug,
            routes=routes,
            middleware=middleware,
            on_startup=[self.startup],
            on_shutdown=[self.shutdown]
        )
        
        # Request handler - use provided or create default
        self.request_handler = http_handler or DefaultRequestHandler(
            task_store=self.task_store,
            push_notifier=self.push_notifier
        )
        
        logger.info("A2AStarletteApplication initialized")
    
    def build(self):
        """Build and return the Starlette application instance.
        
        Returns:
            Starlette application ready for uvicorn
        """
        return self.app
    
    async def startup(self):
        """Application startup handler."""
        logger.info("A2A MCP Framework server starting up...")
        # Initialize any async resources here
        await self.task_store.initialize()
        await self.push_notifier.initialize()
    
    async def shutdown(self):
        """Application shutdown handler."""
        logger.info("A2A MCP Framework server shutting down...")
        # Clean up async resources
        await self.task_store.cleanup()
        await self.push_notifier.cleanup()
    
    async def index(self, request: Request) -> PlainTextResponse:
        """Root endpoint."""
        return PlainTextResponse(
            "A2A MCP Framework Server v2.0\n"
            "Production-ready with Starlette/uvicorn architecture\n\n"
            "Endpoints:\n"
            "- GET  /health - Health check\n"
            "- POST /api/v1/agent/execute - Execute agent task\n"
            "- GET  /api/v1/tasks/{task_id} - Get task status\n"
            "- GET  /api/v1/tasks - List all tasks\n"
            "- WS   /ws/notifications - WebSocket notifications\n"
        )
    
    async def health_check(self, request: Request) -> JSONResponse:
        """Health check endpoint."""
        health_status = {
            "status": "healthy",
            "service": "a2a-mcp-framework",
            "version": "2.0.0",
            "components": {
                "task_store": await self.task_store.health_check(),
                "push_notifier": await self.push_notifier.health_check(),
            }
        }
        
        # Check if all components are healthy
        all_healthy = all(
            component.get("status") == "healthy"
            for component in health_status["components"].values()
        )
        
        return JSONResponse(
            health_status,
            status_code=200 if all_healthy else 503
        )
    
    async def execute_agent(self, request: Request) -> JSONResponse:
        """Execute an agent task."""
        try:
            # Parse request body
            body = await request.json()
            
            # Validate required fields
            if "agent_name" not in body:
                return JSONResponse(
                    {"error": "Missing required field: agent_name"},
                    status_code=400
                )
            
            if "query" not in body:
                return JSONResponse(
                    {"error": "Missing required field: query"},
                    status_code=400
                )
            
            # Process request through handler
            result = await self.request_handler.handle_agent_request(
                agent_name=body["agent_name"],
                query=body["query"],
                context_id=body.get("context_id"),
                metadata=body.get("metadata", {})
            )
            
            return JSONResponse(result)
            
        except json.JSONDecodeError:
            return JSONResponse(
                {"error": "Invalid JSON in request body"},
                status_code=400
            )
        except Exception as e:
            logger.error(f"Error executing agent: {e}")
            return JSONResponse(
                {"error": f"Internal server error: {str(e)}"},
                status_code=500
            )
    
    async def get_task(self, request: Request) -> JSONResponse:
        """Get task status by ID."""
        task_id = request.path_params["task_id"]
        
        task = await self.task_store.get_task(task_id)
        if not task:
            return JSONResponse(
                {"error": f"Task {task_id} not found"},
                status_code=404
            )
        
        return JSONResponse(task)
    
    async def list_tasks(self, request: Request) -> JSONResponse:
        """List all tasks with optional filtering."""
        # Get query parameters
        status = request.query_params.get("status")
        agent_name = request.query_params.get("agent_name")
        limit = int(request.query_params.get("limit", "100"))
        offset = int(request.query_params.get("offset", "0"))
        
        # Get tasks from store
        tasks = await self.task_store.list_tasks(
            status=status,
            agent_name=agent_name,
            limit=limit,
            offset=offset
        )
        
        return JSONResponse({
            "tasks": tasks,
            "total": len(tasks),
            "limit": limit,
            "offset": offset
        })
    
    async def notification_websocket(self, websocket):
        """WebSocket endpoint for real-time notifications."""
        await websocket.accept()
        
        # Subscribe to push notifications
        subscription_id = await self.push_notifier.subscribe(websocket)
        
        try:
            # Keep connection alive
            while True:
                # Wait for client messages (e.g., ping/pong)
                message = await websocket.receive_text()
                
                # Handle ping
                if message == "ping":
                    await websocket.send_text("pong")
                    
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            # Unsubscribe on disconnect
            await self.push_notifier.unsubscribe(subscription_id)