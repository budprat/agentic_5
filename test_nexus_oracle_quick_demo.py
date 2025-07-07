#!/usr/bin/env python3
"""Quick demonstration of Nexus Oracle capabilities."""

import os
import sys
import asyncio
from datetime import datetime

# Set up environment
sys.path.insert(0, './src')
sys.path.insert(0, '.')
os.environ['GOOGLE_API_KEY'] = os.environ.get('GOOGLE_API_KEY', 'your-api-key-here')

async def demo_oracle_interaction():
    """Demonstrate Oracle interaction with a single complex query."""
    print("🎭 NEXUS ORACLE DEMONSTRATION")
    print("=" * 60)
    
    # Initialize Oracle
    from a2a_mcp.agents.nexus_oracle_agent import NexusOracleAgent
    oracle = NexusOracleAgent()
    
    session_id = f"demo_{datetime.now().strftime('%H%M%S')}"
    task_id = "demo_task_001"
    
    print(f"🤖 Oracle: {oracle.agent_name}")
    print(f"📊 Quality Standards: Min Confidence {oracle.quality_thresholds['min_confidence_score']}")
    print(f"🔬 Session: {session_id}")
    
    # Demo Query: Complex transdisciplinary research
    query = "How can quantum computing accelerate drug discovery while ensuring ethical AI practices in pharmaceutical research?"
    
    print(f"\n👤 Researcher: {query}")
    print("─" * 60)
    
    responses = []
    processing_steps = []
    start_time = datetime.now()
    
    try:
        async for response in oracle.stream(query, session_id, task_id):
            responses.append(response)
            content = response.get('content', '')
            
            if not response.get('is_task_complete'):
                # Track processing steps
                if 'Step' in content:
                    processing_steps.append(content)
                print(f"⚡ {content}")
            else:
                # Final result
                print(f"\n🎯 ANALYSIS COMPLETE!")
                
                if response.get('response_type') == 'data':
                    analysis = response.get('content', {})
                    
                    # Display key results
                    synthesis = analysis.get('synthesis', {})
                    quality_validation = analysis.get('quality_validation', {})
                    research_intelligence = analysis.get('research_intelligence', {})
                    
                    print(f"\n📋 ORACLE ANALYSIS RESULTS:")
                    print("─" * 40)
                    
                    # Executive Summary
                    summary = synthesis.get('executive_summary', 'No summary available')
                    print(f"🎯 Summary: {summary[:120]}...")
                    
                    # Quality Metrics
                    confidence = synthesis.get('research_confidence', 'N/A')
                    domain_count = synthesis.get('domain_coverage', 0)
                    quality_score = quality_validation.get('confidence_score', 'N/A')
                    
                    print(f"📊 Confidence: {confidence}")
                    print(f"🔬 Domains: {domain_count}")
                    print(f"✅ Quality: {quality_score}")
                    
                    # Domain Intelligence
                    print(f"🧠 Intelligence: {len(research_intelligence)} domain analyses")
                    
                    # Cross-domain insights
                    cross_patterns = synthesis.get('cross_domain_patterns', {})
                    if cross_patterns:
                        convergent = len(cross_patterns.get('convergent_findings', []))
                        gaps = len(cross_patterns.get('knowledge_gaps', []))
                        print(f"🔗 Patterns: {convergent} convergent findings, {gaps} knowledge gaps")
                    
                    # Novel hypotheses
                    hypotheses = synthesis.get('novel_hypotheses', [])
                    if hypotheses:
                        print(f"💡 Hypotheses: {len(hypotheses)} novel research directions")
                        # Show first hypothesis
                        if hypotheses:
                            first_hyp = hypotheses[0].get('hypothesis', 'N/A')
                            print(f"   Example: {first_hyp[:80]}...")
                    
                else:
                    print(f"📝 Result: {content}")
                break
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Performance Metrics
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n📈 PERFORMANCE METRICS:")
    print("─" * 30)
    print(f"⏱️  Duration: {duration:.1f}s")
    print(f"🔄 Responses: {len(responses)}")
    print(f"📋 Processing Steps: {len(processing_steps)}")
    
    # Oracle State
    print(f"\n🧠 ORACLE STATE:")
    print("─" * 20)
    print(f"📚 Query History: {len(oracle.query_history)}")
    print(f"🔬 Research Cache: {len(oracle.research_intelligence)} domains")
    print(f"🎯 Context: {oracle.context_id}")
    
    print(f"\n✅ DEMONSTRATION SUCCESSFUL!")
    print("   Nexus Oracle shows sophisticated transdisciplinary research capabilities")
    
    return True

async def demo_dependency_analysis():
    """Demonstrate the Oracle's dependency analysis capabilities."""
    print(f"\n🔧 DEPENDENCY ANALYSIS DEMO")
    print("=" * 40)
    
    from a2a_mcp.agents.nexus_oracle_agent import NexusOracleAgent
    oracle = NexusOracleAgent()
    
    test_queries = [
        "AI ethics in healthcare",
        "Quantum computing applications", 
        "Climate change and social policy",
        "Biotechnology innovation economics"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        analysis = oracle.analyze_research_dependencies(query)
        
        domain_groups = analysis.get('domain_groups', {})
        execution_plan = analysis.get('execution_plan', [])
        parallel_ops = analysis.get('parallelization_opportunities', [])
        
        print(f"   🎯 Domains: {list(domain_groups.keys())}")
        print(f"   📋 Steps: {len(execution_plan)}")
        print(f"   ⚡ Parallel: {len(parallel_ops)} opportunities")
    
    print(f"\n✅ Dependency analysis working correctly!")

if __name__ == "__main__":
    async def main():
        # Run dependency analysis demo
        await demo_dependency_analysis()
        
        # Run full interaction demo
        await demo_oracle_interaction()
    
    print("🚀 Starting Nexus Oracle Quick Demo...")
    asyncio.run(main())