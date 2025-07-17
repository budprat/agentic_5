# Google Cloud Deployment Tutorial for A2A-MCP Framework V2.0

## ✅ V2.0 Deployment Feasibility Assessment

**YES, you can deploy V2.0 agents to Google Cloud!** This tutorial covers complete deployment with V2.0 features including quality validation, observability, and PHASE 7 streaming.

### V2.0 Architecture Compatibility:
- ✅ V2.0 agents use `StandardizedAgentBase` with cloud-ready design
- ✅ Google Cloud Run supports HTTP/2 for V2.0 connection pooling
- ✅ Built-in observability integrates with Google Cloud Operations
- ✅ PHASE 7 streaming works with Cloud Run's response streaming
- ✅ Quality framework compatible with cloud metrics

## 📚 Essential V2.0 References
- [Framework Components Guide](../docs/FRAMEWORK_COMPONENTS_AND_ORCHESTRATION_GUIDE.md)
- [Multi-Agent Workflow Guide](../docs/MULTI_AGENT_WORKFLOW_GUIDE.md)

## 🚀 V2.0 Deployment Strategy Options

### Option 1: Microservices Deployment (Recommended for V2.0)
**Deploy each V2.0 agent as a separate Cloud Run service with observability**

**V2.0 Agents Ready for Deployment:**
1. **StandardizedAgentBase Agents** (Quality-validated domain specialists)
2. **GenericDomainAgent Instances** (Quick-deploy specialists)
3. **EnhancedMasterOrchestrator** (PHASE 7 streaming coordinator)
4. **Parallel Workflow Services** (Performance-optimized processors)
5. **Quality Validation Services** (Domain-specific validators)

**V2.0 Deployment Commands:**
```bash
# Deploy V2.0 agents with observability
cd src/a2a_mcp/common/

# Deploy StandardizedAgentBase agents
gcloud run deploy domain-specialist-v2 \
  --source . \
  --allow-unauthenticated \
  --set-env-vars="ENABLE_OBSERVABILITY=true,QUALITY_DOMAIN=ANALYTICAL" \
  --cpu=2 --memory=4Gi \
  --concurrency=1000 \
  --http2  # Enable HTTP/2 for connection pooling

# Deploy GenericDomainAgent
gcloud run deploy generic-agent-v2 \
  --source . \
  --set-env-vars="DOMAIN=Finance,SPECIALIZATION=analyst" \
  --http2
```

### Option 2: V2.0 Orchestrator-Centric Deployment
**Deploy Enhanced Orchestrator with agent discovery**

### Option 3: Serverless Function Deployment
**Deploy lightweight agents as Cloud Functions**

## 📋 V2.0 Deployment Preparations

### 1. **V2.0 Environment Variables Setup**:
```bash
# V2.0 Framework Configuration
export ORCHESTRATION_MODE="enhanced"
export ENABLE_PHASE_7_STREAMING="true"
export ENABLE_OBSERVABILITY="true"
export CONNECTION_POOL_SIZE="20"
export DEFAULT_QUALITY_DOMAIN="ANALYTICAL"

# Google Cloud Configuration
export GOOGLE_CLOUD_PROJECT="business-cloud"
export GOOGLE_CLOUD_LOCATION="us-central1"  
export GOOGLE_CLOUD_ENABLE_TRACING="true"
export GOOGLE_CLOUD_ENABLE_PROFILER="true"

# Observability Configuration
export OTEL_SERVICE_NAME="a2a-mcp-v2"
export OTEL_EXPORTER_OTLP_ENDPOINT="https://otel-collector.googleapis.com"
export TRACING_ENABLED="true"
export METRICS_ENABLED="true"

# V2.0 Performance Settings
export ENABLE_HTTP2="true"
export MAX_CONCURRENT_REQUESTS="1000"
export REQUEST_TIMEOUT="30000"
```

### 2. **V2.0 Agent Structure Requirements**:
Your V2.0 agents follow this enhanced structure:

```
agent_v2/
├── __init__.py              # Exports V2.0 agent classes
├── agent.py                 # StandardizedAgentBase implementation
├── quality_config.yaml      # Quality validation settings
├── observability.yaml       # Tracing and metrics config
├── requirements.txt         # V2.0 dependencies
└── Dockerfile              # V2.0 optimized container
```

**V2.0 Dockerfile Example:**
```dockerfile
# V2.0 Python runtime with observability
FROM python:3.11-slim

# Install OpenTelemetry agents
RUN pip install opentelemetry-distro[otlp] \
    opentelemetry-instrumentation

# Copy V2.0 framework
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app
WORKDIR /app

# Enable V2.0 features
ENV PYTHONUNBUFFERED=1
ENV ENABLE_OBSERVABILITY=true
ENV ENABLE_PHASE_7_STREAMING=true

# Auto-instrument with OpenTelemetry
CMD ["opentelemetry-instrument", "python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--http", "h2"]
```

### 3. **V2.0 Agent Code Structure**:
```python
# agent.py - V2.0 StandardizedAgentBase implementation
from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.common.quality_framework import QualityDomain
from a2a_mcp.common.observability import trace_async
from typing import Dict, Any
import os

class CloudDeployedAgentV2(StandardizedAgentBase):
    """V2.0 Cloud-optimized agent with full features"""
    
    def __init__(self):
        super().__init__(
            agent_name="Cloud Domain Specialist V2",
            description="Cloud-deployed specialist with quality validation",
            capabilities=[
                "Process domain requests",
                "Validate quality metrics",
                "Stream real-time updates",
                "Export observability data"
            ],
            quality_config={
                "domain": QualityDomain[os.getenv("QUALITY_DOMAIN", "ANALYTICAL")],
                "thresholds": {
                    "completeness": float(os.getenv("QUALITY_COMPLETENESS", "0.90")),
                    "accuracy": float(os.getenv("QUALITY_ACCURACY", "0.95")),
                    "relevance": float(os.getenv("QUALITY_RELEVANCE", "0.88"))
                }
            },
            enable_observability=os.getenv("ENABLE_OBSERVABILITY", "true").lower() == "true"
        )
    
    @trace_async
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process with V2.0 quality validation and tracing"""
        
        # Quality-validated processing
        result = await self.execute_with_quality(request)
        
        # Add cloud metadata
        result["cloud_metadata"] = {
            "service": os.getenv("K_SERVICE", "unknown"),
            "revision": os.getenv("K_REVISION", "unknown"),
            "trace_id": self.get_current_trace_id()
        }
        
        return result

# For quick deployment
from a2a_mcp.common.generic_domain_agent import GenericDomainAgent

def create_cloud_agent():
    """Create V2.0 agent for cloud deployment"""
    return GenericDomainAgent(
        domain=os.getenv("AGENT_DOMAIN", "Generic"),
        specialization=os.getenv("AGENT_SPECIALIZATION", "analyst"),
        capabilities=os.getenv("AGENT_CAPABILITIES", "").split(","),
        quality_domain=QualityDomain[os.getenv("QUALITY_DOMAIN", "GENERIC")],
        enable_observability=True
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

## 🛠️ V2.0 Implementation Steps

### Phase 1: V2.0 Infrastructure Setup
1. **Deploy Observability Stack** to Google Cloud
   ```bash
   # Deploy OpenTelemetry Collector
   gcloud run deploy otel-collector \
     --image=otel/opentelemetry-collector-contrib:latest \
     --port=4317 \
     --set-env-vars="GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}"
   ```

2. **Set up Cloud Monitoring Dashboard**
   ```bash
   # Create V2.0 monitoring dashboard
   gcloud monitoring dashboards create \
     --config-from-file=monitoring/v2-dashboard.yaml
   ```

3. **Configure Cloud Trace** for distributed tracing
4. **Set up Cloud Profiler** for performance analysis

### Phase 2: V2.0 Agent Deployment
1. **Deploy StandardizedAgentBase agents**
   ```bash
   # Deploy with V2.0 features enabled
   gcloud run deploy agent-v2 \
     --source=. \
     --set-env-vars="@env-v2.yaml" \
     --cpu=2 --memory=4Gi \
     --concurrency=1000 \
     --http2 \
     --set-cloudsql-instances=${CLOUD_SQL_CONNECTION}
   ```

2. **Deploy Enhanced Master Orchestrator**
   ```bash
   # Deploy orchestrator with PHASE 7 streaming
   gcloud run deploy orchestrator-v2 \
     --source=. \
     --set-env-vars="ENABLE_PHASE_7_STREAMING=true" \
     --timeout=3600 \
     --cpu=4 --memory=8Gi
   ```

3. **Configure Service Mesh** for inter-agent communication
4. **Enable connection pooling** between services

### Phase 3: V2.0 Quality & Performance
1. **Deploy Quality Validation Service**
2. **Configure auto-scaling policies**
   ```yaml
   # v2-autoscaling.yaml
   apiVersion: autoscaling.k8s.io/v1
   kind: VerticalPodAutoscaler
   spec:
     targetCPUUtilizationPercentage: 70
     minReplicas: 2
     maxReplicas: 100
   ```
3. **Set up performance monitoring**
4. **Configure quality alerts**

## ⚙️ V2.0 Technical Considerations

### Cloud Run V2.0 Features:
- **HTTP/2 Support**: Enables connection pooling (60% performance gain)
- **Response Streaming**: Supports PHASE 7 real-time updates
- **Concurrent Requests**: Handle 1000+ concurrent with V2.0
- **Observability Integration**: Native OpenTelemetry support
- **Quality Metrics Export**: Direct to Cloud Monitoring

### V2.0 Framework Cloud Integration:
- **Distributed Tracing**: Full request flow visibility
- **Quality Validation**: Cloud-based quality scoring
- **Parallel Execution**: Multi-region deployment support
- **Connection Pooling**: Persistent HTTP/2 connections
- **Streaming Responses**: WebSocket and SSE support

### V2.0 Performance Optimizations:
```yaml
# cloud-run-v2.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: agent-v2
  annotations:
    run.googleapis.com/cpu-throttling: "false"
    run.googleapis.com/execution-environment: gen2
spec:
  template:
    metadata:
      annotations:
        # V2.0 Performance settings
        run.googleapis.com/network-interfaces: "[{\"network\":\"default\",\"subnetwork\":\"premium\"}]"
        run.googleapis.com/vpc-access-connector: projects/${PROJECT}/locations/${REGION}/connectors/vpc-connector
    spec:
      containerConcurrency: 1000
      timeoutSeconds: 3600
      serviceAccountName: agent-v2-sa@${PROJECT}.iam.gserviceaccount.com
```

## 🔐 V2.0 Security & Configuration

### V2.0 Environment Variables for Cloud Run:
```yaml
# env-v2.yaml - V2.0 Configuration
# Framework V2.0 Settings
ORCHESTRATION_MODE: enhanced
ENABLE_PHASE_7_STREAMING: "true"
ENABLE_OBSERVABILITY: "true"
CONNECTION_POOL_SIZE: "20"
DEFAULT_QUALITY_DOMAIN: ANALYTICAL

# Quality Thresholds
QUALITY_COMPLETENESS: "0.90"
QUALITY_ACCURACY: "0.95"
QUALITY_RELEVANCE: "0.88"

# Observability
OTEL_SERVICE_NAME: a2a-mcp-v2-${K_SERVICE}
OTEL_EXPORTER_OTLP_ENDPOINT: https://cloudtrace.googleapis.com
TRACING_ENABLED: "true"
METRICS_ENABLED: "true"
JSON_LOGS: "true"

# Performance
ENABLE_HTTP2: "true"
MAX_CONCURRENT_REQUESTS: "1000"
REQUEST_TIMEOUT: "30000"
CONNECTION_KEEPALIVE: "true"

# Secrets (from Secret Manager)
DATABASE_URL: sm://database-url-v2
REDIS_URL: sm://redis-url-v2
API_KEYS: sm://api-keys-v2
```

### V2.0 Secret Manager Integration:
```bash
# Create V2.0 secrets
echo -n "${DATABASE_URL}" | gcloud secrets create database-url-v2 --data-file=-
echo -n "${REDIS_URL}" | gcloud secrets create redis-url-v2 --data-file=-

# Grant access to service account
gcloud secrets add-iam-policy-binding database-url-v2 \
  --member="serviceAccount:agent-v2-sa@${PROJECT}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### V2.0 IAM Configuration:
```bash
# Create V2.0 service account
gcloud iam service-accounts create agent-v2-sa \
  --display-name="A2A-MCP V2.0 Agent Service Account"

# Grant required permissions
gcloud projects add-iam-policy-binding ${PROJECT} \
  --member="serviceAccount:agent-v2-sa@${PROJECT}.iam.gserviceaccount.com" \
  --role="roles/cloudtrace.agent"

gcloud projects add-iam-policy-binding ${PROJECT} \
  --member="serviceAccount:agent-v2-sa@${PROJECT}.iam.gserviceaccount.com" \
  --role="roles/cloudprofiler.agent"
```

## 📊 V2.0 Deployment Architecture

```
Internet → Cloud CDN → Global Load Balancer → Cloud Armor (DDoS)
                                                    ↓
                                          ┌─────────────────┐
                                          │ Enhanced Master │
                                          │ Orchestrator V2 │
                                          │ (PHASE 7)       │
                                          └────────┬────────┘
                                                   ↓ HTTP/2 + Pooling
        ┌──────────────────┬──────────────────┬──────────────────┐
        │                  │                  │                  │
┌───────▼────────┐ ┌───────▼────────┐ ┌───────▼────────┐ ┌───────▼────────┐
│ Standardized   │ │ Generic Domain │ │ Quality Valid. │ │ Parallel Work. │
│ Agent Base V2  │ │ Agents V2      │ │ Service V2     │ │ Service V2     │
│ (Cloud Run)    │ │ (Cloud Run)    │ │ (Cloud Run)    │ │ (Cloud Run)    │
└────────┬───────┘ └────────┬───────┘ └────────┬───────┘ └────────┬───────┘
         │                  │                  │                  │
         └──────────────────┴──────────────────┴──────────────────┘
                                     ↓
                            ┌─────────────────┐
                            │ Connection Pool │
                            │ Manager V2      │
                            └────────┬────────┘
                                     ↓
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ Cloud SQL       │ Memorystore     │ Cloud Trace     │ Cloud Monitoring│
│ (PostgreSQL)    │ (Redis)         │ (Distributed)   │ (Metrics)       │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

### V2.0 Multi-Region Architecture:
```
us-central1          europe-west1         asia-southeast1
    │                     │                     │
    ▼                     ▼                     ▼
┌─────────┐         ┌─────────┐         ┌─────────┐
│ Agent   │◄────────│ Agent   │◄────────│ Agent   │
│ Cluster │ Global  │ Cluster │ Global  │ Cluster │
│ V2      │ Sync    │ V2      │ Sync    │ V2      │
└─────────┘         └─────────┘         └─────────┘
    │                     │                     │
    └─────────────────────┴─────────────────────┘
                          │
                  ┌───────▼────────┐
                  │ Global Spanner │
                  │ Database       │
                  └────────────────┘
```

## 🎯 V2.0 Step-by-Step Deployment Guide

### Prerequisites:
```bash
# Install Google Cloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Authenticate with Google Cloud
gcloud auth login
gcloud config set project "business-cloud"

# Install V2.0 dependencies
pip install opentelemetry-distro[otlp]
pip install opentelemetry-instrumentation
pip install a2a-mcp-framework[v2]
```

### Step 1: V2.0 Project Setup
```bash
# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  cloudtrace.googleapis.com \
  cloudprofiler.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com

# Create V2.0 artifact repository
gcloud artifacts repositories create a2a-mcp-v2 \
  --repository-format=docker \
  --location=us-central1
adk --version
```

### Step 2: V2.0 FastAPI Application
```python
# main.py - V2.0 Cloud Run application
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import uvicorn
import os
import asyncio
import json

from a2a_mcp.common.master_orchestrator_template import EnhancedMasterOrchestratorTemplate
from a2a_mcp.common.observability import setup_observability
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Initialize observability
setup_observability("a2a-mcp-v2")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.orchestrator = EnhancedMasterOrchestratorTemplate(
        domain_name=os.getenv("DOMAIN_NAME", "Generic"),
        domain_specialists=json.loads(os.getenv("DOMAIN_SPECIALISTS", "{}")),
        enable_phase_7_streaming=True,
        enable_observability=True
    )
    yield
    # Shutdown
    await app.state.orchestrator.cleanup()

app = FastAPI(
    title="A2A-MCP Framework V2.0",
    version="2.0.0",
    lifespan=lifespan
)

# Instrument FastAPI with OpenTelemetry
FastAPIInstrumentor.instrument_app(app)

@app.post("/process")
async def process_request(request: Request):
    """V2.0 endpoint with PHASE 7 streaming"""
    data = await request.json()
    
    async def stream_response():
        async for event in app.state.orchestrator.stream_with_artifacts(
            query=data["query"],
            session_id=data.get("session_id", "default"),
            task_id=data.get("task_id", "default")
        ):
            yield f"data: {json.dumps(event)}\n\n"
    
    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "features": {
            "streaming": True,
            "observability": True,
            "quality_validation": True,
            "connection_pooling": True
        }
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        http="h2",  # HTTP/2
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter"
                }
            },
            "handlers": {
                "default": {
                    "formatter": "json",
                    "class": "logging.StreamHandler"
                }
            },
            "root": {
                "level": "INFO",
                "handlers": ["default"]
            }
        }
    )
```

### Step 3: V2.0 Deployment Package
```bash
# Create V2.0 deployment structure
mkdir -p deploy_v2/
cd deploy_v2/

# Copy main application
cp ../main.py .

# Create requirements.txt
cat > requirements.txt << 'EOF'
# A2A-MCP Framework V2.0
a2a-mcp-framework[v2]==2.0.0

# FastAPI and server
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Observability
opentelemetry-distro[otlp]==0.43b0
opentelemetry-instrumentation-fastapi==0.43b0
opentelemetry-exporter-gcp-trace==1.6.0
opentelemetry-exporter-gcp-monitoring==1.6.0
opentelemetry-resourcedetector-gcp==1.6.0
python-json-logger==2.0.7

# Google Cloud
google-cloud-trace==1.12.0
google-cloud-monitoring==2.18.0
google-cloud-logging==3.9.0
google-cloud-profiler==4.1.0

# Performance
httpx[http2]==0.26.0
aiohttp==3.9.3
aiodns==3.1.1

# Database and caching
asyncpg==0.29.0
redis[hiredis]==5.0.1
EOF

# Create V2.0 Dockerfile
cat > Dockerfile << 'EOF'
# V2.0 optimized Python runtime
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN useradd -m -u 1000 appuser

# Copy application
WORKDIR /app
COPY --chown=appuser:appuser . .

# V2.0 environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENABLE_OBSERVABILITY=true \
    ENABLE_PHASE_7_STREAMING=true \
    CONNECTION_POOL_SIZE=20 \
    ENABLE_HTTP2=true

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Start with OpenTelemetry auto-instrumentation
CMD ["opentelemetry-instrument", "python", "main.py"]
EOF
```

### Step 4: V2.0 Cloud Run Deployment

#### Build and Push Container:
```bash
# Configure Docker for Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build V2.0 container with Cloud Build
gcloud builds submit --tag us-central1-docker.pkg.dev/${PROJECT}/a2a-mcp-v2/orchestrator:latest

# Or build locally
docker build -t us-central1-docker.pkg.dev/${PROJECT}/a2a-mcp-v2/orchestrator:latest .
docker push us-central1-docker.pkg.dev/${PROJECT}/a2a-mcp-v2/orchestrator:latest
```

#### Deploy to Cloud Run:
```bash
# Deploy V2.0 orchestrator with all features
gcloud run deploy a2a-mcp-orchestrator-v2 \
  --image=us-central1-docker.pkg.dev/${PROJECT}/a2a-mcp-v2/orchestrator:latest \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated \
  --cpu=4 \
  --memory=8Gi \
  --concurrency=1000 \
  --timeout=3600 \
  --http2 \
  --set-env-vars="@env-v2.yaml" \
  --set-cloudsql-instances=${PROJECT}:us-central1:a2a-db \
  --vpc-connector=projects/${PROJECT}/locations/us-central1/connectors/vpc-connector \
  --service-account=a2a-v2-sa@${PROJECT}.iam.gserviceaccount.com \
  --execution-environment=gen2 \
  --cpu-boost \
  --session-affinity
```

#### Expected Output:
```bash
✓ Building and deploying from repository...
✓ Creating Container Repository...
✓ Uploading sources...
✓ Building Container... 
✓ Creating Revision...
✓ Routing traffic...
✓ Setting IAM Policy...
Done.
Service [a2a-mcp-orchestrator-v2] revision [a2a-mcp-orchestrator-v2-00001-xyz] has been deployed and is serving 100 percent of traffic.
Service URL: https://a2a-mcp-orchestrator-v2-xxx-uc.a.run.app
```

### Step 5: Deploy V2.0 Agent Services

#### Deploy StandardizedAgentBase Agents:
```bash
# Deploy each V2.0 agent as a microservice
for agent in "finance-analyst" "risk-assessor" "compliance-monitor" "fraud-detector"; do
  gcloud run deploy ${agent}-v2 \
    --source=./agents/${agent} \
    --cpu=2 --memory=4Gi \
    --concurrency=500 \
    --http2 \
    --set-env-vars="\
QUALITY_DOMAIN=ANALYTICAL,\
QUALITY_COMPLETENESS=0.95,\
QUALITY_ACCURACY=0.98,\
ENABLE_OBSERVABILITY=true"
done
```

#### Deploy GenericDomainAgent Services:
```bash
# Quick deployment of generic agents
gcloud run deploy generic-agent-v2 \
  --image=us-central1-docker.pkg.dev/${PROJECT}/a2a-mcp-v2/generic-agent:latest \
  --set-env-vars="\
AGENT_DOMAIN=${DOMAIN},\
AGENT_SPECIALIZATION=${SPECIALIZATION},\
AGENT_CAPABILITIES='analyze,validate,report',\
QUALITY_DOMAIN=GENERIC"
```

#### Deploy Quality Validation Service:
```bash
# Dedicated quality validation service
gcloud run deploy quality-validator-v2 \
  --source=./services/quality-validator \
  --cpu=1 --memory=2Gi \
  --concurrency=100 \
  --set-env-vars="VALIDATION_MODE=strict,QUALITY_THRESHOLD=0.90"
```

### Step 6: V2.0 Service Discovery Configuration
```yaml
# service-discovery-v2.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: agent-registry-v2
data:
  agents.json: |
    {
      "orchestrator": {
        "name": "Enhanced Master Orchestrator V2",
        "url": "https://a2a-mcp-orchestrator-v2-xxx.run.app",
        "version": "2.0.0",
        "features": {
          "phase7_streaming": true,
          "quality_validation": true,
          "parallel_execution": true,
          "connection_pooling": true
        }
      },
      "agents": [
        {
          "name": "Financial Analyst V2",
          "type": "StandardizedAgentBase",
          "url": "https://finance-analyst-v2-xxx.run.app",
          "quality_domain": "ANALYTICAL",
          "capabilities": ["analyze_markets", "evaluate_risk"]
        },
        {
          "name": "Generic Processor V2",
          "type": "GenericDomainAgent",
          "url": "https://generic-agent-v2-xxx.run.app",
          "quality_domain": "GENERIC",
          "configurable": true
        }
      ]
    }
```

### Step 4: Deploy Remaining Agents
```bash
# Deploy all A2A-MCP agents
adk deploy cloud_run --agent analytics_agent.py
adk deploy cloud_run --agent service_agent.py
adk deploy cloud_run --agent notification_agent.py
adk deploy cloud_run --agent data_processing_agent.py
adk deploy cloud_run --agent integration_agent.py
adk deploy cloud_run --agent workflow_agent.py
adk deploy cloud_run --agent reporting_agent.py
```

### Step 5: Deploy MCP Server
```bash
# Deploy MCP server to coordinate agents
cd src/a2a_mcp/mcp/
adk deploy cloud_run --service server.py
```

## 🧪 V2.0 Testing and Validation

### Testing PHASE 7 Streaming:
```bash
# Test streaming endpoint
curl -N -X POST https://a2a-mcp-orchestrator-v2-xxx.run.app/process \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{
    "query": "Analyze market trends for tech stocks",
    "session_id": "test-session",
    "task_id": "test-001"
  }'

# Expected streaming response:
data: {"type": "planning", "content": "Analyzing your query...", "timestamp": "2024-01-15T10:00:00Z"}
data: {"type": "task_start", "task": "market_analysis", "description": "Fetching market data"}
data: {"type": "progress", "percent": 25, "message": "Processing historical trends"}
data: {"type": "quality_check", "score": 0.94, "domain": "ANALYTICAL"}
data: {"type": "artifact", "artifact": {"type": "market_report", "data": {...}}}
data: {"type": "completed", "result": {...}, "quality_summary": {...}}
```

### Quality Validation Testing:
```python
# test_quality_v2.py
import requests
import json

def test_quality_validation():
    response = requests.post(
        "https://quality-validator-v2-xxx.run.app/validate",
        json={
            "content": "Test analysis content",
            "domain": "ANALYTICAL",
            "expected_score": 0.90
        }
    )
    
    result = response.json()
    assert result["quality_score"] >= 0.90
    assert all(result["dimension_scores"][dim] >= 0.85 for dim in result["dimension_scores"])
    print(f"Quality validation passed: {result['quality_score']:.2f}")
```

### V2.0 Performance Testing:
```bash
# Load test with V2.0 features
docker run -i grafana/k6 run - <<EOF
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  stages: [
    { duration: '30s', target: 100 },
    { duration: '1m', target: 500 },
    { duration: '30s', target: 1000 },
    { duration: '1m', target: 1000 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(99)<1000'], // 99% of requests under 1s
    http_req_failed: ['rate<0.01'], // Error rate under 1%
  },
};

export default function () {
  const url = 'https://a2a-mcp-orchestrator-v2-xxx.run.app/process';
  const payload = JSON.stringify({
    query: 'Test query ' + Math.random(),
    session_id: 'load-test',
    task_id: 'test-' + __VU + '-' + __ITER,
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ${TOKEN}',
    },
  };

  let response = http.post(url, payload, params);
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response has streaming data': (r) => r.body.includes('data:'),
    'quality score present': (r) => r.body.includes('quality_score'),
  });
}
EOF
```

### Observability Validation:
```bash
# Check traces in Cloud Trace
gcloud trace list --filter="\
  resource.type=\"cloud_run_revision\" AND \
  resource.labels.service_name=\"a2a-mcp-orchestrator-v2\" AND \
  timestamp>=\"$(date -u -Iseconds -d '5 minutes ago')\""

# View metrics in Cloud Monitoring
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/request_latencies" AND \
           resource.labels.service_name="a2a-mcp-orchestrator-v2"' \
  --format="table(resource.labels.service_name, metric.labels, points[0].value)"

# Check quality metrics
gcloud logging read '
  resource.type="cloud_run_revision" AND 
  resource.labels.service_name="a2a-mcp-orchestrator-v2" AND
  jsonPayload.quality_score>0' \
  --limit=10 \
  --format="json" | jq '.[] | {timestamp: .timestamp, quality: .jsonPayload.quality_score}'
```

#### For Streaming Responses:
```bash
# Set "streaming": true for Server-Sent Events
curl -X POST -H "Authorization: Bearer $TOKEN" \
    $APP_URL/run_sse \
    -H "Content-Type: application/json" \
    -d '{
    "app_name": "domain_specialist",
    "user_id": "user_123",
    "session_id": "session_abc", 
    "new_message": {
        "role": "user",
        "parts": [{
        "text": "Validate business rules for new order"
        }]
    },
    "streaming": true
    }'
```

## 📊 V2.0 Monitoring & Operations

### V2.0 Monitoring Dashboard:
```yaml
# monitoring/v2-dashboard.yaml
displayName: "A2A-MCP V2.0 Operations"
mosaicLayout:
  columns: 12
  tiles:
  - width: 6
    height: 4
    widget:
      title: "Request Latency (P50, P90, P99)"
      xyChart:
        dataSets:
        - timeSeriesQuery:
            timeSeriesFilter:
              filter: |
                resource.type="cloud_run_revision"
                metric.type="run.googleapis.com/request_latencies"
                resource.label.service_name=~".*-v2$"
            aggregation:
              alignmentPeriod: 60s
              perSeriesAligner: ALIGN_DELTA
              crossSeriesReducer: REDUCE_PERCENTILE_50
              groupByFields: ["resource.label.service_name"]
  - width: 6
    height: 4
    widget:
      title: "Quality Scores by Domain"
      xyChart:
        dataSets:
        - timeSeriesQuery:
            timeSeriesFilter:
              filter: |
                resource.type="cloud_run_revision"
                metric.type="custom.googleapis.com/a2a/quality_score"
            aggregation:
              alignmentPeriod: 60s
              perSeriesAligner: ALIGN_MEAN
              groupByFields: ["metric.label.quality_domain"]
  - width: 12
    height: 4
    widget:
      title: "Connection Pool Efficiency"
      xyChart:
        dataSets:
        - timeSeriesQuery:
            timeSeriesFilter:
              filter: |
                metric.type="custom.googleapis.com/a2a/connection_pool_reuse_rate"
```

### V2.0 Alert Policies:
```bash
# Create quality alert
gcloud alpha monitoring policies create \
  --notification-channels=${NOTIFICATION_CHANNEL} \
  --display-name="V2.0 Quality Score Alert" \
  --condition-display-name="Quality below threshold" \
  --condition="{
    \"displayName\": \"Quality Score < 0.85\",
    \"conditionThreshold\": {
      \"filter\": \"metric.type=\\\"custom.googleapis.com/a2a/quality_score\\\" resource.type=\\\"cloud_run_revision\\\"\",
      \"comparison\": \"COMPARISON_LT\",
      \"thresholdValue\": 0.85,
      \"duration\": \"300s\",
      \"aggregations\": [{
        \"alignmentPeriod\": \"60s\",
        \"perSeriesAligner\": \"ALIGN_MEAN\"
      }]
    }
  }"

# Create performance alert
gcloud alpha monitoring policies create \
  --notification-channels=${NOTIFICATION_CHANNEL} \
  --display-name="V2.0 Latency Alert" \
  --condition-display-name="P99 latency > 1s" \
  --condition="{
    \"displayName\": \"P99 Latency > 1000ms\",
    \"conditionThreshold\": {
      \"filter\": \"metric.type=\\\"run.googleapis.com/request_latencies\\\" resource.type=\\\"cloud_run_revision\\\" metric.label.\\\"response_code_class\\\"=\\\"2xx\\\"\",
      \"comparison\": \"COMPARISON_GT\",
      \"thresholdValue\": 1000,
      \"duration\": \"300s\",
      \"aggregations\": [{
        \"alignmentPeriod\": \"60s\",
        \"perSeriesAligner\": \"ALIGN_PERCENTILE_99\",
        \"crossSeriesReducer\": \"REDUCE_MAX\",
        \"groupByFields\": [\"resource.label.service_name\"]
      }]
    }
  }"
```

### V2.0 SLO Configuration:
```yaml
# slo-v2.yaml
apiVersion: monitoring.googleapis.com/v1
kind: ServiceLevelObjective
metadata:
  name: a2a-mcp-v2-slo
spec:
  serviceLevelIndicator:
    requestBased:
      goodTotalRatio:
        goodServiceFilter: |
          resource.type="cloud_run_revision"
          metric.type="run.googleapis.com/request_count"
          metric.label.response_code_class="2xx"
        totalServiceFilter: |
          resource.type="cloud_run_revision"
          metric.type="run.googleapis.com/request_count"
  goal: 0.999  # 99.9% availability
  rollingPeriod: 2419200s  # 28 days
```

## 💡 Benefits of ADK Cloud Deployment

- **Cost Optimization**: Pay only for actual usage (scales to zero)
- **Automatic Scaling**: Handle variable workloads seamlessly
- **Built-in Monitoring**: Google Cloud Operations integration
- **Security**: Google Cloud IAM and VPC integration
- **Reliability**: Google's infrastructure and SLA guarantees
- **Global Distribution**: Deploy to multiple regions easily

## 🔧 V2.0 Troubleshooting Guide

### 1. **Streaming Not Working**:
```bash
# Check HTTP/2 is enabled
gcloud run services describe a2a-mcp-orchestrator-v2 \
  --format="value(spec.template.metadata.annotations['run.googleapis.com/http2'])"

# Fix: Update service
gcloud run services update a2a-mcp-orchestrator-v2 --http2
```

### 2. **Quality Scores Missing**:
```python
# Debug quality validation
curl -X POST https://your-service.run.app/debug/quality \
  -H "Content-Type: application/json" \
  -d '{"test_content": "Sample text for validation"}'

# Check environment variables
gcloud run services describe a2a-mcp-orchestrator-v2 \
  --format="yaml" | grep -A 20 "env:"
```

### 3. **Connection Pool Issues**:
```bash
# Monitor connection metrics
gcloud logging read '
  resource.type="cloud_run_revision" AND
  jsonPayload.connection_pool_size>0' \
  --limit=50 \
  --format="table(timestamp, jsonPayload.connection_pool_size, jsonPayload.active_connections)"

# Adjust pool size
gcloud run services update a2a-mcp-orchestrator-v2 \
  --set-env-vars="CONNECTION_POOL_SIZE=50"
```

### 4. **Observability Data Missing**:
```bash
# Verify OpenTelemetry is running
gcloud logging read '
  textPayload:"OpenTelemetry" AND
  resource.labels.service_name="a2a-mcp-orchestrator-v2"' \
  --limit=10

# Check trace export
gcloud trace list --limit=5 --filter='resource.labels.service_name="a2a-mcp-orchestrator-v2"'

# Fix: Ensure OTEL environment variables are set
gcloud run services update a2a-mcp-orchestrator-v2 \
  --set-env-vars="\
OTEL_SERVICE_NAME=a2a-mcp-v2,\
OTEL_TRACES_EXPORTER=gcp_trace,\
OTEL_METRICS_EXPORTER=gcp_monitoring"
```

### 5. **Performance Degradation**:
```bash
# Enable CPU boost for better cold starts
gcloud run services update a2a-mcp-orchestrator-v2 \
  --cpu-boost

# Increase minimum instances
gcloud run services update a2a-mcp-orchestrator-v2 \
  --min-instances=2

# Enable session affinity for stateful connections
gcloud run services update a2a-mcp-orchestrator-v2 \
  --session-affinity
```

## 🚀 V2.0 Advanced Deployment Patterns

### Multi-Region Active-Active Deployment:
```bash
# Deploy to multiple regions with global load balancing
REGIONS=("us-central1" "europe-west1" "asia-southeast1")

for REGION in "${REGIONS[@]}"; do
  gcloud run deploy a2a-mcp-orchestrator-v2-${REGION} \
    --image=us-central1-docker.pkg.dev/${PROJECT}/a2a-mcp-v2/orchestrator:latest \
    --region=${REGION} \
    --set-env-vars="REGION=${REGION},ENABLE_CROSS_REGION_SYNC=true" \
    --vpc-connector=projects/${PROJECT}/locations/${REGION}/connectors/vpc-connector
done

# Set up global load balancer
gcloud compute backend-services create a2a-mcp-v2-global \
  --global \
  --load-balancing-scheme=EXTERNAL_MANAGED \
  --protocol=HTTP2

# Add regional backends
for REGION in "${REGIONS[@]}"; do
  gcloud compute backend-services add-backend a2a-mcp-v2-global \
    --global \
    --network-endpoint-group=a2a-mcp-orchestrator-v2-${REGION}-neg \
    --network-endpoint-group-region=${REGION}
done
```

### V2.0 GitOps Deployment:
```yaml
# .github/workflows/deploy-v2.yml
name: Deploy A2A-MCP V2.0
on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - 'Dockerfile'
      - '.github/workflows/deploy-v2.yml'

jobs:
  quality-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run V2.0 Quality Validation
        run: |
          python -m pytest tests/v2/test_quality.py
          python scripts/validate_quality_thresholds.py

  build-and-deploy:
    needs: quality-check
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    
    steps:
      - uses: actions/checkout@v3
      
      - id: 'auth'
        uses: 'google-github-actions/auth@v2'
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
      
      - name: 'Set up Cloud SDK'
        uses: 'google-github-actions/setup-gcloud@v2'
      
      - name: 'Configure Docker'
        run: gcloud auth configure-docker us-central1-docker.pkg.dev
      
      - name: 'Build and Push V2.0 Image'
        run: |
          docker build -t us-central1-docker.pkg.dev/${{ vars.PROJECT }}/a2a-mcp-v2/orchestrator:${{ github.sha }} .
          docker push us-central1-docker.pkg.dev/${{ vars.PROJECT }}/a2a-mcp-v2/orchestrator:${{ github.sha }}
      
      - name: 'Deploy to Cloud Run'
        run: |
          gcloud run deploy a2a-mcp-orchestrator-v2 \
            --image=us-central1-docker.pkg.dev/${{ vars.PROJECT }}/a2a-mcp-v2/orchestrator:${{ github.sha }} \
            --region=us-central1 \
            --set-env-vars="@.github/env-v2.yaml" \
            --service-account=a2a-v2-sa@${{ vars.PROJECT }}.iam.gserviceaccount.com
      
      - name: 'Run Smoke Tests'
        run: |
          SERVICE_URL=$(gcloud run services describe a2a-mcp-orchestrator-v2 --region=us-central1 --format='value(status.url)')
          python scripts/smoke_test_v2.py --url=$SERVICE_URL

  deploy-agents:
    needs: build-and-deploy
    runs-on: ubuntu-latest
    strategy:
      matrix:
        agent: [finance-analyst, risk-assessor, compliance-monitor]
    
    steps:
      - uses: actions/checkout@v3
      - name: Deploy ${{ matrix.agent }} Agent
        run: |
          gcloud run deploy ${{ matrix.agent }}-v2 \
            --source=./agents/${{ matrix.agent }} \
            --region=us-central1 \
            --set-env-vars="ORCHESTRATOR_URL=${{ needs.build-and-deploy.outputs.service-url }}"
```

### Terraform Infrastructure as Code:
```hcl
# terraform/main.tf
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

resource "google_cloud_run_v2_service" "orchestrator" {
  name     = "a2a-mcp-orchestrator-v2"
  location = var.region
  
  template {
    service_account = google_service_account.a2a_v2.email
    
    scaling {
      min_instance_count = 2
      max_instance_count = 1000
    }
    
    containers {
      image = "us-central1-docker.pkg.dev/${var.project}/a2a-mcp-v2/orchestrator:latest"
      
      resources {
        limits = {
          cpu    = "4"
          memory = "8Gi"
        }
        cpu_idle = false
      }
      
      env {
        name  = "ENABLE_PHASE_7_STREAMING"
        value = "true"
      }
      
      env {
        name  = "ENABLE_OBSERVABILITY"
        value = "true"
      }
    }
    
    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "ALL_TRAFFIC"
    }
  }
  
  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}
```

## 🎆 V2.0 Production Checklist

☐ Enable all V2.0 features (streaming, observability, quality)
☐ Configure connection pooling with appropriate size
☐ Set up monitoring dashboards and alerts
☐ Implement SLOs for quality scores and latency
☐ Deploy to multiple regions for high availability
☐ Enable Cloud Armor for DDoS protection
☐ Configure backup and disaster recovery
☐ Set up CI/CD with quality gates
☐ Document runbooks for common issues
☐ Load test with expected traffic patterns

This comprehensive V2.0 deployment guide enables you to leverage all the enhanced features of the A2A-MCP Framework V2.0 on Google Cloud Platform!