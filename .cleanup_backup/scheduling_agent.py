"""Main Scheduling Agent for Innerverse.

This module contains the main SchedulingAgent class that coordinates all
scheduling functionality including natural language processing, conflict
resolution, and event management.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Ensure the workspace root is in Python path for proper imports
workspace_root = Path(__file__).parent.parent.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from agents.common.tool_results import SchedulingToolResult
from agents.scheduling_agent.tools import (
    parse_and_create_events,
    create_event,
    read_events,
    update_event,
    delete_event,
    create_multiple_events,
    create_recurring_events,
    create_events_with_conflict_resolution,
    suggest_alternative_times_bulk
)
from agents.scheduling_agent.prompts import (
    SCHEDULING_AGENT_SYSTEM_PROMPT,
    CONFLICT_RESOLUTION_PROMPT,
    BULK_SCHEDULING_PROMPT,
    SUCCESS_CONFIRMATION_PROMPT,
    PARSING_CLARIFICATION_PROMPT,
    ALTERNATIVE_SUGGESTIONS_PROMPT,
    ERROR_HANDLING_PROMPT,
    CONVERSATION_STARTERS,
    FOLLOW_UP_QUESTIONS,
    CONFIRMATION_TEMPLATES,
    HELP_MESSAGES
)

logger = logging.getLogger(__name__)


class SchedulingAgent(Agent):
    """Intelligent scheduling agent with natural language processing and conflict resolution."""
    
    def __init__(self):
        super().__init__(
            model="gemini-2.5-flash",
            name="scheduling_agent",
            instruction=SCHEDULING_AGENT_SYSTEM_PROMPT
        )
        # Use a global dictionary to store state since Pydantic doesn't allow custom attributes
        if not hasattr(SchedulingAgent, '_global_state'):
            SchedulingAgent._global_state = {
                'conversation_state': {},
                'pending_confirmations': {}
            }
    
    async def process_message(self, message: str, user_id: str, callback_context: CallbackContext) -> str:
        """
        Process user message and handle scheduling requests.
        
        Args:
            message: User's message
            user_id: User identifier
            callback_context: Conversation context
            
        Returns:
            Response message
        """
        try:
            logger.info(f"Processing scheduling message from user {user_id}: {message}")
            
            # Update conversation state
            conversation_state = SchedulingAgent._global_state['conversation_state']
            if user_id not in conversation_state:
                conversation_state[user_id] = {
                    'last_action': None,
                    'pending_events': [],
                    'context': {}
                }
            
            # Determine the type of request
            request_type = self._classify_request(message)
            
            # Route to appropriate handler
            if request_type == 'natural_language_scheduling':
                return await self._handle_natural_language_scheduling(message, user_id, callback_context)
            elif request_type == 'conflict_resolution':
                return await self._handle_conflict_resolution(message, user_id, callback_context)
            elif request_type == 'calendar_management':
                return await self._handle_calendar_management(message, user_id, callback_context)
            elif request_type == 'help_request':
                return self._handle_help_request(message, user_id)
            else:
                return await self._handle_general_scheduling(message, user_id, callback_context)
                
        except Exception as e:
            logger.error(f"Error processing scheduling message: {e}")
            return self._format_error_response(str(e))
    
    def _classify_request(self, message: str) -> str:
        """Classify the type of scheduling request."""
        message_lower = message.lower()
        
        # Help requests
        if any(word in message_lower for word in ['help', 'how', 'what can', 'explain']):
            return 'help_request'
        
        # Conflict resolution responses
        if any(word in message_lower for word in ['resolve', 'conflict', 'alternative', 'reschedule']):
            return 'conflict_resolution'
        
        # Calendar management
        if any(word in message_lower for word in ['show', 'list', 'view', 'delete', 'remove', 'update', 'change']):
            return 'calendar_management'
        
        # Natural language scheduling
        if any(word in message_lower for word in ['schedule', 'add', 'create', 'book', 'every', 'daily', 'weekly']):
            return 'natural_language_scheduling'
        
        return 'general_scheduling'
    
    async def _handle_natural_language_scheduling(self, message: str, user_id: str, 
                                                callback_context: CallbackContext) -> str:
        """Handle natural language scheduling requests."""
        try:
            # Parse and create events
            result = await parse_and_create_events(user_id, message)
            
            if result.success:
                # Successful scheduling
                return self._format_success_response(result, user_id)
            else:
                # Handle conflicts or errors
                if 'conflicts' in str(result.error_details):
                    return await self._format_conflict_response(result, user_id)
                else:
                    return self._format_parsing_error_response(result, message)
                    
        except Exception as e:
            logger.error(f"Error in natural language scheduling: {e}")
            return self._format_error_response(str(e))
    
    async def _handle_conflict_resolution(self, message: str, user_id: str,
                                        callback_context: CallbackContext) -> str:
        """Handle conflict resolution responses."""
        try:
            # Check if user has pending conflicts
            conversation_state = SchedulingAgent._global_state['conversation_state']
            state = conversation_state.get(user_id, {})
            pending_conflicts = state.get('pending_conflicts', [])
            
            if not pending_conflicts:
                return "I don't see any pending conflicts to resolve. Would you like to schedule something new?"
            
            # Parse user's resolution choice
            choice = self._parse_resolution_choice(message)
            
            if choice == 'accept_recommended':
                # Accept recommended resolution
                return await self._apply_recommended_resolution(user_id, pending_conflicts)
            elif choice == 'choose_alternative':
                # User wants to choose a different alternative
                return await self._show_alternative_options(user_id, pending_conflicts)
            elif choice == 'custom_time':
                # User wants to provide custom time
                return self._request_custom_time(user_id)
            elif choice == 'cancel':
                # Cancel the conflicted events
                return self._cancel_conflicted_events(user_id)
            else:
                return "I didn't understand your choice. Please let me know how you'd like to resolve the conflicts."
                
        except Exception as e:
            logger.error(f"Error in conflict resolution: {e}")
            return self._format_error_response(str(e))
    
    async def _handle_calendar_management(self, message: str, user_id: str,
                                        callback_context: CallbackContext) -> str:
        """Handle calendar management requests (view, update, delete)."""
        try:
            message_lower = message.lower()
            
            if any(word in message_lower for word in ['show', 'list', 'view', 'calendar']):
                # Show calendar events
                return await self._show_calendar_events(user_id, message)
            elif any(word in message_lower for word in ['delete', 'remove', 'cancel']):
                # Delete events
                return await self._handle_delete_request(user_id, message)
            elif any(word in message_lower for word in ['update', 'change', 'modify', 'reschedule']):
                # Update events
                return await self._handle_update_request(user_id, message)
            else:
                return "I can help you view, update, or delete calendar events. What would you like to do?"
                
        except Exception as e:
            logger.error(f"Error in calendar management: {e}")
            return self._format_error_response(str(e))
    
    def _handle_help_request(self, message: str, user_id: str) -> str:
        """Handle help and information requests."""
        message_lower = message.lower()
        
        if 'natural language' in message_lower or 'how to schedule' in message_lower:
            return f"## Natural Language Scheduling\n{HELP_MESSAGES['natural_language']}"
        elif 'conflict' in message_lower or 'resolution' in message_lower:
            return f"## Conflict Resolution\n{HELP_MESSAGES['conflict_resolution']}"
        elif 'recurring' in message_lower or 'repeat' in message_lower:
            return f"## Recurring Events\n{HELP_MESSAGES['recurring_events']}"
        elif 'bulk' in message_lower or 'multiple' in message_lower:
            return f"## Bulk Operations\n{HELP_MESSAGES['bulk_operations']}"
        else:
            return self._get_general_help()
    
    async def _handle_general_scheduling(self, message: str, user_id: str,
                                       callback_context: CallbackContext) -> str:
        """Handle general scheduling conversations."""
        try:
            # Try to parse as a scheduling request
            result = await parse_and_create_events(user_id, message)
            
            if result.success:
                return self._format_success_response(result, user_id)
            else:
                # Couldn't parse - ask for clarification
                return self._request_clarification(message)
                
        except Exception as e:
            logger.error(f"Error in general scheduling: {e}")
            return self._format_error_response(str(e))
    
    async def _show_calendar_events(self, user_id: str, message: str) -> str:
        """Show user's calendar events."""
        try:
            # Parse any date filters from the message
            date_range = self._parse_date_range(message)
            event_type = self._parse_event_type_filter(message)
            
            result = await read_events(user_id, date_range, event_type)
            
            if result.success:
                events = result.data['events']
                if not events:
                    return "Your calendar is empty. Would you like to schedule something?"
                
                # Format events for display
                events_summary = self._format_events_summary(events)
                return f"## Your Calendar Events\n\n{events_summary}\n\nWould you like to modify any of these events?"
            else:
                return f"I couldn't retrieve your calendar events: {result.message}"
                
        except Exception as e:
            logger.error(f"Error showing calendar events: {e}")
            return "I had trouble accessing your calendar. Please try again."
    
    def _format_success_response(self, result: SchedulingToolResult, user_id: str) -> str:
        """Format successful scheduling response."""
        try:
            data = result.data
            
            if 'created_events' in data:
                events = data['created_events']
                events_count = len(events) if isinstance(events, list) else data.get('success_count', 1)
                
                # Create summary
                summary = self._create_events_summary(events if isinstance(events, list) else [events])
                
                return SUCCESS_CONFIRMATION_PROMPT.format(
                    scheduled_events_summary=summary,
                    events_created=events_count,
                    google_calendar_status="✅ Synced",
                    next_event=self._get_next_event_info(events if isinstance(events, list) else [events])
                )
            else:
                return f"✅ {result.message}\n\nWhat else would you like to schedule?"
                
        except Exception as e:
            logger.error(f"Error formatting success response: {e}")
            return f"✅ {result.message}\n\nScheduling completed successfully!"
    
    async def _format_conflict_response(self, result: SchedulingToolResult, user_id: str) -> str:
        """Format conflict resolution response."""
        try:
            error_details = result.error_details
            
            if isinstance(error_details, dict) and 'conflicts' in error_details:
                conflicts = error_details['conflicts']
                resolutions = error_details.get('resolutions', [])
                
                # Store conflicts in conversation state
                conversation_state = SchedulingAgent._global_state['conversation_state']
                if user_id not in conversation_state:
                    conversation_state[user_id] = {}
                conversation_state[user_id]['pending_conflicts'] = conflicts
                
                # Format conflict information
                conflict_summary = self._format_conflicts_summary(conflicts)
                resolution_options = self._format_resolution_options(resolutions)
                
                return CONFLICT_RESOLUTION_PROMPT.format(
                    event_title=conflicts[0]['event']['title'] if conflicts else "Multiple events",
                    requested_time=self._format_datetime(conflicts[0]['event']['datetime']) if conflicts else "Various times",
                    duration=conflicts[0]['event']['duration'] if conflicts else "Various",
                    conflicting_events=conflict_summary,
                    resolution_options=resolution_options,
                    recommended_option=resolutions[0]['recommended_option']['description'] if resolutions and resolutions[0].get('recommended_option') else "Reschedule to next available time"
                )
            else:
                return f"❌ {result.message}\n\nWould you like to try scheduling at a different time?"
                
        except Exception as e:
            logger.error(f"Error formatting conflict response: {e}")
            return f"❌ {result.message}\n\nI can help you resolve this conflict. What would you prefer to do?"
    
    def _format_parsing_error_response(self, result: SchedulingToolResult, original_message: str) -> str:
        """Format parsing error response with suggestions."""
        try:
            suggestions = [
                "Try being more specific about dates and times",
                "Use formats like 'tomorrow at 2PM' or 'next Tuesday at 6PM'",
                "Break complex requests into simpler parts",
                "Specify duration if it's not a standard event type"
            ]
            
            return PARSING_CLARIFICATION_PROMPT.format(
                parsed_interpretation="I had trouble understanding your request",
                clarification_questions="Could you please rephrase with more specific details?",
                assumptions=f"Original message: '{original_message}'"
            ) + f"\n\n**Suggestions:**\n" + "\n".join(f"• {s}" for s in suggestions)
            
        except Exception as e:
            logger.error(f"Error formatting parsing error: {e}")
            return f"I had trouble understanding your scheduling request. Could you please be more specific about the date, time, and event details?"
    
    def _format_error_response(self, error: str) -> str:
        """Format general error response."""
        return ERROR_HANDLING_PROMPT.format(
            error_description=error,
            error_suggestions=[
                "Try rephrasing your request",
                "Check if you have the necessary permissions",
                "Make sure your request includes date and time information"
            ]
        )
    
    def _parse_resolution_choice(self, message: str) -> str:
        """Parse user's conflict resolution choice."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['accept', 'yes', '1', 'recommended', 'first']):
            return 'accept_recommended'
        elif any(word in message_lower for word in ['alternative', '2', 'different', 'other']):
            return 'choose_alternative'
        elif any(word in message_lower for word in ['custom', '3', 'my own', 'specific']):
            return 'custom_time'
        elif any(word in message_lower for word in ['cancel', '4', 'skip', 'never mind']):
            return 'cancel'
        else:
            return 'unclear'
    
    def _create_events_summary(self, events: List[Dict]) -> str:
        """Create a summary of scheduled events."""
        if not events:
            return "No events scheduled"
        
        summary_lines = []
        for event in events[:5]:  # Limit to first 5 events
            if isinstance(event, dict):
                event_data = event.get('event_details', event)
                title = event_data.get('title', 'Untitled Event')
                scheduled_time = event_data.get('scheduledTime', event_data.get('datetime'))
                
                if scheduled_time:
                    if isinstance(scheduled_time, str):
                        try:
                            scheduled_time = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                        except:
                            pass
                    
                    if isinstance(scheduled_time, datetime):
                        time_str = scheduled_time.strftime('%A, %B %d at %I:%M %p')
                        summary_lines.append(f"• **{title}** - {time_str}")
                    else:
                        summary_lines.append(f"• **{title}**")
                else:
                    summary_lines.append(f"• **{title}**")
        
        if len(events) > 5:
            summary_lines.append(f"• ... and {len(events) - 5} more events")
        
        return "\n".join(summary_lines)
    
    def _get_next_event_info(self, events: List[Dict]) -> str:
        """Get information about the next upcoming event."""
        if not events:
            return "No upcoming events"
        
        try:
            # Find the earliest event
            earliest_event = None
            earliest_time = None
            
            for event in events:
                if isinstance(event, dict):
                    event_data = event.get('event_details', event)
                    scheduled_time = event_data.get('scheduledTime', event_data.get('datetime'))
                    
                    if scheduled_time:
                        if isinstance(scheduled_time, str):
                            try:
                                scheduled_time = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                            except:
                                continue
                        
                        if isinstance(scheduled_time, datetime):
                            if earliest_time is None or scheduled_time < earliest_time:
                                earliest_time = scheduled_time
                                earliest_event = event_data
            
            if earliest_event and earliest_time:
                title = earliest_event.get('title', 'Untitled Event')
                time_str = earliest_time.strftime('%A, %B %d at %I:%M %p')
                return f"{title} on {time_str}"
            else:
                return "No upcoming events"
                
        except Exception as e:
            logger.error(f"Error getting next event info: {e}")
            return "Unable to determine next event"
    
    def _format_conflicts_summary(self, conflicts: List[Dict]) -> str:
        """Format conflicts summary for display."""
        if not conflicts:
            return "No conflicts"
        
        summary_lines = []
        for conflict in conflicts[:3]:  # Limit to first 3 conflicts
            event = conflict.get('event', {})
            conflict_details = conflict.get('conflicts', [])
            
            title = event.get('title', 'Untitled Event')
            datetime_str = self._format_datetime(event.get('datetime'))
            
            conflicting_with = []
            for conf in conflict_details[:2]:  # Limit to 2 conflicting events per conflict
                conf_event = conf.get('conflicting_event', {})
                conf_title = conf_event.get('title', 'Existing Event')
                conflicting_with.append(conf_title)
            
            conflicts_str = ", ".join(conflicting_with)
            summary_lines.append(f"• **{title}** ({datetime_str}) conflicts with: {conflicts_str}")
        
        return "\n".join(summary_lines)
    
    def _format_resolution_options(self, resolutions: List[Dict]) -> str:
        """Format resolution options for display."""
        if not resolutions:
            return "No resolution options available"
        
        options_lines = []
        for i, resolution in enumerate(resolutions[:3], 1):  # Limit to 3 resolutions
            recommended_option = resolution.get('recommended_option')
            if recommended_option:
                description = recommended_option.get('description', 'Alternative option')
                options_lines.append(f"{i}. {description}")
        
        return "\n".join(options_lines) if options_lines else "Reschedule to next available time"
    
    def _format_datetime(self, dt) -> str:
        """Format datetime for display."""
        if dt is None:
            return "Unknown time"
        
        try:
            if isinstance(dt, str):
                dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
            
            if isinstance(dt, datetime):
                return dt.strftime('%A, %B %d at %I:%M %p')
            else:
                return str(dt)
        except:
            return str(dt)
    
    def _format_events_summary(self, events: List[Dict]) -> str:
        """Format events summary for calendar display."""
        if not events:
            return "No events found"
        
        summary_lines = []
        for event in events:
            title = event.get('title', 'Untitled Event')
            scheduled_time = event.get('scheduledTime', event.get('datetime'))
            duration = event.get('durationMinutes', event.get('duration', 60))
            event_type = event.get('type', event.get('event_type', 'personal'))
            
            time_str = self._format_datetime(scheduled_time)
            summary_lines.append(f"• **{title}** ({event_type}) - {time_str} ({duration} min)")
        
        return "\n".join(summary_lines)
    
    def _get_general_help(self) -> str:
        """Get general help message."""
        return f"""# Scheduling Assistant Help

I can help you with all your scheduling needs:

{HELP_MESSAGES['natural_language']}

{HELP_MESSAGES['conflict_resolution']}

{HELP_MESSAGES['recurring_events']}

{HELP_MESSAGES['bulk_operations']}

## Quick Examples:
• "Schedule therapy every Tuesday at 6PM for 4 weeks"
• "Add workout Monday, Wednesday, Friday at 7AM"
• "I need: dentist tomorrow 2PM, groceries Saturday 10AM"
• "Show my calendar for this week"
• "Delete my Thursday meeting"

What would you like to schedule today?"""
    
    def _request_clarification(self, original_message: str) -> str:
        """Request clarification for unclear messages."""
        return f"""I want to help you schedule something, but I need a bit more information.

**Your message:** "{original_message}"

**To help me understand better, please include:**
• What you want to schedule
• When (date and time)
• How long it should be

**Examples of clear requests:**
• "Schedule dentist appointment tomorrow at 2PM"
• "Add weekly therapy sessions on Tuesdays at 6PM"
• "I need to schedule a 30-minute workout every morning at 7AM"

What would you like to schedule?"""
    
    def _parse_date_range(self, message: str) -> Optional[Dict]:
        """Parse date range from message."""
        # This is a simplified implementation
        # In a real implementation, you'd use more sophisticated date parsing
        message_lower = message.lower()
        
        if 'today' in message_lower:
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            return {'start_date': today, 'end_date': today.replace(hour=23, minute=59)}
        elif 'this week' in message_lower:
            today = datetime.now()
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            return {'start_date': start_of_week, 'end_date': end_of_week}
        
        return None
    
    def _parse_event_type_filter(self, message: str) -> Optional[str]:
        """Parse event type filter from message."""
        message_lower = message.lower()
        
        event_types = ['therapy', 'exercise', 'journaling', 'work', 'personal', 'meal', 'social']
        
        for event_type in event_types:
            if event_type in message_lower:
                return event_type
        
        return None
    
    async def _handle_delete_request(self, user_id: str, message: str) -> str:
        """Handle delete event requests."""
        # This would need more sophisticated parsing to identify which events to delete
        return "To delete events, please be specific about which events you want to remove. You can say things like:\n• 'Delete my Thursday meeting'\n• 'Cancel tomorrow's dentist appointment'\n• 'Remove all my workout sessions this week'"
    
    async def _handle_update_request(self, user_id: str, message: str) -> str:
        """Handle update event requests."""
        # This would need more sophisticated parsing to identify which events to update and how
        return "To update events, please specify which event and what changes you want. For example:\n• 'Move my Tuesday therapy to Wednesday at 7PM'\n• 'Change my workout from 7AM to 8AM'\n• 'Extend my meeting to 2 hours'" 