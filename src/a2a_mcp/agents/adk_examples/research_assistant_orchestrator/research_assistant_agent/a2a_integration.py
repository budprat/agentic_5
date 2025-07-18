"""
ABOUTME: A2A protocol integration for research agent communication
ABOUTME: Manages inter-agent communication with connection pooling and retry logic
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

# A2A-MCP Framework imports
import sys
sys.path.append('/Users/mac/Agents/agentic_5/src')
from a2a_mcp.common.a2a_protocol import A2AProtocolClient, create_a2a_request
from a2a_mcp.common.a2a_connection_pool import get_global_connection_pool
from a2a_mcp.common.metrics_collector import record_a2a_message

logger = logging.getLogger(__name__)


class ResearchA2AIntegration:
    """
    Manages A2A communication between research agents.
    
    Features:
    - Connection pooling for 60% performance improvement
    - Automatic retry with exponential backoff
    - Health monitoring for agent availability
    - Structured message formatting
    - Metric collection for communication patterns
    """
    
    def __init__(self, source_agent_name: str = "research_orchestrator"):
        """Initialize A2A integration for research agents."""
        self.source_agent = source_agent_name
        self.connection_pool = get_global_connection_pool()
        
        # Initialize A2A client with connection pooling
        self.a2a_client = A2AProtocolClient(
            connection_pool=self.connection_pool,
            source_agent_name=self.source_agent,
            default_timeout=60,
            max_retries=3,
            retry_delay=1.0
        )
        
        # Research agent port mapping (14000-14999 range)
        self.agent_ports = {
            "literature_review": 14001,
            "patent_analyzer": 14002,
            "experiment_designer": 14003,
            "data_synthesis": 14004,
            "hypothesis_generator": 14005,
            "grant_writer": 14006,
            "collaboration_finder": 14007,
            "publication_assistant": 14008,
            "methodology_analyzer": 14009,
            "citation_network": 14010
        }
        
        # Agent capabilities for routing decisions
        self.agent_capabilities = {
            "literature_review": {
                "description": "Searches and analyzes academic papers",
                "max_papers": 100,
                "sources": ["arxiv", "pubmed", "semantic_scholar"],
                "capabilities": ["search", "summarize", "extract_citations", "quality_assessment"]
            },
            "patent_analyzer": {
                "description": "Analyzes patent landscape and IP opportunities",
                "databases": ["uspto", "epo", "wipo"],
                "capabilities": ["prior_art_search", "claim_analysis", "infringement_risk"]
            },
            "experiment_designer": {
                "description": "Designs research experiments and protocols",
                "capabilities": ["hypothesis_formulation", "control_design", "statistical_planning"]
            },
            "data_synthesis": {
                "description": "Synthesizes data from multiple sources",
                "capabilities": ["meta_analysis", "data_fusion", "trend_analysis"]
            },
            "hypothesis_generator": {
                "description": "Generates and evaluates research hypotheses",
                "capabilities": ["hypothesis_creation", "testability_assessment", "novelty_check"]
            }
        }
        
        logger.info(f"Research A2A Integration initialized for {source_agent_name}")
    
    async def delegate_to_specialist(
        self, 
        specialist_name: str, 
        task: str, 
        context: Optional[Dict[str, Any]] = None,
        priority: str = "normal",
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Delegate task to specialist agent via A2A protocol.
        
        Args:
            specialist_name: Name of the specialist agent
            task: Task description or query
            context: Optional context including session_id, task_id, metadata
            priority: Task priority (low, normal, high, critical)
            timeout: Optional custom timeout in seconds
            
        Returns:
            Response from specialist agent with results
        """
        # Validate specialist
        if specialist_name not in self.agent_ports:
            raise ValueError(f"Unknown specialist: {specialist_name}. Available: {list(self.agent_ports.keys())}")
        
        port = self.agent_ports[specialist_name]
        
        # Prepare context with metadata
        full_context = {
            "source_agent": self.source_agent,
            "target_agent": specialist_name,
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
            "capabilities_requested": self._get_requested_capabilities(specialist_name, task)
        }
        
        if context:
            full_context.update(context)
        
        # Log delegation
        logger.info(f"Delegating to {specialist_name} on port {port}: {task[:100]}...")
        
        try:
            # Send message via A2A protocol
            response = await self.a2a_client.send_message(
                port=port,
                message=task,
                metadata=full_context,
                timeout=timeout
            )
            
            # Record successful communication
            record_a2a_message(
                source=self.source_agent,
                target=specialist_name,
                status="success",
                duration=response.get("duration", 0)
            )
            
            return response
            
        except Exception as e:
            # Record failed communication
            record_a2a_message(
                source=self.source_agent,
                target=specialist_name,
                status="error",
                error_type=type(e).__name__
            )
            
            logger.error(f"Failed to delegate to {specialist_name}: {e}")
            raise
    
    async def parallel_delegate(
        self,
        tasks: List[Dict[str, Any]],
        max_concurrent: int = 5
    ) -> Dict[str, Any]:
        """
        Delegate multiple tasks to specialists in parallel.
        
        Args:
            tasks: List of task dictionaries with 'specialist', 'task', 'context'
            max_concurrent: Maximum concurrent delegations
            
        Returns:
            Dictionary mapping specialist names to their responses
        """
        results = {}
        errors = {}
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def delegate_with_semaphore(task_info):
            async with semaphore:
                specialist = task_info["specialist"]
                try:
                    result = await self.delegate_to_specialist(
                        specialist_name=specialist,
                        task=task_info["task"],
                        context=task_info.get("context", {})
                    )
                    return specialist, result
                except Exception as e:
                    logger.error(f"Parallel delegation failed for {specialist}: {e}")
                    return specialist, {"error": str(e)}
        
        # Execute all delegations in parallel
        delegation_tasks = [
            delegate_with_semaphore(task_info) for task_info in tasks
        ]
        
        # Gather results
        responses = await asyncio.gather(*delegation_tasks, return_exceptions=True)
        
        # Process responses
        for response in responses:
            if isinstance(response, Exception):
                errors["exception"] = str(response)
            else:
                specialist, result = response
                if "error" in result:
                    errors[specialist] = result["error"]
                else:
                    results[specialist] = result
        
        return {
            "results": results,
            "errors": errors,
            "summary": {
                "total_tasks": len(tasks),
                "successful": len(results),
                "failed": len(errors)
            }
        }
    
    async def check_specialist_health(self, specialist_name: str) -> Dict[str, Any]:
        """
        Check health status of a specialist agent.
        
        Args:
            specialist_name: Name of the specialist to check
            
        Returns:
            Health status information
        """
        if specialist_name not in self.agent_ports:
            return {"status": "unknown", "error": "Specialist not found"}
        
        port = self.agent_ports[specialist_name]
        
        try:
            # Send health check request
            response = await self.a2a_client.send_message(
                port=port,
                message="health_check",
                metadata={"type": "health_check"},
                timeout=5  # Short timeout for health checks
            )
            
            return {
                "status": "healthy",
                "specialist": specialist_name,
                "port": port,
                "response_time": response.get("duration", 0),
                "details": response.get("health", {})
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "specialist": specialist_name,
                "port": port,
                "error": str(e)
            }
    
    async def check_all_specialists_health(self) -> Dict[str, Any]:
        """Check health of all registered specialists."""
        health_checks = []
        
        for specialist in self.agent_ports.keys():
            health = await self.check_specialist_health(specialist)
            health_checks.append(health)
        
        healthy_count = sum(1 for h in health_checks if h["status"] == "healthy")
        
        return {
            "summary": {
                "total_specialists": len(self.agent_ports),
                "healthy": healthy_count,
                "unhealthy": len(self.agent_ports) - healthy_count
            },
            "specialists": health_checks,
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_requested_capabilities(self, specialist_name: str, task: str) -> List[str]:
        """
        Determine which capabilities are needed based on task.
        
        Args:
            specialist_name: Target specialist
            task: Task description
            
        Returns:
            List of requested capabilities
        """
        capabilities = self.agent_capabilities.get(specialist_name, {}).get("capabilities", [])
        
        # Simple keyword matching for capability selection
        requested = []
        task_lower = task.lower()
        
        if specialist_name == "literature_review":
            if "search" in task_lower or "find" in task_lower:
                requested.append("search")
            if "summar" in task_lower:
                requested.append("summarize")
            if "citation" in task_lower:
                requested.append("extract_citations")
            if "quality" in task_lower or "assess" in task_lower:
                requested.append("quality_assessment")
                
        elif specialist_name == "patent_analyzer":
            if "prior art" in task_lower:
                requested.append("prior_art_search")
            if "claim" in task_lower:
                requested.append("claim_analysis")
            if "infringement" in task_lower or "risk" in task_lower:
                requested.append("infringement_risk")
        
        # Default to all capabilities if none specifically requested
        return requested if requested else capabilities
    
    def get_specialist_info(self, specialist_name: str) -> Dict[str, Any]:
        """Get information about a specialist's capabilities."""
        if specialist_name not in self.agent_ports:
            return {"error": f"Unknown specialist: {specialist_name}"}
        
        return {
            "name": specialist_name,
            "port": self.agent_ports[specialist_name],
            "capabilities": self.agent_capabilities.get(specialist_name, {}),
            "available": True  # Could check actual availability
        }
    
    def list_all_specialists(self) -> List[Dict[str, Any]]:
        """List all available specialists with their info."""
        specialists = []
        
        for name in self.agent_ports.keys():
            info = self.get_specialist_info(name)
            specialists.append(info)
        
        return specialists
    
    async def create_research_pipeline(
        self,
        research_query: str,
        required_specialists: List[str]
    ) -> Dict[str, Any]:
        """
        Create a research pipeline with multiple specialists.
        
        Args:
            research_query: Main research question
            required_specialists: List of specialists to involve
            
        Returns:
            Pipeline execution plan
        """
        # Validate specialists
        invalid = [s for s in required_specialists if s not in self.agent_ports]
        if invalid:
            raise ValueError(f"Invalid specialists: {invalid}")
        
        # Create execution plan
        pipeline = {
            "query": research_query,
            "specialists": required_specialists,
            "execution_order": self._determine_execution_order(required_specialists),
            "dependencies": self._identify_dependencies(required_specialists),
            "estimated_duration": len(required_specialists) * 30,  # 30s per specialist estimate
            "created_at": datetime.now().isoformat()
        }
        
        return pipeline
    
    def _determine_execution_order(self, specialists: List[str]) -> List[List[str]]:
        """
        Determine optimal execution order for specialists.
        
        Returns list of lists, where each inner list can run in parallel.
        """
        # Define dependencies between specialists
        dependencies = {
            "literature_review": [],  # Can run first
            "patent_analyzer": [],    # Can run first
            "data_synthesis": ["literature_review"],  # Needs literature
            "hypothesis_generator": ["literature_review", "data_synthesis"],
            "experiment_designer": ["hypothesis_generator"],
            "methodology_analyzer": ["literature_review"],
            "citation_network": ["literature_review"],
            "grant_writer": ["hypothesis_generator", "experiment_designer"],
            "publication_assistant": ["data_synthesis", "hypothesis_generator"],
            "collaboration_finder": []  # Can run independently
        }
        
        # Build execution levels
        levels = []
        remaining = set(specialists)
        completed = set()
        
        while remaining:
            # Find specialists that can run now
            current_level = []
            for specialist in remaining:
                deps = dependencies.get(specialist, [])
                if all(dep in completed or dep not in specialists for dep in deps):
                    current_level.append(specialist)
            
            if not current_level:
                # Circular dependency or missing dependency
                current_level = list(remaining)
            
            levels.append(current_level)
            completed.update(current_level)
            remaining.difference_update(current_level)
        
        return levels
    
    def _identify_dependencies(self, specialists: List[str]) -> Dict[str, List[str]]:
        """Identify dependencies between requested specialists."""
        # Simplified dependency mapping
        all_dependencies = {
            "data_synthesis": ["literature_review"],
            "hypothesis_generator": ["literature_review", "data_synthesis"],
            "experiment_designer": ["hypothesis_generator"],
            "grant_writer": ["hypothesis_generator", "experiment_designer"],
            "publication_assistant": ["data_synthesis", "hypothesis_generator"]
        }
        
        # Filter to only requested specialists
        dependencies = {}
        for specialist in specialists:
            if specialist in all_dependencies:
                deps = [d for d in all_dependencies[specialist] if d in specialists]
                if deps:
                    dependencies[specialist] = deps
        
        return dependencies