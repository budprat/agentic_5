---
description: Guidelines for creating Google ADK-based agents using the crash course examples
globs: 
  - "**/*agent*.py"
  - "**/agents/**"
  - "agent-development-kit-crash-course/**"
alwaysApply: true
---
# Google ADK Agent Development Guidelines

When creating agents based on Google ADK, ALWAYS reference and use patterns from the `agent-development-kit-crash-course/` folder.

## ADK Crash Course Reference

The crash course contains 12 progressive examples that teach essential ADK patterns:

### Example Selection Guide

1. **Basic Agent (Example 1)** - Use when:
   - Creating a simple conversational agent
   - No tools or special features needed
   - Starting point for any ADK agent

2. **Tool Agent (Example 2)** - Use when:
   - Agent needs built-in tools (Code Execution, Google Search, Grounding)
   - Creating custom tools for specific functionality
   - **Important**: Only ONE built-in tool per agent allowed

3. **LiteLLM Agent (Example 3)** - Use when:
   - Need multi-provider model support
   - Want to use non-Google models (OpenAI, Anthropic, etc.)
   - Cost optimization across providers

4. **Structured Output (Example 4)** - Use when:
   - Need validated, structured responses
   - Building APIs that return JSON
   - Data extraction or form processing

5. **Sessions & State (Example 5)** - Use when:
   - Building conversational agents with memory
   - Need to track user context across turns
   - Implementing personalized experiences

6. **Persistent Storage (Example 6)** - Use when:
   - Need long-term memory beyond sessions
   - Database integration required
   - Building production-ready agents

7. **Multi-Agent Basic (Example 7)** - Use when:
   - Task requires specialized sub-agents
   - Building orchestrator patterns
   - Delegating to domain experts

8. **Stateful Multi-Agent (Example 8)** - Use when:
   - Sub-agents need shared state
   - Complex workflows with interdependencies
   - Building sophisticated agent teams

9. **Callbacks (Example 9)** - Use when:
   - Need monitoring/logging
   - Implementing security filters
   - Custom response processing

10. **Sequential Workflow (Example 10)** - Use when:
    - Tasks must execute in order
    - Building step-by-step processes
    - Pipeline-style architectures

11. **Parallel Workflow (Example 11)** - Use when:
    - Tasks can run simultaneously
    - Performance optimization needed
    - Independent subtask processing

12. **Loop Agent (Example 12)** - Use when:
    - Iterative refinement needed
    - Quality improvement cycles
    - Self-correcting systems

## Implementation Checklist

When creating a new ADK agent:

1. **Choose Base Example**:
   - [ ] Identify which example(s) best match your use case
   - [ ] Copy the relevant folder structure
   - [ ] Review the example's README for specific patterns

2. **Follow ADK Structure**:
   ```
   your_agent/
   ├── agent.yaml          # Agent configuration
   ├── requirements.txt    # Dependencies
   └── src/
       └── agent_name.py   # Agent implementation
   ```

3. **Key Patterns to Follow**:
   - [ ] Use `BaseAgent` class from ADK
   - [ ] Implement `run()` method for agent logic
   - [ ] Use proper async patterns for I/O operations
   - [ ] Follow tool limitations (one built-in tool max)
   - [ ] Use template variables for state access: `{var_name}`

4. **Model Selection**:
   - Default: `gemini-2.0-flash-exp` for cost-effective general use
   - Complex reasoning: `gemini-2.0-pro` or `gemini-2.5-pro`
   - Check `agent-development-kit-crash-course/GEMINI_MODELS.md` for details

5. **Common Pitfalls to Avoid**:
   - Don't mix built-in and custom tools in same agent
   - Built-in tools unavailable in sub-agents
   - State variables must be accessed via template syntax
   - Always handle async operations properly

## Integration with A2A Framework

When integrating ADK agents into A2A:

1. **Inherit from StandardizedAgentBase**:
   ```python
   from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
   from google.genai.adk import BaseAgent
   
   class YourADKAgent(StandardizedAgentBase):
       def __init__(self):
           self.adk_agent = BaseAgent(...)
   ```

2. **Use A2A Protocol**:
   - Wrap ADK responses in A2A protocol format
   - Handle memory integration if needed
   - Follow tier hierarchy (orchestrator/specialist/service)

3. **Reference Examples**:
   - `src/a2a_mcp/agents/example_travel_domain/adk_travel_agent.py`
   - `examples/travel/adk_travel_agent.py`

## Production Considerations

1. **Cost Optimization**:
   - Use flash models for high-volume operations
   - Reserve pro models for complex reasoning
   - Implement caching where appropriate

2. **Error Handling**:
   - Always wrap ADK calls in try-except
   - Implement retry logic for transient failures
   - Log errors for debugging

3. **Testing**:
   - Test with example inputs from crash course
   - Verify tool integrations work correctly
   - Check state management in multi-turn conversations

## Quick Reference Commands

```bash
# Generate new ADK agent from template
python scripts/generate_agent.py --type adk --name your_agent --example 7

# Test ADK agent
cd agent-development-kit-crash-course/7-multi-agent
python src/multi_agent.py

# Review specific example
cat agent-development-kit-crash-course/[1-12]-*/README.md
```

Remember: ALWAYS start from a working example in the crash course rather than building from scratch!