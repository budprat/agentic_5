#!/usr/bin/env python3
"""Test First Principles Oracle with web citations."""

import asyncio
import sys
import os

# Set up environment
sys.path.insert(0, './src')
sys.path.insert(0, '.')

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

async def test_oracle_web_citations():
    """Test Oracle with query that should get web citations."""
    print("🚀 TESTING FIRST PRINCIPLES ORACLE WITH WEB CITATIONS")
    print("=" * 60)
    
    try:
        from a2a_mcp.agents.nexus_oracle_agent import NexusOracleAgent
        
        # Test with an AI education query in non-interactive mode
        oracle = NexusOracleAgent()
        
        query = "How can AI improve education quality in India?"
        session_id = "test_web_citations_session"
        task_id = "test_web_citations_task"
        
        print(f"🧠 Query: {query}")
        print(f"🔍 Testing Oracle analysis with web search integration...")
        
        responses = []
        async for response in oracle.stream(query, session_id, task_id):
            responses.append(response)
            content = response.get('content', '')
            
            if not response.get('is_task_complete'):
                print(f"⚡ {content}")
            else:
                print(f"\n🎯 ORACLE ANALYSIS COMPLETE!")
                print("=" * 50)
                
                if response.get('response_type') == 'data':
                    analysis_result = response.get('content', {})
                    synthesis = analysis_result.get('synthesis', {})
                    
                    # Show executive summary
                    executive_summary = synthesis.get('executive_summary', '')
                    print(f"📋 EXECUTIVE SUMMARY:")
                    print(f"   {executive_summary}")
                    
                    # Check for citations
                    has_brackets = '[' in executive_summary and ']' in executive_summary
                    print(f"\n🔍 CITATION CHECK:")
                    print(f"   Contains citation brackets: {has_brackets}")
                    
                    if has_brackets:
                        print("✅ SUCCESS: Web citations are appearing in Oracle output!")
                        
                        # Extract potential citations
                        import re
                        citations = re.findall(r'\[([^\]]+)\]', executive_summary)
                        if citations:
                            print(f"   Found citations: {citations}")
                    else:
                        print("❌ No citations found in executive summary")
                        print("💡 This might indicate the AI model needs stronger citation instructions")
                    
                    # Show any key insights with citations
                    key_insights = synthesis.get('key_insights', [])
                    if key_insights:
                        print(f"\n📚 KEY INSIGHTS ({len(key_insights)} found):")
                        for i, insight in enumerate(key_insights[:3], 1):
                            insight_text = insight.get('insight', 'N/A') if isinstance(insight, dict) else str(insight)
                            has_citation = '[' in insight_text and ']' in insight_text
                            print(f"   {i}. {insight_text[:100]}... {'[✅ Has citation]' if has_citation else '[❌ No citation]'}")
                
                break
        
        print(f"\n📊 Total responses: {len(responses)}")
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_oracle_web_citations())