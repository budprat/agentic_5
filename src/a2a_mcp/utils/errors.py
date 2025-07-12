# ABOUTME: Error handling utilities for A2A MCP Framework
# ABOUTME: Provides ServerError and other error types

from typing import Optional, Any


class ServerError(Exception):
    """Server error with structured error information."""
    
    def __init__(self, error: Any, message: Optional[str] = None):
        """Initialize server error.
        
        Args:
            error: Error object (e.g., InvalidParamsError)
            message: Optional error message
        """
        self.error = error
        self.message = message or str(error)
        super().__init__(self.message)