# Integration Patterns Guide - Framework V2.0

This guide covers advanced integration patterns for the A2A-MCP Framework V2.0, including connection pooling, observability integration, and quality-aware patterns.

## 🎯 Overview

The A2A-MCP Framework V2.0 enhances the Model Context Protocol (MCP) integration layer with:
- Connection pooling for 60% performance improvement
- Built-in observability with OpenTelemetry
- Quality validation for all integrations
- PHASE 7 streaming support
- Parallel execution capabilities

## 📚 Essential References
- [Framework Components Guide](./FRAMEWORK_COMPONENTS_AND_ORCHESTRATION_GUIDE.md)
- [Multi-Agent Workflow Guide](./MULTI_AGENT_WORKFLOW_GUIDE.md)

## 🏗️ V2.0 Integration Architecture

```
┌─────────────────────────┐    ┌─────────────────────────┐    ┌─────────────────┐
│   A2A Agents (V2.0)     │    │   MCP Server (V2.0)     │    │ External Systems│
│                         │    │                         │    │                 │
│ ┌─────────────────────┐ │    │ ┌─────────────────────┐ │    │ ┌─────────────┐ │
│ │Enhanced Orchestrator│ │◄──►│ │Tool Router + Pooling│ │◄──►│ │ Databases   │ │
│ │  + Quality + PHASE 7│ │    │ │   + Observability   │ │    │ └─────────────┘ │
│ └─────────────────────┘ │    │ └─────────────────────┘ │    │ ┌─────────────┐ │
│ ┌─────────────────────┐ │    │ ┌─────────────────────┐ │    │ │ APIs        │ │
│ │StandardizedAgentBase│ │◄──►│ │ Connection Pool     │ │◄──►│ └─────────────┘ │
│ │   + Observability   │ │    │ │   + HTTP/2 Support  │ │    │ ┌─────────────┐ │
│ └─────────────────────┘ │    │ └─────────────────────┘ │    │ │Cloud Services│ │
│ ┌─────────────────────┐ │    │ ┌─────────────────────┐ │    │ └─────────────┘ │
│ │ Quality Framework   │ │◄──►│ │ Metrics Collector   │ │◄──►│ ┌─────────────┐ │
│ │   + Validation      │ │    │ │   + Tracing         │ │    │ │ Observability│ │
│ └─────────────────────┘ │    │ └─────────────────────┘ │    │ └─────────────┘ │
└─────────────────────────┘    └─────────────────────────┘    └─────────────────┘
```

## 🔌 Core Integration Patterns

### Pattern 1: V2.0 Database Integration with Connection Pooling

**Use Case**: High-performance database access with observability  
**Complexity**: Medium  
**Performance**: Very High (60% improvement with pooling)  
**Best For**: Transactional data, business records, real-time analytics

**V2.0 Features**:
- Connection pooling with automatic management
- Distributed tracing for query performance
- Quality validation for data integrity
- Metrics collection for monitoring

**Implementation**:

```python
# mcp_servers/database_server_v2.py
# ABOUTME: V2.0 MCP server with connection pooling and observability
# ABOUTME: Supports SQL queries, transactions, tracing, and metrics

import asyncio
import asyncpg
import sqlite3
from mcp.server import Server
from mcp.types import TextContent, Tool
from typing import Dict, Any, List
from a2a_mcp.common.connection_pool import ConnectionPool
from a2a_mcp.common.observability import trace_async, ObservabilityManager
from a2a_mcp.common.metrics_collector import get_metrics_collector
import json

app = Server("database-integration-v2")

# V2.0: Initialize observability
observability = ObservabilityManager()
observability.init_tracing(service_name="database-mcp-server")
metrics = get_metrics_collector()

class V2DatabaseConnector:
    def __init__(self):
        # V2.0: Use connection pools instead of single connections
        self.pools = {}
        self.http_pool = ConnectionPool(
            max_connections=20,
            enable_http2=True,
            enable_metrics=True
        )
        
    async def get_pool(self, database_type: str, connection_string: str):
        """Get or create database connection pool with monitoring"""
        pool_key = f"{database_type}_{hash(connection_string)}"
        
        if pool_key not in self.pools:
            if database_type == "postgresql":
                # Create PostgreSQL connection pool
                self.pools[pool_key] = await asyncpg.create_pool(
                    connection_string,
                    min_size=5,
                    max_size=20,
                    max_queries=50000,
                    max_inactive_connection_lifetime=300
                )
            elif database_type == "sqlite":
                # SQLite doesn't support true pooling, use queue
                self.pools[pool_key] = SqlitePool(connection_string, pool_size=10)
                
            # Record pool creation
            metrics.record_custom_metric("database_pool_created", 1, {
                "database_type": database_type
            })
            
        return self.pools[pool_key]

db_connector = DatabaseConnector()

@app.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="execute_query",
            description="Execute SQL query with parameters",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "SQL query to execute"},
                    "parameters": {"type": "array", "description": "Query parameters"},
                    "database": {"type": "string", "description": "Database identifier"}
                },
                "required": ["query", "database"]
            }
        ),
        Tool(
            name="execute_transaction",
            description="Execute multiple queries in a transaction",
            inputSchema={
                "type": "object",
                "properties": {
                    "queries": {"type": "array", "description": "List of SQL queries"},
                    "database": {"type": "string", "description": "Database identifier"}
                },
                "required": ["queries", "database"]
            }
        ),
        Tool(
            name="get_schema",
            description="Get database schema information",
            inputSchema={
                "type": "object", 
                "properties": {
                    "database": {"type": "string", "description": "Database identifier"},
                    "table_name": {"type": "string", "description": "Specific table (optional)"}
                },
                "required": ["database"]
            }
        )
    ]

@app.call_tool()
@trace_async  # V2.0: Automatic distributed tracing
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Execute tool with observability and quality validation"""
    
    # Track metrics
    with metrics.track_mcp_tool_call(name):
        try:
            if name == "execute_query":
                return await execute_database_query(arguments)
            elif name == "execute_transaction":
                return await execute_database_transaction(arguments)
            elif name == "get_schema":
                return await get_database_schema(arguments)
            elif name == "execute_parallel_queries":  # V2.0: New parallel capability
                return await execute_parallel_queries(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
        except Exception as e:
            metrics.record_tool_error(name, type(e).__name__)
            return [TextContent(type="text", text=f"Error: {str(e)}")]

@trace_async
async def execute_database_query(args: Dict[str, Any]) -> List[TextContent]:
    """Execute a single database query with V2.0 features"""
    query = args["query"]
    parameters = args.get("parameters", [])
    database = args["database"]
    enable_quality_check = args.get("quality_validation", True)
    
    # Get database configuration
    db_config = get_database_config(database)
    pool = await db_connector.get_pool(db_config["type"], db_config["connection_string"])
    
    # Add query to current span
    span = observability.get_current_span()
    if span:
        span.set_attribute("db.statement", query)
        span.set_attribute("db.system", db_config["type"])
    
    start_time = asyncio.get_event_loop().time()
    
    try:
        if db_config["type"] == "postgresql":
            async with pool.acquire() as conn:
                result = await conn.fetch(query, *parameters)
                rows = [dict(row) for row in result]
        elif db_config["type"] == "sqlite":
            rows = await pool.execute(query, parameters)
        
        # Record query metrics
        duration = asyncio.get_event_loop().time() - start_time
        metrics.record_database_query(database, duration, len(rows))
        
        # V2.0: Quality validation
        if enable_quality_check:
            quality_result = validate_query_result(rows, args.get("expected_schema"))
            
        return [TextContent(
            type="text", 
            text=json.dumps({
                "rows": rows,
                "count": len(rows),
                "execution_time_ms": duration * 1000,
                "quality_validation": quality_result if enable_quality_check else None
            }, indent=2)
        )]
        
    except Exception as e:
        if span:
            span.record_exception(e)
        raise

async def execute_database_transaction(args: Dict[str, Any]) -> List[TextContent]:
    """Execute multiple queries in a transaction"""
    queries = args["queries"]
    database = args["database"]
    
    db_config = get_database_config(database)
    conn = await db_connector.get_connection(db_config["type"], db_config["connection_string"])
    
    results = []
    
    if db_config["type"] == "postgresql":
        async with conn.transaction():
            for query_data in queries:
                result = await conn.fetch(query_data["query"], *query_data.get("parameters", []))
                results.append([dict(row) for row in result])
    elif db_config["type"] == "sqlite":
        conn.execute("BEGIN")
        try:
            for query_data in queries:
                cursor = conn.execute(query_data["query"], query_data.get("parameters", []))
                results.append([dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()])
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
    
    return [TextContent(type="text", text=f"Transaction results: {results}")]

def get_database_config(database: str) -> Dict[str, str]:
    """Get database configuration from environment or config file"""
    # This would typically load from environment variables or config file
    configs = {
        "primary": {
            "type": "postgresql",
            "connection_string": "postgresql://user:pass@localhost/dbname"
        },
        "analytics": {
            "type": "sqlite", 
            "connection_string": "./data/analytics.db"
        }
    }
    return configs.get(database, configs["primary"])

if __name__ == "__main__":
    asyncio.run(app.run())
```

**V2.0 Usage with StandardizedAgentBase**:
```python
# V2.0 Agent using enhanced database integration
from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.common.quality_framework import QualityDomain
from a2a_mcp.common.observability import trace_async

class V2BusinessAgent(StandardizedAgentBase):
    def __init__(self):
        super().__init__(
            agent_name="Business Operations Agent",
            description="Handles business data operations",
            quality_config={
                "domain": QualityDomain.ANALYTICAL,
                "thresholds": {"completeness": 0.95, "accuracy": 0.98}
            },
            enable_observability=True
        )
        
    @trace_async
    async def process_request(self, message: dict) -> dict:
        # V2.0: Parallel query execution
        results = await self.use_mcp_tool(
            "execute_parallel_queries",
            {
                "queries": [
                    {
                        "query": "SELECT * FROM customers WHERE id = $1",
                        "parameters": [customer_id],
                        "alias": "customer"
                    },
                    {
                        "query": "SELECT * FROM orders WHERE customer_id = $1 ORDER BY created_at DESC LIMIT 10",
                        "parameters": [customer_id],
                        "alias": "recent_orders"
                    },
                    {
                        "query": "SELECT SUM(total) as lifetime_value FROM orders WHERE customer_id = $1",
                        "parameters": [customer_id],
                        "alias": "metrics"
                    }
                ],
                "database": "primary",
                "quality_validation": True
            }
        )
        
        # V2.0: Transaction with observability
        transaction_result = await self.use_mcp_tool(
            "execute_transaction", 
            {
                "queries": [
                    {
                        "query": "UPDATE orders SET status = $1, processed_at = $2 WHERE id = $3",
                        "parameters": ["processed", datetime.now(), order_id]
                    },
                    {
                        "query": "INSERT INTO order_history (order_id, status, timestamp, agent_id) VALUES ($1, $2, $3, $4)",
                        "parameters": [order_id, "processed", datetime.now(), self.agent_name]
                    }
                ],
                "database": "primary",
                "isolation_level": "SERIALIZABLE"  # V2.0: Transaction isolation
            }
        )
        
        # Return with quality metadata
        return self.format_response({
            "customer_data": results["customer"],
            "recent_orders": results["recent_orders"],
            "metrics": results["metrics"],
            "transaction": transaction_result
        })
```

### Pattern 2: V2.0 REST API Integration with HTTP/2 Support

**Use Case**: High-performance API integration with connection reuse  
**Complexity**: Medium  
**Performance**: High (60% improvement with HTTP/2 pooling)  
**Best For**: Third-party services, microservices, real-time APIs

**V2.0 Features**:
- HTTP/2 connection pooling
- Automatic retry with circuit breaker
- Request/response quality validation
- Distributed tracing across API calls

**Implementation**:

```python
# mcp_servers/api_server.py  
# ABOUTME: MCP server for REST API integrations
# ABOUTME: Handles HTTP requests, authentication, and response processing

import asyncio
import aiohttp
import json
from mcp.server import Server
from mcp.types import TextContent, Tool
from typing import Dict, Any, List

app = Server("api-integration")

class V2APIConnector:
    def __init__(self):
        # V2.0: Use connection pool for all HTTP connections
        self.connection_pool = ConnectionPool(
            max_connections=100,
            max_keepalive_connections=50,
            keepalive_expiry=300.0,
            enable_http2=True,  # V2.0: HTTP/2 support
            enable_metrics=True
        )
        self.auth_tokens = {}
        self.circuit_breakers = {}  # V2.0: Circuit breaker per API
        
    async def get_session(self, api_name: str) -> aiohttp.ClientSession:
        """Get HTTP session with V2.0 connection pooling"""
        # Use shared connection pool for all APIs
        return self.connection_pool.get_session(
            headers=self.get_default_headers(api_name)
        )
    
    def get_circuit_breaker(self, api_name: str):
        """Get or create circuit breaker for API"""
        if api_name not in self.circuit_breakers:
            self.circuit_breakers[api_name] = CircuitBreaker(
                failure_threshold=5,
                recovery_timeout=60,
                expected_exception=aiohttp.ClientError
            )
        return self.circuit_breakers[api_name]
        
    def get_default_headers(self, api_name: str) -> Dict[str, str]:
        """Get default headers for API"""
        headers = {"Content-Type": "application/json"}
        
        # Add authentication headers
        auth_config = get_api_auth_config(api_name)
        if auth_config["type"] == "bearer":
            headers["Authorization"] = f"Bearer {auth_config['token']}"
        elif auth_config["type"] == "api_key":
            headers[auth_config["header"]] = auth_config["key"]
            
        return headers

api_connector = APIConnector()

@app.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="http_request",
            description="Make HTTP request to external API",
            inputSchema={
                "type": "object",
                "properties": {
                    "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"]},
                    "url": {"type": "string", "description": "API endpoint URL"},
                    "headers": {"type": "object", "description": "Additional headers"},
                    "body": {"type": "object", "description": "Request body"},
                    "api_name": {"type": "string", "description": "API configuration name"},
                    "timeout": {"type": "number", "description": "Request timeout in seconds"}
                },
                "required": ["method", "url", "api_name"]
            }
        ),
        Tool(
            name="webhook_send",
            description="Send webhook notification",
            inputSchema={
                "type": "object",
                "properties": {
                    "webhook_url": {"type": "string", "description": "Webhook endpoint"},
                    "payload": {"type": "object", "description": "Webhook payload"},
                    "signature_secret": {"type": "string", "description": "Webhook signature secret"}
                },
                "required": ["webhook_url", "payload"]
            }
        ),
        Tool(
            name="api_batch_request",
            description="Execute multiple API requests concurrently",
            inputSchema={
                "type": "object",
                "properties": {
                    "requests": {"type": "array", "description": "List of HTTP requests"},
                    "api_name": {"type": "string", "description": "API configuration name"}
                },
                "required": ["requests", "api_name"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    try:
        if name == "http_request":
            return await make_http_request(arguments)
        elif name == "webhook_send":
            return await send_webhook(arguments)
        elif name == "api_batch_request":
            return await execute_batch_requests(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def make_http_request(args: Dict[str, Any]) -> List[TextContent]:
    """Make HTTP request to external API"""
    method = args["method"]
    url = args["url"]
    api_name = args["api_name"]
    headers = args.get("headers", {})
    body = args.get("body")
    timeout = args.get("timeout", 30)
    
    session = await api_connector.get_session(api_name)
    
    # Merge with default headers
    session_headers = session.headers.copy()
    session_headers.update(headers)
    
    async with session.request(
        method=method,
        url=url,
        headers=session_headers,
        json=body if body else None,
        timeout=aiohttp.ClientTimeout(total=timeout)
    ) as response:
        response_text = await response.text()
        
        try:
            response_data = json.loads(response_text) if response_text else {}
        except json.JSONDecodeError:
            response_data = {"raw_response": response_text}
        
        result = {
            "status_code": response.status,
            "headers": dict(response.headers),
            "data": response_data,
            "success": 200 <= response.status < 300
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

async def send_webhook(args: Dict[str, Any]) -> List[TextContent]:
    """Send webhook notification with signature"""
    webhook_url = args["webhook_url"]
    payload = args["payload"]
    signature_secret = args.get("signature_secret")
    
    headers = {"Content-Type": "application/json"}
    
    # Add webhook signature if secret provided
    if signature_secret:
        import hmac
        import hashlib
        payload_bytes = json.dumps(payload).encode()
        signature = hmac.new(
            signature_secret.encode(),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        headers["X-Webhook-Signature"] = f"sha256={signature}"
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            webhook_url,
            json=payload,
            headers=headers
        ) as response:
            result = {
                "status_code": response.status,
                "success": 200 <= response.status < 300,
                "response": await response.text()
            }
            
    return [TextContent(type="text", text=json.dumps(result, indent=2))]

async def execute_batch_requests(args: Dict[str, Any]) -> List[TextContent]:
    """Execute multiple API requests concurrently"""
    requests = args["requests"]
    api_name = args["api_name"]
    
    session = await api_connector.get_session(api_name)
    
    async def single_request(request_data):
        try:
            async with session.request(
                method=request_data["method"],
                url=request_data["url"],
                json=request_data.get("body"),
                headers=request_data.get("headers", {})
            ) as response:
                return {
                    "status_code": response.status,
                    "data": await response.json() if response.content_type == "application/json" else await response.text(),
                    "success": 200 <= response.status < 300,
                    "request_id": request_data.get("id", "unknown")
                }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
                "request_id": request_data.get("id", "unknown")
            }
    
    # Execute all requests concurrently
    results = await asyncio.gather(*[single_request(req) for req in requests])
    
    return [TextContent(type="text", text=json.dumps(results, indent=2))]

def get_api_auth_config(api_name: str) -> Dict[str, str]:
    """Get API authentication configuration"""
    # This would typically load from environment variables or secure storage
    configs = {
        "payment_gateway": {
            "type": "bearer",
            "token": "your_bearer_token"
        },
        "crm_system": {
            "type": "api_key",
            "header": "X-API-Key",
            "key": "your_api_key"
        },
        "analytics_service": {
            "type": "bearer",
            "token": "your_analytics_token"
        }
    }
    return configs.get(api_name, {"type": "none"})

if __name__ == "__main__":
    asyncio.run(app.run())
```

### Pattern 3: Cloud Services Integration

**Use Case**: Connect to AWS, GCP, Azure cloud services  
**Complexity**: Medium-High  
**Performance**: Medium  
**Best For**: Storage, compute, managed services, AI/ML APIs

**AWS Integration Example**:

```python
# mcp_servers/aws_server.py
# ABOUTME: MCP server for AWS service integrations
# ABOUTME: Supports S3, DynamoDB, Lambda, SQS, and other AWS services

import asyncio
import boto3
import json
from mcp.server import Server
from mcp.types import TextContent, Tool
from typing import Dict, Any, List
from botocore.exceptions import ClientError

app = Server("aws-integration")

class AWSConnector:
    def __init__(self):
        self.clients = {}
        
    def get_client(self, service_name: str, region: str = "us-east-1"):
        """Get or create AWS service client"""
        client_key = f"{service_name}_{region}"
        if client_key not in self.clients:
            self.clients[client_key] = boto3.client(service_name, region_name=region)
        return self.clients[client_key]

aws_connector = AWSConnector()

@app.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="s3_operations",
            description="Perform S3 bucket operations",
            inputSchema={
                "type": "object",
                "properties": {
                    "operation": {"type": "string", "enum": ["list", "get", "put", "delete"]},
                    "bucket": {"type": "string", "description": "S3 bucket name"},
                    "key": {"type": "string", "description": "Object key"},
                    "content": {"type": "string", "description": "Content for put operations"},
                    "region": {"type": "string", "description": "AWS region"}
                },
                "required": ["operation", "bucket"]
            }
        ),
        Tool(
            name="dynamodb_operations", 
            description="Perform DynamoDB operations",
            inputSchema={
                "type": "object",
                "properties": {
                    "operation": {"type": "string", "enum": ["get_item", "put_item", "query", "scan"]},
                    "table_name": {"type": "string", "description": "DynamoDB table name"},
                    "key": {"type": "object", "description": "Item key"},
                    "item": {"type": "object", "description": "Item data"},
                    "condition": {"type": "object", "description": "Query/scan conditions"},
                    "region": {"type": "string", "description": "AWS region"}
                },
                "required": ["operation", "table_name"]
            }
        ),
        Tool(
            name="lambda_invoke",
            description="Invoke AWS Lambda function",
            inputSchema={
                "type": "object",
                "properties": {
                    "function_name": {"type": "string", "description": "Lambda function name"},
                    "payload": {"type": "object", "description": "Function payload"},
                    "invocation_type": {"type": "string", "enum": ["RequestResponse", "Event"]},
                    "region": {"type": "string", "description": "AWS region"}
                },
                "required": ["function_name"]
            }
        ),
        Tool(
            name="sqs_operations",
            description="Perform SQS queue operations", 
            inputSchema={
                "type": "object",
                "properties": {
                    "operation": {"type": "string", "enum": ["send_message", "receive_messages", "delete_message"]},
                    "queue_url": {"type": "string", "description": "SQS queue URL"},
                    "message_body": {"type": "string", "description": "Message content"},
                    "receipt_handle": {"type": "string", "description": "Message receipt handle"},
                    "region": {"type": "string", "description": "AWS region"}
                },
                "required": ["operation", "queue_url"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    try:
        if name == "s3_operations":
            return await handle_s3_operations(arguments)
        elif name == "dynamodb_operations":
            return await handle_dynamodb_operations(arguments)
        elif name == "lambda_invoke":
            return await invoke_lambda_function(arguments)
        elif name == "sqs_operations":
            return await handle_sqs_operations(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def handle_s3_operations(args: Dict[str, Any]) -> List[TextContent]:
    """Handle S3 bucket operations"""
    operation = args["operation"]
    bucket = args["bucket"]
    key = args.get("key")
    content = args.get("content")
    region = args.get("region", "us-east-1")
    
    s3_client = aws_connector.get_client("s3", region)
    
    try:
        if operation == "list":
            response = s3_client.list_objects_v2(Bucket=bucket)
            objects = [obj["Key"] for obj in response.get("Contents", [])]
            result = {"objects": objects}
            
        elif operation == "get":
            response = s3_client.get_object(Bucket=bucket, Key=key)
            content = response["Body"].read().decode("utf-8")
            result = {"content": content, "metadata": response.get("Metadata", {})}
            
        elif operation == "put":
            s3_client.put_object(Bucket=bucket, Key=key, Body=content)
            result = {"success": True, "message": f"Object {key} uploaded to {bucket}"}
            
        elif operation == "delete":
            s3_client.delete_object(Bucket=bucket, Key=key)
            result = {"success": True, "message": f"Object {key} deleted from {bucket}"}
            
    except ClientError as e:
        result = {"error": str(e), "error_code": e.response["Error"]["Code"]}
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]

async def handle_dynamodb_operations(args: Dict[str, Any]) -> List[TextContent]:
    """Handle DynamoDB operations"""
    operation = args["operation"]
    table_name = args["table_name"]
    region = args.get("region", "us-east-1")
    
    dynamodb = aws_connector.get_client("dynamodb", region)
    
    try:
        if operation == "get_item":
            response = dynamodb.get_item(TableName=table_name, Key=args["key"])
            result = {"item": response.get("Item", {})}
            
        elif operation == "put_item":
            dynamodb.put_item(TableName=table_name, Item=args["item"])
            result = {"success": True, "message": "Item added to table"}
            
        elif operation == "query":
            response = dynamodb.query(TableName=table_name, **args["condition"])
            result = {"items": response.get("Items", []), "count": response.get("Count", 0)}
            
        elif operation == "scan":
            response = dynamodb.scan(TableName=table_name, **args.get("condition", {}))
            result = {"items": response.get("Items", []), "count": response.get("Count", 0)}
            
    except ClientError as e:
        result = {"error": str(e), "error_code": e.response["Error"]["Code"]}
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]
```

### Pattern 4: Message Queue Integration

**Use Case**: Asynchronous processing, event-driven architecture  
**Complexity**: Medium  
**Performance**: High  
**Best For**: Background tasks, event processing, decoupling

**Implementation**:

```python
# mcp_servers/queue_server.py
# ABOUTME: MCP server for message queue integrations  
# ABOUTME: Supports Redis, RabbitMQ, Apache Kafka, and cloud queues

import asyncio
import redis.asyncio as redis
import json
from mcp.server import Server
from mcp.types import TextContent, Tool
from typing import Dict, Any, List

app = Server("queue-integration")

class QueueConnector:
    def __init__(self):
        self.connections = {}
        
    async def get_redis_connection(self, connection_name: str):
        """Get or create Redis connection"""
        if connection_name not in self.connections:
            config = get_queue_config(connection_name)
            self.connections[connection_name] = redis.Redis(
                host=config["host"],
                port=config["port"],
                db=config["db"],
                password=config.get("password")
            )
        return self.connections[connection_name]

queue_connector = QueueConnector()

@app.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="queue_send",
            description="Send message to queue",
            inputSchema={
                "type": "object",
                "properties": {
                    "queue_name": {"type": "string", "description": "Queue name"},
                    "message": {"type": "object", "description": "Message payload"},
                    "priority": {"type": "number", "description": "Message priority"},
                    "delay": {"type": "number", "description": "Delay in seconds"},
                    "connection": {"type": "string", "description": "Queue connection name"}
                },
                "required": ["queue_name", "message", "connection"]
            }
        ),
        Tool(
            name="queue_receive",
            description="Receive messages from queue",
            inputSchema={
                "type": "object", 
                "properties": {
                    "queue_name": {"type": "string", "description": "Queue name"},
                    "count": {"type": "number", "description": "Number of messages to receive"},
                    "timeout": {"type": "number", "description": "Receive timeout"},
                    "connection": {"type": "string", "description": "Queue connection name"}
                },
                "required": ["queue_name", "connection"]
            }
        ),
        Tool(
            name="publish_event",
            description="Publish event to topic/exchange",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Topic or exchange name"},
                    "event": {"type": "object", "description": "Event payload"},
                    "routing_key": {"type": "string", "description": "Message routing key"},
                    "connection": {"type": "string", "description": "Queue connection name"}
                },
                "required": ["topic", "event", "connection"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    try:
        if name == "queue_send":
            return await send_queue_message(arguments)
        elif name == "queue_receive":
            return await receive_queue_messages(arguments)
        elif name == "publish_event":
            return await publish_event(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def send_queue_message(args: Dict[str, Any]) -> List[TextContent]:
    """Send message to queue"""
    queue_name = args["queue_name"]
    message = args["message"]
    connection_name = args["connection"]
    priority = args.get("priority", 0)
    delay = args.get("delay", 0)
    
    redis_conn = await queue_connector.get_redis_connection(connection_name)
    
    # Prepare message with metadata
    message_data = {
        "payload": message,
        "priority": priority,
        "timestamp": asyncio.get_event_loop().time(),
        "id": f"{queue_name}_{asyncio.get_event_loop().time()}"
    }
    
    if delay > 0:
        # Use sorted set for delayed messages
        score = asyncio.get_event_loop().time() + delay
        await redis_conn.zadd(f"{queue_name}:delayed", {json.dumps(message_data): score})
    else:
        # Send to immediate queue
        await redis_conn.lpush(queue_name, json.dumps(message_data))
    
    result = {
        "success": True,
        "message_id": message_data["id"],
        "queue": queue_name,
        "delayed": delay > 0
    }
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]

async def receive_queue_messages(args: Dict[str, Any]) -> List[TextContent]:
    """Receive messages from queue"""
    queue_name = args["queue_name"]
    connection_name = args["connection"]
    count = args.get("count", 1)
    timeout = args.get("timeout", 5)
    
    redis_conn = await queue_connector.get_redis_connection(connection_name)
    
    messages = []
    
    for _ in range(count):
        # Try to get message with timeout
        message_data = await redis_conn.brpop(queue_name, timeout=timeout)
        if message_data:
            queue, message_json = message_data
            message = json.loads(message_json)
            messages.append(message)
        else:
            break  # No more messages available
    
    result = {
        "messages": messages,
        "count": len(messages),
        "queue": queue_name
    }
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]

def get_queue_config(connection_name: str) -> Dict[str, Any]:
    """Get queue connection configuration"""
    configs = {
        "default": {
            "host": "localhost",
            "port": 6379,
            "db": 0
        },
        "priority": {
            "host": "localhost", 
            "port": 6379,
            "db": 1
        }
    }
    return configs.get(connection_name, configs["default"])

if __name__ == "__main__":
    asyncio.run(app.run())
```

## 🔄 Advanced Integration Patterns

### Pattern 5: Event-Driven Integration

**Implementation**:

```python
# Event-driven agent coordination
class EventDrivenOrchestrator(BaseAgent):
    def __init__(self):
        super().__init__()
        self.event_handlers = {}
        
    async def register_event_handler(self, event_type: str, handler_func):
        """Register handler for specific event type"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler_func)
        
    async def emit_event(self, event_type: str, event_data: dict):
        """Emit event to all registered handlers"""
        await self.mcp_client.call_tool(
            "publish_event",
            {
                "topic": "agent_events",
                "event": {
                    "type": event_type,
                    "data": event_data,
                    "timestamp": datetime.utcnow().isoformat(),
                    "source_agent": self.agent_name
                },
                "connection": "default"
            }
        )
        
    async def handle_event(self, event: dict):
        """Handle incoming event"""
        event_type = event["type"]
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                await handler(event["data"])

# Example usage
orchestrator = EventDrivenOrchestrator()

@orchestrator.register_event_handler("order_created")
async def handle_order_created(order_data):
    # Trigger inventory check
    await orchestrator.call_agent("inventory_agent", {"action": "reserve", "order": order_data})
    
    # Trigger payment processing
    await orchestrator.call_agent("payment_agent", {"action": "process", "order": order_data})
```

### Pattern 6: V2.0 Quality-Aware Integration

**Use Case**: Ensure integration quality with validation  
**Complexity**: Medium  
**Performance**: High  
**Best For**: Critical business integrations

**Implementation**:

```python
# V2.0 Quality-aware integration pattern
from a2a_mcp.common.quality_framework import QualityThresholdFramework, QualityDomain
from a2a_mcp.common.observability import trace_async
from a2a_mcp.common.metrics_collector import get_metrics_collector

class QualityAwareIntegration:
    def __init__(self, quality_domain: QualityDomain = QualityDomain.ANALYTICAL):
        self.quality_framework = QualityThresholdFramework()
        self.quality_framework.configure_domain(quality_domain)
        self.quality_framework.set_thresholds({
            "completeness": 0.95,
            "accuracy": 0.98,
            "consistency": 0.90
        })
        self.metrics = get_metrics_collector()
        
    @trace_async
    async def execute_with_quality_validation(
        self, 
        integration_name: str,
        operation: callable,
        expected_schema: dict = None
    ):
        """Execute integration with quality validation"""
        
        # Execute the integration
        start_time = asyncio.get_event_loop().time()
        try:
            result = await operation()
            duration = asyncio.get_event_loop().time() - start_time
            
            # Validate result quality
            quality_result = self.quality_framework.validate_output({
                "content": result,
                "metadata": {
                    "integration": integration_name,
                    "duration_ms": duration * 1000
                }
            })
            
            # Record metrics
            self.metrics.record_quality_validation(
                domain=self.quality_framework.current_domain.value,
                status="passed" if quality_result["passed"] else "failed",
                scores=quality_result["scores"]
            )
            
            if not quality_result["passed"]:
                raise QualityValidationError(
                    f"Quality validation failed: {quality_result['failed_metrics']}"
                )
            
            return {
                "result": result,
                "quality": quality_result,
                "performance": {
                    "duration_ms": duration * 1000,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            self.metrics.record_integration_error(integration_name, str(e))
            raise

# Usage in V2.0 agent
class QualityAwareAgent(StandardizedAgentBase):
    def __init__(self):
        super().__init__(
            agent_name="Quality-Aware Integration Agent",
            quality_config={"domain": QualityDomain.ANALYTICAL}
        )
        self.quality_integration = QualityAwareIntegration()
        
    async def fetch_critical_data(self, params: dict):
        """Fetch data with quality guarantees"""
        
        async def fetch_operation():
            return await self.use_mcp_tool(
                "http_request",
                {
                    "method": "GET",
                    "url": f"https://api.critical-service.com/data/{params['id']}",
                    "api_name": "critical_service"
                }
            )
        
        # Execute with quality validation
        result = await self.quality_integration.execute_with_quality_validation(
            "critical_data_fetch",
            fetch_operation,
            expected_schema={
                "type": "object",
                "required": ["id", "status", "data"],
                "properties": {
                    "id": {"type": "string"},
                    "status": {"type": "string"},
                    "data": {"type": "object"}
                }
            }
        )
        
        return self.format_response(result)
```

### Pattern 7: V2.0 Circuit Breaker with Observability

**Implementation**:

```python
# V2.0 Circuit breaker with metrics and tracing
from a2a_mcp.common.observability import trace_async
from a2a_mcp.common.metrics_collector import get_metrics_collector
import time

class V2CircuitBreaker:
    def __init__(self, 
                 failure_threshold: int = 5, 
                 recovery_timeout: int = 60,
                 name: str = "default"):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.metrics = get_metrics_collector()
        
    async def call_with_circuit_breaker(self, tool_name: str, arguments: dict):
        """Call MCP tool with circuit breaker protection"""
        
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN - service unavailable")
        
        try:
            result = await self.mcp_client.call_tool(tool_name, arguments)
            
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
                
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                
            raise e

# Usage in agent
class ResilientAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.circuit_breaker = CircuitBreakerMCPTool()
        
    async def call_external_service(self, service_data):
        try:
            return await self.circuit_breaker.call_with_circuit_breaker(
                "http_request",
                {
                    "method": "POST",
                    "url": "https://external-service.com/api",
                    "body": service_data,
                    "api_name": "external_service"
                }
            )
        except Exception as e:
            # Fallback mechanism
            return await self.handle_service_failure(service_data)
            
    async def handle_service_failure(self, service_data):
        """Fallback when external service is unavailable"""
        # Queue for later processing
        await self.mcp_client.call_tool(
            "queue_send",
            {
                "queue_name": "failed_requests",
                "message": service_data,
                "connection": "default"
            }
        )
        return {"status": "queued_for_retry"}
```

## 📊 V2.0 Performance & Monitoring

### Enhanced Integration Metrics

```python
# V2.0 Integration monitoring with observability
from a2a_mcp.common.metrics_collector import MetricsCollector
from a2a_mcp.common.observability import ObservabilityManager
from a2a_mcp.common.structured_logger import StructuredLogger

class V2IntegrationMonitor:
    def __init__(self):
        self.metrics = MetricsCollector(
            namespace="a2a_mcp",
            subsystem="integrations"
        )
        self.observability = ObservabilityManager()
        self.logger = StructuredLogger("integration_monitor")
        
    async def record_integration_call(self, integration_name: str, duration: float, success: bool):
        """Record integration call metrics"""
        if integration_name not in self.metrics:
            self.metrics[integration_name] = {
                "call_count": 0,
                "success_count": 0,
                "total_duration": 0,
                "avg_duration": 0,
                "success_rate": 0
            }
        
        metric = self.metrics[integration_name]
        metric["call_count"] += 1
        metric["total_duration"] += duration
        metric["avg_duration"] = metric["total_duration"] / metric["call_count"]
        
        if success:
            metric["success_count"] += 1
        
        metric["success_rate"] = metric["success_count"] / metric["call_count"]
        
    def get_integration_health(self) -> dict:
        """Get health status of all integrations"""
        health_report = {}
        
        for integration, metrics in self.metrics.items():
            health_status = "healthy"
            if metrics["success_rate"] < 0.95:
                health_status = "degraded"
            elif metrics["success_rate"] < 0.8:
                health_status = "unhealthy"
                
            health_report[integration] = {
                "status": health_status,
                "success_rate": metrics["success_rate"],
                "avg_response_time": metrics["avg_duration"],
                "total_calls": metrics["call_count"]
            }
            
        return health_report
```

## 🛠️ V2.0 Integration Best Practices

### Connection Management (V2.0)
- **Always use ConnectionPool** for 60% performance improvement
- **Enable HTTP/2** for multiplexing and reduced latency
- **Configure pool sizes** based on load patterns
- **Monitor pool metrics** for optimization
```python
pool = ConnectionPool(
    max_connections=50,
    max_keepalive_connections=25,
    keepalive_expiry=300.0,
    enable_http2=True,
    enable_metrics=True
)
```

### Error Handling (V2.0)
- **Use V2CircuitBreaker** with observability
- **Implement quality validation** for critical integrations
- **Enable distributed tracing** for debugging
- **Use structured logging** with trace correlation

### Security (V2.0)
- **Rotate credentials** with zero-downtime updates
- **Use mutual TLS** for service-to-service auth
- **Implement rate limiting** with adaptive thresholds
- **Enable audit logging** for compliance

### Performance (V2.0)
- **Use parallel execution** for independent operations
- **Enable PHASE 7 streaming** for real-time updates
- **Implement quality-aware caching**
- **Use connection pooling** for all external calls

### Observability (V2.0)
- **Enable tracing** for all integration points
- **Export metrics** to Prometheus
- **Use structured logging** with trace IDs
- **Create Grafana dashboards** for monitoring

## 📚 Integration Examples by Domain

### E-commerce
- Payment gateways (Stripe, PayPal)
- Inventory management systems
- Shipping providers (FedEx, UPS)
- CRM systems (Salesforce, HubSpot)

### Healthcare
- Electronic Health Records (EHR)
- Laboratory information systems
- Pharmacy management systems
- Insurance verification services

### Financial Services
- Core banking systems
- Risk management platforms
- Regulatory reporting systems
- Trading platforms

### Manufacturing
- Enterprise Resource Planning (ERP)
- Manufacturing Execution Systems (MES)
- Supply chain management
- Quality management systems

## 🚀 V2.0 Integration Patterns Summary

### Key V2.0 Enhancements
1. **Connection Pooling**: 60% performance improvement
2. **HTTP/2 Support**: Reduced latency, multiplexing
3. **Quality Validation**: Ensure data integrity
4. **Observability**: Full tracing and metrics
5. **Parallel Execution**: Process multiple integrations concurrently
6. **PHASE 7 Streaming**: Real-time integration updates

### Migration from V1.0
1. Replace single connections with connection pools
2. Add quality validation to critical integrations
3. Enable observability for all MCP servers
4. Update agents to use StandardizedAgentBase
5. Implement structured logging with trace correlation

---

**Next Steps**: 
- Review [FRAMEWORK_COMPONENTS_AND_ORCHESTRATION_GUIDE.md](./FRAMEWORK_COMPONENTS_AND_ORCHESTRATION_GUIDE.md) for V2.0 architecture
- See [EXAMPLE_IMPLEMENTATIONS.md](./EXAMPLE_IMPLEMENTATIONS.md) for complete domain examples
- Follow [GENERIC_DEPLOYMENT_GUIDE.md](./GENERIC_DEPLOYMENT_GUIDE.md) for V2.0 deployment