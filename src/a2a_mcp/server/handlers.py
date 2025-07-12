# ABOUTME: Request handlers for processing agent execution requests
# ABOUTME: Manages task lifecycle, agent selection, and response formatting

import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from a2a_mcp.common.agent_executor import GenericAgentExecutor
from .task_store import InMemoryTaskStore
from .notifier import InMemoryPushNotifier

logger = logging.getLogger(__name__)


class DefaultRequestHandler:
    """Default request handler for agent execution requests.
    
    Responsibilities:
    - Create and track tasks
    - Select appropriate agent executor
    - Handle streaming responses
    - Update task status
    - Send push notifications
    """
    
    def __init__(
        self,
        agent_executor: GenericAgentExecutor,
        task_store: InMemoryTaskStore,
        push_notifier: InMemoryPushNotifier
    ):
        """Initialize the request handler.
        
        Args:
            agent_executor: Agent executor instance
            task_store: Task persistence store
            push_notifier: Push notification service
        """
        self.agent_executor = agent_executor
        self.task_store = task_store
        self.push_notifier = push_notifier
        
        logger.info("DefaultRequestHandler initialized")
    
    async def handle_agent_request(
        self,
        agent_name: str,
        query: str,
        context_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle an agent execution request.
        
        Args:
            agent_name: Name of the agent to execute
            query: Query to send to the agent
            context_id: Optional context/session ID
            metadata: Optional request metadata
            
        Returns:
            Dict containing task information and initial status
        """
        # Generate task ID
        task_id = str(uuid.uuid4())
        context_id = context_id or str(uuid.uuid4())
        
        # Create task record
        task = {
            "id": task_id,
            "agent_name": agent_name,
            "query": query,
            "context_id": context_id,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
            "result": None,
            "error": None,
            "progress": []
        }
        
        # Store task
        await self.task_store.create_task(task)
        
        # Send initial notification
        await self.push_notifier.notify({
            "type": "task_created",
            "task_id": task_id,
            "agent_name": agent_name,
            "status": "pending"
        })
        
        # Execute task asynchronously
        # In production, this would be sent to a task queue
        # For now, we'll execute synchronously but track progress
        try:
            # Update status to running
            await self._update_task_status(task_id, "running")
            
            # Execute through executor
            result = await self.agent_executor.execute(
                agent_name=agent_name,
                query=query,
                context_id=context_id,
                task_id=task_id,
                on_progress=lambda progress: self._handle_progress(task_id, progress)
            )
            
            # Update task with result
            await self._complete_task(task_id, result)
            
            # Return initial response
            return {
                "task_id": task_id,
                "status": "completed",
                "result": result,
                "created_at": task["created_at"]
            }
            
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {e}")
            
            # Update task with error
            await self._fail_task(task_id, str(e))
            
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(e),
                "created_at": task["created_at"]
            }
    
    async def _update_task_status(self, task_id: str, status: str):
        """Update task status and send notification."""
        await self.task_store.update_task(task_id, {
            "status": status,
            "updated_at": datetime.utcnow().isoformat()
        })
        
        await self.push_notifier.notify({
            "type": "task_status_changed",
            "task_id": task_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _handle_progress(self, task_id: str, progress: Dict[str, Any]):
        """Handle progress update from executor."""
        # Add to progress array
        task = await self.task_store.get_task(task_id)
        if task:
            task["progress"].append({
                "timestamp": datetime.utcnow().isoformat(),
                "data": progress
            })
            await self.task_store.update_task(task_id, {"progress": task["progress"]})
        
        # Send progress notification
        await self.push_notifier.notify({
            "type": "task_progress",
            "task_id": task_id,
            "progress": progress,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _complete_task(self, task_id: str, result: Any):
        """Mark task as completed with result."""
        await self.task_store.update_task(task_id, {
            "status": "completed",
            "result": result,
            "updated_at": datetime.utcnow().isoformat()
        })
        
        await self.push_notifier.notify({
            "type": "task_completed",
            "task_id": task_id,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _fail_task(self, task_id: str, error: str):
        """Mark task as failed with error."""
        await self.task_store.update_task(task_id, {
            "status": "failed",
            "error": error,
            "updated_at": datetime.utcnow().isoformat()
        })
        
        await self.push_notifier.notify({
            "type": "task_failed",
            "task_id": task_id,
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        })