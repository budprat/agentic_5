# type: ignore

import json
import logging
import os
import re

from collections.abc import AsyncIterable
from typing import Any, Dict, List, Optional

from a2a_mcp.common.agent_runner import AgentRunner
from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import get_mcp_server_config, init_api_key
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from google.genai import types as genai_types


logger = logging.getLogger(__name__)


class ADKServiceAgent(BaseAgent):
    """Generic ADK-powered service agent for any domain.
    
    This class demonstrates the production-ready pattern for integrating
    Google ADK with A2A-MCP framework. It can be configured for any business
    domain through the parameters.
    
    Example usage:
        # Travel domain
        travel_agent = ADKServiceAgent(
            agent_name='AirTicketingAgent',
            description='Book air tickets given criteria',
            instructions=travel_prompts.AIRFARE_COT_INSTRUCTIONS
        )
        
        # Finance domain  
        finance_agent = ADKServiceAgent(
            agent_name='TradingAgent',
            description='Execute trading strategies',
            instructions=finance_prompts.TRADING_INSTRUCTIONS
        )
        
        # Any domain
        custom_agent = ADKServiceAgent(
            agent_name='CustomAgent',
            description='Handle domain-specific tasks',
            instructions='Your specialized instructions here...'
        )
    """

    def __init__(
        self, 
        agent_name: str, 
        description: str, 
        instructions: str,
        content_types: Optional[List[str]] = None,
        temperature: float = 0.0
    ):
        """Initialize ADK service agent.
        
        Args:
            agent_name: Name of the agent (e.g., 'CustomerSupportAgent')
            description: Description of agent capabilities
            instructions: Domain-specific instructions for the agent
            content_types: Supported content types (defaults to text)
            temperature: LLM temperature for response generation
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
            
        # Stream execution via agent runner
        async for chunk in self.runner.run_stream(
            self.agent, query, context_id
        ):
            logger.info(f'Received chunk: {chunk}')
            
            if isinstance(chunk, dict) and chunk.get('type') == 'final_result':
                # Final result - format and yield
                response = chunk['response']
                yield self.get_agent_response(response)
            else:
                # Intermediate progress update
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': f'{self.agent_name}: Processing request...',
                }

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
            
            if isinstance(data, dict):
                # Handle structured responses
                if 'status' in data and data['status'] == 'input_required':
                    # Interactive mode - requires user input
                    return {
                        'response_type': 'text',
                        'is_task_complete': False,
                        'require_user_input': True,
                        'content': data['question'],
                    }
                else:
                    # Data mode - structured output
                    return {
                        'response_type': 'data',
                        'is_task_complete': True,
                        'require_user_input': False,
                        'content': data,
                    }
            else:
                # Handle text responses
                response_type = 'data'
                try:
                    # Try to parse text as JSON
                    data = json.loads(data)
                    response_type = 'data'
                except Exception as json_e:
                    logger.debug(f'JSON conversion failed: {json_e}')
                    response_type = 'text'
                    
                return {
                    'response_type': response_type,
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': data,
                }
                
        except Exception as e:
            # Error handling with graceful degradation
            logger.error(f'Error in get_agent_response: {e}')
            return {
                'response_type': 'text',
                'is_task_complete': True,
                'require_user_input': False,
                'content': 'Could not complete the requested task. Please try again.',
            }