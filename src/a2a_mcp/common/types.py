# type: ignore
# ABOUTME: Common types for A2A MCP Framework infrastructure
# ABOUTME: Contains ServerConfig and other shared infrastructure types

from typing import Optional
from pydantic import BaseModel


class ServerConfig(BaseModel):
    """Server Configuration for MCP connections."""

    host: str
    port: int
    transport: str
    url: str