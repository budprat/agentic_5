# ABOUTME: A2A (Agent-to-Agent) communication protocol implementation
# ABOUTME: Defines message formats, routing, and protocol handling

import asyncio
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field, asdict

from a2a_mcp.common.utils import logger, generate_id, utc_now


class MessageType(Enum):
    """Types of messages in the A2A protocol"""
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"
    NOTIFICATION = "NOTIFICATION"
    BROADCAST = "BROADCAST"
    ERROR = "ERROR"
    HANDSHAKE = "HANDSHAKE"
    HEARTBEAT = "HEARTBEAT"


class MessageStatus(Enum):
    """Status of message processing"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"


class ProtocolVersion(Enum):
    """A2A protocol versions"""
    V1_0 = "1.0"
    V1_1 = "1.1"
    V2_0 = "2.0"


@dataclass
class A2AMessage:
    """
    Standard message format for agent-to-agent communication
    """
    message_id: str
    sender_id: str
    receiver_id: str
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=utc_now)
    protocol_version: ProtocolVersion = ProtocolVersion.V1_0
    status: MessageStatus = MessageStatus.PENDING
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        data = asdict(self)
        # Convert enums to strings
        data["message_type"] = self.message_type.value
        data["status"] = self.status.value
        data["protocol_version"] = self.protocol_version.value
        data["timestamp"] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "A2AMessage":
        """Create message from dictionary"""
        # Convert strings back to enums
        data["message_type"] = MessageType(data["message_type"])
        data["status"] = MessageStatus(data["status"])
        data["protocol_version"] = ProtocolVersion(data["protocol_version"])
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


class ProtocolError(Exception):
    """Exception raised for protocol-related errors"""
    pass


class MessageValidator:
    """Validates A2A messages according to protocol rules"""
    
    @staticmethod
    def validate(message: A2AMessage, raise_on_error: bool = False) -> bool:
        """
        Validate a message according to protocol rules
        
        Args:
            message: Message to validate
            raise_on_error: Whether to raise exception on validation failure
            
        Returns:
            True if valid, False otherwise
            
        Raises:
            ProtocolError: If raise_on_error=True and validation fails
        """
        errors = []
        
        # Check required fields
        if not message.message_id:
            errors.append("Message ID is required")
        
        if not message.sender_id:
            errors.append("Sender ID is required")
        
        if not message.receiver_id:
            errors.append("Receiver ID is required")
        
        # Check content for certain message types
        if message.message_type == MessageType.REQUEST and not message.content:
            errors.append("Request messages must have content")
        
        # Check protocol version compatibility
        if not MessageValidator.is_version_compatible(
            message,
            ProtocolVersion.V1_0
        ):
            errors.append(f"Unsupported protocol version: {message.protocol_version}")
        
        if errors and raise_on_error:
            raise ProtocolError(f"Message validation failed: {'; '.join(errors)}")
        
        return len(errors) == 0
    
    @staticmethod
    def is_version_compatible(
        message: A2AMessage,
        supported_version: ProtocolVersion
    ) -> bool:
        """Check if message protocol version is compatible"""
        # Simple version check - in real implementation would be more sophisticated
        try:
            msg_version = float(message.protocol_version.value)
            supported = float(supported_version.value)
            return msg_version <= supported
        except (ValueError, AttributeError):
            return False


class A2AProtocol:
    """
    Main protocol handler for agent-to-agent communication
    """
    
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.pending_responses: Dict[str, asyncio.Future] = {}
        
    def register_agent(self, agent: Any) -> None:
        """
        Register an agent with the protocol
        
        Args:
            agent: Agent to register
            
        Raises:
            ProtocolError: If agent is already registered
        """
        if agent.agent_id in self.agents:
            raise ProtocolError(f"Agent {agent.agent_id} is already registered")
        
        self.agents[agent.agent_id] = agent
        logger.info(f"Registered agent: {agent.agent_id}")
    
    def unregister_agent(self, agent_id: str) -> None:
        """
        Unregister an agent
        
        Args:
            agent_id: ID of agent to unregister
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Unregistered agent: {agent_id}")
    
    def get_agent(self, agent_id: str) -> Optional[Any]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    async def route_message(self, message: A2AMessage) -> None:
        """
        Route a message to the appropriate agent
        
        Args:
            message: Message to route
            
        Raises:
            ProtocolError: If receiver agent not found
        """
        # Validate message
        MessageValidator.validate(message, raise_on_error=True)
        
        # Find receiver agent
        receiver = self.agents.get(message.receiver_id)
        if not receiver:
            raise ProtocolError(f"Agent not found: {message.receiver_id}")
        
        # Route message
        logger.debug(
            f"Routing message from {message.sender_id} to {message.receiver_id}"
        )
        
        # Process message through agent
        response = await receiver.process_message(message)
        
        # If this was a request and we got a response, handle correlation
        if (message.message_type == MessageType.REQUEST and 
            response and 
            message.message_id in self.pending_responses):
            
            future = self.pending_responses.pop(message.message_id)
            future.set_result(response)
    
    async def send_request(
        self,
        message: A2AMessage,
        timeout: float = 30.0
    ) -> A2AMessage:
        """
        Send a request and wait for response
        
        Args:
            message: Request message
            timeout: Timeout in seconds
            
        Returns:
            Response message
            
        Raises:
            asyncio.TimeoutError: If timeout exceeded
        """
        # Create future for response
        future = asyncio.Future()
        self.pending_responses[message.message_id] = future
        
        try:
            # Route the message
            await self.route_message(message)
            
            # Wait for response with timeout
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
            
        except asyncio.TimeoutError:
            # Clean up pending response
            self.pending_responses.pop(message.message_id, None)
            raise
        
    async def broadcast_message(
        self,
        message: A2AMessage,
        capability_filter: Optional[Any] = None
    ) -> None:
        """
        Broadcast a message to multiple agents
        
        Args:
            message: Message to broadcast
            capability_filter: Optional capability to filter agents
        """
        # Get target agents
        target_agents = []
        for agent in self.agents.values():
            if capability_filter:
                if hasattr(agent, 'has_capability') and agent.has_capability(capability_filter):
                    target_agents.append(agent)
            else:
                target_agents.append(agent)
        
        # Send to all target agents
        logger.info(f"Broadcasting message to {len(target_agents)} agents")
        
        tasks = []
        for agent in target_agents:
            # Create individual message for each agent
            agent_message = A2AMessage(
                message_id=generate_id("msg"),
                sender_id=message.sender_id,
                receiver_id=agent.agent_id,
                message_type=message.message_type,
                content=message.content,
                correlation_id=message.message_id,
                metadata=message.metadata
            )
            
            tasks.append(agent.process_message(agent_message))
        
        # Process all messages concurrently
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def query_agent_capabilities(self, agent_id: str) -> Set[Any]:
        """
        Query capabilities of a specific agent
        
        Args:
            agent_id: ID of agent to query
            
        Returns:
            Set of agent capabilities
        """
        agent = self.get_agent(agent_id)
        if agent and hasattr(agent, 'capabilities'):
            return agent.capabilities
        return set()