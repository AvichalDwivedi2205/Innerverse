#!/usr/bin/env python3
"""
Firebase Calendar System Setup

This script initializes the Firebase calendar system with the necessary
collections and user profiles for the Innerverse scheduling system.
"""

import os
import sys
from pathlib import Path
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add workspace to path
workspace_root = Path(__file__).parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

from google.cloud import firestore
from agents.scheduling_agent.firebase_calendar import firebase_calendar


def initialize_firebase_calendar():
    """Initialize Firebase collections and indexes for calendar system."""
    print("🔧 Initializing Firebase Calendar System...")
    
    # Get project info
    project_id = os.getenv('FIREBASE_PROJECT_ID') or os.getenv('GOOGLE_CLOUD_PROJECT')
    print(f"📊 Project ID: {project_id}")
    
    try:
        # Initialize Firestore client
        if project_id:
            db = firestore.Client(project=project_id)
        else:
            db = firestore.Client()
        
        print("✅ Connected to Firestore")
        
        # Create sample user profile
        user_id = "current_user"
        user_ref = db.collection("users").document(user_id)
        
        # Default user profile
        user_profile = {
            "profile": {
                "name": "Default User",
                "email": "user@innerverse.com",
                "timezone": "America/New_York",
                "created_at": datetime.now(),
                "system_version": "firebase-calendar-v1"
            },
            "calendar_settings": {
                "default_duration": 60,
                "work_hours_start": "09:00",
                "work_hours_end": "17:00",
                "default_event_type": "personal",
                "time_format": "12-hour",
                "auto_conflict_detection": True,
                "reminder_default": 15  # minutes before event
            }
        }
        
        # Set user profile
        user_ref.set(user_profile, merge=True)
        print(f"✅ Created user profile for: {user_id}")
        
        # Create a sample event to verify the system works
        sample_event_ref = user_ref.collection("calendar_events").document("sample_event")
        sample_event = {
            "event_id": "sample_event",
            "user_id": user_id,
            "title": "Welcome to Firebase Calendar!",
            "description": "This is a sample event to verify your calendar system is working.",
            "start_time": datetime.now().replace(hour=14, minute=0, second=0, microsecond=0),
            "end_time": datetime.now().replace(hour=15, minute=0, second=0, microsecond=0),
            "duration_minutes": 60,
            "event_type": "system",
            "status": "scheduled",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "location": "Firebase Cloud",
            "reminder_settings": {"enabled": True, "minutes_before": 15}
        }
        
        sample_event_ref.set(sample_event)
        print("✅ Created sample calendar event")
        
        print("\n🎉 Firebase Calendar System initialized successfully!")
        print("📊 Collections created:")
        print("   ├── users/{user_id}/")
        print("   │   ├── profile")
        print("   │   ├── calendar_settings")
        print("   │   └── calendar_events/{event_id}")
        print("\n💡 System is ready for scheduling!")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize Firebase Calendar: {e}")
        return False


async def test_firebase_calendar():
    """Test the Firebase calendar system with basic operations."""
    print("\n🧪 Testing Firebase Calendar System...")
    
    try:
        user_id = "current_user"
        
        # Test 1: Initialize user profile
        success = await firebase_calendar.initialize_user_profile(user_id, {
            "name": "Test User",
            "email": "test@innerverse.com"
        })
        
        if success:
            print("✅ Test 1: User profile initialization - PASSED")
        else:
            print("❌ Test 1: User profile initialization - FAILED")
            return False
        
        # Test 2: Create a test event
        test_event_data = {
            "title": "Test Meeting",
            "description": "Firebase calendar test event",
            "start_time": datetime.now() + timedelta(hours=1),  
            "end_time": datetime.now() + timedelta(hours=2),
            "duration_minutes": 60,
            "event_type": "meeting",
            "location": "Test Location"
        }
        
        create_result = await firebase_calendar.create_event(user_id, test_event_data)
        
        if create_result and "event_id" in create_result:
            print("✅ Test 2: Event creation - PASSED")
            test_event_id = create_result["event_id"]
        else:
            print("❌ Test 2: Event creation - FAILED")
            return False
        
        # Test 3: Retrieve events
        events = await firebase_calendar.get_events(user_id)
        
        if len(events) >= 1:
            print(f"✅ Test 3: Event retrieval - PASSED ({len(events)} events found)")
        else:
            print("❌ Test 3: Event retrieval - FAILED")
            return False
        
        # Test 4: Conflict detection
        conflict_start = test_event_data["start_time"] + timedelta(minutes=30)
        conflict_end = conflict_start + timedelta(hours=1)
        
        conflicts = await firebase_calendar.check_conflicts(user_id, conflict_start, conflict_end)
        
        if len(conflicts) > 0:
            print("✅ Test 4: Conflict detection - PASSED")
        else:
            print("❌ Test 4: Conflict detection - FAILED")
            return False
        
        # Test 5: Update event
        update_success = await firebase_calendar.update_event(
            user_id, 
            test_event_id, 
            {"title": "Updated Test Meeting"}
        )
        
        if update_success:
            print("✅ Test 5: Event update - PASSED")
        else:
            print("❌ Test 5: Event update - FAILED")
            return False
        
        # Test 6: Delete event (cleanup)
        delete_success = await firebase_calendar.delete_event(user_id, test_event_id)
        
        if delete_success:
            print("✅ Test 6: Event deletion - PASSED")
        else:
            print("❌ Test 6: Event deletion - FAILED")
            return False
        
        print("\n🎉 All Firebase Calendar tests PASSED!")
        print("🚀 Your calendar system is fully operational!")
        
        return True
        
    except Exception as e:
        print(f"❌ Firebase Calendar test failed: {e}")
        return False


def main():
    """Main setup function."""
    print("🏗️  Firebase Calendar System Setup")
    print("=" * 50)
    
    # Step 1: Initialize Firebase
    init_success = initialize_firebase_calendar()
    
    if not init_success:
        print("❌ Setup failed. Please check your Firebase configuration.")
        return False
    
    # Step 2: Test the system
    print("\n" + "=" * 50)
    test_success = asyncio.run(test_firebase_calendar())
    
    if test_success:
        print("\n🎊 SETUP COMPLETE!")
        print("🚀 Your Firebase Calendar is ready to use!")
        print("\n📝 Quick Start:")
        print("   1. Run: python run_adk_web.py")
        print("   2. Go to ADK web interface")
        print("   3. Select scheduling agent")
        print("   4. Try: 'Schedule a meeting tomorrow at 2pm'")
        return True
    else:
        print("\n❌ Setup completed but tests failed.")
        print("💡 Check your Firebase configuration and try again.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 