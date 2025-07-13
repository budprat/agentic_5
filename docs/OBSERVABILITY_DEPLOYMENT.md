# A2A MCP Framework V2.0 - Observability Deployment Guide

This guide covers deploying and configuring the comprehensive observability stack for the A2A MCP Framework V2.0, including OpenTelemetry, Prometheus, Grafana, and structured logging.

## Table of Contents
- [Overview](#overview)
- [Quick Start](#quick-start)
- [Components](#components)
- [Deployment Options](#deployment-options)
- [Configuration](#configuration)
- [Monitoring Dashboard](#monitoring-dashboard)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Overview

The A2A MCP Framework V2.0 includes enterprise-grade observability features:

- **Distributed Tracing**: OpenTelemetry integration for end-to-end request tracing
- **Metrics Collection**: Prometheus metrics for performance monitoring
- **Structured Logging**: JSON-formatted logs with trace correlation
- **Real-time Dashboards**: Pre-built Grafana dashboards
- **Alerting**: Configurable alerts for critical conditions

## Quick Start

### 1. Install Dependencies

```bash
# Core observability dependencies
pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation
pip install opentelemetry-exporter-otlp
pip install prometheus-client

# Optional: Additional instrumentations
pip install opentelemetry-instrumentation-logging
pip install opentelemetry-instrumentation-aiohttp
pip install opentelemetry-instrumentation-asyncio
```

### 2. Deploy Observability Stack (Docker Compose)

Create `docker-compose.observability.yml`:

```yaml
version: '3.8'

services:
  # OpenTelemetry Collector
  otel-collector:
    image: otel/opentelemetry-collector:latest
    command: ["--config=/etc/otel-collector-config.yaml"]
    volumes:
      - ./configs/otel-collector-config.yaml:/etc/otel-collector-config.yaml
    ports:
      - "4317:4317"   # OTLP gRPC receiver
      - "4318:4318"   # OTLP HTTP receiver
      - "8888:8888"   # Prometheus metrics
    networks:
      - observability

  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./configs/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
    networks:
      - observability

  # Grafana
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana-data:/var/lib/grafana
      - ./src/a2a_mcp/common/dashboards:/var/lib/grafana/dashboards
      - ./configs/grafana-datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml
      - ./configs/grafana-dashboards.yml:/etc/grafana/provisioning/dashboards/dashboards.yml
    networks:
      - observability

  # Jaeger (Tracing UI)
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # Jaeger UI
      - "14268:14268"  # Jaeger collector
    environment:
      - COLLECTOR_OTLP_ENABLED=true
    networks:
      - observability

networks:
  observability:
    driver: bridge

volumes:
  prometheus-data:
  grafana-data:
```

### 3. Configure OpenTelemetry Collector

Create `configs/otel-collector-config.yaml`:

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
  memory_limiter:
    check_interval: 1s
    limit_percentage: 75
    spike_limit_percentage: 15

exporters:
  prometheus:
    endpoint: "0.0.0.0:8888"
    namespace: a2a_mcp
    
  jaeger:
    endpoint: jaeger:14250
    tls:
      insecure: true
      
  logging:
    loglevel: info

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [jaeger, logging]
      
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [prometheus]
```

### 4. Configure Prometheus

Create `configs/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: []

rule_files:
  - "alerts.yml"

scrape_configs:
  # Framework metrics
  - job_name: 'a2a-mcp-framework'
    static_configs:
      - targets: ['host.docker.internal:9090']
        
  # OpenTelemetry Collector metrics
  - job_name: 'otel-collector'
    static_configs:
      - targets: ['otel-collector:8888']
```

### 5. Start the Stack

```bash
# Start observability stack
docker-compose -f docker-compose.observability.yml up -d

# Check status
docker-compose -f docker-compose.observability.yml ps
```

### 6. Configure Framework

Set environment variables:

```bash
# OpenTelemetry
export OTEL_SERVICE_NAME=a2a-mcp-framework
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
export TRACING_ENABLED=true

# Prometheus
export METRICS_ENABLED=true
export METRICS_PORT=9090

# Logging
export JSON_LOGS=true
export LOG_LEVEL=INFO
```

## Components

### OpenTelemetry Integration

The framework uses OpenTelemetry for distributed tracing:

```python
from a2a_mcp.common.observability import trace_span, trace_async

# Trace a sync operation
with trace_span("operation_name", {"key": "value"}) as span:
    # Your code here
    span.set_attribute("result", "success")

# Trace an async operation
@trace_async("async_operation")
async def my_async_function():
    # Your code here
    pass
```

### Prometheus Metrics

Available metrics:

| Metric | Type | Description |
|--------|------|-------------|
| `orchestration_requests_total` | Counter | Total orchestration requests |
| `tasks_executed_total` | Counter | Total tasks executed |
| `errors_total` | Counter | Total errors by component |
| `orchestration_duration_seconds` | Histogram | Orchestration execution time |
| `task_duration_seconds` | Histogram | Individual task execution time |
| `active_sessions` | Gauge | Current active sessions |
| `workflow_nodes_active` | Gauge | Active workflow nodes by state |

### Structured Logging

The framework uses structured JSON logging:

```python
from a2a_mcp.common.observability import get_logger

logger = get_logger(__name__)

# Structured log with context
logger.info("Operation completed",
            session_id="123",
            duration=1.5,
            task_count=10)
```

## Deployment Options

### Kubernetes Deployment

For production Kubernetes deployments:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: a2a-observability-config
data:
  observability.yaml: |
    service:
      name: a2a-mcp-framework
      environment: production
    # ... rest of config

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: a2a-mcp-framework
spec:
  template:
    spec:
      containers:
      - name: framework
        env:
        - name: OTEL_SERVICE_NAME
          value: a2a-mcp-framework
        - name: OTEL_EXPORTER_OTLP_ENDPOINT
          value: http://otel-collector:4317
        volumeMounts:
        - name: config
          mountPath: /app/configs
      volumes:
      - name: config
        configMap:
          name: a2a-observability-config
```

### AWS Deployment

For AWS deployments using AWS Distro for OpenTelemetry:

```bash
# Install ADOT Collector
aws cloudformation create-stack \
  --stack-name ADOT-Collector \
  --template-body file://adot-collector-cfn.yaml \
  --parameters ParameterKey=IAMRole,ParameterValue=<YOUR_IAM_ROLE>
```

### Cloud Provider Integration

#### Google Cloud

```yaml
# Use Google Cloud Operations suite
exporters:
  googlecloud:
    project: your-project-id
    metric:
      prefix: a2a_mcp/
    trace:
      bundle_delay_threshold: 2s
```

#### Azure

```yaml
# Use Azure Monitor
exporters:
  azuremonitor:
    instrumentation_key: ${AZURE_INSTRUMENTATION_KEY}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TRACING_ENABLED` | Enable OpenTelemetry tracing | `true` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP endpoint | `localhost:4317` |
| `METRICS_ENABLED` | Enable Prometheus metrics | `true` |
| `METRICS_PORT` | Prometheus metrics port | `9090` |
| `JSON_LOGS` | Enable JSON structured logging | `true` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Advanced Configuration

For advanced configuration, modify `configs/observability.yaml`:

```yaml
# Custom sampling
tracing:
  sampling:
    type: trace_id_ratio
    ratio: 0.1  # Sample 10% of traces

# Custom metric buckets
metrics:
  histograms:
    custom_metric:
      buckets: [0.01, 0.05, 0.1, 0.5, 1.0]
```

## Monitoring Dashboard

### Accessing Grafana

1. Navigate to http://localhost:3000
2. Login with admin/admin
3. Go to Dashboards → A2A MCP Framework

### Dashboard Panels

The pre-built dashboard includes:

- **Orchestration Overview**: Request rate, success rate, latency
- **Task Performance**: Task execution metrics by specialist
- **Error Analysis**: Error rates by component and type
- **Resource Usage**: Active sessions, memory usage
- **Workflow Analysis**: Node states, execution flow

### Creating Custom Dashboards

Import the dashboard JSON:

```bash
curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @src/a2a_mcp/common/dashboards/a2a_mcp_monitoring.json
```

## Troubleshooting

### Common Issues

1. **No traces appearing in Jaeger**
   - Check OTLP endpoint connectivity
   - Verify TRACING_ENABLED=true
   - Check collector logs: `docker logs <collector-container>`

2. **Metrics not showing in Prometheus**
   - Verify metrics endpoint is accessible
   - Check Prometheus targets: http://localhost:9090/targets
   - Ensure METRICS_ENABLED=true

3. **High memory usage**
   - Adjust batch processor settings
   - Enable sampling for high-volume environments
   - Configure memory limits in collector

### Debug Commands

```bash
# Check OpenTelemetry Collector status
curl http://localhost:13133/

# Verify Prometheus scraping
curl http://localhost:9090/api/v1/targets

# Test OTLP connectivity
grpcurl -plaintext localhost:4317 list

# View structured logs
docker logs <framework-container> | jq .
```

## Best Practices

### 1. Sampling Strategy

For production environments, implement intelligent sampling:

```python
# In observability configuration
tracing:
  sampling:
    type: parent_based
    ratio: 0.1
    rules:
      - path: /health
        sample_rate: 0.01  # 1% for health checks
      - path: /api/orchestrate
        sample_rate: 0.5   # 50% for critical paths
```

### 2. Metric Cardinality

Avoid high-cardinality labels:

```python
# Bad: Creates too many time series
record_metric('requests_total', 1, {'user_id': user_id})

# Good: Use bounded labels
record_metric('requests_total', 1, {'user_type': get_user_type(user_id)})
```

### 3. Log Aggregation

For production, use log aggregation services:

```yaml
logging:
  outputs:
    - type: fluentd
      host: fluentd-aggregator
      port: 24224
      tag: a2a.mcp
```

### 4. Alert Fatigue

Configure meaningful alerts:

```yaml
alerts:
  - name: CriticalErrorRate
    expr: rate(errors_total{severity="critical"}[5m]) > 0.01
    for: 5m
    annotations:
      runbook_url: https://wiki/runbooks/critical-errors
```

### 5. Performance Impact

Monitor observability overhead:

```python
# Measure instrumentation overhead
from a2a_mcp.common.observability import measure_performance

@measure_performance("overhead_test")
def performance_critical_function():
    pass
```

## Security Considerations

1. **Secure OTLP Endpoints**
   ```yaml
   exporter:
     endpoint: otel-collector:4317
     tls:
       cert_file: /certs/client.crt
       key_file: /certs/client.key
   ```

2. **Sanitize Sensitive Data**
   ```python
   # Configure log sanitization
   logging:
     sanitize_fields:
       - password
       - api_key
       - token
   ```

3. **Access Control**
   - Use RBAC for Grafana dashboards
   - Implement authentication for metrics endpoints
   - Encrypt data in transit

## Next Steps

1. **Production Hardening**
   - Configure persistent storage for metrics
   - Set up backup and retention policies
   - Implement high availability for collectors

2. **Advanced Features**
   - Enable trace sampling rules
   - Configure custom exporters
   - Implement SLO monitoring

3. **Integration**
   - Connect to APM platforms
   - Set up incident management
   - Implement automated remediation

For more information, see:
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Grafana Documentation](https://grafana.com/docs/)