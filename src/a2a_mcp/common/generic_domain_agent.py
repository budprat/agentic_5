"""
Generic Domain Agent Template for Framework V2.0.

This template provides sophisticated domain agent patterns derived from battle-tested 
solopreneur implementations. It sits between StandardizedAgentBase and domain-specific 
agents, providing common patterns like tier determination, health monitoring, A2A 
protocol handling, and response formatting.

Usage:
    class YourDomainAgent(GenericDomainAgent):
        def __init__(self, agent_name, description, instructions, port=None):
            super().__init__(
                agent_name=agent_name,
                description=description, 
                instructions=instructions,
                port=port,
                port_ranges={
                    "tier_1": (11001, 11001),
                    "tier_2": (11002, 11006),
                    "tier_3": (11010, 11059)
                },
                quality_domain="technical",
                domain_name="YourDomain"
            )
"""

# type: ignore

import json
import logging
import os
import re
import uuid
from collections.abc import AsyncIterable
from typing import Any, Dict, Optional, Tuple

from a2a_mcp.common.agent_runner import AgentRunner
from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.common.utils import get_mcp_server_config, init_api_key
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams
from google.genai import types as genai_types

logger = logging.getLogger(__name__)

def validate_environment(required_vars: list[str] = None):
    """Validate required environment variables."""
    if required_vars is None:
        required_vars = ['GOOGLE_API_KEY']
    
    for var in required_vars:
        if not os.environ.get(var):
            raise ValueError(f'{var} is required but not set')
    
    # Validate quoted values
    if 'GOOGLE_CLOUD_PROJECT' in os.environ:
        project = os.environ['GOOGLE_CLOUD_PROJECT']
        if ' ' in project and not (project.startswith('"') and project.endswith('"')):
            logger.warning('GOOGLE_CLOUD_PROJECT contains spaces but is not quoted')

def create_a2a_request(method: str, message: str, metadata: dict = None):
    """Standardize A2A request format per protocol specification."""
    return {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": method,  # Use 'message/send' or 'message/stream'
        "params": {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": message}],
                "messageId": str(uuid.uuid4()),
                "kind": "message"
            },
            "metadata": metadata or {}
        }
    }

class GenericDomainAgent(StandardizedAgentBase):
    """
    Generic Framework V2.0 compliant domain agent template.
    
    Provides sophisticated patterns for tier-based agents including:
    - Configurable port ranges and tier determination
    - Domain-specific quality configuration
    - A2A protocol integration
    - Advanced response formatting
    - Health monitoring with tier awareness
    - Robust error handling and fallbacks
    """
    
    def __init__(
        self, 
        agent_name: str, 
        description: str, 
        instructions: str,
        port: int = None,
        port_ranges: Dict[str, Tuple[int, int]] = None,
        quality_domain: str = "TECHNICAL",
        domain_name: str = "Generic",
        required_env_vars: list[str] = None
    ):
        """
        Initialize generic domain agent.
        
        Args:
            agent_name: Name of the agent
            description: Agent description
            instructions: Agent instructions/prompt
            port: Port number for tier determination
            port_ranges: Dict defining tier port ranges
                Example: {"tier_1": (10001, 10001), "tier_2": (10002, 10006), "tier_3": (10010, 10059)}
            quality_domain: Quality domain (TECHNICAL, BUSINESS, CREATIVE, SERVICE)
            domain_name: Name of the domain for logging/identification
            required_env_vars: List of required environment variables
        """
        # Set default port ranges if not provided
        if port_ranges is None:
            port_ranges = {
                "tier_1": (10001, 10001),
                "tier_2": (10002, 10009), 
                "tier_3": (10010, 10099)
            }
        
        # Validate environment first
        try:
            validate_environment(required_env_vars)
        except ValueError as e:
            logger.error(f'Environment validation failed: {e}')
            raise
            
        # Use StandardizedAgentBase initialization (handles init_api_key internally)
        super().__init__(
            agent_name=agent_name,
            description=description,
            instructions=instructions,
            quality_config={"domain": quality_domain.lower()},  # Framework V2.0 quality config
            mcp_tools_enabled=True,
            a2a_enabled=True
        )
        
        logger.info(f'Init {self.agent_name} ({domain_name})')
        
        # Domain-specific attributes
        self.port = port
        self.port_ranges = port_ranges
        self.domain_name = domain_name
        self.quality_domain = quality_domain
        self.tier = self._determine_tier(port) if port else 0
        
        # StandardizedAgentBase handles: agent, tools, mcp_enabled, etc.
        
    def _determine_tier(self, port: int) -> int:
        """Determine agent tier based on configurable port ranges."""
        if not port:
            return 0
            
        for tier_name, (min_port, max_port) in self.port_ranges.items():
            if min_port <= port <= max_port:
                return int(tier_name.split('_')[1])
        
        return 0  # Unknown tier
        
    async def _execute_agent_logic(self, query: str, context_id: str, task_id: str):
        """
        Implement Framework V2.0 required abstract method.
        Uses inherited StandardizedAgentBase agent for processing.
        """
        logger.info(f'{self.domain_name} agent executing logic for: {query}')
        
        # Use inherited agent from StandardizedAgentBase
        if not self.agent:
            await self.init_agent()  # Framework V2.0 initialization
        
        if not self.agent:
            return {
                "error": "Agent initialization failed", 
                "content": f"Fallback response for: {query}"
            }
        
        # Simple delegation to inherited ADK agent
        try:
            from a2a_mcp.common.agent_runner import AgentRunner
            if not hasattr(self, 'runner') or not self.runner:
                self.runner = AgentRunner()
            
            result = ""
            async for chunk in self.runner.run_stream(self.agent, query, context_id):
                if isinstance(chunk, dict) and chunk.get('type') == 'final_result':
                    result = chunk['response']
                    break
            
            return {"content": result}
            
        except Exception as e:
            logger.error(f'{self.domain_name} execution error: {e}')
            return {"error": str(e), "content": f"Error processing: {query}"}
        
    async def invoke(self, query, session_id) -> dict:
        """Legacy invoke method - recommends streaming."""
        logger.info(f'Running {self.agent_name} for session {session_id}')
        raise NotImplementedError('Please use the streaming function')
                
    def format_response(self, chunk: str) -> Any:
        """
        Response formatting with configurable patterns.
        Domains can override this method to add domain-specific formatting.
        """
        # Default patterns - domains can extend this list
        patterns = [
            r'```\\n(.*?)\\n```',
            r'```json\\s*(.*?)\\s*```',
            r'```tool_outputs\\s*(.*?)\\s*```',
        ]

        for pattern in patterns:
            match = re.search(pattern, chunk, re.DOTALL)
            if match:
                content = match.group(1)
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return content
        return chunk

    async def health_check(self) -> Dict[str, Any]:
        """Enhanced health check with domain and tier information."""
        base_health = super().get_health_status()  # Framework V2.0 health check
        return {
            **base_health,
            "domain": self.domain_name,
            "quality_domain": self.quality_domain,
            "tier": getattr(self, 'tier', 0),
            "port": getattr(self, 'port', None),
            "port_ranges": getattr(self, 'port_ranges', {})
        }

    def get_agent_response(self, chunk: Any) -> Dict[str, Any]:
        """
        Agent response handling with Framework V2.0 compliance.
        Provides sophisticated response processing with domain awareness.
        """
        logger.info(f'{self.domain_name} Response Type {type(chunk)}')
        
        # Use StandardizedAgentBase initialization status
        if not self.initialization_complete:
            return {
                'response_type': 'text',
                'is_task_complete': True,
                'require_user_input': False,
                'content': f"Fallback response for: {chunk} (Framework V2.0 {self.domain_name} agent unavailable)"
            }
        
        data = self.format_response(chunk)
        logger.info(f'{self.domain_name} Formatted Response {data}')
        
        try:
            if isinstance(data, dict):
                if 'status' in data and data['status'] == 'input_required':
                    return {
                        'response_type': 'text',
                        'is_task_complete': False,
                        'require_user_input': True,
                        'content': data['question'],
                    }
                else:
                    return {
                        'response_type': 'data',
                        'is_task_complete': True,
                        'require_user_input': False,
                        'content': data,
                    }
            else:
                return_type = 'data'
                try:
                    data = json.loads(data)
                    return_type = 'data'
                except Exception as json_e:
                    logger.error(f'{self.domain_name} Json conversion error {json_e}')
                    return_type = 'text'
                return {
                    'response_type': return_type,
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': data,
                }
        except Exception as e:
            logger.error(f'{self.domain_name} Error in get_agent_response: {e}')
            return {
                'response_type': 'text',
                'is_task_complete': True,
                'require_user_input': False,
                'content': 'Could not complete task. Please try again.',
            }
    
    def get_domain_config(self) -> Dict[str, Any]:
        """Get domain-specific configuration information."""
        return {
            "domain_name": self.domain_name,
            "quality_domain": self.quality_domain,
            "tier": self.tier,
            "port": self.port,
            "port_ranges": self.port_ranges,
            "framework_version": "2.0"
        }
    
    def create_domain_a2a_request(self, method: str, message: str, metadata: dict = None) -> Dict[str, Any]:
        """Create A2A request with domain-specific metadata."""
        domain_metadata = {
            "domain": self.domain_name,
            "tier": self.tier,
            "port": self.port
        }
        
        if metadata:
            domain_metadata.update(metadata)
            
        return create_a2a_request(method, message, domain_metadata)


# Example domain-specific implementation
class ExampleDomainAgent(GenericDomainAgent):
    """
    Example of how to create domain-specific agents using GenericDomainAgent.
    Domains should create similar classes customized for their needs.
    """
    
    def __init__(self, agent_name: str, description: str, instructions: str, port: int = None):
        super().__init__(
            agent_name=agent_name,
            description=description,
            instructions=instructions,
            port=port,
            port_ranges={
                "tier_1": (12001, 12001),  # Example domain uses 12xxx ports
                "tier_2": (12002, 12006),
                "tier_3": (12010, 12059)
            },
            quality_domain="TECHNICAL",
            domain_name="Example",
            required_env_vars=['GOOGLE_API_KEY']  # Add domain-specific env vars
        )
    
    def format_response(self, chunk: str) -> Any:
        """Override with domain-specific response formatting."""
        # Add domain-specific patterns
        domain_patterns = [
            r'```example\\s*(.*?)\\s*```',  # Domain-specific code blocks
            r'\\[EXAMPLE\\](.*?)\\[/EXAMPLE\\]',  # Domain-specific tags
        ]
        
        # Try domain patterns first
        for pattern in domain_patterns:
            match = re.search(pattern, chunk, re.DOTALL)
            if match:
                content = match.group(1).strip()
                return {"type": "example_output", "content": content}
        
        # Fall back to parent formatting
        return super().format_response(chunk)
    
    async def _execute_agent_logic(self, query: str, context_id: str, task_id: str):
        """Domain-specific logic can be added here."""
        # Pre-processing
        logger.info(f"Example domain processing: {query}")
        
        # Call parent logic
        result = await super()._execute_agent_logic(query, context_id, task_id)
        
        # Post-processing
        if isinstance(result, dict) and "content" in result:
            result["domain_processed"] = True
            result["domain"] = self.domain_name
        
        return result


if __name__ == "__main__":
    # Example usage
    import asyncio
    
    async def test_generic_domain_agent():
        """Test the generic domain agent."""
        agent = ExampleDomainAgent(
            agent_name="Test Example Agent",
            description="Test agent for example domain",
            instructions="You are a test agent for the example domain.",
            port=12010
        )
        
        print(f"Agent: {agent.agent_name}")
        print(f"Domain: {agent.domain_name}")
        print(f"Tier: {agent.tier}")
        print(f"Quality Domain: {agent.quality_domain}")
        
        # Test health check
        health = await agent.health_check()
        print(f"Health: {health}")
        
        # Test domain config
        config = agent.get_domain_config()
        print(f"Config: {config}")
    
    # Run test
    asyncio.run(test_generic_domain_agent())