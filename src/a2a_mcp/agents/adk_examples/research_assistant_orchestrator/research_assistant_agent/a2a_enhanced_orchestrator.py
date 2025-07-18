"""
ABOUTME: Comprehensive A2A-MCP enhanced research orchestrator with Reference Intelligence
ABOUTME: Combines all A2A features including quality validation, observability, and multi-source aggregation
"""

import os
import logging
import asyncio
from typing import Dict, Any, Optional, List, Set
from datetime import datetime
import json

# A2A-MCP Framework imports
import sys
sys.path.append('/Users/mac/Agents/agentic_5/src')
from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.common.quality_framework import QualityDomain, QualityThresholdFramework
from a2a_mcp.common.observability import ObservabilityManager, trace_async, record_metric
from a2a_mcp.common.a2a_protocol import A2AProtocolClient
from a2a_mcp.common.response_formatter import ResponseFormatter
from a2a_mcp.common.metrics_collector import MetricsCollector
from a2a_mcp.common.reference_intelligence import ReferenceIntelligenceService
from a2a_mcp.common.citation_tracker import CitationTracker

# Import existing Google ADK agent
from .agent import research_orchestrator
from .callbacks import research_progress_callback, save_research_state_callback

logger = logging.getLogger(__name__)


class A2AEnhancedOrchestrator(StandardizedAgentBase):
    """
    Comprehensive A2A-MCP enhanced research orchestrator with Reference Intelligence.
    
    This unified orchestrator provides ALL features:
    
    Core A2A-MCP Features:
    - Quality validation for academic research
    - Enterprise observability with OpenTelemetry
    - A2A protocol for inter-agent communication
    - Parallel workflow capabilities
    - Streaming with research artifacts
    
    Reference Intelligence Features:
    - Multi-source paper aggregation (ArXiv, Semantic Scholar, PubMed)
    - Intelligent reference deduplication
    - Cross-source validation
    - Quality-based source ranking
    - Parallel source querying
    - Reference completeness tracking
    
    While preserving:
    - Google ADK LlmAgent functionality
    - MCPToolset integration
    - Existing callbacks and state management
    """
    
    def __init__(self):
        """Initialize comprehensive enhanced research orchestrator."""
        # Initialize StandardizedAgentBase with academic quality config
        super().__init__(
            agent_name="A2A Enhanced Research Orchestrator",
            description="Enterprise-grade research orchestrator with multi-source intelligence",
            instructions="""You are an advanced research orchestrator with A2A-MCP capabilities.
            
            Your enhanced features include:
            - Academic quality validation with 7 research-specific metrics
            - Distributed observability and tracing
            - Inter-agent communication via A2A protocol
            - Parallel workflow optimization
            - Multi-source reference aggregation
            - Intelligent deduplication and ranking
            - Citation network analysis
            
            Coordinate research activities efficiently while maintaining high quality standards.""",
            quality_config={
                "domain": QualityDomain.ACADEMIC,
                "enabled": True,
                "thresholds": {
                    # Research-specific quality metrics
                    "research_confidence": {"min_value": 0.8, "weight": 1.2},
                    "evidence_quality": {"min_value": 0.85, "weight": 1.3},
                    "methodological_rigor": {"min_value": 0.8, "weight": 1.1},
                    "citation_quality": {"min_value": 0.75, "weight": 1.0},
                    "bias_mitigation": {"min_value": 0.7, "weight": 0.9},
                    "reproducibility": {"min_value": 0.8, "weight": 1.0},
                    "domain_coverage": {"min_value": 3, "max_value": 10, "weight": 0.8}
                }
            },
            mcp_tools_enabled=True,
            a2a_enabled=True
        )
        
        # Store reference to original Google ADK agent
        self.adk_agent = research_orchestrator
        
        # Initialize metrics collector
        self.metrics = MetricsCollector(
            namespace="research_orchestrator",
            subsystem="enhanced"
        )
        self._init_metrics()
        
        # Initialize Reference Intelligence Service
        self.reference_service = ReferenceIntelligenceService(
            config={
                "enabled": True,
                "sources": {
                    "arxiv": True,
                    "semantic_scholar": True,  # Enable with caution
                    "mcp_scholarly": True,
                    "pubmed": False,  # Disabled by default
                    "google_scholar": False  # Disabled by default
                },
                "parallel_search": True,
                "deduplication": True,
                "quality_ranking": True
            }
        )
        
        # Initialize Citation Tracker for cross-referencing
        self.citation_tracker = CitationTracker()
        
        # Source performance tracking
        self.source_performance = {}
        
        logger.info("A2A Enhanced Orchestrator initialized with Reference Intelligence")
    
    def _init_metrics(self):
        """Initialize comprehensive metrics for both A2A and Reference features."""
        # Research workflow metrics
        self.papers_analyzed = self.metrics.create_counter(
            'papers_analyzed_total',
            'Total papers analyzed across all sources',
            ['agent', 'status']
        )
        
        self.research_quality = self.metrics.create_histogram(
            'research_quality_score',
            'Quality scores for research outputs',
            ['domain_metric'],
            buckets=[0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0]
        )
        
        self.literature_search_duration = self.metrics.create_histogram(
            'literature_search_duration_seconds',
            'Time taken for literature searches',
            ['agent', 'search_type'],
            buckets=[1, 5, 10, 30, 60, 120, 300]
        )
        
        self.active_sessions = self.metrics.create_gauge(
            'active_research_sessions',
            'Number of active research sessions'
        )
        
        # Reference Intelligence metrics
        self.source_queries = self.metrics.create_counter(
            'reference_source_queries_total',
            'Total queries to each reference source',
            ['source', 'status']
        )
        
        self.deduplication_efficiency = self.metrics.create_histogram(
            'deduplication_efficiency',
            'Percentage of duplicates removed',
            ['strategy'],
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        )
        
        self.aggregation_duration = self.metrics.create_histogram(
            'aggregation_duration_seconds',
            'Time taken to aggregate from multiple sources',
            ['aggregate_strategy'],
            buckets=[1, 5, 10, 20, 30, 60]
        )
    
    @trace_async("enhanced_research_coordination")
    async def coordinate_research(
        self, 
        query: str, 
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Coordinate research with full A2A-MCP enhancements and Reference Intelligence.
        
        Args:
            query: Research query
            config: Optional configuration overrides
            
        Returns:
            Enhanced research results with quality validation and multi-source data
        """
        start_time = datetime.now()
        self.active_sessions.inc()
        
        try:
            # Apply default config
            config = config or {}
            aggregate_sources = config.get("aggregate_sources", True)
            quality_validation = config.get("quality_validation", True)
            
            # Execute base research using Google ADK agent
            base_results = await self._execute_adk_research(query)
            
            # Enhance with multi-source aggregation if enabled
            if aggregate_sources:
                aggregated_results = await self._aggregate_from_sources(query, config)
                base_results = self._merge_results(base_results, aggregated_results)
            
            # Apply quality validation if enabled
            if quality_validation:
                quality_result = await self._validate_research_quality(base_results)
                base_results["quality_validation"] = quality_result
            
            # Track performance
            duration = (datetime.now() - start_time).total_seconds()
            self.literature_search_duration.observe(
                duration,
                labels={'agent': 'orchestrator', 'search_type': 'comprehensive'}
            )
            
            # Record session metrics
            self._record_research_metrics(base_results)
            
            # Format response
            return {
                "success": True,
                "query": query,
                "results": base_results,
                "metadata": {
                    "orchestrator": "a2a_enhanced",
                    "duration": duration,
                    "sources_used": list(self.source_performance.keys()),
                    "quality_validated": quality_validation,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Research coordination error: {e}")
            record_metric("research_coordination_errors", 1)
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
        finally:
            self.active_sessions.dec()
    
    async def _execute_adk_research(self, query: str) -> Dict[str, Any]:
        """Execute research using base Google ADK agent."""
        # Use existing callbacks
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        
        runner = Runner(
            agent=self.adk_agent,
            app_name="Enhanced Research",
            session_service=InMemorySessionService(),
            before_agent_callback=research_progress_callback,
            after_agent_callback=save_research_state_callback
        )
        
        # Execute and collect results
        results = []
        async for event in runner.run_async(
            user_id="enhanced_orchestrator",
            session_id=f"research_{datetime.now().timestamp()}",
            new_message={"role": "user", "content": query}
        ):
            if event.is_final_response():
                results.append(event.content)
        
        # Parse and return results
        if results:
            return self._parse_adk_results(results[-1])
        return {"papers": [], "insights": []}
    
    async def _aggregate_from_sources(
        self, 
        query: str, 
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Aggregate papers from multiple sources using Reference Intelligence."""
        aggregate_config = {
            "strategy": config.get("aggregate_strategy", "quality_weighted"),
            "max_results_per_source": config.get("max_per_source", 20),
            "filters": config.get("filters", {})
        }
        
        # Use Reference Intelligence to aggregate
        aggregated = await self.reference_service.aggregate_papers(
            query=query,
            sources=["arxiv", "semantic_scholar", "mcp_scholarly"],
            config=aggregate_config
        )
        
        # Track source performance
        for source, performance in aggregated.get("source_metrics", {}).items():
            self.source_performance[source] = performance
            self.source_queries.inc(
                labels={'source': source, 'status': 'success' if performance['success'] else 'failed'}
            )
        
        # Record deduplication metrics
        if "deduplication_stats" in aggregated:
            stats = aggregated["deduplication_stats"]
            efficiency = stats.get("duplicates_removed", 0) / max(stats.get("total_before", 1), 1)
            self.deduplication_efficiency.observe(
                efficiency,
                labels={'strategy': aggregate_config["strategy"]}
            )
        
        return aggregated
    
    async def research_with_multi_source(
        self, 
        query: str,
        sources: Optional[List[str]] = None,
        aggregate_strategy: str = "quality_weighted"
    ) -> Dict[str, Any]:
        """
        Research with explicit multi-source aggregation.
        
        Args:
            query: Research query
            sources: List of sources to use (defaults to all enabled)
            aggregate_strategy: How to combine results
            
        Returns:
            Multi-source research results
        """
        start_time = datetime.now()
        
        # Configure sources
        if sources:
            config = self.reference_service.config.copy()
            for source in config["sources"]:
                config["sources"][source] = source in sources
            self.reference_service.config = config
        
        # Execute aggregation
        results = await self.reference_service.aggregate_papers(
            query=query,
            sources=sources or ["arxiv", "semantic_scholar", "mcp_scholarly"],
            config={"strategy": aggregate_strategy}
        )
        
        # Track aggregation time
        duration = (datetime.now() - start_time).total_seconds()
        self.aggregation_duration.observe(
            duration,
            labels={'aggregate_strategy': aggregate_strategy}
        )
        
        # Apply quality validation
        if results.get("papers"):
            quality_result = await self._validate_research_quality(results)
            results["quality_validation"] = quality_result
        
        return {
            "query": query,
            "strategy": aggregate_strategy,
            "sources_used": sources or list(self.reference_service.config["sources"].keys()),
            "results": results,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
    
    async def search_with_filters(
        self,
        query: str,
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Search with advanced filtering across sources.
        
        Args:
            query: Search query
            filters: Filter criteria (year, citations, keywords, etc.)
            
        Returns:
            Filtered research results
        """
        # Apply filters through Reference Intelligence
        config = {
            "filters": filters,
            "strategy": "filtered_search",
            "deduplication": True
        }
        
        results = await self.reference_service.aggregate_papers(
            query=query,
            sources=filters.get("sources", ["arxiv", "semantic_scholar"]),
            config=config
        )
        
        # Log filter effectiveness
        total_before = sum(m.get("total_found", 0) for m in results.get("source_metrics", {}).values())
        total_after = len(results.get("papers", []))
        
        logger.info(f"Filter effectiveness: {total_after}/{total_before} papers passed filters")
        
        return {
            "query": query,
            "filters": filters,
            "results": results,
            "filter_stats": {
                "total_found": total_before,
                "after_filtering": total_after,
                "filter_rate": (total_before - total_after) / max(total_before, 1)
            }
        }
    
    def _merge_results(
        self, 
        base_results: Dict[str, Any], 
        aggregated_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge base ADK results with aggregated multi-source results."""
        # Combine papers, removing duplicates
        all_papers = base_results.get("papers", []) + aggregated_results.get("papers", [])
        
        # Deduplicate by DOI/title
        seen = set()
        unique_papers = []
        for paper in all_papers:
            key = paper.get("doi") or paper.get("title", "")
            if key and key not in seen:
                seen.add(key)
                unique_papers.append(paper)
        
        # Merge insights
        all_insights = (
            base_results.get("insights", []) + 
            aggregated_results.get("key_insights", [])
        )
        
        return {
            "papers": unique_papers,
            "insights": list(set(all_insights)),  # Remove duplicate insights
            "total_sources": len(self.source_performance),
            "aggregation_metadata": aggregated_results.get("metadata", {})
        }
    
    async def _validate_research_quality(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Apply academic quality validation to research results."""
        # Calculate quality metrics
        papers = results.get("papers", [])
        
        quality_metrics = {
            "research_confidence": self._calculate_confidence(papers),
            "evidence_quality": self._assess_evidence_quality(papers),
            "methodological_rigor": self._evaluate_methodology(papers),
            "citation_quality": self._assess_citations(papers),
            "bias_mitigation": self._check_bias_coverage(papers),
            "reproducibility": self._evaluate_reproducibility(papers),
            "domain_coverage": len(set(p.get("domain", "unknown") for p in papers))
        }
        
        # Record quality metrics
        for metric, score in quality_metrics.items():
            self.research_quality.observe(
                score if isinstance(score, (int, float)) else 0,
                labels={'domain_metric': metric}
            )
        
        # Validate against thresholds
        if self.quality_framework:
            validation_result = await self.quality_framework.validate_response(
                quality_metrics,
                "research_output"
            )
            
            return {
                "quality_approved": validation_result.get("quality_approved", True),
                "overall_score": validation_result.get("overall_score", 0.0),
                "metrics": quality_metrics,
                "recommendations": validation_result.get("recommendations", [])
            }
        
        return {"metrics": quality_metrics}
    
    def _calculate_confidence(self, papers: List[Dict[str, Any]]) -> float:
        """Calculate research confidence based on paper quality and quantity."""
        if not papers:
            return 0.0
        
        # Factors: citation count, peer review, recent publications
        confidence_scores = []
        for paper in papers:
            score = 0.0
            score += min(paper.get("citation_count", 0) / 100, 0.4)  # Up to 0.4
            score += 0.3 if paper.get("peer_reviewed", False) else 0.0
            score += 0.3 if paper.get("year", 0) >= 2020 else 0.1
            confidence_scores.append(score)
        
        return sum(confidence_scores) / len(confidence_scores)
    
    def _assess_evidence_quality(self, papers: List[Dict[str, Any]]) -> float:
        """Assess quality of evidence in papers."""
        if not papers:
            return 0.0
        
        quality_indicators = ["methodology", "sample_size", "statistical_analysis", "reproducible"]
        scores = []
        
        for paper in papers:
            indicators_present = sum(1 for ind in quality_indicators if paper.get(ind))
            scores.append(indicators_present / len(quality_indicators))
        
        return sum(scores) / len(scores)
    
    def _evaluate_methodology(self, papers: List[Dict[str, Any]]) -> float:
        """Evaluate methodological rigor across papers."""
        if not papers:
            return 0.0
        
        methodology_scores = []
        for paper in papers:
            method_type = paper.get("methodology_type", "unknown")
            if method_type in ["experimental", "meta_analysis"]:
                methodology_scores.append(0.9)
            elif method_type in ["observational", "computational"]:
                methodology_scores.append(0.7)
            else:
                methodology_scores.append(0.5)
        
        return sum(methodology_scores) / len(methodology_scores)
    
    def _assess_citations(self, papers: List[Dict[str, Any]]) -> float:
        """Assess citation quality and network."""
        if not papers:
            return 0.0
        
        # Check for highly cited papers and citation diversity
        citation_counts = [p.get("citation_count", 0) for p in papers]
        if not citation_counts:
            return 0.0
        
        avg_citations = sum(citation_counts) / len(citation_counts)
        has_highly_cited = any(c > 100 for c in citation_counts)
        
        score = min(avg_citations / 50, 0.7)  # Up to 0.7 based on average
        if has_highly_cited:
            score += 0.3
        
        return min(score, 1.0)
    
    def _check_bias_coverage(self, papers: List[Dict[str, Any]]) -> float:
        """Check for bias mitigation through diverse sources."""
        if not papers:
            return 0.0
        
        # Check diversity of: authors, institutions, countries, years
        unique_institutions = set()
        unique_countries = set()
        year_range = set()
        
        for paper in papers:
            if "institution" in paper:
                unique_institutions.add(paper["institution"])
            if "country" in paper:
                unique_countries.add(paper["country"])
            if "year" in paper:
                year_range.add(paper["year"])
        
        diversity_score = 0.0
        diversity_score += min(len(unique_institutions) / 10, 0.3)
        diversity_score += min(len(unique_countries) / 5, 0.3)
        diversity_score += min(len(year_range) / 5, 0.4)
        
        return diversity_score
    
    def _evaluate_reproducibility(self, papers: List[Dict[str, Any]]) -> float:
        """Evaluate reproducibility indicators."""
        if not papers:
            return 0.0
        
        reproducibility_indicators = [
            "code_available", "data_available", "preregistered", 
            "materials_available", "protocol_shared"
        ]
        
        scores = []
        for paper in papers:
            indicators = sum(1 for ind in reproducibility_indicators if paper.get(ind, False))
            scores.append(indicators / len(reproducibility_indicators))
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _record_research_metrics(self, results: Dict[str, Any]):
        """Record comprehensive research metrics."""
        # Count papers by status
        papers = results.get("papers", [])
        self.papers_analyzed.inc(
            value=len(papers),
            labels={'agent': 'orchestrator', 'status': 'completed'}
        )
        
        # Log summary
        logger.info(f"Research completed: {len(papers)} papers, "
                   f"{len(results.get('insights', []))} insights")
    
    def _parse_adk_results(self, raw_results: Any) -> Dict[str, Any]:
        """Parse results from Google ADK agent."""
        if isinstance(raw_results, dict):
            return raw_results
        elif isinstance(raw_results, str):
            try:
                return json.loads(raw_results)
            except:
                return {"papers": [], "insights": [raw_results]}
        else:
            return {"papers": [], "insights": []}
    
    async def stream_research_with_artifacts(
        self,
        query: str,
        stream_callback: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Stream research results with artifacts as they become available.
        
        Args:
            query: Research query
            stream_callback: Callback for streaming updates
            
        Returns:
            Final aggregated results
        """
        # Initialize streaming response
        streaming_results = {
            "query": query,
            "papers": [],
            "insights": [],
            "artifacts": [],
            "status": "in_progress"
        }
        
        # Stream from each source
        sources = ["arxiv", "semantic_scholar", "mcp_scholarly"]
        for source in sources:
            if stream_callback:
                await stream_callback({
                    "type": "source_start",
                    "source": source,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Query source
            try:
                source_results = await self.reference_service.search_single_source(
                    source, query
                )
                
                # Add papers incrementally
                new_papers = source_results.get("papers", [])
                streaming_results["papers"].extend(new_papers)
                
                if stream_callback:
                    await stream_callback({
                        "type": "papers_found",
                        "source": source,
                        "count": len(new_papers),
                        "papers": new_papers[:5]  # First 5 as preview
                    })
                
            except Exception as e:
                logger.error(f"Error streaming from {source}: {e}")
                if stream_callback:
                    await stream_callback({
                        "type": "source_error",
                        "source": source,
                        "error": str(e)
                    })
        
        # Final deduplication and ranking
        streaming_results = self.reference_service._deduplicate_papers(
            streaming_results["papers"]
        )
        
        streaming_results["status"] = "completed"
        return streaming_results


# Convenience function to create orchestrator instance
def create_enhanced_orchestrator() -> A2AEnhancedOrchestrator:
    """Create and return an enhanced orchestrator instance."""
    return A2AEnhancedOrchestrator()