"""
ABOUTME: Parallel workflow management for research tasks
ABOUTME: Enables efficient execution of independent research activities
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# A2A-MCP Framework imports
import sys
sys.path.append('/Users/mac/Agents/agentic_5/src')
from a2a_mcp.common.enhanced_workflow import DynamicWorkflowGraph, WorkflowNode, WorkflowState
from a2a_mcp.common.parallel_workflow import ParallelWorkflowGraph
from a2a_mcp.common.observability import trace_async, record_metric

# Local imports
from .a2a_integration import ResearchA2AIntegration

logger = logging.getLogger(__name__)


class ResearchTaskType(Enum):
    """Types of research tasks for workflow optimization."""
    LITERATURE_SEARCH = "literature_search"
    PATENT_ANALYSIS = "patent_analysis"
    DATA_SYNTHESIS = "data_synthesis"
    HYPOTHESIS_GENERATION = "hypothesis_generation"
    EXPERIMENT_DESIGN = "experiment_design"
    CITATION_ANALYSIS = "citation_analysis"
    METHODOLOGY_REVIEW = "methodology_review"
    GRANT_WRITING = "grant_writing"


@dataclass
class ResearchTask:
    """Enhanced research task with parallel execution metadata."""
    id: str
    type: ResearchTaskType
    description: str
    specialist: str
    dependencies: Set[str]
    priority: int = 1
    estimated_duration: int = 30
    can_parallelize: bool = True
    metadata: Dict[str, Any] = None


class ResearchWorkflowManager:
    """
    Manages parallel execution of research tasks.
    
    Features:
    - Automatic parallelization detection
    - Dependency resolution
    - Resource optimization
    - Progress tracking
    - Quality checkpoints
    """
    
    def __init__(self):
        """Initialize research workflow manager."""
        self.dynamic_workflow = DynamicWorkflowGraph()
        self.parallel_workflow = ParallelWorkflowGraph()
        self.a2a_integration = ResearchA2AIntegration()
        
        # Task execution statistics
        self.execution_stats = {
            "total_tasks": 0,
            "parallel_executions": 0,
            "sequential_executions": 0,
            "average_speedup": 1.0
        }
        
        logger.info("Research Workflow Manager initialized")
    
    @trace_async("create_research_workflow")
    async def create_research_workflow(
        self, 
        research_plan: Dict[str, Any],
        optimization_level: str = "balanced"
    ) -> DynamicWorkflowGraph:
        """
        Create optimized workflow from research plan.
        
        Args:
            research_plan: Research plan with tasks and dependencies
            optimization_level: "speed" | "quality" | "balanced"
            
        Returns:
            Optimized workflow graph
        """
        # Extract tasks from plan
        tasks = self._extract_research_tasks(research_plan)
        
        # Analyze for parallelization opportunities
        parallel_groups = self._identify_parallel_tasks(tasks, optimization_level)
        
        # Build workflow graph
        workflow = await self._build_optimized_workflow(parallel_groups, tasks)
        
        # Add quality checkpoints
        if optimization_level in ["quality", "balanced"]:
            workflow = self._add_quality_checkpoints(workflow)
        
        # Record workflow metrics
        record_metric('research_workflow_created', 1, {
            'task_count': str(len(tasks)),
            'parallel_groups': str(len(parallel_groups)),
            'optimization': optimization_level
        })
        
        return workflow
    
    def _extract_research_tasks(self, research_plan: Dict[str, Any]) -> List[ResearchTask]:
        """Extract research tasks from plan."""
        tasks = []
        
        for task_data in research_plan.get("tasks", []):
            task = ResearchTask(
                id=task_data.get("id", f"task_{len(tasks)}"),
                type=ResearchTaskType(task_data.get("type", "literature_search")),
                description=task_data.get("description", ""),
                specialist=task_data.get("specialist", "literature_review"),
                dependencies=set(task_data.get("dependencies", [])),
                priority=task_data.get("priority", 1),
                estimated_duration=task_data.get("duration", 30),
                can_parallelize=task_data.get("can_parallelize", True),
                metadata=task_data.get("metadata", {})
            )
            tasks.append(task)
        
        return tasks
    
    def _identify_parallel_tasks(
        self, 
        tasks: List[ResearchTask],
        optimization_level: str
    ) -> List[List[ResearchTask]]:
        """
        Identify tasks that can run in parallel.
        
        Uses topological sorting with parallel level detection.
        """
        # Build dependency graph
        task_map = {task.id: task for task in tasks}
        dependents = {task.id: set() for task in tasks}
        
        for task in tasks:
            for dep in task.dependencies:
                if dep in dependents:
                    dependents[dep].add(task.id)
        
        # Find parallel execution levels
        parallel_groups = []
        completed = set()
        remaining = set(task.id for task in tasks)
        
        while remaining:
            # Find tasks that can run now
            current_group = []
            
            for task_id in remaining:
                task = task_map[task_id]
                # Check if all dependencies are completed
                if task.dependencies.issubset(completed):
                    # Check parallelization constraints
                    if self._can_parallelize(task, current_group, optimization_level):
                        current_group.append(task)
            
            if not current_group:
                # Handle circular dependencies
                logger.warning("Potential circular dependency detected")
                current_group = [task_map[remaining.pop()]]
            
            parallel_groups.append(current_group)
            completed.update(task.id for task in current_group)
            remaining.difference_update(task.id for task in current_group)
        
        return parallel_groups
    
    def _can_parallelize(
        self, 
        task: ResearchTask,
        current_group: List[ResearchTask],
        optimization_level: str
    ) -> bool:
        """Determine if task can be parallelized with current group."""
        if not task.can_parallelize:
            return False
        
        # Optimization level constraints
        if optimization_level == "speed":
            # Aggressive parallelization
            return len(current_group) < 10  # Max 10 parallel tasks
        elif optimization_level == "quality":
            # Conservative parallelization for quality
            return len(current_group) < 3 and task.priority <= 2
        else:  # balanced
            # Balanced approach
            return len(current_group) < 5
    
    async def _build_optimized_workflow(
        self,
        parallel_groups: List[List[ResearchTask]],
        all_tasks: List[ResearchTask]
    ) -> DynamicWorkflowGraph:
        """Build optimized workflow from parallel groups."""
        workflow = DynamicWorkflowGraph()
        node_map = {}
        
        # Create nodes for each task
        for task in all_tasks:
            node = WorkflowNode(
                task=task.description,
                node_key=task.specialist,
                node_label=f"{task.type.value}: {task.id}",
                metadata={
                    "task_type": task.type.value,
                    "priority": task.priority,
                    "estimated_duration": task.estimated_duration,
                    "can_parallelize": task.can_parallelize
                }
            )
            workflow.add_node(node)
            node_map[task.id] = node
        
        # Add edges based on dependencies
        for task in all_tasks:
            for dep_id in task.dependencies:
                if dep_id in node_map:
                    workflow.add_edge(node_map[dep_id].id, node_map[task.id].id)
        
        # Mark parallel groups in metadata
        for i, group in enumerate(parallel_groups):
            for task in group:
                node = node_map[task.id]
                node.metadata["parallel_group"] = i
                node.metadata["group_size"] = len(group)
        
        return workflow
    
    def _add_quality_checkpoints(
        self, 
        workflow: DynamicWorkflowGraph
    ) -> DynamicWorkflowGraph:
        """Add quality validation checkpoints to workflow."""
        # Add checkpoint after each parallel group
        checkpoint_nodes = []
        
        # Group nodes by parallel group
        groups = {}
        for node_id, node in workflow.nodes.items():
            group_id = node.metadata.get("parallel_group", -1)
            if group_id not in groups:
                groups[group_id] = []
            groups[group_id].append(node)
        
        # Add quality checkpoint after each group
        for group_id, nodes in groups.items():
            if group_id >= 0:  # Valid group
                checkpoint = WorkflowNode(
                    task=f"Quality checkpoint for group {group_id}",
                    node_key="quality_validator",
                    node_label=f"QC-{group_id}",
                    metadata={
                        "checkpoint_type": "quality",
                        "group_id": group_id,
                        "validation_threshold": 0.8
                    }
                )
                workflow.add_node(checkpoint)
                
                # Connect all nodes in group to checkpoint
                for node in nodes:
                    workflow.add_edge(node.id, checkpoint.id)
                
                checkpoint_nodes.append(checkpoint)
        
        return workflow
    
    @trace_async("execute_parallel_research")
    async def execute_parallel_research(
        self,
        workflow: DynamicWorkflowGraph,
        session_id: str,
        max_concurrent: int = 5
    ) -> Dict[str, Any]:
        """
        Execute research workflow with parallel optimization.
        
        Args:
            workflow: Research workflow to execute
            session_id: Session identifier
            max_concurrent: Maximum concurrent tasks
            
        Returns:
            Execution results with performance metrics
        """
        start_time = datetime.now()
        results = {}
        errors = {}
        
        # Get execution plan
        execution_levels = workflow.get_execution_plan()
        
        logger.info(f"Executing research workflow with {len(execution_levels)} levels")
        
        # Execute each level
        for level_idx, level_nodes in enumerate(execution_levels):
            level_start = datetime.now()
            
            # Determine if level can be parallelized
            if len(level_nodes) > 1 and all(
                workflow.nodes[node_id].metadata.get("can_parallelize", True)
                for node_id in level_nodes
            ):
                # Parallel execution
                level_results = await self._execute_parallel_level(
                    level_nodes, workflow, session_id, max_concurrent
                )
                self.execution_stats["parallel_executions"] += len(level_nodes)
            else:
                # Sequential execution
                level_results = await self._execute_sequential_level(
                    level_nodes, workflow, session_id
                )
                self.execution_stats["sequential_executions"] += len(level_nodes)
            
            # Collect results
            for node_id, result in level_results.items():
                if "error" in result:
                    errors[node_id] = result["error"]
                else:
                    results[node_id] = result
            
            # Record level metrics
            level_duration = (datetime.now() - level_start).total_seconds()
            record_metric('research_level_duration', level_duration, {
                'level': str(level_idx),
                'node_count': str(len(level_nodes)),
                'execution_type': 'parallel' if len(level_nodes) > 1 else 'sequential'
            })
        
        # Calculate execution metrics
        total_duration = (datetime.now() - start_time).total_seconds()
        sequential_estimate = sum(
            workflow.nodes[node_id].metadata.get("estimated_duration", 30)
            for node_id in workflow.nodes
        )
        speedup = sequential_estimate / total_duration if total_duration > 0 else 1.0
        
        # Update statistics
        self.execution_stats["total_tasks"] += len(workflow.nodes)
        self.execution_stats["average_speedup"] = (
            (self.execution_stats["average_speedup"] + speedup) / 2
        )
        
        return {
            "results": results,
            "errors": errors,
            "metrics": {
                "total_duration": total_duration,
                "sequential_estimate": sequential_estimate,
                "speedup": speedup,
                "parallel_levels": len([l for l in execution_levels if len(l) > 1]),
                "total_levels": len(execution_levels)
            },
            "execution_stats": self.execution_stats
        }
    
    async def _execute_parallel_level(
        self,
        node_ids: List[str],
        workflow: DynamicWorkflowGraph,
        session_id: str,
        max_concurrent: int
    ) -> Dict[str, Any]:
        """Execute nodes in parallel with concurrency control."""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_node(node_id):
            async with semaphore:
                node = workflow.nodes[node_id]
                specialist = node.node_key
                task = node.task
                
                try:
                    # Mark node as running
                    node.start_execution()
                    
                    # Delegate to specialist
                    result = await self.a2a_integration.delegate_to_specialist(
                        specialist_name=specialist,
                        task=task,
                        context={
                            "session_id": session_id,
                            "node_id": node_id,
                            "metadata": node.metadata
                        }
                    )
                    
                    # Mark node as completed
                    node.complete_execution(result)
                    
                    return node_id, result
                    
                except Exception as e:
                    # Mark node as failed
                    node.fail_execution(str(e))
                    return node_id, {"error": str(e)}
        
        # Execute all nodes in parallel
        tasks = [execute_node(node_id) for node_id in node_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        level_results = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Parallel execution error: {result}")
            else:
                node_id, node_result = result
                level_results[node_id] = node_result
        
        return level_results
    
    async def _execute_sequential_level(
        self,
        node_ids: List[str],
        workflow: DynamicWorkflowGraph,
        session_id: str
    ) -> Dict[str, Any]:
        """Execute nodes sequentially."""
        level_results = {}
        
        for node_id in node_ids:
            node = workflow.nodes[node_id]
            specialist = node.node_key
            task = node.task
            
            try:
                # Mark node as running
                node.start_execution()
                
                # Delegate to specialist
                result = await self.a2a_integration.delegate_to_specialist(
                    specialist_name=specialist,
                    task=task,
                    context={
                        "session_id": session_id,
                        "node_id": node_id,
                        "metadata": node.metadata
                    }
                )
                
                # Mark node as completed
                node.complete_execution(result)
                level_results[node_id] = result
                
            except Exception as e:
                # Mark node as failed
                node.fail_execution(str(e))
                level_results[node_id] = {"error": str(e)}
                logger.error(f"Sequential execution error for {node_id}: {e}")
        
        return level_results
    
    async def optimize_literature_search(
        self,
        topics: List[str],
        sources: List[str] = None
    ) -> Dict[str, Any]:
        """
        Optimize parallel literature search across multiple topics.
        
        Args:
            topics: List of research topics
            sources: Optional list of sources to search
            
        Returns:
            Aggregated search results
        """
        if not sources:
            sources = ["arxiv", "pubmed", "semantic_scholar"]
        
        # Create tasks for topic-source combinations
        search_tasks = []
        for topic in topics:
            for source in sources:
                search_tasks.append({
                    "specialist": "literature_review",
                    "task": f"Search {source} for papers on: {topic}",
                    "context": {
                        "topic": topic,
                        "source": source,
                        "max_results": 20
                    }
                })
        
        # Execute searches in parallel
        results = await self.a2a_integration.parallel_delegate(
            tasks=search_tasks,
            max_concurrent=min(len(search_tasks), 10)
        )
        
        # Aggregate results by topic
        aggregated = {}
        for topic in topics:
            topic_results = []
            for task_result in results.get("results", {}).values():
                if isinstance(task_result, dict) and task_result.get("topic") == topic:
                    topic_results.extend(task_result.get("papers", []))
            
            # Remove duplicates based on title
            seen_titles = set()
            unique_papers = []
            for paper in topic_results:
                if paper.get("title") not in seen_titles:
                    seen_titles.add(paper.get("title"))
                    unique_papers.append(paper)
            
            aggregated[topic] = {
                "total_found": len(unique_papers),
                "papers": unique_papers,
                "sources_searched": sources
            }
        
        return aggregated
    
    def get_workflow_visualization(
        self, 
        workflow: DynamicWorkflowGraph
    ) -> Dict[str, Any]:
        """Generate workflow visualization data."""
        visualization = {
            "nodes": [],
            "edges": [],
            "levels": []
        }
        
        # Add nodes
        for node_id, node in workflow.nodes.items():
            visualization["nodes"].append({
                "id": node_id,
                "label": node.node_label,
                "type": node.metadata.get("task_type", "unknown"),
                "group": node.metadata.get("parallel_group", -1),
                "can_parallelize": node.metadata.get("can_parallelize", True)
            })
        
        # Add edges
        for from_id, to_id in workflow.graph.edges():
            visualization["edges"].append({
                "from": from_id,
                "to": to_id
            })
        
        # Add execution levels
        execution_plan = workflow.get_execution_plan()
        for i, level in enumerate(execution_plan):
            visualization["levels"].append({
                "level": i,
                "nodes": level,
                "can_parallelize": len(level) > 1
            })
        
        return visualization