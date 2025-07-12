# ABOUTME: Task management and update utilities for agent execution
# ABOUTME: Provides TaskUpdater for managing task lifecycle and artifacts

import logging
from typing import List, Any, Optional
from datetime import datetime

from a2a_mcp.common.types import (
    TaskState,
    TaskStatusUpdateEvent,
    TaskArtifactUpdateEvent,
    Message,
    Part,
)

logger = logging.getLogger(__name__)


class TaskUpdater:
    """Manages task updates and artifacts during agent execution."""
    
    def __init__(self, event_queue: Any, task_id: str, context_id: str):
        """Initialize task updater.
        
        Args:
            event_queue: Event queue for publishing updates
            task_id: ID of the task being updated
            context_id: Context ID for the task
        """
        self.event_queue = event_queue
        self.task_id = task_id
        self.context_id = context_id
        self._artifacts = []
        
    async def update_status(
        self, 
        state: TaskState, 
        message: Optional[Message] = None,
        final: bool = False
    ) -> None:
        """Update task status.
        
        Args:
            state: New task state
            message: Optional status message
            final: Whether this is the final status update
        """
        event = TaskStatusUpdateEvent(
            taskId=self.task_id,
            contextId=self.context_id,
            state=state,
            message=message,
            timestamp=datetime.utcnow().isoformat()
        )
        
        await self.event_queue.enqueue_event(event)
        
        if final:
            logger.info(f"Task {self.task_id} reached final state: {state}")
            
    async def add_artifact(
        self, 
        parts: List[Part],
        name: str,
        metadata: Optional[dict] = None
    ) -> None:
        """Add artifact to task.
        
        Args:
            parts: Artifact parts (text, data, etc.)
            name: Artifact name
            metadata: Optional artifact metadata
        """
        artifact = {
            'name': name,
            'parts': parts,
            'metadata': metadata or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self._artifacts.append(artifact)
        
        event = TaskArtifactUpdateEvent(
            taskId=self.task_id,
            contextId=self.context_id,
            artifact=artifact
        )
        
        await self.event_queue.enqueue_event(event)
        
    async def complete(self) -> None:
        """Mark task as completed."""
        await self.update_status(TaskState.completed, final=True)
        
    async def fail(self, error: str) -> None:
        """Mark task as failed.
        
        Args:
            error: Error message
        """
        from a2a_mcp.utils import new_agent_text_message
        
        error_message = new_agent_text_message(
            f"Task failed: {error}",
            self.context_id,
            self.task_id
        )
        
        await self.update_status(
            TaskState.failed, 
            message=error_message, 
            final=True
        )
        
    def get_artifacts(self) -> List[dict]:
        """Get all artifacts added to this task."""
        return self._artifacts.copy()