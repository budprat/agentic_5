#!/usr/bin/env python3
"""Run First Principles Oracle with AI education query in non-interactive mode."""

import asyncio
import sys
import os

# Set up environment
sys.path.insert(0, './src')
sys.path.insert(0, '.')

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️  python-dotenv not available, using system environment variables")

class AIEducationOracle:
    """Oracle specifically for AI education testing."""
    
    def __init__(self):
        self.oracle = None
        
    async def initialize(self):
        """Initialize the Oracle."""
        try:
            from a2a_mcp.agents.nexus_oracle_agent import NexusOracleAgent
            self.oracle = NexusOracleAgent()
            print(f"✅ Oracle initialized: {self.oracle.agent_name}")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize Oracle: {e}")
            return False
    
    async def run_ai_education_analysis(self):
        """Run AI education analysis and check for web citations."""
        if not await self.initialize():
            return
            
        query = "How can AI improve education quality in India?"
        session_id = "ai_education_test"
        task_id = "ai_education_task"
        
        print(f"\n🧠 ANALYZING: {query}")
        print("=" * 60)
        
        try:
            responses = []
            async for response in self.oracle.stream(query, session_id, task_id):
                responses.append(response)
                content = response.get('content', '')
                
                if not response.get('is_task_complete'):
                    print(f"⚡ {content}")
                else:
                    print(f"\n🎯 ORACLE ANALYSIS COMPLETE!")
                    print("=" * 50)
                    
                    if response.get('response_type') == 'data':
                        analysis_result = response.get('content', {})
                        await self.display_analysis_with_citations(analysis_result, query)
                    break
            
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            import traceback
            traceback.print_exc()
    
    async def display_analysis_with_citations(self, analysis: dict, query: str):
        """Display analysis results and check for citations."""
        synthesis = analysis.get('synthesis', {})
        
        # Executive Summary
        executive_summary = synthesis.get('executive_summary', '')
        print(f"📋 EXECUTIVE SUMMARY:")
        print(f"   {executive_summary}")
        
        # Citation Analysis
        has_citations = '[' in executive_summary and ']' in executive_summary
        print(f"\n🔍 CITATION ANALYSIS:")
        print(f"   ✅ Contains citations: {has_citations}")
        
        if has_citations:
            import re
            citations = re.findall(r'\[([^\]]+)\]', executive_summary)
            print(f"   📚 Citations found: {citations}")
            
            # Check if citations include web sources
            web_citations = [c for c in citations if any(domain in c.lower() for domain in ['unesco', 'org', 'edu', 'gov'])]
            if web_citations:
                print(f"   🌐 Web citations: {web_citations}")
                print("✅ SUCCESS: Web sources are being cited!")
            else:
                print("⚠️  No recognizable web sources in citations")
        else:
            print("❌ No citations found in executive summary")
        
        # Key Insights
        key_insights = synthesis.get('key_insights', [])
        print(f"\n📚 KEY INSIGHTS ({len(key_insights)} found):")
        citation_count = 0
        for i, insight in enumerate(key_insights[:3], 1):
            insight_text = insight.get('insight', 'N/A') if isinstance(insight, dict) else str(insight)
            has_citation = '[' in insight_text and ']' in insight_text
            if has_citation:
                citation_count += 1
            print(f"   {i}. {insight_text[:80]}... {'[✅]' if has_citation else '[❌]'}")
        
        print(f"\n📊 FINAL CITATION METRICS:")
        print(f"   Executive Summary Citations: {'✅' if has_citations else '❌'}")
        print(f"   Key Insights Citations: {citation_count}/{len(key_insights)}")
        
        # Show external references that were loaded
        external_refs = analysis.get('research_context', {}).get('external_references', {})
        if external_refs.get('sources'):
            print(f"\n📖 EXTERNAL SOURCES LOADED:")
            for source, data in external_refs['sources'].items():
                papers = data.get('papers', [])
                print(f"   {source}: {len(papers)} papers")

if __name__ == "__main__":
    print("🚀 Starting AI Education Oracle Test...")
    oracle = AIEducationOracle()
    asyncio.run(oracle.run_ai_education_analysis())