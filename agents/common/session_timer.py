"""Local Session Timer for Innerverse - Hybrid Approach.

This module provides real-time session timing locally with final results stored in Firestore.
Supports therapy sessions (50-60 min with phases) and exercise sessions (10 min fixed).
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


class PhaseStatus(Enum):
    """Enum for phase completion status."""
    PENDING = "pending"
    ACTIVE = "active" 
    COMPLETED = "completed"
    SKIPPED = "skipped"


@dataclass
class SessionPhase:
    """Represents a single phase in a session."""
    name: str
    duration_minutes: int
    description: str
    status: PhaseStatus = PhaseStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    actual_duration: Optional[float] = None
    notes: Optional[str] = None


@dataclass
class SessionData:
    """Complete session data structure."""
    session_id: str
    session_type: SessionType
    start_time: float
    total_duration_minutes: int
    phases: List[SessionPhase]
    current_phase_index: int = 0
    is_active: bool = False
    is_completed: bool = False
    end_time: Optional[float] = None
    actual_total_duration: Optional[float] = None
    completion_percentage: float = 0.0
    user_notes: Optional[str] = None


class LocalSessionTimer:
    """Local timer for real-time session tracking with Firestore storage of final results."""
    
    def __init__(self, session_type: SessionType, user_id: str, callback_fn: Optional[Callable] = None):
        """Initialize the session timer.
        
        Args:
            session_type: Type of session (therapy or exercise)
            user_id: User identifier for Firestore storage
            callback_fn: Optional callback function for real-time updates
        """
        self.logger = logging.getLogger(__name__)
        self.session_type = session_type
        self.user_id = user_id
        self.callback_fn = callback_fn
        
        # Initialize session data
        self.session_data = self._create_session_data()
        
        # Timer state
        self._timer_task: Optional[asyncio.Task] = None
        self._update_interval = 1.0  # Update every second
        
        self.logger.info(f"LocalSessionTimer initialized for {session_type.value} session")
    
    def _create_session_data(self) -> SessionData:
        """Create session data with appropriate phases based on session type."""
        session_id = str(uuid.uuid4())
        
        if self.session_type == SessionType.THERAPY:
            phases = [
                SessionPhase(
                    name="opening",
                    duration_minutes=10,
                    description="Check-in, mood assessment, safety screening"
                ),
                SessionPhase(
                    name="working", 
                    duration_minutes=35,
                    description="Deep therapeutic work and exploration"
                ),
                SessionPhase(
                    name="integration",
                    duration_minutes=8,
                    description="Insights, empowerment, and integration"
                ),
                SessionPhase(
                    name="closing",
                    duration_minutes=7,
                    description="Summary, homework, and scheduling"
                )
            ]
            total_duration = 60
            
        elif self.session_type == SessionType.EXERCISE:
            phases = [
                SessionPhase(
                    name="exercise",
                    duration_minutes=10,
                    description="10-minute focused exercise session"
                )
            ]
            total_duration = 10
        
        return SessionData(
            session_id=session_id,
            session_type=self.session_type,
            start_time=0,  # Will be set when session starts
            total_duration_minutes=total_duration,
            phases=phases
        )
    
    async def start_session(self) -> str:
        """Start the session timer.
        
        Returns:
            Session ID
        """
        if self.session_data.is_active:
            return f"Session {self.session_data.session_id} is already active"
        
        # Set start time
        current_time = time.time()
        self.session_data.start_time = current_time
        self.session_data.is_active = True
        
        # Start first phase
        if self.session_data.phases:
            self.session_data.phases[0].status = PhaseStatus.ACTIVE
            self.session_data.phases[0].start_time = current_time
        
        # Start the timer task
        self._timer_task = asyncio.create_task(self._timer_loop())
        
        self.logger.info(f"Session {self.session_data.session_id} started")
        return self.session_data.session_id
    
    async def _timer_loop(self):
        """Main timer loop that runs continuously during the session."""
        try:
            while self.session_data.is_active and not self.session_data.is_completed:
                await asyncio.sleep(self._update_interval)
                
                current_time = time.time()
                elapsed_time = current_time - self.session_data.start_time
                
                # Update session progress
                self._update_session_progress(current_time, elapsed_time)
                
                # Check for phase transitions
                self._check_phase_transitions(current_time)
                
                # Send real-time updates if callback is provided
                if self.callback_fn:
                    await self._send_update()
                
                # Check if session should complete
                if elapsed_time >= (self.session_data.total_duration_minutes * 60):
                    await self.complete_session()
                    
        except asyncio.CancelledError:
            self.logger.info("Timer loop cancelled")
        except Exception as e:
            self.logger.error(f"Timer loop error: {e}")
    
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
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
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