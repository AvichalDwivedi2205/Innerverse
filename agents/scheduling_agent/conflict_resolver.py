"""Conflict Resolver for Intelligent Scheduling.

This module handles conflict detection and resolution for scheduling events,
including bulk conflict resolution and intelligent alternative suggestions.
"""

import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ConflictResolver:
    """Handles conflict detection and resolution for scheduling events."""
    
    def __init__(self):
        self.event_priorities = {
            'therapy': 9,
            'work': 8,
            'personal': 7,
            'exercise': 6,
            'journaling': 5,
            'meal': 4,
            'social': 3
        }
    
    def check_bulk_conflicts(self, user_calendar: List[Dict], proposed_events: List[Dict]) -> List[Dict]:
        """
        Check for conflicts across multiple proposed events.
        
        Args:
            user_calendar: List of existing calendar events
            proposed_events: List of events to be scheduled
            
        Returns:
            List of conflict dictionaries with details
        """
        conflicts = []
        
        try:
            for i, proposed_event in enumerate(proposed_events):
                # Check against existing calendar
                existing_conflicts = self._check_against_existing_calendar(
                    proposed_event, user_calendar
                )
                
                # Check against other proposed events
                other_proposed = proposed_events[:i] + proposed_events[i+1:]
                proposed_conflicts = self._check_against_proposed_events(
                    proposed_event, other_proposed
                )
                
                # Combine conflicts
                all_conflicts = existing_conflicts + proposed_conflicts
                
                if all_conflicts:
                    conflicts.append({
                        'event': proposed_event,
                        'event_index': i,
                        'conflicts': all_conflicts,
                        'severity': self._calculate_conflict_severity(all_conflicts)
                    })
                    
        except Exception as e:
            logger.error(f"Error checking bulk conflicts: {e}")
        
        return conflicts
    
    def _check_against_existing_calendar(self, proposed_event: Dict, calendar: List[Dict]) -> List[Dict]:
        """Check proposed event against existing calendar events."""
        conflicts = []
        
        try:
            proposed_start = proposed_event['datetime']
            proposed_end = proposed_start + timedelta(minutes=proposed_event['duration'])
            
            for existing_event in calendar:
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
                if self._events_overlap(proposed_start, proposed_end, existing_start, existing_end):
                    conflicts.append({
                        'type': 'existing_event',
                        'conflicting_event': existing_event,
                        'overlap_start': max(proposed_start, existing_start),
                        'overlap_end': min(proposed_end, existing_end)
                    })
                    
        except Exception as e:
            logger.error(f"Error checking against existing calendar: {e}")
        
        return conflicts
    
    def _check_against_proposed_events(self, proposed_event: Dict, other_events: List[Dict]) -> List[Dict]:
        """Check proposed event against other proposed events."""
        conflicts = []
        
        try:
            proposed_start = proposed_event['datetime']
            proposed_end = proposed_start + timedelta(minutes=proposed_event['duration'])
            
            for other_event in other_events:
                other_start = other_event['datetime']
                other_end = other_start + timedelta(minutes=other_event['duration'])
                
                # Check for overlap
                if self._events_overlap(proposed_start, proposed_end, other_start, other_end):
                    conflicts.append({
                        'type': 'proposed_event',
                        'conflicting_event': other_event,
                        'overlap_start': max(proposed_start, other_start),
                        'overlap_end': min(proposed_end, other_end)
                    })
                    
        except Exception as e:
            logger.error(f"Error checking against proposed events: {e}")
        
        return conflicts
    
    def _events_overlap(self, start1: datetime, end1: datetime, start2: datetime, end2: datetime) -> bool:
        """Check if two time ranges overlap."""
        return start1 < end2 and start2 < end1
    
    def _calculate_conflict_severity(self, conflicts: List[Dict]) -> str:
        """Calculate the severity of conflicts."""
        if not conflicts:
            return 'none'
        
        # High severity if conflicts with high-priority events
        for conflict in conflicts:
            conflicting_event = conflict['conflicting_event']
            event_type = conflicting_event.get('event_type', conflicting_event.get('type', 'personal'))
            
            if self.event_priorities.get(event_type, 5) >= 8:
                return 'high'
        
        return 'medium' if len(conflicts) > 1 else 'low'
    
    def resolve_conflicts_intelligently(self, conflicts: List[Dict], user_preferences: Dict = None) -> List[Dict]:
        """
        Automatically resolve conflicts based on priorities and preferences.
        
        Args:
            conflicts: List of conflict dictionaries
            user_preferences: User preferences for conflict resolution
            
        Returns:
            List of resolution suggestions
        """
        resolutions = []
        
        try:
            for conflict in conflicts:
                event = conflict['event']
                conflict_details = conflict['conflicts']
                
                # Generate resolution options
                resolution_options = self._generate_resolution_options(
                    event, conflict_details, user_preferences
                )
                
                resolutions.append({
                    'original_event': event,
                    'conflicts': conflict_details,
                    'resolution_options': resolution_options,
                    'recommended_option': resolution_options[0] if resolution_options else None
                })
                
        except Exception as e:
            logger.error(f"Error resolving conflicts: {e}")
        
        return resolutions
    
    def _generate_resolution_options(self, event: Dict, conflicts: List[Dict], 
                                   user_preferences: Dict = None) -> List[Dict]:
        """Generate resolution options for a conflicted event."""
        options = []
        
        try:
            event_start = event['datetime']
            event_duration = event['duration']
            event_type = event['event_type']
            
            # Option 1: Find alternative times on the same day
            same_day_alternatives = self._find_alternative_times_same_day(
                event_start, event_duration, conflicts
            )
            
            for alt_time in same_day_alternatives:
                options.append({
                    'type': 'reschedule_same_day',
                    'new_datetime': alt_time,
                    'description': f"Move to {alt_time.strftime('%I:%M %p')} on the same day",
                    'priority': 8
                })
            
            # Option 2: Move to next available day
            next_day_alternative = self._find_next_available_day(
                event_start, event_duration, event_type
            )
            
            if next_day_alternative:
                options.append({
                    'type': 'reschedule_next_day',
                    'new_datetime': next_day_alternative,
                    'description': f"Move to {next_day_alternative.strftime('%A %I:%M %p')}",
                    'priority': 6
                })
            
            # Option 3: Adjust duration if possible
            if event_duration > 30:
                shorter_duration = max(30, event_duration - 30)
                options.append({
                    'type': 'reduce_duration',
                    'new_duration': shorter_duration,
                    'description': f"Reduce duration to {shorter_duration} minutes",
                    'priority': 4
                })
            
            # Option 4: Keep conflict (user decides)
            options.append({
                'type': 'keep_conflict',
                'description': "Keep the conflict and let user decide later",
                'priority': 2
            })
            
            # Sort by priority (higher priority first)
            options.sort(key=lambda x: x['priority'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error generating resolution options: {e}")
        
        return options
    
    def _find_alternative_times_same_day(self, original_time: datetime, duration: int, 
                                       conflicts: List[Dict]) -> List[datetime]:
        """Find alternative times on the same day."""
        alternatives = []
        
        try:
            same_day = original_time.replace(hour=8, minute=0, second=0, microsecond=0)
            end_of_day = original_time.replace(hour=22, minute=0, second=0, microsecond=0)
            
            # Check every 30-minute slot
            current_time = same_day
            while current_time + timedelta(minutes=duration) <= end_of_day:
                slot_end = current_time + timedelta(minutes=duration)
                
                # Check if this slot conflicts
                has_conflict = False
                for conflict in conflicts:
                    conflicting_event = conflict['conflicting_event']
                    conf_start = conflicting_event.get('datetime') or conflicting_event.get('scheduledTime')
                    
                    if isinstance(conf_start, str):
                        try:
                            conf_start = datetime.fromisoformat(conf_start.replace('Z', '+00:00'))
                        except:
                            continue
                    
                    conf_duration = conflicting_event.get('duration', conflicting_event.get('durationMinutes', 60))
                    conf_end = conf_start + timedelta(minutes=conf_duration)
                    
                    if self._events_overlap(current_time, slot_end, conf_start, conf_end):
                        has_conflict = True
                        break
                
                if not has_conflict:
                    alternatives.append(current_time)
                    if len(alternatives) >= 3:  # Limit to 3 alternatives
                        break
                
                current_time += timedelta(minutes=30)
                
        except Exception as e:
            logger.error(f"Error finding alternative times: {e}")
        
        return alternatives
    
    def _find_next_available_day(self, original_time: datetime, duration: int, event_type: str) -> Optional[datetime]:
        """Find the next available day for the event."""
        try:
            # Preferred times based on event type
            preferred_hours = {
                'therapy': [18, 19, 20],  # 6-8 PM
                'exercise': [7, 8, 17, 18],  # 7-8 AM or 5-6 PM
                'journaling': [8, 9, 21, 22],  # 8-9 AM or 9-10 PM
                'work': [9, 10, 14, 15],  # 9-10 AM or 2-3 PM
                'personal': [10, 11, 14, 15, 16],  # Mid-morning or afternoon
                'meal': [12, 13, 18, 19],  # Lunch or dinner time
                'social': [18, 19, 20]  # Evening
            }
            
            hours = preferred_hours.get(event_type, [original_time.hour])
            
            # Check next 7 days
            for days_ahead in range(1, 8):
                target_date = original_time + timedelta(days=days_ahead)
                
                for hour in hours:
                    candidate_time = target_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                    # For simplicity, assume this time is available
                    # In a real implementation, you'd check against the calendar
                    return candidate_time
                    
        except Exception as e:
            logger.error(f"Error finding next available day: {e}")
        
        return None
    
    def suggest_batch_alternatives(self, conflicted_events: List[Dict], available_slots: List[datetime]) -> List[Dict]:
        """Suggest alternative times for multiple conflicted events."""
        suggestions = []
        
        try:
            for i, event_conflict in enumerate(conflicted_events):
                event = event_conflict['event']
                
                # Find best matching slot
                best_slot = self._find_best_matching_slot(event, available_slots)
                
                if best_slot:
                    suggestions.append({
                        'original_event': event,
                        'suggested_time': best_slot,
                        'reason': 'Alternative time slot found'
                    })
                    # Remove used slot
                    available_slots.remove(best_slot)
                else:
                    suggestions.append({
                        'original_event': event,
                        'suggested_time': None,
                        'reason': 'No suitable alternative found'
                    })
                    
        except Exception as e:
            logger.error(f"Error suggesting batch alternatives: {e}")
        
        return suggestions
    
    def _find_best_matching_slot(self, event: Dict, available_slots: List[datetime]) -> Optional[datetime]:
        """Find the best matching time slot for an event."""
        if not available_slots:
            return None
        
        try:
            original_time = event['datetime']
            event_type = event['event_type']
            
            # Score each slot based on how well it matches preferences
            scored_slots = []
            
            for slot in available_slots:
                score = 0
                
                # Prefer same day
                if slot.date() == original_time.date():
                    score += 10
                
                # Prefer similar time of day
                time_diff = abs(slot.hour - original_time.hour)
                score += max(0, 5 - time_diff)
                
                # Prefer appropriate times for event type
                if event_type == 'exercise' and slot.hour in [7, 8, 17, 18]:
                    score += 5
                elif event_type == 'therapy' and slot.hour in [18, 19, 20]:
                    score += 5
                elif event_type == 'journaling' and slot.hour in [8, 9, 21, 22]:
                    score += 5
                
                scored_slots.append((slot, score))
            
            # Return the highest scored slot
            scored_slots.sort(key=lambda x: x[1], reverse=True)
            return scored_slots[0][0] if scored_slots else None
            
        except Exception as e:
            logger.error(f"Error finding best matching slot: {e}")
            return available_slots[0] if available_slots else None
    
    def prioritize_events(self, events_list: List[Dict], event_priorities: Dict = None) -> List[Dict]:
        """Prioritize events based on type and user preferences."""
        if event_priorities is None:
            event_priorities = self.event_priorities
        
        try:
            # Add priority scores to events
            for event in events_list:
                event_type = event.get('event_type', 'personal')
                event['priority_score'] = event_priorities.get(event_type, 5)
            
            # Sort by priority (higher first)
            return sorted(events_list, key=lambda x: x['priority_score'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error prioritizing events: {e}")
            return events_list
    
    def auto_resolve_conflicts(self, events_list: List[Dict], resolution_preferences: Dict = None) -> Dict:
        """
        Automatically resolve conflicts with minimal user intervention.
        
        Args:
            events_list: List of events to schedule
            resolution_preferences: User preferences for automatic resolution
            
        Returns:
            Dictionary with resolved events and remaining conflicts
        """
        try:
            # Prioritize events
            prioritized_events = self.prioritize_events(events_list)
            
            resolved_events = []
            remaining_conflicts = []
            occupied_slots = []
            
            for event in prioritized_events:
                event_start = event['datetime']
                event_end = event_start + timedelta(minutes=event['duration'])
                
                # Check if this slot is already occupied
                has_conflict = False
                for occupied_start, occupied_end in occupied_slots:
                    if self._events_overlap(event_start, event_end, occupied_start, occupied_end):
                        has_conflict = True
                        break
                
                if not has_conflict:
                    # No conflict, add to resolved
                    resolved_events.append(event)
                    occupied_slots.append((event_start, event_end))
                else:
                    # Try to find alternative
                    alternative_time = self._find_alternative_times_same_day(
                        event_start, event['duration'], []
                    )
                    
                    if alternative_time:
                        # Use first alternative
                        event['datetime'] = alternative_time[0]
                        resolved_events.append(event)
                        alt_end = alternative_time[0] + timedelta(minutes=event['duration'])
                        occupied_slots.append((alternative_time[0], alt_end))
                    else:
                        # Cannot resolve automatically
                        remaining_conflicts.append(event)
            
            return {
                'resolved_events': resolved_events,
                'remaining_conflicts': remaining_conflicts,
                'auto_resolution_success': len(remaining_conflicts) == 0
            }
            
        except Exception as e:
            logger.error(f"Error in auto conflict resolution: {e}")
            return {
                'resolved_events': [],
                'remaining_conflicts': events_list,
                'auto_resolution_success': False,
                'error': str(e)
            } 