#!/usr/bin/env python3
"""Test Oracle with a query that should find relevant ArXiv papers."""

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

async def test_domain_with_likely_citations():
    """Test with queries likely to find relevant ArXiv papers."""
    print("🧪 TESTING ORACLE WITH DOMAIN-SPECIFIC QUERIES")
    print("=" * 60)
    
    try:
        from a2a_mcp.agents.nexus_oracle_agent import NexusOracleAgent
        
        oracle = NexusOracleAgent()
        
        # Test with machine learning query (more likely to find relevant ArXiv papers)
        test_query = "How can neural networks improve image recognition accuracy?"
        print(f"🧠 Test Query: {test_query}")
        
        # Load research context
        await oracle.load_research_context(test_query)
        
        # Check what external references were found
        if oracle.external_references.get('sources'):
            total_papers = 0
            relevant_papers = 0
            
            for source, data in oracle.external_references['sources'].items():
                papers = data.get('papers', [])
                total_papers += len(papers)
                
                print(f"\n📚 {source.upper()}: {len(papers)} papers found")
                
                # Check relevance of first few papers
                for i, paper in enumerate(papers[:3], 1):
                    title = paper.get('title', 'No title')
                    is_relevant = oracle._is_paper_relevant_to_query(paper, test_query.lower())
                    if is_relevant:
                        relevant_papers += 1
                    print(f"   {i}. {title[:60]}...")
                    print(f"      Relevant to query: {is_relevant}")
            
            print(f"\n📊 SUMMARY:")
            print(f"   Total papers found: {total_papers}")
            print(f"   Relevant papers: {relevant_papers}")
            
            # Format external references to see what would be passed to AI
            formatted_refs = oracle._format_external_references()
            print(f"\n📝 Formatted References Preview:")
            print("-" * 50)
            print(formatted_refs[:800] + "..." if len(formatted_refs) > 800 else formatted_refs)
            print("-" * 50)
            
            if relevant_papers > 0:
                print("✅ This query should produce citations in the Oracle output")
            else:
                print("❌ No relevant papers found - Oracle should not include citations")
        else:
            print("❌ No external references found")
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_domain_with_likely_citations())