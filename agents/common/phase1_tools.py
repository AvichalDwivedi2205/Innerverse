"""Phase 1 Tools Demonstration - Innerverse.

This module demonstrates how to use the new Phase 1 components:
- Enhanced tool results system
- Google Services Hub (STT, Vision, Calendar)
- Local Session Timer (hybrid approach)
- New Firestore collections

These are example tools that can be integrated into agents.
"""

import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from .tool_results import (
    ExerciseToolResult, 
    SchedulingToolResult, 
    NutritionToolResult, 
    TimerToolResult
)
from .google_services import google_services
from .session_timer import LocalSessionTimer, SessionType
from google.cloud import firestore

logger = logging.getLogger(__name__)


# ============================================================================
# EXERCISE TOOLS (10-minute sessions)
# ============================================================================

async def start_exercise_session(
    exercise_type: str,  # "CBT", "mindfulness", "gratitude", "PMR"
    user_id: str
) -> ExerciseToolResult:
    """Start a 10-minute exercise session with real-time timing.
    
    Args:
        exercise_type: Type of exercise (CBT, mindfulness, gratitude, PMR)
        user_id: User identifier
        
    Returns:
        ExerciseToolResult with session details
    """
    try:
        # Validate exercise type
        valid_types = ["CBT", "mindfulness", "gratitude", "PMR"]
        if exercise_type not in valid_types:
            return ExerciseToolResult.error_result(
                message=f"Invalid exercise type. Must be one of: {valid_types}",
                error_details=f"Provided: {exercise_type}"
            )
        
        # Create session timer
        timer = LocalSessionTimer(SessionType.EXERCISE, user_id)
        
        # Start the session
        session_id = await timer.start_session()
        
        # Store initial exercise record in Firestore
        exercise_id = str(uuid.uuid4())
        db = firestore.Client()
        
        exercise_doc = {
            "exerciseId": exercise_id,
            "sessionId": session_id,
            "type": exercise_type,
            "userId": user_id,
            "startTime": datetime.now().isoformat(),
            "duration": 10,  # Fixed 10 minutes
            "status": "active",
            "effectivenessScore": None,
            "notes": "",
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat()
        }
        
        db.collection("users").document(user_id).collection("exercises").document(exercise_id).set(exercise_doc)
        
        logger.info(f"Exercise session started: {exercise_type} for user {user_id}")
        
        return ExerciseToolResult.success_result(
            data={
                "exercise_id": exercise_id,
                "session_id": session_id,
                "timer_status": timer.get_session_status(),
                "exercise_instructions": _get_exercise_instructions(exercise_type)
            },
            message=f"Started {exercise_type} exercise session (10 minutes)",
            exercise_id=exercise_id,
            exercise_type=exercise_type,
            next_actions=["follow_exercise_instructions", "complete_when_done"]
        )
        
    except Exception as e:
        logger.error(f"Failed to start exercise session: {e}")
        return ExerciseToolResult.error_result(
            message="Failed to start exercise session",
            error_details=str(e)
        )


async def complete_exercise_session(
    exercise_id: str,
    user_id: str,
    effectiveness_score: int,  # 1-10 scale
    notes: Optional[str] = None
) -> ExerciseToolResult:
    """Complete an exercise session and store results.
    
    Args:
        exercise_id: Exercise session identifier
        user_id: User identifier
        effectiveness_score: How effective was the exercise (1-10)
        notes: Optional user notes
        
    Returns:
        ExerciseToolResult with completion details
    """
    try:
        # Validate effectiveness score
        if not 1 <= effectiveness_score <= 10:
            return ExerciseToolResult.error_result(
                message="Effectiveness score must be between 1 and 10",
                error_details=f"Provided: {effectiveness_score}"
            )
        
        # Update exercise record in Firestore
        db = firestore.Client()
        exercise_ref = db.collection("users").document(user_id).collection("exercises").document(exercise_id)
        
        update_data = {
            "completedAt": datetime.now().isoformat(),
            "effectivenessScore": effectiveness_score,
            "notes": notes or "",
            "status": "completed",
            "updatedAt": datetime.now().isoformat()
        }
        
        exercise_ref.update(update_data)
        
        logger.info(f"Exercise session completed: {exercise_id} with score {effectiveness_score}")
        
        return ExerciseToolResult.success_result(
            data={
                "completion_time": datetime.now().isoformat(),
                "effectiveness_score": effectiveness_score,
                "notes": notes
            },
            message=f"Exercise completed with effectiveness score: {effectiveness_score}/10",
            exercise_id=exercise_id,
            effectiveness_score=effectiveness_score,
            next_actions=["view_exercise_progress", "schedule_next_exercise"]
        )
        
    except Exception as e:
        logger.error(f"Failed to complete exercise session: {e}")
        return ExerciseToolResult.error_result(
            message="Failed to complete exercise session",
            error_details=str(e)
        )


def _get_exercise_instructions(exercise_type: str) -> Dict[str, Any]:
    """Get instructions for each exercise type."""
    instructions = {
        "CBT": {
            "title": "Cognitive Behavioral Therapy - Thought Examination",
            "duration": "10 minutes",
            "steps": [
                "Identify a current negative thought or belief",
                "Examine the evidence for and against this thought",
                "Consider alternative, more balanced perspectives",
                "Practice replacing the thought with a more helpful one",
                "Reflect on how this new perspective feels"
            ],
            "focus": "Examining and restructuring thought patterns"
        },
        "mindfulness": {
            "title": "Mindfulness - Present Awareness",
            "duration": "10 minutes",
            "steps": [
                "Find a comfortable position and close your eyes",
                "Focus on your breath, feeling each inhale and exhale",
                "Notice thoughts and feelings without judgment",
                "When mind wanders, gently return focus to breath",
                "End with a moment of gratitude for this time"
            ],
            "focus": "Cultivating present-moment awareness"
        },
        "gratitude": {
            "title": "Gratitude Practice - Appreciation Creation",
            "duration": "10 minutes",
            "steps": [
                "Think of 3 specific things you're grateful for today",
                "Reflect on why each item brings you gratitude",
                "Feel the positive emotions associated with each",
                "Consider how you can express gratitude to others",
                "Write down your reflections if helpful"
            ],
            "focus": "Developing appreciation and positive emotions"
        },
        "PMR": {
            "title": "Progressive Muscle Relaxation - Body Awareness",
            "duration": "10 minutes",
            "steps": [
                "Start with your toes, tense for 5 seconds then relax",
                "Move up to calves, thighs, abdomen, arms",
                "Tense each muscle group, then release completely",
                "Notice the difference between tension and relaxation",
                "End with full-body relaxation and deep breathing"
            ],
            "focus": "Physical relaxation and body awareness"
        }
    }
    
    return instructions.get(exercise_type, {})


# ============================================================================
# SCHEDULING TOOLS (Wellness + General Life)
# ============================================================================

async def create_schedule_event(
    user_id: str,
    title: str,
    description: str,
    start_time: datetime,
    duration_minutes: int,
    event_type: str,  # "therapy", "exercise", "journaling", "meal", "sleep", "study", "work", "personal"
    frequency: str = "once"  # "daily", "weekly", "biweekly", "monthly", "once"
) -> SchedulingToolResult:
    """Create a scheduled event with Google Calendar integration.
    
    Args:
        user_id: User identifier
        title: Event title
        description: Event description
        start_time: When the event starts
        duration_minutes: How long the event lasts
        event_type: Type of event
        frequency: How often it repeats
        
    Returns:
        SchedulingToolResult with scheduling details
    """
    try:
        # Validate event type
        valid_types = ["therapy", "exercise", "journaling", "meal", "sleep", "study", "work", "personal"]
        if event_type not in valid_types:
            return SchedulingToolResult.error_result(
                message=f"Invalid event type. Must be one of: {valid_types}",
                error_details=f"Provided: {event_type}"
            )
        
        # Calculate end time
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Create Google Calendar event
        event_details = {
            "title": title,
            "description": description,
            "start_time": start_time,
            "end_time": end_time
        }
        
        google_event_id = await google_services.create_calendar_event(event_details)
        
        # Store in Firestore
        schedule_id = str(uuid.uuid4())
        db = firestore.Client()
        
        # Determine category based on event type
        category = "wellness" if event_type in ["therapy", "exercise", "journaling"] else "personal"
        
        schedule_doc = {
            "scheduleId": schedule_id,
            "userId": user_id,
            "title": title,
            "description": description,
            "type": event_type,
            "category": category,
            "googleEventId": google_event_id,
            "scheduledTime": start_time,
            "endTime": end_time,
            "durationMinutes": duration_minutes,
            "frequency": frequency,
            "status": "scheduled",
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        db.collection("users").document(user_id).collection("schedules").document(schedule_id).set(schedule_doc)
        
        logger.info(f"Schedule event created: {title} for user {user_id}")
        
        return SchedulingToolResult.success_result(
            data={
                "schedule_id": schedule_id,
                "google_event_id": google_event_id,
                "event_details": schedule_doc
            },
            message=f"Scheduled '{title}' for {start_time.strftime('%Y-%m-%d %H:%M')}",
            google_event_id=google_event_id,
            scheduled_time=start_time,
            schedule_category=category,
            frequency=frequency,
            next_actions=["set_reminders", "view_schedule"]
        )
        
    except Exception as e:
        logger.error(f"Failed to create schedule event: {e}")
        return SchedulingToolResult.error_result(
            message="Failed to create schedule event",
            error_details=str(e)
        )


# ============================================================================
# NUTRITION TOOLS (Mock implementation)
# ============================================================================

async def analyze_food_image(
    user_id: str,
    image_data: bytes,
    meal_type: str = "snack"  # "breakfast", "lunch", "dinner", "snack"
) -> NutritionToolResult:
    """Analyze food image for calorie tracking using Google Vision API.
    
    Args:
        user_id: User identifier
        image_data: Image data in bytes
        meal_type: Type of meal
        
    Returns:
        NutritionToolResult with food analysis
    """
    try:
        # Use Google Vision API to analyze food
        analysis_result = await google_services.analyze_food_image(image_data)
        
        # Get today's date for daily calorie tracking
        today_date = datetime.now().strftime("%Y-%m-%d")
        
        # Store/update daily calories in Firestore
        db = firestore.Client()
        daily_calories_ref = db.collection("users").document(user_id).collection("nutrition").document("dailyCalories").collection(today_date).document("total")
        
        # Get current daily total
        daily_doc = daily_calories_ref.get()
        current_total = daily_doc.to_dict().get("totalCalories", 0) if daily_doc.exists else 0
        
        # Add new calories
        new_total = current_total + analysis_result["estimated_calories"]
        
        # Update daily calories
        daily_data = {
            "totalCalories": new_total,
            "lastUpdated": datetime.now().isoformat(),
            "meals": firestore.ArrayUnion([{
                "mealType": meal_type,
                "calories": analysis_result["estimated_calories"],
                "foods": analysis_result["detected_foods"],
                "timestamp": datetime.now().isoformat(),
                "confidence": analysis_result["confidence"]
            }])
        }
        
        daily_calories_ref.set(daily_data, merge=True)
        
        logger.info(f"Food analysis completed for user {user_id}: {analysis_result['estimated_calories']} calories")
        
        return NutritionToolResult.success_result(
            data={
                "analysis_result": analysis_result,
                "daily_total": new_total,
                "meal_added": {
                    "type": meal_type,
                    "calories": analysis_result["estimated_calories"],
                    "foods": analysis_result["detected_foods"]
                }
            },
            message=f"Added {analysis_result['estimated_calories']} calories. Daily total: {new_total}",
            daily_calories=new_total,
            vision_analysis_confidence=analysis_result["confidence"],
            food_items_detected=analysis_result["detected_foods"],
            next_actions=["view_daily_nutrition", "add_more_meals"]
        )
        
    except Exception as e:
        logger.error(f"Failed to analyze food image: {e}")
        return NutritionToolResult.error_result(
            message="Failed to analyze food image",
            error_details=str(e)
        )


async def reset_daily_calories(user_id: str) -> NutritionToolResult:
    """Reset daily calorie counter to 0.
    
    Args:
        user_id: User identifier
        
    Returns:
        NutritionToolResult with reset confirmation
    """
    try:
        today_date = datetime.now().strftime("%Y-%m-%d")
        
        # Reset today's calories in Firestore
        db = firestore.Client()
        daily_calories_ref = db.collection("users").document(user_id).collection("nutrition").document("dailyCalories").collection(today_date).document("total")
        
        reset_data = {
            "totalCalories": 0,
            "lastReset": datetime.now().isoformat(),
            "meals": []
        }
        
        daily_calories_ref.set(reset_data)
        
        logger.info(f"Daily calories reset for user {user_id}")
        
        return NutritionToolResult.success_result(
            data={
                "reset_date": today_date,
                "reset_time": datetime.now().isoformat()
            },
            message="Daily calorie counter reset to 0",
            daily_calories=0,
            next_actions=["start_new_day_tracking"]
        )
        
    except Exception as e:
        logger.error(f"Failed to reset daily calories: {e}")
        return NutritionToolResult.error_result(
            message="Failed to reset daily calories",
            error_details=str(e)
        )


# ============================================================================
# SPEECH-TO-TEXT TOOLS
# ============================================================================

async def transcribe_audio_input(
    audio_data: bytes,
    context: str = "general",  # "therapy", "journaling", "general"
    language_code: str = "en-US"
) -> Dict[str, Any]:
    """Transcribe audio input using Google Speech-to-Text.
    
    Args:
        audio_data: Audio data in bytes format
        context: Context for better transcription accuracy
        language_code: Language code for transcription
        
    Returns:
        Dictionary with transcription results
    """
    try:
        # Use Google Speech-to-Text
        transcript = await google_services.transcribe_audio(audio_data, language_code)
        
        logger.info(f"Audio transcribed successfully for context: {context}")
        
        return {
            "success": True,
            "transcript": transcript,
            "context": context,
            "language": language_code,
            "timestamp": datetime.now().isoformat(),
            "character_count": len(transcript)
        }
        
    except Exception as e:
        logger.error(f"Failed to transcribe audio: {e}")
        return {
            "success": False,
            "error": str(e),
            "context": context
        }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def get_google_services_status() -> Dict[str, Any]:
    """Get status of all Google Cloud services."""
    try:
        # Initialize services
        await google_services.initialize_all_services()
        
        # Get service status
        status = google_services.get_service_status()
        
        # Perform health check
        health = await google_services.health_check()
        
        return {
            "service_status": status,
            "health_check": health,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get services status: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


async def get_user_phase1_summary(user_id: str) -> Dict[str, Any]:
    """Get a summary of all Phase 1 data for a user.
    
    Args:
        user_id: User identifier
        
    Returns:
        Dictionary with comprehensive user data
    """
    try:
        db = firestore.Client()
        
        # Get exercise data
        exercises_ref = db.collection("users").document(user_id).collection("exercises")
        exercises = [doc.to_dict() for doc in exercises_ref.stream()]
        
        # Get schedule data
        schedules_ref = db.collection("users").document(user_id).collection("schedules")
        schedules = [doc.to_dict() for doc in schedules_ref.stream()]
        
        # Get nutrition data (today)
        today_date = datetime.now().strftime("%Y-%m-%d")
        nutrition_ref = db.collection("users").document(user_id).collection("nutrition").document("dailyCalories").collection(today_date).document("total")
        nutrition_doc = nutrition_ref.get()
        nutrition_data = nutrition_doc.to_dict() if nutrition_doc.exists else {"totalCalories": 0}
        
        # Get session timers
        timers_ref = db.collection("users").document(user_id).collection("sessionTimers")
        timers = [doc.to_dict() for doc in timers_ref.stream()]
        
        summary = {
            "user_id": user_id,
            "exercises": {
                "total_sessions": len(exercises),
                "recent_exercises": exercises[-5:] if exercises else [],
                "average_effectiveness": sum(ex.get("effectivenessScore", 0) for ex in exercises if ex.get("effectivenessScore")) / len(exercises) if exercises else 0
            },
            "schedules": {
                "total_events": len(schedules),
                "upcoming_events": [s for s in schedules if s.get("scheduledTime") and s["scheduledTime"] > datetime.now()],
                "wellness_events": [s for s in schedules if s.get("category") == "wellness"]
            },
            "nutrition": {
                "today_calories": nutrition_data.get("totalCalories", 0),
                "meals_today": len(nutrition_data.get("meals", []))
            },
            "session_timers": {
                "total_sessions": len(timers),
                "recent_sessions": timers[-3:] if timers else []
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Failed to get user Phase 1 summary: {e}")
        return {
            "error": str(e),
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        } 