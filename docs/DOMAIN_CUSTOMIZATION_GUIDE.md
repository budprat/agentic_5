# Domain Customization Guide - Framework V2.0

This guide shows how to adapt the A2A-MCP Framework V2.0 for your specific business domain using the latest components and patterns.

## 🎯 Overview

The A2A-MCP Framework V2.0 is designed to be domain-agnostic with enterprise-grade features. This guide walks you through customizing it for any business domain using:
- **StandardizedAgentBase** for all agents
- **Master Orchestrator Templates** for different complexity levels
- **Quality Framework** for domain-specific validation
- **Observability** for production monitoring

## 📚 Essential References
- [Framework Components Guide](./FRAMEWORK_COMPONENTS_AND_ORCHESTRATION_GUIDE.md)
- [Multi-Agent Workflow Guide](./MULTI_AGENT_WORKFLOW_GUIDE.md)

## 🏗️ V2.0 Customization Layers

### Layer 1: Domain Definition & Planning
**What**: Define domain requirements, workflows, and quality needs  
**When**: Always required - foundation for everything else  
**Effort**: 2-4 hours

### Layer 2: Agent Implementation (V2.0)
**What**: Create agents using StandardizedAgentBase or GenericDomainAgent  
**When**: Required for all custom functionality  
**Effort**: 1-3 days

### Layer 3: Orchestration Setup
**What**: Configure master orchestrator with your domain specialists  
**When**: Required for multi-agent coordination  
**Effort**: 1-2 days

### Layer 4: Quality & Observability
**What**: Configure quality domains and monitoring  
**When**: Required for production systems  
**Effort**: 1-2 days

### Layer 5: Data Integration
**What**: MCP tool integration with your systems  
**When**: Required for real-world applications  
**Effort**: 2-5 days

## 📋 Step-by-Step Customization Process

### Step 1: Define Your Domain

**1.1 Choose Quality Domain**
```python
from a2a_mcp.common.quality_framework import QualityDomain

# Available domains:
# - QualityDomain.GENERIC (default)
# - QualityDomain.CREATIVE (content generation)
# - QualityDomain.ANALYTICAL (data analysis, research)
# - QualityDomain.CODING (code generation)
# - QualityDomain.COMMUNICATION (customer interaction)

# Example for E-commerce
quality_domain = QualityDomain.COMMUNICATION  # Customer-facing
# or
quality_domain = QualityDomain.ANALYTICAL  # Data analysis focus
```

**1.2 Identify Core Business Entities**
```yaml
# Example for E-commerce domain
entities:
  - products
  - customers  
  - orders
  - inventory
  - payments
  - shipping

# Example for Healthcare domain  
entities:
  - patients
  - appointments
  - medical_records
  - prescriptions
  - billing
  - insurance
```

**1.3 Map Business Workflows**
```yaml
# Example E-commerce workflows
workflows:
  order_processing:
    strategy: "sequential"  # or "parallel", "hybrid"
    steps:
      - validate_order
      - check_inventory
      - process_payment
      - update_inventory
      - schedule_shipping
      - send_confirmation
    
  customer_service:
    strategy: "parallel"
    steps:
      - classify_inquiry
      - route_to_specialist
      - resolve_issue
      - update_records
```

### Step 2: Create Domain Configuration

**2.1 Create Domain Config File**

Create `configs/domains/ecommerce.yaml`:

```yaml
domain:
  name: "E-commerce"
  description: "Multi-agent e-commerce system"
  version: "2.0"
  
quality:
  domain: "COMMUNICATION"
  thresholds:
    completeness: 0.90
    accuracy: 0.95
    relevance: 0.85
    customer_satisfaction: 0.92

specialists:
  order_processor:
    description: "Handles order validation and processing"
    tier: 2
    port: 10201
    capabilities:
      - order_validation
      - inventory_checking
      - payment_processing
    quality_focus: ["accuracy", "completeness"]
    
  customer_service:
    description: "Manages customer inquiries and issues"
    tier: 2
    port: 10202
    capabilities:
      - inquiry_classification
      - issue_resolution
      - sentiment_analysis
    quality_focus: ["customer_satisfaction", "relevance"]
    
  inventory_manager:
    description: "Tracks and manages inventory"
    tier: 2
    port: 10203
    capabilities:
      - stock_tracking
      - reorder_management
      - availability_checking
    quality_focus: ["accuracy", "completeness"]

orchestration:
  type: "EnhancedMasterOrchestratorTemplate"
  enable_phase_7_streaming: true
  enable_observability: true
  parallel_threshold: 3
  session_timeout: 3600

observability:
  tracing:
    enabled: true
    sample_rate: 1.0
  metrics:
    enabled: true
    export_interval: 60
  logging:
    level: "INFO"
    structured: true
```

### Step 3: Implement Domain Agents (V2.0)

**3.1 Quick Implementation with GenericDomainAgent**

```python
# src/a2a_mcp/agents/ecommerce/specialists.py
from a2a_mcp.common.generic_domain_agent import GenericDomainAgent
from a2a_mcp.common.quality_framework import QualityDomain

def create_ecommerce_specialists(config):
    """Create all domain specialists using V2.0 templates."""
    specialists = {}
    
    # Order Processing Specialist
    specialists['order_processor'] = GenericDomainAgent(
        domain="E-commerce",
        specialization="order_processor",
        capabilities=[
            "Validate customer orders",
            "Check product availability",
            "Process payments securely",
            "Coordinate with shipping"
        ],
        quality_domain=QualityDomain.ANALYTICAL,
        tools=["database_query", "payment_gateway", "inventory_check"],
        custom_instructions="""
        You are an order processing specialist. Always:
        1. Validate order details thoroughly
        2. Check inventory before confirming
        3. Ensure payment security
        4. Provide clear status updates
        """
    )
    
    # Customer Service Specialist
    specialists['customer_service'] = GenericDomainAgent(
        domain="E-commerce",
        specialization="customer_service",
        capabilities=[
            "Handle customer inquiries",
            "Resolve order issues",
            "Process returns and refunds",
            "Analyze customer sentiment"
        ],
        quality_domain=QualityDomain.COMMUNICATION,
        tools=["order_lookup", "customer_history", "sentiment_analysis"],
        quality_thresholds={
            "customer_satisfaction": 0.92,
            "response_relevance": 0.90
        }
    )
    
    return specialists
```

**3.2 Custom Implementation with StandardizedAgentBase**

```python
# src/a2a_mcp/agents/ecommerce/order_processor.py
from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.common.quality_framework import QualityDomain
from a2a_mcp.common.observability import trace_async
from a2a_mcp.common.response_formatter import ResponseFormatter
from typing import Dict, Any
import json

class OrderProcessingAgent(StandardizedAgentBase):
    """V2.0 Order Processing Agent with full enterprise features."""
    
    def __init__(self):
        super().__init__(
            agent_name="E-commerce Order Processor",
            description="Handles complex order processing with validation",
            instructions=self._get_order_processing_instructions(),
            content_types=['text', 'application/json'],
            quality_config={
                "domain": QualityDomain.ANALYTICAL,
                "thresholds": {
                    "completeness": 0.95,
                    "accuracy": 0.98,
                    "consistency": 0.90
                }
            },
            mcp_tools_enabled=True,
            a2a_enabled=True,
            enable_observability=True
        )
        
    def _get_order_processing_instructions(self) -> str:
        return """
        You are an expert order processing agent for an e-commerce platform.
        
        Your responsibilities:
        1. Validate all order details (customer, products, shipping, payment)
        2. Check inventory availability in real-time
        3. Process payments securely through payment gateway
        4. Update inventory after successful payment
        5. Schedule shipping and generate tracking
        6. Send confirmation to customer
        
        Quality standards:
        - All validations must be thorough (95%+ completeness)
        - Payment processing must be 100% accurate
        - Customer communication must be clear and professional
        
        Use available MCP tools:
        - inventory_check: Check product availability
        - payment_process: Process payment transactions
        - shipping_schedule: Schedule shipment
        - notification_send: Send customer notifications
        """
    
    @trace_async
    async def process_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process order with full V2.0 features."""
        try:
            action = message.get("action")
            data = message.get("data", {})
            
            self.logger.info("Processing order request", extra={
                "action": action,
                "order_id": data.get("order_id"),
                "trace_id": self.get_trace_id()
            })
            
            if action == "process_order":
                result = await self._process_order(data)
            elif action == "validate_order":
                result = await self._validate_order(data)
            elif action == "check_order_status":
                result = await self._check_order_status(data)
            else:
                result = {"error": "Unknown action", "status": "failed"}
            
            # V2.0: Automatic quality validation and formatting
            return self.format_response(result)
            
        except Exception as e:
            self.logger.error(f"Order processing error: {e}", 
                            extra={"trace_id": self.get_trace_id()},
                            exc_info=True)
            return self.format_error_response(str(e))
    
    async def _process_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process complete order with quality checks."""
        order_id = order_data.get("order_id")
        
        # Step 1: Validate order
        validation = await self._validate_order(order_data)
        if not validation["valid"]:
            return {
                "status": "failed",
                "reason": "validation_failed",
                "details": validation["errors"]
            }
        
        # Step 2: Check inventory (parallel for multiple items)
        inventory_checks = await self._check_inventory_parallel(
            order_data["items"]
        )
        if not all(check["available"] for check in inventory_checks):
            return {
                "status": "failed",
                "reason": "insufficient_inventory",
                "unavailable_items": [
                    item for item, check in zip(order_data["items"], inventory_checks)
                    if not check["available"]
                ]
            }
        
        # Step 3: Process payment
        payment_result = await self.use_mcp_tool("payment_process", {
            "amount": order_data["total_amount"],
            "payment_method": order_data["payment_method"],
            "customer_id": order_data["customer_id"]
        })
        
        if payment_result["status"] != "success":
            return {
                "status": "failed",
                "reason": "payment_failed",
                "payment_error": payment_result.get("error")
            }
        
        # Step 4: Update inventory
        await self._update_inventory(order_data["items"])
        
        # Step 5: Schedule shipping
        shipping = await self.use_mcp_tool("shipping_schedule", {
            "order_id": order_id,
            "items": order_data["items"],
            "shipping_address": order_data["shipping_address"],
            "shipping_method": order_data["shipping_method"]
        })
        
        # Step 6: Send confirmation
        await self.use_mcp_tool("notification_send", {
            "type": "order_confirmation",
            "order_id": order_id,
            "customer_email": order_data["customer_email"],
            "tracking_number": shipping["tracking_number"]
        })
        
        return {
            "status": "success",
            "order_id": order_id,
            "tracking_number": shipping["tracking_number"],
            "estimated_delivery": shipping["estimated_delivery"],
            "payment_confirmation": payment_result["transaction_id"]
        }
    
    async def _check_inventory_parallel(self, items: list) -> list:
        """Check inventory for multiple items in parallel."""
        import asyncio
        
        tasks = [
            self.use_mcp_tool("inventory_check", {
                "product_id": item["product_id"],
                "quantity": item["quantity"]
            })
            for item in items
        ]
        
        return await asyncio.gather(*tasks)
```

### Step 4: Create Master Orchestrator

```python
# src/a2a_mcp/agents/ecommerce/orchestrator.py
from a2a_mcp.common.master_orchestrator_template import EnhancedMasterOrchestratorTemplate
from a2a_mcp.common.quality_framework import QualityDomain

def create_ecommerce_orchestrator(config):
    """Create V2.0 orchestrator for e-commerce domain."""
    
    orchestrator = EnhancedMasterOrchestratorTemplate(
        domain_name="E-commerce",
        domain_description="Comprehensive e-commerce operations platform",
        domain_specialists={
            "order_processor": "Handles order validation and processing",
            "customer_service": "Manages customer inquiries and support",
            "inventory_manager": "Tracks and manages product inventory",
            "shipping_coordinator": "Coordinates shipping and delivery",
            "payment_processor": "Handles payment transactions"
        },
        quality_domain=QualityDomain.COMMUNICATION,
        enable_phase_7_streaming=True,
        enable_observability=True,
        quality_thresholds={
            "completeness": 0.92,
            "accuracy": 0.96,
            "customer_satisfaction": 0.90
        },
        parallel_threshold=3,  # Parallel execution for 3+ independent tasks
        session_timeout=3600
    )
    
    return orchestrator
```

### Step 5: Configure MCP Tools

```python
# src/a2a_mcp/mcp/ecommerce_tools.py
from a2a_mcp.common.generic_mcp_server_template import GenericMCPServerTemplate

class EcommerceMCPServer(GenericMCPServerTemplate):
    """MCP server with e-commerce specific tools."""
    
    def __init__(self):
        tools = {
            "inventory_check": self.inventory_check,
            "payment_process": self.payment_process,
            "shipping_schedule": self.shipping_schedule,
            "order_lookup": self.order_lookup,
            "customer_history": self.customer_history,
            "notification_send": self.notification_send
        }
        
        super().__init__(
            server_name="E-commerce MCP Server",
            version="2.0",
            tools=tools
        )
    
    async def inventory_check(self, product_id: str, quantity: int) -> dict:
        """Check product availability."""
        # Integration with inventory system
        # This would connect to your actual inventory database
        available = await self.db.check_inventory(product_id, quantity)
        return {
            "product_id": product_id,
            "requested": quantity,
            "available": available,
            "in_stock": available >= quantity
        }
    
    async def payment_process(self, amount: float, payment_method: dict, 
                             customer_id: str) -> dict:
        """Process payment transaction."""
        # Integration with payment gateway
        # This would connect to Stripe, PayPal, etc.
        result = await self.payment_gateway.process(
            amount=amount,
            method=payment_method,
            customer=customer_id
        )
        return {
            "status": result.status,
            "transaction_id": result.transaction_id,
            "amount_charged": result.amount
        }
```

### Step 6: Create Launch Configuration

```python
# launch/launch_ecommerce.py
from a2a_mcp.common.agent_runner import AgentRunner
from a2a_mcp.agents.ecommerce.specialists import create_ecommerce_specialists
from a2a_mcp.agents.ecommerce.orchestrator import create_ecommerce_orchestrator
from a2a_mcp.common.config_manager import ConfigManager
import asyncio

async def launch_ecommerce_system():
    """Launch complete e-commerce multi-agent system."""
    
    # Load configuration
    config = ConfigManager()
    domain_config = config.load_domain_config("ecommerce")
    
    # Create orchestrator
    orchestrator = create_ecommerce_orchestrator(domain_config)
    orchestrator_runner = AgentRunner(
        agent=orchestrator,
        port=10200,
        enable_health_check=True
    )
    
    # Create specialists
    specialists = create_ecommerce_specialists(domain_config)
    specialist_runners = []
    
    for name, agent in specialists.items():
        port = domain_config["specialists"][name]["port"]
        runner = AgentRunner(
            agent=agent,
            port=port,
            enable_health_check=True
        )
        specialist_runners.append(runner)
    
    # Start all agents
    await orchestrator_runner.start()
    for runner in specialist_runners:
        await runner.start()
    
    print("E-commerce system launched successfully!")
    print(f"Orchestrator: http://localhost:10200")
    print(f"Grafana Dashboard: http://localhost:3000")
    
    # Keep running
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(launch_ecommerce_system())
```

### Step 7: Test Your Domain

```python
# tests/test_ecommerce_domain.py
import pytest
from a2a_mcp.common.generic_a2a_client import GenericA2AClient

@pytest.fixture
async def ecommerce_client():
    client = GenericA2AClient(base_url="http://localhost:10200")
    yield client
    await client.close()

async def test_order_processing(ecommerce_client):
    """Test complete order processing workflow."""
    
    # Submit order
    response = await ecommerce_client.send_request({
        "action": "process_order",
        "data": {
            "order_id": "ORD-12345",
            "customer_id": "CUST-789",
            "items": [
                {"product_id": "PROD-001", "quantity": 2, "price": 29.99},
                {"product_id": "PROD-002", "quantity": 1, "price": 49.99}
            ],
            "total_amount": 109.97,
            "shipping_address": {
                "street": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip": "10001"
            },
            "payment_method": {
                "type": "credit_card",
                "last_four": "1234"
            }
        }
    })
    
    assert response["status"] == "success"
    assert "tracking_number" in response
    assert "payment_confirmation" in response

async def test_customer_service(ecommerce_client):
    """Test customer service inquiry."""
    
    response = await ecommerce_client.send_request({
        "action": "customer_inquiry",
        "data": {
            "inquiry_type": "order_status",
            "order_id": "ORD-12345",
            "customer_message": "Where is my order?"
        }
    })
    
    assert response["status"] == "success"
    assert response["quality_metadata"]["customer_satisfaction"] >= 0.9
```

## 🎨 Domain Examples

### Finance Domain
```yaml
specialists:
  market_analyst: "Analyzes market trends and indicators"
  risk_assessor: "Evaluates investment risks"
  portfolio_manager: "Optimizes portfolio allocation"
  compliance_checker: "Ensures regulatory compliance"
quality_domain: ANALYTICAL
```

### Healthcare Domain
```yaml
specialists:
  patient_intake: "Handles patient registration and history"
  symptom_analyzer: "Analyzes symptoms and suggests next steps"
  appointment_scheduler: "Manages appointment booking"
  prescription_manager: "Handles prescription workflows"
quality_domain: COMMUNICATION  # Patient-facing
```

### Manufacturing Domain
```yaml
specialists:
  production_planner: "Plans production schedules"
  quality_inspector: "Monitors quality metrics"
  inventory_tracker: "Tracks raw materials and products"
  maintenance_scheduler: "Schedules equipment maintenance"
quality_domain: ANALYTICAL
```

## 📊 Monitoring Your Domain

### 1. Domain-Specific Metrics
```python
# Add custom metrics for your domain
from a2a_mcp.common.metrics_collector import get_metrics_collector

metrics = get_metrics_collector()

# E-commerce specific metrics
metrics.record_custom_metric("orders_processed", 1)
metrics.record_custom_metric("average_order_value", 109.97)
metrics.record_custom_metric("cart_abandonment_rate", 0.15)
```

### 2. Custom Dashboards
Create domain-specific Grafana dashboards:
- Order processing pipeline visualization
- Customer satisfaction trends
- Inventory levels monitoring
- Payment success rates

### 3. Quality Monitoring
```python
# Monitor domain-specific quality metrics
quality_metrics = {
    "order_accuracy": 0.98,
    "delivery_on_time": 0.95,
    "customer_satisfaction": 0.92
}

metrics.record_quality_validation(
    domain="E-commerce",
    status="passed",
    scores=quality_metrics
)
```

## 🚀 Best Practices

1. **Start Simple**: Use GenericDomainAgent for quick prototypes
2. **Iterate**: Add complexity as you understand requirements
3. **Monitor Early**: Enable observability from the start
4. **Test Thoroughly**: Create domain-specific test scenarios
5. **Document**: Keep your domain configuration well-documented
6. **Validate Quality**: Set appropriate thresholds for your domain

## 📚 Next Steps

1. Review [Framework Components Guide](./FRAMEWORK_COMPONENTS_AND_ORCHESTRATION_GUIDE.md) for detailed component documentation
2. Follow [Multi-Agent Workflow Guide](./MULTI_AGENT_WORKFLOW_GUIDE.md) for workflow patterns
3. Check `examples/domains/` for more domain examples
4. Set up monitoring using [Observability Deployment Guide](./OBSERVABILITY_DEPLOYMENT.md)

The A2A-MCP Framework V2.0 provides all the tools needed to build sophisticated domain-specific multi-agent systems with enterprise-grade features!