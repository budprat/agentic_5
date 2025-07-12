# Finance Multi-Agent System Workflow
## Complete End-to-End User Query Execution Using Framework V2.0

This document demonstrates how a user query flows through a finance multi-agent system built using our Framework V2.0 boilerplate templates.

---

## 1. System Setup Using Framework V2.0 Boilerplate

### Step 1: Create Finance Domain Registry
```bash
# Copy template and customize for finance domain
cp src/a2a_mcp/common/agent_registry_template.py finance_agent_registry.py
```

**Finance Agent Registry Structure:**
```python
# finance_agent_registry.py
FINANCE_AGENTS = {
    # TIER 1: Master Orchestrator (Port 13001)
    "Finance Master Orchestrator": {
        "port": 13001,
        "tier": 1, 
        "template": "MasterOrchestratorTemplate",
        "description": "Master financial intelligence orchestrator",
        "instructions": "Coordinate financial analysis across market, risk, portfolio domains..."
    },
    
    # TIER 2: Domain Specialists (Ports 13002-13006)
    "Market Analysis Specialist": {
        "port": 13002,
        "tier": 2,
        "template": "StandardizedAgentBase", 
        "description": "Market trends and technical analysis specialist"
    },
    "Risk Assessment Specialist": {
        "port": 13003,
        "tier": 2,
        "template": "StandardizedAgentBase",
        "description": "Risk modeling and compliance specialist"  
    },
    "Portfolio Management Specialist": {
        "port": 13004,
        "tier": 2,
        "template": "StandardizedAgentBase",
        "description": "Portfolio optimization and allocation specialist"
    },
    
    # TIER 3: Intelligence Modules (Ports 13010-13059)
    "Stock Price Monitor": {
        "port": 13010,
        "tier": 3,
        "template": "ADKServiceAgent",
        "description": "Real-time stock price monitoring via APIs"
    },
    "Financial Data Aggregator": {
        "port": 13011, 
        "tier": 3,
        "template": "ADKServiceAgent",
        "description": "Financial data collection from multiple sources"
    },
    "Trend Pattern Analyzer": {
        "port": 13012,
        "tier": 3,
        "template": "StandardizedAgentBase", 
        "description": "Technical pattern recognition and trend analysis"
    },
    "Risk Calculator": {
        "port": 13013,
        "tier": 3,
        "template": "ADKServiceAgent",
        "description": "VaR, volatility, and risk metrics calculation"
    },
    "Portfolio Optimizer": {
        "port": 13014,
        "tier": 3,
        "template": "StandardizedAgentBase",
        "description": "Modern portfolio theory optimization"
    }
    # ... more agents as needed
}
```

### Step 2: Create Finance Domain Base Agent
```python
# finance_base_agent.py - Using GenericDomainAgent
from a2a_mcp.common.generic_domain_agent import GenericDomainAgent

class FinanceDomainAgent(GenericDomainAgent):
    def __init__(self, agent_name: str, description: str, instructions: str, port: int = None):
        super().__init__(
            agent_name=agent_name,
            description=description,
            instructions=instructions,
            port=port,
            port_ranges={
                "tier_1": (13001, 13001),  # Finance Master Orchestrator
                "tier_2": (13002, 13009),  # Domain Specialists
                "tier_3": (13010, 13059)   # Intelligence Modules
            },
            quality_domain="BUSINESS",
            domain_name="Finance", 
            required_env_vars=['GOOGLE_API_KEY', 'FINANCE_API_KEY']
        )
```

### Step 3: Create Finance Client
```python
# finance_client.py - Using generic_a2a_client template
from a2a_mcp.common.generic_a2a_client import GenericA2AClient

class FinanceA2AClient(GenericA2AClient):
    def __init__(self, orchestrator_url: str = "http://localhost:13001"):
        super().__init__(orchestrator_url, "Finance")
    
    def display_result(self, result: Dict[str, Any]) -> None:
        """Finance-specific result display."""
        if "error" in result:
            console.print(f"[red]Error: {result['error']}[/red]")
            return
            
        # Display financial analysis
        if "portfolio_analysis" in result:
            # Display portfolio metrics, risk analysis, recommendations
            self._display_portfolio_analysis(result["portfolio_analysis"])
        
        if "market_insights" in result:
            # Display market trends, key indicators
            self._display_market_insights(result["market_insights"])
```

---

## 2. Complete User Query Workflow

### User Query: "Analyze my portfolio risk and suggest optimizations"

Let's trace this query through the entire system:

### Phase 1: Client Entry Point

**1. User Input Processing**
```python
# User runs: python finance_client.py
# Or uses interactive session:

async with FinanceA2AClient() as client:
    query = "Analyze my portfolio risk and suggest optimizations"
    result = await client.query_agent(query)
    client.display_result(result)
```

**2. A2A Protocol Request Creation**
```python
# finance_client.py creates A2A JSON-RPC request
json_rpc_request = {
    "jsonrpc": "2.0",
    "id": "uuid-12345",
    "method": "message/stream",
    "params": {
        "message": {
            "role": "user", 
            "parts": [{"kind": "text", "text": "Analyze my portfolio risk and suggest optimizations"}],
            "messageId": "msg-uuid-67890",
            "kind": "message"
        },
        "metadata": {"domain": "finance"}
    }
}

# Sent to: http://localhost:13001 (Finance Master Orchestrator)
```

### Phase 2: Tier 1 - Master Orchestrator Processing

**3. Finance Master Orchestrator (Port 13001)**
```python
# Uses MasterOrchestratorTemplate with LangGraph workflow

class FinanceMasterOrchestrator(MasterOrchestratorTemplate):
    def __init__(self):
        domain_specialists = {
            "market_specialist": "Market analysis and trends (port 13002)",
            "risk_specialist": "Risk assessment and modeling (port 13003)", 
            "portfolio_specialist": "Portfolio optimization (port 13004)"
        }
        
        planning_instructions = """
        You are the Finance Master Orchestrator. For portfolio risk analysis:
        1. Activate risk_specialist for comprehensive risk assessment
        2. Activate portfolio_specialist for optimization recommendations  
        3. Activate market_specialist for current market context
        4. Synthesize insights into actionable portfolio strategy
        """
```

**4. Task Decomposition (LangGraph Planning Node)**
```python
# MasterOrchestratorTemplate internally creates execution plan:
execution_plan = {
    "tasks": [
        {
            "specialist": "risk_specialist",
            "task": "Analyze current portfolio risk metrics, VaR, volatility patterns",
            "priority": "high",
            "dependencies": []
        },
        {
            "specialist": "portfolio_specialist", 
            "task": "Generate optimization recommendations based on risk analysis",
            "priority": "high",
            "dependencies": ["risk_analysis_complete"]
        },
        {
            "specialist": "market_specialist",
            "task": "Provide current market context affecting portfolio decisions", 
            "priority": "medium",
            "dependencies": []
        }
    ],
    "coordination": "parallel_with_dependencies"
}
```

### Phase 3: Tier 2 - Domain Specialists Activation

**5. Risk Assessment Specialist (Port 13003)**
```python
# Uses StandardizedAgentBase + FinanceDomainAgent patterns
class RiskAssessmentSpecialist(FinanceDomainAgent):
    async def _execute_agent_logic(self, query: str, context_id: str, task_id: str):
        # Coordinates with Tier 3 intelligence modules:
        
        # A2A call to Risk Calculator (13013)
        risk_metrics = await self.a2a_client.call_agent(
            "http://localhost:13013",
            "Calculate VaR, beta, Sharpe ratio for current portfolio"
        )
        
        # A2A call to Financial Data Aggregator (13011) 
        historical_data = await self.a2a_client.call_agent(
            "http://localhost:13011",
            "Fetch 2-year historical data for portfolio holdings"
        )
        
        # Process with Google ADK agent
        analysis_result = await self.agent.run(
            f"Analyze portfolio risk using: {risk_metrics} and {historical_data}"
        )
        
        return {
            "risk_score": 7.2,
            "var_95": "$12,500",
            "beta": 1.15,
            "volatility": "18.5%",
            "risk_factors": ["Tech concentration", "Interest rate sensitivity"],
            "recommendations": ["Diversify sectors", "Add defensive assets"]
        }
```

**6. Portfolio Management Specialist (Port 13004)**
```python
class PortfolioManagementSpecialist(FinanceDomainAgent):
    async def _execute_agent_logic(self, query: str, context_id: str, task_id: str):
        # Wait for risk analysis dependency
        risk_data = await self.get_dependency_result("risk_analysis_complete")
        
        # A2A call to Portfolio Optimizer (13014)
        optimization = await self.a2a_client.call_agent(
            "http://localhost:13014", 
            f"Optimize portfolio allocation given risk constraints: {risk_data}"
        )
        
        return {
            "current_allocation": {"Tech": 45%, "Healthcare": 20%, "Finance": 15%, "Bonds": 20%},
            "recommended_allocation": {"Tech": 35%, "Healthcare": 20%, "Finance": 15%, "Bonds": 20%, "REITs": 10%},
            "expected_return": "12.3%",
            "risk_reduction": "15%",
            "rebalancing_trades": [
                {"action": "SELL", "symbol": "AAPL", "shares": 50},
                {"action": "BUY", "symbol": "VNQ", "shares": 100}
            ]
        }
```

**7. Market Analysis Specialist (Port 13002)**
```python
class MarketAnalysisSpecialist(FinanceDomainAgent):
    async def _execute_agent_logic(self, query: str, context_id: str, task_id: str):
        # A2A calls to intelligence modules
        current_prices = await self.a2a_client.call_agent(
            "http://localhost:13010",  # Stock Price Monitor
            "Get current market data for portfolio holdings"
        )
        
        trend_analysis = await self.a2a_client.call_agent(
            "http://localhost:13012",  # Trend Pattern Analyzer
            "Analyze current market trends affecting portfolio"
        )
        
        return {
            "market_sentiment": "Cautiously Optimistic",
            "sector_outlook": {
                "Technology": "Neutral to Positive",
                "Healthcare": "Positive", 
                "REITs": "Positive"
            },
            "key_risks": ["Fed policy uncertainty", "Inflation concerns"],
            "opportunities": ["Defensive REITs", "Healthcare growth"]
        }
```

### Phase 4: Tier 3 - Intelligence Modules Execution

**8. Risk Calculator (Port 13013) - ADKServiceAgent**
```python
class RiskCalculator(ADKServiceAgent):
    async def _execute_agent_logic(self, query: str, context_id: str, task_id: str):
        # Uses MCP tools for financial calculations
        portfolio_data = await self.mcp_tools.get_portfolio_data()
        
        # Direct calculation using financial libraries
        var_95 = calculate_var(portfolio_data, confidence=0.95)
        beta = calculate_beta(portfolio_data, market_data)
        
        return {
            "var_95": var_95,
            "beta": beta,
            "volatility": calculate_volatility(portfolio_data),
            "correlation_matrix": calculate_correlations(portfolio_data)
        }
```

**9. Stock Price Monitor (Port 13010) - ADKServiceAgent**
```python
class StockPriceMonitor(ADKServiceAgent):
    async def _execute_agent_logic(self, query: str, context_id: str, task_id: str):
        # MCP tool calls to external APIs
        prices = await self.mcp_tools.fetch_current_prices(symbols)
        market_data = await self.mcp_tools.fetch_market_indicators()
        
        return {
            "prices": prices,
            "market_data": market_data,
            "last_updated": datetime.now().isoformat()
        }
```

### Phase 5: Response Synthesis and Delivery

**10. Master Orchestrator Synthesis**
```python
# MasterOrchestratorTemplate synthesis phase
synthesis_result = {
    "executive_summary": "Portfolio shows elevated risk due to tech concentration. Recommend rebalancing to reduce risk by 15% while maintaining growth potential.",
    
    "risk_analysis": {
        "current_risk_score": 7.2,
        "risk_factors": ["45% tech concentration", "High beta of 1.15"],
        "var_95": "$12,500 daily risk"
    },
    
    "optimization_recommendations": {
        "target_allocation": {"Tech": 35%, "Healthcare": 20%, "Finance": 15%, "Bonds": 20%, "REITs": 10%},
        "expected_improvement": "15% risk reduction, maintain 12%+ returns",
        "specific_trades": [
            {"action": "SELL", "symbol": "AAPL", "shares": 50, "reason": "Reduce tech concentration"},
            {"action": "BUY", "symbol": "VNQ", "shares": 100, "reason": "Add defensive diversification"}
        ]
    },
    
    "market_context": {
        "timing": "Good time for rebalancing - market stability",
        "sector_outlook": {"REITs": "Positive", "Tech": "Neutral"}
    },
    
    "action_plan": {
        "immediate": ["Execute rebalancing trades", "Set stop-loss orders"],
        "short_term": ["Monitor Fed policy impact", "Review in 30 days"],
        "long_term": ["Quarterly rebalancing", "Annual strategy review"]
    },
    
    "confidence_score": 0.87
}
```

**11. Response Streaming Back to Client**
```python
# A2A JSON-RPC streaming response
for chunk in synthesis_result:
    sse_event = {
        "data": {
            "jsonrpc": "2.0",
            "id": "uuid-12345", 
            "result": {
                "kind": "streaming-response",
                "message": {
                    "parts": [{"kind": "text", "text": chunk}]
                },
                "final": is_last_chunk
            }
        }
    }
    # Stream to client
```

**12. Client Display**
```python
# FinanceA2AClient displays formatted results
def display_result(self, result):
    # Portfolio Risk Dashboard
    console.print(Panel(
        f"Risk Score: {result['risk_analysis']['current_risk_score']}/10\n"
        f"Daily VaR (95%): {result['risk_analysis']['var_95']}\n"
        f"Key Risks: {', '.join(result['risk_analysis']['risk_factors'])}",
        title="📊 Portfolio Risk Analysis", 
        style="red"
    ))
    
    # Optimization Recommendations  
    console.print(Panel(
        f"Recommended Allocation:\n" +
        "\n".join([f"  {sector}: {pct}" for sector, pct in result['optimization_recommendations']['target_allocation'].items()]) +
        f"\n\nExpected Improvement: {result['optimization_recommendations']['expected_improvement']}",
        title="⚡ Optimization Recommendations",
        style="green"
    ))
    
    # Action Plan
    console.print(Panel(
        f"Immediate Actions:\n" + 
        "\n".join([f"  • {action}" for action in result['action_plan']['immediate']]),
        title="🎯 Action Plan",
        style="cyan"
    ))
```

---

## 3. Complete System Architecture Flow

```
User Query: "Analyze portfolio risk and suggest optimizations"
     ↓
┌─────────────────────────────────────────────────────────────┐
│ FINANCE A2A CLIENT (finance_client.py)                     │
│ • A2A JSON-RPC request creation                            │  
│ • Progress display with Rich UI                            │
│ • Finance-specific result formatting                       │
└─────────────────────────┬───────────────────────────────────┘
                          ↓ HTTP POST to localhost:13001
┌─────────────────────────────────────────────────────────────┐
│ TIER 1: FINANCE MASTER ORCHESTRATOR (Port 13001)          │
│ Template: MasterOrchestratorTemplate                       │
│ • Query analysis and task decomposition                    │
│ • LangGraph workflow planning                              │
│ • Parallel specialist coordination                         │
│ • Quality-aware decision making                            │
└─────────────────────────┬───────────────────────────────────┘
                          ↓ A2A calls to specialists
    ┌─────────────────────┼─────────────────────┐
    ↓                     ↓                     ↓
┌─────────────┐ ┌─────────────┐ ┌─────────────────┐
│TIER 2: RISK │ │TIER 2: PORT │ │TIER 2: MARKET   │
│SPECIALIST   │ │SPECIALIST   │ │SPECIALIST       │
│Port 13003   │ │Port 13004   │ │Port 13002       │
└─────┬───────┘ └─────┬───────┘ └─────┬───────────┘
      ↓               ↓               ↓
┌─────────────────────────────────────────────────────────────┐
│ TIER 3: INTELLIGENCE MODULES                               │
│ • Risk Calculator (13013) - ADKServiceAgent               │
│ • Portfolio Optimizer (13014) - StandardizedAgentBase    │
│ • Stock Price Monitor (13010) - ADKServiceAgent          │
│ • Financial Data Aggregator (13011) - ADKServiceAgent    │
│ • Trend Pattern Analyzer (13012) - StandardizedAgentBase │
└─────────────────────────┬───────────────────────────────────┘
                          ↓ Results synthesis
┌─────────────────────────────────────────────────────────────┐
│ MASTER ORCHESTRATOR SYNTHESIS                              │
│ • Cross-domain insight integration                         │
│ • Executive summary generation                             │
│ • Actionable recommendations                               │
│ • Confidence scoring and quality validation               │
└─────────────────────────┬───────────────────────────────────┘
                          ↓ A2A streaming response  
┌─────────────────────────────────────────────────────────────┐
│ CLIENT RESULT DISPLAY                                      │
│ • Risk analysis dashboard                                  │
│ • Portfolio optimization recommendations                   │
│ • Market context and timing                               │
│ • Actionable next steps                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Framework V2.0 Benefits Demonstrated

**✅ Tier-Based Architecture:** Clear separation of concerns with specialized agents per tier

**✅ Template Reusability:** All agents built from standardized Framework V2.0 templates

**✅ A2A Protocol Compliance:** Seamless inter-agent communication using JSON-RPC

**✅ Quality Validation:** Built-in quality thresholds and confidence scoring

**✅ Graceful Degradation:** Fallback handling when agents unavailable

**✅ Domain Specialization:** Finance-specific logic while maintaining framework standards

**✅ Parallel Processing:** LangGraph coordination enables efficient parallel execution

**✅ MCP Tool Integration:** Tier 3 agents seamlessly integrate external data sources

This workflow demonstrates how our Framework V2.0 boilerplate enables rapid creation of sophisticated multi-agent systems while ensuring consistency, quality, and maintainability across the entire ecosystem.