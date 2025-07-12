# ABOUTME: Prometheus metrics collection for Framework V2.0 monitoring
# ABOUTME: Provides system, agent, and communication metrics with minimal overhead

import time
import logging
import asyncio
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from contextlib import contextmanager
from collections import defaultdict
import threading

logger = logging.getLogger(__name__)

# Try to import prometheus_client, but make it optional
try:
    from prometheus_client import (
        Counter, Gauge, Histogram, Summary,
        CollectorRegistry, generate_latest,
        start_http_server, push_to_gateway
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    logger.info("prometheus_client not installed, metrics will be collected but not exported")
    PROMETHEUS_AVAILABLE = False
    
    # Create dummy classes for when prometheus_client is not available
    class DummyMetric:
        def __init__(self, *args, **kwargs):
            self.value = 0
            
        def inc(self, value=1):
            self.value += value
            
        def dec(self, value=1):
            self.value -= value
            
        def set(self, value):
            self.value = value
            
        def observe(self, value):
            pass
            
        def labels(self, **kwargs):
            return self
    
    Counter = Gauge = Histogram = Summary = DummyMetric
    CollectorRegistry = object
    
    def generate_latest(registry):
        return b"# Prometheus client not installed"
    
    def start_http_server(port, registry=None):
        logger.warning(f"Cannot start metrics server on port {port} - prometheus_client not installed")


class MetricsCollector:
    """
    Framework V2.0 Metrics Collector
    
    Provides comprehensive metrics collection for:
    - Agent lifecycle and performance
    - A2A communication statistics
    - Quality validation results
    - Connection pool performance
    - System resource usage
    
    Designed for minimal overhead and optional Prometheus export.
    """
    
    def __init__(
        self,
        namespace: str = "a2a_mcp",
        subsystem: str = "framework",
        registry: Optional[Any] = None,
        enable_system_metrics: bool = True
    ):
        """
        Initialize metrics collector.
        
        Args:
            namespace: Metrics namespace (prefix)
            subsystem: Metrics subsystem
            registry: Prometheus CollectorRegistry (creates new if None)
            enable_system_metrics: Whether to collect system metrics
        """
        self.namespace = namespace
        self.subsystem = subsystem
        self.registry = registry or (CollectorRegistry() if PROMETHEUS_AVAILABLE else None)
        self.enable_system_metrics = enable_system_metrics
        
        # Internal metrics storage (always available)
        self._metrics_data = defaultdict(lambda: defaultdict(float))
        self._start_time = time.time()
        self._lock = threading.Lock()
        
        # Initialize Prometheus metrics if available
        self._init_prometheus_metrics()
        
        # Initialize internal collectors
        self._init_internal_collectors()
        
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metric collectors."""
        if not PROMETHEUS_AVAILABLE:
            return
            
        # Agent metrics
        self.agent_requests_total = Counter(
            f'{self.namespace}_{self.subsystem}_agent_requests_total',
            'Total number of agent requests',
            ['agent_name', 'status'],
            registry=self.registry
        )
        
        self.agent_request_duration_seconds = Histogram(
            f'{self.namespace}_{self.subsystem}_agent_request_duration_seconds',
            'Agent request duration in seconds',
            ['agent_name'],
            buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
            registry=self.registry
        )
        
        self.agent_active_requests = Gauge(
            f'{self.namespace}_{self.subsystem}_agent_active_requests',
            'Number of active agent requests',
            ['agent_name'],
            registry=self.registry
        )
        
        # A2A communication metrics
        self.a2a_messages_total = Counter(
            f'{self.namespace}_{self.subsystem}_a2a_messages_total',
            'Total A2A messages sent',
            ['source_agent', 'target_agent', 'status'],
            registry=self.registry
        )
        
        self.a2a_message_latency_seconds = Histogram(
            f'{self.namespace}_{self.subsystem}_a2a_message_latency_seconds',
            'A2A message latency in seconds',
            ['source_agent', 'target_agent'],
            buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5),
            registry=self.registry
        )
        
        # Connection pool metrics
        self.connection_pool_active = Gauge(
            f'{self.namespace}_{self.subsystem}_connection_pool_active',
            'Active connections in pool',
            ['pool_name'],
            registry=self.registry
        )
        
        self.connection_pool_created_total = Counter(
            f'{self.namespace}_{self.subsystem}_connection_pool_created_total',
            'Total connections created',
            ['pool_name'],
            registry=self.registry
        )
        
        self.connection_pool_reused_total = Counter(
            f'{self.namespace}_{self.subsystem}_connection_pool_reused_total',
            'Total connections reused',
            ['pool_name'],
            registry=self.registry
        )
        
        # Quality validation metrics
        self.quality_validations_total = Counter(
            f'{self.namespace}_{self.subsystem}_quality_validations_total',
            'Total quality validations performed',
            ['domain', 'status'],
            registry=self.registry
        )
        
        self.quality_score = Gauge(
            f'{self.namespace}_{self.subsystem}_quality_score',
            'Current quality score',
            ['domain', 'metric'],
            registry=self.registry
        )
        
        # System metrics
        if self.enable_system_metrics:
            self.system_uptime_seconds = Gauge(
                f'{self.namespace}_{self.subsystem}_uptime_seconds',
                'System uptime in seconds',
                registry=self.registry
            )
            
            self.system_agents_active = Gauge(
                f'{self.namespace}_{self.subsystem}_agents_active',
                'Number of active agents',
                registry=self.registry
            )
    
    def _init_internal_collectors(self):
        """Initialize internal metric collectors."""
        # Agent performance tracking
        self._agent_request_count = defaultdict(int)
        self._agent_error_count = defaultdict(int)
        self._agent_total_duration = defaultdict(float)
        
        # A2A communication tracking
        self._a2a_message_count = defaultdict(int)
        self._a2a_error_count = defaultdict(int)
        self._a2a_total_latency = defaultdict(float)
        
        # Connection pool tracking
        self._pool_connections_created = 0
        self._pool_connections_reused = 0
        self._pool_active_connections = 0
        
        # Quality tracking
        self._quality_validation_count = defaultdict(int)
        self._quality_scores = defaultdict(list)
    
    # Agent metrics methods
    
    def record_agent_request(self, agent_name: str, status: str = "success", duration: Optional[float] = None):
        """Record an agent request."""
        with self._lock:
            self._agent_request_count[agent_name] += 1
            if status != "success":
                self._agent_error_count[agent_name] += 1
            if duration:
                self._agent_total_duration[agent_name] += duration
            
            if PROMETHEUS_AVAILABLE:
                self.agent_requests_total.labels(agent_name=agent_name, status=status).inc()
                if duration:
                    self.agent_request_duration_seconds.labels(agent_name=agent_name).observe(duration)
    
    @contextmanager
    def track_agent_request(self, agent_name: str):
        """Context manager to track agent request timing."""
        start_time = time.time()
        
        # Increment active requests
        if PROMETHEUS_AVAILABLE:
            self.agent_active_requests.labels(agent_name=agent_name).inc()
        
        try:
            yield
            # Success
            duration = time.time() - start_time
            self.record_agent_request(agent_name, "success", duration)
        except Exception as e:
            # Error
            duration = time.time() - start_time
            self.record_agent_request(agent_name, "error", duration)
            raise
        finally:
            # Decrement active requests
            if PROMETHEUS_AVAILABLE:
                self.agent_active_requests.labels(agent_name=agent_name).dec()
    
    # A2A communication metrics
    
    def record_a2a_message(
        self,
        source_agent: str,
        target_agent: str,
        status: str = "success",
        latency: Optional[float] = None
    ):
        """Record an A2A message."""
        with self._lock:
            key = f"{source_agent}->{target_agent}"
            self._a2a_message_count[key] += 1
            if status != "success":
                self._a2a_error_count[key] += 1
            if latency:
                self._a2a_total_latency[key] += latency
            
            if PROMETHEUS_AVAILABLE:
                self.a2a_messages_total.labels(
                    source_agent=source_agent,
                    target_agent=target_agent,
                    status=status
                ).inc()
                if latency:
                    self.a2a_message_latency_seconds.labels(
                        source_agent=source_agent,
                        target_agent=target_agent
                    ).observe(latency)
    
    # Connection pool metrics
    
    def update_connection_pool_metrics(
        self,
        pool_name: str = "default",
        active: Optional[int] = None,
        created: Optional[int] = None,
        reused: Optional[int] = None
    ):
        """Update connection pool metrics."""
        with self._lock:
            if active is not None:
                self._pool_active_connections = active
                if PROMETHEUS_AVAILABLE:
                    self.connection_pool_active.labels(pool_name=pool_name).set(active)
            
            if created is not None:
                increment = created - self._pool_connections_created
                self._pool_connections_created = created
                if PROMETHEUS_AVAILABLE and increment > 0:
                    self.connection_pool_created_total.labels(pool_name=pool_name).inc(increment)
            
            if reused is not None:
                increment = reused - self._pool_connections_reused
                self._pool_connections_reused = reused
                if PROMETHEUS_AVAILABLE and increment > 0:
                    self.connection_pool_reused_total.labels(pool_name=pool_name).inc(increment)
    
    # Quality metrics
    
    def record_quality_validation(
        self,
        domain: str,
        status: str = "passed",
        scores: Optional[Dict[str, float]] = None
    ):
        """Record quality validation results."""
        with self._lock:
            self._quality_validation_count[f"{domain}_{status}"] += 1
            
            if PROMETHEUS_AVAILABLE:
                self.quality_validations_total.labels(domain=domain, status=status).inc()
            
            if scores:
                for metric, score in scores.items():
                    self._quality_scores[f"{domain}_{metric}"].append(score)
                    if PROMETHEUS_AVAILABLE:
                        self.quality_score.labels(domain=domain, metric=metric).set(score)
    
    # System metrics
    
    def update_system_metrics(self, active_agents: Optional[int] = None):
        """Update system-level metrics."""
        if not self.enable_system_metrics:
            return
            
        with self._lock:
            uptime = time.time() - self._start_time
            
            if PROMETHEUS_AVAILABLE:
                self.system_uptime_seconds.set(uptime)
                if active_agents is not None:
                    self.system_agents_active.set(active_agents)
    
    # Export and reporting
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all collected metrics."""
        with self._lock:
            uptime = time.time() - self._start_time
            
            # Calculate agent statistics
            agent_stats = {}
            for agent in self._agent_request_count:
                total = self._agent_request_count[agent]
                errors = self._agent_error_count[agent]
                avg_duration = (
                    self._agent_total_duration[agent] / total
                    if total > 0 else 0
                )
                agent_stats[agent] = {
                    "total_requests": total,
                    "error_rate": errors / total if total > 0 else 0,
                    "average_duration_seconds": avg_duration
                }
            
            # Calculate A2A statistics
            a2a_stats = {}
            for route in self._a2a_message_count:
                total = self._a2a_message_count[route]
                errors = self._a2a_error_count[route]
                avg_latency = (
                    self._a2a_total_latency[route] / total
                    if total > 0 else 0
                )
                a2a_stats[route] = {
                    "total_messages": total,
                    "error_rate": errors / total if total > 0 else 0,
                    "average_latency_seconds": avg_latency
                }
            
            # Calculate quality statistics
            quality_stats = {}
            for key, scores in self._quality_scores.items():
                if scores:
                    quality_stats[key] = {
                        "average_score": sum(scores) / len(scores),
                        "min_score": min(scores),
                        "max_score": max(scores),
                        "validation_count": len(scores)
                    }
            
            return {
                "uptime_seconds": uptime,
                "uptime_human": self._format_duration(uptime),
                "agent_metrics": agent_stats,
                "a2a_metrics": a2a_stats,
                "connection_pool": {
                    "active_connections": self._pool_active_connections,
                    "total_created": self._pool_connections_created,
                    "total_reused": self._pool_connections_reused,
                    "reuse_rate": (
                        self._pool_connections_reused /
                        max(1, self._pool_connections_created + self._pool_connections_reused)
                    )
                },
                "quality_metrics": quality_stats,
                "prometheus_available": PROMETHEUS_AVAILABLE
            }
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format."""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{secs}s")
        
        return " ".join(parts)
    
    def export_prometheus(self) -> bytes:
        """Export metrics in Prometheus format."""
        if PROMETHEUS_AVAILABLE and self.registry:
            return generate_latest(self.registry)
        return b"# Prometheus metrics not available"
    
    async def start_metrics_server(self, port: int = 9090):
        """Start Prometheus metrics HTTP server."""
        if PROMETHEUS_AVAILABLE:
            start_http_server(port, registry=self.registry)
            logger.info(f"Prometheus metrics server started on port {port}")
        else:
            logger.warning("Cannot start metrics server - prometheus_client not installed")


# Global metrics collector instance
_global_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create global metrics collector."""
    global _global_metrics_collector
    if _global_metrics_collector is None:
        _global_metrics_collector = MetricsCollector()
    return _global_metrics_collector


def record_agent_request(agent_name: str, status: str = "success", duration: Optional[float] = None):
    """Record an agent request in global metrics."""
    get_metrics_collector().record_agent_request(agent_name, status, duration)


def record_a2a_message(
    source_agent: str,
    target_agent: str,
    status: str = "success",
    latency: Optional[float] = None
):
    """Record an A2A message in global metrics."""
    get_metrics_collector().record_a2a_message(source_agent, target_agent, status, latency)


def get_metrics_summary() -> Dict[str, Any]:
    """Get summary of all metrics from global collector."""
    return get_metrics_collector().get_metrics_summary()


# Convenience exports
__all__ = [
    'MetricsCollector',
    'get_metrics_collector',
    'record_agent_request',
    'record_a2a_message',
    'get_metrics_summary',
    'PROMETHEUS_AVAILABLE'
]