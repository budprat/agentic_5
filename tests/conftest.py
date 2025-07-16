# ABOUTME: Pytest configuration with real API fixtures for Video Script & Storyboard Generator testing
# ABOUTME: Provides shared fixtures, test data, and configuration for TDD implementation with no mocks

"""
Pytest Configuration for Video Generator Tests

This module provides:
- Real API client fixtures (no mocks)
- Test data generators
- Shared test utilities
- Performance tracking
- Coverage configuration
"""

import pytest
import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Any, List
import json
import time
from datetime import datetime
import aiohttp
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

# Import framework components
from src.a2a_mcp.common.connection_pool import ConnectionPool
from src.a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from src.a2a_mcp.common.quality_framework import QualityThresholdFramework
from src.a2a_mcp.common.observability import get_logger

# Test configuration
TEST_CONFIG = {
    "gemini_api_key": os.getenv("GEMINI_API_KEY"),
    "gemini_model": "gemini-2.0-flash-exp",
    "test_timeout": 30,
    "real_api_calls": True,
    "video_formats": ["youtube", "tiktok", "instagram_reels"],
    "quality_domain": "BUSINESS"
}

# Ensure we have API key for real testing
if not TEST_CONFIG["gemini_api_key"]:
    pytest.skip("GEMINI_API_KEY not set - required for real API testing", allow_module_level=True)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def connection_pool():
    """Real connection pool for agent communication."""
    pool = ConnectionPool(
        max_connections_per_host=10,
        keepalive_timeout=30,
        connector_limit=100
    )
    yield pool
    await pool.close()


@pytest.fixture(scope="session")
def quality_framework():
    """Real quality framework instance."""
    return QualityThresholdFramework()


@pytest.fixture
def test_logger():
    """Logger for tests."""
    return get_logger("test_video_generator")


@pytest.fixture
def video_request_samples():
    """Sample video generation requests for testing."""
    return {
        "youtube_educational": {
            "content": "How to learn Python programming",
            "platforms": ["youtube"],
            "style": "educational",
            "preferences": {
                "tone": "friendly",
                "pace": "moderate",
                "audience": "beginners"
            }
        },
        "tiktok_viral": {
            "content": "5 Python tricks that will blow your mind",
            "platforms": ["tiktok"],
            "style": "entertainment",
            "preferences": {
                "tone": "energetic",
                "pace": "fast",
                "audience": "general"
            }
        },
        "reels_tutorial": {
            "content": "Build a web scraper in 60 seconds",
            "platforms": ["instagram_reels"],
            "style": "tutorial",
            "preferences": {
                "tone": "concise",
                "pace": "rapid",
                "audience": "developers"
            }
        },
        "multi_platform": {
            "content": "Understanding async programming",
            "platforms": ["youtube", "tiktok", "instagram_reels"],
            "style": "educational",
            "preferences": {
                "tone": "clear",
                "pace": "adaptive",
                "audience": "intermediate"
            }
        }
    }


@pytest.fixture
def quality_thresholds():
    """Quality threshold configurations for testing."""
    return {
        "script_coherence": 0.85,
        "visual_feasibility": 0.80,
        "engagement_potential": 0.75,
        "platform_compliance": 0.90
    }


@pytest.fixture
def format_constraints():
    """Platform-specific format constraints."""
    return {
        "youtube": {
            "min_duration": 60,
            "max_duration": 1200,
            "structure": ["hook", "intro", "main_content", "outro", "cta"],
            "requires": ["chapters", "description", "tags"]
        },
        "tiktok": {
            "min_duration": 15,
            "max_duration": 60,
            "structure": ["hook", "story", "loop"],
            "requires": ["trending_audio", "hashtags", "effects"]
        },
        "instagram_reels": {
            "min_duration": 15,
            "max_duration": 90,
            "structure": ["hook", "value", "cta"],
            "requires": ["cover_frame", "music", "hashtags"]
        }
    }


@pytest.fixture
async def real_gemini_client():
    """Real Gemini API client for testing."""
    import google.generativeai as genai
    
    genai.configure(api_key=TEST_CONFIG["gemini_api_key"])
    model = genai.GenerativeModel(TEST_CONFIG["gemini_model"])
    
    return model


@pytest.fixture
def performance_tracker():
    """Track performance metrics during tests."""
    class PerformanceTracker:
        def __init__(self):
            self.metrics = []
        
        def start(self, operation: str):
            return {
                "operation": operation,
                "start_time": time.time(),
                "context": {}
            }
        
        def end(self, context: Dict[str, Any], **kwargs):
            context["end_time"] = time.time()
            context["duration"] = context["end_time"] - context["start_time"]
            context.update(kwargs)
            self.metrics.append(context)
        
        def get_report(self):
            if not self.metrics:
                return "No metrics collected"
            
            total_duration = sum(m["duration"] for m in self.metrics)
            avg_duration = total_duration / len(self.metrics)
            
            return {
                "total_operations": len(self.metrics),
                "total_duration": total_duration,
                "average_duration": avg_duration,
                "operations": self.metrics
            }
    
    return PerformanceTracker()


@pytest.fixture
def agent_port_registry():
    """Registry of agent ports for testing."""
    return {
        "video_orchestrator": 10106,
        "script_writer": 10212,
        "scene_designer": 10213,
        "timing_coordinator": 10214,
        "hook_creator": 10215,
        "shot_describer": 10301,
        "transition_planner": 10302,
        "cta_generator": 10303
    }


@pytest.fixture
async def cleanup_agents(agent_port_registry):
    """Cleanup any running agents after tests."""
    yield
    # Cleanup code to stop any agents that might still be running
    for agent_name, port in agent_port_registry.items():
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(f"http://localhost:{port}/shutdown", timeout=5)
        except:
            pass  # Agent might not be running


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "real_api: mark test as using real API"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        # Add integration marker to tests in integration directory
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Add real_api marker to all tests (since we don't use mocks)
        item.add_marker(pytest.mark.real_api)


# Test utilities
class TestDataGenerator:
    """Generate test data for video generation."""
    
    @staticmethod
    def generate_script_segment(duration: int, style: str) -> Dict[str, Any]:
        """Generate a script segment for testing."""
        return {
            "duration": duration,
            "type": "narration",
            "content": f"Test content for {style} style video",
            "timing": {
                "start": 0,
                "end": duration
            },
            "cues": ["visual", "audio"]
        }
    
    @staticmethod
    def generate_scene(scene_number: int, duration: int) -> Dict[str, Any]:
        """Generate a scene for testing."""
        return {
            "scene_number": scene_number,
            "duration": duration,
            "shots": [
                {
                    "shot_number": 1,
                    "type": "wide",
                    "duration": duration / 2
                },
                {
                    "shot_number": 2,
                    "type": "close-up",
                    "duration": duration / 2
                }
            ],
            "description": f"Scene {scene_number} description"
        }


@pytest.fixture
def test_data_generator():
    """Provide test data generator."""
    return TestDataGenerator()


# Coverage configuration
def pytest_sessionfinish(session, exitstatus):
    """Generate coverage report after test session."""
    if session.config.option.cov:
        print("\n\nCoverage Report:")
        print("=" * 80)
        # Coverage report will be generated by pytest-cov


# Async test helpers
async def wait_for_condition(condition_func, timeout=10, interval=0.1):
    """Wait for a condition to become true."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if await condition_func():
            return True
        await asyncio.sleep(interval)
    return False


async def assert_eventually(assertion_func, timeout=10, interval=0.1):
    """Assert that a condition eventually becomes true."""
    result = await wait_for_condition(assertion_func, timeout, interval)
    assert result, f"Condition did not become true within {timeout} seconds"