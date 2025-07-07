#!/usr/bin/env python3
"""Citation Tracking System for Oracle reference management."""

import logging
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import requests
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class CitationTracker:
    """Manages citation metadata, DOI resolution, and source provenance tracking."""
    
    def __init__(self):
        self.citation_cache = {}
        self.provenance_map = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'A2A-MCP-Oracle/1.0 (Research Assistant)'
        })
    
    def track_citation(self, paper: Dict, source: str) -> Dict[str, Any]:
        """Track a citation with full metadata and provenance."""
        citation_id = self._generate_citation_id(paper)
        
        citation_data = {
            "citation_id": citation_id,
            "title": paper.get("title", ""),
            "authors": paper.get("authors", []),
            "year": paper.get("year"),
            "venue": paper.get("venue"),
            "doi": paper.get("doi"),
            "url": paper.get("pdf_url") or paper.get("url"),
            "source": source,
            "citation_count": paper.get("citation_count", 0),
            "quality_score": paper.get("quality_score", 0.0),
            "tracked_at": datetime.now().isoformat(),
            "metadata": {
                "abstract": paper.get("abstract", "")[:200] + "..." if paper.get("abstract") else "",
                "keywords": self._extract_keywords(paper),
                "open_access": paper.get("is_open_access", False),
                "arxiv_id": paper.get("arxiv_id"),
                "semantic_scholar_id": paper.get("semantic_scholar_id")
            }
        }
        
        # Store in cache
        self.citation_cache[citation_id] = citation_data
        
        # Track provenance
        self._track_provenance(citation_id, source, paper)
        
        return citation_data
    
    def _generate_citation_id(self, paper: Dict) -> str:
        """Generate unique citation ID."""
        # Prefer DOI if available
        if paper.get("doi"):
            return f"doi:{paper['doi']}"
        
        # Use ArXiv ID if available
        if paper.get("arxiv_id"):
            return f"arxiv:{paper['arxiv_id']}"
        
        # Use Semantic Scholar ID if available
        if paper.get("semantic_scholar_id"):
            return f"ss:{paper['semantic_scholar_id']}"
        
        # Fallback to title hash
        title = paper.get("title", "").lower().strip()
        title_hash = hash(title) % 1000000
        return f"title_hash:{title_hash}"
    
    def _extract_keywords(self, paper: Dict) -> List[str]:
        """Extract keywords from paper metadata."""
        keywords = []
        
        # From categories (ArXiv)
        if paper.get("categories"):
            keywords.extend(paper["categories"])
        
        # From title (simple extraction)
        title = paper.get("title", "").lower()
        # Extract common research terms
        research_terms = [
            "quantum", "machine learning", "artificial intelligence", "neural network",
            "algorithm", "optimization", "simulation", "analysis", "framework",
            "methodology", "approach", "system", "model", "theory"
        ]
        
        for term in research_terms:
            if term in title:
                keywords.append(term)
        
        return list(set(keywords))  # Remove duplicates
    
    def _track_provenance(self, citation_id: str, source: str, paper: Dict):
        """Track the provenance of a citation."""
        provenance = {
            "source": source,
            "retrieved_at": datetime.now().isoformat(),
            "query_context": paper.get("query_context"),
            "domain": paper.get("domain"),
            "original_data": {
                "source_specific_id": paper.get("arxiv_id") or paper.get("semantic_scholar_id"),
                "source_url": paper.get("pdf_url") or paper.get("url"),
                "source_metadata": paper.get("source_metadata", {})
            }
        }
        
        if citation_id not in self.provenance_map:
            self.provenance_map[citation_id] = []
        
        self.provenance_map[citation_id].append(provenance)
    
    def resolve_doi(self, doi: str) -> Optional[Dict]:
        """Resolve DOI to get additional metadata."""
        if not doi:
            return None
        
        try:
            # Use CrossRef API for DOI resolution
            url = f"https://api.crossref.org/works/{doi}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                work = data.get("message", {})
                
                return {
                    "title": work.get("title", [None])[0],
                    "authors": [
                        f"{author.get('given', '')} {author.get('family', '')}"
                        for author in work.get("author", [])
                    ],
                    "published_date": work.get("published-print", {}).get("date-parts", [[None]])[0],
                    "journal": work.get("container-title", [None])[0],
                    "publisher": work.get("publisher"),
                    "url": work.get("URL"),
                    "is_referenced_by_count": work.get("is-referenced-by-count", 0),
                    "crossref_type": work.get("type")
                }
        
        except Exception as e:
            logger.warning(f"Failed to resolve DOI {doi}: {e}")
        
        return None
    
    def format_citation(self, citation_id: str, style: str = "apa") -> str:
        """Format citation in specified style."""
        if citation_id not in self.citation_cache:
            return f"[Citation {citation_id} not found]"
        
        citation = self.citation_cache[citation_id]
        
        if style.lower() == "apa":
            return self._format_apa_citation(citation)
        elif style.lower() == "ieee":
            return self._format_ieee_citation(citation)
        else:
            return self._format_plain_citation(citation)
    
    def _format_apa_citation(self, citation: Dict) -> str:
        """Format citation in APA style."""
        authors = citation.get("authors", [])
        if len(authors) == 0:
            author_str = "Unknown Author"
        elif len(authors) == 1:
            author_str = authors[0]
        elif len(authors) <= 3:
            author_str = ", ".join(authors[:-1]) + f", & {authors[-1]}"
        else:
            author_str = f"{authors[0]}, et al."
        
        year = citation.get("year", "n.d.")
        title = citation.get("title", "Untitled")
        venue = citation.get("venue", "")
        doi = citation.get("doi", "")
        
        formatted = f"{author_str} ({year}). {title}."
        
        if venue:
            formatted += f" {venue}."
        
        if doi:
            formatted += f" https://doi.org/{doi}"
        
        return formatted
    
    def _format_ieee_citation(self, citation: Dict) -> str:
        """Format citation in IEEE style."""
        authors = citation.get("authors", [])
        if len(authors) == 0:
            author_str = "Unknown Author"
        elif len(authors) <= 3:
            author_str = ", ".join(authors)
        else:
            author_str = f"{authors[0]}, et al."
        
        title = citation.get("title", "Untitled")
        venue = citation.get("venue", "")
        year = citation.get("year", "")
        doi = citation.get("doi", "")
        
        formatted = f"{author_str}, \"{title}\""
        
        if venue:
            formatted += f", {venue}"
        
        if year:
            formatted += f", {year}"
        
        if doi:
            formatted += f", doi: {doi}"
        
        formatted += "."
        return formatted
    
    def _format_plain_citation(self, citation: Dict) -> str:
        """Format citation in plain text."""
        title = citation.get("title", "Untitled")
        authors = citation.get("authors", [])
        year = citation.get("year", "Unknown year")
        source = citation.get("source", "Unknown source")
        
        author_str = ", ".join(authors[:3]) if authors else "Unknown authors"
        if len(authors) > 3:
            author_str += ", et al."
        
        return f"{title} by {author_str} ({year}) [Source: {source}]"
    
    def get_citation_statistics(self) -> Dict[str, Any]:
        """Get statistics about tracked citations."""
        if not self.citation_cache:
            return {"total_citations": 0}
        
        citations = list(self.citation_cache.values())
        
        # Source distribution
        sources = [c.get("source", "unknown") for c in citations]
        source_dist = {source: sources.count(source) for source in set(sources)}
        
        # Year distribution
        years = [c.get("year") for c in citations if c.get("year")]
        year_dist = {year: years.count(year) for year in set(years)}
        
        # Quality scores
        quality_scores = [c.get("quality_score", 0) for c in citations]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # Citation counts
        citation_counts = [c.get("citation_count", 0) for c in citations]
        total_citations = sum(citation_counts)
        avg_citations = total_citations / len(citation_counts) if citation_counts else 0
        
        return {
            "total_citations": len(citations),
            "source_distribution": source_dist,
            "year_distribution": year_dist,
            "quality_metrics": {
                "avg_quality_score": round(avg_quality, 3),
                "avg_citations_per_paper": round(avg_citations, 1),
                "total_citation_impact": total_citations
            },
            "doi_coverage": sum(1 for c in citations if c.get("doi")) / len(citations),
            "open_access_ratio": sum(1 for c in citations if c.get("metadata", {}).get("open_access")) / len(citations)
        }
    
    def export_citations(self, format: str = "json") -> str:
        """Export all tracked citations in specified format."""
        if format.lower() == "json":
            return json.dumps(self.citation_cache, indent=2)
        
        elif format.lower() == "bibtex":
            return self._export_bibtex()
        
        elif format.lower() == "csv":
            return self._export_csv()
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_bibtex(self) -> str:
        """Export citations in BibTeX format."""
        bibtex_entries = []
        
        for citation_id, citation in self.citation_cache.items():
            # Generate BibTeX key
            first_author = citation.get("authors", ["Unknown"])[0].split()[-1] if citation.get("authors") else "Unknown"
            year = citation.get("year", "XXXX")
            key = f"{first_author}{year}".replace(" ", "")
            
            # Format entry
            entry = f"@article{{{key},\n"
            entry += f"  title = {{{citation.get('title', 'Untitled')}}},\n"
            
            if citation.get("authors"):
                authors_str = " and ".join(citation["authors"])
                entry += f"  author = {{{authors_str}}},\n"
            
            if citation.get("year"):
                entry += f"  year = {{{citation['year']}}},\n"
            
            if citation.get("venue"):
                entry += f"  journal = {{{citation['venue']}}},\n"
            
            if citation.get("doi"):
                entry += f"  doi = {{{citation['doi']}}},\n"
            
            if citation.get("url"):
                entry += f"  url = {{{citation['url']}}},\n"
            
            entry += "}\n"
            bibtex_entries.append(entry)
        
        return "\n".join(bibtex_entries)
    
    def _export_csv(self) -> str:
        """Export citations in CSV format."""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "Citation ID", "Title", "Authors", "Year", "Venue", "DOI", 
            "Source", "Citation Count", "Quality Score", "Open Access"
        ])
        
        # Data rows
        for citation_id, citation in self.citation_cache.items():
            authors_str = "; ".join(citation.get("authors", []))
            writer.writerow([
                citation_id,
                citation.get("title", ""),
                authors_str,
                citation.get("year", ""),
                citation.get("venue", ""),
                citation.get("doi", ""),
                citation.get("source", ""),
                citation.get("citation_count", 0),
                citation.get("quality_score", 0.0),
                citation.get("metadata", {}).get("open_access", False)
            ])
        
        return output.getvalue()
    
    def clear_cache(self):
        """Clear citation cache and provenance map."""
        self.citation_cache.clear()
        self.provenance_map.clear()
        logger.info("Citation cache cleared")
    
    def get_provenance_chain(self, citation_id: str) -> List[Dict]:
        """Get full provenance chain for a citation."""
        return self.provenance_map.get(citation_id, [])