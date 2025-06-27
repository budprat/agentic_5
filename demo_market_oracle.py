#!/usr/bin/env python3
"""Demo script for Market Oracle investment intelligence system."""

import asyncio
import json
from datetime import datetime

# Import our Market Oracle agents
from src.a2a_mcp.agents.market_oracle import (
    OraclePrimeAgent,
    SentimentSeekerAgent,
    FundamentalAnalystAgent
)

async def demo_oracle_prime():
    """Demonstrate Oracle Prime orchestrator capabilities."""
    print("\n" + "="*50)
    print("MARKET ORACLE - Investment Intelligence Demo")
    print("="*50 + "\n")
    
    # Initialize Oracle Prime
    oracle = OraclePrimeAgent()
    
    # Example queries
    queries = [
        "Should I invest in TSLA given current market conditions?",
        "Analyze AAPL for a long-term investment",
        "What's the investment opportunity in NVDA?"
    ]
    
    for query in queries:
        print(f"\n🤖 Query: {query}")
        print("-" * 40)
        
        # Stream the analysis
        async for response in oracle.stream(query, "demo_session", "task_001"):
            if response.get('is_task_complete'):
                if response.get('response_type') == 'data':
                    data = response['content']
                    
                    # Display recommendation
                    if 'recommendation' in data:
                        rec = data['recommendation']
                        print(f"\n📊 Investment Recommendation: {rec.get('investment_recommendation', 'N/A')}")
                        print(f"📈 Confidence Score: {rec.get('confidence_score', 0):.2f}")
                        print(f"💰 Position Size: {rec.get('position_size', 'N/A')}")
                        print(f"\n💡 Executive Summary:")
                        print(f"   {rec.get('executive_summary', 'N/A')}")
                        
                        # Risk assessment
                        risk = rec.get('risk_assessment', {})
                        print(f"\n⚠️  Risk Assessment:")
                        print(f"   - Risk Score: {risk.get('risk_score', 0)}/100")
                        print(f"   - Key Risks: {', '.join(risk.get('key_risks', []))}")
                        
                        # Entry/Exit strategy
                        entry = rec.get('entry_strategy', {})
                        exit_strat = rec.get('exit_strategy', {})
                        print(f"\n📍 Entry Strategy:")
                        print(f"   - Entry Price: {entry.get('entry_price', 'N/A')}")
                        print(f"   - Timing: {entry.get('timing', 'N/A')}")
                        print(f"\n🎯 Exit Strategy:")
                        print(f"   - Target Price: {exit_strat.get('target_price', 'N/A')}")
                        print(f"   - Stop Loss: {exit_strat.get('stop_loss', 'N/A')}")
                        print(f"   - Time Horizon: {exit_strat.get('time_horizon', 'N/A')}")
                    
                    # Risk validation
                    if 'risk_validation' in data:
                        risk_val = data['risk_validation']
                        print(f"\n✅ Risk Validation:")
                        print(f"   - Approved: {'Yes' if risk_val.get('approved') else 'No'}")
                        if risk_val.get('requires_human'):
                            print(f"   - ⚠️  Human Override Required!")
                        
                        checks = risk_val.get('checks', {})
                        for check, passed in checks.items():
                            status = "✓" if passed else "✗"
                            print(f"   - {status} {check.replace('_', ' ').title()}")
                else:
                    print(f"\n📝 {response['content']}")
            else:
                # Progress update
                print(f"⏳ {response['content']}")
        
        print("\n" + "-"*40)
        
        # Wait before next query
        await asyncio.sleep(2)

async def demo_sentiment_analysis():
    """Demonstrate Sentiment Seeker capabilities."""
    print("\n\n" + "="*50)
    print("SENTIMENT ANALYSIS DEMO")
    print("="*50 + "\n")
    
    sentiment_agent = SentimentSeekerAgent()
    
    query = "What is the Reddit sentiment on TSLA?"
    print(f"🔍 Analyzing: {query}")
    
    async for response in sentiment_agent.stream(query, "demo_session", "task_002"):
        if response.get('is_task_complete'):
            if response.get('response_type') == 'data':
                data = response['content']
                
                print(f"\n📊 Sentiment Analysis Results:")
                print(f"   - Symbol: {data.get('symbol', 'N/A')}")
                print(f"   - Sentiment Score: {data.get('sentiment_score', 0):.2f} (-1 to +1)")
                print(f"   - Confidence: {data.get('confidence', 0):.2f}")
                print(f"   - Volume: {data.get('volume_score', 'N/A')}")
                print(f"   - Recommendation: {data.get('recommendation', 'N/A')}")
                
                if 'risk_flags' in data and data['risk_flags']:
                    print(f"\n⚠️  Risk Flags:")
                    for flag in data['risk_flags']:
                        print(f"   - {flag.replace('_', ' ').title()}")
                
                print(f"\n💬 Analysis Summary:")
                print(f"   {data.get('analysis_summary', 'N/A')}")
        else:
            print(f"⏳ {response['content']}")

async def demo_fundamental_analysis():
    """Demonstrate Fundamental Analyst capabilities."""
    print("\n\n" + "="*50)
    print("FUNDAMENTAL ANALYSIS DEMO")
    print("="*50 + "\n")
    
    fundamental_agent = FundamentalAnalystAgent()
    
    query = "Analyze Apple's fundamentals"
    print(f"📈 Analyzing: {query}")
    
    async for response in fundamental_agent.stream(query, "demo_session", "task_003"):
        if response.get('is_task_complete'):
            if response.get('response_type') == 'data':
                data = response['content']
                
                print(f"\n📊 Fundamental Analysis:")
                print(f"   - Symbol: {data.get('symbol', 'N/A')}")
                print(f"   - Company: {data.get('company_name', 'N/A')}")
                print(f"   - Fundamental Score: {data.get('fundamental_score', 0):.2f}")
                
                # Financial metrics
                metrics = data.get('financial_metrics', {})
                if metrics:
                    print(f"\n📈 Key Financial Metrics:")
                    print(f"   - P/E Ratio: {metrics.get('pe_ratio', 'N/A')}")
                    print(f"   - Revenue Growth: {metrics.get('revenue_growth_yoy', 0)*100:.1f}%")
                    print(f"   - Net Margin: {metrics.get('net_margin', 0)*100:.1f}%")
                    print(f"   - Debt/Equity: {metrics.get('debt_to_equity', 'N/A')}")
                
                # Investment thesis
                print(f"\n💡 Investment Thesis:")
                print(f"   {data.get('investment_thesis', 'N/A')}")
                
                # Strengths and weaknesses
                if 'strengths' in data:
                    print(f"\n✅ Strengths:")
                    for strength in data['strengths']:
                        print(f"   - {strength}")
                
                if 'weaknesses' in data:
                    print(f"\n❌ Weaknesses:")
                    for weakness in data['weaknesses']:
                        print(f"   - {weakness}")
        else:
            print(f"⏳ {response['content']}")

async def main():
    """Run all Market Oracle demos."""
    print("\n🚀 Starting Market Oracle Demo...\n")
    
    # Demo Oracle Prime orchestrator
    await demo_oracle_prime()
    
    # Demo individual agents
    await demo_sentiment_analysis()
    await demo_fundamental_analysis()
    
    print("\n\n✅ Market Oracle Demo Complete!")
    print("\nThe system demonstrates:")
    print("- Multi-agent coordination for investment analysis")
    print("- Risk management and position sizing")
    print("- Social sentiment analysis from Reddit")
    print("- Fundamental analysis with financial metrics")
    print("- Comprehensive investment recommendations")
    
    print("\n📌 Next Steps:")
    print("1. Deploy agents on their respective ports (10501-10508)")
    print("2. Configure MCP connections for live data")
    print("3. Connect to real trading APIs")
    print("4. Implement ML models for price prediction")
    print("5. Set up real-time monitoring dashboards")

if __name__ == "__main__":
    asyncio.run(main())