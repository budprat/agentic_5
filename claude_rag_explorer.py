#!/usr/bin/env python3
# ABOUTME: RAG exploration tool for Claude to understand SuperClaude repository
# ABOUTME: Enables Claude to systematically learn from the RAG corpus

"""
Claude's RAG Explorer for SuperClaude

This tool is designed for Claude to use when exploring and understanding
the SuperClaude repository stored in the RAG corpus. It provides structured
query methods to build comprehensive knowledge.
"""

import os
import sys
from pathlib import Path

# Simple dotenv loader
def load_dotenv():
    env_path = Path('.env')
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip('"').strip("'")

# Load environment
load_dotenv()

# Configuration
PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'gen-lang-client-0871164439')
LOCATION = os.getenv('GCP_LOCATION', 'us-central1')
CORPUS_ID = "2587317985924349952"
MODEL_ID = os.getenv('GEMINI_MODEL', 'gemini-2.5-pro-latest')

# Import and setup
try:
    import vertexai
    from google.auth import default
    from google import genai
    from google.genai.types import GenerateContentConfig, Retrieval, Tool, VertexRagStore
    
    credentials, project = default()
    PROJECT_ID = project or PROJECT_ID
    
    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        credentials=credentials
    )
    
    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION
    )
    
    corpus_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragCorpora/{CORPUS_ID}"
    rag_tool = Tool(
        retrieval=Retrieval(
            vertex_rag_store=VertexRagStore(
                rag_corpora=[corpus_name],
                similarity_top_k=15,
                vector_distance_threshold=0.3,
            )
        )
    )
    
    def ask_rag(question):
        """Direct RAG query"""
        try:
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=question,
                config=GenerateContentConfig(tools=[rag_tool]),
            )
            return response.text
        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                response = client.models.generate_content(
                    model="gemini-2.0-flash-exp",
                    contents=question,
                    config=GenerateContentConfig(tools=[rag_tool]),
                )
                return response.text
            else:
                return f"Error: {str(e)}"
    
    READY = True
    
except ImportError:
    READY = False
    def ask_rag(question):
        return "RAG not available - missing packages"

# Exploration functions for Claude to use
def explore_architecture():
    """Understand SuperClaude's core architecture"""
    questions = [
        "What is the overall architecture of SuperClaude? What are its main components?",
        "How do the .claude/ directory and its subdirectories work?",
        "What is the purpose of CLAUDE.md and how does it differ from standard Claude?"
    ]
    
    for q in questions:
        print(f"\n🔍 {q}")
        print(f"📖 {ask_rag(q)}\n")

def explore_commands():
    """Learn about available commands"""
    questions = [
        "List all slash commands available in SuperClaude with brief descriptions",
        "What are the most powerful commands for development automation?",
        "How do commands like /spawn, /task, and /analyze work?"
    ]
    
    for q in questions:
        print(f"\n🔍 {q}")
        print(f"📖 {ask_rag(q)}\n")

def explore_personas():
    """Understand the persona system"""
    questions = [
        "What personas are available in SuperClaude and what are their specialties?",
        "How do personas collaborate and when are they automatically activated?",
        "What are cognitive archetypes in SuperClaude?"
    ]
    
    for q in questions:
        print(f"\n🔍 {q}")
        print(f"📖 {ask_rag(q)}\n")

def explore_rules():
    """Learn about rules and standards"""
    questions = [
        "What rules does SuperClaude enforce and how do they work?",
        "What are the typescript-best-practices.md guidelines?",
        "How does SuperClaude handle code quality, testing, and security?"
    ]
    
    for q in questions:
        print(f"\n🔍 {q}")
        print(f"📖 {ask_rag(q)}\n")

def explore_workflows():
    """Understand development workflows"""
    questions = [
        "What development workflows does SuperClaude support?",
        "How does task management work with TodoWrite?",
        "What is the recommended git workflow in SuperClaude?"
    ]
    
    for q in questions:
        print(f"\n🔍 {q}")
        print(f"📖 {ask_rag(q)}\n")

def explore_mcp():
    """Learn about MCP integration"""
    questions = [
        "What MCP servers are configured in SuperClaude?",
        "How does MCP enhance SuperClaude's capabilities?",
        "What are the most useful MCP tools for development?"
    ]
    
    for q in questions:
        print(f"\n🔍 {q}")
        print(f"📖 {ask_rag(q)}\n")

def explore_advanced():
    """Discover advanced features"""
    questions = [
        "What are SuperClaude's advanced features like UltraCompressed mode?",
        "How does token economy and performance optimization work?",
        "What is introspection mode and when should it be used?"
    ]
    
    for q in questions:
        print(f"\n🔍 {q}")
        print(f"📖 {ask_rag(q)}\n")

def quick_lookup(topic):
    """Quick lookup for specific topics"""
    return ask_rag(f"Explain {topic} in SuperClaude")

def find_examples(feature):
    """Find examples of how to use a feature"""
    return ask_rag(f"Show examples of using {feature} in SuperClaude")

def compare_approach(task):
    """Compare SuperClaude approach vs standard approach"""
    return ask_rag(f"How does SuperClaude handle {task} differently from standard Claude?")

# Main function for testing
if __name__ == "__main__":
    if not READY:
        print("❌ RAG not available - missing required packages")
        sys.exit(1)
    
    print("🤖 Claude's SuperClaude Explorer")
    print("=" * 50)
    print(f"RAG Corpus: {CORPUS_ID}")
    print(f"Ready to explore!")
    print("\nAvailable functions:")
    print("- explore_architecture()")
    print("- explore_commands()")
    print("- explore_personas()")
    print("- explore_rules()")
    print("- explore_workflows()")
    print("- explore_mcp()")
    print("- explore_advanced()")
    print("- quick_lookup(topic)")
    print("- find_examples(feature)")
    print("- compare_approach(task)")
    
    # Example usage
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
        print(f"\n🔍 Looking up: {topic}")
        print(f"📖 {quick_lookup(topic)}")