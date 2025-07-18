"""
ABOUTME: A2A-MCP enhanced literature review agent with citation tracking
ABOUTME: Adds citation network analysis and reference tracking to existing agent
"""

import os
import logging
import asyncio
import re
from typing import Dict, Any, Optional, List, Set
from datetime import datetime
import json

# A2A-MCP Framework imports
import sys
sys.path.append('/Users/mac/Agents/agentic_5/src')
from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.common.citation_tracker import CitationTracker
from a2a_mcp.common.quality_framework import QualityDomain
from a2a_mcp.common.metrics_collector import MetricsCollector
from a2a_mcp.common.observability import trace_async, record_metric
from a2a_mcp.common.response_formatter import ResponseFormatter, create_agent_error

# Import existing agent
from .agent import literature_review_agent

logger = logging.getLogger(__name__)


class A2ALiteratureReviewAgent(StandardizedAgentBase):
    """
    Enhanced literature review agent with citation tracking and network analysis.
    
    Features:
    - Citation tracking with DOI resolution
    - Citation network visualization
    - Cross-reference validation
    - Impact analysis based on citations
    - Quality validation for literature reviews
    """
    
    def __init__(self):
        """Initialize enhanced literature review agent."""
        super().__init__(
            agent_name="A2A Literature Review Agent",
            description="Enhanced literature review with citation tracking",
            instructions="""You are an advanced literature review specialist with citation tracking.
            
            Your enhanced capabilities include:
            - Track citations with full metadata and provenance
            - Build citation networks showing paper relationships
            - Validate cross-references and detect missing citations
            - Calculate citation impact and h-index metrics
            - Identify highly cited seminal works
            - Track citation trends over time
            - Detect self-citations and citation rings
            - Generate citation quality reports
            """,
            quality_config={
                "domain": QualityDomain.ACADEMIC,
                "enabled": True,
                "thresholds": {
                    "citation_completeness": {"min_value": 0.85, "weight": 1.3},
                    "reference_accuracy": {"min_value": 0.9, "weight": 1.2},
                    "source_diversity": {"min_value": 0.7, "weight": 1.0},
                    "temporal_coverage": {"min_value": 0.75, "weight": 0.9},
                    "impact_factor": {"min_value": 0.6, "weight": 1.1}
                }
            },
            mcp_tools_enabled=True,
            a2a_enabled=True
        )
        
        # Preserve existing Google ADK agent
        self.adk_agent = literature_review_agent
        
        # Initialize citation tracker
        self.citation_tracker = CitationTracker()
        
        # Initialize metrics
        self.metrics = MetricsCollector(
            namespace="literature_review",
            subsystem="citations"
        )
        self._init_citation_metrics()
        
        # Citation analysis cache
        self.citation_cache = {}
        self.network_cache = {}
        
        logger.info("A2A Literature Review Agent initialized with citation tracking")
    
    def extract_structured_content(self, response: str) -> Dict[str, Any]:
        """
        Extract structured content from LLM responses using pattern matching.
        
        This method handles:
        - Code blocks (algorithms, equations, etc.)
        - JSON data structures
        - Tool outputs from MCP tools
        
        Args:
            response: Raw response from LLM
            
        Returns:
            Dict containing extracted content and metadata
        """
        extracted_content = {
            "raw_response": response,
            "code_blocks": [],
            "json_blocks": [],
            "tool_outputs": [],
            "plain_text": response  # Default to full response
        }
        
        # Pattern definitions
        patterns = {
            "code": r'```\n(.*?)\n```',              # Generic code blocks
            "json": r'```json\s*(.*?)\s*```',        # JSON blocks
            "tool": r'```tool_outputs\s*(.*?)\s*```', # Tool output blocks
            "python": r'```python\s*(.*?)\s*```',     # Python code
            "equation": r'```equation\s*(.*?)\s*```',  # Mathematical equations
        }
        
        # Extract each pattern type
        for pattern_type, pattern in patterns.items():
            matches = re.findall(pattern, response, re.DOTALL)
            
            for match in matches:
                if pattern_type == "json":
                    try:
                        # Parse JSON and add to json_blocks
                        parsed_json = json.loads(match)
                        extracted_content["json_blocks"].append({
                            "type": "json",
                            "content": parsed_json,
                            "raw": match
                        })
                    except json.JSONDecodeError:
                        # If not valid JSON, treat as code
                        extracted_content["code_blocks"].append({
                            "type": "json_invalid",
                            "content": match
                        })
                
                elif pattern_type == "tool":
                    # Tool outputs might be JSON or structured text
                    try:
                        parsed_tool = json.loads(match)
                        extracted_content["tool_outputs"].append({
                            "type": "tool_json",
                            "content": parsed_tool,
                            "raw": match
                        })
                    except:
                        extracted_content["tool_outputs"].append({
                            "type": "tool_text",
                            "content": match
                        })
                
                elif pattern_type in ["code", "python", "equation"]:
                    extracted_content["code_blocks"].append({
                        "type": pattern_type,
                        "content": match,
                        "language": pattern_type if pattern_type != "code" else "generic"
                    })
        
        # Remove all extracted blocks from plain_text
        plain_text = response
        for pattern in patterns.values():
            plain_text = re.sub(pattern, "[EXTRACTED_CONTENT]", plain_text, flags=re.DOTALL)
        
        extracted_content["plain_text"] = plain_text.strip()
        
        # Add extraction metadata
        extracted_content["metadata"] = {
            "total_code_blocks": len(extracted_content["code_blocks"]),
            "total_json_blocks": len(extracted_content["json_blocks"]),
            "total_tool_outputs": len(extracted_content["tool_outputs"]),
            "has_structured_content": bool(
                extracted_content["code_blocks"] or 
                extracted_content["json_blocks"] or 
                extracted_content["tool_outputs"]
            )
        }
        
        return extracted_content
    
    def _init_citation_metrics(self):
        """Initialize citation-specific metrics."""
        # Citation tracking metrics
        self.citations_tracked = self.metrics.create_counter(
            'citations_tracked_total',
            'Total citations tracked by source',
            ['source', 'citation_type']
        )
        
        self.citation_depth = self.metrics.create_histogram(
            'citation_network_depth',
            'Depth of citation networks analyzed',
            ['topic'],
            buckets=[1, 2, 3, 5, 10, 20, 50]
        )
        
        self.doi_resolution = self.metrics.create_counter(
            'doi_resolution_total',
            'DOI resolution attempts',
            ['status', 'source']
        )
        
        self.citation_quality = self.metrics.create_histogram(
            'citation_quality_score',
            'Quality scores for citations',
            ['quality_metric'],
            buckets=[0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0]
        )
    
    @trace_async("enhanced_literature_review")
    async def review_with_citations(
        self, 
        query: str, 
        max_papers: int = 50,
        citation_depth: int = 2,
        include_network: bool = True
    ) -> Dict[str, Any]:
        """
        Perform literature review with enhanced citation tracking.
        
        Args:
            query: Research query
            max_papers: Maximum papers to analyze
            citation_depth: How deep to follow citations (1-3)
            include_network: Whether to build citation network
            
        Returns:
            Enhanced review results with citation analysis
        """
        start_time = datetime.now()
        
        # Execute base literature review
        base_results = await self._execute_base_review(query, max_papers)
        
        # Extract and track citations
        papers_with_citations = await self._track_paper_citations(
            base_results.get("papers", [])
        )
        
        # Build citation network if requested
        citation_network = None
        if include_network:
            citation_network = await self._build_citation_network(
                papers_with_citations, 
                citation_depth
            )
        
        # Analyze citation patterns
        citation_analysis = self._analyze_citation_patterns(
            papers_with_citations,
            citation_network
        )
        
        # Apply citation-aware quality validation
        quality_result = await self._validate_citation_quality(
            papers_with_citations,
            citation_analysis
        )
        
        # Record metrics
        duration = (datetime.now() - start_time).total_seconds()
        self.citation_depth.observe(
            citation_depth,
            labels={'topic': query[:50]}
        )
        
        return {
            "query": query,
            "total_papers": len(papers_with_citations),
            "papers": papers_with_citations,
            "citation_analysis": citation_analysis,
            "citation_network": citation_network,
            "quality_validation": quality_result,
            "execution_time": duration,
            "metadata": {
                "agent": "a2a_literature_review",
                "citation_depth": citation_depth,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    async def _execute_base_review(self, query: str, max_papers: int) -> Dict[str, Any]:
        """Execute literature review using base ADK agent with response formatting."""
        try:
            # Use existing ADK agent
            from google.adk.runners import Runner
            from google.adk.sessions import InMemorySessionService
            
            runner = Runner(
                agent=self.adk_agent,
                app_name="Literature Review",
                session_service=InMemorySessionService()
            )
            
            # Execute review
            results = []
            raw_responses = []
            async for event in runner.run_async(
                user_id="citation_analysis",
                session_id=f"review_{datetime.now().timestamp()}",
                new_message={"role": "user", "content": f"Review papers on: {query}. Limit: {max_papers}"}
            ):
                if event.is_final_response():
                    results.append(event.content)
                    raw_responses.append(event.content)
            
            # Process and format results
            if results:
                # Extract structured content from response
                raw_response = results[-1] if isinstance(results[-1], str) else json.dumps(results[-1])
                extracted = self.extract_structured_content(raw_response)
                
                # Try to get parsed result
                parsed_result = None
                if extracted["json_blocks"]:
                    # Use first valid JSON block
                    parsed_result = extracted["json_blocks"][0]["content"]
                else:
                    # Try to parse the whole response as JSON
                    try:
                        parsed_result = json.loads(raw_response)
                    except:
                        # Extract papers from plain text if possible
                        parsed_result = self._extract_papers_from_text(extracted["plain_text"])
                
                # Use ResponseFormatter to standardize the output
                formatted_response = ResponseFormatter.standardize_response_format(
                    content=parsed_result,
                    is_interactive=False,
                    is_complete=True,
                    agent_name=self.agent_name,
                    metadata={
                        "extraction_info": extracted["metadata"],
                        "has_code_snippets": len(extracted["code_blocks"]) > 0,
                        "has_tool_outputs": len(extracted["tool_outputs"]) > 0
                    }
                )
                
                # Return the formatted content
                return formatted_response.get("content", {"papers": []})
                
        except Exception as e:
            logger.error(f"Error in base review execution: {e}")
            # Use create_agent_error for standardized error handling
            error_response = create_agent_error(
                error_message=f"Failed to execute literature review: {str(e)}",
                agent_name=self.agent_name,
                error_type="execution_error",
                context={
                    "query": query,
                    "max_papers": max_papers,
                    "error": str(e)
                }
            )
            return {"papers": [], "error": error_response}
        
        return {"papers": []}
    
    def _extract_papers_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract paper information from plain text when JSON parsing fails.
        
        This is a fallback method that attempts to identify papers
        in unstructured text responses.
        """
        papers = []
        
        # Common patterns for paper citations
        title_pattern = r'(?:Title|Paper):\s*"?([^"\n]+)"?'
        author_pattern = r'(?:Authors?|By):\s*([^\n]+)'
        year_pattern = r'(?:Year|Published):\s*(\d{4})'
        doi_pattern = r'(?:DOI|doi):\s*([^\s\n]+)'
        
        # Try to find paper blocks
        paper_blocks = re.split(r'\n\s*\n', text)
        
        for block in paper_blocks:
            paper = {}
            
            # Extract title
            title_match = re.search(title_pattern, block, re.IGNORECASE)
            if title_match:
                paper["title"] = title_match.group(1).strip()
            
            # Extract authors
            author_match = re.search(author_pattern, block, re.IGNORECASE)
            if author_match:
                authors_text = author_match.group(1).strip()
                # Split by common delimiters
                authors = re.split(r'[,;&]|\sand\s', authors_text)
                paper["authors"] = [a.strip() for a in authors if a.strip()]
            
            # Extract year
            year_match = re.search(year_pattern, block, re.IGNORECASE)
            if year_match:
                paper["year"] = int(year_match.group(1))
            
            # Extract DOI
            doi_match = re.search(doi_pattern, block, re.IGNORECASE)
            if doi_match:
                paper["doi"] = doi_match.group(1).strip()
            
            # Only add if we found at least a title
            if paper.get("title"):
                papers.append(paper)
        
        return {"papers": papers}
    
    async def _track_paper_citations(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Track citations for all papers."""
        enhanced_papers = []
        
        for paper in papers:
            # Track citation with full metadata
            citation_data = self.citation_tracker.track_citation(
                paper,
                source="literature_review"
            )
            
            # Enhance paper with citation data
            enhanced_paper = {**paper}
            enhanced_paper["citation_data"] = citation_data
            
            # Track forward and backward citations
            if "references" in paper:
                enhanced_paper["backward_citations"] = await self._track_references(
                    paper["references"]
                )
            
            if "cited_by" in paper:
                enhanced_paper["forward_citations"] = await self._track_citations(
                    paper["cited_by"]
                )
            
            enhanced_papers.append(enhanced_paper)
            
            # Record metrics
            self.citations_tracked.inc(labels={
                'source': paper.get('source', 'unknown'),
                'citation_type': 'primary'
            })
        
        return enhanced_papers
    
    async def _track_references(self, references: List[Any]) -> List[Dict[str, Any]]:
        """Track backward citations (references)."""
        tracked_refs = []
        
        for ref in references:
            if isinstance(ref, dict):
                citation = self.citation_tracker.track_citation(
                    ref,
                    source="reference"
                )
                tracked_refs.append(citation)
                
                self.citations_tracked.inc(labels={
                    'source': 'reference',
                    'citation_type': 'backward'
                })
        
        return tracked_refs
    
    async def _track_citations(self, citations: List[Any]) -> List[Dict[str, Any]]:
        """Track forward citations (papers citing this work)."""
        tracked_citations = []
        
        for cite in citations:
            if isinstance(cite, dict):
                citation = self.citation_tracker.track_citation(
                    cite,
                    source="citation"
                )
                tracked_citations.append(citation)
                
                self.citations_tracked.inc(labels={
                    'source': 'citation',
                    'citation_type': 'forward'
                })
        
        return tracked_citations
    
    async def _build_citation_network(
        self, 
        papers: List[Dict[str, Any]], 
        max_depth: int
    ) -> Dict[str, Any]:
        """Build citation network graph."""
        network = {
            "nodes": [],
            "edges": [],
            "metrics": {}
        }
        
        # Create nodes for papers
        paper_ids = set()
        for paper in papers:
            node = {
                "id": paper["citation_data"]["citation_id"],
                "title": paper.get("title", "Unknown"),
                "year": paper.get("year"),
                "citation_count": paper.get("citation_count", 0),
                "type": "primary"
            }
            network["nodes"].append(node)
            paper_ids.add(node["id"])
        
        # Add citation edges
        for paper in papers:
            source_id = paper["citation_data"]["citation_id"]
            
            # Backward citations (references)
            for ref in paper.get("backward_citations", []):
                target_id = ref["citation_id"]
                if target_id not in paper_ids:
                    # Add reference node
                    network["nodes"].append({
                        "id": target_id,
                        "title": ref.get("title", "Reference"),
                        "year": ref.get("year"),
                        "type": "reference"
                    })
                    paper_ids.add(target_id)
                
                network["edges"].append({
                    "source": source_id,
                    "target": target_id,
                    "type": "cites"
                })
            
            # Forward citations
            for cite in paper.get("forward_citations", []):
                source_cite_id = cite["citation_id"]
                if source_cite_id not in paper_ids:
                    # Add citing paper node
                    network["nodes"].append({
                        "id": source_cite_id,
                        "title": cite.get("title", "Citing Paper"),
                        "year": cite.get("year"),
                        "type": "citing"
                    })
                    paper_ids.add(source_cite_id)
                
                network["edges"].append({
                    "source": source_cite_id,
                    "target": source_id,
                    "type": "cites"
                })
        
        # Calculate network metrics
        network["metrics"] = {
            "total_nodes": len(network["nodes"]),
            "total_edges": len(network["edges"]),
            "primary_papers": len([n for n in network["nodes"] if n["type"] == "primary"]),
            "max_citation_count": max((n.get("citation_count", 0) for n in network["nodes"]), default=0)
        }
        
        return network
    
    def _analyze_citation_patterns(
        self, 
        papers: List[Dict[str, Any]],
        network: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze citation patterns and metrics."""
        analysis = {
            "total_papers": len(papers),
            "total_citations": 0,
            "average_citations": 0,
            "h_index": 0,
            "most_cited": None,
            "citation_distribution": {},
            "temporal_analysis": {},
            "source_diversity": {}
        }
        
        # Citation counts
        citation_counts = []
        for paper in papers:
            count = paper.get("citation_count", 0)
            citation_counts.append(count)
            analysis["total_citations"] += count
            
            # Track source diversity
            source = paper.get("source", "unknown")
            analysis["source_diversity"][source] = analysis["source_diversity"].get(source, 0) + 1
        
        # Calculate metrics
        if citation_counts:
            analysis["average_citations"] = analysis["total_citations"] / len(citation_counts)
            
            # H-index calculation
            citation_counts.sort(reverse=True)
            h_index = 0
            for i, count in enumerate(citation_counts):
                if count >= i + 1:
                    h_index = i + 1
                else:
                    break
            analysis["h_index"] = h_index
            
            # Most cited paper
            if papers:
                most_cited = max(papers, key=lambda p: p.get("citation_count", 0))
                analysis["most_cited"] = {
                    "title": most_cited.get("title", "Unknown"),
                    "citations": most_cited.get("citation_count", 0),
                    "year": most_cited.get("year")
                }
        
        # Citation distribution
        ranges = [(0, 10), (10, 50), (50, 100), (100, 500), (500, float('inf'))]
        for min_val, max_val in ranges:
            key = f"{min_val}-{max_val if max_val != float('inf') else '500+'}"
            analysis["citation_distribution"][key] = sum(
                1 for c in citation_counts if min_val <= c < max_val
            )
        
        # Temporal analysis
        for paper in papers:
            year = paper.get("year")
            if year:
                analysis["temporal_analysis"][str(year)] = analysis["temporal_analysis"].get(str(year), 0) + 1
        
        return analysis
    
    async def _validate_citation_quality(
        self, 
        papers: List[Dict[str, Any]],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate citation quality metrics."""
        quality_metrics = {
            "citation_completeness": self._calculate_citation_completeness(papers),
            "reference_accuracy": self._assess_reference_accuracy(papers),
            "source_diversity": self._calculate_source_diversity(analysis),
            "temporal_coverage": self._assess_temporal_coverage(analysis),
            "impact_factor": self._calculate_impact_factor(analysis)
        }
        
        # Record quality metrics
        for metric, score in quality_metrics.items():
            self.citation_quality.observe(
                score,
                labels={'quality_metric': metric}
            )
        
        # Validate against thresholds
        if self.quality_framework:
            validation_result = await self.quality_framework.validate_response(
                quality_metrics,
                "citation_analysis"
            )
            
            return {
                "quality_approved": validation_result.get("quality_approved", True),
                "overall_score": validation_result.get("overall_score", 0.0),
                "scores": quality_metrics,
                "issues": validation_result.get("quality_issues", [])
            }
        
        return {"scores": quality_metrics}
    
    def _calculate_citation_completeness(self, papers: List[Dict[str, Any]]) -> float:
        """Calculate how complete citation data is."""
        if not papers:
            return 0.0
        
        complete_count = 0
        for paper in papers:
            # Check for essential citation data
            has_doi = bool(paper.get("doi"))
            has_citations = "citation_count" in paper
            has_references = "references" in paper or "backward_citations" in paper
            
            if has_doi and has_citations and has_references:
                complete_count += 1
        
        return complete_count / len(papers)
    
    def _assess_reference_accuracy(self, papers: List[Dict[str, Any]]) -> float:
        """Assess accuracy of references."""
        # Check for DOI resolution success
        total_refs = 0
        resolved_refs = 0
        
        for paper in papers:
            refs = paper.get("backward_citations", [])
            total_refs += len(refs)
            resolved_refs += sum(1 for ref in refs if ref.get("doi"))
        
        if total_refs == 0:
            return 0.8  # Default score
        
        return resolved_refs / total_refs
    
    def _calculate_source_diversity(self, analysis: Dict[str, Any]) -> float:
        """Calculate diversity of sources."""
        sources = analysis.get("source_diversity", {})
        if not sources:
            return 0.0
        
        # Shannon diversity index
        total = sum(sources.values())
        if total == 0:
            return 0.0
        
        diversity = 0
        for count in sources.values():
            if count > 0:
                p = count / total
                diversity -= p * (p if p > 0 else 0)
        
        # Normalize to 0-1 range
        max_diversity = -((1/len(sources)) * len(sources)) if len(sources) > 1 else 0
        return diversity / max_diversity if max_diversity != 0 else 0
    
    def _assess_temporal_coverage(self, analysis: Dict[str, Any]) -> float:
        """Assess temporal coverage of citations."""
        temporal = analysis.get("temporal_analysis", {})
        if not temporal:
            return 0.0
        
        years = [int(y) for y in temporal.keys() if y.isdigit()]
        if not years:
            return 0.0
        
        # Check coverage of recent years
        current_year = datetime.now().year
        recent_years = set(range(current_year - 5, current_year + 1))
        covered_years = set(years) & recent_years
        
        return len(covered_years) / len(recent_years)
    
    def _calculate_impact_factor(self, analysis: Dict[str, Any]) -> float:
        """Calculate normalized impact factor."""
        avg_citations = analysis.get("average_citations", 0)
        h_index = analysis.get("h_index", 0)
        
        # Normalize based on field averages (simplified)
        normalized_citations = min(avg_citations / 50, 1.0)  # 50 as field average
        normalized_h = min(h_index / 20, 1.0)  # 20 as good h-index
        
        return (normalized_citations + normalized_h) / 2
    
    async def find_seminal_works(self, papers: List[Dict[str, Any]], threshold: int = 100) -> List[Dict[str, Any]]:
        """Identify seminal works based on citation count."""
        seminal = []
        
        for paper in papers:
            if paper.get("citation_count", 0) >= threshold:
                seminal.append({
                    "title": paper.get("title"),
                    "authors": paper.get("authors", []),
                    "year": paper.get("year"),
                    "citations": paper.get("citation_count"),
                    "doi": paper.get("doi"),
                    "significance": "seminal_work"
                })
        
        # Sort by citation count
        seminal.sort(key=lambda x: x["citations"], reverse=True)
        
        return seminal
    
    def generate_citation_report(self, review_results: Dict[str, Any]) -> str:
        """Generate human-readable citation analysis report."""
        analysis = review_results.get("citation_analysis", {})
        quality = review_results.get("quality_validation", {})
        
        report = f"""
# Citation Analysis Report

## Overview
- Total Papers Analyzed: {analysis.get('total_papers', 0)}
- Total Citations: {analysis.get('total_citations', 0)}
- Average Citations per Paper: {analysis.get('average_citations', 0):.1f}
- H-Index: {analysis.get('h_index', 0)}

## Most Cited Work
{self._format_most_cited(analysis.get('most_cited'))}

## Citation Distribution
{self._format_distribution(analysis.get('citation_distribution', {}))}

## Temporal Coverage
{self._format_temporal(analysis.get('temporal_analysis', {}))}

## Source Diversity
{self._format_sources(analysis.get('source_diversity', {}))}

## Quality Assessment
- Overall Quality Score: {quality.get('overall_score', 0):.2f}
- Citation Completeness: {quality.get('scores', {}).get('citation_completeness', 0):.2f}
- Reference Accuracy: {quality.get('scores', {}).get('reference_accuracy', 0):.2f}
- Source Diversity: {quality.get('scores', {}).get('source_diversity', 0):.2f}
- Temporal Coverage: {quality.get('scores', {}).get('temporal_coverage', 0):.2f}
- Impact Factor: {quality.get('scores', {}).get('impact_factor', 0):.2f}

## Quality Issues
{self._format_issues(quality.get('issues', []))}
"""
        return report
    
    def _format_most_cited(self, most_cited: Optional[Dict[str, Any]]) -> str:
        """Format most cited paper."""
        if not most_cited:
            return "No citation data available"
        
        return f"""Title: {most_cited.get('title', 'Unknown')}
Year: {most_cited.get('year', 'Unknown')}
Citations: {most_cited.get('citations', 0)}"""
    
    def _format_distribution(self, distribution: Dict[str, int]) -> str:
        """Format citation distribution."""
        lines = []
        for range_key, count in sorted(distribution.items()):
            lines.append(f"- {range_key} citations: {count} papers")
        return "\n".join(lines) if lines else "No distribution data"
    
    def _format_temporal(self, temporal: Dict[str, int]) -> str:
        """Format temporal distribution."""
        if not temporal:
            return "No temporal data"
        
        sorted_years = sorted(temporal.items(), reverse=True)[:5]
        lines = [f"- {year}: {count} papers" for year, count in sorted_years]
        return "\n".join(lines)
    
    def _format_sources(self, sources: Dict[str, int]) -> str:
        """Format source distribution."""
        if not sources:
            return "No source data"
        
        sorted_sources = sorted(sources.items(), key=lambda x: x[1], reverse=True)
        lines = [f"- {source}: {count} papers" for source, count in sorted_sources[:5]]
        return "\n".join(lines)
    
    def _format_issues(self, issues: List[str]) -> str:
        """Format quality issues."""
        if not issues:
            return "No quality issues detected"
        
        return "\n".join(f"- {issue}" for issue in issues)