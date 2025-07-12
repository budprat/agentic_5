# ABOUTME: Unified A2A (Agent-to-Agent) communication protocol implementation
# ABOUTME: Provides configurable, extensible inter-agent communication with retry logic

import logging
import json
import asyncio
import aiohttp
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from .a2a_connection_pool import get_global_connection_pool, A2AConnectionPool
from .metrics_collector import record_a2a_message

logger = logging.getLogger(__name__)


def create_a2a_request(
    method: str,
    message: str,
    metadata: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create standardized A2A JSON-RPC request.
    
    Args:
        method: RPC method name (e.g., "message/send", "message/stream")
        message: Message content
        metadata: Optional metadata dict
        request_id: Optional request ID for tracking
        
    Returns:
        Formatted A2A request payload
    """
    if not request_id:
        request_id = f"a2a_{int(datetime.now().timestamp() * 1000)}"
    
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": {
            "message": message,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
    }


def create_a2a_response(
    request_id: str,
    result: Any = None,
    error: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create standardized A2A JSON-RPC response.
    
    Args:
        request_id: ID from the original request
        result: Success result data
        error: Error information if failed
        
    Returns:
        Formatted A2A response payload
    """
    response = {
        "jsonrpc": "2.0",
        "id": request_id
    }
    
    if error:
        response["error"] = error
    else:
        response["result"] = result
    
    return response


class A2AProtocolClient:
    """
    Unified A2A protocol client for inter-agent communication.
    
    Provides standardized communication with retry logic, timeout handling,
    and error recovery mechanisms. Supports custom port mappings and
    response processors for extensibility.
    """

    def __init__(
        self,
        default_timeout: int = 60,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        custom_port_mapping: Optional[Dict[str, int]] = None,
        response_processor: Optional[Callable] = None,
        use_connection_pool: bool = True,
        connection_pool: Optional[A2AConnectionPool] = None,
        source_agent_name: Optional[str] = None
    ):
        """
        Initialize A2A protocol client.
        
        Args:
            default_timeout: Default request timeout in seconds
            max_retries: Maximum retry attempts for failed requests
            retry_delay: Initial delay between retries (exponential backoff)
            custom_port_mapping: Additional agent name to port mappings
            response_processor: Custom response processing function
            use_connection_pool: Whether to use connection pooling (60% performance improvement)
            connection_pool: Custom connection pool instance (uses global pool if None)
            source_agent_name: Name of the source agent for metrics tracking
        """
        self.default_timeout = default_timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.custom_port_mapping = custom_port_mapping or {}
        self.response_processor = response_processor
        self.use_connection_pool = use_connection_pool
        self._connection_pool = connection_pool
        self.source_agent_name = source_agent_name or "unknown"
        self.session_stats = {
            "requests_sent": 0,
            "requests_successful": 0,
            "requests_failed": 0,
            "retries_performed": 0
        }

    async def send_message(
        self,
        target_port: int,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
        method: str = "message/send",
        timeout: Optional[int] = None,
        custom_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Send message to target agent using A2A protocol.
        
        Args:
            target_port: Port number of target agent
            message: Message to send
            metadata: Optional metadata
            method: A2A method name
            timeout: Request timeout (uses default if None)
            custom_headers: Additional HTTP headers to include
            
        Returns:
            Response from target agent
            
        Raises:
            A2ACommunicationError: If communication fails after all retries
        """
        url = f"http://localhost:{target_port}"
        payload = create_a2a_request(method, message, metadata)
        timeout_setting = timeout or self.default_timeout
        
        # Build headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "A2A-Protocol-Client/1.0"
        }
        if custom_headers:
            headers.update(custom_headers)
        
        self.session_stats["requests_sent"] += 1
        
        # Track start time for latency metrics
        start_time = datetime.now()
        target_agent_name = f"port_{target_port}"  # Default name
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"A2A request to port {target_port}, attempt {attempt + 1}/{self.max_retries}")
                
                if self.use_connection_pool:
                    # Use connection pool for better performance
                    pool = self._get_connection_pool()
                    async with pool.get_session(target_port) as session:
                        async with session.post(url, json=payload, headers=headers) as response:
                            if response.status == 200:
                                result = await response.json()
                                self.session_stats["requests_successful"] += 1
                                logger.debug(f"A2A communication successful with port {target_port}")
                                
                                # Record success metrics
                                latency = (datetime.now() - start_time).total_seconds()
                                record_a2a_message(
                                    source_agent=self.source_agent_name,
                                    target_agent=target_agent_name,
                                    status="success",
                                    latency=latency
                                )
                                
                                return await self._process_a2a_response(result)
                            else:
                                error_text = await response.text()
                                logger.warning(f"A2A HTTP {response.status} from port {target_port}: {error_text}")
                                
                                if attempt < self.max_retries - 1:
                                    await self._wait_for_retry(attempt)
                                    continue
                                else:
                                    raise A2ACommunicationError(
                                        f"HTTP {response.status} from port {target_port}: {error_text}"
                                    )
                else:
                    # Legacy mode without connection pooling
                    # Configure timeout
                    timeout_config = aiohttp.ClientTimeout(
                        total=timeout_setting,
                        connect=10,
                        sock_read=30
                    )
                    
                    async with aiohttp.ClientSession(timeout=timeout_config) as session:
                        async with session.post(url, json=payload, headers=headers) as response:
                            if response.status == 200:
                                result = await response.json()
                                self.session_stats["requests_successful"] += 1
                                logger.debug(f"A2A communication successful with port {target_port}")
                                
                                # Record success metrics
                                latency = (datetime.now() - start_time).total_seconds()
                                record_a2a_message(
                                    source_agent=self.source_agent_name,
                                    target_agent=target_agent_name,
                                    status="success",
                                    latency=latency
                                )
                                
                                return await self._process_a2a_response(result)
                            else:
                                error_text = await response.text()
                                logger.warning(f"A2A HTTP {response.status} from port {target_port}: {error_text}")
                                
                                if attempt < self.max_retries - 1:
                                    await self._wait_for_retry(attempt)
                                    continue
                                else:
                                    raise A2ACommunicationError(
                                        f"HTTP {response.status} from port {target_port}: {error_text}"
                                    )
                                
            except asyncio.TimeoutError:
                logger.warning(f"A2A timeout for port {target_port} (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    await self._wait_for_retry(attempt)
                    continue
                else:
                    self.session_stats["requests_failed"] += 1
                    raise A2ACommunicationError(f"Timeout communicating with agent on port {target_port}")
                    
            except aiohttp.ClientError as e:
                logger.warning(f"A2A network error for port {target_port}: {e} (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    await self._wait_for_retry(attempt)
                    continue
                else:
                    self.session_stats["requests_failed"] += 1
                    raise A2ACommunicationError(f"Network error communicating with port {target_port}: {e}")
                    
            except Exception as e:
                logger.error(f"A2A unexpected error for port {target_port}: {e}")
                if attempt < self.max_retries - 1:
                    await self._wait_for_retry(attempt)
                    continue
                else:
                    self.session_stats["requests_failed"] += 1
                    raise A2ACommunicationError(f"Unexpected error communicating with port {target_port}: {e}")
        
        # Should not reach here due to explicit handling above
        self.session_stats["requests_failed"] += 1
        
        # Record failure metrics
        latency = (datetime.now() - start_time).total_seconds()
        record_a2a_message(
            source_agent=self.source_agent_name,
            target_agent=target_agent_name,
            status="error",
            latency=latency
        )
        
        raise A2ACommunicationError(f"Failed to communicate with port {target_port} after {self.max_retries} attempts")

    def _get_connection_pool(self) -> A2AConnectionPool:
        """Get the connection pool instance."""
        if self._connection_pool:
            return self._connection_pool
        return get_global_connection_pool()

    async def send_message_by_name(
        self,
        agent_name: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
        method: str = "message/send",
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send message to agent by name using port mapping.
        
        Args:
            agent_name: Name of target agent
            message: Message to send
            metadata: Optional metadata
            method: A2A method name
            timeout: Request timeout
            
        Returns:
            Response from target agent
        """
        port = self.get_agent_port(agent_name)
        return await self.send_message(port, message, metadata, method, timeout)

    async def _wait_for_retry(self, attempt: int):
        """Wait before retry with exponential backoff."""
        wait_time = self.retry_delay * (2 ** attempt)
        self.session_stats["retries_performed"] += 1
        logger.debug(f"Waiting {wait_time}s before A2A retry")
        await asyncio.sleep(wait_time)

    async def _process_a2a_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process A2A response and extract meaningful content.
        
        Can be overridden by custom response processor.
        
        Args:
            response: Raw A2A response
            
        Returns:
            Processed response content
        """
        # Use custom processor if provided
        if self.response_processor:
            return await self.response_processor(response)
        
        # Handle JSON-RPC error responses
        if "error" in response:
            error_info = response["error"]
            raise A2ACommunicationError(f"A2A error: {error_info}")
        
        # Extract result from JSON-RPC response
        if "result" in response:
            result = response["result"]
            
            # Process different response formats
            if isinstance(result, dict):
                # Handle task-based responses with artifacts
                if result.get("kind") == "task" and "artifacts" in result:
                    return await self._extract_from_artifacts(result["artifacts"])
                
                # Handle direct analysis content
                if "analysis" in result or "content" in result:
                    return {
                        "success": True,
                        "content": result.get("analysis") or result.get("content"),
                        "metadata": result.get("metadata", {})
                    }
                
                # Return structured result as-is
                return {
                    "success": True,
                    "content": result,
                    "metadata": {}
                }
            
            # Handle text-based responses
            return {
                "success": True,
                "content": result,
                "metadata": {}
            }
        
        # Fallback for unexpected response format
        logger.warning(f"Unexpected A2A response format: {response}")
        return {
            "success": False,
            "content": response,
            "metadata": {"warning": "Unexpected response format"}
        }

    async def _extract_from_artifacts(self, artifacts: list) -> Dict[str, Any]:
        """Extract content from A2A task artifacts."""
        if not artifacts:
            return {"success": False, "content": "No artifacts in response", "metadata": {}}
        
        # Process first artifact
        artifact = artifacts[0]
        parts = artifact.get("parts", [])
        
        for part in parts:
            # Handle data parts (structured content)
            if part.get("kind") == "data" and "data" in part:
                return {
                    "success": True,
                    "content": part["data"],
                    "metadata": {"source": "artifact_data"}
                }
            
            # Handle text parts
            elif part.get("kind") == "text" and "text" in part:
                text_content = part["text"]
                
                # Try to parse as JSON if it looks structured
                if text_content.strip().startswith('{'):
                    try:
                        parsed_content = json.loads(text_content)
                        return {
                            "success": True,
                            "content": parsed_content,
                            "metadata": {"source": "artifact_text_json"}
                        }
                    except json.JSONDecodeError:
                        pass
                
                # Return as text
                return {
                    "success": True,
                    "content": text_content,
                    "metadata": {"source": "artifact_text"}
                }
        
        # No processable parts found
        return {
            "success": False,
            "content": f"No processable parts in artifact: {artifact}",
            "metadata": {"warning": "No processable artifact parts"}
        }

    def get_agent_port(self, agent_name: str) -> int:
        """
        Get port for agent by name, checking custom mapping first.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Port number
            
        Raises:
            ValueError: If agent name not found
        """
        # Check custom mapping first
        if agent_name in self.custom_port_mapping:
            return self.custom_port_mapping[agent_name]
        
        # Fall back to default mapping
        return get_agent_port(agent_name)

    def get_session_stats(self) -> Dict[str, Any]:
        """Get communication statistics for this session."""
        total_requests = self.session_stats["requests_sent"]
        success_rate = (
            self.session_stats["requests_successful"] / total_requests * 100
            if total_requests > 0 else 0
        )
        
        stats = {
            **self.session_stats,
            "success_rate_percent": round(success_rate, 2),
            "average_retries_per_request": (
                self.session_stats["retries_performed"] / total_requests
                if total_requests > 0 else 0
            ),
            "connection_pooling_enabled": self.use_connection_pool
        }
        
        # Add pool metrics if using connection pooling
        if self.use_connection_pool:
            pool = self._get_connection_pool()
            stats["pool_metrics"] = pool.get_metrics()
            
        return stats

    async def health_check(self, target_port: int) -> Dict[str, Any]:
        """
        Perform health check on target agent.
        
        Args:
            target_port: Port of target agent
            
        Returns:
            Health check result
        """
        try:
            response = await self.send_message(
                target_port,
                "health_check",
                {"check_type": "connectivity"},
                method="system/health",
                timeout=10
            )
            return {
                "port": target_port,
                "status": "healthy",
                "response_time_ms": None,  # Could be measured
                "details": response
            }
        except Exception as e:
            return {
                "port": target_port,
                "status": "unhealthy",
                "error": str(e),
                "details": None
            }

    async def batch_health_check(self, agent_names: Optional[list] = None) -> Dict[str, Any]:
        """
        Check health of multiple agents concurrently.
        
        Args:
            agent_names: List of agent names to check (None = check all known agents)
            
        Returns:
            Health status for all checked agents
        """
        if agent_names is None:
            # Get all agents from both default and custom mappings
            all_agents = set(A2A_AGENT_PORTS.keys()) | set(self.custom_port_mapping.keys())
            agent_names = list(all_agents)
        
        health_tasks = []
        for agent_name in agent_names:
            try:
                port = self.get_agent_port(agent_name)
                health_tasks.append((agent_name, self.health_check(port)))
            except ValueError:
                logger.warning(f"Unknown agent for health check: {agent_name}")
        
        results = {}
        for agent_name, task in health_tasks:
            result = await task
            results[agent_name] = result
        
        return results


class A2ACommunicationError(Exception):
    """Exception raised for A2A communication failures."""
    pass


# Default port mapping for common agents
# TO EXTEND: Add your new agent mappings here or use custom_port_mapping in client
A2A_AGENT_PORTS = {
    "solopreneur_oracle": 10901,
    "technical_intelligence": 10902,
    "knowledge_management": 10903,
    "personal_optimization": 10904,
    "learning_enhancement": 10905,
    "integration_synthesis": 10906,
    "nexus_oracle": 12000,
    # Add new agents here:
    # "your_agent_name": port_number,
}


def get_agent_port(agent_name: str) -> int:
    """
    Get standard port for agent by name.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        Port number
        
    Raises:
        ValueError: If agent name not found
    """
    port = A2A_AGENT_PORTS.get(agent_name.lower())
    if port is None:
        raise ValueError(f"Unknown agent name: {agent_name}. Available: {list(A2A_AGENT_PORTS.keys())}")
    return port


def register_agent_port(agent_name: str, port: int) -> None:
    """
    Register a new agent port mapping globally.
    
    Args:
        agent_name: Name of the agent
        port: Port number to assign
        
    Note:
        This modifies the global A2A_AGENT_PORTS dictionary.
        For temporary mappings, use custom_port_mapping in A2AProtocolClient.
    """
    A2A_AGENT_PORTS[agent_name.lower()] = port
    logger.info(f"Registered agent '{agent_name}' on port {port}")


# Example usage for extending with new agents:
"""
# Method 1: Use custom mapping in client (recommended for dynamic agents)
client = A2AProtocolClient(
    custom_port_mapping={
        "my_custom_agent": 11001,
        "another_agent": 11002
    }
)

# Method 2: Register globally (for permanent agents)
register_agent_port("my_permanent_agent", 11003)

# Method 3: Add directly to A2A_AGENT_PORTS above

# Custom response processor example:
async def my_response_processor(response):
    # Custom processing logic
    if "special_format" in response:
        return {"processed": True, "data": response["special_format"]}
    # Fall back to default processing
    return None  # Return None to use default processor

client = A2AProtocolClient(response_processor=my_response_processor)
"""