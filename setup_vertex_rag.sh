#!/bin/bash
# ABOUTME: Script to create Vertex AI RAG corpus and import files
# ABOUTME: Uses gcloud AI commands to set up RAG for code search

set -e

# Configuration
PROJECT_ID="gen-lang-client-0871164439"
LOCATION="us-central1"
BUCKET_NAME="sankhya-gen-lang-client-0871164439"
GCS_FOLDER_PATH="sankhya"
EMBEDDING_MODEL="text-embedding-005"
MODEL_ID="gemini-2.5-pro-preview-06-05"
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# Generate unique IDs
UUID=$(uuidgen | tr '[:upper:]' '[:lower:]' || date +%s)
RAG_CORPUS_NAME="rag-corpus-code-${UUID}"
RAG_ENGINE_NAME="rag-engine-code-${UUID}"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting Vertex AI RAG Setup"
echo "Configuration:"
echo "  - Project: $PROJECT_ID"
echo "  - Location: $LOCATION"
echo "  - Corpus Name: $RAG_CORPUS_NAME"
echo "  - Model: $MODEL_ID"
echo "  - Chunk Size: $CHUNK_SIZE"
echo "  - Chunk Overlap: $CHUNK_OVERLAP"

# Note: Direct gcloud commands for RAG are limited. 
# We'll prepare the configuration for API calls instead

echo ""
echo "Creating RAG configuration files..."

# Create corpus configuration
cat > rag_corpus_config.json << EOF
{
  "displayName": "$RAG_CORPUS_NAME",
  "description": "Codebase files from https://github.com/google/adk-python",
  "corpus": {
    "ragEmbeddingModelConfig": {
      "vertexPredictionEndpoint": {
        "endpoint": "projects/$PROJECT_ID/locations/$LOCATION/publishers/google/models/$EMBEDDING_MODEL"
      }
    }
  }
}
EOF

# Create import configuration
cat > rag_import_config.json << EOF
{
  "importRagFilesConfig": {
    "gcsSource": {
      "uris": ["gs://$BUCKET_NAME/$GCS_FOLDER_PATH/"]
    },
    "ragFileChunkingConfig": {
      "chunkSize": $CHUNK_SIZE,
      "chunkOverlap": $CHUNK_OVERLAP
    }
  }
}
EOF

echo ""
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Configuration files created:"
echo "  - rag_corpus_config.json"
echo "  - rag_import_config.json"

echo ""
echo "To create the RAG corpus using the Vertex AI API, you would need to:"
echo "1. Use the Vertex AI Python SDK or REST API to create the corpus"
echo "2. Import the files from GCS using the import configuration"
echo "3. Create a retrieval tool for querying"

echo ""
echo "Alternative: Use Vertex AI Studio"
echo "Visit: https://console.cloud.google.com/vertex-ai/generative/language/create/text"
echo "And configure RAG with:"
echo "  - Corpus: $RAG_CORPUS_NAME"
echo "  - Source: gs://$BUCKET_NAME/$GCS_FOLDER_PATH/"
echo "  - Model: $MODEL_ID"