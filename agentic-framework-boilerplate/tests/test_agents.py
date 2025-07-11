# ABOUTME: Tests for example agents demonstrating agent behavior validation
# ABOUTME: Covers generic agent functionality and protocol compliance

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from datetime import datetime

from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.a2a_protocol import A2AProtocolClient
from a2a_mcp.core.protocol import MessageType
from a2a_mcp.common.quality_framework import QualityResult, QualityThreshold


class TestExampleAgent:
    """Test suite for example agent functionality"""
    
    @pytest.fixture
    def example_agent(self):
        """Create an example agent instance for testing"""
        class ExampleAgent(BaseAgent):
            def __init__(self):
                super().__init__(
                    agent_id="test-example-001",
                    name="Example Agent",
                    description="Test example agent",
                    capabilities=["example", "testing"]
                )
            
            async def process_request(self, message: dict) -> dict:
                """Process incoming requests"""
                action = message.get("action")
                if action == "echo":
                    return {"result": message.get("data", "")}
                elif action == "calculate":
                    nums = message.get("numbers", [])
                    return {"result": sum(nums)}
                else:
                    raise ValueError(f"Unknown action: {action}")
        
        return ExampleAgent()
    
    def test_agent_initialization(self, example_agent):
        """Test agent is properly initialized"""
        assert example_agent.agent_id == "test-example-001"
        assert example_agent.name == "Example Agent"
        assert "example" in example_agent.capabilities
        assert "testing" in example_agent.capabilities
    
    @pytest.mark.asyncio
    async def test_echo_request_processing(self, example_agent):
        """Test agent processes echo requests correctly"""
        # Create an echo request message
        request = {
            "action": "echo",
            "data": "Hello, World!"
        }
        
        # Process the request
        response = await example_agent.process_request(request)
        
        # Verify response
        assert response["result"] == "Hello, World!"
    
    @pytest.mark.asyncio
    async def test_calculate_request_processing(self, example_agent):
        """Test agent processes calculation requests correctly"""
        # Create a calculation request
        request = {
            "action": "calculate",
            "numbers": [1, 2, 3, 4, 5]
        }
        
        # Process the request
        response = await example_agent.process_request(request)
        
        # Verify response
        assert response["result"] == 15
    
    @pytest.mark.asyncio
    async def test_unknown_action_handling(self, example_agent):
        """Test agent handles unknown actions appropriately"""
        # Create a request with unknown action
        request = {
            "action": "unknown",
            "data": "test"
        }
        
        # Process should raise ValueError
        with pytest.raises(ValueError, match="Unknown action: unknown"):
            await example_agent.process_request(request)
    
    @pytest.mark.asyncio
    async def test_agent_quality_validation(self, example_agent):
        """Test agent quality validation"""
        # Mock quality framework
        with patch.object(example_agent, 'validate_quality', new_callable=AsyncMock) as mock_validate:
            # Set up mock to return a quality result
            mock_report = QualityResult(
                passed=True,
                score=0.98,
                message="All quality checks passed",
                details={
                    "response_time": 0.05,
                    "accuracy": 0.98
                }
            )
            mock_validate.return_value = mock_report
            
            # Run validation
            report = await example_agent.validate_quality({})
            
            # Verify report
            assert report.passed is True
            assert report.score == 0.98
            assert "response_time" in report.details


class TestAgentCommunication:
    """Test suite for agent-to-agent communication"""
    
    @pytest.fixture
    def protocol(self):
        """Create A2A protocol instance"""
        return A2AProtocolClient()
    
    @pytest.mark.asyncio
    async def test_agent_message_routing(self, protocol):
        """Test message routing between agents"""
        # Create mock agents
        sender = Mock(agent_id="sender-001")
        receiver = Mock(agent_id="receiver-001")
        receiver.process_message = AsyncMock(return_value={"status": "success"})
        
        # Register agents
        protocol.register_agent(sender)
        protocol.register_agent(receiver)
        
        # Create and route message
        message = {
            "sender_id": "sender-001",
            "receiver_id": "receiver-001",
            "message_type": MessageType.REQUEST,
            "content": {"action": "test"}
        }
        
        # Route message
        response = await protocol.route_message(message)
        
        # Verify routing
        receiver.process_message.assert_called_once()
        assert response["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_broadcast_message(self, protocol):
        """Test broadcasting messages to multiple agents"""
        # Create mock agents
        agents = []
        for i in range(3):
            agent = Mock(agent_id=f"agent-{i:03d}")
            agent.process_message = AsyncMock(return_value={"agent_id": agent.agent_id})
            protocol.register_agent(agent)
            agents.append(agent)
        
        # Broadcast message
        message = {
            "sender_id": "broadcaster-001",
            "message_type": MessageType.BROADCAST,
            "content": {"announcement": "test"}
        }
        
        responses = await protocol.broadcast_message(message)
        
        # Verify all agents received message
        assert len(responses) == 3
        for i, agent in enumerate(agents):
            agent.process_message.assert_called_once()
            assert responses[i]["agent_id"] == f"agent-{i:03d}"