#!/usr/bin/env python3
"""Interactive Market Oracle - Real-time market analysis with user input."""

import asyncio
import logging
import sys
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('interactive_oracle.log')
    ]
)
logger = logging.getLogger(__name__)

# Import Oracle Prime and utilities
from src.a2a_mcp.agents.market_oracle.oracle_prime_agent_supabase import OraclePrimeAgentSupabase
from src.a2a_mcp.common.supabase_client import SupabaseClient

class InteractiveMarketOracle:
    """Interactive Market Oracle interface."""
    
    def __init__(self):
        self.oracle = OraclePrimeAgentSupabase()
        self.supabase = SupabaseClient()
        self.session_id = f"interactive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.popular_stocks = ["TSLA", "NVDA", "AAPL", "MSFT", "GOOGL", "META", "AMZN"]
        
    def clear_screen(self):
        """Clear the terminal screen."""
        print("\033[2J\033[H")
        
    def print_header(self):
        """Print the Market Oracle header."""
        self.clear_screen()
        print("="*80)
        print("🔮 MARKET ORACLE - AI-POWERED INVESTMENT ASSISTANT 🔮".center(80))
        print("="*80)
        print("Powered by 8 specialized AI agents working together".center(80))
        print("="*80)
        print()
        
    def print_menu(self):
        """Display the main menu."""
        print("\n📊 MAIN MENU:")
        print("-"*50)
        print("1. 📱 Sentiment Analysis (Reddit via BrightData)")
        print("2. 📈 Technical Analysis (with ML predictions)")
        print("3. 💼 Portfolio Risk Assessment")
        print("4. 🔍 Stock Comparison (multiple stocks)")
        print("5. 📄 Investment Report (comprehensive)")
        print("6. 🎯 Quick Signal Check")
        print("7. 📊 View My Portfolio")
        print("8. 🔄 Market Trends Analysis")
        print("9. ❓ Help - How to use Market Oracle")
        print("0. 🚪 Exit")
        print("-"*50)
        
    async def get_user_input(self, prompt: str) -> str:
        """Get user input asynchronously."""
        return await asyncio.get_event_loop().run_in_executor(None, input, prompt)
        
    async def sentiment_analysis(self):
        """Interactive sentiment analysis."""
        self.print_header()
        print("📱 SENTIMENT ANALYSIS - Reddit Data via BrightData")
        print("="*80)
        
        print("\nPopular stocks:", ", ".join(self.popular_stocks))
        stock = await self.get_user_input("\nEnter stock symbol (e.g., TSLA): ")
        stock = stock.upper().strip()
        
        if not stock:
            print("❌ Invalid input. Returning to menu...")
            await asyncio.sleep(2)
            return
            
        print(f"\n🔍 Analyzing Reddit sentiment for {stock}...")
        print("⏳ Fetching real Reddit posts via BrightData API...\n")
        
        query = f"Analyze current Reddit sentiment for {stock} with detailed breakdown"
        
        try:
            result = None
            async for response in self.oracle.stream(query, self.session_id, f"sentiment_{stock}"):
                if not response.get('is_task_complete'):
                    step = response.get('content', '')
                    if step and "Oracle Prime:" in step:
                        print(f"   {step}")
                else:
                    if response.get('response_type') == 'data':
                        result = response['content']
                        break
                        
            if result:
                print("\n" + "="*60)
                print("✅ SENTIMENT ANALYSIS RESULTS")
                print("="*60)
                
                # Extract key metrics
                sentiment_score = result.get('sentiment_score', 0)
                confidence = result.get('confidence', 0.5)
                
                # Visual sentiment meter
                print(f"\n📊 {stock} SENTIMENT METER:")
                meter_position = int((sentiment_score + 1) * 25)  # Convert -1 to 1 into 0-50
                meter = "─" * 50
                meter = meter[:meter_position] + "▓" + meter[meter_position+1:]
                print(f"   Bearish [{meter}] Bullish")
                print(f"   Score: {sentiment_score:+.3f} (Confidence: {confidence*100:.1f}%)")
                
                # Sentiment interpretation
                if sentiment_score > 0.5:
                    print("\n   💚 VERY BULLISH - Strong positive sentiment")
                elif sentiment_score > 0.2:
                    print("\n   🟢 BULLISH - Positive sentiment")
                elif sentiment_score > -0.2:
                    print("\n   🟡 NEUTRAL - Mixed sentiment")
                elif sentiment_score > -0.5:
                    print("\n   🟠 BEARISH - Negative sentiment")
                else:
                    print("\n   🔴 VERY BEARISH - Strong negative sentiment")
                    
                # Additional insights
                print(f"\n📝 Market Mood: {result.get('market_mood', 'Unknown')}")
                print(f"💡 Recommendation: {result.get('recommendation', 'Hold')}")
                
                if 'key_themes' in result:
                    print(f"\n🔑 Key Themes Detected:")
                    for theme in result.get('key_themes', [])[:5]:
                        print(f"   • {theme}")
                        
                print(f"\n📅 Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logger.error(f"Sentiment analysis error: {e}")
            
        await self.get_user_input("\nPress Enter to continue...")
        
    async def technical_analysis(self):
        """Interactive technical analysis."""
        self.print_header()
        print("📈 TECHNICAL ANALYSIS - ML-Powered Predictions")
        print("="*80)
        
        print("\nPopular stocks:", ", ".join(self.popular_stocks))
        stock = await self.get_user_input("\nEnter stock symbol (e.g., NVDA): ")
        stock = stock.upper().strip()
        
        if not stock:
            print("❌ Invalid input. Returning to menu...")
            await asyncio.sleep(2)
            return
            
        print(f"\n🔍 Running technical analysis for {stock}...")
        print("⏳ Generating ML predictions and indicators...\n")
        
        query = f"Provide detailed technical analysis for {stock} with ML predictions and key levels"
        
        try:
            result = None
            async for response in self.oracle.stream(query, self.session_id, f"technical_{stock}"):
                if not response.get('is_task_complete'):
                    step = response.get('content', '')
                    if step and "Oracle Prime:" in step:
                        print(f"   {step}")
                else:
                    if response.get('response_type') == 'data':
                        result = response['content']
                        break
                        
            if result:
                print("\n" + "="*60)
                print("✅ TECHNICAL ANALYSIS RESULTS")
                print("="*60)
                
                # ML Prediction
                ml_pred = result.get('ml_prediction', {})
                direction = ml_pred.get('direction', 'neutral')
                confidence = ml_pred.get('confidence', 0.5)
                price_change = ml_pred.get('price_change', 0)
                
                print(f"\n🤖 ML PREDICTION FOR {stock}:")
                print(f"   Direction: ", end="")
                if direction.lower() == 'bullish':
                    print("📈 BULLISH ↗️")
                elif direction.lower() == 'bearish':
                    print("📉 BEARISH ↘️")
                else:
                    print("➡️ NEUTRAL →")
                    
                print(f"   Expected Move: {price_change:+.2f}%")
                print(f"   Confidence: {confidence*100:.1f}%")
                print(f"   Timeframe: {ml_pred.get('timeframe', '1 week')}")
                
                # Key Levels
                print(f"\n📊 KEY PRICE LEVELS:")
                resistance = ml_pred.get('resistance', 100)
                support = ml_pred.get('support', 95)
                current = (resistance + support) / 2
                
                print(f"   🔴 Resistance: ${resistance:.2f}")
                print(f"   📍 Current: ${current:.2f}")
                print(f"   🟢 Support: ${support:.2f}")
                
                # Visual price range
                range_size = resistance - support
                current_pos = int(((current - support) / range_size) * 30)
                price_bar = "─" * 30
                price_bar = price_bar[:current_pos] + "●" + price_bar[current_pos+1:]
                print(f"\n   Price Range: [{price_bar}]")
                print(f"                 ${support:.2f}     ${resistance:.2f}")
                
                # Trading Signal
                signal = result.get('trading_signal', {})
                action = signal.get('action', 'hold')
                
                print(f"\n🎯 TRADING SIGNAL:")
                if action.lower() == 'buy':
                    print("   ✅ BUY - Technical indicators are bullish")
                elif action.lower() == 'sell':
                    print("   ❌ SELL - Technical indicators are bearish")
                else:
                    print("   ⏸️ HOLD - Wait for clearer signals")
                    
                # Technical Indicators
                if 'indicators' in result:
                    print(f"\n📐 TECHNICAL INDICATORS:")
                    indicators = result['indicators']
                    print(f"   RSI: {indicators.get('rsi', 50):.1f}")
                    print(f"   MACD: {indicators.get('macd_signal', 'Neutral')}")
                    print(f"   Moving Averages: {indicators.get('ma_signal', 'Neutral')}")
                    
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logger.error(f"Technical analysis error: {e}")
            
        await self.get_user_input("\nPress Enter to continue...")
        
    async def portfolio_risk(self):
        """Interactive portfolio risk assessment."""
        self.print_header()
        print("💼 PORTFOLIO RISK ASSESSMENT")
        print("="*80)
        
        print("\n🔍 Analyzing your portfolio risk...")
        print("⏳ Evaluating positions and market conditions...\n")
        
        query = "Analyze my portfolio risk with detailed metrics and recommendations"
        
        try:
            result = None
            async for response in self.oracle.stream(query, self.session_id, "risk_assessment"):
                if not response.get('is_task_complete'):
                    step = response.get('content', '')
                    if step and "Oracle Prime:" in step:
                        print(f"   {step}")
                else:
                    if response.get('response_type') == 'data':
                        result = response['content']
                        break
                        
            if result and 'portfolio_analysis' in result:
                portfolio = result['portfolio_analysis']
                
                print("\n" + "="*60)
                print("✅ PORTFOLIO RISK ANALYSIS")
                print("="*60)
                
                # Portfolio Overview
                print(f"\n💼 PORTFOLIO OVERVIEW:")
                print(f"   Total Value: ${portfolio.get('total_value', 100000):,.2f}")
                print(f"   Positions: {portfolio.get('position_count', 5)} stocks")
                print(f"   Cash: ${portfolio.get('cash_balance', 20000):,.2f}")
                
                # Risk Level Visual
                risk_level = portfolio.get('risk_level', 'medium').lower()
                print(f"\n⚠️ RISK ASSESSMENT:")
                
                # Risk meter
                risk_levels = ['low', 'medium', 'high']
                risk_index = risk_levels.index(risk_level) if risk_level in risk_levels else 1
                risk_meter = ["🟢", "🟡", "🔴"]
                
                print(f"   Risk Level: {risk_meter[risk_index]} {risk_level.upper()}")
                print(f"   [{'█' * (risk_index + 1)}{'░' * (2 - risk_index)}]")
                
                # Risk Metrics
                if 'risk_metrics' in portfolio:
                    metrics = portfolio['risk_metrics']
                    print(f"\n📊 RISK METRICS:")
                    print(f"   Beta: {metrics.get('beta', 1.0):.2f}")
                    print(f"   Volatility: {metrics.get('volatility', 0.15)*100:.1f}%")
                    print(f"   Sharpe Ratio: {metrics.get('sharpe_ratio', 1.0):.2f}")
                    print(f"   Max Drawdown: {metrics.get('max_drawdown', -0.10)*100:.1f}%")
                    
                # Diversification
                print(f"\n🎯 DIVERSIFICATION:")
                div_score = portfolio.get('diversification_score', 'Good')
                print(f"   Score: {div_score}")
                
                # Recommendations
                print(f"\n💡 RECOMMENDATIONS:")
                for i, rec in enumerate(portfolio.get('recommendations', [])[:3], 1):
                    print(f"   {i}. {rec}")
                    
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logger.error(f"Risk assessment error: {e}")
            
        await self.get_user_input("\nPress Enter to continue...")
        
    async def stock_comparison(self):
        """Compare multiple stocks."""
        self.print_header()
        print("🔍 STOCK COMPARISON - Multi-Stock Analysis")
        print("="*80)
        
        print("\nEnter 2-5 stock symbols separated by commas")
        print("Example: TSLA, NVDA, AAPL")
        
        stocks_input = await self.get_user_input("\nEnter stocks: ")
        stocks = [s.strip().upper() for s in stocks_input.split(',') if s.strip()]
        
        if len(stocks) < 2:
            print("❌ Please enter at least 2 stocks. Returning to menu...")
            await asyncio.sleep(2)
            return
            
        print(f"\n🔍 Comparing {', '.join(stocks)}...")
        print("⏳ Analyzing all stocks...\n")
        
        query = f"Compare investment opportunities between {', '.join(stocks)} with scores"
        
        try:
            result = None
            async for response in self.oracle.stream(query, self.session_id, "comparison"):
                if not response.get('is_task_complete'):
                    step = response.get('content', '')
                    if step and "Oracle Prime:" in step:
                        print(f"   {step}")
                else:
                    if response.get('response_type') == 'data':
                        result = response['content']
                        break
                        
            if result and 'comparison' in result:
                comparison = result['comparison']
                
                print("\n" + "="*60)
                print("✅ STOCK COMPARISON RESULTS")
                print("="*60)
                
                # Comparison table
                print(f"\n{'Stock':<8} {'Signal':<10} {'Score':<8} {'Risk':<10} {'Outlook':<15}")
                print("-"*60)
                
                for stock_data in comparison:
                    symbol = stock_data.get('symbol', 'N/A')
                    signal = stock_data.get('signal', 'Hold')
                    score = stock_data.get('score', 5.0)
                    risk = stock_data.get('risk', 'Medium')
                    outlook = stock_data.get('outlook', 'Neutral')
                    
                    # Signal color
                    if signal.lower() == 'buy':
                        signal_str = "🟢 BUY"
                    elif signal.lower() == 'sell':
                        signal_str = "🔴 SELL"
                    else:
                        signal_str = "🟡 HOLD"
                        
                    print(f"{symbol:<8} {signal_str:<10} {score:<8.1f} {risk:<10} {outlook:<15}")
                    
                # Best pick
                if 'best_pick' in result:
                    best = result['best_pick']
                    print(f"\n🏆 BEST INVESTMENT: {best['symbol']}")
                    print(f"   Reason: {best['reason']}")
                    
                # Visual comparison
                print(f"\n📊 INVESTMENT SCORES:")
                for stock_data in comparison:
                    symbol = stock_data.get('symbol', 'N/A')
                    score = stock_data.get('score', 5.0)
                    bar_length = int(score * 5)
                    bar = "█" * bar_length + "░" * (50 - bar_length)
                    print(f"   {symbol}: [{bar}] {score:.1f}/10")
                    
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logger.error(f"Stock comparison error: {e}")
            
        await self.get_user_input("\nPress Enter to continue...")
        
    async def quick_signal(self):
        """Quick signal check for a stock."""
        self.print_header()
        print("🎯 QUICK SIGNAL CHECK")
        print("="*80)
        
        stock = await self.get_user_input("\nEnter stock symbol: ")
        stock = stock.upper().strip()
        
        if not stock:
            print("❌ Invalid input. Returning to menu...")
            await asyncio.sleep(2)
            return
            
        print(f"\n⚡ Quick signal check for {stock}...\n")
        
        query = f"Quick buy/sell/hold signal for {stock}"
        
        try:
            result = None
            async for response in self.oracle.stream(query, self.session_id, f"signal_{stock}"):
                if response.get('is_task_complete') and response.get('response_type') == 'data':
                    result = response['content']
                    break
                    
            if result:
                signal = result.get('signal', 'HOLD')
                confidence = result.get('confidence', 0.5)
                
                print("\n" + "="*40)
                print(f"⚡ {stock} SIGNAL")
                print("="*40)
                
                if signal.upper() == 'BUY':
                    print("\n   🟢 BUY SIGNAL")
                    print("   ↗️ Bullish indicators detected")
                elif signal.upper() == 'SELL':
                    print("\n   🔴 SELL SIGNAL")
                    print("   ↘️ Bearish indicators detected")
                else:
                    print("\n   🟡 HOLD SIGNAL")
                    print("   → No clear direction")
                    
                print(f"\n   Confidence: {confidence*100:.0f}%")
                print(f"   Timestamp: {datetime.now().strftime('%H:%M:%S')}")
                
                if result.get('reason'):
                    print(f"\n   Reason: {result['reason']}")
                    
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logger.error(f"Quick signal error: {e}")
            
        await self.get_user_input("\nPress Enter to continue...")
        
    async def view_portfolio(self):
        """View current portfolio."""
        self.print_header()
        print("📊 MY PORTFOLIO")
        print("="*80)
        
        print("\n⏳ Loading portfolio data...\n")
        
        try:
            # Get portfolio data
            portfolios = await self.supabase.get_portfolios(user_id="demo_user")
            
            if portfolios:
                portfolio = portfolios[0]
                print(f"Portfolio: {portfolio['name']}")
                print(f"Total Value: ${portfolio['total_value']:,.2f}")
                print(f"Cash Balance: ${portfolio['cash_balance']:,.2f}")
                
                # Get positions
                positions = await self.supabase.get_positions(portfolio['id'])
                
                if positions:
                    print(f"\n📈 CURRENT POSITIONS:")
                    print(f"{'Symbol':<8} {'Shares':<10} {'Entry':<12} {'Current':<12} {'P&L':<15}")
                    print("-"*70)
                    
                    total_pnl = 0
                    for pos in positions:
                        symbol = pos['symbol']
                        shares = pos['quantity']
                        entry = pos['entry_price']
                        current = pos.get('current_price', entry)
                        pnl = (current - entry) * shares
                        pnl_pct = ((current - entry) / entry) * 100
                        total_pnl += pnl
                        
                        pnl_str = f"${pnl:+,.2f} ({pnl_pct:+.1f}%)"
                        
                        print(f"{symbol:<8} {shares:<10} ${entry:<11.2f} ${current:<11.2f} {pnl_str:<15}")
                        
                    print("-"*70)
                    print(f"{'TOTAL':<8} {'':<10} {'':<12} {'':<12} ${total_pnl:+,.2f}")
                    
                # Recent signals
                print(f"\n🎯 RECENT SIGNALS:")
                signals = await self.supabase.get_latest_signals(limit=5)
                
                for signal in signals:
                    time_str = datetime.fromisoformat(signal['created_at'].replace('Z', '+00:00')).strftime("%H:%M")
                    signal_icon = "🟢" if signal['signal_type'] == 'buy' else "🔴" if signal['signal_type'] == 'sell' else "🟡"
                    print(f"   {time_str} - {signal_icon} {signal['symbol']}: {signal['signal_type'].upper()} ({signal['confidence_score']*100:.0f}%)")
                    
            else:
                print("No portfolio found.")
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logger.error(f"Portfolio view error: {e}")
            
        await self.get_user_input("\nPress Enter to continue...")
        
    async def show_help(self):
        """Show help information."""
        self.print_header()
        print("❓ HOW TO USE MARKET ORACLE")
        print("="*80)
        
        print("\n🤖 ABOUT MARKET ORACLE:")
        print("   Market Oracle uses 8 specialized AI agents to analyze markets:")
        print("   • Oracle Prime - Orchestrates all analyses")
        print("   • Sentiment Seeker - Reddit sentiment via BrightData")
        print("   • Technical Prophet - ML-powered predictions")
        print("   • Fundamental Analyst - Financial metrics")
        print("   • Risk Guardian - Portfolio risk assessment")
        print("   • Trend Correlator - Market trends analysis")
        print("   • Report Synthesizer - Investment reports")
        print("   • Audio Briefer - Voice briefings")
        
        print("\n📊 KEY FEATURES:")
        print("   • Real-time Reddit sentiment analysis")
        print("   • ML-powered price predictions")
        print("   • Technical indicator analysis")
        print("   • Portfolio risk assessment")
        print("   • Multi-stock comparison")
        print("   • Professional investment reports")
        
        print("\n💡 TIPS:")
        print("   • Use sentiment analysis to gauge market mood")
        print("   • Combine technical + sentiment for better signals")
        print("   • Check portfolio risk regularly")
        print("   • Compare multiple stocks before investing")
        print("   • All data is saved to track performance")
        
        print("\n🎯 SIGNAL MEANINGS:")
        print("   🟢 BUY - Strong positive indicators")
        print("   🔴 SELL - Strong negative indicators")
        print("   🟡 HOLD - Mixed or unclear signals")
        
        await self.get_user_input("\nPress Enter to continue...")
        
    async def run_interactive(self):
        """Run the interactive Market Oracle."""
        self.print_header()
        print("Welcome to Market Oracle! 🚀")
        print("Your AI-powered investment assistant is ready.\n")
        
        while True:
            self.print_menu()
            
            try:
                choice = await self.get_user_input("\nSelect option (0-9): ")
                
                if choice == '0':
                    print("\n👋 Thank you for using Market Oracle!")
                    print("May your investments prosper! 💰")
                    break
                elif choice == '1':
                    await self.sentiment_analysis()
                elif choice == '2':
                    await self.technical_analysis()
                elif choice == '3':
                    await self.portfolio_risk()
                elif choice == '4':
                    await self.stock_comparison()
                elif choice == '5':
                    # Investment report
                    stock = await self.get_user_input("\nEnter stock for report: ")
                    stock = stock.upper().strip()
                    if stock:
                        print(f"\n⏳ Generating comprehensive report for {stock}...")
                        query = f"Generate comprehensive investment report for {stock}"
                        async for response in self.oracle.stream(query, self.session_id, f"report_{stock}"):
                            if not response.get('is_task_complete'):
                                step = response.get('content', '')
                                if step:
                                    print(f"   {step}")
                            else:
                                print("\n✅ Report generated and saved to database!")
                                break
                        await self.get_user_input("\nPress Enter to continue...")
                elif choice == '6':
                    await self.quick_signal()
                elif choice == '7':
                    await self.view_portfolio()
                elif choice == '8':
                    # Market trends
                    stock = await self.get_user_input("\nEnter stock for trends: ")
                    stock = stock.upper().strip()
                    if stock:
                        print(f"\n⏳ Analyzing trends for {stock}...")
                        query = f"Analyze search trends and correlation for {stock}"
                        async for response in self.oracle.stream(query, self.session_id, f"trends_{stock}"):
                            if not response.get('is_task_complete'):
                                step = response.get('content', '')
                                if step:
                                    print(f"   {step}")
                            else:
                                print("\n✅ Trend analysis complete!")
                                break
                        await self.get_user_input("\nPress Enter to continue...")
                elif choice == '9':
                    await self.show_help()
                else:
                    print("\n❌ Invalid option. Please try again.")
                    await asyncio.sleep(1)
                    
            except KeyboardInterrupt:
                print("\n\n👋 Exiting Market Oracle...")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                logger.error(f"Menu error: {e}")
                await asyncio.sleep(2)


async def main():
    """Run the interactive Market Oracle."""
    oracle = InteractiveMarketOracle()
    await oracle.run_interactive()


if __name__ == "__main__":
    print("Starting Market Oracle...")
    asyncio.run(main())