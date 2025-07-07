#!/usr/bin/env python3
"""Test Oracle with AI education query to verify web citations appear."""

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

async def test_ai_education_oracle():
    """Test Oracle with AI education query that should get web citations."""
    print("🧪 TESTING ORACLE WITH AI EDUCATION QUERY")
    print("=" * 60)
    
    try:
        from a2a_mcp.agents.nexus_oracle_agent import NexusOracleAgent
        
        oracle = NexusOracleAgent()
        print(f"✅ Oracle initialized: {oracle.agent_name}")
        
        # Test AI education query
        query = "How can AI improve education quality in India?"
        print(f"🧠 Test Query: {query}")
        
        # Load research context and external references
        await oracle.load_research_context(query)
        
        # Check external references
        if oracle.external_references.get('sources'):
            print(f"\n📚 EXTERNAL SOURCES FOUND:")
            total_papers = 0
            total_relevant = 0
            
            for source, data in oracle.external_references['sources'].items():
                papers = data.get('papers', [])
                total_papers += len(papers)
                
                relevant_papers = []
                for paper in papers:
                    if oracle._is_paper_relevant_to_query(paper, query.lower()):
                        relevant_papers.append(paper)
                        
                total_relevant += len(relevant_papers)
                
                print(f"   📖 {source.upper()}: {len(papers)} total, {len(relevant_papers)} relevant")
                
                # Show first few relevant papers
                for i, paper in enumerate(relevant_papers[:2], 1):
                    title = paper.get('title', 'No title')[:50]
                    domain = paper.get('domain', 'Unknown')
                    year = paper.get('year', 'Unknown')
                    print(f"      {i}. {title}... ({domain}, {year})")
            
            print(f"\n📊 SUMMARY: {total_relevant} relevant papers from {total_papers} total")
            
            # Format references to see what Oracle will use
            formatted_refs = oracle._format_external_references()
            print(f"\n📝 FORMATTED REFERENCES:")
            print("-" * 50)
            print(formatted_refs[:1000] + "..." if len(formatted_refs) > 1000 else formatted_refs)
            print("-" * 50)
            
            if total_relevant > 0:
                print("✅ This query should produce web citations in Oracle output!")
            else:
                print("❌ No relevant papers found - need to improve relevance filtering")
        else:
            print("❌ No external references loaded")
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ai_education_oracle())