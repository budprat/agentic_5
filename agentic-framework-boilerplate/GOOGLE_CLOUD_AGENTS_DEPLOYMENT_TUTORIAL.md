# Google ADK Deployment Tutorial for A2A-MCP Framework

## ✅ Deployment Feasibility Assessment

**YES, you can use `adk deploy` for your agents!** This tutorial covers complete deployment to Google Cloud.

### Current Architecture Compatibility:
- ✅ Your agents use `google.adk.agents.Agent` (confirmed in sentiment_seeker_agent.py, adk_travel_agent.py)
- ✅ Google Cloud project configured: "Agents Cloud" in "asia-south2-c"
- ✅ ADK supports `adk deploy cloud_run` command for Python agents
- ✅ Your Market Oracle agents are ADK-compatible

## 🚀 Deployment Strategy Options

### Option 1: Individual Agent Deployment (Recommended)
**Deploy each specialized agent separately to Cloud Run**

**Agents Ready for Deployment:**
1. **Sentiment Seeker Agent** (Reddit/social sentiment analysis)
2. **Fundamental Analyst Agent** (SEC filings analysis)
3. **Technical Prophet Agent** (ML predictions)
4. **Travel Agents** (Air/Hotel/Car booking)
5. **Oracle Prime Agent** (Master orchestrator)

**Commands:**
```bash
# For each agent directory
cd src/a2a_mcp/agents/market_oracle/
adk deploy cloud_run --agent sentiment_seeker_agent.py
adk deploy cloud_run --agent fundamental_analyst_agent.py
# etc.
```

### Option 2: Monolithic Deployment
**Deploy the entire A2A system as a single service**

## 📋 Required Deployment Preparations

### 1. **Environment Variables Setup** (CRITICAL - Official ADK Requirements):
```bash
# REQUIRED Google Cloud Environment Variables
export GOOGLE_CLOUD_PROJECT="Agents Cloud"
export GOOGLE_CLOUD_LOCATION="asia-south2-c"  
export GOOGLE_GENAI_USE_VERTEXAI=0  # Set to True for Vertex AI, False for standard Gemini API

# OPTIONAL - For cleaner deployment commands
export AGENT_PATH="./src/a2a_mcp/agents/market_oracle"
export SERVICE_NAME="sentiment-seeker-agent"
export APP_NAME="sentiment-seeker"
```

### 2. **Agent Structure Requirements** (ADK Standards):
Your agents MUST follow this structure for `adk deploy` to work:

```
sentiment_seeker_agent/
├── __init__.py              # Must contain: from . import agent
├── agent.py                 # Must contain: root_agent = YourAgent()
└── requirements.txt         # Dependencies
```

**Critical Requirements:**
- Agent code must be in file called `agent.py`
- Agent variable must be named `root_agent`
- `__init__.py` must contain `from . import agent`

### 3. **Agent Code Structure** (Update Required):
```python
# agent.py - Update your existing agents to this format
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams
from a2a_mcp.common.utils import get_mcp_server_config, init_api_key

# Initialize API key
init_api_key()

# Configure MCP tools
config = get_mcp_server_config()
tools = await MCPToolset(
    connection_params=SseConnectionParams(url=config.url)
).get_tools()

# Create the agent (this MUST be named 'root_agent')
root_agent = Agent(
    name="Sentiment Seeker",
    instruction="You are a specialized agent for analyzing social media sentiment...",
    model='gemini-2.0-flash',
    tools=tools
)
```

### 4. **Multiple Deployment Options**:

#### Option A: ADK CLI (Recommended - Simplest)
- Uses `adk deploy cloud_run` command
- Auto-generates Dockerfile and container
- Minimal configuration required

#### Option B: gcloud CLI with Custom FastAPI
- Full control over deployment
- Custom FastAPI application structure
- Manual Dockerfile creation required

## 🛠️ Implementation Steps

### Phase 1: Individual Agent Deployment
1. **Create ADK deployment configs** for each Market Oracle agent
2. **Extract agent-specific environment variables**
3. **Set up Google Cloud authentication** (`gcloud auth login`)
4. **Deploy Sentiment Seeker first** (simplest agent to test)
5. **Validate deployment** and test agent endpoints
6. **Deploy remaining agents** one by one

### Phase 2: Service Integration
1. **Update A2A orchestrator** to use deployed Cloud Run endpoints
2. **Configure load balancing** and health checks
3. **Set up monitoring** and logging with Cloud Operations
4. **Implement auto-scaling** based on request volume

### Phase 3: MCP Server Deployment
1. **Deploy MCP server** to Cloud Run
2. **Configure agent discovery** for cloud-deployed agents
3. **Update agent cards** with Cloud Run URLs
4. **Test end-to-end workflows**

## ⚙️ Technical Considerations

### ADK Cloud Run Features:
- **Auto-scaling**: Scales to zero when not in use
- **Built-in authentication**: Integrates with Google Cloud IAM
- **Load balancing**: Automatic traffic distribution
- **Monitoring**: Built-in metrics and logging

### A2A Framework Integration:
- **Agent Cards**: Update URLs to Cloud Run endpoints
- **MCP Connectivity**: Ensure agents can reach MCP servers
- **Authentication**: Configure bearer tokens for agent communication

## 🔐 Security & Configuration

### Environment Variables for Cloud Run:
```bash
GOOGLE_API_KEY=
GOOGLE_CLOUD_PROJECT=Agents
GOOGLE_CLOUD_LOCATION=asia-south2-c
GOOGLE_GENAI_USE_VERTEXAI=0
SNOWFLAKE_ACCOUNT=xxx
SUPABASE_URL=xxx
BRIGHTDATA_API_TOKEN=xxx
# etc.
```

### Secret Manager Integration:
- Store sensitive API keys in Google Secret Manager
- Reference secrets in Cloud Run deployment
- Automatic secret rotation support

## 📊 Deployment Architecture

```
Internet → Cloud Load Balancer → Cloud Run Services
                                      ↓
┌─────────────────┬─────────────────┬─────────────────┐
│ Sentiment       │ Fundamental     │ Technical       │
│ Seeker Agent    │ Analyst Agent   │ Prophet Agent   │
│ (Cloud Run)     │ (Cloud Run)     │ (Cloud Run)     │
└─────────────────┴─────────────────┴─────────────────┘
                                      ↓
                          MCP Server (Cloud Run)
                                      ↓
┌─────────────────┬─────────────────┬─────────────────┐
│ Snowflake       │ Supabase        │ External APIs   │
│ (Data)          │ (Real-time)     │ (BrightData)    │
└─────────────────┴─────────────────┴─────────────────┘
```

## 🎯 Step-by-Step Deployment Guide

### Prerequisites:
```bash
# Install Google Cloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Authenticate with Google Cloud
gcloud auth login
gcloud config set project "agents-cloud"

# Verify ADK installation
adk --version
```

### Step 1: Authentication Setup
```bash
# Authenticate with Google Cloud (REQUIRED)
gcloud auth login
gcloud config set project "agents-cloud"

# Verify ADK installation
adk --version
```

### Step 2: Environment Variables (Official ADK Requirements)
```bash
# Set REQUIRED environment variables (per official ADK docs)
export GOOGLE_CLOUD_PROJECT="Agents Cloud"
export GOOGLE_CLOUD_LOCATION="asia-south2-c"  
export GOOGLE_GENAI_USE_VERTEXAI=0  # Important: 0 for Gemini API, True for Vertex AI

# Set deployment variables for convenience
export AGENT_PATH="./src/a2a_mcp/agents/market_oracle/sentiment_seeker_agent"
export SERVICE_NAME="sentiment-seeker-agent"
export APP_NAME="sentiment-seeker"
```

### Step 3: Prepare Agent Directory Structure
```bash
# Create proper ADK-compliant structure for each agent
mkdir -p deploy_agents/sentiment_seeker_agent
cd deploy_agents/sentiment_seeker_agent

# Create required files
cat > __init__.py << 'EOF'
from . import agent
EOF

cat > agent.py << 'EOF'
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams
from google.genai import types as genai_types

# This MUST be named 'root_agent' for ADK deployment
root_agent = Agent(
    name="Sentiment Seeker",
    instruction="""You are Sentiment Seeker, a specialized agent for analyzing social media sentiment around stocks and investments.

Your capabilities:
1. Monitor Reddit communities (WallStreetBets, stocks, investing, StockMarket)
2. Analyze sentiment from posts and comments
3. Track unusual volume spikes in discussions
4. Identify retail vs institutional sentiment divergence
5. Detect early meme stock movements

When analyzing a stock symbol, provide sentiment analysis and key insights.""",
    model='gemini-2.0-flash',
    generate_content_config=genai_types.GenerateContentConfig(temperature=0.1)
)
EOF

cat > requirements.txt << 'EOF'
google-adk
a2a-sdk
google-generativeai
mcp
EOF
```

### Step 4A: Deploy with ADK CLI (Recommended)

#### Minimal Deployment Command:
```bash
adk deploy cloud_run \
--project="Agents Cloud" \
--region="asia-south2-c" \
./sentiment_seeker_agent
```

#### Full Command with All Options:
```bash
adk deploy cloud_run \
--project="Agents Cloud" \
--region="asia-south2-c" \
--service_name="sentiment-seeker-agent" \
--app_name="sentiment-seeker" \
--with_ui \
./sentiment_seeker_agent
```

#### Authentication Prompt:
When prompted: `Allow unauthenticated invocations to [sentiment-seeker-agent] (y/N)?`
- Enter `y` for public access (testing)
- Enter `N` for authenticated access (production)

#### Expected Output:
```bash
✓ Building container image...
✓ Pushing to Artifact Registry...
✓ Deploying to Cloud Run...
✓ Service URL: https://sentiment-seeker-agent-xxx-asia-south2.run.app
```

### Step 4B: Deploy with gcloud CLI (Advanced)

#### Create Custom FastAPI Structure:
```bash
mkdir -p custom_deploy/sentiment_seeker_agent
cd custom_deploy

# Create main.py
cat > main.py << 'EOF'
import os
import uvicorn
from google.adk.cli.fast_api import get_fast_api_app

# Get the directory where main.py is located
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_DB_URL = "sqlite:///./sessions.db"
ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
SERVE_WEB_INTERFACE = True

app = get_fast_api_app(
    agents_dir=AGENT_DIR,
    session_service_uri=SESSION_DB_URL,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
EOF

# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.13-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN adduser --disabled-password --gecos "" myuser && \
    chown -R myuser:myuser /app

COPY . .
USER myuser
ENV PATH="/home/myuser/.local/bin:$PATH"

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
EOF

# Deploy with gcloud
gcloud run deploy sentiment-seeker-agent \
--source . \
--region asia-south2-c \
--project "agents-cloud" \
--allow-unauthenticated \
--set-env-vars="GOOGLE_CLOUD_PROJECT=Agents Cloud,GOOGLE_CLOUD_LOCATION=asia-south2-c,GOOGLE_GENAI_USE_VERTEXAI=0,GOOGLE_API_KEY=```

### Step 3: Update Agent Cards
```json
{
    "name": "Sentiment Seeker",
    "description": "Reddit and social media sentiment analyzer for market intelligence",
    "url": "https://sentiment-seeker-agent-xxx.asia-south2.run.app/",
    "provider": "Google Cloud Run",
    "version": "1.0.0",
    "capabilities": {
        "streaming": "True",
        "pushNotifications": "True",
        "stateTransitionHistory": "False"
    }
}
```

### Step 4: Deploy Remaining Agents
```bash
# Deploy all Market Oracle agents
adk deploy cloud_run --agent fundamental_analyst_agent.py
adk deploy cloud_run --agent technical_prophet_agent.py
adk deploy cloud_run --agent oracle_prime_agent.py
adk deploy cloud_run --agent risk_guardian_agent.py
adk deploy cloud_run --agent trend_correlator_agent.py
adk deploy cloud_run --agent report_synthesizer_agent.py
adk deploy cloud_run --agent audio_briefer_agent.py
```

### Step 5: Deploy MCP Server
```bash
# Deploy MCP server to coordinate agents
cd src/a2a_mcp/mcp/
adk deploy cloud_run --service server.py
```

## 🧪 Testing Deployed Agents (Official ADK Testing Methods)

### UI Testing (If --with_ui flag used):
Simply navigate to your Cloud Run service URL in a web browser:
```bash
# Example URL format
https://sentiment-seeker-agent-xxx-asia-south2.run.app
```

The ADK dev UI allows you to:
1. Select your agent from the dropdown
2. Type messages and verify responses
3. Manage sessions and view execution details

### API Testing with curl (Official ADK API Endpoints):

#### Step 1: Set Application URL
```bash
export APP_URL="https://sentiment-seeker-agent-xxx-asia-south2.run.app"
```

#### Step 2: Get Identity Token (if authentication required)
```bash
export TOKEN=$(gcloud auth print-identity-token)
```

#### Step 3: List Available Apps
```bash
curl -X GET -H "Authorization: Bearer $TOKEN" $APP_URL/list-apps
```

#### Step 4: Create or Update Session
```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
    $APP_URL/apps/sentiment_seeker/users/user_123/sessions/session_abc \
    -H "Content-Type: application/json" \
    -d '{"state": {"preferred_language": "English", "visit_count": 1}}'
```

#### Step 5: Run the Agent (Official ADK Format)
```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
    $APP_URL/run_sse \
    -H "Content-Type: application/json" \
    -d '{
    "app_name": "sentiment_seeker",
    "user_id": "user_123", 
    "session_id": "session_abc",
    "new_message": {
        "role": "user",
        "parts": [{
        "text": "What is the sentiment on AAPL?"
        }]
    },
    "streaming": false
    }'
```

#### For Streaming Responses:
```bash
# Set "streaming": true for Server-Sent Events
curl -X POST -H "Authorization: Bearer $TOKEN" \
    $APP_URL/run_sse \
    -H "Content-Type: application/json" \
    -d '{
    "app_name": "sentiment_seeker",
    "user_id": "user_123",
    "session_id": "session_abc", 
    "new_message": {
        "role": "user",
        "parts": [{
        "text": "Analyze sentiment for Tesla stock"
        }]
    },
    "streaming": true
    }'
```

## 📊 Monitoring & Maintenance

### Cloud Operations Integration:
```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=sentiment-seeker-agent"

# Monitor metrics
gcloud monitoring metrics list --filter="metric.type:run.googleapis.com"
```

### Auto-scaling Configuration:
```yaml
# In adk.yaml
scaling:
  min_instances: 0
  max_instances: 100
  target_cpu_utilization: 70
  target_concurrency: 80
```

## 💡 Benefits of ADK Cloud Deployment

- **Cost Optimization**: Pay only for actual usage (scales to zero)
- **Automatic Scaling**: Handle variable workloads seamlessly
- **Built-in Monitoring**: Google Cloud Operations integration
- **Security**: Google Cloud IAM and VPC integration
- **Reliability**: Google's infrastructure and SLA guarantees
- **Global Distribution**: Deploy to multiple regions easily

## 🔧 Troubleshooting Common Issues

### 1. **Authentication Errors**:
```bash
# Re-authenticate
gcloud auth application-default login
```

### 2. **Memory Issues**:
```yaml
# Increase memory in adk.yaml
memory: "2Gi"
cpu: "2"
```

### 3. **Environment Variables**:
```bash
# Use Secret Manager for sensitive data
gcloud secrets create REDDIT_CLIENT_SECRET --data-file=secret.txt
```

### 4. **Cold Start Optimization**:
```yaml
# Keep minimum instances warm
min_instances: 1
```

## 🚀 Advanced Deployment Patterns

### Multi-Region Deployment:
```bash
# Deploy to multiple regions for global availability
adk deploy cloud_run --region us-central1
adk deploy cloud_run --region europe-west1
adk deploy cloud_run --region asia-southeast1
```

### CI/CD Integration:
```yaml
# .github/workflows/deploy.yml
name: Deploy to Cloud Run
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: google-github-actions/setup-gcloud@v0
      - run: adk deploy cloud_run --agent sentiment_seeker_agent.py
```

This comprehensive tutorial enables full cloud deployment of your A2A-MCP agent ecosystem using Google's ADK platform!