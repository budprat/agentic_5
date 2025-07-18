"""
ABOUTME: Demonstration of using ArXiv for research paper retrieval
ABOUTME: Shows how to use our enhanced Literature Review Agent with real ArXiv data
"""

import asyncio
import json
from datetime import datetime
import sys

# Add path for imports
sys.path.append('/Users/mac/Agents/agentic_5/src')

# Import our enhanced agents
from research_assistant_agent.sub_agents.literature_review_agent.a2a_enhanced_agent import (
    A2ALiteratureReviewAgent
)
from research_assistant_agent.a2a_enhanced_orchestrator import (
    A2AEnhancedOrchestrator
)


async def search_arxiv_papers(query: str, max_results: int = 10):
    """
    Search ArXiv for research papers using our enhanced Literature Review Agent.
    
    Args:
        query: Search query for ArXiv
        max_results: Maximum number of papers to retrieve
    """
    print(f"\n{'='*60}")
    print(f"ArXiv Research Paper Search")
    print(f"{'='*60}\n")
    
    # Initialize enhanced Literature Review Agent
    print("1. Initializing Enhanced Literature Review Agent...")
    agent = A2ALiteratureReviewAgent()
    print("   ✓ Agent ready with Citation Tracker")
    print("   ✓ ArXiv integration enabled")
    
    # Search ArXiv
    print(f"\n2. Searching ArXiv for: '{query}'")
    print(f"   Max results: {max_results}")
    
    try:
        # Use the agent to search and analyze papers
        results = await agent.review_with_citations(
            query=query,
            max_papers=max_results,
            citation_depth=1,  # Only follow 1 level of citations
            include_network=True
        )
        
        # Display results
        print(f"\n3. Search Results:")
        print(f"   ✓ Papers found: {results['total_papers']}")
        print(f"   ✓ Execution time: {results['execution_time']:.2f} seconds")
        
        # Show paper details
        papers = results.get("papers", [])
        print(f"\n4. Paper Details:")
        print("   " + "-"*56)
        
        for i, paper in enumerate(papers[:5]):  # Show first 5
            print(f"\n   Paper {i+1}:")
            print(f"   Title: {paper.get('title', 'Unknown')[:80]}...")
            
            # Authors
            authors = paper.get('authors', [])
            if authors:
                author_str = ', '.join(authors[:3])
                if len(authors) > 3:
                    author_str += f" (+{len(authors)-3} more)"
                print(f"   Authors: {author_str}")
            
            # Metadata
            print(f"   Year: {paper.get('year', 'Unknown')}")
            print(f"   Source: {paper.get('_source', 'Unknown')}")
            print(f"   Citations: {paper.get('citation_count', 0)}")
            
            # ArXiv specific
            if paper.get('arxiv_id'):
                print(f"   ArXiv ID: {paper['arxiv_id']}")
                print(f"   ArXiv URL: https://arxiv.org/abs/{paper['arxiv_id']}")
            
            # Abstract preview
            abstract = paper.get('abstract', '')
            if abstract:
                print(f"   Abstract: {abstract[:150]}...")
            
            # Quality score if available
            if paper.get('_quality_score'):
                print(f"   Quality Score: {paper['_quality_score']:.2f}")
        
        # Citation analysis
        analysis = results.get("citation_analysis", {})
        if analysis:
            print(f"\n5. Citation Analysis:")
            print(f"   - Total citations: {analysis.get('total_citations', 0)}")
            print(f"   - Average citations: {analysis.get('average_citations', 0):.1f}")
            print(f"   - H-index: {analysis.get('h_index', 0)}")
            
            # Most cited paper
            if analysis.get('most_cited'):
                most_cited = analysis['most_cited']
                print(f"\n   Most Cited Paper:")
                print(f"   - {most_cited.get('title', 'Unknown')[:60]}...")
                print(f"   - Citations: {most_cited.get('citations', 0)}")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"arxiv_search_{query.replace(' ', '_')}_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n✓ Full results saved to: {filename}")
        
        return results
        
    except Exception as e:
        print(f"\n✗ Error searching ArXiv: {e}")
        import traceback
        traceback.print_exc()
        return None


async def search_arxiv_with_filters(query: str, filters: dict):
    """
    Search ArXiv with advanced filtering using Reference Intelligence.
    
    Args:
        query: Search query
        filters: Filter criteria (min_year, max_year, min_citations, etc.)
    """
    print(f"\n{'='*60}")
    print(f"ArXiv Filtered Search")
    print(f"{'='*60}\n")
    
    # Initialize enhanced orchestrator
    print("1. Initializing Reference-Enhanced Orchestrator...")
    orchestrator = ReferenceEnhancedOrchestrator()
    print("   ✓ Multi-source aggregation ready")
    print("   ✓ ArXiv as primary source")
    
    # Display filters
    print("\n2. Search Filters:")
    for key, value in filters.items():
        print(f"   - {key}: {value}")
    
    try:
        # Execute filtered search
        print(f"\n3. Searching with filters...")
        results = await orchestrator.search_with_filters(query, filters)
        
        # Display results
        papers = results.get("multi_source_papers", [])
        print(f"\n4. Filtered Results:")
        print(f"   ✓ Papers matching criteria: {len(papers)}")
        
        # Verify filters were applied
        if papers:
            years = [p.get("year", 0) for p in papers if p.get("year")]
            citations = [p.get("citation_count", 0) for p in papers]
            
            if years:
                print(f"   ✓ Year range: {min(years)} - {max(years)}")
            if citations:
                print(f"   ✓ Citation range: {min(citations)} - {max(citations)}")
        
        return results
        
    except Exception as e:
        print(f"\n✗ Error in filtered search: {e}")
        return None


async def get_arxiv_paper_by_id(arxiv_id: str):
    """
    Get a specific ArXiv paper by ID and analyze its citations.
    
    Args:
        arxiv_id: ArXiv paper ID (e.g., "2301.08561")
    """
    print(f"\n{'='*60}")
    print(f"ArXiv Paper Analysis: {arxiv_id}")
    print(f"{'='*60}\n")
    
    agent = A2ALiteratureReviewAgent()
    
    # Search for specific paper
    query = f"arxiv:{arxiv_id}"
    
    try:
        results = await agent.review_with_citations(
            query=query,
            max_papers=1,
            citation_depth=2,  # Follow 2 levels of citations
            include_network=True
        )
        
        papers = results.get("papers", [])
        if papers:
            paper = papers[0]
            print("Paper Details:")
            print(f"Title: {paper.get('title', 'Unknown')}")
            print(f"Authors: {', '.join(paper.get('authors', []))}")
            print(f"Year: {paper.get('year', 'Unknown')}")
            print(f"URL: https://arxiv.org/abs/{arxiv_id}")
            
            # Citation network
            network = results.get("citation_network", {})
            if network:
                print(f"\nCitation Network:")
                print(f"- Total nodes: {network['metrics']['total_nodes']}")
                print(f"- Total edges: {network['metrics']['total_edges']}")
        
        return results
        
    except Exception as e:
        print(f"Error analyzing paper: {e}")
        return None


async def demo_arxiv_categories():
    """Demonstrate searching different ArXiv categories."""
    print(f"\n{'='*60}")
    print("ArXiv Category Search Demo")
    print(f"{'='*60}\n")
    
    # Different ArXiv categories to search
    categories = {
        "cs.AI": "artificial intelligence",
        "cs.LG": "machine learning",
        "cs.CL": "natural language processing",
        "quant-ph": "quantum computing",
        "stat.ML": "statistical machine learning"
    }
    
    agent = A2ALiteratureReviewAgent()
    
    for category, description in categories.items():
        print(f"\n📚 Category: {category} ({description})")
        
        # Search with category filter
        query = f"cat:{category} AND neural"
        
        try:
            results = await agent.review_with_citations(
                query=query,
                max_papers=3,
                citation_depth=0,  # No citation following
                include_network=False
            )
            
            papers = results.get("papers", [])
            print(f"   Found {len(papers)} papers")
            
            for paper in papers[:2]:  # Show first 2
                print(f"   - {paper.get('title', 'Unknown')[:60]}...")
                
        except Exception as e:
            print(f"   Error: {e}")


async def main():
    """Main demo function."""
    print("ArXiv Research Paper Retrieval Demo")
    print("===================================")
    print("\nThis demo shows how to use our enhanced Literature Review Agent")
    print("to search and analyze research papers from ArXiv.\n")
    
    # Demo 1: Basic search
    print("\n" + "="*60)
    print("Demo 1: Basic ArXiv Search")
    print("="*60)
    await search_arxiv_papers(
        query="transformer models attention mechanism",
        max_results=10
    )
    
    # Demo 2: Filtered search
    print("\n" + "="*60)
    print("Demo 2: Filtered ArXiv Search")
    print("="*60)
    filters = {
        "min_year": 2022,
        "max_year": 2024,
        "sources": ["arxiv"],
        "min_citations": 5
    }
    await search_arxiv_with_filters(
        query="large language models",
        filters=filters
    )
    
    # Demo 3: Specific paper analysis
    print("\n" + "="*60)
    print("Demo 3: Specific Paper Analysis")
    print("="*60)
    # Example: "Attention Is All You Need" paper
    await get_arxiv_paper_by_id("1706.03762")
    
    # Demo 4: Category search
    print("\n" + "="*60)
    print("Demo 4: ArXiv Category Search")
    print("="*60)
    await demo_arxiv_categories()
    
    print("\n\n✅ ArXiv demo completed!")
    print("\nKey Features Demonstrated:")
    print("- Direct ArXiv search integration")
    print("- Citation network analysis")
    print("- Quality-based ranking")
    print("- Advanced filtering")
    print("- Category-specific searches")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())