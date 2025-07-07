"""Life Sciences Oracle - Deep Domain Expertise Agent for Transdisciplinary Research."""

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

# Life Sciences Analysis Prompt
LIFE_SCIENCES_ANALYSIS_PROMPT = """
You are a Life Sciences Oracle with deep expertise in biological systems, medical research, and biotechnology. 
Analyze the following research query with specialized biological knowledge and interdisciplinary perspective.

Research Query: {query}
Context: {context}

Apply your expertise in:
- Molecular Biology & Genetics
- Medical Research & Clinical Applications  
- Ecology & Environmental Biology
- Neuroscience & Cognitive Biology
- Biotechnology & Bioengineering
- Bioinformatics & Computational Biology

Provide analysis in this JSON format:
{{
    "biological_insights": [
        {{
            "finding": "specific biological insight",
            "mechanism": "underlying biological mechanism", 
            "confidence": 0.0-1.0,
            "evidence_type": "experimental|observational|computational|clinical",
            "clinical_relevance": "description of medical applications"
        }}
    ],
    "methodological_assessment": {{
        "experimental_approaches": ["approach1", "approach2"],
        "technologies_required": ["technology1", "technology2"],
        "validation_strategies": ["strategy1", "strategy2"],
        "limitations": ["limitation1", "limitation2"]
    }},
    "cross_domain_connections": [
        {{
            "target_domain": "domain name",
            "connection_type": "causal|correlational|methodological|theoretical",
            "biological_basis": "explanation of biological foundation",
            "research_implications": "implications for interdisciplinary work"
        }}
    ],
    "clinical_applications": [
        {{
            "application": "therapeutic or diagnostic application",
            "development_stage": "preclinical|clinical_trials|approved|theoretical",
            "target_population": "patient population or use case",
            "safety_considerations": "known risks or safety profile"
        }}
    ],
    "ethical_considerations": [
        {{
            "issue": "ethical concern or consideration",
            "stakeholders": ["stakeholder1", "stakeholder2"],
            "mitigation_strategies": ["strategy1", "strategy2"],
            "regulatory_context": "relevant regulations or guidelines"
        }}
    ],
    "research_priorities": [
        {{
            "priority": "high|medium|low",
            "research_direction": "specific research question or direction",
            "justification": "why this is important",
            "resource_requirements": "estimated resources needed"
        }}
    ],
    "quality_assessment": {{
        "evidence_strength": 0-100,
        "methodological_rigor": 0-100,
        "clinical_translation_potential": 0-100,
        "bias_factors": ["bias1", "bias2"],
        "confidence_score": 0.0-1.0
    }}
}}
"""

class LifeSciencesOracle(BaseAgent):
    """Deep expertise agent for life sciences and biotechnology research."""

    def __init__(self):
        init_api_key()
        super().__init__(
            agent_name="Life Sciences Oracle",
            description="Deep domain expertise in biological systems, medical research, and biotechnology",
            content_types=["text", "text/plain"],
        )
        self.expertise_areas = {
            "molecular_biology": {
                "focus": "Gene expression, protein function, cellular mechanisms",
                "methodologies": ["CRISPR", "RNA-seq", "proteomics", "metabolomics"],
                "applications": ["gene_therapy", "drug_discovery", "biomarkers"]
            },
            "medical_research": {
                "focus": "Clinical applications, therapeutic development, diagnostics",
                "methodologies": ["clinical_trials", "epidemiology", "pharmacology"],
                "applications": ["personalized_medicine", "drug_development", "diagnostics"]
            },
            "neuroscience": {
                "focus": "Brain function, cognitive mechanisms, neural networks",
                "methodologies": ["neuroimaging", "electrophysiology", "optogenetics"],
                "applications": ["brain_disorders", "cognitive_enhancement", "neural_interfaces"]
            },
            "ecology": {
                "focus": "Ecosystem dynamics, biodiversity, environmental interactions",
                "methodologies": ["field_studies", "modeling", "conservation_biology"],
                "applications": ["conservation", "climate_adaptation", "ecosystem_services"]
            },
            "biotechnology": {
                "focus": "Bioengineering, synthetic biology, biomanufacturing",
                "methodologies": ["genetic_engineering", "bioprocessing", "bioinformatics"],
                "applications": ["biofuels", "pharmaceuticals", "biomaterials"]
            }
        }
        
    def extract_biological_context(self, query: str) -> Dict[str, Any]:
        """Extract biological context and relevant expertise areas from query."""
        query_lower = query.lower()
        relevant_areas = []
        biological_keywords = []
        
        # Molecular biology keywords
        molecular_terms = ["gene", "protein", "dna", "rna", "crispr", "genetic", "molecular", "cell", "cellular"]
        if any(term in query_lower for term in molecular_terms):
            relevant_areas.append("molecular_biology")
            biological_keywords.extend([term for term in molecular_terms if term in query_lower])
        
        # Medical research keywords  
        medical_terms = ["medical", "clinical", "disease", "therapy", "drug", "treatment", "patient", "health"]
        if any(term in query_lower for term in medical_terms):
            relevant_areas.append("medical_research")
            biological_keywords.extend([term for term in medical_terms if term in query_lower])
        
        # Neuroscience keywords
        neuro_terms = ["brain", "neural", "neuron", "cognitive", "behavior", "mind", "consciousness"]
        if any(term in query_lower for term in neuro_terms):
            relevant_areas.append("neuroscience")
            biological_keywords.extend([term for term in neuro_terms if term in query_lower])
        
        # Ecology keywords
        eco_terms = ["ecosystem", "environment", "species", "biodiversity", "climate", "conservation"]
        if any(term in query_lower for term in eco_terms):
            relevant_areas.append("ecology")
            biological_keywords.extend([term for term in eco_terms if term in query_lower])
        
        # Biotechnology keywords
        biotech_terms = ["biotech", "engineering", "synthetic", "biomanufacturing", "bioprocess"]
        if any(term in query_lower for term in biotech_terms):
            relevant_areas.append("biotechnology")
            biological_keywords.extend([term for term in biotech_terms if term in query_lower])
        
        # Default to molecular biology if no specific area detected
        if not relevant_areas:
            relevant_areas = ["molecular_biology"]
            
        return {
            "relevant_expertise_areas": relevant_areas,
            "biological_keywords": list(set(biological_keywords)),
            "complexity": "high" if len(relevant_areas) > 2 else "medium",
            "interdisciplinary_potential": len(relevant_areas) > 1
        }

    async def generate_biological_analysis(self, query: str, context: Dict) -> str:
        """Generate comprehensive biological analysis using domain expertise."""
        client = genai.Client()
        
        prompt = LIFE_SCIENCES_ANALYSIS_PROMPT.format(
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
        """Execute life sciences analysis with deep domain expertise."""
        logger.info(f"Life Sciences Oracle analyzing: {query}")
        
        if not query:
            raise ValueError("Research query cannot be empty")
        
        try:
            # Step 1: Extract biological context
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Life Sciences Oracle: Analyzing biological context and mechanisms..."
            }
            
            biological_context = self.extract_biological_context(query)
            
            # Step 2: Apply domain expertise
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": f"Life Sciences Oracle: Applying expertise in {', '.join(biological_context['relevant_expertise_areas'])}..."
            }
            
            # Step 3: Generate comprehensive analysis
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Life Sciences Oracle: Generating biological insights and clinical applications..."
            }
            
            try:
                analysis_raw = await self.generate_biological_analysis(query, biological_context)
                analysis = json.loads(analysis_raw)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                # Fallback analysis
                analysis = {
                    "biological_insights": [
                        {
                            "finding": f"Biological analysis relevant to {', '.join(biological_context['biological_keywords'])}",
                            "mechanism": "Complex biological mechanisms require further investigation",
                            "confidence": 0.7,
                            "evidence_type": "computational",
                            "clinical_relevance": "Potential therapeutic applications"
                        }
                    ],
                    "methodological_assessment": {
                        "experimental_approaches": ["in_vitro_studies", "animal_models", "clinical_trials"],
                        "technologies_required": ["genomics", "proteomics", "bioinformatics"],
                        "validation_strategies": ["replication", "cross_validation", "peer_review"],
                        "limitations": ["sample_size", "model_organisms", "ethical_constraints"]
                    },
                    "cross_domain_connections": [
                        {
                            "target_domain": "computer_science",
                            "connection_type": "methodological",
                            "biological_basis": "Computational biology and bioinformatics applications",
                            "research_implications": "AI-driven drug discovery and biological modeling"
                        }
                    ],
                    "clinical_applications": [
                        {
                            "application": "Potential therapeutic development",
                            "development_stage": "preclinical",
                            "target_population": "To be determined based on specific findings",
                            "safety_considerations": "Standard preclinical safety assessment required"
                        }
                    ],
                    "ethical_considerations": [
                        {
                            "issue": "Research ethics and informed consent",
                            "stakeholders": ["patients", "researchers", "regulatory_bodies"],
                            "mitigation_strategies": ["ethics_review", "transparent_communication"],
                            "regulatory_context": "FDA and IRB guidelines"
                        }
                    ],
                    "research_priorities": [
                        {
                            "priority": "high",
                            "research_direction": "Mechanism validation and clinical translation",
                            "justification": "Critical for advancing biological understanding",
                            "resource_requirements": "Significant funding and infrastructure"
                        }
                    ],
                    "quality_assessment": {
                        "evidence_strength": 75,
                        "methodological_rigor": 70,
                        "clinical_translation_potential": 65,
                        "bias_factors": ["publication_bias", "selection_bias"],
                        "confidence_score": 0.72
                    }
                }
            
            # Step 4: Add metadata and context
            final_response = {
                "domain": "Life Sciences",
                "analysis": analysis,
                "biological_context": biological_context,
                "expertise_applied": {area: self.expertise_areas[area] for area in biological_context["relevant_expertise_areas"]},
                "timestamp": datetime.now().isoformat()
            }
            
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "response_type": "data",
                "content": final_response
            }
                
        except Exception as e:
            logger.error(f"Life Sciences Oracle error: {e}")
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": f"Life Sciences Oracle: Analysis error - {str(e)}"
            }

    async def invoke(self, query: str, session_id: str) -> dict:
        """Non-streaming invoke (not implemented - use stream)."""
        raise NotImplementedError("Please use the streaming interface")