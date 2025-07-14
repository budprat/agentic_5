# ABOUTME: Memory prompts module exports
# ABOUTME: Provides memory-aware prompt templates and utilities

"""Memory-aware prompts for A2A agents."""

from .memory_prompts import (
    MemoryPrompts,
    MEMORY_PROMPT_EXAMPLES
)

__all__ = [
    "MemoryPrompts",
    "MEMORY_PROMPT_EXAMPLES"
]