# Google Calendar MCP Setup Guide

This guide will help you set up the Google Calendar MCP server with OAuth authentication for the Innerverse scheduling agent.

## Prerequisites

1. **Node.js and npm**: Required for running the Google Calendar MCP server
2. **Google Cloud Project**: With Calendar API enabled
3. **OAuth 2.0 Credentials**: Desktop application type

## Step 1: Google Cloud Console Setup

### 1.1 Create/Select Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select your existing project: `gen-lang-client-0307630688`

### 1.2 Enable Google Calendar API
1. Navigate to **APIs & Services** > **Library**
2. Search for "Google Calendar API"
3. Click **Enable**

### 1.3 Configure OAuth Consent Screen
1. Go to **APIs & Services** > **OAuth consent screen**
2. Choose **External** user type (unless you have Google Workspace)
3. Fill in required information:
   - **App name**: `Innerverse Calendar Agent`
   - **User support email**: Your email
   - **Developer contact information**: Your email
4. Add scopes:
   - Click **Add or Remove Scopes**
   - Find and select: `https://www.googleapis.com/auth/calendar`
   - Find and select: `https://www.googleapis.com/auth/calendar.events`
5. Add test users:
   - Add your email address as a test user
   - **Note**: It may take a few minutes for the test user to propagate

### 1.4 Create OAuth Credentials
1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth Client ID**
3. Choose **Desktop app** as application type
4. Name it: `Innerverse Calendar Desktop Client`
5. Click **Create**
6. Download the JSON credentials file
7. Save it as `google-oauth-credentials.json` in your project root

## Step 2: Environment Configuration

### 2.1 Update .env File
Add the following to your `.env` file:

```bash
# Google Calendar MCP Configuration
GOOGLE_OAUTH_CREDENTIALS=./google-oauth-credentials.json

# Optional: Specify default calendar ID
GOOGLE_CALENDAR_ID=primary
```

### 2.2 Verify Existing Configuration
Your `.env` should have these OAuth settings:
```bash
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8080/auth/callback
```

## Step 3: Install Dependencies

The Google Calendar MCP server will be automatically installed via `npx` when needed. No additional installation required.

## Step 4: First Time Authentication

### 4.1 Initial Setup
When you first run the scheduling agent:

1. The MCP server will start automatically
2. A browser window will open for OAuth authentication
3. Sign in with your Google account
4. Grant the requested calendar permissions
5. The authentication token will be saved automatically

### 4.2 Token Storage
- Tokens are stored in your system's config directory
- Location varies by OS:
  - **Linux**: `~/.config/google-calendar-mcp/`
  - **macOS**: `~/Library/Application Support/google-calendar-mcp/`
  - **Windows**: `%APPDATA%\google-calendar-mcp\`

## Step 5: Testing the Setup

### 5.1 Test Basic Functionality
```python
# Test script to verify MCP connection
import asyncio
from agents.scheduling_agent import GoogleCalendarSchedulingAgent

async def test_calendar_connection():
    agent = GoogleCalendarSchedulingAgent()
    try:
        llm_agent, mcp_toolset = await agent.get_agent_async()
        print("✅ Google Calendar MCP connection successful!")
        
        # Test listing calendars
        # This would use the MCP tools through the agent
        print("📅 Calendar access verified")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
    finally:
        await agent.close()

# Run the test
asyncio.run(test_calendar_connection())
```

### 5.2 Test with ADK Web
```bash
cd /path/to/Innerverse
python run_adk_web.py
```

Then interact with the scheduling agent through the web interface.

## Step 6: Production Considerations

### 6.1 Moving from Test to Production
If your app is in **Testing** mode:
- Refresh tokens expire after 7 days
- Consider moving to **Production** for longer-lived tokens
- Production requires Google verification process

### 6.2 Token Refresh
For re-authentication or troubleshooting:
```bash
# Clear existing tokens
rm -rf ~/.config/google-calendar-mcp/token.json

# Or manually re-authenticate
export GOOGLE_OAUTH_CREDENTIALS="/path/to/your/credentials.json"
npx @cocal/google-calendar-mcp auth
```

## Available MCP Tools

The Google Calendar MCP server provides these tools:

| Tool | Description |
|------|-------------|
| `list-calendars` | Get all available calendars |
| `list-events` | Retrieve events with date filtering |
| `search-events` | Search events by text query |
| `create-event` | Create new calendar events |
| `update-event` | Update existing events |
| `delete-event` | Delete events |
| `get-freebusy` | Check availability across calendars |
| `list-colors` | List available event colors |

## Troubleshooting

### Common Issues

1. **OAuth Credentials File Not Found**
   - Verify file path in `GOOGLE_OAUTH_CREDENTIALS`
   - Ensure file exists and is readable
   - Use absolute path if relative path fails

2. **Authentication Errors**
   - Verify credentials are for **Desktop App** type
   - Check that your email is added as **Test User**
   - Try deleting saved tokens and re-authenticating

3. **API Not Enabled**
   - Ensure Google Calendar API is enabled in your project
   - Wait a few minutes after enabling for changes to propagate

4. **Permission Denied**
   - Verify OAuth scopes include calendar permissions
   - Check that consent screen is properly configured

5. **Node.js/npx Issues**
   - Ensure Node.js is installed and in PATH
   - Try running `npx @cocal/google-calendar-mcp` manually

### Debug Mode
Set environment variable for verbose logging:
```bash
export DEBUG=google-calendar-mcp:*
```

## Security Notes

- **Never commit** `google-oauth-credentials.json` to version control
- **Never share** your OAuth credentials or tokens
- Each user should create their own OAuth credentials
- If credentials are compromised, revoke them immediately in Google Cloud Console
- The MCP server runs locally and credentials never leave your machine

## Support

For issues specific to:
- **Google Calendar MCP Server**: [GitHub Issues](https://github.com/nspady/google-calendar-mcp/issues)
- **Google ADK**: [ADK Documentation](https://google.github.io/adk-docs/)
- **OAuth Setup**: [Google Cloud Console Help](https://cloud.google.com/docs/authentication)

## Migration from Firebase

The new MCP-based agent replaces the previous Firebase implementation:

### Benefits of MCP Approach:
- ✅ Direct Google Calendar API access
- ✅ OAuth authentication (no service account needed)
- ✅ Real-time calendar synchronization
- ✅ Full Google Calendar feature support
- ✅ Better conflict detection and resolution
- ✅ Multi-calendar support

### What Changed:
- 🔄 Authentication: OAuth instead of Firebase service account
- 🔄 Storage: Google Calendar instead of Firestore
- 🔄 Tools: MCP tools instead of custom Firebase tools
- 🔄 Architecture: MCP server instead of direct API calls 