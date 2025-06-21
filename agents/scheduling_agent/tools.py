"""Scheduling Agent Tools.

This module provides all the tools for the scheduling agent including
CRUD operations, bulk operations, and intelligent conflict resolution.
"""

import uuid
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Ensure the workspace root is in Python path for proper imports
workspace_root = Path(__file__).parent.parent.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

from google.cloud import firestore
from agents.common.tool_results import SchedulingToolResult
from agents.common.google_services import google_services
from agents.scheduling_agent.event_parser import EventParser
from agents.scheduling_agent.conflict_resolver import ConflictResolver
from agents.scheduling_agent.recurring_events import RecurringEventsHandler

logger = logging.getLogger(__name__)


class SchedulingTools:
    """Collection of scheduling tools and utilities."""
    
    def __init__(self):
        self.event_parser = EventParser()
        self.conflict_resolver = ConflictResolver()
        self.recurring_handler = RecurringEventsHandler()
        self.db = firestore.Client()
    
    async def get_user_calendar(self, user_id: str, date_range: Optional[Dict] = None) -> List[Dict]:
        """Retrieve user's existing calendar events."""
        try:
            # Get events from Firestore
            schedules_ref = self.db.collection("users").document(user_id).collection("schedules")
            
            if date_range:
                start_date = date_range.get('start_date')
                end_date = date_range.get('end_date')
                if start_date and end_date:
                    schedules_ref = schedules_ref.where("scheduledTime", ">=", start_date).where("scheduledTime", "<=", end_date)
            
            docs = schedules_ref.stream()
            events = []
            
            for doc in docs:
                event_data = doc.to_dict()
                events.append(event_data)
            
            return events
            
        except Exception as e:
            logger.error(f"Error retrieving user calendar: {e}")
            return []


# ============================================================================
# SINGLE EVENT CRUD OPERATIONS
# ============================================================================

async def create_event(
    user_id: str,
    title: str,
    event_datetime: str,
    duration: int,
    event_type: str,
    description: str = ""
) -> SchedulingToolResult:
    """
    Create a single calendar event.
    
    Args:
        user_id: User identifier
        title: Event title
        event_datetime: When the event starts (ISO format string: YYYY-MM-DD HH:MM:SS or YYYY-MM-DDTHH:MM:SS)
        duration: Duration in minutes
        event_type: Type of event (therapy, exercise, personal, etc.)
        description: Optional event description
        
    Returns:
        SchedulingToolResult with creation details
    """
    try:
        tools = SchedulingTools()
        
        # Parse datetime string to datetime object
        try:
            # Handle different datetime string formats
            if 'T' in event_datetime:
                # ISO format with T separator
                parsed_datetime = datetime.fromisoformat(event_datetime.replace('Z', '+00:00'))
            else:
                # Format: YYYY-MM-DD HH:MM:SS
                parsed_datetime = datetime.strptime(event_datetime, '%Y-%m-%d %H:%M:%S')
        except ValueError as e:
            return SchedulingToolResult.error_result(
                message="Invalid datetime format",
                error_details=f"Please use format 'YYYY-MM-DD HH:MM:SS' or ISO format. Error: {str(e)}"
            )
        
        # Create event data
        event_data = {
            'title': title,
            'datetime': parsed_datetime,
            'duration': duration,
            'event_type': event_type,
            'description': description
        }
        
        # Check for conflicts
        existing_calendar = await tools.get_user_calendar(user_id)
        conflicts = tools.conflict_resolver.check_bulk_conflicts(existing_calendar, [event_data])
        
        if conflicts:
            # Return conflict information
            conflict_details = conflicts[0]
            return SchedulingToolResult.error_result(
                message=f"Scheduling conflict detected for '{title}'",
                error_details=f"Conflicts with {len(conflict_details['conflicts'])} existing events",
                next_actions=["suggest_alternative_times", "resolve_conflicts"]
            )
        
        # No conflicts, create the event
        schedule_id = str(uuid.uuid4())
        end_time = parsed_datetime + timedelta(minutes=duration)
        
        # Create Google Calendar event
        google_event_details = {
            "title": title,
            "description": description,
            "start_time": parsed_datetime,
            "end_time": end_time
        }
        
        google_event_id = await google_services.create_calendar_event(google_event_details)
        
        # Store in Firestore
        category = "wellness" if event_type in ["therapy", "exercise", "journaling"] else "personal"
        
        schedule_doc = {
            "scheduleId": schedule_id,
            "userId": user_id,
            "title": title,
            "description": description,
            "type": event_type,
            "category": category,
            "googleEventId": google_event_id,
            "scheduledTime": parsed_datetime,
            "endTime": end_time,
            "durationMinutes": duration,
            "frequency": "once",
            "status": "scheduled",
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        tools.db.collection("users").document(user_id).collection("schedules").document(schedule_id).set(schedule_doc)
        
        logger.info(f"Event created: {title} for user {user_id}")
        
        return SchedulingToolResult.success_result(
            data={
                "schedule_id": schedule_id,
                "google_event_id": google_event_id,
                "event_details": schedule_doc
            },
            message=f"Successfully scheduled '{title}' for {parsed_datetime.strftime('%Y-%m-%d %H:%M')}",
            google_event_id=google_event_id,
            scheduled_time=parsed_datetime,
            schedule_category=category,
            frequency="once",
            next_actions=["view_calendar", "set_reminders"]
        )
        
    except Exception as e:
        logger.error(f"Failed to create event: {e}")
        return SchedulingToolResult.error_result(
            message="Failed to create event",
            error_details=str(e)
        )


async def read_events(
    user_id: str,
    date_range: str = "",
    event_type: Optional[str] = None
) -> SchedulingToolResult:
    """
    Read/list calendar events for a user.
    
    Args:
        user_id: User identifier
        date_range: Optional date range filter as JSON string (e.g., '{"start_date": "2024-01-01", "end_date": "2024-01-31"}')
        event_type: Optional event type filter
        
    Returns:
        SchedulingToolResult with events list
    """
    try:
        tools = SchedulingTools()
        
        # Parse date_range string to dict if provided
        parsed_date_range = None
        if date_range and date_range.strip():
            try:
                parsed_date_range = json.loads(date_range)
                # Convert string dates to datetime objects if needed
                if 'start_date' in parsed_date_range:
                    parsed_date_range['start_date'] = datetime.fromisoformat(parsed_date_range['start_date'])
                if 'end_date' in parsed_date_range:
                    parsed_date_range['end_date'] = datetime.fromisoformat(parsed_date_range['end_date'])
            except (json.JSONDecodeError, ValueError) as e:
                return SchedulingToolResult.error_result(
                    message="Invalid date range format",
                    error_details=f"Please provide date_range as JSON: {str(e)}"
                )
        
        events = await tools.get_user_calendar(user_id, parsed_date_range)
        
        # Filter by event type if specified
        if event_type:
            events = [event for event in events if event.get('type') == event_type]
        
        return SchedulingToolResult.success_result(
            data={
                "events": events,
                "count": len(events),
                "date_range": parsed_date_range,
                "event_type": event_type
            },
            message=f"Retrieved {len(events)} events",
            next_actions=["create_event", "update_event", "delete_event"]
        )
        
    except Exception as e:
        logger.error(f"Failed to read events: {e}")
        return SchedulingToolResult.error_result(
            message="Failed to retrieve events",
            error_details=str(e)
        )


async def update_event(
    user_id: str,
    event_id: str,
    updated_details: str
) -> SchedulingToolResult:
    """
    Update an existing calendar event.
    
    Args:
        user_id: User identifier
        event_id: Event identifier to update
        updated_details: JSON string of fields to update (e.g., '{"title": "New Title", "duration": 90}')
        
    Returns:
        SchedulingToolResult with update status
    """
    try:
        tools = SchedulingTools()
        
        # Parse updated_details string to dict
        try:
            parsed_details = json.loads(updated_details)
        except json.JSONDecodeError as e:
            return SchedulingToolResult.error_result(
                message="Invalid update details format",
                error_details=f"Please provide updated_details as JSON: {str(e)}"
            )
        
        # Get existing event
        event_ref = tools.db.collection("users").document(user_id).collection("schedules").document(event_id)
        event_doc = event_ref.get()
        
        if not event_doc.exists:
            return SchedulingToolResult.error_result(
                message="Event not found",
                error_details=f"No event found with ID: {event_id}"
            )
        
        existing_event = event_doc.to_dict()
        
        # Check for conflicts if datetime or duration is being updated
        if 'scheduledTime' in parsed_details or 'durationMinutes' in parsed_details:
            new_datetime = parsed_details.get('scheduledTime', existing_event['scheduledTime'])
            new_duration = parsed_details.get('durationMinutes', existing_event['durationMinutes'])
            
            # Create temporary event data for conflict checking
            temp_event = {
                'datetime': new_datetime,
                'duration': new_duration,
                'event_type': existing_event['type']
            }
            
            # Get other events (excluding this one)
            existing_calendar = await tools.get_user_calendar(user_id)
            other_events = [e for e in existing_calendar if e.get('scheduleId') != event_id]
            
            conflicts = tools.conflict_resolver.check_bulk_conflicts(other_events, [temp_event])
            
            if conflicts:
                return SchedulingToolResult.error_result(
                    message="Update would create scheduling conflict",
                    error_details=f"New time conflicts with existing events",
                    next_actions=["suggest_alternative_times", "force_update"]
                )
        
        # Update the event
        parsed_details['updatedAt'] = datetime.now()
        event_ref.update(parsed_details)
        
        # Update Google Calendar if needed
        if any(field in parsed_details for field in ['title', 'description', 'scheduledTime', 'durationMinutes']):
            google_event_id = existing_event.get('googleEventId')
            if google_event_id:
                # In a real implementation, you would update the Google Calendar event
                logger.info(f"Would update Google Calendar event: {google_event_id}")
        
        logger.info(f"Event updated: {event_id} for user {user_id}")
        
        return SchedulingToolResult.success_result(
            data={
                "event_id": event_id,
                "updated_fields": list(parsed_details.keys()),
                "updated_details": parsed_details
            },
            message=f"Successfully updated event",
            next_actions=["view_event", "view_calendar"]
        )
        
    except Exception as e:
        logger.error(f"Failed to update event: {e}")
        return SchedulingToolResult.error_result(
            message="Failed to update event",
            error_details=str(e)
        )


async def delete_event(
    user_id: str,
    event_id: str
) -> SchedulingToolResult:
    """
    Delete a calendar event.
    
    Args:
        user_id: User identifier
        event_id: Event identifier to delete
        
    Returns:
        SchedulingToolResult with deletion status
    """
    try:
        tools = SchedulingTools()
        
        # Get existing event
        event_ref = tools.db.collection("users").document(user_id).collection("schedules").document(event_id)
        event_doc = event_ref.get()
        
        if not event_doc.exists:
            return SchedulingToolResult.error_result(
                message="Event not found",
                error_details=f"No event found with ID: {event_id}"
            )
        
        existing_event = event_doc.to_dict()
        google_event_id = existing_event.get('googleEventId')
        
        # Delete from Firestore
        event_ref.delete()
        
        # Delete from Google Calendar
        if google_event_id:
            # In a real implementation, you would delete the Google Calendar event
            logger.info(f"Would delete Google Calendar event: {google_event_id}")
        
        logger.info(f"Event deleted: {event_id} for user {user_id}")
        
        return SchedulingToolResult.success_result(
            data={
                "deleted_event_id": event_id,
                "deleted_event_title": existing_event.get('title', 'Unknown'),
                "google_event_id": google_event_id
            },
            message=f"Successfully deleted event '{existing_event.get('title', 'Unknown')}'",
            next_actions=["view_calendar", "create_event"]
        )
        
    except Exception as e:
        logger.error(f"Failed to delete event: {e}")
        return SchedulingToolResult.error_result(
            message="Failed to delete event",
            error_details=str(e)
        )


# ============================================================================
# BULK OPERATIONS
# ============================================================================

async def create_multiple_events(
    user_id: str,
    events_list: str
) -> SchedulingToolResult:
    """
    Create multiple events in a single operation.
    
    Args:
        user_id: User identifier
        events_list: JSON string of event dictionaries list (e.g., '[{"title": "Meeting", "datetime": "2024-01-01T10:00:00", "duration": 60, "event_type": "meeting"}]')
        
    Returns:
        SchedulingToolResult with bulk creation results
    """
    try:
        tools = SchedulingTools()
        
        # Parse events_list string to list
        try:
            import json
            parsed_events_list = json.loads(events_list)
        except json.JSONDecodeError as e:
            return SchedulingToolResult.error_result(
                message="Invalid events list format",
                error_details=f"Please provide events_list as JSON: {str(e)}"
            )
        
        # Get existing calendar for conflict checking
        existing_calendar = await tools.get_user_calendar(user_id)
        
        # Check for conflicts
        conflicts = tools.conflict_resolver.check_bulk_conflicts(existing_calendar, parsed_events_list)
        
        if conflicts:
            # Return conflict information with suggestions
            conflict_resolutions = tools.conflict_resolver.resolve_conflicts_intelligently(conflicts)
            
            return SchedulingToolResult.error_result(
                message=f"Found {len(conflicts)} scheduling conflicts",
                error_details={
                    "conflicts": conflicts,
                    "resolutions": conflict_resolutions
                },
                next_actions=["resolve_conflicts", "auto_resolve_conflicts", "force_create_all"]
            )
        
        # No conflicts, create all events
        created_events = []
        failed_events = []
        
        for event_data in parsed_events_list:
            try:
                result = await create_event(
                    user_id=user_id,
                    title=event_data['title'],
                    event_datetime=event_data['datetime'],
                    duration=event_data['duration'],
                    event_type=event_data['event_type'],
                    description=event_data.get('description', '')
                )
                
                if result.success:
                    created_events.append(result.data)
                else:
                    failed_events.append({
                        'event': event_data,
                        'error': result.message
                    })
                    
            except Exception as e:
                failed_events.append({
                    'event': event_data,
                    'error': str(e)
                })
        
        success_count = len(created_events)
        total_count = len(parsed_events_list)
        
        return SchedulingToolResult.success_result(
            data={
                "created_events": created_events,
                "failed_events": failed_events,
                "success_count": success_count,
                "total_count": total_count,
                "success_rate": success_count / total_count if total_count > 0 else 0
            },
            message=f"Successfully created {success_count} out of {total_count} events",
            next_actions=["view_calendar", "retry_failed_events"] if failed_events else ["view_calendar"]
        )
        
    except Exception as e:
        logger.error(f"Failed to create multiple events: {e}")
        return SchedulingToolResult.error_result(
            message="Failed to create multiple events",
            error_details=str(e)
        )


async def create_recurring_events(
    user_id: str,
    event_template: str,
    frequency: str,
    duration_info: str
) -> SchedulingToolResult:
    """
    Create recurring events based on a template and pattern.
    
    Args:
        user_id: User identifier
        event_template: JSON string of base event template (e.g., '{"title": "Daily Standup", "duration": 30, "event_type": "meeting"}')
        frequency: Frequency of recurrence (daily, weekly, etc.)
        duration_info: JSON string of how long to repeat (e.g., '{"count": 10, "unit": "days"}')
        
    Returns:
        SchedulingToolResult with recurring events creation results
    """
    try:
        tools = SchedulingTools()
        
        # Parse JSON parameters
        try:
            import json
            parsed_template = json.loads(event_template)
            parsed_duration = json.loads(duration_info)
        except json.JSONDecodeError as e:
            return SchedulingToolResult.error_result(
                message="Invalid JSON format in parameters",
                error_details=f"Please provide valid JSON: {str(e)}"
            )
        
        # Create recurring pattern
        pattern = {
            'frequency': frequency,
            'duration': parsed_duration
        }
        
        # Generate event instances
        event_instances = tools.recurring_handler.create_recurring_series(
            parsed_template, pattern
        )
        
        if not event_instances:
            return SchedulingToolResult.error_result(
                message="Failed to generate recurring events",
                error_details="No event instances were generated"
            )
        
        # Check for conflicts
        existing_calendar = await tools.get_user_calendar(user_id)
        conflict_analysis = tools.recurring_handler.handle_recurring_conflicts(
            event_instances, existing_calendar
        )
        
        if conflict_analysis['conflicts']:
            return SchedulingToolResult.error_result(
                message=f"Recurring events have {conflict_analysis['conflict_count']} conflicts",
                error_details={
                    "conflict_analysis": conflict_analysis,
                    "suggestions": conflict_analysis['suggestions']
                },
                next_actions=["resolve_recurring_conflicts", "modify_recurring_pattern", "proceed_with_conflicts"]
            )
        
        # Create all event instances
        result = await create_multiple_events(user_id, event_instances)
        
        if result.success:
            return SchedulingToolResult.success_result(
                data={
                    "recurring_series": result.data,
                    "frequency": frequency,
                    "total_instances": len(event_instances),
                    "pattern": pattern
                },
                message=f"Successfully created {frequency} recurring series with {len(event_instances)} instances",
                frequency=frequency,
                next_actions=["view_calendar", "modify_recurring_series"]
            )
        else:
            return result
        
    except Exception as e:
        logger.error(f"Failed to create recurring events: {e}")
        return SchedulingToolResult.error_result(
            message="Failed to create recurring events",
            error_details=str(e)
        )


async def batch_update_events(
    user_id: str,
    events_updates: List[Dict[str, Any]]
) -> SchedulingToolResult:
    """
    Update multiple events in a single operation.
    
    Args:
        user_id: User identifier
        events_updates: List of event update dictionaries with event_id and updated_details
        
    Returns:
        SchedulingToolResult with batch update results
    """
    try:
        updated_events = []
        failed_updates = []
        
        for update_data in events_updates:
            try:
                event_id = update_data['event_id']
                updated_details = update_data['updated_details']
                
                result = await update_event(user_id, event_id, json.dumps(updated_details))
                
                if result.success:
                    updated_events.append(result.data)
                else:
                    failed_updates.append({
                        'event_id': event_id,
                        'error': result.message
                    })
                    
            except Exception as e:
                failed_updates.append({
                    'event_id': update_data.get('event_id', 'unknown'),
                    'error': str(e)
                })
        
        success_count = len(updated_events)
        total_count = len(events_updates)
        
        return SchedulingToolResult.success_result(
            data={
                "updated_events": updated_events,
                "failed_updates": failed_updates,
                "success_count": success_count,
                "total_count": total_count
            },
            message=f"Successfully updated {success_count} out of {total_count} events",
            next_actions=["view_calendar", "retry_failed_updates"] if failed_updates else ["view_calendar"]
        )
        
    except Exception as e:
        logger.error(f"Failed to batch update events: {e}")
        return SchedulingToolResult.error_result(
            message="Failed to batch update events",
            error_details=str(e)
        )


async def batch_delete_events(
    user_id: str,
    event_ids: List[str]
) -> SchedulingToolResult:
    """
    Delete multiple events in a single operation.
    
    Args:
        user_id: User identifier
        event_ids: List of event IDs to delete
        
    Returns:
        SchedulingToolResult with batch deletion results
    """
    try:
        deleted_events = []
        failed_deletions = []
        
        for event_id in event_ids:
            try:
                result = await delete_event(user_id, event_id)
                
                if result.success:
                    deleted_events.append(result.data)
                else:
                    failed_deletions.append({
                        'event_id': event_id,
                        'error': result.message
                    })
                    
            except Exception as e:
                failed_deletions.append({
                    'event_id': event_id,
                    'error': str(e)
                })
        
        success_count = len(deleted_events)
        total_count = len(event_ids)
        
        return SchedulingToolResult.success_result(
            data={
                "deleted_events": deleted_events,
                "failed_deletions": failed_deletions,
                "success_count": success_count,
                "total_count": total_count
            },
            message=f"Successfully deleted {success_count} out of {total_count} events",
            next_actions=["view_calendar", "retry_failed_deletions"] if failed_deletions else ["view_calendar"]
        )
        
    except Exception as e:
        logger.error(f"Failed to batch delete events: {e}")
        return SchedulingToolResult.error_result(
            message="Failed to batch delete events",
            error_details=str(e)
        )


# ============================================================================
# INTELLIGENT CONFLICT RESOLUTION
# ============================================================================

async def create_events_with_conflict_resolution(
    user_id: str,
    events_list: str,
    auto_resolve: bool = True
) -> SchedulingToolResult:
    """
    Create events with intelligent conflict resolution.
    
    Args:
        user_id: User identifier
        events_list: JSON string of events to create (e.g., '[{"title": "Meeting", "datetime": "2024-01-01T10:00:00", "duration": 60}]')
        auto_resolve: Whether to automatically resolve conflicts
        
    Returns:
        SchedulingToolResult with conflict resolution results
    """
    try:
        tools = SchedulingTools()
        
        # Parse events_list string to list
        try:
            import json
            parsed_events_list = json.loads(events_list)
        except json.JSONDecodeError as e:
            return SchedulingToolResult.error_result(
                message="Invalid events list format",
                error_details=f"Please provide events_list as JSON: {str(e)}"
            )
        
        # Get existing calendar
        existing_calendar = await tools.get_user_calendar(user_id)
        
        if auto_resolve:
            # Try automatic conflict resolution
            resolution_result = tools.conflict_resolver.auto_resolve_conflicts(parsed_events_list)
            
            if resolution_result['auto_resolution_success']:
                # All conflicts resolved, create events
                resolved_events = resolution_result['resolved_events']
                result = await create_multiple_events(user_id, json.dumps(resolved_events))
                
                return SchedulingToolResult.success_result(
                    data={
                        "created_events": result.data,
                        "auto_resolved": True,
                        "original_events_count": len(parsed_events_list),
                        "resolved_events_count": len(resolved_events)
                    },
                    message=f"Successfully created {len(resolved_events)} events with automatic conflict resolution",
                    next_actions=["view_calendar"]
                )
            else:
                # Some conflicts couldn't be resolved automatically
                remaining_conflicts = resolution_result['remaining_conflicts']
                resolved_events = resolution_result['resolved_events']
                
                # Create the resolved events
                if resolved_events:
                    await create_multiple_events(user_id, json.dumps(resolved_events))
                
                # Return information about remaining conflicts
                conflict_resolutions = tools.conflict_resolver.resolve_conflicts_intelligently(
                    [{'event': event, 'conflicts': []} for event in remaining_conflicts]
                )
                
                return SchedulingToolResult.error_result(
                    message=f"Auto-resolved {len(resolved_events)} events, {len(remaining_conflicts)} conflicts remain",
                    error_details={
                        "resolved_events": resolved_events,
                        "remaining_conflicts": remaining_conflicts,
                        "conflict_resolutions": conflict_resolutions
                    },
                    next_actions=["resolve_remaining_conflicts", "manual_resolution"]
                )
        else:
            # Manual conflict resolution
            conflicts = tools.conflict_resolver.check_bulk_conflicts(existing_calendar, parsed_events_list)
            
            if conflicts:
                conflict_resolutions = tools.conflict_resolver.resolve_conflicts_intelligently(conflicts)
                
                return SchedulingToolResult.error_result(
                    message=f"Found {len(conflicts)} conflicts requiring manual resolution",
                    error_details={
                        "conflicts": conflicts,
                        "resolutions": conflict_resolutions
                    },
                    next_actions=["choose_resolution", "auto_resolve_conflicts", "force_create_all"]
                )
            else:
                # No conflicts, create all events
                return await create_multiple_events(user_id, json.dumps(parsed_events_list))
        
    except Exception as e:
        logger.error(f"Failed to create events with conflict resolution: {e}")
        return SchedulingToolResult.error_result(
            message="Failed to create events with conflict resolution",
            error_details=str(e)
        )


async def suggest_alternative_times_bulk(
    user_id: str,
    conflicted_events: str
) -> SchedulingToolResult:
    """
    Suggest alternative times for multiple conflicted events.
    
    Args:
        user_id: User identifier
        conflicted_events: JSON string of events that have conflicts (e.g., '[{"title": "Meeting", "datetime": "2024-01-01T10:00:00"}]')
        
    Returns:
        SchedulingToolResult with alternative time suggestions
    """
    try:
        tools = SchedulingTools()
        
        # Parse conflicted_events string to list
        try:
            import json
            parsed_conflicted_events = json.loads(conflicted_events)
        except json.JSONDecodeError as e:
            return SchedulingToolResult.error_result(
                message="Invalid conflicted events format",
                error_details=f"Please provide conflicted_events as JSON: {str(e)}"
            )
        
        # Get existing calendar
        existing_calendar = await tools.get_user_calendar(user_id)
        
        # Find available time slots
        available_slots = []
        
        # Generate potential time slots for the next 7 days
        base_date = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        
        for day_offset in range(7):
            current_day = base_date + timedelta(days=day_offset)
            
            # Check time slots from 8 AM to 10 PM
            for hour in range(8, 22):
                slot_time = current_day.replace(hour=hour)
                
                # Check if this slot is free
                slot_end = slot_time + timedelta(hours=1)  # Assume 1-hour slots
                
                is_free = True
                for existing_event in existing_calendar:
                    existing_start = existing_event.get('datetime') or existing_event.get('scheduledTime')
                    if not existing_start:
                        continue
                    
                    if isinstance(existing_start, str):
                        try:
                            existing_start = datetime.fromisoformat(existing_start.replace('Z', '+00:00'))
                        except:
                            continue
                    
                    existing_duration = existing_event.get('duration', existing_event.get('durationMinutes', 60))
                    existing_end = existing_start + timedelta(minutes=existing_duration)
                    
                    if slot_time < existing_end and existing_start < slot_end:
                        is_free = False
                        break
                
                if is_free:
                    available_slots.append(slot_time)
        
        # Suggest alternatives for each conflicted event
        suggestions = tools.conflict_resolver.suggest_batch_alternatives(
            [{'event': event} for event in parsed_conflicted_events],
            available_slots
        )
        
        return SchedulingToolResult.success_result(
            data={
                "conflicted_events": parsed_conflicted_events,
                "suggestions": suggestions,
                "available_slots": available_slots[:10]  # Limit to first 10 slots
            },
            message=f"Generated alternative time suggestions for {len(parsed_conflicted_events)} events",
            next_actions=["choose_alternative", "create_with_alternatives", "find_more_alternatives"]
        )
        
    except Exception as e:
        logger.error(f"Failed to suggest alternative times: {e}")
        return SchedulingToolResult.error_result(
            message="Failed to suggest alternative times",
            error_details=str(e)
        )


# ============================================================================
# NATURAL LANGUAGE PROCESSING
# ============================================================================

async def parse_and_create_events(
    user_id: str,
    user_input: str
) -> SchedulingToolResult:
    """
    Parse natural language input and create events accordingly.
    
    Args:
        user_id: User identifier
        user_input: Natural language scheduling request
        
    Returns:
        SchedulingToolResult with parsing and creation results
    """
    try:
        tools = SchedulingTools()
        
        # Parse the user input
        parsed_events = tools.event_parser.parse_scheduling_request(user_input)
        
        if not parsed_events:
            return SchedulingToolResult.error_result(
                message="Could not understand the scheduling request",
                error_details="No events could be parsed from the input",
                next_actions=["rephrase_request", "use_structured_input"]
            )
        
        # Create events with conflict resolution
        result = await create_events_with_conflict_resolution(
            user_id, json.dumps(parsed_events), auto_resolve=True
        )
        
        # Add parsing information to the result
        if result.success:
            result.data['parsed_events'] = parsed_events
            result.data['original_input'] = user_input
            result.message = f"Parsed and created {len(parsed_events)} events from your request: '{user_input}'"
        else:
            # Add parsing info to error details
            if isinstance(result.error_details, dict):
                result.error_details['parsed_events'] = parsed_events
                result.error_details['original_input'] = user_input
            else:
                result.error_details = {
                    'original_error': result.error_details,
                    'parsed_events': parsed_events,
                    'original_input': user_input
                }
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to parse and create events: {e}")
        return SchedulingToolResult.error_result(
            message="Failed to parse and create events",
            error_details=str(e)
        ) 