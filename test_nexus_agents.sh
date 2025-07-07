#!/bin/bash
# test_nexus_agents.sh - Comprehensive testing for Nexus system

echo "Testing Nexus Transdisciplinary Research Synthesis System..."

# Test MCP Server connectivity
echo "Testing MCP Server connectivity..."
curl -f http://localhost:10100/health || {
    echo "MCP Server not responding"
    exit 1
}

# Test Nexus Orchestrator Agent
echo "Testing Nexus Orchestrator..."
curl -X POST http://localhost:11001/test \
  -H "Content-Type: application/json" \
  -d '{"query": "Analyze the intersection of AI ethics research across philosophy, computer science, and policy domains"}' || {
    echo "Nexus Orchestrator test failed"
    exit 1
}

# Test Nexus Planner Agent
echo "Testing Nexus Planner..."
curl -X POST http://localhost:11002/test \
  -H "Content-Type: application/json" \
  -d '{"query": "Plan a comprehensive analysis of climate change impacts spanning environmental science, economics, and social studies"}' || {
    echo "Nexus Planner test failed"
    exit 1
}

# Test Disciplinary Domain Supervisors
echo "Testing Domain Supervisors..."
supervisors=(11003 11004 11005 11006 11007 11013 11019 11020)
supervisor_names=("Life Sciences" "Social Sciences" "Economics & Policy" "Physical Sciences" "Computer Science" "Psychology" "Cross-Domain Analysis" "Visualization & Synthesis")

for i in "${!supervisors[@]}"; do
    port=${supervisors[$i]}
    name=${supervisor_names[$i]}
    echo "Testing $name Supervisor on port $port..."
    curl -f http://localhost:$port/health || {
        echo "$name Supervisor on port $port not responding"
        exit 1
    }
done

# Test specific cross-domain analysis capability
echo "Testing Cross-Domain Analysis capability..."
curl -X POST http://localhost:11019/test \
  -H "Content-Type: application/json" \
  -d '{"query": "Identify patterns between neuroscience research on decision-making and AI research on explainable AI"}' || {
    echo "Cross-Domain Analysis test failed"
    exit 1
}

# Test visualization capability
echo "Testing Visualization & Synthesis capability..."
curl -X POST http://localhost:11020/test \
  -H "Content-Type: application/json" \
  -d '{"query": "Create a knowledge graph visualization for the relationship between climate science and economic policy research"}' || {
    echo "Visualization & Synthesis test failed"
    exit 1
}

echo "All Nexus agents tested successfully!"
echo "System ready for transdisciplinary research synthesis."