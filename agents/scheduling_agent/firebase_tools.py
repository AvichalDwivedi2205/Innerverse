"""
Firebase Calendar Tools for Scheduling Agent

This module provides Firebase-based calendar operations without requiring Google Calendar OAuth.
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

# Ensure the workspace root is in Python path
workspace_root = Path(__file__).parent.parent.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

from agents.scheduling_agent.firebase_calendar import firebase_calendar
from agents.common.tool_results import SchedulingToolResult

logger = logging.getLogger(__name__)


async def create_calendar_event(
    user_id: str,
    title: str,
    start_time: datetime,
    duration_minutes: int = 60,
    event_type: str = "personal",
    description: str = "",
    location: str = ""
) -> SchedulingToolResult:
    """Create a calendar event in Firebase."""
    try:
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Check for conflicts first
        conflicts = await firebase_calendar.check_conflicts(user_id, start_time, end_time)
        
        if conflicts:
            conflict_details = []
            for conflict in conflicts:
                conflict_details.append({
                    "title": conflict["title"],
                    "start_time": conflict["start_time"],
                    "end_time": conflict["end_time"],
                    "event_type": conflict.get("event_type", "unknown")
                })
            
            return SchedulingToolResult.error_result(
                message=f"Scheduling conflict detected with {len(conflicts)} existing event(s)",
                error_details=f"Conflicts: {', '.join([c['title'] for c in conflict_details[:3]])}",
                next_actions=["suggest_alternative_times", "force_create", "resolve_conflicts"]
            )
        
        # Create event data
        event_data = {
            "title": title,
            "description": description,
            "start_time": start_time,
            "end_time": end_time,
            "duration_minutes": duration_minutes,
            "event_type": event_type,
            "location": location
        }
        
        # Create the event
        result = await firebase_calendar.create_event(user_id, event_data)
        
        return SchedulingToolResult.success_result(
            data=result,
            message=f"Successfully scheduled '{title}' for {start_time.strftime('%A, %B %d at %I:%M %p')}",
            scheduled_time=start_time,
            schedule_category=event_type,
            next_actions=["view_calendar", "set_reminders"]
        )
        
    except Exception as e:
        logger.error(f"Failed to create calendar event: {e}")
        return SchedulingToolResult.error_result(
            message="Failed to create calendar event",
            error_details=str(e)
        )


async def get_calendar_events(
    user_id: str,
    days_ahead: int = 7,
    event_type_filter: str = None
) -> SchedulingToolResult:
    """Get calendar events for a user."""
    try:
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=days_ahead)
        
        events = await firebase_calendar.get_events(user_id, start_date, end_date)
        
        # Filter by event type if specified
        if event_type_filter:
            events = [e for e in events if e.get("event_type") == event_type_filter]
        
        return SchedulingToolResult.success_result(
            data={"events": events, "count": len(events)},
            message=f"Retrieved {len(events)} events for the next {days_ahead} days"
        )
        
    except Exception as e:
        logger.error(f"Failed to retrieve calendar events: {e}")
        return SchedulingToolResult.error_result(
            message="Failed to retrieve calendar events",
            error_details=str(e)
        ) 