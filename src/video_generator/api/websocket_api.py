# ABOUTME: WebSocket API for real-time video generation streaming with bidirectional communication
# ABOUTME: Provides WebSocket endpoints for live progress updates and artifact streaming

"""
Video Generation WebSocket API

This module implements WebSocket endpoints for real-time video generation:
- Real-time progress updates
- Streaming artifacts as they're generated
- Interactive mode support
- Live quality validation updates
- Bidirectional communication for dynamic adjustments
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, Any, List, Optional, Set
import json
import uuid
import asyncio
from datetime import datetime
from enum import Enum

from video_generator.agents.video_orchestrator_v2 import VideoOrchestratorV2
from video_generator.workflow.video_generation_workflow import VideoGenerationWorkflow
from a2a_mcp.common.observability import get_logger, trace_span, record_metric
from a2a_mcp.common.a2a_connection_pool import ConnectionPool
from a2a_mcp.common.quality_framework import QualityDomain


class MessageType(str, Enum):
    """WebSocket message types."""
    # Client to server
    GENERATE_REQUEST = "generate_request"
    CANCEL_REQUEST = "cancel_request"
    ADJUST_PARAMETERS = "adjust_parameters"
    PING = "ping"
    
    # Server to client
    JOB_STARTED = "job_started"
    PLANNING_UPDATE = "planning_update"
    AGENT_UPDATE = "agent_update"
    ARTIFACT_READY = "artifact_ready"
    PROGRESS_UPDATE = "progress_update"
    QUALITY_UPDATE = "quality_update"
    JOB_COMPLETED = "job_completed"
    JOB_FAILED = "job_failed"
    ERROR = "error"
    PONG = "pong"


class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_jobs: Dict[str, str] = {}  # connection_id -> job_id
        self.job_connections: Dict[str, Set[str]] = {}  # job_id -> set of connection_ids
        
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept and store connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        
    def disconnect(self, client_id: str):
        """Remove connection and clean up mappings."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            
        # Clean up job mappings
        if client_id in self.connection_jobs:
            job_id = self.connection_jobs[client_id]
            del self.connection_jobs[client_id]
            
            if job_id in self.job_connections:
                self.job_connections[job_id].discard(client_id)
                if not self.job_connections[job_id]:
                    del self.job_connections[job_id]
    
    def assign_job(self, client_id: str, job_id: str):
        """Assign a job to a connection."""
        self.connection_jobs[client_id] = job_id
        
        if job_id not in self.job_connections:
            self.job_connections[job_id] = set()
        self.job_connections[job_id].add(client_id)
    
    async def send_personal_message(self, message: Dict[str, Any], client_id: str):
        """Send message to specific client."""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            await websocket.send_json(message)
    
    async def broadcast_to_job(self, message: Dict[str, Any], job_id: str):
        """Broadcast message to all clients watching a job."""
        if job_id in self.job_connections:
            for client_id in self.job_connections[job_id]:
                await self.send_personal_message(message, client_id)


# Global resources
manager = ConnectionManager()
orchestrator: Optional[VideoOrchestratorV2] = None
workflow: Optional[VideoGenerationWorkflow] = None
active_jobs: Dict[str, Dict[str, Any]] = {}
logger = get_logger("video_generation_websocket")


# Create WebSocket app
app = FastAPI(
    title="Video Generation WebSocket API",
    description="WebSocket API for real-time video generation streaming",
    version="2.0.0"
)


@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup."""
    global orchestrator, workflow
    
    logger.info("Starting WebSocket API")
    
    # Initialize orchestrator
    orchestrator = VideoOrchestratorV2(
        enable_phase_7_streaming=True,
        enable_observability=True
    )
    
    # Initialize workflow
    connection_pool = ConnectionPool()
    workflow = VideoGenerationWorkflow(connection_pool=connection_pool)


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    logger.info("Shutting down WebSocket API")
    
    if workflow:
        await workflow.cleanup()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Main WebSocket endpoint for video generation."""
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == MessageType.GENERATE_REQUEST:
                await handle_generate_request(client_id, data)
                
            elif message_type == MessageType.CANCEL_REQUEST:
                await handle_cancel_request(client_id, data)
                
            elif message_type == MessageType.ADJUST_PARAMETERS:
                await handle_adjust_parameters(client_id, data)
                
            elif message_type == MessageType.PING:
                await manager.send_personal_message(
                    {"type": MessageType.PONG, "timestamp": datetime.utcnow().isoformat()},
                    client_id
                )
                
            else:
                await manager.send_personal_message(
                    {
                        "type": MessageType.ERROR,
                        "error": f"Unknown message type: {message_type}"
                    },
                    client_id
                )
                
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected")
        manager.disconnect(client_id)
        
        # Cancel any active jobs for this client
        if client_id in manager.connection_jobs:
            job_id = manager.connection_jobs[client_id]
            if job_id in active_jobs and active_jobs[job_id]["status"] == "running":
                await cancel_job(job_id)
                
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {str(e)}")
        manager.disconnect(client_id)


async def handle_generate_request(client_id: str, data: Dict[str, Any]):
    """Handle video generation request."""
    try:
        # Extract request parameters
        request = data.get("request", {})
        job_id = str(uuid.uuid4())
        
        # Store job information
        active_jobs[job_id] = {
            "id": job_id,
            "client_id": client_id,
            "status": "starting",
            "request": request,
            "created_at": datetime.utcnow()
        }
        
        # Assign job to connection
        manager.assign_job(client_id, job_id)
        
        # Send job started message
        await manager.send_personal_message(
            {
                "type": MessageType.JOB_STARTED,
                "job_id": job_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            client_id
        )
        
        # Start streaming generation
        asyncio.create_task(
            stream_video_generation(job_id, request)
        )
        
    except Exception as e:
        logger.error(f"Error handling generate request: {str(e)}")
        await manager.send_personal_message(
            {
                "type": MessageType.ERROR,
                "error": str(e)
            },
            client_id
        )


async def stream_video_generation(job_id: str, request: Dict[str, Any]):
    """Stream video generation with real-time updates."""
    try:
        # Update job status
        active_jobs[job_id]["status"] = "running"
        
        # Use orchestrator's streaming capability
        session_id = f"ws-{job_id}"
        
        async for event in orchestrator.generate_video_content(
            request,
            session_id,
            stream=True
        ):
            # Process different event types
            event_type = event.get("type", "")
            
            if event_type == "planning":
                await manager.broadcast_to_job(
                    {
                        "type": MessageType.PLANNING_UPDATE,
                        "job_id": job_id,
                        "content": event.get("content", ""),
                        "tasks": event.get("tasks", []),
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    job_id
                )
                
            elif event_type == "agent_update":
                await manager.broadcast_to_job(
                    {
                        "type": MessageType.AGENT_UPDATE,
                        "job_id": job_id,
                        "agent": event.get("agent", ""),
                        "action": event.get("action", ""),
                        "status": event.get("status", ""),
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    job_id
                )
                
            elif event_type == "artifact":
                artifact = event.get("artifact", {})
                await manager.broadcast_to_job(
                    {
                        "type": MessageType.ARTIFACT_READY,
                        "job_id": job_id,
                        "artifact_type": artifact.get("type", ""),
                        "artifact_id": artifact.get("id", ""),
                        "content": artifact.get("content", {}),
                        "metadata": artifact.get("metadata", {}),
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    job_id
                )
                
            elif event_type == "progress":
                await manager.broadcast_to_job(
                    {
                        "type": MessageType.PROGRESS_UPDATE,
                        "job_id": job_id,
                        "progress": event.get("progress", 0),
                        "current_task": event.get("current_task", ""),
                        "completed_tasks": event.get("completed_tasks", []),
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    job_id
                )
                
            elif event_type == "quality_update":
                await manager.broadcast_to_job(
                    {
                        "type": MessageType.QUALITY_UPDATE,
                        "job_id": job_id,
                        "metrics": event.get("metrics", {}),
                        "passed": event.get("passed", True),
                        "issues": event.get("issues", []),
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    job_id
                )
                
            elif event_type == "completion":
                # Final result
                active_jobs[job_id]["status"] = "completed"
                active_jobs[job_id]["result"] = event.get("result", {})
                
                await manager.broadcast_to_job(
                    {
                        "type": MessageType.JOB_COMPLETED,
                        "job_id": job_id,
                        "result": event.get("result", {}),
                        "duration": event.get("duration", 0),
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    job_id
                )
                
                # Record completion metric
                record_metric(
                    "websocket_jobs_completed",
                    1,
                    {"platform": ",".join(request.get("platforms", ["youtube"]))}
                )
                
    except Exception as e:
        logger.error(f"Error in video generation stream: {str(e)}")
        
        # Update job status
        active_jobs[job_id]["status"] = "failed"
        active_jobs[job_id]["error"] = str(e)
        
        # Send failure message
        await manager.broadcast_to_job(
            {
                "type": MessageType.JOB_FAILED,
                "job_id": job_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            },
            job_id
        )
        
        # Record failure metric
        record_metric(
            "websocket_jobs_failed",
            1,
            {"platform": ",".join(request.get("platforms", ["youtube"]))}
        )


async def handle_cancel_request(client_id: str, data: Dict[str, Any]):
    """Handle job cancellation request."""
    job_id = data.get("job_id")
    
    if not job_id:
        await manager.send_personal_message(
            {
                "type": MessageType.ERROR,
                "error": "Job ID required for cancellation"
            },
            client_id
        )
        return
    
    if job_id not in active_jobs:
        await manager.send_personal_message(
            {
                "type": MessageType.ERROR,
                "error": f"Job {job_id} not found"
            },
            client_id
        )
        return
    
    # Check if client owns the job
    job = active_jobs[job_id]
    if job["client_id"] != client_id:
        await manager.send_personal_message(
            {
                "type": MessageType.ERROR,
                "error": "Unauthorized to cancel this job"
            },
            client_id
        )
        return
    
    # Cancel the job
    await cancel_job(job_id)
    
    await manager.send_personal_message(
        {
            "type": "job_cancelled",
            "job_id": job_id,
            "timestamp": datetime.utcnow().isoformat()
        },
        client_id
    )


async def handle_adjust_parameters(client_id: str, data: Dict[str, Any]):
    """Handle dynamic parameter adjustment during generation."""
    job_id = data.get("job_id")
    adjustments = data.get("adjustments", {})
    
    if not job_id or job_id not in active_jobs:
        await manager.send_personal_message(
            {
                "type": MessageType.ERROR,
                "error": "Invalid job ID"
            },
            client_id
        )
        return
    
    job = active_jobs[job_id]
    
    if job["status"] != "running":
        await manager.send_personal_message(
            {
                "type": MessageType.ERROR,
                "error": f"Cannot adjust parameters for {job['status']} job"
            },
            client_id
        )
        return
    
    # Apply adjustments (this would interact with the running workflow)
    # For now, just acknowledge
    await manager.send_personal_message(
        {
            "type": "parameters_adjusted",
            "job_id": job_id,
            "adjustments": adjustments,
            "timestamp": datetime.utcnow().isoformat()
        },
        client_id
    )


async def cancel_job(job_id: str):
    """Cancel a running job."""
    if job_id in active_jobs:
        active_jobs[job_id]["status"] = "cancelled"
        # TODO: Implement actual cancellation in orchestrator


# Demo HTML page for testing
@app.get("/")
async def get():
    """Serve demo HTML page."""
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>Video Generation WebSocket Demo</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        #messages { border: 1px solid #ccc; height: 400px; overflow-y: scroll; padding: 10px; }
        .message { margin: 5px 0; padding: 5px; border-radius: 3px; }
        .sent { background: #e3f2fd; }
        .received { background: #f5f5f5; }
        .error { background: #ffebee; color: #c62828; }
        .artifact { background: #e8f5e9; }
        button { margin: 5px; padding: 10px; }
    </style>
</head>
<body>
    <h1>Video Generation WebSocket Demo</h1>
    
    <div>
        <button onclick="connect()">Connect</button>
        <button onclick="disconnect()">Disconnect</button>
        <button onclick="generateVideo()">Generate Video</button>
        <button onclick="cancelJob()">Cancel Job</button>
    </div>
    
    <div id="messages"></div>
    
    <script>
        let ws = null;
        let currentJobId = null;
        const clientId = 'demo-' + Math.random().toString(36).substr(2, 9);
        
        function addMessage(message, type = 'received') {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + type;
            messageDiv.textContent = typeof message === 'string' ? message : JSON.stringify(message, null, 2);
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function connect() {
            ws = new WebSocket(`ws://localhost:8001/ws/${clientId}`);
            
            ws.onopen = function(event) {
                addMessage('Connected to WebSocket');
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                
                if (data.type === 'job_started') {
                    currentJobId = data.job_id;
                    addMessage('Job started: ' + data.job_id);
                } else if (data.type === 'artifact_ready') {
                    addMessage('Artifact ready: ' + data.artifact_type, 'artifact');
                } else if (data.type === 'job_completed') {
                    addMessage('Job completed!', 'artifact');
                    currentJobId = null;
                }
                
                addMessage(data);
            };
            
            ws.onerror = function(error) {
                addMessage('WebSocket error: ' + error, 'error');
            };
            
            ws.onclose = function(event) {
                addMessage('Disconnected from WebSocket');
            };
        }
        
        function disconnect() {
            if (ws) {
                ws.close();
            }
        }
        
        function generateVideo() {
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                addMessage('Not connected', 'error');
                return;
            }
            
            const request = {
                type: 'generate_request',
                request: {
                    content: 'How to learn Python programming',
                    platforms: ['youtube', 'tiktok'],
                    style: 'educational'
                }
            };
            
            ws.send(JSON.stringify(request));
            addMessage(request, 'sent');
        }
        
        function cancelJob() {
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                addMessage('Not connected', 'error');
                return;
            }
            
            if (!currentJobId) {
                addMessage('No active job', 'error');
                return;
            }
            
            const request = {
                type: 'cancel_request',
                job_id: currentJobId
            };
            
            ws.send(JSON.stringify(request));
            addMessage(request, 'sent');
        }
    </script>
</body>
</html>
    """)


# Run with: uvicorn src.video_generator.api.websocket_api:app --reload --port 8001
