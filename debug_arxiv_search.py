#!/usr/bin/env python3
"""Debug ArXiv search to see what queries are being used."""

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

async def debug_arxiv_search():
    """Debug what ArXiv queries are actually being sent."""
    print("🔍 DEBUGGING ARXIV SEARCH QUERIES")
    print("=" * 50)
    
    try:
        from a2a_mcp.common.reference_intelligence import ReferenceIntelligenceService
        
        # Initialize service
        service = ReferenceIntelligenceService()
        
        # Test different queries
        test_cases = [
            ("How can neural networks improve image recognition accuracy?", "computer_science"),
            ("How can AI improve education quality in India?", "social_sciences"),
            ("How can quantum computing solve climate change challenges?", "physical_sciences"),
        ]
        
        for query, domain in test_cases:
            print(f"\n📋 Testing: '{query}'")
            print(f"🏷️  Domain: {domain}")
            
            # Get enhanced query
            enhanced_query = service._enhance_query_for_arxiv_domain(query, domain)
            print(f"🔍 Enhanced ArXiv Query: {enhanced_query}")
            
            # Try direct ArXiv search to see what we get
            try:
                result = await service._search_arxiv(query, domain)
                
                papers = result.get('papers', [])
                query_used = result.get('query_used', 'Unknown')
                
                print(f"📊 Results: {len(papers)} papers found")
                print(f"🔎 Query actually used: {query_used}")
                
                # Show first few paper titles
                for i, paper in enumerate(papers[:3], 1):
                    title = paper.get('title', 'No title')[:60]
                    print(f"   {i}. {title}...")
                    
            except Exception as e:
                print(f"❌ Search error: {e}")
            
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ Debug error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_arxiv_search())