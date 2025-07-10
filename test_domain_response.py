#!/usr/bin/env python3
"""
Quick test for domain agent response display
"""
import asyncio
from interactive_oracle_chat import SolopreneurOracleChat

async def test_domain_response():
    """Test domain agent response display."""
    chat = SolopreneurOracleChat(debug=True)
    
    print("Testing domain agent response display...")
    
    # Test knowledge agent
    result = await chat.send_domain_message("knowledge", "How can I manage my Notion database using agents?")
    
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(test_domain_response())