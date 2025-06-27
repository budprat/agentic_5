# Market Oracle Configuration Guide

This guide walks you through configuring all API keys, MCP connections, and environment settings required to run the Market Oracle investment intelligence system.

## Prerequisites

- Python 3.11+
- `uv` package manager installed
- Access to required API services
- Docker (optional, for containerized deployment)

## 1. Environment Variables Setup

### Create `.env` file

First, create a `.env` file in the project root:

```bash
# Create .env file from template
cp .env.example .env
```

### Required API Keys

Add the following API keys to your `.env` file:

```bash
# Google API Key (Required for all agents using Gemini)
GOOGLE_API_KEY=your_google_api_key_here

# Reddit API (for Sentiment Seeker)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT="MarketOracle/1.0"

# BrightData API (for web scraping and SEC filings)
BRIGHTDATA_API_TOKEN=your_brightdata_token
BRIGHTDATA_CUSTOMER_ID=your_customer_id
BRIGHTDATA_ZONE=your_zone_name

# Brave Search API (for news and web search)
BRAVE_API_KEY=your_brave_api_key

# HuggingFace (for ML models)
HUGGINGFACE_API_KEY=your_huggingface_key

# Snowflake (for historical data)
SNOWFLAKE_ACCOUNT=your_account.region
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=MARKET_DATA
SNOWFLAKE_WAREHOUSE=COMPUTE_WH

# Supabase (for real-time data)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# n8n Webhooks (for automation)
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook
N8N_API_KEY=your_n8n_api_key

# Notion (for documentation)
NOTION_API_KEY=your_notion_integration_token
NOTION_DATABASE_ID=your_market_research_database_id

# ElevenLabs (for audio briefings)
ELEVENLABS_API_KEY=your_elevenlabs_key
ELEVENLABS_VOICE_ID=your_preferred_voice_id

# Google Trends (unofficial API)
GOOGLE_TRENDS_API_KEY=your_serpapi_key  # Using SerpAPI for trends

# Market Data Provider (optional)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
POLYGON_API_KEY=your_polygon_key
```

## 2. MCP Configuration

### Update `.mcp.json`

The Market Oracle system requires specific MCP configurations. Update your `.mcp.json` file:

```json
{
  "mcpServers": {
    "reddit": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-reddit"],
      "env": {
        "REDDIT_CLIENT_ID": "${REDDIT_CLIENT_ID}",
        "REDDIT_CLIENT_SECRET": "${REDDIT_CLIENT_SECRET}",
        "REDDIT_USER_AGENT": "${REDDIT_USER_AGENT}"
      }
    },
    "brightdata": {
      "type": "stdio",
      "command": "npx",
      "args": ["@brightdata/mcp"],
      "env": {
        "API_TOKEN": "${BRIGHTDATA_API_TOKEN}",
        "CUSTOMER_ID": "${BRIGHTDATA_CUSTOMER_ID}",
        "ZONE": "${BRIGHTDATA_ZONE}"
      }
    },
    "brave": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      }
    },
    "huggingface": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-huggingface"],
      "env": {
        "HUGGINGFACE_API_KEY": "${HUGGINGFACE_API_KEY}"
      }
    },
    "snowflake": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-snowflake"],
      "env": {
        "SNOWFLAKE_ACCOUNT": "${SNOWFLAKE_ACCOUNT}",
        "SNOWFLAKE_USER": "${SNOWFLAKE_USER}",
        "SNOWFLAKE_PASSWORD": "${SNOWFLAKE_PASSWORD}",
        "SNOWFLAKE_DATABASE": "${SNOWFLAKE_DATABASE}",
        "SNOWFLAKE_WAREHOUSE": "${SNOWFLAKE_WAREHOUSE}"
      }
    },
    "supabase": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@supabase/mcp-server-supabase"],
      "env": {
        "SUPABASE_URL": "${SUPABASE_URL}",
        "SUPABASE_ANON_KEY": "${SUPABASE_ANON_KEY}",
        "SUPABASE_SERVICE_ROLE_KEY": "${SUPABASE_SERVICE_ROLE_KEY}"
      }
    },
    "n8n": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@n8n/mcp-server-n8n"],
      "env": {
        "N8N_WEBHOOK_URL": "${N8N_WEBHOOK_URL}",
        "N8N_API_KEY": "${N8N_API_KEY}"
      }
    },
    "notion": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": {
        "NOTION_API_KEY": "${NOTION_API_KEY}"
      }
    },
    "elevenlabs": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@elevenlabs/mcp-server"],
      "env": {
        "ELEVENLABS_API_KEY": "${ELEVENLABS_API_KEY}",
        "ELEVENLABS_VOICE_ID": "${ELEVENLABS_VOICE_ID}"
      }
    },
    "google-trends": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-serpapi"],
      "env": {
        "SERPAPI_API_KEY": "${GOOGLE_TRENDS_API_KEY}"
      }
    }
  }
}
```

## 3. Agent-Specific Configuration

### Oracle Prime (Port 10501)

No additional configuration needed - uses Google API key from environment.

### Sentiment Seeker (Port 10502)

Configure Reddit API access:

1. Create Reddit App at https://www.reddit.com/prefs/apps
2. Choose "script" type
3. Add redirect URI: `http://localhost:8080`
4. Copy Client ID and Secret to `.env`

### Fundamental Analyst (Port 10503)

Configure BrightData for SEC filing access:

1. Create BrightData account
2. Set up Web Unlocker zone
3. Enable SEC EDGAR scraping
4. Add residential proxies for reliability

### Technical Prophet (Port 10504)

Configure HuggingFace models:

```python
# In technical_prophet_config.py
HUGGINGFACE_MODELS = {
    "price_prediction": "ProsusAI/finbert",
    "sentiment_analysis": "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis",
    "pattern_recognition": "custom/market-pattern-cnn"  # Your custom model
}
```

### Risk Guardian (Port 10505)

Configure portfolio limits:

```python
# In risk_guardian_config.py
RISK_LIMITS = {
    "max_position_size": 0.05,  # 5% of portfolio
    "max_daily_loss": 0.02,     # 2% daily loss limit
    "max_drawdown": 0.15,       # 15% maximum drawdown
    "correlation_limit": 0.40,   # 40% portfolio correlation
    "var_confidence": 0.95,      # 95% VaR
    "margin_requirement": 0.25   # 25% margin requirement
}
```

### Trend Correlator (Port 10506)

Configure Google Trends via SerpAPI:

```python
# In trend_correlator_config.py
TREND_SEARCH_PARAMS = {
    "engine": "google_trends",
    "geo": "US",  # or "GLOBAL"
    "timeframe": "today 3-m",  # 3 months
    "category": 7,  # Finance category
}
```

### Report Synthesizer (Port 10507)

Configure Notion workspace:

1. Create Notion integration at https://www.notion.so/my-integrations
2. Share your database with the integration
3. Create database with schema:
   ```
   - Title (title)
   - Symbol (text)
   - Analysis Date (date)
   - Recommendation (select: BUY/HOLD/SELL)
   - Target Price (number)
   - Risk Score (number)
   - Full Report (rich text)
   ```

### Audio Briefer (Port 10508)

Configure ElevenLabs voices:

```python
# In audio_briefer_config.py
VOICE_PROFILES = {
    "default": "21m00Tcm4TlvDq8ikWAM",  # Rachel
    "professional": "AZnzlk1XvdvUeBnXmlld",  # Domi
    "energetic": "EXAVITQu4vr4xnSDxMaL"  # Bella
}

AUDIO_SETTINGS = {
    "stability": 0.75,
    "similarity_boost": 0.75,
    "style": 0.5,
    "use_speaker_boost": True
}
```

## 4. Database Configuration

### Initialize Market Oracle Database

```bash
# Create and populate the database
python init_market_oracle_database.py
```

### Snowflake Historical Data Setup

```sql
-- Create Market Oracle schema in Snowflake
CREATE SCHEMA IF NOT EXISTS MARKET_ORACLE;

-- Historical price data table
CREATE TABLE MARKET_ORACLE.HISTORICAL_PRICES (
    symbol VARCHAR(10),
    date DATE,
    open DECIMAL(10,2),
    high DECIMAL(10,2),
    low DECIMAL(10,2),
    close DECIMAL(10,2),
    volume BIGINT,
    adjusted_close DECIMAL(10,2)
);

-- Grant permissions
GRANT USAGE ON SCHEMA MARKET_ORACLE TO ROLE MARKET_ORACLE_ROLE;
GRANT SELECT ON ALL TABLES IN SCHEMA MARKET_ORACLE TO ROLE MARKET_ORACLE_ROLE;
```

### Supabase Real-time Setup

```sql
-- Create real-time tables in Supabase
CREATE TABLE portfolios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    total_value DECIMAL(15,2),
    cash_balance DECIMAL(15,2),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Enable real-time
ALTER TABLE portfolios REPLICA IDENTITY FULL;

-- Create RLS policies
ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own portfolios" ON portfolios
    FOR SELECT USING (auth.uid()::text = user_id);
```

## 5. Service Dependencies

### Install Required NPM Packages

```bash
# Install all MCP servers
npm install -g \
  @modelcontextprotocol/server-reddit \
  @brightdata/mcp \
  @modelcontextprotocol/server-brave-search \
  @modelcontextprotocol/server-huggingface \
  @modelcontextprotocol/server-snowflake \
  @supabase/mcp-server-supabase \
  @n8n/mcp-server-n8n \
  @notionhq/notion-mcp-server \
  @elevenlabs/mcp-server \
  @modelcontextprotocol/server-serpapi
```

## 6. Launch Configuration

### Start All Services

Create a launch script `start_market_oracle.sh`:

```bash
#!/bin/bash

# Load environment variables
source .env

# Start MCP Server
echo "Starting MCP Server..."
uv run a2a-mcp --run mcp-server --transport sse --host localhost --port 10100 &
MCP_PID=$!

# Wait for MCP server to start
sleep 5

# Start Oracle Prime
echo "Starting Oracle Prime..."
uv run src/a2a_mcp/agents/ --agent-card agent_cards/oracle_prime_agent.json --port 10501 &

# Start Sentiment Seeker
echo "Starting Sentiment Seeker..."
uv run src/a2a_mcp/agents/ --agent-card agent_cards/sentiment_seeker_agent.json --port 10502 &

# Start Fundamental Analyst
echo "Starting Fundamental Analyst..."
uv run src/a2a_mcp/agents/ --agent-card agent_cards/fundamental_analyst_agent.json --port 10503 &

# Continue for all agents...

echo "Market Oracle is running!"
echo "Access Oracle Prime at: http://localhost:10501"
```

### Docker Compose Configuration

For production deployment:

```yaml
version: '3.8'

services:
  mcp-server:
    build: .
    command: uv run a2a-mcp --run mcp-server --transport sse --host 0.0.0.0 --port 10100
    ports:
      - "10100:10100"
    env_file:
      - .env
    networks:
      - market-oracle

  oracle-prime:
    build: .
    command: uv run src/a2a_mcp/agents/ --agent-card agent_cards/oracle_prime_agent.json --port 10501
    ports:
      - "10501:10501"
    env_file:
      - .env
    depends_on:
      - mcp-server
    networks:
      - market-oracle

  # Additional services...

networks:
  market-oracle:
    driver: bridge
```

## 7. Testing Configuration

### Verify API Connections

Create `test_market_oracle_config.py`:

```python
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def test_apis():
    """Test all API connections."""
    
    # Test Google API
    if os.getenv('GOOGLE_API_KEY'):
        print("✅ Google API key configured")
    else:
        print("❌ Missing GOOGLE_API_KEY")
    
    # Test Reddit
    if os.getenv('REDDIT_CLIENT_ID') and os.getenv('REDDIT_CLIENT_SECRET'):
        print("✅ Reddit API configured")
    else:
        print("❌ Missing Reddit credentials")
    
    # Test BrightData
    if os.getenv('BRIGHTDATA_API_TOKEN'):
        print("✅ BrightData configured")
    else:
        print("❌ Missing BrightData token")
    
    # Continue for all services...

if __name__ == "__main__":
    asyncio.run(test_apis())
```

## 8. Production Considerations

### Rate Limiting

Configure rate limits to avoid API throttling:

```python
# In config/rate_limits.py
RATE_LIMITS = {
    "reddit": {"requests_per_minute": 60},
    "google_trends": {"requests_per_hour": 100},
    "brightdata": {"concurrent_requests": 5},
    "elevenlabs": {"characters_per_month": 100000}
}
```

### Monitoring

Set up monitoring with Prometheus:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'market-oracle'
    static_configs:
      - targets: 
        - 'localhost:10501'  # Oracle Prime
        - 'localhost:10502'  # Sentiment Seeker
        # ... other agents
```

### Backup Configuration

```bash
# Backup script
#!/bin/bash
# backup_market_oracle.sh

# Backup database
sqlite3 market_oracle.db ".backup 'backups/market_oracle_$(date +%Y%m%d).db'"

# Backup configuration
tar -czf backups/config_$(date +%Y%m%d).tar.gz .env .mcp.json agent_cards/

# Upload to S3 (optional)
aws s3 cp backups/ s3://your-bucket/market-oracle-backups/ --recursive
```

## 9. Troubleshooting

### Common Issues

1. **MCP Connection Failed**
   - Check MCP server is running on port 10100
   - Verify all NPM packages are installed
   - Check firewall settings

2. **API Rate Limits**
   - Implement exponential backoff
   - Use caching for frequently accessed data
   - Consider upgrading API plans

3. **Agent Communication Issues**
   - Verify all agents are registered with MCP server
   - Check JWT authentication is working
   - Review agent logs in `logs/` directory

### Debug Mode

Enable debug logging:

```bash
export MARKET_ORACLE_DEBUG=true
export LOG_LEVEL=DEBUG
```

## 10. Next Steps

1. **Get API Keys**: Sign up for all required services
2. **Configure Environment**: Set up `.env` file with your keys
3. **Install Dependencies**: Run npm and pip installations
4. **Initialize Database**: Run database setup scripts
5. **Start Services**: Launch MCP server and agents
6. **Test Integration**: Run demo script to verify setup
7. **Monitor Performance**: Set up logging and monitoring
8. **Optimize**: Tune rate limits and caching

For support, check the logs in the `logs/` directory or refer to the [Market Oracle README](MARKET_ORACLE_README.md).