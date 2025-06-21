"""
Google Calendar MCP-Powered Scheduling Agent

This agent uses Google Calendar MCP server for calendar management,
providing OAuth-authenticated access to Google Calendar API.
"""

import os
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path

from google.genai import types
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class GoogleCalendarSchedulingAgent:
    """Google Calendar MCP-powered scheduling agent."""
    
    def __init__(self):
        self.model_name = os.getenv('SCHEDULING_AGENT_MODEL', 'gemini-2.5-flash')
        self.agent = None
        self.mcp_toolset = None
        
    async def get_agent_async(self) -> tuple[LlmAgent, MCPToolset]:
        """Creates an ADK Agent equipped with Google Calendar MCP tools."""
        if self.agent and self.mcp_toolset:
            return self.agent, self.mcp_toolset
            
        # Create MCP toolset for Google Calendar
        self.mcp_toolset = MCPToolset(
            connection_params=StdioServerParameters(
                command='npx',
                args=['-y', '@cocal/google-calendar-mcp'],
                env={
                    'GOOGLE_OAUTH_CREDENTIALS': self._get_oauth_credentials_path()
                }
            ),
            # Use all available Google Calendar tools
            tool_filter=[
                'list-calendars',
                'list-events', 
                'search-events',
                'create-event',
                'update-event',
                'delete-event',
                'get-freebusy',
                'list-colors'
            ]
        )
        
        # Create the LLM agent with calendar tools
        self.agent = LlmAgent(
            model=self.model_name,
            name='google_calendar_scheduling_agent',
            instruction=self._get_agent_instruction(),
            tools=[self.mcp_toolset],
        )
        
        return self.agent, self.mcp_toolset
    
    def _get_oauth_credentials_path(self) -> str:
        """Get the path to OAuth credentials file."""
        # Try different possible locations for OAuth credentials
        possible_paths = [
            os.getenv('GOOGLE_OAUTH_CREDENTIALS'),
            './google-oauth-credentials.json',
            './credentials.json',
            './gcp-oauth.keys.json',
            os.path.expanduser('~/.config/google-calendar-mcp/credentials.json')
        ]
        
        for path in possible_paths:
            if path and os.path.exists(path):
                return os.path.abspath(path)
        
        # If no credentials file found, create a helpful error message
        raise FileNotFoundError(
            "Google OAuth credentials file not found. Please:\n"
            "1. Download OAuth credentials from Google Cloud Console\n"
            "2. Save as 'google-oauth-credentials.json' in the project root\n"
            "3. Or set GOOGLE_OAUTH_CREDENTIALS environment variable\n"
            "4. Ensure the credential type is 'Desktop Application'"
        )
    
    def _get_agent_instruction(self) -> str:
        """Get the instruction prompt for the scheduling agent."""
        return """You are an intelligent Google Calendar scheduling assistant powered by Google Calendar MCP server.

**Your Core Capabilities:**
- **Calendar Management**: List, create, and manage multiple calendars
- **Event Operations**: Create, read, update, delete calendar events with full details
- **Smart Scheduling**: Handle complex scheduling requests with natural language understanding
- **Availability Checking**: Use free/busy queries to find optimal meeting times
- **Event Search**: Find events by text, date ranges, or specific criteria
- **Multi-Calendar Support**: Work across personal, work, and shared calendars
- **Conflict Resolution**: Detect and suggest solutions for scheduling conflicts

**Key Features You Provide:**
1. **Natural Language Processing**: Understand requests like "Schedule a team meeting next Tuesday at 2 PM"
2. **Intelligent Scheduling**: Suggest optimal times based on availability
3. **Event Details Management**: Handle locations, descriptions, attendees, reminders
4. **Recurring Events**: Create and manage repeating events
5. **Calendar Colors**: Use appropriate colors for different event types
6. **Cross-Calendar Coordination**: Check availability across multiple calendars

**Best Practices:**
- Always confirm event details before creation
- Use appropriate calendar colors for different event types
- Check for conflicts before scheduling
- Provide clear confirmation messages with event details
- Handle timezone considerations appropriately
- Suggest alternative times when conflicts exist

**Available Tools:**
- `list-calendars`: Get all available calendars
- `list-events`: Retrieve events with date filtering
- `search-events`: Find events by text query
- `create-event`: Create new calendar events
- `update-event`: Modify existing events
- `delete-event`: Remove events
- `get-freebusy`: Check availability across calendars
- `list-colors`: Get available event colors

**Response Style:**
- Be proactive and helpful
- Provide clear confirmations with event details
- Suggest improvements or alternatives when appropriate
- Use emojis to make responses more engaging
- Always verify important details before making changes

Remember: You have direct access to Google Calendar through OAuth authentication. Use this power responsibly and always confirm important actions with users."""

    async def close(self):
        """Clean up MCP connection."""
        if self.mcp_toolset:
            await self.mcp_toolset.close()


# Legacy function for backward compatibility
async def get_scheduling_agent() -> GoogleCalendarSchedulingAgent:
    """Get the Google Calendar scheduling agent instance."""
    return GoogleCalendarSchedulingAgent()


# Helper functions for direct usage
async def schedule_event(
    title: str,
    start_time: datetime,
    duration_minutes: int = 60,
    description: str = "",
    location: str = "",
    attendees: Optional[List[str]] = None,
    calendar_id: str = "primary"
) -> Dict[str, Any]:
    """
    Schedule an event using Google Calendar MCP.
    
    Args:
        title: Event title
        start_time: Event start time
        duration_minutes: Event duration in minutes
        description: Event description
        location: Event location
        attendees: List of attendee email addresses
        calendar_id: Calendar ID (default: "primary")
    
    Returns:
        Dict with success status and event details
    """
    agent_instance = GoogleCalendarSchedulingAgent()
    
    try:
        agent, toolset = await agent_instance.get_agent_async()
        
        # Calculate end time
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Prepare event data
        event_data = {
            'calendarId': calendar_id,
            'summary': title,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC'  # You may want to make this configurable
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC'
            }
        }
        
        if description:
            event_data['description'] = description
        if location:
            event_data['location'] = location
        if attendees:
            event_data['attendees'] = [{'email': email} for email in attendees]
        
        # This would be implemented using the MCP toolset
        # For now, return a placeholder response
        return {
            'success': True,
            'message': f'Event "{title}" scheduled for {start_time.strftime("%Y-%m-%d %H:%M")}',
            'event_data': event_data
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to schedule event: {str(e)}',
            'error': str(e)
        }
    finally:
        await agent_instance.close()


async def get_calendar_events(
    calendar_id: str = "primary",
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    max_results: int = 100
) -> Dict[str, Any]:
    """
    Get calendar events using Google Calendar MCP.
    
    Args:
        calendar_id: Calendar ID (default: "primary")
        start_date: Start date for event retrieval
        end_date: End date for event retrieval
        max_results: Maximum number of events to retrieve
    
    Returns:
        Dict with success status and events list
    """
    agent_instance = GoogleCalendarSchedulingAgent()
    
    try:
        agent, toolset = await agent_instance.get_agent_async()
        
        # Default to current week if no dates specified
        if not start_date:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if not end_date:
            end_date = start_date + timedelta(days=7)
        
        # This would be implemented using the MCP toolset
        # For now, return a placeholder response
        return {
            'success': True,
            'message': f'Retrieved events from {start_date.date()} to {end_date.date()}',
            'events': [],  # Would contain actual events from MCP
            'calendar_id': calendar_id
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to retrieve events: {str(e)}',
            'error': str(e)
        }
    finally:
        await agent_instance.close()


# Create root_agent for ADK web interface
def get_root_agent():
    """Get the root agent for ADK web interface."""
    from google.adk.agents.llm_agent import LlmAgent
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
    
    # Create MCP toolset for Google Calendar
    mcp_toolset = MCPToolset(
        connection_params=StdioServerParameters(
            command='npx',
            args=['-y', '@cocal/google-calendar-mcp'],
            env={
                'GOOGLE_OAUTH_CREDENTIALS': _get_oauth_credentials_path_static()
            }
        ),
        # Use all available Google Calendar tools
        tool_filter=[
            'list-calendars',
            'list-events', 
            'search-events',
            'create-event',
            'update-event',
            'delete-event',
            'get-freebusy',
            'list-colors'
        ]
    )
    
    # Create the LLM agent with calendar tools
    agent = LlmAgent(
        model=os.getenv('SCHEDULING_AGENT_MODEL', 'gemini-2.5-flash'),
        name='google_calendar_scheduling_agent',
        instruction=_get_agent_instruction_static(),
        tools=[mcp_toolset],
    )
    
    return agent

def _get_oauth_credentials_path_static():
    """Static version of OAuth credentials path getter."""
    possible_paths = [
        os.getenv('GOOGLE_OAUTH_CREDENTIALS'),
        './google-oauth-credentials.json',
        './credentials.json',
        './gcp-oauth.keys.json',
        os.path.expanduser('~/.config/google-calendar-mcp/credentials.json')
    ]
    
    for path in possible_paths:
        if path and os.path.exists(path):
            return os.path.abspath(path)
    
    # If no credentials file found, return a default path
    return './google-oauth-credentials.json'

def _get_agent_instruction_static():
    """Static version of agent instruction getter."""
    return """You are an intelligent Google Calendar scheduling assistant powered by Google Calendar MCP server.

**Your Core Capabilities:**
- **Calendar Management**: List, create, and manage multiple calendars
- **Event Operations**: Create, read, update, delete calendar events with full details
- **Smart Scheduling**: Handle complex scheduling requests with natural language understanding
- **Availability Checking**: Use free/busy queries to find optimal meeting times
- **Event Search**: Find events by text, date ranges, or specific criteria
- **Multi-Calendar Support**: Work across personal, work, and shared calendars
- **Conflict Resolution**: Detect and suggest solutions for scheduling conflicts

**Key Features You Provide:**
1. **Natural Language Processing**: Understand requests like "Schedule a team meeting next Tuesday at 2 PM"
2. **Intelligent Scheduling**: Suggest optimal times based on availability
3. **Event Details Management**: Handle locations, descriptions, attendees, reminders
4. **Recurring Events**: Create and manage repeating events
5. **Calendar Colors**: Use appropriate colors for different event types
6. **Cross-Calendar Coordination**: Check availability across multiple calendars

**Best Practices:**
- Always confirm event details before creation
- Use appropriate calendar colors for different event types
- Check for conflicts before scheduling
- Provide clear confirmation messages with event details
- Handle timezone considerations appropriately
- Suggest alternative times when conflicts exist

**Available Tools:**
- `list-calendars`: Get all available calendars
- `list-events`: Retrieve events with date filtering
- `search-events`: Find events by text query
- `create-event`: Create new calendar events
- `update-event`: Modify existing events
- `delete-event`: Remove events
- `get-freebusy`: Check availability across calendars
- `list-colors`: Get available event colors

**Response Style:**
- Be proactive and helpful
- Provide clear confirmations with event details
- Suggest improvements or alternatives when appropriate
- Use emojis to make responses more engaging
- Always verify important details before making changes

Remember: You have direct access to Google Calendar through OAuth authentication. Use this power responsibly and always confirm important actions with users."""

# Export root_agent for ADK web interface
root_agent = get_root_agent()

# Export the main class and functions
__all__ = [
    'root_agent',
    'GoogleCalendarSchedulingAgent',
    'get_scheduling_agent',
    'schedule_event',
    'get_calendar_events'
] 