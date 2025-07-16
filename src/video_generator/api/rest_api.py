# ABOUTME: REST API endpoints for video generation system with FastAPI implementation
# ABOUTME: Provides HTTP endpoints for video script and storyboard generation workflows

"""
Video Generation REST API

This module implements REST API endpoints for the video generation system:
- Create video generation jobs
- Check job status and progress
- Retrieve generated content
- Platform-specific endpoints
- Health and metrics endpoints
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Literal
from datetime import datetime
import uuid
import asyncio
import json
from contextlib import asynccontextmanager

from video_generator.workflow.video_generation_workflow import VideoGenerationWorkflow
from video_generator.agents.video_orchestrator_v2 import VideoOrchestratorV2
from a2a_mcp.common.observability import get_logger, trace_span, record_metric
from a2a_mcp.common.a2a_connection_pool import ConnectionPool
from a2a_mcp.common.quality_framework import QualityThresholdFramework, QualityDomain


# Pydantic models for request/response validation
class VideoGenerationRequest(BaseModel):
    """Request model for video generation."""
    content: str = Field(..., description="The topic or content to create video about")
    platforms: List[Literal["youtube", "tiktok", "instagram_reels"]] = Field(
        default=["youtube"],
        description="Target platforms for the video"
    )
    style: Literal["educational", "entertainment", "marketing", "tutorial", "viral"] = Field(
        default="educational",
        description="Video style"
    )
    preferences: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional preferences like tone, audience, etc."
    )
    webhook_url: Optional[str] = Field(
        default=None,
        description="Webhook URL for job completion notification"
    )


class VideoGenerationResponse(BaseModel):
    """Response model for video generation job creation."""
    job_id: str
    status: str
    created_at: datetime
    estimated_completion_time: Optional[int] = Field(
        None,
        description="Estimated completion time in seconds"
    )
    message: str


class JobStatusResponse(BaseModel):
    """Response model for job status queries."""
    job_id: str
    status: Literal["pending", "running", "completed", "failed", "cancelled"]
    progress_percentage: float
    progress_details: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class VideoContentResponse(BaseModel):
    """Response model for completed video content."""
    job_id: str
    status: str
    outputs: Dict[str, Any]
    quality_validation: Dict[str, Any]
    metadata: Dict[str, Any]
    recommendations: List[str]


# Global resources
workflow_instance: Optional[VideoGenerationWorkflow] = None
connection_pool: Optional[ConnectionPool] = None
job_store: Dict[str, Dict[str, Any]] = {}
logger = get_logger("video_generation_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global workflow_instance, connection_pool
    
    # Startup
    logger.info("Starting Video Generation API")
    
    # Initialize connection pool
    connection_pool = ConnectionPool(
        max_connections_per_host=50,
        keepalive_timeout=30,
        connector_limit=100
    )
    
    # Initialize workflow
    workflow_instance = VideoGenerationWorkflow(
        connection_pool=connection_pool
    )
    
    yield
    
    # Shutdown
    logger.info("Shutting down Video Generation API")
    if workflow_instance:
        await workflow_instance.cleanup()
    if connection_pool:
        await connection_pool.close()


# Create FastAPI app
app = FastAPI(
    title="Video Generation API",
    description="API for generating video scripts and storyboards using AI agents",
    version="2.0.0",
    lifespan=lifespan
)


@app.post("/api/v1/generate", response_model=VideoGenerationResponse)
async def create_video_generation_job(
    request: VideoGenerationRequest,
    background_tasks: BackgroundTasks
):
    """Create a new video generation job."""
    job_id = str(uuid.uuid4())
    
    # Store job information
    job_store[job_id] = {
        "id": job_id,
        "status": "pending",
        "request": request.dict(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Add background task
    background_tasks.add_task(
        execute_video_generation,
        job_id,
        request.dict()
    )
    
    # Estimate completion time based on platform count
    estimated_time = 60 + (len(request.platforms) * 30)
    
    return VideoGenerationResponse(
        job_id=job_id,
        status="pending",
        created_at=job_store[job_id]["created_at"],
        estimated_completion_time=estimated_time,
        message="Video generation job created successfully"
    )


async def execute_video_generation(job_id: str, request: Dict[str, Any]):
    """Execute video generation workflow in background."""
    try:
        # Update job status
        job_store[job_id]["status"] = "running"
        job_store[job_id]["updated_at"] = datetime.utcnow()
        
        # Record metric
        record_metric(
            "video_generation_jobs_started",
            1,
            {"platform": ",".join(request.get("platforms", ["youtube"]))}
        )
        
        # Execute workflow
        result = await workflow_instance.execute(request)
        
        # Update job with result
        job_store[job_id].update({
            "status": "completed",
            "result": result,
            "completed_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        
        # Send webhook if provided
        if request.get("webhook_url"):
            await send_webhook_notification(
                request["webhook_url"],
                job_id,
                "completed"
            )
        
        # Record completion metric
        record_metric(
            "video_generation_jobs_completed",
            1,
            {"platform": ",".join(request.get("platforms", ["youtube"]))}
        )
        
    except Exception as e:
        logger.error(f"Video generation failed for job {job_id}: {str(e)}")
        
        # Update job with error
        job_store[job_id].update({
            "status": "failed",
            "error": str(e),
            "updated_at": datetime.utcnow()
        })
        
        # Send webhook for failure
        if request.get("webhook_url"):
            await send_webhook_notification(
                request["webhook_url"],
                job_id,
                "failed",
                error=str(e)
            )
        
        # Record failure metric
        record_metric(
            "video_generation_jobs_failed",
            1,
            {"platform": ",".join(request.get("platforms", ["youtube"]))}
        )


@app.get("/api/v1/jobs/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get the status of a video generation job."""
    if job_id not in job_store:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = job_store[job_id]
    
    # Get progress from workflow if running
    progress_percentage = 0.0
    progress_details = None
    
    if job["status"] == "running" and workflow_instance:
        workflow_status = await workflow_instance.get_workflow_status(job_id)
        if workflow_status["status"] != "not_found":
            progress_percentage = workflow_status["progress_percentage"]
            progress_details = workflow_status["progress_details"]
    elif job["status"] == "completed":
        progress_percentage = 100.0
    
    return JobStatusResponse(
        job_id=job_id,
        status=job["status"],
        progress_percentage=progress_percentage,
        progress_details=progress_details,
        created_at=job["created_at"],
        updated_at=job["updated_at"],
        completed_at=job.get("completed_at"),
        error=job.get("error")
    )


@app.get("/api/v1/jobs/{job_id}/content", response_model=VideoContentResponse)
async def get_job_content(job_id: str):
    """Get the generated content for a completed job."""
    if job_id not in job_store:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = job_store[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job is {job['status']}, not completed"
        )
    
    if "result" not in job:
        raise HTTPException(
            status_code=500,
            detail="Job completed but result not found"
        )
    
    result = job["result"]
    
    return VideoContentResponse(
        job_id=job_id,
        status=result.get("status", "completed"),
        outputs=result.get("outputs", {}),
        quality_validation=result.get("quality_validation", {}),
        metadata=result.get("metadata", {}),
        recommendations=result.get("recommendations", [])
    )


@app.delete("/api/v1/jobs/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a running job."""
    if job_id not in job_store:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = job_store[job_id]
    
    if job["status"] not in ["pending", "running"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job in {job['status']} status"
        )
    
    # Cancel workflow if running
    if workflow_instance:
        await workflow_instance.cancel_workflow(job_id)
    
    # Update job status
    job_store[job_id].update({
        "status": "cancelled",
        "updated_at": datetime.utcnow()
    })
    
    return {"message": "Job cancelled successfully", "job_id": job_id}


@app.get("/api/v1/jobs")
async def list_jobs(
    status: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
):
    """List all jobs with optional status filter."""
    # Filter jobs by status if provided
    filtered_jobs = list(job_store.values())
    
    if status:
        filtered_jobs = [j for j in filtered_jobs if j["status"] == status]
    
    # Sort by created_at descending
    filtered_jobs.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Apply pagination
    total = len(filtered_jobs)
    paginated = filtered_jobs[offset:offset + limit]
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "jobs": [
            {
                "job_id": job["id"],
                "status": job["status"],
                "created_at": job["created_at"],
                "platforms": job["request"]["platforms"]
            }
            for job in paginated
        ]
    }


# Platform-specific endpoints
@app.post("/api/v1/generate/youtube")
async def generate_youtube_video(
    content: str,
    style: str = "educational",
    background_tasks: BackgroundTasks = None
):
    """Generate video specifically for YouTube."""
    request = VideoGenerationRequest(
        content=content,
        platforms=["youtube"],
        style=style,
        preferences={"optimize_for": "youtube_algorithm"}
    )
    
    return await create_video_generation_job(request, background_tasks)


@app.post("/api/v1/generate/tiktok")
async def generate_tiktok_video(
    content: str,
    style: str = "viral",
    background_tasks: BackgroundTasks = None
):
    """Generate video specifically for TikTok."""
    request = VideoGenerationRequest(
        content=content,
        platforms=["tiktok"],
        style=style,
        preferences={"optimize_for": "tiktok_fyp"}
    )
    
    return await create_video_generation_job(request, background_tasks)


@app.post("/api/v1/generate/reels")
async def generate_instagram_reel(
    content: str,
    style: str = "entertainment",
    background_tasks: BackgroundTasks = None
):
    """Generate video specifically for Instagram Reels."""
    request = VideoGenerationRequest(
        content=content,
        platforms=["instagram_reels"],
        style=style,
        preferences={"optimize_for": "instagram_explore"}
    )
    
    return await create_video_generation_job(request, background_tasks)


# Health and metrics endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    # Check workflow health
    workflow_healthy = workflow_instance is not None
    
    # Check active jobs
    active_jobs = sum(
        1 for job in job_store.values()
        if job["status"] in ["pending", "running"]
    )
    
    return {
        "status": "healthy" if workflow_healthy else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "active_jobs": active_jobs,
        "total_jobs": len(job_store)
    }


@app.get("/metrics")
async def get_metrics():
    """Get API metrics."""
    # Calculate metrics
    total_jobs = len(job_store)
    jobs_by_status = {}
    
    for job in job_store.values():
        status = job["status"]
        jobs_by_status[status] = jobs_by_status.get(status, 0) + 1
    
    # Average completion time for completed jobs
    completed_jobs = [
        job for job in job_store.values()
        if job["status"] == "completed" and "completed_at" in job
    ]
    
    avg_completion_time = 0
    if completed_jobs:
        total_time = sum(
            (job["completed_at"] - job["created_at"]).total_seconds()
            for job in completed_jobs
        )
        avg_completion_time = total_time / len(completed_jobs)
    
    return {
        "total_jobs": total_jobs,
        "jobs_by_status": jobs_by_status,
        "average_completion_time_seconds": avg_completion_time,
        "timestamp": datetime.utcnow().isoformat()
    }


# Webhook helper
async def send_webhook_notification(
    webhook_url: str,
    job_id: str,
    status: str,
    error: Optional[str] = None
):
    """Send webhook notification for job status change."""
    try:
        # In production, use aiohttp or httpx for async HTTP
        logger.info(f"Webhook notification: {webhook_url} - Job {job_id} is {status}")
    except Exception as e:
        logger.error(f"Failed to send webhook: {str(e)}")


# Error handling
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Run with: uvicorn src.video_generator.api.rest_api:app --reload --port 8000
