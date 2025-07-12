# Integration Patterns Guide

This guide covers common patterns for integrating the A2A-MCP framework with existing systems and external services.

## 🎯 Overview

The A2A-MCP framework uses the Model Context Protocol (MCP) as its primary integration layer. This document provides proven patterns for connecting to databases, APIs, cloud services, and enterprise systems across any business domain.

## 🏗️ Integration Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   A2A Agents    │    │   MCP Server    │    │ External Systems│
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │Orchestrator │ │◄──►│ │ Tool Router │ │◄──►│ │ Databases   │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Specialists │ │◄──►│ │ Connectors  │ │◄──►│ │ APIs        │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │  Services   │ │◄──►│ │ Adapters    │ │◄──►│ │Cloud Services│ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔌 Core Integration Patterns

### Pattern 1: Database Integration

**Use Case**: Connect agents to SQL/NoSQL databases  
**Complexity**: Low  
**Performance**: High  
**Best For**: Transactional data, business records, user data

**Implementation**:

```python
# mcp_servers/database_server.py
# ABOUTME: MCP server providing database access tools
# ABOUTME: Supports SQL queries, transactions, and connection pooling

import asyncio
import asyncpg
import sqlite3
from mcp.server import Server
from mcp.types import TextContent, Tool
from typing import Dict, Any, List

app = Server("database-integration")

class DatabaseConnector:
    def __init__(self):
        self.connections = {}
        
    async def get_connection(self, database_type: str, connection_string: str):
        """Get or create database connection"""
        if database_type not in self.connections:
            if database_type == "postgresql":
                self.connections[database_type] = await asyncpg.connect(connection_string)
            elif database_type == "sqlite":
                self.connections[database_type] = sqlite3.connect(connection_string)
        return self.connections[database_type]

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
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    try:
        if name == "execute_query":
            return await execute_database_query(arguments)
        elif name == "execute_transaction":
            return await execute_database_transaction(arguments)
        elif name == "get_schema":
            return await get_database_schema(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def execute_database_query(args: Dict[str, Any]) -> List[TextContent]:
    """Execute a single database query"""
    query = args["query"]
    parameters = args.get("parameters", [])
    database = args["database"]
    
    # Get database connection based on configuration
    db_config = get_database_config(database)
    conn = await db_connector.get_connection(db_config["type"], db_config["connection_string"])
    
    if db_config["type"] == "postgresql":
        result = await conn.fetch(query, *parameters)
        rows = [dict(row) for row in result]
    elif db_config["type"] == "sqlite":
        cursor = conn.execute(query, parameters)
        rows = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    
    return [TextContent(type="text", text=f"Query results: {rows}")]

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

**Usage in Agent**:
```python
# Agent using database integration
class BusinessAgent(BaseAgent):
    async def process_request(self, message: dict) -> dict:
        # Query customer data
        customer_result = await self.mcp_client.call_tool(
            "execute_query",
            {
                "query": "SELECT * FROM customers WHERE id = $1",
                "parameters": [customer_id],
                "database": "primary"
            }
        )
        
        # Update order status in transaction
        transaction_result = await self.mcp_client.call_tool(
            "execute_transaction", 
            {
                "queries": [
                    {
                        "query": "UPDATE orders SET status = $1 WHERE id = $2",
                        "parameters": ["processed", order_id]
                    },
                    {
                        "query": "INSERT INTO order_history (order_id, status, timestamp) VALUES ($1, $2, $3)",
                        "parameters": [order_id, "processed", datetime.now()]
                    }
                ],
                "database": "primary"
            }
        )
        
        return {"status": "success", "customer": customer_result, "transaction": transaction_result}
```

### Pattern 2: REST API Integration

**Use Case**: Connect to external REST APIs and web services  
**Complexity**: Medium  
**Performance**: Medium  
**Best For**: Third-party services, microservices, webhooks

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

class APIConnector:
    def __init__(self):
        self.sessions = {}
        self.auth_tokens = {}
        
    async def get_session(self, api_name: str) -> aiohttp.ClientSession:
        """Get or create HTTP session for API"""
        if api_name not in self.sessions:
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
            timeout = aiohttp.ClientTimeout(total=30)
            self.sessions[api_name] = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self.get_default_headers(api_name)
            )
        return self.sessions[api_name]
        
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

### Pattern 6: Circuit Breaker Integration

**Implementation**:

```python
# Circuit breaker for external service integration
class CircuitBreakerMCPTool:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        
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

## 📊 Performance & Monitoring

### Integration Metrics

```python
# Monitor integration performance
class IntegrationMetrics:
    def __init__(self):
        self.metrics = {}
        
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

## 🛠️ Integration Best Practices

### Connection Management
- Use connection pooling for databases and HTTP clients
- Implement retry logic with exponential backoff
- Set appropriate timeout values
- Monitor connection health

### Error Handling
- Implement circuit breaker pattern for external services
- Use graceful degradation when services are unavailable
- Log integration errors with context
- Implement fallback mechanisms

### Security
- Store credentials securely (environment variables, secret management)
- Use authentication tokens with appropriate scopes
- Implement request signing for webhooks
- Validate all external data

### Performance
- Cache frequently accessed data
- Use async/await for I/O operations
- Implement request batching where possible
- Monitor integration performance metrics

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

---

**Next Steps**: See [EXAMPLE_IMPLEMENTATIONS.md](EXAMPLE_IMPLEMENTATIONS.md) for complete domain-specific integration examples and [GENERIC_DEPLOYMENT_GUIDE.md](GENERIC_DEPLOYMENT_GUIDE.md) for deployment strategies.