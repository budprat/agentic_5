# ABOUTME: Master oracle agent that coordinates multiple specialized agents
# ABOUTME: Demonstrates A2A patterns for agent orchestration and quality control

"""
Master Oracle Agent

This agent serves as a coordinator for multiple specialized agents,
demonstrating key A2A (Agent-to-Agent) communication patterns.

Key patterns demonstrated:
1. Agent inheritance from StandardizedAgentBase
2. Quality framework integration with "business" domain
3. Coordinating multiple agents via message passing
4. Hierarchical decision making
5. Result aggregation and synthesis
"""

import asyncio
from typing import Dict, Any, List, Optional, AsyncIterable
from dataclasses import dataclass, field

from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.common.a2a_protocol import A2AProtocolClient
from a2a_mcp.common.quality_framework import QualityThresholdFramework
import logging


@dataclass
class OracleContext:
    """Context for master oracle operations"""
    subordinate_agents: List[str] = field(default_factory=list)
    pending_tasks: Dict[str, Any] = field(default_factory=dict)
    aggregated_results: Dict[str, Any] = field(default_factory=dict)
    decision_criteria: Dict[str, float] = field(default_factory=dict)


class MasterOracleAgent(StandardizedAgentBase):
    """
    Master Oracle Agent that coordinates multiple specialized agents.
    
    This agent demonstrates:
    - Hierarchical agent coordination
    - Quality-aware decision making
    - Result aggregation from multiple sources
    - Business domain quality standards
    """
    
    def __init__(self, agent_id: str = "master_oracle"):
        # Define oracle-specific instructions
        instructions = """
        You are a Master Oracle agent that coordinates and synthesizes insights from multiple specialized agents.
        Your role is to:
        1. Delegate complex requests to appropriate specialist agents
        2. Aggregate and synthesize responses from multiple sources
        3. Apply quality validation to ensure high-quality outputs
        4. Make hierarchical decisions based on weighted consensus
        
        Maintain a professional, analytical tone and provide comprehensive insights.
        """
        
        super().__init__(
            agent_name=agent_id,
            description="Master Oracle - Coordinates multiple specialized agents for comprehensive analysis",
            instructions=instructions,
            quality_config={
                "min_confidence_score": 0.75,
                "require_sources": True,
                "max_response_length": 5000
            }
        )
        
        # Oracle-specific context
        self.context = OracleContext()
        
        # Register specialized agent IDs that this oracle coordinates
        self.context.subordinate_agents = [
            "data_analyst_agent",
            "risk_assessor_agent", 
            "market_predictor_agent"
        ]
        
        # Decision thresholds for quality control
        self.context.decision_criteria = {
            "confidence_threshold": 0.75,
            "consensus_threshold": 0.66,  # 2/3 agents must agree
            "quality_min_score": 0.8
        }
    
    async def _execute_agent_logic(
        self, query: str, context_id: str, task_id: str
    ) -> AsyncIterable[Dict[str, Any]]:
        """
        Process incoming messages and coordinate responses.
        
        Demonstrates:
        - Message type handling
        - Quality validation
        - Multi-agent coordination
        """
        # Parse the query to determine operation type
        operation = self._determine_operation(query)
        
        # Yield initial processing message
        yield {
            "is_task_complete": False,
            "require_user_input": False,
            "content": f"Analyzing request and coordinating specialized agents..."
        }
        
        # Process based on operation type
        if operation == "comprehensive_analysis":
            async for result in self._perform_comprehensive_analysis(query, context_id):
                yield result
        elif operation == "risk_assessment":
            async for result in self._perform_risk_assessment(query, context_id):
                yield result
        elif operation == "status_check":
            async for result in self._check_analysis_status(query, context_id):
                yield result
        else:
            # Default to comprehensive analysis
            async for result in self._perform_comprehensive_analysis(query, context_id):
                yield result
    
    def _determine_operation(self, query: str) -> str:
        """Determine the type of operation based on query content."""
        query_lower = query.lower()
        if "risk" in query_lower:
            return "risk_assessment"
        elif "status" in query_lower or "check" in query_lower:
            return "status_check"
        else:
            return "comprehensive_analysis"
    
    async def _perform_comprehensive_analysis(self, query: str, context_id: str) -> AsyncIterable[Dict[str, Any]]:
        """
        Perform comprehensive analysis by coordinating multiple agents.
        """
        request_id = f"analysis_{context_id}_{asyncio.get_event_loop().time()}"
        
        # Store request context
        self.context.pending_tasks[request_id] = {
            "query": query,
            "analysis_type": "comprehensive",
            "responses_received": {},
            "started_at": asyncio.get_event_loop().time()
        }
        
        # Yield status update
        yield {
            "is_task_complete": False,
            "require_user_input": False,
            "content": f"Delegating analysis to {len(self.context.subordinate_agents)} specialized agents..."
        }
        
        # In a real implementation, we would use A2A protocol to communicate with other agents
        # For this example, we'll simulate responses
        await asyncio.sleep(1)  # Simulate network delay
        
        # Simulate receiving responses from agents
        simulated_responses = {
            "data_analyst_agent": {
                "analysis": "Data trends show positive growth indicators",
                "confidence": 0.85,
                "key_metrics": {"growth_rate": 0.12, "volatility": 0.23}
            },
            "risk_assessor_agent": {
                "risk_score": 0.65,
                "risk_factors": ["market volatility", "regulatory changes"],
                "confidence": 0.78
            },
            "market_predictor_agent": {
                "prediction": "Bullish trend expected",
                "probability": 0.72,
                "timeframe": "3-6 months"
            }
        }
        
        # Process responses
        for agent_id, response_data in simulated_responses.items():
            self.context.pending_tasks[request_id]["responses_received"][agent_id] = {
                "payload": response_data,
                "quality_score": response_data.get("confidence", 0.75),
                "timestamp": asyncio.get_event_loop().time()
            }
        
        # Synthesize final response
        synthesis = self._synthesize_responses(self.context.pending_tasks[request_id])
        
        # Clean up
        del self.context.pending_tasks[request_id]
        
        # Yield final result
        yield {
            "is_task_complete": True,
            "require_user_input": False,
            "content": synthesis
        }
    
    async def _perform_risk_assessment(self, query: str, context_id: str) -> AsyncIterable[Dict[str, Any]]:
        """
        Perform focused risk assessment using risk assessor agent.
        """
        yield {
            "is_task_complete": False,
            "require_user_input": False,
            "content": "Initiating risk-focused analysis..."
        }
        
        # Simulate risk assessment (in real implementation, use A2A protocol)
        await asyncio.sleep(0.5)
        
        risk_assessment = {
            "overall_risk": "MODERATE",
            "risk_score": 0.65,
            "key_risks": [
                {"factor": "Market Volatility", "impact": "HIGH", "probability": "MEDIUM"},
                {"factor": "Regulatory Changes", "impact": "MEDIUM", "probability": "LOW"},
                {"factor": "Competition", "impact": "MEDIUM", "probability": "HIGH"}
            ],
            "mitigation_strategies": [
                "Diversify portfolio to reduce market exposure",
                "Monitor regulatory developments closely",
                "Strengthen competitive positioning"
            ],
            "confidence": 0.82
        }
        
        yield {
            "is_task_complete": True,
            "require_user_input": False,
            "content": risk_assessment
        }
    
    async def _check_analysis_status(self, query: str, context_id: str) -> AsyncIterable[Dict[str, Any]]:
        """Check status of ongoing analyses."""
        if not self.context.pending_tasks:
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": {
                    "status": "No ongoing analyses",
                    "pending_tasks": 0
                }
            }
        else:
            status_info = {
                "pending_tasks": len(self.context.pending_tasks),
                "tasks": []
            }
            
            for task_id, task_context in self.context.pending_tasks.items():
                elapsed = asyncio.get_event_loop().time() - task_context["started_at"]
                status_info["tasks"].append({
                    "task_id": task_id,
                    "type": task_context["analysis_type"],
                    "responses_received": len(task_context["responses_received"]),
                    "elapsed_seconds": round(elapsed, 2)
                })
            
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": status_info
            }
    
    def _synthesize_responses(self, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize responses from multiple agents into a comprehensive analysis.
        """
        responses = task_context["responses_received"]
        
        # Calculate weighted consensus
        total_weight = 0
        weighted_results = {}
        insights = []
        
        for agent_id, response_data in responses.items():
            weight = response_data["quality_score"]
            if weight >= self.context.decision_criteria["quality_min_score"]:
                total_weight += weight
                
                # Extract key insights from each agent
                payload = response_data["payload"]
                if agent_id == "data_analyst_agent":
                    insights.append(f"**Data Analysis**: {payload.get('analysis', 'No analysis provided')}")
                    for key, value in payload.get('key_metrics', {}).items():
                        if key not in weighted_results:
                            weighted_results[key] = 0
                        weighted_results[key] += value * weight
                elif agent_id == "risk_assessor_agent":
                    insights.append(f"**Risk Assessment**: Risk score {payload.get('risk_score', 0):.2f} - Key factors: {', '.join(payload.get('risk_factors', []))}")
                elif agent_id == "market_predictor_agent":
                    insights.append(f"**Market Prediction**: {payload.get('prediction', 'No prediction')} (Probability: {payload.get('probability', 0):.0%})")
        
        # Normalize weighted results
        if total_weight > 0:
            for key in weighted_results:
                weighted_results[key] /= total_weight
        
        # Build comprehensive synthesis
        return {
            "synthesis_type": "Master Oracle Analysis",
            "executive_summary": f"Based on analysis from {len(responses)} specialized agents with an average confidence of {self._calculate_confidence(responses):.0%}:",
            "key_insights": insights,
            "aggregated_metrics": weighted_results,
            "contributing_agents": list(responses.keys()),
            "confidence_score": self._calculate_confidence(responses),
            "quality_metrics": {
                "average_quality": sum(r["quality_score"] for r in responses.values()) / len(responses) if responses else 0,
                "total_agents_consulted": len(responses)
            },
            "timestamp": asyncio.get_event_loop().time()
        }
    
    async def _communicate_with_agent(self, agent_id: str, message: str, metadata: Dict[str, Any] = None):
        """
        Communicate with another agent using A2A protocol.
        
        This uses the standardized A2A communication from the base class.
        """
        # Map agent IDs to ports (in production, this would be configured)
        agent_ports = {
            "data_analyst_agent": 10910,
            "risk_assessor_agent": 10911,
            "market_predictor_agent": 10912
        }
        
        if agent_id in agent_ports:
            try:
                response = await self.communicate_with_agent(
                    agent_ports[agent_id],
                    message,
                    metadata or {}
                )
                return response
            except Exception as e:
                logging.error(f"Failed to communicate with {agent_id}: {e}")
                return None
        else:
            logging.warning(f"Unknown agent ID: {agent_id}")
            return None
    
    def get_agent_temperature(self) -> float:
        """Use lower temperature for oracle coordination."""
        return 0.3
    
    def get_response_mime_type(self) -> str:
        """Return structured JSON responses."""
        return "application/json"
    
    
    def _calculate_confidence(self, responses: Dict[str, Any]) -> float:
        """
        Calculate confidence score based on response quality and agreement.
        
        This is a simplified example - real implementation would be more sophisticated.
        """
        if not responses:
            return 0.0
        
        # Average quality score
        quality_scores = [r["quality_score"] for r in responses.values()]
        avg_quality = sum(quality_scores) / len(quality_scores)
        
        # Agreement factor (simplified - checks if responses are similar)
        # In reality, this would compare actual values
        agreement_factor = 1.0 if len(responses) >= 2 else 0.5
        
        # Combined confidence
        confidence = avg_quality * agreement_factor
        
        return min(confidence, 1.0)
    


# Example usage:
# This agent would be deployed as part of a larger system where it coordinates
# multiple specialized agents to provide comprehensive analysis and insights.
# 
# Example queries it can handle:
# - "Provide a comprehensive analysis of the current market situation"
# - "Assess the risk factors for this investment opportunity"
# - "Check the status of ongoing analyses"
#
# The agent uses the StandardizedAgentBase framework to ensure consistent
# behavior, quality validation, and integration with MCP tools when needed.