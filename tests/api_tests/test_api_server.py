#!/usr/bin/env python3
"""Simple API server for testing Video Generation System."""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
from typing import Dict, Any, List
import asyncio
import uuid

app = FastAPI(title="Video Generation API Test Server")

# In-memory storage for jobs
jobs_db = {}


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "service": "Video Generation API",
        "version": "1.0.0",
        "endpoints": {
            "generate": "/generate",
            "status": "/jobs/{job_id}/status",
            "content": "/jobs/{job_id}/content",
            "docs": "/docs"
        }
    }


@app.post("/generate")
async def generate_video(request: Dict[str, Any]):
    """Generate video content."""
    # Validate request
    if "content" not in request:
        raise HTTPException(status_code=400, detail="Missing 'content' field")
    
    # Create job
    job_id = str(uuid.uuid4())
    job = {
        "id": job_id,
        "status": "processing",
        "created_at": datetime.now().isoformat(),
        "request": request,
        "progress": 0
    }
    jobs_db[job_id] = job
    
    # Simulate async processing
    asyncio.create_task(process_video_generation(job_id))
    
    return {
        "job_id": job_id,
        "status": "accepted",
        "message": "Video generation started",
        "status_url": f"/jobs/{job_id}/status"
    }


async def process_video_generation(job_id: str):
    """Simulate video generation process."""
    job = jobs_db[job_id]
    
    # Simulate stages
    stages = [
        ("analyzing", 10, 2),
        ("script_writing", 30, 3),
        ("scene_design", 50, 3),
        ("timing_coordination", 70, 2),
        ("synthesis", 90, 2),
        ("completed", 100, 1)
    ]
    
    for stage, progress, duration in stages:
        await asyncio.sleep(duration)
        job["status"] = stage
        job["progress"] = progress
        
        if stage == "completed":
            # Generate result
            request = job["request"]
            job["result"] = {
                "script": {
                    "content": f"Generated script for: {request['content']}",
                    "duration": request.get("duration_preferences", {}).get("youtube", 300),
                    "style": request.get("style", "educational"),
                    "sections": [
                        {"title": "Introduction", "duration": 30},
                        {"title": "Main Content", "duration": 210},
                        {"title": "Conclusion", "duration": 60}
                    ]
                },
                "storyboard": {
                    "scenes": [
                        {"id": 1, "type": "title", "duration": 5},
                        {"id": 2, "type": "talking_head", "duration": 25},
                        {"id": 3, "type": "demonstration", "duration": 180},
                        {"id": 4, "type": "summary", "duration": 60},
                        {"id": 5, "type": "call_to_action", "duration": 30}
                    ],
                    "transitions": ["fade", "cut", "wipe", "fade"],
                    "visual_style": "modern_clean"
                },
                "timing": {
                    "total_duration": 300,
                    "pacing": "dynamic",
                    "key_moments": [30, 90, 180, 270],
                    "engagement_points": [45, 120, 225]
                },
                "quality_scores": {
                    "script_coherence": 0.92,
                    "visual_feasibility": 0.88,
                    "engagement_potential": 0.85,
                    "platform_compliance": 0.95,
                    "overall": 0.90
                },
                "platforms": {
                    "youtube": {
                        "optimized": True,
                        "duration": 300,
                        "format": "16:9"
                    },
                    "tiktok": {
                        "clips": [
                            {"start": 90, "end": 150, "hook": "Key insight"},
                            {"start": 180, "end": 240, "hook": "Main demo"}
                        ],
                        "format": "9:16"
                    }
                }
            }
            job["completed_at"] = datetime.now().isoformat()


@app.get("/jobs/{job_id}/status")
async def get_job_status(job_id: str):
    """Get job status."""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_db[job_id]
    return {
        "job_id": job_id,
        "status": job["status"],
        "progress": job["progress"],
        "created_at": job["created_at"],
        "completed_at": job.get("completed_at")
    }


@app.get("/jobs/{job_id}/content")
async def get_job_content(job_id: str):
    """Get generated content."""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_db[job_id]
    if job["status"] != "completed":
        raise HTTPException(
            status_code=202, 
            detail=f"Job still processing. Status: {job['status']}, Progress: {job['progress']}%"
        )
    
    return {
        "job_id": job_id,
        "request": job["request"],
        "result": job["result"],
        "created_at": job["created_at"],
        "completed_at": job["completed_at"]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "video-generation-api"}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Video Generation API Test Server')
    parser.add_argument('--port', type=int, default=8000, help='Port to run on (default: 8000)')
    args = parser.parse_args()
    
    print("=" * 80)
    print("Video Generation API Test Server")
    print("=" * 80)
    print(f"\nStarting server on http://localhost:{args.port}")
    print(f"API Documentation: http://localhost:{args.port}/docs")
    print("\nPress Ctrl+C to stop")
    print("=" * 80)
    
    uvicorn.run(app, host="0.0.0.0", port=args.port)