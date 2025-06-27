#!/usr/bin/env python3
"""Interactive Market Oracle Demonstration."""

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
        logging.FileHandler('interactive_demo.log')
    ]
)
logger = logging.getLogger(__name__)

# Import Oracle Prime
from src.a2a_mcp.agents.market_oracle.oracle_prime_agent_supabase import OraclePrimeAgentSupabase
from src.a2a_mcp.common.supabase_client import SupabaseClient

class MarketOracleDemo:
    """Interactive demonstration of Market Oracle capabilities."""
    
    def __init__(self):
        self.oracle = OraclePrimeAgentSupabase()
        self.supabase = SupabaseClient()
        self.demo_stocks = ["TSLA", "NVDA", "AAPL", "MSFT", "META"]
        
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
        self.print_header("REAL-TIME SENTIMENT ANALYSIS")
        
        stock = "TSLA"
        print(f"\n🎯 Analyzing Reddit sentiment for {stock}...")
        print("This uses BrightData API to fetch real Reddit posts\n")
        
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
                    await asyncio.sleep(0.5)  # Visual delay
            else:
                if response.get('response_type') == 'data':
                    result = response['content']
                    break
                    
        if result:
            print("\n✅ SENTIMENT ANALYSIS RESULTS:")
            print(f"   Symbol: {result.get('symbol', stock)}")
            print(f"   Sentiment Score: {result.get('sentiment_score', 0):.2f} (-1 to +1)")
            print(f"   Confidence: {result.get('confidence', 0)*100:.1f}%")
            print(f"   Market Mood: {result.get('market_mood', 'Unknown')}")
            
            # Show actual Reddit data
            if 'reddit_highlights' in result:
                print("\n   📱 Top Reddit Posts:")
                for i, post in enumerate(result['reddit_highlights'][:3], 1):
                    print(f"      {i}. {post.get('title', 'No title')}")
                    print(f"         Upvotes: {post.get('upvotes', 0):,}")
                    
            print(f"\n   💡 Recommendation: {result.get('recommendation', 'Hold')}")
            
    async def demo_technical_analysis(self):
        """Demonstrate technical analysis capabilities."""
        self.print_header("TECHNICAL ANALYSIS WITH ML PREDICTIONS")
        
        stock = "NVDA"
        print(f"\n🎯 Running technical analysis for {stock}...")
        print("This combines traditional indicators with ML predictions\n")
        
        query = f"Provide technical analysis for {stock} with price predictions"
        
        result = None
        async for response in self.oracle.stream(query, "demo_technical", "task_2"):
            if not response.get('is_task_complete'):
                step = response.get('content', '')
                if step and "Oracle Prime:" in step:
                    print(f"⏳ {step}")
                    await asyncio.sleep(0.5)
            else:
                if response.get('response_type') == 'data':
                    result = response['content']
                    break
                    
        if result:
            print("\n✅ TECHNICAL ANALYSIS RESULTS:")
            
            # ML Predictions
            if 'ml_prediction' in result:
                ml = result['ml_prediction']
                print(f"\n   🤖 ML Prediction:")
                print(f"      Direction: {ml.get('direction', 'Unknown').upper()}")
                print(f"      Expected Move: {ml.get('price_change', 0):+.2f}%")
                print(f"      Confidence: {ml.get('confidence', 0)*100:.1f}%")
                print(f"      Timeframe: {ml.get('timeframe', 'Unknown')}")
                
            # Technical Indicators
            if 'technical_indicators' in result:
                tech = result['technical_indicators']
                print(f"\n   📈 Technical Indicators:")
                print(f"      RSI: {tech.get('rsi', 0):.1f}")
                print(f"      MACD: {tech.get('macd_signal', 'Unknown')}")
                print(f"      Support: ${tech.get('support', 0):.2f}")
                print(f"      Resistance: ${tech.get('resistance', 0):.2f}")
                
            # Trading Signal
            if 'trading_signal' in result:
                signal = result['trading_signal']
                print(f"\n   🎯 Trading Signal: {signal.get('action', 'Hold').upper()}")
                print(f"      Strength: {signal.get('strength', 'Unknown')}")
                
    async def demo_risk_analysis(self):
        """Demonstrate portfolio risk analysis."""
        self.print_header("PORTFOLIO RISK ANALYSIS")
        
        print("\n🎯 Analyzing portfolio risk and market conditions...")
        print("This evaluates multiple risk factors and correlations\n")
        
        query = "Analyze my portfolio risk considering current market conditions"
        
        result = None
        async for response in self.oracle.stream(query, "demo_risk", "task_3"):
            if not response.get('is_task_complete'):
                step = response.get('content', '')
                if step and "Oracle Prime:" in step:
                    print(f"⏳ {step}")
                    await asyncio.sleep(0.5)
            else:
                if response.get('response_type') == 'data':
                    result = response['content']
                    break
                    
        if result and 'portfolio_analysis' in result:
            portfolio = result['portfolio_analysis']
            
            print("\n✅ PORTFOLIO RISK ANALYSIS:")
            
            # Portfolio Overview
            print(f"\n   💼 Portfolio Overview:")
            print(f"      Total Value: ${portfolio.get('total_value', 0):,.2f}")
            print(f"      Number of Positions: {portfolio.get('position_count', 0)}")
            print(f"      Cash Balance: ${portfolio.get('cash_balance', 0):,.2f}")
            
            # Risk Metrics
            if 'risk_metrics' in portfolio:
                risk = portfolio['risk_metrics']
                print(f"\n   ⚠️  Risk Metrics:")
                print(f"      Portfolio Beta: {risk.get('beta', 0):.2f}")
                print(f"      Volatility: {risk.get('volatility', 0)*100:.1f}%")
                print(f"      VaR (95%): ${risk.get('value_at_risk', 0):,.2f}")
                print(f"      Sharpe Ratio: {risk.get('sharpe_ratio', 0):.2f}")
                
            # Risk Assessment
            print(f"\n   🎯 Risk Level: {portfolio.get('risk_level', 'Unknown').upper()}")
            print(f"      Diversification: {portfolio.get('diversification_score', 'Unknown')}")
            
    async def demo_market_trends(self):
        """Demonstrate trend correlation analysis."""
        self.print_header("MARKET TREND CORRELATION")
        
        stock = "AAPL"
        print(f"\n🎯 Analyzing search trends correlation for {stock}...")
        print("This correlates Google Trends with stock movements\n")
        
        query = f"Analyze trend correlation for {stock}"
        
        result = None
        async for response in self.oracle.stream(query, "demo_trends", "task_4"):
            if not response.get('is_task_complete'):
                step = response.get('content', '')
                if step and "Oracle Prime:" in step:
                    print(f"⏳ {step}")
                    await asyncio.sleep(0.5)
            else:
                if response.get('response_type') == 'data':
                    result = response['content']
                    break
                    
        if result and 'trend_analysis' in result:
            trends = result['trend_analysis']
            
            print("\n✅ TREND CORRELATION RESULTS:")
            print(f"   Symbol: {stock}")
            
            # Search Terms
            if 'search_terms' in trends:
                print(f"\n   🔍 Search Terms Analyzed:")
                for term, data in trends['search_terms'].items():
                    print(f"      '{term}': Volume {data.get('volume', 0)}, Trend {data.get('trend', 'Unknown')}")
                    
            # Correlation
            print(f"\n   📊 Correlation Metrics:")
            print(f"      Correlation Coefficient: {trends.get('correlation', 0):.3f}")
            print(f"      Lead/Lag: {trends.get('lead_lag_days', 0)} days")
            print(f"      Predictive Power: {trends.get('predictive_power', 'Unknown')}")
            
    async def demo_comprehensive_report(self):
        """Demonstrate comprehensive investment report generation."""
        self.print_header("COMPREHENSIVE INVESTMENT REPORT")
        
        stock = "META"
        print(f"\n🎯 Generating full investment report for {stock}...")
        print("This combines all agent analyses into a professional report\n")
        
        query = f"Generate a comprehensive investment report for {stock}"
        
        result = None
        async for response in self.oracle.stream(query, "demo_report", "task_5"):
            if not response.get('is_task_complete'):
                step = response.get('content', '')
                if step and "Oracle Prime:" in step:
                    print(f"⏳ {step}")
                    await asyncio.sleep(0.5)
            else:
                if response.get('response_type') == 'data':
                    result = response['content']
                    break
                    
        if result:
            print("\n✅ INVESTMENT REPORT GENERATED:")
            print(f"\n   📄 {stock} - Investment Analysis Report")
            print(f"   {'─'*50}")
            
            # Executive Summary
            if 'executive_summary' in result:
                print(f"\n   📋 Executive Summary:")
                summary = result['executive_summary']
                print(f"      Overall Rating: {summary.get('rating', 'Unknown')}")
                print(f"      Investment Thesis: {summary.get('thesis', 'No thesis available')}")
                
            # Key Metrics
            if 'key_metrics' in result:
                print(f"\n   📊 Key Metrics:")
                metrics = result['key_metrics']
                for key, value in metrics.items():
                    print(f"      {key}: {value}")
                    
            # Recommendations
            if 'recommendations' in result:
                print(f"\n   💡 Recommendations:")
                recs = result['recommendations']
                print(f"      Action: {recs.get('action', 'Hold').upper()}")
                print(f"      Target Price: ${recs.get('target_price', 0):.2f}")
                print(f"      Stop Loss: ${recs.get('stop_loss', 0):.2f}")
                
    async def demo_multi_stock_comparison(self):
        """Demonstrate multi-stock comparison."""
        self.print_header("MULTI-STOCK COMPARISON")
        
        stocks = ["TSLA", "NVDA", "AAPL"]
        print(f"\n🎯 Comparing multiple stocks: {', '.join(stocks)}")
        print("This provides side-by-side analysis for investment decisions\n")
        
        query = f"Compare investment opportunities between {', '.join(stocks)}"
        
        result = None
        async for response in self.oracle.stream(query, "demo_compare", "task_6"):
            if not response.get('is_task_complete'):
                step = response.get('content', '')
                if step and "Oracle Prime:" in step:
                    print(f"⏳ {step}")
                    await asyncio.sleep(0.5)
            else:
                if response.get('response_type') == 'data':
                    result = response['content']
                    break
                    
        if result and 'comparison' in result:
            comparison = result['comparison']
            
            print("\n✅ STOCK COMPARISON RESULTS:")
            print(f"\n   {'Stock':<10} {'Signal':<10} {'Sentiment':<12} {'Risk':<10} {'Score':<10}")
            print(f"   {'-'*52}")
            
            for stock_data in comparison:
                symbol = stock_data.get('symbol', 'Unknown')
                signal = stock_data.get('signal', 'Hold')
                sentiment = f"{stock_data.get('sentiment', 0):+.2f}"
                risk = stock_data.get('risk', 'Medium')
                score = f"{stock_data.get('score', 0):.1f}/10"
                
                print(f"   {symbol:<10} {signal:<10} {sentiment:<12} {risk:<10} {score:<10}")
                
            # Best Pick
            if 'best_pick' in result:
                print(f"\n   🏆 Best Investment: {result['best_pick']['symbol']}")
                print(f"      Reason: {result['best_pick']['reason']}")
                
    async def show_portfolio_performance(self):
        """Show real portfolio performance from database."""
        self.print_header("PORTFOLIO PERFORMANCE TRACKING")
        
        print("\n📊 Fetching real portfolio data from Supabase...")
        
        try:
            # Get portfolio data
            portfolios = await self.supabase.get_portfolios(user_id="demo_user")
            
            if portfolios:
                portfolio = portfolios[0]
                print(f"\n✅ Portfolio: {portfolio['name']}")
                print(f"   Total Value: ${portfolio['total_value']:,.2f}")
                print(f"   Cash Balance: ${portfolio['cash_balance']:,.2f}")
                
                # Get positions
                positions = await self.supabase.get_positions(portfolio['id'])
                if positions:
                    print(f"\n   📈 Current Positions:")
                    print(f"   {'Symbol':<10} {'Shares':<10} {'Entry':<10} {'Current':<10} {'P&L':<12} {'%':<8}")
                    print(f"   {'-'*60}")
                    
                    for pos in positions[:5]:  # Show top 5
                        symbol = pos['symbol']
                        shares = pos['quantity']
                        entry = f"${pos['entry_price']:.2f}"
                        current = f"${pos.get('current_price', pos['entry_price']):.2f}"
                        pnl = pos.get('unrealized_pnl', 0)
                        pnl_pct = pos.get('unrealized_pnl_percentage', 0)
                        
                        pnl_str = f"${pnl:+,.2f}" if pnl != 0 else "$0.00"
                        pct_str = f"{pnl_pct:+.1f}%" if pnl_pct != 0 else "0.0%"
                        
                        print(f"   {symbol:<10} {shares:<10} {entry:<10} {current:<10} {pnl_str:<12} {pct_str:<8}")
                        
                # Get recent signals
                signals = await self.supabase.get_latest_signals(limit=5)
                if signals:
                    print(f"\n   🎯 Recent Trading Signals:")
                    for signal in signals:
                        time_str = datetime.fromisoformat(signal['created_at'].replace('Z', '+00:00')).strftime("%H:%M")
                        print(f"      {time_str} - {signal['symbol']}: {signal['signal_type'].upper()} "
                              f"(Confidence: {signal['confidence_score']*100:.0f}%)")
                        
        except Exception as e:
            logger.error(f"Error fetching portfolio data: {e}")
            print(f"   ❌ Error: {e}")
            
    async def run_interactive_demo(self):
        """Run the complete interactive demonstration."""
        print("\n" + "="*80)
        print("🌟 MARKET ORACLE INTERACTIVE DEMONSTRATION")
        print("="*80)
        print("\nWelcome to Market Oracle - Your AI-Powered Investment Assistant")
        print("This demo showcases real-time market analysis using multiple specialized agents")
        
        demos = [
            ("Sentiment Analysis", self.demo_sentiment_analysis),
            ("Technical Analysis", self.demo_technical_analysis),
            ("Risk Analysis", self.demo_risk_analysis),
            ("Trend Correlation", self.demo_market_trends),
            ("Investment Report", self.demo_comprehensive_report),
            ("Multi-Stock Comparison", self.demo_multi_stock_comparison),
            ("Portfolio Performance", self.show_portfolio_performance)
        ]
        
        for i, (name, demo_func) in enumerate(demos, 1):
            print(f"\n🔸 Demo {i}/{len(demos)}: {name}")
            input("Press Enter to continue...")
            
            try:
                await demo_func()
            except Exception as e:
                print(f"\n❌ Error in {name}: {e}")
                logger.error(f"Demo error: {e}")
                
            if i < len(demos):
                print("\n" + "─"*60)
                await asyncio.sleep(2)
                
        # Final summary
        self.print_header("DEMONSTRATION COMPLETE")
        print("\n✅ Market Oracle Features Demonstrated:")
        print("   • Real-time Reddit sentiment analysis via BrightData")
        print("   • ML-powered price predictions")
        print("   • Technical indicator analysis")
        print("   • Portfolio risk assessment")
        print("   • Google Trends correlation")
        print("   • Comprehensive investment reports")
        print("   • Multi-stock comparison")
        print("   • Real-time signal generation")
        print("\n🚀 All data is stored in Supabase for historical tracking")
        print("💡 The system uses 8 specialized AI agents working together")
        print("\n" + "="*80)


async def main():
    """Run the interactive demonstration."""
    demo = MarketOracleDemo()
    await demo.run_interactive_demo()


if __name__ == "__main__":
    asyncio.run(main())