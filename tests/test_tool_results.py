"""Tests for structured tool results."""

import pytest
from datetime import datetime
from agents.common.tool_results import (
    ToolResult,
    JournalingToolResult,
    TherapyToolResult,
    OrchestratorToolResult,
    CoordinationResult
)


class TestToolResult:
    """Test cases for base ToolResult class."""
    
    def test_success_result_creation(self):
        """Test creating a successful tool result."""
        result = ToolResult(
            success=True,
            data={"key": "value"},
            message="Operation successful",
            next_suggested_actions=["next_action"]
        )
        
        assert result.success is True
        assert result.data == {"key": "value"}
        assert result.message == "Operation successful"
        assert result.next_suggested_actions == ["next_action"]
        assert result.error_details is None
        assert isinstance(result.timestamp, datetime)
    
    def test_error_result_creation(self):
        """Test creating an error tool result."""
        result = ToolResult(
            success=False,
            data={},
            message="Operation failed",
            error_details="Detailed error message"
        )
        
        assert result.success is False
        assert result.data == {}
        assert result.message == "Operation failed"
        assert result.error_details == "Detailed error message"
    
    def test_json_serialization(self):
        """Test that tool results can be serialized to JSON."""
        result = ToolResult(
            success=True,
            data={"test": "data"},
            message="Test message"
        )
        
        json_data = result.dict()
        assert "timestamp" in json_data
        assert json_data["success"] is True
        assert json_data["data"] == {"test": "data"}


class TestJournalingToolResult:
    """Test cases for JournalingToolResult class."""
    
    def test_success_result_helper(self):
        """Test the success_result class method."""
        result = JournalingToolResult.success_result(
            data={"standardized_entry": {"text": "processed"}},
            message="Journal processed successfully",
            next_actions=["generate_insights"],
            journal_id="journal_123",
            embedding_id="embed_456"
        )
        
        assert result.success is True
        assert result.data == {"standardized_entry": {"text": "processed"}}
        assert result.message == "Journal processed successfully"
        assert result.next_suggested_actions == ["generate_insights"]
        assert result.journal_id == "journal_123"
        assert result.embedding_id == "embed_456"
    
    def test_error_result_helper(self):
        """Test the error_result class method."""
        result = JournalingToolResult.error_result(
            message="Journal processing failed",
            error_details="Invalid input format",
            next_actions=["retry_processing"]
        )
        
        assert result.success is False
        assert result.data == {}
        assert result.message == "Journal processing failed"
        assert result.error_details == "Invalid input format"
        assert result.next_suggested_actions == ["retry_processing"]
        assert result.journal_id is None
        assert result.embedding_id is None


class TestTherapyToolResult:
    """Test cases for TherapyToolResult class."""
    
    def test_success_result_helper(self):
        """Test the success_result class method."""
        result = TherapyToolResult.success_result(
            data={"session_summary": {"duration": 60}},
            message="Therapy session processed",
            next_actions=["generate_notes"],
            session_id="session_789",
            embedding_id="embed_101"
        )
        
        assert result.success is True
        assert result.data == {"session_summary": {"duration": 60}}
        assert result.session_id == "session_789"
        assert result.embedding_id == "embed_101"
    
    def test_error_result_helper(self):
        """Test the error_result class method."""
        result = TherapyToolResult.error_result(
            message="Session processing failed",
            error_details="Transcript too short"
        )
        
        assert result.success is False
        assert result.message == "Session processing failed"
        assert result.error_details == "Transcript too short"
        assert result.next_suggested_actions == ["retry_operation"]


class TestOrchestratorToolResult:
    """Test cases for OrchestratorToolResult class."""
    
    def test_success_result_helper(self):
        """Test the success_result class method."""
        result = OrchestratorToolResult.success_result(
            data={"mind_map": {"nodes": [], "edges": []}},
            message="Mind map updated",
            next_actions=["generate_insights"],
            mind_map_version=2,
            clusters_count=5
        )
        
        assert result.success is True
        assert result.data == {"mind_map": {"nodes": [], "edges": []}}
        assert result.mind_map_version == 2
        assert result.clusters_count == 5
    
    def test_error_result_helper(self):
        """Test the error_result class method."""
        result = OrchestratorToolResult.error_result(
            message="Clustering failed",
            error_details="Insufficient data points"
        )
        
        assert result.success is False
        assert result.message == "Clustering failed"
        assert result.error_details == "Insufficient data points"


class TestCoordinationResult:
    """Test cases for CoordinationResult class."""
    
    def test_successful_coordination(self):
        """Test creating successful coordination result."""
        result = CoordinationResult(
            success=True,
            coordinated_agents=["journaling_agent", "orchestrator_agent"],
            results={"step1": "completed", "step2": "completed"},
            message="Workflow completed successfully"
        )
        
        assert result.success is True
        assert len(result.coordinated_agents) == 2
        assert "journaling_agent" in result.coordinated_agents
        assert result.results == {"step1": "completed", "step2": "completed"}
        assert result.message == "Workflow completed successfully"
        assert len(result.errors) == 0
    
    def test_failed_coordination(self):
        """Test creating failed coordination result."""
        result = CoordinationResult(
            success=False,
            coordinated_agents=["journaling_agent"],
            results={"step1": "completed"},
            message="Workflow failed",
            errors=["Agent not found", "Data missing"]
        )
        
        assert result.success is False
        assert result.coordinated_agents == ["journaling_agent"]
        assert len(result.errors) == 2
        assert "Agent not found" in result.errors
    
    def test_json_serialization(self):
        """Test that coordination results can be serialized."""
        result = CoordinationResult(
            success=True,
            coordinated_agents=["test_agent"],
            results={"test": "data"},
            message="Test completed"
        )
        
        json_data = result.dict()
        assert "timestamp" in json_data
        assert json_data["success"] is True
        assert json_data["coordinated_agents"] == ["test_agent"] 