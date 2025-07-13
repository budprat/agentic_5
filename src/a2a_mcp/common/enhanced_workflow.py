# ABOUTME: Enhanced workflow system with dynamic graph management for advanced orchestration
# ABOUTME: Framework V2.0 sophisticated workflow capabilities inspired by reference orchestrator patterns

"""
Enhanced Workflow System - Framework V2.0

This module provides sophisticated workflow management capabilities including:
- Dynamic graph building with nodes and edges
- Task metadata and execution tracking
- State management (RUNNING, PAUSED, COMPLETED)
- Node attribute management for orchestration
- Integration with existing ParallelWorkflow system

Based on reference orchestrator patterns but enhanced for Framework V2.0.
"""

import uuid
import logging
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class WorkflowState(Enum):
    """Workflow execution states."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NodeState(Enum):
    """Individual node execution states."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"


@dataclass
class WorkflowNode:
    """
    Enhanced workflow node with metadata and execution tracking.
    
    Attributes:
        id: Unique node identifier
        task: Task description/query
        node_key: Optional key for node type identification
        node_label: Human-readable label
        state: Current execution state
        metadata: Additional node metadata
        created_at: Node creation timestamp
        started_at: Execution start timestamp
        completed_at: Execution completion timestamp
        result: Node execution result
        error: Error information if failed
        dependencies: Set of node IDs this node depends on
        dependents: Set of node IDs that depend on this node
    """
    task: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    node_key: Optional[str] = None
    node_label: Optional[str] = None
    state: NodeState = NodeState.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    
    def __post_init__(self):
        """Initialize node with default values."""
        if not self.node_label:
            self.node_label = self.task[:50] + "..." if len(self.task) > 50 else self.task
    
    def set_attributes(self, attributes: Dict[str, Any]):
        """Set multiple metadata attributes."""
        self.metadata.update(attributes)
    
    def get_attribute(self, key: str, default: Any = None) -> Any:
        """Get metadata attribute."""
        return self.metadata.get(key, default)
    
    def start_execution(self):
        """Mark node as started."""
        self.state = NodeState.RUNNING
        self.started_at = datetime.now()
    
    def complete_execution(self, result: Any = None):
        """Mark node as completed."""
        self.state = NodeState.COMPLETED
        self.completed_at = datetime.now()
        self.result = result
    
    def fail_execution(self, error: str):
        """Mark node as failed."""
        self.state = NodeState.FAILED
        self.completed_at = datetime.now()
        self.error = error
    
    def can_execute(self, completed_nodes: Set[str]) -> bool:
        """Check if node can execute based on dependencies."""
        return self.dependencies.issubset(completed_nodes)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary representation."""
        return {
            'id': self.id,
            'task': self.task,
            'node_key': self.node_key,
            'node_label': self.node_label,
            'state': self.state.value,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'dependencies': list(self.dependencies),
            'dependents': list(self.dependents),
            'has_result': self.result is not None,
            'error': self.error
        }


class DynamicWorkflowGraph:
    """
    Enhanced workflow graph with dynamic node management.
    
    Features:
    - Dynamic node and edge creation
    - State management and tracking
    - Dependency resolution
    - Pause/resume capabilities
    - Execution ordering and validation
    """
    
    def __init__(self, workflow_id: Optional[str] = None):
        """
        Initialize dynamic workflow graph.
        
        Args:
            workflow_id: Optional workflow identifier
        """
        self.workflow_id = workflow_id or str(uuid.uuid4())
        self.nodes: Dict[str, WorkflowNode] = {}
        self.edges: Dict[str, Set[str]] = {}  # node_id -> set of dependent node_ids
        self.state = WorkflowState.PENDING
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.paused_node_id: Optional[str] = None
        self.execution_order: List[str] = []
        self.metadata: Dict[str, Any] = {}
        
        logger.info(f"Initialized DynamicWorkflowGraph {self.workflow_id}")
    
    def add_node(self, node: WorkflowNode) -> str:
        """
        Add a node to the workflow graph.
        
        Args:
            node: WorkflowNode to add
            
        Returns:
            Node ID
        """
        self.nodes[node.id] = node
        if node.id not in self.edges:
            self.edges[node.id] = set()
        
        logger.debug(f"Added node {node.id} ({node.node_label}) to workflow {self.workflow_id}")
        return node.id
    
    def add_edge(self, from_node_id: str, to_node_id: str):
        """
        Add an edge (dependency) between nodes.
        
        Args:
            from_node_id: Source node ID
            to_node_id: Target node ID (depends on source)
        """
        if from_node_id not in self.nodes or to_node_id not in self.nodes:
            raise ValueError(f"Cannot add edge: nodes {from_node_id} or {to_node_id} not found")
        
        # Add edge in adjacency list
        self.edges[from_node_id].add(to_node_id)
        
        # Update node dependencies
        self.nodes[to_node_id].dependencies.add(from_node_id)
        self.nodes[from_node_id].dependents.add(to_node_id)
        
        logger.debug(f"Added edge {from_node_id} -> {to_node_id} in workflow {self.workflow_id}")
    
    def remove_node(self, node_id: str):
        """Remove a node and all its edges."""
        if node_id not in self.nodes:
            return
        
        # Remove all edges involving this node
        for other_id in list(self.edges.keys()):
            self.edges[other_id].discard(node_id)
            if other_id in self.nodes:
                self.nodes[other_id].dependencies.discard(node_id)
                self.nodes[other_id].dependents.discard(node_id)
        
        # Remove from dependencies/dependents of other nodes
        for other_node in self.nodes.values():
            other_node.dependencies.discard(node_id)
            other_node.dependents.discard(node_id)
        
        # Remove the node itself
        del self.nodes[node_id]
        del self.edges[node_id]
        
        logger.debug(f"Removed node {node_id} from workflow {self.workflow_id}")
    
    def set_node_attributes(self, node_id: str, attributes: Dict[str, Any]):
        """
        Set attributes on a workflow node.
        
        Args:
            node_id: Target node ID
            attributes: Attributes to set
        """
        if node_id in self.nodes:
            self.nodes[node_id].set_attributes(attributes)
            logger.debug(f"Set attributes on node {node_id}: {list(attributes.keys())}")
        else:
            logger.warning(f"Cannot set attributes: node {node_id} not found")
    
    def get_node(self, node_id: str) -> Optional[WorkflowNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)
    
    def get_nodes_by_key(self, node_key: str) -> List[WorkflowNode]:
        """Get all nodes with a specific key."""
        return [node for node in self.nodes.values() if node.node_key == node_key]
    
    def get_executable_nodes(self) -> List[WorkflowNode]:
        """Get nodes that can be executed (dependencies satisfied)."""
        completed_nodes = {
            node_id for node_id, node in self.nodes.items() 
            if node.state == NodeState.COMPLETED
        }
        
        return [
            node for node in self.nodes.values()
            if node.state == NodeState.PENDING and node.can_execute(completed_nodes)
        ]
    
    def get_execution_plan(self) -> List[List[str]]:
        """
        Get execution plan as layers of node IDs that can run in parallel.
        
        Returns:
            List of layers, each containing node IDs that can execute in parallel
        """
        remaining_nodes = set(self.nodes.keys())
        completed_nodes = set()
        execution_layers = []
        
        while remaining_nodes:
            # Find nodes that can execute now
            executable_now = []
            for node_id in remaining_nodes:
                node = self.nodes[node_id]
                if node.can_execute(completed_nodes):
                    executable_now.append(node_id)
            
            if not executable_now:
                # Circular dependency or other issue
                logger.error(f"Cannot resolve execution order for nodes: {remaining_nodes}")
                break
            
            execution_layers.append(executable_now)
            completed_nodes.update(executable_now)
            remaining_nodes.difference_update(executable_now)
        
        return execution_layers
    
    def start_workflow(self):
        """Start workflow execution."""
        self.state = WorkflowState.RUNNING
        self.started_at = datetime.now()
        logger.info(f"Started workflow {self.workflow_id}")
    
    def pause_workflow(self, paused_node_id: Optional[str] = None):
        """Pause workflow execution."""
        self.state = WorkflowState.PAUSED
        self.paused_node_id = paused_node_id
        logger.info(f"Paused workflow {self.workflow_id} at node {paused_node_id}")
    
    def resume_workflow(self):
        """Resume workflow execution."""
        if self.state == WorkflowState.PAUSED:
            self.state = WorkflowState.RUNNING
            logger.info(f"Resumed workflow {self.workflow_id}")
    
    def complete_workflow(self):
        """Mark workflow as completed."""
        self.state = WorkflowState.COMPLETED
        self.completed_at = datetime.now()
        logger.info(f"Completed workflow {self.workflow_id}")
    
    def fail_workflow(self, error: str):
        """Mark workflow as failed."""
        self.state = WorkflowState.FAILED
        self.completed_at = datetime.now()
        self.metadata['error'] = error
        logger.error(f"Failed workflow {self.workflow_id}: {error}")
    
    def get_workflow_stats(self) -> Dict[str, Any]:
        """Get workflow statistics."""
        node_states = {}
        for state in NodeState:
            node_states[state.value] = sum(
                1 for node in self.nodes.values() if node.state == state
            )
        
        return {
            'workflow_id': self.workflow_id,
            'state': self.state.value,
            'total_nodes': len(self.nodes),
            'node_states': node_states,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'paused_node_id': self.paused_node_id,
            'has_cycles': self._has_cycles(),
            'execution_layers': len(self.get_execution_plan())
        }
    
    def _has_cycles(self) -> bool:
        """Check if the graph has cycles using DFS."""
        visited = set()
        rec_stack = set()
        
        def has_cycle_util(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            
            for neighbor in self.edges.get(node_id, []):
                if neighbor not in visited:
                    if has_cycle_util(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node_id)
            return False
        
        for node_id in self.nodes.keys():
            if node_id not in visited:
                if has_cycle_util(node_id):
                    return True
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary representation."""
        return {
            'workflow_id': self.workflow_id,
            'state': self.state.value,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'paused_node_id': self.paused_node_id,
            'metadata': self.metadata,
            'nodes': {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            'edges': {node_id: list(edges) for node_id, edges in self.edges.items()},
            'stats': self.get_workflow_stats()
        }


class WorkflowManager:
    """
    Manager for multiple workflow graphs with advanced capabilities.
    
    Features:
    - Multiple workflow management
    - Session-based workflow isolation
    - Workflow templates and patterns
    - Performance monitoring
    """
    
    def __init__(self):
        """Initialize workflow manager."""
        self.workflows: Dict[str, DynamicWorkflowGraph] = {}
        self.session_workflows: Dict[str, List[str]] = {}  # session_id -> [workflow_ids]
        self.active_workflows: Set[str] = set()
        
        logger.info("Initialized WorkflowManager")
    
    def create_workflow(self, session_id: str, workflow_id: Optional[str] = None) -> DynamicWorkflowGraph:
        """Create a new workflow for a session."""
        workflow = DynamicWorkflowGraph(workflow_id)
        
        self.workflows[workflow.workflow_id] = workflow
        
        if session_id not in self.session_workflows:
            self.session_workflows[session_id] = []
        self.session_workflows[session_id].append(workflow.workflow_id)
        
        logger.info(f"Created workflow {workflow.workflow_id} for session {session_id}")
        return workflow
    
    def get_workflow(self, workflow_id: str) -> Optional[DynamicWorkflowGraph]:
        """Get workflow by ID."""
        return self.workflows.get(workflow_id)
    
    def get_session_workflows(self, session_id: str) -> List[DynamicWorkflowGraph]:
        """Get all workflows for a session."""
        workflow_ids = self.session_workflows.get(session_id, [])
        return [self.workflows[wid] for wid in workflow_ids if wid in self.workflows]
    
    def cleanup_session(self, session_id: str):
        """Clean up all workflows for a session."""
        if session_id in self.session_workflows:
            workflow_ids = self.session_workflows[session_id]
            for workflow_id in workflow_ids:
                if workflow_id in self.workflows:
                    del self.workflows[workflow_id]
                self.active_workflows.discard(workflow_id)
            
            del self.session_workflows[session_id]
            logger.info(f"Cleaned up {len(workflow_ids)} workflows for session {session_id}")
    
    def get_manager_stats(self) -> Dict[str, Any]:
        """Get manager statistics."""
        return {
            'total_workflows': len(self.workflows),
            'active_workflows': len(self.active_workflows),
            'total_sessions': len(self.session_workflows),
            'workflow_states': {
                state.value: sum(
                    1 for wf in self.workflows.values() if wf.state == state
                )
                for state in WorkflowState
            }
        }


# Global workflow manager instance
workflow_manager = WorkflowManager()