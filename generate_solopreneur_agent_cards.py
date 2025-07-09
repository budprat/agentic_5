"""Generate all 56 agent cards for the Solopreneur Oracle system."""

import json
import os
from pathlib import Path

# Import the agent registry
import sys
sys.path.append('/home/solopreneur/src')
from a2a_mcp.agents.solopreneur_oracle.agent_registry import SOLOPRENEUR_AGENTS

# Create directories
os.makedirs("agent_cards/tier1", exist_ok=True)
os.makedirs("agent_cards/tier2", exist_ok=True)
os.makedirs("agent_cards/tier3", exist_ok=True)

# Agent card template
def create_agent_card(name, config):
    """Create agent card following framework pattern."""
    port = config["port"]
    tier = config["tier"]
    
    card = {
        "name": name,
        "description": config.get("description", f"{name} - Tier {tier} agent"),
        "url": f"http://localhost:{port}/",
        "provider": None,
        "version": "1.0.0",
        "documentationUrl": None,
        "capabilities": {
            "streaming": "True",
            "pushNotifications": "True",
            "stateTransitionHistory": str(tier == 1)  # Only master has history
        },
        "auth_required": True,
        "auth_schemes": [
            {
                "type": "bearer",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            },
            {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key"
            }
        ],
        "authentication": {
            "credentials": None,
            "schemes": ["bearer", "apiKey"]
        },
        "defaultInputModes": ["text", "text/plain"],
        "defaultOutputModes": ["text", "text/plain", "application/json"],
        "skills": [{
            "id": name.lower().replace(" ", "_"),
            "name": name,
            "description": config.get("description", f"{name} capabilities"),
            "tags": [f"tier{tier}", "solopreneur", "oracle"],
            "examples": get_agent_examples(name, tier),
            "inputModes": None,
            "outputModes": None
        }]
    }
    
    # Add tier-specific metadata
    if tier == 1:
        card["skills"][0]["tags"].extend(["orchestrator", "master"])
    elif tier == 2:
        card["skills"][0]["tags"].extend(["domain-specialist", "coordinator"])
    else:
        card["skills"][0]["tags"].extend(["intelligence-module", "analyzer"])
    
    # Determine subdirectory
    if tier == 1:
        subdir = "tier1"
    elif tier == 2:
        subdir = "tier2"
    else:
        subdir = "tier3"
    
    # Save agent card
    filename = f"agent_cards/{subdir}/{name.lower().replace(' ', '_')}.json"
    with open(filename, 'w') as f:
        json.dump(card, f, indent=4)
    
    print(f"Created: {filename}")
    return filename

def get_agent_examples(name, tier):
    """Get example queries for each agent."""
    if tier == 1:
        return [
            "Analyze the feasibility of implementing a new AI feature with LangGraph",
            "Optimize my daily schedule for deep work and learning new frameworks",
            "Create a comprehensive learning plan for mastering transformer architectures"
        ]
    elif tier == 2:
        if "Technical" in name:
            return [
                "Monitor latest developments in transformer architectures",
                "Analyze emerging trends in MLOps and model deployment",
                "Evaluate the architecture of my current project"
            ]
        elif "Personal" in name:
            return [
                "Optimize my daily schedule based on energy patterns",
                "Identify my peak performance windows for coding",
                "Create a recovery plan to prevent burnout"
            ]
        elif "Knowledge" in name:
            return [
                "Build a knowledge graph of AI concepts I'm learning",
                "Find connections between different ML frameworks",
                "Identify knowledge gaps in my understanding"
            ]
        elif "Learning" in name:
            return [
                "Create a learning path for Rust programming",
                "Design a spaced repetition schedule for ML concepts",
                "Track my progress in learning new technologies"
            ]
        elif "Integration" in name:
            return [
                "Find synergies between my technical and personal goals",
                "Optimize workflows across different tools",
                "Identify cross-domain opportunities"
            ]
    else:  # Tier 3
        if "Research" in name:
            return ["Analyze recent papers on attention mechanisms"]
        elif "Energy" in name:
            return ["Analyze my energy patterns over the last week"]
        elif "Architecture" in name:
            return ["Evaluate the scalability of my microservices design"]
        else:
            return [f"Perform specialized analysis in {name.lower()}"]

# Generate all 56 agent cards
created_files = []
tier_counts = {1: 0, 2: 0, 3: 0}

for agent_name, config in SOLOPRENEUR_AGENTS.items():
    filename = create_agent_card(agent_name, config)
    created_files.append(filename)
    tier_counts[config["tier"]] += 1

# Create a summary file
summary = {
    "total_agents": len(SOLOPRENEUR_AGENTS),
    "tier_1_agents": tier_counts[1],
    "tier_2_agents": tier_counts[2],
    "tier_3_agents": tier_counts[3],
    "agent_files": created_files,
    "port_range": {
        "tier_1": "10901",
        "tier_2": "10902-10906",
        "tier_3": "10910-10959"
    }
}

with open("agent_cards/summary.json", 'w') as f:
    json.dump(summary, f, indent=4)

print(f"\n✅ Generated all {len(SOLOPRENEUR_AGENTS)} agent cards!")
print(f"   Tier 1: {tier_counts[1]} agents")
print(f"   Tier 2: {tier_counts[2]} agents")
print(f"   Tier 3: {tier_counts[3]} agents")
print(f"\nSummary saved to: agent_cards/summary.json")