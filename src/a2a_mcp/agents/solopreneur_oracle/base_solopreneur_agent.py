"""Base class for all solopreneur agents following Google ADK framework pattern."""

# type: ignore

import json
import logging
import os
import re
import uuid
from collections.abc import AsyncIterable
from typing import Any, Dict, Optional

from a2a_mcp.common.agent_runner import AgentRunner
from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import get_mcp_server_config, init_api_key
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams
from google.genai import types as genai_types

logger = logging.getLogger(__name__)

def validate_environment():
    """Validate required environment variables."""
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
    """Standardize A2A request format."""
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

class UnifiedSolopreneurAgent(BaseAgent):
    """
    Framework-compliant base class for all solopreneur agents.
    Uses Google ADK following the proven adk_nexus_agent.py and TravelAgent patterns.
    """
    
    def __init__(
        self, 
        agent_name: str, 
        description: str, 
        instructions: str,
        port: int = None
    ):
        # Validate environment first
        try:
            validate_environment()
        except ValueError as e:
            logger.error(f'Environment validation failed: {e}')
            raise
            
        init_api_key()
        super().__init__(
            agent_name=agent_name,
            description=description,
            content_types=['text', 'text/plain', 'application/json']
        )
        
        logger.info(f'Init {self.agent_name}')
        
        self.instructions = instructions
        self.port = port
        self.tier = self._determine_tier(port) if port else 0
        self.agent = None
        self.tools = []
        self.mcp_enabled = False
        self.google_adk_initialized = False
        
    def _determine_tier(self, port: int) -> int:
        """Determine agent tier based on port number."""
        if port == 10901:
            return 1  # Master Oracle
        elif 10902 <= port <= 10906:
            return 2  # Domain Specialists
        elif 10910 <= port <= 10959:
            return 3  # Intelligence Modules
        else:
            return 0  # Unknown
        
    async def init_agent(self):
        """Initialize with domain-specific MCP tools following ADK framework pattern."""
        logger.info(f'Initializing {self.agent_name} metadata')
        
        # Try to load MCP tools, but continue without them if unavailable
        self.tools = []
        if os.environ.get('DISABLE_MCP_TOOLS', 'false').lower() != 'true':
            try:
                config = get_mcp_server_config()
                logger.info(f'MCP Server url={config.url}')
                
                # Load MCP tools following ADK pattern from adk_travel_agent.py
                self.tools = await MCPToolset(
                    connection_params=SseConnectionParams(url=config.url)
                ).get_tools()
                
                for tool in self.tools:
                    logger.info(f'Loaded tools {tool.name}')
                self.mcp_enabled = True
                logger.info('MCP tools loaded successfully')
            except Exception as e:
                logger.warning(f'Could not connect to MCP server: {e}. Continuing without MCP tools.')
                self.mcp_enabled = False
        else:
            logger.info('MCP tools disabled by environment variable')
            self.mcp_enabled = False
            
        generate_content_config = genai_types.GenerateContentConfig(
            temperature=0.0
        )
        
        # Initialize Google ADK agent following adk_nexus_agent.py pattern with robust error handling
        try:
            # Convert agent name to valid identifier (replace spaces with underscores)
            valid_name = self.agent_name.replace(' ', '_').replace('-', '_')
            
            self.agent = Agent(
                name=valid_name,
                instruction=self.instructions,
                model='gemini-2.0-flash',
                disallow_transfer_to_parent=True,
                disallow_transfer_to_peers=True,
                generate_content_config=generate_content_config,
                tools=self.tools,
            )
            self.runner = AgentRunner()
            self.google_adk_initialized = True
            logger.info(f'Google ADK agent initialized successfully for {self.agent_name}')
        except Exception as e:
            logger.warning(f'Agent initialization failed: {e}. Using fallback mode.')
            self.agent = None
            self.runner = None
            self.google_adk_initialized = False
        
    async def invoke(self, query, session_id) -> dict:
        logger.info(f'Running {self.agent_name} for session {session_id}')
        raise NotImplementedError('Please use the streaming function')
        
    async def stream(
        self, query, context_id, task_id
    ) -> AsyncIterable[Dict[str, Any]]:
        """Stream implementation with graceful degradation."""
        logger.info(
            f'Running {self.agent_name} stream for session {context_id} {task_id} - {query}'
        )
        
        if not query:
            raise ValueError('Query cannot be empty')
        
        # Try to initialize agent if not already done
        if not self.agent:
            await self.init_agent()
        
        # Graceful degradation - if agent is not available, provide fallback response
        if not self.google_adk_initialized or not self.agent or not self.runner:
            logger.warning(f'Agent not fully initialized, providing fallback response')
            yield {
                'response_type': 'text',
                'is_task_complete': True,
                'require_user_input': False,
                'content': f"{self.agent_name} fallback response: {query} (Google ADK unavailable - MCP enabled: {self.mcp_enabled})"
            }
            return
            
        # Use established AgentRunner pattern from ADK
        try:
            async for chunk in self.runner.run_stream(
                self.agent, query, context_id
            ):
                logger.info(f'Received chunk {chunk}')
                if isinstance(chunk, dict) and chunk.get('type') == 'final_result':
                    response = chunk['response']
                    yield self.get_agent_response(response)
                else:
                    yield {
                        'is_task_complete': False,
                        'require_user_input': False,
                        'content': f'{self.agent_name}: Processing Request...',
                    }
        except Exception as e:
            logger.error(f'Error in agent stream: {e}')
            yield {
                'response_type': 'text',
                'is_task_complete': True,
                'require_user_input': False,
                'content': f"Error processing request: {str(e)}"
            }
                
    def format_response(self, chunk):
        """Response formatting following TravelAgent pattern."""
        patterns = [
            r'```\n(.*?)\n```',
            r'```json\s*(.*?)\s*```',
            r'```tool_outputs\s*(.*?)\s*```',
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

    async def health_check(self):
        """Add health check endpoints to all agents."""
        return {
            "status": "healthy",
            "agent": self.agent_name,
            "mcp_enabled": self.mcp_enabled,
            "google_adk_initialized": self.google_adk_initialized,
            "tools_count": len(self.tools) if self.tools else 0,
            "tier": getattr(self, 'tier', 0)
        }

    def get_agent_response(self, chunk):
        """Agent response handling with graceful degradation."""
        logger.info(f'Response Type {type(chunk)}')
        
        # Graceful degradation - if agent is not initialized, provide fallback
        if not self.google_adk_initialized:
            return {
                'response_type': 'text',
                'is_task_complete': True,
                'require_user_input': False,
                'content': f"Fallback response for: {chunk} (Google ADK unavailable)"
            }
        
        data = self.format_response(chunk)
        logger.info(f'Formatted Response {data}')
        
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
                    logger.error(f'Json conversion error {json_e}')
                    return_type = 'text'
                return {
                    'response_type': return_type,
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': data,
                }
        except Exception as e:
            logger.error(f'Error in get_agent_response: {e}')
            return {
                'response_type': 'text',
                'is_task_complete': True,
                'require_user_input': False,
                'content': 'Could not complete task. Please try again.',
            }