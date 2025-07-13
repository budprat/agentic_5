#!/usr/bin/env python3
# ABOUTME: Example travel MCP server using the generic template with Google Places and travel database
# ABOUTME: Demonstrates real-world usage patterns for API and database tool integration

"""
Travel MCP Server Example

This example shows how to use the GenericMCPServerTemplate to create
a travel services MCP server with:
- Google Places API integration  
- Travel database queries
- Custom travel-specific tools

Usage:
    python examples/travel_mcp_server_example.py

Environment Variables Required:
    GOOGLE_PLACES_API_KEY - Your Google Places API key
    TRAVEL_DB - Path to SQLite travel database (optional, defaults to travel.db)
"""

import os
import sys
import sqlite3
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from a2a_mcp.common.generic_mcp_server_template import (
    GenericMCPServerTemplate,
    APIConfig,
    DatabaseConfig,
    create_google_places_tool,
    create_travel_database_tool
)


def setup_travel_database(db_path: str):
    """Set up sample travel database for demo."""
    
    # Create sample data if database doesn't exist
    if not os.path.exists(db_path):
        print(f"Creating sample travel database at {db_path}")
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Airlines table
            cursor.execute('''
                CREATE TABLE airlines (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    code TEXT NOT NULL,
                    country TEXT,
                    fleet_size INTEGER,
                    founded_year INTEGER
                )
            ''')
            
            # Hotels table
            cursor.execute('''
                CREATE TABLE hotels (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    city TEXT NOT NULL,
                    country TEXT NOT NULL,
                    stars INTEGER,
                    price_per_night REAL,
                    available_rooms INTEGER
                )
            ''')
            
            # Car rentals table
            cursor.execute('''
                CREATE TABLE car_rentals (
                    id INTEGER PRIMARY KEY,
                    company TEXT NOT NULL,
                    location TEXT NOT NULL,
                    car_type TEXT NOT NULL,
                    price_per_day REAL,
                    available_cars INTEGER
                )
            ''')
            
            # Bookings table
            cursor.execute('''
                CREATE TABLE bookings (
                    id INTEGER PRIMARY KEY,
                    customer_name TEXT NOT NULL,
                    booking_type TEXT NOT NULL,
                    service_id INTEGER,
                    booking_date TEXT,
                    status TEXT DEFAULT 'confirmed'
                )
            ''')
            
            # Insert sample data
            airlines_data = [
                ('American Airlines', 'AA', 'USA', 956, 1930),
                ('Lufthansa', 'LH', 'Germany', 273, 1953),
                ('Emirates', 'EK', 'UAE', 271, 1985),
                ('Singapore Airlines', 'SQ', 'Singapore', 138, 1972),
                ('British Airways', 'BA', 'UK', 273, 1974)
            ]
            
            cursor.executemany('''
                INSERT INTO airlines (name, code, country, fleet_size, founded_year)
                VALUES (?, ?, ?, ?, ?)
            ''', airlines_data)
            
            hotels_data = [
                ('Grand Hotel Central', 'Barcelona', 'Spain', 5, 450.0, 25),
                ('Hotel Okura Tokyo', 'Tokyo', 'Japan', 5, 380.0, 12),
                ('The Plaza', 'New York', 'USA', 5, 695.0, 8),
                ('Hotel Bristol', 'Vienna', 'Austria', 5, 520.0, 15),
                ('Burj Al Arab', 'Dubai', 'UAE', 7, 1200.0, 3)
            ]
            
            cursor.executemany('''
                INSERT INTO hotels (name, city, country, stars, price_per_night, available_rooms)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', hotels_data)
            
            car_rental_data = [
                ('Hertz', 'Los Angeles Airport', 'Economy', 45.0, 15),
                ('Avis', 'London Heathrow', 'Compact', 38.0, 22),
                ('Enterprise', 'Miami Beach', 'Luxury', 125.0, 5),
                ('Budget', 'Barcelona Center', 'SUV', 78.0, 8),
                ('Europcar', 'Paris CDG', 'Electric', 65.0, 12)
            ]
            
            cursor.executemany('''
                INSERT INTO car_rentals (company, location, car_type, price_per_day, available_cars)
                VALUES (?, ?, ?, ?, ?)
            ''', car_rental_data)
            
            booking_data = [
                ('John Smith', 'flight', 1, '2024-02-15', 'confirmed'),
                ('Maria Garcia', 'hotel', 2, '2024-02-20', 'confirmed'),
                ('David Wilson', 'car', 3, '2024-02-18', 'pending'),
                ('Sarah Johnson', 'flight', 4, '2024-03-01', 'confirmed'),
                ('Ahmed Hassan', 'hotel', 5, '2024-02-25', 'cancelled')
            ]
            
            cursor.executemany('''
                INSERT INTO bookings (customer_name, booking_type, service_id, booking_date, status)
                VALUES (?, ?, ?, ?, ?)
            ''', booking_data)
            
            conn.commit()
            print("Sample travel database created successfully!")


def create_travel_recommendation_tool():
    """Create a custom travel recommendation tool."""
    def get_travel_recommendations(destination: str, budget: str, travel_type: str = "leisure"):
        """Generate travel recommendations based on destination and budget."""
        
        # Simple recommendation logic (in production, this would be more sophisticated)
        recommendations = {
            'destination': destination,
            'budget_category': budget,
            'travel_type': travel_type,
            'recommendations': []
        }
        
        budget_mapping = {
            'low': {'hotel_max': 100, 'car_max': 50},
            'medium': {'hotel_max': 300, 'car_max': 80}, 
            'high': {'hotel_max': 1000, 'car_max': 150}
        }
        
        budget_limits = budget_mapping.get(budget.lower(), budget_mapping['medium'])
        
        # Basic recommendations based on budget
        if budget.lower() == 'low':
            recommendations['recommendations'] = [
                "Look for budget airlines and book in advance",
                "Consider hostels or budget hotels under $100/night",
                "Use public transportation or economy car rentals",
                "Book accommodations outside city center for lower prices"
            ]
        elif budget.lower() == 'high':
            recommendations['recommendations'] = [
                "Consider premium airlines with good service",
                "Book luxury hotels with concierge services",
                "Rent premium or luxury vehicles", 
                "Look into private tour guides and exclusive experiences"
            ]
        else:
            recommendations['recommendations'] = [
                "Balance cost and comfort with mid-range options",
                "Look for 3-4 star hotels with good reviews",
                "Consider compact or standard car rentals",
                "Mix of popular attractions and local experiences"
            ]
        
        # Add destination-specific advice
        destination_lower = destination.lower()
        if any(city in destination_lower for city in ['tokyo', 'japan']):
            recommendations['recommendations'].append("Get a JR Pass for efficient train travel")
        elif any(city in destination_lower for city in ['london', 'uk', 'britain']):
            recommendations['recommendations'].append("Consider an Oyster Card for London transport")
        elif any(city in destination_lower for city in ['paris', 'france']):
            recommendations['recommendations'].append("Book museum passes in advance")
        
        return recommendations
    
    return get_travel_recommendations


def main():
    """Main function to run the travel MCP server."""
    print("🚀 Starting Travel Services MCP Server")
    
    # Configuration
    db_path = os.getenv('TRAVEL_DB', 'travel.db')
    host = os.getenv('MCP_HOST', 'localhost')
    port = int(os.getenv('MCP_PORT', '8080'))
    transport = os.getenv('MCP_TRANSPORT', 'stdio')
    
    # Set up database
    setup_travel_database(db_path)
    
    # Create MCP server
    travel_server = GenericMCPServerTemplate(
        server_name="travel-services",
        description="Comprehensive travel booking and search services",
        host=host,
        port=port,
        transport=transport
    )
    
    # Add Google Places API tool (exactly like your example)
    print("📍 Adding Google Places API integration...")
    places_config = create_google_places_tool()
    travel_server.add_api_tool("google_places", places_config)
    
    # Add travel database tool (exactly like your example)
    print("🗃️ Adding travel database integration...")
    travel_db_config = create_travel_database_tool(db_path)
    travel_server.add_database_tool("travel_db", travel_db_config)
    
    # Add custom travel recommendation tool
    print("🎯 Adding travel recommendation engine...")
    recommendation_func = create_travel_recommendation_tool()
    travel_server.add_custom_tool(
        name="get_travel_recommendations",
        description="Get personalized travel recommendations based on destination, budget, and travel type",
        handler_func=recommendation_func,
        parameters={
            "type": "object",
            "properties": {
                "destination": {"type": "string", "description": "Travel destination"},
                "budget": {"type": "string", "description": "Budget category: low, medium, high"},
                "travel_type": {"type": "string", "description": "Type of travel: leisure, business, adventure"}
            },
            "required": ["destination", "budget"]
        }
    )
    
    # Add schema information tool
    def get_database_schema():
        """Get travel database schema information."""
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            schema = {}
            for (table_name,) in tables:
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                schema[table_name] = [
                    {"name": col[1], "type": col[2], "nullable": not col[3]}
                    for col in columns
                ]
            
        return {"database_schema": schema}
    
    travel_server.add_custom_tool(
        name="get_database_schema",
        description="Get the schema of the travel database to help construct proper SQL queries",
        handler_func=get_database_schema,
        parameters={}
    )
    
    print(f"✅ Travel MCP Server configured with {len(travel_server.tool_handlers)} tools")
    print(f"🌐 Server will run on {host}:{port} using {transport} transport")
    
    # Check environment variables
    if not os.getenv('GOOGLE_PLACES_API_KEY'):
        print("⚠️  Warning: GOOGLE_PLACES_API_KEY not set. Google Places tool will return errors.")
    
    print("\n🎉 Starting MCP server...")
    
    # Run the server
    travel_server.run()


if __name__ == "__main__":
    main()