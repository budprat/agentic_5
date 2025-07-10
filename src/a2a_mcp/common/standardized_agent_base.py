# ABOUTME: Standardized base agent implementation using Google ADK + MCPToolset pattern
# ABOUTME: Provides unified agent architecture following best practices from travel/nexus agent analysis

import logging
import asyncio
import json
from abc import ABC, abstractmethod
from collections.abc import AsyncIterable
from typing import Dict, Any, Optional, List
from datetime import datetime

from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import get_mcp_server_config, init_api_key
from a2a_mcp.common.quality_framework import QualityThresholdFramework
from a2a_mcp.common.a2a_protocol import A2AProtocolClient
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from google.genai import types as genai_types

logger = logging.getLogger(__name__)


class StandardizedAgentBase(BaseAgent, ABC):
    """
    Standardized base agent implementation following Google ADK + MCPToolset pattern.
    
    This class provides:
    - Google ADK framework integration
    - MCP tool loading via MCPToolset
    - A2A communication protocol support
    - Configurable quality threshold framework
    - Unified error handling and fallback mechanisms
    """

    def __init__(
        self,
        agent_name: str,
        description: str,
        instructions: str,
        quality_config: Optional[Dict[str, Any]] = None,
        mcp_tools_enabled: bool = True,
        a2a_enabled: bool = True
    ):
        """
        Initialize standardized agent with unified configuration.
        
        Args:
            agent_name: Human-readable agent name
            description: Agent description for discovery
            instructions: System instructions for the agent
            quality_config: Quality threshold configuration
            mcp_tools_enabled: Whether to load MCP tools
            a2a_enabled: Whether to enable A2A communication
        """
        init_api_key()
        
        super().__init__(
            agent_name=agent_name,
            description=description,
            content_types=['text', 'text/plain', 'application/json'],
        )
        
        self.instructions = instructions
        self.agent = None
        self.tools = []
        self.quality_framework = QualityThresholdFramework(quality_config or {})
        self.a2a_client = A2AProtocolClient() if a2a_enabled else None
        self.mcp_tools_enabled = mcp_tools_enabled
        
        # Agent state management
        self.context_id = None
        self.session_state = {}
        self.initialization_complete = False

    async def init_agent(self):
        """Initialize Google ADK agent with MCP tools following standardized pattern."""
        if self.initialization_complete:
            return
            
        logger.info(f'Initializing standardized agent: {self.agent_name}')
        
        try:
            # Load MCP tools if enabled
            if self.mcp_tools_enabled:
                config = get_mcp_server_config()
                logger.info(f'Loading MCP tools from server: {config.url}')
                
                self.tools = await MCPToolset(
                    connection_params=SseServerParams(url=config.url)
                ).get_tools()
                
                logger.info(f'Loaded {len(self.tools)} MCP tools')
                for tool in self.tools:
                    logger.debug(f'Available tool: {tool.name}')
            else:
                logger.info('MCP tools disabled, using agent without external tools')
                self.tools = []

            # Configure generation settings
            generate_content_config = genai_types.GenerateContentConfig(
                temperature=self.get_agent_temperature(),
                response_mime_type=self.get_response_mime_type()
            )
            
            # Initialize Google ADK agent
            self.agent = Agent(
                name=self.agent_name,
                instruction=self.instructions,
                model=self.get_model_name(),
                disallow_transfer_to_parent=True,
                disallow_transfer_to_peers=True,
                generate_content_config=generate_content_config,
                tools=self.tools,
            )
            
            self.initialization_complete = True
            logger.info(f'Standardized agent {self.agent_name} initialized successfully')
            
        except Exception as e:
            logger.error(f'Failed to initialize agent {self.agent_name}: {e}')
            await self._handle_initialization_failure(e)

    async def _handle_initialization_failure(self, error: Exception):
        """Handle agent initialization failure with graceful degradation."""
        logger.warning(f'Agent initialization failed, attempting fallback mode: {error}')
        
        # Try without MCP tools
        if self.mcp_tools_enabled:
            logger.info('Retrying initialization without MCP tools')
            self.mcp_tools_enabled = False
            self.tools = []
            await self.init_agent()
            return
        
        # If still failing, create minimal agent
        try:
            generate_content_config = genai_types.GenerateContentConfig(
                temperature=0.7,
                response_mime_type="text/plain"
            )
            
            self.agent = Agent(
                name=self.agent_name,
                instruction=f"You are {self.agent_name}. Provide helpful responses based on your knowledge.",
                model='gemini-2.0-flash',
                generate_content_config=generate_content_config,
                tools=[],
            )
            
            self.initialization_complete = True
            logger.warning(f'Agent {self.agent_name} initialized in minimal fallback mode')
            
        except Exception as fallback_error:
            logger.error(f'Complete initialization failure for {self.agent_name}: {fallback_error}')
            raise fallback_error

    async def stream(
        self, query: str, context_id: str, task_id: str
    ) -> AsyncIterable[Dict[str, Any]]:
        """Standardized streaming implementation with quality validation."""
        logger.info(f'{self.agent_name} processing query: {query[:100]}... (session: {context_id})')
        
        if not query:
            raise ValueError("Query cannot be empty")
        
        # Initialize agent if needed
        if not self.agent:
            await self.init_agent()
        
        # Manage session state
        if self.context_id != context_id:
            await self._reset_session_state(context_id)
        
        try:
            # Pre-processing phase
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": f"{self.agent_name}: Processing request..."
            }
            
            # Execute agent-specific processing
            async for response_chunk in self._execute_agent_logic(query, context_id, task_id):
                # Apply quality validation if this is a final response
                if response_chunk.get("is_task_complete", False):
                    response_chunk = await self._apply_quality_validation(response_chunk, query)
                
                yield response_chunk
                
        except Exception as e:
            logger.error(f'{self.agent_name} execution error: {e}')
            yield await self._create_error_response(str(e))

    @abstractmethod
    async def _execute_agent_logic(
        self, query: str, context_id: str, task_id: str
    ) -> AsyncIterable[Dict[str, Any]]:
        """
        Execute agent-specific logic. Must be implemented by subclasses.
        
        This method should contain the core agent logic and yield response chunks
        following the standardized response format.
        """
        pass

    async def _apply_quality_validation(
        self, response: Dict[str, Any], original_query: str
    ) -> Dict[str, Any]:
        """Apply quality threshold validation to final responses."""
        try:
            if not self.quality_framework.is_enabled():
                return response
            
            # Extract response content for validation
            content = response.get("content", {})
            
            # Apply quality checks
            quality_result = await self.quality_framework.validate_response(
                content, original_query
            )
            
            # Add quality metadata to response
            if quality_result.get("quality_approved", True):
                logger.info(f'Quality validation passed for {self.agent_name}')
            else:
                logger.warning(f'Quality issues detected: {quality_result.get("quality_issues", [])}')
                # Add quality warning to response
                if isinstance(content, dict):
                    content["quality_warning"] = f"Quality threshold validation: {', '.join(quality_result.get('quality_issues', []))}"
                
            response["quality_metadata"] = quality_result
            return response
            
        except Exception as e:
            logger.error(f'Quality validation error: {e}')
            return response

    async def _reset_session_state(self, new_context_id: str):
        """Reset session state for new context."""
        self.context_id = new_context_id
        self.session_state.clear()
        logger.debug(f'Session state reset for context: {new_context_id}')

    async def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "is_task_complete": True,
            "require_user_input": False,
            "response_type": "error",
            "content": f"{self.agent_name}: {error_message}",
            "error_details": {
                "agent": self.agent_name,
                "timestamp": datetime.now().isoformat(),
                "error": error_message
            }
        }

    async def invoke(self, query: str, session_id: str) -> dict:
        """Non-streaming invocation (not recommended, use streaming)."""
        logger.warning(f'{self.agent_name} non-streaming invoke called - recommend using stream()')
        raise NotImplementedError("Use streaming function for standardized agents")

    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status for the agent."""
        return {
            "agent_name": self.agent_name,
            "initialization_complete": self.initialization_complete,
            "mcp_tools_enabled": self.mcp_tools_enabled,
            "mcp_tools_loaded": len(self.tools),
            "a2a_enabled": self.a2a_client is not None,
            "quality_framework_enabled": self.quality_framework.is_enabled(),
            "last_context_id": self.context_id,
            "timestamp": datetime.now().isoformat()
        }

    # Configurable methods for subclass customization
    
    def get_agent_temperature(self) -> float:
        """Get temperature setting for the agent. Override in subclasses."""
        return 0.1

    def get_response_mime_type(self) -> str:
        """Get response MIME type. Override in subclasses."""
        return "application/json"

    def get_model_name(self) -> str:
        """Get model name. Override in subclasses."""
        return 'gemini-2.0-flash'

    async def communicate_with_agent(
        self, target_agent_port: int, message: str, metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Communicate with another agent using A2A protocol.
        
        Args:
            target_agent_port: Port number of target agent
            message: Message to send
            metadata: Optional metadata
            
        Returns:
            Response from target agent
        """
        if not self.a2a_client:
            raise RuntimeError("A2A communication not enabled for this agent")
        
        return await self.a2a_client.send_message(
            target_agent_port, message, metadata or {}
        )