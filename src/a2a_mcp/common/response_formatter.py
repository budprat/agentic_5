# ABOUTME: Shared response formatting utilities for Framework V2.0
# ABOUTME: Eliminates code duplication and standardizes response processing across all agent types

import json
import re
import logging
from typing import Any, Dict, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)


class ResponseFormatter:
    """
    Framework V2.0 Universal Response Formatter
    
    Provides consistent response formatting, parsing, and standardization
    across all agent types. Eliminates code duplication and ensures
    uniform response handling throughout the framework.
    """

    # Response type constants
    RESPONSE_TYPE_DATA = "data"
    RESPONSE_TYPE_TEXT = "text"
    RESPONSE_TYPE_JSON = "json"
    RESPONSE_TYPE_STRUCTURED = "structured"
    RESPONSE_TYPE_INTERACTIVE = "interactive"
    RESPONSE_TYPE_ERROR = "error"
    RESPONSE_TYPE_PROGRESS = "progress"

    # Regex patterns for content extraction
    PATTERNS = [
        (r'```json\s*(.*?)\s*```', 'json'),         # JSON blocks
        (r'```\n(.*?)\n```', 'code'),               # Code blocks
        (r'```tool_outputs\s*(.*?)\s*```', 'tool'), # Tool output blocks
        (r'```python\s*(.*?)\s*```', 'python'),     # Python code blocks
        (r'```javascript\s*(.*?)\s*```', 'js'),     # JavaScript code blocks
    ]

    @classmethod
    def format_response(cls, chunk: Any) -> Any:
        """
        Format and parse agent response with intelligent content detection.
        
        Handles multiple output formats from LLMs including:
        - JSON code blocks
        - Plain code blocks  
        - Tool output blocks
        - Raw JSON strings
        - Plain text responses
        
        Args:
            chunk: Raw response from agent
            
        Returns:
            Parsed response (dict, string, or original chunk)
        """
        if not isinstance(chunk, str):
            return chunk
        
        # Try pattern matching first
        for pattern, pattern_type in cls.PATTERNS:
            match = re.search(pattern, chunk, re.DOTALL)
            if match:
                content = match.group(1).strip()
                
                # Try to parse as JSON for json/tool patterns
                if pattern_type in ['json', 'tool']:
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        pass
                
                return content
        
        # Try to parse entire chunk as JSON
        chunk_stripped = chunk.strip()
        if chunk_stripped.startswith('{') or chunk_stripped.startswith('['):
            try:
                return json.loads(chunk_stripped)
            except json.JSONDecodeError:
                pass
        
        # Return original chunk if no patterns match
        return chunk

    @classmethod
    def detect_interactive_mode(cls, content: Any) -> bool:
        """
        Detect if response requires user interaction.
        
        Enhanced interactive mode detection that identifies:
        - Explicit interactive mode signals
        - Question patterns in content
        - User input requirement flags
        
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
            if 'question' in content and content.get('question'):
                return True
            if content.get('missing_information') or content.get('needs_clarification'):
                return True
        
        if isinstance(content, str):
            # Look for question patterns in text
            question_indicators = [
                '?', 'please provide', 'what is', 'which', 'how', 'when', 'where',
                'could you specify', 'can you clarify', 'need more information',
                'please confirm', 'would you like', 'do you want'
            ]
            content_lower = content.lower()
            return any(indicator in content_lower for indicator in question_indicators)
        
        return False

    @classmethod
    def standardize_response_format(
        cls,
        content: Any, 
        is_interactive: bool = False, 
        is_complete: bool = True,
        agent_name: str = "Agent",
        quality_metadata: Optional[Dict[str, Any]] = None,
        response_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Standardize response format across all agent types.
        
        Creates unified response structure with:
        - Consistent field naming
        - Type detection and classification
        - Error handling integration
        - Quality metadata inclusion
        
        Args:
            content: Response content
            is_interactive: Whether response requires user input
            is_complete: Whether task is complete
            agent_name: Name of the responding agent
            quality_metadata: Quality validation results
            response_type: Optional explicit response type
            
        Returns:
            Standardized response format
        """
        try:
            if is_interactive:
                # Interactive mode - requires user input
                question = content.get('question', str(content)) if isinstance(content, dict) else str(content)
                return {
                    'response_type': cls.RESPONSE_TYPE_INTERACTIVE,
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': question,
                    'agent_name': agent_name,
                    'timestamp': datetime.now().isoformat(),
                    'quality_metadata': quality_metadata
                }
            
            # Determine response type if not provided
            if response_type is None:
                response_type = cls._determine_response_type(content)
            
            standardized_response = {
                'response_type': response_type,
                'is_task_complete': is_complete,
                'require_user_input': False,
                'content': content,
                'agent_name': agent_name,
                'timestamp': datetime.now().isoformat()
            }
            
            # Add quality metadata if provided
            if quality_metadata:
                standardized_response['quality_metadata'] = quality_metadata
            
            return standardized_response
                
        except Exception as e:
            logger.error(f'Error in standardize_response_format: {e}')
            return cls.create_error_response(
                error_message='Response formatting error occurred.',
                agent_name=agent_name,
                error_type='formatting',
                context={'error': str(e), 'content_type': type(content).__name__}
            )

    @classmethod
    def _determine_response_type(cls, content: Any) -> str:
        """
        Determine the appropriate response type based on content.
        
        Args:
            content: Response content to analyze
            
        Returns:
            Response type string
        """
        if isinstance(content, dict):
            return cls.RESPONSE_TYPE_STRUCTURED
        elif isinstance(content, list):
            return cls.RESPONSE_TYPE_DATA
        elif isinstance(content, str):
            try:
                json.loads(content)
                return cls.RESPONSE_TYPE_JSON
            except json.JSONDecodeError:
                return cls.RESPONSE_TYPE_TEXT
        else:
            return cls.RESPONSE_TYPE_DATA

    @classmethod
    def create_error_response(
        cls,
        error_message: str, 
        agent_name: str = "Agent",
        error_type: str = "general",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create standardized error response format.
        
        Args:
            error_message: Human-readable error description
            agent_name: Name of the agent that encountered the error
            error_type: Type of error (e.g., 'validation', 'communication', 'processing')
            context: Additional context about the error
            
        Returns:
            Standardized error response
        """
        return {
            'response_type': cls.RESPONSE_TYPE_ERROR,
            'is_task_complete': True,
            'require_user_input': False,
            'content': f"{agent_name}: {error_message}",
            'agent_name': agent_name,
            'timestamp': datetime.now().isoformat(),
            'error_details': {
                'error_type': error_type,
                'error_message': error_message,
                'context': context or {}
            }
        }

    @classmethod
    def create_progress_response(
        cls,
        message: str,
        agent_name: str = "Agent", 
        progress_percentage: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create standardized progress response format.
        
        Args:
            message: Progress message
            agent_name: Name of the reporting agent
            progress_percentage: Optional progress percentage (0.0-1.0)
            metadata: Additional progress metadata
            
        Returns:
            Standardized progress response
        """
        progress_response = {
            'response_type': cls.RESPONSE_TYPE_PROGRESS,
            'is_task_complete': False,
            'require_user_input': False,
            'content': message,
            'agent_name': agent_name,
            'timestamp': datetime.now().isoformat()
        }
        
        if progress_percentage is not None:
            progress_response['progress_percentage'] = max(0.0, min(1.0, progress_percentage))
        
        if metadata:
            progress_response['progress_metadata'] = metadata
            
        return progress_response


# Convenience functions for common operations
def format_agent_response(
    chunk: Any, 
    agent_name: str = "Agent",
    quality_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Convenience function for standard agent response formatting."""
    formatted_content = ResponseFormatter.format_response(chunk)
    is_interactive = ResponseFormatter.detect_interactive_mode(formatted_content)
    
    return ResponseFormatter.standardize_response_format(
        formatted_content,
        is_interactive=is_interactive,
        is_complete=not is_interactive,
        agent_name=agent_name,
        quality_metadata=quality_metadata
    )


def create_agent_error(
    error_message: str, 
    agent_name: str = "Agent", 
    error_type: str = "general",
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Convenience function for creating standardized error responses."""
    return ResponseFormatter.create_error_response(error_message, agent_name, error_type, context)


def create_agent_progress(
    message: str, 
    agent_name: str = "Agent", 
    progress: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Convenience function for creating standardized progress responses."""
    return ResponseFormatter.create_progress_response(message, agent_name, progress, metadata)