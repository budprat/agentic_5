# Market Oracle API Setup Guide

This guide provides step-by-step instructions for obtaining all the API keys required to run Market Oracle.

## Quick Reference Table

| Service | Purpose | Free Tier | Sign Up Link |
|---------|---------|-----------|--------------|
| Google AI | Core LLM for all agents | 15 RPM | [Google AI Studio](https://makersuite.google.com/app/apikey) |
| Reddit | Social sentiment analysis | 60 requests/min | [Reddit Apps](https://www.reddit.com/prefs/apps) |
| BrightData | SEC filings, web scraping | Trial available | [BrightData](https://brightdata.com) |
| Brave Search | News and web search | 2000 queries/month | [Brave Search API](https://brave.com/search/api/) |
| HuggingFace | ML models | Free tier available | [HuggingFace](https://huggingface.co/settings/tokens) |
| Snowflake | Historical data | 30-day trial | [Snowflake](https://signup.snowflake.com) |
| Supabase | Real-time database | Free tier | [Supabase](https://app.supabase.com) |
| n8n | Automation workflows | Self-hosted free | [n8n](https://n8n.io) |
| Notion | Documentation | Free tier | [Notion Integrations](https://www.notion.so/my-integrations) |
| ElevenLabs | Voice synthesis | 10K chars/month | [ElevenLabs](https://elevenlabs.io) |
| SerpAPI | Google Trends | 100 searches/month | [SerpAPI](https://serpapi.com) |

## Detailed Setup Instructions

### 1. Google AI API Key (Required)

**Purpose**: Powers all agents with Gemini 2.0 Flash model

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Choose "Create API key in new project"
5. Copy the API key and save it as `GOOGLE_API_KEY`

**Free Tier Limits**:
- 15 requests per minute
- 1 million tokens per minute
- 1,500 requests per day

### 2. Reddit API (Sentiment Seeker)

**Purpose**: Analyze WallStreetBets and investing subreddits

1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Click "Create App" or "Create Another App"
3. Fill in the form:
   - Name: `Market Oracle Bot`
   - App type: Select **script**
   - Description: `Investment sentiment analysis bot`
   - About URL: (leave blank)
   - Redirect URI: `http://localhost:8080`
4. Click "Create app"
5. Save the following:
   - `REDDIT_CLIENT_ID`: The ID under "personal use script"
   - `REDDIT_CLIENT_SECRET`: The secret key

**Rate Limits**:
- 60 requests per minute for OAuth clients

### 3. BrightData (Fundamental Analyst)

**Purpose**: Scrape SEC filings and financial data

1. Go to [BrightData Sign Up](https://brightdata.com/cp/start)
2. Create an account (free trial available)
3. Navigate to "Web Unlocker" product
4. Create a new zone:
   - Zone name: `market_oracle_sec`
   - Type: Datacenter
5. Go to "Access Parameters" to get:
   - `BRIGHTDATA_API_TOKEN`: Your API token
   - `BRIGHTDATA_CUSTOMER_ID`: Your customer ID
   - `BRIGHTDATA_ZONE`: The zone name you created

**Free Trial**:
- $5 credit for testing
- Datacenter IPs included

### 4. Brave Search API (News & Web Search)

**Purpose**: Search for market news and company information

1. Go to [Brave Search API](https://brave.com/search/api/)
2. Click "Get Started"
3. Sign up for an account
4. Navigate to API Keys section
5. Create a new API key
6. Save as `BRAVE_API_KEY`

**Free Tier**:
- 2,000 queries per month
- Web and news search included

### 5. HuggingFace (Technical Prophet)

**Purpose**: Access financial ML models

1. Go to [HuggingFace](https://huggingface.co/join)
2. Create an account
3. Go to [Settings > Access Tokens](https://huggingface.co/settings/tokens)
4. Click "New token"
5. Name: `market_oracle`
6. Select "Read" access
7. Copy and save as `HUGGINGFACE_API_KEY`

**Free Tier**:
- Unlimited model access
- Rate limits vary by model

### 6. Snowflake (Historical Data)

**Purpose**: Store and analyze historical market data

1. Go to [Snowflake Trial](https://signup.snowflake.com)
2. Sign up for 30-day free trial
3. Choose cloud provider and region
4. After setup, go to Account > Admin > Worksheets
5. Run the setup script:
```sql
-- Create user and database
CREATE USER market_oracle_user PASSWORD = 'StrongPassword123!';
CREATE DATABASE MARKET_DATA;
CREATE WAREHOUSE COMPUTE_WH WITH WAREHOUSE_SIZE = 'XSMALL';
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO USER market_oracle_user;
GRANT ALL ON DATABASE MARKET_DATA TO USER market_oracle_user;
```
6. Save credentials:
   - `SNOWFLAKE_ACCOUNT`: Your account identifier (e.g., `abc12345.us-east-1`)
   - `SNOWFLAKE_USER`: `market_oracle_user`
   - `SNOWFLAKE_PASSWORD`: The password you set

**Free Trial**:
- 30 days
- $400 credits

### 7. Supabase (Real-time Portfolio)

**Purpose**: Real-time portfolio tracking and sync

1. Go to [Supabase](https://app.supabase.com)
2. Create a new project
3. Choose a name: `market-oracle`
4. Set a strong database password
5. Wait for project to provision
6. Go to Settings > API
7. Copy:
   - `SUPABASE_URL`: Your project URL
   - `SUPABASE_ANON_KEY`: The `anon` public key
   - `SUPABASE_SERVICE_ROLE_KEY`: The `service_role` key (keep secret!)

**Free Tier**:
- 500MB database
- 2GB bandwidth
- 50,000 monthly active users

### 8. n8n (Trading Automation)

**Purpose**: Webhook automation for trade execution

**Option A: Self-hosted (Recommended)**
```bash
# Using Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

**Option B: Cloud**
1. Go to [n8n.cloud](https://n8n.cloud)
2. Sign up for account
3. Create a workflow
4. Add webhook trigger
5. Copy webhook URL and API key

Save:
- `N8N_WEBHOOK_URL`: Your webhook URL
- `N8N_API_KEY`: Your API key (cloud only)

### 9. Notion (Documentation)

**Purpose**: Store investment research and reports

1. Go to [Notion](https://www.notion.so)
2. Create workspace if needed
3. Go to [My Integrations](https://www.notion.so/my-integrations)
4. Click "New integration"
5. Name: `Market Oracle`
6. Select your workspace
7. Capabilities: Read, Update, Insert content
8. Save the "Internal Integration Token" as `NOTION_API_KEY`
9. Create a database for research:
   - Add properties: Symbol, Date, Recommendation, Target Price, etc.
   - Share database with your integration
   - Copy database ID from URL: `notion.so/[workspace]/[database_id]?v=...`
   - Save as `NOTION_DATABASE_ID`

### 10. ElevenLabs (Audio Briefings)

**Purpose**: Generate voice market updates

1. Go to [ElevenLabs](https://elevenlabs.io)
2. Sign up for account
3. Go to Profile Settings
4. Copy your API key
5. Save as `ELEVENLABS_API_KEY`
6. Choose a voice:
   - Go to Voice Library
   - Select a voice (e.g., "Rachel")
   - Copy Voice ID
   - Save as `ELEVENLABS_VOICE_ID`

**Free Tier**:
- 10,000 characters per month
- ~5-10 market briefings

### 11. SerpAPI (Google Trends)

**Purpose**: Track search trends correlation

1. Go to [SerpAPI](https://serpapi.com/users/sign_up)
2. Sign up for account
3. Go to Dashboard
4. Copy your API key
5. Save as `GOOGLE_TRENDS_API_KEY`

**Free Tier**:
- 100 searches per month

## Testing Your Configuration

After setting up all APIs, test your configuration:

```bash
# Check environment
./start_market_oracle.sh

# If all checks pass, run the demo
python demo_market_oracle.py
```

## Cost Optimization Tips

### Free Tier Strategy
1. **Development**: Use free tiers for all services
2. **Production**: Upgrade only what you need:
   - Google AI: Consider paid plan for higher RPM
   - BrightData: Pay-as-you-go for SEC filings
   - Snowflake: Store only essential historical data

### API Key Rotation
- Rotate API keys monthly for security
- Use separate keys for dev/prod environments
- Monitor usage to avoid overages

### Caching Strategy
- Cache Reddit sentiment for 15 minutes
- Cache fundamental data for 24 hours
- Cache Google Trends for 1 hour
- Store all analysis in local SQLite

## Security Best Practices

1. **Never commit API keys**:
   ```bash
   # Add to .gitignore
   .env
   .env.*
   ```

2. **Use environment-specific keys**:
   ```bash
   # .env.development
   GOOGLE_API_KEY=dev_key_here
   
   # .env.production
   GOOGLE_API_KEY=prod_key_here
   ```

3. **Implement key rotation**:
   - Set calendar reminders
   - Use secret management tools
   - Monitor for exposed keys

4. **Limit API permissions**:
   - Use read-only where possible
   - Restrict to specific resources
   - Enable IP whitelisting

## Troubleshooting

### Common Issues

1. **"API key invalid"**
   - Double-check key is copied correctly
   - Ensure no extra spaces
   - Verify key is activated

2. **"Rate limit exceeded"**
   - Implement exponential backoff
   - Check current usage in provider dashboard
   - Consider upgrading plan

3. **"Connection refused"**
   - Check firewall settings
   - Verify API endpoints
   - Test with curl/Postman

### Support Resources

- Google AI: [Documentation](https://ai.google.dev/docs)
- Reddit: [API Documentation](https://www.reddit.com/dev/api/)
- BrightData: [Support Center](https://docs.brightdata.com)
- Snowflake: [Documentation](https://docs.snowflake.com)

For Market Oracle specific issues, check the logs in `logs/` directory.