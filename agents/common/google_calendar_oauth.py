"""
Google Calendar OAuth Handler for Automatic Authentication
"""

import os
import json
from pathlib import Path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

class GoogleCalendarAuth:
    """Handle Google Calendar OAuth flow automatically."""
    
    def __init__(self):
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8080/auth/callback')
        self.scopes = ['https://www.googleapis.com/auth/calendar']
        self.token_file = 'token.json'
        
    def get_credentials(self):
        """Get valid credentials, refreshing or initiating OAuth if needed."""
        creds = None
        
        # Load existing token
        if Path(self.token_file).exists():
            creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Token refresh failed: {e}")
                    creds = None
            
            if not creds:
                creds = self._run_oauth_flow()
            
            # Save the credentials for the next run
            if creds:
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())
        
        return creds
    
    def _run_oauth_flow(self):
        """Run the OAuth flow to get new credentials."""
        if not all([self.client_id, self.client_secret]):
            raise ValueError("Missing OAuth client credentials")
        
        # Create OAuth flow configuration
        flow_config = {
            "web": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [self.redirect_uri]
            }
        }
        
        flow = Flow.from_client_config(flow_config, scopes=self.scopes)
        flow.redirect_uri = self.redirect_uri
        
        # Get the authorization URL
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        print("\n🔐 GOOGLE CALENDAR AUTHENTICATION REQUIRED")
        print("=" * 50)
        print("Please follow these steps:")
        print(f"1. Open this URL in your browser: {auth_url}")
        print("2. Sign in to Google and grant calendar permissions")
        print("3. Copy the authorization code from the redirect URL")
        print("4. Paste it below")
        
        auth_code = input("\nEnter the authorization code: ").strip()
        
        # Exchange code for token
        flow.fetch_token(code=auth_code)
        
        return flow.credentials
    
    def get_calendar_service(self):
        """Get authenticated Google Calendar service."""
        creds = self.get_credentials()
        if not creds:
            raise ValueError("Could not obtain valid credentials")
        
        return build('calendar', 'v3', credentials=creds)

# Global instance
calendar_auth = GoogleCalendarAuth() 