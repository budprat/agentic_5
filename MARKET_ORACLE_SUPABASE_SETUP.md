# Market Oracle Supabase Setup Guide

This guide walks you through setting up Supabase as the database backend for Market Oracle.

## Prerequisites

- Supabase account with a project created
- Supabase URL and API keys (already in your .env file)

## Step 1: Create Database Schema

1. **Go to your Supabase Dashboard**
   - Navigate to: https://app.supabase.com/project/udjwjoymlofdocclufxv
   - Click on "SQL Editor" in the left sidebar

2. **Run the Schema Creation Script**
   - Copy the entire contents of `init_supabase_market_oracle.sql`
   - Paste it into the SQL Editor
   - Click "Run" to execute

   This will create:
   - 8 tables for Market Oracle data
   - Proper indexes for performance
   - Row Level Security policies
   - Useful views and functions
   - Sample data for testing

## Step 2: Verify Tables Were Created

1. Go to "Table Editor" in the sidebar
2. You should see these tables:
   - `portfolios`
   - `positions`
   - `trading_signals`
   - `sentiment_data`
   - `risk_metrics`
   - `investment_research`
   - `market_trends`
   - `audio_briefings`

## Step 3: Install Python Dependencies

```bash
# Install Supabase Python client
pip install supabase
```

Or add to your requirements.txt:
```
supabase>=2.0.0
```

## Step 4: Configure Market Oracle for Supabase

Your `.env` file already contains:
```
SUPABASE_URL=https://udjwjoymlofdocclufxv.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

## Step 5: Update Agent Imports

To use the Supabase-enabled agents, update your imports:

```python
# Instead of:
from src.a2a_mcp.agents.market_oracle import OraclePrimeAgent

# Use:
from src.a2a_mcp.agents.market_oracle.oracle_prime_agent_supabase import OraclePrimeAgentSupabase
```

## Step 6: Test Supabase Connection

Create a test script:

```python
from src.a2a_mcp.common.supabase_client import SupabaseClient

# Test connection
client = SupabaseClient.get_client()

# Test query
response = client.table('portfolios').select("*").execute()
print(f"Portfolios: {response.data}")

# Test creating a signal
signal = client.table('trading_signals').insert({
    'symbol': 'AAPL',
    'signal_type': 'buy',
    'confidence_score': 0.85,
    'agent_name': 'test',
    'reasoning': 'Test signal'
}).execute()
print(f"Created signal: {signal.data}")
```

## Advantages of Using Supabase

1. **Real-time Updates**: Subscribe to changes in portfolios, signals, etc.
2. **Scalability**: PostgreSQL backend handles large datasets
3. **Security**: Built-in Row Level Security
4. **API Access**: REST API for external integrations
5. **Dashboard**: Visual database management

## Real-time Subscriptions (Optional)

Enable real-time features for live updates:

```python
# Subscribe to new trading signals
channel = client.channel('trading-signals')
channel.on('postgres_changes', 
          event='INSERT', 
          schema='public', 
          table='trading_signals', 
          callback=handle_new_signal)
channel.subscribe()

def handle_new_signal(payload):
    print(f"New signal: {payload['new']}")
```

## Database Backup

Supabase automatically backs up your database. You can also:

1. Go to Settings > Database
2. Click "Backups"
3. Download a backup or restore from a point in time

## Monitoring

1. **Database Metrics**: Settings > Database > Usage
2. **API Metrics**: Settings > API > Usage
3. **Query Performance**: SQL Editor > Query Performance

## Troubleshooting

### Connection Issues
- Verify your Supabase URL and keys are correct
- Check if your project is paused (free tier pauses after 1 week of inactivity)

### Permission Errors
- Make sure you're using the service role key for write operations
- Check RLS policies if getting empty results

### Performance
- Use the provided indexes
- Monitor slow queries in the dashboard
- Consider upgrading for better performance

## Next Steps

1. **Update all agents** to use Supabase client
2. **Create dashboard** using Supabase's built-in analytics
3. **Set up webhooks** for trade execution via n8n
4. **Enable real-time** portfolio updates
5. **Configure backups** for production use

## Migration from SQLite

If you have existing data in SQLite:

```python
import sqlite3
from supabase import create_client

# Connect to SQLite
sqlite_conn = sqlite3.connect('market_oracle.db')
sqlite_cursor = sqlite_conn.cursor()

# Connect to Supabase
supabase = create_client(url, key)

# Migrate portfolios
sqlite_cursor.execute("SELECT * FROM portfolios")
portfolios = sqlite_cursor.fetchall()
for portfolio in portfolios:
    supabase.table('portfolios').insert({
        'user_id': portfolio[1],
        'total_value': portfolio[2],
        'cash_balance': portfolio[3]
    }).execute()
```

The Market Oracle system is now configured to use Supabase as its database backend!