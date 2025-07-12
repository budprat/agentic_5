# ABOUTME: Connection pooling manager for A2A protocol to optimize network performance
# ABOUTME: Provides persistent HTTP sessions with health monitoring and automatic cleanup

import asyncio
import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import aiohttp
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class A2AConnectionPool:
    """
    Framework V2.0 Connection Pool Manager for A2A Protocol
    
    Provides connection pooling with:
    - Persistent HTTP sessions per target port
    - Automatic connection health monitoring
    - Connection reuse and lifecycle management
    - Configurable pool limits and timeouts
    - Performance metrics tracking
    
    Expected performance improvement: 60% reduction in connection overhead
    """
    
    def __init__(
        self,
        max_connections_per_host: int = 10,
        max_keepalive_connections: int = 5,
        keepalive_timeout: int = 30,
        connection_timeout: int = 10,
        total_timeout: int = 60,
        health_check_interval: int = 300,  # 5 minutes
        cleanup_interval: int = 600  # 10 minutes
    ):
        """
        Initialize connection pool manager.
        
        Args:
            max_connections_per_host: Maximum concurrent connections per host
            max_keepalive_connections: Maximum idle connections to keep alive
            keepalive_timeout: Seconds to keep idle connections alive
            connection_timeout: Timeout for establishing connection
            total_timeout: Total timeout for requests
            health_check_interval: Seconds between health checks
            cleanup_interval: Seconds between cleanup cycles
        """
        self.max_connections_per_host = max_connections_per_host
        self.max_keepalive_connections = max_keepalive_connections
        self.keepalive_timeout = keepalive_timeout
        self.connection_timeout = connection_timeout
        self.total_timeout = total_timeout
        self.health_check_interval = health_check_interval
        self.cleanup_interval = cleanup_interval
        
        # Port -> Session mapping
        self._sessions: Dict[int, aiohttp.ClientSession] = {}
        self._session_created_at: Dict[int, datetime] = {}
        self._session_last_used: Dict[int, datetime] = {}
        self._session_request_count: Dict[int, int] = {}
        
        # Performance metrics
        self._metrics = {
            "connections_created": 0,
            "connections_reused": 0,
            "connections_closed": 0,
            "health_checks_performed": 0,
            "total_requests": 0,
            "connection_errors": 0
        }
        
        # Background tasks
        self._health_check_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False
        
    async def start(self):
        """Start background tasks for health monitoring and cleanup."""
        if self._running:
            return
            
        self._running = True
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("A2A connection pool started")
        
    async def stop(self):
        """Stop background tasks and close all connections."""
        self._running = False
        
        # Cancel background tasks
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
                
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Close all sessions
        await self.close_all()
        logger.info("A2A connection pool stopped")
        
    @asynccontextmanager
    async def get_session(self, port: int) -> aiohttp.ClientSession:
        """
        Get or create a session for the specified port.
        
        Args:
            port: Target agent port
            
        Yields:
            aiohttp.ClientSession configured for the port
            
        Note:
            Sessions are automatically reused when possible
        """
        session = await self._get_or_create_session(port)
        
        try:
            # Update usage tracking
            self._session_last_used[port] = datetime.now()
            self._session_request_count[port] = self._session_request_count.get(port, 0) + 1
            self._metrics["total_requests"] += 1
            
            yield session
            
        except Exception as e:
            # Track connection errors
            self._metrics["connection_errors"] += 1
            logger.error(f"Connection error for port {port}: {e}")
            
            # Consider closing problematic session
            if isinstance(e, (aiohttp.ClientError, asyncio.TimeoutError)):
                await self._close_session(port)
                
            raise
            
    async def _get_or_create_session(self, port: int) -> aiohttp.ClientSession:
        """Get existing session or create new one."""
        if port in self._sessions and not self._sessions[port].closed:
            # Reuse existing session
            self._metrics["connections_reused"] += 1
            logger.debug(f"Reusing connection for port {port}")
            return self._sessions[port]
            
        # Create new session
        logger.debug(f"Creating new connection for port {port}")
        
        # Configure connector with pooling settings
        connector = aiohttp.TCPConnector(
            limit_per_host=self.max_connections_per_host,
            limit=self.max_connections_per_host * 10,  # Total limit
            ttl_dns_cache=300,  # DNS cache for 5 minutes
            enable_cleanup_closed=True,
            force_close=False,
            keepalive_timeout=self.keepalive_timeout
        )
        
        # Configure timeouts
        timeout = aiohttp.ClientTimeout(
            total=self.total_timeout,
            connect=self.connection_timeout,
            sock_connect=self.connection_timeout,
            sock_read=30
        )
        
        # Create session
        session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                "User-Agent": "A2A-Protocol-Client/2.0-Pooled",
                "Connection": "keep-alive"
            }
        )
        
        # Track session
        self._sessions[port] = session
        self._session_created_at[port] = datetime.now()
        self._session_last_used[port] = datetime.now()
        self._session_request_count[port] = 0
        self._metrics["connections_created"] += 1
        
        return session
        
    async def _close_session(self, port: int):
        """Close and remove a session."""
        if port in self._sessions:
            session = self._sessions[port]
            if not session.closed:
                await session.close()
                self._metrics["connections_closed"] += 1
                
            # Clean up tracking
            del self._sessions[port]
            if port in self._session_created_at:
                del self._session_created_at[port]
            if port in self._session_last_used:
                del self._session_last_used[port]
            if port in self._session_request_count:
                del self._session_request_count[port]
                
            logger.debug(f"Closed connection for port {port}")
            
    async def close_all(self):
        """Close all sessions in the pool."""
        ports = list(self._sessions.keys())
        for port in ports:
            await self._close_session(port)
            
    async def _health_check_loop(self):
        """Background task to check connection health."""
        while self._running:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
                
    async def _cleanup_loop(self):
        """Background task to clean up idle connections."""
        while self._running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_idle_connections()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
                
    async def _perform_health_checks(self):
        """Check health of all active connections."""
        current_time = datetime.now()
        ports_to_check = list(self._sessions.keys())
        
        for port in ports_to_check:
            try:
                session = self._sessions.get(port)
                if not session or session.closed:
                    await self._close_session(port)
                    continue
                    
                # Simple health check - OPTIONS request
                url = f"http://localhost:{port}"
                async with session.options(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status >= 500:
                        logger.warning(f"Unhealthy connection to port {port}, closing")
                        await self._close_session(port)
                        
                self._metrics["health_checks_performed"] += 1
                
            except Exception as e:
                logger.debug(f"Health check failed for port {port}: {e}")
                await self._close_session(port)
                
    async def _cleanup_idle_connections(self):
        """Clean up connections that have been idle too long."""
        current_time = datetime.now()
        idle_threshold = timedelta(seconds=self.keepalive_timeout * 2)
        
        ports_to_check = list(self._sessions.keys())
        
        for port in ports_to_check:
            last_used = self._session_last_used.get(port)
            if last_used and (current_time - last_used) > idle_threshold:
                logger.debug(f"Closing idle connection for port {port}")
                await self._close_session(port)
                
    def get_metrics(self) -> Dict[str, Any]:
        """Get connection pool performance metrics."""
        active_connections = len([s for s in self._sessions.values() if not s.closed])
        
        reuse_rate = 0
        if self._metrics["total_requests"] > 0:
            reuse_rate = (self._metrics["connections_reused"] / 
                         self._metrics["total_requests"]) * 100
                         
        return {
            **self._metrics,
            "active_connections": active_connections,
            "connection_reuse_rate": round(reuse_rate, 2),
            "average_requests_per_connection": (
                self._metrics["total_requests"] / max(1, self._metrics["connections_created"])
            )
        }
        
    def get_connection_stats(self) -> Dict[int, Dict[str, Any]]:
        """Get detailed stats for each connection."""
        stats = {}
        current_time = datetime.now()
        
        for port, session in self._sessions.items():
            if session and not session.closed:
                created_at = self._session_created_at.get(port)
                last_used = self._session_last_used.get(port)
                
                stats[port] = {
                    "status": "active",
                    "created_at": created_at.isoformat() if created_at else None,
                    "last_used": last_used.isoformat() if last_used else None,
                    "age_seconds": (current_time - created_at).total_seconds() if created_at else 0,
                    "idle_seconds": (current_time - last_used).total_seconds() if last_used else 0,
                    "request_count": self._session_request_count.get(port, 0)
                }
                
        return stats


# Global connection pool instance
_global_pool: Optional[A2AConnectionPool] = None


def get_global_connection_pool() -> A2AConnectionPool:
    """Get or create the global connection pool instance."""
    global _global_pool
    if _global_pool is None:
        _global_pool = A2AConnectionPool()
    return _global_pool


async def initialize_global_pool(**kwargs):
    """Initialize and start the global connection pool with custom settings."""
    global _global_pool
    _global_pool = A2AConnectionPool(**kwargs)
    await _global_pool.start()
    return _global_pool


async def shutdown_global_pool():
    """Shutdown the global connection pool."""
    global _global_pool
    if _global_pool:
        await _global_pool.stop()
        _global_pool = None