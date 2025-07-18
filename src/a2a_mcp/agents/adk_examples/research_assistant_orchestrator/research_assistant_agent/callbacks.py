"""
ABOUTME: Advanced callbacks for research orchestrator
ABOUTME: Implements progress tracking, caching, and session management
"""

from datetime import datetime
from typing import Optional, Dict, Any
import json
import time

from google.adk.agents.callback_context import CallbackContext
from google.genai import types


class ResearchProgressTracker:
    """Track research progress across sessions"""
    
    def __init__(self):
        self.start_times = {}
        self.paper_cache = {}
        self.search_cache = {}
    
    def before_agent_callback(self, callback_context: CallbackContext) -> Optional[types.Content]:
        """
        Execute before agent processing - initialize tracking
        """
        state = callback_context.state
        agent_name = callback_context.agent_name if hasattr(callback_context, 'agent_name') else 'unknown'
        
        # Initialize research session
        if "research_session_id" not in state:
            state["research_session_id"] = f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            state["papers_analyzed"] = 0
            state["citations_collected"] = []
            state["research_timeline"] = []
            state["search_queries"] = []
            state["key_insights"] = []
        
        # Track agent start
        self.start_times[agent_name] = time.time()
        
        # Log research action
        state["research_timeline"].append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "action": "started",
            "query": callback_context.state.get("current_query", "")
        })
        
        # Check cache for repeated queries
        current_query = state.get("current_query", "")
        if current_query and current_query in self.search_cache:
            print(f"[CACHE HIT] Using cached results for: {current_query}")
            # Could return cached content here to skip processing
        
        print(f"\n{'='*60}")
        print(f"[RESEARCH] Starting: {agent_name}")
        print(f"Session ID: {state['research_session_id']}")
        print(f"Papers analyzed so far: {state['papers_analyzed']}")
        print(f"{'='*60}\n")
        
        return None
    
    def after_agent_callback(self, callback_context: CallbackContext) -> Optional[types.Content]:
        """
        Execute after agent processing - save progress and insights
        """
        state = callback_context.state
        agent_name = callback_context.agent_name if hasattr(callback_context, 'agent_name') else 'unknown'
        
        # Calculate duration
        duration = time.time() - self.start_times.get(agent_name, time.time())
        
        # Update statistics based on agent type
        if "literature_review" in agent_name:
            # Extract paper count from results
            if hasattr(callback_context, 'result'):
                result = callback_context.result
                if hasattr(result, 'papers_analyzed'):
                    state["papers_analyzed"] += len(result.papers_analyzed)
                if hasattr(result, 'key_findings'):
                    state["key_insights"].extend(result.key_findings)
        
        # Log completion
        state["research_timeline"].append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "action": "completed",
            "duration": f"{duration:.2f}s",
            "papers_added": state["papers_analyzed"]
        })
        
        # Cache results for future use
        current_query = state.get("current_query", "")
        if current_query and hasattr(callback_context, 'result'):
            self.search_cache[current_query] = {
                "result": callback_context.result,
                "timestamp": datetime.now().isoformat(),
                "duration": duration
            }
        
        print(f"\n{'='*60}")
        print(f"[RESEARCH] Completed: {agent_name}")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Total papers analyzed: {state['papers_analyzed']}")
        print(f"Key insights found: {len(state.get('key_insights', []))}")
        print(f"{'='*60}\n")
        
        # Save session state periodically
        if state["papers_analyzed"] % 10 == 0 and state["papers_analyzed"] > 0:
            self._save_session_state(state)
        
        return None
    
    def _save_session_state(self, state: Dict[str, Any]):
        """Save session state to file for recovery"""
        session_file = f".research_sessions/{state['research_session_id']}.json"
        
        # Create session data
        session_data = {
            "session_id": state["research_session_id"],
            "papers_analyzed": state["papers_analyzed"],
            "key_insights": state.get("key_insights", []),
            "research_timeline": state.get("research_timeline", []),
            "last_updated": datetime.now().isoformat()
        }
        
        # Save to file (in production, use proper storage)
        print(f"[SESSION] Saving research progress to {session_file}")
        # json.dump(session_data, open(session_file, 'w'), indent=2)


# Create singleton instance
research_progress_tracker = ResearchProgressTracker()


def research_progress_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """Main callback function for research progress tracking"""
    return research_progress_tracker.before_agent_callback(callback_context)


def save_research_state_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """Main callback function for saving research state"""
    return research_progress_tracker.after_agent_callback(callback_context)


class ResearchCacheManager:
    """Manage caching for expensive research operations"""
    
    def __init__(self, cache_ttl: int = 3600):
        self.paper_cache = {}
        self.search_cache = {}
        self.analysis_cache = {}
        self.cache_ttl = cache_ttl  # Time to live in seconds
    
    def get_cached_paper(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached paper data"""
        if paper_id in self.paper_cache:
            cached = self.paper_cache[paper_id]
            if time.time() - cached["timestamp"] < self.cache_ttl:
                return cached["data"]
        return None
    
    def cache_paper(self, paper_id: str, paper_data: Dict[str, Any]):
        """Cache paper data"""
        self.paper_cache[paper_id] = {
            "data": paper_data,
            "timestamp": time.time()
        }
    
    def get_cached_search(self, query: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached search results"""
        if query in self.search_cache:
            cached = self.search_cache[query]
            if time.time() - cached["timestamp"] < self.cache_ttl:
                return cached["data"]
        return None
    
    def cache_search(self, query: str, results: Dict[str, Any]):
        """Cache search results"""
        self.search_cache[query] = {
            "data": results,
            "timestamp": time.time()
        }
    
    def clear_expired_cache(self):
        """Remove expired cache entries"""
        current_time = time.time()
        
        # Clear expired papers
        self.paper_cache = {
            k: v for k, v in self.paper_cache.items()
            if current_time - v["timestamp"] < self.cache_ttl
        }
        
        # Clear expired searches
        self.search_cache = {
            k: v for k, v in self.search_cache.items()
            if current_time - v["timestamp"] < self.cache_ttl
        }


# Create cache manager instance
research_cache_manager = ResearchCacheManager()


def log_research_metrics(state: Dict[str, Any]):
    """Log research metrics for monitoring"""
    metrics = {
        "session_id": state.get("research_session_id", "unknown"),
        "papers_analyzed": state.get("papers_analyzed", 0),
        "citations_collected": len(state.get("citations_collected", [])),
        "key_insights": len(state.get("key_insights", [])),
        "search_queries": len(state.get("search_queries", [])),
        "timeline_events": len(state.get("research_timeline", [])),
        "timestamp": datetime.now().isoformat()
    }
    
    print("\n[METRICS] Research Session Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    print()