"""Enhanced Orchestrator Agent with parallel task execution."""

import logging
import json
from collections.abc import AsyncIterable

from a2a.types import (
    SendStreamingMessageSuccessResponse,
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatusUpdateEvent,
)
from a2a_mcp.common import prompts
from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import init_api_key
from a2a_mcp.common.parallel_workflow import (
    Status, 
    ParallelWorkflowGraph, 
    ParallelWorkflowNode
)
from google import genai


logger = logging.getLogger(__name__)


class ParallelOrchestratorAgent(BaseAgent):
    """Enhanced Orchestrator Agent with parallel task execution capabilities."""

    def __init__(self):
        init_api_key()
        super().__init__(
            agent_name="Parallel Orchestrator Agent",
            description="Facilitate inter agent communication with parallel execution",
            content_types=["text", "text/plain"],
        )
        self.graph = None
        self.results = []
        self.travel_context = {}
        self.query_history = []
        self.context_id = None
        self.enable_parallel = True  # Feature flag for parallel execution

    async def generate_summary(self) -> str:
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompts.SUMMARY_COT_INSTRUCTIONS.replace(
                "{travel_data}", str(self.results)
            ),
            config={"temperature": 0.0},
        )
        return response.text

    def answer_user_question(self, question) -> str:
        try:
            client = genai.Client()
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompts.QA_COT_PROMPT.replace(
                    "{TRIP_CONTEXT}", str(self.travel_context)
                )
                .replace("{CONVERSATION_HISTORY}", str(self.query_history))
                .replace("{TRIP_QUESTION}", question),
                config={
                    "temperature": 0.0,
                    "response_mime_type": "application/json",
                },
            )
            return response.text
        except Exception as e:
            logger.info(f"Error answering user question: {e}")
        return '{"can_answer": "no", "answer": "Cannot answer based on provided context"}'

    def set_node_attributes(
        self, node_id, task_id=None, context_id=None, query=None
    ):
        attr_val = {}
        if task_id:
            attr_val["task_id"] = task_id
        if context_id:
            attr_val["context_id"] = context_id
        if query:
            attr_val["query"] = query

        self.graph.set_node_attributes(node_id, attr_val)

    def add_graph_node(
        self,
        task_id,
        context_id,
        query: str,
        node_id: str = None,
        node_key: str = None,
        node_label: str = None,
    ) -> ParallelWorkflowNode:
        """Add a node to the graph."""
        node = ParallelWorkflowNode(
            task=query, node_key=node_key, node_label=node_label
        )
        self.graph.add_node(node)
        if node_id:
            self.graph.add_edge(node_id, node.id)
        self.set_node_attributes(node.id, task_id, context_id, query)
        return node

    def analyze_task_dependencies(self, tasks: list[dict]) -> dict[str, list[str]]:
        """Analyze tasks to identify dependencies and parallel opportunities."""
        # Simple heuristic: tasks for different services can run in parallel
        task_groups = {
            "flights": [],
            "hotels": [],
            "cars": [],
            "other": []
        }
        
        for idx, task in enumerate(tasks):
            desc = task.get("description", "").lower()
            if "flight" in desc or "air" in desc:
                task_groups["flights"].append(idx)
            elif "hotel" in desc or "accommodation" in desc:
                task_groups["hotels"].append(idx)
            elif "car" in desc or "rental" in desc:
                task_groups["cars"].append(idx)
            else:
                task_groups["other"].append(idx)
        
        # Log parallel execution opportunities
        parallel_count = sum(1 for group in task_groups.values() if len(group) > 0)
        if parallel_count > 1:
            logger.info(f"Identified {parallel_count} task groups that can run in parallel")
        
        return task_groups

    def clear_state(self):
        self.graph = None
        self.results.clear()
        self.travel_context.clear()
        self.query_history.clear()

    async def stream(
        self, query, context_id, task_id
    ) -> AsyncIterable[dict[str, any]]:
        """Execute and stream response with parallel task execution."""
        logger.info(
            f"Running {self.agent_name} stream for session {context_id}, task {task_id} - {query}"
        )
        if not query:
            raise ValueError("Query cannot be empty")
        if self.context_id != context_id:
            # Clear state when the context changes
            self.clear_state()
            self.context_id = context_id

        self.query_history.append(query)
        start_node_id = None
        
        # Graph does not exist, start a new graph with planner node.
        if not self.graph:
            self.graph = ParallelWorkflowGraph()
            planner_node = self.add_graph_node(
                task_id=task_id,
                context_id=context_id,
                query=query,
                node_key="planner",
                node_label="Planner",
            )
            start_node_id = planner_node.id
        # Paused state is when the agent might need more information.
        elif self.graph.state == Status.PAUSED:
            start_node_id = self.graph.paused_node_id
            self.set_node_attributes(node_id=start_node_id, query=query)

        while True:
            # Set attributes on the node so we propagate task and context
            self.set_node_attributes(
                node_id=start_node_id,
                task_id=task_id,
                context_id=context_id,
            )
            # Resume workflow, used when the workflow nodes are updated.
            should_resume_workflow = False
            
            async for chunk in self.graph.run_workflow(
                start_node_id=start_node_id
            ):
                if isinstance(chunk.root, SendStreamingMessageSuccessResponse):
                    # The graph node returned TaskStatusUpdateEvent
                    if isinstance(chunk.root.result, TaskStatusUpdateEvent):
                        task_status_event = chunk.root.result
                        context_id = task_status_event.contextId
                        if (
                            task_status_event.status.state
                            == TaskState.completed
                            and context_id
                        ):
                            continue
                        if (
                            task_status_event.status.state
                            == TaskState.input_required
                        ):
                            question = task_status_event.status.message.parts[
                                0
                            ].root.text

                            try:
                                answer = json.loads(
                                    self.answer_user_question(question)
                                )
                                logger.info(f"Agent Answer {answer}")
                                if answer["can_answer"] == "yes":
                                    # Orchestrator can answer on behalf of the user
                                    query = answer["answer"]
                                    start_node_id = self.graph.paused_node_id
                                    self.set_node_attributes(
                                        node_id=start_node_id, query=query
                                    )
                                    should_resume_workflow = True
                            except Exception:
                                logger.info("Cannot convert answer data")

                    # The graph node returned TaskArtifactUpdateEvent
                    if isinstance(chunk.root.result, TaskArtifactUpdateEvent):
                        artifact = chunk.root.result.artifact
                        self.results.append(artifact)
                        if artifact.name == "PlannerAgent-result":
                            # Planning agent returned data, update graph.
                            artifact_data = artifact.parts[0].root.data
                            if "trip_info" in artifact_data:
                                self.travel_context = artifact_data["trip_info"]
                            
                            tasks = artifact_data.get('tasks', [])
                            logger.info(
                                f"Updating workflow with {len(tasks)} task nodes"
                            )
                            
                            # Analyze task dependencies for parallel execution
                            task_groups = self.analyze_task_dependencies(tasks)
                            
                            # Build graph with parallel execution in mind
                            current_node_ids = [start_node_id]
                            
                            # Process each task group
                            for group_name, task_indices in task_groups.items():
                                if not task_indices:
                                    continue
                                
                                group_nodes = []
                                for idx in task_indices:
                                    task_data = tasks[idx]
                                    # Each task in the group depends on all previous level nodes
                                    for prev_node_id in current_node_ids:
                                        node = self.add_graph_node(
                                            task_id=task_id,
                                            context_id=context_id,
                                            query=task_data["description"],
                                            node_id=prev_node_id,
                                            node_label=f"{group_name.title()} Task {idx}",
                                        )
                                        group_nodes.append(node.id)
                                        # Only add edge from first previous node to avoid redundancy
                                        break
                                
                                # Update current nodes for next level
                                if group_nodes:
                                    current_node_ids = group_nodes
                            
                            # Log execution plan
                            if self.enable_parallel:
                                execution_plan = self.graph.visualize_execution_plan()
                                logger.info(f"\n{execution_plan}")
                            
                            # Restart from first new node
                            should_resume_workflow = True
                            # Get first task node after planner
                            successors = list(self.graph.graph.successors(start_node_id))
                            if successors:
                                start_node_id = successors[0]
                        else:
                            # Not planner but artifacts from other tasks
                            continue
                
                # When the workflow needs to be resumed, do not yield partial.
                if not should_resume_workflow:
                    logger.info("No workflow resume detected, yielding chunk")
                    yield chunk
            
            # The graph is complete and no updates, so okay to break from the loop.
            if not should_resume_workflow:
                logger.info(
                    "Workflow iteration complete and no restart requested. Exiting main loop."
                )
                break
            else:
                logger.info("Restarting workflow loop.")
        
        if self.graph.state == Status.COMPLETED:
            # All individual actions complete, now generate the summary
            logger.info(f"Generating summary for {len(self.results)} results")
            summary = await self.generate_summary()
            self.clear_state()
            logger.info(f"Summary: {summary}")
            yield {
                "response_type": "text",
                "is_task_complete": True,
                "require_user_input": False,
                "content": summary,
            }