"""ADK Agent Interface for Scheduling Agent - FIXED VERSION.

This file exposes the root_agent that the ADK web interface expects to find.
It wraps the SchedulingAgent class to make it compatible with ADK web.
"""

import os
import sys
import asyncio
import re
from pathlib import Path
from datetime import datetime, timedelta
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext

# Ensure the workspace root is in Python path for proper imports
workspace_root = Path(__file__).parent.parent.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

def parse_relative_datetime(date_time_str: str) -> datetime:
    """Parse relative date/time expressions like 'tomorrow at 2pm'."""
    date_time_lower = date_time_str.lower().strip()
    now = datetime.now()
    
    # Handle "tomorrow"
    if "tomorrow" in date_time_lower:
        base_date = now + timedelta(days=1)
        
        # Extract time - enhanced pattern matching
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(am|pm)',  # 2:30pm
            r'(\d{1,2})\s*(am|pm)',          # 2pm
            r'at\s+(\d{1,2}):(\d{2})\s*(am|pm)',  # at 2:30pm
            r'at\s+(\d{1,2})\s*(am|pm)'           # at 2pm
        ]
        
        for pattern in time_patterns:
            time_match = re.search(pattern, date_time_lower)
            if time_match:
                groups = time_match.groups()
                hour = int(groups[0])
                
                if len(groups) >= 3 and groups[1] and groups[1].isdigit():
                    # Has minutes (2:30pm format)
                    minutes = int(groups[1])
                    ampm = groups[2]
                else:
                    # Just hour (2pm format)
                    minutes = 0
                    ampm = groups[1] if len(groups) > 1 else groups[-1]
                
                if ampm == 'pm' and hour != 12:
                    hour += 12
                elif ampm == 'am' and hour == 12:
                    hour = 0
                    
                return base_date.replace(hour=hour, minute=minutes, second=0, microsecond=0)
        
        # Default to 2 PM if no time specified
        return base_date.replace(hour=14, minute=0, second=0, microsecond=0)
    
    # Handle "today"
    elif "today" in date_time_lower:
        base_date = now
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(am|pm)',
            r'(\d{1,2})\s*(am|pm)',
            r'at\s+(\d{1,2}):(\d{2})\s*(am|pm)',
            r'at\s+(\d{1,2})\s*(am|pm)'
        ]
        
        for pattern in time_patterns:
            time_match = re.search(pattern, date_time_lower)
            if time_match:
                groups = time_match.groups()
                hour = int(groups[0])
                
                if len(groups) >= 3 and groups[1] and groups[1].isdigit():
                    minutes = int(groups[1])
                    ampm = groups[2]
                else:
                    minutes = 0
                    ampm = groups[1] if len(groups) > 1 else groups[-1]
                    
                if ampm == 'pm' and hour != 12:
                    hour += 12
                elif ampm == 'am' and hour == 12:
                    hour = 0
                    
                return base_date.replace(hour=hour, minute=minutes, second=0, microsecond=0)
    
    # Handle "next [day]"
    elif "next" in date_time_lower:
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for i, day in enumerate(days):
            if day in date_time_lower:
                days_ahead = (i - now.weekday() + 7) % 7
                if days_ahead == 0:  # If it's the same day, go to next week
                    days_ahead = 7
                base_date = now + timedelta(days=days_ahead)
                
                # Extract time with same patterns
                time_patterns = [
                    r'(\d{1,2}):(\d{2})\s*(am|pm)',
                    r'(\d{1,2})\s*(am|pm)',
                    r'at\s+(\d{1,2}):(\d{2})\s*(am|pm)',
                    r'at\s+(\d{1,2})\s*(am|pm)'
                ]
                
                for pattern in time_patterns:
                    time_match = re.search(pattern, date_time_lower)
                    if time_match:
                        groups = time_match.groups()
                        hour = int(groups[0])
                        
                        if len(groups) >= 3 and groups[1] and groups[1].isdigit():
                            minutes = int(groups[1])
                            ampm = groups[2]
                        else:
                            minutes = 0
                            ampm = groups[1] if len(groups) > 1 else groups[-1]
                            
                        if ampm == 'pm' and hour != 12:
                            hour += 12
                        elif ampm == 'am' and hour == 12:
                            hour = 0
                            
                        return base_date.replace(hour=hour, minute=minutes, second=0, microsecond=0)
                break
    
    # If no relative date found, try to parse as absolute
    try:
        from dateutil import parser
        return parser.parse(date_time_str)
    except:
        # Last resort - return current time + 1 hour
        return now + timedelta(hours=1)

# Create wrapper functions that don't require user_id from the user
def schedule_meeting(title: str, when: str, duration: int = 60, event_type: str = "meeting", description: str = "") -> str:
    """
    Schedule a meeting with natural language date/time parsing.
    
    Args:
        title: Meeting title
        when: When to schedule (e.g., "tomorrow at 2pm", "next Tuesday at 10am")
        duration: Duration in minutes (default: 60)
        event_type: Type of event (default: "meeting")
        description: Optional description
    """
    try:
        # Parse the relative date/time
        parsed_datetime = parse_relative_datetime(when)
        
        # Format for the underlying function
        event_datetime_str = parsed_datetime.strftime('%Y-%m-%d %H:%M:%S')
        
        # Use a default user_id - ADK should provide this in context
        user_id = "current_user"  # This will be replaced by ADK's user session
        
        # Import and call the actual scheduling function
        from agents.scheduling_agent.tools import create_event
        
        # Run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                create_event(user_id, title, event_datetime_str, duration, event_type, description)
            )
        finally:
            loop.close()
        
        if result.success:
            return f"✅ Successfully scheduled '{title}' for {parsed_datetime.strftime('%A, %B %d at %I:%M %p')} ({duration} minutes)\n\nEvent Details:\n- Title: {title}\n- Date/Time: {parsed_datetime.strftime('%A, %B %d at %I:%M %p')}\n- Duration: {duration} minutes\n- Type: {event_type}\n- Description: {description or 'None'}"
        else:
            # Check if it's an OAuth/authentication error
            if "oauth" in result.message.lower() or "auth" in result.message.lower() or "permission" in result.message.lower():
                return f"🔐 Calendar access required! Please authenticate with Google Calendar:\n\n1. I'll open a browser window for you to sign in\n2. Grant permission to access your calendar\n3. After that, scheduling will work automatically\n\nError details: {result.message}"
            else:
                return f"❌ Could not schedule the meeting: {result.message}\n\nTried to schedule:\n- Title: {title}\n- When: {when} (parsed as {parsed_datetime.strftime('%A, %B %d at %I:%M %p')})\n- Duration: {duration} minutes"
                
    except Exception as e:
        return f"❌ Error scheduling meeting: {str(e)}\n\nPlease try rephrasing your request. Examples:\n- 'Schedule a meeting tomorrow at 2pm for 1 hour'\n- 'Schedule therapy next Tuesday at 6pm'\n- 'Schedule lunch today at 12:30pm for 30 minutes'"

def show_calendar(time_period: str = "this week") -> str:
    """
    Show calendar events for a specified time period.
    
    Args:
        time_period: Time period to show (e.g., "today", "this week", "next week")
    """
    try:
        user_id = "current_user"  # ADK should provide this automatically
        
        from agents.scheduling_agent.tools import read_events
        
        # Simple implementation for now
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(read_events(user_id, "", None))
        finally:
            loop.close()
            
        if result.success and result.data.get('events'):
            events = result.data['events']
            if not events:
                return "📅 Your calendar is empty for the specified period."
            
            summary = f"📅 **Your Calendar ({time_period}):**\n\n"
            for event in events[:10]:  # Limit to 10 events
                title = event.get('title', 'Untitled')
                scheduled_time = event.get('scheduledTime', event.get('datetime', 'Unknown time'))
                duration = event.get('durationMinutes', event.get('duration', 60))
                event_type = event.get('type', event.get('event_type', 'personal'))
                
                # Format time
                if isinstance(scheduled_time, str):
                    try:
                        scheduled_time = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                        time_str = scheduled_time.strftime('%A, %B %d at %I:%M %p')
                    except:
                        time_str = str(scheduled_time)
                elif isinstance(scheduled_time, datetime):
                    time_str = scheduled_time.strftime('%A, %B %d at %I:%M %p')
                else:
                    time_str = str(scheduled_time)
                
                summary += f"• **{title}** ({event_type}) - {time_str} ({duration} min)\n"
            
            return summary
        else:
            return f"❌ Could not retrieve your calendar events: {result.message if hasattr(result, 'message') else 'Unknown error'}"
            
    except Exception as e:
        return f"❌ Error retrieving calendar: {str(e)}"

def quick_schedule(request: str) -> str:
    """
    Handle quick scheduling requests in natural language.
    
    Args:
        request: Natural language request (e.g., "meeting tomorrow 2pm 1 hour")
    """
    try:
        # Parse the request to extract components
        request_lower = request.lower()
        
        # Extract title (default to "Meeting" if not clear)
        title = "Meeting"
        if "therapy" in request_lower:
            title = "Therapy Session"
        elif "workout" in request_lower or "exercise" in request_lower or "gym" in request_lower:
            title = "Workout"
        elif "lunch" in request_lower:
            title = "Lunch"
        elif "dinner" in request_lower:
            title = "Dinner"
        elif "call" in request_lower:
            title = "Phone Call"
        elif "interview" in request_lower:
            title = "Interview"
        
        # Extract duration
        duration = 60  # default
        duration_match = re.search(r'(\d+)\s*(hour|hr|minute|min)', request_lower)
        if duration_match:
            num = int(duration_match.group(1))
            unit = duration_match.group(2)
            if "hour" in unit or "hr" in unit:
                duration = num * 60
            else:
                duration = num
        
        # Use the main scheduling function
        return schedule_meeting(title, request, duration)
        
    except Exception as e:
        return f"❌ Error processing request: {str(e)}\n\nPlease try: 'Schedule a meeting tomorrow at 2pm for 1 hour'"

# Create the agent with the wrapper functions
try:
    from agents.scheduling_agent.prompts import SCHEDULING_AGENT_SYSTEM_PROMPT
    
    root_agent = Agent(
        model="gemini-2.5-flash",
        name="scheduling_agent", 
        instruction="""You are a helpful scheduling assistant. You can:

1. Schedule meetings and appointments using natural language
2. Show calendar events  
3. Handle recurring events
4. Parse relative dates like "tomorrow", "next Tuesday", etc.

Key capabilities:
- Use schedule_meeting() for specific scheduling requests
- Use show_calendar() to display calendar events  
- Use quick_schedule() for simple natural language requests

When users say things like:
- "Schedule a meeting tomorrow at 2pm" → Use schedule_meeting()
- "Schedule therapy every Tuesday at 6pm" → Use schedule_meeting()
- "Show my calendar" → Use show_calendar()
- "meeting tomorrow 2pm" → Use quick_schedule()

You handle authentication and user context automatically. If OAuth is needed for calendar access, guide the user through the process.

IMPORTANT: You do NOT need to ask for user IDs or exact dates. You can parse:
- "tomorrow" = next day
- "today" = current day  
- "next Tuesday" = next occurrence of Tuesday
- "2pm" = 2:00 PM
- "2:30pm" = 2:30 PM

Always use the wrapper functions that handle user context automatically.""",
        tools=[schedule_meeting, show_calendar, quick_schedule]
    )
    
    # For compatibility with different naming conventions
    agent = root_agent
    main_agent = root_agent

except Exception as e:
    print(f"Error creating scheduling agent: {e}")
    
    def fallback_schedule(title: str, when: str, duration: int = 60) -> str:
        return f"Scheduling agent not fully available. Would schedule: {title} at {when} for {duration} minutes."
    
    root_agent = Agent(
        model="gemini-2.5-flash",
        name="scheduling_agent_fallback",
        instruction="I'm a fallback scheduling agent with limited functionality.",
        tools=[fallback_schedule]
    )
    
    agent = root_agent
    main_agent = root_agent

# Export the agent
__all__ = ['root_agent', 'agent', 'main_agent'] 