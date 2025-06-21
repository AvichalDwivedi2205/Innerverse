#!/usr/bin/env python3
"""
Test Firebase Scheduling Agent

This script demonstrates the Firebase-powered scheduling agent functionality.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add workspace to path
workspace_root = Path(__file__).parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

# Import the scheduling agent
from agents.scheduling_agent.agent import schedule_meeting, show_calendar


def test_scheduling_scenarios():
    """Test various scheduling scenarios."""
    print("🧪 Testing Firebase Scheduling Agent")
    print("=" * 50)
    
    # Test 1: Schedule a meeting for tomorrow
    print("\n📅 Test 1: Schedule meeting tomorrow at 2pm")
    result = schedule_meeting(
        title="Team Standup",
        when="tomorrow at 2pm", 
        duration=30,
        event_type="meeting",
        description="Daily team standup meeting"
    )
    print(result)
    
    # Test 2: Schedule another meeting (should detect conflict)
    print("\n📅 Test 2: Schedule conflicting meeting")
    result = schedule_meeting(
        title="Project Review",
        when="tomorrow at 2:15pm",
        duration=60,
        event_type="meeting",
        description="Quarterly project review"
    )
    print(result)
    
    # Test 3: Schedule a non-conflicting meeting
    print("\n📅 Test 3: Schedule non-conflicting meeting")
    result = schedule_meeting(
        title="Client Call",
        when="tomorrow at 4pm",
        duration=45,
        event_type="meeting",
        description="Client check-in call"
    )
    print(result)
    
    # Test 4: Schedule therapy session
    print("\n📅 Test 4: Schedule therapy session")
    result = schedule_meeting(
        title="Therapy Session",
        when="next Tuesday at 6pm",
        duration=60,
        event_type="therapy",
        description="Weekly therapy appointment"
    )
    print(result)
    
    # Test 5: Show calendar
    print("\n📅 Test 5: Show calendar")
    result = show_calendar("this week")
    print(result)


def test_natural_language_parsing():
    """Test various natural language date/time inputs."""
    print("\n🗣️ Testing Natural Language Parsing")
    print("=" * 50)
    
    test_cases = [
        ("tomorrow at 2pm", "Team Meeting"),
        ("today at 5:30pm", "End of Day Review"),
        ("next Friday at 10am", "Weekly Planning"),
        ("Tuesday at 3pm", "Client Call"),
        ("tomorrow at 9am", "Morning Standup")
    ]
    
    for when, title in test_cases:
        print(f"\n🔍 Parsing: '{when}' for '{title}'")
        result = schedule_meeting(
            title=title,
            when=when,
            duration=60,
            event_type="meeting"
        )
        # Just show the first few lines of the result
        lines = result.split('\n')
        print(lines[0])  # Show success/failure line
        if len(lines) > 3:
            print(lines[3])  # Show when info


if __name__ == "__main__":
    print("🚀 Firebase Calendar System - Functionality Test")
    print("=" * 60)
    
    # Test basic scheduling
    test_scheduling_scenarios()
    
    # Test natural language parsing
    test_natural_language_parsing()
    
    print("\n" + "=" * 60)
    print("🎉 Firebase Scheduling Test Complete!")
    print("\n💡 Next Steps:")
    print("   1. Run: python run_adk_web.py")
    print("   2. Go to ADK web interface")
    print("   3. Select 'firebase_scheduling_agent'")
    print("   4. Try: 'Schedule a meeting tomorrow at 2pm for 1 hour'")
    print("   5. Try: 'Show my calendar this week'") 