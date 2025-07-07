#!/usr/bin/env python3
"""Realistic user scenario testing for Nexus Oracle Agent."""

import os
import sys
import asyncio
import json
from datetime import datetime

# Set up environment
sys.path.insert(0, './src')
sys.path.insert(0, '.')
os.environ['GOOGLE_API_KEY'] = os.environ.get('GOOGLE_API_KEY', 'your-api-key-here')

class RealisticUserScenario:
    """Simulates a realistic user research session with the Nexus Oracle."""
    
    def __init__(self, user_name: str, research_domain: str):
        self.user_name = user_name
        self.research_domain = research_domain
        self.oracle = None
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.conversation_history = []
        
    async def initialize_session(self):
        """Start a new research session with the Oracle."""
        from a2a_mcp.agents.nexus_oracle_agent import NexusOracleAgent
        self.oracle = NexusOracleAgent()
        
        print(f"🔬 NEW RESEARCH SESSION")
        print("=" * 50)
        print(f"👤 Researcher: {self.user_name}")
        print(f"🎯 Domain: {self.research_domain}")
        print(f"🆔 Session: {self.session_id}")
        print(f"🤖 Oracle: {self.oracle.agent_name}")
        print(f"📊 Quality Thresholds: {self.oracle.quality_thresholds}")
        print("=" * 50)
        
    async def ask_oracle(self, question: str, show_details: bool = True):
        """Ask the Oracle a research question."""
        task_id = f"task_{len(self.conversation_history) + 1:03d}"
        
        print(f"\n👤 {self.user_name}: {question}")
        print("─" * 60)
        
        if show_details:
            print(f"🔍 Oracle analyzing... (Task: {task_id})")
        
        responses = []
        key_insights = []
        start_time = datetime.now()
        
        try:
            async for response in self.oracle.stream(question, self.session_id, task_id):
                responses.append(response)
                content = response.get('content', '')
                
                if not response.get('is_task_complete'):
                    if show_details:
                        print(f"⚡ {content}")
                else:
                    # Process final result
                    print(f"\n🎯 ORACLE RESPONSE:")
                    
                    if response.get('response_type') == 'data':
                        analysis = response.get('content', {})
                        insight = await self.extract_key_insights(analysis)
                        key_insights.append(insight)
                        
                        print(f"📝 {insight['summary']}")
                        
                        if show_details:
                            print(f"\n📊 Analysis Details:")
                            print(f"   Confidence: {insight['confidence']}")
                            print(f"   Domains: {insight['domains']}")
                            print(f"   Quality: {insight['quality']}")
                            
                            if insight['hypotheses']:
                                print(f"   💡 Key Hypothesis: {insight['hypotheses'][0][:80]}...")
                    else:
                        summary = content[:150] + "..." if len(content) > 150 else content
                        key_insights.append({"summary": summary, "confidence": "N/A"})
                        print(f"📝 {summary}")
                    break
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
        
        # Record conversation
        duration = (datetime.now() - start_time).total_seconds()
        conversation_entry = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "task_id": task_id,
            "duration": duration,
            "responses": len(responses),
            "insights": key_insights[0] if key_insights else None
        }
        self.conversation_history.append(conversation_entry)
        
        if show_details:
            print(f"\n📈 Duration: {duration:.1f}s | Responses: {len(responses)}")
        
        return key_insights[0] if key_insights else None
        
    async def extract_key_insights(self, analysis: dict):
        """Extract key insights from Oracle analysis."""
        synthesis = analysis.get('synthesis', {})
        quality_validation = analysis.get('quality_validation', {})
        research_intelligence = analysis.get('research_intelligence', {})
        
        return {
            "summary": synthesis.get('executive_summary', 'No summary available'),
            "confidence": synthesis.get('research_confidence', 'N/A'),
            "domains": synthesis.get('domain_coverage', 0),
            "quality": quality_validation.get('confidence_score', 'N/A'),
            "patterns": len(synthesis.get('cross_domain_patterns', {}).get('convergent_findings', [])),
            "hypotheses": [h.get('hypothesis', '') for h in synthesis.get('novel_hypotheses', [])],
            "recommendations": synthesis.get('research_recommendations', {})
        }
    
    async def print_session_summary(self):
        """Print a summary of the research session."""
        print(f"\n📋 SESSION SUMMARY")
        print("=" * 40)
        print(f"👤 Researcher: {self.user_name}")
        print(f"🔬 Domain: {self.research_domain}")
        print(f"🆔 Session: {self.session_id}")
        print(f"❓ Questions Asked: {len(self.conversation_history)}")
        
        total_duration = sum(entry['duration'] for entry in self.conversation_history)
        total_responses = sum(entry['responses'] for entry in self.conversation_history)
        
        print(f"⏱️  Total Time: {total_duration:.1f}s")
        print(f"🔄 Total Responses: {total_responses}")
        
        # Oracle state
        print(f"\n🧠 ORACLE STATE:")
        print(f"   Query History: {len(self.oracle.query_history)}")
        print(f"   Research Cache: {len(self.oracle.research_intelligence)} domains")
        print(f"   Session Context: {self.oracle.context_id}")
        
        # Conversation highlights
        if self.conversation_history:
            print(f"\n💡 KEY INSIGHTS:")
            for i, entry in enumerate(self.conversation_history, 1):
                if entry['insights']:
                    insight = entry['insights']
                    print(f"   {i}. {insight['summary'][:60]}... (Conf: {insight['confidence']})")

async def run_realistic_scenario():
    """Run a realistic research scenario."""
    print("🎭 NEXUS ORACLE REALISTIC USER SCENARIO")
    print("=" * 70)
    
    # Scenario: PhD Student researching AI Ethics
    researcher = RealisticUserScenario(
        user_name="Dr. Sarah Chen",
        research_domain="AI Ethics & Policy"
    )
    
    await researcher.initialize_session()
    
    # Research conversation flow
    print(f"\n📚 RESEARCH CONVERSATION:")
    
    # Question 1: Initial broad research question
    await researcher.ask_oracle(
        "What are the main ethical challenges in deploying large language models in healthcare applications?",
        show_details=True
    )
    
    # Question 2: Follow-up on specific aspect
    await researcher.ask_oracle(
        "How can we ensure patient privacy when using AI for medical diagnosis?",
        show_details=False
    )
    
    # Question 3: Policy implications
    await researcher.ask_oracle(
        "What regulatory frameworks are needed for responsible AI deployment in clinical settings?",
        show_details=False
    )
    
    # Session summary
    await researcher.print_session_summary()
    
    print(f"\n✅ REALISTIC SCENARIO COMPLETE!")
    print("   The Oracle successfully supported a complex research conversation")
    print("   Demonstrating practical utility for real researchers")

if __name__ == "__main__":
    print("🚀 Starting Realistic User Scenario Test...")
    asyncio.run(run_realistic_scenario())