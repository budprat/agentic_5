# type: ignore
# ABOUTME: Generic reusable types for A2A MCP Framework
# ABOUTME: Contains AgentCard, Task types, and other shared infrastructure types that can be reused across domains

from typing import List, Dict, Any, Optional, Union, Literal
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field


# Infrastructure types
class ServerConfig(BaseModel):
    """Server Configuration for MCP connections."""

    host: str
    port: int
    transport: str
    url: str


# Agent configuration types - prefer A2A library version if available
try:
    from a2a.types import AgentCard
except ImportError:
    # Fallback to local implementation if A2A library not available
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
        tier: Optional[int] = None
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


# Task and workflow types
class TaskState(str, Enum):
    """Task execution states."""
    pending = "pending"
    working = "working"
    completed = "completed"
    failed = "failed"
    input_required = "input_required"


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
    """Message with parts and metadata."""
    parts: List[Part]
    role: str = "user"
    timestamp: Optional[datetime] = None
    context_id: Optional[str] = None
    task_id: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class Task:
    """Task representation with state and metadata."""
    id: str
    contextId: str
    state: TaskState
    message: Union[Message, Dict[str, Any]]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


# Generic task types for orchestrators
@dataclass 
class GenericTask:
    """Generic task for orchestration across any domain."""
    id: str
    description: str
    status: str = "pending"
    agent_type: Optional[str] = None
    domain: Optional[str] = None
    priority: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TaskList:
    """Generic task list for orchestrators."""
    tasks: List[GenericTask]
    original_query: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# Generic agent response types
@dataclass 
class AgentResponse:
    """Generic agent response format for all Framework V2.0 agents."""
    content: Union[str, Dict[str, Any]]
    is_task_complete: bool
    require_user_input: bool
    agent_name: Optional[str] = None
    response_type: str = "text"  # "text", "data", "json"
    context_id: Optional[str] = None
    task_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class GenericPlannerTask(BaseModel):
    """Generic task model that can be used across domains."""
    
    id: Union[int, str] = Field(description='Unique ID for the task.')
    description: str = Field(description='Clear description of the task to be executed.')
    status: Literal[
        'pending', 'in_progress', 'completed', 'failed', 
        'input_required', 'todo', 'not_started'
    ] = Field(description='Status of the task', default='pending')
    agent_type: Optional[str] = Field(description='Type of agent to handle this task', default=None)
    domain: Optional[str] = Field(description='Domain this task belongs to', default=None)
    priority: Optional[int] = Field(description='Task priority (1-10)', default=5)
    dependencies: Optional[List[Union[int, str]]] = Field(description='Task IDs this depends on', default=None)
    estimated_duration: Optional[str] = Field(description='Estimated time to complete', default=None)
    metadata: Optional[Dict[str, Any]] = Field(description='Additional task metadata', default=None)


class GenericTaskList(BaseModel):
    """Generic task list that can be used across domains."""
    
    original_query: Optional[str] = Field(description='The original user query for context.')
    domain: Optional[str] = Field(description='Domain this task list belongs to')
    tasks: List[GenericPlannerTask] = Field(description='A list of tasks to be executed.')
    coordination_strategy: Optional[Literal['sequential', 'parallel', 'hybrid']] = Field(
        description='How tasks should be coordinated', default='sequential'
    )
    estimated_total_duration: Optional[str] = Field(description='Total estimated duration', default=None)
    metadata: Optional[Dict[str, Any]] = Field(description='Additional metadata', default=None)


class GenericAgentResponse(BaseModel):
    """Generic agent response that can be used across domains."""
    
    status: Literal['completed', 'input_required', 'error', 'in_progress']
    content: Optional[Union[str, Dict[str, Any]]] = Field(description='Response content', default=None)
    message: Optional[str] = Field(description='Human-readable message', default=None)
    task_list: Optional[GenericTaskList] = Field(description='Task list if applicable', default=None)
    question: Optional[str] = Field(description='Question for the user if input required', default=None)
    agent_name: Optional[str] = Field(description='Name of the responding agent', default=None)
    response_type: Optional[str] = Field(description='Type of response', default='text')
    metadata: Optional[Dict[str, Any]] = Field(description='Additional metadata', default=None)


# Event types
@dataclass
class TaskStatusUpdateEvent:
    """Event for task status updates."""
    taskId: str
    contextId: str
    state: TaskState
    message: Optional[Message] = None
    final: bool = False
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class TaskArtifactUpdateEvent:
    """Event for task artifact updates."""
    taskId: str
    contextId: str
    artifacts: List[Part]
    name: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class SendStreamingMessageSuccessResponse:
    """Response for successful streaming message."""
    result: Union[TaskStatusUpdateEvent, TaskArtifactUpdateEvent]


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