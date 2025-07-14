#!/usr/bin/env python3
# ABOUTME: Example demonstrating how to use memory-aware prompts in agents
# ABOUTME: Shows integration of memory search results with prompt templates

"""Example of using memory-aware prompts in A2A agents."""

import asyncio
from typing import Dict, List, Optional

from a2a_mcp.memory.prompts import MemoryPrompts
from a2a_mcp.memory.memory_integration import MemoryIntegration
from a2a_mcp.memory.vertex_ai_memory_bank import VertexAIMemoryBankService


class MemoryAwareAgentExample:
    """Example agent that uses memory-aware prompts."""
    
    def __init__(self, agent_name: str, agent_type: str = "specialist"):
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.memory_integration = None
        self.base_system_prompt = "You are a helpful AI assistant."
        
    async def initialize_memory(self, memory_config: Dict):
        """Initialize memory service with configuration."""
        if memory_config.get("enabled", False):
            # Initialize memory service
            memory_service = VertexAIMemoryBankService(
                project_id=memory_config.get("project_id"),
                location=memory_config.get("location", "us-central1"),
                agent_engine_id=memory_config.get("agent_engine_id")
            )
            
            # Create memory integration
            self.memory_integration = MemoryIntegration(
                memory_service=memory_service,
                app_name=memory_config.get("app_name", self.agent_name),
                auto_save=memory_config.get("auto_save_sessions", True)
            )
            
            # Create memory-aware system prompt
            self.system_prompt = MemoryPrompts.create_memory_aware_prompt(
                agent_name=self.agent_name,
                agent_type=self.agent_type,
                base_system_prompt=self.base_system_prompt,
                memory_config=memory_config
            )
        else:
            self.system_prompt = self.base_system_prompt
            
    async def process_with_memory(self, user_input: str, user_id: Optional[str] = None):
        """Process user input with memory context."""
        
        # 1. Search memory for relevant context
        memory_context = []
        if self.memory_integration:
            print(f"🔍 Searching memory for relevant context...")
            memory_results = await self.memory_integration.search_memory(
                query=user_input,
                user_id=user_id,
                top_k=5
            )
            
            if memory_results:
                print(f"📚 Found {len(memory_results)} relevant memory results")
                memory_context = memory_results
            else:
                print("💭 No relevant memory found, proceeding with fresh context")
        
        # 2. Enhance prompt with memory context
        if memory_context:
            enhanced_prompt = MemoryPrompts.inject_memory_context(
                user_prompt=user_input,
                memory_results=memory_context,
                format_type="conversational" if self.agent_type == "specialist" else "structured",
                max_results=3
            )
        else:
            enhanced_prompt = user_input
            
        # 3. Generate response (simulated)
        response = await self._generate_response(enhanced_prompt)
        
        # 4. Save interaction to memory
        if self.memory_integration:
            await self.memory_integration.add_message(
                role="user",
                content=user_input,
                user_id=user_id
            )
            await self.memory_integration.add_message(
                role="assistant",
                content=response
            )
            
        return response
    
    async def _generate_response(self, enhanced_prompt: str) -> str:
        """Simulate response generation with enhanced prompt."""
        print("\n📝 Enhanced Prompt:")
        print("-" * 50)
        print(enhanced_prompt)
        print("-" * 50)
        
        # In a real implementation, this would call the LLM
        return "This is a simulated response that would consider the memory context provided."
    
    def demonstrate_prompt_patterns(self):
        """Show different memory prompt patterns."""
        print("\n🎯 Memory Prompt Patterns:\n")
        
        # 1. System Prompts
        print("1. System Prompts for Different Agent Types:")
        print("-" * 50)
        for agent_type in ["base", "orchestrator", "specialist"]:
            prompt = MemoryPrompts.build_system_prompt(
                agent_type=agent_type,
                memory_enabled=True,
                search_enabled=True
            )
            print(f"\n{agent_type.upper()}:")
            print(prompt)
        
        # 2. Context Injection Examples
        print("\n\n2. Context Injection Templates:")
        print("-" * 50)
        
        sample_results = [
            {
                "content": "User prefers technical explanations with examples",
                "score": 0.92,
                "timestamp": "2024-01-10",
                "session_id": "sess_123"
            },
            {
                "content": "Previously discussed Python async patterns",
                "score": 0.87,
                "timestamp": "2024-01-12",
                "session_id": "sess_124"
            }
        ]
        
        for format_type in ["conversational", "structured", "concise"]:
            print(f"\n{format_type.upper()} FORMAT:")
            enhanced = MemoryPrompts.inject_memory_context(
                user_prompt="How do I implement async functions?",
                memory_results=sample_results,
                format_type=format_type
            )
            print(enhanced)
        
        # 3. Memory-Aware Examples
        print("\n\n3. Memory-Aware Response Examples:")
        print("-" * 50)
        for example_name, template in MEMORY_PROMPT_EXAMPLES.items():
            print(f"\n{example_name.upper()}:")
            print(template)


async def main():
    """Run the memory prompt example."""
    print("🧠 Memory-Aware Prompt Example\n")
    
    # Create example agent
    agent = MemoryAwareAgentExample(
        agent_name="technical_assistant",
        agent_type="specialist"
    )
    
    # Memory configuration
    memory_config = {
        "enabled": True,
        "app_name": "technical_assistant",
        "auto_save_sessions": True,
        "search_before_response": True,
        "project_id": "your-project-id",
        "location": "us-central1",
        "agent_engine_id": "your-agent-engine-id"
    }
    
    # Initialize with memory
    print("Initializing memory service...")
    # await agent.initialize_memory(memory_config)  # Commented out as it requires real credentials
    
    # Demonstrate prompt patterns
    agent.demonstrate_prompt_patterns()
    
    # Show how prompts would be used in practice
    print("\n\n4. Practical Usage Example:")
    print("-" * 50)
    print("\nUser Input: 'Can you help me with async Python code?'")
    print("\nWith memory context, the prompt might become:")
    
    enhanced_example = """Based on our previous conversations:

- User prefers technical explanations with examples
- Previously discussed Python async patterns

Now, regarding your current question:

Can you help me with async Python code?"""
    
    print(enhanced_example)
    
    print("\n\n✅ Memory-aware prompts help agents:")
    print("- Maintain context across conversations")
    print("- Provide personalized responses")
    print("- Build on previous interactions")
    print("- Avoid repeating information")


if __name__ == "__main__":
    asyncio.run(main())