"""Recurring Events Handler for Scheduling Agent.

This module handles the creation and management of recurring events,
including pattern recognition and instance generation.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)


class RecurringEventsHandler:
    """Handles creation and management of recurring events."""
    
    def __init__(self):
        self.frequency_mappings = {
            'daily': {'days': 1, 'weeks': 0, 'months': 0},
            'weekly': {'days': 0, 'weeks': 1, 'months': 0},
            'biweekly': {'days': 0, 'weeks': 2, 'months': 0},
            'monthly': {'days': 0, 'weeks': 0, 'months': 1}
        }
        
        self.default_durations = {
            'daily': {'count': 30, 'unit': 'days'},
            'weekly': {'count': 8, 'unit': 'weeks'},
            'biweekly': {'count': 12, 'unit': 'weeks'},
            'monthly': {'count': 6, 'unit': 'months'}
        }
    
    def create_recurring_series(self, event_template: Dict, pattern: Dict, end_date: datetime = None) -> List[Dict]:
        """
        Create a series of recurring events based on a template and pattern.
        
        Args:
            event_template: Base event template with title, duration, etc.
            pattern: Recurring pattern with frequency, days, duration info
            end_date: Optional end date for the series
            
        Returns:
            List of individual event instances
        """
        try:
            frequency = pattern.get('frequency', 'weekly')
            duration_info = pattern.get('duration', self.default_durations.get(frequency))
            specific_days = pattern.get('days', [])
            
            # Calculate series end date if not provided
            if not end_date:
                end_date = self._calculate_end_date(event_template['datetime'], duration_info)
            
            # Generate event instances
            if frequency == 'daily':
                return self._generate_daily_events(event_template, end_date)
            elif frequency == 'weekly':
                if specific_days:
                    return self._generate_weekly_events_specific_days(
                        event_template, specific_days, end_date
                    )
                else:
                    return self._generate_weekly_events(event_template, end_date)
            elif frequency == 'biweekly':
                return self._generate_biweekly_events(event_template, end_date)
            elif frequency == 'monthly':
                return self._generate_monthly_events(event_template, end_date)
            else:
                logger.warning(f"Unknown frequency: {frequency}")
                return [event_template]
                
        except Exception as e:
            logger.error(f"Error creating recurring series: {e}")
            return []
    
    def _calculate_end_date(self, start_date: datetime, duration_info: Dict) -> datetime:
        """Calculate the end date for a recurring series."""
        try:
            count = duration_info.get('count', 4)
            unit = duration_info.get('unit', 'weeks')
            
            if unit == 'days':
                return start_date + timedelta(days=count)
            elif unit == 'weeks':
                return start_date + timedelta(weeks=count)
            elif unit == 'months':
                return start_date + relativedelta(months=count)
            else:
                # Default to 4 weeks
                return start_date + timedelta(weeks=4)
                
        except Exception as e:
            logger.error(f"Error calculating end date: {e}")
            return start_date + timedelta(weeks=4)
    
    def _generate_daily_events(self, template: Dict, end_date: datetime) -> List[Dict]:
        """Generate daily recurring events."""
        events = []
        
        try:
            current_date = template['datetime']
            
            while current_date <= end_date:
                event = template.copy()
                event['datetime'] = current_date
                event['frequency'] = 'daily'
                event['description'] = f"Daily {template['title']}"
                events.append(event)
                
                current_date += timedelta(days=1)
                
        except Exception as e:
            logger.error(f"Error generating daily events: {e}")
        
        return events
    
    def _generate_weekly_events(self, template: Dict, end_date: datetime) -> List[Dict]:
        """Generate weekly recurring events (same day each week)."""
        events = []
        
        try:
            current_date = template['datetime']
            
            while current_date <= end_date:
                event = template.copy()
                event['datetime'] = current_date
                event['frequency'] = 'weekly'
                event['description'] = f"Weekly {template['title']}"
                events.append(event)
                
                current_date += timedelta(weeks=1)
                
        except Exception as e:
            logger.error(f"Error generating weekly events: {e}")
        
        return events
    
    def _generate_weekly_events_specific_days(self, template: Dict, days: List[int], 
                                            end_date: datetime) -> List[Dict]:
        """Generate weekly events for specific days (e.g., Mon/Wed/Fri)."""
        events = []
        
        try:
            start_date = template['datetime']
            current_week_start = start_date - timedelta(days=start_date.weekday())
            
            while current_week_start <= end_date:
                for day_num in days:
                    event_date = current_week_start + timedelta(days=day_num)
                    
                    # Only include events from start date onwards
                    if event_date >= start_date and event_date <= end_date:
                        event = template.copy()
                        # Keep the same time but change the date
                        event['datetime'] = event_date.replace(
                            hour=start_date.hour,
                            minute=start_date.minute,
                            second=start_date.second
                        )
                        event['frequency'] = 'weekly'
                        event['description'] = f"Weekly {template['title']} ({self._get_day_name(day_num)})"
                        events.append(event)
                
                current_week_start += timedelta(weeks=1)
                
        except Exception as e:
            logger.error(f"Error generating weekly events for specific days: {e}")
        
        return events
    
    def _generate_biweekly_events(self, template: Dict, end_date: datetime) -> List[Dict]:
        """Generate biweekly (every other week) recurring events."""
        events = []
        
        try:
            current_date = template['datetime']
            
            while current_date <= end_date:
                event = template.copy()
                event['datetime'] = current_date
                event['frequency'] = 'biweekly'
                event['description'] = f"Biweekly {template['title']}"
                events.append(event)
                
                current_date += timedelta(weeks=2)
                
        except Exception as e:
            logger.error(f"Error generating biweekly events: {e}")
        
        return events
    
    def _generate_monthly_events(self, template: Dict, end_date: datetime) -> List[Dict]:
        """Generate monthly recurring events."""
        events = []
        
        try:
            current_date = template['datetime']
            
            while current_date <= end_date:
                event = template.copy()
                event['datetime'] = current_date
                event['frequency'] = 'monthly'
                event['description'] = f"Monthly {template['title']}"
                events.append(event)
                
                # Add one month
                current_date = current_date + relativedelta(months=1)
                
        except Exception as e:
            logger.error(f"Error generating monthly events: {e}")
        
        return events
    
    def _get_day_name(self, day_num: int) -> str:
        """Convert day number to day name."""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[day_num] if 0 <= day_num < 7 else 'Unknown'
    
    def generate_event_instances(self, template: Dict, frequency: str, count: int) -> List[Dict]:
        """
        Generate a specific number of event instances.
        
        Args:
            template: Base event template
            frequency: Frequency of recurrence
            count: Number of instances to generate
            
        Returns:
            List of event instances
        """
        events = []
        
        try:
            current_date = template['datetime']
            frequency_delta = self.frequency_mappings.get(frequency, {'days': 7, 'weeks': 0, 'months': 0})
            
            for i in range(count):
                event = template.copy()
                event['datetime'] = current_date
                event['frequency'] = frequency
                event['description'] = f"{frequency.title()} {template['title']} (#{i+1})"
                events.append(event)
                
                # Calculate next occurrence
                current_date = self._add_frequency_delta(current_date, frequency_delta)
                
        except Exception as e:
            logger.error(f"Error generating event instances: {e}")
        
        return events
    
    def _add_frequency_delta(self, date: datetime, delta: Dict) -> datetime:
        """Add frequency delta to a date."""
        try:
            new_date = date
            
            if delta['days']:
                new_date += timedelta(days=delta['days'])
            if delta['weeks']:
                new_date += timedelta(weeks=delta['weeks'])
            if delta['months']:
                new_date += relativedelta(months=delta['months'])
            
            return new_date
            
        except Exception as e:
            logger.error(f"Error adding frequency delta: {e}")
            return date + timedelta(days=1)  # Fallback
    
    def handle_recurring_conflicts(self, recurring_events: List[Dict], existing_calendar: List[Dict]) -> Dict:
        """
        Handle conflicts for an entire recurring series.
        
        Args:
            recurring_events: List of recurring event instances
            existing_calendar: Existing calendar events
            
        Returns:
            Dictionary with conflict analysis and suggestions
        """
        try:
            conflicts = []
            conflict_free_events = []
            
            for event in recurring_events:
                event_start = event['datetime']
                event_end = event_start + timedelta(minutes=event['duration'])
                
                # Check for conflicts with existing calendar
                has_conflict = False
                conflicting_events = []
                
                for existing_event in existing_calendar:
                    existing_start = existing_event.get('datetime') or existing_event.get('scheduledTime')
                    if not existing_start:
                        continue
                    
                    # Handle different datetime formats
                    if isinstance(existing_start, str):
                        try:
                            existing_start = datetime.fromisoformat(existing_start.replace('Z', '+00:00'))
                        except:
                            continue
                    
                    existing_duration = existing_event.get('duration', existing_event.get('durationMinutes', 60))
                    existing_end = existing_start + timedelta(minutes=existing_duration)
                    
                    # Check for overlap
                    if self._events_overlap(event_start, event_end, existing_start, existing_end):
                        has_conflict = True
                        conflicting_events.append(existing_event)
                
                if has_conflict:
                    conflicts.append({
                        'event': event,
                        'conflicting_with': conflicting_events
                    })
                else:
                    conflict_free_events.append(event)
            
            # Generate suggestions for conflicts
            suggestions = self._generate_recurring_conflict_suggestions(conflicts)
            
            return {
                'total_events': len(recurring_events),
                'conflict_free_events': conflict_free_events,
                'conflicts': conflicts,
                'conflict_count': len(conflicts),
                'suggestions': suggestions,
                'success_rate': len(conflict_free_events) / len(recurring_events) if recurring_events else 0
            }
            
        except Exception as e:
            logger.error(f"Error handling recurring conflicts: {e}")
            return {
                'total_events': len(recurring_events),
                'conflict_free_events': [],
                'conflicts': recurring_events,
                'conflict_count': len(recurring_events),
                'suggestions': [],
                'success_rate': 0,
                'error': str(e)
            }
    
    def _events_overlap(self, start1: datetime, end1: datetime, start2: datetime, end2: datetime) -> bool:
        """Check if two time ranges overlap."""
        return start1 < end2 and start2 < end1
    
    def _generate_recurring_conflict_suggestions(self, conflicts: List[Dict]) -> List[Dict]:
        """Generate suggestions for resolving recurring event conflicts."""
        suggestions = []
        
        try:
            if not conflicts:
                return suggestions
            
            # Analyze conflict patterns
            conflict_count = len(conflicts)
            total_events = conflict_count  # Assuming we only have conflicts in this list
            
            if conflict_count == 1:
                # Single conflict - suggest rescheduling that instance
                conflict = conflicts[0]
                event = conflict['event']
                
                suggestions.append({
                    'type': 'reschedule_single',
                    'description': f"Reschedule the {event['datetime'].strftime('%A, %B %d')} session",
                    'action': 'reschedule_instance',
                    'affected_events': [event]
                })
                
            elif conflict_count <= total_events * 0.3:
                # Less than 30% conflicts - suggest rescheduling individual instances
                suggestions.append({
                    'type': 'reschedule_individual',
                    'description': f"Reschedule {conflict_count} conflicting sessions individually",
                    'action': 'reschedule_instances',
                    'affected_events': [c['event'] for c in conflicts]
                })
                
            else:
                # High conflict rate - suggest changing the entire series
                first_event = conflicts[0]['event']
                
                suggestions.extend([
                    {
                        'type': 'change_time',
                        'description': f"Change the recurring time (currently {first_event['datetime'].strftime('%I:%M %p')})",
                        'action': 'change_series_time',
                        'affected_events': 'all'
                    },
                    {
                        'type': 'change_day',
                        'description': f"Change the recurring day (currently {first_event['datetime'].strftime('%A')})",
                        'action': 'change_series_day', 
                        'affected_events': 'all'
                    },
                    {
                        'type': 'reduce_frequency',
                        'description': f"Reduce frequency to avoid conflicts",
                        'action': 'reduce_frequency',
                        'affected_events': 'all'
                    }
                ])
            
            # Add option to proceed with conflicts
            suggestions.append({
                'type': 'proceed_with_conflicts',
                'description': f"Proceed anyway and resolve {conflict_count} conflicts manually",
                'action': 'manual_resolution',
                'affected_events': [c['event'] for c in conflicts]
            })
            
        except Exception as e:
            logger.error(f"Error generating recurring conflict suggestions: {e}")
        
        return suggestions
    
    def modify_recurring_series(self, original_events: List[Dict], modification: Dict) -> List[Dict]:
        """
        Modify an existing recurring series.
        
        Args:
            original_events: Original recurring event instances
            modification: Modification details (new_time, new_day, etc.)
            
        Returns:
            Modified event instances
        """
        try:
            modification_type = modification.get('type')
            
            if modification_type == 'change_time':
                return self._change_series_time(original_events, modification.get('new_time'))
            elif modification_type == 'change_day':
                return self._change_series_day(original_events, modification.get('new_day'))
            elif modification_type == 'reduce_frequency':
                return self._reduce_series_frequency(original_events, modification.get('new_frequency'))
            else:
                logger.warning(f"Unknown modification type: {modification_type}")
                return original_events
                
        except Exception as e:
            logger.error(f"Error modifying recurring series: {e}")
            return original_events
    
    def _change_series_time(self, events: List[Dict], new_time: str) -> List[Dict]:
        """Change the time for all events in a series."""
        try:
            # Parse new time (e.g., "2:00 PM")
            from dateutil.parser import parse
            time_obj = parse(new_time).time()
            
            modified_events = []
            for event in events:
                modified_event = event.copy()
                original_datetime = event['datetime']
                new_datetime = original_datetime.replace(
                    hour=time_obj.hour,
                    minute=time_obj.minute,
                    second=0,
                    microsecond=0
                )
                modified_event['datetime'] = new_datetime
                modified_events.append(modified_event)
            
            return modified_events
            
        except Exception as e:
            logger.error(f"Error changing series time: {e}")
            return events
    
    def _change_series_day(self, events: List[Dict], new_day: int) -> List[Dict]:
        """Change the day of week for all events in a series."""
        try:
            modified_events = []
            
            for event in events:
                modified_event = event.copy()
                original_datetime = event['datetime']
                
                # Calculate the new date with the new day of week
                days_diff = new_day - original_datetime.weekday()
                new_datetime = original_datetime + timedelta(days=days_diff)
                
                modified_event['datetime'] = new_datetime
                modified_events.append(modified_event)
            
            return modified_events
            
        except Exception as e:
            logger.error(f"Error changing series day: {e}")
            return events
    
    def _reduce_series_frequency(self, events: List[Dict], new_frequency: str) -> List[Dict]:
        """Reduce the frequency of a recurring series."""
        try:
            if new_frequency == 'biweekly' and len(events) > 1:
                # Keep every other event
                return events[::2]
            elif new_frequency == 'monthly' and len(events) > 3:
                # Keep every 4th event (approximately monthly)
                return events[::4]
            else:
                # Return first half of events
                return events[:len(events)//2]
                
        except Exception as e:
            logger.error(f"Error reducing series frequency: {e}")
            return events 