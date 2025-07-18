"""
ABOUTME: Direct ArXiv search using the Reference Intelligence Service
ABOUTME: Simple example of getting papers from ArXiv without full agent orchestration
"""

import asyncio
import arxiv
from datetime import datetime
import json
import sys

# Add path for imports
sys.path.append('/Users/mac/Agents/agentic_5/src')

# Import reference intelligence
from a2a_mcp.common.reference_intelligence import ReferenceIntelligenceService


async def direct_arxiv_search(query: str, max_results: int = 10):
    """
    Direct ArXiv search using the arxiv Python library.
    
    Args:
        query: Search query
        max_results: Maximum papers to retrieve
    """
    print(f"\n🔍 Direct ArXiv Search: '{query}'")
    print("="*60)
    
    # Create ArXiv client
    client = arxiv.Client(
        page_size=max_results,
        delay_seconds=1.0,  # Respectful rate limiting
        num_retries=3
    )
    
    # Search ArXiv
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )
    
    papers = []
    
    try:
        # Execute search
        for i, result in enumerate(client.results(search)):
            paper_info = {
                "title": result.title,
                "authors": [author.name for author in result.authors],
                "abstract": result.summary,
                "arxiv_id": result.entry_id.split('/')[-1],
                "published": result.published.isoformat() if result.published else None,
                "updated": result.updated.isoformat() if result.updated else None,
                "doi": result.doi,
                "primary_category": result.primary_category,
                "categories": result.categories,
                "pdf_url": result.pdf_url,
                "links": [link.href for link in result.links],
                "comment": result.comment,
                "journal_ref": result.journal_ref
            }
            
            papers.append(paper_info)
            
            # Display progress
            print(f"\n📄 Paper {i+1}:")
            print(f"   Title: {paper_info['title'][:80]}...")
            print(f"   Authors: {', '.join(paper_info['authors'][:3])}")
            if len(paper_info['authors']) > 3:
                print(f"            (+{len(paper_info['authors'])-3} more)")
            print(f"   ArXiv ID: {paper_info['arxiv_id']}")
            print(f"   Category: {paper_info['primary_category']}")
            print(f"   Published: {paper_info['published'][:10] if paper_info['published'] else 'Unknown'}")
            print(f"   PDF: {paper_info['pdf_url']}")
            
        print(f"\n✅ Found {len(papers)} papers")
        return papers
        
    except Exception as e:
        print(f"\n❌ Error searching ArXiv: {e}")
        return []


async def search_by_category(category: str, max_results: int = 5):
    """
    Search ArXiv by category.
    
    Common categories:
    - cs.AI: Artificial Intelligence
    - cs.LG: Machine Learning
    - cs.CL: Computation and Language
    - cs.CV: Computer Vision
    - cs.NE: Neural and Evolutionary Computing
    - quant-ph: Quantum Physics
    - stat.ML: Machine Learning (Statistics)
    """
    print(f"\n📚 Category Search: {category}")
    print("="*60)
    
    query = f"cat:{category}"
    return await direct_arxiv_search(query, max_results)


async def search_by_author(author_name: str, max_results: int = 5):
    """Search ArXiv by author name."""
    print(f"\n👤 Author Search: {author_name}")
    print("="*60)
    
    query = f'au:"{author_name}"'
    return await direct_arxiv_search(query, max_results)


async def get_paper_details(arxiv_id: str):
    """Get detailed information about a specific ArXiv paper."""
    print(f"\n📋 Paper Details: {arxiv_id}")
    print("="*60)
    
    client = arxiv.Client()
    search = arxiv.Search(id_list=[arxiv_id])
    
    try:
        results = list(client.results(search))
        if results:
            paper = results[0]
            
            details = {
                "title": paper.title,
                "authors": [author.name for author in paper.authors],
                "abstract": paper.summary,
                "arxiv_id": arxiv_id,
                "published": paper.published.isoformat() if paper.published else None,
                "updated": paper.updated.isoformat() if paper.updated else None,
                "doi": paper.doi,
                "primary_category": paper.primary_category,
                "categories": paper.categories,
                "pdf_url": paper.pdf_url,
                "comment": paper.comment,
                "journal_ref": paper.journal_ref,
                "links": [{"href": link.href, "title": link.title} for link in paper.links]
            }
            
            # Display details
            print(f"\nTitle: {details['title']}")
            print(f"\nAuthors:")
            for author in details['authors']:
                print(f"  - {author}")
            
            print(f"\nAbstract:\n{details['abstract'][:500]}...")
            
            print(f"\nMetadata:")
            print(f"  - ArXiv ID: {details['arxiv_id']}")
            print(f"  - Published: {details['published'][:10] if details['published'] else 'Unknown'}")
            print(f"  - Category: {details['primary_category']}")
            print(f"  - DOI: {details['doi'] or 'Not available'}")
            print(f"  - Journal: {details['journal_ref'] or 'Not published'}")
            
            print(f"\nLinks:")
            print(f"  - PDF: {details['pdf_url']}")
            print(f"  - Abstract: https://arxiv.org/abs/{arxiv_id}")
            
            return details
        else:
            print(f"❌ Paper not found: {arxiv_id}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting paper details: {e}")
        return None


async def advanced_search(
    query: str,
    category: str = None,
    author: str = None,
    year_from: int = None,
    year_to: int = None,
    max_results: int = 10
):
    """
    Advanced ArXiv search with multiple filters.
    
    Args:
        query: Main search query
        category: Category filter (e.g., 'cs.LG')
        author: Author name filter
        year_from: Start year
        year_to: End year
        max_results: Maximum results
    """
    print(f"\n🔍 Advanced ArXiv Search")
    print("="*60)
    
    # Build query
    search_parts = []
    
    if query:
        search_parts.append(f'all:"{query}"')
    
    if category:
        search_parts.append(f"cat:{category}")
    
    if author:
        search_parts.append(f'au:"{author}"')
    
    # Combine query parts
    full_query = " AND ".join(search_parts) if search_parts else "all:*"
    
    print(f"Query: {full_query}")
    if year_from or year_to:
        print(f"Year range: {year_from or 'any'} - {year_to or 'any'}")
    
    # Search
    papers = await direct_arxiv_search(full_query, max_results)
    
    # Filter by year if specified
    if year_from or year_to:
        filtered_papers = []
        for paper in papers:
            if paper.get('published'):
                year = int(paper['published'][:4])
                if year_from and year < year_from:
                    continue
                if year_to and year > year_to:
                    continue
                filtered_papers.append(paper)
        
        print(f"\n✅ After year filtering: {len(filtered_papers)} papers")
        return filtered_papers
    
    return papers


async def use_reference_intelligence():
    """Use Reference Intelligence Service for multi-source search."""
    print(f"\n🤖 Using Reference Intelligence Service")
    print("="*60)
    
    # Initialize service
    ref_service = ReferenceIntelligenceService(
        config={
            "enabled": True,
            "sources": {
                "arxiv": True,
                "semantic_scholar": False,  # Disable for this demo
                "mcp_scholarly": False,
                "web_search": False
            },
            "limits": {
                "max_papers_per_source": 10,
                "max_total_papers": 10,
                "request_timeout": 30
            }
        }
    )
    
    # Search
    query = "attention mechanism transformer"
    domain = "computer_science"
    
    print(f"Query: {query}")
    print(f"Domain: {domain}")
    
    try:
        results = await ref_service.gather_domain_references(query, domain)
        
        arxiv_papers = results.get("sources", {}).get("arxiv", [])
        print(f"\n✅ Found {len(arxiv_papers)} papers from ArXiv")
        
        for i, paper in enumerate(arxiv_papers[:3]):
            print(f"\n📄 Paper {i+1}:")
            print(f"   Title: {paper.get('title', 'Unknown')[:80]}...")
            print(f"   Year: {paper.get('year', 'Unknown')}")
            print(f"   Citations: {paper.get('citation_count', 0)}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


async def main():
    """Main demo function."""
    print("ArXiv Direct Search Examples")
    print("===========================")
    
    # Example 1: Basic search
    print("\n\n1️⃣ Basic Search Example")
    await direct_arxiv_search("quantum computing algorithms", max_results=3)
    
    # Example 2: Category search
    print("\n\n2️⃣ Category Search Example")
    await search_by_category("cs.LG", max_results=3)
    
    # Example 3: Author search
    print("\n\n3️⃣ Author Search Example")
    await search_by_author("Yoshua Bengio", max_results=3)
    
    # Example 4: Get specific paper
    print("\n\n4️⃣ Specific Paper Example")
    await get_paper_details("1706.03762")  # Attention Is All You Need
    
    # Example 5: Advanced search
    print("\n\n5️⃣ Advanced Search Example")
    await advanced_search(
        query="neural networks",
        category="cs.LG",
        year_from=2023,
        year_to=2024,
        max_results=5
    )
    
    # Example 6: Reference Intelligence
    print("\n\n6️⃣ Reference Intelligence Example")
    await use_reference_intelligence()
    
    print("\n\n✅ All examples completed!")
    
    # Save example results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    example_papers = await direct_arxiv_search("transformer", max_results=5)
    
    with open(f"arxiv_example_results_{timestamp}.json", 'w') as f:
        json.dump(example_papers, f, indent=2)
    
    print(f"\n📁 Example results saved to: arxiv_example_results_{timestamp}.json")


if __name__ == "__main__":
    asyncio.run(main())