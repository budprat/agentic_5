# Domain Customization Guide

This guide shows how to adapt the A2A-MCP framework for your specific business domain.

## 🎯 Overview

The A2A-MCP framework is designed to be domain-agnostic. This guide will walk you through customizing it for any business domain - whether it's e-commerce, finance, healthcare, manufacturing, or any other industry.

## 🏗️ Customization Layers

### Layer 1: Agent Cards Configuration
**What**: JSON configurations defining agent capabilities and metadata  
**When**: Always required for any domain adaptation  
**Effort**: 1-2 hours

### Layer 2: Business Logic Implementation  
**What**: Domain-specific processing, validation, and workflow logic  
**When**: Required for complex business rules  
**Effort**: 1-3 days

### Layer 3: Data Integration
**What**: MCP tool integration with your data sources and systems  
**When**: Required for real-world applications  
**Effort**: 2-5 days

### Layer 4: UI/API Customization
**What**: Custom interfaces and API endpoints for your domain  
**When**: Optional, for enhanced user experience  
**Effort**: 3-7 days

## 📋 Step-by-Step Customization Process

### Step 1: Define Your Domain

**1.1 Identify Core Business Entities**
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

**1.2 Map Business Workflows**
```yaml
# Example E-commerce workflows
workflows:
  order_processing:
    - validate_order
    - check_inventory
    - process_payment
    - update_inventory
    - schedule_shipping
    - send_confirmation
    
  customer_service:
    - receive_inquiry
    - lookup_order
    - resolve_issue
    - update_records
    - follow_up
```

### Step 2: Create Domain-Specific Agent Cards

**2.1 Tier 1 - Master Orchestrator**

Create `agent_cards/tier1/{your_domain}_master_orchestrator.json`:

```json
{
  "name": "E-commerce Master Orchestrator",
  "description": "Coordinates complex e-commerce workflows including order processing, inventory management, and customer service",
  "tier": 1,
  "capabilities": [
    "workflow_orchestration",
    "business_rule_enforcement", 
    "multi_agent_coordination",
    "exception_handling"
  ],
  "specializations": [
    "order_processing",
    "inventory_management",
    "customer_service",
    "payment_processing"
  ],
  "dependencies": {
    "tier_2_agents": [
      "order_processing_specialist",
      "inventory_specialist", 
      "customer_service_specialist"
    ]
  },
  "business_rules": {
    "order_validation": "required",
    "inventory_checks": "mandatory",
    "payment_verification": "required"
  }
}
```

**2.2 Tier 2 - Domain Specialists**

Create `agent_cards/tier2/{domain}_specialist.json` for each business area:

```json
{
  "name": "Order Processing Specialist",
  "description": "Handles order validation, processing, and fulfillment workflows",
  "tier": 2,
  "capabilities": [
    "order_validation",
    "inventory_checking",
    "payment_processing",
    "fulfillment_coordination"
  ],
  "specializations": [
    "b2b_orders",
    "b2c_orders", 
    "subscription_orders",
    "bulk_orders"
  ],
  "dependencies": {
    "tier_3_agents": [
      "payment_service",
      "inventory_service",
      "shipping_service"
    ]
  },
  "validation_rules": {
    "min_order_value": 0.01,
    "max_order_items": 100,
    "customer_verification": "required"
  }
}
```

**2.3 Tier 3 - Service Agents**

Create `agent_cards/tier3/{service}_agent.json` for each external service:

```json
{
  "name": "Payment Processing Service",
  "description": "Handles payment transactions and verification",
  "tier": 3,
  "capabilities": [
    "payment_processing",
    "refund_handling",
    "fraud_detection",
    "compliance_checking"
  ],
  "tools": [
    "stripe_mcp",
    "paypal_mcp",
    "fraud_detection_mcp"
  ],
  "response_format": {
    "type": "structured",
    "schema": "payment_result"
  }
}
```

### Step 3: Implement Domain-Specific Business Logic

**3.1 Create Domain Models**

Create `src/a2a_mcp/domains/{your_domain}/models.py`:

```python
# ABOUTME: Domain-specific data models and business entities
# ABOUTME: Defines the core business objects for the domain

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

@dataclass
class Order:
    """E-commerce order model"""
    order_id: str
    customer_id: str
    items: List['OrderItem']
    total_amount: Decimal
    status: str = "pending"
    created_at: datetime = None
    
    def validate(self) -> bool:
        """Validate order business rules"""
        if self.total_amount <= 0:
            return False
        if not self.items:
            return False
        return True

@dataclass  
class OrderItem:
    """Order line item"""
    product_id: str
    quantity: int
    unit_price: Decimal
    
    @property
    def total_price(self) -> Decimal:
        return self.quantity * self.unit_price
```

**3.2 Create Domain Business Rules**

Create `src/a2a_mcp/domains/{your_domain}/rules.py`:

```python
# ABOUTME: Business rules and validation logic for the domain
# ABOUTME: Implements domain-specific constraints and policies

from typing import Dict, Any, List
from .models import Order, OrderItem

class EcommerceBusinessRules:
    """E-commerce specific business rules"""
    
    def __init__(self):
        self.max_order_value = Decimal("10000.00")
        self.max_items_per_order = 50
        
    def validate_order(self, order: Order) -> Dict[str, Any]:
        """Validate order against business rules"""
        errors = []
        
        # Check order value limits
        if order.total_amount > self.max_order_value:
            errors.append(f"Order value exceeds maximum of {self.max_order_value}")
            
        # Check item count limits  
        if len(order.items) > self.max_items_per_order:
            errors.append(f"Order exceeds maximum of {self.max_items_per_order} items")
            
        # Check inventory availability
        unavailable_items = self.check_inventory_availability(order.items)
        if unavailable_items:
            errors.append(f"Items not in stock: {unavailable_items}")
            
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
        
    def check_inventory_availability(self, items: List[OrderItem]) -> List[str]:
        """Check if items are available in inventory"""
        # Implement inventory checking logic
        return []
```

**3.3 Create Domain Workflows**

Create `src/a2a_mcp/domains/{your_domain}/workflows.py`:

```python
# ABOUTME: Domain-specific workflow definitions and orchestration
# ABOUTME: Implements business process flows and coordination logic

from typing import Dict, Any, List
from a2a_mcp.common.workflow import BaseWorkflow
from .models import Order
from .rules import EcommerceBusinessRules

class OrderProcessingWorkflow(BaseWorkflow):
    """E-commerce order processing workflow"""
    
    def __init__(self):
        super().__init__()
        self.business_rules = EcommerceBusinessRules()
        
    async def execute(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the order processing workflow"""
        
        # Step 1: Parse and validate order
        order = self.parse_order(order_data)
        validation_result = self.business_rules.validate_order(order)
        
        if not validation_result["valid"]:
            return {
                "status": "failed",
                "errors": validation_result["errors"]
            }
            
        # Step 2: Process payment
        payment_result = await self.process_payment(order)
        if not payment_result["success"]:
            return {
                "status": "failed", 
                "error": "Payment processing failed"
            }
            
        # Step 3: Update inventory
        inventory_result = await self.update_inventory(order)
        if not inventory_result["success"]:
            # Compensate: refund payment
            await self.refund_payment(payment_result["transaction_id"])
            return {
                "status": "failed",
                "error": "Inventory update failed"
            }
            
        # Step 4: Schedule fulfillment
        fulfillment_result = await self.schedule_fulfillment(order)
        
        return {
            "status": "success",
            "order_id": order.order_id,
            "payment_id": payment_result["transaction_id"],
            "fulfillment_id": fulfillment_result["fulfillment_id"]
        }
```

### Step 4: Configure MCP Tool Integration

**4.1 Define Domain-Specific Tools**

Create `.mcp.json` configuration for your domain tools:

```json
{
  "mcpServers": {
    "ecommerce_database": {
      "command": "python",
      "args": ["mcp_servers/ecommerce_db_server.py"],
      "description": "E-commerce database access"
    },
    "payment_gateway": {
      "command": "python", 
      "args": ["mcp_servers/payment_server.py"],
      "description": "Payment processing integration"
    },
    "inventory_system": {
      "command": "python",
      "args": ["mcp_servers/inventory_server.py"], 
      "description": "Inventory management system"
    },
    "shipping_api": {
      "command": "python",
      "args": ["mcp_servers/shipping_server.py"],
      "description": "Shipping and logistics API"
    }
  }
}
```

**4.2 Implement MCP Server for Domain Data**

Create `mcp_servers/ecommerce_db_server.py`:

```python
# ABOUTME: MCP server providing access to e-commerce database
# ABOUTME: Implements tools for querying orders, products, customers

import asyncio
from mcp.server import Server
from mcp.types import TextContent, Tool
import sqlite3

app = Server("ecommerce-db")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="query_orders",
            description="Query orders by various criteria",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "status": {"type": "string"},
                    "date_range": {"type": "object"}
                }
            }
        ),
        Tool(
            name="query_products", 
            description="Query products and inventory",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_id": {"type": "string"},
                    "category": {"type": "string"},
                    "in_stock": {"type": "boolean"}
                }
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "query_orders":
        # Implement order querying logic
        results = query_orders_db(arguments)
        return [TextContent(type="text", text=f"Orders found: {results}")]
        
    elif name == "query_products":
        # Implement product querying logic
        results = query_products_db(arguments)
        return [TextContent(type="text", text=f"Products found: {results}")]
        
    raise ValueError(f"Unknown tool: {name}")

def query_orders_db(criteria: dict):
    """Query orders from database"""
    # Implement actual database querying
    return []

def query_products_db(criteria: dict):
    """Query products from database"""
    # Implement actual database querying
    return []

if __name__ == "__main__":
    asyncio.run(app.run())
```

### Step 5: Create Domain-Specific Agent Instructions

**5.1 Create Instruction Templates**

Create `src/a2a_mcp/domains/{your_domain}/instructions.py`:

```python
# ABOUTME: Domain-specific instruction templates for agents
# ABOUTME: Provides specialized prompts and decision trees

ECOMMERCE_MASTER_ORCHESTRATOR_INSTRUCTIONS = """
You are the E-commerce Master Orchestrator, responsible for coordinating complex e-commerce workflows.

Your responsibilities:
1. Order Processing: Validate, process, and fulfill customer orders
2. Inventory Management: Ensure accurate inventory tracking and availability
3. Customer Service: Handle inquiries, returns, and support requests
4. Business Rules: Enforce e-commerce policies and compliance

DECISION TREE for Order Processing:
├── Order Received
│   ├── Validate Order → Invalid? → Return Error
│   └── Valid Order → Continue
├── Check Inventory → Out of Stock? → Notify Customer
├── Process Payment → Failed? → Cancel Order
├── Update Inventory → Update Failed? → Refund Payment
└── Schedule Fulfillment → Success

When processing orders, always:
- Validate order against business rules
- Check inventory availability before payment
- Process payment before inventory updates
- Implement compensation for failures
- Provide clear status updates

Output format: Return structured JSON with order status, processing steps, and any errors.
"""

ORDER_PROCESSING_SPECIALIST_INSTRUCTIONS = """
You are the Order Processing Specialist focused on order validation and fulfillment.

Chain-of-thought process:
1. ORDER_VALIDATION: Check order completeness and business rules
2. INVENTORY_CHECK: Verify product availability and quantities
3. CUSTOMER_VERIFICATION: Validate customer information and payment method
4. BUSINESS_RULES: Apply domain-specific constraints and policies
5. FULFILLMENT_PLANNING: Determine shipping method and timeline

Always ensure:
- Order meets minimum/maximum value requirements
- All products are in stock with sufficient quantities
- Customer information is complete and verified
- Payment method is valid and authorized
- Shipping address is deliverable

Return detailed order processing results with status and next steps.
"""
```

## 🛠️ Domain Examples

### E-commerce Platform

**Key Agents**:
- Order Processing Orchestrator
- Inventory Management Specialist  
- Payment Processing Service
- Shipping Coordination Service
- Customer Service Agent

**Workflows**:
- Order fulfillment
- Return processing
- Inventory replenishment
- Customer support

### Financial Services

**Key Agents**:
- Transaction Processing Orchestrator
- Risk Assessment Specialist
- Compliance Validation Service
- Fraud Detection Service
- Notification Service

**Workflows**:
- Payment processing
- Loan application
- Account management
- Regulatory reporting

### Healthcare Management

**Key Agents**:
- Patient Care Orchestrator
- Appointment Scheduling Specialist
- Medical Records Service
- Insurance Verification Service
- Billing Processing Service

**Workflows**:
- Patient registration
- Appointment scheduling
- Treatment planning
- Insurance processing

### Manufacturing Operations

**Key Agents**:
- Production Planning Orchestrator
- Quality Control Specialist
- Supply Chain Service
- Equipment Monitoring Service
- Compliance Tracking Service

**Workflows**:
- Production scheduling
- Quality assurance
- Supply chain optimization
- Equipment maintenance

## 🎯 Best Practices

### Agent Design
- **Single Responsibility**: Each agent should have a clear, focused purpose
- **Domain Expertise**: Agents should embody deep knowledge of their business area
- **Loose Coupling**: Minimize dependencies between agents
- **Clear Interfaces**: Use well-defined input/output contracts

### Business Logic
- **Centralized Rules**: Keep business rules in dedicated modules
- **Validation Layers**: Implement multiple validation checkpoints
- **Error Handling**: Plan for failure scenarios and compensation
- **Audit Trails**: Track all business operations for compliance

### Data Integration
- **MCP First**: Use MCP tools for all external system access
- **Schema Validation**: Validate data at system boundaries
- **Connection Pooling**: Optimize database and API connections
- **Caching Strategy**: Cache frequently accessed business data

### Testing Strategy
- **Business Scenarios**: Test real-world business workflows
- **Edge Cases**: Test boundary conditions and error scenarios
- **Integration Tests**: Test full agent collaboration flows
- **Performance Tests**: Validate under expected load

## 🚀 Quick Start Templates

Use these templates to rapidly bootstrap your domain:

```bash
# Generate domain template
python scripts/generate_domain.py --domain=your_domain --entities=entity1,entity2

# Create agent cards
python scripts/create_agent_cards.py --domain=your_domain --tier=1,2,3

# Generate MCP servers
python scripts/create_mcp_servers.py --domain=your_domain --services=service1,service2

# Set up testing
python scripts/setup_domain_tests.py --domain=your_domain
```

## 📚 Additional Resources

- [INTEGRATION_PATTERNS.md](INTEGRATION_PATTERNS.md) - Common integration patterns
- [EXAMPLE_IMPLEMENTATIONS.md](EXAMPLE_IMPLEMENTATIONS.md) - Complete domain examples  
- [GENERIC_DEPLOYMENT_GUIDE.md](GENERIC_DEPLOYMENT_GUIDE.md) - Deployment strategies
- [Framework Architecture Guide](docs/ARCHITECTURE.md) - Technical details

---

**Next Steps**: After customizing your domain, see [INTEGRATION_PATTERNS.md](INTEGRATION_PATTERNS.md) for connecting to your existing systems.