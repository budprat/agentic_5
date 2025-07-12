#!/usr/bin/env python3
# ABOUTME: Demonstrates Prometheus metrics collection in Framework V2.0
# ABOUTME: Shows metrics collection, aggregation, and export capabilities

import asyncio
import time
import random
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from a2a_mcp.common import (
    MetricsCollector,
    get_metrics_collector,
    record_agent_request,
    record_a2a_message,
    get_metrics_summary,
    StandardizedAgentBase
)

# Simulate agent activity
AGENT_NAMES = ["orchestrator", "analyzer", "processor", "validator"]
A2A_ROUTES = [
    ("orchestrator", "analyzer"),
    ("orchestrator", "processor"),
    ("analyzer", "validator"),
    ("processor", "validator")
]


async def simulate_agent_activity(duration: int = 30):
    """Simulate agent requests and A2A communication."""
    print(f"\n=== Simulating Agent Activity for {duration} seconds ===")
    
    metrics = get_metrics_collector()
    start_time = time.time()
    
    while time.time() - start_time < duration:
        # Simulate agent request
        agent = random.choice(AGENT_NAMES)
        request_duration = random.uniform(0.1, 2.0)
        success = random.random() > 0.1  # 90% success rate
        
        # Track with context manager
        try:
            async with metrics.track_agent_request(agent):
                await asyncio.sleep(request_duration)
                if not success:
                    raise Exception("Simulated error")
        except:
            pass  # Error already tracked
        
        # Simulate A2A message
        if random.random() > 0.5:  # 50% chance
            source, target = random.choice(A2A_ROUTES)
            latency = random.uniform(0.01, 0.5)
            a2a_success = random.random() > 0.05  # 95% success rate
            
            record_a2a_message(
                source,
                target,
                "success" if a2a_success else "error",
                latency
            )
        
        # Simulate quality validation
        if random.random() > 0.7:  # 30% chance
            domain = random.choice(["BUSINESS", "SERVICE", "ACADEMIC"])
            passed = random.random() > 0.2  # 80% pass rate
            scores = {
                "accuracy": random.uniform(0.7, 1.0),
                "completeness": random.uniform(0.6, 1.0),
                "relevance": random.uniform(0.8, 1.0)
            }
            metrics.record_quality_validation(domain, "passed" if passed else "failed", scores)
        
        # Update connection pool metrics
        if random.random() > 0.8:  # 20% chance
            active = random.randint(1, 10)
            created = random.randint(10, 50)
            reused = random.randint(20, 100)
            metrics.update_connection_pool_metrics(
                active=active,
                created=created,
                reused=reused
            )
        
        # Small delay
        await asyncio.sleep(0.1)
    
    print(f"✓ Activity simulation complete")


def display_metrics_summary():
    """Display comprehensive metrics summary."""
    print("\n=== Metrics Summary ===")
    
    summary = get_metrics_summary()
    
    # System metrics
    print(f"\nSystem Metrics:")
    print(f"  Uptime: {summary['uptime_human']}")
    print(f"  Prometheus Available: {summary['prometheus_available']}")
    
    # Agent metrics
    print(f"\nAgent Performance:")
    for agent, stats in summary['agent_metrics'].items():
        print(f"\n  {agent}:")
        print(f"    Total Requests: {stats['total_requests']}")
        print(f"    Error Rate: {stats['error_rate']:.2%}")
        print(f"    Avg Duration: {stats['average_duration_seconds']:.3f}s")
    
    # A2A metrics
    print(f"\nA2A Communication:")
    for route, stats in summary['a2a_metrics'].items():
        print(f"\n  {route}:")
        print(f"    Total Messages: {stats['total_messages']}")
        print(f"    Error Rate: {stats['error_rate']:.2%}")
        print(f"    Avg Latency: {stats['average_latency_seconds']:.3f}s")
    
    # Connection pool metrics
    pool = summary['connection_pool']
    print(f"\nConnection Pool:")
    print(f"  Active Connections: {pool['active_connections']}")
    print(f"  Total Created: {pool['total_created']}")
    print(f"  Total Reused: {pool['total_reused']}")
    print(f"  Reuse Rate: {pool['reuse_rate']:.2%}")
    
    # Quality metrics
    print(f"\nQuality Validation:")
    for domain_metric, stats in summary['quality_metrics'].items():
        print(f"\n  {domain_metric}:")
        print(f"    Average Score: {stats['average_score']:.3f}")
        print(f"    Min/Max: {stats['min_score']:.3f} / {stats['max_score']:.3f}")
        print(f"    Validations: {stats['validation_count']}")


async def demonstrate_prometheus_export():
    """Demonstrate Prometheus metrics export."""
    print("\n=== Prometheus Export Demo ===")
    
    metrics = get_metrics_collector()
    
    # Check if Prometheus is available
    try:
        from prometheus_client import REGISTRY
        print("✓ Prometheus client is available")
        
        # Export metrics
        prometheus_data = metrics.export_prometheus()
        print(f"\nPrometheus Export ({len(prometheus_data)} bytes):")
        print("-" * 50)
        
        # Show first few lines
        lines = prometheus_data.decode('utf-8').split('\n')
        for line in lines[:20]:
            if line and not line.startswith('#'):
                print(line)
        
        if len(lines) > 20:
            print(f"... ({len(lines) - 20} more lines)")
        
    except ImportError:
        print("✗ Prometheus client not installed")
        print("  Install with: pip install prometheus-client")


async def demonstrate_metrics_server():
    """Demonstrate starting Prometheus metrics HTTP server."""
    print("\n=== Metrics Server Demo ===")
    
    metrics = get_metrics_collector()
    
    try:
        # Try to start server (will fail if prometheus_client not installed)
        await metrics.start_metrics_server(port=9091)
        print("✓ Metrics server would be available at http://localhost:9091")
        print("  (Server not actually started in demo mode)")
    except:
        print("✗ Cannot start metrics server without prometheus_client")


def demonstrate_custom_metrics():
    """Demonstrate custom metric collection patterns."""
    print("\n=== Custom Metrics Patterns ===")
    
    # Pattern 1: Direct metric recording
    print("\n1. Direct Recording:")
    record_agent_request("custom_agent", "success", 1.5)
    record_a2a_message("agent_a", "agent_b", "success", 0.05)
    print("   ✓ Metrics recorded")
    
    # Pattern 2: Context manager for timing
    print("\n2. Context Manager Pattern:")
    metrics = get_metrics_collector()
    
    async def timed_operation():
        async with metrics.track_agent_request("timed_agent"):
            await asyncio.sleep(0.5)
            print("   ✓ Operation completed and timed")
    
    asyncio.run(timed_operation())
    
    # Pattern 3: Batch metrics update
    print("\n3. Batch Update Pattern:")
    metrics.update_connection_pool_metrics(
        pool_name="custom_pool",
        active=5,
        created=20,
        reused=80
    )
    print("   ✓ Pool metrics updated")


async def main():
    """Run metrics demonstration."""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║           Prometheus Metrics Collection Demo                  ║
    ╚══════════════════════════════════════════════════════════════╝
    
    This demo shows Framework V2.0's metrics collection capabilities
    including agent performance, A2A communication, and quality metrics.
    """)
    
    # Initialize metrics collector
    metrics = MetricsCollector(
        namespace="a2a_mcp_demo",
        subsystem="framework",
        enable_system_metrics=True
    )
    
    # Simulate activity
    await simulate_agent_activity(duration=10)
    
    # Display summary
    display_metrics_summary()
    
    # Demonstrate Prometheus export
    await demonstrate_prometheus_export()
    
    # Demonstrate metrics server
    await demonstrate_metrics_server()
    
    # Demonstrate custom patterns
    demonstrate_custom_metrics()
    
    print("\n" + "="*60)
    print("Metrics Collection Benefits:")
    print("1. Real-time performance monitoring")
    print("2. Quality validation tracking")
    print("3. A2A communication analysis")
    print("4. Connection pool optimization")
    print("5. Prometheus integration (optional)")
    print("6. Minimal overhead design")
    print("="*60)
    
    print("\nMetrics Integration Points:")
    print("- StandardizedAgentBase: Automatic request tracking")
    print("- A2AProtocolClient: Communication latency metrics")
    print("- QualityFramework: Validation score tracking")
    print("- ConnectionPool: Resource utilization metrics")


if __name__ == "__main__":
    asyncio.run(main())