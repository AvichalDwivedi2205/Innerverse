#!/bin/bash
# Innerverse Production Deployment Script
# Quick deployment for tomorrow's submission

set -e  # Exit on any error

echo "🚀 INNERVERSE PRODUCTION DEPLOYMENT"
echo "====================================="

# Check if required environment variables are set
if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
    echo "❌ Please set GOOGLE_CLOUD_PROJECT environment variable"
    exit 1
fi

# Set default values
GOOGLE_CLOUD_LOCATION=${GOOGLE_CLOUD_LOCATION:-"us-central1"}
SERVICE_NAME=${SERVICE_NAME:-"innerverse-ai"}
APP_NAME=${APP_NAME:-"innerverse"}

echo "📋 Deployment Configuration:"
echo "   Project: $GOOGLE_CLOUD_PROJECT"
echo "   Location: $GOOGLE_CLOUD_LOCATION"
echo "   Service: $SERVICE_NAME"
echo "   App: $APP_NAME"
echo ""

# Authenticate with Google Cloud (if not already done)
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

# Create .dockerignore if it doesn't exist
if [ ! -f .dockerignore ]; then
    echo "📄 Creating .dockerignore file..."
    cat > .dockerignore << EOF
.git
.gitignore
README.md
.env
.venv
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
.pytest_cache/
.coverage
htmlcov/
.tox/
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.DS_Store
*.tmp
EOF
fi

# Deploy using gcloud (more reliable than adk CLI for production)
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --source . \
    --region $GOOGLE_CLOUD_LOCATION \
    --project $GOOGLE_CLOUD_PROJECT \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10 \
    --timeout 300 \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GOOGLE_GENAI_USE_VERTEXAI=True,ENVIRONMENT=production,USER_TIMEZONE=America/New_York"

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "====================================="

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$GOOGLE_CLOUD_LOCATION --project=$GOOGLE_CLOUD_PROJECT --format="value(status.url)")

echo "🌐 Your Innerverse AI is deployed at:"
echo "   $SERVICE_URL"
echo ""
echo "📊 Service Endpoints:"
echo "   • Main UI: $SERVICE_URL"
echo "   • Health Check: $SERVICE_URL/health"
echo "   • Preview System: $SERVICE_URL:8081/preview/{id}"
echo ""
echo "🧪 Test Commands:"
echo "   curl $SERVICE_URL/health"
echo "   curl $SERVICE_URL/list-apps"
echo ""
echo "📱 Next Steps:"
echo "   1. Open $SERVICE_URL in your browser"
echo "   2. Test the scheduling agent with calendar permissions"
echo "   3. Try the mental orchestrator for dashboard previews"
echo "   4. Submit your project! 🎯"
echo ""
echo "🔗 Useful Links:"
echo "   • Cloud Run Console: https://console.cloud.google.com/run"
echo "   • Logs: gcloud logs tail $SERVICE_NAME --project=$GOOGLE_CLOUD_PROJECT" 