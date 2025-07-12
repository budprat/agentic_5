# ABOUTME: Push notification system for real-time updates to connected clients
# ABOUTME: Supports WebSocket connections, event filtering, and message queuing

import logging
import asyncio
import json
import uuid
from typing import Dict, Any, Set, Optional, Callable
from datetime import datetime
from collections import defaultdict
from weakref import WeakSet

logger = logging.getLogger(__name__)


class PushNotifier:
    """Abstract base class for push notification systems."""
    
    async def initialize(self):
        """Initialize the notifier."""
        pass
    
    async def cleanup(self):
        """Clean up resources."""
        pass
    
    async def notify(self, message: Dict[str, Any]):
        """Send a notification to subscribers."""
        raise NotImplementedError
    
    async def subscribe(self, connection: Any) -> str:
        """Subscribe a connection for notifications."""
        raise NotImplementedError
    
    async def unsubscribe(self, subscription_id: str):
        """Unsubscribe a connection."""
        raise NotImplementedError
    
    async def health_check(self) -> Dict[str, Any]:
        """Check notifier health."""
        return {"status": "healthy"}


class InMemoryPushNotifier(PushNotifier):
    """In-memory push notification system with WebSocket support.
    
    Features:
    - WebSocket connection management
    - Event filtering by type/agent
    - Message queuing for offline clients
    - Broadcast and targeted notifications
    - Connection health monitoring
    """
    
    def __init__(
        self,
        client: Optional[Any] = None,  # httpx.AsyncClient
        max_queue_size: int = 1000,
        queue_ttl_seconds: int = 3600,  # 1 hour
        heartbeat_interval: int = 30  # seconds
    ):
        """Initialize the push notifier.
        
        Args:
            client: Optional httpx.AsyncClient for external notifications
            max_queue_size: Maximum messages to queue per subscription
            queue_ttl_seconds: TTL for queued messages
            heartbeat_interval: Interval for connection heartbeats
        """
        self.client = client  # For external webhook notifications if needed
        self.max_queue_size = max_queue_size
        self.queue_ttl_seconds = queue_ttl_seconds
        self.heartbeat_interval = heartbeat_interval
        
        # Subscription management
        self._subscriptions: Dict[str, 'Subscription'] = {}
        self._connections: WeakSet = WeakSet()
        self._lock = asyncio.Lock()
        
        # Message queues for offline clients
        self._message_queues: Dict[str, list] = defaultdict(list)
        
        # Heartbeat task
        self._heartbeat_task = None
        
        logger.info("InMemoryPushNotifier initialized")
    
    async def initialize(self):
        """Start heartbeat monitoring."""
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        logger.info("InMemoryPushNotifier started")
    
    async def cleanup(self):
        """Stop heartbeat monitoring and close connections."""
        # Cancel heartbeat
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # Close all connections
        async with self._lock:
            for sub in self._subscriptions.values():
                try:
                    await sub.close()
                except:
                    pass
            
            self._subscriptions.clear()
            self._message_queues.clear()
        
        logger.info("InMemoryPushNotifier cleaned up")
    
    async def notify(self, message: Dict[str, Any]):
        """Broadcast notification to all subscribers."""
        # Add timestamp if not present
        if "timestamp" not in message:
            message["timestamp"] = datetime.utcnow().isoformat()
        
        # Get active subscriptions
        async with self._lock:
            active_subs = list(self._subscriptions.values())
        
        # Send to each subscription
        send_tasks = []
        for sub in active_subs:
            if sub.matches_filter(message):
                send_tasks.append(self._send_to_subscription(sub, message))
        
        # Wait for all sends to complete
        if send_tasks:
            await asyncio.gather(*send_tasks, return_exceptions=True)
        
        logger.debug(f"Notified {len(send_tasks)} subscribers")
    
    async def subscribe(
        self,
        connection: Any,
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Subscribe a WebSocket connection.
        
        Args:
            connection: WebSocket connection object
            filters: Optional filters for notifications
            
        Returns:
            Subscription ID
        """
        subscription_id = str(uuid.uuid4())
        
        async with self._lock:
            # Create subscription
            sub = Subscription(
                id=subscription_id,
                connection=connection,
                filters=filters or {},
                created_at=datetime.utcnow()
            )
            
            self._subscriptions[subscription_id] = sub
            self._connections.add(connection)
            
            # Send queued messages if any
            if subscription_id in self._message_queues:
                queued = self._message_queues.pop(subscription_id)
                for msg in queued:
                    await self._send_to_subscription(sub, msg)
        
        logger.info(f"New subscription: {subscription_id}")
        return subscription_id
    
    async def unsubscribe(self, subscription_id: str):
        """Unsubscribe a connection."""
        async with self._lock:
            if subscription_id in self._subscriptions:
                sub = self._subscriptions.pop(subscription_id)
                try:
                    await sub.close()
                except:
                    pass
                
                logger.info(f"Unsubscribed: {subscription_id}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check notifier health."""
        async with self._lock:
            sub_count = len(self._subscriptions)
            queue_count = sum(len(q) for q in self._message_queues.values())
        
        return {
            "status": "healthy",
            "active_subscriptions": sub_count,
            "queued_messages": queue_count,
            "max_queue_size": self.max_queue_size
        }
    
    async def _send_to_subscription(self, sub: 'Subscription', message: Dict[str, Any]):
        """Send message to a specific subscription."""
        try:
            # Convert to JSON
            data = json.dumps(message)
            
            # Send via WebSocket
            await sub.send(data)
            
        except Exception as e:
            logger.error(f"Failed to send to {sub.id}: {e}")
            
            # Queue message for retry
            await self._queue_message(sub.id, message)
            
            # Remove failed subscription
            await self.unsubscribe(sub.id)
    
    async def _queue_message(self, subscription_id: str, message: Dict[str, Any]):
        """Queue message for offline subscriber."""
        async with self._lock:
            queue = self._message_queues[subscription_id]
            
            # Enforce queue size limit
            if len(queue) >= self.max_queue_size:
                queue.pop(0)  # Remove oldest
            
            queue.append(message)
    
    async def _heartbeat_loop(self):
        """Monitor connection health."""
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                
                # Check each subscription
                async with self._lock:
                    dead_subs = []
                    
                    for sub_id, sub in self._subscriptions.items():
                        try:
                            # Send ping
                            await sub.ping()
                        except:
                            dead_subs.append(sub_id)
                
                # Remove dead subscriptions
                for sub_id in dead_subs:
                    await self.unsubscribe(sub_id)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")


class Subscription:
    """Represents a push notification subscription."""
    
    def __init__(
        self,
        id: str,
        connection: Any,
        filters: Dict[str, Any],
        created_at: datetime
    ):
        """Initialize subscription.
        
        Args:
            id: Unique subscription ID
            connection: WebSocket connection
            filters: Notification filters
            created_at: Creation timestamp
        """
        self.id = id
        self.connection = connection
        self.filters = filters
        self.created_at = created_at
        self.last_ping = datetime.utcnow()
    
    def matches_filter(self, message: Dict[str, Any]) -> bool:
        """Check if message matches subscription filters."""
        if not self.filters:
            return True
        
        # Check event type filter
        if "types" in self.filters:
            if message.get("type") not in self.filters["types"]:
                return False
        
        # Check agent name filter
        if "agents" in self.filters:
            if message.get("agent_name") not in self.filters["agents"]:
                return False
        
        # Check task ID filter
        if "task_ids" in self.filters:
            if message.get("task_id") not in self.filters["task_ids"]:
                return False
        
        return True
    
    async def send(self, data: str):
        """Send data through WebSocket."""
        if hasattr(self.connection, 'send_text'):
            await self.connection.send_text(data)
        elif hasattr(self.connection, 'send_str'):
            await self.connection.send_str(data)
        else:
            await self.connection.send(data)
    
    async def ping(self):
        """Send ping to check connection health."""
        self.last_ping = datetime.utcnow()
        
        if hasattr(self.connection, 'ping'):
            await self.connection.ping()
        else:
            # Send custom ping message
            await self.send(json.dumps({"type": "ping"}))
    
    async def close(self):
        """Close the connection."""
        if hasattr(self.connection, 'close'):
            await self.connection.close()


class BroadcastNotifier(InMemoryPushNotifier):
    """Enhanced notifier with topic-based broadcasting."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._topics: Dict[str, Set[str]] = defaultdict(set)
    
    async def subscribe_to_topic(self, subscription_id: str, topic: str):
        """Subscribe to a specific topic."""
        async with self._lock:
            self._topics[topic].add(subscription_id)
    
    async def unsubscribe_from_topic(self, subscription_id: str, topic: str):
        """Unsubscribe from a topic."""
        async with self._lock:
            if topic in self._topics:
                self._topics[topic].discard(subscription_id)
    
    async def notify_topic(self, topic: str, message: Dict[str, Any]):
        """Send notification to topic subscribers."""
        async with self._lock:
            subscriber_ids = self._topics.get(topic, set()).copy()
        
        # Send to topic subscribers
        for sub_id in subscriber_ids:
            if sub_id in self._subscriptions:
                sub = self._subscriptions[sub_id]
                await self._send_to_subscription(sub, message)