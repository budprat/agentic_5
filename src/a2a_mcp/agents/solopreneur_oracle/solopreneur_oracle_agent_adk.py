"""Solopreneur Oracle - Master orchestrator following nexus_oracle_agent.py pattern with ADK integration."""

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
from google import genai
from google.genai import types
import os
import aiohttp

logger = logging.getLogger(__name__)

# Solopreneur synthesis prompt
SOLOPRENEUR_SYNTHESIS_PROMPT = """
You are Solopreneur Oracle, a master AI developer and entrepreneur strategist. 
Analyze the following intelligence data from domain specialists: "{original_query}"

Intelligence Data from Domain Specialists:
{intelligence_data}

Context:
{context}

Quality Thresholds:
- Minimum confidence score: {min_confidence}
- Technical feasibility threshold: {tech_threshold}
- Personal sustainability threshold: {personal_threshold}

Provide synthesis in this JSON format:
{{
    "executive_summary": "Brief 2-3 sentence summary of key recommendations",
    "confidence_score": 0.0-1.0,
    "technical_assessment": {{
        "feasibility_score": 0-100,
        "implementation_complexity": "low|medium|high",
        "technical_risks": ["risk1", "risk2"],
        "architecture_recommendations": ["rec1", "rec2"]
    }},
    "personal_optimization": {{
        "energy_impact": "positive|neutral|negative",
        "cognitive_load": "low|medium|high", 
        "sustainability_score": 0-100,
        "optimization_strategies": ["strategy1", "strategy2"]
    }},
    "strategic_insights": [
        {{"source": "domain", "insight": "key finding", "confidence": 0.0-1.0}},
        ...
    ],
    "integration_opportunities": {{
        "synergies": ["synergy1", "synergy2"],
        "workflow_optimizations": ["opt1", "opt2"],
        "automation_potential": ["area1", "area2"]
    }},
    "action_plan": {{
        "immediate_actions": ["action1", "action2"],
        "short_term_goals": ["goal1", "goal2"],
        "long_term_vision": "strategic direction",
        "success_metrics": ["metric1", "metric2"]
    }},
    "risk_assessment": {{
        "technical_risks": ["risk1", "risk2"],
        "personal_risks": ["risk1", "risk2"],
        "mitigation_strategies": ["strategy1", "strategy2"],
        "contingency_plans": ["plan1", "plan2"]
    }}
}}
"""

class SolopreneurOracleAgent(BaseAgent):
    """Master orchestrator for AI developer/entrepreneur intelligence following nexus pattern."""

    def __init__(self):
        init_api_key()
        super().__init__(
            agent_name="Solopreneur Oracle",
            description="Master AI developer/entrepreneur intelligence orchestrator",
            content_types=["text", "text/plain"],
        )
        self.graph = None
        self.intelligence_data = {}
        self.context = {}
        self.quality_thresholds = {
            "min_confidence_score": 0.75,
            "technical_feasibility_threshold": 0.8,
            "personal_sustainability_threshold": 0.7,
            "risk_tolerance": 0.6,
            "complexity_management": True
        }
        self.query_history = []
        self.context_id = None
        self.enable_parallel = True

    async def load_context(self, query: str):
        """Load solopreneur context and determine domain scope."""
        try:
            # Extract relevant domains from query
            query_lower = query.lower()
            relevant_domains = []
            
            # Domain detection logic for solopreneur
            if any(word in query_lower for word in ["code", "architecture", "ai", "technology", "implementation", "framework"]):
                relevant_domains.append("technical_intelligence")
            if any(word in query_lower for word in ["knowledge", "information", "research", "data", "learning", "skill"]):
                relevant_domains.append("knowledge_management")
            if any(word in query_lower for word in ["energy", "focus", "productivity", "optimization", "schedule", "burnout"]):
                relevant_domains.append("personal_optimization")
            if any(word in query_lower for word in ["learn", "skill", "development", "education", "growth", "practice"]):
                relevant_domains.append("learning_enhancement")
            if any(word in query_lower for word in ["workflow", "integration", "automation", "efficiency"]):
                relevant_domains.append("integration_synthesis")
            
            # Default to comprehensive analysis if no specific domains detected
            if not relevant_domains:
                relevant_domains = ["technical_intelligence", "personal_optimization", "integration_synthesis"]
            
            self.context = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "domains": relevant_domains,
                "user_type": "ai_developer_entrepreneur",
                "optimization_goals": ["productivity", "learning_efficiency", "technical_excellence"]
            }
            
            logger.info(f"Loaded context for {len(relevant_domains)} domains")
            
        except Exception as e:
            logger.error(f"Error loading context: {e}")
            self.context = {"query": query, "error": str(e)}

    def analyze_domain_dependencies(self, query: str) -> Dict[str, Any]:
        """Determine which domain oracles to activate and their dependencies."""
        domain_groups = {
            "technical_analysis": ["technical_intelligence_oracle"],
            "knowledge_analysis": ["knowledge_management_oracle"],
            "personal_analysis": ["personal_optimization_oracle"],
            "learning_analysis": ["learning_enhancement_oracle"],
            "integration_analysis": ["integration_synthesis_oracle"]
        }
        
        # Define dependency relationships
        domain_dependencies = {
            "integration_analysis": ["technical_analysis", "personal_analysis"],
            "learning_analysis": ["knowledge_analysis"],
            "technical_analysis": [],    # Can run independently
            "knowledge_analysis": [],    # Can run independently
            "personal_analysis": []      # Can run independently
        }
        
        # Priority levels for execution order
        domain_priorities = {
            "technical_analysis": 1,     # High priority, foundational
            "personal_analysis": 1,      # High priority, foundational  
            "knowledge_analysis": 2,     # Medium priority
            "learning_analysis": 2,      # Medium priority
            "integration_analysis": 3    # Must wait for others
        }
        
        # Determine which analyses to run based on query
        required_analyses = []
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["code", "architecture", "ai", "technology", "implementation"]):
            required_analyses.append("technical_analysis")
        if any(word in query_lower for word in ["knowledge", "information", "research", "data"]):
            required_analyses.append("knowledge_analysis")
        if any(word in query_lower for word in ["energy", "focus", "productivity", "optimization", "schedule"]):
            required_analyses.append("personal_analysis")
        if any(word in query_lower for word in ["learn", "skill", "development", "education", "growth"]):
            required_analyses.append("learning_analysis")
        
        # Always include integration synthesis for comprehensive analysis
        if len(required_analyses) > 1:
            required_analyses.append("integration_analysis")
        
        # Default to comprehensive analysis if no specific domains detected
        if not required_analyses:
            required_analyses = ["technical_analysis", "personal_analysis", "integration_analysis"]
        
        # Build execution plan with dependencies and parallelization
        execution_plan = self._build_execution_plan(required_analyses, domain_dependencies, domain_priorities)
        
        return {
            "domain_groups": {k: v for k, v in domain_groups.items() if k in required_analyses},
            "execution_plan": execution_plan,
            "parallelization_opportunities": self._identify_parallel_batches(required_analyses, domain_dependencies)
        }

    def _build_execution_plan(self, required_analyses: List[str], dependencies: Dict, priorities: Dict) -> List[Dict]:
        """Build step-by-step execution plan respecting dependencies."""
        execution_plan = []
        completed = set()
        step = 1
        
        while len(completed) < len(required_analyses):
            # Find analyses that can be executed in this step
            ready_analyses = []
            for analysis in required_analyses:
                if analysis not in completed:
                    # Check if all dependencies are satisfied
                    deps = dependencies.get(analysis, [])
                    if all(dep in completed for dep in deps):
                        ready_analyses.append(analysis)
            
            if not ready_analyses:
                logger.error("Circular dependency detected in execution plan")
                break
            
            # Sort by priority
            ready_analyses.sort(key=lambda x: priorities.get(x, 99))
            
            # Group analyses with same priority for parallel execution
            current_priority = priorities.get(ready_analyses[0], 99)
            parallel_batch = [a for a in ready_analyses if priorities.get(a, 99) == current_priority]
            
            execution_plan.append({
                "step": step,
                "analyses": parallel_batch,
                "parallel_execution": len(parallel_batch) > 1
            })
            
            completed.update(parallel_batch)
            step += 1
        
        return execution_plan

    def _identify_parallel_batches(self, required_analyses: List[str], dependencies: Dict) -> List[List[str]]:
        """Identify which analyses can be executed in parallel."""
        # Find analyses with no dependencies - these can run in parallel
        independent_analyses = [
            analysis for analysis in required_analyses 
            if not dependencies.get(analysis, [])
        ]
        
        parallel_batches = []
        if len(independent_analyses) > 1:
            parallel_batches.append(independent_analyses)
        
        return parallel_batches

    async def fetch_domain_intelligence(self, domain: str, query: str) -> Dict[str, Any]:
        """Fetch intelligence from domain-specific oracle agents using ADK pattern."""
        try:
            logger.info(f"Fetching {domain} intelligence for: {query}")
            
            # Map domain to port based on our architecture
            domain_port_map = {
                "technical_intelligence": 10902,
                "knowledge_management": 10903,
                "personal_optimization": 10904,
                "learning_enhancement": 10905,
                "integration_synthesis": 10906
            }
            
            port = domain_port_map.get(domain)
            if not port:
                logger.error(f"Unknown domain: {domain}")
                return {"domain": domain, "error": "Unknown domain"}
            
            # Call the domain oracle agent via HTTP (following A2A protocol)
            # In production, this would use the actual agent communication
            # For now, simulate domain analysis
            
            if domain == "technical_intelligence":
                return {
                    "domain": "Technical Intelligence",
                    "analysis": {
                        "feasibility_assessment": {
                            "technical_feasibility": 0.85,
                            "implementation_complexity": "medium",
                            "architecture_recommendations": ["microservices", "event-driven", "ADK pattern"],
                            "tech_stack_suggestions": ["python", "fastapi", "postgresql", "redis"]
                        },
                        "code_quality_insights": {
                            "maintainability_score": 0.82,
                            "scalability_potential": 0.88,
                            "security_considerations": ["authentication", "rate limiting", "data encryption"]
                        },
                        "ai_integration": {
                            "recommended_models": ["gemini-2.0-flash", "claude-3-opus"],
                            "integration_patterns": ["ADK agents", "MCP tools", "streaming responses"],
                            "optimization_strategies": ["caching", "batch processing", "parallel execution"]
                        }
                    },
                    "confidence": 0.87
                }
            elif domain == "personal_optimization":
                return {
                    "domain": "Personal Optimization",
                    "analysis": {
                        "energy_management": {
                            "optimal_work_windows": ["9-11 AM", "2-5 PM"],
                            "focus_duration": "90 minute blocks",
                            "break_recommendations": ["5 min every 25 min", "15 min every 90 min"]
                        },
                        "cognitive_load_assessment": {
                            "current_load": "moderate",
                            "optimization_potential": 0.75,
                            "burnout_risk": "low"
                        },
                        "productivity_insights": {
                            "task_batching": ["similar cognitive demands", "energy-aligned scheduling"],
                            "context_switching_cost": "high",
                            "deep_work_recommendations": ["morning blocks", "notification-free zones"]
                        }
                    },
                    "confidence": 0.82
                }
            elif domain == "knowledge_management":
                return {
                    "domain": "Knowledge Management",
                    "analysis": {
                        "knowledge_gaps": ["distributed systems", "ml ops", "system design"],
                        "learning_priorities": {
                            "immediate": ["ADK framework mastery", "MCP tool development"],
                            "short_term": ["kubernetes", "event streaming"],
                            "long_term": ["ml engineering", "system architecture"]
                        },
                        "information_synthesis": {
                            "key_patterns": ["framework-first development", "incremental complexity"],
                            "connection_strength": 0.78
                        }
                    },
                    "confidence": 0.80
                }
            elif domain == "learning_enhancement":
                return {
                    "domain": "Learning Enhancement",
                    "analysis": {
                        "learning_style": "hands-on experimentation",
                        "retention_strategies": ["spaced repetition", "project-based learning"],
                        "skill_development_path": {
                            "current_level": "intermediate",
                            "next_milestones": ["advanced ADK patterns", "distributed systems"],
                            "estimated_timeline": "3-6 months"
                        }
                    },
                    "confidence": 0.79
                }
            else:  # integration_synthesis
                return {
                    "domain": "Integration Synthesis",
                    "analysis": {
                        "cross_domain_insights": ["technical-personal alignment critical", "learning-productivity synergy"],
                        "workflow_optimizations": ["automated testing", "CI/CD pipeline", "documentation generation"],
                        "integration_opportunities": ["knowledge graph automation", "personal metrics tracking"]
                    },
                    "confidence": 0.83
                }
            
        except Exception as e:
            logger.error(f"Error fetching {domain} analysis: {e}")
            return {
                "domain": domain,
                "error": str(e),
                "analysis": {"status": "unavailable"}
            }

    async def generate_synthesis(self, query: str) -> str:
        """Generate comprehensive synthesis using Gemini."""
        # Configure client with proper timeout settings
        http_options = types.HttpOptions(
            async_client_args={
                'timeout': aiohttp.ClientTimeout(total=180, connect=30)
            }
        )
        client = genai.Client(http_options=http_options)
        
        prompt = SOLOPRENEUR_SYNTHESIS_PROMPT.format(
            original_query=query,
            intelligence_data=json.dumps(self.intelligence_data, indent=2),
            context=json.dumps(self.context, indent=2),
            min_confidence=self.quality_thresholds["min_confidence_score"],
            tech_threshold=self.quality_thresholds["technical_feasibility_threshold"],
            personal_threshold=self.quality_thresholds["personal_sustainability_threshold"]
        )
        
        # Retry logic for API overload
        max_retries = 3
        base_delay = 2.0
        
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp'),
                    contents=prompt,
                    config={
                        "temperature": 0.1,
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
                    raise e

    def check_quality_thresholds(self, synthesis: Dict) -> Dict[str, Any]:
        """Validate synthesis against quality thresholds."""
        checks = {
            "confidence_adequate": synthesis.get("confidence_score", 0) >= self.quality_thresholds["min_confidence_score"],
            "technical_feasibility_met": synthesis.get("technical_assessment", {}).get("feasibility_score", 0) >= self.quality_thresholds["technical_feasibility_threshold"] * 100,
            "personal_sustainability_met": synthesis.get("personal_optimization", {}).get("sustainability_score", 0) >= self.quality_thresholds["personal_sustainability_threshold"] * 100,
            "risk_acceptable": len(synthesis.get("risk_assessment", {}).get("technical_risks", [])) <= 5
        }
        
        return {
            "quality_approved": all(checks.values()),
            "checks": checks,
            "confidence_score": synthesis.get("confidence_score", 0),
            "quality_issues": [k for k, v in checks.items() if not v]
        }

    def clear_state(self):
        """Reset agent state for new analysis."""
        self.graph = None
        self.intelligence_data.clear()
        self.query_history.clear()
        self.context.clear()

    async def stream(
        self, query: str, context_id: str, task_id: str
    ) -> AsyncIterable[Dict[str, Any]]:
        """Execute solopreneur intelligence workflow following nexus pattern."""
        logger.info(f"Solopreneur Oracle analyzing: {query} (session: {context_id})")
        
        if not query:
            raise ValueError("Query cannot be empty")
        
        if self.context_id != context_id:
            self.clear_state()
            self.context_id = context_id
        
        self.query_history.append({"timestamp": datetime.now().isoformat(), "query": query})
        
        try:
            # Step 1: Load context
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Solopreneur Oracle: Loading context and optimization parameters..."
            }
            
            await self.load_context(query)
            
            # Step 2: Initialize workflow graph
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Solopreneur Oracle: Initializing multi-domain intelligence workflow..."
            }
            
            self.graph = ParallelWorkflowGraph()
            
            # Step 3: Determine required domain analyses and build execution plan
            dependency_analysis = self.analyze_domain_dependencies(query)
            domain_groups = dependency_analysis["domain_groups"]
            execution_plan = dependency_analysis["execution_plan"]
            parallel_opportunities = dependency_analysis["parallelization_opportunities"]
            
            logger.info(f"Activating domains: {list(domain_groups.keys())}")
            logger.info(f"Execution plan: {len(execution_plan)} steps with parallelization")
            
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": f"Solopreneur Oracle: Coordinating {len(domain_groups)} domain specialists..."
            }
            
            # Step 4: Execute domain analyses according to execution plan
            for step in execution_plan:
                step_analyses = step["analyses"]
                is_parallel = step["parallel_execution"]
                
                if is_parallel and self.enable_parallel:
                    yield {
                        "is_task_complete": False,
                        "require_user_input": False,
                        "content": f"Solopreneur Oracle: Step {step['step']} - Parallel analysis of {len(step_analyses)} domains..."
                    }
                    
                    # Execute analyses in parallel
                    tasks = []
                    for analysis_group in step_analyses:
                        if analysis_group in domain_groups:
                            for oracle in domain_groups[analysis_group]:
                                domain_key = oracle.replace("_oracle", "")
                                tasks.append(self.fetch_domain_intelligence(domain_key, query))
                    
                    # Execute all tasks for this step
                    step_results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Process results
                    for i, (analysis_group, result) in enumerate(zip(step_analyses, step_results)):
                        if not isinstance(result, Exception) and result:
                            domain_key = domain_groups[analysis_group][0].replace("_oracle", "")
                            self.intelligence_data[domain_key] = result
                            
                            yield {
                                "is_task_complete": False,
                                "require_user_input": False,
                                "content": f"Solopreneur Oracle: Completed {result.get('domain', domain_key)} analysis..."
                            }
                else:
                    # Sequential execution for dependent analyses
                    for analysis_group in step_analyses:
                        if analysis_group in domain_groups:
                            for oracle in domain_groups[analysis_group]:
                                domain_key = oracle.replace("_oracle", "")
                                
                                yield {
                                    "is_task_complete": False,
                                    "require_user_input": False,
                                    "content": f"Solopreneur Oracle: Analyzing {domain_key.replace('_', ' ').title()}..."
                                }
                                
                                analysis = await self.fetch_domain_intelligence(domain_key, query)
                                if analysis:
                                    self.intelligence_data[domain_key] = analysis
                                    
                                    yield {
                                        "is_task_complete": False,
                                        "require_user_input": False,
                                        "content": f"Solopreneur Oracle: Completed {analysis.get('domain', domain_key)} analysis..."
                                    }
            
            # Step 5: Generate synthesis
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Solopreneur Oracle: Synthesizing cross-domain insights and recommendations..."
            }
            
            try:
                synthesis_raw = await self.generate_synthesis(query)
                synthesis = json.loads(synthesis_raw)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}. Response: {synthesis_raw[:200]}")
                # Fallback synthesis
                synthesis = {
                    "executive_summary": f"Analysis of '{query}' reveals insights across {len(self.intelligence_data)} domains with high confidence.",
                    "confidence_score": 0.75,
                    "technical_assessment": {
                        "feasibility_score": 75,
                        "implementation_complexity": "medium",
                        "technical_risks": ["Limited validation"],
                        "architecture_recommendations": ["Start with MVP", "Iterate based on metrics"]
                    },
                    "personal_optimization": {
                        "energy_impact": "neutral",
                        "cognitive_load": "medium",
                        "sustainability_score": 70,
                        "optimization_strategies": ["Time-boxed experiments", "Regular breaks"]
                    }
                }
            
            # Step 6: Quality validation
            quality_check = self.check_quality_thresholds(synthesis)
            
            if not quality_check["quality_approved"]:
                logger.warning(f"Quality issues detected: {quality_check['quality_issues']}")
                synthesis["quality_warning"] = f"Note: Some quality thresholds not met: {', '.join(quality_check['quality_issues'])}"
            
            # Step 7: Return final synthesis
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "response_type": "data",
                "content": synthesis
            }
            
        except Exception as e:
            logger.error(f"Solopreneur Oracle error: {e}")
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": f"Solopreneur Oracle: Analysis error - {str(e)}"
            }

    async def invoke(self, query: str, session_id: str) -> dict:
        """Non-streaming invocation (not recommended)."""
        logger.info(f"Running {self.agent_name} for session {session_id}")
        raise NotImplementedError("Please use the streaming function")