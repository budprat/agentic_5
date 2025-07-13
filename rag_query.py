#!/usr/bin/env python3
# ABOUTME: Single file to query existing Vertex AI RAG corpus
# ABOUTME: Supports command line, interactive, and batch query modes

"""
RAG Query Tool

Query an existing Vertex AI RAG corpus with multiple usage modes:
- Command line: python rag_query.py "Your question here"
- Interactive: python rag_query.py
- Batch mode: Type 'batch' in interactive mode
"""

import sys
import vertexai
try:
    from vertexai import rag
except ImportError:
    from vertexai.preview import rag
from google import genai
from google.genai.types import GenerateContentConfig, Retrieval, Tool, VertexRagStore

# Configuration
PROJECT_ID = "gen-lang-client-0871164439"
LOCATION = "us-central1"
CORPUS_ID = "2587317985924349952"  # Actual corpus ID
MODEL_ID = "gemini-2.0-flash-exp"

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Create client
client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

# Create RAG retrieval tool
corpus_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragCorpora/{CORPUS_ID}"
rag_tool = Tool(
    retrieval=Retrieval(
        vertex_rag_store=VertexRagStore(
            rag_corpora=[corpus_name],
            similarity_top_k=10,
            vector_distance_threshold=0.5,
        )
    )
)

def query_rag(question):
    """Query the RAG corpus and return response"""
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=question,
            config=GenerateContentConfig(tools=[rag_tool]),
        )
        return response.text
    except Exception as e:
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
        response = query_rag(question)
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
                print(query_rag(query))
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
    print(f"RAG Query Tool - Corpus: {CORPUS_ID}")
    
    if len(sys.argv) > 1:
        # Command line mode
        question = " ".join(sys.argv[1:])
        print(f"\nQuestion: {question}")
        print("-" * 80)
        print(query_rag(question))
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()