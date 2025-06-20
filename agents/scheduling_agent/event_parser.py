"""Event Parser for Natural Language Scheduling Requests.

This module handles parsing complex scheduling requests from natural language input,
extracting multiple events, recurring patterns, and event details.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_date
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)


class EventParser:
    """Parses natural language scheduling requests into structured event data."""
    
    def __init__(self):
        self.day_patterns = {
            'monday': 0, 'mon': 0,
            'tuesday': 1, 'tue': 1, 'tues': 1,
            'wednesday': 2, 'wed': 2,
            'thursday': 3, 'thu': 3, 'thurs': 3,
            'friday': 4, 'fri': 4,
            'saturday': 5, 'sat': 5,
            'sunday': 6, 'sun': 6
        }
        
        self.frequency_patterns = {
            'daily': 'daily',
            'every day': 'daily',
            'weekly': 'weekly',
            'every week': 'weekly',
            'biweekly': 'biweekly',
            'every other week': 'biweekly',
            'monthly': 'monthly',
            'every month': 'monthly'
        }
        
        self.event_type_keywords = {
            'therapy': ['therapy', 'therapist', 'counseling', 'session'],
            'exercise': ['workout', 'exercise', 'gym', 'fitness', 'training'],
            'journaling': ['journal', 'journaling', 'writing', 'reflection'],
            'meal': ['meal', 'lunch', 'dinner', 'breakfast', 'eating'],
            'work': ['work', 'meeting', 'conference', 'office', 'team'],
            'personal': ['personal', 'appointment', 'dentist', 'doctor', 'shopping'],
            'social': ['dinner', 'friends', 'social', 'party', 'hangout']
        }
    
    def parse_scheduling_request(self, user_input: str) -> List[Dict]:
        """
        Parse complex scheduling requests and return structured event data.
        
        Args:
            user_input: Natural language scheduling request
            
        Returns:
            List of event dictionaries with parsed details
        """
        try:
            user_input = user_input.lower().strip()
            logger.info(f"Parsing scheduling request: {user_input}")
            
            # Check if it's a recurring event request
            if self._is_recurring_request(user_input):
                return self._parse_recurring_events(user_input)
            
            # Check if it's a multiple event request
            elif self._is_multiple_events_request(user_input):
                return self._parse_multiple_events(user_input)
            
            # Single event request
            else:
                single_event = self._parse_single_event(user_input)
                return [single_event] if single_event else []
                
        except Exception as e:
            logger.error(f"Error parsing scheduling request: {e}")
            return []
    
    def _is_recurring_request(self, text: str) -> bool:
        """Check if the request is for recurring events."""
        recurring_indicators = [
            'every', 'daily', 'weekly', 'monthly', 'biweekly',
            'for the next', 'for 4 weeks', 'for 2 months',
            'mon/wed/fri', 'monday wednesday friday'
        ]
        return any(indicator in text for indicator in recurring_indicators)
    
    def _is_multiple_events_request(self, text: str) -> bool:
        """Check if the request contains multiple distinct events."""
        multiple_indicators = [
            ' and ', ', ', ': ', 'also ', 'plus ',
            'i need to', 'schedule:', 'add:'
        ]
        return any(indicator in text for indicator in multiple_indicators)
    
    def _parse_recurring_events(self, text: str) -> List[Dict]:
        """Parse recurring event patterns."""
        events = []
        
        try:
            # Extract the base event details
            event_title = self._extract_event_title(text)
            event_type = self._identify_event_type(text)
            duration = self._extract_duration(text)
            time_str = self._extract_time(text)
            
            # Parse recurring pattern
            pattern = self._parse_recurring_pattern(text)
            
            if pattern and time_str:
                # Generate individual event instances
                event_instances = self._generate_recurring_instances(
                    event_title, event_type, time_str, duration, pattern
                )
                events.extend(event_instances)
            
        except Exception as e:
            logger.error(f"Error parsing recurring events: {e}")
        
        return events
    
    def _parse_multiple_events(self, text: str) -> List[Dict]:
        """Parse multiple distinct events from a single request."""
        events = []
        
        try:
            # Split the text into individual event parts
            event_parts = self._split_multiple_events(text)
            
            for part in event_parts:
                event = self._parse_single_event(part.strip())
                if event:
                    events.append(event)
                    
        except Exception as e:
            logger.error(f"Error parsing multiple events: {e}")
        
        return events
    
    def _parse_single_event(self, text: str) -> Optional[Dict]:
        """Parse a single event from text."""
        try:
            event = {
                'title': self._extract_event_title(text),
                'event_type': self._identify_event_type(text),
                'datetime': self._extract_datetime(text),
                'duration': self._extract_duration(text),
                'description': text,
                'frequency': 'once'
            }
            
            # Validate that we have minimum required information
            if event['title'] and event['datetime']:
                return event
            
        except Exception as e:
            logger.error(f"Error parsing single event: {e}")
        
        return None
    
    def _extract_event_title(self, text: str) -> str:
        """Extract event title from text."""
        # Remove common scheduling words to get the core activity
        scheduling_words = ['schedule', 'add', 'create', 'book', 'set up']
        
        for word in scheduling_words:
            text = text.replace(word, '').strip()
        
        # Try to identify the main activity
        for event_type, keywords in self.event_type_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    if event_type == 'therapy':
                        return 'Therapy Session'
                    elif event_type == 'exercise':
                        return 'Exercise/Workout'
                    elif event_type == 'journaling':
                        return 'Journaling'
                    else:
                        return keyword.title()
        
        # Fallback: use first few words
        words = text.split()[:3]
        return ' '.join(words).title() if words else 'Scheduled Event'
    
    def _identify_event_type(self, text: str) -> str:
        """Identify the type of event from text."""
        for event_type, keywords in self.event_type_keywords.items():
            if any(keyword in text for keyword in keywords):
                return event_type
        return 'personal'
    
    def _extract_datetime(self, text: str) -> Optional[datetime]:
        """Extract datetime from text."""
        try:
            # Common time patterns
            time_patterns = [
                r'(\d{1,2}):(\d{2})\s*(am|pm)',
                r'(\d{1,2})\s*(am|pm)',
                r'at\s+(\d{1,2}):(\d{2})\s*(am|pm)?',
                r'at\s+(\d{1,2})\s*(am|pm)'
            ]
            
            # Date patterns
            date_patterns = [
                r'tomorrow',
                r'today',
                r'next\s+(\w+)',
                r'this\s+(\w+)',
                r'(\w+day)'
            ]
            
            # Try to extract time
            time_match = None
            for pattern in time_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    time_match = match
                    break
            
            # Try to extract date
            date_match = None
            for pattern in date_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    date_match = match
                    break
            
            # Combine date and time
            if time_match:
                return self._construct_datetime(date_match, time_match, text)
            
        except Exception as e:
            logger.error(f"Error extracting datetime: {e}")
        
        return None
    
    def _extract_time(self, text: str) -> Optional[str]:
        """Extract time string from text."""
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(am|pm)',
            r'(\d{1,2})\s*(am|pm)',
            r'at\s+(\d{1,2}):(\d{2})\s*(am|pm)?',
            r'at\s+(\d{1,2})\s*(am|pm)'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def _extract_duration(self, text: str) -> int:
        """Extract duration in minutes from text."""
        # Duration patterns
        duration_patterns = [
            r'(\d+)\s*hours?',
            r'(\d+)\s*minutes?',
            r'(\d+)\s*mins?',
            r'for\s+(\d+)\s*hours?',
            r'for\s+(\d+)\s*minutes?'
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                duration = int(match.group(1))
                if 'hour' in pattern:
                    return duration * 60
                else:
                    return duration
        
        # Default durations based on event type
        event_type = self._identify_event_type(text)
        default_durations = {
            'therapy': 60,
            'exercise': 30,
            'journaling': 15,
            'meal': 60,
            'work': 60,
            'personal': 30,
            'social': 120
        }
        
        return default_durations.get(event_type, 60)
    
    def _parse_recurring_pattern(self, text: str) -> Optional[Dict]:
        """Parse recurring pattern from text."""
        pattern = {}
        
        # Check for frequency
        for freq_text, freq_value in self.frequency_patterns.items():
            if freq_text in text:
                pattern['frequency'] = freq_value
                break
        
        # Check for specific days (Mon/Wed/Fri pattern)
        days_match = re.search(r'(mon|tue|wed|thu|fri|sat|sun)[/,\s]+(mon|tue|wed|thu|fri|sat|sun)', text, re.IGNORECASE)
        if days_match:
            pattern['frequency'] = 'weekly'
            pattern['days'] = self._extract_days_from_text(text)
        
        # Check for duration (how long to repeat)
        duration_match = re.search(r'for\s+(\d+)\s+(weeks?|months?)', text, re.IGNORECASE)
        if duration_match:
            count = int(duration_match.group(1))
            unit = duration_match.group(2).lower()
            pattern['duration'] = {'count': count, 'unit': unit}
        
        return pattern if pattern else None
    
    def _extract_days_from_text(self, text: str) -> List[int]:
        """Extract day numbers from text like 'Mon/Wed/Fri'."""
        days = []
        for day_name, day_num in self.day_patterns.items():
            if day_name in text:
                days.append(day_num)
        return sorted(list(set(days)))
    
    def _split_multiple_events(self, text: str) -> List[str]:
        """Split text into individual event parts."""
        # Split on common separators
        separators = [' and ', ', ', ': ', ' also ', ' plus ']
        
        parts = [text]
        for separator in separators:
            new_parts = []
            for part in parts:
                new_parts.extend(part.split(separator))
            parts = new_parts
        
        # Clean up parts
        cleaned_parts = []
        for part in parts:
            part = part.strip()
            if len(part) > 5:  # Filter out very short parts
                cleaned_parts.append(part)
        
        return cleaned_parts
    
    def _generate_recurring_instances(self, title: str, event_type: str, time_str: str, 
                                    duration: int, pattern: Dict) -> List[Dict]:
        """Generate individual event instances from recurring pattern."""
        events = []
        
        try:
            frequency = pattern.get('frequency', 'weekly')
            duration_info = pattern.get('duration', {'count': 4, 'unit': 'weeks'})
            days = pattern.get('days', [])
            
            # Calculate end date
            end_date = datetime.now()
            if duration_info['unit'] == 'weeks':
                end_date += timedelta(weeks=duration_info['count'])
            elif duration_info['unit'] == 'months':
                end_date += relativedelta(months=duration_info['count'])
            
            # Generate events based on frequency
            current_date = datetime.now()
            
            while current_date <= end_date:
                if frequency == 'daily':
                    event_datetime = self._combine_date_time(current_date, time_str)
                    if event_datetime:
                        events.append({
                            'title': title,
                            'event_type': event_type,
                            'datetime': event_datetime,
                            'duration': duration,
                            'description': f'Recurring {title}',
                            'frequency': frequency
                        })
                    current_date += timedelta(days=1)
                    
                elif frequency == 'weekly':
                    if days:
                        # Specific days (Mon/Wed/Fri)
                        for day in days:
                            event_date = current_date + timedelta(days=(day - current_date.weekday()) % 7)
                            if event_date <= end_date:
                                event_datetime = self._combine_date_time(event_date, time_str)
                                if event_datetime:
                                    events.append({
                                        'title': title,
                                        'event_type': event_type,
                                        'datetime': event_datetime,
                                        'duration': duration,
                                        'description': f'Recurring {title}',
                                        'frequency': frequency
                                    })
                    else:
                        # Same day each week
                        event_datetime = self._combine_date_time(current_date, time_str)
                        if event_datetime:
                            events.append({
                                'title': title,
                                'event_type': event_type,
                                'datetime': event_datetime,
                                'duration': duration,
                                'description': f'Recurring {title}',
                                'frequency': frequency
                            })
                    current_date += timedelta(weeks=1)
                    
        except Exception as e:
            logger.error(f"Error generating recurring instances: {e}")
        
        return events
    
    def _combine_date_time(self, date: datetime, time_str: str) -> Optional[datetime]:
        """Combine date and time string into datetime."""
        try:
            # Parse time string
            time_match = re.search(r'(\d{1,2}):?(\d{2})?\s*(am|pm)', time_str, re.IGNORECASE)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2)) if time_match.group(2) else 0
                ampm = time_match.group(3).lower()
                
                if ampm == 'pm' and hour != 12:
                    hour += 12
                elif ampm == 'am' and hour == 12:
                    hour = 0
                
                return date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
        except Exception as e:
            logger.error(f"Error combining date and time: {e}")
        
        return None
    
    def _construct_datetime(self, date_match, time_match, text: str) -> Optional[datetime]:
        """Construct datetime from date and time matches."""
        try:
            # Get base date
            base_date = datetime.now()
            
            if date_match:
                date_text = date_match.group(0).lower()
                if 'tomorrow' in date_text:
                    base_date += timedelta(days=1)
                elif 'next' in date_text:
                    # Next [day of week]
                    day_name = date_match.group(1) if date_match.groups() else None
                    if day_name and day_name.lower() in self.day_patterns:
                        target_day = self.day_patterns[day_name.lower()]
                        days_ahead = (target_day - base_date.weekday() + 7) % 7
                        if days_ahead == 0:  # If it's the same day, go to next week
                            days_ahead = 7
                        base_date += timedelta(days=days_ahead)
            
            # Apply time
            if time_match:
                groups = time_match.groups()
                try:
                    hour = int(groups[0])
                    minute = int(groups[1]) if len(groups) > 1 and groups[1] and groups[1].isdigit() else 0
                    ampm = groups[-1].lower() if groups[-1] and groups[-1].lower() in ['am', 'pm'] else None
                    
                    if ampm == 'pm' and hour != 12:
                        hour += 12
                    elif ampm == 'am' and hour == 12:
                        hour = 0
                    
                    return base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                except (ValueError, TypeError) as e:
                    logger.error(f"Error parsing time components: {e}")
                    return None
            
        except Exception as e:
            logger.error(f"Error constructing datetime: {e}")
        
        return None 