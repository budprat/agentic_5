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
from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
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

class UnifiedSolopreneurAgent(StandardizedAgentBase):
    """
    Framework V2.0 compliant base class for all solopreneur agents.
    Uses StandardizedAgentBase with Google ADK + MCP tools integration.
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
            
        # Use StandardizedAgentBase initialization (handles init_api_key internally)
        super().__init__(
            agent_name=agent_name,
            description=description,
            instructions=instructions,
            quality_config={"domain": "business"},  # Framework V2.0 quality config
            mcp_tools_enabled=True,
            a2a_enabled=True
        )
        
        logger.info(f'Init {self.agent_name}')
        
        # Additional solopreneur-specific attributes
        self.port = port
        self.tier = self._determine_tier(port) if port else 0
        
        # StandardizedAgentBase handles: agent, tools, mcp_enabled, etc.
        
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
        
    async def _execute_agent_logic(self, query: str, context_id: str, task_id: str):
        """
        Implement Framework V2.0 required abstract method.
        Uses inherited StandardizedAgentBase agent for processing.
        """
        logger.info(f'UnifiedSolopreneurAgent executing logic for: {query}')
        
        # Use inherited agent from StandardizedAgentBase
        if not self.agent:
            await self.init_agent()  # Framework V2.0 initialization
        
        if not self.agent:
            return {"error": "Agent initialization failed", "content": f"Fallback response for: {query}"}
        
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
            logger.error(f'Execution error: {e}')
            return {"error": str(e), "content": f"Error processing: {query}"}
        
    async def invoke(self, query, session_id) -> dict:
        logger.info(f'Running {self.agent_name} for session {session_id}')
        raise NotImplementedError('Please use the streaming function')
                
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
        base_health = super().get_health_status()  # Framework V2.0 health check
        return {
            **base_health,
            "tier": getattr(self, 'tier', 0),
            "port": getattr(self, 'port', None)
        }

    def get_agent_response(self, chunk):
        """Agent response handling with Framework V2.0 compliance."""
        logger.info(f'Response Type {type(chunk)}')
        
        # Use StandardizedAgentBase initialization status
        if not self.initialization_complete:
            return {
                'response_type': 'text',
                'is_task_complete': True,
                'require_user_input': False,
                'content': f"Fallback response for: {chunk} (Framework V2.0 agent unavailable)"
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