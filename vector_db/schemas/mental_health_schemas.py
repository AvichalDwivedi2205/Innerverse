from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class VectorType(Enum):
    """Enumeration of vector types in the mental health system"""
    USER_MENTAL_PROFILE = "user_mental_profiles"
    JOURNAL_ENTRY = "journal_entries"
    THERAPY_SESSION = "therapy_sessions"
    MENTAL_EXERCISE = "mental_exercises"
    PROGRESS_TRACKING = "progress_tracking"

@dataclass
class BaseVectorSchema:
    """Base schema for all vector entries"""
    id: str
    user_id: str
    vector: List[float]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UserMentalProfileVector(BaseVectorSchema):
    """768-dimensional vector schema for comprehensive mental health profiles"""
    
    # Mental health profile specific fields
    conditions: List[str] = field(default_factory=list)
    severity_scores: Dict[str, float] = field(default_factory=dict)
    therapeutic_goals: List[str] = field(default_factory=list)
    preferred_frameworks: List[str] = field(default_factory=list)
    risk_level: str = "low"
    last_assessment_date: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate 768-dimensional vector"""
        if len(self.vector) != 768:
            raise ValueError(f"UserMentalProfileVector requires 768 dimensions, got {len(self.vector)}")
    
    @classmethod
    def get_pinecone_index_name(cls) -> str:
        return "user-mental-profiles"

@dataclass
class JournalEntryVector(BaseVectorSchema):
    """768-dimensional vector schema for daily emotional states and life events"""
    
    # Journal entry specific fields
    mood_score: float = 0.0
    emotional_intensity: float = 0.0
    triggers: List[str] = field(default_factory=list)
    coping_mechanisms: List[str] = field(default_factory=list)
    entry_type: str = "daily"  # daily, crisis, reflection
    word_count: int = 0
    sentiment_score: float = 0.0
    
    def __post_init__(self):
        """Validate 768-dimensional vector"""
        if len(self.vector) != 768:
            raise ValueError(f"JournalEntryVector requires 768 dimensions, got {len(self.vector)}")
    
    @classmethod
    def get_pinecone_index_name(cls) -> str:
        return "journal-entries"

@dataclass
class TherapySessionVector(BaseVectorSchema):
    """768-dimensional vector schema for therapeutic insights and progress"""
    
    # Therapy session specific fields
    session_type: str = "individual"  # individual, group, crisis
    therapeutic_framework: str = "CBT"  # CBT, DBT, ACT, mindfulness
    progress_score: float = 0.0
    insights: List[str] = field(default_factory=list)
    homework_assigned: List[str] = field(default_factory=list)
    therapist_notes: str = ""
    session_duration: int = 50  # minutes
    
    def __post_init__(self):
        """Validate 768-dimensional vector"""
        if len(self.vector) != 768:
            raise ValueError(f"TherapySessionVector requires 768 dimensions, got {len(self.vector)}")
    
    @classmethod
    def get_pinecone_index_name(cls) -> str:
        return "therapy-sessions"

@dataclass
class MentalExerciseVector(BaseVectorSchema):
    """384-dimensional vector schema for exercise recommendations and effectiveness"""
    
    # Mental exercise specific fields
    exercise_type: str = "CBT"  # CBT, mindfulness, emotional_regulation, behavioral_activation
    difficulty_level: str = "beginner"  # beginner, intermediate, advanced
    estimated_duration: int = 10  # minutes
    effectiveness_score: float = 0.0
    completion_rate: float = 0.0
    user_rating: float = 0.0
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate 384-dimensional vector"""
        if len(self.vector) != 384:
            raise ValueError(f"MentalExerciseVector requires 384 dimensions, got {len(self.vector)}")
    
    @classmethod
    def get_pinecone_index_name(cls) -> str:
        return "mental-exercises"

@dataclass
class ProgressTrackingVector(BaseVectorSchema):
    """384-dimensional vector schema for longitudinal health monitoring"""
    
    # Progress tracking specific fields
    tracking_period: str = "weekly"  # daily, weekly, monthly
    overall_wellness_score: float = 0.0
    mood_trend: str = "stable"  # improving, stable, declining
    therapy_engagement: float = 0.0
    exercise_completion: float = 0.0
    journal_consistency: float = 0.0
    crisis_incidents: int = 0
    
    def __post_init__(self):
        """Validate 384-dimensional vector"""
        if len(self.vector) != 384:
            raise ValueError(f"ProgressTrackingVector requires 384 dimensions, got {len(self.vector)}")
    
    @classmethod
    def get_pinecone_index_name(cls) -> str:
        return "progress-tracking"

class VectorSchemaFactory:
    """Factory class for creating appropriate vector schemas"""
    
    SCHEMA_MAPPING = {
        VectorType.USER_MENTAL_PROFILE: UserMentalProfileVector,
        VectorType.JOURNAL_ENTRY: JournalEntryVector,
        VectorType.THERAPY_SESSION: TherapySessionVector,
        VectorType.MENTAL_EXERCISE: MentalExerciseVector,
        VectorType.PROGRESS_TRACKING: ProgressTrackingVector
    }
    
    @classmethod
    def create_schema(cls, vector_type: VectorType, **kwargs) -> BaseVectorSchema:
        """Create appropriate vector schema based on type"""
        schema_class = cls.SCHEMA_MAPPING.get(vector_type)
        if not schema_class:
            raise ValueError(f"Unknown vector type: {vector_type}")
        
        return schema_class(**kwargs)
    
    @classmethod
    def get_expected_dimensions(cls, vector_type: VectorType) -> int:
        """Get expected dimensions for vector type"""
        dimension_mapping = {
            VectorType.USER_MENTAL_PROFILE: 768,
            VectorType.JOURNAL_ENTRY: 768,
            VectorType.THERAPY_SESSION: 768,
            VectorType.MENTAL_EXERCISE: 384,
            VectorType.PROGRESS_TRACKING: 384
        }
        return dimension_mapping.get(vector_type, 768)
