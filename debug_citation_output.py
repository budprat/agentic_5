#!/usr/bin/env python3
"""Debug script to trace why citations aren't appearing in Oracle output."""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime

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

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def debug_oracle_citation_flow():
    """Debug the complete citation flow in Oracle synthesis."""
    print("🔍 DEBUGGING ORACLE CITATION FLOW")
    print("=" * 60)
    
    try:
        from a2a_mcp.agents.nexus_oracle_agent import NexusOracleAgent
        from google import genai
        
        # Initialize Oracle
        oracle = NexusOracleAgent()
        print(f"✅ Oracle initialized: {oracle.agent_name}")
        
        # Test query
        test_query = "How can quantum computing solve climate change challenges?"
        print(f"🧠 Test Query: {test_query}")
        
        # Step 1: Load research context and external references
        print("\n📋 STEP 1: Loading research context...")
        await oracle.load_research_context(test_query)
        
        print(f"✅ Research context loaded")
        print(f"📊 External references enabled: {oracle.external_references.get('enabled', False)}")
        
        if oracle.external_references.get('sources'):
            total_papers = 0
            for source, data in oracle.external_references['sources'].items():
                paper_count = len(data.get('papers', []))
                total_papers += paper_count
                print(f"   📚 {source}: {paper_count} papers")
            print(f"   📝 Total papers found: {total_papers}")
        
        # Step 2: Format external references
        print("\n📋 STEP 2: Formatting external references...")
        formatted_refs = oracle._format_external_references()
        print(f"✅ Formatted references ({len(formatted_refs)} characters)")
        print(f"📄 First 500 characters of formatted references:")
        print("-" * 50)
        print(formatted_refs[:500] + "..." if len(formatted_refs) > 500 else formatted_refs)
        print("-" * 50)
        
        # Step 3: Test research synthesis generation with detailed logging
        print("\n📋 STEP 3: Testing synthesis generation...")
        
        # Mock research intelligence for testing
        oracle.research_intelligence = {
            "computer_science": {
                "domain": "Computer Science",
                "insights": [
                    {"finding": "Quantum algorithms show promise for optimization", "confidence": 0.85},
                    {"finding": "Current quantum hardware limitations exist", "confidence": 0.78}
                ],
                "evidence_quality": 0.82
            },
            "physical_sciences": {
                "domain": "Physical Sciences", 
                "insights": [
                    {"finding": "Quantum materials research advancing rapidly", "confidence": 0.80},
                    {"finding": "Energy storage breakthroughs needed", "confidence": 0.75}
                ],
                "evidence_quality": 0.79
            }
        }
        
        # Step 4: Generate synthesis with debug tracing
        print("\n📋 STEP 4: Generating synthesis with debug tracing...")
        
        client = genai.Client()
        
        # Import the prompt template
        from a2a_mcp.agents.nexus_oracle_agent import RESEARCH_SYNTHESIS_PROMPT
        
        # Format the complete prompt
        full_prompt = RESEARCH_SYNTHESIS_PROMPT.format(
            original_query=test_query,
            research_data=json.dumps(oracle.research_intelligence, indent=2),
            research_context=json.dumps(oracle.research_context, indent=2),
            external_references=formatted_refs,
            min_confidence=oracle.quality_thresholds["min_confidence_score"],
            required_domains=oracle.quality_thresholds["min_domain_coverage"],
            evidence_threshold=oracle.quality_thresholds["evidence_quality_threshold"]
        )
        
        print(f"📝 Complete prompt length: {len(full_prompt)} characters")
        print(f"🔍 External references section in prompt:")
        print("-" * 50)
        
        # Extract just the external references section from the prompt
        lines = full_prompt.split('\n')
        in_external_refs = False
        for line in lines:
            if 'External Academic References:' in line:
                in_external_refs = True
            elif in_external_refs and line.strip() and not line.startswith('Quality Thresholds'):
                print(line)
            elif in_external_refs and line.startswith('Quality Thresholds'):
                break
        print("-" * 50)
        
        # Generate the AI response
        print("\n📋 STEP 5: Calling AI model...")
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=full_prompt,
            config={
                "temperature": 0.1,
                "response_mime_type": "application/json"
            }
        )
        
        print(f"✅ AI response received ({len(response.text)} characters)")
        
        # Parse and analyze the response
        try:
            synthesis = json.loads(response.text)
            print(f"✅ Successfully parsed JSON response")
            
            # Check if citations appear in the synthesis
            synthesis_text = json.dumps(synthesis, indent=2)
            print(f"\n🔍 CITATION ANALYSIS:")
            print(f"   Response contains '[' bracket: {'[' in synthesis_text}")
            print(f"   Response contains 'et al.': {'et al.' in synthesis_text}")
            print(f"   Response contains 'ArXiv': {'arxiv' in synthesis_text.lower()}")
            print(f"   Response contains citations: {'citation' in synthesis_text.lower()}")
            
            # Show executive summary specifically
            executive_summary = synthesis.get('executive_summary', '')
            print(f"\n📋 EXECUTIVE SUMMARY:")
            print(f"   {executive_summary}")
            
            # Check key insights for citations
            key_insights = synthesis.get('key_insights', [])
            print(f"\n📋 KEY INSIGHTS ({len(key_insights)} found):")
            for i, insight in enumerate(key_insights[:3], 1):
                insight_text = insight.get('insight', 'N/A') if isinstance(insight, dict) else str(insight)
                print(f"   {i}. {insight_text}")
                
            # Check novel hypotheses for citations
            hypotheses = synthesis.get('novel_hypotheses', [])
            print(f"\n📋 NOVEL HYPOTHESES ({len(hypotheses)} found):")
            for i, hypothesis in enumerate(hypotheses[:2], 1):
                if isinstance(hypothesis, dict):
                    hyp_text = hypothesis.get('hypothesis', 'N/A')
                    print(f"   {i}. {hyp_text}")
                else:
                    print(f"   {i}. {str(hypothesis)}")
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            print(f"📄 Raw response (first 1000 chars):")
            print(response.text[:1000])
        
        # Step 6: Test with explicit citation instruction
        print("\n📋 STEP 6: Testing with explicit citation instruction...")
        
        explicit_prompt = f"""
You are Nexus Oracle. Analyze this question: "{test_query}"

EXTERNAL REFERENCES AVAILABLE:
{formatted_refs}

CRITICAL INSTRUCTION: You MUST include citations in your analysis using the format [Author et al., Year] when referencing the external papers provided above.

Research Data:
{json.dumps(oracle.research_intelligence, indent=2)}

Provide a brief analysis that SPECIFICALLY CITES the external academic papers using [Author et al., Year] format.
"""
        
        explicit_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=explicit_prompt,
            config={"temperature": 0.1}
        )
        
        print(f"✅ Explicit citation test response:")
        print("-" * 50)
        print(explicit_response.text[:800] + "..." if len(explicit_response.text) > 800 else explicit_response.text)
        print("-" * 50)
        
        # Check for citations in explicit test
        explicit_text = explicit_response.text
        has_brackets = '[' in explicit_text and ']' in explicit_text
        has_et_al = 'et al.' in explicit_text
        print(f"\n🔍 EXPLICIT TEST CITATION CHECK:")
        print(f"   Contains [brackets]: {has_brackets}")
        print(f"   Contains 'et al.': {has_et_al}")
        print(f"   Successfully cited: {has_brackets and has_et_al}")
        
        if not (has_brackets and has_et_al):
            print("\n❌ PROBLEM IDENTIFIED: AI model is not following citation instructions")
            print("💡 POSSIBLE SOLUTIONS:")
            print("   1. Modify prompt to be more explicit about citation requirements")
            print("   2. Provide specific citation examples in the prompt")
            print("   3. Post-process the response to add citations")
            print("   4. Use a different model or approach for citation integration")
        else:
            print("\n✅ EXPLICIT TEST PASSED: AI can generate citations when specifically instructed")
            print("💡 SOLUTION: Enhance the Oracle prompt template with more explicit citation instructions")
        
    except Exception as e:
        logger.error(f"Debug error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Oracle Citation Debug...")
    asyncio.run(debug_oracle_citation_flow())