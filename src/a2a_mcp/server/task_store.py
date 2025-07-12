# ABOUTME: Task storage implementations for persisting agent execution tasks
# ABOUTME: Provides in-memory storage with optional persistence backends

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import OrderedDict
import json

logger = logging.getLogger(__name__)


class TaskStore:
    """Abstract base class for task storage."""
    
    async def initialize(self):
        """Initialize the store."""
        pass
    
    async def cleanup(self):
        """Clean up resources."""
        pass
    
    async def create_task(self, task: Dict[str, Any]) -> str:
        """Create a new task."""
        raise NotImplementedError
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a task by ID."""
        raise NotImplementedError
    
    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Update a task."""
        raise NotImplementedError
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        raise NotImplementedError
    
    async def list_tasks(
        self,
        status: Optional[str] = None,
        agent_name: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List tasks with optional filtering."""
        raise NotImplementedError
    
    async def health_check(self) -> Dict[str, Any]:
        """Check store health."""
        return {"status": "healthy"}


class InMemoryTaskStore(TaskStore):
    """In-memory task store with TTL and size limits.
    
    Features:
    - Fast in-memory storage
    - Automatic TTL expiration
    - Size-based eviction (LRU)
    - Optional persistence to disk
    - Thread-safe operations
    """
    
    def __init__(
        self,
        max_tasks: int = 10000,
        ttl_seconds: int = 86400,  # 24 hours
        persist_path: Optional[str] = None,
        cleanup_interval: int = 300  # 5 minutes
    ):
        """Initialize the in-memory store.
        
        Args:
            max_tasks: Maximum number of tasks to store
            ttl_seconds: Time-to-live for tasks in seconds
            persist_path: Optional path to persist tasks
            cleanup_interval: Interval for cleanup task in seconds
        """
        self.max_tasks = max_tasks
        self.ttl_seconds = ttl_seconds
        self.persist_path = persist_path
        self.cleanup_interval = cleanup_interval
        
        # Use OrderedDict for LRU behavior
        self._tasks: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._lock = asyncio.Lock()
        self._cleanup_task = None
        
        logger.info(f"InMemoryTaskStore initialized (max_tasks={max_tasks}, ttl={ttl_seconds}s)")
    
    async def initialize(self):
        """Initialize the store and start cleanup task."""
        # Load persisted tasks if path provided
        if self.persist_path:
            await self._load_from_disk()
        
        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("InMemoryTaskStore initialized")
    
    async def cleanup(self):
        """Stop cleanup task and persist if needed."""
        # Cancel cleanup task
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Persist to disk if path provided
        if self.persist_path:
            await self._persist_to_disk()
        
        logger.info("InMemoryTaskStore cleaned up")
    
    async def create_task(self, task: Dict[str, Any]) -> str:
        """Create a new task."""
        async with self._lock:
            task_id = task["id"]
            
            # Enforce size limit (LRU eviction)
            if len(self._tasks) >= self.max_tasks:
                # Remove oldest task
                self._tasks.popitem(last=False)
            
            # Add expiration time
            task["expires_at"] = (
                datetime.utcnow() + timedelta(seconds=self.ttl_seconds)
            ).isoformat()
            
            # Store task (moves to end for LRU)
            self._tasks[task_id] = task
            self._tasks.move_to_end(task_id)
            
            return task_id
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a task by ID."""
        async with self._lock:
            if task_id not in self._tasks:
                return None
            
            task = self._tasks[task_id]
            
            # Check expiration
            if self._is_expired(task):
                del self._tasks[task_id]
                return None
            
            # Move to end for LRU
            self._tasks.move_to_end(task_id)
            
            return task.copy()
    
    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Update a task."""
        async with self._lock:
            if task_id not in self._tasks:
                return False
            
            task = self._tasks[task_id]
            
            # Check expiration
            if self._is_expired(task):
                del self._tasks[task_id]
                return False
            
            # Apply updates
            task.update(updates)
            task["updated_at"] = datetime.utcnow().isoformat()
            
            # Move to end for LRU
            self._tasks.move_to_end(task_id)
            
            return True
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        async with self._lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
                return True
            return False
    
    async def list_tasks(
        self,
        status: Optional[str] = None,
        agent_name: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List tasks with optional filtering."""
        async with self._lock:
            # Remove expired tasks first
            await self._remove_expired()
            
            # Filter tasks
            filtered_tasks = []
            for task in self._tasks.values():
                if status and task.get("status") != status:
                    continue
                if agent_name and task.get("agent_name") != agent_name:
                    continue
                filtered_tasks.append(task.copy())
            
            # Apply pagination
            start = offset
            end = offset + limit
            return filtered_tasks[start:end]
    
    async def health_check(self) -> Dict[str, Any]:
        """Check store health."""
        async with self._lock:
            task_count = len(self._tasks)
            
        return {
            "status": "healthy",
            "task_count": task_count,
            "max_tasks": self.max_tasks,
            "utilization": f"{(task_count / self.max_tasks * 100):.1f}%"
        }
    
    def _is_expired(self, task: Dict[str, Any]) -> bool:
        """Check if a task has expired."""
        if "expires_at" not in task:
            return False
        
        expires_at = datetime.fromisoformat(task["expires_at"])
        return datetime.utcnow() > expires_at
    
    async def _remove_expired(self):
        """Remove all expired tasks."""
        expired_ids = [
            task_id for task_id, task in self._tasks.items()
            if self._is_expired(task)
        ]
        
        for task_id in expired_ids:
            del self._tasks[task_id]
        
        if expired_ids:
            logger.info(f"Removed {len(expired_ids)} expired tasks")
    
    async def _cleanup_loop(self):
        """Periodic cleanup of expired tasks."""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                async with self._lock:
                    await self._remove_expired()
                    
                # Persist if enabled
                if self.persist_path:
                    await self._persist_to_disk()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    async def _persist_to_disk(self):
        """Persist tasks to disk."""
        if not self.persist_path:
            return
        
        try:
            async with self._lock:
                data = {
                    "tasks": dict(self._tasks),
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Write atomically
            temp_path = f"{self.persist_path}.tmp"
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Rename atomically
            import os
            os.replace(temp_path, self.persist_path)
            
            logger.debug(f"Persisted {len(data['tasks'])} tasks to {self.persist_path}")
            
        except Exception as e:
            logger.error(f"Failed to persist tasks: {e}")
    
    async def _load_from_disk(self):
        """Load tasks from disk."""
        if not self.persist_path:
            return
        
        try:
            import os
            if not os.path.exists(self.persist_path):
                return
            
            with open(self.persist_path, 'r') as f:
                data = json.load(f)
            
            # Load tasks
            loaded = 0
            for task_id, task in data.get("tasks", {}).items():
                if not self._is_expired(task):
                    self._tasks[task_id] = task
                    loaded += 1
            
            logger.info(f"Loaded {loaded} tasks from {self.persist_path}")
            
        except Exception as e:
            logger.error(f"Failed to load tasks from disk: {e}")