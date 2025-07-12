#!/usr/bin/env python3
# ABOUTME: Demonstrates centralized configuration management in Framework V2.0
# ABOUTME: Shows configuration loading, environment overrides, and agent setup

import os
import sys
import asyncio
import logging
import yaml
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from a2a_mcp.common import (
    ConfigManager,
    FrameworkConfig,
    AgentConfig,
    get_config,
    get_agent_config,
    StandardizedAgentBase
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigDemoAgent(StandardizedAgentBase):
    """Demo agent that uses centralized configuration."""
    
    async def _execute_agent_logic(self, query: str, context_id: str, task_id: str):
        """Simple demo logic."""
        return {"content": f"Demo response for: {query}"}


def demonstrate_config_loading():
    """Demonstrate basic configuration loading."""
    print("\n=== Configuration Loading Demo ===")
    
    # Create config manager
    config_manager = ConfigManager()
    config = config_manager.config
    
    print(f"\nFramework Configuration:")
    print(f"  Version: {config.framework_version}")
    print(f"  Environment: {config.environment}")
    print(f"  Log Level: {config.log_level}")
    
    print(f"\nMCP Server Configuration:")
    print(f"  Host: {config.mcp_server.host}")
    print(f"  Port: {config.mcp_server.port}")
    print(f"  URL: {config.mcp_server.url}")
    
    print(f"\nConnection Pool Configuration:")
    print(f"  Enabled: {config.connection_pool.enabled}")
    print(f"  Max Connections: {config.connection_pool.max_connections_per_host}")
    print(f"  Keepalive Timeout: {config.connection_pool.keepalive_timeout}s")
    
    print(f"\nQuality Framework Configuration:")
    print(f"  Domain: {config.quality.domain}")
    print(f"  Validation Enabled: {config.quality.validation_enabled}")
    print(f"  Thresholds: {config.quality.thresholds}")
    
    print(f"\nFeature Flags:")
    for feature, enabled in config.features.items():
        print(f"  {feature}: {enabled}")


def demonstrate_environment_overrides():
    """Demonstrate environment variable overrides."""
    print("\n=== Environment Override Demo ===")
    
    # Set some environment variables
    os.environ['A2A_MCP_LOG_LEVEL'] = 'DEBUG'
    os.environ['A2A_MCP_ENVIRONMENT'] = 'production'
    os.environ['A2A_MCP_CONNECTION_POOL_MAX_CONNECTIONS_PER_HOST'] = '20'
    os.environ['A2A_MCP_FEATURES'] = '{"prometheus_metrics": true}'
    
    # Create new config manager (will pick up env vars)
    config_manager = ConfigManager()
    config = config_manager.config
    
    print(f"\nOverridden Configuration:")
    print(f"  Environment: {config.environment} (was: development)")
    print(f"  Log Level: {config.log_level} (was: INFO)")
    print(f"  Max Connections: {config.connection_pool.max_connections_per_host} (was: 10)")
    print(f"  Prometheus Metrics: {config.features.get('prometheus_metrics')} (was: False)")
    
    print(f"\nEnvironment Overrides Applied:")
    for key, value in config_manager.get_env_overrides().items():
        print(f"  {key}: {value}")


def demonstrate_agent_configuration():
    """Demonstrate agent-specific configuration."""
    print("\n=== Agent Configuration Demo ===")
    
    # Get configuration for specific agents
    agents_to_check = ["master_orchestrator", "technical_specialist", "code_analyzer"]
    
    for agent_id in agents_to_check:
        agent_config = get_agent_config(agent_id)
        if agent_config:
            print(f"\n{agent_config.name}:")
            print(f"  Port: {agent_config.port}")
            print(f"  Tier: {agent_config.tier}")
            print(f"  Quality Domain: {agent_config.quality_domain}")
            print(f"  Temperature: {agent_config.temperature}")
            print(f"  Model: {agent_config.model}")
            print(f"  Capabilities: {', '.join(agent_config.capabilities)}")


async def demonstrate_agent_with_config():
    """Demonstrate creating an agent that uses centralized config."""
    print("\n=== Agent with Centralized Config Demo ===")
    
    # Create agent that will load config automatically
    agent = ConfigDemoAgent(
        agent_name="master_orchestrator",
        description="",  # Will be loaded from config
        instructions="",  # Will be loaded from config
    )
    
    print(f"\nAgent Configuration Loaded:")
    print(f"  Name: {agent.agent_name}")
    print(f"  Description: {agent.description}")
    print(f"  Temperature: {agent.get_agent_temperature()}")
    print(f"  Model: {agent.get_model_name()}")
    print(f"  MCP Tools: {agent.mcp_tools_enabled}")
    print(f"  A2A Enabled: {agent.a2a_client is not None}")


def demonstrate_config_validation():
    """Demonstrate configuration validation."""
    print("\n=== Configuration Validation Demo ===")
    
    config_manager = ConfigManager()
    
    # Validate configuration
    issues = config_manager.validate()
    
    if issues:
        print("\nValidation Issues Found:")
        for issue in issues:
            print(f"  ⚠️  {issue}")
    else:
        print("\n✅ Configuration is valid!")


def demonstrate_dynamic_config():
    """Demonstrate dynamic configuration updates."""
    print("\n=== Dynamic Configuration Demo ===")
    
    config_manager = ConfigManager()
    
    # Add a new agent dynamically
    new_agent = AgentConfig(
        agent_id="custom_agent",
        name="Custom Demo Agent",
        port=10999,
        tier=3,
        description="Dynamically added agent",
        quality_domain="SERVICE",
        temperature=0.5,
        capabilities=["demo", "testing"]
    )
    
    config_manager.add_agent_config(new_agent)
    print(f"\nAdded new agent: {new_agent.name}")
    
    # Verify it was added
    retrieved = config_manager.get_agent_config("custom_agent")
    if retrieved:
        print(f"  Retrieved: {retrieved.name} on port {retrieved.port}")


def create_example_config():
    """Create an example configuration file."""
    print("\n=== Creating Example Configuration ===")
    
    example_config = {
        "framework_version": "2.0",
        "environment": "development",
        "log_level": "INFO",
        "mcp_server": {
            "host": "localhost",
            "port": 10099,
            "transport": "sse"
        },
        "connection_pool": {
            "enabled": True,
            "max_connections_per_host": 10,
            "keepalive_timeout": 30
        },
        "quality": {
            "domain": "GENERIC",
            "validation_enabled": True,
            "thresholds": {
                "accuracy": 0.8,
                "completeness": 0.9,
                "relevance": 0.85
            }
        },
        "features": {
            "response_formatting_v2": True,
            "connection_pooling": True,
            "quality_validation": True,
            "prometheus_metrics": False
        },
        "agents": {
            "example_agent": {
                "name": "Example Agent",
                "port": 10500,
                "tier": 2,
                "description": "Example configuration",
                "quality_domain": "SERVICE",
                "temperature": 0.1,
                "model": "gemini-2.0-flash",
                "capabilities": ["example", "demo"]
            }
        }
    }
    
    # Save to file
    example_path = Path("example_config.yaml")
    with open(example_path, 'w') as f:
        yaml.dump(example_config, f, default_flow_style=False)
    
    print(f"Created example configuration at: {example_path}")
    print("\nExample usage:")
    print("  export A2A_MCP_CONFIG_FILE=example_config.yaml")
    print("  python your_agent.py")


async def main():
    """Run all configuration demonstrations."""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║        Centralized Configuration Management Demo              ║
    ╚══════════════════════════════════════════════════════════════╝
    
    This demo shows Framework V2.0's centralized configuration system
    including loading, validation, environment overrides, and usage.
    """)
    
    # Run demonstrations
    demonstrate_config_loading()
    demonstrate_environment_overrides()
    demonstrate_agent_configuration()
    await demonstrate_agent_with_config()
    demonstrate_config_validation()
    demonstrate_dynamic_config()
    create_example_config()
    
    print("\n" + "="*60)
    print("Centralized Configuration Benefits:")
    print("1. Single source of truth for all settings")
    print("2. Environment variable overrides for deployment")
    print("3. Type-safe configuration with validation")
    print("4. Dynamic configuration updates")
    print("5. Consistent settings across all agents")
    print("="*60)


if __name__ == "__main__":
    # Clean up env vars from demo
    env_vars_to_clean = [
        'A2A_MCP_LOG_LEVEL',
        'A2A_MCP_ENVIRONMENT',
        'A2A_MCP_CONNECTION_POOL_MAX_CONNECTIONS_PER_HOST',
        'A2A_MCP_FEATURES'
    ]
    
    # Run demo
    asyncio.run(main())
    
    # Clean up
    for var in env_vars_to_clean:
        os.environ.pop(var, None)