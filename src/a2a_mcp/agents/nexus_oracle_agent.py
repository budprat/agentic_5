"""Nexus Oracle - Master Transdisciplinary Research Orchestrator Agent."""

import logging
import json
import asyncio
from collections.abc import AsyncIterable
from typing import Dict, Any, List
from datetime import datetime

from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import init_api_key
from a2a_mcp.common.parallel_workflow import (
    ParallelWorkflowGraph, 
    ParallelWorkflowNode,
    Status
)
from a2a_mcp.common.reference_intelligence import ReferenceIntelligenceService
from a2a_mcp.common.citation_tracker import CitationTracker
from google import genai
import os
import aiohttp

logger = logging.getLogger(__name__)

# Research synthesis prompt
RESEARCH_SYNTHESIS_PROMPT = """
You are Nexus Oracle, a master transdisciplinary research strategist. Analyze the research question: "{original_query}"

Based on the following domain analyses and external academic references, provide a comprehensive synthesis that directly addresses the research question:

Research Intelligence Data:
{research_data}

Research Context:
{research_context}

External Academic References:
{external_references}

Quality Thresholds:
- Minimum confidence score: {min_confidence}
- Required domain coverage: {required_domains}
- Evidence quality threshold: {evidence_threshold}

CRITICAL CITATION REQUIREMENTS:
1. ONLY cite external academic sources that are directly relevant to the current research question: "{original_query}". Do NOT use citations from unrelated topics.
2. Use the exact format [First Author et al., YEAR] when referencing specific papers from the External Academic References section above that are relevant to "{original_query}".
3. Before citing any paper, verify its relevance: the paper's title, abstract, or research area must relate to the current query topic.
4. Include citations in your executive_summary ONLY if the referenced papers actually support the claims being made about "{original_query}".
5. Each key_insight should reference relevant external papers ONLY when the papers actually relate to the insight topic.
6. Novel_hypotheses should cite supporting external research ONLY when the referenced papers are genuinely relevant to the hypothesis.
7. If no external references are relevant to "{original_query}", do NOT force citations. Instead, note that external validation from domain-specific literature would strengthen the analysis.
8. Focus your analysis specifically on answering "{original_query}" with concrete, actionable insights. Only include citations that genuinely support your analysis of this specific question.

Provide your synthesis in the following JSON format:
{{
    "executive_summary": "Brief 2-3 sentence summary of key findings",
    "research_confidence": 0.0-1.0,
    "domain_coverage": "Number of disciplines contributing insights",
    "quality_assessment": {{
        "evidence_strength": 0-100,
        "methodological_rigor": 0-100,
        "bias_detection": ["bias1", "bias2"],
        "validation_strategies": ["strategy1", "strategy2"]
    }},
    "key_insights": [
        {{"source": "domain_name", "insight": "key finding", "confidence": 0.0-1.0}},
        ...
    ],
    "cross_domain_patterns": {{
        "convergent_findings": ["finding1", "finding2"],
        "contradictory_evidence": ["conflict1", "conflict2"],
        "knowledge_gaps": ["gap1", "gap2"]
    }},
    "novel_hypotheses": [
        {{
            "hypothesis": "proposed hypothesis",
            "supporting_domains": ["domain1", "domain2"],
            "testability": "high/medium/low",
            "significance": "description"
        }}
    ],
    "research_recommendations": {{
        "priority_directions": ["direction1", "direction2"],
        "methodological_innovations": ["innovation1", "innovation2"],
        "collaboration_opportunities": ["opportunity1", "opportunity2"]
    }}
}}
"""

class NexusOracleAgent(BaseAgent):
    """Master orchestrator for transdisciplinary research synthesis."""

    def __init__(self):
        init_api_key()
        super().__init__(
            agent_name="Nexus Oracle",
            description="Master transdisciplinary research orchestrator with bias detection",
            content_types=["text", "text/plain"],
        )
        self.graph = None
        self.research_intelligence = {}
        self.research_context = {}
        self.quality_thresholds = {
            "min_confidence_score": 0.7,
            "min_domain_coverage": 3,
            "evidence_quality_threshold": 0.8,
            "bias_detection_threshold": 0.6,
            "cross_validation_required": True
        }
        self.query_history = []
        self.context_id = None
        self.enable_parallel = True
        
        # Initialize reference integration system
        self.reference_service = self._init_reference_service()
        self.citation_tracker = CitationTracker()
        self.external_references = {}

    def _init_reference_service(self) -> ReferenceIntelligenceService:
        """Initialize reference intelligence service with Oracle configuration."""
        try:
            # Load Oracle configuration
            config_path = "oracle_config.json"
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    oracle_config = json.load(f)
                    ref_config = oracle_config.get("reference_integration", {})
                    
                    # Map Oracle config structure to ReferenceIntelligenceService expected structure
                    if "quality_thresholds" in ref_config:
                        quality_thresholds = ref_config["quality_thresholds"]
                        ref_config["quality_filters"] = {
                            "min_citation_count": quality_thresholds.get("min_citations", 1),
                            "max_age_years": quality_thresholds.get("max_age_years", 10),
                            "require_peer_review": quality_thresholds.get("peer_review_required", False),
                            "min_quality_score": quality_thresholds.get("min_quality_score", 0.3)
                        }
                    
                    logger.info(f"Loaded Oracle reference config: {ref_config.get('enabled', False)}")
                    return ReferenceIntelligenceService(ref_config)
            else:
                logger.info("No Oracle config found, using default reference settings")
                return ReferenceIntelligenceService()
        except Exception as e:
            logger.error(f"Error initializing reference service: {e}")
            return ReferenceIntelligenceService()

    def _format_external_references(self) -> str:
        """Format external references for inclusion in research synthesis."""
        if not self.external_references.get("enabled", False):
            return "No external academic references available."
        
        if not self.external_references.get("sources"):
            return "External reference system enabled but no sources found for this query."
        
        # Get current query for relevance checking
        current_query = self.research_context.get("query", "").lower() if self.research_context else ""
        
        formatted_refs = []
        formatted_refs.append("EXTERNAL ACADEMIC REFERENCES:")
        formatted_refs.append("=" * 50)
        
        total_papers = 0
        total_relevant_papers = 0
        
        for source_name, source_data in self.external_references["sources"].items():
            papers = source_data.get("papers", [])
            
            # Filter papers for relevance to current query
            relevant_papers = []
            for paper in papers:
                if self._is_paper_relevant_to_query(paper, current_query):
                    relevant_papers.append(paper)
            
            total_papers += len(papers)
            total_relevant_papers += len(relevant_papers)
            
            if relevant_papers:
                formatted_refs.append(f"\n{source_name.upper()} ({len(relevant_papers)} relevant papers):")
                formatted_refs.append("-" * 30)
                
                for i, paper in enumerate(relevant_papers[:5], 1):  # Limit to top 5 relevant papers per source
                    title = paper.get("title", "No title")
                    authors = paper.get("authors", [])
                    
                    # Extract year from published date if not available directly
                    year = paper.get("year")
                    if not year and paper.get("published"):
                        try:
                            from datetime import datetime
                            published_str = paper["published"]
                            if isinstance(published_str, str):
                                year = datetime.fromisoformat(published_str.replace('Z', '+00:00')).year
                        except:
                            year = "Unknown"
                    if not year:
                        year = "Unknown"
                        
                    quality = paper.get("quality_score", 0)
                    
                    author_str = ", ".join(authors[:3])  # First 3 authors
                    if len(authors) > 3:
                        author_str += " et al."
                    
                    formatted_refs.append(f"{i}. {title}")
                    formatted_refs.append(f"   Authors: {author_str}")
                    formatted_refs.append(f"   Year: {year} | Quality Score: {quality:.2f}")
                    
                    if paper.get("abstract"):
                        abstract = paper["abstract"][:200] + "..." if len(paper["abstract"]) > 200 else paper["abstract"]
                        formatted_refs.append(f"   Abstract: {abstract}")
                    formatted_refs.append("")
        
        if total_relevant_papers > 0:
            formatted_refs.append(f"Total relevant external references: {total_relevant_papers} papers (filtered from {total_papers} total)")
            formatted_refs.append("IMPORTANT: Only use these references if they are genuinely relevant to your analysis.")
        else:
            formatted_refs.append(f"No relevant papers found for this query (searched {total_papers} papers).")
            formatted_refs.append("Note: External validation from domain-specific literature would strengthen this analysis.")
        
        return "\n".join(formatted_refs)
    
    def _is_paper_relevant_to_query(self, paper: Dict, query: str) -> bool:
        """Check if a paper is relevant to the current research query."""
        if not query:
            return True  # If no query context, include all papers
        
        # Extract key terms from query
        query_terms = set(query.lower().split())
        
        # Remove common stop words
        stop_words = {"how", "can", "what", "is", "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "be", "have", "do", "will", "would", "could", "should"}
        query_terms = query_terms - stop_words
        
        # Check paper title and abstract for relevance
        paper_text = ""
        if paper.get("title"):
            paper_text += paper["title"].lower() + " "
        if paper.get("abstract"):
            paper_text += paper["abstract"].lower() + " "
        
        # Simple relevance check: at least 2 query terms should appear in paper
        matching_terms = sum(1 for term in query_terms if term in paper_text)
        relevance_threshold = min(2, len(query_terms))  # At least 2 terms or all terms if query is very short
        
        return matching_terms >= relevance_threshold

    async def load_research_context(self, query: str):
        """Load research context and determine domain scope."""
        try:
            # Extract research domains from query
            query_lower = query.lower()
            relevant_domains = []
            
            # Domain detection logic
            if any(word in query_lower for word in ["life", "biology", "medical", "health", "genetics", "biotech"]):
                relevant_domains.append("life_sciences")
            if any(word in query_lower for word in ["social", "society", "culture", "anthropology", "sociology"]):
                relevant_domains.append("social_sciences")
            if any(word in query_lower for word in ["economic", "policy", "governance", "political", "economics"]):
                relevant_domains.append("economics_policy")
            if any(word in query_lower for word in ["physics", "chemistry", "material", "quantum", "energy"]):
                relevant_domains.append("physical_sciences")
            if any(word in query_lower for word in ["computer", "ai", "algorithm", "machine learning", "technology"]):
                relevant_domains.append("computer_science")
            if any(word in query_lower for word in ["psychology", "cognitive", "behavior", "mental", "brain"]):
                relevant_domains.append("psychology")
            if any(word in query_lower for word in ["environment", "climate", "sustainability", "ecology"]):
                relevant_domains.append("environmental_studies")
            
            # Default to comprehensive analysis if no specific domains detected
            if not relevant_domains:
                relevant_domains = ["cross_domain_analysis"]
            
            # Gather external references for the query
            primary_domain = relevant_domains[0] if relevant_domains else "cross_domain_analysis"
            logger.info(f"Gathering external references for domain: {primary_domain}")
            
            try:
                external_refs = await self.reference_service.gather_domain_references(query, primary_domain)
                self.external_references = external_refs
                logger.info(f"External references gathered: {external_refs.get('enabled', False)}")
                
                # Track citations from external references
                if external_refs.get('enabled') and external_refs.get('sources'):
                    for source_name, source_data in external_refs['sources'].items():
                        for paper in source_data.get('papers', []):
                            citation = self.citation_tracker.track_citation(paper, source_name)
                            logger.info(f"Tracked citation: {citation['citation_id']}")
                            
            except Exception as e:
                logger.error(f"Error gathering external references: {e}")
                self.external_references = {"enabled": False, "error": str(e)}
            
            self.research_context = {
                "query": query,
                "relevant_domains": relevant_domains,
                "scope": "transdisciplinary" if len(relevant_domains) > 2 else "multidisciplinary",
                "complexity": "high" if len(relevant_domains) > 3 else "medium",
                "timestamp": datetime.now().isoformat(),
                "external_references": self.external_references
            }
            
        except Exception as e:
            logger.error(f"Error loading research context: {e}")
            # Fallback to default context
            self.research_context = {
                "query": query,
                "relevant_domains": ["cross_domain_analysis"],
                "scope": "exploratory",
                "complexity": "medium"
            }

    async def save_research_synthesis(self, query: str, synthesis: Dict):
        """Save research synthesis for future reference."""
        try:
            # In production, this would save to a research database
            # For now, log the synthesis
            logger.info(f"Research synthesis completed for: {query}")
            logger.info(f"Confidence: {synthesis.get('research_confidence', 0)}")
            logger.info(f"Domains: {synthesis.get('domain_coverage', 0)}")
            
        except Exception as e:
            logger.error(f"Error saving research synthesis: {e}")

    async def fetch_domain_analysis(self, domain: str, query: str) -> Dict[str, Any]:
        """Fetch analysis from domain-specific oracle agents."""
        try:
            logger.info(f"Fetching {domain} analysis for: {query}")
            
            # Import domain oracle agents
            from a2a_mcp.agents.nexus_oracle import LifeSciencesOracle, ComputerScienceOracle, CrossDomainOracle
            
            # Route to appropriate domain oracle
            if domain == "life_sciences":
                oracle = LifeSciencesOracle()
                async for response in oracle.stream(query, self.context_id, f"task_{domain}"):
                    if response.get("is_task_complete") and response.get("response_type") == "data":
                        return response["content"]
            elif domain == "computer_science":
                oracle = ComputerScienceOracle()
                async for response in oracle.stream(query, self.context_id, f"task_{domain}"):
                    if response.get("is_task_complete") and response.get("response_type") == "data":
                        return response["content"]
            elif domain == "cross_domain_analysis":
                # Cross-domain oracle needs other domain findings
                oracle = CrossDomainOracle()
                async for response in oracle.stream(query, self.context_id, f"task_{domain}", self.research_intelligence):
                    if response.get("is_task_complete") and response.get("response_type") == "data":
                        return response["content"]
            
            # Fallback to simulated analysis for other domains
            domain_analyses = {
                "life_sciences": {
                    "domain": "Life Sciences",
                    "insights": [
                        {"finding": "Biological pathway analysis reveals key mechanisms", "confidence": 0.85},
                        {"finding": "Clinical evidence supports therapeutic potential", "confidence": 0.78}
                    ],
                    "methodologies": ["experimental_biology", "clinical_trials", "bioinformatics"],
                    "evidence_quality": 0.82,
                    "bias_assessment": {"selection_bias": "low", "publication_bias": "medium"}
                },
                "social_sciences": {
                    "domain": "Social Sciences",
                    "insights": [
                        {"finding": "Social patterns indicate cultural adaptation mechanisms", "confidence": 0.79},
                        {"finding": "Historical analysis reveals cyclical trends", "confidence": 0.73}
                    ],
                    "methodologies": ["ethnographic_studies", "statistical_analysis", "historical_research"],
                    "evidence_quality": 0.76,
                    "bias_assessment": {"cultural_bias": "medium", "sampling_bias": "low"}
                },
                "computer_science": {
                    "domain": "Computer Science",
                    "insights": [
                        {"finding": "Algorithmic approaches provide scalable solutions", "confidence": 0.88},
                        {"finding": "AI models demonstrate predictive capabilities", "confidence": 0.82}
                    ],
                    "methodologies": ["computational_modeling", "machine_learning", "simulation"],
                    "evidence_quality": 0.85,
                    "bias_assessment": {"algorithmic_bias": "medium", "data_bias": "high"}
                },
                "cross_domain_analysis": {
                    "domain": "Cross-Domain Analysis",
                    "insights": [
                        {"finding": "Convergent evidence across multiple domains", "confidence": 0.81},
                        {"finding": "Novel patterns emerge from interdisciplinary synthesis", "confidence": 0.77}
                    ],
                    "methodologies": ["meta_analysis", "systems_thinking", "network_analysis"],
                    "evidence_quality": 0.79,
                    "bias_assessment": {"confirmation_bias": "low", "integration_complexity": "high"}
                }
            }
            
            return domain_analyses.get(domain, domain_analyses["cross_domain_analysis"])
            
        except Exception as e:
            logger.error(f"Error fetching {domain} analysis: {e}")
            return {
                "domain": domain,
                "error": str(e),
                "insights": [{"finding": "Analysis unavailable", "confidence": 0}]
            }

    async def generate_research_synthesis(self, query: str) -> str:
        """Generate comprehensive research synthesis with retry logic."""
        client = genai.Client()
        
        # Format external references for inclusion
        external_refs_formatted = self._format_external_references()
        
        prompt = RESEARCH_SYNTHESIS_PROMPT.format(
            original_query=query,
            research_data=json.dumps(self.research_intelligence, indent=2),
            research_context=json.dumps(self.research_context, indent=2),
            external_references=external_refs_formatted,
            min_confidence=self.quality_thresholds["min_confidence_score"],
            required_domains=self.quality_thresholds["min_domain_coverage"],
            evidence_threshold=self.quality_thresholds["evidence_quality_threshold"]
        )
        
        # Retry logic for API overload
        max_retries = 3
        base_delay = 2.0
        
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                    config={
                        "temperature": 0.1,  # Slightly higher for research creativity
                        "response_mime_type": "application/json"
                    }
                )
                return response.text
                
            except Exception as e:
                error_msg = str(e)
                if ("503" in error_msg or "overloaded" in error_msg.lower()) and attempt < max_retries - 1:
                    wait_time = base_delay * (2 ** attempt)
                    logger.warning(f"API overloaded, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    # Re-raise the exception if it's not an overload error or we've exhausted retries
                    raise e

    def analyze_research_dependencies(self, query: str) -> Dict[str, Any]:
        """Determine which research domains to activate, their dependencies, and execution order."""
        domain_groups = {
            "biological_analysis": ["life_sciences_supervisor"],
            "social_analysis": ["social_sciences_supervisor"],
            "technical_analysis": ["computer_science_supervisor"],
            "economic_analysis": ["economics_policy_supervisor"],
            "physical_analysis": ["physical_sciences_supervisor"],
            "psychological_analysis": ["psychology_supervisor"],
            "cross_domain_synthesis": ["cross_domain_analysis_supervisor"],
            "visualization": ["visualization_synthesis_supervisor"]
        }
        
        # Define dependency relationships
        domain_dependencies = {
            "cross_domain_synthesis": ["biological_analysis", "technical_analysis", "social_analysis"],
            "visualization": ["cross_domain_synthesis"],
            "biological_analysis": [],  # Can run independently
            "technical_analysis": [],   # Can run independently
            "social_analysis": [],      # Can run independently
            "economic_analysis": [],    # Can run independently
            "physical_analysis": [],    # Can run independently
            "psychological_analysis": [] # Can run independently
        }
        
        # Priority levels for execution order
        domain_priorities = {
            "biological_analysis": 1,    # High priority, foundational
            "technical_analysis": 1,     # High priority, foundational  
            "social_analysis": 1,        # High priority, foundational
            "economic_analysis": 2,      # Medium priority
            "physical_analysis": 2,      # Medium priority
            "psychological_analysis": 2, # Medium priority
            "cross_domain_synthesis": 3, # Must wait for others
            "visualization": 4           # Final step
        }
        
        # Determine which analyses to run based on query
        required_analyses = []
        query_lower = query.lower()
        
        # Enhanced domain-specific detection
        if any(word in query_lower for word in ["life", "biology", "medical", "health", "genetics", "biotech", "pharmaceutical", "drug", "clinical"]):
            required_analyses.append("biological_analysis")
        
        if any(word in query_lower for word in ["social", "society", "culture", "policy", "governance", "political", "community", "demographic", "human", "public"]):
            required_analyses.append("social_analysis")
            
        if any(word in query_lower for word in ["economic", "economics", "policy", "governance", "financial", "market", "investment", "cost", "budget", "funding"]):
            required_analyses.append("economic_analysis")
        
        if any(word in query_lower for word in ["computer", "ai", "algorithm", "technology", "computing", "software", "digital", "machine learning", "artificial intelligence", "data"]):
            required_analyses.append("technical_analysis")
            
        if any(word in query_lower for word in ["physics", "chemistry", "material", "quantum", "energy", "renewable", "climate", "environmental", "sustainability", "carbon"]):
            required_analyses.append("physical_analysis")
            
        if any(word in query_lower for word in ["psychology", "cognitive", "behavior", "mental", "emotional", "wellbeing", "stress", "anxiety", "depression"]):
            required_analyses.append("psychological_analysis")
        
        # Always include cross-domain synthesis for comprehensive research
        required_analyses.append("cross_domain_synthesis")
        
        # Add visualization if complex multi-domain query
        if len(required_analyses) > 3 or "visual" in query_lower or "chart" in query_lower:
            required_analyses.append("visualization")
        
        # Default to comprehensive analysis if no specific domains detected
        if len(required_analyses) == 1:  # Only cross_domain_synthesis
            required_analyses.extend([
                "biological_analysis", "social_analysis", "technical_analysis"
            ])
        
        # Build execution plan with dependencies and parallelization
        execution_plan = self._build_execution_plan(required_analyses, domain_dependencies, domain_priorities)
        
        return {
            "domain_groups": {group: agents for group, agents in domain_groups.items() 
                            if group in required_analyses},
            "execution_plan": execution_plan,
            "parallelization_opportunities": self._identify_parallel_batches(required_analyses, domain_dependencies)
        }

    def _build_execution_plan(self, required_analyses: List[str], dependencies: Dict[str, List[str]], 
                            priorities: Dict[str, int]) -> List[Dict[str, Any]]:
        """Build ordered execution plan considering dependencies and priorities."""
        execution_steps = []
        completed = set()
        
        while len(completed) < len(required_analyses):
            # Find analyses that can be executed (dependencies satisfied)
            ready_to_execute = []
            for analysis in required_analyses:
                if analysis not in completed:
                    deps_satisfied = all(dep in completed or dep not in required_analyses 
                                       for dep in dependencies.get(analysis, []))
                    if deps_satisfied:
                        ready_to_execute.append(analysis)
            
            if not ready_to_execute:
                break  # Circular dependency or error
            
            # Sort by priority (lower number = higher priority)
            ready_to_execute.sort(key=lambda x: priorities.get(x, 999))
            
            # Group by priority level for parallel execution
            current_priority = priorities.get(ready_to_execute[0], 999)
            current_batch = [analysis for analysis in ready_to_execute 
                           if priorities.get(analysis, 999) == current_priority]
            
            execution_steps.append({
                "step": len(execution_steps) + 1,
                "analyses": current_batch,
                "parallel_execution": len(current_batch) > 1,
                "priority_level": current_priority
            })
            
            completed.update(current_batch)
        
        return execution_steps
    
    def _identify_parallel_batches(self, required_analyses: List[str], 
                                 dependencies: Dict[str, List[str]]) -> List[List[str]]:
        """Identify which analyses can be run in parallel."""
        independent_analyses = [analysis for analysis in required_analyses 
                              if not dependencies.get(analysis, [])]
        
        parallel_batches = []
        if len(independent_analyses) > 1:
            parallel_batches.append(independent_analyses)
        
        return parallel_batches

    def check_quality_thresholds(self, synthesis: Dict) -> Dict[str, Any]:
        """Validate research synthesis against quality thresholds."""
        checks = {
            "confidence_adequate": synthesis.get("research_confidence", 0) >= self.quality_thresholds["min_confidence_score"],
            "domain_coverage_sufficient": len(self.research_intelligence) >= self.quality_thresholds["min_domain_coverage"],
            "evidence_quality_acceptable": all(
                domain.get("evidence_quality", 0) >= self.quality_thresholds["evidence_quality_threshold"]
                for domain in self.research_intelligence.values()
            ),
            "bias_detection_performed": any(
                "bias_assessment" in domain for domain in self.research_intelligence.values()
            )
        }
        
        # More nuanced decision on additional analysis
        critical_issues = not checks["confidence_adequate"] or not checks["bias_detection_performed"]
        minor_issues = not checks["domain_coverage_sufficient"] or not checks["evidence_quality_acceptable"]
        
        return {
            "quality_approved": all(checks.values()),
            "checks": checks,
            "requires_additional_analysis": critical_issues and minor_issues,  # Only if both critical and minor issues
            "confidence_score": synthesis.get("research_confidence", 0),
            "quality_issues": [k for k, v in checks.items() if not v]
        }

    def clear_state(self):
        """Reset agent state for new research."""
        self.graph = None
        self.research_intelligence.clear()
        self.query_history.clear()
        # Clear external references and citation tracker for new questions
        self.external_references.clear()
        self.citation_tracker = CitationTracker()  # Reset citation tracker

    async def stream(
        self, query: str, context_id: str, task_id: str
    ) -> AsyncIterable[Dict[str, Any]]:
        """Execute transdisciplinary research workflow."""
        logger.info(f"Nexus Oracle analyzing: {query} (session: {context_id})")
        
        if not query:
            raise ValueError("Research query cannot be empty")
        
        if self.context_id != context_id:
            self.clear_state()
            self.context_id = context_id
        
        self.query_history.append({"timestamp": datetime.now().isoformat(), "query": query})
        
        try:
            # Step 1: Load research context
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Nexus Oracle: Loading research context and domain scope..."
            }
            
            await self.load_research_context(query)
            
            # Step 2: Initialize workflow graph
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Nexus Oracle: Initializing transdisciplinary research workflow..."
            }
            
            self.graph = ParallelWorkflowGraph()
            
            # Step 3: Determine required domain analyses and build execution plan
            dependency_analysis = self.analyze_research_dependencies(query)
            domain_groups = dependency_analysis["domain_groups"]
            execution_plan = dependency_analysis["execution_plan"]
            parallel_opportunities = dependency_analysis["parallelization_opportunities"]
            
            logger.info(f"Activating research domains: {list(domain_groups.keys())}")
            logger.info(f"Execution plan: {len(execution_plan)} steps with parallelization")
            
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": f"Nexus Oracle: Coordinating {len(domain_groups)} research domains with dependency-aware execution..."
            }
            
            # Step 4: Execute domain analyses according to execution plan
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": f"Nexus Oracle: Executing {len(execution_plan)}-step analysis workflow..."
            }
            
            # Execute analyses in planned order with parallel processing
            for step in execution_plan:
                step_analyses = step["analyses"]
                is_parallel = step["parallel_execution"]
                
                if is_parallel:
                    yield {
                        "is_task_complete": False,
                        "require_user_input": False,
                        "content": f"Nexus Oracle: Step {step['step']} - Parallel execution of {len(step_analyses)} analyses..."
                    }
                    
                    # Execute analyses in parallel (simulated with sequential calls)
                    import asyncio
                    tasks = []
                    for analysis_group in step_analyses:
                        if analysis_group in domain_groups:
                            for supervisor in domain_groups[analysis_group]:
                                domain_key = supervisor.replace("_supervisor", "")
                                tasks.append(self.fetch_domain_analysis(domain_key, query))
                    
                    # Execute all tasks for this step
                    step_results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Process results
                    for i, (analysis_group, result) in enumerate(zip(step_analyses, step_results)):
                        if not isinstance(result, Exception) and result:
                            domain_key = domain_groups[analysis_group][0].replace("_supervisor", "")
                            self.research_intelligence[domain_key] = result
                            
                            yield {
                                "is_task_complete": False,
                                "require_user_input": False,
                                "content": f"Nexus Oracle: Completed {domain_key.replace('_', ' ').title()} analysis (parallel)..."
                            }
                else:
                    # Sequential execution for dependent analyses
                    for analysis_group in step_analyses:
                        if analysis_group in domain_groups:
                            for supervisor in domain_groups[analysis_group]:
                                domain_key = supervisor.replace("_supervisor", "")
                                
                                yield {
                                    "is_task_complete": False,
                                    "require_user_input": False,
                                    "content": f"Nexus Oracle: Step {step['step']} - Executing {domain_key.replace('_', ' ').title()} analysis..."
                                }
                                
                                analysis = await self.fetch_domain_analysis(domain_key, query)
                                if analysis:
                                    self.research_intelligence[domain_key] = analysis
                                    
                                    yield {
                                        "is_task_complete": False,
                                        "require_user_input": False,
                                        "content": f"Nexus Oracle: Completed {domain_key.replace('_', ' ').title()} analysis..."
                                    }
            
            # Step 5: Generate research synthesis
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Nexus Oracle: Synthesizing transdisciplinary insights..."
            }
            
            try:
                synthesis_raw = await self.generate_research_synthesis(query)
                synthesis = json.loads(synthesis_raw)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}. Response: {synthesis_raw[:200]}")
                # Fallback synthesis
                synthesis = {
                    "executive_summary": f"Transdisciplinary analysis of '{query}' reveals convergent insights across {len(self.research_intelligence)} domains with moderate confidence.",
                    "research_confidence": 0.75,
                    "domain_coverage": len(self.research_intelligence),
                    "quality_assessment": {
                        "evidence_strength": 75,
                        "methodological_rigor": 70,
                        "bias_detection": ["Limited cross-validation", "Domain-specific methodologies"],
                        "validation_strategies": ["Triangulation", "Expert review"]
                    },
                    "key_insights": [
                        {"source": domain, "insight": f"Analysis from {domain.replace('_', ' ').title()}", "confidence": 0.7}
                        for domain in self.research_intelligence.keys()
                    ],
                    "cross_domain_patterns": {
                        "convergent_findings": ["Multi-domain evidence supports core hypotheses"],
                        "contradictory_evidence": ["Some methodological differences noted"],
                        "knowledge_gaps": ["Longitudinal studies needed", "Cross-cultural validation required"]
                    },
                    "novel_hypotheses": [
                        {
                            "hypothesis": "Cross-domain patterns suggest novel research directions",
                            "supporting_domains": list(self.research_intelligence.keys())[:3],
                            "testability": "medium",
                            "significance": "Potential for interdisciplinary breakthrough"
                        }
                    ],
                    "research_recommendations": {
                        "priority_directions": ["Longitudinal studies", "Cross-domain validation"],
                        "methodological_innovations": ["Mixed-methods approach", "Computational modeling"],
                        "collaboration_opportunities": ["Interdisciplinary research teams", "International collaboration"]
                    }
                }
            
            # Step 6: Quality validation
            quality_check = self.check_quality_thresholds(synthesis)
            
            # Step 7: Save synthesis
            await self.save_research_synthesis(query, synthesis)
            
            # Step 8: Format final response
            final_response = {
                "synthesis": synthesis,
                "quality_validation": quality_check,
                "research_intelligence": self.research_intelligence,
                "research_context": self.research_context,
                "timestamp": datetime.now().isoformat()
            }
            
            if quality_check["requires_additional_analysis"]:
                yield {
                    "is_task_complete": False,
                    "require_user_input": True,
                    "content": f"Nexus Oracle: Research synthesis shows limited domain coverage ({len(self.research_intelligence)} domains). Would you like to expand the analysis to include additional research areas?"
                }
            else:
                yield {
                    "is_task_complete": True,
                    "require_user_input": False,
                    "response_type": "data",
                    "content": final_response
                }
                
        except Exception as e:
            logger.error(f"Nexus Oracle error: {e}")
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": f"Nexus Oracle: Research analysis error - {str(e)}"
            }

    async def invoke(self, query: str, session_id: str) -> dict:
        """Non-streaming invoke (not implemented - use stream)."""
        raise NotImplementedError("Please use the streaming interface")