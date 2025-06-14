from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class FitnessGoal(Enum):
    """Fitness goal categories"""
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    STRENGTH = "strength"
    ENDURANCE = "endurance"
    FLEXIBILITY = "flexibility"
    MAINTENANCE = "maintenance"
    REHABILITATION = "rehabilitation"

class ExerciseCategory(Enum):
    """Exercise categories based on fitness research"""
    AEROBIC_SHORT = "aerobic_short"  # 10-15 min, 30-69% max capacity
    AEROBIC_LONG = "aerobic_long"    # 30min-4hr, 55-89% max capacity
    INCREMENTAL = "incremental"      # Progressive workload increase
    STATIC = "static"               # Isometric contractions
    DYNAMIC_RESISTANCE = "dynamic_resistance"  # Weight lifting
    VERY_HIGH_INTENSITY = "very_high_intensity"  # Seconds to 3 minutes

@dataclass
class WorkoutPlan:
    """Workout plan model for fitness agent"""
    plan_id: str
    user_id: str
    name: str
    description: str
    fitness_goals: List[FitnessGoal]
    
    # Plan structure
    duration_weeks: int
    sessions_per_week: int
    session_duration_minutes: int
    
    # Exercise composition
    exercises: List[Dict[str, Any]] = field(default_factory=list)
    exercise_categories: List[ExerciseCategory] = field(default_factory=list)
    
    # Adaptations
    physical_limitations: List[str] = field(default_factory=list)
    equipment_required: List[str] = field(default_factory=list)
    modifications: List[str] = field(default_factory=list)
    
    # Progress tracking
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    completion_rate: float = 0.0
    
    def to_adk_message(self) -> Dict[str, Any]:
        """Convert to Google ADK agent communication format"""
        return {
            'message_type': 'workout_plan_update',
            'plan_id': self.plan_id,
            'user_id': self.user_id,
            'plan_data': {
                'name': self.name,
                'description': self.description,
                'fitness_goals': [goal.value for goal in self.fitness_goals],
                'duration_weeks': self.duration_weeks,
                'sessions_per_week': self.sessions_per_week,
                'session_duration_minutes': self.session_duration_minutes,
                'exercises': self.exercises,
                'exercise_categories': [cat.value for cat in self.exercise_categories],
                'physical_limitations': self.physical_limitations,
                'equipment_required': self.equipment_required,
                'modifications': self.modifications,
                'completion_rate': self.completion_rate,
                'created_at': self.created_at.isoformat(),
                'last_updated': self.last_updated.isoformat()
            }
        }

@dataclass
class NutritionPlan:
    """Nutrition plan model for nutrition agent"""
    plan_id: str
    user_id: str
    name: str
    description: str
    
    # Nutritional goals
    calorie_target: int
    macronutrient_ratios: Dict[str, float] = field(default_factory=dict)  # protein, carbs, fat
    
    # Meal structure
    meals_per_day: int = 3
    snacks_per_day: int = 2
    meal_plans: List[Dict[str, Any]] = field(default_factory=list)
    
    # Dietary considerations
    dietary_preferences: List[str] = field(default_factory=list)
    dietary_restrictions: List[str] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)
    
    # Progress tracking
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    adherence_rate: float = 0.0
    
    def to_adk_message(self) -> Dict[str, Any]:
        """Convert to Google ADK agent communication format"""
        return {
            'message_type': 'nutrition_plan_update',
            'plan_id': self.plan_id,
            'user_id': self.user_id,
            'plan_data': {
                'name': self.name,
                'description': self.description,
                'calorie_target': self.calorie_target,
                'macronutrient_ratios': self.macronutrient_ratios,
                'meals_per_day': self.meals_per_day,
                'snacks_per_day': self.snacks_per_day,
                'meal_plans': self.meal_plans,
                'dietary_preferences': self.dietary_preferences,
                'dietary_restrictions': self.dietary_restrictions,
                'allergies': self.allergies,
                'adherence_rate': self.adherence_rate,
                'created_at': self.created_at.isoformat(),
                'last_updated': self.last_updated.isoformat()
            }
        }
