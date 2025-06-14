from typing import Dict, List, Any

class TherapeuticFrameworks:
    """Constants for therapeutic frameworks based on research"""
    
    CBT = {
        'name': 'Cognitive Behavioral Therapy',
        'description': 'Focuses on identifying and changing negative thought patterns and behaviors',
        'core_principles': [
            'Thoughts, feelings, and behaviors are interconnected',
            'Changing thoughts can change feelings and behaviors',
            'Present-focused problem-solving approach',
            'Collaborative relationship between therapist and client'
        ],
        'techniques': [
            'Cognitive restructuring',
            'Behavioral activation',
            'Exposure therapy',
            'Thought challenging',
            'Activity scheduling',
            'Homework assignments'
        ],
        'target_conditions': [
            'depression', 'anxiety', 'ptsd', 'ocd', 'panic_disorder'
        ]
    }
    
    DBT = {
        'name': 'Dialectical Behavior Therapy',
        'description': 'Combines CBT techniques with mindfulness and distress tolerance skills',
        'core_principles': [
            'Mindfulness',
            'Distress tolerance', 
            'Emotion regulation',
            'Interpersonal effectiveness'
        ],
        'techniques': [
            'Mindfulness meditation',
            'Distress tolerance skills',
            'Emotion regulation strategies',
            'Interpersonal skills training',
            'Crisis survival strategies'
        ],
        'target_conditions': [
            'borderline_personality_disorder', 'depression', 'eating_disorders', 
            'bipolar_disorder', 'ptsd', 'substance_abuse'
        ]
    }
    
    ACT = {
        'name': 'Acceptance and Commitment Therapy',
        'description': 'Focuses on psychological flexibility and values-based living',
        'core_principles': [
            'Cognitive defusion',
            'Acceptance',
            'Contact with present moment',
            'Observing self',
            'Values clarification',
            'Committed action'
        ],
        'techniques': [
            'Mindfulness exercises',
            'Values clarification',
            'Defusion techniques',
            'Acceptance strategies',
            'Behavioral commitment'
        ],
        'target_conditions': [
            'anxiety_disorders', 'depression', 'chronic_pain', 'addiction'
        ]
    }

class ExerciseCategories:
    """Exercise categories based on fitness research"""
    
    AEROBIC_SHORT = {
        'name': 'Short Aerobic Exercise',
        'description': 'Continuous rhythmical exercise using aerobic energy',
        'duration_minutes': '10-15',
        'intensity': '30-69% of maximal work capacity',
        'examples': ['brisk walking', 'light jogging', 'cycling', 'swimming']
    }
    
    AEROBIC_LONG = {
        'name': 'Long Aerobic Exercise', 
        'description': 'Extended continuous rhythmical exercise',
        'duration_minutes': '30-240',
        'intensity': '55-89% of maximum capacity',
        'examples': ['distance running', 'cycling', 'rowing', 'hiking']
    }
    
    INCREMENTAL = {
        'name': 'Incremental Exercise',
        'description': 'Progressive workload increase to maximum capacity',
        'duration_minutes': '5-30',
        'intensity': 'Light to 100% maximum',
        'examples': ['interval training', 'progressive strength training']
    }
    
    STATIC = {
        'name': 'Static Exercise',
        'description': 'Isometric muscle contractions without movement',
        'duration_minutes': '2-10',
        'intensity': 'Percentage of maximal voluntary contraction',
        'examples': ['planks', 'wall sits', 'isometric holds']
    }
    
    DYNAMIC_RESISTANCE = {
        'name': 'Dynamic Resistance Exercise',
        'description': 'Muscle contractions that overcome resistance with movement',
        'duration': 'Repetition-based, not time-based',
        'intensity': 'Percentage of 1-RM',
        'examples': ['weight lifting', 'resistance bands', 'bodyweight exercises']
    }
    
    VERY_HIGH_INTENSITY = {
        'name': 'Very High Intensity Exercise',
        'description': 'High power anaerobic exercise, often supra-maximal',
        'duration_minutes': '0.1-3',
        'intensity': 'Maximum to supra-maximal',
        'examples': ['sprints', 'HIIT', 'plyometrics']
    }

class AgentEventTypes:
    """Google ADK agent communication event types"""
    
    # Mental health events
    JOURNAL_ENTRY_PROCESSED = "journal_entry_processed"
    CRISIS_DETECTED = "crisis_detected"
    THERAPY_SESSION_COMPLETED = "therapy_session_completed"
    MENTAL_EXERCISE_COMPLETED = "mental_exercise_completed"
    PROGRESS_MILESTONE_REACHED = "progress_milestone_reached"
    
    # Physical health events
    WORKOUT_COMPLETED = "workout_completed"
    NUTRITION_PLAN_UPDATED = "nutrition_plan_updated"
    CALORIE_GOAL_REACHED = "calorie_goal_reached"
    
    # Scheduling events
    APPOINTMENT_SCHEDULED = "appointment_scheduled"
    REMINDER_SENT = "reminder_sent"
    CALENDAR_UPDATED = "calendar_updated"
    
    # System events
    AGENT_COORDINATION_REQUEST = "agent_coordination_request"
    DATA_SYNC_COMPLETED = "data_sync_completed"
    USER_PROFILE_UPDATED = "user_profile_updated"

# Risk assessment constants
RISK_ASSESSMENT_THRESHOLDS = {
    'crisis_keywords_threshold': 1,
    'mood_score_crisis': -0.8,
    'anxiety_level_high': 0.8,
    'depression_level_high': 0.8,
    'consecutive_negative_days': 7
}

# Notification preferences
DEFAULT_NOTIFICATION_PREFERENCES = {
    'journal_reminders': True,
    'therapy_session_reminders': True,
    'exercise_reminders': True,
    'progress_reports': True,
    'crisis_alerts': True,
    'workout_reminders': True,
    'meal_reminders': False
}
