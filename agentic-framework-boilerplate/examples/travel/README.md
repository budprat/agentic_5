# Travel Domain Implementation Examples

This directory contains travel-specific implementations demonstrating how to customize the A2A-MCP framework for the travel industry.

## Files

### `adk_travel_agent.py`
**Original ADK Travel Agent Implementation**

This file preserves the original travel-specific implementation that served as the foundation for the generic `ADKServiceAgent` template. It demonstrates:

**Key Patterns for Travel Domain**:
- Travel-specific agent naming (`TravelAgent`)
- Domain-specific error messages (booking-related)
- Example of domain-specialized ADK integration
- Original implementation before generalization

**Usage as Reference**:
This implementation shows how the generic `ADKServiceAgent` can be specialized for travel:

```python
# Original pattern (preserved for reference)
class TravelAgent(BaseAgent):
    def __init__(self, agent_name: str, description: str, instructions: str):
        # Travel-specific initialization

# Modern pattern (using generic template)
from adk_service_agent import ADKServiceAgent

travel_agent = ADKServiceAgent(
    agent_name='AirTicketingAgent',
    description='Book air tickets given criteria', 
    instructions=prompts.AIRFARE_COT_INSTRUCTIONS
)
```

### `prompts.py`
**Travel-Specific Prompts and Instructions**

Contains Chain-of-Thought (CoT) instructions for travel domain agents:
- `AIRFARE_COT_INSTRUCTIONS` - Flight booking prompts
- Travel-specific reasoning patterns
- Domain expertise for travel agents

### `types.py`
**Travel Domain Data Types**

Contains travel-specific Pydantic models:
- `TripInfo` - Complete trip information structure
- `TravelTaskList` - Travel planning task organization
- Travel-specific validation logic

## How to Use These Examples

### 1. **Reference Implementation**
Use `adk_travel_agent.py` to understand the original travel-specific patterns before they were generalized into the framework template.

### 2. **Domain Customization Guide**
See how travel-specific logic (prompts, types, validation) can be separated from generic infrastructure.

### 3. **Migration Example**
Shows the evolution from domain-specific agent to generic template usage:

**Before (domain-specific)**:
```python
travel_agent = TravelAgent(
    agent_name='AirTicketingAgent',
    description='Book air tickets',
    instructions=prompts.AIRFARE_COT_INSTRUCTIONS
)
```

**After (generic template)**:
```python
travel_agent = ADKServiceAgent(
    agent_name='AirTicketingAgent', 
    description='Book air tickets',
    instructions=prompts.AIRFARE_COT_INSTRUCTIONS
)
```

### 4. **Best Practices**
- **Separation of Concerns**: Infrastructure (ADK integration) vs Domain Logic (prompts, types)
- **Reusable Patterns**: Generic agent template + domain-specific configuration
- **Maintainability**: Single template supports multiple domains

## Domain Adaptation Pattern

This example demonstrates the recommended pattern for domain adaptation:

1. **Use Generic Template**: Start with `ADKServiceAgent` 
2. **Create Domain Assets**: Prompts, types, validation rules
3. **Configure for Domain**: Pass domain-specific instructions and configuration
4. **Maintain Separation**: Keep domain logic separate from infrastructure

This approach provides both reusability and domain specialization while maintaining clean architecture.