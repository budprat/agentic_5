# ABOUTME: Agent executors for running agents with event-driven architecture
# ABOUTME: Provides unified interface for executing agents with proper task and event management

import logging
from typing import Optional, Any

from a2a_mcp.server.events import EventQueue
from a2a_mcp.server.tasks import TaskUpdater
from a2a_mcp.types import (
    DataPart,
    InvalidParamsError,
    SendStreamingMessageSuccessResponse,
    Task,
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatusUpdateEvent,
    TextPart,
    UnsupportedOperationError,
)
from a2a_mcp.utils import new_agent_text_message, new_task
from a2a_mcp.utils.errors import ServerError
from a2a_mcp.common.base_agent import BaseAgent


logger = logging.getLogger(__name__)


class RequestContext:
    """Context for agent execution requests."""
    
    def __init__(self, message: Any, current_task: Optional[Task] = None):
        self.message = message
        self.current_task = current_task
        self._user_input = None
    
    def get_user_input(self) -> str:
        """Extract user input from the message."""
        if self._user_input:
            return self._user_input
            
        # Extract from message based on structure
        if hasattr(self.message, 'query'):
            self._user_input = self.message.query
        elif hasattr(self.message, 'content'):
            self._user_input = self.message.content
        elif hasattr(self.message, 'text'):
            self._user_input = self.message.text
        elif isinstance(self.message, dict):
            self._user_input = self.message.get('query', 
                                                self.message.get('content',
                                                self.message.get('text', '')))
        else:
            self._user_input = str(self.message)
            
        return self._user_input


class AgentExecutor:
    """Abstract base class for agent executors."""
    
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Execute an agent with the given context."""
        raise NotImplementedError
    
    async def cancel(
        self, request: RequestContext, event_queue: EventQueue
    ) -> Optional[Task]:
        """Cancel an ongoing execution."""
        raise NotImplementedError


class GenericAgentExecutor(AgentExecutor):
    """AgentExecutor used by the travel agents."""

    def __init__(self, agent: BaseAgent):
        self.agent = agent

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        logger.info(f'Executing agent {self.agent.agent_name}')
        error = self._validate_request(context)
        if error:
            raise ServerError(error=InvalidParamsError())

        query = context.get_user_input()

        task = context.current_task

        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)

        updater = TaskUpdater(event_queue, task.id, task.contextId)

        async for item in self.agent.stream(query, task.contextId, task.id):
            # Agent to Agent call will return events,
            # Update the relevant ids to proxy back.
            if hasattr(item, 'root') and isinstance(
                item.root, SendStreamingMessageSuccessResponse
            ):
                event = item.root.result
                if isinstance(
                    event,
                    (TaskStatusUpdateEvent | TaskArtifactUpdateEvent),
                ):
                    await event_queue.enqueue_event(event)
                continue

            is_task_complete = item['is_task_complete']
            require_user_input = item['require_user_input']

            if is_task_complete:
                if item['response_type'] == 'data':
                    part = DataPart(data=item['content'])
                else:
                    part = TextPart(text=item['content'])

                await updater.add_artifact(
                    [part],
                    name=f'{self.agent.agent_name}-result',
                )
                await updater.complete()
                break
            if require_user_input:
                await updater.update_status(
                    TaskState.input_required,
                    new_agent_text_message(
                        item['content'],
                        task.contextId,
                        task.id,
                    ),
                    final=True,
                )
                break
            await updater.update_status(
                TaskState.working,
                new_agent_text_message(
                    item['content'],
                    task.contextId,
                    task.id,
                ),
            )

    def _validate_request(self, context: RequestContext) -> bool:
        return False

    async def cancel(
        self, request: RequestContext, event_queue: EventQueue
    ) -> Optional[Task]:
        raise ServerError(error=UnsupportedOperationError())


# Legacy executor for backward compatibility
class LegacyAgentExecutor(AgentExecutor):
    """Legacy executor that adapts to the old interface."""
    
    def __init__(self, agent: Optional[Any] = None, agent_registry: Optional[dict] = None):
        """Initialize with optional agent or registry."""
        self.agent = agent
        self.agent_registry = agent_registry or {}
        self._agent_instances = {}
    
    def register_agent(self, name: str, agent: Any):
        """Register an agent instance."""
        self.agent_registry[name] = agent
    
    async def execute(
        self,
        agent_name: str,
        query: str,
        context_id: str,
        task_id: str,
        on_progress: Optional[Any] = None
    ) -> Any:
        """Legacy execute method for compatibility."""
        # Get agent
        agent = await self._get_agent(agent_name)
        
        # Create mock context and event queue
        message = {'query': query, 'agent_name': agent_name}
        task = Task(
            id=task_id,
            contextId=context_id,
            state=TaskState.working,
            message=message
        )
        context = RequestContext(message, task)
        
        # Simple event queue that calls progress callback
        class SimpleEventQueue:
            async def enqueue_event(self, event):
                if on_progress:
                    await on_progress(event)
        
        event_queue = SimpleEventQueue()
        
        # Create executor and run
        executor = GenericAgentExecutor(agent)
        await executor.execute(context, event_queue)
        
        # Return final result
        return {"status": "completed", "task_id": task_id}
    
    async def _get_agent(self, agent_name: str) -> BaseAgent:
        """Get agent by name."""
        # Use primary agent if provided and name matches
        if self.agent and hasattr(self.agent, 'agent_name') and self.agent.agent_name == agent_name:
            return self.agent
            
        # Check registry
        if agent_name in self.agent_registry:
            return self.agent_registry[agent_name]
            
        # Check instances cache
        if agent_name in self._agent_instances:
            return self._agent_instances[agent_name]
            
        raise ValueError(f"Agent {agent_name} not found")
    
    async def cancel(self, request: RequestContext, event_queue: EventQueue) -> Optional[Task]:
        """Cancel is not supported in legacy mode."""
        raise ServerError(error=UnsupportedOperationError())