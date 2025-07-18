"""
ABOUTME: Utility functions for research assistant orchestrator
ABOUTME: Provides session management, display, and helper functions
"""

from datetime import datetime
from google.genai import types
import json


# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    
    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


def update_research_history(session_service, app_name, user_id, session_id, entry):
    """Add a research entry to the interaction history in state.
    
    Args:
        session_service: The session service instance
        app_name: The application name
        user_id: The user ID
        session_id: The session ID
        entry: A dictionary containing the research data
    """
    try:
        # Get current session
        session = session_service.get_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )
        
        # Get current research history
        research_history = session.state.get("research_history", [])
        
        # Add timestamp if not already present
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Add the entry to research history
        research_history.append(entry)
        
        # Create updated state
        updated_state = session.state.copy()
        updated_state["research_history"] = research_history
        
        # Update research metrics
        if "research_metrics" not in updated_state:
            updated_state["research_metrics"] = {
                "total_queries": 0,
                "papers_analyzed": 0,
                "insights_generated": 0,
                "gaps_identified": 0
            }
        
        # Update metrics based on entry type
        if entry.get("action") == "query":
            updated_state["research_metrics"]["total_queries"] += 1
        elif entry.get("action") == "literature_review":
            updated_state["research_metrics"]["papers_analyzed"] += entry.get("papers_count", 0)
            updated_state["research_metrics"]["insights_generated"] += len(entry.get("key_findings", []))
            updated_state["research_metrics"]["gaps_identified"] += len(entry.get("research_gaps", []))
        
        # Create a new session with updated state
        session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            state=updated_state,
        )
    except Exception as e:
        print(f"Error updating research history: {e}")


def display_research_state(
    session_service, app_name, user_id, session_id, label="Research State"
):
    """Display the current research session state in a formatted way."""
    try:
        session = session_service.get_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )
        
        # Format the output with clear sections
        print(f"\n{Colors.CYAN}{'-' * 20} {label} {'-' * 20}{Colors.RESET}")
        
        # Research session info
        session_info = session.state.get("research_session_id", "Not started")
        print(f"{Colors.BOLD}📚 Research Session: {Colors.RESET}{session_info}")
        
        # Research metrics
        metrics = session.state.get("research_metrics", {})
        if metrics:
            print(f"\n{Colors.BOLD}📊 Research Metrics:{Colors.RESET}")
            print(f"  • Total Queries: {metrics.get('total_queries', 0)}")
            print(f"  • Papers Analyzed: {metrics.get('papers_analyzed', 0)}")
            print(f"  • Insights Generated: {metrics.get('insights_generated', 0)}")
            print(f"  • Gaps Identified: {metrics.get('gaps_identified', 0)}")
        
        # Recent research history
        research_history = session.state.get("research_history", [])
        if research_history:
            print(f"\n{Colors.BOLD}📝 Recent Research Activity:{Colors.RESET}")
            for idx, entry in enumerate(research_history[-5:], 1):  # Show last 5
                action = entry.get("action", "unknown")
                timestamp = entry.get("timestamp", "unknown time")
                
                if action == "query":
                    query = entry.get("query", "")
                    print(f"  {idx}. [{timestamp}] Query: \"{query[:50]}...\"")
                elif action == "literature_review":
                    papers = entry.get("papers_count", 0)
                    topic = entry.get("topic", "unknown")
                    print(f"  {idx}. [{timestamp}] Literature Review: {papers} papers on \"{topic}\"")
                else:
                    print(f"  {idx}. [{timestamp}] {action}")
        
        # Key insights
        key_insights = session.state.get("key_insights", [])
        if key_insights:
            print(f"\n{Colors.BOLD}💡 Key Insights:{Colors.RESET}")
            for idx, insight in enumerate(key_insights[-3:], 1):  # Show last 3
                print(f"  {idx}. {insight[:100]}...")
        
        print(f"{Colors.CYAN}{'-' * (42 + len(label))}{Colors.RESET}\n")
    except Exception as e:
        print(f"Error displaying research state: {e}")


async def process_research_response(event):
    """Process and display research agent response events."""
    print(f"{Colors.YELLOW}Event ID: {event.id}, Author: {event.author}{Colors.RESET}")
    
    # Check for specific parts first
    if event.content and event.content.parts:
        for part in event.content.parts:
            if hasattr(part, "text") and part.text and not part.text.isspace():
                print(f"  {Colors.GREEN}Progress: {part.text.strip()[:100]}...{Colors.RESET}")
    
    # Check for final response
    final_response = None
    if event.is_final_response():
        if (
            event.content
            and event.content.parts
            and hasattr(event.content.parts[0], "text")
            and event.content.parts[0].text
        ):
            final_response = event.content.parts[0].text.strip()
            
            # Use colors and formatting to make the final response stand out
            print(
                f"\n{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}"
                f"╔══ RESEARCH FINDINGS ═══════════════════════════════════════════{Colors.RESET}"
            )
            
            # Parse and display structured results if possible
            try:
                # Try to parse as JSON for structured display
                result_data = json.loads(final_response)
                
                if "literature_review" in result_data:
                    review = result_data["literature_review"]
                    print(f"{Colors.CYAN}{Colors.BOLD}📚 Literature Review Results:{Colors.RESET}")
                    print(f"  • Topic: {review.get('query_topic', 'N/A')}")
                    print(f"  • Papers Found: {review.get('total_papers_found', 0)}")
                    print(f"  • Papers Analyzed: {len(review.get('papers_analyzed', []))}")
                    print(f"  • Key Findings: {len(review.get('key_findings', []))}")
                    print(f"  • Research Gaps: {len(review.get('research_gaps', []))}")
                    
                    # Show synthesis
                    synthesis = review.get('synthesis', '')
                    if synthesis:
                        print(f"\n{Colors.BOLD}📝 Synthesis:{Colors.RESET}")
                        print(f"{synthesis[:500]}...")
                else:
                    # Display as formatted text if not structured
                    print(f"{Colors.CYAN}{final_response}{Colors.RESET}")
                    
            except json.JSONDecodeError:
                # Not JSON, display as text
                print(f"{Colors.CYAN}{final_response}{Colors.RESET}")
            
            print(
                f"{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}"
                f"╚════════════════════════════════════════════════════════════════{Colors.RESET}\n"
            )
        else:
            print(
                f"\n{Colors.BG_RED}{Colors.WHITE}{Colors.BOLD}"
                f"==> Research Response: [No content in final event]{Colors.RESET}\n"
            )
    
    return final_response


async def call_research_agent_async(runner, user_id, session_id, query):
    """Call the research agent asynchronously with the user's query."""
    content = types.Content(role="user", parts=[types.Part(text=query)])
    
    print(
        f"\n{Colors.BG_GREEN}{Colors.BLACK}{Colors.BOLD}"
        f"--- Research Query: {query} ---{Colors.RESET}"
    )
    
    final_response_text = None
    agent_name = None
    
    # Update session state with current query
    session = runner.session_service.get_session(
        app_name=runner.app_name, user_id=user_id, session_id=session_id
    )
    updated_state = session.state.copy()
    updated_state["current_query"] = query
    runner.session_service.create_session(
        app_name=runner.app_name,
        user_id=user_id,
        session_id=session_id,
        state=updated_state
    )
    
    # Display state before processing
    display_research_state(
        runner.session_service,
        runner.app_name,
        user_id,
        session_id,
        "State BEFORE research",
    )
    
    try:
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=content
        ):
            # Capture the agent name from the event if available
            if event.author:
                agent_name = event.author
            
            response = await process_research_response(event)
            if response:
                final_response_text = response
    except Exception as e:
        print(f"{Colors.BG_RED}{Colors.WHITE}ERROR during research: {e}{Colors.RESET}")
    
    # Add the research results to history
    if final_response_text:
        try:
            result_data = json.loads(final_response_text)
            if "literature_review" in result_data:
                review = result_data["literature_review"]
                update_research_history(
                    runner.session_service,
                    runner.app_name,
                    user_id,
                    session_id,
                    {
                        "action": "literature_review",
                        "topic": review.get("query_topic", query),
                        "papers_count": len(review.get("papers_analyzed", [])),
                        "key_findings": review.get("key_findings", []),
                        "research_gaps": review.get("research_gaps", []),
                        "agent": agent_name
                    }
                )
        except:
            # If not JSON, just record the query
            update_research_history(
                runner.session_service,
                runner.app_name,
                user_id,
                session_id,
                {
                    "action": "query",
                    "query": query,
                    "agent": agent_name
                }
            )
    
    # Display state after processing
    display_research_state(
        runner.session_service,
        runner.app_name,
        user_id,
        session_id,
        "State AFTER research",
    )
    
    print(f"{Colors.YELLOW}{'-' * 60}{Colors.RESET}")
    return final_response_text