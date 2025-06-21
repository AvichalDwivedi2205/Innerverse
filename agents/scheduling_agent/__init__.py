"""Scheduling Agent Package for Innerverse.

This package provides intelligent scheduling capabilities including:
- CRUD operations for calendar events
- Bulk event creation and management
- Conflict detection and resolution
- Natural language processing for complex scheduling requests
- Recurring event handling
"""

from .tools import *

__all__ = [
    'create_event',
    'read_events', 
    'update_event',
    'delete_event',
    'create_multiple_events',
    'create_recurring_events',
    'create_events_with_conflict_resolution'
] 