# ABOUTME: Enterprise observability configuration for Framework V2.0 with OpenTelemetry, Prometheus, and structured logging
# ABOUTME: Provides distributed tracing, metrics collection, and JSON logging for production monitoring

"""
Enterprise Observability Module - Framework V2.0

This module provides comprehensive observability capabilities including:
- OpenTelemetry distributed tracing
- Prometheus metrics collection
- Structured JSON logging
- Performance monitoring
- Error tracking and alerting

Designed for production environments requiring deep visibility into
multi-agent orchestration and execution patterns.
"""

import logging
import json
import time
import os
from typing import Dict, Any, Optional, Callable, List
from functools import wraps
from contextlib import contextmanager
from datetime import datetime, timezone
import asyncio

# OpenTelemetry imports
try:
    from opentelemetry import trace, metrics
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.semconv.resource import ResourceAttributes
    from opentelemetry.trace import Status, StatusCode
    from opentelemetry.instrumentation.logging import LoggingInstrumentor
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    logging.warning("OpenTelemetry not available. Install with: pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation")

# Prometheus imports
try:
    from prometheus_client import Counter, Histogram, Gauge, Summary, Info
    from prometheus_client import start_http_server, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logging.warning("Prometheus client not available. Install with: pip install prometheus-client")


class StructuredLogger:
    """
    Structured JSON logger for better observability.
    
    Features:
    - JSON formatted logs
    - Contextual information injection
    - Correlation ID tracking
    - Performance metrics in logs
    """
    
    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Remove existing handlers
        self.logger.handlers = []
        
        # Create JSON formatter
        handler = logging.StreamHandler()
        handler.setFormatter(self.JSONFormatter())
        self.logger.addHandler(handler)
        
        # Context storage
        self.context: Dict[str, Any] = {}
    
    class JSONFormatter(logging.Formatter):
        """Custom JSON formatter for structured logs."""
        
        def format(self, record: logging.LogRecord) -> str:
            log_data = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno,
            }
            
            # Add exception info if present
            if record.exc_info:
                log_data['exception'] = self.formatException(record.exc_info)
            
            # Add extra fields
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'created', 'filename', 
                              'funcName', 'levelname', 'levelno', 'lineno', 
                              'module', 'msecs', 'pathname', 'process', 
                              'processName', 'relativeCreated', 'thread', 
                              'threadName', 'exc_info', 'exc_text', 'stack_info']:
                    log_data[key] = value
            
            return json.dumps(log_data)
    
    def with_context(self, **kwargs) -> 'StructuredLogger':
        """Add context to all subsequent logs."""
        self.context.update(kwargs)
        return self
    
    def _log(self, level: int, msg: str, **kwargs):
        """Internal log method with context injection."""
        # Extract special logging kwargs that shouldn't go in extra
        exc_info = kwargs.pop('exc_info', None)
        stack_info = kwargs.pop('stack_info', None)
        stacklevel = kwargs.pop('stacklevel', None)
        
        # Remaining kwargs go in extra
        extra = {**self.context, **kwargs}
        
        # Build logging kwargs
        log_kwargs = {'extra': extra}
        if exc_info is not None:
            log_kwargs['exc_info'] = exc_info
        if stack_info is not None:
            log_kwargs['stack_info'] = stack_info
        if stacklevel is not None:
            log_kwargs['stacklevel'] = stacklevel
            
        self.logger.log(level, msg, **log_kwargs)
    
    def debug(self, msg: str, **kwargs):
        self._log(logging.DEBUG, msg, **kwargs)
    
    def info(self, msg: str, **kwargs):
        self._log(logging.INFO, msg, **kwargs)
    
    def warning(self, msg: str, **kwargs):
        self._log(logging.WARNING, msg, **kwargs)
    
    def error(self, msg: str, **kwargs):
        self._log(logging.ERROR, msg, **kwargs)
    
    def critical(self, msg: str, **kwargs):
        self._log(logging.CRITICAL, msg, **kwargs)


class ObservabilityManager:
    """
    Central observability management for Framework V2.0.
    
    Provides:
    - OpenTelemetry tracing setup
    - Prometheus metrics registration
    - Structured logging configuration
    - Performance monitoring utilities
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.logger = StructuredLogger('observability')
        
        # Initialize components
        self.tracer = None
        self.meter = None
        self.metrics: Dict[str, Any] = {}
        
        # Configuration
        self.config = self._load_config()
        
        # Initialize based on availability
        if OTEL_AVAILABLE and self.config.get('tracing', {}).get('enabled', True):
            self._init_tracing()
        
        if PROMETHEUS_AVAILABLE and self.config.get('metrics', {}).get('enabled', True):
            self._init_metrics()
        
        self.logger.info("Observability Manager initialized", 
                        tracing_enabled=OTEL_AVAILABLE,
                        metrics_enabled=PROMETHEUS_AVAILABLE)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load observability configuration from environment."""
        return {
            'service_name': os.getenv('OTEL_SERVICE_NAME', 'a2a-mcp-framework'),
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'tracing': {
                'enabled': os.getenv('TRACING_ENABLED', 'true').lower() == 'true',
                'endpoint': os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'localhost:4317'),
                'insecure': os.getenv('OTEL_EXPORTER_OTLP_INSECURE', 'true').lower() == 'true',
            },
            'metrics': {
                'enabled': os.getenv('METRICS_ENABLED', 'true').lower() == 'true',
                'port': int(os.getenv('METRICS_PORT', '9090')),
                'endpoint': os.getenv('OTEL_METRICS_ENDPOINT', 'localhost:4317'),
            },
            'logging': {
                'level': os.getenv('LOG_LEVEL', 'INFO'),
                'json_format': os.getenv('JSON_LOGS', 'true').lower() == 'true',
            }
        }
    
    def _init_tracing(self):
        """Initialize OpenTelemetry tracing."""
        try:
            # Create resource
            resource = Resource.create({
                ResourceAttributes.SERVICE_NAME: self.config['service_name'],
                ResourceAttributes.SERVICE_VERSION: "2.0.0",
                ResourceAttributes.DEPLOYMENT_ENVIRONMENT: self.config['environment'],
            })
            
            # Setup tracing
            provider = TracerProvider(resource=resource)
            
            # Add OTLP exporter
            otlp_exporter = OTLPSpanExporter(
                endpoint=self.config['tracing']['endpoint'],
                insecure=self.config['tracing']['insecure']
            )
            
            span_processor = BatchSpanProcessor(otlp_exporter)
            provider.add_span_processor(span_processor)
            
            # Set global tracer provider
            trace.set_tracer_provider(provider)
            
            # Get tracer
            self.tracer = trace.get_tracer(__name__, "1.0.0")
            
            # Instrument logging
            LoggingInstrumentor().instrument()
            
            self.logger.info("OpenTelemetry tracing initialized",
                           endpoint=self.config['tracing']['endpoint'])
            
        except Exception as e:
            self.logger.error("Failed to initialize tracing", error=str(e))
    
    def _init_metrics(self):
        """Initialize Prometheus metrics."""
        try:
            # Define metrics
            self.metrics = {
                # Counters
                'orchestration_requests_total': Counter(
                    'orchestration_requests_total',
                    'Total number of orchestration requests',
                    ['domain', 'status']
                ),
                'tasks_executed_total': Counter(
                    'tasks_executed_total',
                    'Total number of tasks executed',
                    ['specialist', 'status']
                ),
                'artifacts_created_total': Counter(
                    'artifacts_created_total',
                    'Total number of artifacts created',
                    ['type', 'session']
                ),
                'errors_total': Counter(
                    'errors_total',
                    'Total number of errors',
                    ['component', 'error_type']
                ),
                
                # Histograms
                'orchestration_duration_seconds': Histogram(
                    'orchestration_duration_seconds',
                    'Orchestration request duration in seconds',
                    ['domain', 'strategy'],
                    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0)
                ),
                'task_duration_seconds': Histogram(
                    'task_duration_seconds',
                    'Task execution duration in seconds',
                    ['specialist'],
                    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0)
                ),
                'artifact_size_bytes': Histogram(
                    'artifact_size_bytes',
                    'Size of created artifacts in bytes',
                    ['type'],
                    buckets=(100, 1000, 10000, 100000, 1000000, 10000000)
                ),
                
                # Gauges
                'active_sessions': Gauge(
                    'active_sessions',
                    'Number of active orchestration sessions'
                ),
                'memory_usage_bytes': Gauge(
                    'memory_usage_bytes',
                    'Current memory usage in bytes',
                    ['component']
                ),
                'workflow_nodes_active': Gauge(
                    'workflow_nodes_active',
                    'Number of active workflow nodes',
                    ['state']
                ),
                
                # Summary
                'qa_confidence_score': Summary(
                    'qa_confidence_score',
                    'Q&A confidence scores',
                    ['question_type']
                ),
                
                # Info
                'framework_info': Info(
                    'framework_info',
                    'Framework version and configuration'
                )
            }
            
            # Set framework info
            self.metrics['framework_info'].info({
                'version': '2.0.0',
                'service': self.config['service_name'],
                'environment': self.config['environment']
            })
            
            # Start metrics server
            start_http_server(self.config['metrics']['port'])
            
            self.logger.info("Prometheus metrics initialized",
                           port=self.config['metrics']['port'])
            
        except Exception as e:
            self.logger.error("Failed to initialize metrics", error=str(e))
    
    def get_tracer(self) -> Optional[Any]:
        """Get OpenTelemetry tracer."""
        return self.tracer
    
    def get_logger(self, name: str) -> StructuredLogger:
        """Get structured logger for component."""
        return StructuredLogger(name)
    
    def record_metric(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Record a metric value."""
        if metric_name not in self.metrics:
            self.logger.warning(f"Unknown metric: {metric_name}")
            return
        
        metric = self.metrics[metric_name]
        labels = labels or {}
        
        try:
            if isinstance(metric, Counter):
                metric.labels(**labels).inc(value)
            elif isinstance(metric, Histogram):
                metric.labels(**labels).observe(value)
            elif isinstance(metric, Gauge):
                metric.labels(**labels).set(value)
            elif isinstance(metric, Summary):
                metric.labels(**labels).observe(value)
        except Exception as e:
            self.logger.error(f"Failed to record metric {metric_name}", error=str(e))
    
    @contextmanager
    def trace_span(self, name: str, attributes: Dict[str, Any] = None):
        """Context manager for tracing spans."""
        if not self.tracer:
            yield None
            return
        
        with self.tracer.start_as_current_span(name) as span:
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, value)
            
            try:
                yield span
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
    
    def trace_async(self, name: str = None):
        """Decorator for tracing async functions."""
        def decorator(func: Callable) -> Callable:
            span_name = name or f"{func.__module__}.{func.__name__}"
            
            @wraps(func)
            async def wrapper(*args, **kwargs):
                with self.trace_span(span_name) as span:
                    start_time = time.time()
                    try:
                        result = await func(*args, **kwargs)
                        
                        # Record success metric
                        self.record_metric(
                            'orchestration_requests_total',
                            1,
                            {'domain': 'unknown', 'status': 'success'}
                        )
                        
                        return result
                    except Exception as e:
                        # Record error metric
                        self.record_metric(
                            'errors_total',
                            1,
                            {'component': func.__module__, 'error_type': type(e).__name__}
                        )
                        raise
                    finally:
                        # Record duration
                        duration = time.time() - start_time
                        self.record_metric(
                            'orchestration_duration_seconds',
                            duration,
                            {'domain': 'unknown', 'strategy': 'unknown'}
                        )
            
            return wrapper
        return decorator
    
    def measure_performance(self, metric_name: str, labels: Dict[str, str] = None):
        """Decorator to measure function performance."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration = time.time() - start_time
                    self.record_metric(metric_name, duration, labels)
            
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    duration = time.time() - start_time
                    self.record_metric(metric_name, duration, labels)
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper
        return decorator


# Global instance
observability = ObservabilityManager()


# Convenience functions
def get_tracer():
    """Get global tracer instance."""
    return observability.get_tracer()


def get_logger(name: str) -> StructuredLogger:
    """Get structured logger for component."""
    return observability.get_logger(name)


def trace_span(name: str, attributes: Dict[str, Any] = None):
    """Create a trace span."""
    return observability.trace_span(name, attributes)


def record_metric(metric_name: str, value: float, labels: Dict[str, str] = None):
    """Record a metric value."""
    observability.record_metric(metric_name, value, labels)


def trace_async(name: str = None):
    """Decorator for tracing async functions."""
    return observability.trace_async(name)


def measure_performance(metric_name: str, labels: Dict[str, str] = None):
    """Decorator to measure function performance."""
    return observability.measure_performance(metric_name, labels)


# Dashboard configuration for Grafana
GRAFANA_DASHBOARD_CONFIG = {
    "dashboard": {
        "title": "A2A MCP Framework Monitoring",
        "panels": [
            {
                "title": "Orchestration Request Rate",
                "targets": [
                    {"expr": "rate(orchestration_requests_total[5m])"}
                ]
            },
            {
                "title": "Task Execution Performance",
                "targets": [
                    {"expr": "histogram_quantile(0.95, rate(task_duration_seconds_bucket[5m]))"}
                ]
            },
            {
                "title": "Active Sessions",
                "targets": [
                    {"expr": "active_sessions"}
                ]
            },
            {
                "title": "Error Rate",
                "targets": [
                    {"expr": "rate(errors_total[5m])"}
                ]
            },
            {
                "title": "Artifact Creation Rate",
                "targets": [
                    {"expr": "rate(artifacts_created_total[5m])"}
                ]
            },
            {
                "title": "Memory Usage",
                "targets": [
                    {"expr": "memory_usage_bytes"}
                ]
            }
        ]
    }
}


# Export dashboard config
def export_grafana_dashboard() -> str:
    """Export Grafana dashboard configuration as JSON."""
    return json.dumps(GRAFANA_DASHBOARD_CONFIG, indent=2)