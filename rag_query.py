#!/usr/bin/env python3
# ABOUTME: Query tool for Vertex AI RAG corpus using ADC authentication
# ABOUTME: Single file solution for querying the actual RAG corpus

"""
RAG Query Tool

This tool queries your actual Vertex AI RAG corpus containing 76 files from SuperClaude.
It uses Application Default Credentials (ADC) for authentication.

Setup:
1. Run: gcloud auth application-default login
2. Or use the ADC file already configured in .env

Usage:
- Command line: python rag_query.py "Your question"
- Interactive: python rag_query.py
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

# Try to import required packages
try:
    import vertexai
    from google.auth import default
    from google import genai
    from google.genai.types import GenerateContentConfig, Retrieval, Tool, VertexRagStore
    
    # Initialize Vertex AI
    credentials, project = default()
    PROJECT_ID = project or PROJECT_ID
    
    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        credentials=credentials
    )
    
    # Create genai client
    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION
    )
    
    # Create RAG tool
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
        """Query the RAG corpus"""
        try:
            # Try preferred model first
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=question,
                config=GenerateContentConfig(tools=[rag_tool]),
            )
            return response.text
        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                # Fallback model
                response = client.models.generate_content(
                    model="gemini-2.0-flash-exp",
                    contents=question,
                    config=GenerateContentConfig(tools=[rag_tool]),
                )
                return response.text
            else:
                return f"Error: {str(e)}"
    
    PACKAGES_AVAILABLE = True
    
except ImportError as e:
    PACKAGES_AVAILABLE = False
    MISSING_PACKAGE = str(e)
    
    # Fallback: Try direct API if available
    try:
        import requests
        import json
        
        GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
        
        def query_rag(question):
            """Fallback: Query using direct API"""
            if not GOOGLE_API_KEY:
                return "Error: GOOGLE_API_KEY not found in .env"
                
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ID}:generateContent"
            headers = {"Content-Type": "application/json"}
            data = {"contents": [{"parts": [{"text": question}]}]}
            
            response = requests.post(
                url,
                headers=headers,
                json=data,
                params={"key": GOOGLE_API_KEY}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                return f"API Error: {response.status_code}"
                
        REQUESTS_AVAILABLE = True
    except ImportError:
        REQUESTS_AVAILABLE = False
        def query_rag(question):
            return "Error: Required packages not available. Please install: google-cloud-aiplatform google-auth google-genai"

def main():
    """Main function"""
    print(f"RAG Query Tool")
    print(f"=" * 50)
    
    if PACKAGES_AVAILABLE:
        print(f"✅ Using Vertex AI RAG")
        print(f"   Project: {PROJECT_ID}")
        print(f"   Corpus: {CORPUS_ID} (76 SuperClaude files)")
        print(f"   Model: {MODEL_ID}")
    else:
        if REQUESTS_AVAILABLE:
            print(f"⚠️  Using fallback Google API (no RAG access)")
            print(f"   Model: {MODEL_ID}")
        else:
            print(f"❌ Required packages not installed")
            print(f"   Missing: {MISSING_PACKAGE if 'MISSING_PACKAGE' in locals() else 'google packages'}")
            print(f"\nTo access your RAG corpus, install:")
            print(f"   pip install google-cloud-aiplatform google-auth google-genai")
            return
    
    print(f"=" * 50)
    
    if len(sys.argv) > 1:
        # Command line mode
        question = " ".join(sys.argv[1:])
        print(f"\nQuestion: {question}")
        print("-" * 80)
        print(query_rag(question))
    else:
        # Interactive mode
        print("\nInteractive Mode - Type 'exit' to quit")
        
        while True:
            try:
                query = input("\nYour question: ").strip()
                
                if query.lower() in ['exit', 'quit', 'q']:
                    print("\nGoodbye!")
                    break
                elif query:
                    print("\nResponse:")
                    print("-" * 80)
                    print(query_rag(query))
                    print("-" * 80)
                    
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except EOFError:
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    main()