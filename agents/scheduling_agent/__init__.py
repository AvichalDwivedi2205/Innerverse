"""Google Calendar MCP Scheduling Agent Package for Innerverse.

This package provides intelligent Google Calendar scheduling capabilities using
Model Context Protocol (MCP) with OAuth authentication, including:
- Direct Google Calendar API access through MCP server
- Natural language event creation and management
- Multi-calendar support with conflict detection
- Free/busy queries for optimal scheduling
- Event search and filtering capabilities
- Recurring event handling
- Calendar color management
"""

from .agent import (
    root_agent,
    GoogleCalendarSchedulingAgent,
    get_scheduling_agent,
    schedule_event,
    get_calendar_events
)

__all__ = [
    'root_agent',
    'GoogleCalendarSchedulingAgent',
    'get_scheduling_agent', 
    'schedule_event',
    'get_calendar_events'
] 