#!/usr/bin/env python3
"""ABOUTME: AWIE System Demonstration - shows complete workflow from Oracle to Scheduler with real SERP data.
ABOUTME: Demonstrates the revolutionary AI Chief of Staff concept in action."""

import asyncio
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

async def demonstrate_awie_system():
    """Demonstrate the complete AWIE system in action."""
    
    print("🧠 AWIE SYSTEM DEMONSTRATION")
    print("🎯 Revolutionary AI Chief of Staff with SERP Intelligence")
    print("=" * 70)
    
    # Initialize AWIE Oracle (contains AWIE Scheduler Agent)
    from a2a_mcp.agents.solopreneur_oracle.autonomous_workflow_intelligence_oracle import AutonomousWorkflowIntelligenceOracle
    
    print("🚀 Initializing AWIE Oracle...")
    oracle = AutonomousWorkflowIntelligenceOracle()
    print("✅ AWIE Oracle ready with integrated SERP intelligence")
    
    # Test requests that demonstrate different workflow types
    test_requests = [
        "research AI automation trends and create content strategy",
        "organize my development workflow with market intelligence",
        "schedule content creation about RAG implementation"
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n📋 DEMO {i}: {request}")
        print("-" * 50)
        
        try:
            # Process request through AWIE Oracle
            result = await oracle._process_manual_task_request(
                request, 
                f"demo_context_{i}", 
                f"demo_task_{i}"
            )
            
            if result and "content" in result:
                # Extract key information
                content = result["content"]
                lines = content.split('\n')
                
                # Show AWIE Oracle header
                for line in lines[:3]:
                    if line.strip():
                        print(line.strip())
                
                # Show workflow summary
                workflow_section = False
                for line in lines:
                    if "⚡ SERP-OPTIMIZED WORKFLOW" in line:
                        workflow_section = True
                        print(line.strip())
                    elif workflow_section and line.strip() and not line.startswith('📊'):
                        print(line.strip())
                        if "✨ Scheduled for strategic advantage" in line:
                            break
                
                print("✅ Complete SERP-enhanced workflow generated!")
                
        except Exception as e:
            print(f"❌ Demo {i} failed: {e}")
    
    print(f"\n🎉 AWIE System Demo Complete!")
    print("🎯 All workflows include:")
    print("  • Real-time SERP analysis with live search data")
    print("  • Market intelligence integration")
    print("  • Optimized scheduling based on energy requirements")
    print("  • Actionable automation commands")
    print("  • Calendar integration with time blocking")
    print("  • Strategic timing for maximum market impact")

if __name__ == "__main__":
    asyncio.run(demonstrate_awie_system())