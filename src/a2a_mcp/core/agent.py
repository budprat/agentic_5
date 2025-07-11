# ABOUTME: Base Agent class and capabilities enumeration
# ABOUTME: Defines the foundational agent interface for the A2A MCP framework

from abc import ABC, abstractmethod
from enum import Enum
from typing import Set, Dict, Any, Optional
from datetime import datetime

from a2a_mcp.common.utils import logger, generate_id


class AgentCapability(Enum):
    """Enumeration of agent capabilities"""
    # Core capabilities
    SEARCH = "search"
    SUMMARIZATION = "summarization"
    TEXT_PROCESSING = "text_processing"
    VALIDATION = "validation"
    QUALITY_ASSURANCE = "quality_assurance"
    
    # Extended capabilities
    WEB_SCRAPING = "web_scraping"
    DATA_ANALYSIS = "data_analysis"
    PLANNING = "planning"
    ORCHESTRATION = "orchestration"
    TRANSLATION = "translation"
    CODE_GENERATION = "code_generation"
    
    # Specialized capabilities
    LEARNING = "learning"
    TEACHING = "teaching"
    MONITORING = "monitoring"
    ALERTING = "alerting"
    REPORTING = "reporting"
    INTEGRATION = "integration"


class Agent(ABC):
    """
    Abstract base class for all agents in the A2A MCP framework
    """
    
    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        capabilities: Set[AgentCapability],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize base agent
        
        Args:
            agent_id: Unique identifier for the agent
            agent_type: Type/category of the agent
            capabilities: Set of capabilities this agent has
            metadata: Optional metadata about the agent
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()
        self.status = "active"
        
        # Initialize internal state
        self._message_history = []
        self._performance_metrics = {
            "messages_processed": 0,
            "errors": 0,
            "avg_response_time": 0.0
        }
        
        logger.info(
            f"Initialized {self.agent_type} agent",
            agent_id=self.agent_id,
            capabilities=[cap.value for cap in capabilities]
        )
    
    @abstractmethod
    async def process_request(self, message: Any) -> Any:
        """
        Process an incoming request message
        
        Args:
            message: The message to process
            
        Returns:
            Response message
        """
        pass
    
    async def process_message(self, message: Any) -> Any:
        """
        Process any incoming message (wrapper for process_request)
        
        Args:
            message: The message to process
            
        Returns:
            Response message
        """
        start_time = datetime.utcnow()
        
        try:
            # Process the request
            response = await self.process_request(message)
            
            # Update metrics
            self._update_metrics(start_time, success=True)
            
            return response
            
        except Exception as e:
            logger.error(
                f"Error processing message in {self.agent_type} agent",
                agent_id=self.agent_id,
                error=str(e)
            )
            
            # Update metrics
            self._update_metrics(start_time, success=False)
            
            raise
    
    def has_capability(self, capability: AgentCapability) -> bool:
        """
        Check if agent has a specific capability
        
        Args:
            capability: The capability to check
            
        Returns:
            True if agent has the capability
        """
        return capability in self.capabilities
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get agent status and metrics
        
        Returns:
            Dictionary containing status information
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.status,
            "capabilities": [cap.value for cap in self.capabilities],
            "created_at": self.created_at.isoformat(),
            "metrics": self._performance_metrics,
            "metadata": self.metadata
        }
    
    def _update_metrics(self, start_time: datetime, success: bool) -> None:
        """Update internal performance metrics"""
        response_time = (datetime.utcnow() - start_time).total_seconds()
        
        self._performance_metrics["messages_processed"] += 1
        
        if not success:
            self._performance_metrics["errors"] += 1
        
        # Update rolling average response time
        total_messages = self._performance_metrics["messages_processed"]
        prev_avg = self._performance_metrics["avg_response_time"]
        self._performance_metrics["avg_response_time"] = (
            (prev_avg * (total_messages - 1) + response_time) / total_messages
        )
    
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"agent_id='{self.agent_id}', "
            f"agent_type='{self.agent_type}', "
            f"capabilities={len(self.capabilities)})"
        )