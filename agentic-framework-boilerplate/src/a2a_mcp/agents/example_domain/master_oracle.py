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
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from a2a_mcp.agents.base import StandardizedAgentBase
from a2a_mcp.core.messaging import Message, MessageType
from a2a_mcp.quality.framework import QualityFramework
from a2a_mcp.quality.domains import QualityDomain


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
        super().__init__(agent_id=agent_id)
        
        # Initialize quality framework with business domain
        self.quality = QualityFramework(
            domain=QualityDomain.BUSINESS,
            agent_id=agent_id
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
    
    async def process_message(self, message: Message) -> Optional[Message]:
        """
        Process incoming messages and coordinate responses.
        
        Demonstrates:
        - Message type handling
        - Quality validation
        - Multi-agent coordination
        """
        # Apply quality checks to incoming message
        quality_result = await self.quality.validate_input(
            message.payload,
            context={"message_type": message.type}
        )
        
        if not quality_result.passed:
            return self.create_error_response(
                message,
                f"Quality check failed: {quality_result.issues}"
            )
        
        # Route based on message type
        if message.type == MessageType.REQUEST:
            return await self._handle_analysis_request(message)
        elif message.type == MessageType.RESPONSE:
            return await self._handle_agent_response(message)
        elif message.type == MessageType.QUERY:
            return await self._handle_status_query(message)
        else:
            return await self._handle_generic_message(message)
    
    async def _handle_analysis_request(self, message: Message) -> Message:
        """
        Handle analysis requests by delegating to specialized agents.
        
        This demonstrates the orchestration pattern:
        1. Parse request
        2. Identify required agents
        3. Send coordinated requests
        4. Track pending tasks
        """
        request_id = message.metadata.get("request_id", message.id)
        analysis_type = message.payload.get("type", "comprehensive")
        
        # Store request context
        self.context.pending_tasks[request_id] = {
            "original_message": message,
            "analysis_type": analysis_type,
            "responses_received": {},
            "started_at": asyncio.get_event_loop().time()
        }
        
        # Delegate to specialized agents based on analysis type
        if analysis_type == "comprehensive":
            # Send requests to all subordinate agents
            for agent_id in self.context.subordinate_agents:
                await self._send_to_agent(
                    agent_id,
                    MessageType.REQUEST,
                    {
                        "oracle_request_id": request_id,
                        "data": message.payload.get("data"),
                        "parameters": message.payload.get("parameters", {})
                    }
                )
        elif analysis_type == "risk_focused":
            # Only send to risk assessor
            await self._send_to_agent(
                "risk_assessor_agent",
                MessageType.REQUEST,
                {
                    "oracle_request_id": request_id,
                    "data": message.payload.get("data"),
                    "risk_factors": message.payload.get("risk_factors", [])
                }
            )
        
        # Return acknowledgment
        return self.create_response(
            message,
            {
                "status": "processing",
                "request_id": request_id,
                "delegated_to": self._get_active_agents(analysis_type),
                "estimated_completion": "30-60 seconds"
            }
        )
    
    async def _handle_agent_response(self, message: Message) -> Optional[Message]:
        """
        Handle responses from subordinate agents.
        
        Demonstrates:
        - Response aggregation
        - Quality scoring
        - Decision synthesis
        """
        oracle_request_id = message.payload.get("oracle_request_id")
        if not oracle_request_id or oracle_request_id not in self.context.pending_tasks:
            return None
        
        task_context = self.context.pending_tasks[oracle_request_id]
        sender_id = message.metadata.get("sender_id", "unknown")
        
        # Store response with quality score
        response_quality = await self.quality.score_output(
            message.payload,
            context={"agent_type": sender_id}
        )
        
        task_context["responses_received"][sender_id] = {
            "payload": message.payload,
            "quality_score": response_quality.score,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # Check if we have enough responses to make a decision
        if self._can_make_decision(task_context):
            return await self._synthesize_decision(oracle_request_id)
        
        return None
    
    async def _synthesize_decision(self, request_id: str) -> Message:
        """
        Synthesize a decision from multiple agent responses.
        
        Key pattern: Weighted aggregation based on quality scores
        """
        task_context = self.context.pending_tasks[request_id]
        original_message = task_context["original_message"]
        responses = task_context["responses_received"]
        
        # Calculate weighted consensus
        total_weight = 0
        weighted_results = {}
        
        for agent_id, response_data in responses.items():
            weight = response_data["quality_score"]
            if weight >= self.context.decision_criteria["quality_min_score"]:
                total_weight += weight
                
                # Aggregate numerical results
                for key, value in response_data["payload"].items():
                    if isinstance(value, (int, float)):
                        if key not in weighted_results:
                            weighted_results[key] = 0
                        weighted_results[key] += value * weight
        
        # Normalize weighted results
        if total_weight > 0:
            for key in weighted_results:
                weighted_results[key] /= total_weight
        
        # Build synthesized response
        synthesis = {
            "request_id": request_id,
            "synthesis_type": "weighted_consensus",
            "aggregated_results": weighted_results,
            "contributing_agents": list(responses.keys()),
            "confidence": self._calculate_confidence(responses),
            "quality_metrics": {
                "average_quality": sum(r["quality_score"] for r in responses.values()) / len(responses),
                "total_agents": len(responses)
            }
        }
        
        # Clean up
        del self.context.pending_tasks[request_id]
        
        # Return synthesized response
        return self.create_response(original_message, synthesis)
    
    async def _send_to_agent(self, agent_id: str, msg_type: MessageType, payload: Dict[str, Any]):
        """
        Send a message to another agent.
        
        This is where the actual A2A communication happens.
        In a real implementation, this would use the message broker.
        """
        message = Message(
            type=msg_type,
            payload=payload,
            metadata={
                "sender_id": self.agent_id,
                "target_agent": agent_id,
                "timestamp": asyncio.get_event_loop().time()
            }
        )
        
        # In production, this would publish to the message broker
        # For this example, we'll just log it
        self.logger.info(f"Sending message to {agent_id}: {message.type}")
        
        # TODO: Integrate with actual message broker
        # await self.message_broker.publish(agent_id, message)
    
    def _get_active_agents(self, analysis_type: str) -> List[str]:
        """Determine which agents to use based on analysis type"""
        if analysis_type == "comprehensive":
            return self.context.subordinate_agents
        elif analysis_type == "risk_focused":
            return ["risk_assessor_agent"]
        elif analysis_type == "market_analysis":
            return ["market_predictor_agent", "data_analyst_agent"]
        else:
            return self.context.subordinate_agents
    
    def _can_make_decision(self, task_context: Dict[str, Any]) -> bool:
        """
        Determine if we have enough information to make a decision.
        
        Uses consensus threshold from decision criteria.
        """
        responses_received = len(task_context["responses_received"])
        expected_responses = len(self._get_active_agents(task_context["analysis_type"]))
        
        # Check if we have minimum consensus
        if expected_responses > 0:
            response_ratio = responses_received / expected_responses
            return response_ratio >= self.context.decision_criteria["consensus_threshold"]
        
        return False
    
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
    
    async def _handle_status_query(self, message: Message) -> Message:
        """Handle status queries about pending tasks"""
        request_id = message.payload.get("request_id")
        
        if request_id and request_id in self.context.pending_tasks:
            task_context = self.context.pending_tasks[request_id]
            status = {
                "status": "in_progress",
                "responses_received": len(task_context["responses_received"]),
                "responses_expected": len(self._get_active_agents(task_context["analysis_type"])),
                "elapsed_time": asyncio.get_event_loop().time() - task_context["started_at"]
            }
        else:
            status = {
                "status": "not_found",
                "message": f"No pending task with ID: {request_id}"
            }
        
        return self.create_response(message, status)
    
    async def _handle_generic_message(self, message: Message) -> Message:
        """Fallback handler for unrecognized message types"""
        return self.create_response(
            message,
            {
                "status": "unsupported",
                "message": f"Message type {message.type} not supported by oracle",
                "supported_types": ["REQUEST", "RESPONSE", "QUERY"]
            }
        )
    
    def create_error_response(self, original_message: Message, error: str) -> Message:
        """Create an error response message"""
        return self.create_response(
            original_message,
            {
                "status": "error",
                "error": error,
                "original_request": original_message.id
            }
        )


# Example usage and testing
async def example_oracle_usage():
    """
    Demonstrates how to use the Master Oracle Agent.
    
    This example shows:
    1. Creating the oracle
    2. Sending analysis requests
    3. Handling responses
    """
    # Create oracle instance
    oracle = MasterOracleAgent("business_oracle")
    
    # Example analysis request
    analysis_request = Message(
        type=MessageType.REQUEST,
        payload={
            "type": "comprehensive",
            "data": {
                "market_indicators": [100, 105, 103, 108],
                "risk_factors": ["volatility", "regulation"],
                "timeframe": "Q1-2024"
            },
            "parameters": {
                "confidence_required": 0.8,
                "include_predictions": True
            }
        },
        metadata={"request_id": "analysis_001"}
    )
    
    # Process request
    response = await oracle.process_message(analysis_request)
    print(f"Oracle response: {response.payload}")
    
    # Simulate agent responses
    # In production, these would come from actual agents via message broker
    agent_response_1 = Message(
        type=MessageType.RESPONSE,
        payload={
            "oracle_request_id": "analysis_001",
            "risk_score": 0.65,
            "market_trend": "bullish",
            "confidence": 0.82
        },
        metadata={"sender_id": "risk_assessor_agent"}
    )
    
    agent_response_2 = Message(
        type=MessageType.RESPONSE,
        payload={
            "oracle_request_id": "analysis_001",
            "predicted_growth": 0.12,
            "market_trend": "bullish",
            "volatility": 0.23
        },
        metadata={"sender_id": "market_predictor_agent"}
    )
    
    # Process agent responses
    await oracle.process_message(agent_response_1)
    final_synthesis = await oracle.process_message(agent_response_2)
    
    if final_synthesis:
        print(f"Final synthesis: {final_synthesis.payload}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_oracle_usage())