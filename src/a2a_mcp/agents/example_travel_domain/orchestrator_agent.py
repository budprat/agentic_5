import logging

from collections.abc import AsyncIterable

from a2a.types import (
    SendStreamingMessageSuccessResponse,
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatusUpdateEvent,
)
# Removed prompts import - using configurable prompts instead
from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import init_api_key
from a2a_mcp.common.workflow import Status, WorkflowGraph, WorkflowNode
from google import genai
import json


logger = logging.getLogger(__name__)


class OrchestratorAgent(BaseAgent):
    """Orchestrator Agent."""

    def __init__(self):
        init_api_key()
        super().__init__(
            agent_name="Orchestrator Agent",
            description="Facilitate inter agent communication",
            content_types=["text", "text/plain"],
        )
        self.graph = None
        self.results = []
        self.domain_context = {}
        self.query_history = []
        self.context_id = None

    def get_summary_prompt(self) -> str:
        """Get domain-configurable summary prompt."""
        return """
        Based on the following data: {domain_data}
        
        Generate a comprehensive summary of the completed workflow and results.
        Focus on:
        1. What was accomplished
        2. Key outcomes and decisions
        3. Any important details or insights
        
        Provide a clear, concise summary that captures the essential information.
        """

    def get_qa_prompt(self) -> str:
        """Get domain-configurable Q&A prompt."""
        return """
        Context: {DOMAIN_CONTEXT}
        Conversation History: {CONVERSATION_HISTORY}
        Question: {DOMAIN_QUESTION}
        
        Based on the provided context and conversation history, determine if you can answer the question.
        
        Respond in this JSON format:
        {{
            "can_answer": "yes" or "no",
            "answer": "your answer if can_answer is yes, otherwise explain why you cannot answer"
        }}
        """

    async def generate_summary(self) -> str:
        client = genai.Client()
        response = client.models.generate_content(
            model=os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-001'),
            contents=self.get_summary_prompt().replace(
                "{domain_data}", str(self.results)
            ),
            config={"temperature": 0.0},
        )
        return response.text

    def answer_user_question(self, question) -> str:
        try:
            client = genai.Client()
            response = client.models.generate_content(
                model=os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-001'),
                contents=self.get_qa_prompt().replace(
                    "{DOMAIN_CONTEXT}", str(self.domain_context)
                )
                .replace("{CONVERSATION_HISTORY}", str(self.query_history))
                .replace("{DOMAIN_QUESTION}", question),
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
    ) -> WorkflowNode:
        """Add a node to the graph."""
        node = WorkflowNode(
            task=query, node_key=node_key, node_label=node_label
        )
        self.graph.add_node(node)
        if node_id:
            self.graph.add_edge(node_id, node.id)
        self.set_node_attributes(node.id, task_id, context_id, query)
        return node

    def clear_state(self):
        self.graph = None
        self.results.clear()
        self.domain_context.clear()
        self.query_history.clear()

    async def stream(
        self, query, context_id, task_id
    ) -> AsyncIterable[dict[str, any]]:
        """Execute and stream response."""
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
            self.graph = WorkflowGraph()
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

        # This loop can be avoided if the workflow graph is dynamic or
        # is built from the results of the planner when the planner
        # iself is not a part of the graph.
        # TODO: Make the graph dynamically iterable over edges
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
                    # The graph node retured TaskStatusUpdateEvent
                    # Check if the node is complete and continue to the next node
                    if isinstance(chunk.root.result, TaskStatusUpdateEvent):
                        task_status_event = chunk.root.result
                        context_id = task_status_event.contextId
                        if (
                            task_status_event.status.state
                            == TaskState.completed
                            and context_id
                        ):
                            ## yeild??
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
                                    # Orchestrator can answer on behalf of the user set the query
                                    # Resume workflow from paused state.
                                    query = answer["answer"]
                                    start_node_id = self.graph.paused_node_id
                                    self.set_node_attributes(
                                        node_id=start_node_id, query=query
                                    )
                                    should_resume_workflow = True
                            except Exception:
                                logger.info("Cannot convert answer data")

                    # The graph node retured TaskArtifactUpdateEvent
                    # Store the node and continue.
                    if isinstance(chunk.root.result, TaskArtifactUpdateEvent):
                        artifact = chunk.root.result.artifact
                        self.results.append(artifact)
                        if artifact.name == "PlannerAgent-result":
                            # Planning agent returned data, update graph.
                            artifact_data = artifact.parts[0].root.data
                            if "domain_info" in artifact_data:
                                self.domain_context = artifact_data["domain_info"]
                            logger.info(
                                f"Updating workflow with {len(artifact_data['tasks'])} task nodes"
                            )
                            # Define the edges
                            current_node_id = start_node_id
                            for idx, task_data in enumerate(
                                artifact_data["tasks"]
                            ):
                                node = self.add_graph_node(
                                    task_id=task_id,
                                    context_id=context_id,
                                    query=task_data["description"],
                                    node_id=current_node_id,
                                )
                                current_node_id = node.id
                                # Restart graph from the newly inserted subgraph state
                                # Start from the new node just created.
                                if idx == 0:
                                    should_resume_workflow = True
                                    start_node_id = node.id
                        else:
                            # Not planner but artifacts from other tasks,
                            # continue to the next node in the workflow.
                            # client does not get the artifact,
                            # a summary is shown at the end of the workflow.
                            continue
                # When the workflow needs to be resumed, do not yield partial.
                if not should_resume_workflow:
                    logger.info("No workflow resume detected, yielding chunk")
                    # Yield partial execution
                    yield chunk
            # The graph is complete and no updates, so okay to break from the loop.
            if not should_resume_workflow:
                logger.info(
                    "Workflow iteration complete and no restart requested. Exiting main loop."
                )
                break
            else:
                # Readable logs
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