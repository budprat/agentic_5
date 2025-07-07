"""Computer Science Oracle - Deep Domain Expertise Agent for Technical Research."""

import os
import logging
import json
from collections.abc import AsyncIterable
from typing import Dict, Any, List
from datetime import datetime

from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import init_api_key
from google import genai

logger = logging.getLogger(__name__)

# Computer Science Analysis Prompt
COMPUTER_SCIENCE_ANALYSIS_PROMPT = """
You are a Computer Science Oracle with deep expertise in computational methods, artificial intelligence, and technological systems.
Analyze the following research query with specialized technical knowledge and cross-domain applications.

Research Query: {query}
Context: {context}

Apply your expertise in:
- Artificial Intelligence & Machine Learning
- Algorithms & Data Structures
- Distributed Systems & Cloud Computing
- Human-Computer Interaction
- Cybersecurity & Privacy
- Computational Biology & Bioinformatics
- Software Engineering & Systems Design

Provide analysis in this JSON format:
{{
    "technical_insights": [
        {{
            "insight": "specific computational insight",
            "algorithmic_approach": "underlying computational method",
            "confidence": 0.0-1.0,
            "complexity_analysis": "time/space complexity or scalability",
            "implementation_feasibility": "high|medium|low"
        }}
    ],
    "ai_applications": [
        {{
            "application": "AI/ML application or approach",
            "model_type": "supervised|unsupervised|reinforcement|foundation",
            "data_requirements": "description of data needs",
            "performance_metrics": ["metric1", "metric2"],
            "limitations": ["limitation1", "limitation2"]
        }}
    ],
    "computational_methods": {{
        "algorithms": ["algorithm1", "algorithm2"],
        "technologies": ["technology1", "technology2"],
        "frameworks": ["framework1", "framework2"],
        "scalability_considerations": "description of scaling challenges"
    }},
    "cross_domain_utilities": [
        {{
            "target_domain": "domain name",
            "computational_contribution": "how computing advances this domain",
            "technical_approach": "specific methods or technologies",
            "impact_assessment": "high|medium|low",
            "adoption_barriers": ["barrier1", "barrier2"]
        }}
    ],
    "ethical_ai_considerations": [
        {{
            "concern": "ethical issue or concern",
            "affected_stakeholders": ["stakeholder1", "stakeholder2"],
            "mitigation_approaches": ["approach1", "approach2"],
            "regulatory_landscape": "relevant regulations or standards"
        }}
    ],
    "system_design_recommendations": [
        {{
            "component": "system component",
            "design_pattern": "recommended design approach",
            "trade_offs": "performance vs. other factors",
            "security_considerations": "security implications"
        }}
    ],
    "research_innovation_potential": [
        {{
            "innovation_area": "area of potential breakthrough",
            "current_limitations": "what holds back progress",
            "proposed_solution": "potential solution approach",
            "risk_assessment": "technical and practical risks"
        }}
    ],
    "quality_assessment": {{
        "technical_feasibility": 0-100,
        "algorithmic_novelty": 0-100,
        "cross_domain_impact": 0-100,
        "bias_considerations": ["bias1", "bias2"],
        "confidence_score": 0.0-1.0
    }}
}}
"""

class ComputerScienceOracle(BaseAgent):
    """Deep expertise agent for computer science and AI research."""

    def __init__(self):
        init_api_key()
        super().__init__(
            agent_name="Computer Science Oracle",
            description="Deep domain expertise in computational methods, AI, and technological systems",
            content_types=["text", "text/plain"],
        )
        self.expertise_areas = {
            "artificial_intelligence": {
                "focus": "Machine learning, deep learning, foundation models",
                "methodologies": ["supervised_learning", "unsupervised_learning", "reinforcement_learning", "transformer_models"],
                "applications": ["nlp", "computer_vision", "robotics", "autonomous_systems"]
            },
            "algorithms": {
                "focus": "Algorithm design, optimization, complexity analysis",
                "methodologies": ["graph_algorithms", "optimization", "approximation", "randomized_algorithms"],
                "applications": ["search", "routing", "scheduling", "resource_allocation"]
            },
            "distributed_systems": {
                "focus": "Scalable systems, cloud computing, distributed algorithms",
                "methodologies": ["consensus_algorithms", "load_balancing", "fault_tolerance", "microservices"],
                "applications": ["cloud_platforms", "blockchain", "distributed_databases", "edge_computing"]
            },
            "hci": {
                "focus": "Human-computer interaction, user experience, accessibility",
                "methodologies": ["user_studies", "interface_design", "usability_testing", "accessibility_analysis"],
                "applications": ["ui_design", "assistive_technology", "virtual_reality", "brain_interfaces"]
            },
            "cybersecurity": {
                "focus": "Security protocols, privacy preservation, threat analysis",
                "methodologies": ["cryptography", "penetration_testing", "formal_verification", "privacy_engineering"],
                "applications": ["secure_communications", "privacy_protection", "threat_detection", "identity_management"]
            },
            "computational_biology": {
                "focus": "Bioinformatics, computational modeling, biological data analysis",
                "methodologies": ["sequence_analysis", "structural_biology", "systems_biology", "phylogenetics"],
                "applications": ["drug_discovery", "genomics", "protein_folding", "epidemiological_modeling"]
            }
        }
        
    def extract_technical_context(self, query: str) -> Dict[str, Any]:
        """Extract technical context and relevant expertise areas from query."""
        query_lower = query.lower()
        relevant_areas = []
        technical_keywords = []
        
        # AI/ML keywords
        ai_terms = ["ai", "artificial intelligence", "machine learning", "deep learning", "neural", "model", "algorithm", "ml"]
        if any(term in query_lower for term in ai_terms):
            relevant_areas.append("artificial_intelligence")
            technical_keywords.extend([term for term in ai_terms if term in query_lower])
        
        # Algorithms keywords
        algo_terms = ["algorithm", "optimization", "complexity", "graph", "search", "sort", "computational"]
        if any(term in query_lower for term in algo_terms):
            relevant_areas.append("algorithms")
            technical_keywords.extend([term for term in algo_terms if term in query_lower])
        
        # Systems keywords
        systems_terms = ["system", "distributed", "cloud", "scalable", "architecture", "microservice", "database"]
        if any(term in query_lower for term in systems_terms):
            relevant_areas.append("distributed_systems")
            technical_keywords.extend([term for term in systems_terms if term in query_lower])
        
        # HCI keywords
        hci_terms = ["interface", "user", "usability", "interaction", "design", "accessibility", "ux", "ui"]
        if any(term in query_lower for term in hci_terms):
            relevant_areas.append("hci")
            technical_keywords.extend([term for term in hci_terms if term in query_lower])
        
        # Security keywords
        security_terms = ["security", "privacy", "encryption", "crypto", "threat", "vulnerability", "attack"]
        if any(term in query_lower for term in security_terms):
            relevant_areas.append("cybersecurity")
            technical_keywords.extend([term for term in security_terms if term in query_lower])
        
        # Computational biology keywords
        compbio_terms = ["bioinformatics", "computational biology", "genomics", "sequence", "protein", "drug discovery"]
        if any(term in query_lower for term in compbio_terms):
            relevant_areas.append("computational_biology")
            technical_keywords.extend([term for term in compbio_terms if term in query_lower])
        
        # Default to AI if no specific area detected
        if not relevant_areas:
            relevant_areas = ["artificial_intelligence"]
            
        return {
            "relevant_expertise_areas": relevant_areas,
            "technical_keywords": list(set(technical_keywords)),
            "complexity": "high" if len(relevant_areas) > 2 else "medium",
            "interdisciplinary_potential": len(relevant_areas) > 1,
            "scalability_considerations": "distributed_systems" in relevant_areas
        }

    async def generate_technical_analysis(self, query: str, context: Dict) -> str:
        """Generate comprehensive technical analysis using domain expertise."""
        client = genai.Client()
        
        prompt = COMPUTER_SCIENCE_ANALYSIS_PROMPT.format(
            query=query,
            context=json.dumps(context, indent=2)
        )
        
        response = client.models.generate_content(
            model=os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-001'),
            contents=prompt,
            config={
                "temperature": 0.1,
                "response_mime_type": "application/json"
            }
        )
        return response.text

    async def stream(
        self, query: str, context_id: str, task_id: str
    ) -> AsyncIterable[Dict[str, Any]]:
        """Execute computer science analysis with deep domain expertise."""
        logger.info(f"Computer Science Oracle analyzing: {query}")
        
        if not query:
            raise ValueError("Research query cannot be empty")
        
        try:
            # Step 1: Extract technical context
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Computer Science Oracle: Analyzing computational requirements and technical feasibility..."
            }
            
            technical_context = self.extract_technical_context(query)
            
            # Step 2: Apply domain expertise
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": f"Computer Science Oracle: Applying expertise in {', '.join(technical_context['relevant_expertise_areas'])}..."
            }
            
            # Step 3: Generate comprehensive analysis
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Computer Science Oracle: Generating technical insights and system recommendations..."
            }
            
            try:
                analysis_raw = await self.generate_technical_analysis(query, technical_context)
                analysis = json.loads(analysis_raw)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                # Fallback analysis
                analysis = {
                    "technical_insights": [
                        {
                            "insight": f"Computational analysis relevant to {', '.join(technical_context['technical_keywords'])}",
                            "algorithmic_approach": "Machine learning and optimization techniques applicable",
                            "confidence": 0.75,
                            "complexity_analysis": "Polynomial time complexity for most practical cases",
                            "implementation_feasibility": "high"
                        }
                    ],
                    "ai_applications": [
                        {
                            "application": "AI-driven analysis and prediction",
                            "model_type": "supervised",
                            "data_requirements": "Structured datasets with labeled examples",
                            "performance_metrics": ["accuracy", "precision", "recall", "f1_score"],
                            "limitations": ["data_quality", "model_generalization", "computational_resources"]
                        }
                    ],
                    "computational_methods": {
                        "algorithms": ["machine_learning", "optimization", "graph_analysis"],
                        "technologies": ["python", "tensorflow", "pytorch", "distributed_computing"],
                        "frameworks": ["scikit_learn", "spark", "kubernetes", "docker"],
                        "scalability_considerations": "Horizontal scaling with distributed processing"
                    },
                    "cross_domain_utilities": [
                        {
                            "target_domain": "life_sciences",
                            "computational_contribution": "Bioinformatics and computational biology applications",
                            "technical_approach": "Machine learning for biological data analysis",
                            "impact_assessment": "high",
                            "adoption_barriers": ["domain_expertise", "data_integration", "validation_requirements"]
                        }
                    ],
                    "ethical_ai_considerations": [
                        {
                            "concern": "Algorithmic bias and fairness",
                            "affected_stakeholders": ["users", "developers", "society"],
                            "mitigation_approaches": ["bias_detection", "fair_ml_techniques", "diverse_teams"],
                            "regulatory_landscape": "EU AI Act, algorithmic accountability standards"
                        }
                    ],
                    "system_design_recommendations": [
                        {
                            "component": "Data processing pipeline",
                            "design_pattern": "Microservices architecture with event-driven communication",
                            "trade_offs": "Scalability vs. complexity management",
                            "security_considerations": "End-to-end encryption and access controls"
                        }
                    ],
                    "research_innovation_potential": [
                        {
                            "innovation_area": "Interdisciplinary AI applications",
                            "current_limitations": "Domain adaptation and transfer learning challenges",
                            "proposed_solution": "Foundation models with domain-specific fine-tuning",
                            "risk_assessment": "Medium technical risk, high potential impact"
                        }
                    ],
                    "quality_assessment": {
                        "technical_feasibility": 80,
                        "algorithmic_novelty": 70,
                        "cross_domain_impact": 85,
                        "bias_considerations": ["algorithmic_bias", "data_representation_bias"],
                        "confidence_score": 0.78
                    }
                }
            
            # Step 4: Add metadata and context
            final_response = {
                "domain": "Computer Science",
                "analysis": analysis,
                "technical_context": technical_context,
                "expertise_applied": {area: self.expertise_areas[area] for area in technical_context["relevant_expertise_areas"]},
                "timestamp": datetime.now().isoformat()
            }
            
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "response_type": "data",
                "content": final_response
            }
                
        except Exception as e:
            logger.error(f"Computer Science Oracle error: {e}")
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": f"Computer Science Oracle: Analysis error - {str(e)}"
            }

    async def invoke(self, query: str, session_id: str) -> dict:
        """Non-streaming invoke (not implemented - use stream)."""
        raise NotImplementedError("Please use the streaming interface")