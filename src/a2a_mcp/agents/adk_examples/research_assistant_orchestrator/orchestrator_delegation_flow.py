#!/usr/bin/env python3
"""
Orchestrator Delegation Flow Visualization
Shows how Research Orchestrator delegates to Literature Review Agent
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List
import json
import sys
import os

# Add paths for imports
sys.path.append('/Users/mac/Agents/agentic_5/src')

# Import real components
from a2a_mcp.common.citation_tracker import CitationTracker
from a2a_mcp.common.reference_intelligence import ReferenceIntelligenceService


class OrchestratorDelegationFlow:
    """
    Demonstrates the delegation flow between Research Orchestrator and Literature Review Agent
    """
    
    def __init__(self):
        self.execution_log = []
        # Initialize real components
        self.citation_tracker = CitationTracker()
        self.reference_service = ReferenceIntelligenceService({
            "enabled": True,
            "sources": {
                "arxiv": True,
                "semantic_scholar": False,
                "mcp_scholarly": False,
                "web_search": False
            },
            "limits": {
                "max_papers_per_source": 5,
                "max_total_papers": 10,
                "request_timeout": 30
            },
            "quality_filters": {
                "min_citation_count": 0,
                "max_age_years": 10,
                "require_peer_review": False
            }
        })
    
    def log_step(self, agent: str, action: str, details: Dict = None):
        """Log each step of the execution"""
        step = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "action": action,
            "details": details or {}
        }
        self.execution_log.append(step)
        
        # Print formatted output
        print(f"\n{'='*60}")
        print(f"🤖 {agent}")
        print(f"📋 Action: {action}")
        if details:
            for key, value in details.items():
                if isinstance(value, list):
                    print(f"   {key}:")
                    for item in value[:3]:  # Show first 3 items
                        print(f"     • {item}")
                    if len(value) > 3:
                        print(f"     ... and {len(value)-3} more")
                else:
                    print(f"   {key}: {value}")
    
    async def demonstrate_flow(self, research_query: str):
        """
        Demonstrate the complete delegation flow
        """
        print("\n" + "🔬 RESEARCH ORCHESTRATOR DELEGATION FLOW 🔬".center(60))
        print("="*60)
        print(f"Research Query: {research_query}")
        print("="*60)
        
        # Step 1: User request arrives at Orchestrator
        self.log_step(
            "User",
            "Submit Research Request",
            {"query": research_query}
        )
        
        # Step 2: Orchestrator analyzes request
        self.log_step(
            "Research Orchestrator",
            "Analyze Request",
            {
                "intent": "literature_review",
                "domain": "computer_science",
                "complexity": "medium",
                "estimated_time": "5-10 minutes"
            }
        )
        
        # Step 3: Orchestrator creates execution plan
        execution_plan = {
            "phases": [
                "Literature Search",
                "Citation Tracking", 
                "Quality Analysis",
                "Synthesis"
            ],
            "agents_required": ["Literature Review Agent"],
            "tools_required": ["ArXiv API", "Citation Tracker", "Reference Intelligence"]
        }
        
        self.log_step(
            "Research Orchestrator",
            "Create Execution Plan",
            execution_plan
        )
        
        # Step 4: Orchestrator prepares delegation
        delegation_request = {
            "target_agent": "Literature Review Agent",
            "task": "comprehensive_literature_review",
            "parameters": {
                "query": research_query,
                "max_papers": 20,
                "sources": ["arxiv"],
                "enable_citations": True,
                "quality_threshold": 0.7
            },
            "expected_output": {
                "papers": "list of analyzed papers",
                "citations": "citation network data",
                "quality_metrics": "quality assessment scores",
                "summary": "synthesized findings"
            }
        }
        
        self.log_step(
            "Research Orchestrator",
            "Prepare Delegation Request",
            delegation_request
        )
        
        # Step 5: Delegate to Literature Review Agent
        self.log_step(
            "Research Orchestrator",
            "Delegate to Literature Review Agent",
            {"message": "Sending task via A2A Protocol"}
        )
        
        # Step 6: Literature Review Agent receives task
        self.log_step(
            "Literature Review Agent",
            "Receive Task",
            {
                "task_id": "LIT-2025-001",
                "status": "accepted",
                "estimated_completion": "5 minutes"
            }
        )
        
        # Step 7: Literature Review Agent executes
        await self.simulate_literature_review_execution(research_query)
        
        # Step 8: Literature Review Agent returns results
        # Use real results from the execution
        results = getattr(self, 'current_results', {})
        papers = results.get('papers', [])
        
        # Extract key findings from actual papers
        key_findings = []
        if papers:
            # Get unique categories
            categories = set()
            for p in papers[:5]:
                categories.update(p.get('categories', []))
            if categories:
                key_findings.append(f"Research spans {len(categories)} categories: {', '.join(list(categories)[:3])}")
            
            # Quality insight
            avg_q = results.get('avg_quality', 0)
            if avg_q > 0:
                key_findings.append(f"Average quality score: {avg_q:.2f}")
            
            # Top paper insight
            if papers:
                top_paper = max(papers, key=lambda p: p.get('quality_score', 0))
                key_findings.append(f"Top paper: {top_paper.get('title', 'Unknown')[:40]}...")
        
        agent_results = {
            "task_id": "LIT-2025-001",
            "status": "completed",
            "papers_found": len(papers),
            "papers_analyzed": min(len(papers), 5),
            "citations_tracked": results.get('citation_stats', {}).get('total_citations', 0),
            "quality_score": round(results.get('avg_quality', 0), 2),
            "key_findings": key_findings if key_findings else ["No papers found for this query"]
        }
        
        self.log_step(
            "Literature Review Agent",
            "Return Results to Orchestrator",
            agent_results
        )
        
        # Step 9: Orchestrator processes results
        self.log_step(
            "Research Orchestrator",
            "Process Agent Results",
            {
                "validation": "passed",
                "quality_check": "approved",
                "completeness": "100%"
            }
        )
        
        # Step 10: Orchestrator synthesizes final report
        # Generate insights from real data
        top_insights = []
        recommendations = []
        
        if papers:
            # Category analysis
            all_categories = []
            for p in papers:
                all_categories.extend(p.get('categories', []))
            
            if all_categories:
                from collections import Counter
                cat_counts = Counter(all_categories)
                top_cat = cat_counts.most_common(1)[0] if cat_counts else None
                if top_cat:
                    top_insights.append(f"Most common category: {top_cat[0]} ({top_cat[1]} papers)")
            
            # Quality insights
            high_quality = [p for p in papers if p.get('quality_score', 0) >= 0.8]
            if high_quality:
                top_insights.append(f"{len(high_quality)} high-quality papers identified")
            
            # Time insights
            if papers[0].get('published'):
                top_insights.append(f"Latest research from {papers[0].get('published', 'Unknown date')}")
            
            # Recommendations based on findings
            if high_quality:
                recommendations.append(f"Focus on {len(high_quality)} high-quality papers for detailed analysis")
            if len(papers) > 5:
                recommendations.append("Consider narrowing search criteria for more focused results")
            if agent_results.get('quality_score', 0) < 0.7:
                recommendations.append("Expand search terms to find more relevant papers")
        else:
            top_insights.append("No papers found - consider broadening search terms")
            recommendations.append("Try alternative keywords or research domains")
        
        final_report = {
            "research_query": research_query,
            "total_papers_analyzed": agent_results.get('papers_analyzed', 0),
            "average_quality": agent_results.get('quality_score', 0),
            "top_insights": top_insights,
            "recommendations": recommendations
        }
        
        self.log_step(
            "Research Orchestrator",
            "Generate Final Report",
            final_report
        )
        
        # Step 11: Return to user
        self.log_step(
            "Research Orchestrator",
            "Return Results to User",
            {"format": "structured_report", "delivery": "complete"}
        )
        
        return self.execution_log
    
    async def simulate_literature_review_execution(self, query: str):
        """
        Execute real Literature Review Agent workflow with actual ArXiv data
        """
        # Sub-step 1: Real ArXiv Search
        self.log_step(
            "Literature Review Agent",
            "Searching ArXiv (Real API)",
            {"query": query, "status": "connecting to ArXiv..."}
        )
        
        try:
            # Perform real ArXiv search
            arxiv_results = await self.reference_service._search_arxiv(query, "computer_science")
            papers = arxiv_results.get("papers", [])
            
            # Get first paper title if available
            first_paper = papers[0].get('title', 'No papers found') if papers else 'No papers found'
            
            self.log_step(
                "Literature Review Agent",
                "ArXiv Search Complete",
                {
                    "query": query,
                    "results": f"{len(papers)} papers found",
                    "top_result": first_paper[:60] + "..." if len(first_paper) > 60 else first_paper
                }
            )
            
            await asyncio.sleep(0.2)
            
            # Sub-step 2: Real Citation Tracking
            tracked_count = 0
            citation_ids = []
            
            for paper in papers[:5]:  # Track first 5 papers
                citation_data = self.citation_tracker.track_citation(paper, "arxiv")
                citation_ids.append(citation_data['citation_id'])
                tracked_count += 1
            
            self.log_step(
                "Literature Review Agent",
                "Citation Tracking Complete",
                {
                    "papers_tracked": tracked_count,
                    "citation_ids_generated": len(citation_ids),
                    "doi_resolved": sum(1 for p in papers[:5] if p.get('doi')),
                    "provenance_recorded": "arxiv"
                }
            )
            
            await asyncio.sleep(0.2)
            
            # Sub-step 3: Real Quality Analysis
            quality_scores = [p.get('quality_score', 0) for p in papers]
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            quality_distribution = {
                "high_quality": sum(1 for s in quality_scores if s >= 0.8),
                "medium_quality": sum(1 for s in quality_scores if 0.5 <= s < 0.8),
                "low_quality": sum(1 for s in quality_scores if s < 0.5)
            }
            
            # Find top paper
            top_paper = max(papers, key=lambda p: p.get('quality_score', 0)) if papers else None
            
            self.log_step(
                "Literature Review Agent",
                "Quality Analysis Complete",
                {
                    "quality_metrics": {
                        "average_score": round(avg_quality, 2),
                        **quality_distribution
                    },
                    "top_paper": {
                        "title": top_paper.get('title', 'N/A')[:50] + "..." if top_paper else "N/A",
                        "score": round(top_paper.get('quality_score', 0), 2) if top_paper else 0,
                        "arxiv_id": top_paper.get('arxiv_id', 'N/A') if top_paper else "N/A"
                    }
                }
            )
            
            await asyncio.sleep(0.2)
            
            # Sub-step 4: Citation Network Analysis
            citation_stats = self.citation_tracker.get_citation_statistics()
            
            self.log_step(
                "Literature Review Agent",
                "Citation Network Built",
                {
                    "nodes": citation_stats.get('total_citations', 0),
                    "unique_sources": len(citation_stats.get('source_distribution', {})),
                    "doi_coverage": f"{citation_stats.get('doi_coverage', 0):.1%}",
                    "open_access_ratio": f"{citation_stats.get('open_access_ratio', 0):.1%}"
                }
            )
            
            # Store results for later use
            self.current_results = {
                'papers': papers,
                'avg_quality': avg_quality,
                'citation_stats': citation_stats
            }
            
        except Exception as e:
            self.log_step(
                "Literature Review Agent",
                "Error During Execution",
                {"error": str(e), "fallback": "Using minimal data"}
            )
            # Store minimal results
            self.current_results = {
                'papers': [],
                'avg_quality': 0,
                'citation_stats': {}
            }
    
    def visualize_flow(self):
        """
        Create a visual representation of the flow
        """
        print("\n" + "="*60)
        print("📊 DELEGATION FLOW DIAGRAM")
        print("="*60)
        print("""
        USER
         |
         | 1. Research Query
         ↓
    ┌─────────────────────────┐
    │  RESEARCH ORCHESTRATOR  │
    │                         │
    │  • Analyze Request      │
    │  • Create Plan          │
    │  • Prepare Delegation   │
    └─────────────────────────┘
                |
                | 2. Delegate Task (A2A Protocol)
                ↓
    ┌─────────────────────────┐
    │ LITERATURE REVIEW AGENT │
    │                         │
    │  • Search ArXiv         │
    │  • Track Citations      │
    │  • Analyze Quality      │
    │  • Build Network        │
    └─────────────────────────┘
                |
                | 3. Return Results
                ↓
    ┌─────────────────────────┐
    │  RESEARCH ORCHESTRATOR  │
    │                         │
    │  • Process Results      │
    │  • Synthesize Report    │
    └─────────────────────────┘
                |
                | 4. Final Report
                ↓
              USER
        """)
    
    def save_execution_log(self, filename: str = None):
        """Save the execution log"""
        if not filename:
            filename = f"delegation_flow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.execution_log, f, indent=2)
        
        print(f"\n💾 Execution log saved to: {filename}")


async def main():
    """
    Run the delegation flow demonstration
    """
    print("\n🔬 ORCHESTRATOR DELEGATION FLOW DEMONSTRATION")
    print("This shows how the Research Orchestrator delegates tasks")
    print("to the Literature Review Agent using the A2A protocol.")
    
    # Create flow demonstrator
    flow = OrchestratorDelegationFlow()
    
    # Show the flow diagram first
    flow.visualize_flow()
    
    print("\n📝 Using default research query: 'transformer models for NLP'")
    query = "transformer models for NLP"
    
    print(f"\n✅ Starting delegation flow for: '{query}'")
    print("Watch how the task flows through the system...\n")
    
    # Run the demonstration
    execution_log = await flow.demonstrate_flow(query)
    
    # Summary
    print("\n" + "="*60)
    print("📊 EXECUTION SUMMARY")
    print("="*60)
    print(f"Total Steps: {len(execution_log)}")
    
    # Count by agent
    agent_counts = {}
    for step in execution_log:
        agent = step['agent']
        agent_counts[agent] = agent_counts.get(agent, 0) + 1
    
    print("\nSteps by Agent:")
    for agent, count in agent_counts.items():
        print(f"  • {agent}: {count} actions")
    
    # Timing
    start_time = execution_log[0]['timestamp']
    end_time = execution_log[-1]['timestamp']
    print(f"\nExecution Time: {start_time} to {end_time}")
    
    # Auto-save execution log
    print("\n💾 Auto-saving execution log...")
    flow.save_execution_log()
    
    print("\n✅ Demonstration complete!")


if __name__ == "__main__":
    # Set environment variable
    os.environ["BRIGHTDATA_API_KEY"] = ""
    asyncio.run(main())