"""Generate all 56 agent cards for the Solopreneur Oracle system - standalone version."""

import json
import os

# Define the agents directly (matching the agent_registry.py)
SOLOPRENEUR_AGENTS = {
    # TIER 1: Oracle Master (1 agent)
    "SolopreneurOracle Master Agent": {
        "port": 10901,
        "tier": 1,
        "description": "Master AI orchestrator for developer/entrepreneur intelligence"
    },
    
    # TIER 2: Domain Specialists (5 agents)
    "Technical Intelligence Oracle": {
        "port": 10902,
        "tier": 2,
        "description": "Monitors AI research and technical developments"
    },
    "Knowledge Management Oracle": {
        "port": 10903,
        "tier": 2,
        "description": "Manages knowledge graph and information synthesis"
    },
    "Personal Optimization Oracle": {
        "port": 10904,
        "tier": 2,
        "description": "Optimizes energy, focus, and productivity"
    },
    "Learning Enhancement Oracle": {
        "port": 10905,
        "tier": 2,
        "description": "Enhances skill development and learning efficiency"
    },
    "Integration Synthesis Oracle": {
        "port": 10906,
        "tier": 2,
        "description": "Synthesizes cross-domain insights and workflows"
    },
    
    # TIER 3: Technical Intelligence Modules (10910-10919)
    "AI Research Analyzer": {"port": 10910, "tier": 3, "description": "Analyzes AI research papers and trends"},
    "Code Architecture Evaluator": {"port": 10911, "tier": 3, "description": "Evaluates code architecture and design patterns"},
    "Tech Stack Optimizer": {"port": 10912, "tier": 3, "description": "Optimizes technology stack selections"},
    "Implementation Risk Assessor": {"port": 10913, "tier": 3, "description": "Assesses implementation risks and mitigation strategies"},
    "Framework Compatibility Checker": {"port": 10914, "tier": 3, "description": "Checks framework compatibility and integration"},
    "Performance Bottleneck Detector": {"port": 10915, "tier": 3, "description": "Detects performance bottlenecks and optimization opportunities"},
    "Security Vulnerability Scanner": {"port": 10916, "tier": 3, "description": "Scans for security vulnerabilities and best practices"},
    "Technical Debt Analyzer": {"port": 10917, "tier": 3, "description": "Analyzes and prioritizes technical debt"},
    "API Design Reviewer": {"port": 10918, "tier": 3, "description": "Reviews API design and documentation"},
    "Algorithm Efficiency Optimizer": {"port": 10919, "tier": 3, "description": "Optimizes algorithm efficiency and complexity"},
    
    # Knowledge Systems (10920-10929)
    "Neo4j Graph Manager": {"port": 10920, "tier": 3, "description": "Manages Neo4j knowledge graph operations"},
    "Vector Database Interface": {"port": 10921, "tier": 3, "description": "Interfaces with vector databases for semantic search"},
    "Knowledge Correlator": {"port": 10922, "tier": 3, "description": "Correlates knowledge across different domains"},
    "Insight Synthesizer": {"port": 10923, "tier": 3, "description": "Synthesizes insights from multiple knowledge sources"},
    "Pattern Recognition Engine": {"port": 10924, "tier": 3, "description": "Identifies patterns in data and knowledge"},
    "Information Retrieval Optimizer": {"port": 10925, "tier": 3, "description": "Optimizes information retrieval strategies"},
    "Semantic Search Engine": {"port": 10926, "tier": 3, "description": "Performs semantic search across knowledge bases"},
    "Knowledge Gap Identifier": {"port": 10927, "tier": 3, "description": "Identifies gaps in knowledge coverage"},
    "Citation Network Analyzer": {"port": 10928, "tier": 3, "description": "Analyzes citation networks and research connections"},
    "Concept Map Builder": {"port": 10929, "tier": 3, "description": "Builds concept maps for knowledge visualization"},
    
    # Personal Systems (10930-10939)
    "Circadian Optimizer": {"port": 10930, "tier": 3, "description": "Optimizes schedules based on circadian rhythms"},
    "Focus State Monitor": {"port": 10931, "tier": 3, "description": "Monitors and optimizes focus states"},
    "Energy Pattern Analyzer": {"port": 10932, "tier": 3, "description": "Analyzes personal energy patterns"},
    "Cognitive Load Manager": {"port": 10933, "tier": 3, "description": "Manages cognitive load for optimal performance"},
    "Stress Detection System": {"port": 10934, "tier": 3, "description": "Detects stress patterns and triggers"},
    "Recovery Scheduler": {"port": 10935, "tier": 3, "description": "Schedules recovery periods for sustained performance"},
    "Environment Optimizer": {"port": 10936, "tier": 3, "description": "Optimizes work environment for productivity"},
    "Nutrition Timing Advisor": {"port": 10937, "tier": 3, "description": "Advises on nutrition timing for cognitive performance"},
    "Exercise Integration Planner": {"port": 10938, "tier": 3, "description": "Plans exercise integration for mental performance"},
    "Sleep Quality Analyzer": {"port": 10939, "tier": 3, "description": "Analyzes sleep quality impact on performance"},
    
    # Learning Systems (10940-10949)
    "Skill Gap Analyzer": {"port": 10940, "tier": 3, "description": "Analyzes skill gaps and learning needs"},
    "Learning Efficiency Optimizer": {"port": 10941, "tier": 3, "description": "Optimizes learning strategies for efficiency"},
    "Progress Tracker": {"port": 10942, "tier": 3, "description": "Tracks learning progress and milestones"},
    "Knowledge Retention Enhancer": {"port": 10943, "tier": 3, "description": "Enhances long-term knowledge retention"},
    "Spaced Repetition Scheduler": {"port": 10944, "tier": 3, "description": "Schedules spaced repetition for optimal retention"},
    "Learning Path Generator": {"port": 10945, "tier": 3, "description": "Generates personalized learning paths"},
    "Skill Transfer Identifier": {"port": 10946, "tier": 3, "description": "Identifies transferable skills across domains"},
    "Practice Session Designer": {"port": 10947, "tier": 3, "description": "Designs effective practice sessions"},
    "Competency Assessment Engine": {"port": 10948, "tier": 3, "description": "Assesses competency levels objectively"},
    "Learning Resource Curator": {"port": 10949, "tier": 3, "description": "Curates optimal learning resources"},
    
    # Integration Layer (10950-10959)
    "Cross-Domain Synthesizer": {"port": 10950, "tier": 3, "description": "Synthesizes insights across multiple domains"},
    "Workflow Coordinator": {"port": 10951, "tier": 3, "description": "Coordinates complex multi-step workflows"},
    "Quality Validator": {"port": 10952, "tier": 3, "description": "Validates quality of outputs and recommendations"},
    "Performance Monitor": {"port": 10953, "tier": 3, "description": "Monitors system and personal performance metrics"},
    "Risk Mitigation Planner": {"port": 10954, "tier": 3, "description": "Plans risk mitigation strategies"},
    "Opportunity Detector": {"port": 10955, "tier": 3, "description": "Detects opportunities across domains"},
    "Decision Support System": {"port": 10956, "tier": 3, "description": "Provides data-driven decision support"},
    "Priority Optimization Engine": {"port": 10957, "tier": 3, "description": "Optimizes task and goal prioritization"},
    "Context Awareness Manager": {"port": 10958, "tier": 3, "description": "Manages context across interactions"},
    "Predictive Analytics Engine": {"port": 10959, "tier": 3, "description": "Provides predictive analytics for planning"}
}

# Create directories
os.makedirs("agent_cards/tier1", exist_ok=True)
os.makedirs("agent_cards/tier2", exist_ok=True)
os.makedirs("agent_cards/tier3", exist_ok=True)

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
            "stateTransitionHistory": str(tier == 1)
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
            "inputModes": None,
            "outputModes": None
        }]
    }
    
    # Determine subdirectory
    subdir = f"tier{tier}"
    
    # Save agent card
    filename = f"agent_cards/{subdir}/{name.lower().replace(' ', '_')}.json"
    with open(filename, 'w') as f:
        json.dump(card, f, indent=4)
    
    print(f"Created: {filename}")
    return filename

# Generate all 56 agent cards
created_files = []
tier_counts = {1: 0, 2: 0, 3: 0}

for agent_name, config in SOLOPRENEUR_AGENTS.items():
    filename = create_agent_card(agent_name, config)
    created_files.append(filename)
    tier_counts[config["tier"]] += 1

print(f"\n✅ Generated all {len(SOLOPRENEUR_AGENTS)} agent cards!")
print(f"   Tier 1: {tier_counts[1]} agents")
print(f"   Tier 2: {tier_counts[2]} agents")
print(f"   Tier 3: {tier_counts[3]} agents")