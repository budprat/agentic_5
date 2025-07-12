# ABOUTME: Type definitions for A2A MCP Framework
# ABOUTME: Includes AgentCard and other shared types

from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


@dataclass
class AgentCard:
    """Agent configuration card for A2A agents.
    
    This represents the configuration and metadata for an agent,
    loaded from JSON files and used to instantiate agents.
    """
    name: str
    type: str
    description: str
    version: str
    capabilities: List[str]
    port: Optional[int] = None
    instructions: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    auth_required: Optional[bool] = False
    auth_schemes: Optional[List[Dict[str, Any]]] = None
    
    def __post_init__(self):
        """Validate and set defaults after initialization."""
        if self.config is None:
            self.config = {}
        if self.metadata is None:
            self.metadata = {}
        if self.auth_schemes is None:
            self.auth_schemes = []


class TaskState(str, Enum):
    """Task execution states."""
    pending = "pending"
    working = "working"
    input_required = "input_required"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


@dataclass
class Part:
    """Base class for message parts."""
    pass


@dataclass
class TextPart(Part):
    """Text content part."""
    text: str


@dataclass
class DataPart(Part):
    """Data content part."""
    data: Any


@dataclass
class Message:
    """Message structure for agent communication."""
    id: str
    contextId: str
    taskId: Optional[str] = None
    role: str = "assistant"
    parts: List[Part] = None
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        if self.parts is None:
            self.parts = []
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


@dataclass
class Task:
    """Task representation."""
    id: str
    contextId: str
    state: TaskState
    message: Any
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    
    def __post_init__(self):
        if self.createdAt is None:
            self.createdAt = datetime.utcnow().isoformat()
        if self.updatedAt is None:
            self.updatedAt = self.createdAt


@dataclass
class TaskStatusUpdateEvent:
    """Event for task status updates."""
    taskId: str
    contextId: str
    state: TaskState
    message: Optional[Message] = None
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


@dataclass
class TaskArtifactUpdateEvent:
    """Event for task artifact updates."""
    taskId: str
    contextId: str
    artifact: Dict[str, Any]
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


@dataclass
class SendStreamingMessageSuccessResponse:
    """Response for successful streaming message."""
    result: Union[TaskStatusUpdateEvent, TaskArtifactUpdateEvent]


# Generic task list for orchestrators
@dataclass 
class GenericTask:
    """Generic task for orchestration."""
    id: str
    description: str
    status: str = "pending"
    agent_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TaskList:
    """Generic task list for orchestrators."""
    tasks: List[GenericTask]
    metadata: Optional[Dict[str, Any]] = None


@dataclass 
class AgentResponse:
    """Generic agent response format for all Framework V2.0 agents."""
    content: Union[str, Dict[str, Any]]
    is_task_complete: bool
    require_user_input: bool
    agent_name: Optional[str] = None
    response_type: str = "text"  # "text", "data", "json"
    metadata: Optional[Dict[str, Any]] = None


# Error types
class BaseError(Exception):
    """Base error class."""
    pass


class InvalidParamsError(BaseError):
    """Invalid parameters error."""
    pass


class UnsupportedOperationError(BaseError):
    """Unsupported operation error."""
    pass