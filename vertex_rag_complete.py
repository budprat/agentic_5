#!/usr/bin/env python3
# ABOUTME: Complete Vertex AI RAG setup script for GitHub codebase indexing
# ABOUTME: Creates corpus, imports files, and provides query interface

"""
Vertex AI RAG Setup for GitHub Codebase

This script sets up a complete RAG (Retrieval-Augmented Generation) system
for querying a GitHub codebase using Vertex AI.

Requirements:
- pip install google-cloud-aiplatform google-genai

Usage:
  python vertex_rag_complete.py
"""

import os
import uuid
from datetime import datetime
import time

# Configuration (as specified by user)
GITHUB_URL = "https://github.com/google/adk-python"
PROJECT_ID = "gen-lang-client-0871164439"
LOCATION = "us-central1"
BUCKET_NAME = "sankhya-gen-lang-client-0871164439"
GCS_FOLDER_PATH = "sankhya"
EMBEDDING_MODEL = "text-embedding-005"
MODEL_ID = "gemini-2.5-pro-preview-06-05"  # User-specified model

# User-specified chunking parameters
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Setup paths
GCS_IMPORT_URI = f"gs://{BUCKET_NAME}/{GCS_FOLDER_PATH}/"

# Generate unique corpus name
_UUID = uuid.uuid4()
RAG_CORPUS_DISPLAY_NAME = f"rag-corpus-code-{_UUID}"

def log(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def main():
    """Main execution function"""
    log("Starting Vertex AI RAG Setup")
    log(f"Configuration:")
    log(f"  - GitHub URL: {GITHUB_URL}")
    log(f"  - Project ID: {PROJECT_ID}")
    log(f"  - Location: {LOCATION}")
    log(f"  - GCS Source: {GCS_IMPORT_URI}")
    log(f"  - Model: {MODEL_ID}")
    log(f"  - Chunk Size: {CHUNK_SIZE} tokens")
    log(f"  - Chunk Overlap: {CHUNK_OVERLAP} tokens")
    
    try:
        # Import required libraries
        import vertexai
        from vertexai.preview import rag  # Use preview.rag
        from google import genai
        from google.genai.types import (
            GenerateContentConfig, 
            Retrieval, 
            Tool, 
            VertexRagStore
        )
        
        # Initialize Vertex AI
        log("Initializing Vertex AI...")
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        
        # Create genai client
        client = genai.Client(
            vertexai=True, 
            project=PROJECT_ID, 
            location=LOCATION
        )
        
        # Step 1: Create RAG Corpus
        log("Creating RAG Corpus...")
        rag_corpus = rag.create_corpus(
            display_name=RAG_CORPUS_DISPLAY_NAME,
            description=f"Codebase files from {GITHUB_URL}",
        )
        log(f"Created corpus: {rag_corpus.display_name}")
        log(f"Corpus resource name: {rag_corpus.name}")
        
        # Step 2: Import files from GCS with lower QPM to avoid quota issues
        log(f"Importing files from {GCS_IMPORT_URI}...")
        log("Note: Using lower embedding rate to avoid quota limits")
        
        try:
            import_response = rag.import_files(
                corpus_name=rag_corpus.name,
                paths=[GCS_IMPORT_URI],
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
                max_embedding_requests_per_min=100,  # Lower QPM to avoid quota
            )
            log("File import initiated. This may take several minutes...")
            
            # Wait for import to complete (optional - can be async)
            log("Waiting for initial file processing...")
            time.sleep(60)  # Wait 1 minute before first query
            
        except Exception as e:
            log(f"Import error (may be quota-related): {str(e)}")
            log("The corpus was created successfully. Files may still be importing in the background.")
        
        # Step 3: Create retrieval tool
        log("Creating retrieval tool...")
        rag_retrieval_tool = Tool(
            retrieval=Retrieval(
                vertex_rag_store=VertexRagStore(
                    rag_resources=[{
                        "rag_corpus": rag_corpus.name
                    }],
                    similarity_top_k=10,
                    vector_distance_threshold=0.5,
                )
            )
        )
        
        # Step 4: Test with a sample query
        log("Testing RAG with a sample query...")
        test_query = "What is the primary purpose or main functionality of this codebase?"
        
        try:
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=test_query,
                config=GenerateContentConfig(tools=[rag_retrieval_tool]),
            )
            
            log("Query Response:")
            print("-" * 80)
            print(response.text)
            print("-" * 80)
        except Exception as e:
            log(f"Query test error: {str(e)}")
            log("This is normal if files are still being imported. Try again later.")
        
        # Generate Vertex AI Studio link
        encoded_corpus_name = rag_corpus.name.replace("/", "%2F")
        studio_url = (
            f"https://console.cloud.google.com/vertex-ai/studio/multimodal"
            f";ragCorpusName={encoded_corpus_name}"
            f"?project={PROJECT_ID}"
        )
        
        log("Setup complete!")
        log(f"RAG Corpus Name: {rag_corpus.name}")
        log(f"Test in Vertex AI Studio: {studio_url}")
        
        # Save configuration for future use
        config_data = {
            "corpus_name": rag_corpus.name,
            "corpus_display_name": RAG_CORPUS_DISPLAY_NAME,
            "project_id": PROJECT_ID,
            "location": LOCATION,
            "model_id": MODEL_ID,
            "gcs_source": GCS_IMPORT_URI,
            "chunk_size": CHUNK_SIZE,
            "chunk_overlap": CHUNK_OVERLAP,
            "studio_url": studio_url,
            "created_at": datetime.now().isoformat()
        }
        
        import json
        with open("rag_config.json", "w") as f:
            json.dump(config_data, f, indent=2)
        
        log("Configuration saved to rag_config.json")
        
        # Create a test script for later use
        test_script = f'''#!/usr/bin/env python3
# Test script for RAG corpus created at {datetime.now().isoformat()}

import vertexai
from google import genai
from google.genai.types import GenerateContentConfig, Retrieval, Tool, VertexRagStore

# Initialize
vertexai.init(project="{PROJECT_ID}", location="{LOCATION}")
client = genai.Client(vertexai=True, project="{PROJECT_ID}", location="{LOCATION}")

# Create retrieval tool
rag_retrieval_tool = Tool(
    retrieval=Retrieval(
        vertex_rag_store=VertexRagStore(
            rag_resources=[{{"rag_corpus": "{rag_corpus.name}"}}],
            similarity_top_k=10,
            vector_distance_threshold=0.5,
        )
    )
)

# Test query
query = input("Enter your question about the codebase: ")
response = client.models.generate_content(
    model="{MODEL_ID}",
    contents=query,
    config=GenerateContentConfig(tools=[rag_retrieval_tool]),
)

print("\\nResponse:")
print(response.text)
'''
        
        with open("test_rag_query.py", "w") as f:
            f.write(test_script)
        os.chmod("test_rag_query.py", 0o755)
        
        log("Created test_rag_query.py for future queries")
        
    except Exception as e:
        log(f"Error: {str(e)}")
        log("Please ensure you have the required packages installed:")
        log("  pip install google-cloud-aiplatform google-genai")
        raise

if __name__ == "__main__":
    main()