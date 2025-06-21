#!/usr/bin/env python3
"""
Test existing OAuth credentials with Google Calendar MCP server

This script tests if your existing OAuth credentials (from .env) can be used
with the Google Calendar MCP server.
"""

import os
import json
import tempfile
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_credentials_file_from_env():
    """Create a credentials file from environment variables."""
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8080/auth/callback')
    
    if not client_id or not client_secret:
        print("❌ Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET in .env")
        return None
    
    # Create credentials in the format expected by MCP server
    credentials = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": [redirect_uri, "http://localhost"]
        }
    }
    
    # Write to temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(credentials, temp_file, indent=2)
    temp_file.close()
    
    print(f"✅ Created temporary credentials file: {temp_file.name}")
    return temp_file.name

def test_mcp_with_env_credentials():
    """Test MCP server with credentials from environment."""
    print("🧪 Testing Google Calendar MCP with your existing OAuth credentials...")
    
    # Create credentials file from .env
    creds_file = create_credentials_file_from_env()
    if not creds_file:
        return False
    
    try:
        # Set environment variable for MCP server
        os.environ['GOOGLE_OAUTH_CREDENTIALS'] = creds_file
        
        # Import and test the scheduling agent
        sys.path.insert(0, str(Path(__file__).parent))
        from agents.scheduling_agent import GoogleCalendarSchedulingAgent
        
        import asyncio
        
        async def test_agent():
            agent = GoogleCalendarSchedulingAgent()
            try:
                llm_agent, mcp_toolset = await agent.get_agent_async()
                print("✅ MCP agent created successfully with your existing credentials!")
                print("🎉 Your existing OAuth credentials work with the MCP server!")
                return True
            except Exception as e:
                print(f"❌ Failed to create MCP agent: {e}")
                return False
            finally:
                await agent.close()
        
        result = asyncio.run(test_agent())
        return result
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        # Clean up temporary file
        if creds_file and os.path.exists(creds_file):
            os.unlink(creds_file)
            print(f"🧹 Cleaned up temporary file")

def check_credential_type():
    """Help user identify their credential type."""
    print("\n🔍 Checking your credential configuration...")
    
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
    
    print(f"Client ID: {client_id}")
    print(f"Redirect URI: {redirect_uri}")
    
    if redirect_uri and 'localhost:8080' in redirect_uri:
        print("📱 This looks like Web application credentials (redirect to localhost:8080)")
        print("💡 This might still work with MCP server, let's test it!")
    elif redirect_uri and redirect_uri.startswith('http://localhost'):
        print("🖥️  This looks like Desktop application credentials")
        print("✅ Perfect for MCP server!")
    else:
        print("❓ Credential type unclear from redirect URI")
    
    print("\n📋 To verify in Google Cloud Console:")
    print("1. Go to https://console.cloud.google.com/apis/credentials")
    print("2. Find your OAuth 2.0 Client")  
    print("3. Check the 'Application type' column")

def main():
    print("🚀 Testing Existing OAuth Credentials with Google Calendar MCP")
    print("=" * 65)
    
    # Check current configuration
    check_credential_type()
    
    # Test with MCP server
    print("\n" + "=" * 65)
    success = test_mcp_with_env_credentials()
    
    print("\n" + "=" * 65)
    print("📊 Results:")
    
    if success:
        print("✅ SUCCESS: Your existing OAuth credentials work with MCP server!")
        print("\n🎉 You don't need to create new credentials!")
        print("📚 Next steps:")
        print("1. Add GOOGLE_OAUTH_CREDENTIALS=./google-oauth-credentials.json to .env")
        print("2. Create google-oauth-credentials.json with your existing credentials")
        print("3. Run the scheduling agent")
    else:
        print("❌ FAILED: Your existing credentials don't work with MCP server")
        print("\n💡 Solutions:")
        print("1. Create new Desktop application credentials")
        print("2. Or modify your existing Web credentials")
        print("3. Follow the setup guide in GOOGLE_CALENDAR_MCP_SETUP.md")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        sys.exit(1) 