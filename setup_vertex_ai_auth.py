#!/usr/bin/env python3
# ABOUTME: Setup and test Vertex AI authentication methods
# ABOUTME: Shows how to configure ADC for Vertex AI RAG access

"""
Vertex AI Authentication Setup Guide

This script demonstrates different methods to authenticate with Vertex AI
and provides instructions for setting up Application Default Credentials (ADC).
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_gcloud_installed():
    """Check if gcloud CLI is installed"""
    try:
        result = subprocess.run(['gcloud', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ gcloud CLI is installed")
            print(result.stdout.split('\n')[0])
            return True
    except FileNotFoundError:
        print("❌ gcloud CLI is not installed")
        return False

def check_current_auth():
    """Check current authentication status"""
    print("\n🔍 Checking current authentication status...")
    
    # Check active account
    result = subprocess.run(['gcloud', 'auth', 'list'], capture_output=True, text=True)
    print("\nActive accounts:")
    print(result.stdout)
    
    # Check project
    result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], capture_output=True, text=True)
    project = result.stdout.strip()
    if project:
        print(f"\n📁 Current project: {project}")
    else:
        print("\n⚠️  No project set")
    
    return project

def check_adc_credentials():
    """Check if Application Default Credentials exist"""
    print("\n🔍 Checking Application Default Credentials...")
    
    # Common ADC locations
    home = Path.home()
    adc_paths = [
        home / '.config' / 'gcloud' / 'application_default_credentials.json',
        Path(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', '')),
    ]
    
    for path in adc_paths:
        if path and path.exists():
            print(f"✅ Found ADC at: {path}")
            try:
                with open(path) as f:
                    creds = json.load(f)
                    print(f"   Type: {creds.get('type', 'unknown')}")
                    if 'client_email' in creds:
                        print(f"   Service Account: {creds['client_email']}")
                    return True
            except:
                pass
    
    print("❌ No Application Default Credentials found")
    return False

def setup_user_adc():
    """Setup ADC using user credentials"""
    print("\n🔐 Setting up Application Default Credentials with user account...")
    print("\nThis will open a browser for authentication.")
    print("Run this command:")
    print("\n  gcloud auth application-default login\n")
    
    response = input("Would you like to run this now? (y/n): ")
    if response.lower() == 'y':
        subprocess.run(['gcloud', 'auth', 'application-default', 'login'])

def setup_service_account_adc():
    """Setup ADC using service account"""
    print("\n🤖 Setting up Application Default Credentials with service account...")
    print("\nOption 1: Using service account key file (less secure):")
    print("  export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json")
    print("\nOption 2: Using impersonation (recommended):")
    print("  gcloud auth application-default login --impersonate-service-account=SA_EMAIL@PROJECT.iam.gserviceaccount.com")

def test_vertex_ai_connection():
    """Test Vertex AI connection"""
    print("\n🧪 Testing Vertex AI connection...")
    
    try:
        import vertexai
        from google.auth import default
        
        # Get credentials and project
        credentials, project = default()
        
        if not project:
            project = os.getenv('GCP_PROJECT_ID', 'gen-lang-client-0871164439')
            print(f"⚠️  No project in credentials, using: {project}")
        
        location = os.getenv('GCP_LOCATION', 'us-central1')
        
        # Initialize Vertex AI
        vertexai.init(
            project=project,
            location=location,
            credentials=credentials
        )
        
        print(f"✅ Successfully initialized Vertex AI")
        print(f"   Project: {project}")
        print(f"   Location: {location}")
        
        # Try to import RAG
        try:
            from vertexai import rag
            print("✅ Can import 'from vertexai import rag'")
        except ImportError:
            try:
                from vertexai.preview import rag
                print("✅ Can import 'from vertexai.preview import rag'")
            except ImportError:
                print("❌ Cannot import rag module")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to Vertex AI: {str(e)}")
        return False

def create_rag_auth_script():
    """Create a script that uses proper Vertex AI authentication"""
    script_content = '''#!/usr/bin/env python3
# ABOUTME: Query RAG corpus using Vertex AI with proper authentication
# ABOUTME: Uses Application Default Credentials (ADC) for authentication

"""
Vertex AI RAG Query Tool

Uses Application Default Credentials to authenticate with Vertex AI
and query an existing RAG corpus.
"""

import os
import sys
import vertexai
from google.auth import default

# Get credentials and project from ADC
credentials, project = default()

# Configuration (can be overridden by environment variables)
PROJECT_ID = project or os.getenv('GCP_PROJECT_ID', 'gen-lang-client-0871164439')
LOCATION = os.getenv('GCP_LOCATION', 'us-central1')
CORPUS_ID = "2587317985924349952"

# Import RAG module with fallback
try:
    from vertexai import rag
    print(f"Using standard RAG import")
except ImportError:
    from vertexai.preview import rag
    print(f"Using preview RAG import")

from google import genai
from google.genai.types import GenerateContentConfig, Retrieval, Tool, VertexRagStore

# Initialize Vertex AI with ADC
print(f"Initializing Vertex AI...")
print(f"Project: {PROJECT_ID}")
print(f"Location: {LOCATION}")

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    credentials=credentials
)

# Create genai client with Vertex AI backend
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

def query_rag(question, model_id="gemini-2.0-flash-exp"):
    """Query the RAG corpus"""
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=question,
            config=GenerateContentConfig(tools=[rag_tool]),
        )
        return response.text
    except Exception as e:
        if "404" in str(e):
            # Try fallback model
            print(f"Model {model_id} not found, trying gemini-2.0-flash-exp")
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=question,
                config=GenerateContentConfig(tools=[rag_tool]),
            )
            return response.text
        else:
            return f"Error: {str(e)}"

def main():
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        print(f"\\nQuestion: {question}")
        print("-" * 80)
        print(query_rag(question))
    else:
        print("\\nRAG Query Tool - Using Vertex AI Authentication")
        print("Type 'exit' to quit\\n")
        
        while True:
            question = input("Your question: ").strip()
            if question.lower() in ['exit', 'quit']:
                break
            elif question:
                print("\\nResponse:")
                print("-" * 80)
                print(query_rag(question))
                print("-" * 80)

if __name__ == "__main__":
    main()
'''
    
    with open('vertex_ai_rag_query.py', 'w') as f:
        f.write(script_content)
    os.chmod('vertex_ai_rag_query.py', 0o755)
    print("\n✅ Created vertex_ai_rag_query.py")

def main():
    """Main setup flow"""
    print("=" * 80)
    print("Vertex AI Authentication Setup")
    print("=" * 80)
    
    # Check gcloud
    if not check_gcloud_installed():
        print("\n📥 Please install gcloud CLI:")
        print("  https://cloud.google.com/sdk/docs/install")
        return
    
    # Check current auth
    project = check_current_auth()
    
    # Check ADC
    has_adc = check_adc_credentials()
    
    if not has_adc:
        print("\n⚠️  No Application Default Credentials found!")
        print("\nYou need to set up ADC to use Vertex AI. Choose an option:")
        print("\n1. User account (recommended for development)")
        print("2. Service account (recommended for production)")
        print("3. Skip setup")
        
        choice = input("\nChoice (1/2/3): ")
        
        if choice == '1':
            setup_user_adc()
        elif choice == '2':
            setup_service_account_adc()
    
    # Test connection
    if test_vertex_ai_connection():
        print("\n✅ Vertex AI is properly configured!")
        
        # Create the script
        create_rag_auth_script()
        
        print("\n📝 Next steps:")
        print("1. Make sure ADC is configured (if not already done)")
        print("2. Run: python vertex_ai_rag_query.py 'Your question here'")
        print("\n💡 The script will use your actual RAG corpus with proper authentication")
    else:
        print("\n❌ Vertex AI connection failed")
        print("\n🔧 Troubleshooting:")
        print("1. Run: gcloud auth application-default login")
        print("2. Make sure you have the right permissions")
        print("3. Check if the project ID is correct")

if __name__ == "__main__":
    main()