#!/bin/bash
# Health check for all 56 agents

echo "🔍 Solopreneur Oracle System Status Check"
echo "========================================"

# Check MCP Server
echo -n "MCP Server (10100): "
if curl -s http://localhost:10100/health > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not responding"
fi

# Check Tier 1
echo ""
echo "TIER 1 - Oracle Master:"
echo -n "  SolopreneurOracle Master (10901): "
curl -s http://localhost:10901/health > /dev/null 2>&1 && echo "✅" || echo "❌"

# Check Tier 2
echo ""
echo "TIER 2 - Domain Specialists:"
tier2_running=0
for port in {10902..10906}; do
    echo -n "  Port $port: "
    if curl -s http://localhost:$port/health > /dev/null 2>&1; then
        echo "✅"
        ((tier2_running++))
    else
        echo "❌"
    fi
done

# Check Tier 3
echo ""
echo "TIER 3 - Intelligence Modules:"
tier3_running=0
total_tier3=50

# Quick check sample ports from each range
echo "  Checking Technical Intelligence (10910-10919)..."
for port in 10910 10915 10919; do
    curl -s http://localhost:$port/health > /dev/null 2>&1 && ((tier3_running++))
done

echo "  Checking Knowledge Systems (10920-10929)..."
for port in 10920 10925 10929; do
    curl -s http://localhost:$port/health > /dev/null 2>&1 && ((tier3_running++))
done

echo "  Checking Personal Systems (10930-10939)..."
for port in 10930 10935 10939; do
    curl -s http://localhost:$port/health > /dev/null 2>&1 && ((tier3_running++))
done

echo "  Checking Learning Systems (10940-10949)..."
for port in 10940 10945 10949; do
    curl -s http://localhost:$port/health > /dev/null 2>&1 && ((tier3_running++))
done

echo "  Checking Integration Layer (10950-10959)..."
for port in 10950 10955 10959; do
    curl -s http://localhost:$port/health > /dev/null 2>&1 && ((tier3_running++))
done

echo "  Sample check: $tier3_running / 15 sample ports responding"

# Summary
echo ""
echo "Summary:"
echo "========="
echo "Tier 1: 1 agent expected"
echo "Tier 2: $tier2_running / 5 agents running"
echo "Tier 3: Sampled $tier3_running / 15 ports"

# Check if any agents are actually running via process
if [ -f .agent_pids ]; then
    RUNNING_PIDS=$(cat .agent_pids | wc -l)
    echo ""
    echo "Process Check: $RUNNING_PIDS agent processes tracked"
fi

echo ""
if [ "$tier2_running" -eq 5 ]; then
    echo "Status: ✅ Core system operational!"
else
    echo "Status: ⚠️  Some agents not responding"
    echo "Check logs/ directory for details"
fi