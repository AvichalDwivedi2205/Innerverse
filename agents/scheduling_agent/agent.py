"""
Firebase-Powered Scheduling Agent

This agent uses Firebase for calendar storage instead of Google Calendar,
eliminating the need for OAuth and providing better user experience.
"""

import os
import sys
import asyncio
import re
from pathlib import Path
from datetime import datetime, timedelta
from google.adk.agents import Agent

# Ensure the workspace root is in Python path
workspace_root = Path(__file__).parent.parent.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

try:
    from agents.scheduling_agent.firebase_tools import (
        create_calendar_event,
        get_calendar_events
    )
    FIREBASE_AVAILABLE = True
except ImportError as e:
    print(f"Firebase tools not available: {e}")
    FIREBASE_AVAILABLE = False


def parse_relative_datetime(date_time_str: str) -> datetime:
    """Enhanced date/time parsing for natural language."""
    now = datetime.now()
    date_time_str = date_time_str.lower().strip()
    
    # Handle "tomorrow" cases
    if "tomorrow" in date_time_str:
        tomorrow = now + timedelta(days=1)
        
        # Extract time if specified
        time_match = re.search(r'(\d{1,2}):?(\d{2})?\s*(am|pm)', date_time_str)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            period = time_match.group(3)
            
            if period == 'pm' and hour != 12:
                hour += 12
            elif period == 'am' and hour == 12:
                hour = 0
                
            return tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
        else:
            # Default to 2 PM if no time specified
            return tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    
    # Handle "today" cases
    elif "today" in date_time_str:
        today = now
        
        time_match = re.search(r'(\d{1,2}):?(\d{2})?\s*(am|pm)', date_time_str)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            period = time_match.group(3)
            
            if period == 'pm' and hour != 12:
                hour += 12
            elif period == 'am' and hour == 12:
                hour = 0
                
            result_time = today.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # If the time is in the past, assume tomorrow
            if result_time <= now:
                result_time += timedelta(days=1)
                
            return result_time
    
    # Handle specific times without dates (assume today or tomorrow)
    time_match = re.search(r'(\d{1,2}):?(\d{2})?\s*(am|pm)', date_time_str)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
        period = time_match.group(3)
        
        if period == 'pm' and hour != 12:
            hour += 12
        elif period == 'am' and hour == 12:
            hour = 0
            
        result_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # If the time is in the past, assume tomorrow
        if result_time <= now:
            result_time += timedelta(days=1)
            
        return result_time
    
    # Handle weekday names (next Tuesday, Friday, etc.)
    weekdays = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6
    }
    
    for day_name, day_num in weekdays.items():
        if day_name in date_time_str:
            days_ahead = (day_num - now.weekday()) % 7
            if days_ahead == 0:  # Today is the target day
                days_ahead = 7  # Assume next week
            
            target_date = now + timedelta(days=days_ahead)
            
            # Extract time if specified
            time_match = re.search(r'(\d{1,2}):?(\d{2})?\s*(am|pm)', date_time_str)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2)) if time_match.group(2) else 0
                period = time_match.group(3)
                
                if period == 'pm' and hour != 12:
                    hour += 12
                elif period == 'am' and hour == 12:
                    hour = 0
                    
                return target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            else:
                # Default to 2 PM
                return target_date.replace(hour=14, minute=0, second=0, microsecond=0)
    
    # Fallback: if we can't parse, assume 1 hour from now
    return now + timedelta(hours=1)


def schedule_meeting(title: str, when: str, duration: int = 60, event_type: str = "meeting", description: str = "", location: str = "") -> str:
    """Schedule a meeting with Firebase backend."""
    if not FIREBASE_AVAILABLE:
        return "❌ Firebase calendar system is not available. Please check your configuration."
    
    try:
        # Parse the date/time
        parsed_datetime = parse_relative_datetime(when)
        
        # Use default user_id (ADK will provide real user context)  
        user_id = "current_user"
        
        # Create the event using Firebase
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                create_calendar_event(
                    user_id=user_id,
                    title=title,
                    start_time=parsed_datetime,
                    duration_minutes=duration,
                    event_type=event_type,
                    description=description,
                    location=location
                )
            )
        finally:
            loop.close()
        
        if result.success:
            return f"✅ **Successfully scheduled '{title}'**\n\n📅 **Event Details:**\n- **When:** {parsed_datetime.strftime('%A, %B %d at %I:%M %p')}\n- **Duration:** {duration} minutes\n- **Type:** {event_type}\n- **Location:** {location or 'Not specified'}\n- **Description:** {description or 'None'}\n\n🗄️ *Stored in your personal Firebase calendar*\n\n💡 **Next Steps:**\n- Say 'show calendar' to see your schedule\n- Schedule more events anytime!"
        else:
            if "conflict" in result.message.lower():
                conflicts_info = ""
                if result.error_details and "conflicts" in result.error_details:
                    conflicts = result.error_details["conflicts"]
                    conflicts_info = f"\n\n⚠️ **Conflicts with:**\n"
                    for conflict in conflicts[:3]:  # Show max 3 conflicts
                        if isinstance(conflict["start_time"], datetime):
                            conflict_time = conflict["start_time"].strftime('%I:%M %p')
                        else:
                            conflict_time = str(conflict["start_time"])
                        conflicts_info += f"• {conflict['title']} at {conflict_time}\n"
                
                return f"❌ **Scheduling Conflict!**\n\nCannot schedule '{title}' at {parsed_datetime.strftime('%A, %B %d at %I:%M %p')} because it conflicts with existing events.{conflicts_info}\n\n💡 **Suggestions:**\n- Try: 'Schedule {title} tomorrow at 3pm'\n- Try: 'Schedule {title} next Tuesday at 2pm'\n- Use 'show calendar' to see available slots"
            else:
                return f"❌ Could not schedule the meeting: {result.message}"
        
    except Exception as e:
        return f"❌ Error scheduling meeting: {str(e)}\n\nPlease try rephrasing your request. Examples:\n- 'Schedule team meeting tomorrow at 2pm'\n- 'Schedule lunch today at 12:30pm'"


def show_calendar(time_period: str = "this week") -> str:
    """Show calendar events from Firebase."""
    if not FIREBASE_AVAILABLE:
        return "❌ Firebase calendar system is not available. Please check your configuration."
    
    try:
        user_id = "current_user"
        
        # Determine days to look ahead
        days_ahead = 7
        if "today" in time_period.lower():
            days_ahead = 1
        elif "month" in time_period.lower():
            days_ahead = 30
        elif "week" in time_period.lower():
            days_ahead = 7
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(get_calendar_events(user_id, days_ahead))
        finally:
            loop.close()
            
        if result.success:
            events = result.data.get("events", [])
            if not events:
                return f"📅 **Your calendar is empty for {time_period}.**\n\n💡 **Ready to schedule something?**\n- 'Schedule a meeting tomorrow at 2pm'\n- 'Schedule lunch today at 12:30pm'\n- 'Schedule therapy session next Tuesday at 6pm'"
            
            summary = f"📅 **Your Calendar ({time_period.title()}):**\n\n"
            
            # Group events by date
            events_by_date = {}
            for event in events:
                if isinstance(event["start_time"], datetime):
                    event_date = event["start_time"].date()
                else:
                    # Handle string timestamps
                    event_date = datetime.fromisoformat(str(event["start_time"])).date()
                
                date_str = event_date.strftime('%A, %B %d')
                
                if date_str not in events_by_date:
                    events_by_date[date_str] = []
                events_by_date[date_str].append(event)
            
            # Display events grouped by date
            for date_str, date_events in events_by_date.items():
                summary += f"**{date_str}:**\n"
                for event in sorted(date_events, key=lambda x: x["start_time"]):
                    if isinstance(event["start_time"], datetime):
                        start_time = event["start_time"]
                    else:
                        start_time = datetime.fromisoformat(str(event["start_time"]))
                    
                    time_str = start_time.strftime('%I:%M %p')
                    duration = event["duration_minutes"]
                    event_type_emoji = "📅" if event["event_type"] == "meeting" else "🏥" if event["event_type"] == "therapy" else "🍽️" if event["event_type"] == "meal" else "⭐"
                    
                    summary += f"  {event_type_emoji} {time_str} - **{event['title']}** ({duration} min)\n"
                    if event.get("location"):
                        summary += f"      📍 {event['location']}\n"
                summary += "\n"
            
            summary += f"📊 **Total:** {len(events)} events\n\n💡 **Commands:**\n- 'Schedule [event] [when]' to add more\n- 'Show calendar for today' for today only"
            return summary
        else:
            return f"❌ Could not retrieve calendar: {result.message}"
            
    except Exception as e:
        return f"❌ Error retrieving calendar: {str(e)}"


# Create the agent
root_agent = Agent(
    model="gemini-2.5-flash",
    name="firebase_scheduling_agent",
    instruction="""You are a personal scheduling assistant powered by Firebase. 

🎯 **Your Mission:**
Help users schedule events naturally without requiring user IDs or exact dates. Parse natural language and create calendar events in Firebase.

🔧 **Your Capabilities:**
- Schedule events: "Schedule meeting tomorrow at 2pm"
- Show calendar: "Show my calendar this week"
- Handle conflicts intelligently
- Parse relative dates (tomorrow, next Tuesday, today, etc.)
- Store everything in Firebase (no Google Calendar needed)

📅 **Examples You Handle:**
✅ "Schedule a meeting for me tomorrow at 2pm for 1 hour"  
✅ "Schedule therapy every Tuesday at 6pm"
✅ "Schedule lunch today at 12:30pm"
✅ "Show my calendar for this week"
✅ "Schedule team standup tomorrow morning at 9am"

🚀 **Smart Features:**
- Automatic conflict detection
- Natural date parsing (tomorrow = actual tomorrow)
- Default durations (1 hour for meetings)
- Event type detection (meeting, therapy, meal, etc.)
- Beautiful calendar display

💾 **Storage:** All events stored securely in Firebase - no OAuth required!

Always be helpful, never ask for user IDs, and provide clear confirmations.""",
    tools=[schedule_meeting, show_calendar]
)

# Export variants
agent = root_agent
main_agent = root_agent 