#!/usr/bin/env python3
"""
Comprehensive Credential Test for Innerverse
Tests all configured credentials and services
"""

import os
import sys
import json
from pathlib import Path

def load_environment():
    """Load environment variables from .env file."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Loaded .env file")
        return True
    except ImportError:
        print("❌ python-dotenv not installed")
        print("   Install with: pip install python-dotenv")
        return False
    except Exception as e:
        print(f"❌ Error loading .env: {e}")
        return False

def test_google_ai_api():
    """Test Google AI Studio API."""
    print("\n🧪 TESTING GOOGLE AI API:")
    print("-" * 30)
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY not found")
        return False
    
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # Test with simple request
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content("Hello! Please respond with exactly: 'Google AI API is working'")
        
        print("✅ Google AI API: SUCCESS")
        print(f"   Response: {response.text.strip()}")
        return True
        
    except Exception as e:
        print(f"❌ Google AI API: FAILED - {e}")
        return False

def test_service_account():
    """Test Google Cloud Service Account."""
    print("\n🧪 TESTING SERVICE ACCOUNT:")
    print("-" * 30)
    
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', './service-account-key.json')
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    
    print(f"📁 Credentials file: {creds_path}")
    print(f"🏢 Project ID: {project_id}")
    
    if not Path(creds_path).exists():
        print(f"❌ Service account file not found: {creds_path}")
        return False
    
    try:
        # Read service account info
        with open(creds_path, 'r') as f:
            sa_info = json.load(f)
        
        print(f"📧 Service account email: {sa_info.get('client_email', 'Unknown')}")
        
        # Test Firestore connection
        from google.cloud import firestore
        
        # Set environment for authentication
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(Path(creds_path).resolve())
        
        db = firestore.Client(project=project_id)
        
        # Try to list collections (this tests authentication)
        collections = list(db.collections())
        print("✅ Service Account: SUCCESS")
        print(f"   Firestore accessible, found {len(collections)} collections")
        return True
        
    except Exception as e:
        print(f"❌ Service Account: FAILED - {e}")
        return False

def test_oauth_setup():
    """Test OAuth configuration for Calendar API."""
    print("\n🧪 TESTING OAUTH SETUP:")
    print("-" * 30)
    
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
    
    if not all([client_id, client_secret, redirect_uri]):
        print("❌ Missing OAuth credentials")
        return False
    
    print(f"🆔 Client ID: {client_id[:20]}...{client_id[-10:]}")
    print(f"🔐 Client Secret: {client_secret[:10]}...{client_secret[-4:]}")
    print(f"🔄 Redirect URI: {redirect_uri}")
    
    # Check if we have existing OAuth token
    token_files = ['token.json', 'token.pickle', 'calendar_token.json']
    token_found = False
    
    for token_file in token_files:
        if Path(token_file).exists():
            print(f"✅ Found OAuth token: {token_file}")
            token_found = True
            break
    
    if not token_found:
        print("⚠️  No OAuth token found - you'll need to authenticate first")
        print("   This is normal for first-time setup")
    
    try:
        # Test OAuth flow setup (without actually running it)
        from google_auth_oauthlib.flow import Flow
        
        # Create OAuth flow configuration
        flow_config = {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri]
            }
        }
        
        flow = Flow.from_client_config(
            flow_config,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        flow.redirect_uri = redirect_uri
        
        print("✅ OAuth Configuration: VALID")
        return True
        
    except Exception as e:
        print(f"❌ OAuth Configuration: FAILED - {e}")
        return False

def test_pinecone():
    """Test Pinecone configuration."""
    print("\n🧪 TESTING PINECONE:")
    print("-" * 30)
    
    api_key = os.getenv('PINECONE_API_KEY')
    index_name = os.getenv('PINECONE_INDEX_NAME')
    host = os.getenv('PINECONE_HOST')
    
    if not all([api_key, index_name, host]):
        print("❌ Missing Pinecone configuration")
        return False
    
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"📊 Index: {index_name}")
    print(f"🌐 Host: {host}")
    
    try:
        from pinecone import Pinecone
        
        pc = Pinecone(api_key=api_key)
        index = pc.Index(index_name, host=host)
        
        # Test basic operations
        stats = index.describe_index_stats()
        print("✅ Pinecone: SUCCESS")
        print(f"   Index stats: {stats.total_vector_count} vectors")
        return True
        
    except Exception as e:
        print(f"❌ Pinecone: FAILED - {e}")
        return False

def test_scheduling_agent():
    """Test if scheduling agent can work with current setup."""
    print("\n🧪 TESTING SCHEDULING AGENT SETUP:")
    print("-" * 30)
    
    try:
        # Test if we can import the scheduling agent
        from agents.scheduling_agent.scheduling_agent import SchedulingAgent
        from agents.scheduling_agent.tools import create_event
        
        print("✅ Scheduling agent imports: SUCCESS")
        
        # Test basic functionality (without actually creating events)
        agent = SchedulingAgent()
        print("✅ Scheduling agent creation: SUCCESS")
        
        return True
        
    except Exception as e:
        print(f"❌ Scheduling agent: FAILED - {e}")
        return False

def check_oauth_calendar_flow():
    """Check what's needed for Calendar OAuth flow."""
    print("\n📅 CALENDAR OAUTH FLOW CHECK:")
    print("-" * 30)
    
    # Check if we have all needed components
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    if client_id and client_secret:
        print("✅ OAuth credentials available")
        
        # Check if token exists
        if Path('token.json').exists():
            print("✅ OAuth token exists - Calendar should work!")
            return True
        else:
            print("⚠️  OAuth token missing - first Calendar use will trigger OAuth flow")
            print("\n🔄 WHAT HAPPENS NEXT:")
            print("1. When you first use calendar features, a browser will open")
            print("2. You'll be asked to sign in to Google")
            print("3. Grant permission to access your calendar") 
            print("4. A token.json file will be created for future use")
            print("5. After that, calendar features will work automatically")
            return True
    else:
        print("❌ Missing OAuth credentials")
        return False

def main():
    """Run all credential tests."""
    print("🔬 INNERVERSE CREDENTIAL TEST SUITE")
    print("=" * 50)
    
    # Load environment
    if not load_environment():
        print("❌ Could not load environment variables")
        sys.exit(1)
    
    # Run all tests
    results = {}
    results['google_ai'] = test_google_ai_api()
    results['service_account'] = test_service_account()
    results['oauth_setup'] = test_oauth_setup()
    results['pinecone'] = test_pinecone()
    results['scheduling_agent'] = test_scheduling_agent()
    
    # Check OAuth flow
    oauth_ready = check_oauth_calendar_flow()
    
    # Summary
    print("\n📊 FINAL RESULTS:")
    print("=" * 50)
    
    for service, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {service.replace('_', ' ').title()}: {'Working' if status else 'Failed'}")
    
    print(f"📅 Calendar OAuth: {'Ready' if oauth_ready else 'Needs setup'}")
    
    # Overall status
    working_count = sum(results.values())
    total_count = len(results)
    
    print(f"\n🎯 OVERALL STATUS: {working_count}/{total_count} services working")
    
    if working_count >= 3:  # At least Google AI, Service Account, and Pinecone
        print("🎉 YOU'RE READY TO GO!")
        print("\n🚀 NEXT STEPS:")
        print("1. Start the ADK web interface: python run_adk_web.py")
        print("2. Try scheduling: 'Schedule a meeting tomorrow at 2pm'")
        print("3. First calendar use will trigger OAuth flow (normal!)")
    else:
        print("⚠️  Some services need attention - see failed tests above")

if __name__ == "__main__":
    main() 