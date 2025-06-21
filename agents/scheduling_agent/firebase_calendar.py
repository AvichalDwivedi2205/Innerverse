"""
Firebase Calendar Service for Innerverse Scheduling Agent

This module provides a Firebase-based calendar service for storing and managing
user schedules without requiring Google Calendar OAuth.
"""

import os
import sys
import uuid
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

# Ensure the workspace root is in Python path
workspace_root = Path(__file__).parent.parent.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

logger = logging.getLogger(__name__)


class FirebaseCalendarService:
    """Firebase-based calendar service for storing user schedules."""
    
    def __init__(self):
        """Initialize Firebase client with project configuration."""
        try:
            # Get project ID from environment
            project_id = os.getenv('FIREBASE_PROJECT_ID') or os.getenv('GOOGLE_CLOUD_PROJECT')
            
            if project_id:
                self.db = firestore.Client(project=project_id)
                logger.info(f"Firebase Calendar Service initialized with project: {project_id}")
            else:
                self.db = firestore.Client()
                logger.info("Firebase Calendar Service initialized with default project")
                
        except Exception as e:
            logger.error(f"Failed to initialize Firebase client: {e}")
            raise
    
    async def create_event(self, user_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new calendar event.
        
        Args:
            user_id: User identifier
            event_data: Event information dict
            
        Returns:
            Dict containing event_id, status, and event_data
        """
        try:
            event_id = str(uuid.uuid4())
            
            # Prepare event document
            event_doc = {
                "event_id": event_id,
                "user_id": user_id,
                "title": event_data["title"],
                "description": event_data.get("description", ""),
                "start_time": event_data["start_time"],
                "end_time": event_data["end_time"], 
                "duration_minutes": event_data["duration_minutes"],
                "event_type": event_data.get("event_type", "personal"),
                "status": "scheduled",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "location": event_data.get("location", ""),
                "reminder_settings": event_data.get("reminders", {}),
                "recurrence_rule": event_data.get("recurrence_rule", None)
            }
            
            # Store in Firebase
            doc_ref = self.db.collection("users").document(user_id).collection("calendar_events").document(event_id)
            doc_ref.set(event_doc)
            
            logger.info(f"Created calendar event: {event_id} for user: {user_id}")
            
            return {
                "event_id": event_id, 
                "status": "created", 
                "event_data": event_doc
            }
            
        except Exception as e:
            logger.error(f"Failed to create event: {e}")
            raise
    
    async def get_events(self, user_id: str, start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """
        Get user's calendar events with optional date filtering.
        
        Args:
            user_id: User identifier
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of event dictionaries
        """
        try:
            query = self.db.collection("users").document(user_id).collection("calendar_events")
            
            # Get all events and filter in memory to avoid requiring indexes
            events = []
            for doc in query.stream():
                event_data = doc.to_dict()
                
                # Filter by status
                if event_data.get("status") != "scheduled":
                    continue
                
                # Filter by date range if provided
                event_start = event_data.get("start_time")
                if event_start:
                    try:
                        # Handle timezone consistency for date comparison
                        if hasattr(event_start, 'replace') and event_start.tzinfo:
                            event_start = event_start.replace(tzinfo=None)
                        
                        if start_date and event_start < start_date:
                            continue
                        if end_date and event_start > end_date:
                            continue
                    except Exception:
                        # Skip date filtering if comparison fails
                        pass
                
                events.append(event_data)
            
            # Sort by start time
            events.sort(key=lambda x: x.get("start_time", datetime.min))
            
            logger.info(f"Retrieved {len(events)} events for user: {user_id}")
            return events
            
        except Exception as e:
            logger.error(f"Failed to get events: {e}")
            return []
    
    async def update_event(self, user_id: str, event_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing event.
        
        Args:
            user_id: User identifier
            event_id: Event identifier to update
            updates: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            doc_ref = self.db.collection("users").document(user_id).collection("calendar_events").document(event_id)
            
            # Add updated timestamp
            updates["updated_at"] = datetime.now()
            
            doc_ref.update(updates)
            
            logger.info(f"Updated event: {event_id} for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update event: {e}")
            return False
    
    async def delete_event(self, user_id: str, event_id: str) -> bool:
        """
        Delete an event (or mark as cancelled).
        
        Args:
            user_id: User identifier
            event_id: Event identifier to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            doc_ref = self.db.collection("users").document(user_id).collection("calendar_events").document(event_id)
            
            # Instead of deleting, mark as cancelled for audit trail
            doc_ref.update({
                "status": "cancelled",
                "updated_at": datetime.now()
            })
            
            logger.info(f"Cancelled event: {event_id} for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete event: {e}")
            return False
    
    async def check_conflicts(self, user_id: str, start_time: datetime, end_time: datetime, exclude_event_id: str = None) -> List[Dict]:
        """
        Check for scheduling conflicts.
        
        Args:
            user_id: User identifier
            start_time: Start time of new event
            end_time: End time of new event
            exclude_event_id: Optional event ID to exclude from conflict check
            
        Returns:
            List of conflicting events
        """
        try:
            query = self.db.collection("users").document(user_id).collection("calendar_events")
            
            conflicts = []
            for doc in query.stream():
                event = doc.to_dict()
                
                # Only check scheduled events
                if event.get("status") != "scheduled":
                    continue
                
                # Skip the event we're updating
                if exclude_event_id and event.get("event_id") == exclude_event_id:
                    continue
                
                event_start = event.get("start_time")
                event_end = event.get("end_time")
                
                # Skip events without proper time data
                if not event_start or not event_end:
                    continue
                
                # Ensure timezone consistency for comparison
                try:
                    # Convert to naive datetime if needed
                    if hasattr(event_start, 'replace') and event_start.tzinfo:
                        event_start = event_start.replace(tzinfo=None)
                    if hasattr(event_end, 'replace') and event_end.tzinfo:
                        event_end = event_end.replace(tzinfo=None)
                    if hasattr(start_time, 'replace') and start_time.tzinfo:
                        start_time = start_time.replace(tzinfo=None)
                    if hasattr(end_time, 'replace') and end_time.tzinfo:
                        end_time = end_time.replace(tzinfo=None)
                    
                    # Check for overlap: events overlap if start_time < other_end AND end_time > other_start
                    if (start_time < event_end) and (end_time > event_start):
                        conflicts.append(event)
                except Exception:
                    # Skip this event if datetime comparison fails
                    continue
            
            logger.info(f"Found {len(conflicts)} conflicts for user: {user_id}")
            return conflicts
            
        except Exception as e:
            logger.error(f"Failed to check conflicts: {e}")
            return []
    
    async def get_event_by_id(self, user_id: str, event_id: str) -> Optional[Dict]:
        """
        Get a specific event by ID.
        
        Args:
            user_id: User identifier
            event_id: Event identifier
            
        Returns:
            Event dictionary or None if not found
        """
        try:
            doc_ref = self.db.collection("users").document(user_id).collection("calendar_events").document(event_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to get event by ID: {e}")
            return None
    
    async def initialize_user_profile(self, user_id: str, profile_data: Dict[str, Any] = None) -> bool:
        """
        Initialize user profile and calendar settings.
        
        Args:
            user_id: User identifier
            profile_data: Optional profile information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            user_ref = self.db.collection("users").document(user_id)
            
            # Default profile data
            default_profile = {
                "profile": {
                    "name": profile_data.get("name", "Default User") if profile_data else "Default User",
                    "email": profile_data.get("email", "") if profile_data else "",
                    "timezone": "America/New_York",
                    "created_at": datetime.now()
                },
                "calendar_settings": {
                    "default_duration": 60,
                    "work_hours_start": "09:00",
                    "work_hours_end": "17:00",
                    "default_event_type": "personal",
                    "time_format": "12-hour"
                }
            }
            
            # Merge with provided data
            if profile_data:
                default_profile["profile"].update(profile_data)
            
            user_ref.set(default_profile, merge=True)
            
            logger.info(f"Initialized user profile: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize user profile: {e}")
            return False


# Global instance
firebase_calendar = FirebaseCalendarService() 