# Generic Deployment Guide

This guide covers deployment strategies for the A2A-MCP framework across different platforms and environments.

## 🎯 Overview

The A2A-MCP framework can be deployed in multiple configurations, from local development to enterprise cloud deployments. This guide provides platform-agnostic deployment strategies that work for any business domain.

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

**2. Local Configuration**:
```bash
# .env file
A2A_LOG_LEVEL=INFO
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=10100

# Add your LLM provider API key
OPENAI_API_KEY=your_openai_key
# OR
GOOGLE_API_KEY=your_google_key
# OR
ANTHROPIC_API_KEY=your_anthropic_key

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

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  mcp-server:
    build: .
    ports:
      - "10100:10100"
    environment:
      - MCP_SERVER_HOST=0.0.0.0
      - MCP_SERVER_PORT=10100
      - A2A_LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:10100/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  orchestrator:
    build: .
    ports:
      - "10001:10001"
    environment:
      - AGENT_CARD=agent_cards/tier1/master_orchestrator.json
      - AGENT_PORT=10001
      - MCP_SERVER_URL=http://mcp-server:10100
    depends_on:
      - mcp-server
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

### AWS Deployment

**Architecture**: ECS Fargate + Application Load Balancer + RDS

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

# ECS Task Definition for MCP Server
resource "aws_ecs_task_definition" "mcp_server" {
  family                   = "mcp-server"
  network_mode            = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                     = 512
  memory                  = 1024
  execution_role_arn      = aws_iam_role.ecs_execution_role.arn
  task_role_arn          = aws_iam_role.ecs_task_role.arn
  
  container_definitions = jsonencode([
    {
      name  = "mcp-server"
      image = "${aws_ecr_repository.app.repository_url}:latest"
      
      portMappings = [
        {
          containerPort = 10100
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
  
  # Deploy MCP Server to Cloud Run
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
    - 'run'
    - 'deploy'
    - 'mcp-server'
    - '--image'
    - 'gcr.io/$PROJECT_ID/a2a-mcp:$COMMIT_SHA'
    - '--region'
    - 'us-central1'
    - '--platform'
    - 'managed'
    - '--allow-unauthenticated'
    - '--port'
    - '10100'
    - '--memory'
    - '1Gi'
    - '--cpu'
    - '1'
    - '--min-instances'
    - '1'
    - '--max-instances'
    - '10'
  
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

### Kubernetes Deployment

**Architecture**: Multi-pod deployment with service mesh

**1. Kubernetes Manifests**:

Create `k8s/namespace.yaml`:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: a2a-mcp
  labels:
    name: a2a-mcp
```

Create `k8s/configmap.yaml`:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: a2a-mcp-config
  namespace: a2a-mcp
data:
  MCP_SERVER_HOST: "0.0.0.0"
  MCP_SERVER_PORT: "10100"
  A2A_LOG_LEVEL: "INFO"
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
        image: a2a-mcp:latest
        ports:
        - containerPort: 10100
        envFrom:
        - configMapRef:
            name: a2a-mcp-config
        - secretRef:
            name: a2a-mcp-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
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

## 📊 Monitoring & Observability

### Health Checks

**1. Application Health Endpoints**:
```python
# Add to your agent implementations
@app.route('/health')
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.route('/ready') 
def readiness_check():
    # Check dependencies
    mcp_server_healthy = check_mcp_server_connection()
    database_healthy = check_database_connection()
    
    if mcp_server_healthy and database_healthy:
        return {"status": "ready"}, 200
    else:
        return {"status": "not ready"}, 503
```

**2. Monitoring Stack**:

Create `monitoring/docker-compose.yml`:
```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-storage:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources

  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"
      - "14268:14268"
    environment:
      - COLLECTOR_OTLP_ENABLED=true

volumes:
  grafana-storage:
```

### Logging Configuration

**1. Structured Logging**:
```python
# Configure logging in your applications
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if hasattr(record, 'agent_id'):
            log_entry['agent_id'] = record.agent_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
            
        return json.dumps(log_entry)

# Configure logger
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
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

## 🚀 Performance Optimization

### Caching Strategy

**1. Redis Configuration**:
```yaml
# docker-compose.yml addition
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes
    
  redis-sentinel:
    image: redis:7-alpine
    ports:
      - "26379:26379"
    command: redis-sentinel /etc/redis/sentinel.conf
    volumes:
      - ./redis/sentinel.conf:/etc/redis/sentinel.conf

volumes:
  redis-data:
```

**2. Application Caching**:
```python
# Add caching to your agents
import redis
from functools import wraps

redis_client = redis.Redis(host='redis', port=6379, db=0)

def cache_result(expiration=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator
```

### Auto-Scaling Configuration

**1. Kubernetes HPA**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: mcp-server-hpa
  namespace: a2a-mcp
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: mcp-server
  minReplicas: 3
  maxReplicas: 20
  metrics:
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

## 📚 Best Practices

### Deployment Checklist

- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Health checks implemented
- [ ] Monitoring configured
- [ ] Backups scheduled
- [ ] Auto-scaling enabled
- [ ] Security groups configured
- [ ] Logs aggregated
- [ ] Performance optimized
- [ ] Disaster recovery planned

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

---

**Next Steps**: After deployment, see [INTEGRATION_PATTERNS.md](INTEGRATION_PATTERNS.md) for connecting to your existing systems and [EXAMPLE_IMPLEMENTATIONS.md](EXAMPLE_IMPLEMENTATIONS.md) for domain-specific configurations.