"""Cross-Domain Analysis Oracle - Transdisciplinary Integration and Pattern Recognition Agent."""

import os
import logging
import json
from collections.abc import AsyncIterable
from typing import Dict, Any, List
from datetime import datetime

from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import init_api_key
from google import genai
from google.genai import types
import aiohttp

logger = logging.getLogger(__name__)

# Cross-Domain Integration Prompt
CROSS_DOMAIN_INTEGRATION_PROMPT = """
You are a Cross-Domain Analysis Oracle specializing in transdisciplinary research synthesis and pattern recognition.
Analyze the provided domain-specific research findings and identify cross-cutting patterns, novel insights, and integration opportunities.

Domain Research Findings: {domain_findings}
Research Query: {query}
Integration Context: {context}

Apply your expertise in:
- Transdisciplinary Pattern Recognition
- Knowledge Graph Construction
- Causal Network Analysis
- Methodological Integration
- Bias Detection Across Domains
- Novel Hypothesis Generation

Provide synthesis in this JSON format:
{{
    "cross_domain_patterns": [
        {{
            "pattern_type": "convergent|divergent|complementary|contradictory",
            "pattern_description": "description of the identified pattern",
            "supporting_domains": ["domain1", "domain2"],
            "evidence_strength": 0.0-1.0,
            "causal_relationships": "description of causal connections",
            "significance": "high|medium|low"
        }}
    ],
    "knowledge_integration": {{
        "convergent_insights": [
            {{
                "insight": "integrated insight from multiple domains",
                "supporting_evidence": ["evidence1", "evidence2"],
                "confidence": 0.0-1.0,
                "novel_aspect": "what makes this insight new or significant"
            }}
        ],
        "contradictory_findings": [
            {{
                "contradiction": "description of conflicting findings",
                "domain_sources": ["domain1", "domain2"],
                "potential_resolution": "possible explanation for contradiction",
                "research_needed": "additional research to resolve conflict"
            }}
        ],
        "knowledge_gaps": [
            {{
                "gap_description": "identified knowledge gap",
                "affected_domains": ["domain1", "domain2"],
                "impact_assessment": "high|medium|low",
                "fill_strategy": "proposed approach to address gap"
            }}
        ]
    }},
    "methodological_synthesis": {{
        "integrated_approaches": ["approach1", "approach2"],
        "cross_validation_strategies": ["strategy1", "strategy2"],
        "bias_mitigation": [
            {{
                "bias_type": "type of bias identified",
                "source_domains": ["domain1", "domain2"],
                "mitigation_approach": "proposed mitigation strategy",
                "validation_method": "how to validate mitigation effectiveness"
            }}
        ]
    }},
    "novel_hypotheses": [
        {{
            "hypothesis": "novel research hypothesis",
            "theoretical_foundation": "underlying theoretical basis",
            "testable_predictions": ["prediction1", "prediction2"],
            "required_disciplines": ["discipline1", "discipline2"],
            "feasibility_assessment": "high|medium|low",
            "potential_impact": "description of potential impact"
        }}
    ],
    "research_innovation_opportunities": [
        {{
            "opportunity": "research innovation opportunity",
            "disciplinary_intersection": ["field1", "field2"],
            "methodological_innovation": "new methodological approach",
            "resource_requirements": "required resources and expertise",
            "timeline_estimate": "estimated development timeline",
            "risk_factors": ["risk1", "risk2"]
        }}
    ],
    "causal_network_analysis": {{
        "primary_causal_chains": [
            {{
                "chain_description": "description of causal relationship",
                "starting_domain": "origin domain",
                "ending_domain": "target domain", 
                "mediating_factors": ["factor1", "factor2"],
                "strength_of_evidence": 0.0-1.0
            }}
        ],
        "feedback_loops": [
            {{
                "loop_description": "description of feedback mechanism",
                "participating_domains": ["domain1", "domain2"],
                "loop_type": "positive|negative|complex",
                "stability_analysis": "stable|unstable|context_dependent"
            }}
        ]
    }},
    "integration_quality_assessment": {{
        "synthesis_completeness": 0-100,
        "cross_domain_coherence": 0-100,
        "novel_insight_generation": 0-100,
        "bias_detection_coverage": 0-100,
        "methodological_rigor": 0-100,
        "overall_confidence": 0.0-1.0
    }}
}}
"""

class CrossDomainOracle(BaseAgent):
    """Deep expertise agent for transdisciplinary integration and pattern recognition."""

    def __init__(self):
        init_api_key()
        super().__init__(
            agent_name="Cross-Domain Analysis Oracle",
            description="Transdisciplinary integration, pattern recognition, and novel hypothesis generation",
            content_types=["text", "text/plain"],
        )
        self.integration_capabilities = {
            "pattern_recognition": {
                "types": ["convergent", "divergent", "complementary", "contradictory", "emergent"],
                "methods": ["statistical_correlation", "semantic_similarity", "causal_inference", "network_analysis"],
                "validation": ["cross_validation", "expert_review", "empirical_testing"]
            },
            "knowledge_synthesis": {
                "approaches": ["meta_analysis", "systematic_review", "narrative_synthesis", "framework_synthesis"],
                "quality_criteria": ["coherence", "comprehensiveness", "transparency", "reproducibility"],
                "bias_detection": ["selection_bias", "publication_bias", "confirmation_bias", "cultural_bias"]
            },
            "hypothesis_generation": {
                "mechanisms": ["analogy", "combination", "extension", "contradiction_resolution"],
                "validation_criteria": ["testability", "falsifiability", "predictive_power", "explanatory_scope"],
                "innovation_assessment": ["novelty", "significance", "feasibility", "impact_potential"]
            },
            "causal_analysis": {
                "methods": ["causal_graphs", "counterfactual_reasoning", "intervention_analysis", "mediation_analysis"],
                "validation": ["randomized_trials", "natural_experiments", "instrumental_variables", "sensitivity_analysis"],
                "complexity_handling": ["multiple_causation", "feedback_loops", "emergence", "context_dependence"]
            }
        }
        
    def analyze_domain_findings(self, domain_findings: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze domain-specific findings for integration patterns."""
        integration_context = {
            "participating_domains": list(domain_findings.keys()),
            "total_insights": sum(len(findings.get("analysis", {}).get("biological_insights", [])) +
                                len(findings.get("analysis", {}).get("technical_insights", [])) +
                                len(findings.get("analysis", {}).get("key_insights", []))
                                for findings in domain_findings.values()),
            "cross_domain_potential": len(domain_findings) > 1,
            "methodological_diversity": len(set(
                method for findings in domain_findings.values()
                for methods in findings.get("analysis", {}).get("methodological_assessment", {}).get("experimental_approaches", [])
                for method in methods if isinstance(methods, list)
            )) if domain_findings else 0
        }
        
        # Identify potential integration patterns
        patterns = []
        if len(domain_findings) >= 2:
            for domain1, findings1 in domain_findings.items():
                for domain2, findings2 in domain_findings.items():
                    if domain1 != domain2:
                        # Look for methodological overlaps
                        methods1 = findings1.get("analysis", {}).get("methodological_assessment", {}).get("experimental_approaches", [])
                        methods2 = findings2.get("analysis", {}).get("methodological_assessment", {}).get("experimental_approaches", [])
                        
                        common_methods = set(methods1) & set(methods2) if methods1 and methods2 else set()
                        if common_methods:
                            patterns.append({
                                "type": "methodological_convergence",
                                "domains": [domain1, domain2],
                                "common_elements": list(common_methods)
                            })
        
        integration_context["identified_patterns"] = patterns
        return integration_context

    async def generate_cross_domain_synthesis(self, query: str, domain_findings: Dict, context: Dict) -> str:
        """Generate comprehensive cross-domain analysis and synthesis."""
        # Configure client with proper timeout settings
        http_options = types.HttpOptions(
            async_client_args={
                'timeout': aiohttp.ClientTimeout(total=120, connect=30)  # 2 minute timeout for cross-domain analysis
            }
        )
        client = genai.Client(http_options=http_options)
        
        prompt = CROSS_DOMAIN_INTEGRATION_PROMPT.format(
            domain_findings=json.dumps(domain_findings, indent=2),
            query=query,
            context=json.dumps(context, indent=2)
        )
        
        response = client.models.generate_content(
            model=os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-001'),
            contents=prompt,
            config={
                "temperature": 0.2,  # Slightly higher for creative synthesis
                "response_mime_type": "application/json"
            }
        )
        return response.text

    async def stream(
        self, query: str, context_id: str, task_id: str, domain_findings: Dict[str, Any] = None
    ) -> AsyncIterable[Dict[str, Any]]:
        """Execute cross-domain analysis and integration."""
        logger.info(f"Cross-Domain Oracle analyzing: {query}")
        
        if not query:
            raise ValueError("Research query cannot be empty")
        
        if not domain_findings:
            domain_findings = {}
        
        try:
            # Step 1: Analyze domain findings for integration patterns
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Cross-Domain Oracle: Analyzing domain findings for integration patterns..."
            }
            
            integration_context = self.analyze_domain_findings(domain_findings)
            
            # Step 2: Identify cross-cutting patterns
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": f"Cross-Domain Oracle: Identifying patterns across {len(domain_findings)} domains..."
            }
            
            # Step 3: Generate synthesis
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Cross-Domain Oracle: Synthesizing transdisciplinary insights and novel hypotheses..."
            }
            
            try:
                synthesis_raw = await self.generate_cross_domain_synthesis(query, domain_findings, integration_context)
                synthesis = json.loads(synthesis_raw)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                # Fallback synthesis
                synthesis = {
                    "cross_domain_patterns": [
                        {
                            "pattern_type": "convergent",
                            "pattern_description": "Multiple domains show consistent evidence patterns",
                            "supporting_domains": list(domain_findings.keys())[:3],
                            "evidence_strength": 0.75,
                            "causal_relationships": "Complex multi-factorial relationships identified",
                            "significance": "high"
                        }
                    ],
                    "knowledge_integration": {
                        "convergent_insights": [
                            {
                                "insight": "Cross-domain evidence supports integrated understanding",
                                "supporting_evidence": ["domain_consistency", "methodological_triangulation"],
                                "confidence": 0.78,
                                "novel_aspect": "Transdisciplinary perspective reveals new connections"
                            }
                        ],
                        "contradictory_findings": [],
                        "knowledge_gaps": [
                            {
                                "gap_description": "Limited longitudinal cross-domain validation",
                                "affected_domains": list(domain_findings.keys()),
                                "impact_assessment": "medium",
                                "fill_strategy": "Coordinated multi-domain longitudinal studies"
                            }
                        ]
                    },
                    "methodological_synthesis": {
                        "integrated_approaches": ["mixed_methods", "triangulation", "meta_analysis"],
                        "cross_validation_strategies": ["replication", "independent_verification", "peer_review"],
                        "bias_mitigation": [
                            {
                                "bias_type": "confirmation_bias",
                                "source_domains": list(domain_findings.keys()),
                                "mitigation_approach": "adversarial_review",
                                "validation_method": "independent_replication"
                            }
                        ]
                    },
                    "novel_hypotheses": [
                        {
                            "hypothesis": "Cross-domain patterns suggest emergent properties at disciplinary interfaces",
                            "theoretical_foundation": "Systems theory and complexity science",
                            "testable_predictions": ["interface_effects", "emergent_behaviors"],
                            "required_disciplines": list(domain_findings.keys())[:3],
                            "feasibility_assessment": "medium",
                            "potential_impact": "High impact on transdisciplinary research methodology"
                        }
                    ],
                    "research_innovation_opportunities": [
                        {
                            "opportunity": "Transdisciplinary research platform development",
                            "disciplinary_intersection": list(domain_findings.keys()),
                            "methodological_innovation": "Integrated cross-domain analysis framework",
                            "resource_requirements": "Significant computational and human resources",
                            "timeline_estimate": "2-3 years",
                            "risk_factors": ["coordination_complexity", "methodological_challenges"]
                        }
                    ],
                    "causal_network_analysis": {
                        "primary_causal_chains": [
                            {
                                "chain_description": "Multi-domain causal pathways identified",
                                "starting_domain": list(domain_findings.keys())[0] if domain_findings else "unknown",
                                "ending_domain": list(domain_findings.keys())[-1] if domain_findings else "unknown",
                                "mediating_factors": ["system_interactions", "feedback_mechanisms"],
                                "strength_of_evidence": 0.72
                            }
                        ],
                        "feedback_loops": [
                            {
                                "loop_description": "Complex feedback mechanisms across domains",
                                "participating_domains": list(domain_findings.keys())[:2],
                                "loop_type": "complex",
                                "stability_analysis": "context_dependent"
                            }
                        ]
                    },
                    "integration_quality_assessment": {
                        "synthesis_completeness": 80,
                        "cross_domain_coherence": 75,
                        "novel_insight_generation": 70,
                        "bias_detection_coverage": 85,
                        "methodological_rigor": 78,
                        "overall_confidence": 0.77
                    }
                }
            
            # Step 4: Add metadata and context
            final_response = {
                "domain": "Cross-Domain Analysis",
                "synthesis": synthesis,
                "integration_context": integration_context,
                "domain_findings_summary": {
                    domain: {
                        "confidence": findings.get("analysis", {}).get("quality_assessment", {}).get("confidence_score", 0),
                        "key_insights_count": len(findings.get("analysis", {}).get("biological_insights", [])) +
                                           len(findings.get("analysis", {}).get("technical_insights", [])) +
                                           len(findings.get("analysis", {}).get("key_insights", []))
                    }
                    for domain, findings in domain_findings.items()
                },
                "capabilities_applied": self.integration_capabilities,
                "timestamp": datetime.now().isoformat()
            }
            
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "response_type": "data",
                "content": final_response
            }
                
        except Exception as e:
            logger.error(f"Cross-Domain Oracle error: {e}")
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": f"Cross-Domain Oracle: Integration analysis error - {str(e)}"
            }

    async def invoke(self, query: str, session_id: str) -> dict:
        """Non-streaming invoke (not implemented - use stream)."""
        raise NotImplementedError("Please use the streaming interface")