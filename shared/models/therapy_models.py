from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class TherapeuticFramework(Enum):
    """Therapeutic frameworks supported by the platform"""
    CBT = "cognitive_behavioral_therapy"
    DBT = "dialectical_behavior_therapy"
    ACT = "acceptance_commitment_therapy"
    MINDFULNESS = "mindfulness_based_therapy"
    PSYCHODYNAMIC = "psychodynamic_therapy"
    HUMANISTIC = "humanistic_therapy"

class SessionType(Enum):
    """Types of therapy sessions"""
    INDIVIDUAL = "individual"
    GROUP = "group"
    CRISIS = "crisis"
    ASSESSMENT = "assessment"
    FOLLOW_UP = "follow_up"

class SessionModality(Enum):
    """Session delivery modalities"""
    TEXT = "text"
    VOICE = "voice"
    VIDEO = "video"
    MIXED = "mixed"

@dataclass
class TherapySession:
    """Comprehensive therapy session model"""
    session_id: str
    user_id: str
    therapist_agent_id: str
    session_type: SessionType
    therapeutic_framework: TherapeuticFramework
    modality: SessionModality
    
    # Session timing
    scheduled_start: datetime
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    duration_minutes: int = 50
    
    # Session content
    session_goals: List[str] = field(default_factory=list)
    topics_discussed: List[str] = field(default_factory=list)
    interventions_used: List[str] = field(default_factory=list)
    homework_assigned: List[str] = field(default_factory=list)
    
    # Assessment and progress
    pre_session_mood: Optional[float] = None
    post_session_mood: Optional[float] = None
    progress_score: float = 0.0
    therapeutic_insights: List[str] = field(default_factory=list)
    
    # Session notes
    therapist_notes: str = ""
    user_feedback: str = ""
    session_summary: str = ""
    
    # Crisis and safety
    safety_assessment: Dict[str, Any] = field(default_factory=dict)
    crisis_indicators: List[str] = field(default_factory=list)
    safety_plan_updated: bool = False
    
    def to_adk_message(self) -> Dict[str, Any]:
        """Convert to Google ADK agent communication format"""
        return {
            'message_type': 'therapy_session_update',
            'session_id': self.session_id,
            'user_id': self.user_id,
            'session_data': {
                'session_type': self.session_type.value,
                'therapeutic_framework': self.therapeutic_framework.value,
                'modality': self.modality.value,
                'scheduled_start': self.scheduled_start.isoformat(),
                'actual_start': self.actual_start.isoformat() if self.actual_start else None,
                'actual_end': self.actual_end.isoformat() if self.actual_end else None,
                'duration_minutes': self.duration_minutes,
                'session_goals': self.session_goals,
                'topics_discussed': self.topics_discussed,
                'interventions_used': self.interventions_used,
                'homework_assigned': self.homework_assigned,
                'pre_session_mood': self.pre_session_mood,
                'post_session_mood': self.post_session_mood,
                'progress_score': self.progress_score,
                'therapeutic_insights': self.therapeutic_insights,
                'therapist_notes': self.therapist_notes,
                'user_feedback': self.user_feedback,
                'session_summary': self.session_summary,
                'safety_assessment': self.safety_assessment,
                'crisis_indicators': self.crisis_indicators,
                'safety_plan_updated': self.safety_plan_updated
            }
        }

@dataclass
class MentalExercise:
    """Mental health exercise recommendation model"""
    exercise_id: str
    name: str
    description: str
    therapeutic_framework: TherapeuticFramework
    difficulty_level: str  # beginner, intermediate, advanced
    estimated_duration_minutes: int
    
    # Exercise content
    instructions: List[str] = field(default_factory=list)
    guided_audio_url: Optional[str] = None
    guided_video_url: Optional[str] = None
    
    # Targeting and effectiveness
    target_conditions: List[str] = field(default_factory=list)
    target_symptoms: List[str] = field(default_factory=list)
    effectiveness_score: float = 0.0
    
    # User interaction
    completion_rate: float = 0.0
    average_user_rating: float = 0.0
    user_feedback: List[str] = field(default_factory=list)
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_adk_message(self) -> Dict[str, Any]:
        """Convert to Google ADK agent communication format"""
        return {
            'message_type': 'mental_exercise_recommendation',
            'exercise_id': self.exercise_id,
            'exercise_data': {
                'name': self.name,
                'description': self.description,
                'therapeutic_framework': self.therapeutic_framework.value,
                'difficulty_level': self.difficulty_level,
                'estimated_duration_minutes': self.estimated_duration_minutes,
                'instructions': self.instructions,
                'guided_audio_url': self.guided_audio_url,
                'guided_video_url': self.guided_video_url,
                'target_conditions': self.target_conditions,
                'target_symptoms': self.target_symptoms,
                'effectiveness_score': self.effectiveness_score,
                'completion_rate': self.completion_rate,
                'average_user_rating': self.average_user_rating,
                'tags': self.tags
            }
        }
