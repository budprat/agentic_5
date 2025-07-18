#!/usr/bin/env python3
"""
Interactive Research Demo - Orchestrator delegating to Literature Review Agent
Demonstrates the flow from Research Orchestrator -> Literature Review Agent -> Results
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List
import sys
import os

# Add paths
sys.path.append('/Users/mac/Agents/agentic_5/src')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the enhanced components
from a2a_mcp.common.citation_tracker import CitationTracker
from a2a_mcp.common.reference_intelligence import ReferenceIntelligenceService


class InteractiveResearchDemo:
    """
    Interactive demonstration of Research Orchestrator delegating to Literature Review Agent
    """
    
    def __init__(self):
        # Initialize components that the agents would use
        self.citation_tracker = CitationTracker()
        self.reference_service = ReferenceIntelligenceService({
            "enabled": True,
            "sources": {
                "arxiv": True,
                "semantic_scholar": False,  # Disabled to avoid timeout
                "mcp_scholarly": False,
                "web_search": False
            },
            "limits": {
                "max_papers_per_source": 10,
                "max_total_papers": 20,
                "request_timeout": 30
            },
            "quality_filters": {
                "min_citation_count": 0,
                "max_age_years": 10,
                "require_peer_review": False
            },
            "quality_thresholds": {
                "general": 0.6,
                "academic": 0.7,
                "medical": 0.8,
                "legal": 0.8
            }
        })
        
    async def simulate_orchestrator_delegation(self, research_query: str) -> Dict[str, Any]:
        """
        Simulates how the Research Orchestrator delegates to Literature Review Agent
        """
        print("\n" + "="*80)
        print("🎯 RESEARCH ORCHESTRATOR")
        print("="*80)
        print(f"📋 Received Query: {research_query}")
        print("\n🤔 Analyzing query and planning research strategy...")
        
        # Orchestrator analyzes the query
        research_plan = {
            "primary_task": "literature_review",
            "subtasks": [
                "search_arxiv_papers",
                "track_citations",
                "analyze_quality",
                "generate_summary"
            ],
            "delegation": {
                "agent": "Literature Review Agent",
                "instructions": f"Perform comprehensive literature review on: {research_query}"
            }
        }
        
        print("\n📊 Research Plan:")
        for key, value in research_plan.items():
            if key != "delegation":
                print(f"  • {key}: {value}")
        
        print(f"\n🤝 Delegating to: {research_plan['delegation']['agent']}")
        print(f"   Instructions: {research_plan['delegation']['instructions']}")
        
        # Simulate delegation to Literature Review Agent
        literature_results = await self.simulate_literature_review_agent(
            research_query, 
            research_plan['delegation']['instructions']
        )
        
        # Orchestrator processes results
        print("\n" + "="*80)
        print("🎯 RESEARCH ORCHESTRATOR - Processing Results")
        print("="*80)
        
        final_results = {
            "query": research_query,
            "execution_plan": research_plan,
            "literature_review": literature_results,
            "synthesis": self.synthesize_results(literature_results),
            "timestamp": datetime.now().isoformat()
        }
        
        return final_results
    
    async def simulate_literature_review_agent(self, query: str, instructions: str) -> Dict[str, Any]:
        """
        Simulates the Literature Review Agent execution
        """
        print("\n" + "-"*80)
        print("📚 LITERATURE REVIEW AGENT")
        print("-"*80)
        print(f"📝 Received Instructions: {instructions}")
        print("\n🔍 Starting literature search...")
        
        # Step 1: Search ArXiv
        print("\n1️⃣ Searching ArXiv for papers...")
        arxiv_results = await self.reference_service._search_arxiv(query, "computer_science")
        
        papers = arxiv_results.get("papers", [])
        print(f"   ✅ Found {len(papers)} papers from ArXiv")
        
        # Step 2: Track Citations
        print("\n2️⃣ Tracking citations for each paper...")
        tracked_papers = []
        for i, paper in enumerate(papers[:5], 1):  # Limit to 5 for demo
            citation_data = self.citation_tracker.track_citation(paper, "arxiv")
            tracked_paper = {**paper, "citation_tracking": citation_data}
            tracked_papers.append(tracked_paper)
            print(f"   📎 Tracked: {paper.get('title', 'Unknown')[:60]}...")
        
        # Step 3: Analyze Quality
        print("\n3️⃣ Analyzing paper quality and relevance...")
        quality_analysis = self.analyze_paper_quality(tracked_papers)
        
        # Step 4: Generate Citation Statistics
        print("\n4️⃣ Generating citation statistics...")
        citation_stats = self.citation_tracker.get_citation_statistics()
        
        # Return results to orchestrator
        return {
            "papers_found": len(papers),
            "papers_analyzed": tracked_papers,
            "quality_analysis": quality_analysis,
            "citation_statistics": citation_stats,
            "search_query": query,
            "source": "Literature Review Agent"
        }
    
    def analyze_paper_quality(self, papers: List[Dict]) -> Dict[str, Any]:
        """
        Analyze quality of papers
        """
        quality_scores = []
        high_quality_papers = []
        
        for paper in papers:
            score = paper.get("quality_score", 0)
            quality_scores.append(score)
            if score >= 0.8:
                high_quality_papers.append({
                    "title": paper.get("title", "Unknown"),
                    "score": score,
                    "arxiv_id": paper.get("arxiv_id")
                })
        
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        print(f"   📊 Average Quality Score: {avg_quality:.2f}")
        print(f"   ⭐ High Quality Papers: {len(high_quality_papers)}")
        
        return {
            "average_quality": avg_quality,
            "high_quality_count": len(high_quality_papers),
            "high_quality_papers": high_quality_papers,
            "quality_distribution": {
                "excellent": sum(1 for s in quality_scores if s >= 0.9),
                "good": sum(1 for s in quality_scores if 0.7 <= s < 0.9),
                "fair": sum(1 for s in quality_scores if 0.5 <= s < 0.7),
                "poor": sum(1 for s in quality_scores if s < 0.5)
            }
        }
    
    def synthesize_results(self, literature_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrator synthesizes the results from Literature Review Agent
        """
        papers = literature_results.get("papers_analyzed", [])
        
        if not papers:
            return {"summary": "No papers found for analysis"}
        
        # Create synthesis
        synthesis = {
            "key_findings": [
                f"Analyzed {len(papers)} papers from ArXiv",
                f"Average quality score: {literature_results['quality_analysis']['average_quality']:.2f}",
                f"High quality papers: {literature_results['quality_analysis']['high_quality_count']}"
            ],
            "top_papers": [],
            "research_trends": [],
            "recommendations": []
        }
        
        # Add top papers
        for paper in papers[:3]:
            synthesis["top_papers"].append({
                "title": paper.get("title", "Unknown"),
                "relevance": paper.get("quality_score", 0),
                "citation_id": paper.get("citation_tracking", {}).get("citation_id")
            })
        
        # Extract trends from categories
        categories = {}
        for paper in papers:
            for cat in paper.get("categories", []):
                categories[cat] = categories.get(cat, 0) + 1
        
        synthesis["research_trends"] = [
            f"{cat}: {count} papers" 
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3]
        ]
        
        # Add recommendations
        if literature_results['quality_analysis']['average_quality'] > 0.7:
            synthesis["recommendations"].append("High quality literature available - proceed with detailed analysis")
        else:
            synthesis["recommendations"].append("Limited high-quality sources - consider expanding search criteria")
        
        return synthesis
    
    def display_results(self, results: Dict[str, Any]):
        """
        Display the final results in a user-friendly format
        """
        print("\n" + "="*80)
        print("📊 FINAL RESEARCH RESULTS")
        print("="*80)
        
        print(f"\n🔍 Query: {results['query']}")
        print(f"⏰ Completed: {results['timestamp']}")
        
        # Literature Review Summary
        lit_review = results['literature_review']
        print(f"\n📚 Literature Review Summary:")
        print(f"   • Papers Found: {lit_review['papers_found']}")
        print(f"   • Papers Analyzed: {len(lit_review['papers_analyzed'])}")
        print(f"   • Average Quality: {lit_review['quality_analysis']['average_quality']:.2f}")
        
        # Quality Distribution
        quality_dist = lit_review['quality_analysis']['quality_distribution']
        print(f"\n📊 Quality Distribution:")
        for level, count in quality_dist.items():
            print(f"   • {level.capitalize()}: {count} papers")
        
        # Synthesis
        synthesis = results['synthesis']
        print(f"\n🔬 Key Findings:")
        for finding in synthesis['key_findings']:
            print(f"   • {finding}")
        
        print(f"\n📈 Research Trends:")
        for trend in synthesis['research_trends']:
            print(f"   • {trend}")
        
        print(f"\n💡 Recommendations:")
        for rec in synthesis['recommendations']:
            print(f"   • {rec}")
        
        # Top Papers
        print(f"\n🏆 Top Papers:")
        for i, paper in enumerate(synthesis['top_papers'], 1):
            print(f"   {i}. {paper['title'][:70]}...")
            print(f"      Relevance: {paper['relevance']:.2f}")
            print(f"      Citation ID: {paper['citation_id']}")
        
        # Citation Statistics
        citation_stats = lit_review['citation_statistics']
        print(f"\n📊 Citation Tracking Summary:")
        print(f"   • Total Citations Tracked: {citation_stats.get('total_citations', 0)}")
        print(f"   • DOI Coverage: {citation_stats.get('doi_coverage', 0):.1%}")
        print(f"   • Open Access Ratio: {citation_stats.get('open_access_ratio', 0):.1%}")
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """
        Save results to JSON file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"research_demo_results_{timestamp}.json"
        
        # Clean results for JSON serialization
        def clean_for_json(obj):
            if isinstance(obj, dict):
                return {k: clean_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_for_json(item) for item in obj]
            elif hasattr(obj, 'isoformat'):
                return obj.isoformat()
            else:
                return obj
        
        cleaned_results = clean_for_json(results)
        
        with open(filename, 'w') as f:
            json.dump(cleaned_results, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")


async def main():
    """
    Interactive demo main function
    """
    print("\n" + "🔬 RESEARCH ORCHESTRATOR INTERACTIVE DEMO 🔬".center(80))
    print("="*80)
    print("This demo shows how the Research Orchestrator delegates tasks to")
    print("the Literature Review Agent with Citation Tracking and ArXiv integration.")
    print("="*80)
    
    # Use default query to avoid input issues
    print("\n📝 Using default research query:")
    user_query = "transformer models for natural language processing"
    print(f"   Query: '{user_query}'")
    
    print(f"\n✅ Starting research on: '{user_query}'")
    print("Please wait while the orchestrator coordinates the research...\n")
    
    # Create demo instance
    demo = InteractiveResearchDemo()
    
    try:
        # Run the orchestration
        results = await demo.simulate_orchestrator_delegation(user_query)
        
        # Display results
        demo.display_results(results)
        
        # Auto-save results
        print("\n💾 Auto-saving results...")
        demo.save_results(results)
        
        # Auto-export citations in JSON format
        print("\n📑 Auto-exporting citations in JSON format...")
        citations = demo.citation_tracker.export_citations("json")
        
        filename = f"citations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            f.write(citations)
        
        print(f"✅ Citations exported to: {filename}")
    
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("Demo completed! Thank you for testing the Research Orchestrator.")
    print("="*80)


if __name__ == "__main__":
    # Set environment variable to avoid MCP tool errors
    os.environ["BRIGHTDATA_API_KEY"] = ""
    
    # Run the demo
    asyncio.run(main())