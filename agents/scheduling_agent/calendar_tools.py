"""
Calendar Tools for Firebase-Based Scheduling

This module provides high-level tools for calendar operations using Firebase as the backend,
replacing the need for Google Calendar API and OAuth.
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
    """
    Create a calendar event in Firebase.
    
    Args:
        user_id: User identifier
        title: Event title
        start_time: When the event starts
        duration_minutes: Duration in minutes (default: 60)
        event_type: Type of event (meeting, therapy, workout, etc.)
        description: Optional description
        location: Optional location
        
    Returns:
        SchedulingToolResult with creation details
    """
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
                error_details={"conflicts": conflict_details},
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
    """
    Get calendar events for a user.
    
    Args:
        user_id: User identifier
        days_ahead: Number of days to look ahead (default: 7)
        event_type_filter: Optional filter by event type
        
    Returns:
        SchedulingToolResult with events list
    """
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


async def update_calendar_event(
    user_id: str,
    event_id: str,
    updates: Dict[str, Any]
) -> SchedulingToolResult:
    """
    Update a calendar event.
    
    Args:
        user_id: User identifier
        event_id: Event identifier to update
        updates: Dictionary of fields to update
        
    Returns:
        SchedulingToolResult with update status
    """
    try:
        # If updating time, check for conflicts
        if "start_time" in updates or "duration_minutes" in updates:
            # Get the current event
            current_event = await firebase_calendar.get_event_by_id(user_id, event_id)
            if not current_event:
                return SchedulingToolResult.error_result(
                    message="Event not found",
                    error_details=f"No event found with ID: {event_id}"
                )
            
            # Calculate new times
            new_start = updates.get("start_time", current_event["start_time"])
            new_duration = updates.get("duration_minutes", current_event["duration_minutes"])
            new_end = new_start + timedelta(minutes=new_duration)
            
            # Check conflicts (excluding this event)
            conflicts = await firebase_calendar.check_conflicts(
                user_id, new_start, new_end, exclude_event_id=event_id
            )
            
            if conflicts:
                return SchedulingToolResult.error_result(
                    message="Update would create scheduling conflict",
                    error_details={"conflicts": conflicts},
                    next_actions=["suggest_alternative_times", "force_update"]
                )
            
            # Update end_time if start_time or duration changed
            if "start_time" in updates or "duration_minutes" in updates:
                updates["end_time"] = new_end
        
        success = await firebase_calendar.update_event(user_id, event_id, updates)
        
        if success:
            return SchedulingToolResult.success_result(
                data={"event_id": event_id, "updates": updates},
                message="Event updated successfully"
            )
        else:
            return SchedulingToolResult.error_result(
                message="Failed to update event"
            )
            
    except Exception as e:
        logger.error(f"Failed to update event: {e}")
        return SchedulingToolResult.error_result(
            message="Failed to update event",
            error_details=str(e)
        )


async def delete_calendar_event(user_id: str, event_id: str) -> SchedulingToolResult:
    """
    Delete a calendar event.
    
    Args:
        user_id: User identifier
        event_id: Event identifier to delete
        
    Returns:
        SchedulingToolResult with deletion status
    """
    try:
        # Get event details before deletion for confirmation
        event = await firebase_calendar.get_event_by_id(user_id, event_id)
        if not event:
            return SchedulingToolResult.error_result(
                message="Event not found",
                error_details=f"No event found with ID: {event_id}"
            )
        
        success = await firebase_calendar.delete_event(user_id, event_id)
        
        if success:
            return SchedulingToolResult.success_result(
                data={"event_id": event_id, "deleted_event": event},
                message=f"Successfully deleted event '{event.get('title', 'Unknown')}'",
                next_actions=["view_calendar", "create_event"]
            )
        else:
            return SchedulingToolResult.error_result(
                message="Failed to delete event"
            )
            
    except Exception as e:
        logger.error(f"Failed to delete event: {e}")
        return SchedulingToolResult.error_result(
            message="Failed to delete event",
            error_details=str(e)
        )


async def find_available_slots(
    user_id: str,
    duration_minutes: int = 60,
    days_ahead: int = 7,
    work_hours_only: bool = True
) -> SchedulingToolResult:
    """
    Find available time slots for scheduling.
    
    Args:
        user_id: User identifier
        duration_minutes: Duration needed for the event
        days_ahead: Number of days to look ahead
        work_hours_only: Whether to only suggest business hours
        
    Returns:
        SchedulingToolResult with available slots
    """
    try:
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=days_ahead)
        
        # Get existing events
        existing_events = await firebase_calendar.get_events(user_id, start_date, end_date)
        
        # Generate potential time slots
        available_slots = []
        current_day = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)  # Start at 9 AM
        
        while current_day < end_date:
            # Skip past times
            if current_day < datetime.now():
                current_day += timedelta(hours=1)
                continue
            
            # Work hours check
            if work_hours_only and (current_day.hour < 9 or current_day.hour >= 17):
                current_day += timedelta(hours=1)
                continue
            
            # Check if this slot conflicts with existing events
            slot_end = current_day + timedelta(minutes=duration_minutes)
            
            is_available = True
            for event in existing_events:
                event_start = event["start_time"]
                event_end = event["end_time"]
                
                # Check for overlap
                if (current_day < event_end) and (slot_end > event_start):
                    is_available = False
                    break
            
            if is_available:
                available_slots.append(current_day)
            
            # Move to next hour
            current_day += timedelta(hours=1)
            
            # Limit results
            if len(available_slots) >= 10:
                break
        
        return SchedulingToolResult.success_result(
            data={"available_slots": available_slots, "duration_minutes": duration_minutes},
            message=f"Found {len(available_slots)} available slots"
        )
        
    except Exception as e:
        logger.error(f"Failed to find available slots: {e}")
        return SchedulingToolResult.error_result(
            message="Failed to find available slots",
            error_details=str(e)
        )


async def create_recurring_events(
    user_id: str,
    title: str,
    start_time: datetime,
    duration_minutes: int,
    event_type: str,
    recurrence_pattern: str,
    end_date: datetime,
    description: str = "",
    location: str = ""
) -> SchedulingToolResult:
    """
    Create recurring calendar events.
    
    Args:
        user_id: User identifier
        title: Event title
        start_time: First occurrence start time
        duration_minutes: Duration of each event
        event_type: Type of event
        recurrence_pattern: Pattern (daily, weekly, biweekly, monthly)
        end_date: When to stop creating recurring events
        description: Optional description
        location: Optional location
        
    Returns:
        SchedulingToolResult with creation details
    """
    try:
        created_events = []
        failed_events = []
        
        current_time = start_time
        
        while current_time <= end_date:
            # Try to create event at this time
            result = await create_calendar_event(
                user_id=user_id,
                title=title,
                start_time=current_time,
                duration_minutes=duration_minutes,
                event_type=event_type,
                description=f"{description} (Recurring {recurrence_pattern})",
                location=location
            )
            
            if result.success:
                created_events.append(current_time)
            else:
                failed_events.append({
                    "time": current_time,
                    "reason": result.message
                })
            
            # Calculate next occurrence
            if recurrence_pattern == "daily":
                current_time += timedelta(days=1)
            elif recurrence_pattern == "weekly":
                current_time += timedelta(weeks=1)
            elif recurrence_pattern == "biweekly":
                current_time += timedelta(weeks=2)
            elif recurrence_pattern == "monthly":
                # Simple monthly - same day next month
                if current_time.month == 12:
                    current_time = current_time.replace(year=current_time.year + 1, month=1)
                else:
                    current_time = current_time.replace(month=current_time.month + 1)
            else:
                break  # Unknown pattern
        
        if created_events:
            return SchedulingToolResult.success_result(
                data={
                    "created_events": created_events,
                    "failed_events": failed_events,
                    "pattern": recurrence_pattern
                },
                message=f"Created {len(created_events)} recurring events ({recurrence_pattern})",
                next_actions=["view_calendar", "modify_series"]
            )
        else:
            return SchedulingToolResult.error_result(
                message="Failed to create any recurring events",
                error_details={"failed_events": failed_events}
            )
            
    except Exception as e:
        logger.error(f"Failed to create recurring events: {e}")
        return SchedulingToolResult.error_result(
            message="Failed to create recurring events",
            error_details=str(e)
        ) 