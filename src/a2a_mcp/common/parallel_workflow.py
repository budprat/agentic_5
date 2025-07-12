"""Enhanced workflow module with parallel task execution support."""

import asyncio
import json
import logging
import uuid
from collections.abc import AsyncIterable
from collections import defaultdict
from enum import Enum
from uuid import uuid4

import httpx
import networkx as nx

from a2a.client import A2AClient
from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendStreamingMessageRequest,
    SendStreamingMessageSuccessResponse,
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatusUpdateEvent,
)
from a2a_mcp.common.utils import get_mcp_server_config
from a2a_mcp.common.workflow import Status, WorkflowNode
from a2a_mcp.mcp import client


logger = logging.getLogger(__name__)


class ParallelWorkflowNode(WorkflowNode):
    """Enhanced workflow node with parallel execution support."""
    
    async def run_node_with_result(
        self,
        query: str,
        task_id: str,
        context_id: str,
    ) -> tuple[str, list]:
        """Run node and collect all results for aggregation."""
        results = []
        async for chunk in self.run_node(query, task_id, context_id):
            results.append(chunk)
        return self.id, results


class ParallelWorkflowGraph:
    """Enhanced workflow graph with parallel task execution."""

    def __init__(self):
        self.graph = nx.DiGraph()
        self.nodes = {}
        self.latest_node = None
        self.node_type = None
        self.state = Status.INITIALIZED
        self.paused_node_id = None
        self.parallel_threshold = 2  # Min nodes to trigger parallel execution

    def add_node(self, node: ParallelWorkflowNode) -> None:
        logger.info(f'Adding node {node.id}')
        self.graph.add_node(node.id, query=node.task)
        self.nodes[node.id] = node
        self.latest_node = node.id

    def add_edge(self, from_node_id: str, to_node_id: str) -> None:
        if from_node_id not in self.nodes or to_node_id not in self.nodes:
            raise ValueError('Invalid node IDs')
        self.graph.add_edge(from_node_id, to_node_id)

    def get_execution_levels(self, start_node_id: str = None) -> list[list[str]]:
        """Get nodes grouped by execution level for parallel processing."""
        if not start_node_id or start_node_id not in self.nodes:
            start_nodes = [n for n, d in self.graph.in_degree() if d == 0]
        else:
            start_nodes = [start_node_id]

        # Build applicable subgraph
        applicable_graph = set()
        for node_id in start_nodes:
            applicable_graph.add(node_id)
            applicable_graph.update(nx.descendants(self.graph, node_id))

        # Calculate levels using BFS
        levels = []
        visited = set()
        current_level = set(start_nodes) & applicable_graph
        
        while current_level:
            # Add current level nodes
            level_nodes = list(current_level)
            levels.append(level_nodes)
            visited.update(level_nodes)
            
            # Get next level - nodes whose all predecessors have been visited
            next_level = set()
            for node in current_level:
                for successor in self.graph.successors(node):
                    if successor in applicable_graph:
                        # Check if all predecessors of this successor are visited
                        predecessors = set(self.graph.predecessors(successor))
                        if predecessors.issubset(visited):
                            next_level.add(successor)
            
            current_level = next_level
        
        return levels

    async def execute_parallel_level(
        self, 
        node_ids: list[str],
        chunk_callback: callable
    ) -> dict[str, any]:
        """Execute a level of nodes in parallel."""
        tasks = []
        node_map = {}
        
        for node_id in node_ids:
            node = self.nodes[node_id]
            query = self.graph.nodes[node_id].get('query')
            task_id = self.graph.nodes[node_id].get('task_id')
            context_id = self.graph.nodes[node_id].get('context_id')
            
            # Create async task for each node
            task = asyncio.create_task(
                node.run_node_with_result(query, task_id, context_id)
            )
            tasks.append(task)
            node_map[task] = node
        
        # Execute all tasks in parallel
        logger.info(f"Executing {len(tasks)} nodes in parallel: {node_ids}")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        level_results = {}
        for task, (node_id, chunks) in zip(tasks, results):
            if isinstance(chunks, Exception):
                logger.error(f"Node {node_id} failed with error: {chunks}")
                node_map[task].state = Status.PAUSED
                continue
                
            node = self.nodes[node_id]
            node.state = Status.COMPLETED
            level_results[node_id] = chunks
            
            # Yield chunks through callback
            for chunk in chunks:
                await chunk_callback(chunk)
        
        return level_results

    async def run_workflow(
        self, start_node_id: str = None
    ) -> AsyncIterable[dict[str, any]]:
        """Execute workflow with parallel task execution."""
        logger.info('Executing parallel workflow graph')
        
        # Get execution levels
        levels = self.get_execution_levels(start_node_id)
        logger.info(f'Execution levels: {[[n for n in level] for level in levels]}')
        
        self.state = Status.RUNNING
        collected_chunks = []
        
        # Define callback to collect chunks
        async def chunk_collector(chunk):
            collected_chunks.append(chunk)
        
        # Execute each level
        for level_idx, level_nodes in enumerate(levels):
            logger.info(f'Executing level {level_idx} with {len(level_nodes)} nodes')
            
            # Clear collected chunks for this level
            collected_chunks.clear()
            
            if len(level_nodes) >= self.parallel_threshold:
                # Execute in parallel
                level_results = await self.execute_parallel_level(
                    level_nodes, 
                    chunk_collector
                )
            else:
                # Execute sequentially for small levels
                for node_id in level_nodes:
                    node = self.nodes[node_id]
                    node.state = Status.RUNNING
                    query = self.graph.nodes[node_id].get('query')
                    task_id = self.graph.nodes[node_id].get('task_id')
                    context_id = self.graph.nodes[node_id].get('context_id')
                    
                    async for chunk in node.run_node(query, task_id, context_id):
                        collected_chunks.append(chunk)
                        if isinstance(
                            chunk.root, SendStreamingMessageSuccessResponse
                        ) and isinstance(chunk.root.result, TaskStatusUpdateEvent):
                            task_status_event = chunk.root.result
                            if (
                                task_status_event.status.state == TaskState.input_required
                            ):
                                node.state = Status.PAUSED
                                self.state = Status.PAUSED
                                self.paused_node_id = node.id
                    
                    if node.state == Status.RUNNING:
                        node.state = Status.COMPLETED
            
            # Yield all chunks from this level
            for chunk in collected_chunks:
                yield chunk
            
            # Check if workflow is paused
            if self.state == Status.PAUSED:
                break
        
        if self.state == Status.RUNNING:
            self.state = Status.COMPLETED

    def set_node_attribute(self, node_id, attribute, value):
        nx.set_node_attributes(self.graph, {node_id: value}, attribute)

    def set_node_attributes(self, node_id, attr_val):
        nx.set_node_attributes(self.graph, {node_id: attr_val})

    def is_empty(self) -> bool:
        return self.graph.number_of_nodes() == 0

    def identify_parallel_tasks(self) -> list[list[str]]:
        """Identify tasks that can be executed in parallel."""
        if self.is_empty():
            return []
        
        # Group nodes by their distance from root
        levels = self.get_execution_levels()
        
        # Filter levels that have enough nodes for parallel execution
        parallel_levels = []
        for level in levels:
            if len(level) >= self.parallel_threshold:
                # These nodes have no dependencies on each other
                parallel_levels.append(level)
        
        return parallel_levels

    def get_node_dependencies(self, node_id: str) -> list[str]:
        """Get all dependencies (predecessors) of a node."""
        return list(self.graph.predecessors(node_id))

    def visualize_execution_plan(self) -> str:
        """Generate a text representation of the execution plan."""
        levels = self.get_execution_levels()
        plan = "Execution Plan:\n"
        
        for idx, level in enumerate(levels):
            execution_type = "PARALLEL" if len(level) >= self.parallel_threshold else "SEQUENTIAL"
            plan += f"\nLevel {idx} ({execution_type}):\n"
            for node_id in level:
                node = self.nodes[node_id]
                plan += f"  - {node.node_label or node.id}: {node.task}\n"
        
        return plan