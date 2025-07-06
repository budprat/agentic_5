# Travel Agent Architecture Guide

## Overview

The A2A-MCP travel booking system uses a sophisticated **unified agent architecture** where a single `TravelAgent` class powers all travel booking services through specialized configurations and prompts.

## Unified Agent Design

### Core Implementation

All travel booking services (flights, hotels, car rentals) use the same underlying `TravelAgent` class from `src/a2a_mcp/agents/adk_travel_agent.py`:

```python
class TravelAgent(BaseAgent):
    """Travel Agent backed by ADK."""
    
    def __init__(self, agent_name: str, description: str, instructions: str):
        init_api_key()
        super().__init__(
            agent_name=agent_name,
            description=description,
            content_types=['text', 'text/plain'],
        )
        self.instructions = instructions
        self.agent = None
```

### Service Specialization

Services are differentiated through three key mechanisms:

#### 1. Agent Cards Configuration
Each service has a unique JSON configuration in `agent_cards/`:

```json
// agent_cards/air_ticketing_agent.json
{
  "name": "Air Ticketing Agent",
  "description": "Specializes in booking flights and air travel arrangements",
  "port": 10103,
  "skills": ["flight booking", "airline search", "itinerary planning"]
}

// agent_cards/hotel_booking_agent.json  
{
  "name": "Hotel Booking Agent",
  "description": "Specializes in booking hotels and accommodations",
  "port": 10104,
  "skills": ["hotel booking", "accommodation search", "room selection"]
}

// agent_cards/car_rental_agent.json
{
  "name": "Car Rental Agent", 
  "description": "Specializes in booking rental cars and ground transportation",
  "port": 10105,
  "skills": ["car rental", "vehicle selection", "transportation planning"]
}
```

#### 2. Prompt Instructions Specialization
Each service uses specialized chain-of-thought prompts from `prompts.py`:

**Air Ticketing Instructions:**
```
CHAIN-OF-THOUGHT PROCESS for Flight Booking:
1. ORIGIN: Where is the departure location?
2. DESTINATION: Where is the arrival destination?
3. DEPARTURE_DATE: When do you want to depart?
4. RETURN_DATE: When do you want to return? (for round trips)
5. CLASS: What travel class? (economy/business/first)
6. SEARCH: Query flights database
7. BOOKING: Present options and facilitate booking
```

**Hotel Booking Instructions:**
```
CHAIN-OF-THOUGHT PROCESS for Hotel Booking:
1. CITY: Which city for accommodation?
2. CHECK_IN: What is the check-in date?
3. CHECK_OUT: What is the check-out date?
4. PROPERTY_TYPE: Hotel, Airbnb, or private property?
5. ROOM_TYPE: Standard, single, double, or suite?
6. SEARCH: Query hotels database
7. BOOKING: Present options and facilitate booking
```

**Car Rental Instructions:**
```
CHAIN-OF-THOUGHT PROCESS for Car Rental:
1. CITY: Which city for car rental?
2. PICKUP_DATE: When do you need the car?
3. RETURN_DATE: When will you return the car?
4. CAR_CLASS: Sedan, SUV, or truck?
5. SEARCH: Query rental cars database
6. BOOKING: Present options and facilitate booking
```

#### 3. Port-Based Service Isolation
Each service runs on a dedicated port for isolation:

- **Air Ticketing Agent**: Port 10103
- **Hotel Booking Agent**: Port 10104  
- **Car Rental Agent**: Port 10105

## Agent Instantiation Process

### Service Creation in `__main__.py`

The `get_agent()` function creates specialized TravelAgent instances:

```python
from a2a_mcp.agents.adk_travel_agent import TravelAgent
import prompts

def get_agent(agent_card: AgentCard):
    if agent_card.name == 'Air Ticketing Agent':
        return TravelAgent(
            agent_name='AirTicketingAgent',
            description='Book air tickets given a criteria',
            instructions=prompts.AIRFARE_COT_INSTRUCTIONS,
        )
    elif agent_card.name == 'Hotel Booking Agent':
        return TravelAgent(
            agent_name='HotelBookingAgent',
            description='Book hotels given a criteria',
            instructions=prompts.HOTELS_COT_INSTRUCTIONS,
        )
    elif agent_card.name == 'Car Rental Agent':
        return TravelAgent(
            agent_name='CarRentalBookingAgent',
            description='Book rental cars given a criteria',
            instructions=prompts.CARS_COT_INSTRUCTIONS,
        )
```

### Startup Process

Each service is started with its unique configuration:

```bash
# From run_all_agents.sh
uv run src/a2a_mcp/agents/ --agent-card agent_cards/air_ticketing_agent.json --port 10103 &
uv run src/a2a_mcp/agents/ --agent-card agent_cards/hotel_booking_agent.json --port 10104 &
uv run src/a2a_mcp/agents/ --agent-card agent_cards/car_rental_agent.json --port 10105 &
```

## Technical Integration

### Google ADK Integration

Each TravelAgent instance uses Google's Agent Development Kit:

```python
async def init_agent(self):
    # Connect to MCP server for tool discovery
    config = get_mcp_server_config()
    tools = await MCPToolset(
        connection_params=SseConnectionParams(url=config.url)
    ).get_tools()
    
    # Create Google ADK agent with MCP tools
    self.agent = Agent(
        name=self.agent_name,
        instruction=self.instructions,
        model='gemini-2.0-flash',
        disallow_transfer_to_parent=True,
        disallow_transfer_to_peers=True,
        generate_content_config=generate_content_config,
        tools=tools,
    )
```

### MCP Tool Integration

All TravelAgent instances share the same database access pattern:

```python
# Database queries via MCP tools
await session.call_tool(
    name='query_travel_data',
    arguments={
        'query': "SELECT * FROM flights WHERE from_airport='SFO' AND to_airport='LHR'"
    }
)
```

### Response Format Standardization

All services return consistent response formats:

```python
{
    'response_type': 'data',
    'is_task_complete': True,
    'require_user_input': False,
    'content': {
        'booking_type': 'flights',
        'options': [...],
        'recommendation': '...'
    }
}
```

## Interactive Workflow Patterns

### Chain-of-Thought Execution

Each TravelAgent follows a systematic decision tree:

1. **Information Gathering**: Collect required booking parameters
2. **Validation**: Ensure all necessary information is available
3. **Database Query**: Search relevant database tables via MCP tools
4. **Option Presentation**: Format and present available choices
5. **Booking Facilitation**: Guide user through selection process

### Input Request Handling

When information is missing, agents request user input:

```python
{
    'status': 'input_required',
    'question': 'What are your travel dates for the flight from San Francisco to London?',
    'is_task_complete': False,
    'require_user_input': True
}
```

### Context Preservation

Agents maintain conversation context across interactions:

```python
# Context stored in agent runner
context_data = {
    'origin': 'SFO',
    'destination': 'LHR', 
    'travel_dates': {'start': '2025-05-15', 'end': '2025-05-22'},
    'class_preference': 'business'
}
```

## Database Schema Integration

### Flights Table Access
```sql
SELECT carrier, flight_number, departure_time, arrival_time, price 
FROM flights 
WHERE from_airport=? AND to_airport=? AND ticket_class=?
```

### Hotels Table Access
```sql
SELECT name, hotel_type, room_type, price_per_night 
FROM hotels 
WHERE city=? AND hotel_type=?
```

### Car Rentals Table Access
```sql
SELECT provider, type_of_car, daily_rate 
FROM rental_cars 
WHERE city=? AND type_of_car=?
```

## Benefits of Unified Architecture

### 1. Code Reusability
- Single implementation serves multiple use cases
- Consistent behavior across all travel services
- Reduced maintenance overhead

### 2. Consistent User Experience
- Standardized interaction patterns
- Uniform response formats
- Predictable chain-of-thought workflows

### 3. Scalability
- Easy to add new travel services
- Shared infrastructure and tooling
- Consistent performance characteristics

### 4. Maintainability
- Single codebase for all travel booking logic
- Centralized bug fixes and improvements
- Simplified testing and deployment

## Adding New Travel Services

To add a new travel service using this architecture:

1. **Create Agent Card**: Define service metadata and skills
2. **Add Prompt Instructions**: Create service-specific chain-of-thought prompts
3. **Update Database Schema**: Add relevant tables if needed
4. **Extend `get_agent()`**: Add new service instantiation logic
5. **Assign Port**: Choose unique port for service isolation

This unified architecture demonstrates how a single, well-designed agent implementation can efficiently power multiple specialized services through configuration and prompt engineering.