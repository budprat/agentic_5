#!/usr/bin/env python3
"""Reference Intelligence Service for external source integration."""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import aiohttp
import arxiv
from semanticscholar import SemanticScholar

logger = logging.getLogger(__name__)

class ReferenceIntelligenceService:
    """Unified external reference integration service."""
    
    def __init__(self, config: Dict = None):
        self.config = config or self._default_config()
        self.arxiv_client = self._init_arxiv_client()
        # Initialize SemanticScholar with timeout and proper configuration
        self.semantic_scholar = self._init_semantic_scholar_client()
        self.session = None
        self.cache = {}
        
    def _default_config(self) -> Dict:
        return {
            "enabled": False,
            "sources": {
                "arxiv": True,
                "semantic_scholar": False,  # Disabled due to API timeout issues - TODO: investigate further
                "mcp_scholarly": True,
                "web_search": False  # Rate limited
            },
            "limits": {
                "max_papers_per_source": 10,
                "max_total_papers": 30,
                "request_timeout": 30
            },
            "quality_filters": {
                "min_citation_count": 1,
                "max_age_years": 10,
                "require_peer_review": False
            }
        }
    
    def _init_arxiv_client(self) -> arxiv.Client:
        """Initialize ArXiv client with rate limiting."""
        return arxiv.Client(
            page_size=self.config["limits"]["max_papers_per_source"],
            delay_seconds=3.0,  # Respectful rate limiting
            num_retries=3
        )
    
    def _init_semantic_scholar_client(self) -> SemanticScholar:
        """Initialize Semantic Scholar client with proper timeout configuration."""
        import os
        # Check for API key in environment variables for better rate limits
        api_key = os.getenv('SEMANTIC_SCHOLAR_API_KEY')
        
        if api_key:
            logger.info("Using Semantic Scholar API key for enhanced rate limits")
            return SemanticScholar(api_key=api_key, timeout=30)
        else:
            logger.info("Using Semantic Scholar without API key (5000 requests per 5 minutes)")
            # Initialize with explicit timeout to handle slow responses
            return SemanticScholar(timeout=30)
    
    async def gather_domain_references(self, query: str, domain: str) -> Dict[str, Any]:
        """Gather references from multiple sources for a domain query."""
        if not self.config.get("enabled", False):
            return {"enabled": False, "sources": {}}
        
        logger.info(f"Gathering references for query: {query}, domain: {domain}")
        
        # Parallel execution of all enabled sources
        tasks = {}
        
        if self.config["sources"].get("arxiv", False):
            tasks["arxiv"] = self._search_arxiv(query, domain)
            
        if self.config["sources"].get("semantic_scholar", False):
            tasks["semantic_scholar"] = self._search_semantic_scholar(query)
            
        if self.config["sources"].get("mcp_scholarly", False):
            tasks["mcp_scholarly"] = self._search_mcp_scholarly(query)
        
        # Execute all searches in parallel
        results = await asyncio.gather(
            *tasks.values(), 
            return_exceptions=True
        )
        
        # Combine results with source attribution
        combined_results = {}
        for source_name, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                logger.warning(f"Error from {source_name}: {result}")
                combined_results[source_name] = {"error": str(result), "papers": []}
            else:
                combined_results[source_name] = result
        
        # Post-process and rank results
        processed_results = self._process_and_rank_results(combined_results, query, domain)
        
        return {
            "enabled": True,
            "query": query,
            "domain": domain,
            "sources": combined_results,
            "processed": processed_results,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _search_arxiv(self, query: str, domain: str) -> Dict[str, Any]:
        """Search ArXiv for relevant papers with proper timeout and error handling."""
        try:
            # Enable appropriate logging level for arxiv
            logging.getLogger('arxiv').setLevel(logging.WARNING)
            
            # Domain-specific query enhancement
            enhanced_query = self._enhance_query_for_arxiv_domain(query, domain)
            
            search = arxiv.Search(
                query=enhanced_query,
                max_results=self.config["limits"]["max_papers_per_source"],
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
            
            # Define synchronous function to fetch results
            def fetch_arxiv_results():
                papers = []
                paper_count = 0
                max_papers = self.config["limits"]["max_papers_per_source"]
                
                try:
                    for result in self.arxiv_client.results(search):
                        if paper_count >= max_papers:
                            break
                            
                        # Apply quality filters
                        if self._passes_quality_filters(result):
                            papers.append({
                                "title": result.title,
                                "authors": [author.name for author in result.authors],
                                "abstract": result.summary[:500] + "..." if len(result.summary) > 500 else result.summary,
                                "doi": result.doi,
                                "arxiv_id": result.entry_id.split('/')[-1],
                                "pdf_url": result.pdf_url,
                                "published": result.published.isoformat(),
                                "categories": result.categories,
                                "source": "arxiv",
                                "quality_score": self._calculate_arxiv_quality_score(result)
                            })
                        
                        paper_count += 1
                
                except Exception as e:
                    logger.warning(f"ArXiv iteration error: {e}")
                
                return papers
            
            # Run synchronous function in thread pool with timeout
            try:
                papers = await asyncio.wait_for(
                    asyncio.to_thread(fetch_arxiv_results),
                    timeout=self.config["limits"]["request_timeout"]
                )
                
                return {
                    "papers": papers,
                    "total_found": len(papers),
                    "query_used": enhanced_query,
                    "source": "arxiv",
                    "timeout_occurred": False
                }
                
            except asyncio.TimeoutError:
                logger.warning(f"ArXiv search timed out after {self.config['limits']['request_timeout']}s")
                return {
                    "papers": [],
                    "total_found": 0,
                    "query_used": enhanced_query,
                    "source": "arxiv",
                    "timeout_occurred": True,
                    "error": f"Request timed out after {self.config['limits']['request_timeout']}s"
                }
            
        except Exception as e:
            logger.error(f"ArXiv search error: {e}")
            return {"error": str(e), "papers": [], "source": "arxiv"}
    
    async def _search_semantic_scholar(self, query: str) -> Dict[str, Any]:
        """Search Semantic Scholar for relevant papers with proper timeout handling.
        
        TODO: Currently experiencing API timeout issues despite implementing:
        - Proper retry logic with exponential backoff
        - HTTP 500 error handling as per API docs  
        - Rate limiting compliance (5000 requests per 5 minutes)
        - Explicit timeout configuration
        
        The API status shows operational but calls consistently timeout.
        Need to investigate: API key requirements, network connectivity, 
        or alternative client library implementations.
        """
        try:
            # Define synchronous function to fetch results
            def fetch_semantic_scholar_results():
                papers = []
                
                try:
                    # Enable debug logging for this API call to understand what's happening
                    import logging
                    import time
                    import requests
                    logging.getLogger('semanticscholar').setLevel(logging.DEBUG)
                    
                    logger.info(f"Starting Semantic Scholar search for query: {query}")
                    
                    # Implement retry logic for 500 errors and rate limiting as per API docs
                    max_retries = 3
                    base_delay = 2.0
                    
                    for attempt in range(max_retries):
                        try:
                            logger.info(f"Semantic Scholar attempt {attempt + 1}/{max_retries}")
                            
                            # Use full field set but with proper error handling
                            results = self.semantic_scholar.search_paper(
                                query, 
                                limit=self.config["limits"]["max_papers_per_source"],
                                fields=['title', 'abstract', 'authors', 'citationCount', 
                                       'influentialCitationCount', 'year', 'venue', 'externalIds', 'isOpenAccess']
                            )
                            
                            # If we get here, the request succeeded
                            logger.info(f"Semantic Scholar search succeeded on attempt {attempt + 1}")
                            break
                            
                        except requests.exceptions.HTTPError as e:
                            if e.response.status_code == 500 and attempt < max_retries - 1:
                                # API overloaded, wait and retry as recommended
                                wait_time = base_delay * (2 ** attempt)  # Exponential backoff
                                logger.warning(f"Semantic Scholar API overloaded (500), retrying in {wait_time}s")
                                time.sleep(wait_time)
                                continue
                            else:
                                raise
                        except requests.exceptions.Timeout as e:
                            if attempt < max_retries - 1:
                                wait_time = base_delay * (2 ** attempt)
                                logger.warning(f"Semantic Scholar timeout, retrying in {wait_time}s")
                                time.sleep(wait_time)
                                continue
                            else:
                                raise
                        except Exception as e:
                            if attempt < max_retries - 1:
                                wait_time = base_delay
                                logger.warning(f"Semantic Scholar error: {e}, retrying in {wait_time}s")
                                time.sleep(wait_time)
                                continue
                            else:
                                raise
                    
                    # According to the documentation, get the first page directly instead of iterating
                    # This avoids potential infinite iteration or pagination issues
                    first_page_items = results.items if hasattr(results, 'items') else list(results)
                    
                    logger.info(f"Semantic Scholar returned {len(first_page_items)} results")
                    
                    for paper in first_page_items:
                        if self._passes_semantic_scholar_filters(paper):
                            papers.append({
                                "title": paper.title,
                                "authors": [author.name for author in paper.authors] if paper.authors else [],
                                "abstract": (paper.abstract[:500] + "...") if paper.abstract and len(paper.abstract) > 500 else (paper.abstract or ""),
                                "citation_count": paper.citationCount or 0,
                                "influential_citations": paper.influentialCitationCount or 0,
                                "year": paper.year,
                                "venue": paper.venue,
                                "doi": paper.externalIds.get('DOI') if paper.externalIds else None,
                                "is_open_access": paper.isOpenAccess,
                                "semantic_scholar_id": paper.paperId,
                                "source": "semantic_scholar",
                                "quality_score": self._calculate_semantic_scholar_quality_score(paper)
                            })
                    
                    logger.info(f"Processed {len(papers)} papers after quality filtering")
                            
                except Exception as e:
                    logger.warning(f"Semantic Scholar iteration error: {e}")
                
                return papers
            
            # Run synchronous function in thread pool with proper timeout
            # Increased timeout to account for retry logic and API delays
            semantic_scholar_timeout = max(self.config["limits"]["request_timeout"], 45)
            try:
                papers = await asyncio.wait_for(
                    asyncio.to_thread(fetch_semantic_scholar_results),
                    timeout=semantic_scholar_timeout
                )
                
                return {
                    "papers": papers,
                    "total_found": len(papers),
                    "source": "semantic_scholar",
                    "timeout_occurred": False
                }
                
            except asyncio.TimeoutError:
                logger.warning(f"Semantic Scholar search timed out after {semantic_scholar_timeout}s")
                return {
                    "papers": [],
                    "total_found": 0,
                    "source": "semantic_scholar",
                    "timeout_occurred": True,
                    "error": f"Request timed out after {semantic_scholar_timeout}s (reduced timeout due to API limitations)"
                }
            
        except Exception as e:
            logger.error(f"Semantic Scholar search error: {e}")
            return {"error": str(e), "papers": [], "source": "semantic_scholar"}
    
    async def _search_mcp_scholarly(self, query: str) -> Dict[str, Any]:
        """Search via MCP Scholarly server."""
        try:
            # This would integrate with the MCP Scholarly server
            # For now, return a placeholder structure
            return {
                "papers": [],
                "total_found": 0,
                "source": "mcp_scholarly",
                "note": "MCP Scholarly integration pending"
            }
            
        except Exception as e:
            logger.error(f"MCP Scholarly search error: {e}")
            return {"error": str(e), "papers": [], "source": "mcp_scholarly"}
    
    def _enhance_query_for_arxiv_domain(self, query: str, domain: str) -> str:
        """Enhance query with domain-specific ArXiv categories and keywords."""
        query_lower = query.lower()
        
        # Enhanced domain categorization with keyword detection
        domain_categories = {
            "computer_science": "cat:cs.*",
            "technical_analysis": "cat:cs.*", 
            "physics": "cat:physics.*",
            "physical_analysis": "cat:physics.*",
            "mathematics": "cat:math.*",
            "life_sciences": "cat:q-bio.*",
            "economics": "cat:econ.*",
            "social_sciences": "cat:cs.CY OR cat:physics.soc-ph",  # Computers and Society, Social Physics
            "environmental_studies": "cat:physics.ao-ph OR cat:q-bio.PE",  # Atmospheric Physics, Populations and Evolution
        }
        
        # Enhanced keyword-based category detection
        if any(word in query_lower for word in ["neural", "machine learning", "deep learning", "ai", "artificial intelligence"]):
            category_filter = "cat:cs.LG OR cat:cs.AI OR cat:cs.CV OR cat:cs.CL"  # ML, AI, Computer Vision, Computational Linguistics
        elif any(word in query_lower for word in ["quantum", "qubit", "quantum computing"]):
            category_filter = "cat:quant-ph OR cat:cs.ET"  # Quantum Physics, Emerging Technologies
        elif any(word in query_lower for word in ["climate", "environment", "carbon", "energy"]):
            category_filter = "cat:physics.ao-ph OR cat:physics.gen-ph OR cat:q-bio.PE"  # Atmospheric, General Physics, Populations
        elif any(word in query_lower for word in ["education", "learning", "teaching"]):
            category_filter = "cat:cs.CY OR cat:cs.HC"  # Computers and Society, Human-Computer Interaction
        else:
            # Fallback to domain-based categorization
            category_filter = domain_categories.get(domain, "")
        
        if category_filter:
            return f"({query}) AND ({category_filter})"
        return query
    
    def _passes_quality_filters(self, arxiv_result) -> bool:
        """Check if ArXiv result passes quality filters."""
        try:
            # Age filter - handle timezone-aware vs naive datetime comparison
            age_limit = datetime.now() - timedelta(days=365 * self.config["quality_filters"]["max_age_years"])
            published_date = arxiv_result.published
            
            # Convert to naive datetime if it's timezone-aware
            if published_date.tzinfo is not None:
                published_date = published_date.replace(tzinfo=None)
            
            if published_date < age_limit:
                return False
            
            # Additional quality checks can be added here
            return True
            
        except Exception as e:
            logger.warning(f"Quality filter error: {e}")
            return True  # Default to accept if there's an error
    
    def _passes_semantic_scholar_filters(self, paper) -> bool:
        """Check if Semantic Scholar result passes quality filters."""
        # Citation count filter
        min_citations = self.config["quality_filters"]["min_citation_count"]
        if (paper.citationCount or 0) < min_citations:
            return False
        
        # Age filter
        if paper.year:
            current_year = datetime.now().year
            max_age = self.config["quality_filters"]["max_age_years"]
            if current_year - paper.year > max_age:
                return False
        
        return True
    
    def _calculate_arxiv_quality_score(self, result) -> float:
        """Calculate quality score for ArXiv paper (0.0-1.0)."""
        score = 0.5  # Base score
        
        try:
            # Recency bonus - handle timezone-aware vs naive datetime
            published_date = result.published
            if published_date.tzinfo is not None:
                published_date = published_date.replace(tzinfo=None)
            
            days_old = (datetime.now() - published_date).days
            if days_old < 365:  # Less than 1 year
                score += 0.2
            elif days_old < 365 * 2:  # Less than 2 years
                score += 0.1
        except Exception as e:
            logger.warning(f"Date calculation error in quality score: {e}")
        
        # Category relevance (simplified)
        if len(result.categories) > 1:  # Interdisciplinary
            score += 0.1
        
        # Author count consideration
        if 2 <= len(result.authors) <= 5:  # Optimal collaboration size
            score += 0.1
        
        return min(1.0, score)
    
    def _calculate_semantic_scholar_quality_score(self, paper) -> float:
        """Calculate quality score for Semantic Scholar paper (0.0-1.0)."""
        score = 0.3  # Base score
        
        # Citation impact
        citations = paper.citationCount or 0
        if citations >= 100:
            score += 0.3
        elif citations >= 20:
            score += 0.2
        elif citations >= 5:
            score += 0.1
        
        # Influential citations bonus
        influential = paper.influentialCitationCount or 0
        if influential >= 10:
            score += 0.2
        elif influential >= 3:
            score += 0.1
        
        # Open access bonus
        if paper.isOpenAccess:
            score += 0.1
        
        # Venue quality (simplified)
        if paper.venue and len(paper.venue) > 5:  # Has meaningful venue
            score += 0.1
        
        return min(1.0, score)
    
    def _process_and_rank_results(self, results: Dict, query: str, domain: str) -> Dict[str, Any]:
        """Process and rank combined results from all sources."""
        all_papers = []
        
        # Collect all papers with source attribution
        for source, source_results in results.items():
            if source_results.get("papers"):
                for paper in source_results["papers"]:
                    paper["source_name"] = source
                    all_papers.append(paper)
        
        # Remove duplicates based on title similarity and DOI
        deduplicated_papers = self._deduplicate_papers(all_papers)
        
        # Rank papers by quality score
        ranked_papers = sorted(
            deduplicated_papers, 
            key=lambda p: p.get("quality_score", 0.0), 
            reverse=True
        )
        
        # Limit to max total papers
        max_papers = self.config["limits"]["max_total_papers"]
        top_papers = ranked_papers[:max_papers]
        
        # Calculate aggregate statistics
        stats = self._calculate_reference_statistics(top_papers)
        
        return {
            "papers": top_papers,
            "total_papers": len(top_papers),
            "statistics": stats,
            "ranking_criteria": "quality_score_desc"
        }
    
    def _deduplicate_papers(self, papers: List[Dict]) -> List[Dict]:
        """Remove duplicate papers based on title similarity and DOI."""
        deduplicated = []
        seen_dois = set()
        seen_titles = []
        
        for paper in papers:
            # Check DOI first (most reliable)
            doi = paper.get("doi")
            if doi and doi in seen_dois:
                continue
            
            # Check title similarity (simplified)
            title = paper.get("title", "").lower()
            is_duplicate = False
            for seen_title in seen_titles:
                # Simple similarity check (can be enhanced)
                if len(title) > 10 and title in seen_title or seen_title in title:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                deduplicated.append(paper)
                if doi:
                    seen_dois.add(doi)
                seen_titles.append(title)
        
        return deduplicated
    
    def _calculate_reference_statistics(self, papers: List[Dict]) -> Dict[str, Any]:
        """Calculate aggregate statistics for references."""
        if not papers:
            return {"total": 0}
        
        total_citations = sum(paper.get("citation_count", 0) for paper in papers)
        years = [paper.get("year") for paper in papers if paper.get("year")]
        sources = [paper.get("source") for paper in papers]
        
        return {
            "total": len(papers),
            "total_citations": total_citations,
            "avg_citations": total_citations / len(papers) if papers else 0,
            "avg_year": sum(years) / len(years) if years else None,
            "sources_distribution": {source: sources.count(source) for source in set(sources)},
            "open_access_count": sum(1 for paper in papers if paper.get("is_open_access")),
            "avg_quality_score": sum(paper.get("quality_score", 0) for paper in papers) / len(papers)
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()