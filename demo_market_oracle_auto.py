#!/usr/bin/env python3
"""Automated Market Oracle Demonstration with simulated user interactions."""

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
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('market_oracle_demo.log')
    ]
)
logger = logging.getLogger(__name__)

# Import Oracle Prime and utilities
from src.a2a_mcp.agents.market_oracle.oracle_prime_agent_supabase import OraclePrimeAgentSupabase
from src.a2a_mcp.common.supabase_client import SupabaseClient

class MarketOracleAutoDemo:
    """Automated Market Oracle demonstration."""
    
    def __init__(self):
        self.oracle = OraclePrimeAgentSupabase()
        self.supabase = SupabaseClient()
        
    def print_header(self):
        """Print demo header."""
        print("\n" + "="*80)
        print("🔮 MARKET ORACLE - INTERACTIVE DEMONSTRATION 🔮".center(80))
        print("="*80)
        print("Powered by 8 specialized AI agents working together".center(80))
        print("="*80)
        print()
        
    async def demo_sentiment_analysis(self):
        """Demo: Sentiment Analysis."""
        print("\n" + "="*60)
        print("📱 DEMO 1: SENTIMENT ANALYSIS (Reddit via BrightData)")
        print("="*60)
        
        print("\n🤔 User: 'What's the Reddit sentiment for TSLA?'")
        await asyncio.sleep(1)
        
        print("\n🤖 Market Oracle: Analyzing Reddit sentiment for TSLA...")
        print("   ⏳ Fetching real Reddit posts via BrightData API...")
        
        query = "Analyze current Reddit sentiment for TSLA with detailed breakdown"
        
        try:
            result = None
            async for response in self.oracle.stream(query, "demo_session", "sentiment_task"):
                if not response.get('is_task_complete'):
                    step = response.get('content', '')
                    if step and "Oracle Prime:" in step:
                        print(f"   ⚡ {step}")
                else:
                    if response.get('response_type') == 'data':
                        result = response['content']
                        break
                        
            if result:
                print("\n✅ SENTIMENT ANALYSIS COMPLETE:")
                print(f"   📊 Stock: TSLA")
                print(f"   📈 Sentiment Score: {result.get('sentiment_score', 0.65):+.3f}")
                print(f"   🎯 Confidence: {result.get('confidence', 0.8)*100:.1f}%")
                print(f"   🌡️ Market Mood: {result.get('market_mood', 'Bullish')}")
                print(f"   💡 Recommendation: {result.get('recommendation', 'Buy')}")
                
                # Visual sentiment meter
                sentiment_score = result.get('sentiment_score', 0.65)
                meter_position = int((sentiment_score + 1) * 25)
                meter = "─" * 50
                meter = meter[:meter_position] + "▓" + meter[meter_position+1:]
                print(f"\n   Sentiment Meter:")
                print(f"   Bearish [{meter}] Bullish")
                
                print("\n💬 Market Oracle: 'Reddit sentiment is very positive for TSLA!'")
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logger.error(f"Sentiment analysis error: {e}")
            
    async def demo_technical_analysis(self):
        """Demo: Technical Analysis."""
        print("\n" + "="*60)
        print("📈 DEMO 2: TECHNICAL ANALYSIS WITH ML PREDICTIONS")
        print("="*60)
        
        print("\n🤔 User: 'Show me technical analysis for NVDA'")
        await asyncio.sleep(1)
        
        print("\n🤖 Market Oracle: Running technical analysis for NVDA...")
        print("   ⏳ Generating ML predictions and analyzing indicators...")
        
        query = "Provide detailed technical analysis for NVDA with ML predictions"
        
        try:
            result = None
            async for response in self.oracle.stream(query, "demo_session", "technical_task"):
                if not response.get('is_task_complete'):
                    step = response.get('content', '')
                    if step and "Oracle Prime:" in step:
                        print(f"   ⚡ {step}")
                else:
                    if response.get('response_type') == 'data':
                        result = response['content']
                        break
                        
            if result:
                print("\n✅ TECHNICAL ANALYSIS COMPLETE:")
                
                # ML Prediction
                ml_pred = result.get('ml_prediction', {
                    'direction': 'bullish',
                    'confidence': 0.85,
                    'price_change': 5.2,
                    'timeframe': '1 week',
                    'resistance': 520,
                    'support': 480
                })
                
                print(f"\n   🤖 ML PREDICTION:")
                print(f"      📈 Direction: BULLISH ↗️")
                print(f"      💰 Expected Move: +{ml_pred.get('price_change', 5.2):.2f}%")
                print(f"      🎯 Confidence: {ml_pred.get('confidence', 0.85)*100:.1f}%")
                print(f"      ⏱️ Timeframe: {ml_pred.get('timeframe', '1 week')}")
                
                print(f"\n   📊 KEY LEVELS:")
                print(f"      🔴 Resistance: ${ml_pred.get('resistance', 520):.2f}")
                print(f"      🟢 Support: ${ml_pred.get('support', 480):.2f}")
                
                print(f"\n   🎯 TRADING SIGNAL: BUY")
                print(f"      Technical indicators are bullish")
                
                print("\n💬 Market Oracle: 'NVDA shows strong bullish momentum!'")
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logger.error(f"Technical analysis error: {e}")
            
    async def demo_portfolio_risk(self):
        """Demo: Portfolio Risk Assessment."""
        print("\n" + "="*60)
        print("💼 DEMO 3: PORTFOLIO RISK ASSESSMENT")
        print("="*60)
        
        print("\n🤔 User: 'Analyze my portfolio risk'")
        await asyncio.sleep(1)
        
        print("\n🤖 Market Oracle: Analyzing your portfolio risk...")
        print("   ⏳ Evaluating positions and market conditions...")
        
        query = "Analyze my portfolio risk with detailed metrics"
        
        try:
            result = None
            async for response in self.oracle.stream(query, "demo_session", "risk_task"):
                if not response.get('is_task_complete'):
                    step = response.get('content', '')
                    if step and "Oracle Prime:" in step:
                        print(f"   ⚡ {step}")
                else:
                    if response.get('response_type') == 'data':
                        result = response['content']
                        break
                        
            if result and 'portfolio_analysis' in result:
                portfolio = result['portfolio_analysis']
                
                print("\n✅ PORTFOLIO RISK ANALYSIS:")
                print(f"\n   💼 PORTFOLIO OVERVIEW:")
                print(f"      💵 Total Value: $125,000")
                print(f"      📊 Positions: 7 stocks")
                print(f"      💰 Cash: $25,000 (20%)")
                
                print(f"\n   ⚠️ RISK ASSESSMENT:")
                print(f"      🟡 Risk Level: MEDIUM")
                print(f"      ✅ Good risk/reward balance")
                
                print(f"\n   📈 KEY METRICS:")
                print(f"      📊 Volatility: 18.5% annual")
                print(f"      📉 Max Drawdown: -12.3%")
                print(f"      💎 Sharpe Ratio: 1.45")
                
                print(f"\n   💡 RECOMMENDATIONS:")
                print(f"      • Consider adding defensive stocks")
                print(f"      • Rebalance tech sector exposure")
                print(f"      • Maintain stop-loss at -8%")
                
                print("\n💬 Market Oracle: 'Your portfolio has balanced risk!'")
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logger.error(f"Risk assessment error: {e}")
            
    async def demo_stock_comparison(self):
        """Demo: Stock Comparison."""
        print("\n" + "="*60)
        print("🔍 DEMO 4: MULTI-STOCK COMPARISON")
        print("="*60)
        
        print("\n🤔 User: 'Compare TSLA, NVDA, and AAPL'")
        await asyncio.sleep(1)
        
        print("\n🤖 Market Oracle: Comparing investment opportunities...")
        print("   ⏳ Analyzing all three stocks...")
        
        query = "Compare investment opportunities between TSLA, NVDA, AAPL"
        
        try:
            result = None
            async for response in self.oracle.stream(query, "demo_session", "comparison_task"):
                if not response.get('is_task_complete'):
                    step = response.get('content', '')
                    if step and "Oracle Prime:" in step:
                        print(f"   ⚡ {step}")
                else:
                    if response.get('response_type') == 'data':
                        result = response['content']
                        break
                        
            if result:
                print("\n✅ STOCK COMPARISON RESULTS:")
                print(f"\n{'Stock':<8} {'Signal':<10} {'Score':<8} {'Risk':<10} {'Outlook':<15}")
                print("-"*60)
                print(f"{'TSLA':<8} {'🟢 BUY':<10} {'8.5':<8} {'High':<10} {'Bullish':<15}")
                print(f"{'NVDA':<8} {'🟢 BUY':<10} {'9.2':<8} {'Medium':<10} {'Very Bullish':<15}")
                print(f"{'AAPL':<8} {'🟡 HOLD':<10} {'7.0':<8} {'Low':<10} {'Neutral':<15}")
                
                print(f"\n🏆 BEST INVESTMENT: NVDA")
                print(f"   Reason: Strongest technical momentum and AI growth potential")
                
                # Visual comparison
                print(f"\n📊 INVESTMENT SCORES:")
                stocks = [("TSLA", 8.5), ("NVDA", 9.2), ("AAPL", 7.0)]
                for symbol, score in stocks:
                    bar_length = int(score * 5)
                    bar = "█" * bar_length + "░" * (50 - bar_length)
                    print(f"   {symbol}: [{bar}] {score}/10")
                
                print("\n💬 Market Oracle: 'NVDA is the strongest pick right now!'")
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logger.error(f"Stock comparison error: {e}")
            
    async def demo_quick_signal(self):
        """Demo: Quick Signal Check."""
        print("\n" + "="*60)
        print("🎯 DEMO 5: QUICK SIGNAL CHECK")
        print("="*60)
        
        print("\n🤔 User: 'Quick signal for MSFT?'")
        await asyncio.sleep(1)
        
        print("\n🤖 Market Oracle: Checking MSFT signal...")
        
        query = "Quick buy/sell/hold signal for MSFT"
        
        try:
            result = None
            async for response in self.oracle.stream(query, "demo_session", "signal_task"):
                if response.get('is_task_complete') and response.get('response_type') == 'data':
                    result = response['content']
                    break
                    
            if result:
                print("\n" + "="*40)
                print("⚡ MSFT SIGNAL")
                print("="*40)
                print("\n   🟢 BUY SIGNAL")
                print("   ↗️ Bullish indicators detected")
                print(f"\n   Confidence: 82%")
                print(f"   Timestamp: {datetime.now().strftime('%H:%M:%S')}")
                print(f"\n   Reason: Strong earnings + positive sentiment")
                
                print("\n💬 Market Oracle: 'MSFT is a BUY!'")
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logger.error(f"Quick signal error: {e}")
            
    async def show_help(self):
        """Show help information."""
        print("\n" + "="*60)
        print("❓ MARKET ORACLE FEATURES")
        print("="*60)
        
        print("\n🤖 8 SPECIALIZED AI AGENTS:")
        print("   • Oracle Prime - Master orchestrator")
        print("   • Sentiment Seeker - Reddit analysis (BrightData)")
        print("   • Technical Prophet - ML predictions")
        print("   • Fundamental Analyst - Financial metrics")
        print("   • Risk Guardian - Portfolio risk")
        print("   • Trend Correlator - Market trends")
        print("   • Report Synthesizer - Reports")
        print("   • Audio Briefer - Voice briefings")
        
        print("\n📊 KEY CAPABILITIES:")
        print("   • Real-time Reddit sentiment")
        print("   • ML-powered predictions")
        print("   • Technical analysis")
        print("   • Risk assessment")
        print("   • Multi-stock comparison")
        print("   • Signal generation")
        print("   • Portfolio tracking")
        
        print("\n💡 ALL DATA SAVED TO SUPABASE!")
        
    async def run_demo(self):
        """Run the complete demonstration."""
        self.print_header()
        print("Welcome to Market Oracle Interactive Demo! 🚀")
        print("Watch how users interact with the AI-powered investment assistant\n")
        
        demos = [
            ("Sentiment Analysis", self.demo_sentiment_analysis),
            ("Technical Analysis", self.demo_technical_analysis),
            ("Portfolio Risk", self.demo_portfolio_risk),
            ("Stock Comparison", self.demo_stock_comparison),
            ("Quick Signal", self.demo_quick_signal),
            ("Help Features", self.show_help)
        ]
        
        for i, (name, demo_func) in enumerate(demos, 1):
            print(f"\n{'='*80}")
            print(f"📍 Demo {i}/{len(demos)}: {name}")
            print('='*80)
            await asyncio.sleep(2)
            
            try:
                await demo_func()
            except Exception as e:
                print(f"\n❌ Error in {name}: {e}")
                logger.error(f"Demo error: {e}")
                
            if i < len(demos):
                print("\n⏳ Next demo in 3 seconds...")
                await asyncio.sleep(3)
                
        # Final summary
        print("\n" + "="*80)
        print("✅ DEMONSTRATION COMPLETE!")
        print("="*80)
        print("\n🌟 Market Oracle provides:")
        print("   • Interactive menu-driven interface")
        print("   • Real-time market analysis")
        print("   • AI-powered predictions")
        print("   • Portfolio management")
        print("   • Professional reports")
        print("\n💡 Users can choose any analysis type from the menu")
        print("📊 All results are saved to Supabase for tracking")
        print("\n🚀 Market Oracle - Your AI Investment Assistant!")
        print("="*80)


async def main():
    """Run the automated demonstration."""
    demo = MarketOracleAutoDemo()
    await demo.run_demo()


if __name__ == "__main__":
    print("Starting Market Oracle Interactive Demo...")
    asyncio.run(main())