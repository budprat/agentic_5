# ABOUTME: Tests for A2A (Agent-to-Agent) communication protocol
# ABOUTME: Covers message handling, routing, and protocol compliance

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from datetime import datetime
import json

from a2a_mcp.core.protocol import (
    A2AMessage, MessageType, MessageStatus, ProtocolVersion,
    A2AProtocol, ProtocolError, MessageValidator
)
from a2a_mcp.core.agent import Agent, AgentCapability


class TestA2AMessage:
    """Test suite for A2AMessage functionality"""
    
    def test_message_creation(self):
        """Test creating a valid A2A message"""
        msg = A2AMessage(
            message_id="test-001",
            sender_id="agent-001",
            receiver_id="agent-002",
            message_type=MessageType.REQUEST,
            content={"action": "test"},
            metadata={"priority": "high"}
        )
        
        assert msg.message_id == "test-001"
        assert msg.sender_id == "agent-001"
        assert msg.receiver_id == "agent-002"
        assert msg.message_type == MessageType.REQUEST
        assert msg.content == {"action": "test"}
        assert msg.metadata["priority"] == "high"
        assert msg.timestamp is not None
        assert msg.protocol_version == ProtocolVersion.V1_0
    
    def test_message_serialization(self):
        """Test message serialization to dict"""
        msg = A2AMessage(
            message_id="test-002",
            sender_id="agent-001",
            receiver_id="agent-002",
            message_type=MessageType.RESPONSE,
            content={"result": "success"},
            status=MessageStatus.COMPLETED
        )
        
        msg_dict = msg.to_dict()
        
        assert msg_dict["message_id"] == "test-002"
        assert msg_dict["sender_id"] == "agent-001"
        assert msg_dict["receiver_id"] == "agent-002"
        assert msg_dict["message_type"] == "RESPONSE"
        assert msg_dict["status"] == "COMPLETED"
        assert msg_dict["content"] == {"result": "success"}
        assert "timestamp" in msg_dict
        assert msg_dict["protocol_version"] == "1.0"
    
    def test_message_deserialization(self):
        """Test message deserialization from dict"""
        msg_dict = {
            "message_id": "test-003",
            "sender_id": "agent-001",
            "receiver_id": "agent-002",
            "message_type": "REQUEST",
            "content": {"action": "query"},
            "timestamp": datetime.now().isoformat(),
            "protocol_version": "1.0",
            "status": "PENDING"
        }
        
        msg = A2AMessage.from_dict(msg_dict)
        
        assert msg.message_id == "test-003"
        assert msg.sender_id == "agent-001"
        assert msg.receiver_id == "agent-002"
        assert msg.message_type == MessageType.REQUEST
        assert msg.content == {"action": "query"}
        assert msg.status == MessageStatus.PENDING
    
    def test_message_validation(self):
        """Test message validation"""
        # Valid message
        valid_msg = A2AMessage(
            message_id="test-004",
            sender_id="agent-001",
            receiver_id="agent-002",
            message_type=MessageType.REQUEST,
            content={"action": "test"}
        )
        
        assert MessageValidator.validate(valid_msg) is True
        
        # Invalid message (empty content for REQUEST)
        invalid_msg = A2AMessage(
            message_id="test-005",
            sender_id="agent-001",
            receiver_id="agent-002",
            message_type=MessageType.REQUEST,
            content={}
        )
        
        with pytest.raises(ProtocolError):
            MessageValidator.validate(invalid_msg, raise_on_error=True)


class TestA2AProtocol:
    """Test suite for A2A Protocol implementation"""
    
    @pytest.fixture
    def protocol(self):
        """Create A2AProtocol instance for testing"""
        return A2AProtocol()
    
    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent for testing"""
        agent = Mock(spec=Agent)
        agent.agent_id = "test-agent-001"
        agent.capabilities = {AgentCapability.SEARCH}
        agent.process_message = AsyncMock()
        return agent
    
    @pytest.mark.asyncio
    async def test_agent_registration(self, protocol, mock_agent):
        """Test agent registration with protocol"""
        # Register agent
        protocol.register_agent(mock_agent)
        
        # Verify registration
        assert mock_agent.agent_id in protocol.agents
        assert protocol.get_agent(mock_agent.agent_id) == mock_agent
        
        # Test duplicate registration
        with pytest.raises(ProtocolError):
            protocol.register_agent(mock_agent)
    
    @pytest.mark.asyncio
    async def test_agent_unregistration(self, protocol, mock_agent):
        """Test agent unregistration"""
        # Register and then unregister
        protocol.register_agent(mock_agent)
        protocol.unregister_agent(mock_agent.agent_id)
        
        # Verify unregistration
        assert mock_agent.agent_id not in protocol.agents
        assert protocol.get_agent(mock_agent.agent_id) is None
    
    @pytest.mark.asyncio
    async def test_message_routing(self, protocol, mock_agent):
        """Test message routing between agents"""
        # Register agent
        protocol.register_agent(mock_agent)
        
        # Create message
        message = A2AMessage(
            message_id="route-001",
            sender_id="external",
            receiver_id=mock_agent.agent_id,
            message_type=MessageType.REQUEST,
            content={"action": "test"}
        )
        
        # Route message
        await protocol.route_message(message)
        
        # Verify agent received message
        mock_agent.process_message.assert_called_once()
        call_args = mock_agent.process_message.call_args[0]
        assert call_args[0].message_id == "route-001"
    
    @pytest.mark.asyncio
    async def test_message_routing_unknown_agent(self, protocol):
        """Test routing to unknown agent"""
        message = A2AMessage(
            message_id="route-002",
            sender_id="external",
            receiver_id="unknown-agent",
            message_type=MessageType.REQUEST,
            content={"action": "test"}
        )
        
        with pytest.raises(ProtocolError) as exc_info:
            await protocol.route_message(message)
        
        assert "unknown-agent" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_broadcast_message(self, protocol):
        """Test broadcasting messages to multiple agents"""
        # Create multiple mock agents
        agents = []
        for i in range(3):
            agent = Mock(spec=Agent)
            agent.agent_id = f"test-agent-{i:03d}"
            agent.capabilities = {AgentCapability.SEARCH}
            agent.process_message = AsyncMock()
            protocol.register_agent(agent)
            agents.append(agent)
        
        # Create broadcast message
        message = A2AMessage(
            message_id="broadcast-001",
            sender_id="broadcaster",
            receiver_id="*",  # Broadcast indicator
            message_type=MessageType.BROADCAST,
            content={"notification": "test broadcast"}
        )
        
        # Broadcast message
        await protocol.broadcast_message(message, capability_filter=AgentCapability.SEARCH)
        
        # Verify all agents received message
        for agent in agents:
            agent.process_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_request_response_correlation(self, protocol, mock_agent):
        """Test request-response correlation"""
        protocol.register_agent(mock_agent)
        
        # Configure mock to return response
        response = A2AMessage(
            message_id="resp-001",
            sender_id=mock_agent.agent_id,
            receiver_id="requester",
            message_type=MessageType.RESPONSE,
            content={"result": "success"},
            correlation_id="req-001"
        )
        mock_agent.process_message.return_value = response
        
        # Send request
        request = A2AMessage(
            message_id="req-001",
            sender_id="requester",
            receiver_id=mock_agent.agent_id,
            message_type=MessageType.REQUEST,
            content={"action": "test"}
        )
        
        result = await protocol.send_request(request, timeout=5.0)
        
        assert result.message_id == "resp-001"
        assert result.correlation_id == "req-001"
        assert result.content["result"] == "success"
    
    @pytest.mark.asyncio
    async def test_request_timeout(self, protocol, mock_agent):
        """Test request timeout handling"""
        protocol.register_agent(mock_agent)
        
        # Configure mock to delay response beyond timeout
        async def delayed_response(msg):
            await asyncio.sleep(2.0)
            return A2AMessage(
                message_id="resp-002",
                sender_id=mock_agent.agent_id,
                receiver_id=msg.sender_id,
                message_type=MessageType.RESPONSE,
                content={"result": "success"}
            )
        
        mock_agent.process_message.side_effect = delayed_response
        
        # Send request with short timeout
        request = A2AMessage(
            message_id="req-002",
            sender_id="requester",
            receiver_id=mock_agent.agent_id,
            message_type=MessageType.REQUEST,
            content={"action": "test"}
        )
        
        with pytest.raises(asyncio.TimeoutError):
            await protocol.send_request(request, timeout=0.5)


class TestProtocolHandshake:
    """Test suite for protocol handshake and capability negotiation"""
    
    @pytest.mark.asyncio
    async def test_capability_negotiation(self):
        """Test capability negotiation between agents"""
        protocol = A2AProtocol()
        
        # Create two agents with different capabilities
        agent1 = Mock(spec=Agent)
        agent1.agent_id = "agent-001"
        agent1.capabilities = {AgentCapability.SEARCH, AgentCapability.SUMMARIZATION}
        agent1.process_message = AsyncMock()
        
        agent2 = Mock(spec=Agent)
        agent2.agent_id = "agent-002"
        agent2.capabilities = {AgentCapability.SUMMARIZATION, AgentCapability.VALIDATION}
        agent2.process_message = AsyncMock()
        
        protocol.register_agent(agent1)
        protocol.register_agent(agent2)
        
        # Perform capability query
        capabilities = await protocol.query_agent_capabilities(agent2.agent_id)
        
        assert AgentCapability.SUMMARIZATION in capabilities
        assert AgentCapability.VALIDATION in capabilities
        assert AgentCapability.SEARCH not in capabilities
    
    @pytest.mark.asyncio
    async def test_protocol_version_negotiation(self):
        """Test protocol version compatibility checking"""
        # Test compatible versions
        msg_v1 = A2AMessage(
            message_id="version-001",
            sender_id="agent-001",
            receiver_id="agent-002",
            message_type=MessageType.REQUEST,
            content={"test": "data"},
            protocol_version=ProtocolVersion.V1_0
        )
        
        assert MessageValidator.is_version_compatible(msg_v1, ProtocolVersion.V1_0)
        
        # Test future version handling
        msg_future = A2AMessage(
            message_id="version-002",
            sender_id="agent-001",
            receiver_id="agent-002",
            message_type=MessageType.REQUEST,
            content={"test": "data"}
        )
        # Manually set future version
        msg_future.protocol_version = "2.0"
        
        # Should handle gracefully or raise appropriate error
        assert not MessageValidator.is_version_compatible(msg_future, ProtocolVersion.V1_0)


class TestProtocolSecurity:
    """Test suite for protocol security features"""
    
    def test_message_authentication(self):
        """Test message authentication and integrity"""
        # Create message with authentication
        msg = A2AMessage(
            message_id="secure-001",
            sender_id="trusted-agent",
            receiver_id="receiver",
            message_type=MessageType.REQUEST,
            content={"sensitive": "data"},
            metadata={"authenticated": True, "signature": "mock-signature"}
        )
        
        # Verify authentication metadata
        assert msg.metadata.get("authenticated") is True
        assert "signature" in msg.metadata
    
    @pytest.mark.asyncio
    async def test_message_encryption_placeholder(self):
        """Test placeholder for message encryption (future feature)"""
        # This is a placeholder for future encryption support
        msg = A2AMessage(
            message_id="encrypt-001",
            sender_id="agent-001",
            receiver_id="agent-002",
            message_type=MessageType.REQUEST,
            content={"data": "to-encrypt"},
            metadata={"encryption": "none"}
        )
        
        # Currently no encryption, but structure supports it
        assert msg.metadata.get("encryption") == "none"


class TestProtocolMetrics:
    """Test suite for protocol metrics and monitoring"""
    
    @pytest.mark.asyncio
    async def test_message_latency_tracking(self):
        """Test message latency measurement"""
        protocol = A2AProtocol()
        
        # Create mock agent with controlled response time
        agent = Mock(spec=Agent)
        agent.agent_id = "metrics-agent"
        agent.process_message = AsyncMock()
        
        async def timed_response(msg):
            await asyncio.sleep(0.1)  # 100ms delay
            return A2AMessage(
                message_id="metric-resp",
                sender_id=agent.agent_id,
                receiver_id=msg.sender_id,
                message_type=MessageType.RESPONSE,
                content={"result": "done"}
            )
        
        agent.process_message.side_effect = timed_response
        protocol.register_agent(agent)
        
        # Send request and measure time
        request = A2AMessage(
            message_id="metric-req",
            sender_id="requester",
            receiver_id=agent.agent_id,
            message_type=MessageType.REQUEST,
            content={"action": "test"}
        )
        
        start_time = datetime.now()
        response = await protocol.send_request(request)
        end_time = datetime.now()
        
        latency = (end_time - start_time).total_seconds()
        assert 0.09 < latency < 0.15  # Allow some variance
        assert response.content["result"] == "done"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])