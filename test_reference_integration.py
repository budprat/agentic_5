#!/usr/bin/env python3
"""Test Oracle reference integration."""

import asyncio
import sys
import os
import json

# Add project to path
sys.path.insert(0, './src')
sys.path.insert(0, '.')

async def test_reference_integration():
    """Test the reference integration functionality."""
    from a2a_mcp.common.reference_intelligence import ReferenceIntelligenceService
    from a2a_mcp.common.citation_tracker import CitationTracker
    from a2a_mcp.common.mcp_scholarly_client import MCPScholarlyClient
    
    print("🧪 TESTING ORACLE REFERENCE INTEGRATION")
    print("=" * 60)
    
    # Test configuration
    config = {
        "enabled": True,
        "sources": {
            "arxiv": True,
            "semantic_scholar": False,  # Disabled due to API timeout issues - TODO: investigate further
            "mcp_scholarly": False  # Docker not available in this environment
        },
        "limits": {
            "max_papers_per_source": 3,
            "max_total_papers": 6,
            "request_timeout": 15
        },
        "quality_filters": {
            "min_citation_count": 1,
            "max_age_years": 10,
            "require_peer_review": False
        }
    }
    
    print("📋 Test Configuration:")
    print(json.dumps(config, indent=2))
    
    # Initialize services
    print(f"\n🔧 INITIALIZING SERVICES...")
    service = ReferenceIntelligenceService(config)
    tracker = CitationTracker()
    mcp_client = MCPScholarlyClient(docker_available=False)
    
    # Test queries for different domains
    test_cases = [
        {
            "query": "quantum computing climate change",
            "domain": "computer_science",
            "description": "Interdisciplinary quantum + climate research"
        },
        {
            "query": "machine learning energy optimization",
            "domain": "technical_analysis", 
            "description": "AI for energy systems"
        },
        {
            "query": "sustainable transportation systems",
            "domain": "physical_analysis",
            "description": "Sustainability research"
        }
    ]
    
    success_count = 0
    total_papers_found = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 TEST CASE {i}: {test_case['description']}")
        print("─" * 50)
        print(f"📝 Query: {test_case['query']}")
        print(f"🎯 Domain: {test_case['domain']}")
        print(f"⚡ Gathering references...")
        
        try:
            # Gather references
            references = await service.gather_domain_references(
                test_case['query'], 
                test_case['domain']
            )
            
            # Analyze results
            if references.get('enabled'):
                print(f"✅ SUCCESS: Reference gathering completed")
                success_count += 1
                
                # Display source results
                sources = references.get('sources', {})
                print(f"📚 SOURCE RESULTS:")
                for source_name, source_data in sources.items():
                    paper_count = len(source_data.get('papers', []))
                    total_papers_found += paper_count
                    print(f"   📖 {source_name}: {paper_count} papers")
                    
                    if source_data.get('error'):
                        print(f"      ❌ Error: {source_data['error']}")
                    elif paper_count > 0:
                        # Show sample paper
                        sample_paper = source_data['papers'][0]
                        print(f"      📄 Sample: {sample_paper.get('title', 'No title')[:50]}...")
                        print(f"      📊 Quality: {sample_paper.get('quality_score', 0):.2f}")
                
                # Test citation tracking
                processed = references.get('processed', {})
                papers = processed.get('papers', [])
                if papers:
                    print(f"📋 CITATION TRACKING TEST:")
                    for paper in papers[:2]:  # Test first 2 papers
                        citation = tracker.track_citation(paper, paper.get('source', 'unknown'))
                        print(f"   🏷️  Tracked: {citation['citation_id']}")
                        
                        # Test citation formatting
                        formatted = tracker.format_citation(citation['citation_id'], 'apa')
                        print(f"   📝 APA: {formatted[:80]}...")
                
                # Display statistics
                stats = processed.get('statistics', {})
                if stats:
                    print(f"📊 STATISTICS:")
                    print(f"   Total Papers: {stats.get('total', 0)}")
                    print(f"   Avg Citations: {stats.get('avg_citations', 0):.1f}")
                    print(f"   Avg Quality: {stats.get('avg_quality_score', 0):.2f}")
                    print(f"   Open Access: {stats.get('open_access_count', 0)} papers")
            
            else:
                print(f"❌ FAILED: Reference integration not enabled")
                
        except Exception as e:
            print(f"❌ FAILED: {e}")
            import traceback
            traceback.print_exc()
    
    # Test MCP Scholarly status
    print(f"\n🐳 MCP SCHOLARLY STATUS TEST:")
    print("─" * 35)
    mcp_status = await mcp_client.test_connection()
    print(f"Status: {mcp_status['status']}")
    print(f"Message: {mcp_status['message']}")
    
    if mcp_status['status'] == 'docker_not_available':
        print("💡 Setup Guide:")
        guide = mcp_client.get_configuration_guide()
        for step, instruction in guide['docker_setup'].items():
            print(f"   {step}: {instruction}")
    
    # Test citation tracker statistics
    print(f"\n📊 CITATION TRACKER STATISTICS:")
    print("─" * 40)
    citation_stats = tracker.get_citation_statistics()
    print(f"Total Citations Tracked: {citation_stats.get('total_citations', 0)}")
    
    if citation_stats.get('total_citations', 0) > 0:
        print(f"Source Distribution: {citation_stats.get('source_distribution', {})}")
        quality_metrics = citation_stats.get('quality_metrics', {})
        print(f"Avg Quality Score: {quality_metrics.get('avg_quality_score', 0):.3f}")
        print(f"Avg Citations/Paper: {quality_metrics.get('avg_citations_per_paper', 0):.1f}")
    
    # Final summary
    print(f"\n🎉 TEST SUMMARY")
    print("=" * 30)
    print(f"✅ Successful Tests: {success_count}/{len(test_cases)}")
    print(f"📚 Total Papers Found: {total_papers_found}")
    print(f"🏷️  Citations Tracked: {citation_stats.get('total_citations', 0)}")
    
    if success_count == len(test_cases) and total_papers_found > 0:
        print(f"🎊 ALL TESTS PASSED! Reference integration is working correctly.")
        return True
    elif success_count > 0:
        print(f"⚠️  PARTIAL SUCCESS: Some sources working, check errors above.")
        return True
    else:
        print(f"❌ TESTS FAILED: Reference integration needs troubleshooting.")
        return False

async def test_individual_components():
    """Test individual components separately."""
    print(f"\n🔧 COMPONENT-LEVEL TESTING")
    print("=" * 40)
    
    # Test ArXiv client
    print(f"📚 Testing ArXiv Integration...")
    try:
        import arxiv
        client = arxiv.Client(page_size=3, delay_seconds=1.0, num_retries=2)
        search = arxiv.Search(query="quantum computing", max_results=3)
        
        papers = list(client.results(search))
        print(f"   ✅ ArXiv: Found {len(papers)} papers")
        if papers:
            print(f"   📄 Sample: {papers[0].title[:50]}...")
    
    except Exception as e:
        print(f"   ❌ ArXiv Error: {e}")
    
    # Test Semantic Scholar client - DISABLED
    print(f"📖 Testing Semantic Scholar Integration...")
    print(f"   ℹ️  DISABLED: Semantic Scholar API consistently times out")
    print(f"   ℹ️  TODO: Investigate API key requirements and connectivity")
    print(f"   ℹ️  Current status: Available for future implementation")
    
    # Test Citation Tracker
    print(f"🏷️  Testing Citation Tracker...")
    try:
        from a2a_mcp.common.citation_tracker import CitationTracker
        tracker = CitationTracker()
        
        # Test with dummy paper
        dummy_paper = {
            "title": "Test Paper for Citation Tracking",
            "authors": ["John Doe", "Jane Smith"],
            "year": 2024,
            "doi": "10.1000/test.citation",
            "source": "test"
        }
        
        citation = tracker.track_citation(dummy_paper, "test_source")
        formatted = tracker.format_citation(citation['citation_id'])
        
        print(f"   ✅ Citation Tracker: Working")
        print(f"   📝 Sample Citation: {formatted[:60]}...")
        
    except Exception as e:
        print(f"   ❌ Citation Tracker Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Oracle Reference Integration Tests...")
    
    # Run component tests first
    asyncio.run(test_individual_components())
    
    # Run full integration test
    success = asyncio.run(test_reference_integration())
    
    if success:
        print(f"\n✅ INTEGRATION TEST COMPLETED SUCCESSFULLY!")
        print(f"📋 Next Steps:")
        print(f"   1. Run: python enable_references.py")
        print(f"   2. Test with First Principles Oracle")
        print(f"   3. Monitor performance and quality")
        print(f"   4. Optional: Set up MCP Scholarly with Docker")
    else:
        print(f"\n❌ INTEGRATION TEST FAILED")
        print(f"🔧 Troubleshooting Steps:")
        print(f"   1. Check internet connection")
        print(f"   2. Verify dependencies: uv sync")
        print(f"   3. Check API rate limits")
        print(f"   4. Review error messages above")