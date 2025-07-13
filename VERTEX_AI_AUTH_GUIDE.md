# Vertex AI Authentication Guide

This guide explains how to authenticate with Vertex AI to query your RAG corpus.

## Current Setup

- **Project ID**: `gen-lang-client-0871164439`
- **Location**: `us-central1`
- **RAG Corpus ID**: `2587317985924349952`
- **Corpus Name**: `rag-corpus-code-4cf0475a-2551-4530-8079-3a1480197d61`

## Authentication Methods

### Method 1: Google API Key (Current - `rag_query.py`)

This is what you're currently using with `rag_query.py`. It uses the `GOOGLE_API_KEY` from your `.env` file but **cannot access the actual Vertex AI RAG corpus**. It simulates RAG functionality with embedded knowledge.

```bash
# Already configured in .env
python rag_query.py "Your question here"
```

### Method 2: Application Default Credentials (Recommended - `vertex_ai_rag_query.py`)

This method allows you to access your **actual RAG corpus** in Vertex AI.

#### Step 1: Set up ADC

Run the setup script:
```bash
./setup_adc.sh
```

Or manually run:
```bash
gcloud auth application-default login
```

This will:
1. Open a browser window
2. Ask you to log in with your Google account
3. Create credentials at `~/.config/gcloud/application_default_credentials.json`

#### Step 2: Test Authentication

```bash
python test_vertex_auth.py
```

#### Step 3: Query Your RAG Corpus

```bash
python vertex_ai_rag_query.py "What commands are available in SuperClaude?"
```

### Method 3: Service Account (Production)

For production or automated environments:

1. Create a service account in GCP Console
2. Download the JSON key file
3. Set the environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
   ```

## File Descriptions

- **`rag_query.py`**: Uses Google API Key, simulates RAG with embedded knowledge
- **`vertex_ai_rag_query.py`**: Uses ADC, queries actual Vertex AI RAG corpus
- **`test_vertex_auth.py`**: Tests if authentication is properly configured
- **`setup_adc.sh`**: Helper script to set up Application Default Credentials

## Troubleshooting

### "No Application Default Credentials found"
Run: `gcloud auth application-default login`

### "Project not set in credentials"
The scripts will use the project from `.env` (`gen-lang-client-0871164439`)

### "Cannot import 'rag' from 'vertexai'"
Make sure you have the latest version:
```bash
pip install --upgrade google-cloud-aiplatform
```

### "Model not found"
The scripts will automatically fall back to `gemini-2.0-flash-exp` if your preferred model isn't available.

## Quick Start

1. Run `./setup_adc.sh` to set up authentication
2. Run `python test_vertex_auth.py` to verify setup
3. Run `python vertex_ai_rag_query.py "Your question"` to query your RAG corpus

## Important Notes

- The Google API Key method (`rag_query.py`) cannot access Vertex AI resources
- To query your actual RAG corpus with 76 SuperClaude files, you must use ADC
- The preferred model `gemini-2.5-pro-preview-06-05` may require special access