#!/usr/bin/env python3
"""User interaction simulation for Nexus Oracle Agent."""

import os
import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime

# Set up environment
sys.path.insert(0, './src')
sys.path.insert(0, '.')
os.environ['GOOGLE_API_KEY'] = os.environ.get('GOOGLE_API_KEY', 'your-api-key-here')

class OracleUserSimulation:
    """Simulates realistic user interactions with the Nexus Oracle."""
    
    def __init__(self):
        self.oracle = None
        self.session_id = f"sim_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.interaction_count = 0
        
    async def initialize_oracle(self):
        """Initialize the Nexus Oracle agent."""
        from a2a_mcp.agents.nexus_oracle_agent import NexusOracleAgent
        self.oracle = NexusOracleAgent()
        print(f"🤖 Nexus Oracle initialized for session: {self.session_id}")
        print(f"📊 Quality Standards: {self.oracle.quality_thresholds}")
        print("=" * 80)
        
    async def simulate_research_query(self, query: str, user_profile: str = "Researcher"):
        """Simulate a user research query with the Oracle."""
        self.interaction_count += 1
        task_id = f"task_{self.interaction_count:03d}"
        
        print(f"\n👤 {user_profile}: {query}")
        print("─" * 60)
        print(f"🔍 Oracle Processing (Task {task_id})...")
        
        # Track response metrics
        responses = []
        start_time = datetime.now()
        
        try:
            async for response in self.oracle.stream(query, self.session_id, task_id):
                responses.append(response)
                content = response.get('content', '')
                
                # Show processing updates
                if not response.get('is_task_complete'):
                    print(f"⚡ {content}")
                else:
                    # Final analysis result
                    print(f"\n🎯 Final Analysis Complete!")
                    
                    if response.get('response_type') == 'data':
                        analysis = response.get('content', {})
                        await self.display_analysis_results(analysis, user_profile)
                    else:
                        print(f"📝 Result: {content}")
                    break
                    
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            return False
            
        # Show interaction metrics
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"\n📈 Interaction Metrics:")
        print(f"   Duration: {duration:.2f} seconds")
        print(f"   Response chunks: {len(responses)}")
        print(f"   Session: {self.session_id}")
        
        return True
        
    async def display_analysis_results(self, analysis: dict, user_profile: str):
        """Display the Oracle's analysis results in a user-friendly format."""
        print(f"\n📊 NEXUS ORACLE ANALYSIS FOR {user_profile.upper()}")
        print("=" * 70)
        
        if isinstance(analysis, dict):
            # Extract synthesis information
            synthesis = analysis.get('synthesis', {})
            quality_validation = analysis.get('quality_validation', {})
            research_intelligence = analysis.get('research_intelligence', {})
            research_context = analysis.get('research_context', {})
            
            # Executive Summary
            if synthesis.get('executive_summary'):
                print(f"🎯 Executive Summary:")
                print(f"   {synthesis['executive_summary']}")
            
            # Quality Metrics
            print(f"\n📏 Quality Assessment:")
            confidence = synthesis.get('research_confidence', 'N/A')
            domain_coverage = synthesis.get('domain_coverage', 'N/A')
            print(f"   Research Confidence: {confidence}")
            print(f"   Domain Coverage: {domain_coverage} disciplines")
            
            quality_score = quality_validation.get('confidence_score', 'N/A')
            print(f"   Quality Score: {quality_score}")
            
            # Domain Analysis
            if research_intelligence:
                print(f"\n🧬 Domain Intelligence ({len(research_intelligence)} domains analyzed):")
                for domain, data in research_intelligence.items():
                    insights = data.get('insights', [])
                    evidence_quality = data.get('evidence_quality', 'N/A')
                    print(f"   📚 {domain.replace('_', ' ').title()}: {len(insights)} insights (Evidence: {evidence_quality})")
            
            # Cross-Domain Patterns
            cross_patterns = synthesis.get('cross_domain_patterns', {})
            if cross_patterns:
                print(f"\n🔗 Cross-Domain Insights:")
                convergent = cross_patterns.get('convergent_findings', [])
                gaps = cross_patterns.get('knowledge_gaps', [])
                print(f"   Convergent Findings: {len(convergent)}")
                print(f"   Knowledge Gaps: {len(gaps)}")
                
                # Show first convergent finding if available
                if convergent:
                    print(f"   Key Finding: {convergent[0][:100]}...")
            
            # Novel Hypotheses
            hypotheses = synthesis.get('novel_hypotheses', [])
            if hypotheses:
                print(f"\n💡 Novel Research Hypotheses ({len(hypotheses)} generated):")
                for i, hypothesis in enumerate(hypotheses[:3], 1):
                    hyp_text = hypothesis.get('hypothesis', 'N/A')
                    confidence = hypothesis.get('confidence', 'N/A')
                    print(f"   {i}. {hyp_text[:80]}... (Confidence: {confidence})")
            
            # Research Recommendations
            recommendations = synthesis.get('research_recommendations', {})
            if recommendations:
                print(f"\n🎯 Research Recommendations:")
                priority_areas = recommendations.get('priority_research_areas', [])
                methodologies = recommendations.get('recommended_methodologies', [])
                if priority_areas:
                    print(f"   Priority Areas: {', '.join(priority_areas[:3])}")
                if methodologies:
                    print(f"   Methodologies: {', '.join(methodologies[:3])}")
        else:
            print(f"📝 Analysis Result: {analysis}")
    
    async def simulate_follow_up_interaction(self, follow_up: str, user_profile: str):
        """Simulate a follow-up question in the same session."""
        print(f"\n💬 Follow-up Question:")
        return await self.simulate_research_query(follow_up, user_profile)
        
    async def run_comprehensive_simulation(self):
        """Run a comprehensive user simulation with multiple scenarios."""
        print("🚀 NEXUS ORACLE USER INTERACTION SIMULATION")
        print("=" * 80)
        
        await self.initialize_oracle()
        
        # Scenario 1: Climate Tech Researcher
        print(f"\n📋 SCENARIO 1: Climate Technology Research")
        success1 = await self.simulate_research_query(
            "How can machine learning accelerate carbon capture technology development and what are the socioeconomic implications?",
            "Climate Tech Researcher"
        )
        
        if success1:
            await self.simulate_follow_up_interaction(
                "What are the main ethical considerations for deploying AI-driven carbon capture at scale?",
                "Climate Tech Researcher"
            )
        
        # Scenario 2: Healthcare AI Researcher  
        print(f"\n📋 SCENARIO 2: Healthcare AI Ethics")
        success2 = await self.simulate_research_query(
            "Analyze the intersection of AI bias in medical diagnostics and health equity across different demographic groups",
            "Healthcare AI Researcher"
        )
        
        if success2:
            await self.simulate_follow_up_interaction(
                "What regulatory frameworks are needed to ensure fair AI deployment in healthcare?",
                "Healthcare AI Researcher"
            )
        
        # Scenario 3: Innovation Policy Analyst
        print(f"\n📋 SCENARIO 3: Innovation Policy Analysis")
        success3 = await self.simulate_research_query(
            "What are the economic and social factors driving successful technology adoption in emerging markets?",
            "Innovation Policy Analyst"
        )
        
        # Scenario 4: Complex Multi-domain Query
        print(f"\n📋 SCENARIO 4: Complex Transdisciplinary Analysis")
        success4 = await self.simulate_research_query(
            "Examine the psychological, technological, and economic factors influencing remote work productivity in the post-pandemic era",
            "Organizational Psychologist"
        )
        
        # Simulation Summary
        successful_interactions = sum([success1, success2, success3, success4])
        print(f"\n📊 SIMULATION SUMMARY")
        print("=" * 50)
        print(f"✅ Successful Interactions: {successful_interactions}/4")
        print(f"🔄 Total Interactions: {self.interaction_count}")
        print(f"🎯 Session ID: {self.session_id}")
        print(f"🤖 Oracle Status: {'Operational' if successful_interactions > 0 else 'Issues Detected'}")
        
        # Test Oracle's state persistence
        print(f"\n🧠 Oracle Memory Test:")
        print(f"   Query History: {len(self.oracle.query_history)} queries stored")
        print(f"   Research Intelligence: {len(self.oracle.research_intelligence)} domains cached")
        print(f"   Context ID: {self.oracle.context_id}")
        
        return successful_interactions >= 3

async def main():
    """Run the user simulation."""
    simulation = OracleUserSimulation()
    
    try:
        success = await simulation.run_comprehensive_simulation()
        
        if success:
            print(f"\n🎉 SIMULATION SUCCESSFUL!")
            print("   Nexus Oracle demonstrates robust transdisciplinary research capabilities")
            print("   Ready for production deployment with real users")
        else:
            print(f"\n⚠️  SIMULATION ISSUES DETECTED")
            print("   Review Oracle performance and address any failing scenarios")
            
    except Exception as e:
        print(f"\n❌ SIMULATION FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 Starting Nexus Oracle User Interaction Simulation...")
    asyncio.run(main())