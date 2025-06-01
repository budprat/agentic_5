#!/usr/bin/env python3
"""Initialize the travel agency database with sample data."""

import sqlite3
import os

DB_FILE = 'travel_agency.db'

def init_database():
    """Create and populate the travel agency database."""
    
    # Remove existing database if it exists
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    
    # Create new database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            carrier TEXT NOT NULL,
            flight_number INTEGER NOT NULL,
            from_airport TEXT NOT NULL,
            to_airport TEXT NOT NULL,
            ticket_class TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE hotels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            hotel_type TEXT NOT NULL,
            room_type TEXT NOT NULL,
            price_per_night REAL NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE rental_cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider TEXT NOT NULL,
            city TEXT NOT NULL,
            type_of_car TEXT NOT NULL,
            daily_rate REAL NOT NULL
        )
    ''')
    
    # Insert sample flight data
    flights_data = [
        ('United Airlines', 101, 'SFO', 'LHR', 'ECONOMY', 850.00),
        ('United Airlines', 102, 'SFO', 'LHR', 'BUSINESS', 3200.00),
        ('British Airways', 201, 'SFO', 'LHR', 'ECONOMY', 920.00),
        ('British Airways', 202, 'SFO', 'LHR', 'FIRST', 5500.00),
        ('Virgin Atlantic', 301, 'SFO', 'LHR', 'ECONOMY', 880.00),
        ('United Airlines', 103, 'LHR', 'SFO', 'ECONOMY', 850.00),
        ('United Airlines', 104, 'LHR', 'SFO', 'BUSINESS', 3200.00),
        ('British Airways', 203, 'LHR', 'SFO', 'ECONOMY', 920.00),
        ('British Airways', 204, 'LHR', 'SFO', 'FIRST', 5500.00),
        ('Virgin Atlantic', 302, 'LHR', 'SFO', 'ECONOMY', 880.00),
    ]
    
    cursor.executemany(
        'INSERT INTO flights (carrier, flight_number, from_airport, to_airport, ticket_class, price) VALUES (?, ?, ?, ?, ?, ?)',
        flights_data
    )
    
    # Insert sample hotel data
    hotels_data = [
        ('The Savoy', 'London', 'HOTEL', 'SUITE', 650.00),
        ('The Ritz London', 'London', 'HOTEL', 'SUITE', 850.00),
        ('Claridges', 'London', 'HOTEL', 'DOUBLE', 450.00),
        ('Premier Inn London', 'London', 'HOTEL', 'STANDARD', 120.00),
        ('Cozy London Flat', 'London', 'AIRBNB', 'DOUBLE', 180.00),
        ('Central London Loft', 'London', 'AIRBNB', 'SUITE', 280.00),
        ('Luxury Mayfair House', 'London', 'PRIVATE_PROPERTY', 'SUITE', 1200.00),
    ]
    
    cursor.executemany(
        'INSERT INTO hotels (name, city, hotel_type, room_type, price_per_night) VALUES (?, ?, ?, ?, ?)',
        hotels_data
    )
    
    # Insert sample car rental data
    rental_cars_data = [
        ('Hertz', 'London', 'SEDAN', 65.00),
        ('Hertz', 'London', 'SUV', 95.00),
        ('Avis', 'London', 'SEDAN', 70.00),
        ('Avis', 'London', 'SUV', 100.00),
        ('Enterprise', 'London', 'SEDAN', 60.00),
        ('Enterprise', 'London', 'TRUCK', 120.00),
        ('Budget', 'London', 'SEDAN', 55.00),
    ]
    
    cursor.executemany(
        'INSERT INTO rental_cars (provider, city, type_of_car, daily_rate) VALUES (?, ?, ?, ?)',
        rental_cars_data
    )
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"Database '{DB_FILE}' initialized successfully!")
    
    # Verify data
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM flights")
    flight_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM hotels")
    hotel_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM rental_cars")
    car_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"Inserted {flight_count} flights, {hotel_count} hotels, and {car_count} rental cars.")


if __name__ == "__main__":
    init_database()