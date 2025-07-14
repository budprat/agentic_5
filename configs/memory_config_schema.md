# Memory Configuration Schema

This document describes the memory configuration options available for agents in the A2A-MCP framework.

## Global Memory Configuration (framework.yaml)

```yaml
memory:
  enabled: false  # Global flag to enable/disable memory services
  default_provider: "vertex_ai_memory_bank"
  providers:
    vertex_ai_memory_bank:
      project_id: "${GOOGLE_CLOUD_PROJECT}"
      location: "${GOOGLE_CLOUD_LOCATION:-us-central1}"
      agent_engine_id: "${VERTEX_AI_AGENT_ENGINE_ID}"
      batch_size: 10
      search_top_k: 5
      metadata_filters:
        - "app_name"
        - "user_id"
        - "session_id"
  session:
    auto_save_interval: 300  # seconds
    max_events_per_session: 1000
    retention_days: 90
  search:
    include_metadata: true
    max_results: 10
    similarity_threshold: 0.7
```

## Agent-Level Memory Configuration

### In framework.yaml agents section:

```yaml
agents:
  my_agent:
    # ... other config ...
    memory:
      enabled: true
      provider: "vertex_ai_memory_bank"  # Optional, uses default if not specified
      app_name: "my_agent"  # Required for filtering
      search_before_response: true
      auto_save_sessions: true
      context_window: 10  # Number of previous interactions to consider
```

### In agent card JSON files:

```json
{
  "configuration": {
    "memory": {
      "enabled": true,
      "provider": "vertex_ai_memory_bank",
      "app_name": "my_agent",
      "settings": {
        "search_before_response": true,
        "auto_save_sessions": true,
        "save_interval": 300,
        "context_window": 20,
        "search_top_k": 5,
        "similarity_threshold": 0.75,
        "metadata_tags": ["domain", "user_id", "session_type"],
        "retention_policy": {
          "days": 90,
          "important_sessions": 365
        }
      },
      "session_config": {
        "track_tool_calls": true,
        "track_a2a_interactions": true,
        "summarize_long_sessions": true,
        "max_events_per_session": 500
      },
      "search_config": {
        "include_system_prompts": false,
        "include_tool_outputs": true,
        "format": "conversational"
      }
    }
  }
}
```

## Configuration Options Explained

### Provider Settings

- **enabled**: Enable/disable memory for this agent
- **provider**: Memory provider to use (defaults to framework setting)
- **app_name**: Unique identifier for this agent's memory namespace

### Memory Settings

- **search_before_response**: Automatically search memory before generating responses
- **auto_save_sessions**: Save conversations to memory automatically
- **save_interval**: How often to save ongoing sessions (seconds)
- **context_window**: Number of previous messages to include as context
- **search_top_k**: Number of memory results to retrieve
- **similarity_threshold**: Minimum similarity score for memory results
- **metadata_tags**: Additional metadata fields to track

### Session Configuration

- **track_tool_calls**: Include tool usage in memory
- **track_a2a_interactions**: Include agent-to-agent communications
- **summarize_long_sessions**: Create summaries for long conversations
- **max_events_per_session**: Maximum events before starting new session

### Search Configuration

- **include_system_prompts**: Include system prompts in search results
- **include_tool_outputs**: Include tool outputs in search results
- **format**: Output format for memory results ("conversational", "structured")

## Environment Variables

The following environment variables can override memory settings:

```bash
# Global memory settings
export A2A_MCP_MEMORY_ENABLED=true
export A2A_MCP_MEMORY_DEFAULT_PROVIDER=vertex_ai_memory_bank

# Vertex AI specific
export GOOGLE_CLOUD_PROJECT=my-project-id
export GOOGLE_CLOUD_LOCATION=us-central1
export VERTEX_AI_AGENT_ENGINE_ID=my-agent-engine-id

# Override specific agent memory settings
export A2A_MCP_AGENTS_MY_AGENT_MEMORY_ENABLED=true
export A2A_MCP_AGENTS_MY_AGENT_MEMORY_APP_NAME=my_custom_app_name
```

## Usage Patterns

### 1. Basic Memory-Enabled Agent

```yaml
my_agent:
  memory:
    enabled: true
    app_name: "my_agent"
```

### 2. Context-Aware Specialist

```yaml
specialist:
  memory:
    enabled: true
    app_name: "domain_specialist"
    search_before_response: true
    context_window: 20
```

### 3. Session-Tracking Orchestrator

```yaml
orchestrator:
  memory:
    enabled: true
    app_name: "master_orchestrator"
    auto_save_sessions: true
    search_before_response: true
```

### 4. Minimal Memory Service

```yaml
service_agent:
  memory:
    enabled: false  # Service agents might not need memory
```

## Best Practices

1. **App Name Convention**: Use snake_case matching the agent name
2. **Context Window**: Start with 10-20 messages, adjust based on needs
3. **Search Threshold**: 0.7-0.8 for general use, 0.8-0.9 for precise matching
4. **Metadata Tags**: Include tags that help filter memories by context
5. **Save Interval**: 300s (5 min) is good default, reduce for critical conversations
6. **Retention**: Consider compliance requirements when setting retention days

## Memory Provider Support

Currently supported:
- **vertex_ai_memory_bank**: Google Vertex AI Agent Engine Memory Bank

Future support planned:
- **pinecone**: Pinecone vector database
- **chromadb**: Local ChromaDB instance
- **weaviate**: Weaviate vector search
- **custom**: Bring your own memory implementation