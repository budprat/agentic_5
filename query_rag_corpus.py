#!/usr/bin/env python3
# Query script for RAG corpus created at 2025-07-13T16:35:04.029133

import vertexai
from google import genai
from google.genai.types import GenerateContentConfig, Retrieval, Tool, VertexRagStore

# Initialize
vertexai.init(project="gen-lang-client-0871164439", location="us-central1")
client = genai.Client(vertexai=True, project="gen-lang-client-0871164439", location="us-central1")

# Create retrieval tool
rag_retrieval_tool = Tool(
    retrieval=Retrieval(
        vertex_rag_store=VertexRagStore(
            rag_resources=[{"rag_corpus": "projects/616868565535/locations/us-central1/ragCorpora/8207810320882728960"}],
            similarity_top_k=10,
            vector_distance_threshold=0.5,
        )
    )
)

# Interactive query loop
print("RAG Query Tool - Type 'exit' to quit")
print("-" * 80)

while True:
    query = input("\nEnter your question about the codebase: ")
    if query.lower() in ['exit', 'quit', 'q']:
        break
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro-preview-06-05",
            contents=query,
            config=GenerateContentConfig(tools=[rag_retrieval_tool]),
        )
        print("\nResponse:")
        print(response.text)
        print("-" * 80)
    except Exception as e:
        print(f"Error: {e}")
