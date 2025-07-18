"""
ABOUTME: Custom tools for literature review that work alongside MCP tools
ABOUTME: Provides paper analysis, citation network building, and synthesis capabilities
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import re


def analyze_paper_relevance(paper_data: Dict[str, Any], research_topic: str) -> Dict[str, Any]:
    """
    Analyze paper relevance to research topic
    
    Args:
        paper_data: Paper metadata and content
        research_topic: The research topic to evaluate against
        
    Returns:
        Dictionary with relevance score and justification
    """
    # Extract key information
    title = paper_data.get("title", "").lower()
    abstract = paper_data.get("abstract", "").lower()
    keywords = [kw.lower() for kw in paper_data.get("keywords", [])]
    
    # Tokenize research topic
    topic_terms = set(research_topic.lower().split())
    
    # Calculate relevance scores
    title_matches = sum(1 for term in topic_terms if term in title)
    abstract_matches = sum(1 for term in topic_terms if term in abstract)
    keyword_matches = sum(1 for term in topic_terms for kw in keywords if term in kw)
    
    # Weight the scores
    title_score = title_matches / len(topic_terms) if topic_terms else 0
    abstract_score = abstract_matches / (len(topic_terms) * 10) if topic_terms else 0
    keyword_score = keyword_matches / len(topic_terms) if topic_terms else 0
    
    # Combined score with weights
    relevance_score = (
        title_score * 0.4 +
        abstract_score * 0.4 +
        keyword_score * 0.2
    )
    
    # Determine relevance level
    if relevance_score >= 0.7:
        relevance_level = "high"
    elif relevance_score >= 0.4:
        relevance_level = "medium"
    else:
        relevance_level = "low"
    
    return {
        "relevance_score": min(relevance_score, 1.0),
        "relevance_level": relevance_level,
        "title_matches": title_matches,
        "abstract_matches": abstract_matches,
        "keyword_matches": keyword_matches
    }


def extract_methodology(abstract: str, full_text: Optional[str] = None) -> Dict[str, str]:
    """
    Extract methodology information from paper
    
    Args:
        abstract: Paper abstract
        full_text: Full paper text if available
        
    Returns:
        Dictionary with methodology details
    """
    text = full_text if full_text else abstract
    text_lower = text.lower()
    
    # Common methodology indicators
    methodology_patterns = {
        "experimental": [
            "experiment", "randomized", "controlled trial", "treatment group",
            "control group", "measured", "tested"
        ],
        "observational": [
            "observational study", "cohort", "case-control", "cross-sectional",
            "longitudinal", "survey", "questionnaire"
        ],
        "theoretical": [
            "theoretical framework", "mathematical model", "proof", "theorem",
            "hypothesis", "conceptual"
        ],
        "computational": [
            "simulation", "computational model", "algorithm", "machine learning",
            "neural network", "deep learning", "data mining"
        ],
        "review": [
            "systematic review", "meta-analysis", "literature review",
            "scoping review", "narrative review"
        ],
        "meta_analysis": [
            "meta-analysis", "pooled analysis", "effect size", "forest plot"
        ]
    }
    
    # Find methodology type
    methodology_type = "experimental"  # default
    max_matches = 0
    
    for method_type, indicators in methodology_patterns.items():
        matches = sum(1 for indicator in indicators if indicator in text_lower)
        if matches > max_matches:
            max_matches = matches
            methodology_type = method_type
    
    # Extract methodology description
    methodology_sentences = []
    sentences = text.split('.')
    
    methodology_keywords = [
        "method", "approach", "technique", "procedure", "protocol",
        "design", "framework", "model", "algorithm"
    ]
    
    for sentence in sentences:
        if any(keyword in sentence.lower() for keyword in methodology_keywords):
            methodology_sentences.append(sentence.strip())
            if len(methodology_sentences) >= 3:
                break
    
    methodology_description = ". ".join(methodology_sentences) if methodology_sentences else "Methodology details not clearly specified in abstract"
    
    return {
        "methodology_type": methodology_type,
        "methodology_description": methodology_description[:300]  # Limit length
    }


def build_citation_network(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build citation network from paper data
    
    Args:
        papers: List of paper data with citations
        
    Returns:
        Dictionary with citation clusters and relationships
    """
    # Create citation graph
    citation_graph = {}
    paper_index = {p.get("doi", p.get("title", "")): p for p in papers}
    
    for paper in papers:
        paper_id = paper.get("doi", paper.get("title", ""))
        citations = paper.get("references", [])
        citation_graph[paper_id] = citations
    
    # Find highly cited papers (hubs)
    citation_counts = {}
    for paper_id, citations in citation_graph.items():
        for cited_id in citations:
            citation_counts[cited_id] = citation_counts.get(cited_id, 0) + 1
    
    # Sort by citation count
    highly_cited = sorted(
        citation_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    # Identify clusters (simplified clustering)
    clusters = []
    if highly_cited:
        # Create a cluster around each highly cited paper
        for hub_id, count in highly_cited[:3]:  # Top 3 hubs
            cluster_papers = [hub_id]
            
            # Add papers that cite the hub
            for paper_id, citations in citation_graph.items():
                if hub_id in citations and paper_id != hub_id:
                    cluster_papers.append(paper_id)
            
            if len(cluster_papers) > 1:
                clusters.append({
                    "hub_paper": hub_id,
                    "cluster_size": len(cluster_papers),
                    "papers": cluster_papers[:5]  # Limit to 5 papers per cluster
                })
    
    return {
        "total_papers": len(papers),
        "highly_cited_papers": [{"paper_id": p[0], "citations": p[1]} for p in highly_cited],
        "citation_clusters": clusters,
        "average_citations": sum(citation_counts.values()) / len(citation_counts) if citation_counts else 0
    }


def identify_research_gaps(papers: List[Dict[str, Any]], key_findings: List[str]) -> List[Dict[str, Any]]:
    """
    Identify research gaps from analyzed papers
    
    Args:
        papers: List of analyzed papers
        key_findings: List of key findings from literature
        
    Returns:
        List of identified research gaps
    """
    gaps = []
    
    # Analyze limitations mentioned in papers
    all_limitations = []
    for paper in papers:
        limitations = paper.get("limitations", [])
        all_limitations.extend(limitations)
    
    # Common limitation themes that indicate gaps
    gap_indicators = {
        "sample size": "Limited sample sizes in current studies",
        "generalization": "Lack of generalizability across populations",
        "longitudinal": "Need for long-term longitudinal studies",
        "mechanism": "Unclear underlying mechanisms",
        "replication": "Lack of replication studies",
        "interdisciplinary": "Limited interdisciplinary approaches",
        "real-world": "Gap between laboratory and real-world applications"
    }
    
    # Check for gap indicators in limitations
    for indicator, gap_description in gap_indicators.items():
        if any(indicator in lim.lower() for lim in all_limitations):
            gaps.append({
                "gap_description": gap_description,
                "importance": f"Multiple studies mention {indicator} as a limitation",
                "potential_approaches": [
                    f"Design studies addressing {indicator}",
                    "Collaborate with researchers who have addressed similar limitations",
                    "Apply novel methodologies to overcome this limitation"
                ]
            })
    
    # Analyze methodology distribution
    methodology_counts = {}
    for paper in papers:
        method = paper.get("methodology_type", "unknown")
        methodology_counts[method] = methodology_counts.get(method, 0) + 1
    
    # Check for underrepresented methodologies
    all_methods = ["experimental", "observational", "theoretical", "computational", "review"]
    for method in all_methods:
        if methodology_counts.get(method, 0) < len(papers) * 0.1:  # Less than 10%
            gaps.append({
                "gap_description": f"Limited {method} studies in this field",
                "importance": f"Diverse methodologies provide comprehensive understanding",
                "potential_approaches": [
                    f"Apply {method} approaches to existing questions",
                    f"Combine {method} with dominant methodologies",
                    "Validate findings using different methodological approaches"
                ]
            })
    
    return gaps[:5]  # Return top 5 gaps


def generate_synthesis(
    papers: List[Dict[str, Any]],
    key_findings: List[str],
    research_gaps: List[Dict[str, Any]],
    research_topic: str
) -> str:
    """
    Generate a comprehensive synthesis of the literature
    
    Args:
        papers: List of analyzed papers
        key_findings: Major findings from literature
        research_gaps: Identified gaps
        research_topic: Original research topic
        
    Returns:
        Synthesis text
    """
    # Count papers by year
    year_distribution = {}
    for paper in papers:
        year = paper.get("year", 0)
        if year > 0:
            year_distribution[year] = year_distribution.get(year, 0) + 1
    
    # Find trend
    recent_years = sorted(year_distribution.keys())[-5:] if year_distribution else []
    trend = "increasing" if len(recent_years) > 2 and year_distribution.get(recent_years[-1], 0) > year_distribution.get(recent_years[0], 0) else "stable"
    
    synthesis = f"""
Based on the analysis of {len(papers)} papers on "{research_topic}", several key patterns emerge:

**Research Trajectory**: The field shows {trend} research activity, with {len([p for p in papers if p.get('year', 0) >= 2020])} papers published since 2020.

**Key Consensus Areas**:
{chr(10).join(f"- {finding}" for finding in key_findings[:3])}

**Methodological Landscape**: The research predominantly uses {max(set([p.get('methodology_type', 'experimental') for p in papers]), key=lambda x: [p.get('methodology_type', 'experimental') for p in papers].count(x))} approaches, indicating a need for methodological diversity.

**Critical Gaps**: {len(research_gaps)} significant gaps were identified, with the most critical being the need for more comprehensive, long-term studies that bridge theoretical insights with practical applications.

**Future Directions**: The field is poised for advancement through interdisciplinary collaboration, novel methodological approaches, and addressing the identified gaps in current research.
    """.strip()
    
    return synthesis


def extract_paper_metadata(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and normalize paper metadata from various sources
    
    Args:
        raw_data: Raw paper data from various sources
        
    Returns:
        Normalized paper metadata
    """
    # Handle different source formats
    metadata = {
        "title": raw_data.get("title", raw_data.get("Title", "")),
        "authors": [],
        "year": 0,
        "doi": None,
        "arxiv_id": None,
        "pubmed_id": None,
        "abstract": raw_data.get("abstract", raw_data.get("Abstract", raw_data.get("summary", ""))),
        "journal": raw_data.get("journal", raw_data.get("venue", raw_data.get("publisher", ""))),
        "keywords": [],
        "source_url": None
    }
    
    # Extract authors
    if "authors" in raw_data:
        if isinstance(raw_data["authors"], list):
            metadata["authors"] = [a.get("name", str(a)) for a in raw_data["authors"]][:20]
        else:
            metadata["authors"] = [raw_data["authors"]]
    elif "author" in raw_data:
        metadata["authors"] = [raw_data["author"]]
    
    # Extract year
    if "year" in raw_data:
        metadata["year"] = int(raw_data["year"])
    elif "published" in raw_data:
        # Extract year from date string
        year_match = re.search(r"20\d{2}|19\d{2}", str(raw_data["published"]))
        if year_match:
            metadata["year"] = int(year_match.group())
    
    # Extract identifiers
    metadata["doi"] = raw_data.get("doi", raw_data.get("DOI"))
    metadata["arxiv_id"] = raw_data.get("arxiv_id", raw_data.get("id"))
    metadata["pubmed_id"] = raw_data.get("pmid", raw_data.get("pubmed_id"))
    
    # Extract keywords
    keywords = raw_data.get("keywords", raw_data.get("categories", raw_data.get("tags", [])))
    if isinstance(keywords, list):
        metadata["keywords"] = keywords[:10]
    elif isinstance(keywords, str):
        metadata["keywords"] = [k.strip() for k in keywords.split(",")][:10]
    
    # Build source URL
    if metadata["doi"]:
        metadata["source_url"] = f"https://doi.org/{metadata['doi']}"
    elif metadata["arxiv_id"]:
        metadata["source_url"] = f"https://arxiv.org/abs/{metadata['arxiv_id']}"
    elif metadata["pubmed_id"]:
        metadata["source_url"] = f"https://pubmed.ncbi.nlm.nih.gov/{metadata['pubmed_id']}"
    
    return metadata