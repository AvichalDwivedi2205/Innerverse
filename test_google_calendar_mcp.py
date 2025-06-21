#!/usr/bin/env python3
"""
Test script for Google Calendar MCP Scheduling Agent

This script tests the new MCP-based scheduling agent to ensure it's properly
configured and can connect to Google Calendar.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from agents.scheduling_agent import GoogleCalendarSchedulingAgent
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


async def test_mcp_connection():
    """Test basic MCP connection to Google Calendar."""
    print("🧪 Testing Google Calendar MCP Connection...")
    
    agent = GoogleCalendarSchedulingAgent()
    
    try:
        # Test agent creation
        llm_agent, mcp_toolset = await agent.get_agent_async()
        print("✅ Successfully created MCP agent and toolset")
        
        # Verify toolset has expected tools
        expected_tools = [
            'list-calendars',
            'list-events', 
            'search-events',
            'create-event',
            'update-event',
            'delete-event',
            'get-freebusy',
            'list-colors'
        ]
        
        print(f"📋 Expected tools: {len(expected_tools)}")
        print("✅ MCP toolset created successfully")
        
        return True
        
    except FileNotFoundError as e:
        print(f"❌ OAuth credentials file not found: {e}")
        print("\n📝 Setup Instructions:")
        print("1. Download OAuth credentials from Google Cloud Console")
        print("2. Save as 'google-oauth-credentials.json' in project root")
        print("3. Or set GOOGLE_OAUTH_CREDENTIALS environment variable")
        return False
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False
        
    finally:
        await agent.close()


async def test_environment_setup():
    """Test environment configuration."""
    print("\n🔧 Testing Environment Setup...")
    
    # Check for Node.js/npx
    try:
        import subprocess
        result = subprocess.run(['npx', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ npx available: {result.stdout.strip()}")
        else:
            print("❌ npx not available or not working")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ npx not found - please install Node.js")
        return False
    
    # Check environment variables
    oauth_creds = os.getenv('GOOGLE_OAUTH_CREDENTIALS')
    if oauth_creds:
        print(f"✅ GOOGLE_OAUTH_CREDENTIALS set: {oauth_creds}")
        if os.path.exists(oauth_creds):
            print("✅ OAuth credentials file exists")
        else:
            print("❌ OAuth credentials file not found at specified path")
            return False
    else:
        # Check for default locations
        default_paths = [
            './google-oauth-credentials.json',
            './credentials.json',
            './gcp-oauth.keys.json'
        ]
        
        found_file = None
        for path in default_paths:
            if os.path.exists(path):
                found_file = path
                break
        
        if found_file:
            print(f"✅ Found OAuth credentials at: {found_file}")
        else:
            print("❌ No OAuth credentials file found")
            print("Expected locations:", default_paths)
            return False
    
    # Check Google Cloud project
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    if project_id:
        print(f"✅ Google Cloud Project: {project_id}")
    else:
        print("⚠️  GOOGLE_CLOUD_PROJECT not set (optional)")
    
    return True


async def test_oauth_credentials_format():
    """Test OAuth credentials file format."""
    print("\n📄 Testing OAuth Credentials Format...")
    
    oauth_creds_path = None
    
    # Find credentials file
    possible_paths = [
        os.getenv('GOOGLE_OAUTH_CREDENTIALS'),
        './google-oauth-credentials.json',
        './credentials.json',
        './gcp-oauth.keys.json'
    ]
    
    for path in possible_paths:
        if path and os.path.exists(path):
            oauth_creds_path = path
            break
    
    if not oauth_creds_path:
        print("❌ No OAuth credentials file found")
        return False
    
    try:
        import json
        with open(oauth_creds_path, 'r') as f:
            creds = json.load(f)
        
        # Check if it's the right type of credentials
        if 'installed' in creds:
            client_info = creds['installed']
            print("✅ Desktop application credentials detected")
            
            required_fields = ['client_id', 'client_secret', 'auth_uri', 'token_uri']
            missing_fields = [field for field in required_fields if field not in client_info]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            else:
                print("✅ All required OAuth fields present")
                
        elif 'web' in creds:
            print("❌ Web application credentials detected")
            print("Please use Desktop application credentials instead")
            return False
        else:
            print("❌ Unknown credentials format")
            return False
            
    except json.JSONDecodeError:
        print("❌ Invalid JSON in credentials file")
        return False
    except Exception as e:
        print(f"❌ Error reading credentials file: {e}")
        return False
    
    return True


async def main():
    """Run all tests."""
    print("🚀 Google Calendar MCP Scheduling Agent Test Suite")
    print("=" * 60)
    
    tests = [
        ("Environment Setup", test_environment_setup),
        ("OAuth Credentials Format", test_oauth_credentials_format),
        ("MCP Connection", test_mcp_connection),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your Google Calendar MCP setup is ready.")
        print("\n📚 Next steps:")
        print("1. Run 'python run_adk_web.py' to start the web interface")
        print("2. Interact with the scheduling agent")
        print("3. First run will require OAuth authentication in browser")
    else:
        print("\n⚠️  Some tests failed. Please check the setup guide:")
        print("   📖 See GOOGLE_CALENDAR_MCP_SETUP.md for detailed instructions")
    
    return passed == len(results)


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        sys.exit(1) 