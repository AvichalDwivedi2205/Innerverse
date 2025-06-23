#!/bin/bash
# SECURE Innerverse Production Deployment Script
# This script shows the PROPER way to handle API keys

set -e  # Exit on any error

echo "🔐 SECURE INNERVERSE DEPLOYMENT"
echo "================================"

# Check if required environment variables are set
if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
    echo "❌ Please set GOOGLE_CLOUD_PROJECT environment variable"
    exit 1
fi

# Check if API keys are provided as environment variables (NOT hardcoded!)
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ Please set GOOGLE_API_KEY environment variable"
    echo "   Example: export GOOGLE_API_KEY='your_key_here'"
    exit 1
fi

if [ -z "$PINECONE_API_KEY" ]; then
    echo "❌ Please set PINECONE_API_KEY environment variable"
    echo "   Example: export PINECONE_API_KEY='your_key_here'"
    exit 1
fi

# Set default values
GOOGLE_CLOUD_LOCATION=${GOOGLE_CLOUD_LOCATION:-"us-central1"}
SERVICE_NAME=${SERVICE_NAME:-"innerverse-ai"}

echo "📋 Deployment Configuration:"
echo "   Project: $GOOGLE_CLOUD_PROJECT"
echo "   Location: $GOOGLE_CLOUD_LOCATION"
echo "   Service: $SERVICE_NAME"
echo "   🔐 API keys: ✅ Loaded from environment variables"
echo ""

# Authenticate with Google Cloud
echo "🔐 Checking Google Cloud authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "."; then
    echo "❌ Not authenticated with Google Cloud. Please run:"
    echo "   gcloud auth login"
    echo "   gcloud config set project $GOOGLE_CLOUD_PROJECT"
    exit 1
fi

echo "✅ Google Cloud authentication verified"

# Enable required APIs
echo "🔧 Enabling required Google Cloud APIs..."
gcloud services enable cloudbuild.googleapis.com --project=$GOOGLE_CLOUD_PROJECT
gcloud services enable run.googleapis.com --project=$GOOGLE_CLOUD_PROJECT
gcloud services enable aiplatform.googleapis.com --project=$GOOGLE_CLOUD_PROJECT

# Deploy using gcloud with SECURE environment variable passing
echo "🚀 Deploying to Cloud Run with SECURE environment variables..."
gcloud run deploy $SERVICE_NAME \
    --source . \
    --region $GOOGLE_CLOUD_LOCATION \
    --project $GOOGLE_CLOUD_PROJECT \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10 \
    --timeout 300 \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GOOGLE_GENAI_USE_VERTEXAI=False,ENVIRONMENT=production,USER_TIMEZONE=America/New_York,GOOGLE_API_KEY=$GOOGLE_API_KEY,PINECONE_API_KEY=$PINECONE_API_KEY,PINECONE_INDEX_NAME=innerverse,PINECONE_HOST=https://innerverse-uxvd5v0.svc.aped-4627-b74a.pinecone.io,VERTEX_AI_PROJECT=$GOOGLE_CLOUD_PROJECT,VERTEX_AI_LOCATION=$GOOGLE_CLOUD_LOCATION,FIREBASE_PROJECT_ID=$GOOGLE_CLOUD_PROJECT,DEV_USER_ID=avichal_dev_user,JOURNALING_AGENT_MODEL=gemini-2.5-flash,THERAPY_AGENT_MODEL=gemini-2.5-flash,ORCHESTRATOR_AGENT_MODEL=gemini-2.5-flash"

echo ""
echo "🎉 SECURE DEPLOYMENT COMPLETE!"
echo "==============================="

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$GOOGLE_CLOUD_LOCATION --project=$GOOGLE_CLOUD_PROJECT --format="value(status.url)")

echo "🌐 Your Innerverse AI is deployed at:"
echo "   $SERVICE_URL"
echo ""
echo "🔐 SECURITY NOTES:"
echo "   ✅ API keys passed via environment variables (NOT in code)"
echo "   ✅ No sensitive data hardcoded in Docker images"
echo "   ✅ Credentials managed by Cloud Run environment"
echo ""
echo "📱 Next Steps:"
echo "   1. Open $SERVICE_URL in your browser"
echo "   2. Test all agents functionality"
echo "   3. Verify no sensitive data in git history"
echo ""

# Usage instructions
echo "🚀 USAGE INSTRUCTIONS:"
echo "To use this secure deployment script:"
echo "   export GOOGLE_CLOUD_PROJECT='gen-lang-client-0307630688'"
echo "   export GOOGLE_API_KEY='your_new_api_key_here'"
echo "   export PINECONE_API_KEY='your_pinecone_key_here'"
echo "   ./deploy-secure.sh" 