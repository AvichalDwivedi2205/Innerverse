"""Integration tests for journaling agent with focus on tool coordination and state management."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from agents.common.tool_results import JournalingToolResult, CoordinationResult
from agents.journaling_agent.tools import (
    standardize_journal_text,
    generate_journal_insights,
    trigger_mental_orchestrator
)


class TestJournalingAgentIntegration:
    """Test journaling agent integration and tool coordination."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_context = Mock()
        self.mock_context.state = {
            "user_id": "test_user_123",
            "journal_session": {
                "raw_text": "",
                "standardized_entry": {},
                "insights": {},
                "reflection_question": "",
                "embedding_id": "",
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
        }

    @pytest.mark.asyncio
    async def test_standardize_journal_text_success(self):
        """Test successful journal text standardization."""
        # Test data
        raw_text = "Today I felt anxious about my presentation, but I realize it's my thoughts creating this feeling."
        
        # Mock the model response to return valid JSON
        with patch('agents.journaling_agent.tools.get_gemini_model') as mock_model:
            mock_response = Mock()
            mock_response.text = '{"date": "2025-01-15", "mood": "contemplative", "keyEvents": "presentation anxiety", "reflection": "recognizing thoughts create feelings"}'
            mock_model.return_value.generate_content.return_value = mock_response
            
            # Test the function
            result = await standardize_journal_text(raw_text, self.mock_context)
            
            # Verify result structure
            assert isinstance(result, JournalingToolResult)
            assert result.success is True
            assert "standardized_entry" in result.data
            assert result.message == "Journal text standardized with empowerment focus"

    @pytest.mark.asyncio
    async def test_standardize_journal_text_error(self):
        """Test journal text standardization with invalid JSON response."""
        raw_text = "Test journal entry"
        
        # Mock the model to return invalid JSON
        with patch('agents.journaling_agent.tools.get_gemini_model') as mock_model:
            mock_response = Mock()
            mock_response.text = "Invalid JSON response"
            mock_model.return_value.generate_content.return_value = mock_response
            
            # Test the function
            result = await standardize_journal_text(raw_text, self.mock_context)
            
            # Verify error handling
            assert isinstance(result, JournalingToolResult)
            assert result.success is False
            assert "Failed to parse standardized entry JSON" in result.message

    @pytest.mark.asyncio
    async def test_generate_journal_insights_success(self):
        """Test successful journal insights generation."""
        # Set up context with standardized entry
        self.mock_context.state["journal_session"]["standardized_entry"] = {
            "date": "2025-01-15",
            "mood": "contemplative",
            "keyEvents": "presentation anxiety",
            "reflection": "recognizing thoughts create feelings"
        }
        
        # Mock the model response
        with patch('agents.journaling_agent.tools.get_gemini_model') as mock_model:
            mock_response = Mock()
            mock_response.text = '{"sentiment": "neutral", "emotion": "contemplative", "intensity": 6, "themes": ["self_awareness"], "triggers": ["internal_thoughts"]}'
            mock_model.return_value.generate_content.return_value = mock_response
            
            # Test the function
            result = await generate_journal_insights(self.mock_context)
            
            # Verify result
            assert isinstance(result, JournalingToolResult)
            assert result.success is True
            assert "insights" in result.data

    @pytest.mark.asyncio
    async def test_generate_journal_insights_no_standardized_entry(self):
        """Test insights generation without standardized entry."""
        # Empty context
        self.mock_context.state["journal_session"]["standardized_entry"] = {}
        
        # Test the function
        result = await generate_journal_insights(self.mock_context)
        
        # Verify error handling
        assert isinstance(result, JournalingToolResult)
        assert result.success is False
        assert "No standardized entry found" in result.message

    @pytest.mark.asyncio
    @patch('agents.journaling_agent.tools.coordinator')
    async def test_trigger_mental_orchestrator_success(self, mock_coordinator):
        """Test successful mental orchestrator triggering."""
        # Set up context with required data
        self.mock_context.state["journal_id"] = "journal_456"
        
        # Mock coordinator response
        mock_coordination_result = CoordinationResult(
            success=True,
            coordinated_agents=["mental_orchestrator_agent"],
            results={"mind_map_updated": True},
            message="Mind map updated successfully"
        )
        mock_coordinator.trigger_mindmap_update.return_value = mock_coordination_result
        
        # Test the function
        result = await trigger_mental_orchestrator(self.mock_context)
        
        # Verify result structure
        assert isinstance(result, JournalingToolResult)
        assert result.success is True

    @pytest.mark.asyncio
    @patch('agents.journaling_agent.tools.coordinator')
    async def test_trigger_mental_orchestrator_coordination_failure(self, mock_coordinator):
        """Test mental orchestrator triggering with coordination failure."""
        # Set up context with required data
        self.mock_context.state["journal_id"] = "journal_456"
        
        # Mock coordinator failure response
        mock_coordination_result = CoordinationResult(
            success=False,
            coordinated_agents=[],
            results={},
            message="Coordination failed",
            errors=["Agent not found"]
        )
        mock_coordinator.trigger_mindmap_update.return_value = mock_coordination_result
        
        # Test the function
        result = await trigger_mental_orchestrator(self.mock_context)
        
        # Verify error result
        assert isinstance(result, JournalingToolResult)
        assert result.success is False

    @pytest.mark.asyncio
    async def test_trigger_mental_orchestrator_missing_context(self):
        """Test mental orchestrator triggering without required context."""
        # Remove journal_id from context
        self.mock_context.state.pop("journal_id", None)
        
        # Test the function
        result = await trigger_mental_orchestrator(self.mock_context)
        
        # Verify error handling
        assert isinstance(result, JournalingToolResult)
        assert result.success is False
        assert "journal_id not found" in result.message

    @pytest.mark.asyncio
    async def test_trigger_mental_orchestrator_exception(self):
        """Test mental orchestrator triggering with exception."""
        # Set up context
        self.mock_context.state["journal_id"] = "journal_456"
        
        # Mock coordinator to raise exception
        with patch('agents.journaling_agent.tools.coordinator') as mock_coordinator:
            mock_coordinator.trigger_mindmap_update.side_effect = Exception("Test exception")
            
            # Test the function
            result = await trigger_mental_orchestrator(self.mock_context)
            
            # Verify error handling
            assert isinstance(result, JournalingToolResult)
            assert result.success is False
            assert "Error triggering Mental Orchestrator" in result.message


class TestJournalingAgentStateManagement:
    """Test journaling agent state management and session handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_callback_context = Mock()
        self.mock_callback_context.state = {}

    def test_setup_before_agent_call_new_session(self):
        """Test setup with new session state."""
        # Mock the callback context structure
        mock_agent = Mock()
        mock_invocation = Mock()
        mock_invocation.agent = mock_agent
        self.mock_callback_context._invocation_context = mock_invocation
        
        from agents.journaling_agent.journaling_agent import setup_before_agent_call
        
        # Call setup function
        setup_before_agent_call(self.mock_callback_context)
        
        # Verify session initialization
        assert "journal_session" in self.mock_callback_context.state
        session = self.mock_callback_context.state["journal_session"]
        assert session["status"] == "active"
        assert "created_at" in session

    def test_setup_before_agent_call_existing_session(self):
        """Test setup with existing session state preservation."""
        # Mock the callback context structure
        mock_agent = Mock()
        mock_invocation = Mock()
        mock_invocation.agent = mock_agent
        self.mock_callback_context._invocation_context = mock_invocation
        
        # Set up existing state
        existing_session_data = {
            "raw_text": "Existing journal text",
            "standardized_entry": {"reflection": "Existing reflection"},
            "insights": {"pattern": "existing_pattern"},
            "created_at": "2025-01-01T00:00:00",
            "status": "processing"
        }
        self.mock_callback_context.state = {
            "user_id": "existing_user",
            "journal_session": existing_session_data
        }
        
        from agents.journaling_agent.journaling_agent import setup_before_agent_call
        
        # Call setup function
        setup_before_agent_call(self.mock_callback_context)
        
        # Verify existing state preserved
        session = self.mock_callback_context.state["journal_session"]
        assert session["raw_text"] == "Existing journal text"
        assert session["status"] == "processing"
        assert session["created_at"] == "2025-01-01T00:00:00"

    def test_setup_before_agent_call_partial_existing_session(self):
        """Test setup with partially complete existing session."""
        # Mock the callback context structure
        mock_agent = Mock()
        mock_invocation = Mock()
        mock_invocation.agent = mock_agent
        self.mock_callback_context._invocation_context = mock_invocation
        
        # Set up partial existing state
        partial_session_data = {
            "raw_text": "Partial journal text",
            "created_at": "2025-01-01T12:00:00"
            # Missing other required keys
        }
        self.mock_callback_context.state = {
            "journal_session": partial_session_data
        }
        
        from agents.journaling_agent.journaling_agent import setup_before_agent_call
        
        # Call setup function
        setup_before_agent_call(self.mock_callback_context)
        
        # Verify partial state preserved and missing keys added
        session = self.mock_callback_context.state["journal_session"]
        assert session["raw_text"] == "Partial journal text"
        assert session["created_at"] == "2025-01-01T12:00:00"
        assert "insights" in session
        assert "standardized_entry" in session 