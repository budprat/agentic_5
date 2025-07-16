# ABOUTME: Video Generation API module providing REST and WebSocket endpoints
# ABOUTME: Exports FastAPI applications for both synchronous and real-time interactions

"""
Video Generation API Module

This module provides:
- REST API for job-based video generation
- WebSocket API for real-time streaming generation
- Unified interface for client applications
"""

from .rest_api import app as rest_app
from .websocket_api import app as websocket_app

__all__ = ["rest_app", "websocket_app"]