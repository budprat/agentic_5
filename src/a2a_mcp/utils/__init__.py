# ABOUTME: Utility functions for A2A MCP Framework
# ABOUTME: Provides helper functions for tasks, messages, and common operations

import uuid
from datetime import datetime
from typing import Any, Optional

from a2a_mcp.common.types import Task, TaskState, Message, TextPart


def new_task(message: Any) -> Task:
    """Create a new task from a message.
    
    Args:
        message: Source message for the task
        
    Returns:
        New Task instance
    """
    # Extract context ID
    context_id = None
    if hasattr(message, 'contextId'):
        context_id = message.contextId
    elif isinstance(message, dict) and 'contextId' in message:
        context_id = message['contextId']
    else:
        context_id = str(uuid.uuid4())
    
    # Create task
    task = Task(
        id=str(uuid.uuid4()),
        contextId=context_id,
        state=TaskState.pending,
        message=message
    )
    
    return task


def new_agent_text_message(
    text: str,
    context_id: str,
    task_id: Optional[str] = None
) -> Message:
    """Create a new agent text message.
    
    Args:
        text: Message text content
        context_id: Context ID for the message
        task_id: Optional task ID
        
    Returns:
        New Message instance
    """
    return Message(
        id=str(uuid.uuid4()),
        contextId=context_id,
        taskId=task_id,
        role="assistant",
        parts=[TextPart(text=text)]
    )