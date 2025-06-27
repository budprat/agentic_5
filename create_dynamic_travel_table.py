#!/usr/bin/env python3
"""Create a dynamic table combining travel passengers and flights data."""

import os
import snowflake.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_connection():
    """Create Snowflake connection."""
    return snowflake.connector.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        database='TRAVEL',
        schema='PUBLIC'
    )

def analyze_common_keys():
    """Analyze the data to identify common keys between tables."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        print("🔍 Analyzing table structures and data...")
        
        # Check table schemas
        print("\n📋 TRAVEL_FLIGHTS columns:")
        cursor.execute("DESC TABLE travel_flights")
        flight_cols = cursor.fetchall()
        for col in flight_cols:
            print(f"  - {col[0]}: {col[1]}")
        
        print("\n📋 TRAVEL_PASSENGERS columns:")
        cursor.execute("DESC TABLE travel_passengers")
        passenger_cols = cursor.fetchall()
        for col in passenger_cols:
            print(f"  - {col[0]}: {col[1]}")
        
        # Check sample data to verify the relationship
        print("\n🔗 Checking common key: FLIGHT_NUMBER")
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT p.flight_number) as unique_passenger_flights,
                COUNT(DISTINCT f.flight_number) as unique_flight_numbers,
                COUNT(p.flight_number) as total_passenger_bookings
            FROM travel_passengers p
            FULL OUTER JOIN travel_flights f ON p.flight_number = f.flight_number
        """)
        result = cursor.fetchone()
        print(f"  - Unique flight numbers in passengers: {result[0]}")
        print(f"  - Unique flight numbers in flights: {result[1]}")
        print(f"  - Total passenger bookings: {result[2]}")
        
        # Verify the join works
        cursor.execute("""
            SELECT COUNT(*) 
            FROM travel_passengers p
            INNER JOIN travel_flights f ON p.flight_number = f.flight_number
        """)
        join_count = cursor.fetchone()[0]
        print(f"  - Successful joins: {join_count}")
        
        print("\n✅ Common key identified: FLIGHT_NUMBER")
        
    finally:
        cursor.close()
        conn.close()

def create_dynamic_table():
    """Create a dynamic table joining passengers and flights."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        print("\n🚀 Creating dynamic table...")
        
        # First, let's create a regular view to test the join
        print("Creating view PASSENGER_FLIGHT_DETAILS...")
        cursor.execute("""
            CREATE OR REPLACE VIEW passenger_flight_details AS
            SELECT 
                -- Passenger Information
                p.passenger_id,
                p.customer_id,
                p.customer_name,
                p.email,
                p.phone_number,
                p.booking_date,
                p.seat_number,
                p.ticket_class,
                
                -- Flight Information
                f.flight_number,
                f.airline_code,
                f.source_country,
                f.destination_country,
                f.departure_time,
                f.arrival_time,
                f.flight_duration_hours,
                f.aircraft_type,
                
                -- Calculated Fields
                CASE 
                    WHEN p.ticket_class = 'FIRST' THEN 'Priority'
                    WHEN p.ticket_class = 'BUSINESS' THEN 'Priority'
                    ELSE 'Standard'
                END AS boarding_group,
                
                CONCAT(f.source_country, ' → ', f.destination_country) AS route,
                
                -- Timestamps
                p.created_at AS booking_created_at,
                f.created_at AS flight_created_at
                
            FROM travel_passengers p
            INNER JOIN travel_flights f ON p.flight_number = f.flight_number
        """)
        
        print("✅ View created successfully!")
        
        # Now create a dynamic table (Snowflake feature for materialized views that auto-refresh)
        print("\nCreating dynamic table PASSENGER_FLIGHT_BOOKINGS...")
        cursor.execute("""
            CREATE OR REPLACE DYNAMIC TABLE passenger_flight_bookings
            TARGET_LAG = '1 minute'
            WAREHOUSE = COMPUTE_WH
            AS
            SELECT 
                -- Passenger Information
                p.passenger_id,
                p.customer_id,
                p.customer_name,
                p.email,
                p.phone_number,
                p.booking_date,
                p.seat_number,
                p.ticket_class,
                
                -- Flight Information
                f.flight_number,
                f.airline_code,
                f.source_country,
                f.destination_country,
                f.departure_time,
                f.arrival_time,
                f.flight_duration_hours,
                f.aircraft_type,
                
                -- Calculated Fields
                CASE 
                    WHEN p.ticket_class = 'FIRST' THEN 'Priority'
                    WHEN p.ticket_class = 'BUSINESS' THEN 'Priority'
                    ELSE 'Standard'
                END AS boarding_group,
                
                CONCAT(f.source_country, ' → ', f.destination_country) AS route,
                
                -- Additional Analytics Fields
                CASE 
                    WHEN f.flight_duration_hours < 2 THEN 'Short-haul'
                    WHEN f.flight_duration_hours < 6 THEN 'Medium-haul'
                    ELSE 'Long-haul'
                END AS flight_category,
                
                -- Timestamps
                p.created_at AS booking_created_at,
                f.created_at AS flight_created_at,
                CURRENT_TIMESTAMP() AS last_refreshed
                
            FROM travel_passengers p
            INNER JOIN travel_flights f ON p.flight_number = f.flight_number
        """)
        
        print("✅ Dynamic table created successfully!")
        
        # Create an aggregate dynamic table for analytics
        print("\nCreating aggregate dynamic table FLIGHT_BOOKING_STATS...")
        cursor.execute("""
            CREATE OR REPLACE DYNAMIC TABLE flight_booking_stats
            TARGET_LAG = '5 minutes'
            WAREHOUSE = COMPUTE_WH
            AS
            SELECT 
                f.flight_number,
                f.airline_code,
                f.source_country,
                f.destination_country,
                f.aircraft_type,
                
                -- Passenger Statistics
                COUNT(DISTINCT p.customer_id) AS total_passengers,
                COUNT(CASE WHEN p.ticket_class = 'ECONOMY' THEN 1 END) AS economy_passengers,
                COUNT(CASE WHEN p.ticket_class = 'PREMIUM_ECONOMY' THEN 1 END) AS premium_economy_passengers,
                COUNT(CASE WHEN p.ticket_class = 'BUSINESS' THEN 1 END) AS business_passengers,
                COUNT(CASE WHEN p.ticket_class = 'FIRST' THEN 1 END) AS first_class_passengers,
                
                -- Booking Insights
                MIN(p.booking_date) AS first_booking_date,
                MAX(p.booking_date) AS last_booking_date,
                
                -- Route Info
                CONCAT(f.source_country, ' → ', f.destination_country) AS route,
                f.flight_duration_hours,
                
                -- Last Update
                CURRENT_TIMESTAMP() AS stats_last_refreshed
                
            FROM travel_flights f
            LEFT JOIN travel_passengers p ON f.flight_number = p.flight_number
            GROUP BY 
                f.flight_number,
                f.airline_code,
                f.source_country,
                f.destination_country,
                f.aircraft_type,
                f.flight_duration_hours
        """)
        
        print("✅ Aggregate dynamic table created successfully!")
        
        # Show sample data from the dynamic tables
        print("\n📊 Sample Data from Dynamic Tables:")
        
        print("\n1️⃣ PASSENGER_FLIGHT_BOOKINGS (first 5 rows):")
        cursor.execute("SELECT * FROM passenger_flight_bookings LIMIT 5")
        columns = [desc[0] for desc in cursor.description]
        print(f"Columns: {', '.join(columns[:8])}...")  # Show first 8 columns
        
        for row in cursor.fetchall():
            print(f"  Customer: {row[2]}, Flight: {row[8]} ({row[10]} → {row[11]}), Class: {row[7]}")
        
        print("\n2️⃣ FLIGHT_BOOKING_STATS (Top 5 most booked flights):")
        cursor.execute("""
            SELECT 
                flight_number,
                route,
                total_passengers,
                economy_passengers,
                business_passengers,
                first_class_passengers
            FROM flight_booking_stats
            WHERE total_passengers > 0
            ORDER BY total_passengers DESC
            LIMIT 5
        """)
        
        for row in cursor.fetchall():
            print(f"  Flight {row[0]}: {row[1]} - {row[2]} passengers "
                  f"(Economy: {row[3]}, Business: {row[4]}, First: {row[5]})")
        
        # Get dynamic table status
        print("\n📈 Dynamic Table Status:")
        cursor.execute("""
            SHOW DYNAMIC TABLES LIKE '%passenger%' IN SCHEMA PUBLIC
        """)
        for row in cursor.fetchall():
            print(f"  - {row[1]} (Schema: {row[2]}, State: Active)")
        
    except Exception as e:
        print(f"Error creating dynamic tables: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🔄 Creating Dynamic Tables in Snowflake TRAVEL Database...")
    print("=" * 60)
    
    # First analyze the common keys
    analyze_common_keys()
    
    # Then create the dynamic tables
    create_dynamic_table()
    
    print("\n✅ Dynamic table setup complete!")
    print("\n📝 Summary:")
    print("  - Common Key: FLIGHT_NUMBER")
    print("  - View Created: PASSENGER_FLIGHT_DETAILS (real-time join)")
    print("  - Dynamic Table 1: PASSENGER_FLIGHT_BOOKINGS (refreshes every 1 minute)")
    print("  - Dynamic Table 2: FLIGHT_BOOKING_STATS (refreshes every 5 minutes)")
    print("\n💡 Dynamic tables automatically refresh based on the TARGET_LAG setting!")