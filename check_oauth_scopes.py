#!/usr/bin/env python3
"""
Check OAuth Consent Screen Configuration

This script helps you verify your OAuth consent screen has the right scopes
and provides step-by-step guidance for adding them.
"""

import webbrowser
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'gen-lang-client-0307630688')
    
    print("🔍 OAuth Consent Screen Configuration Checker")
    print("=" * 50)
    print(f"📋 Project: {project_id}")
    print()
    
    print("🌐 Step 1: Open OAuth Consent Screen")
    consent_url = f"https://console.cloud.google.com/apis/credentials/consent?project={project_id}"
    print(f"URL: {consent_url}")
    print()
    
    try:
        webbrowser.open(consent_url)
        print("✅ Opened in your browser!")
    except:
        print("⚠️  Please copy the URL above and open it manually")
    
    print()
    print("📝 Step 2: Check Current Scopes")
    print("Look for these scopes in your OAuth consent screen:")
    print("   ✅ https://www.googleapis.com/auth/calendar")
    print("   ✅ https://www.googleapis.com/auth/calendar.events")
    print()
    
    print("❓ Are both scopes present? (y/n): ", end="")
    scopes_present = input().lower().startswith('y')
    
    if not scopes_present:
        print()
        print("📋 Step 3: Add Missing Scopes")
        print("1. Click 'EDIT APP' on your OAuth consent screen")
        print("2. Navigate to 'Scopes' section")
        print("3. Click 'ADD OR REMOVE SCOPES'")
        print("4. Search for 'calendar'")
        print("5. Select both calendar scopes:")
        print("   • https://www.googleapis.com/auth/calendar")
        print("   • https://www.googleapis.com/auth/calendar.events")
        print("6. Click 'UPDATE' then 'SAVE AND CONTINUE'")
        print()
    
    print("❓ Are you added as a test user? (y/n): ", end="")
    test_user_added = input().lower().startswith('y')
    
    if not test_user_added:
        print()
        print("👤 Step 4: Add Test User")
        print("1. Go to 'Test users' section")
        print("2. Click 'ADD USERS'")
        print("3. Enter your email address")
        print("4. Click 'ADD'")
        print("5. Click 'SAVE AND CONTINUE'")
        print()
    
    if scopes_present and test_user_added:
        print("🎉 Great! Your OAuth consent screen is properly configured!")
        print()
        print("🚀 Next Steps:")
        print("1. Your Google Calendar MCP is ready to use")
        print("2. Run: python run_adk_web.py")
        print("3. First use will prompt for OAuth authorization")
    else:
        print("⚠️  Please complete the missing steps above")
        print("   After making changes, test with: python test_google_calendar_mcp.py")
    
    print()
    print("📚 Need help? Check GOOGLE_CALENDAR_MCP_SETUP.md for detailed instructions")

if __name__ == "__main__":
    main() 