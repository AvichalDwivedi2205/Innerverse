"""Common tool result structures for consistent agent responses.

This module provides structured response classes for all agent tools to ensure
consistent, programmatic responses that can be properly processed by agents.
"""

from pydantic import BaseModel
from typing import Dict, Any, List, Optional, Union
from datetime import datetime


class ToolResult(BaseModel):
    """Base class for all tool results with consistent structure."""
    
    success: bool
    data: Dict[str, Any]
    message: str
    next_suggested_actions: List[str] = []
    error_details: Optional[str] = None
    timestamp: datetime = datetime.now()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class JournalingToolResult(ToolResult):
    """Specific result class for journaling agent tools."""
    
    journal_id: Optional[str] = None
    embedding_id: Optional[str] = None
    
    @classmethod
    def success_result(
        cls, 
        data: Dict[str, Any], 
        message: str, 
        next_actions: List[str] = None,
        journal_id: str = None,
        embedding_id: str = None
    ):
        return cls(
            success=True,
            data=data,
            message=message,
            next_suggested_actions=next_actions or [],
            journal_id=journal_id,
            embedding_id=embedding_id
        )
    
    @classmethod
    def error_result(
        cls, 
        message: str, 
        error_details: str = None,
        next_actions: List[str] = None
    ):
        return cls(
            success=False,
            data={},
            message=message,
            error_details=error_details,
            next_suggested_actions=next_actions or ["retry_operation"]
        )


class TherapyToolResult(ToolResult):
    """Specific result class for therapy agent tools."""
    
    session_id: Optional[str] = None
    embedding_id: Optional[str] = None
    
    @classmethod
    def success_result(
        cls, 
        data: Dict[str, Any], 
        message: str, 
        next_actions: List[str] = None,
        session_id: str = None,
        embedding_id: str = None
    ):
        return cls(
            success=True,
            data=data,
            message=message,
            next_suggested_actions=next_actions or [],
            session_id=session_id,
            embedding_id=embedding_id
        )
    
    @classmethod
    def error_result(
        cls, 
        message: str, 
        error_details: str = None,
        next_actions: List[str] = None
    ):
        return cls(
            success=False,
            data={},
            message=message,
            error_details=error_details,
            next_suggested_actions=next_actions or ["retry_operation"]
        )


class OrchestratorToolResult(ToolResult):
    """Specific result class for mental orchestrator agent tools."""
    
    mind_map_version: Optional[int] = None
    clusters_count: Optional[int] = None
    
    @classmethod
    def success_result(
        cls, 
        data: Dict[str, Any], 
        message: str, 
        next_actions: List[str] = None,
        mind_map_version: int = None,
        clusters_count: int = None
    ):
        return cls(
            success=True,
            data=data,
            message=message,
            next_suggested_actions=next_actions or [],
            mind_map_version=mind_map_version,
            clusters_count=clusters_count
        )
    
    @classmethod
    def error_result(
        cls, 
        message: str, 
        error_details: str = None,
        next_actions: List[str] = None
    ):
        return cls(
            success=False,
            data={},
            message=message,
            error_details=error_details,
            next_suggested_actions=next_actions or ["retry_operation"]
        )


class ExerciseToolResult(ToolResult):
    """Specific result class for exercise agent tools (10-minute sessions)."""
    
    exercise_id: Optional[str] = None
    exercise_type: Optional[str] = None  # CBT, mindfulness, gratitude, PMR
    duration_minutes: int = 10  # Fixed 10-minute duration
    effectiveness_score: Optional[int] = None  # 1-10 scale
    
    @classmethod
    def success_result(
        cls,
        data: Dict[str, Any],
        message: str,
        next_actions: List[str] = None,
        exercise_id: str = None,
        exercise_type: str = None,
        effectiveness_score: int = None
    ):
        return cls(
            success=True,
            data=data,
            message=message,
            next_suggested_actions=next_actions or [],
            exercise_id=exercise_id,
            exercise_type=exercise_type,
            effectiveness_score=effectiveness_score
        )
    
    @classmethod
    def error_result(
        cls,
        message: str,
        error_details: str = None,
        next_actions: List[str] = None
    ):
        return cls(
            success=False,
            data={},
            message=message,
            error_details=error_details,
            next_suggested_actions=next_actions or ["retry_exercise", "try_different_exercise"]
        )


class SchedulingToolResult(ToolResult):
    """Specific result class for scheduling agent tools (wellness + general life scheduling)."""
    
    google_event_id: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    schedule_category: Optional[str] = None  # wellness, personal, work, health
    frequency: Optional[str] = None  # daily, weekly, biweekly, monthly, once
    
    @classmethod
    def success_result(
        cls,
        data: Dict[str, Any],
        message: str,
        next_actions: List[str] = None,
        google_event_id: str = None,
        scheduled_time: datetime = None,
        schedule_category: str = None,
        frequency: str = None
    ):
        return cls(
            success=True,
            data=data,
            message=message,
            next_suggested_actions=next_actions or [],
            google_event_id=google_event_id,
            scheduled_time=scheduled_time,
            schedule_category=schedule_category,
            frequency=frequency
        )
    
    @classmethod
    def error_result(
        cls,
        message: str,
        error_details: str = None,
        next_actions: List[str] = None
    ):
        return cls(
            success=False,
            data={},
            message=message,
            error_details=error_details,
            next_suggested_actions=next_actions or ["retry_scheduling", "check_calendar_permissions"]
        )


class NutritionToolResult(ToolResult):
    """Specific result class for nutrition agent tools."""
    
    meal_plan_id: Optional[str] = None
    daily_calories: Optional[int] = None
    vision_analysis_confidence: Optional[float] = None  # 0.0-1.0
    food_items_detected: Optional[List[str]] = None
    
    @classmethod
    def success_result(
        cls,
        data: Dict[str, Any],
        message: str,
        next_actions: List[str] = None,
        meal_plan_id: str = None,
        daily_calories: int = None,
        vision_analysis_confidence: float = None,
        food_items_detected: List[str] = None
    ):
        return cls(
            success=True,
            data=data,
            message=message,
            next_suggested_actions=next_actions or [],
            meal_plan_id=meal_plan_id,
            daily_calories=daily_calories,
            vision_analysis_confidence=vision_analysis_confidence,
            food_items_detected=food_items_detected or []
        )
    
    @classmethod
    def error_result(
        cls,
        message: str,
        error_details: str = None,
        next_actions: List[str] = None
    ):
        return cls(
            success=False,
            data={},
            message=message,
            error_details=error_details,
            next_suggested_actions=next_actions or ["retry_analysis", "manual_calorie_entry"]
        )


class TimerToolResult(ToolResult):
    """Specific result class for session timing tools (final results only)."""
    
    session_id: Optional[str] = None
    session_type: Optional[str] = None  # therapy, exercise
    completed_phases: Optional[List[str]] = None
    total_duration: Optional[int] = None  # minutes
    phase_completion_data: Optional[Dict[str, Any]] = None
    
    @classmethod
    def success_result(
        cls,
        data: Dict[str, Any],
        message: str,
        next_actions: List[str] = None,
        session_id: str = None,
        session_type: str = None,
        completed_phases: List[str] = None,
        total_duration: int = None,
        phase_completion_data: Dict[str, Any] = None
    ):
        return cls(
            success=True,
            data=data,
            message=message,
            next_suggested_actions=next_actions or [],
            session_id=session_id,
            session_type=session_type,
            completed_phases=completed_phases or [],
            total_duration=total_duration,
            phase_completion_data=phase_completion_data or {}
        )
    
    @classmethod
    def error_result(
        cls,
        message: str,
        error_details: str = None,
        next_actions: List[str] = None
    ):
        return cls(
            success=False,
            data={},
            message=message,
            error_details=error_details,
            next_suggested_actions=next_actions or ["retry_timer_save", "manual_session_completion"]
        )


class CoordinationResult(BaseModel):
    """Result class for agent coordination operations."""
    
    success: bool
    coordinated_agents: List[str]
    results: Dict[str, Any]
    message: str
    errors: List[str] = []
    timestamp: datetime = datetime.now()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 