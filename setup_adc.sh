#!/bin/bash
# ABOUTME: Script to set up Application Default Credentials for Vertex AI
# ABOUTME: Run this to authenticate with Google Cloud for local development

echo "Setting up Application Default Credentials (ADC) for Vertex AI..."
echo "=================================================="
echo ""
echo "This will open a browser window for authentication."
echo "Please log in with your Google account that has access to the project:"
echo "Project ID: gen-lang-client-0871164439"
echo ""

# Run the ADC login command
gcloud auth application-default login

# Check if successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ ADC setup successful!"
    echo ""
    echo "Testing ADC file..."
    if [ -f "$HOME/.config/gcloud/application_default_credentials.json" ]; then
        echo "✅ ADC file created at: $HOME/.config/gcloud/application_default_credentials.json"
    else
        echo "⚠️  ADC file not found at expected location"
    fi
    echo ""
    echo "You can now run: python vertex_ai_rag_query.py 'Your question'"
else
    echo ""
    echo "❌ ADC setup failed. Please try again."
fi