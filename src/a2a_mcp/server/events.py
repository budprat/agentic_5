# ABOUTME: Event queue system for asynchronous event handling
# ABOUTME: Manages event flow between agents, tasks, and UI updates

import asyncio
import logging
from typing import Any, Optional, List, Callable
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class Event:
    """Base event class."""
    
    def __init__(self, event_type: str, data: Any, timestamp: Optional[datetime] = None):
        self.id = str(uuid.uuid4())
        self.type = event_type
        self.data = data
        self.timestamp = timestamp or datetime.utcnow()


class EventQueue:
    """Asynchronous event queue for agent communication."""
    
    def __init__(self, max_size: int = 1000):
        """Initialize event queue.
        
        Args:
            max_size: Maximum queue size before blocking
        """
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=max_size)
        self.handlers: dict[str, List[Callable]] = {}
        self.running = False
        self._process_task = None
        
    async def start(self):
        """Start processing events."""
        self.running = True
        self._process_task = asyncio.create_task(self._process_events())
        logger.info("EventQueue started")
        
    async def stop(self):
        """Stop processing events."""
        self.running = False
        if self._process_task:
            self._process_task.cancel()
            try:
                await self._process_task
            except asyncio.CancelledError:
                pass
        logger.info("EventQueue stopped")
    
    async def enqueue_event(self, event: Any) -> None:
        """Add event to queue.
        
        Args:
            event: Event to enqueue
        """
        await self.queue.put(event)
        
    def register_handler(self, event_type: str, handler: Callable):
        """Register event handler.
        
        Args:
            event_type: Type of event to handle
            handler: Async callable to handle event
        """
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
        
    def unregister_handler(self, event_type: str, handler: Callable):
        """Unregister event handler."""
        if event_type in self.handlers:
            self.handlers[event_type].remove(handler)
            
    async def _process_events(self):
        """Process events from queue."""
        while self.running:
            try:
                # Wait for event with timeout
                event = await asyncio.wait_for(
                    self.queue.get(), 
                    timeout=1.0
                )
                
                # Determine event type
                event_type = None
                if hasattr(event, 'type'):
                    event_type = event.type
                elif hasattr(event, '__class__'):
                    event_type = event.__class__.__name__
                
                # Call handlers
                if event_type and event_type in self.handlers:
                    for handler in self.handlers[event_type]:
                        try:
                            await handler(event)
                        except Exception as e:
                            logger.error(f"Error in event handler: {e}")
                            
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing event: {e}")


class SimpleEventQueue(EventQueue):
    """Simple event queue that stores events for retrieval."""
    
    def __init__(self):
        super().__init__()
        self.events = []
        
    async def enqueue_event(self, event: Any) -> None:
        """Store event for later retrieval."""
        self.events.append(event)
        await super().enqueue_event(event)
        
    def get_events(self) -> List[Any]:
        """Get all stored events."""
        return self.events.copy()
        
    def clear_events(self):
        """Clear stored events."""
        self.events.clear()