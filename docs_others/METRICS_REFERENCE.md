# A2A MCP Framework V2.0 - Metrics Reference Guide

This guide provides a comprehensive reference for all Prometheus metrics available in the A2A MCP Framework V2.0, including quality metrics, streaming metrics, and performance optimizations.

## 📚 V2.0 Reference Documentation
- [Framework Components Guide](../docs/FRAMEWORK_COMPONENTS_AND_ORCHESTRATION_GUIDE.md)
- [Multi-Agent Workflow Guide](../docs/MULTI_AGENT_WORKFLOW_GUIDE.md)

## Table of Contents
- [Overview](#overview)
- [Metric Types](#metric-types)
- [V2.0 Quality Metrics](#v20-quality-metrics)
- [Orchestration Metrics](#orchestration-metrics)
- [Task Execution Metrics](#task-execution-metrics)
- [System Metrics](#system-metrics)
- [V2.0 Streaming Metrics](#v20-streaming-metrics)
- [V2.0 Connection Pool Metrics](#v20-connection-pool-metrics)
- [Error Metrics](#error-metrics)
- [V2.0 Observability Metrics](#v20-observability-metrics)
- [Best Practices](#best-practices)

## Overview

All metrics follow Prometheus naming conventions and include appropriate labels for filtering and aggregation. Metrics are automatically collected when `METRICS_ENABLED=true` in your environment configuration.

## Metric Types

- **Counter**: Cumulative metric that only increases (e.g., total requests)
- **Gauge**: Metric that can go up or down (e.g., active sessions)
- **Histogram**: Samples observations and counts them in buckets (e.g., request duration)
- **Summary**: Similar to histogram but calculates quantiles (V2.0 quality scores)

## V2.0 Quality Metrics

### agent_quality_score
**Type**: Gauge  
**Description**: Current quality score for each agent (0.0-1.0)  
**Labels**:
- `agent_name`: Name of the agent
- `quality_domain`: Quality domain (ANALYTICAL, CREATIVE, CODING, COMMUNICATION)
- `agent_type`: Type (StandardizedAgentBase, GenericDomainAgent)

**Example Query**:
```promql
# Average quality score by domain
avg by (quality_domain) (agent_quality_score)

# Agents below quality threshold
agent_quality_score < 0.85
```

### quality_validation_total
**Type**: Counter  
**Description**: Total quality validations performed  
**Labels**:
- `domain`: Quality domain
- `validation_type`: Type of validation (input, output, streaming)
- `status`: Validation result (passed, failed, degraded)

### quality_validation_duration_seconds
**Type**: Histogram  
**Description**: Time taken for quality validation  
**Labels**:
- `domain`: Quality domain
- `validation_type`: Type of validation

**Buckets**: 0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25 seconds

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
- `orchestrator_version`: Version ("v1", "v2_enhanced")

**Buckets**: 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0 seconds

### phase7_streaming_latency_seconds
**Type**: Histogram  
**Description**: PHASE 7 streaming event latency  
**Labels**:
- `event_type`: Type of streaming event
- `phase`: Processing phase (1-7)

**Buckets**: 0.001, 0.005, 0.01, 0.025, 0.05, 0.1 seconds

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

## V2.0 Streaming Metrics

### streaming_sessions_active
**Type**: Gauge  
**Description**: Number of active V2.0 streaming sessions  
**Labels**:
- `stream_type`: Type ("phase7", "artifact", "quality_updates")

### streaming_events_total
**Type**: Counter  
**Description**: Total V2.0 streaming events emitted  
**Labels**:
- `event_type`: Type of event ("progress", "artifact", "task_update", "workflow_state", "quality_score", "phase_transition")
- `phase`: PHASE number (1-7)

### streaming_duration_seconds
**Type**: Histogram  
**Description**: Duration of V2.0 streaming sessions  
**Labels**:
- `type`: Stream type ("artifact_streaming", "workflow_streaming", "phase7_streaming")

**Buckets**: 0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0 seconds

### streaming_events_per_second
**Type**: Gauge  
**Description**: Current rate of streaming events  
**Labels**:
- `stream_id`: Stream identifier

## V2.0 Connection Pool Metrics

### connection_pool_size
**Type**: Gauge  
**Description**: Current size of connection pool  
**Labels**:
- `pool_name`: Name of the pool
- `state`: Connection state ("active", "idle", "stale")

### connection_pool_utilization
**Type**: Gauge  
**Description**: Connection pool utilization percentage  
**Labels**:
- `pool_name`: Name of the pool

### connection_reuse_total
**Type**: Counter  
**Description**: Number of times connections were reused  
**Labels**:
- `pool_name`: Name of the pool
- `protocol`: Protocol ("http1", "http2")

### connection_acquisition_duration_seconds
**Type**: Histogram  
**Description**: Time to acquire connection from pool  
**Labels**:
- `pool_name`: Name of the pool

**Buckets**: 0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1 seconds

## Error Metrics

### errors_total
**Type**: Counter  
**Description**: Total errors encountered  
**Labels**:
- `component`: Component where error occurred (e.g., "orchestration_execution", "task_coordination", "artifact_collection", "quality_validation")
- `error_type`: Error class name (e.g., "ValueError", "TimeoutError", "ConnectionError", "QualityValidationError")
- `severity`: Error severity ("critical", "error", "warning")
- `recovery_attempted`: Whether recovery was attempted ("true", "false")

## V2.0 Observability Metrics

### trace_export_total
**Type**: Counter  
**Description**: Total traces exported  
**Labels**:
- `exporter`: Exporter type ("otlp", "jaeger", "zipkin")
- `status`: Export status ("success", "failed")

### trace_export_duration_seconds
**Type**: Histogram  
**Description**: Time taken to export traces  
**Labels**:
- `exporter`: Exporter type

### span_duration_seconds
**Type**: Histogram  
**Description**: Duration of trace spans  
**Labels**:
- `span_name`: Name of the span
- `span_kind`: Kind of span ("client", "server", "internal")

### metrics_export_total
**Type**: Counter  
**Description**: Total metrics exported  
**Labels**:
- `exporter`: Exporter type
- `status`: Export status

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
record_metric('tasks_executed_total', 1, {
    'specialist': agent_type, 
    'status': 'completed',
    'quality_domain': 'ANALYTICAL'
})

# Bad: Unbounded label values
record_metric('tasks_executed_total', 1, {'user_id': user_id})  # Don't use unique IDs
record_metric('tasks_executed_total', 1, {'trace_id': trace_id})  # Don't use trace IDs
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

### 4. V2.0 Useful Queries

**V2.0 System Health Overview**:
```promql
# Overall success rate with quality
sum(rate(orchestration_requests_total{status="success", orchestrator_version="v2_enhanced"}[5m])) / 
sum(rate(orchestration_requests_total{orchestrator_version="v2_enhanced"}[5m]))

# Average quality-weighted response time
(rate(orchestration_duration_seconds_sum[5m]) / rate(orchestration_duration_seconds_count[5m])) * 
avg(agent_quality_score)

# V2.0 Error rate with recovery
sum(rate(errors_total{recovery_attempted="false"}[5m]))

# Connection pool efficiency
avg(connection_pool_utilization) * avg(connection_reuse_total[5m])
```

**V2.0 Quality Monitoring**:
```promql
# Quality degradation detection
rate(quality_validation_total{status="degraded"}[5m]) > 0.01

# Average quality by domain
avg by (quality_domain) (agent_quality_score)

# Quality validation performance
histogram_quantile(0.95, rate(quality_validation_duration_seconds_bucket[5m]))
```

**V2.0 Streaming Performance**:
```promql
# PHASE 7 streaming latency (p99)
histogram_quantile(0.99, rate(phase7_streaming_latency_seconds_bucket[5m]))

# Streaming event rate
sum(rate(streaming_events_total{phase="7"}[5m]))

# Active streaming sessions by type
sum by (stream_type) (streaming_sessions_active)
```

**Capacity Planning**:
```promql
# Peak concurrent sessions
max_over_time(active_sessions[7d])

# Task throughput capacity
sum(rate(tasks_executed_total[5m])) * 60
```

**V2.0 Performance Analysis**:
```promql
# V1 vs V2 performance comparison
histogram_quantile(0.5, rate(orchestration_duration_seconds_bucket{orchestrator_version="v2_enhanced"}[5m])) /
histogram_quantile(0.5, rate(orchestration_duration_seconds_bucket{orchestrator_version="v1"}[5m]))

# Connection pooling impact
avg(connection_acquisition_duration_seconds) * rate(connection_reuse_total[5m])

# Quality-adjusted performance
histogram_quantile(0.95, rate(orchestration_duration_seconds_bucket[5m])) * 
(1 - avg(agent_quality_score))

# Parallel workflow efficiency
sum(rate(tasks_executed_total{specialist=~".*parallel.*"}[5m])) /
sum(rate(orchestration_duration_seconds_count[5m]))
```

### 5. Integration with Grafana

Import the pre-built dashboard from `src/a2a_mcp/common/dashboards/a2a_mcp_monitoring.json` for instant visibility into all metrics.

### 6. V2.0 Custom Metrics

To add custom metrics in V2.0 agents:

```python
from a2a_mcp.common.observability import record_metric, create_histogram
from a2a_mcp.common.quality_framework import QualityDomain

# V2.0 StandardizedAgentBase automatically records quality metrics
class MyV2Agent(StandardizedAgentBase):
    def __init__(self):
        super().__init__(
            agent_name="My V2 Agent",
            quality_config={
                "domain": QualityDomain.ANALYTICAL,
                "thresholds": {"accuracy": 0.95}
            }
        )
    
    async def process(self, input_data):
        # Quality validation is automatic
        with self.observe_operation("custom_processing"):
            # Your logic here
            result = await self.do_processing(input_data)
            
            # Custom metric with quality context
            record_metric('custom_operations_total', 1, {
                'operation': 'process',
                'quality_domain': self.quality_domain.value,
                'quality_score': str(self.current_quality_score)
            })
            
            return result
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
      
  - alert: V2QualityDegradation
    expr: |
      avg(agent_quality_score) < 0.85
    for: 10m
    labels:
      severity: critical
    annotations:
      summary: "V2.0 Agent quality below threshold"
      
  - alert: ConnectionPoolExhaustion
    expr: |
      avg(connection_pool_utilization) > 0.9
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Connection pool near capacity"
      
  - alert: StreamingLatencyHigh
    expr: |
      histogram_quantile(0.99, rate(phase7_streaming_latency_seconds_bucket[5m])) > 0.1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "PHASE 7 streaming latency exceeds 100ms"
```

## V2.0 Dashboard Templates

Import pre-built V2.0 dashboards:
- `src/a2a_mcp/common/dashboards/v2_quality_monitoring.json` - Quality metrics dashboard
- `src/a2a_mcp/common/dashboards/v2_streaming_performance.json` - PHASE 7 streaming metrics
- `src/a2a_mcp/common/dashboards/v2_connection_pooling.json` - Connection pool analytics
- `src/a2a_mcp/common/dashboards/v2_system_overview.json` - Complete V2.0 overview

## Related Documentation
- [Framework Components Guide](../docs/FRAMEWORK_COMPONENTS_AND_ORCHESTRATION_GUIDE.md)
- [Multi-Agent Workflow Guide](../docs/MULTI_AGENT_WORKFLOW_GUIDE.md)
- [Observability Deployment Guide](OBSERVABILITY_DEPLOYMENT.md)
- [Architecture Documentation](../docs/ARCHITECTURE.md)
- [Developer Guide](../docs/DEVELOPER_GUIDE.md)