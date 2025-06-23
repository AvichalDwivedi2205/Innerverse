"""Enhanced Session Timer for Innerverse - Phase 2 Implementation.

This module provides real-time session timing with exact phase transitions, background monitoring,
and hybrid local/Firestore synchronization. Supports both 60-minute and 30-minute therapy sessions
with precise phase timing, plus 10-minute exercise sessions.
"""

import time
import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from .tool_results import TimerToolResult


class SessionType(Enum):
    """Enum for different session types."""
    THERAPY = "therapy"
    EXERCISE = "exercise"


class TherapyPhase(Enum):
    """Enum for therapy session phases with exact timing."""
    PRE_SESSION = "pre_session"      # 2 min (1 min for short): Context review
    OPENING = "opening"              # 6 min (3 min for short): Check-in, mood assessment  
    WORKING = "working"              # 40 min (20 min for short): Main therapeutic work
    INTEGRATION = "integration"      # 6 min (3 min for short): Empowerment focus
    CLOSING = "closing"              # 6 min (3 min for short): Summary, homework


class ExercisePhase(Enum):
    """Enum for exercise session phases."""
    PREPARATION = "preparation"      # 2-3 min: Setup, breathing
    INSTRUCTION = "instruction"      # 2-3 min: Exercise explanation
    PRACTICE = "practice"           # 5-10 min: Main exercise
    REFLECTION = "reflection"       # 2-5 min: Integration, insights


# Fixed Session Configurations with Exact Timing
THERAPY_PHASE_CONFIGS = {
    "standard_60": {
        TherapyPhase.PRE_SESSION: {"duration": 2, "description": "Context review and preparation"},
        TherapyPhase.OPENING: {"duration": 6, "description": "Check-in, mood assessment, safety screening"},
        TherapyPhase.WORKING: {"duration": 40, "description": "Main therapeutic work and exploration"},
        TherapyPhase.INTEGRATION: {"duration": 6, "description": "Empowerment insights and integration"},
        TherapyPhase.CLOSING: {"duration": 6, "description": "Summary, homework, and scheduling"}
        # Total: 60 minutes
    },
    "short_30": {
        TherapyPhase.PRE_SESSION: {"duration": 1, "description": "Quick context review"},
        TherapyPhase.OPENING: {"duration": 3, "description": "Brief check-in and assessment"},
        TherapyPhase.WORKING: {"duration": 20, "description": "Focused therapeutic work"},
        TherapyPhase.INTEGRATION: {"duration": 3, "description": "Key insights and empowerment"},
        TherapyPhase.CLOSING: {"duration": 3, "description": "Quick summary and next steps"}
        # Total: 30 minutes
    }
}

SESSION_CONFIGURATIONS = {
    "standard_60": {
        "total_duration": 3600,  # 60 minutes in seconds
        "phases": {
            "pre_session": 120,   # 2 minutes
            "opening": 360,       # 6 minutes
            "working": 2400,      # 40 minutes
            "integration": 360,   # 6 minutes
            "closing": 360        # 6 minutes
        }
    },
    "short_30": {
        "total_duration": 1800,  # 30 minutes in seconds
        "phases": {
            "pre_session": 60,    # 1 minute
            "opening": 180,       # 3 minutes
            "working": 1200,      # 20 minutes
            "integration": 180,   # 3 minutes
            "closing": 180        # 3 minutes
        }
    }
}


class PhaseStatus(Enum):
    """Enum for phase completion status."""
    PENDING = "pending"
    ACTIVE = "active" 
    COMPLETED = "completed"
    SKIPPED = "skipped"


@dataclass
class SessionPhase:
    """Represents a single phase in a session with exact timing."""
    name: str
    duration_minutes: int
    duration_seconds: int
    description: str
    status: PhaseStatus = PhaseStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    actual_duration: Optional[float] = None
    notes: Optional[str] = None
    remaining_seconds: int = 0


@dataclass
class SessionData:
    """Complete session data structure with enhanced phase tracking."""
    session_id: str
    session_type: SessionType
    therapy_session_type: Optional[str]  # "standard_60" or "short_30"
    start_time: float
    total_duration_minutes: int
    total_duration_seconds: int
    phases: List[SessionPhase]
    current_phase_index: int = 0
    current_phase: Optional[str] = None
    is_active: bool = False
    is_completed: bool = False
    end_time: Optional[float] = None
    actual_total_duration: Optional[float] = None
    completion_percentage: float = 0.0
    user_notes: Optional[str] = None
    phase_history: List[Dict] = None


class TherapyPhaseCallbacks:
    """Phase-specific callbacks with fixed timing for therapy sessions."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def on_pre_session_start(self, session_data: SessionData):
        """2 min (or 1 min for short): Load context, prepare materials."""
        duration = 2 if session_data.therapy_session_type == "standard_60" else 1
        self.logger.info(f"PRE-SESSION phase started - Duration: {duration} minutes")
        
    async def on_opening_start(self, session_data: SessionData):
        """6 min (or 3 min for short): Mood assessment, check-in."""
        duration = 6 if session_data.therapy_session_type == "standard_60" else 3
        self.logger.info(f"OPENING phase started - Duration: {duration} minutes")
        
    async def on_working_start(self, session_data: SessionData):
        """40 min (or 20 min for short): Main therapeutic work."""
        duration = 40 if session_data.therapy_session_type == "standard_60" else 20
        self.logger.info(f"WORKING phase started - Duration: {duration} minutes")
        
    async def on_integration_start(self, session_data: SessionData):
        """6 min (or 3 min for short): Empowerment insights, reflection."""
        duration = 6 if session_data.therapy_session_type == "standard_60" else 3
        self.logger.info(f"INTEGRATION phase started - Duration: {duration} minutes")
        
    async def on_closing_start(self, session_data: SessionData):
        """6 min (or 3 min for short): Summary, homework, scheduling."""
        duration = 6 if session_data.therapy_session_type == "standard_60" else 3
        self.logger.info(f"CLOSING phase started - Duration: {duration} minutes")


class EnhancedSessionTimer:
    """
    Enhanced hybrid session timer with exact phase timing and background monitoring.
    Supports both 60-minute and 30-minute therapy sessions with precise transitions.
    """
    
    def __init__(self, user_id: str, session_type: SessionType = SessionType.THERAPY, 
                 therapy_session_type: str = "standard_60", callback_fn: Optional[Callable] = None):
        """Initialize the enhanced session timer.
        
        Args:
            user_id: User identifier for Firestore storage
            session_type: Type of session (therapy or exercise)
            therapy_session_type: "standard_60" or "short_30" for therapy sessions
            callback_fn: Optional callback function for real-time updates
        """
        self.logger = logging.getLogger(__name__)
        self.user_id = user_id
        self.session_type = session_type
        self.therapy_session_type = therapy_session_type
        self.callback_fn = callback_fn
        
        # Enhanced timer features
        self.phase_callbacks = TherapyPhaseCallbacks()
        self.firebase_sync_interval = 30  # Sync every 30 seconds
        self.phase_transition_alerts = True
        self.background_task: Optional[asyncio.Task] = None
        
        # Initialize session data with exact timing
        self.session_data = self._create_session_data()
        
        # Timer state
        self._timer_task: Optional[asyncio.Task] = None
        self._update_interval = 1.0  # Update every second
        
        total = self.session_data.total_duration_minutes
        self.logger.info(f"Enhanced SessionTimer initialized: {session_type.value} "
                        f"({therapy_session_type if session_type == SessionType.THERAPY else 'exercise'}) - {total} minutes")
    
    def _create_session_data(self) -> SessionData:
        """Create session data with exact phase timing based on session type."""
        session_id = str(uuid.uuid4())
        
        if self.session_type == SessionType.THERAPY:
            # Use fixed timing configurations
            config = THERAPY_PHASE_CONFIGS.get(self.therapy_session_type, THERAPY_PHASE_CONFIGS["standard_60"])
            
            phases = []
            total_seconds = 0
            
            for therapy_phase, phase_config in config.items():
                duration_min = phase_config["duration"]
                duration_sec = duration_min * 60
                total_seconds += duration_sec
                
                phase = SessionPhase(
                    name=therapy_phase.value,
                    duration_minutes=duration_min,
                    duration_seconds=duration_sec,
                    description=phase_config["description"],
                    remaining_seconds=duration_sec
                )
                phases.append(phase)
            
            total_duration_min = total_seconds // 60
            
        elif self.session_type == SessionType.EXERCISE:
            phases = [
                SessionPhase(
                    name="exercise",
                    duration_minutes=10,
                    duration_seconds=600,
                    description="10-minute focused exercise session",
                    remaining_seconds=600
                )
            ]
            total_duration_min = 10
            total_seconds = 600
        
        return SessionData(
            session_id=session_id,
            session_type=self.session_type,
            therapy_session_type=self.therapy_session_type if self.session_type == SessionType.THERAPY else None,
            start_time=0,  # Will be set when session starts
            total_duration_minutes=total_duration_min,
            total_duration_seconds=total_seconds,
            phases=phases,
            phase_history=[]
        )
    
    async def start_session(self) -> TimerToolResult:
        """Start the session timer with enhanced timing features.
        
        Returns:
            TimerToolResult with session details
        """
        if self.session_data.is_active:
            return TimerToolResult(
                success=False,
                message="Session already active",
                session_id=self.session_data.session_id
            )
        
        # Set start time
        current_time = time.time()
        self.session_data.start_time = current_time
        self.session_data.is_active = True
        
        # Start first phase with exact timing
        if self.session_data.phases:
            first_phase = self.session_data.phases[0]
            first_phase.status = PhaseStatus.ACTIVE
            first_phase.start_time = current_time
            first_phase.remaining_seconds = first_phase.duration_seconds
            self.session_data.current_phase = first_phase.name
            
            # Trigger first phase callback
            if self.session_type == SessionType.THERAPY:
                callback_name = f"on_{first_phase.name}_start"
                if hasattr(self.phase_callbacks, callback_name):
                    callback = getattr(self.phase_callbacks, callback_name)
                    await callback(self.session_data)
        
        # Start the enhanced timer task with background monitoring
        self._timer_task = asyncio.create_task(self._timer_loop())
        
        session_type_display = self.therapy_session_type if self.session_type == SessionType.THERAPY else "exercise"
        self.logger.info(f"Enhanced session {self.session_data.session_id} started: {session_type_display}")
        
        return TimerToolResult(
            success=True,
            message=f"Session started: {session_type_display} ({self.session_data.total_duration_minutes} minutes)",
            session_id=self.session_data.session_id,
            data={
                "session_type": self.session_type.value,
                "therapy_session_type": self.therapy_session_type,
                "total_duration": self.session_data.total_duration_minutes,
                "current_phase": self.session_data.current_phase,
                "phase_duration": self.session_data.phases[0].duration_minutes,
                "phases": [
                    {
                        "name": p.name,
                        "duration": p.duration_minutes,
                        "description": p.description
                    } for p in self.session_data.phases
                ]
            }
        )
    
    async def choose_session_duration(self, preferences: Dict = None) -> TimerToolResult:
        """Present session duration options and recommendations."""
        return TimerToolResult(
            success=True,
            message="Session duration options available",
            session_id=None,
            data={
                "available_sessions": {
                    "standard_60": {
                        "duration": 60,
                        "phases": [
                            {"name": "pre_session", "duration": 2, "description": "Context review and preparation"},
                            {"name": "opening", "duration": 6, "description": "Check-in, mood assessment, safety screening"},
                            {"name": "working", "duration": 40, "description": "Main therapeutic work and exploration"},
                            {"name": "integration", "duration": 6, "description": "Empowerment insights and integration"},
                            {"name": "closing", "duration": 6, "description": "Summary, homework, and scheduling"}
                        ],
                        "recommended_for": "Full therapeutic work, complex issues, first sessions"
                    },
                    "short_30": {
                        "duration": 30,
                        "phases": [
                            {"name": "pre_session", "duration": 1, "description": "Quick context review"},
                            {"name": "opening", "duration": 3, "description": "Brief check-in and assessment"},
                            {"name": "working", "duration": 20, "description": "Focused therapeutic work"},
                            {"name": "integration", "duration": 3, "description": "Key insights and empowerment"},
                            {"name": "closing", "duration": 3, "description": "Quick summary and next steps"}
                        ],
                        "recommended_for": "Check-ins, follow-ups, busy schedules"
                    }
                },
                "user_preferences": preferences or {}
            }
        )
    
    async def get_session_timer_status(self) -> TimerToolResult:
        """Get real-time session progress with exact timing."""
        if not self.session_data.is_active and not self.session_data.is_completed:
            return TimerToolResult(
                success=False,
                message="No session active",
                session_id=self.session_data.session_id
            )
        
        current_time = time.time()
        total_elapsed = int(current_time - self.session_data.start_time) if self.session_data.start_time else 0
        
        current_phase_data = None
        if self.session_data.current_phase_index < len(self.session_data.phases):
            current_phase = self.session_data.phases[self.session_data.current_phase_index]
            current_phase_data = {
                "name": current_phase.name,
                "duration_minutes": current_phase.duration_minutes,
                "remaining_seconds": current_phase.remaining_seconds,
                "remaining_minutes": current_phase.remaining_seconds // 60,
                "progress_percentage": max(0, 100 - (current_phase.remaining_seconds / current_phase.duration_seconds * 100))
            }
        
        return TimerToolResult(
            success=True,
            message="Session status retrieved",
            session_id=self.session_data.session_id,
            data={
                "session_type": self.session_type.value,
                "therapy_session_type": self.therapy_session_type,
                "is_active": self.session_data.is_active,
                "is_completed": self.session_data.is_completed,
                "total_elapsed_seconds": total_elapsed,
                "total_elapsed_minutes": total_elapsed // 60,
                "total_duration_minutes": self.session_data.total_duration_minutes,
                "current_phase": current_phase_data,
                "phase_history": self.session_data.phase_history,
                "completion_percentage": (total_elapsed / self.session_data.total_duration_seconds * 100) if self.session_data.total_duration_seconds > 0 else 0
            }
        )
    
    async def transition_to_next_phase_manual(self, force: bool = False) -> TimerToolResult:
        """Manual phase transition (therapist override)."""
        if not self.session_data.is_active:
            return TimerToolResult(
                success=False,
                message="No active session",
                session_id=self.session_data.session_id
            )
        
        current_index = self.session_data.current_phase_index
        if current_index >= len(self.session_data.phases):
            return TimerToolResult(
                success=False,
                message="Session already completed",
                session_id=self.session_data.session_id
            )
        
        # Force transition
        await self._transition_to_next_phase()
        
        next_phase_name = None
        if self.session_data.current_phase_index < len(self.session_data.phases):
            next_phase_name = self.session_data.phases[self.session_data.current_phase_index].name
        
        return TimerToolResult(
            success=True,
            message=f"Transitioned to {'next phase' if next_phase_name else 'session completion'}: {next_phase_name or 'completed'}",
            session_id=self.session_data.session_id,
            data={
                "current_phase": next_phase_name,
                "phase_index": self.session_data.current_phase_index,
                "completed": self.session_data.is_completed
            }
        )
    
    async def _timer_loop(self):
        """Enhanced timer loop with exact phase timing and background monitoring."""
        try:
            while self.session_data.is_active and not self.session_data.is_completed:
                await asyncio.sleep(self._update_interval)
                
                current_time = time.time()
                elapsed_time = current_time - self.session_data.start_time
                
                # Update session progress with exact timing
                self._update_session_progress(current_time, elapsed_time)
                
                # Check for exact phase transitions
                await self._check_phase_transitions_exact(current_time)
                
                # Background Firebase sync every 30 seconds
                if int(elapsed_time) % self.firebase_sync_interval == 0:
                    await self._sync_with_firebase()
                
                # Send real-time updates if callback is provided
                if self.callback_fn:
                    await self._send_update()
                
                # Check if session should complete (exact timing)
                if elapsed_time >= self.session_data.total_duration_seconds:
                    await self.complete_session()
                    
        except asyncio.CancelledError:
            self.logger.info("Enhanced timer loop cancelled")
        except Exception as e:
            self.logger.error(f"Enhanced timer loop error: {e}")
    
    async def _check_phase_transitions_exact(self, current_time: float):
        """Check for automatic phase transitions at exact times."""
        current_phase = self.get_current_phase()
        if not current_phase or not current_phase.start_time:
            return
        
        # Calculate exact phase elapsed time
        phase_elapsed = current_time - current_phase.start_time
        phase_duration_seconds = current_phase.duration_seconds
        
        # Update remaining time
        current_phase.remaining_seconds = max(0, phase_duration_seconds - int(phase_elapsed))
        
        # Automatic transition at exact time
        if phase_elapsed >= phase_duration_seconds and current_phase.status == PhaseStatus.ACTIVE:
            await self._transition_to_next_phase()
    
    async def _transition_to_next_phase(self):
        """Transition to the next phase with exact timing."""
        current_phase = self.get_current_phase()
        if not current_phase:
            return
        
        current_time = time.time()
        
        # Complete current phase
        current_phase.end_time = current_time
        current_phase.actual_duration = current_time - current_phase.start_time
        current_phase.status = PhaseStatus.COMPLETED
        current_phase.remaining_seconds = 0
        
        # Add to phase history
        self.session_data.phase_history.append({
            "phase": current_phase.name,
            "start_time": current_phase.start_time,
            "end_time": current_phase.end_time,
            "planned_duration": current_phase.duration_seconds,
            "actual_duration": current_phase.actual_duration,
            "status": "completed"
        })
        
        self.logger.info(f"Phase completed: {current_phase.name} "
                        f"(planned: {current_phase.duration_minutes}min, "
                        f"actual: {current_phase.actual_duration/60:.1f}min)")
        
        # Move to next phase
        self.session_data.current_phase_index += 1
        
        if self.session_data.current_phase_index < len(self.session_data.phases):
            # Start next phase
            next_phase = self.session_data.phases[self.session_data.current_phase_index]
            next_phase.status = PhaseStatus.ACTIVE
            next_phase.start_time = current_time
            next_phase.remaining_seconds = next_phase.duration_seconds
            self.session_data.current_phase = next_phase.name
            
            # Trigger phase callback
            if self.session_type == SessionType.THERAPY:
                callback_name = f"on_{next_phase.name}_start"
                if hasattr(self.phase_callbacks, callback_name):
                    callback = getattr(self.phase_callbacks, callback_name)
                    await callback(self.session_data)
            
            self.logger.info(f"Phase started: {next_phase.name} ({next_phase.duration_minutes} minutes)")
        else:
            # All phases complete
            await self.complete_session()
    
    async def _sync_with_firebase(self, final: bool = False):
        """Sync session state with Firebase (background monitoring)."""
        try:
            current_time = time.time()
            sync_data = {
                "sessionId": self.session_data.session_id,
                "sessionType": self.session_type.value,
                "therapySessionType": self.therapy_session_type,
                "currentPhase": self.session_data.current_phase,
                "currentPhaseIndex": self.session_data.current_phase_index,
                "totalElapsed": int(current_time - self.session_data.start_time) if self.session_data.start_time else 0,
                "phaseHistory": self.session_data.phase_history,
                "isActive": self.session_data.is_active,
                "isCompleted": self.session_data.is_completed,
                "syncType": "final" if final else "periodic",
                "timestamp": current_time
            }
            
            # Add current phase remaining time
            current_phase = self.get_current_phase()
            if current_phase:
                sync_data["currentPhaseRemaining"] = current_phase.remaining_seconds
            
            self.logger.debug(f"Firebase sync {'(FINAL)' if final else ''}: "
                             f"{sync_data['totalElapsed']}s elapsed, "
                             f"phase: {sync_data['currentPhase']}")
            
            # TODO: Replace with actual Firestore implementation
            # await firestore_client.collection('users').document(self.user_id)\
            #     .collection('sessionTimers').document(self.session_data.session_id).set(sync_data)
            
        except Exception as e:
            self.logger.error(f"Firebase sync error: {e}")
    
    def _update_session_progress(self, current_time: float, elapsed_time: float):
        """Update session progress and completion percentage."""
        total_seconds = self.session_data.total_duration_minutes * 60
        self.session_data.completion_percentage = min(100.0, (elapsed_time / total_seconds) * 100)
        
        # Update current phase progress
        current_phase = self.get_current_phase()
        if current_phase and current_phase.start_time:
            phase_elapsed = current_time - current_phase.start_time
            phase_duration_seconds = current_phase.duration_minutes * 60
            
            # Update phase actual duration
            current_phase.actual_duration = phase_elapsed
    
    def _check_phase_transitions(self, current_time: float):
        """Check if it's time to transition to the next phase."""
        current_phase = self.get_current_phase()
        if not current_phase or not current_phase.start_time:
            return
        
        phase_elapsed = current_time - current_phase.start_time
        phase_duration_seconds = current_phase.duration_minutes * 60
        
        # Auto-transition if phase time is up (with 30-second buffer)
        if phase_elapsed >= (phase_duration_seconds + 30):
            asyncio.create_task(self.next_phase())
    
    async def next_phase(self) -> Dict[str, Any]:
        """Transition to the next phase.
        
        Returns:
            Dictionary with phase transition information
        """
        if not self.session_data.is_active:
            return {"error": "Session is not active"}
        
        current_phase = self.get_current_phase()
        if current_phase:
            # Complete current phase
            current_time = time.time()
            current_phase.status = PhaseStatus.COMPLETED
            current_phase.end_time = current_time
            if current_phase.start_time:
                current_phase.actual_duration = current_time - current_phase.start_time
        
        # Move to next phase
        if self.session_data.current_phase_index < len(self.session_data.phases) - 1:
            self.session_data.current_phase_index += 1
            next_phase = self.session_data.phases[self.session_data.current_phase_index]
            next_phase.status = PhaseStatus.ACTIVE
            next_phase.start_time = time.time()
            
            self.logger.info(f"Transitioned to phase: {next_phase.name}")
            return {
                "success": True,
                "current_phase": next_phase.name,
                "phase_index": self.session_data.current_phase_index,
                "description": next_phase.description
            }
        else:
            # All phases completed
            await self.complete_session()
            return {
                "success": True,
                "message": "All phases completed, session finished"
            }
    
    async def previous_phase(self) -> Dict[str, Any]:
        """Go back to the previous phase.
        
        Returns:
            Dictionary with phase transition information
        """
        if not self.session_data.is_active:
            return {"error": "Session is not active"}
        
        if self.session_data.current_phase_index > 0:
            # Reset current phase
            current_phase = self.get_current_phase()
            if current_phase:
                current_phase.status = PhaseStatus.PENDING
                current_phase.start_time = None
                current_phase.end_time = None
                current_phase.actual_duration = None
            
            # Move to previous phase
            self.session_data.current_phase_index -= 1
            prev_phase = self.session_data.phases[self.session_data.current_phase_index]
            prev_phase.status = PhaseStatus.ACTIVE
            prev_phase.start_time = time.time()
            
            self.logger.info(f"Moved back to phase: {prev_phase.name}")
            return {
                "success": True,
                "current_phase": prev_phase.name,
                "phase_index": self.session_data.current_phase_index,
                "description": prev_phase.description
            }
        else:
            return {"error": "Already at first phase"}
    
    async def pause_session(self) -> Dict[str, Any]:
        """Pause the session timer."""
        if not self.session_data.is_active:
            return {"error": "Session is not active"}
        
        self.session_data.is_active = False
        
        if self._timer_task:
            self._timer_task.cancel()
        
        self.logger.info(f"Session {self.session_data.session_id} paused")
        return {"success": True, "message": "Session paused"}
    
    async def resume_session(self) -> Dict[str, Any]:
        """Resume the paused session."""
        if self.session_data.is_active:
            return {"error": "Session is already active"}
        
        if self.session_data.is_completed:
            return {"error": "Session is already completed"}
        
        # Adjust start time to account for pause duration
        current_time = time.time()
        if self.session_data.start_time:
            # Calculate total elapsed time before pause
            phases_duration = sum(
                phase.actual_duration or 0 
                for phase in self.session_data.phases 
                if phase.status == PhaseStatus.COMPLETED
            )
            
            # Reset start time accounting for completed time
            self.session_data.start_time = current_time - phases_duration
        
        self.session_data.is_active = True
        
        # Resume current phase timing
        current_phase = self.get_current_phase()
        if current_phase and current_phase.status == PhaseStatus.ACTIVE:
            current_phase.start_time = current_time
        
        # Restart timer task
        self._timer_task = asyncio.create_task(self._timer_loop())
        
        self.logger.info(f"Session {self.session_data.session_id} resumed")
        return {"success": True, "message": "Session resumed"}
    
    async def complete_session(self, user_notes: Optional[str] = None) -> TimerToolResult:
        """Complete the session and store final results in Firestore.
        
        Args:
            user_notes: Optional notes from the user
            
        Returns:
            TimerToolResult with session completion data
        """
        current_time = time.time()
        
        # Complete current phase if active
        current_phase = self.get_current_phase()
        if current_phase and current_phase.status == PhaseStatus.ACTIVE:
            current_phase.status = PhaseStatus.COMPLETED
            current_phase.end_time = current_time
            if current_phase.start_time:
                current_phase.actual_duration = current_time - current_phase.start_time
        
        # Update session completion data
        self.session_data.is_active = False
        self.session_data.is_completed = True
        self.session_data.end_time = current_time
        self.session_data.user_notes = user_notes
        
        if self.session_data.start_time:
            self.session_data.actual_total_duration = current_time - self.session_data.start_time
        
        self.session_data.completion_percentage = 100.0
        
        # Cancel timer task
        if self._timer_task:
            self._timer_task.cancel()
        
        # Store final results in Firestore
        firestore_result = await self._store_session_results()
        
        self.logger.info(f"Session {self.session_data.session_id} completed")
        
        # Return structured result
        return TimerToolResult.success_result(
            data={
                "session_data": asdict(self.session_data),
                "firestore_stored": firestore_result,
                "total_duration_actual": self.session_data.actual_total_duration,
                "phases_completed": [p.name for p in self.session_data.phases if p.status == PhaseStatus.COMPLETED]
            },
            message=f"Session completed successfully in {self.session_data.actual_total_duration:.1f} seconds",
            session_id=self.session_data.session_id,
            session_type=self.session_data.session_type.value,
            completed_phases=[p.name for p in self.session_data.phases if p.status == PhaseStatus.COMPLETED],
            total_duration=int(self.session_data.actual_total_duration // 60) if self.session_data.actual_total_duration else 0,
            phase_completion_data={
                phase.name: {
                    "planned_duration": phase.duration_minutes,
                    "actual_duration": phase.actual_duration,
                    "status": phase.status.value
                }
                for phase in self.session_data.phases
            }
        )
    
    async def _store_session_results(self) -> bool:
        """Store final session results in Firestore.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            from google.cloud import firestore
            
            # Get Firestore client
            db = firestore.Client()
            
            # Prepare session document for Firestore
            session_doc = {
                "sessionId": self.session_data.session_id,
                "sessionType": self.session_data.session_type.value,
                "userId": self.user_id,
                "startTime": datetime.fromtimestamp(self.session_data.start_time),
                "endTime": datetime.fromtimestamp(self.session_data.end_time) if self.session_data.end_time else None,
                "plannedDuration": self.session_data.total_duration_minutes,
                "actualDuration": self.session_data.actual_total_duration,
                "completionPercentage": self.session_data.completion_percentage,
                "userNotes": self.session_data.user_notes,
                "phasesCompleted": [p.name for p in self.session_data.phases if p.status == PhaseStatus.COMPLETED],
                "phaseDetails": [
                    {
                        "name": phase.name,
                        "description": phase.description,
                        "plannedDuration": phase.duration_minutes,
                        "actualDuration": phase.actual_duration,
                        "status": phase.status.value,
                        "startTime": datetime.fromtimestamp(phase.start_time) if phase.start_time else None,
                        "endTime": datetime.fromtimestamp(phase.end_time) if phase.end_time else None,
                        "notes": phase.notes
                    }
                    for phase in self.session_data.phases
                ],
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat()
            }
            
            # Store in Firestore
            db.collection("users").document(self.user_id).collection("sessionTimers").document(self.session_data.session_id).set(session_doc)
            
            self.logger.info(f"Session results stored in Firestore: {self.session_data.session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store session results: {e}")
            return False
    
    async def _send_update(self):
        """Send real-time update via callback function."""
        if self.callback_fn:
            update_data = {
                "session_id": self.session_data.session_id,
                "session_type": self.session_data.session_type.value,
                "completion_percentage": self.session_data.completion_percentage,
                "current_phase": self.get_current_phase_name(),
                "time_remaining": self.get_time_remaining(),
                "is_active": self.session_data.is_active
            }
            
            try:
                await self.callback_fn(update_data)
            except Exception as e:
                self.logger.error(f"Callback function error: {e}")
    
    # Utility Methods
    def get_current_phase(self) -> Optional[SessionPhase]:
        """Get the current active phase."""
        if 0 <= self.session_data.current_phase_index < len(self.session_data.phases):
            return self.session_data.phases[self.session_data.current_phase_index]
        return None
    
    def get_current_phase_name(self) -> str:
        """Get the name of the current phase."""
        current_phase = self.get_current_phase()
        return current_phase.name if current_phase else "No active phase"
    
    def get_time_remaining(self) -> int:
        """Get remaining time in seconds for the entire session."""
        if not self.session_data.start_time:
            return self.session_data.total_duration_minutes * 60
        
        elapsed = time.time() - self.session_data.start_time
        total_seconds = self.session_data.total_duration_minutes * 60
        remaining = max(0, total_seconds - elapsed)
        return int(remaining)
    
    def get_current_phase_time_remaining(self) -> int:
        """Get remaining time in seconds for the current phase."""
        current_phase = self.get_current_phase()
        if not current_phase or not current_phase.start_time:
            return 0
        
        elapsed = time.time() - current_phase.start_time
        total_seconds = current_phase.duration_minutes * 60
        remaining = max(0, total_seconds - elapsed)
        return int(remaining)
    
    def get_session_status(self) -> Dict[str, Any]:
        """Get comprehensive session status."""
        current_phase = self.get_current_phase()
        
        return {
            "session_id": self.session_data.session_id,
            "session_type": self.session_data.session_type.value,
            "is_active": self.session_data.is_active,
            "is_completed": self.session_data.is_completed,
            "completion_percentage": self.session_data.completion_percentage,
            "current_phase": {
                "name": current_phase.name if current_phase else None,
                "index": self.session_data.current_phase_index,
                "description": current_phase.description if current_phase else None,
                "time_remaining": self.get_current_phase_time_remaining()
            },
            "total_time_remaining": self.get_time_remaining(),
            "phases": [
                {
                    "name": phase.name,
                    "status": phase.status.value,
                    "duration_minutes": phase.duration_minutes,
                    "actual_duration": phase.actual_duration
                }
                for phase in self.session_data.phases
            ]
        }


# Backwards compatibility aliases
LocalSessionTimer = EnhancedSessionTimer
SessionTimer = EnhancedSessionTimer 