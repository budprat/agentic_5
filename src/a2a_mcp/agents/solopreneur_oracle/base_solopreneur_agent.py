"""Base class for all solopreneur agents following Google ADK framework pattern."""

# type: ignore

import json
import logging
import re
from collections.abc import AsyncIterable
from typing import Any, Dict

from a2a_mcp.common.agent_runner import AgentRunner
from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import get_mcp_server_config, init_api_key
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams
from google.genai import types as genai_types

logger = logging.getLogger(__name__)

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
        tools = []
        if os.environ.get('DISABLE_MCP_TOOLS', 'false').lower() != 'true':
            try:
                config = get_mcp_server_config()
                logger.info(f'MCP Server url={config.url}')
                
                # Load MCP tools following ADK pattern from adk_travel_agent.py
                tools = await MCPToolset(
                    connection_params=SseConnectionParams(url=config.url)
                ).get_tools()
                
                for tool in tools:
                    logger.info(f'Loaded tools {tool.name}')
            except Exception as e:
                logger.warning(f'Could not connect to MCP server: {e}. Continuing without MCP tools.')
        else:
            logger.info('MCP tools disabled by environment variable')
            
        generate_content_config = genai_types.GenerateContentConfig(
            temperature=0.0
        )
        
        # Initialize Google ADK agent following adk_nexus_agent.py pattern
        self.agent = Agent(
            name=self.agent_name,
            instruction=self.instructions,
            model='gemini-2.0-flash',
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            generate_content_config=generate_content_config,
            tools=tools,
        )
        self.runner = AgentRunner()
        
    async def invoke(self, query, session_id) -> dict:
        logger.info(f'Running {self.agent_name} for session {session_id}')
        raise NotImplementedError('Please use the streaming function')
        
    async def stream(
        self, query, context_id, task_id
    ) -> AsyncIterable[Dict[str, Any]]:
        """Stream implementation following ADK framework patterns."""
        logger.info(
            f'Running {self.agent_name} stream for session {context_id} {task_id} - {query}'
        )
        
        if not query:
            raise ValueError('Query cannot be empty')
            
        if not self.agent:
            await self.init_agent()
            
        # Use established AgentRunner pattern from ADK
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

    def get_agent_response(self, chunk):
        """Agent response handling following TravelAgent pattern."""
        logger.info(f'Response Type {type(chunk)}')
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