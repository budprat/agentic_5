# ABOUTME: Example agents package initialization
# ABOUTME: Makes example agents available for import

"""
Example Agents for A2A-MCP Framework

This package contains example agents demonstrating different patterns:
- SearchAgent: Web search capabilities using MCP tools
- SummarizationAgent: Text processing with quality validation
- DataValidationAgent: Data validation with custom rules
"""

from .search_agent import SearchAgent
from .summarization_agent import SummarizationAgent
from .data_validation_agent import DataValidationAgent

__all__ = [
    "SearchAgent",
    "SummarizationAgent", 
    "DataValidationAgent"
]