# ABOUTME: A2A Protocol wrapper for video generation agents to enable proper inter-agent communication
# ABOUTME: Provides standardized A2A communication capabilities to all video agents

"""
A2A Protocol Wrapper for Video Generation Agents

This module provides a wrapper that adds A2A Protocol communication capabilities
to video generation agents, ensuring proper framework compliance.
"""

import asyncio
from typing import Dict, Any, Optional, Callable
import json
from datetime import datetime

from a2a_mcp.common.a2a_protocol import (
    A2AProtocolClient,
    create_a2a_response,
    register_agent_port,
    A2ACommunicationError
)
from a2a_mcp.common.observability import get_logger


class A2AAgentWrapper:
    """
    Wrapper that adds A2A Protocol communication capabilities to agents.
    
    This can be used as a mixin or wrapper to make any agent A2A-compliant.
    """
    
    def __init__(
        self,
        agent_name: str,
        agent_port: int,
        wrapped_agent: Optional[Any] = None,
        enable_connection_pool: bool = True
    ):
        """
        Initialize A2A wrapper.
        
        Args:
            agent_name: Name of the agent for A2A registration
            agent_port: Port number for this agent
            wrapped_agent: The actual agent instance to wrap
            enable_connection_pool: Use connection pooling for performance
        """
        self.agent_name = agent_name
        self.agent_port = agent_port
        self.wrapped_agent = wrapped_agent or self
        self.logger = get_logger(f"A2A_{agent_name}")
        
        # Register this agent in the A2A Protocol
        register_agent_port(agent_name, agent_port)
        
        # Initialize A2A client for outgoing communication
        self.a2a_client = A2AProtocolClient(
            source_agent_name=agent_name,
            use_connection_pool=enable_connection_pool,
            custom_port_mapping={
                # Video generation agent ports
                "script_writer": 10212,
                "scene_designer": 10213,
                "timing_coordinator": 10214,
                "hook_creator": 10215,
                "shot_describer": 10216,
                "transition_planner": 10217,
                "cta_generator": 10218,
                "video_orchestrator": 10211
            }
        )
        
        # Store active A2A server
        self.a2a_server = None
        
    async def start_a2a_server(self):
        """Start A2A Protocol server to receive messages."""
        from aiohttp import web
        
        app = web.Application()
        app.router.add_post('/', self._handle_a2a_request)
        
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, 'localhost', self.agent_port)
        await site.start()
        
        self.a2a_server = runner
        self.logger.info(f"A2A server started for {self.agent_name} on port {self.agent_port}")
        
    async def stop_a2a_server(self):
        """Stop A2A Protocol server."""
        if self.a2a_server:
            await self.a2a_server.cleanup()
            self.a2a_server = None
            self.logger.info(f"A2A server stopped for {self.agent_name}")
    
    async def _handle_a2a_request(self, request):
        """Handle incoming A2A Protocol requests."""
        from aiohttp import web
        
        try:
            # Parse JSON-RPC request
            data = await request.json()
            request_id = data.get("id", "unknown")
            method = data.get("method", "")
            params = data.get("params", {})
            
            self.logger.debug(f"Received A2A request: {method}")
            
            # Route to appropriate handler
            if method == "message/send":
                result = await self._handle_message(params)
            elif method == "system/health":
                result = await self._handle_health_check(params)
            elif method == "task/execute":
                result = await self._handle_task_execution(params)
            else:
                # Try to delegate to wrapped agent
                if hasattr(self.wrapped_agent, 'handle_a2a_request'):
                    result = await self.wrapped_agent.handle_a2a_request(method, params)
                else:
                    raise ValueError(f"Unknown A2A method: {method}")
            
            # Create success response
            response = create_a2a_response(request_id, result)
            
            return web.json_response(response)
            
        except Exception as e:
            self.logger.error(f"A2A request handling error: {e}", exc_info=True)
            
            # Create error response
            error_response = create_a2a_response(
                data.get("id", "unknown"),
                error={
                    "code": -32603,
                    "message": str(e),
                    "data": {"agent": self.agent_name}
                }
            )
            
            return web.json_response(error_response, status=500)
    
    async def _handle_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle basic message request."""
        message = params.get("message", "")
        metadata = params.get("metadata", {})
        
        # Delegate to wrapped agent if it has a process method
        if hasattr(self.wrapped_agent, 'process'):
            result = await self.wrapped_agent.process(message, metadata)
            return {
                "success": True,
                "response": result,
                "agent": self.agent_name,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": True,
                "response": f"{self.agent_name} received: {message}",
                "agent": self.agent_name,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _handle_health_check(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle health check request."""
        return {
            "status": "healthy",
            "agent": self.agent_name,
            "port": self.agent_port,
            "capabilities": self._get_agent_capabilities(),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_task_execution(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle task execution request."""
        task_type = params.get("task_type", "")
        task_params = params.get("task_params", {})
        
        # Delegate to wrapped agent's execute method if available
        if hasattr(self.wrapped_agent, 'execute_task'):
            result = await self.wrapped_agent.execute_task(task_type, task_params)
            return {
                "success": True,
                "task_type": task_type,
                "result": result,
                "agent": self.agent_name,
                "timestamp": datetime.now().isoformat()
            }
        elif hasattr(self.wrapped_agent, '_execute_agent_logic'):
            # For StandardizedAgentBase agents
            # Define TaskContext inline
            from dataclasses import dataclass
            from typing import Dict as _Dict, Any as _Any, Optional as _Optional
            
            @dataclass
            class TaskContext:
                task_id: str = ""
                session_id: str = ""
                context_id: str = ""
                workflow_id: _Optional[str] = None
                metadata: _Dict[str, _Any] = None
            
            context = TaskContext(
                task_id=params.get("task_id", ""),
                session_id=params.get("session_id", "default"),
                context_id=params.get("context_id", ""),
                metadata=params.get("metadata", {}) or {}
            )
            
            result = await self.wrapped_agent._execute_agent_logic(context)
            
            # Convert TaskResult to dict
            return {
                "success": result.status == "success",
                "result": {
                    "artifacts": [
                        {
                            "type": a.type,
                            "content": a.content,
                            "metadata": a.metadata
                        } for a in result.artifacts
                    ] if result.artifacts else [],
                    "message": result.message,
                    "metadata": result.metadata
                },
                "agent": self.agent_name,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise NotImplementedError(f"{self.agent_name} does not support task execution")
    
    def _get_agent_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities for health check."""
        capabilities = {
            "a2a_protocol": True,
            "connection_pooling": self.a2a_client.use_connection_pool,
            "methods": ["message/send", "system/health", "task/execute"]
        }
        
        # Add wrapped agent capabilities if available
        if hasattr(self.wrapped_agent, 'get_capabilities'):
            capabilities.update(self.wrapped_agent.get_capabilities())
        
        return capabilities
    
    # Outgoing A2A communication methods
    
    async def send_to_agent(
        self,
        target_agent: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send message to another agent using A2A Protocol.
        
        Args:
            target_agent: Name of target agent
            message: Message content
            metadata: Optional metadata
            timeout: Request timeout
            
        Returns:
            Response from target agent
        """
        try:
            return await self.a2a_client.send_message_by_name(
                target_agent,
                message,
                metadata,
                timeout=timeout
            )
        except A2ACommunicationError as e:
            self.logger.error(f"Failed to communicate with {target_agent}: {e}")
            raise
    
    async def execute_remote_task(
        self,
        target_agent: str,
        task_type: str,
        task_params: Dict[str, Any],
        session_id: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute task on remote agent using A2A Protocol.
        
        Args:
            target_agent: Name of target agent
            task_type: Type of task to execute
            task_params: Task parameters
            session_id: Session ID for tracking
            timeout: Request timeout
            
        Returns:
            Task execution result
        """
        return await self.a2a_client.send_message_by_name(
            target_agent,
            "execute_task",
            {
                "task_type": task_type,
                "task_params": task_params,
                "session_id": session_id or "default"
            },
            method="task/execute",
            timeout=timeout
        )
    
    async def broadcast_to_agents(
        self,
        target_agents: list[str],
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Broadcast message to multiple agents concurrently.
        
        Args:
            target_agents: List of target agent names
            message: Message to broadcast
            metadata: Optional metadata
            
        Returns:
            Dict mapping agent names to their responses
        """
        tasks = []
        for agent in target_agents:
            task = self.send_to_agent(agent, message, metadata)
            tasks.append((agent, task))
        
        results = {}
        for agent, task in tasks:
            try:
                results[agent] = await task
            except Exception as e:
                results[agent] = {
                    "success": False,
                    "error": str(e)
                }
        
        return results
    
    def get_a2a_stats(self) -> Dict[str, Any]:
        """Get A2A communication statistics."""
        return {
            "agent_name": self.agent_name,
            "agent_port": self.agent_port,
            "client_stats": self.a2a_client.get_session_stats(),
            "server_running": self.a2a_server is not None
        }


def create_a2a_enabled_agent(
    agent_class: type,
    agent_name: str,
    agent_port: int,
    *args,
    **kwargs
) -> A2AAgentWrapper:
    """
    Factory function to create an A2A-enabled agent.
    
    Args:
        agent_class: The agent class to instantiate
        agent_name: Name for A2A registration
        agent_port: Port for A2A communication
        *args: Arguments for agent constructor
        **kwargs: Keyword arguments for agent constructor
        
    Returns:
        A2A-enabled agent instance
    """
    # Create the base agent
    agent = agent_class(*args, **kwargs)
    
    # Wrap with A2A capabilities
    wrapper = A2AAgentWrapper(
        agent_name=agent_name,
        agent_port=agent_port,
        wrapped_agent=agent
    )
    
    # Copy important attributes to wrapper for convenience
    for attr in ['agent_id', 'quality_framework', 'connection_pool']:
        if hasattr(agent, attr):
            setattr(wrapper, attr, getattr(agent, attr))
    
    # Delegate method calls to wrapped agent
    def __getattr__(self, name):
        return getattr(self.wrapped_agent, name)
    
    wrapper.__getattr__ = __getattr__.__get__(wrapper, A2AAgentWrapper)
    
    return wrapper
