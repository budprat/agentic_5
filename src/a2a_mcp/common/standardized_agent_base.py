# ABOUTME: Standardized base agent implementation using Google ADK + MCPToolset pattern
# ABOUTME: Provides unified agent architecture for building robust, quality-aware agents

import logging
import asyncio
import json
import os
import re
from abc import ABC, abstractmethod
from collections.abc import AsyncIterable
from typing import Dict, Any, Optional, List
from datetime import datetime

from .base_agent import BaseAgent
from .utils import get_mcp_server_config
from .quality_framework import QualityThresholdFramework
from .a2a_protocol import A2AProtocolClient
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams
from google.genai import types as genai_types

logger = logging.getLogger(__name__)


class StandardizedAgentBase(BaseAgent, ABC):
    """
    Standardized base agent implementation following Google ADK + MCPToolset pattern.
    
    This class provides a robust foundation for building agents with:
    - Google ADK framework integration for powerful LLM capabilities
    - MCP (Model Context Protocol) tool loading via MCPToolset
    - A2A (Agent-to-Agent) communication protocol support
    - Configurable quality threshold framework for response validation
    - Unified error handling and graceful fallback mechanisms
    - Session state management and context tracking
    
    Extend this class to create domain-specific agents with consistent
    architecture and best practices built-in.
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
            agent_name: Human-readable agent name for identification
            description: Agent description for discovery and documentation
            instructions: System instructions defining agent behavior
            quality_config: Quality threshold configuration for response validation
            mcp_tools_enabled: Whether to load and use MCP tools
            a2a_enabled: Whether to enable agent-to-agent communication
        """
        # Initialize API key if needed (handled by deployment)
        
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
                    connection_params=SseConnectionParams(url=config.url)
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
                model=os.getenv('GEMINI_MODEL', 'gemini-2.0-flash'),
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
        """Standardized streaming implementation with enhanced response intelligence."""
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
                # Enhanced response processing with intelligence
                if response_chunk.get("is_task_complete", False):
                    # Apply intelligent response formatting
                    content = response_chunk.get("content")
                    if content:
                        # Format the response content
                        formatted_content = self.format_response(content)
                        
                        # Detect interactive mode
                        is_interactive = self.detect_interactive_mode(formatted_content)
                        
                        # Standardize response format
                        response_chunk = self.standardize_response_format(
                            formatted_content, 
                            is_interactive=is_interactive,
                            is_complete=not is_interactive
                        )
                    
                    # Apply quality validation for completed tasks
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
        
        Args:
            query: User input or request
            context_id: Session context identifier
            task_id: Unique task identifier
            
        Yields:
            Response chunks with standardized format
        """
        pass

    def format_response(self, chunk: Any) -> Any:
        """Format and parse agent response with intelligent content detection.
        
        Enhanced with response intelligence from ADKServiceAgent pattern.
        Handles multiple output formats from LLMs.
        
        Args:
            chunk: Raw response from agent
            
        Returns:
            Parsed response (dict, string, or original chunk)
        """
        if not isinstance(chunk, str):
            return chunk
            
        # Patterns for extracting structured content
        patterns = [
            r'```\n(.*?)\n```',              # Code blocks
            r'```json\s*(.*?)\s*```',        # JSON blocks
            r'```tool_outputs\s*(.*?)\s*```', # Tool output blocks
        ]

        for pattern in patterns:
            match = re.search(pattern, chunk, re.DOTALL)
            if match:
                content = match.group(1)
                try:
                    # Try to parse as JSON
                    return json.loads(content)
                except json.JSONDecodeError:
                    # Return as string if not valid JSON
                    return content
                    
        # Return original chunk if no patterns match
        return chunk

    def detect_interactive_mode(self, content: Any) -> bool:
        """Detect if response requires user interaction.
        
        Enhanced interactive mode detection from ADKServiceAgent pattern.
        
        Args:
            content: Response content to analyze
            
        Returns:
            True if user input is required
        """
        if isinstance(content, dict):
            # Check for explicit interactive mode signals
            if content.get('status') == 'input_required':
                return True
            if content.get('require_user_input', False):
                return True
            # Check for question patterns
            if 'question' in content and content.get('question'):
                return True
        
        if isinstance(content, str):
            # Look for question patterns in text
            question_indicators = ['?', 'please provide', 'what is', 'which', 'how', 'when', 'where']
            content_lower = content.lower()
            return any(indicator in content_lower for indicator in question_indicators)
        
        return False

    def standardize_response_format(
        self, content: Any, is_interactive: bool = False, is_complete: bool = True
    ) -> Dict[str, Any]:
        """Standardize response format across all agent types.
        
        Enhanced with ADKServiceAgent response standardization patterns.
        
        Args:
            content: Response content
            is_interactive: Whether response requires user input
            is_complete: Whether task is complete
            
        Returns:
            Standardized response format
        """
        try:
            if is_interactive:
                # Interactive mode - requires user input
                question = content.get('question', str(content)) if isinstance(content, dict) else str(content)
                return {
                    'response_type': 'interactive',
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': question,
                }
            
            # Determine response type
            response_type = 'text'
            if isinstance(content, dict):
                response_type = 'data'
            elif isinstance(content, str):
                try:
                    # Try to parse as JSON
                    json.loads(content)
                    response_type = 'data'
                except json.JSONDecodeError:
                    response_type = 'text'
            
            return {
                'response_type': response_type,
                'is_task_complete': is_complete,
                'require_user_input': False,
                'content': content,
            }
                
        except Exception as e:
            logger.error(f'Error in standardize_response_format: {e}')
            return {
                'response_type': 'text',
                'is_task_complete': True,
                'require_user_input': False,
                'content': 'Response formatting error occurred.',
                'error_details': {
                    'agent': self.agent_name,
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e)
                }
            }

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
        """Get comprehensive health status for the agent.
        
        Enhanced with dependency health monitoring from ADKServiceAgent pattern.
        """
        # Check dependencies health
        dependencies_healthy = True
        dependency_details = {}
        
        # Check initialization
        if not self.initialization_complete:
            dependencies_healthy = False
            dependency_details["initialization"] = "incomplete"
        else:
            dependency_details["initialization"] = "complete"
        
        # Check ADK agent
        if not self.agent:
            dependencies_healthy = False
            dependency_details["adk_agent"] = "not_initialized"
        else:
            dependency_details["adk_agent"] = "active"
        
        # Check MCP tools
        if self.mcp_tools_enabled:
            if len(self.tools) > 0:
                dependency_details["mcp_tools"] = f"loaded_{len(self.tools)}_tools"
            else:
                dependencies_healthy = False
                dependency_details["mcp_tools"] = "no_tools_loaded"
        else:
            dependency_details["mcp_tools"] = "disabled"
        
        # Check A2A protocol
        if self.a2a_client:
            dependency_details["a2a_protocol"] = "enabled"
        else:
            dependency_details["a2a_protocol"] = "disabled"
        
        # Check quality framework
        dependency_details["quality_framework"] = "enabled" if self.quality_framework.is_enabled() else "disabled"
        
        return {
            "agent_name": self.agent_name,
            "framework_version": "2.0",
            "initialization_complete": self.initialization_complete,
            "dependencies_healthy": dependencies_healthy,
            "dependency_details": dependency_details,
            "last_context_id": self.context_id,
            "timestamp": datetime.now().isoformat(),
            "capabilities": {
                "a2a_communication": self.a2a_client is not None,
                "quality_validation": self.quality_framework.is_enabled(),
                "mcp_tools": len(self.tools) > 0,
                "streaming_responses": True,
                "interactive_mode": True,
                "response_intelligence": True
            }
        }

    # Configurable methods for subclass customization
    
    def get_agent_temperature(self) -> float:
        """
        Get temperature setting for the agent. Override in subclasses.
        
        Lower values (0.0-0.3) for more deterministic outputs
        Higher values (0.7-1.0) for more creative outputs
        """
        return 0.1

    def get_response_mime_type(self) -> str:
        """
        Get response MIME type. Override in subclasses.
        
        Common options:
        - "application/json" for structured data
        - "text/plain" for simple text
        - "text/markdown" for formatted text
        """
        return "application/json"

    def get_model_name(self) -> str:
        """
        Get model name. Override in subclasses.
        
        Examples:
        - "gemini-2.0-flash" for fast responses
        - "gemini-1.5-pro" for complex reasoning
        """
        return os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')

    async def communicate_with_agent(
        self, target_agent_port: int, message: str, metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Communicate with another agent using A2A protocol.
        
        This enables agents to collaborate and share information
        for complex multi-agent workflows.
        
        Args:
            target_agent_port: Port number of target agent
            message: Message to send
            metadata: Optional metadata for routing or context
            
        Returns:
            Response from target agent
            
        Raises:
            RuntimeError: If A2A communication is not enabled
        """
        if not self.a2a_client:
            raise RuntimeError("A2A communication not enabled for this agent")
        
        return await self.a2a_client.send_message(
            target_agent_port, message, metadata or {}
        )