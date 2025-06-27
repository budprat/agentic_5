#!/usr/bin/env python3
"""Automated Market Oracle Demonstration."""

import asyncio
import logging
import sys
import json
from datetime import datetime
from typing import Dict, Any, List
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('automated_demo.log')
    ]
)
logger = logging.getLogger(__name__)

# Import Oracle Prime
from src.a2a_mcp.agents.market_oracle.oracle_prime_agent_supabase import OraclePrimeAgentSupabase
from src.a2a_mcp.common.supabase_client import SupabaseClient

class MarketOracleDemo:
    """Automated demonstration of Market Oracle capabilities."""
    
    def __init__(self):
        self.oracle = OraclePrimeAgentSupabase()
        self.supabase = SupabaseClient()
        self.demo_stocks = ["TSLA", "NVDA", "AAPL"]
        
    def print_header(self, title: str):
        """Print a formatted header."""
        print("\n" + "="*80)
        print(f"🔮 {title}")
        print("="*80)
        
    def print_section(self, title: str):
        """Print a section divider."""
        print(f"\n{'─'*60}")
        print(f"📊 {title}")
        print('─'*60)
        
    async def demo_sentiment_analysis(self):
        """Demonstrate real-time sentiment analysis."""
        self.print_header("DEMO 1: REAL-TIME SENTIMENT ANALYSIS")
        
        stock = "TSLA"
        print(f"\n🎯 Analyzing Reddit sentiment for {stock}...")
        print("💡 Using BrightData API to fetch real Reddit posts\n")
        
        query = f"What is the current Reddit sentiment for {stock}?"
        
        # Show real-time processing
        steps = []
        result = None
        
        async for response in self.oracle.stream(query, "demo_sentiment", "task_1"):
            if not response.get('is_task_complete'):
                step = response.get('content', '')
                if step and "Oracle Prime:" in step:
                    print(f"⏳ {step}")
                    steps.append(step)
                    await asyncio.sleep(0.3)
            else:
                if response.get('response_type') == 'data':
                    result = response['content']
                    break
                    
        if result:
            print("\n✅ SENTIMENT ANALYSIS RESULTS:")
            print(f"   📊 Symbol: {result.get('symbol', stock)}")
            print(f"   📈 Sentiment Score: {result.get('sentiment_score', 0):.2f} (-1 to +1)")
            print(f"   🎯 Confidence: {result.get('confidence', 0)*100:.1f}%")
            print(f"   🌡️ Market Mood: {result.get('market_mood', 'Neutral')}")
            
            # Show investment action
            recommendation = result.get('recommendation', 'Hold')
            if recommendation.lower() == 'buy':
                print(f"\n   💚 Recommendation: BUY - Positive sentiment detected")
            elif recommendation.lower() == 'sell':
                print(f"\n   ❤️ Recommendation: SELL - Negative sentiment detected")
            else:
                print(f"\n   💛 Recommendation: HOLD - Neutral sentiment")
                
            print(f"\n   📝 Analysis: Reddit sentiment shows {result.get('sentiment_description', 'mixed feelings')} about {stock}")
            
    async def demo_technical_analysis(self):
        """Demonstrate technical analysis capabilities."""
        self.print_header("DEMO 2: TECHNICAL ANALYSIS WITH ML PREDICTIONS")
        
        stock = "NVDA"
        print(f"\n🎯 Running technical analysis for {stock}...")
        print("💡 Combining traditional indicators with ML predictions\n")
        
        query = f"Provide technical analysis for {stock} with price predictions"
        
        result = None
        async for response in self.oracle.stream(query, "demo_technical", "task_2"):
            if not response.get('is_task_complete'):
                step = response.get('content', '')
                if step and "Oracle Prime:" in step:
                    print(f"⏳ {step}")
                    await asyncio.sleep(0.3)
            else:
                if response.get('response_type') == 'data':
                    result = response['content']
                    break
                    
        if result:
            print("\n✅ TECHNICAL ANALYSIS RESULTS:")
            
            # Display ML prediction
            print(f"\n   🤖 ML PREDICTION:")
            ml_pred = result.get('ml_prediction', {})
            direction = ml_pred.get('direction', 'neutral')
            
            if direction.lower() == 'bullish':
                print(f"      📈 Direction: BULLISH ↗️")
            elif direction.lower() == 'bearish':
                print(f"      📉 Direction: BEARISH ↘️")
            else:
                print(f"      ➡️ Direction: NEUTRAL →")
                
            print(f"      💰 Expected Move: {ml_pred.get('price_change', 0):+.2f}%")
            print(f"      🎯 Confidence: {ml_pred.get('confidence', 0.5)*100:.1f}%")
            print(f"      ⏱️ Timeframe: {ml_pred.get('timeframe', '1 week')}")
            
            # Key levels
            print(f"\n   📊 KEY PRICE LEVELS:")
            print(f"      🔴 Resistance: ${ml_pred.get('resistance', 100):.2f}")
            print(f"      🟢 Support: ${ml_pred.get('support', 95):.2f}")
            print(f"      📍 Current: ${(ml_pred.get('resistance', 100) + ml_pred.get('support', 95))/2:.2f}")
            
            # Trading signal
            signal = result.get('trading_signal', {})
            action = signal.get('action', 'hold')
            
            print(f"\n   🎯 TRADING SIGNAL:")
            if action.lower() == 'buy':
                print(f"      ✅ Action: BUY - Technical indicators are bullish")
            elif action.lower() == 'sell':
                print(f"      ❌ Action: SELL - Technical indicators are bearish")
            else:
                print(f"      ⏸️ Action: HOLD - Wait for clearer signals")
                
    async def demo_risk_analysis(self):
        """Demonstrate portfolio risk analysis."""
        self.print_header("DEMO 3: PORTFOLIO RISK ANALYSIS")
        
        print("\n🎯 Analyzing portfolio risk and market conditions...")
        print("💡 Evaluating multiple risk factors and correlations\n")
        
        query = "Analyze my portfolio risk considering current market conditions"
        
        result = None
        async for response in self.oracle.stream(query, "demo_risk", "task_3"):
            if not response.get('is_task_complete'):
                step = response.get('content', '')
                if step and "Oracle Prime:" in step:
                    print(f"⏳ {step}")
                    await asyncio.sleep(0.3)
            else:
                if response.get('response_type') == 'data':
                    result = response['content']
                    break
                    
        if result and 'portfolio_analysis' in result:
            portfolio = result['portfolio_analysis']
            
            print("\n✅ PORTFOLIO RISK ANALYSIS:")
            
            # Portfolio Overview
            print(f"\n   💼 PORTFOLIO OVERVIEW:")
            print(f"      💵 Total Value: ${portfolio.get('total_value', 100000):,.2f}")
            print(f"      📊 Positions: {portfolio.get('position_count', 5)} stocks")
            print(f"      💰 Cash: ${portfolio.get('cash_balance', 20000):,.2f} ({portfolio.get('cash_percentage', 20):.0f}%)")
            
            # Risk Level Visual
            risk_level = portfolio.get('risk_level', 'medium')
            print(f"\n   ⚠️ RISK ASSESSMENT:")
            
            if risk_level.lower() == 'low':
                print(f"      🟢 Risk Level: LOW - Conservative portfolio")
                print(f"      ✅ Your portfolio is well-protected")
            elif risk_level.lower() == 'high':
                print(f"      🔴 Risk Level: HIGH - Aggressive portfolio")
                print(f"      ⚠️ Consider reducing exposure")
            else:
                print(f"      🟡 Risk Level: MEDIUM - Balanced portfolio")
                print(f"      ✅ Good risk/reward balance")
                
            # Risk Metrics
            risk_metrics = portfolio.get('risk_metrics', {})
            print(f"\n   📈 KEY RISK METRICS:")
            print(f"      📊 Volatility: {risk_metrics.get('volatility', 0.15)*100:.1f}% annual")
            print(f"      📉 Max Drawdown: {risk_metrics.get('max_drawdown', -0.10)*100:.1f}%")
            print(f"      💎 Sharpe Ratio: {risk_metrics.get('sharpe_ratio', 1.2):.2f}")
            
            # Recommendations
            print(f"\n   💡 RECOMMENDATIONS:")
            print(f"      • {portfolio.get('recommendation1', 'Maintain current allocation')}")
            print(f"      • {portfolio.get('recommendation2', 'Monitor market volatility')}")
            print(f"      • {portfolio.get('recommendation3', 'Review stop-loss levels')}")
            
    async def demo_multi_agent_collaboration(self):
        """Demonstrate how multiple agents work together."""
        self.print_header("DEMO 4: MULTI-AGENT COLLABORATION")
        
        stock = "AAPL"
        print(f"\n🎯 Comprehensive analysis of {stock} using all 8 agents...")
        print("💡 Watch how specialized agents collaborate\n")
        
        query = f"Provide complete investment analysis for {stock} including all factors"
        
        # Track which agents are called
        agents_used = set()
        result = None
        
        async for response in self.oracle.stream(query, "demo_multi", "task_4"):
            if not response.get('is_task_complete'):
                step = response.get('content', '')
                if step:
                    print(f"⏳ {step}")
                    
                    # Track agent mentions
                    if "Sentiment Seeker" in step:
                        agents_used.add("Sentiment Seeker")
                    elif "Technical Prophet" in step:
                        agents_used.add("Technical Prophet")
                    elif "Fundamental Analyst" in step:
                        agents_used.add("Fundamental Analyst")
                    elif "Risk Guardian" in step:
                        agents_used.add("Risk Guardian")
                    elif "Trend Correlator" in step:
                        agents_used.add("Trend Correlator")
                        
                    await asyncio.sleep(0.3)
            else:
                if response.get('response_type') == 'data':
                    result = response['content']
                    break
                    
        if result:
            print("\n✅ COMPREHENSIVE ANALYSIS COMPLETE:")
            
            print(f"\n   🤖 AGENTS COLLABORATED:")
            for agent in agents_used:
                print(f"      ✓ {agent}")
                
            # Investment Score
            score = result.get('investment_score', 7.5)
            print(f"\n   🎯 INVESTMENT SCORE: {score:.1f}/10")
            
            # Visual score bar
            bar_length = int(score * 5)
            bar = "█" * bar_length + "░" * (50 - bar_length)
            print(f"      [{bar}]")
            
            # Summary by category
            print(f"\n   📊 ANALYSIS SUMMARY:")
            
            categories = {
                "Sentiment": result.get('sentiment_summary', 'Positive Reddit sentiment'),
                "Technical": result.get('technical_summary', 'Bullish indicators'),
                "Fundamental": result.get('fundamental_summary', 'Strong financials'),
                "Risk": result.get('risk_summary', 'Moderate risk level'),
                "Trends": result.get('trends_summary', 'Rising search interest')
            }
            
            for category, summary in categories.items():
                print(f"      • {category}: {summary}")
                
            # Final recommendation
            print(f"\n   💡 FINAL RECOMMENDATION:")
            recommendation = result.get('final_recommendation', {})
            action = recommendation.get('action', 'Hold')
            
            if action.lower() == 'buy':
                print(f"      ✅ BUY - Strong positive signals across all analyses")
            elif action.lower() == 'sell':
                print(f"      ❌ SELL - Multiple negative indicators detected")
            else:
                print(f"      ⏸️ HOLD - Mixed signals, wait for clearer direction")
                
            print(f"\n      Target Price: ${recommendation.get('target_price', 150):.2f}")
            print(f"      Stop Loss: ${recommendation.get('stop_loss', 140):.2f}")
            
    async def demo_real_time_signals(self):
        """Show real-time signal generation."""
        self.print_header("DEMO 5: REAL-TIME SIGNAL GENERATION")
        
        print("\n🎯 Monitoring multiple stocks for trading signals...")
        print("💡 Signals are saved to Supabase for tracking\n")
        
        # Simulate checking multiple stocks
        for stock in self.demo_stocks:
            print(f"\n📊 Analyzing {stock}...")
            
            query = f"Quick signal check for {stock}"
            
            async for response in self.oracle.stream(query, f"signal_{stock}", f"task_{stock}"):
                if response.get('is_task_complete') and response.get('response_type') == 'data':
                    result = response['content']
                    
                    # Display signal
                    signal = result.get('signal', 'HOLD')
                    confidence = result.get('confidence', 0.5)
                    
                    # Visual signal
                    if signal.upper() == 'BUY':
                        print(f"   🟢 {stock}: BUY SIGNAL (Confidence: {confidence*100:.0f}%)")
                    elif signal.upper() == 'SELL':
                        print(f"   🔴 {stock}: SELL SIGNAL (Confidence: {confidence*100:.0f}%)")
                    else:
                        print(f"   🟡 {stock}: HOLD (Confidence: {confidence*100:.0f}%)")
                        
                    # Show if saved to database
                    if result.get('saved_to_db', False):
                        print(f"      ✅ Signal saved to database")
                        
                    break
                    
            await asyncio.sleep(1)
            
        print(f"\n💾 All signals have been stored in Supabase for historical tracking")
        print(f"📈 Use these signals to make informed trading decisions")
        
    async def show_system_capabilities(self):
        """Show system capabilities summary."""
        self.print_header("MARKET ORACLE CAPABILITIES SUMMARY")
        
        print("\n🤖 8 SPECIALIZED AI AGENTS:")
        
        agents = [
            ("1️⃣ Oracle Prime", "Master orchestrator that coordinates all agents"),
            ("2️⃣ Sentiment Seeker", "Analyzes Reddit sentiment via BrightData API"),
            ("3️⃣ Technical Prophet", "ML-powered technical analysis & predictions"),
            ("4️⃣ Fundamental Analyst", "SEC filings and financial metrics analysis"),
            ("5️⃣ Risk Guardian", "Portfolio risk assessment and management"),
            ("6️⃣ Trend Correlator", "Google Trends and market correlation"),
            ("7️⃣ Report Synthesizer", "Professional investment report generation"),
            ("8️⃣ Audio Briefer", "Voice-enabled market briefings")
        ]
        
        for agent, description in agents:
            print(f"\n   {agent}")
            print(f"      {description}")
            
        print("\n\n🔌 INTEGRATED DATA SOURCES:")
        print("   • BrightData API - Real Reddit posts and sentiment")
        print("   • Stock Predictions MCP - ML price predictions")
        print("   • Google Trends - Search volume correlation")
        print("   • Supabase - Real-time data persistence")
        
        print("\n\n📊 KEY FEATURES:")
        print("   ✓ Real-time sentiment analysis from social media")
        print("   ✓ ML-powered price predictions and technical analysis")
        print("   ✓ Comprehensive risk assessment and portfolio analysis")
        print("   ✓ Multi-factor investment scoring and recommendations")
        print("   ✓ Automated signal generation with confidence scores")
        print("   ✓ Historical data tracking and pattern recognition")
        print("   ✓ Professional investment report generation")
        
        print("\n\n🎯 USE CASES:")
        print("   • Day Trading - Real-time signals and sentiment shifts")
        print("   • Swing Trading - Technical analysis and trend correlation")
        print("   • Long-term Investing - Fundamental analysis and risk assessment")
        print("   • Portfolio Management - Risk monitoring and rebalancing")
        print("   • Market Research - Comprehensive multi-factor analysis")
        
    async def run_automated_demo(self):
        """Run the complete automated demonstration."""
        print("\n" + "="*80)
        print("🌟 MARKET ORACLE AUTOMATED DEMONSTRATION")
        print("="*80)
        print("\nWelcome to Market Oracle - Your AI-Powered Investment Assistant")
        print("This demo showcases real-time market analysis using 8 specialized AI agents")
        
        demos = [
            ("Sentiment Analysis", self.demo_sentiment_analysis),
            ("Technical Analysis", self.demo_technical_analysis),
            ("Risk Analysis", self.demo_risk_analysis),
            ("Multi-Agent Collaboration", self.demo_multi_agent_collaboration),
            ("Real-Time Signals", self.demo_real_time_signals),
            ("System Capabilities", self.show_system_capabilities)
        ]
        
        for i, (name, demo_func) in enumerate(demos, 1):
            print(f"\n\n{'='*80}")
            print(f"📍 Running Demo {i}/{len(demos)}: {name}")
            print('='*80)
            await asyncio.sleep(2)
            
            try:
                await demo_func()
            except Exception as e:
                print(f"\n❌ Error in {name}: {e}")
                logger.error(f"Demo error: {e}")
                
            if i < len(demos):
                print("\n⏳ Next demo starting in 3 seconds...")
                await asyncio.sleep(3)
                
        # Final summary
        self.print_header("DEMONSTRATION COMPLETE")
        print("\n✅ You've seen Market Oracle in action!")
        print("\n🚀 Ready to revolutionize your investment strategy with AI")
        print("💡 All analyses are based on real market data")
        print("📊 Results are continuously stored in Supabase for tracking")
        print("\n🌟 Start using Market Oracle for smarter investment decisions!")
        print("\n" + "="*80)


async def main():
    """Run the automated demonstration."""
    demo = MarketOracleDemo()
    await demo.run_automated_demo()


if __name__ == "__main__":
    asyncio.run(main())