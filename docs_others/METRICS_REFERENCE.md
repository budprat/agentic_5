# A2A MCP Framework - Metrics Reference Guide

This guide provides a comprehensive reference for all Prometheus metrics available in the A2A MCP Framework V2.0.

## Table of Contents
- [Overview](#overview)
- [Metric Types](#metric-types)
- [Orchestration Metrics](#orchestration-metrics)
- [Task Execution Metrics](#task-execution-metrics)
- [System Metrics](#system-metrics)
- [Streaming Metrics](#streaming-metrics)
- [Error Metrics](#error-metrics)
- [Best Practices](#best-practices)

## Overview

All metrics follow Prometheus naming conventions and include appropriate labels for filtering and aggregation. Metrics are automatically collected when `METRICS_ENABLED=true` in your environment configuration.

## Metric Types

- **Counter**: Cumulative metric that only increases (e.g., total requests)
- **Gauge**: Metric that can go up or down (e.g., active sessions)
- **Histogram**: Samples observations and counts them in buckets (e.g., request duration)

## Orchestration Metrics

### orchestration_requests_total
**Type**: Counter  
**Description**: Total number of orchestration requests received  
**Labels**:
- `domain`: The orchestrator domain (e.g., "finance", "research", "general")
- `status`: Request status ("success", "error", "timeout")

**Example Query**:
```promql
# Request rate by domain
rate(orchestration_requests_total[5m])

# Success rate
rate(orchestration_requests_total{status="success"}[5m]) / rate(orchestration_requests_total[5m])
```

### orchestration_duration_seconds
**Type**: Histogram  
**Description**: Time taken to complete orchestration requests  
**Labels**:
- `domain`: The orchestrator domain
- `strategy`: Coordination strategy used ("sequential", "parallel", "hybrid")

**Buckets**: 0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0 seconds

**Example Query**:
```promql
# 95th percentile latency by strategy
histogram_quantile(0.95, rate(orchestration_duration_seconds_bucket[5m]))

# Average orchestration time
rate(orchestration_duration_seconds_sum[5m]) / rate(orchestration_duration_seconds_count[5m])
```

## Task Execution Metrics

### tasks_executed_total
**Type**: Counter  
**Description**: Total number of tasks executed by specialists  
**Labels**:
- `specialist`: The specialist agent name
- `status`: Task completion status ("completed", "failed", "timeout")

**Example Query**:
```promql
# Task execution rate by specialist
rate(tasks_executed_total[5m])

# Failure rate by specialist
rate(tasks_executed_total{status="failed"}[5m])
```

### task_duration_seconds
**Type**: Histogram  
**Description**: Time taken to execute individual tasks  
**Labels**:
- `specialist`: The specialist agent name

**Buckets**: 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0 seconds

**Example Query**:
```promql
# Task execution time by specialist
histogram_quantile(0.5, rate(task_duration_seconds_bucket[5m]))
```

## System Metrics

### active_sessions
**Type**: Gauge  
**Description**: Current number of active orchestration sessions  
**Labels**: None

**Example Query**:
```promql
# Current active sessions
active_sessions

# Max sessions over time
max_over_time(active_sessions[1h])
```

### workflow_nodes_active
**Type**: Gauge  
**Description**: Number of active workflow nodes by state  
**Labels**:
- `state`: Node state ("pending", "executing", "completed", "failed")

**Example Query**:
```promql
# Workflow node distribution
workflow_nodes_active

# Pending vs executing ratio
workflow_nodes_active{state="pending"} / workflow_nodes_active{state="executing"}
```

### artifacts_created_total
**Type**: Counter  
**Description**: Total number of artifacts created  
**Labels**:
- `type`: Artifact type ("orchestration_results", "task_output", "streamed")
- `session`: Session identifier

**Example Query**:
```promql
# Artifact creation rate
rate(artifacts_created_total[5m])

# Artifacts by type
sum by (type) (rate(artifacts_created_total[5m]))
```

### artifact_size_bytes
**Type**: Histogram  
**Description**: Size of created artifacts in bytes  
**Labels**:
- `type`: Artifact type

**Buckets**: 100, 1000, 10000, 100000, 1000000, 10000000 bytes

**Example Query**:
```promql
# Average artifact size
rate(artifact_size_bytes_sum[5m]) / rate(artifact_size_bytes_count[5m])

# Large artifacts (>1MB)
histogram_quantile(0.95, rate(artifact_size_bytes_bucket[5m]))
```

## Streaming Metrics

### streaming_sessions_active
**Type**: Gauge  
**Description**: Number of active streaming sessions  
**Labels**: None

### streaming_events_total
**Type**: Counter  
**Description**: Total streaming events emitted  
**Labels**:
- `event_type`: Type of event ("progress", "artifact", "task_update", "workflow_state")

### streaming_duration_seconds
**Type**: Histogram  
**Description**: Duration of streaming sessions  
**Labels**:
- `type`: Stream type ("artifact_streaming", "workflow_streaming")

**Buckets**: 0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0 seconds

## Error Metrics

### errors_total
**Type**: Counter  
**Description**: Total errors encountered  
**Labels**:
- `component`: Component where error occurred (e.g., "orchestration_execution", "task_coordination", "artifact_collection")
- `error_type`: Error class name (e.g., "ValueError", "TimeoutError", "ConnectionError")

**Example Query**:
```promql
# Error rate by component
rate(errors_total[5m])

# Top error types
topk(5, sum by (error_type) (rate(errors_total[1h])))

# Alert on high error rate
rate(errors_total[5m]) > 0.1
```

## Best Practices

### 1. Label Cardinality
Keep label values bounded to prevent high cardinality:
```python
# Good: Bounded label values
record_metric('tasks_executed_total', 1, {'specialist': agent_type, 'status': 'completed'})

# Bad: Unbounded label values
record_metric('tasks_executed_total', 1, {'user_id': user_id})  # Don't use unique IDs
```

### 2. Metric Naming
Follow Prometheus naming conventions:
- Use `_total` suffix for counters
- Use `_seconds`, `_bytes` for units
- Use underscores, not camelCase

### 3. Histogram Buckets
Choose buckets that match your SLOs:
```yaml
# For APIs with 1s SLO
buckets: [0.05, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0]

# For batch jobs
buckets: [1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0]
```

### 4. Useful Queries

**System Health Overview**:
```promql
# Overall success rate
sum(rate(orchestration_requests_total{status="success"}[5m])) / sum(rate(orchestration_requests_total[5m]))

# Average response time
rate(orchestration_duration_seconds_sum[5m]) / rate(orchestration_duration_seconds_count[5m])

# Error rate
sum(rate(errors_total[5m]))
```

**Capacity Planning**:
```promql
# Peak concurrent sessions
max_over_time(active_sessions[7d])

# Task throughput capacity
sum(rate(tasks_executed_total[5m])) * 60
```

**Performance Analysis**:
```promql
# Slowest operations (p99)
histogram_quantile(0.99, rate(orchestration_duration_seconds_bucket[5m]))

# Compare sequential vs parallel performance
histogram_quantile(0.5, rate(orchestration_duration_seconds_bucket{strategy="sequential"}[5m])) /
histogram_quantile(0.5, rate(orchestration_duration_seconds_bucket{strategy="parallel"}[5m]))
```

### 5. Integration with Grafana

Import the pre-built dashboard from `src/a2a_mcp/common/dashboards/a2a_mcp_monitoring.json` for instant visibility into all metrics.

### 6. Custom Metrics

To add custom metrics in your agents:

```python
from a2a_mcp.common.observability import record_metric, create_histogram

# Create custom histogram
custom_histogram = create_histogram(
    'my_custom_operation_seconds',
    'Time for custom operation',
    buckets=[0.1, 0.5, 1.0, 5.0]
)

# Record metric
record_metric('my_custom_total', 1, {'operation': 'process'})
```

## Alerting Examples

Common alerts to configure in Prometheus:

```yaml
groups:
- name: a2a_mcp_alerts
  rules:
  - alert: HighErrorRate
    expr: rate(errors_total[5m]) > 0.1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High error rate detected"
      
  - alert: LowSuccessRate
    expr: |
      sum(rate(orchestration_requests_total{status="success"}[5m])) /
      sum(rate(orchestration_requests_total[5m])) < 0.9
    for: 10m
    labels:
      severity: critical
      
  - alert: HighOrchestrationLatency
    expr: |
      histogram_quantile(0.95, rate(orchestration_duration_seconds_bucket[5m])) > 30
    for: 5m
    labels:
      severity: warning
```

## Related Documentation
- [Observability Deployment Guide](OBSERVABILITY_DEPLOYMENT.md)
- [Architecture Documentation](ARCHITECTURE.md)
- [Developer Guide](DEVELOPER_GUIDE.md)