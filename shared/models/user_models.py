from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class MentalHealthCondition(Enum):
    """Enumeration of mental health conditions"""
    DEPRESSION = "depression"
    ANXIETY = "anxiety"
    BIPOLAR = "bipolar"
    PTSD = "ptsd"
    OCD = "ocd"
    BORDERLINE_PD = "borderline_personality_disorder"
    ADHD = "adhd"
    EATING_DISORDER = "eating_disorder"
    SUBSTANCE_ABUSE = "substance_abuse"

class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRISIS = "crisis"

@dataclass
class UserProfile:
    """Comprehensive user profile for wellness platform"""
    user_id: str
    email: str
    name: str
    age: int
    created_at: datetime
    updated_at: datetime
    
    # Mental health profile
    mental_health_conditions: List[MentalHealthCondition] = field(default_factory=list)
    current_medications: List[str] = field(default_factory=list)
    therapeutic_goals: List[str] = field(default_factory=list)
    preferred_therapeutic_frameworks: List[str] = field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.LOW
    emergency_contacts: List[Dict[str, str]] = field(default_factory=list)
    
    # Physical health profile
    fitness_goals: List[str] = field(default_factory=list)
    physical_limitations: List[str] = field(default_factory=list)
    dietary_preferences: List[str] = field(default_factory=list)
    dietary_restrictions: List[str] = field(default_factory=list)
    
    # Preferences
    preferred_communication_mode: str = "text"  # text, voice, video
    timezone: str = "UTC"
    notification_preferences: Dict[str, bool] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user profile to dictionary for Google ADK communication"""
        return {
            'user_id': self.user_id,
            'email': self.email,
            'name': self.name,
            'age': self.age,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'mental_health_conditions': [condition.value for condition in self.mental_health_conditions],
            'current_medications': self.current_medications,
            'therapeutic_goals': self.therapeutic_goals,
            'preferred_therapeutic_frameworks': self.preferred_therapeutic_frameworks,
            'risk_level': self.risk_level.value,
            'emergency_contacts': self.emergency_contacts,
            'fitness_goals': self.fitness_goals,
            'physical_limitations': self.physical_limitations,
            'dietary_preferences': self.dietary_preferences,
            'dietary_restrictions': self.dietary_restrictions,
            'preferred_communication_mode': self.preferred_communication_mode,
            'timezone': self.timezone,
            'notification_preferences': self.notification_preferences
        }

@dataclass
class MentalHealthState:
    """Current mental health state representation"""
    user_id: str
    timestamp: datetime
    mood_score: float  # -1.0 to 1.0
    anxiety_level: float  # 0.0 to 1.0
    depression_level: float  # 0.0 to 1.0
    stress_level: float  # 0.0 to 1.0
    energy_level: float  # 0.0 to 1.0
    sleep_quality: float  # 0.0 to 1.0
    
    # Contextual information
    triggers: List[str] = field(default_factory=list)
    coping_mechanisms_used: List[str] = field(default_factory=list)
    life_events: List[str] = field(default_factory=list)
    
    # Assessment metadata
    assessment_method: str = "journal"  # journal, therapy, self_report
    confidence_score: float = 0.8
    
    def to_adk_message(self) -> Dict[str, Any]:
        """Convert to Google ADK agent communication format"""
        return {
            'message_type': 'mental_health_state_update',
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat(),
            'state_data': {
                'mood_score': self.mood_score,
                'anxiety_level': self.anxiety_level,
                'depression_level': self.depression_level,
                'stress_level': self.stress_level,
                'energy_level': self.energy_level,
                'sleep_quality': self.sleep_quality,
                'triggers': self.triggers,
                'coping_mechanisms_used': self.coping_mechanisms_used,
                'life_events': self.life_events,
                'assessment_method': self.assessment_method,
                'confidence_score': self.confidence_score
            }
        }
