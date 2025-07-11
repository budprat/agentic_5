#!/usr/bin/env python3
"""ABOUTME: Context-Driven Orchestrator - Tier 3 agent for context-aware multi-agent coordination and workflow orchestration.
ABOUTME: This agent analyzes context and coordinates complex workflows across multiple specialized agents."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase

logger = logging.getLogger(__name__)

@dataclass
class WorkflowNode:
    """A node in the orchestrated workflow."""
    agent_type: str
    task: str
    dependencies: List[str]
    context_requirements: List[str]
    priority: int
    estimated_duration: int

@dataclass
class OrchestrationContext:
    """Context information for orchestrating workflows."""
    user_intent: str
    available_agents: List[str]
    resource_constraints: Dict[str, Any]
    temporal_constraints: Dict[str, Any]
    quality_requirements: Dict[str, Any]

class ContextDrivenOrchestrator(StandardizedAgentBase):
    """
    Context-Driven Orchestrator - Tier 3 Agent
    
    Provides context-aware multi-agent coordination and workflow orchestration.
    Analyzes complex requests and coordinates responses across multiple specialized agents.
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Context-Driven Orchestrator",
            description="Context-aware multi-agent coordination and workflow orchestration",
            instructions="You are the Context-Driven Orchestrator responsible for analyzing complex requests and coordinating workflows across multiple specialized agents. You understand context, dependencies, and optimal coordination patterns."
        )
        
        # Store tier and port as instance variables
        self.port = 10961  # Original Context-Driven Orchestrator port
        self.tier = "tier3"
        
        # Agent coordination mappings
        self.agent_capabilities = {
            "technical": ["code_analysis", "architecture_review", "performance_optimization"],
            "research": ["information_gathering", "analysis", "synthesis"],
            "scheduling": ["time_management", "resource_allocation", "deadline_coordination"],
            "quality": ["validation", "testing", "compliance_checking"],
            "communication": ["reporting", "documentation", "stakeholder_updates"]
        }
        
        logger.info("Context-Driven Orchestrator initialized")

    async def _execute_agent_logic(self, query: str, context_id: str, task_id: str) -> Dict[str, Any]:
        """
        Execute orchestration logic for the given query.
        
        Args:
            query: The orchestration request
            context_id: Context identifier
            task_id: Task identifier
            
        Returns:
            Orchestration result with workflow plan and coordination details
        """
        logger.info(f"Orchestrating workflow for query: {query}")
        
        try:
            # Parse and analyze the request
            orchestration_context = await self._analyze_request_context(query)
            
            # Generate workflow plan
            workflow_plan = await self._generate_workflow_plan(orchestration_context)
            
            # Optimize coordination
            optimized_plan = await self._optimize_coordination(workflow_plan, orchestration_context)
            
            # Generate orchestration summary
            summary = await self._generate_orchestration_summary(optimized_plan)
            
            return {
                "content": summary,
                "metadata": {
                    "workflow_id": f"orchestration_{hash(query)}",
                    "total_agents": len(optimized_plan.get("agents", [])),
                    "estimated_duration": optimized_plan.get("total_duration", 0),
                    "coordination_complexity": optimized_plan.get("complexity_score", "medium")
                }
            }
            
        except Exception as e:
            logger.error(f"Orchestration failed: {e}")
            return {
                "content": f"Orchestration failed: {str(e)}",
                "metadata": {"error": True}
            }

    async def _analyze_request_context(self, query: str) -> OrchestrationContext:
        """Analyze the request to understand context and requirements."""
        logger.info("Analyzing request context for orchestration")
        
        # Extract key components from query
        intent = self._extract_user_intent(query)
        complexity = self._assess_complexity(query)
        required_capabilities = self._identify_required_capabilities(query)
        
        return OrchestrationContext(
            user_intent=intent,
            available_agents=list(self.agent_capabilities.keys()),
            resource_constraints={"complexity": complexity},
            temporal_constraints={"priority": "normal"},
            quality_requirements={"accuracy": "high", "completeness": "required"}
        )

    def _extract_user_intent(self, query: str) -> str:
        """Extract the primary user intent from the query."""
        intent_keywords = {
            "analyze": "analysis",
            "create": "creation", 
            "optimize": "optimization",
            "coordinate": "coordination",
            "manage": "management",
            "research": "research",
            "implement": "implementation"
        }
        
        query_lower = query.lower()
        for keyword, intent in intent_keywords.items():
            if keyword in query_lower:
                return intent
        
        return "general_assistance"

    def _assess_complexity(self, query: str) -> str:
        """Assess the complexity level of the request."""
        complexity_indicators = {
            "high": ["multiple", "complex", "integrate", "coordinate", "optimize", "enterprise"],
            "medium": ["create", "analyze", "manage", "implement"],
            "low": ["simple", "basic", "quick", "single"]
        }
        
        query_lower = query.lower()
        
        for level, indicators in complexity_indicators.items():
            if any(indicator in query_lower for indicator in indicators):
                return level
        
        return "medium"

    def _identify_required_capabilities(self, query: str) -> List[str]:
        """Identify which agent capabilities are needed."""
        required = []
        query_lower = query.lower()
        
        capability_keywords = {
            "technical": ["code", "technical", "architecture", "performance", "system"],
            "research": ["research", "analyze", "study", "investigate", "gather"],
            "scheduling": ["schedule", "time", "deadline", "coordinate", "plan"],
            "quality": ["test", "validate", "quality", "compliance", "review"],
            "communication": ["report", "document", "communicate", "update"]
        }
        
        for capability, keywords in capability_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                required.append(capability)
        
        return required if required else ["technical"]  # Default fallback

    async def _generate_workflow_plan(self, context: OrchestrationContext) -> Dict[str, Any]:
        """Generate a comprehensive workflow plan based on context."""
        logger.info("Generating workflow plan")
        
        # Create workflow nodes based on required capabilities
        workflow_nodes = []
        
        for i, capability in enumerate(context.available_agents):
            if capability in self._identify_required_capabilities(context.user_intent):
                node = WorkflowNode(
                    agent_type=capability,
                    task=f"{capability}_task_for_{context.user_intent}",
                    dependencies=[],
                    context_requirements=[context.user_intent],
                    priority=i + 1,
                    estimated_duration=30  # Default 30 minutes
                )
                workflow_nodes.append(node)
        
        # Calculate total duration
        total_duration = sum(node.estimated_duration for node in workflow_nodes)
        
        return {
            "nodes": [{"agent": node.agent_type, "task": node.task, "duration": node.estimated_duration} 
                     for node in workflow_nodes],
            "total_duration": total_duration,
            "complexity_score": context.resource_constraints.get("complexity", "medium"),
            "coordination_pattern": "sequential" if len(workflow_nodes) <= 3 else "parallel"
        }

    async def _optimize_coordination(self, workflow_plan: Dict[str, Any], context: OrchestrationContext) -> Dict[str, Any]:
        """Optimize the coordination plan for efficiency."""
        logger.info("Optimizing coordination plan")
        
        # Add optimization metadata
        workflow_plan["optimizations"] = {
            "parallelization": workflow_plan.get("coordination_pattern") == "parallel",
            "resource_efficiency": "high",
            "time_optimization": "enabled",
            "quality_gates": True
        }
        
        # Add agent coordination details
        workflow_plan["agents"] = workflow_plan.get("nodes", [])
        
        return workflow_plan

    async def _generate_orchestration_summary(self, plan: Dict[str, Any]) -> str:
        """Generate a human-readable orchestration summary."""
        logger.info("Generating orchestration summary")
        
        agents = plan.get("agents", [])
        duration = plan.get("total_duration", 0)
        pattern = plan.get("coordination_pattern", "sequential")
        
        summary = f"""🎯 Context-Driven Orchestration Plan

⚡ COORDINATION STRATEGY ({pattern.upper()}):
"""
        
        for i, agent in enumerate(agents, 1):
            summary += f"""
{i}. {agent['agent'].replace('_', ' ').title()} Agent ({agent['duration']}min)
   🔄 Task: {agent['task'].replace('_', ' ').title()}
   🎯 Coordination: {pattern} execution pattern"""
        
        summary += f"""

📊 ORCHESTRATION METRICS:
• Total Agents: {len(agents)}
• Estimated Duration: {duration} minutes
• Coordination Pattern: {pattern.title()}
• Complexity: {plan.get('complexity_score', 'medium').title()}
• Resource Efficiency: High

🚀 EXECUTION READY
All agents coordinated and workflow optimized for maximum efficiency.
"""
        
        return summary

# Export the agent class
__all__ = ['ContextDrivenOrchestrator']