#!/usr/bin/env python3
"""Demo script for Market Oracle multi-agent system with Supabase integration."""

import asyncio
import json
from a2a_sdk.client import A2AClient
from datetime import datetime

async def test_individual_agent(name, url, query):
    """Test an individual agent."""
    print(f"\n🤖 Testing {name}...")
    print("-" * 40)
    
    try:
        client = A2AClient(base_url=url)
        stream = await client.astream(
            message=query,
            session_id="demo_session",
            task_id=f"test_{name}"
        )
        
        async for response in stream:
            if response.get('is_task_complete'):
                if response.get('response_type') == 'data':
                    print(f"✅ {name} returned data successfully")
                    return response['content']
                else:
                    print(f"Response: {response.get('content', '')[:100]}...")
            else:
                print(f"  {response.get('content', '')}")
        
    except Exception as e:
        print(f"❌ {name} error: {e}")
        return None

async def test_oracle_prime_full_analysis():
    """Test full Oracle Prime orchestration."""
    print("\n" + "=" * 60)
    print("🎯 FULL MARKET ORACLE ANALYSIS")
    print("=" * 60)
    
    client = A2AClient(base_url="http://localhost:10501")
    
    query = "Analyze AAPL for investment. Should I buy? What are the risks?"
    
    print(f"\nQuery: {query}")
    print("-" * 60)
    print("Oracle Prime is orchestrating all agents...")
    print()
    
    try:
        stream = await client.astream(
            message=query,
            session_id="demo_session",
            task_id="full_analysis"
        )
        
        async for response in stream:
            if response.get('is_task_complete'):
                if response.get('response_type') == 'data':
                    data = response['content']
                    
                    print("\n📊 INVESTMENT RECOMMENDATION")
                    print("=" * 40)
                    
                    rec = data.get('recommendation', {})
                    print(f"Action: {rec.get('investment_recommendation', 'N/A')}")
                    print(f"Confidence: {rec.get('confidence_score', 0):.1%}")
                    print(f"\nSummary: {rec.get('executive_summary', 'N/A')}")
                    
                    print("\n📈 KEY INSIGHTS")
                    print("-" * 40)
                    for insight in rec.get('key_insights', [])[:5]:
                        print(f"• [{insight.get('source', 'Unknown')}] {insight.get('insight', '')}")
                    
                    print("\n⚠️ RISK ASSESSMENT")
                    print("-" * 40)
                    risk = rec.get('risk_assessment', {})
                    print(f"Risk Score: {risk.get('risk_score', 0)}/100")
                    print("Key Risks:")
                    for r in risk.get('key_risks', [])[:3]:
                        print(f"  - {r}")
                    
                    print("\n💰 TRADING STRATEGY")
                    print("-" * 40)
                    print(f"Position Size: {rec.get('position_size', 'N/A')}")
                    
                    entry = rec.get('entry_strategy', {})
                    print(f"Entry: {entry.get('entry_price', 'N/A')} ({entry.get('timing', 'N/A')})")
                    
                    exit_strat = rec.get('exit_strategy', {})
                    print(f"Target: {exit_strat.get('target_price', 'N/A')}")
                    print(f"Stop Loss: {exit_strat.get('stop_loss', 'N/A')}")
                    print(f"Time Horizon: {exit_strat.get('time_horizon', 'N/A')}")
                    
                    # Show data from Supabase
                    print("\n💾 SUPABASE DATA")
                    print("-" * 40)
                    recent_signals = data.get('recent_signals', [])
                    print(f"Recent Signals in Database: {len(recent_signals)}")
                    for signal in recent_signals[:3]:
                        print(f"  - {signal.get('signal_type', '').upper()} "
                              f"(confidence: {signal.get('confidence_score', 0):.0%}) "
                              f"by {signal.get('agent_name', 'unknown')}")
                    
                    print("\n✅ Analysis Complete!")
                    
            else:
                content = response.get('content', '')
                if content:
                    print(f"  {content}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

async def test_audio_briefing():
    """Test audio briefing generation."""
    print("\n" + "=" * 60)
    print("🎙️ AUDIO BRIEFING TEST")
    print("=" * 60)
    
    client = A2AClient(base_url="http://localhost:10508")
    
    try:
        stream = await client.astream(
            message="Generate a daily portfolio briefing",
            session_id="demo_session",
            task_id="audio_briefing"
        )
        
        async for response in stream:
            if response.get('is_task_complete'):
                if response.get('response_type') == 'data':
                    data = response['content']
                    
                    print("\n📝 BRIEFING SCRIPT")
                    print("-" * 40)
                    print(data.get('plain_text', 'No script generated')[:500] + "...")
                    
                    print("\n🎵 AUDIO CONFIG")
                    print("-" * 40)
                    config = data.get('audio_config', {})
                    print(f"Voice: {config.get('voice', 'N/A')}")
                    print(f"Duration: {data.get('metadata', {}).get('duration', 0)} seconds")
                    
            else:
                print(f"  {response.get('content', '')}")
        
    except Exception as e:
        print(f"❌ Audio Briefer error: {e}")

async def test_report_generation():
    """Test report generation."""
    print("\n" + "=" * 60)
    print("📄 REPORT GENERATION TEST")
    print("=" * 60)
    
    client = A2AClient(base_url="http://localhost:10507")
    
    try:
        stream = await client.astream(
            message="Generate investment report for AAPL",
            session_id="demo_session",
            task_id="report_generation"
        )
        
        async for response in stream:
            if response.get('is_task_complete'):
                if response.get('response_type') == 'data':
                    data = response['content']
                    
                    print("\n📊 REPORT METADATA")
                    print("-" * 40)
                    meta = data.get('metadata', {})
                    print(f"Report ID: {meta.get('report_id', 'N/A')}")
                    print(f"Data Sources: {meta.get('data_sources', 0)}")
                    print(f"Confidence: {meta.get('confidence_score', 0):.0%}")
                    
                    print("\n📝 REPORT PREVIEW")
                    print("-" * 40)
                    markdown = data.get('markdown', '')
                    print(markdown[:500] + "..." if len(markdown) > 500 else markdown)
                    
            else:
                print(f"  {response.get('content', '')}")
        
    except Exception as e:
        print(f"❌ Report Synthesizer error: {e}")

async def main():
    """Test Market Oracle multi-agent system with Supabase."""
    
    print("=" * 60)
    print("Market Oracle Demo with Supabase Integration")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test individual agents first
    agents = [
        ("Technical Prophet", "http://localhost:10504", "Analyze AAPL technical indicators"),
        ("Risk Guardian", "http://localhost:10505", "Assess portfolio risk for AAPL trade"),
        ("Trend Correlator", "http://localhost:10506", "Analyze Google Trends for AAPL"),
    ]
    
    print("🧪 Testing Individual Agents...")
    for name, url, query in agents:
        await test_individual_agent(name, url, query)
    
    # Test full orchestration
    await test_oracle_prime_full_analysis()
    
    # Test specialized features
    await test_audio_briefing()
    await test_report_generation()
    
    print("\n" + "=" * 60)
    print("✅ Demo Complete!")
    print("=" * 60)
    print("\nAll trading signals and analyses have been saved to Supabase.")
    print("Check your Supabase dashboard to see the data:")
    print("https://app.supabase.com/project/udjwjoymlofdocclufxv")

if __name__ == "__main__":
    asyncio.run(main())