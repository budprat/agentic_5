# ABOUTME: Unified A2A (Agent-to-Agent) communication protocol implementation
# ABOUTME: Standardizes inter-agent communication with retry logic and error handling

import logging
import json
import asyncio
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime

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
    and error recovery mechanisms.
    """

    def __init__(
        self,
        default_timeout: int = 60,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize A2A protocol client.
        
        Args:
            default_timeout: Default request timeout in seconds
            max_retries: Maximum retry attempts for failed requests
            retry_delay: Initial delay between retries (exponential backoff)
        """
        self.default_timeout = default_timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
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
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send message to target agent using A2A protocol.
        
        Args:
            target_port: Port number of target agent
            message: Message to send
            metadata: Optional metadata
            method: A2A method name
            timeout: Request timeout (uses default if None)
            
        Returns:
            Response from target agent
            
        Raises:
            A2ACommunicationError: If communication fails after all retries
        """
        url = f"http://localhost:{target_port}"
        payload = create_a2a_request(method, message, metadata)
        timeout_setting = timeout or self.default_timeout
        
        self.session_stats["requests_sent"] += 1
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"A2A request to port {target_port}, attempt {attempt + 1}/{self.max_retries}")
                
                # Configure timeout
                timeout_config = aiohttp.ClientTimeout(
                    total=timeout_setting,
                    connect=10,
                    sock_read=30
                )
                
                async with aiohttp.ClientSession(timeout=timeout_config) as session:
                    async with session.post(url, json=payload) as response:
                        if response.status == 200:
                            result = await response.json()
                            self.session_stats["requests_successful"] += 1
                            logger.debug(f"A2A communication successful with port {target_port}")
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
        raise A2ACommunicationError(f"Failed to communicate with port {target_port} after {self.max_retries} attempts")

    async def _wait_for_retry(self, attempt: int):
        """Wait before retry with exponential backoff."""
        wait_time = self.retry_delay * (2 ** attempt)
        self.session_stats["retries_performed"] += 1
        logger.debug(f"Waiting {wait_time}s before A2A retry")
        await asyncio.sleep(wait_time)

    async def _process_a2a_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process A2A response and extract meaningful content.
        
        Args:
            response: Raw A2A response
            
        Returns:
            Processed response content
        """
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

    def get_session_stats(self) -> Dict[str, Any]:
        """Get communication statistics for this session."""
        total_requests = self.session_stats["requests_sent"]
        success_rate = (
            self.session_stats["requests_successful"] / total_requests * 100
            if total_requests > 0 else 0
        )
        
        return {
            **self.session_stats,
            "success_rate_percent": round(success_rate, 2),
            "average_retries_per_request": (
                self.session_stats["retries_performed"] / total_requests
                if total_requests > 0 else 0
            )
        }

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


class A2ACommunicationError(Exception):
    """Exception raised for A2A communication failures."""
    pass


# Port mapping for common agents
A2A_AGENT_PORTS = {
    "solopreneur_oracle": 10901,
    "technical_intelligence": 10902,
    "knowledge_management": 10903,
    "personal_optimization": 10904,
    "learning_enhancement": 10905,
    "integration_synthesis": 10906,
    "nexus_oracle": 12000,
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