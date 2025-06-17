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