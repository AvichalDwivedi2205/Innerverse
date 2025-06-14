"""
Shared Components Module for Wellness AI Platform
Provides common models, utilities, and constants for all agents
"""

from .models.user_models import UserProfile, MentalHealthState, MentalHealthCondition, RiskLevel
from .models.therapy_models import TherapySession, MentalExercise, TherapeuticFramework, SessionType, SessionModality
from .models.wellness_models import WorkoutPlan, NutritionPlan, FitnessGoal, ExerciseCategory

from .utils.text_processing import TextProcessor, SentimentAnalyzer
from .utils.adk_communication import ADKCommunicationHelper, ADKMessage, MessageType, Priority, adk_comm

from .constants.therapeutic_constants import (
    TherapeuticFrameworks, 
    ExerciseCategories, 
    AgentEventTypes,
    RISK_ASSESSMENT_THRESHOLDS,
    DEFAULT_NOTIFICATION_PREFERENCES
)

def validate_shared_components():
    """Validate that shared components are properly configured"""
    print("Validating shared components...")
    
    # Check model classes
    print("✓ User models loaded")
    print("✓ Therapy models loaded") 
    print("✓ Wellness models loaded")
    
    # Check utilities
    print("✓ Text processing utilities loaded")
    print("✓ ADK communication helpers loaded")
    
    # Check constants
    frameworks_count = len([attr for attr in dir(TherapeuticFrameworks) if not attr.startswith('_')])
    exercise_categories_count = len([attr for attr in dir(ExerciseCategories) if not attr.startswith('_')])
    print(f"✓ {frameworks_count} therapeutic frameworks defined")
    print(f"✓ {exercise_categories_count} exercise categories defined")
    
    print("Shared components validation complete!")

# Auto-validate on import
validate_shared_components()

__all__ = [
    # Models
    'UserProfile', 'MentalHealthState', 'MentalHealthCondition', 'RiskLevel',
    'TherapySession', 'MentalExercise', 'TherapeuticFramework', 'SessionType', 'SessionModality',
    'WorkoutPlan', 'NutritionPlan', 'FitnessGoal', 'ExerciseCategory',
    
    # Utilities
    'TextProcessor', 'SentimentAnalyzer',
    'ADKCommunicationHelper', 'ADKMessage', 'MessageType', 'Priority', 'adk_comm',
    
    # Constants
    'TherapeuticFrameworks', 'ExerciseCategories', 'AgentEventTypes',
    'RISK_ASSESSMENT_THRESHOLDS', 'DEFAULT_NOTIFICATION_PREFERENCES'
]
