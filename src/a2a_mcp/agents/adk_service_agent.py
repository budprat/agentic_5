# type: ignore

import json
import logging
import os
import re

from collections.abc import AsyncIterable
from typing import Any, Dict, List, Optional
from datetime import datetime

from a2a_mcp.common.agent_runner import AgentRunner
from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import get_mcp_server_config, init_api_key
from a2a_mcp.common.a2a_protocol import A2AProtocolClient
from a2a_mcp.common.quality_framework import QualityThresholdFramework, QualityDomain
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from google.genai import types as genai_types


logger = logging.getLogger(__name__)


class ADKServiceAgent(BaseAgent):
    """Framework V2.0 Universal Service Agent Template.
    
    The production-ready universal template for ALL service agents in Framework V2.0.
    Provides Google ADK integration, MCP tool support, and A2A protocol communication
    in a single, domain-agnostic class.
    
    Key Framework V2.0 Features:
    - Google ADK agent integration with streaming support
    - Automatic MCP tool discovery and loading
    - A2A protocol for inter-agent communication
    - Universal domain adaptation via configuration
    - Production-ready error handling and logging
    
    Example usage:
        # Travel domain service agent
        travel_agent = ADKServiceAgent(
            agent_name='AirTicketingAgent',
            description='Book air tickets given criteria',
            instructions=travel_prompts.AIRFARE_COT_INSTRUCTIONS,
            a2a_enabled=True  # Enable communication with other agents
        )
        
        # Finance domain service agent
        finance_agent = ADKServiceAgent(
            agent_name='TradingAgent',
            description='Execute trading strategies',
            instructions=finance_prompts.TRADING_INSTRUCTIONS,
            a2a_enabled=True  # Can coordinate with finance specialists
        )
        
        # Healthcare domain service agent
        healthcare_agent = ADKServiceAgent(
            agent_name='PatientCareAgent',
            description='Coordinate patient care workflows',
            instructions='You are a patient care coordination specialist...',
            a2a_enabled=True  # Can communicate with medical specialists
        )
        
        # Multi-agent communication example
        response = await finance_agent.communicate_with_agent(
            target_agent_port=11001,
            message="Analyze market volatility for portfolio optimization",
            metadata={"domain": "finance", "priority": "high"}
        )
    """

    def __init__(
        self, 
        agent_name: str, 
        description: str, 
        instructions: str,
        content_types: Optional[List[str]] = None,
        temperature: float = 0.0,
        a2a_enabled: bool = True,
        quality_config: Optional[Dict[str, Any]] = None,
        quality_domain: QualityDomain = QualityDomain.SERVICE
    ):
        """Initialize ADK service agent.
        
        Args:
            agent_name: Name of the agent (e.g., 'CustomerSupportAgent')
            description: Description of agent capabilities
            instructions: Domain-specific instructions for the agent
            content_types: Supported content types (defaults to text)
            temperature: LLM temperature for response generation
            a2a_enabled: Enable A2A protocol for inter-agent communication
            quality_config: Quality threshold configuration for response validation
            quality_domain: Quality validation domain type (SERVICE, BUSINESS, ACADEMIC)
        """
        init_api_key()

        super().__init__(
            agent_name=agent_name,
            description=description,
            content_types=content_types or ['text', 'text/plain'],
        )

        logger.info(f'Initializing {self.agent_name}')

        self.instructions = instructions
        self.temperature = temperature
        self.agent = None
        self.runner = None
        
        # Framework V2.0: Quality Framework Integration
        if not quality_config:
            quality_config = {
                "domain": quality_domain,
                "thresholds": self._get_default_quality_thresholds(quality_domain)
            }
        self.quality_framework = QualityThresholdFramework(quality_config)
        
        # Framework V2.0: A2A Protocol Support
        self.a2a_client = A2AProtocolClient() if a2a_enabled else None
        
        # Agent state management
        self.context_id = None
        self.session_state = {}
        self.initialization_complete = False
        self.last_successful_operation = None
        
        if a2a_enabled:
            logger.info(f'{self.agent_name}: A2A protocol enabled')
        else:
            logger.info(f'{self.agent_name}: A2A protocol disabled')
        
        logger.info(f'{self.agent_name}: Quality framework enabled for {quality_domain.value} domain')

    async def init_agent(self):
        """Initialize the ADK agent with MCP tools.
        
        This method demonstrates the production pattern for:
        - MCP tool discovery and loading
        - ADK agent configuration
        - Agent runner setup
        """
        logger.info(f'Initializing {self.agent_name} with ADK and MCP tools')
        
        # Get MCP server configuration
        config = get_mcp_server_config()
        logger.info(f'MCP Server url={config.url}')
        
        # Load MCP tools dynamically
        tools = await MCPToolset(
            connection_params=SseServerParams(url=config.url)
        ).get_tools()

        # Log loaded tools for debugging
        for tool in tools:
            logger.info(f'Loaded MCP tool: {tool.name}')
            
        # Configure ADK agent
        generate_content_config = genai_types.GenerateContentConfig(
            temperature=self.temperature
        )
        
        self.agent = Agent(
            name=self.agent_name,
            instruction=self.instructions,
            model=os.getenv('GEMINI_MODEL', 'gemini-2.0-flash'),
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            generate_content_config=generate_content_config,
            tools=tools,  # MCP tools integrated into ADK agent
        )
        
        # Initialize agent runner for A2A protocol
        self.runner = AgentRunner()
        logger.info(f'{self.agent_name} initialization complete')

    async def invoke(self, query, session_id) -> dict:
        """Legacy invoke method - use stream() instead."""
        logger.info(f'Running {self.agent_name} for session {session_id}')
        raise NotImplementedError('Please use the streaming function')

    async def stream(
        self, query, context_id, task_id
    ) -> AsyncIterable[Dict[str, Any]]:
        """Execute agent query with streaming response.
        
        This method demonstrates the production pattern for:
        - Input validation
        - Lazy agent initialization  
        - Streaming response handling
        - Error management
        
        Args:
            query: User query or task description
            context_id: Session context identifier
            task_id: Task identifier for tracking
            
        Yields:
            Dict containing response chunks with metadata
        """
        logger.info(
            f'Running {self.agent_name} stream for session {context_id}, task {task_id} - {query}'
        )

        # Input validation
        if not query:
            raise ValueError('Query cannot be empty')

        # Lazy initialization of ADK agent
        if not self.agent:
            await self.init_agent()
        
        # Manage session state
        if self.context_id != context_id:
            await self._reset_session_state(context_id)
            
        # Stream execution via agent runner
        async for chunk in self.runner.run_stream(
            self.agent, query, context_id
        ):
            logger.info(f'Received chunk: {chunk}')
            
            if isinstance(chunk, dict) and chunk.get('type') == 'final_result':
                # Final result - format and yield with quality validation
                response = chunk['response']
                yield await self.get_agent_response(response, query)
            else:
                # Intermediate progress update
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': f'{self.agent_name}: Processing request...',
                }

    async def _reset_session_state(self, new_context_id: str):
        """Reset session state for new context."""
        self.context_id = new_context_id
        self.session_state.clear()
        logger.debug(f'{self.agent_name}: Session state reset for context: {new_context_id}')

    def format_response(self, chunk):
        """Format and parse agent response.
        
        This method demonstrates intelligent response processing that can
        handle multiple output formats from the LLM.
        
        Args:
            chunk: Raw response from ADK agent
            
        Returns:
            Parsed response (dict, string, or original chunk)
        """
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

    def get_agent_response(self, chunk):
        """Convert agent output to standardized A2A response format.
        
        This method demonstrates the production pattern for response
        standardization across different agent types.
        
        Args:
            chunk: Formatted response from format_response()
            
        Returns:
            Dict with standardized A2A response format
        """
        logger.info(f'Processing response type: {type(chunk)}')
        
        try:
            # Format the response content
            data = self.format_response(chunk)
            logger.info(f'Formatted response: {data}')
            
            # Detect interactive mode
            is_interactive = ResponseFormatter.detect_interactive_mode(data)
            
            # Create standardized response using ResponseFormatter
            response = ResponseFormatter.standardize_response_format(
                content=data,
                is_interactive=is_interactive,
                is_complete=not is_interactive,
                agent_name=self.agent_name
            )
            
            # Apply quality validation if enabled and task is complete
            if response.get('is_task_complete', False) and self.quality_framework.is_enabled():
                # Note: Original query not available in this method signature
                # Quality validation could be enhanced by passing query through stream method
                quality_result = self.quality_framework.validate_response_sync(
                    response.get('content', {}), ""
                )
                response['quality_metadata'] = quality_result
            
            # Update last successful operation timestamp
            self.last_successful_operation = datetime.now().isoformat()
            
            return response
                
        except Exception as e:
            # Error handling with graceful degradation
            logger.error(f'Error in get_agent_response: {e}')
            return create_agent_error(
                error_message='Could not complete the requested task. Please try again.',
                agent_name=self.agent_name,
                error_type='processing',
                context={'error': str(e)}
            )
    
    async def communicate_with_agent(
        self, target_agent_port: int, message: str, metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Communicate with another agent using A2A protocol.
        
        Framework V2.0 feature: Enables universal agent-to-agent communication
        for building sophisticated multi-agent workflows.
        
        Args:
            target_agent_port: Port number of target agent
            message: Message to send to target agent
            metadata: Optional metadata for routing or context
            
        Returns:
            Response from target agent
            
        Raises:
            RuntimeError: If A2A communication is not enabled
            
        Example:
            # Service agent communicating with specialist
            response = await service_agent.communicate_with_agent(
                target_agent_port=11001,
                message="Analyze market trends for Q4",
                metadata={"domain": "finance", "urgency": "high"}
            )
        """
        if not self.a2a_client:
            raise RuntimeError(
                f"A2A communication not enabled for {self.agent_name}. "
                "Initialize with a2a_enabled=True to enable inter-agent communication."
            )
        
        logger.info(
            f'{self.agent_name}: Sending A2A message to port {target_agent_port}'
        )
        
        try:
            response = await self.a2a_client.send_message(
                target_agent_port, message, metadata or {}
            )
            logger.info(
                f'{self.agent_name}: Received A2A response from port {target_agent_port}'
            )
            return response
        except Exception as e:
            logger.error(
                f'{self.agent_name}: A2A communication failed with port {target_agent_port}: {e}'
            )
            raise
    
    def get_a2a_status(self) -> Dict[str, Any]:
        """Get A2A protocol status for this agent.
        
        Returns:
            Dict containing A2A configuration and status information
        """
        return {
            "agent_name": self.agent_name,
            "a2a_enabled": self.a2a_client is not None,
            "a2a_client_status": "active" if self.a2a_client else "disabled",
            "communication_capability": "full" if self.a2a_client else "none",
            "framework_version": "2.0"
        }