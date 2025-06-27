# Market Oracle - Autonomous Investment Intelligence System

## Overview

Market Oracle is a sophisticated multi-agent investment intelligence system built on the A2A-MCP framework. It democratizes hedge fund-level market analysis by combining social sentiment, fundamental analysis, technical indicators, and automated risk management.

## System Architecture

### 8 Specialized Agents

1. **Oracle Prime (Port 10501)** - Master orchestrator with risk management
2. **Sentiment Seeker (Port 10502)** - Reddit/social sentiment analysis  
3. **Fundamental Analyst (Port 10503)** - SEC filings, earnings analysis
4. **Technical Prophet (Port 10504)** - ML-powered price prediction
5. **Risk Guardian (Port 10505)** - Portfolio risk management
6. **Trend Correlator (Port 10506)** - Google Trends correlation
7. **Report Synthesizer (Port 10507)** - Investment documentation
8. **Audio Briefer (Port 10508)** - Personalized market briefings

### MCP Integration

- **Reddit MCP**: WallStreetBets sentiment, retail investor discussions
- **Google Trends MCP**: Search volume correlation with stock movements
- **HuggingFace MCP**: Financial document analysis, price prediction models
- **BrightData MCP**: SEC filings, news scraping, earnings data
- **Snowflake MCP**: Historical market data analysis, backtesting
- **Supabase MCP**: Portfolio tracking, real-time positions
- **n8n MCP**: Trading automation, alert systems
- **Notion MCP**: Research documentation, investment thesis
- **ElevenLabs MCP**: Daily audio market briefings

## Key Features

### Investment Analysis
- Comprehensive multi-source analysis for any stock
- Real-time sentiment tracking from social media
- Deep fundamental analysis with peer comparison
- ML-powered technical analysis and price prediction
- External trend correlation analysis

### Risk Management
- Position sizing based on portfolio risk
- Maximum drawdown limits (15% monthly)
- Portfolio correlation monitoring
- Human override for large positions (>$10K)
- Real-time risk scoring

### Trading Modes
- **Swing Trading**: 2-10 day positions
- **Value Investing**: Long-term fundamental plays
- **Momentum**: Trend-following strategies
- **Arbitrage**: Market inefficiency detection
- **Risk-Off**: Defensive positioning

## Quick Start

### 1. Initialize Database
```bash
python init_market_oracle_database.py
```

### 2. Start MCP Server
```bash
uv run a2a-mcp --run mcp-server --transport sse --host localhost --port 10100
```

### 3. Launch Agents
```bash
# Oracle Prime Orchestrator
uv run src/a2a_mcp/agents/ --agent-card agent_cards/oracle_prime_agent.json --port 10501

# Sentiment Seeker
uv run src/a2a_mcp/agents/ --agent-card agent_cards/sentiment_seeker_agent.json --port 10502

# Fundamental Analyst
uv run src/a2a_mcp/agents/ --agent-card agent_cards/fundamental_analyst_agent.json --port 10503

# ... launch remaining agents on ports 10504-10508
```

### 4. Run Demo
```bash
python demo_market_oracle.py
```

## Usage Examples

### Basic Investment Analysis
```python
# Query Oracle Prime for investment recommendation
response = await oracle_prime.stream(
    "Should I invest in TSLA?",
    context_id="session_123",
    task_id="task_001"
)
```

### Response Structure
```json
{
    "recommendation": {
        "executive_summary": "Tesla shows strong momentum but elevated risk",
        "investment_recommendation": "BUY",
        "confidence_score": 0.75,
        "position_size": "3%",
        "risk_assessment": {
            "risk_score": 65,
            "key_risks": ["valuation", "competition"],
            "mitigation_strategies": ["position sizing", "stop loss"]
        }
    },
    "market_intelligence": {
        "sentiment": {"score": 0.82, "volume": "extreme"},
        "fundamentals": {"pe_ratio": 45.2, "revenue_growth": 0.23},
        "technical": {"trend": "bullish", "rsi": 72}
    }
}
```

## Database Schema

### Core Tables
- `portfolios`: User portfolios and balances
- `positions`: Current and historical positions
- `trading_signals`: Agent-generated signals
- `sentiment_data`: Social media sentiment tracking
- `risk_metrics`: Portfolio risk calculations
- `investment_research`: Detailed analysis documentation

## Security & Compliance

### Built-in Safeguards
- API key encryption (AES-256)
- JWT authentication between agents
- Complete audit trail
- Rate limiting on external APIs
- Human approval for large trades

## Performance Metrics

### Target KPIs
- Sharpe Ratio: >1.5 annually
- Win Rate: >55% on trades
- Maximum Drawdown: <15% monthly
- Signal Accuracy: >70%
- System Uptime: 99.9%

## Deployment

### Production Setup
```yaml
# docker-compose.yml
version: '3.8'
services:
  oracle-prime:
    image: market-oracle/oracle-prime:latest
    ports:
      - "10501:10501"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - REDDIT_CLIENT_ID=${REDDIT_CLIENT_ID}
      - BRIGHTDATA_API_KEY=${BRIGHTDATA_API_KEY}
```

### Scaling Options
- Horizontal: Add crypto, forex, commodities agents
- Vertical: Increase ML model complexity
- Geographic: Multi-region deployment

## Roadmap

### Phase 1 (Current)
- ✅ Core 8-agent architecture
- ✅ Basic MCP integrations
- ✅ Risk management framework
- ✅ Demo implementation

### Phase 2
- [ ] Real broker API integration
- [ ] Advanced ML models (Transformers)
- [ ] Live paper trading
- [ ] Performance dashboard

### Phase 3
- [ ] Multi-asset support (crypto, forex)
- [ ] Options strategies
- [ ] Automated backtesting
- [ ] Mobile app integration

## Contributing

Market Oracle is part of the A2A-MCP framework. Contributions should follow the established patterns for agent development and MCP integration.

## License

This implementation is for educational and research purposes. Always conduct your own due diligence before making investment decisions.