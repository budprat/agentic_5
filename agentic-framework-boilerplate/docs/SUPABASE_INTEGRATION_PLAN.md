# Supabase Database Integration Plan for A2A-MCP

## Current State Analysis
- **Current Database**: SQLite (`travel_agency.db`) with 3 tables: flights, hotels, rental_cars
- **Supabase Project**: Already configured with project URL `https://clvnttpnofghgolxkrqx.supabase.co`
- **MCP Integration**: Supabase MCP server already configured in `.mcp.json`
- **Data Structure**: Well-defined schema with sample travel data

## Migration Strategy

### Phase 1: Supabase Schema Setup
1. **Create Supabase migrations** for travel agency tables:
   - `flights` table with carriers, routes, classes, pricing
   - `hotels` table with accommodations, types, locations, rates
   - `rental_cars` table with providers, vehicle types, rates
2. **Apply migrations** using Supabase CLI
3. **Seed data** from existing SQLite database

### Phase 2: Application Integration
1. **Update MCP Server** (`src/a2a_mcp/mcp/server.py`):
   - Replace SQLite connections with Supabase client
   - Modify `query_travel_data` tool to use Supabase REST API
   - Add Supabase authentication and connection handling
2. **Environment Configuration**:
   - Add Supabase credentials to `.env.example`
   - Configure Supabase client initialization
3. **Database Client Integration**:
   - Install `supabase-py` client library
   - Create Supabase connection utilities

### Phase 3: Enhanced Features
1. **Real-time capabilities**:
   - Add subscription support for live travel data updates
   - Implement real-time booking status notifications
2. **Advanced queries**:
   - Leverage PostgREST for complex filtering and joins
   - Add full-text search for travel options
3. **Row Level Security (RLS)**:
   - Implement policies for data access control
   - Add user-specific booking history

### Phase 4: Agent Enhancements
1. **Booking Management**:
   - Add actual booking creation/storage
   - Implement booking confirmation and tracking
2. **User Profiles**:
   - Store user preferences and booking history
   - Personalized travel recommendations
3. **Analytics Dashboard**:
   - Track booking patterns and popular destinations
   - Revenue and usage metrics

## Technical Implementation Details

### Database Schema Migration
```sql
-- flights table with enhanced fields
CREATE TABLE flights (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  carrier text NOT NULL,
  flight_number text NOT NULL,
  from_airport text NOT NULL,
  to_airport text NOT NULL,
  departure_time timestamptz,
  arrival_time timestamptz,
  ticket_class text NOT NULL,
  price decimal NOT NULL,
  available_seats integer,
  created_at timestamptz DEFAULT now()
);

-- hotels table with enhanced fields
CREATE TABLE hotels (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  name text NOT NULL,
  city text NOT NULL,
  country text,
  hotel_type text NOT NULL,
  room_type text NOT NULL,
  price_per_night decimal NOT NULL,
  available_rooms integer,
  amenities text[],
  rating decimal(2,1),
  created_at timestamptz DEFAULT now()
);

-- rental_cars table with enhanced fields
CREATE TABLE rental_cars (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  provider text NOT NULL,
  city text NOT NULL,
  country text,
  type_of_car text NOT NULL,
  daily_rate decimal NOT NULL,
  available_count integer,
  features text[],
  fuel_type text,
  created_at timestamptz DEFAULT now()
);

-- bookings table for tracking reservations
CREATE TABLE bookings (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id uuid,
  booking_type text NOT NULL, -- 'flight', 'hotel', 'car'
  item_id uuid NOT NULL,
  status text DEFAULT 'pending', -- 'pending', 'confirmed', 'cancelled'
  booking_details jsonb,
  total_amount decimal,
  booking_date timestamptz DEFAULT now(),
  travel_date timestamptz
);
```

### MCP Tool Updates
- Replace SQLite queries with Supabase REST API calls
- Add error handling for network requests
- Implement connection pooling and retry logic

### Benefits
1. **Scalability**: Cloud-native database with automatic scaling
2. **Real-time**: Live updates and subscriptions
3. **Security**: Built-in authentication and RLS
4. **Performance**: Optimized queries and caching
5. **Monitoring**: Built-in analytics and logging
6. **Backup**: Automatic backups and point-in-time recovery

## Execution Order
1. Set up Supabase schema and migrations
2. Migrate existing data from SQLite
3. Update MCP server to use Supabase
4. Test all agent workflows
5. Implement enhanced features
6. Add monitoring and analytics

## Environment Variables Needed
```bash
# Supabase Configuration
SUPABASE_URL=https://clvnttpnofghgolxkrqx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Dependencies to Add
```toml
# Add to pyproject.toml
supabase = ">=2.0.0"
postgrest = ">=0.14.0"
```

This plan maintains backward compatibility while adding powerful cloud database capabilities to the A2A-MCP framework.

---
**Status**: APPROVED - Ready for implementation
**Date**: December 26, 2025
**Version**: 1.0