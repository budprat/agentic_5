#!/usr/bin/env python3
"""
Quick Test Script for Interactive Oracle Chat
=============================================

This script demonstrates the key features of the interactive chat interface
by running automated tests and showing sample interactions.
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from interactive_oracle_chat import SolopreneurOracleChat, Colors

async def test_chat_features():
    """Test the main features of the interactive chat."""
    print(f"{Colors.BOLD + Colors.CYAN}🧪 TESTING SOLOPRENEUR ORACLE INTERACTIVE CHAT{Colors.END}")
    print("="*70)
    
    # Initialize chat interface
    chat = SolopreneurOracleChat(debug=True, save_history=True)
    
    print(f"\n{Colors.YELLOW}📋 Test 1: System Health Check{Colors.END}")
    health_status = await chat.check_system_health()
    
    if health_status["overall"] in ["excellent", "good"]:
        print(f"{Colors.GREEN}✅ System health check passed!{Colors.END}")
        
        print(f"\n{Colors.YELLOW}📋 Test 2: Oracle Communication (message/send){Colors.END}")
        result = await chat.send_oracle_message("What are the best practices for microservices architecture?", False)
        
        if result.get("status") == "success":
            print(f"{Colors.GREEN}✅ Oracle communication (message/send) successful!{Colors.END}")
            print(f"   Response time: {result.get('response_time', 0):.1f}s")
        else:
            print(f"{Colors.RED}❌ Oracle communication failed: {result.get('error', 'Unknown error')}{Colors.END}")
        
        print(f"\n{Colors.YELLOW}📋 Test 3: Oracle Streaming (message/stream){Colors.END}")
        stream_result = await chat.send_oracle_message("How can I optimize my development workflow?", True)
        
        if stream_result.get("status") == "success":
            print(f"{Colors.GREEN}✅ Oracle streaming successful!{Colors.END}")
            print(f"   Events received: {stream_result.get('events', 0)}")
            print(f"   Response time: {stream_result.get('response_time', 0):.1f}s")
        else:
            print(f"{Colors.RED}❌ Oracle streaming failed: {stream_result.get('error', 'Unknown error')}{Colors.END}")
        
        print(f"\n{Colors.YELLOW}📋 Test 4: Domain Agent Communication{Colors.END}")
        domain_result = await chat.send_domain_message("technical", "Evaluate microservices vs monolith architecture")
        
        if domain_result.get("status") == "success":
            print(f"{Colors.GREEN}✅ Domain agent communication successful!{Colors.END}")
            print(f"   Response time: {domain_result.get('response_time', 0):.1f}s")
        else:
            print(f"{Colors.RED}❌ Domain agent communication failed: {domain_result.get('error', 'Unknown error')}{Colors.END}")
        
        print(f"\n{Colors.YELLOW}📋 Test 5: Performance Metrics{Colors.END}")
        chat.show_performance_metrics()
        
        print(f"\n{Colors.GREEN}🎉 All tests completed! The interactive chat is ready for use.{Colors.END}")
        print(f"\n{Colors.BOLD + Colors.CYAN}🚀 To start the interactive chat:{Colors.END}")
        print(f"   python interactive_oracle_chat.py")
        print(f"\n{Colors.BOLD + Colors.CYAN}📚 Available options:{Colors.END}")
        print(f"   python interactive_oracle_chat.py --help")
        print(f"   python interactive_oracle_chat.py --streaming --save-history")
        
    else:
        print(f"{Colors.RED}❌ System health check failed. Please ensure all agents are running.{Colors.END}")
        print(f"\n{Colors.YELLOW}💡 To start the system:{Colors.END}")
        print(f"   1. Start domain agents: Follow TESTING_WORKFLOW.md Phase 2")
        print(f"   2. Start Oracle agent: Follow TESTING_WORKFLOW.md Phase 2.2")
        print(f"   3. Run this test again")

if __name__ == "__main__":
    try:
        asyncio.run(test_chat_features())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}🛑 Test interrupted by user.{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Test error: {e}{Colors.END}")
        sys.exit(1)