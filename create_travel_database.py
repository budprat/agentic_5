#!/usr/bin/env python3
"""Create travel database with tables and sample data in Snowflake."""

import os
import snowflake.connector
from dotenv import load_dotenv
import random
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

def get_connection():
    """Create Snowflake connection."""
    return snowflake.connector.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        database='SNOWFLAKE',  # Start with default database
        schema='PUBLIC'
    )

def create_travel_database():
    """Create travel database and tables."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Create database
        print("Creating TRAVEL database...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS TRAVEL")
        cursor.execute("USE DATABASE TRAVEL")
        cursor.execute("USE SCHEMA PUBLIC")
        
        # Create travel_destinations table
        print("Creating travel_destinations table...")
        cursor.execute("""
            CREATE OR REPLACE TABLE travel_destinations (
                destination_id NUMBER AUTOINCREMENT PRIMARY KEY,
                region VARCHAR(50) NOT NULL,
                country VARCHAR(100) NOT NULL,
                country_code VARCHAR(3),
                capital_city VARCHAR(100),
                latitude DECIMAL(10, 6) NOT NULL,
                longitude DECIMAL(10, 6) NOT NULL,
                created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
            )
        """)
        
        # Create travel_flights table
        print("Creating travel_flights table...")
        cursor.execute("""
            CREATE OR REPLACE TABLE travel_flights (
                flight_id NUMBER AUTOINCREMENT PRIMARY KEY,
                flight_number VARCHAR(10) NOT NULL UNIQUE,
                airline_code VARCHAR(3) NOT NULL,
                source_country VARCHAR(100) NOT NULL,
                destination_country VARCHAR(100) NOT NULL,
                departure_time TIME NOT NULL,
                arrival_time TIME NOT NULL,
                flight_duration_hours DECIMAL(4, 2),
                aircraft_type VARCHAR(50),
                created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
            )
        """)
        
        # Create travel_passengers table
        print("Creating travel_passengers table...")
        cursor.execute("""
            CREATE OR REPLACE TABLE travel_passengers (
                passenger_id NUMBER AUTOINCREMENT PRIMARY KEY,
                customer_id VARCHAR(20) NOT NULL UNIQUE,
                customer_name VARCHAR(200) NOT NULL,
                email VARCHAR(200),
                phone_number VARCHAR(20),
                flight_number VARCHAR(10) NOT NULL,
                booking_date DATE DEFAULT CURRENT_DATE(),
                seat_number VARCHAR(5),
                ticket_class VARCHAR(20) DEFAULT 'ECONOMY',
                created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                FOREIGN KEY (flight_number) REFERENCES travel_flights(flight_number)
            )
        """)
        
        print("✅ Database and tables created successfully!")
        
    except Exception as e:
        print(f"Error creating database/tables: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def generate_sample_data():
    """Generate sample data for all tables."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("USE DATABASE TRAVEL")
        cursor.execute("USE SCHEMA PUBLIC")
        
        # Sample data for destinations
        destinations = [
            # Asia
            ('Asia', 'India', 'IN', 'New Delhi', 28.6139, 77.2090),
            ('Asia', 'China', 'CN', 'Beijing', 39.9042, 116.4074),
            ('Asia', 'Japan', 'JP', 'Tokyo', 35.6762, 139.6503),
            ('Asia', 'Thailand', 'TH', 'Bangkok', 13.7563, 100.5018),
            ('Asia', 'Singapore', 'SG', 'Singapore', 1.3521, 103.8198),
            ('Asia', 'South Korea', 'KR', 'Seoul', 37.5665, 126.9780),
            ('Asia', 'Malaysia', 'MY', 'Kuala Lumpur', 3.1390, 101.6869),
            ('Asia', 'Indonesia', 'ID', 'Jakarta', -6.2088, 106.8456),
            ('Asia', 'Vietnam', 'VN', 'Hanoi', 21.0285, 105.8542),
            ('Asia', 'Philippines', 'PH', 'Manila', 14.5995, 120.9842),
            # Europe
            ('Europe', 'Germany', 'DE', 'Berlin', 52.5200, 13.4050),
            ('Europe', 'France', 'FR', 'Paris', 48.8566, 2.3522),
            ('Europe', 'United Kingdom', 'GB', 'London', 51.5074, -0.1278),
            ('Europe', 'Italy', 'IT', 'Rome', 41.9028, 12.4964),
            ('Europe', 'Spain', 'ES', 'Madrid', 40.4168, -3.7038),
            ('Europe', 'Netherlands', 'NL', 'Amsterdam', 52.3702, 4.8952),
            ('Europe', 'Switzerland', 'CH', 'Bern', 46.9480, 7.4474),
            ('Europe', 'Poland', 'PL', 'Warsaw', 52.2297, 21.0122),
            ('Europe', 'Greece', 'GR', 'Athens', 37.9838, 23.7275),
            ('Europe', 'Portugal', 'PT', 'Lisbon', 38.7223, -9.1393),
            # Americas
            ('Americas', 'United States', 'US', 'Washington D.C.', 38.9072, -77.0369),
            ('Americas', 'Canada', 'CA', 'Ottawa', 45.4215, -75.6972),
            ('Americas', 'Brazil', 'BR', 'Brasília', -15.8267, -47.9218),
            ('Americas', 'Mexico', 'MX', 'Mexico City', 19.4326, -99.1332),
            ('Americas', 'Argentina', 'AR', 'Buenos Aires', -34.6037, -58.3816),
            ('Americas', 'Chile', 'CL', 'Santiago', -33.4489, -70.6693),
            ('Americas', 'Peru', 'PE', 'Lima', -12.0464, -77.0428),
            ('Americas', 'Colombia', 'CO', 'Bogotá', 4.7110, -74.0721),
            # Africa
            ('Africa', 'South Africa', 'ZA', 'Pretoria', -25.7479, 28.2293),
            ('Africa', 'Egypt', 'EG', 'Cairo', 30.0444, 31.2357),
            ('Africa', 'Kenya', 'KE', 'Nairobi', -1.2921, 36.8219),
            ('Africa', 'Nigeria', 'NG', 'Abuja', 9.0765, 7.3986),
            ('Africa', 'Morocco', 'MA', 'Rabat', 33.9716, -6.8498),
            # Oceania
            ('Oceania', 'Australia', 'AU', 'Canberra', -35.2809, 149.1300),
            ('Oceania', 'New Zealand', 'NZ', 'Wellington', -41.2865, 174.7762),
        ]
        
        # Insert destinations and create more to reach 100
        print("Inserting travel destinations...")
        all_destinations = []
        for dest in destinations:
            all_destinations.append(dest)
        
        # Generate additional destinations to reach 100
        while len(all_destinations) < 100:
            base_dest = random.choice(destinations)
            # Create variations with nearby cities
            lat_offset = random.uniform(-2, 2)
            lon_offset = random.uniform(-2, 2)
            city_suffix = random.choice(['North', 'South', 'East', 'West', 'Central'])
            new_dest = (
                base_dest[0],
                base_dest[1],
                base_dest[2],
                f"{city_suffix} {base_dest[3]}",
                base_dest[4] + lat_offset,
                base_dest[5] + lon_offset
            )
            all_destinations.append(new_dest)
        
        cursor.executemany("""
            INSERT INTO travel_destinations (region, country, country_code, capital_city, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, all_destinations[:100])
        
        # Generate flight data
        print("Inserting travel flights...")
        airlines = ['AA', 'BA', 'LH', 'AF', 'EK', 'SQ', 'QF', 'AI', 'CX', 'JL', 'KL', 'TG']
        aircraft_types = ['Boeing 737', 'Boeing 777', 'Boeing 787', 'Airbus A320', 'Airbus A350', 'Airbus A380']
        countries = [d[1] for d in destinations]
        
        flights = []
        for i in range(100):
            airline = random.choice(airlines)
            flight_num = f"{airline}{1000 + i}"
            source = random.choice(countries)
            dest = random.choice([c for c in countries if c != source])
            
            # Generate departure and arrival times
            dep_hour = random.randint(0, 23)
            dep_min = random.randint(0, 59)
            duration_hours = random.uniform(1, 15)
            arr_hour = (dep_hour + int(duration_hours)) % 24
            arr_min = random.randint(0, 59)
            
            flights.append((
                flight_num,
                airline,
                source,
                dest,
                f"{dep_hour:02d}:{dep_min:02d}:00",
                f"{arr_hour:02d}:{arr_min:02d}:00",
                round(duration_hours, 2),
                random.choice(aircraft_types)
            ))
        
        cursor.executemany("""
            INSERT INTO travel_flights 
            (flight_number, airline_code, source_country, destination_country, 
             departure_time, arrival_time, flight_duration_hours, aircraft_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, flights)
        
        # Generate passenger data
        print("Inserting travel passengers...")
        first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emma', 'Robert', 'Lisa', 
                      'William', 'Mary', 'James', 'Patricia', 'Richard', 'Jennifer', 'Charles',
                      'Raj', 'Priya', 'Chen', 'Wei', 'Yuki', 'Akira', 'Carlos', 'Maria']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
                     'Davis', 'Rodriguez', 'Martinez', 'Wilson', 'Anderson', 'Taylor', 'Thomas',
                     'Kumar', 'Patel', 'Wang', 'Li', 'Tanaka', 'Suzuki', 'Silva', 'Santos']
        
        passengers = []
        classes = ['ECONOMY', 'ECONOMY', 'ECONOMY', 'PREMIUM_ECONOMY', 'BUSINESS', 'FIRST']
        
        for i in range(100):
            customer_id = f"CUST{100000 + i}"
            first = random.choice(first_names)
            last = random.choice(last_names)
            name = f"{first} {last}"
            email = f"{first.lower()}.{last.lower()}{i}@email.com"
            phone = f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            flight = random.choice(flights)[0]  # Get flight number
            seat = f"{random.randint(1, 40)}{random.choice(['A', 'B', 'C', 'D', 'E', 'F'])}"
            ticket_class = random.choice(classes)
            
            passengers.append((
                customer_id,
                name,
                email,
                phone,
                flight,
                seat,
                ticket_class
            ))
        
        cursor.executemany("""
            INSERT INTO travel_passengers 
            (customer_id, customer_name, email, phone_number, flight_number, seat_number, ticket_class)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, passengers)
        
        conn.commit()
        print("✅ Sample data inserted successfully!")
        
        # Show sample counts
        cursor.execute("SELECT COUNT(*) FROM travel_destinations")
        dest_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM travel_flights")
        flight_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM travel_passengers")
        passenger_count = cursor.fetchone()[0]
        
        print(f"\n📊 Data Summary:")
        print(f"  - Destinations: {dest_count} rows")
        print(f"  - Flights: {flight_count} rows")
        print(f"  - Passengers: {passenger_count} rows")
        
        # Show sample data
        print("\n📋 Sample Data:")
        
        print("\n🌍 Travel Destinations (first 5):")
        cursor.execute("SELECT * FROM travel_destinations LIMIT 5")
        for row in cursor.fetchall():
            print(f"  {row}")
        
        print("\n✈️ Travel Flights (first 5):")
        cursor.execute("SELECT * FROM travel_flights LIMIT 5")
        for row in cursor.fetchall():
            print(f"  {row}")
        
        print("\n👥 Travel Passengers (first 5):")
        cursor.execute("SELECT * FROM travel_passengers LIMIT 5")
        for row in cursor.fetchall():
            print(f"  {row}")
        
    except Exception as e:
        print(f"Error generating sample data: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🚀 Creating Travel Database in Snowflake...")
    create_travel_database()
    generate_sample_data()
    print("\n✅ Travel database setup complete!")