"""
ABOUTME: Enhanced main entry point with A2A-MCP capabilities
ABOUTME: Drop-in replacement for main.py with quality validation and observability
"""

import asyncio
import os
from dotenv import load_dotenv
import sys

# Add path for A2A-MCP imports
sys.path.append('/Users/mac/Agents/agentic_5/src')

# Import Google ADK components
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# Import enhanced orchestrator
from research_assistant_agent.a2a_enhanced_orchestrator import A2AEnhancedOrchestrator

# Import original utilities
from utils import (
    update_research_history,
    Colors
)

# Load environment variables
load_dotenv()


# ===== PART 1: Initialize Enhanced Components =====
# A2A-MCP enhanced orchestrator with quality validation
research_orchestrator = A2AEnhancedOrchestrator()

# Session service (reuse existing)
session_service = InMemorySessionService()


# ===== PART 2: Define Initial State (Same as original) =====
initial_state = {
    "user_name": "NU",
    "research_history": [],
    "research_metrics": {
        "total_queries": 0,
        "papers_analyzed": 0,
        "insights_generated": 0,
        "gaps_identified": 0,
        # New A2A metrics
        "quality_scores": [],
        "parallel_executions": 0
    },
    "key_insights": [],
}


async def call_research_agent_async_enhanced(runner, user_id, session_id, query):
    """Enhanced research execution with quality validation and streaming."""
    print(f"\n{Colors.BOLD}Research Query:{Colors.RESET} {query}")
    
    # Option 1: Stream with artifacts (recommended)
    if os.getenv("ENABLE_STREAMING", "true").lower() == "true":
        print(f"{Colors.CYAN}Streaming research with quality validation...{Colors.RESET}")
        
        async for event in research_orchestrator.stream_with_artifacts(
            query=query,
            session_id=session_id,
            task_id=f"task_{session_id}"
        ):
            # Display streaming events
            if event["type"] == "planning":
                print(f"{Colors.YELLOW}📋 Planning: {event['content']}{Colors.RESET}")
            elif event["type"] == "execution":
                print(f"{Colors.GREEN}⚡ Executing: {event['content']}{Colors.RESET}")
            elif event["type"] == "artifact":
                artifact = event.get("artifact_info", {})
                print(f"{Colors.BLUE}📄 Artifact: {artifact.get('type', 'unknown')}{Colors.RESET}")
            elif event["type"] == "completion":
                result = event.get("result", {})
                quality = result.get("quality_metadata", {})
                
                # Display quality validation results
                if quality:
                    print(f"\n{Colors.BOLD}{Colors.CYAN}Quality Validation Results:{Colors.RESET}")
                    print(f"  • Overall Score: {quality.get('overall_score', 'N/A')}")
                    print(f"  • Quality Approved: {quality.get('quality_approved', True)}")
                    
                    if "scores" in quality:
                        print(f"  • Detailed Scores:")
                        for metric, score in quality["scores"].items():
                            status = "✅" if score >= 0.8 else "⚠️"
                            print(f"    {status} {metric}: {score:.2f}")
                
                # Display final result
                print(f"\n{Colors.BOLD}Final Result:{Colors.RESET}")
                print(result.get("content", "No content"))
                
                return result
    
    # Option 2: Direct execution (fallback)
    else:
        result = await research_orchestrator._execute_agent_logic(
            query=query,
            context_id=user_id,
            task_id=session_id
        )
        
        # Display quality if available
        if "quality_metadata" in result:
            quality = result["quality_metadata"]
            print(f"\n{Colors.CYAN}Quality Score: {quality.get('overall_score', 'N/A')}{Colors.RESET}")
        
        return result


async def main_async():
    # Setup constants
    APP_NAME = "Research Assistant"
    USER_ID = "nu"
    
    # ===== PART 3: Session Creation =====
    new_session = session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state=initial_state,
    )
    SESSION_ID = new_session.id
    print(f"{Colors.GREEN}Created enhanced research session: {SESSION_ID}{Colors.RESET}")
    
    # ===== PART 4: Enhanced Agent Runner Setup =====
    # Note: We use the ADK agent inside the enhanced orchestrator
    runner = Runner(
        agent=research_orchestrator.adk_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )
    
    # ===== PART 5: Enhanced Welcome Message =====
    print(f"\n{Colors.BOLD}{Colors.CYAN}╔═══════════════════════════════════════════════════════════════╗")
    print(f"║     🔬 AI Research Assistant (A2A-MCP Enhanced) 🔬           ║")
    print(f"╚═══════════════════════════════════════════════════════════════╝{Colors.RESET}")
    print(f"\n{Colors.YELLOW}Welcome to your enhanced AI-powered research assistant!{Colors.RESET}")
    print(f"New features:")
    print(f"  • {Colors.GREEN}Academic quality validation (7 metrics){Colors.RESET}")
    print(f"  • {Colors.GREEN}Parallel literature search optimization{Colors.RESET}")
    print(f"  • {Colors.GREEN}Real-time streaming with progress{Colors.RESET}")
    print(f"  • {Colors.GREEN}Enterprise observability and metrics{Colors.RESET}")
    print(f"\n{Colors.CYAN}Type 'exit' or 'quit' to end. Type 'help' for info.{Colors.RESET}\n")
    
    # ===== PART 6: Enhanced Research Loop =====
    while True:
        # Get user input
        user_input = input(f"{Colors.BOLD}Research Query:{Colors.RESET} ")
        
        # Check for exit commands
        if user_input.lower() in ["exit", "quit"]:
            print(f"\n{Colors.YELLOW}Ending enhanced research session. Goodbye!{Colors.RESET}")
            break
        
        # Check for help command
        if user_input.lower() == "help":
            print(f"\n{Colors.CYAN}Enhanced Research Assistant Help:{Colors.RESET}")
            print("Example queries:")
            print("  • 'Review literature on quantum computing applications'")
            print("  • 'Analyze research gaps in AI safety'")
            print("  • 'Compare methodologies in neural network interpretability'")
            print("\nEnhanced features:")
            print("  • Quality scores show research confidence and rigor")
            print("  • Parallel searches across multiple databases")
            print("  • Real-time progress updates during search")
            print()
            continue
        
        # Skip empty queries
        if not user_input.strip():
            print(f"{Colors.RED}Please enter a valid research query.{Colors.RESET}")
            continue
        
        # Update research history
        update_research_history(
            session_service, APP_NAME, USER_ID, SESSION_ID,
            {
                "action": "query",
                "query": user_input,
                "framework": "a2a_mcp_enhanced"
            }
        )
        
        # Process with enhanced agent
        await call_research_agent_async_enhanced(runner, USER_ID, SESSION_ID, user_input)
    
    # ===== PART 7: Enhanced Final Summary =====
    final_session = session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}Enhanced Research Session Summary:{Colors.RESET}")
    metrics = final_session.state.get("research_metrics", {})
    print(f"  • Total Queries: {metrics.get('total_queries', 0)}")
    print(f"  • Papers Analyzed: {metrics.get('papers_analyzed', 0)}")
    print(f"  • Insights Generated: {metrics.get('insights_generated', 0)}")
    print(f"  • Research Gaps: {metrics.get('gaps_identified', 0)}")
    
    # Show quality metrics if available
    quality_scores = metrics.get("quality_scores", [])
    if quality_scores:
        avg_quality = sum(quality_scores) / len(quality_scores)
        print(f"  • Average Quality Score: {avg_quality:.2f}")
    
    # Show health status
    health = research_orchestrator.get_health_status()
    print(f"\n{Colors.BOLD}System Health:{Colors.RESET}")
    print(f"  • Quality Validation: {'✅' if health['research_metrics']['quality_validation_enabled'] else '❌'}")
    print(f"  • Observability: {'✅' if health['research_metrics']['observability_enabled'] else '❌'}")
    print(f"  • Papers Analyzed: {health['research_metrics']['total_papers_analyzed']}")


def main():
    """Enhanced entry point with A2A-MCP capabilities."""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Enhanced research session interrupted. Goodbye!{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")


if __name__ == "__main__":
    main()