# Generic Deployment Guide - Framework V2.0

This guide covers deployment strategies for the A2A-MCP Framework V2.0 across different platforms and environments, including the new observability stack and quality framework.

## 🎯 Overview

The A2A-MCP Framework V2.0 can be deployed in multiple configurations, from local development to enterprise cloud deployments with full observability. This guide provides platform-agnostic deployment strategies that work for any business domain, with emphasis on V2.0 features like distributed tracing, metrics collection, and quality validation.

## 📚 Essential References
- [Framework Components Guide](./FRAMEWORK_COMPONENTS_AND_ORCHESTRATION_GUIDE.md)
- [Observability Deployment Guide](./OBSERVABILITY_DEPLOYMENT.md)
- [Multi-Agent Workflow Guide](./MULTI_AGENT_WORKFLOW_GUIDE.md)

## 🏗️ Deployment Architectures

### Single-Node Development
**Use Case**: Local development, testing, prototyping  
**Complexity**: Low  
**Cost**: Free  
**Scalability**: Limited  

### Multi-Node Production
**Use Case**: Production workloads, high availability  
**Complexity**: Medium  
**Cost**: Medium  
**Scalability**: High  

### Cloud-Native Microservices
**Use Case**: Enterprise, auto-scaling, global distribution  
**Complexity**: High  
**Cost**: Variable  
**Scalability**: Unlimited  

### Hybrid Edge-Cloud
**Use Case**: Edge computing, latency-sensitive applications  
**Complexity**: High  
**Cost**: High  
**Scalability**: Regional  

## 🚀 Quick Start Deployments

### Local Development Setup

**Prerequisites**:
- Python 3.9+
- Docker (optional)
- Git

**1. Environment Setup**:
```bash
# Clone the framework
git clone <your-repository>
cd agentic-framework-boilerplate

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
# Edit .env with your API keys and configuration
```

**2. Local Configuration (V2.0)**:
```bash
# .env file
# Core Settings
A2A_LOG_LEVEL=INFO
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=10100

# LLM Provider API Keys
GEMINI_API_KEY=your_gemini_key
# OR
OPENAI_API_KEY=your_openai_key
# OR
ANTHROPIC_API_KEY=your_anthropic_key

# V2.0 Observability Settings
ENABLE_OBSERVABILITY=true
OTEL_SERVICE_NAME=a2a-mcp-framework
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
TRACING_ENABLED=true
METRICS_ENABLED=true
METRICS_PORT=9090
JSON_LOGS=true

# V2.0 Quality Framework
DEFAULT_QUALITY_DOMAIN=GENERIC
MIN_QUALITY_SCORE=0.85

# V2.0 Performance
CONNECTION_POOL_SIZE=20
ENABLE_HTTP2=true
ENABLE_PHASE_7_STREAMING=true

# Database configuration (optional)
DATABASE_URL=sqlite:///./data/framework.db
```

**3. Start Services**:
```bash
# Start all services
./start.sh

# Or start individually for debugging
python -m src.a2a_mcp.mcp.server &
python -m src.a2a_mcp.agents --agent-card agent_cards/tier1/master_orchestrator.json --port 10001 &
python -m src.a2a_mcp.agents --agent-card agent_cards/tier2/domain_specialist.json --port 10002 &
```

**4. Test Deployment**:
```bash
# Run test suite
./run_tests.sh

# Test with example client
python examples/simple_client.py

# Interactive testing
curl -X POST http://localhost:10001 \
  -H "Content-Type: application/json" \
  -d '{"message": {"role": "user", "parts": [{"text": "Hello, test the system"}]}}'
```

### Docker Containerized Deployment

**1. Container Configuration**:

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ src/
COPY agent_cards/ agent_cards/
COPY configs/ configs/
COPY examples/ examples/

# Create non-root user
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/health || exit 1

# Default command
CMD ["python", "-m", "src.a2a_mcp.mcp.server"]
```

Create `docker-compose.yml` (V2.0 with Observability):
```yaml
version: '3.8'

services:
  # Observability Stack (V2.0)
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # Jaeger UI
      - "14268:14268"  # HTTP collector
    environment:
      - COLLECTOR_ZIPKIN_HOST_PORT=:9411

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./configs/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - ./src/a2a_mcp/common/dashboards:/var/lib/grafana/dashboards
      - grafana_data:/var/lib/grafana

  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    ports:
      - "4317:4317"   # OTLP gRPC
      - "4318:4318"   # OTLP HTTP
    volumes:
      - ./configs/otel-collector.yaml:/etc/otel-collector.yaml
    command: ["--config=/etc/otel-collector.yaml"]

  # A2A-MCP Services
  mcp-server:
    build: .
    ports:
      - "10100:10100"
    environment:
      - MCP_SERVER_HOST=0.0.0.0
      - MCP_SERVER_PORT=10100
      - A2A_LOG_LEVEL=INFO
      # V2.0 Observability
      - ENABLE_OBSERVABILITY=true
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
      - TRACING_ENABLED=true
      - METRICS_ENABLED=true
      - JSON_LOGS=true
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:10100/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    depends_on:
      - otel-collector

  orchestrator:
    build: .
    ports:
      - "10001:10001"
    environment:
      - AGENT_CARD=agent_cards/tier1/master_orchestrator.json
      - AGENT_PORT=10001
      - MCP_SERVER_URL=http://mcp-server:10100
      # V2.0 Features
      - ENABLE_PHASE_7_STREAMING=true
      - ENABLE_OBSERVABILITY=true
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
      - DEFAULT_QUALITY_DOMAIN=GENERIC
      - CONNECTION_POOL_SIZE=20
    depends_on:
      - mcp-server
      - otel-collector
    command: ["python", "-m", "src.a2a_mcp.agents"]
    restart: unless-stopped

  domain-specialist:
    build: .
    ports:
      - "10002:10002"
    environment:
      - AGENT_CARD=agent_cards/tier2/domain_specialist.json
      - AGENT_PORT=10002
      - MCP_SERVER_URL=http://mcp-server:10100
    depends_on:
      - mcp-server
    command: ["python", "-m", "src.a2a_mcp.agents"]
    restart: unless-stopped
    scale: 2  # Run 2 instances for load balancing

volumes:
  prometheus_data:
  grafana_data:

  service-agent:
    build: .
    ports:
      - "10003-10005:10003"
    environment:
      - AGENT_CARD=agent_cards/tier3/service_agent.json
      - AGENT_PORT=10003
      - MCP_SERVER_URL=http://mcp-server:10100
    depends_on:
      - mcp-server
    command: ["python", "-m", "src.a2a_mcp.agents"]
    restart: unless-stopped
    scale: 3  # Run 3 instances for different services

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./configs/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - orchestrator
      - domain-specialist
      - service-agent
    restart: unless-stopped

volumes:
  data:
  logs:
```

**2. Start Docker Deployment**:
```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Scale specific services
docker-compose up -d --scale domain-specialist=3

# Stop services
docker-compose down
```

## ☁️ Cloud Platform Deployments

### Prerequisites for V2.0 Cloud Deployments

**Required Services**:
- Container orchestration (ECS, Cloud Run, AKS)
- Load balancing for agent distribution
- Observability stack (Jaeger, Prometheus, Grafana)
- Connection pooling support
- PHASE 7 streaming capabilities

### AWS Deployment

**Architecture**: ECS Fargate + ALB + RDS + OpenTelemetry

**1. Infrastructure as Code (Terraform)**:

Create `terraform/main.tf`:
```hcl
provider "aws" {
  region = var.aws_region
}

# VPC and networking
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  
  name = "a2a-mcp-vpc"
  cidr = "10.0.0.0/16"
  
  azs             = ["${var.aws_region}a", "${var.aws_region}b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]
  
  enable_nat_gateway = true
  enable_vpn_gateway = false
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "a2a-mcp-cluster"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "a2a-mcp-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets           = module.vpc.public_subnets
}

# ECS Service for MCP Server
resource "aws_ecs_service" "mcp_server" {
  name            = "mcp-server"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.mcp_server.arn
  desired_count   = 2
  
  load_balancer {
    target_group_arn = aws_lb_target_group.mcp_server.arn
    container_name   = "mcp-server"
    container_port   = 10100
  }
  
  depends_on = [aws_lb_listener.main]
}

# V2.0 Observability Infrastructure
module "observability" {
  source = "./modules/observability"
  
  cluster_name = aws_ecs_cluster.main.name
  vpc_id       = module.vpc.vpc_id
  subnets      = module.vpc.private_subnets
}

# ECS Task Definition for MCP Server (V2.0)
resource "aws_ecs_task_definition" "mcp_server" {
  family                   = "mcp-server-v2"
  network_mode            = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                     = 1024  # Increased for V2.0
  memory                  = 2048  # Increased for V2.0
  execution_role_arn      = aws_iam_role.ecs_execution_role.arn
  task_role_arn          = aws_iam_role.ecs_task_role.arn
  
  container_definitions = jsonencode([
    {
      name  = "mcp-server"
      image = "${aws_ecr_repository.app.repository_url}:v2-latest"
      
      portMappings = [
        {
          containerPort = 10100
          protocol      = "tcp"
        },
        {
          containerPort = 9090  # Metrics port
          protocol      = "tcp"
        }
      ]
      
      environment = [
        {
          name  = "MCP_SERVER_HOST"
          value = "0.0.0.0"
        },
        {
          name  = "MCP_SERVER_PORT" 
          value = "10100"
        },
        # V2.0 Observability
        {
          name  = "ENABLE_OBSERVABILITY"
          value = "true"
        },
        {
          name  = "OTEL_EXPORTER_OTLP_ENDPOINT"
          value = module.observability.collector_endpoint
        },
        {
          name  = "TRACING_ENABLED"
          value = "true"
        },
        {
          name  = "METRICS_ENABLED"
          value = "true"
        },
        {
          name  = "JSON_LOGS"
          value = "true"
        },
        # V2.0 Performance
        {
          name  = "CONNECTION_POOL_SIZE"
          value = "20"
        },
        {
          name  = "ENABLE_HTTP2"
          value = "true"
        },
        {
          name  = "ENABLE_PHASE_7_STREAMING"
          value = "true"
        },
        # V2.0 Quality Framework
        {
          name  = "DEFAULT_QUALITY_DOMAIN"
          value = "GENERIC"
        },
        {
          name  = "MIN_QUALITY_SCORE"
          value = "0.85"
        }
      ]
      
      secrets = [
        {
          name      = "OPENAI_API_KEY"
          valueFrom = aws_ssm_parameter.openai_api_key.arn
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.app.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "mcp-server"
        }
      }
      
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:10100/health || exit 1"]
        interval    = 30
        timeout     = 10
        retries     = 3
        startPeriod = 60
      }
    }
  ])
}
```

**2. Deploy to AWS**:
```bash
# Initialize Terraform
cd terraform
terraform init

# Plan deployment
terraform plan

# Deploy infrastructure
terraform apply

# Push Docker image to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-west-2.amazonaws.com
docker build -t a2a-mcp .
docker tag a2a-mcp:latest <account-id>.dkr.ecr.us-west-2.amazonaws.com/a2a-mcp:latest
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/a2a-mcp:latest

# Update ECS service
aws ecs update-service --cluster a2a-mcp-cluster --service mcp-server --force-new-deployment
```

### Google Cloud Platform Deployment

**Architecture**: Cloud Run + Cloud Load Balancing + Cloud SQL

**1. Deployment Configuration**:

Create `cloudbuild.yaml`:
```yaml
steps:
  # Build container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/a2a-mcp:$COMMIT_SHA', '.']
  
  # Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/a2a-mcp:$COMMIT_SHA']
  
  # Deploy MCP Server to Cloud Run (V2.0)
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
    - 'run'
    - 'deploy'
    - 'mcp-server-v2'
    - '--image'
    - 'gcr.io/$PROJECT_ID/a2a-mcp:v2-$COMMIT_SHA'
    - '--region'
    - 'us-central1'
    - '--platform'
    - 'managed'
    - '--allow-unauthenticated'
    - '--port'
    - '10100'
    - '--memory'
    - '2Gi'  # Increased for V2.0
    - '--cpu'
    - '2'    # Increased for V2.0
    - '--min-instances'
    - '2'    # Increased for HA
    - '--max-instances'
    - '20'   # Increased for scalability
    - '--set-env-vars'
    - 'ENABLE_OBSERVABILITY=true,OTEL_EXPORTER_OTLP_ENDPOINT=https://otel-collector.example.com:4317,TRACING_ENABLED=true,METRICS_ENABLED=true,JSON_LOGS=true,CONNECTION_POOL_SIZE=20,ENABLE_HTTP2=true,ENABLE_PHASE_7_STREAMING=true,DEFAULT_QUALITY_DOMAIN=GENERIC,MIN_QUALITY_SCORE=0.85'
  
  # Deploy Orchestrator
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
    - 'run'
    - 'deploy'
    - 'orchestrator'
    - '--image'
    - 'gcr.io/$PROJECT_ID/a2a-mcp:$COMMIT_SHA'
    - '--region'
    - 'us-central1'
    - '--platform'
    - 'managed'
    - '--allow-unauthenticated'
    - '--port'
    - '10001'
    - '--set-env-vars'
    - 'AGENT_CARD=agent_cards/tier1/master_orchestrator.json'

images:
  - 'gcr.io/$PROJECT_ID/a2a-mcp:$COMMIT_SHA'
```

**2. Deploy to GCP**:
```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sql-component.googleapis.com

# Deploy with Cloud Build
gcloud builds submit --config cloudbuild.yaml

# Set up load balancer
gcloud compute url-maps create a2a-mcp-map --default-service=orchestrator-backend
gcloud compute backend-services create orchestrator-backend \
  --protocol=HTTP \
  --port-name=http \
  --health-checks=orchestrator-health-check \
  --global

# Configure domain mapping
gcloud run domain-mappings create --service=orchestrator --domain=your-domain.com
```

### Azure Deployment

**Architecture**: Container Instances + Application Gateway + Azure Database

**1. Resource Group Setup**:
```bash
# Create resource group
az group create --name a2a-mcp-rg --location eastus

# Create container registry
az acr create --resource-group a2a-mcp-rg --name a2amcpregistry --sku Standard

# Build and push image
az acr build --registry a2amcpregistry --image a2a-mcp:latest .
```

**2. Deploy Container Instances**:

Create `azure-deploy.yml`:
```yaml
apiVersion: 2019-12-01
location: eastus
name: a2a-mcp-container-group
properties:
  containers:
  - name: mcp-server
    properties:
      image: a2amcpregistry.azurecr.io/a2a-mcp:latest
      ports:
      - port: 10100
        protocol: TCP
      resources:
        requests:
          cpu: 1.0
          memoryInGB: 2.0
      environmentVariables:
      - name: MCP_SERVER_HOST
        value: "0.0.0.0"
      - name: MCP_SERVER_PORT
        value: "10100"
      - name: OPENAI_API_KEY
        secureValue: "<your-openai-key>"
  
  - name: orchestrator
    properties:
      image: a2amcpregistry.azurecr.io/a2a-mcp:latest
      ports:
      - port: 10001
        protocol: TCP
      resources:
        requests:
          cpu: 1.0
          memoryInGB: 2.0
      environmentVariables:
      - name: AGENT_CARD
        value: "agent_cards/tier1/master_orchestrator.json"
      - name: AGENT_PORT
        value: "10001"
      - name: MCP_SERVER_URL
        value: "http://localhost:10100"
  
  osType: Linux
  restartPolicy: Always
  ipAddress:
    type: Public
    ports:
    - protocol: TCP
      port: 80
    - protocol: TCP
      port: 443
    dnsNameLabel: a2a-mcp-deployment
  imageRegistryCredentials:
  - server: a2amcpregistry.azurecr.io
    username: a2amcpregistry
    password: "<registry-password>"

tags:
  Environment: production
  Application: a2a-mcp
type: Microsoft.ContainerInstance/containerGroups
```

**3. Deploy to Azure**:
```bash
# Deploy container group
az container create --resource-group a2a-mcp-rg --file azure-deploy.yml

# Set up application gateway
az network application-gateway create \
  --name a2a-mcp-gateway \
  --resource-group a2a-mcp-rg \
  --location eastus \
  --capacity 2 \
  --sku Standard_v2
```

### Kubernetes Deployment (V2.0)

**Architecture**: Multi-pod deployment with service mesh and full observability

**1. V2.0 Kubernetes Manifests**:

Create `k8s/namespace.yaml`:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: a2a-mcp-v2
  labels:
    name: a2a-mcp-v2
    version: "2.0"
    istio-injection: enabled  # For service mesh
```

Create `k8s/configmap.yaml`:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: a2a-mcp-config-v2
  namespace: a2a-mcp-v2
data:
  # Core Settings
  MCP_SERVER_HOST: "0.0.0.0"
  MCP_SERVER_PORT: "10100"
  A2A_LOG_LEVEL: "INFO"
  
  # V2.0 Observability
  ENABLE_OBSERVABILITY: "true"
  OTEL_SERVICE_NAME: "a2a-mcp-framework"
  OTEL_EXPORTER_OTLP_ENDPOINT: "http://otel-collector.observability:4317"
  TRACING_ENABLED: "true"
  METRICS_ENABLED: "true"
  METRICS_PORT: "9090"
  JSON_LOGS: "true"
  
  # V2.0 Quality Framework
  DEFAULT_QUALITY_DOMAIN: "GENERIC"
  MIN_QUALITY_SCORE: "0.85"
  
  # V2.0 Performance
  CONNECTION_POOL_SIZE: "20"
  ENABLE_HTTP2: "true"
  ENABLE_PHASE_7_STREAMING: "true"
  
  # V2.0 Orchestration
  PARALLEL_THRESHOLD: "3"
  SESSION_TIMEOUT: "3600"
  ENABLE_DYNAMIC_WORKFLOWS: "true"
```

Create `k8s/deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
  namespace: a2a-mcp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-server
  template:
    metadata:
      labels:
        app: mcp-server
    spec:
      containers:
      - name: mcp-server
        image: a2a-mcp:v2-latest
        ports:
        - containerPort: 10100
          name: http
        - containerPort: 9090
          name: metrics
        envFrom:
        - configMapRef:
            name: a2a-mcp-config-v2
        - secretRef:
            name: a2a-mcp-secrets
        resources:
          requests:
            memory: "1Gi"   # Increased for V2.0
            cpu: "500m"     # Increased for V2.0
          limits:
            memory: "2Gi"   # Increased for V2.0
            cpu: "1000m"    # Increased for V2.0
        livenessProbe:
          httpGet:
            path: /health
            port: 10100
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 10100
          initialDelaySeconds: 5
          periodSeconds: 5
        # V2.0: Sidecar for distributed tracing
      - name: jaeger-agent
        image: jaegertracing/jaeger-agent:latest
        ports:
        - containerPort: 5775
          protocol: UDP
        - containerPort: 6831
          protocol: UDP
        - containerPort: 6832
          protocol: UDP
        - containerPort: 5778
          protocol: TCP
        args:
        - "--reporter.grpc.host-port=jaeger-collector.observability:14250"
        resources:
          limits:
            memory: "128Mi"
            cpu: "100m"
---
apiVersion: v1
kind: Service
metadata:
  name: mcp-server-service
  namespace: a2a-mcp
spec:
  selector:
    app: mcp-server
  ports:
    - protocol: TCP
      port: 80
      targetPort: 10100
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: a2a-mcp-ingress
  namespace: a2a-mcp
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: a2a-mcp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: mcp-server-service
            port:
              number: 80
```

**2. Deploy to Kubernetes**:
```bash
# Apply manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n a2a-mcp
kubectl get services -n a2a-mcp

# Scale deployment
kubectl scale deployment mcp-server --replicas=5 -n a2a-mcp

# Update deployment
kubectl set image deployment/mcp-server mcp-server=a2a-mcp:v2 -n a2a-mcp
```

## 🔒 Security Considerations

### Authentication & Authorization

**1. API Security**:
```bash
# Generate secure API keys
python -c "import secrets; print(f'API_KEY_{secrets.token_urlsafe(32)}')"

# Set up JWT authentication
export JWT_SECRET_KEY="your-secure-secret-key"
export JWT_ALGORITHM="HS256"
export JWT_EXPIRATION_HOURS=24
```

**2. Network Security**:
```bash
# Configure firewall rules (example for AWS)
aws ec2 create-security-group --group-name a2a-mcp-sg --description "A2A-MCP Security Group"
aws ec2 authorize-security-group-ingress --group-name a2a-mcp-sg --protocol tcp --port 443 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-name a2a-mcp-sg --protocol tcp --port 80 --cidr 0.0.0.0/0
```

**3. Secrets Management**:

For AWS:
```bash
# Store secrets in Parameter Store
aws ssm put-parameter --name "/a2a-mcp/openai-api-key" --value "your-api-key" --type "SecureString"
aws ssm put-parameter --name "/a2a-mcp/database-password" --value "your-db-password" --type "SecureString"
```

For Kubernetes:
```bash
# Create secrets
kubectl create secret generic a2a-mcp-secrets \
  --from-literal=OPENAI_API_KEY=your-api-key \
  --from-literal=DATABASE_PASSWORD=your-db-password \
  -n a2a-mcp
```

### SSL/TLS Configuration

**1. Let's Encrypt with Certbot**:
```bash
# Install certbot
sudo apt-get install certbot

# Generate certificates
sudo certbot certonly --standalone -d yourdomain.com

# Configure auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

**2. Load Balancer SSL Termination**:
```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/ssl/certs/yourdomain.com.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.com.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    
    location / {
        proxy_pass http://backend_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📊 Monitoring & Observability (V2.0)

### V2.0 Observability Stack

**Components**:
- **OpenTelemetry Collector**: Central telemetry hub
- **Jaeger**: Distributed tracing
- **Prometheus**: Metrics collection
- **Grafana**: Visualization and dashboards
- **Structured Logging**: JSON logs with trace correlation

### Health Checks (V2.0)

**1. Enhanced Health Endpoints**:
```python
# V2.0 Health check with quality and performance metrics
from a2a_mcp.common.metrics_collector import get_metrics_collector
from a2a_mcp.common.quality_framework import QualityThresholdFramework

@app.route('/health')
async def health_check():
    metrics = get_metrics_collector()
    quality = QualityThresholdFramework()
    
    # Get system metrics
    system_health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "metrics": {
            "active_connections": metrics.get_active_connections(),
            "connection_pool_health": metrics.get_pool_health(),
            "quality_domain": quality.current_domain.value,
            "min_quality_score": quality.get_min_threshold()
        },
        "features": {
            "observability": True,
            "phase_7_streaming": True,
            "connection_pooling": True,
            "quality_validation": True
        }
    }
    return system_health

@app.route('/ready') 
async def readiness_check():
    # V2.0: Enhanced dependency checks
    checks = {
        "mcp_server": await check_mcp_server_connection(),
        "database": await check_database_connection(),
        "observability": await check_otel_connection(),
        "connection_pool": check_pool_ready()
    }
    
    all_ready = all(checks.values())
    
    return {
        "status": "ready" if all_ready else "not ready",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }, 200 if all_ready else 503
```

**2. V2.0 Monitoring Stack**:

Create `monitoring/docker-compose.yml`:
```yaml
version: '3.8'

services:
  # OpenTelemetry Collector (V2.0)
  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    command: ["--config=/etc/otel-collector.yaml"]
    ports:
      - "4317:4317"   # OTLP gRPC
      - "4318:4318"   # OTLP HTTP
      - "8888:8888"   # Prometheus metrics
    volumes:
      - ./configs/otel-collector.yaml:/etc/otel-collector.yaml
    environment:
      - OTEL_RESOURCE_ATTRIBUTES=service.name=otel-collector

  # Jaeger for Distributed Tracing
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # Jaeger UI
      - "14268:14268"  # HTTP collector
      - "14250:14250"  # gRPC collector
    environment:
      - COLLECTOR_OTLP_ENABLED=true
      - SPAN_STORAGE_TYPE=badger
      - BADGER_EPHEMERAL=false
      - BADGER_DIRECTORY_VALUE=/badger/data
      - BADGER_DIRECTORY_KEY=/badger/key
    volumes:
      - jaeger-data:/badger

  # Prometheus for Metrics
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./configs/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'

  # Grafana for Visualization
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
    volumes:
      - grafana-data:/var/lib/grafana
      - ./src/a2a_mcp/common/dashboards:/etc/grafana/provisioning/dashboards
      - ./configs/grafana-datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml
    depends_on:
      - prometheus
      - jaeger

  # Loki for Log Aggregation (V2.0)
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - ./configs/loki.yaml:/etc/loki/loki.yaml
      - loki-data:/loki
    command: -config.file=/etc/loki/loki.yaml

  # Promtail for Log Collection
  promtail:
    image: grafana/promtail:latest
    volumes:
      - ./configs/promtail.yaml:/etc/promtail/promtail.yaml
      - /var/log:/var/log:ro
      - ./logs:/app/logs:ro
    command: -config.file=/etc/promtail/promtail.yaml

volumes:
  prometheus-data:
  grafana-data:
  jaeger-data:
  loki-data:
```

### V2.0 Structured Logging

**1. Enhanced Structured Logging with Trace Correlation**:
```python
# V2.0 Structured logging with full observability integration
from a2a_mcp.common.structured_logger import StructuredLogger
from a2a_mcp.common.observability import get_trace_context

# Initialize V2.0 logger
logger = StructuredLogger("my_agent")

# Logs automatically include trace context
logger.info("Processing request", extra={
    "request_id": request_id,
    "action": action,
    "quality_domain": "ANALYSIS",
    "session_id": session_id
})

# Error logging with full context
try:
    result = await process_task(task)
except Exception as e:
    logger.error("Task processing failed", 
        extra={
            "error_type": type(e).__name__,
            "task_id": task.id,
            "trace_id": get_trace_context().trace_id,
            "span_id": get_trace_context().span_id
        },
        exc_info=True
    )

# Performance logging
with logger.log_duration("database_query"):
    results = await db.query(sql)
# Automatically logs duration and adds to metrics
```

**2. Log Aggregation**:

Create `logging/filebeat.yml`:
```yaml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /app/logs/*.log
  fields:
    service: a2a-mcp
  fields_under_root: true

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  
setup.kibana:
  host: "kibana:5601"

logging.level: info
```

## 🚀 Performance Optimization (V2.0)

### V2.0 Performance Features

**Key Improvements**:
- 60% performance boost via connection pooling
- HTTP/2 support for multiplexing
- Parallel workflow execution
- PHASE 7 streaming for real-time visibility
- Intelligent caching strategies

### Connection Pooling Configuration

**1. V2.0 Connection Pool Setup**:
```python
# V2.0 Connection pooling for optimal performance
from a2a_mcp.common.connection_pool import ConnectionPool

# Initialize with V2.0 settings
connection_pool = ConnectionPool(
    max_connections=20,
    max_keepalive_connections=10,
    keepalive_expiry=30.0,
    enable_http2=True,  # V2.0: HTTP/2 support
    enable_metrics=True  # V2.0: Pool metrics
)

# Monitor pool performance
pool_stats = connection_pool.get_statistics()
print(f"Connection reuse rate: {pool_stats['connection_reuse_rate']}%")
print(f"Average response time: {pool_stats['avg_response_time_ms']}ms")
```

### Caching Strategy (V2.0)

**1. Redis Configuration with Clustering**:
```yaml
# docker-compose.yml V2.0 caching
  # Redis Cluster for V2.0
  redis-master:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-master-data:/data
    command: >
      redis-server
      --appendonly yes
      --maxmemory 2gb
      --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    
  redis-replica:
    image: redis:7-alpine
    ports:
      - "6380:6379"
    volumes:
      - redis-replica-data:/data
    command: redis-server --replicaof redis-master 6379
    depends_on:
      - redis-master
    
  redis-sentinel:
    image: redis:7-alpine
    ports:
      - "26379:26379"
    command: redis-sentinel /etc/redis/sentinel.conf
    volumes:
      - ./configs/redis-sentinel.conf:/etc/redis/sentinel.conf
    depends_on:
      - redis-master
      - redis-replica

volumes:
  redis-master-data:
  redis-replica-data:
```

**2. V2.0 Intelligent Caching**:
```python
# V2.0 Enhanced caching with quality awareness
from a2a_mcp.common.cache_manager import CacheManager
from a2a_mcp.common.quality_framework import QualityDomain

# Initialize V2.0 cache manager
cache_manager = CacheManager(
    redis_url="redis://redis-master:6379",
    enable_clustering=True,
    enable_metrics=True
)

# Quality-aware caching
@cache_manager.cache_with_quality(
    expiration=3600,
    quality_threshold=0.9,  # Only cache high-quality results
    domain=QualityDomain.ANALYSIS
)
async def analyze_data(data: dict) -> dict:
    # Expensive analysis operation
    result = await perform_analysis(data)
    return result

# Cache with invalidation patterns
@cache_manager.cache_with_invalidation(
    expiration=1800,
    invalidation_patterns=["user:*:update", "data:refresh"]
)
async def get_user_insights(user_id: str) -> dict:
    # Automatically invalidated when user data changes
    return await calculate_insights(user_id)

# Monitor cache performance
cache_stats = cache_manager.get_statistics()
print(f"Cache hit rate: {cache_stats['hit_rate']}%")
print(f"Average retrieval time: {cache_stats['avg_retrieval_ms']}ms")
```

### V2.0 Auto-Scaling Configuration

**1. Enhanced Kubernetes HPA with Custom Metrics**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: mcp-server-hpa-v2
  namespace: a2a-mcp-v2
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: mcp-server
  minReplicas: 3
  maxReplicas: 50  # Increased for V2.0
  metrics:
  # Standard resource metrics
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  # V2.0 Custom metrics
  - type: Pods
    pods:
      metric:
        name: agent_request_rate
      target:
        type: AverageValue
        averageValue: "100"
  - type: Pods
    pods:
      metric:
        name: connection_pool_saturation
      target:
        type: AverageValue
        averageValue: "0.8"
  - type: Pods
    pods:
      metric:
        name: quality_validation_latency_ms
      target:
        type: AverageValue
        averageValue: "500"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
      - type: Pods
        value: 5
        periodSeconds: 60
```

**2. AWS Auto Scaling**:
```bash
# Create auto scaling group
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name a2a-mcp-asg \
  --launch-template LaunchTemplateName=a2a-mcp-template \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 3 \
  --target-group-arns arn:aws:elasticloadbalancing:region:account:targetgroup/a2a-mcp-targets

# Create scaling policies
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name a2a-mcp-asg \
  --policy-name scale-up \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration file://scale-up-policy.json
```

## 🛠️ Troubleshooting

### Common Deployment Issues

**1. Port Conflicts**:
```bash
# Check port usage
netstat -tulpn | grep :10100
lsof -i :10100

# Kill processes on port
sudo kill -9 $(lsof -t -i:10100)

# Use different ports
export MCP_SERVER_PORT=10200
export ORCHESTRATOR_PORT=10201
```

**2. Resource Limits**:
```bash
# Check system resources
free -h
df -h
docker stats

# Increase container limits
docker run --memory="2g" --cpus="1.0" a2a-mcp:latest
```

**3. Network Connectivity**:
```bash
# Test agent connectivity
curl -v http://localhost:10100/health
telnet localhost 10100

# Check DNS resolution
nslookup mcp-server
dig mcp-server

# Test MCP server connectivity
python -c "
import asyncio
import aiohttp

async def test():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:10100/health') as resp:
            print(f'Status: {resp.status}')
            print(await resp.text())

asyncio.run(test())
"
```

### Debugging Tools

**1. Container Debugging**:
```bash
# Enter running container
docker exec -it <container-id> /bin/bash

# View container logs
docker logs <container-id> --follow

# Copy files from container
docker cp <container-id>:/app/logs/agent.log ./local-agent.log
```

**2. Kubernetes Debugging**:
```bash
# Get pod logs
kubectl logs -f deployment/mcp-server -n a2a-mcp

# Execute commands in pod
kubectl exec -it pod/mcp-server-xxx -n a2a-mcp -- /bin/bash

# Describe resources
kubectl describe pod mcp-server-xxx -n a2a-mcp
kubectl describe service mcp-server-service -n a2a-mcp
```

## 📚 Best Practices (V2.0)

### V2.0 Deployment Checklist

#### Core Requirements
- [ ] Environment variables configured (including V2.0 settings)
- [ ] SSL certificates installed and configured
- [ ] V2.0 health checks with quality metrics
- [ ] Connection pooling enabled and tuned
- [ ] PHASE 7 streaming configured

#### Observability Stack
- [ ] OpenTelemetry collector deployed
- [ ] Jaeger configured for distributed tracing
- [ ] Prometheus scraping all metrics endpoints
- [ ] Grafana dashboards imported from `src/a2a_mcp/common/dashboards/`
- [ ] Structured logging with trace correlation
- [ ] Alert rules configured

#### Quality Framework
- [ ] Quality domain selected for deployment
- [ ] Quality thresholds configured
- [ ] Validation metrics exposed
- [ ] Quality dashboards set up

#### Performance
- [ ] Connection pool size optimized
- [ ] HTTP/2 enabled
- [ ] Redis cluster configured
- [ ] Parallel workflow thresholds set
- [ ] Auto-scaling policies tuned

#### Security
- [ ] API authentication configured
- [ ] Network policies applied
- [ ] Secrets management integrated
- [ ] Rate limiting enabled
- [ ] Security scanning automated

### Security Checklist

- [ ] API keys stored securely
- [ ] Network access restricted
- [ ] SSL/TLS enabled
- [ ] Authentication implemented
- [ ] Authorization configured
- [ ] Input validation enabled
- [ ] Rate limiting configured
- [ ] Audit logging enabled
- [ ] Regular security updates
- [ ] Penetration testing completed

## 🎯 V2.0 Deployment Recommendations

### By Use Case

#### Development/Testing
- Use Docker Compose with full observability stack
- Enable all V2.0 features for testing
- Use lightweight orchestrator for rapid iteration

#### Production - Small Scale
- Kubernetes with 3-5 replicas per service
- Basic auto-scaling with HPA
- Single-region deployment
- Standard observability

#### Production - Enterprise
- Multi-region Kubernetes/ECS deployment
- Advanced auto-scaling with custom metrics
- Full observability with long-term retention
- Service mesh integration
- Disaster recovery across regions

### Performance Targets

| Metric | Development | Production | Enterprise |
|--------|------------|------------|------------|
| Agent Response Time | < 2s | < 500ms | < 200ms |
| Connection Pool Reuse | > 50% | > 80% | > 95% |
| Quality Score | > 0.7 | > 0.85 | > 0.95 |
| Trace Coverage | 80% | 95% | 99% |
| Uptime | 95% | 99.5% | 99.99% |

---

**Next Steps**: 
- Review [FRAMEWORK_COMPONENTS_AND_ORCHESTRATION_GUIDE.md](FRAMEWORK_COMPONENTS_AND_ORCHESTRATION_GUIDE.md) for detailed V2.0 architecture
- See [INTEGRATION_PATTERNS.md](INTEGRATION_PATTERNS.md) for connecting to existing systems
- Check [MULTI_AGENT_WORKFLOW_GUIDE.md](MULTI_AGENT_WORKFLOW_GUIDE.md) for workflow patterns
- Explore [EXAMPLE_IMPLEMENTATIONS.md](EXAMPLE_IMPLEMENTATIONS.md) for domain-specific configurations