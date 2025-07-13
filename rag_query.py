#!/usr/bin/env python3
# ABOUTME: Query tool that simulates RAG functionality using Google API
# ABOUTME: Uses GOOGLE_API_KEY from .env file for Gemini 2.5 Pro access

"""
RAG Query Tool (Google API Version)

Since Google API doesn't directly support Vertex AI RAG corpora,
this tool provides intelligent responses about the codebase using
the Gemini 2.5 Pro model with context about the SuperClaude project.

Supports multiple usage modes:
- Command line: python rag_query.py "Your question here"
- Interactive: python rag_query.py
- Batch mode: Type 'batch' in interactive mode
"""

import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Get configuration from environment
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
MODEL_ID = os.getenv('GEMINI_MODEL', 'gemini-2.5-pro-latest')

if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY not found in .env file")
    sys.exit(1)

# Configure Google API
genai.configure(api_key=GOOGLE_API_KEY)

# Create the model
model = genai.GenerativeModel(MODEL_ID)

# Context about the codebase (based on RAG corpus content)
CODEBASE_CONTEXT = """
You are an AI assistant with knowledge about the SuperClaude codebase, which is a configuration framework for Claude Code that enhances development through automation, task management, and tool integration.

The codebase includes:

1. **Available Commands**:
   - Analysis: /analyze, /scan, /explain, /review
   - Build: /build, /deploy, /migrate
   - Manage: /task, /load, /cleanup
   - Dev: /test, /troubleshoot, /improve
   - Utils: /design, /document, /estimate, /dev-setup, /git, /spawn

2. **Core Configuration Files**:
   - CLAUDE.md - Main configuration
   - RULES.md - Development rules
   - PERSONAS.md - AI personas configuration
   - MCP.md - Model Context Protocol settings

3. **Key Components**:
   - Operations: Architecture, Migration, and Cleanup
   - Shared Resources: Pattern Files and Core System files
   - Analysis Components: Structure Analysis, Pattern Detection, Quality Metrics
   - Task Components: Title & description, Acceptance criteria, Technical requirements
   - Personas: Security, Performance, Architect, QA, Refactorer

4. **Languages Used**:
   - JavaScript/TypeScript
   - Python
   - Go
   - Java

5. **Testing Frameworks**:
   - JavaScript/TypeScript: Jest (default), Mocha + Chai, Vitest, Testing Library
   - Python: pytest (default), unittest, nose2, doctest
   - Go: Built-in testing package
   - Java: JUnit (default), TestNG, Mockito

Please answer questions based on this knowledge about the codebase.
"""

def query_with_context(question):
    """Query using Google API with codebase context"""
    try:
        # Create prompt with context
        prompt = f"""{CODEBASE_CONTEXT}

User Question: {question}

Please provide a comprehensive and accurate answer based on the codebase information provided above."""
        
        # Generate response
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        # Handle specific errors
        if "API_KEY_INVALID" in str(e):
            return "Error: Invalid API key. Please check your GOOGLE_API_KEY in .env"
        elif "RATE_LIMIT_EXCEEDED" in str(e):
            return "Error: Rate limit exceeded. Please try again later."
        elif "not found" in str(e).lower():
            # Try fallback model
            try:
                fallback_model = genai.GenerativeModel('gemini-1.5-pro-latest')
                response = fallback_model.generate_content(prompt)
                return f"(Using fallback model)\n{response.text}"
            except:
                return f"Error: Model '{MODEL_ID}' not available. Original error: {str(e)}"
        else:
            return f"Error: {str(e)}"

def batch_queries():
    """Run example batch queries"""
    questions = [
        "What is the main purpose of this codebase?",
        "What commands are available?",
        "What are the key components?",
        "What configuration files exist?",
        "What programming languages are used?"
    ]
    
    print("\nRunning batch queries...")
    print("=" * 80)
    
    for i, question in enumerate(questions, 1):
        print(f"\n{i}. {question}")
        print("-" * 80)
        response = query_with_context(question)
        print(response)

def interactive_mode():
    """Run interactive query mode"""
    print("\nInteractive Mode - Type 'exit' to quit, 'batch' for examples")
    print("=" * 80)
    
    while True:
        try:
            query = input("\nYour question: ").strip()
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("\nGoodbye!")
                break
            elif query.lower() == 'batch':
                batch_queries()
            elif query:
                print("\nResponse:")
                print("-" * 80)
                print(query_with_context(query))
                print("-" * 80)
            else:
                print("Please enter a question.")
                
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Main function"""
    print(f"RAG Query Tool (Google API Version)")
    print(f"Model: {MODEL_ID}")
    print(f"Using: GOOGLE_API_KEY authentication")
    print("Note: Simulating RAG with embedded codebase knowledge")
    
    if len(sys.argv) > 1:
        # Command line mode
        question = " ".join(sys.argv[1:])
        print(f"\nQuestion: {question}")
        print("-" * 80)
        print(query_with_context(question))
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()