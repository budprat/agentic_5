# ABOUTME: Google ADK Agent base class placeholder
# ABOUTME: Provides minimal Agent interface for compatibility

"""Google ADK Agent base class."""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class Agent(ABC):
    """Base Agent class for Google ADK compatibility."""
    
    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None):
        """Initialize agent."""
        self.agent_id = agent_id
        self.config = config or {}
        self.capabilities = []
    
    @abstractmethod
    async def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a query."""
        pass
    
    def get_capabilities(self) -> list:
        """Get agent capabilities."""
        return self.capabilities
    
    def add_capability(self, capability: str):
        """Add a capability."""
        if capability not in self.capabilities:
            self.capabilities.append(capability)