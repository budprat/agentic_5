# ABOUTME: Base classes for memory service providing abstract interface for memory operations
# ABOUTME: Defines MemoryEntry, MemoryQuery, and MemoryServiceBase for implementation by backends

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional, Set
from enum import Enum


class MemoryType(Enum):
    """Types of memory entries"""
    CONVERSATION = "conversation"
    FACT = "fact"
    PROCEDURE = "procedure"
    CONTEXT = "context"
    RELATIONSHIP = "relationship"
    PREFERENCE = "preference"
    DECISION = "decision"
    ERROR = "error"
    LEARNING = "learning"


@dataclass
class MemoryEntry:
    """Single memory entry with metadata"""
    content: str
    memory_type: MemoryType
    agent_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    importance: float = 0.5  # 0-1 scale
    ttl_seconds: Optional[int] = None  # Time to live
    embedding: Optional[List[float]] = None  # Pre-computed embedding
    memory_id: Optional[str] = None  # Assigned by storage backend
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "content": self.content,
            "memory_type": self.memory_type.value,
            "agent_id": self.agent_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "tags": list(self.tags),
            "importance": self.importance,
            "ttl_seconds": self.ttl_seconds,
            "memory_id": self.memory_id,
            "session_id": self.session_id,
            "user_id": self.user_id
        }


@dataclass
class MemoryQuery:
    """Query parameters for retrieving memories"""
    query_text: Optional[str] = None
    agent_id: Optional[str] = None
    memory_types: Optional[List[MemoryType]] = None
    tags: Optional[Set[str]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    min_importance: Optional[float] = None
    max_results: int = 10
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    include_expired: bool = False
    similarity_threshold: float = 0.7


@dataclass
class MemorySearchResult:
    """Result from memory search"""
    memory: MemoryEntry
    relevance_score: float
    match_reason: str


class MemoryServiceBase(ABC):
    """Abstract base class for memory services"""
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the memory service with configuration"""
        pass
    
    @abstractmethod
    async def store_memory(self, memory: MemoryEntry) -> str:
        """Store a memory entry and return its ID"""
        pass
    
    @abstractmethod
    async def retrieve_memories(self, query: MemoryQuery) -> List[MemorySearchResult]:
        """Retrieve memories based on query parameters"""
        pass
    
    @abstractmethod
    async def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing memory"""
        pass
    
    @abstractmethod
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory by ID"""
        pass
    
    @abstractmethod
    async def get_memory_by_id(self, memory_id: str) -> Optional[MemoryEntry]:
        """Get a specific memory by ID"""
        pass
    
    async def consolidate_memories(self, agent_id: str) -> Optional[MemoryEntry]:
        """Consolidate related memories into higher-level insights"""
        # Default implementation - can be overridden
        memories = await self.retrieve_memories(
            MemoryQuery(agent_id=agent_id, max_results=100)
        )
        
        if len(memories) < 5:
            return None
            
        # Basic consolidation logic
        memory_contents = [m.memory.content for m in memories[:20]]
        consolidated_content = f"Consolidated insights from {len(memory_contents)} memories:\n"
        consolidated_content += "\n".join(f"- {content}" for content in memory_contents[:5])
        
        return MemoryEntry(
            content=consolidated_content,
            memory_type=MemoryType.LEARNING,
            agent_id=agent_id,
            importance=0.8,
            metadata={"consolidated": True, "source_count": len(memory_contents)}
        )
    
    async def forget_old_memories(self, agent_id: str, days: int = 30) -> int:
        """Remove memories older than specified days"""
        cutoff_time = datetime.now() - timedelta(days=days)
        memories = await self.retrieve_memories(
            MemoryQuery(
                agent_id=agent_id,
                end_time=cutoff_time,
                max_results=1000
            )
        )
        
        deleted_count = 0
        for result in memories:
            if result.memory.importance < 0.7:  # Only forget less important memories
                if await self.delete_memory(result.memory.memory_id):
                    deleted_count += 1
                    
        return deleted_count
    
    async def get_agent_summary(self, agent_id: str) -> Dict[str, Any]:
        """Get summary statistics for an agent's memories"""
        memories = await self.retrieve_memories(
            MemoryQuery(agent_id=agent_id, max_results=1000)
        )
        
        type_counts = {}
        for result in memories:
            mem_type = result.memory.memory_type.value
            type_counts[mem_type] = type_counts.get(mem_type, 0) + 1
            
        return {
            "total_memories": len(memories),
            "memory_types": type_counts,
            "average_importance": sum(r.memory.importance for r in memories) / len(memories) if memories else 0,
            "oldest_memory": min((r.memory.timestamp for r in memories), default=None),
            "newest_memory": max((r.memory.timestamp for r in memories), default=None)
        }


from datetime import timedelta