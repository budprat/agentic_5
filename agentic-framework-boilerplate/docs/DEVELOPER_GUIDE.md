# Developer Guide: Adding New Travel Services

## Overview

This guide demonstrates how to add new travel services to the A2A-MCP system using the existing unified TravelAgent architecture. We'll walk through adding a "Travel Insurance Agent" as a complete example.

## Understanding the Architecture

### Unified Agent Pattern

The A2A-MCP system uses a single `TravelAgent` class that powers all travel services through:
- **Agent Cards**: JSON configurations defining service metadata
- **Prompt Instructions**: Service-specific chain-of-thought workflows  
- **Port Assignment**: Unique ports for service isolation
- **Database Integration**: MCP tools for data access

### Existing Services Structure

```
Current Services:
├── Air Ticketing Agent (port 10103) - Flight booking
├── Hotel Booking Agent (port 10104) - Accommodation booking
└── Car Rental Agent (port 10105) - Vehicle rental
```

## Step-by-Step Implementation

### Step 1: Define Service Requirements

For our Travel Insurance Agent example:

**Service Requirements:**
- **Purpose**: Help travelers find and purchase travel insurance
- **Input**: Trip details, traveler information, coverage preferences
- **Output**: Insurance options with coverage details and pricing
- **Dependencies**: May require existing booking information
- **Database**: New table for insurance products

### Step 2: Create Database Schema

Add insurance-related tables to the database:

```sql
-- Add to init_database.py or create migration
CREATE TABLE travel_insurance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT NOT NULL,
    plan_name TEXT NOT NULL,
    coverage_type TEXT NOT NULL,  -- 'BASIC', 'COMPREHENSIVE', 'PREMIUM'
    trip_duration_max INTEGER NOT NULL,  -- Maximum trip length in days
    coverage_amount INTEGER NOT NULL,     -- Coverage amount in USD
    premium_per_day REAL NOT NULL,       -- Daily premium cost
    medical_coverage INTEGER DEFAULT 0,   -- Medical coverage amount
    baggage_coverage INTEGER DEFAULT 0,   -- Baggage coverage amount
    trip_cancellation BOOLEAN DEFAULT 0,  -- Trip cancellation coverage
    emergency_evacuation BOOLEAN DEFAULT 0 -- Emergency evacuation coverage
);

-- Sample data
INSERT INTO travel_insurance VALUES
(1, 'TravelGuard', 'Essential Plan', 'BASIC', 30, 50000, 8.50, 25000, 1000, 1, 0),
(2, 'World Nomads', 'Explorer Plan', 'COMPREHENSIVE', 365, 100000, 12.75, 100000, 2500, 1, 1),
(3, 'Allianz', 'Premium Protection', 'PREMIUM', 180, 250000, 18.90, 250000, 5000, 1, 1),
(4, 'IMG Global', 'Patriot Travel', 'BASIC', 364, 75000, 6.25, 50000, 1500, 1, 0),
(5, 'Seven Corners', 'Liaison Majestic', 'COMPREHENSIVE', 364, 200000, 15.40, 150000, 3000, 1, 1);
```

### Step 3: Create Agent Card Configuration

Create `agent_cards/travel_insurance_agent.json`:

```json
{
  "name": "Travel Insurance Agent",
  "description": "Specializes in finding and recommending travel insurance policies based on trip details and coverage needs",
  "port": 10106,
  "version": "1.0.0",
  "auth_required": false,
  "auth_schemes": [
    {
      "type": "bearer",
      "scheme": "bearer", 
      "bearerFormat": "JWT"
    }
  ],
  "skills": [
    "travel insurance search",
    "coverage analysis", 
    "premium calculation",
    "policy recommendation",
    "claims information",
    "coverage comparison"
  ],
  "specializations": [
    "medical coverage",
    "trip cancellation",
    "baggage protection", 
    "emergency evacuation",
    "adventure sports coverage",
    "pre-existing conditions"
  ],
  "supported_regions": ["worldwide"],
  "supported_trip_types": [
    "business travel",
    "leisure travel", 
    "adventure travel",
    "family vacation",
    "solo travel",
    "group travel"
  ],
  "response_format": {
    "type": "structured",
    "schema": "insurance_options"
  }
}
```

### Step 4: Create Chain-of-Thought Instructions

Add to `src/a2a_mcp/agents/prompts.py`:

```python
TRAVEL_INSURANCE_COT_INSTRUCTIONS = """
You are a Travel Insurance Agent specialized in helping travelers find the right insurance coverage for their trips.

CHAIN-OF-THOUGHT PROCESS for Travel Insurance:

1. TRIP_DETAILS: What are the trip details?
   - If unknown, ask: "Could you provide your trip details including destination, dates, and purpose of travel?"

2. TRAVELER_INFO: Who is traveling?
   - If unknown, ask: "How many travelers, and what are their ages? Any pre-existing medical conditions?"

3. COVERAGE_NEEDS: What coverage is needed?
   - If unknown, ask: "What type of coverage are you looking for? (medical, cancellation, baggage, etc.)"

4. BUDGET: What is the budget for insurance?
   - If unknown, ask: "What's your budget range for travel insurance?"

5. SEARCH: Query insurance database
   - Use trip duration, destination, and coverage needs to find suitable policies

6. COMPARISON: Present options with coverage analysis
   - Compare coverage limits, exclusions, and premiums
   - Highlight recommended option based on needs

7. BOOKING: Provide next steps for purchase
   - Explain application process and required documentation

DECISION TREE:
├── Trip Details Available? 
│   ├── Yes → Check Traveler Info
│   └── No → Ask for trip destination, dates, duration, purpose
├── Traveler Info Available?
│   ├── Yes → Check Coverage Needs  
│   └── No → Ask for number of travelers, ages, medical conditions
├── Coverage Needs Known?
│   ├── Yes → Check Budget
│   └── No → Ask about preferred coverage types
├── Budget Defined?
│   ├── Yes → Search Insurance Database
│   └── No → Ask for premium budget range
├── Search Results Available?
│   ├── Yes → Present Recommendations
│   └── No → Suggest Alternative Coverage
└── Ready to Book?
    ├── Yes → Provide Booking Instructions
    └── No → Answer Additional Questions

When providing recommendations, always include:
- Coverage details and limits
- Premium costs (daily and total)
- Key exclusions and limitations  
- Claims process information
- Comparison with other options

Output Format (JSON):
{
  "booking_type": "travel_insurance",
  "search_criteria": {
    "destination": "destination country/region",
    "trip_duration": "number of days",
    "travelers": "number and demographics",
    "coverage_type": "coverage preferences"
  },
  "options": [
    {
      "provider": "insurance company name",
      "plan_name": "plan name",
      "coverage_type": "BASIC/COMPREHENSIVE/PREMIUM", 
      "total_premium": "total cost for trip",
      "daily_premium": "cost per day",
      "coverage_highlights": {
        "medical": "medical coverage amount",
        "baggage": "baggage coverage amount", 
        "cancellation": "trip cancellation coverage",
        "evacuation": "emergency evacuation included"
      },
      "key_benefits": ["benefit1", "benefit2"],
      "exclusions": ["exclusion1", "exclusion2"]
    }
  ],
  "recommendation": "recommended option with reasoning",
  "next_steps": ["step1", "step2"]
}

Use available MCP tools to query the travel_insurance database for suitable policies.
"""
```

### Step 5: Update Agent Factory

Modify `src/a2a_mcp/agents/__main__.py`:

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
    # NEW: Add Travel Insurance Agent
    elif agent_card.name == 'Travel Insurance Agent':
        return TravelAgent(
            agent_name='TravelInsuranceAgent',
            description='Find and recommend travel insurance policies',
            instructions=prompts.TRAVEL_INSURANCE_COT_INSTRUCTIONS,
        )
    # ... other agent types
```

### Step 6: Update Startup Scripts

Modify `run_all_agents.sh`:

```bash
#!/bin/bash

# Start MCP Server first
echo "Starting MCP Server..."
uv run a2a-mcp --run mcp-server --transport sse --host localhost --port 10100 &
sleep 2

# Start Orchestrator Agent
echo "Starting Orchestrator Agent..."
uv run src/a2a_mcp/agents/ --agent-card agent_cards/orchestrator_agent.json --port 10101 &

# Start Planner Agent
echo "Starting Planner Agent..."
uv run src/a2a_mcp/agents/ --agent-card agent_cards/planner_agent.json --port 10102 &

# Start Travel Service Agents
echo "Starting Travel Service Agents..."
uv run src/a2a_mcp/agents/ --agent-card agent_cards/air_ticketing_agent.json --port 10103 &
uv run src/a2a_mcp/agents/ --agent-card agent_cards/hotel_booking_agent.json --port 10104 &
uv run src/a2a_mcp/agents/ --agent-card agent_cards/car_rental_agent.json --port 10105 &

# NEW: Start Travel Insurance Agent
echo "Starting Travel Insurance Agent..."
uv run src/a2a_mcp/agents/ --agent-card agent_cards/travel_insurance_agent.json --port 10106 &

echo "All agents started. Check logs/ directory for individual agent logs."
echo "Services available:"
echo "  MCP Server: http://localhost:10100"
echo "  Orchestrator: http://localhost:10101" 
echo "  Planner: http://localhost:10102"
echo "  Air Ticketing: http://localhost:10103"
echo "  Hotel Booking: http://localhost:10104"
echo "  Car Rental: http://localhost:10105"
echo "  Travel Insurance: http://localhost:10106"
```

### Step 7: Update Database Initialization

Modify `init_database.py`:

```python
import sqlite3

def init_database():
    """Initialize the travel agency database with sample data."""
    conn = sqlite3.connect('travel_agency.db')
    cursor = conn.cursor()
    
    # Existing tables: flights, hotels, rental_cars
    # ... existing code ...
    
    # NEW: Create travel insurance table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS travel_insurance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        provider TEXT NOT NULL,
        plan_name TEXT NOT NULL, 
        coverage_type TEXT NOT NULL,
        trip_duration_max INTEGER NOT NULL,
        coverage_amount INTEGER NOT NULL,
        premium_per_day REAL NOT NULL,
        medical_coverage INTEGER DEFAULT 0,
        baggage_coverage INTEGER DEFAULT 0,
        trip_cancellation BOOLEAN DEFAULT 0,
        emergency_evacuation BOOLEAN DEFAULT 0
    )
    ''')
    
    # Insert sample insurance data
    insurance_data = [
        ('TravelGuard', 'Essential Plan', 'BASIC', 30, 50000, 8.50, 25000, 1000, 1, 0),
        ('World Nomads', 'Explorer Plan', 'COMPREHENSIVE', 365, 100000, 12.75, 100000, 2500, 1, 1),
        ('Allianz', 'Premium Protection', 'PREMIUM', 180, 250000, 18.90, 250000, 5000, 1, 1),
        ('IMG Global', 'Patriot Travel', 'BASIC', 364, 75000, 6.25, 50000, 1500, 1, 0),
        ('Seven Corners', 'Liaison Majestic', 'COMPREHENSIVE', 364, 200000, 15.40, 150000, 3000, 1, 1)
    ]
    
    cursor.executemany('''
        INSERT INTO travel_insurance 
        (provider, plan_name, coverage_type, trip_duration_max, coverage_amount, 
         premium_per_day, medical_coverage, baggage_coverage, trip_cancellation, emergency_evacuation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', insurance_data)
    
    conn.commit()
    conn.close()
    print("Database initialized with travel insurance data")

if __name__ == "__main__":
    init_database()
```

### Step 8: Update MCP Server Agent Registry

The MCP server automatically discovers new agent cards, but you may want to update the registry CSV if used:

```csv
# agent_registry.csv (if used)
name,description,port,agent_card_path
Air Ticketing Agent,Specializes in booking flights,10103,agent_cards/air_ticketing_agent.json
Hotel Booking Agent,Specializes in booking hotels,10104,agent_cards/hotel_booking_agent.json  
Car Rental Agent,Specializes in booking rental cars,10105,agent_cards/car_rental_agent.json
Travel Insurance Agent,Specializes in travel insurance,10106,agent_cards/travel_insurance_agent.json
```

### Step 9: Test the New Service

Create `test_insurance_agent.py`:

```python
#!/usr/bin/env python3
import asyncio
import json
import httpx

async def test_insurance_agent():
    """Test the Travel Insurance Agent."""
    
    # Test query
    query = "I need travel insurance for a 10-day trip to Europe for 2 adults"
    
    # Create request
    request_data = {
        "message": {
            "role": "user",
            "parts": [{"kind": "text", "text": query}]
        }
    }
    
    # Send to agent
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:10106/",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("Travel Insurance Agent Response:")
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {response.status_code} - {response.text}")

# Also test via orchestrator
async def test_via_orchestrator():
    """Test insurance agent via orchestrator."""
    
    query = "Plan a trip to Japan including flights, hotel, and travel insurance"
    
    request_data = {
        "message": {
            "role": "user", 
            "parts": [{"kind": "text", "text": query}]
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:10101/",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("Orchestrator Response (with Insurance):")
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    asyncio.run(test_insurance_agent())
    print("\n" + "="*50 + "\n")
    asyncio.run(test_via_orchestrator())
```

### Step 10: Update Documentation

Update `CLAUDE.md` to reflect the new service:

```markdown
# Task Agents
uv run src/a2a_mcp/agents/ --agent-card agent_cards/air_ticketing_agent.json --port 10103
uv run src/a2a_mcp/agents/ --agent-card agent_cards/hotel_booking_agent.json --port 10104
uv run src/a2a_mcp/agents/ --agent-card agent_cards/car_rental_agent.json --port 10105
uv run src/a2a_mcp/agents/ --agent-card agent_cards/travel_insurance_agent.json --port 10106
```

## Advanced Customization Options

### Custom Validation Logic

Add service-specific validation in the TravelAgent class:

```python
# In adk_travel_agent.py - add validation method
def validate_insurance_request(self, query: str) -> dict:
    """Validate travel insurance request parameters."""
    
    required_fields = ['destination', 'trip_duration', 'travelers']
    missing_fields = []
    
    # Extract fields from query (simplified)
    if 'destination' not in query.lower():
        missing_fields.append('destination')
    if not any(word in query.lower() for word in ['day', 'week', 'month']):
        missing_fields.append('trip_duration')
    if not any(word in query.lower() for word in ['adult', 'traveler', 'person']):
        missing_fields.append('travelers')
    
    return {
        'valid': len(missing_fields) == 0,
        'missing_fields': missing_fields
    }
```

### Custom Response Processing

Add insurance-specific response formatting:

```python
# In adk_travel_agent.py - extend format_response method
def format_insurance_response(self, response: str) -> dict:
    """Format travel insurance specific responses."""
    
    base_response = self.format_response(response)
    
    # Add insurance-specific enhancements
    if base_response.get('booking_type') == 'travel_insurance':
        # Add premium calculations
        for option in base_response.get('options', []):
            if 'daily_premium' in option and 'trip_duration' in base_response.get('search_criteria', {}):
                duration = base_response['search_criteria']['trip_duration']
                option['total_premium'] = option['daily_premium'] * duration
        
        # Add coverage comparisons
        base_response['coverage_comparison'] = self.generate_coverage_comparison(
            base_response.get('options', [])
        )
    
    return base_response
```

### Integration with Existing Workflow

The new Travel Insurance Agent will automatically integrate with the orchestrator through:

1. **Agent Discovery**: MCP server will match insurance-related queries to the new agent
2. **Workflow Integration**: Orchestrator can include insurance in multi-service bookings
3. **Parallel Execution**: Insurance searches can run alongside other booking tasks

Example integrated workflow:
```
User: "Plan a complete trip to Tokyo with flights, hotel, car, and insurance"

Orchestrator → Planner → Task Decomposition:
├── Flight Booking (parallel)
├── Hotel Booking (parallel)  
├── Car Rental (parallel)
└── Travel Insurance (parallel)

All tasks execute concurrently, reducing total time from ~20s to ~8s
```

## Testing and Validation

### Unit Tests

Create `tests/test_insurance_agent.py`:

```python
import pytest
import asyncio
from unittest.mock import Mock, patch
from src.a2a_mcp.agents.adk_travel_agent import TravelAgent
import prompts

class TestTravelInsuranceAgent:
    
    @pytest.fixture
    def insurance_agent(self):
        return TravelAgent(
            agent_name='TravelInsuranceAgent',
            description='Find and recommend travel insurance policies',
            instructions=prompts.TRAVEL_INSURANCE_COT_INSTRUCTIONS,
        )
    
    def test_agent_initialization(self, insurance_agent):
        assert insurance_agent.agent_name == 'TravelInsuranceAgent'
        assert 'travel insurance' in insurance_agent.instructions.lower()
    
    @patch('src.a2a_mcp.agents.adk_travel_agent.MCPToolset')
    async def test_insurance_search(self, mock_toolset, insurance_agent):
        # Mock MCP tool response
        mock_tools = Mock()
        mock_toolset.return_value.get_tools.return_value = [mock_tools]
        
        # Test query
        query = "Travel insurance for 7-day Europe trip for 2 adults"
        
        # This would test the actual agent flow
        # Implementation depends on your testing framework
        assert True  # Placeholder
    
    def test_prompt_instructions(self, insurance_agent):
        instructions = insurance_agent.instructions
        
        # Verify key elements are in the prompt
        assert 'TRIP_DETAILS' in instructions
        assert 'COVERAGE_NEEDS' in instructions
        assert 'travel_insurance' in instructions
        assert 'JSON' in instructions
```

### Integration Tests

```python
# tests/test_insurance_integration.py
import pytest
import httpx
import asyncio

@pytest.mark.asyncio
async def test_insurance_agent_endpoint():
    """Test Travel Insurance Agent via HTTP."""
    
    query = {
        "message": {
            "role": "user",
            "parts": [{"kind": "text", "text": "Insurance for Tokyo trip"}]
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:10106/",
            json=query,
            timeout=30.0
        )
        
        assert response.status_code == 200
        result = response.json()
        assert 'booking_type' in str(result).lower() or 'insurance' in str(result).lower()

@pytest.mark.asyncio  
async def test_orchestrator_with_insurance():
    """Test insurance integration via orchestrator."""
    
    query = {
        "message": {
            "role": "user",
            "parts": [{"kind": "text", "text": "Plan trip with flights, hotel, and insurance"}]
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:10101/",
            json=query,
            timeout=60.0
        )
        
        assert response.status_code == 200
        # Verify insurance is included in orchestrated response
        result = response.json()
        assert 'insurance' in str(result).lower()
```

## Best Practices

### 1. Agent Card Design
- **Clear Skills**: Define specific skills that help with agent discovery
- **Accurate Description**: Write descriptions that match common user queries
- **Proper Categorization**: Use appropriate specializations and supported types

### 2. Prompt Engineering
- **Structured Flow**: Follow the established chain-of-thought pattern
- **Clear Questions**: Ask specific, actionable questions for missing information
- **Consistent Output**: Use standardized JSON response format
- **Error Handling**: Include guidance for edge cases and errors

### 3. Database Design
- **Normalized Schema**: Design efficient database schema for your service
- **Sample Data**: Include representative sample data for testing
- **Performance**: Consider indexing for common query patterns

### 4. Testing Strategy
- **Unit Tests**: Test individual agent components
- **Integration Tests**: Test agent within the system
- **End-to-End Tests**: Test complete workflows including your service
- **Performance Tests**: Verify response times and resource usage

### 5. Documentation
- **Agent Documentation**: Document your service's capabilities and usage
- **API Documentation**: Document any new endpoints or parameters
- **User Guide**: Provide examples of how to use your service

## Troubleshooting Common Issues

### Agent Not Discovered
- **Check Agent Card**: Verify JSON syntax and required fields
- **Verify Embeddings**: Ensure MCP server has processed your agent card
- **Test Queries**: Try different query phrasings to match your agent

### Database Connection Issues
- **Table Creation**: Ensure database tables are created properly
- **Data Population**: Verify sample data is inserted correctly
- **Query Syntax**: Test SQL queries manually before using in agent

### Response Format Problems
- **JSON Validation**: Ensure response format is valid JSON
- **Schema Consistency**: Match the expected response schema
- **Error Handling**: Implement proper error response formats

This comprehensive developer guide demonstrates how the unified TravelAgent architecture makes it straightforward to add new travel services while maintaining consistency and leveraging existing infrastructure for agent discovery, tool integration, and workflow orchestration.