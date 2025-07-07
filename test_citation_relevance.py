#!/usr/bin/env python3
"""Test script to verify citation relevance filtering."""

import asyncio
import sys
import os

# Set up environment
sys.path.insert(0, './src')
sys.path.insert(0, '.')

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️  python-dotenv not available, using system environment variables")

async def test_citation_relevance():
    """Test that different questions get relevant citations."""
    print("🧪 TESTING CITATION RELEVANCE FILTERING")
    print("=" * 50)
    
    try:
        from a2a_mcp.agents.nexus_oracle_agent import NexusOracleAgent
        
        # Initialize Oracle
        oracle = NexusOracleAgent()
        print(f"✅ Oracle initialized: {oracle.agent_name}")
        
        # Test 1: AI and Education query
        print("\n📋 TEST 1: AI and Education Query")
        ai_query = "How can AI improve education quality in India?"
        await oracle.load_research_context(ai_query)
        
        ai_refs = oracle._format_external_references()
        print(f"📝 AI Query References (first 300 chars):")
        print(ai_refs[:300] + "..." if len(ai_refs) > 300 else ai_refs)
        
        # Clear state and test different query
        oracle.clear_state()
        print("\n🧹 State cleared")
        
        # Test 2: Quantum Computing query  
        print("\n📋 TEST 2: Quantum Computing Query")
        quantum_query = "How can quantum computing accelerate climate modeling?"
        await oracle.load_research_context(quantum_query)
        
        quantum_refs = oracle._format_external_references()
        print(f"📝 Quantum Query References (first 300 chars):")
        print(quantum_refs[:300] + "..." if len(quantum_refs) > 300 else quantum_refs)
        
        # Test relevance filtering
        print("\n🔍 RELEVANCE FILTERING TEST")
        test_papers = [
            {
                "title": "Machine Learning for Educational Assessment in Rural India",
                "abstract": "This paper explores AI applications in education for underserved populations",
                "authors": ["Smith", "Kumar"]
            },
            {
                "title": "Quantum Algorithms for Climate Simulation", 
                "abstract": "Novel quantum computing approaches for atmospheric modeling",
                "authors": ["Johnson", "Patel"]
            },
            {
                "title": "Deep Learning for Personalized Education Content",
                "abstract": "AI-driven content recommendation systems for students",
                "authors": ["Chen", "Singh"]
            }
        ]
        
        ai_query_clean = "ai education india"
        quantum_query_clean = "quantum computing climate"
        
        print(f"\n📊 Testing papers against AI query: '{ai_query_clean}'")
        for i, paper in enumerate(test_papers, 1):
            relevant = oracle._is_paper_relevant_to_query(paper, ai_query_clean)
            print(f"   {i}. '{paper['title'][:40]}...' - Relevant: {relevant}")
            
        print(f"\n📊 Testing papers against Quantum query: '{quantum_query_clean}'")
        for i, paper in enumerate(test_papers, 1):
            relevant = oracle._is_paper_relevant_to_query(paper, quantum_query_clean)
            print(f"   {i}. '{paper['title'][:40]}...' - Relevant: {relevant}")
            
        print("\n✅ Citation relevance filtering test completed!")
        print("💡 Papers should only be marked relevant when they match query topics")
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Citation Relevance Test...")
    asyncio.run(test_citation_relevance())