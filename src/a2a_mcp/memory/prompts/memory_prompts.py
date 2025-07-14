# ABOUTME: Memory-aware prompt templates for agents with memory service integration
# ABOUTME: Provides system prompts, user prompts, and context injection templates

"""Memory-aware prompt templates for A2A agents."""

from typing import Dict, List, Optional


class MemoryPrompts:
    """Collection of memory-aware prompt templates."""
    
    # System prompts that inform the agent about memory capabilities
    SYSTEM_PROMPTS = {
        "base": """You have access to a memory service that stores and retrieves past conversations and context. 
This allows you to provide more personalized and contextually relevant responses based on previous interactions.""",
        
        "with_search": """You have access to conversation history through a memory service. Before responding to queries, 
relevant past conversations will be automatically retrieved to provide context. Use this information to:
- Reference previous discussions when relevant
- Maintain consistency with past decisions and preferences
- Provide personalized responses based on user history
- Build upon previous conversations rather than starting fresh""",
        
        "orchestrator": """As an orchestrator, you have access to memory of past agent interactions and decisions. 
Use this to:
- Track ongoing multi-agent tasks and their progress
- Remember successful delegation patterns
- Avoid repeating failed approaches
- Maintain context across complex, multi-step workflows""",
        
        "specialist": """You have access to domain-specific memory related to your area of expertise. 
This includes past analyses, decisions, and user preferences within your domain. Use this context to provide 
more informed and consistent specialized advice.""",
        
        "no_memory": """Note: Memory service is currently unavailable. Proceed with the current context only."""
    }
    
    # Templates for injecting memory context into prompts
    CONTEXT_INJECTION_TEMPLATES = {
        "conversational": """Based on our previous conversations:

{memory_content}

Now, regarding your current question:""",
        
        "structured": """## Relevant Context from Memory

{memory_results}

## Current Request

Please consider the above context when responding to:""",
        
        "summary": """## Previous Interaction Summary

- Last discussed: {last_topic}
- Key decisions: {decisions}
- User preferences: {preferences}

## Current Context""",
        
        "empty": """No relevant previous context found. Proceeding with current information only."""
    }
    
    # Templates for formatting memory search results
    MEMORY_RESULT_FORMATS = {
        "detailed": """### Memory Result {index}
**Date**: {timestamp}
**Session**: {session_id}
**Relevance**: {score:.2f}

**Context**:
{content}

**Key Points**:
{summary}
---""",
        
        "concise": """[{timestamp}] {summary} (relevance: {score:.2f})""",
        
        "bullets": """• {summary}
  - Session: {session_id}
  - Relevance: {score:.2f}"""
    }
    
    # Prompts for different memory operations
    OPERATION_PROMPTS = {
        "search_guidance": """Searching memory for: {query}
Looking for relevant past conversations, decisions, and context...""",
        
        "save_confirmation": """This conversation has been saved to memory for future reference.""",
        
        "memory_error": """Note: Memory service encountered an error. Proceeding without historical context.""",
        
        "first_interaction": """This appears to be our first interaction. I'll remember this conversation for future reference."""
    }
    
    @staticmethod
    def build_system_prompt(
        agent_type: str = "base",
        memory_enabled: bool = True,
        search_enabled: bool = True,
        custom_additions: Optional[str] = None
    ) -> str:
        """Build a complete system prompt with memory awareness.
        
        Args:
            agent_type: Type of agent (base, orchestrator, specialist)
            memory_enabled: Whether memory is enabled
            search_enabled: Whether memory search is enabled
            custom_additions: Additional custom prompt content
            
        Returns:
            Complete system prompt
        """
        if not memory_enabled:
            base_prompt = MemoryPrompts.SYSTEM_PROMPTS["no_memory"]
        elif search_enabled:
            base_prompt = MemoryPrompts.SYSTEM_PROMPTS.get(
                agent_type, 
                MemoryPrompts.SYSTEM_PROMPTS["with_search"]
            )
        else:
            base_prompt = MemoryPrompts.SYSTEM_PROMPTS.get(
                agent_type,
                MemoryPrompts.SYSTEM_PROMPTS["base"]
            )
            
        if custom_additions:
            return f"{base_prompt}\n\n{custom_additions}"
        return base_prompt
    
    @staticmethod
    def inject_memory_context(
        user_prompt: str,
        memory_results: List[Dict],
        format_type: str = "conversational",
        max_results: int = 5
    ) -> str:
        """Inject memory context into a user prompt.
        
        Args:
            user_prompt: Original user prompt
            memory_results: List of memory search results
            format_type: How to format the context
            max_results: Maximum number of results to include
            
        Returns:
            Enhanced prompt with memory context
        """
        if not memory_results:
            context = MemoryPrompts.CONTEXT_INJECTION_TEMPLATES["empty"]
        else:
            # Format memory results
            formatted_results = MemoryPrompts._format_memory_results(
                memory_results[:max_results],
                format_type
            )
            
            # Select appropriate template
            template = MemoryPrompts.CONTEXT_INJECTION_TEMPLATES.get(
                format_type,
                MemoryPrompts.CONTEXT_INJECTION_TEMPLATES["conversational"]
            )
            
            # Inject formatted results
            if format_type == "conversational":
                context = template.format(memory_content=formatted_results)
            elif format_type == "structured":
                context = template.format(memory_results=formatted_results)
            else:
                context = formatted_results
                
        return f"{context}\n\n{user_prompt}"
    
    @staticmethod
    def _format_memory_results(
        results: List[Dict],
        format_type: str
    ) -> str:
        """Format memory search results.
        
        Args:
            results: Memory search results
            format_type: Format to use
            
        Returns:
            Formatted results string
        """
        if format_type == "detailed":
            template = MemoryPrompts.MEMORY_RESULT_FORMATS["detailed"]
            formatted = []
            for i, result in enumerate(results, 1):
                formatted.append(template.format(
                    index=i,
                    timestamp=result.get("timestamp", "Unknown"),
                    session_id=result.get("session_id", "Unknown"),
                    score=result.get("score", 0.0),
                    content=result.get("content", ""),
                    summary=result.get("summary", result.get("content", "")[:100] + "...")
                ))
            return "\n".join(formatted)
            
        elif format_type == "concise":
            template = MemoryPrompts.MEMORY_RESULT_FORMATS["concise"]
            formatted = []
            for result in results:
                formatted.append(template.format(
                    timestamp=result.get("timestamp", "Unknown"),
                    summary=result.get("summary", result.get("content", "")[:100] + "..."),
                    score=result.get("score", 0.0)
                ))
            return "\n".join(formatted)
            
        else:  # conversational
            # Extract key information in a natural way
            contents = []
            for result in results:
                content = result.get("content", "")
                if content:
                    contents.append(f"- {content}")
            return "\n".join(contents)
    
    @staticmethod
    def create_memory_aware_prompt(
        agent_name: str,
        agent_type: str,
        base_system_prompt: str,
        memory_config: Dict
    ) -> str:
        """Create a complete memory-aware system prompt for an agent.
        
        Args:
            agent_name: Name of the agent
            agent_type: Type of agent
            base_system_prompt: Original system prompt
            memory_config: Memory configuration dict
            
        Returns:
            Enhanced system prompt
        """
        memory_enabled = memory_config.get("enabled", False)
        search_enabled = memory_config.get("search_before_response", False)
        
        # Build memory awareness addition
        memory_addition = MemoryPrompts.build_system_prompt(
            agent_type=agent_type,
            memory_enabled=memory_enabled,
            search_enabled=search_enabled
        )
        
        # Add agent-specific context
        if memory_enabled:
            agent_context = f"\nYour memory is stored under the identifier '{agent_name}'."
            if app_name := memory_config.get("app_name"):
                agent_context = f"\nYour memory is stored under the identifier '{app_name}'."
            memory_addition += agent_context
        
        # Combine with base prompt
        return f"{base_system_prompt}\n\n{memory_addition}"


# Example usage templates
MEMORY_PROMPT_EXAMPLES = {
    "user_preference_recall": """I see from our previous conversations that you prefer {preference}. 
I'll keep that in mind for this response.""",
    
    "task_continuation": """Continuing from where we left off on {date}, when we were working on {task}...""",
    
    "context_reference": """As we discussed previously regarding {topic}, {summary}. 
Building on that foundation...""",
    
    "decision_consistency": """In our last discussion about this, we decided to {decision}. 
Shall we proceed with that approach, or would you like to reconsider?""",
    
    "no_previous_context": """I don't have any previous context about this topic in my memory. 
Let me help you with this fresh perspective."""
}