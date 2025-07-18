"""
ABOUTME: Pydantic schemas for literature review agent
ABOUTME: Defines structured output formats for academic paper analysis
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime


class PaperRelevance(str, Enum):
    """Relevance levels for papers"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    
    
class MethodologyType(str, Enum):
    """Common research methodology types"""
    EXPERIMENTAL = "experimental"
    OBSERVATIONAL = "observational"
    THEORETICAL = "theoretical"
    COMPUTATIONAL = "computational"
    REVIEW = "review"
    META_ANALYSIS = "meta_analysis"


class PaperSummary(BaseModel):
    """Detailed summary of a research paper"""
    title: str = Field(description="Paper title", max_length=300)
    authors: List[str] = Field(description="List of authors", max_items=20)
    year: int = Field(description="Publication year", ge=1900, le=2025)
    doi: Optional[str] = Field(description="Digital Object Identifier", default=None)
    arxiv_id: Optional[str] = Field(description="arXiv identifier", default=None)
    pubmed_id: Optional[str] = Field(description="PubMed identifier", default=None)
    
    abstract_summary: str = Field(
        description="Concise summary of the abstract",
        min_length=100,
        max_length=500
    )
    
    key_contributions: List[str] = Field(
        description="Main contributions of the paper",
        min_items=1,
        max_items=5
    )
    
    methodology: str = Field(
        description="Research methodology used",
        max_length=300
    )
    
    methodology_type: MethodologyType = Field(
        description="Type of research methodology"
    )
    
    key_findings: List[str] = Field(
        description="Key findings and results",
        min_items=1,
        max_items=5
    )
    
    limitations: List[str] = Field(
        description="Identified limitations",
        max_items=3,
        default=[]
    )
    
    relevance_score: float = Field(
        description="Relevance to research query (0-1)",
        ge=0,
        le=1
    )
    
    relevance_level: PaperRelevance = Field(
        description="Categorical relevance level"
    )
    
    citations_count: Optional[int] = Field(
        description="Number of citations",
        ge=0,
        default=None
    )
    
    journal: Optional[str] = Field(
        description="Journal or conference name",
        default=None
    )
    
    keywords: List[str] = Field(
        description="Paper keywords",
        max_items=10,
        default=[]
    )
    
    source_url: Optional[str] = Field(
        description="URL to access the paper",
        default=None
    )


class MethodologyTrend(BaseModel):
    """Trends in research methodologies"""
    methodology: str = Field(description="Methodology name", max_length=100)
    frequency: int = Field(description="Number of papers using this methodology", ge=1)
    percentage: float = Field(description="Percentage of papers", ge=0, le=100)
    evolution: str = Field(
        description="How this methodology has evolved",
        max_length=300
    )


class ResearchGap(BaseModel):
    """Identified gap in current research"""
    gap_description: str = Field(
        description="Description of the research gap",
        min_length=50,
        max_length=500
    )
    importance: str = Field(
        description="Why this gap is important",
        max_length=300
    )
    potential_approaches: List[str] = Field(
        description="Suggested approaches to address the gap",
        max_items=3
    )
    related_papers: List[str] = Field(
        description="Papers that highlight this gap",
        max_items=5
    )


class CitationCluster(BaseModel):
    """Cluster of related papers by citation"""
    cluster_name: str = Field(description="Name/theme of the cluster", max_length=100)
    core_papers: List[str] = Field(
        description="Most influential papers in cluster",
        min_items=1,
        max_items=5
    )
    size: int = Field(description="Number of papers in cluster", ge=1)
    key_authors: List[str] = Field(
        description="Key authors in this cluster",
        max_items=10
    )


class LiteratureReviewResult(BaseModel):
    """Complete literature review analysis result"""
    query_topic: str = Field(
        description="Research topic searched",
        min_length=10,
        max_length=200
    )
    
    search_date: str = Field(
        description="Date of literature search",
        default_factory=lambda: datetime.now().isoformat()
    )
    
    total_papers_found: int = Field(
        description="Total number of papers discovered",
        ge=0
    )
    
    papers_analyzed: List[PaperSummary] = Field(
        description="Detailed analysis of relevant papers",
        max_items=50
    )
    
    key_findings: List[str] = Field(
        description="Major discoveries from literature",
        min_items=1,
        max_items=10
    )
    
    research_gaps: List[ResearchGap] = Field(
        description="Identified gaps in current research",
        max_items=5,
        default=[]
    )
    
    methodology_trends: List[MethodologyTrend] = Field(
        description="Common methodologies used",
        max_items=5,
        default=[]
    )
    
    citation_clusters: List[CitationCluster] = Field(
        description="Citation network clusters",
        max_items=5,
        default=[]
    )
    
    emerging_topics: List[str] = Field(
        description="Emerging research topics identified",
        max_items=5,
        default=[]
    )
    
    recommended_papers: List[str] = Field(
        description="Must-read papers for this topic",
        max_items=10
    )
    
    synthesis: str = Field(
        description="Overall synthesis of the literature",
        min_length=200,
        max_length=1000
    )
    
    next_steps: List[str] = Field(
        description="Recommended next steps for research",
        min_items=1,
        max_items=5
    )