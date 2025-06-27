#!/usr/bin/env python3
"""Comprehensive test of the complete Market Oracle system."""

import asyncio
import logging
import sys
import json
from datetime import datetime
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('complete_system_test.log')
    ]
)
logger = logging.getLogger(__name__)

# Import all agents
from src.a2a_mcp.agents.market_oracle.oracle_prime_agent_supabase import OraclePrimeAgentSupabase
from src.a2a_mcp.agents.market_oracle.sentiment_seeker_agent_brightdata import SentimentSeekerAgentBrightData
from src.a2a_mcp.agents.market_oracle.fundamental_analyst_agent import FundamentalAnalystAgent
from src.a2a_mcp.agents.market_oracle.technical_prophet_agent import TechnicalProphetAgent
from src.a2a_mcp.agents.market_oracle.risk_guardian_agent import RiskGuardianAgent
from src.a2a_mcp.agents.market_oracle.trend_correlator_agent import TrendCorrelatorAgent
from src.a2a_mcp.agents.market_oracle.report_synthesizer_agent import ReportSynthesizerAgent
from src.a2a_mcp.agents.market_oracle.audio_briefer_agent import AudioBrieferAgent

# Import utilities
from src.a2a_mcp.common.supabase_client import SupabaseClient
from src.a2a_mcp.common.stock_mcp_client import StockMCPClient
from src.a2a_mcp.common.brightdata_cache import BrightDataCache

class MarketOracleSystemTest:
    """Complete system test for Market Oracle."""
    
    def __init__(self):
        self.agents = {}
        self.supabase = SupabaseClient()
        self.stock_mcp = StockMCPClient()
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "workflows": {},
            "integrations": {},
            "performance": {}
        }
        
    async def initialize_agents(self):
        """Initialize all Market Oracle agents."""
        print("\n" + "="*80)
        print("🚀 INITIALIZING MARKET ORACLE AGENTS")
        print("="*80)
        
        try:
            # Initialize each agent
            print("\n1️⃣ Oracle Prime (Orchestrator)")
            self.agents['oracle_prime'] = OraclePrimeAgentSupabase()
            print("   ✅ Initialized")
            
            print("\n2️⃣ Sentiment Seeker (Reddit via BrightData)")
            self.agents['sentiment_seeker'] = SentimentSeekerAgentBrightData()
            print("   ✅ Initialized")
            
            print("\n3️⃣ Fundamental Analyst")
            self.agents['fundamental_analyst'] = FundamentalAnalystAgent()
            print("   ✅ Initialized")
            
            print("\n4️⃣ Technical Prophet")
            self.agents['technical_prophet'] = TechnicalProphetAgent()
            print("   ✅ Initialized")
            
            print("\n5️⃣ Risk Guardian")
            self.agents['risk_guardian'] = RiskGuardianAgent()
            print("   ✅ Initialized")
            
            print("\n6️⃣ Trend Correlator")
            self.agents['trend_correlator'] = TrendCorrelatorAgent()
            print("   ✅ Initialized")
            
            print("\n7️⃣ Report Synthesizer")
            self.agents['report_synthesizer'] = ReportSynthesizerAgent()
            print("   ✅ Initialized")
            
            print("\n8️⃣ Audio Briefer")
            self.agents['audio_briefer'] = AudioBrieferAgent()
            print("   ✅ Initialized")
            
            self.test_results["components"]["agents"] = {
                "status": "SUCCESS",
                "count": len(self.agents),
                "agents": list(self.agents.keys())
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            self.test_results["components"]["agents"] = {
                "status": "FAILED",
                "error": str(e)
            }
            raise
            
    async def test_integrations(self):
        """Test all external integrations."""
        print("\n" + "="*80)
        print("🔌 TESTING INTEGRATIONS")
        print("="*80)
        
        # Test Supabase
        print("\n📊 Testing Supabase...")
        try:
            test_signal = await self.supabase.create_trading_signal(
                symbol="TEST",
                signal_type="buy",
                confidence_score=0.99,
                agent_name="System Test",
                reasoning="Integration test"
            )
            if test_signal:
                print("   ✅ Supabase: Connected and operational")
                self.test_results["integrations"]["supabase"] = "SUCCESS"
            else:
                print("   ❌ Supabase: Failed to create test signal")
                self.test_results["integrations"]["supabase"] = "FAILED"
        except Exception as e:
            print(f"   ❌ Supabase: {e}")
            self.test_results["integrations"]["supabase"] = f"ERROR: {e}"
            
        # Test Stock MCP
        print("\n📈 Testing Stock MCP...")
        try:
            prediction = await self.stock_mcp.get_prediction("AAPL")
            print(f"   ✅ Stock MCP: {prediction['prediction']['direction']} prediction")
            self.test_results["integrations"]["stock_mcp"] = "SUCCESS"
        except Exception as e:
            print(f"   ❌ Stock MCP: {e}")
            self.test_results["integrations"]["stock_mcp"] = f"ERROR: {e}"
            
        # Test BrightData
        print("\n🌐 Testing BrightData...")
        try:
            cache = BrightDataCache()
            # Try to use cached data first
            cached = await cache.get("TSLA")
            if cached:
                print("   ✅ BrightData: Using cached data")
                self.test_results["integrations"]["brightdata"] = "SUCCESS (cached)"
            else:
                # Try live API
                sentiment_agent = self.agents['sentiment_seeker']
                result = await sentiment_agent.fetch_reddit_data("TSLA")
                if "error" not in result:
                    print("   ✅ BrightData: Live API working")
                    self.test_results["integrations"]["brightdata"] = "SUCCESS"
                else:
                    print(f"   ⚠️  BrightData: {result['error']}")
                    self.test_results["integrations"]["brightdata"] = "PARTIAL"
        except Exception as e:
            print(f"   ❌ BrightData: {e}")
            self.test_results["integrations"]["brightdata"] = f"ERROR: {e}"
            
    async def test_individual_agents(self):
        """Test each agent individually."""
        print("\n" + "="*80)
        print("🤖 TESTING INDIVIDUAL AGENTS")
        print("="*80)
        
        test_symbols = ["TSLA", "AAPL", "NVDA"]
        
        for agent_name, agent in self.agents.items():
            print(f"\n📍 Testing {agent_name}...")
            try:
                # Skip Oracle Prime for individual testing
                if agent_name == "oracle_prime":
                    print("   ⏭️  Skipping (will test in workflow)")
                    continue
                    
                # Test with a simple query
                query = f"Analyze {test_symbols[0]}"
                context_id = f"test_{agent_name}"
                task_id = f"task_{agent_name}"
                
                result = None
                async for response in agent.stream(query, context_id, task_id):
                    if response.get('is_task_complete'):
                        if response.get('response_type') == 'data':
                            result = response['content']
                        break
                        
                if result:
                    print(f"   ✅ {agent_name}: Responded successfully")
                    self.test_results["components"][agent_name] = "SUCCESS"
                else:
                    print(f"   ⚠️  {agent_name}: No data response")
                    self.test_results["components"][agent_name] = "NO_DATA"
                    
            except Exception as e:
                print(f"   ❌ {agent_name}: {e}")
                self.test_results["components"][agent_name] = f"ERROR: {e}"
                
    async def test_complete_workflow(self):
        """Test the complete Market Oracle workflow."""
        print("\n" + "="*80)
        print("🔄 TESTING COMPLETE WORKFLOW")
        print("="*80)
        
        # Test comprehensive analysis
        test_query = "Provide a complete market analysis for TSLA including sentiment, technical analysis, and risk assessment"
        
        print(f"\n📊 Query: {test_query}")
        print("-" * 60)
        
        try:
            oracle = self.agents['oracle_prime']
            context_id = "workflow_test"
            task_id = "complete_analysis"
            
            steps = []
            final_result = None
            
            async for response in oracle.stream(test_query, context_id, task_id):
                if not response.get('is_task_complete'):
                    step = response.get('content', '')
                    if step:
                        print(f"   ⏳ {step}")
                        steps.append(step)
                else:
                    if response.get('response_type') == 'data':
                        final_result = response['content']
                        break
                        
            if final_result:
                print("\n   ✅ Workflow completed successfully!")
                print("\n📋 ANALYSIS RESULTS:")
                print("-" * 60)
                
                # Display key results
                if isinstance(final_result, dict):
                    if 'sentiment_analysis' in final_result:
                        sentiment = final_result['sentiment_analysis']
                        print(f"\n   📰 Sentiment Analysis:")
                        print(f"      Score: {sentiment.get('sentiment_score', 'N/A')}")
                        print(f"      Recommendation: {sentiment.get('recommendation', 'N/A')}")
                        
                    if 'technical_analysis' in final_result:
                        technical = final_result['technical_analysis']
                        print(f"\n   📈 Technical Analysis:")
                        print(f"      Signal: {technical.get('signal', 'N/A')}")
                        print(f"      Confidence: {technical.get('confidence', 'N/A')}")
                        
                    if 'risk_assessment' in final_result:
                        risk = final_result['risk_assessment']
                        print(f"\n   ⚠️  Risk Assessment:")
                        print(f"      Level: {risk.get('risk_level', 'N/A')}")
                        print(f"      Score: {risk.get('risk_score', 'N/A')}")
                        
                self.test_results["workflows"]["complete_analysis"] = {
                    "status": "SUCCESS",
                    "steps": len(steps),
                    "agents_used": self._extract_agents_from_steps(steps)
                }
            else:
                print("   ❌ Workflow failed to produce results")
                self.test_results["workflows"]["complete_analysis"] = "FAILED"
                
        except Exception as e:
            print(f"   ❌ Workflow error: {e}")
            self.test_results["workflows"]["complete_analysis"] = f"ERROR: {e}"
            
    def _extract_agents_from_steps(self, steps: List[str]) -> List[str]:
        """Extract agent names from workflow steps."""
        agents_used = []
        agent_keywords = {
            "Sentiment Seeker": "sentiment",
            "Technical Prophet": "technical",
            "Fundamental Analyst": "fundamental",
            "Risk Guardian": "risk",
            "Trend Correlator": "trend",
            "Report Synthesizer": "report",
            "Audio Briefer": "audio"
        }
        
        for step in steps:
            step_lower = step.lower()
            for agent, keyword in agent_keywords.items():
                if keyword in step_lower and agent not in agents_used:
                    agents_used.append(agent)
                    
        return agents_used
        
    async def test_performance(self):
        """Test system performance metrics."""
        print("\n" + "="*80)
        print("⚡ TESTING PERFORMANCE")
        print("="*80)
        
        # Test response times
        print("\n⏱️  Measuring response times...")
        
        test_queries = [
            ("Simple sentiment", "What is the Reddit sentiment for AAPL?"),
            ("Technical analysis", "Provide technical analysis for NVDA"),
            ("Complete analysis", "Full market analysis for TSLA")
        ]
        
        for query_type, query in test_queries:
            start_time = datetime.now()
            
            try:
                oracle = self.agents['oracle_prime']
                async for response in oracle.stream(query, f"perf_{query_type}", "perf_task"):
                    if response.get('is_task_complete'):
                        break
                        
                elapsed = (datetime.now() - start_time).total_seconds()
                print(f"   ✅ {query_type}: {elapsed:.2f} seconds")
                
                self.test_results["performance"][query_type] = {
                    "time_seconds": elapsed,
                    "status": "SUCCESS"
                }
                
            except Exception as e:
                print(f"   ❌ {query_type}: Failed - {e}")
                self.test_results["performance"][query_type] = {
                    "status": "FAILED",
                    "error": str(e)
                }
                
    def generate_report(self):
        """Generate comprehensive test report."""
        print("\n" + "="*80)
        print("📊 MARKET ORACLE SYSTEM TEST REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Component Status
        print("\n🔧 COMPONENT STATUS:")
        print("-" * 40)
        components = self.test_results.get("components", {})
        for component, status in components.items():
            icon = "✅" if status == "SUCCESS" else "❌" if "ERROR" in str(status) else "⚠️"
            print(f"   {icon} {component}: {status}")
            
        # Integration Status
        print("\n🔌 INTEGRATION STATUS:")
        print("-" * 40)
        integrations = self.test_results.get("integrations", {})
        for integration, status in integrations.items():
            icon = "✅" if status == "SUCCESS" else "❌" if "ERROR" in str(status) else "⚠️"
            print(f"   {icon} {integration}: {status}")
            
        # Workflow Status
        print("\n🔄 WORKFLOW STATUS:")
        print("-" * 40)
        workflows = self.test_results.get("workflows", {})
        for workflow, result in workflows.items():
            if isinstance(result, dict):
                status = result.get("status", "UNKNOWN")
                icon = "✅" if status == "SUCCESS" else "❌"
                print(f"   {icon} {workflow}: {status}")
                if result.get("agents_used"):
                    print(f"      Agents used: {', '.join(result['agents_used'])}")
            else:
                icon = "❌" if "ERROR" in str(result) else "⚠️"
                print(f"   {icon} {workflow}: {result}")
                
        # Performance Metrics
        print("\n⚡ PERFORMANCE METRICS:")
        print("-" * 40)
        performance = self.test_results.get("performance", {})
        total_time = 0
        for metric, result in performance.items():
            if isinstance(result, dict) and result.get("status") == "SUCCESS":
                time_sec = result.get("time_seconds", 0)
                total_time += time_sec
                print(f"   ⏱️  {metric}: {time_sec:.2f}s")
                
        if total_time > 0:
            print(f"   📊 Average response time: {total_time/len(performance):.2f}s")
            
        # Overall Assessment
        print("\n🎯 OVERALL ASSESSMENT:")
        print("-" * 40)
        
        # Calculate success rate
        total_tests = 0
        successful_tests = 0
        
        for category in ["components", "integrations", "workflows", "performance"]:
            tests = self.test_results.get(category, {})
            for test, result in tests.items():
                total_tests += 1
                if isinstance(result, dict):
                    if result.get("status") == "SUCCESS":
                        successful_tests += 1
                elif result == "SUCCESS":
                    successful_tests += 1
                    
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"   Success Rate: {success_rate:.1f}% ({successful_tests}/{total_tests} tests)")
        
        if success_rate >= 90:
            print("   Status: ✅ SYSTEM FULLY OPERATIONAL")
        elif success_rate >= 70:
            print("   Status: ⚠️  SYSTEM PARTIALLY OPERATIONAL")
        else:
            print("   Status: ❌ SYSTEM NEEDS ATTENTION")
            
        # Save detailed report
        report_file = "market_oracle_test_report.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        print("\n" + "="*80)
        print("✅ TESTING COMPLETE")
        print("="*80)
        
    async def run_all_tests(self):
        """Run all system tests."""
        try:
            await self.initialize_agents()
            await self.test_integrations()
            await self.test_individual_agents()
            await self.test_complete_workflow()
            await self.test_performance()
            self.generate_report()
            
        except Exception as e:
            logger.error(f"Critical test failure: {e}")
            print(f"\n❌ CRITICAL ERROR: {e}")
            self.generate_report()
            

async def main():
    """Run complete system test."""
    tester = MarketOracleSystemTest()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())