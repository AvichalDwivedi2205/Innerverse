"""Integration tests for journaling agent with structured results."""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

from google.adk.tools import ToolContext
from google.adk.agents.callback_context import CallbackContext
from agents.journaling_agent.tools import (
    standardize_journal_text,
    generate_journal_insights,
    trigger_mental_orchestrator
)
from agents.common.tool_results import JournalingToolResult


class TestJournalingAgentIntegration:
    """Integration tests for journaling agent tools."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_context = Mock(spec=ToolContext)
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
    @patch('agents.journaling_agent.tools.model')
    async def test_standardize_journal_text_success(self, mock_model):
        """Test successful journal text standardization."""
        # Mock the Gemini response
        mock_response = Mock()
        mock_response.text = json.dumps({
            "reflection": "Today I felt overwhelmed by work pressure, but I realize I created this stress through my thoughts.",
            "empowerment_theme": "self_creation",
            "internal_focus": 0.8,
            "processed_at": datetime.now().isoformat()
        })
        mock_model.generate_content.return_value = mock_response
        
        # Test the function
        result = await standardize_journal_text(
            "I had a terrible day at work. My boss was being difficult.",
            self.mock_context
        )
        
        # Verify result structure
        assert isinstance(result, JournalingToolResult)
        assert result.success is True
        assert "standardized_entry" in result.data
        assert result.message == "Journal text standardized with empowerment focus"
        assert "generate_journal_insights" in result.next_suggested_actions
        
        # Verify context was updated
        assert self.mock_context.state["journal_session"]["raw_text"] != ""
        assert self.mock_context.state["journal_session"]["standardized_entry"] != {}
    
    @pytest.mark.asyncio
    @patch('agents.journaling_agent.tools.model')
    async def test_standardize_journal_text_error(self, mock_model):
        """Test journal text standardization with error."""
        # Mock an exception
        mock_model.generate_content.side_effect = Exception("API connection failed")
        
        # Test the function
        result = await standardize_journal_text(
            "Test journal entry",
            self.mock_context
        )
        
        # Verify error result
        assert isinstance(result, JournalingToolResult)
        assert result.success is False
        assert result.message == "Error standardizing journal text"
        assert result.error_details == "API connection failed"
        assert "retry_standardization" in result.next_suggested_actions
    
    @pytest.mark.asyncio
    @patch('agents.journaling_agent.tools.model')
    async def test_generate_journal_insights_success(self, mock_model):
        """Test successful journal insights generation."""
        # Set up context with standardized entry
        self.mock_context.state["journal_session"]["standardized_entry"] = {
            "reflection": "I notice I create my own stress through negative thinking patterns.",
            "empowerment_theme": "self_creation"
        }
        
        # Mock the Gemini response
        mock_response = Mock()
        mock_response.text = json.dumps({
            "patterns": ["negative_self_talk", "catastrophizing"],
            "empowerment_opportunities": ["mindfulness_practice", "thought_reframing"],
            "internal_locus_score": 0.7,
            "generated_at": datetime.now().isoformat()
        })
        mock_model.generate_content.return_value = mock_response
        
        # Test the function
        result = await generate_journal_insights(self.mock_context)
        
        # Verify result structure
        assert isinstance(result, JournalingToolResult)
        assert result.success is True
        assert "insights" in result.data
        assert result.message == "Journal insights generated with empowerment themes"
        assert "generate_reflection_question" in result.next_suggested_actions
        
        # Verify context was updated
        assert self.mock_context.state["journal_session"]["insights"] != {}
    
    @pytest.mark.asyncio
    async def test_generate_journal_insights_no_standardized_entry(self):
        """Test insights generation when no standardized entry exists."""
        # Clear standardized entry
        self.mock_context.state["journal_session"]["standardized_entry"] = {}
        
        # Test the function
        result = await generate_journal_insights(self.mock_context)
        
        # Verify error result
        assert isinstance(result, JournalingToolResult)
        assert result.success is False
        assert result.message == "No standardized entry found"
        assert result.error_details == "standardize_journal_text must be called first"
        assert "standardize_journal_text" in result.next_suggested_actions
    
    @pytest.mark.asyncio
    @patch('agents.journaling_agent.tools.coordinator')
    async def test_trigger_mental_orchestrator_success(self, mock_coordinator):
        """Test successful mental orchestrator triggering."""
        # Set up context with required data
        self.mock_context.state["journal_id"] = "journal_456"
        
        # Mock coordinator response
        from agents.common.tool_results import CoordinationResult
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
        assert "coordination_result" in result.data
        assert "coordinated_agents" in result.data
        assert result.message == "Mental Orchestrator Agent coordination completed successfully"
        
        # Verify coordinator was called with correct parameters
        mock_coordinator.trigger_mindmap_update.assert_called_once_with(
            user_id="test_user_123",
            source_type="journal",
            source_id="journal_456",
            callback_context=self.mock_context
        )
    
    @pytest.mark.asyncio
    @patch('agents.journaling_agent.tools.coordinator')
    async def test_trigger_mental_orchestrator_coordination_failure(self, mock_coordinator):
        """Test mental orchestrator triggering with coordination failure."""
        # Set up context with required data
        self.mock_context.state["journal_id"] = "journal_456"
        
        # Mock coordinator failure response
        from agents.common.tool_results import CoordinationResult
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
        assert result.message == "Failed to coordinate with Mental Orchestrator"
        assert "Agent not found" in result.error_details
        assert "retry_coordination" in result.next_suggested_actions
    
    @pytest.mark.asyncio
    async def test_trigger_mental_orchestrator_missing_context(self):
        """Test mental orchestrator triggering with missing context data."""
        # Remove required context data
        self.mock_context.state.pop("user_id", None)
        
        # Test the function
        result = await trigger_mental_orchestrator(self.mock_context)
        
        # Verify error result
        assert isinstance(result, JournalingToolResult)
        assert result.success is False
        assert result.message == "Missing required context data"
        assert "User ID or Journal ID not found" in result.error_details
        assert "verify_user_context" in result.next_suggested_actions
    
    @pytest.mark.asyncio
    @patch('agents.journaling_agent.tools.coordinator')
    async def test_trigger_mental_orchestrator_exception(self, mock_coordinator):
        """Test mental orchestrator triggering with exception."""
        # Set up context with required data
        self.mock_context.state["journal_id"] = "journal_456"
        
        # Mock coordinator exception
        mock_coordinator.trigger_mindmap_update.side_effect = Exception("Coordinator error")
        
        # Test the function
        result = await trigger_mental_orchestrator(self.mock_context)
        
        # Verify error result
        assert isinstance(result, JournalingToolResult)
        assert result.success is False
        assert result.message == "Error triggering Mental Orchestrator"
        assert result.error_details == "Coordinator error"
        assert "retry_coordination" in result.next_suggested_actions


class TestJournalingAgentStateManagement:
    """Tests for improved state management in journaling agent."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_callback_context = Mock(spec=CallbackContext)
        self.mock_callback_context.state = {}
    
    def test_setup_before_agent_call_new_session(self):
        """Test setup with new session state."""
        from agents.journaling_agent.journaling_agent import setup_before_agent_call
        
        # Call setup function
        setup_before_agent_call(self.mock_callback_context)
        
        # Verify initialization
        assert "user_id" in self.mock_callback_context.state
        assert "journal_session" in self.mock_callback_context.state
        
        session = self.mock_callback_context.state["journal_session"]
        assert "raw_text" in session
        assert "standardized_entry" in session
        assert "insights" in session
        assert "reflection_question" in session
        assert "embedding_id" in session
        assert "created_at" in session
        assert "status" in session
        assert session["status"] == "active"
    
    def test_setup_before_agent_call_existing_session(self):
        """Test setup with existing session state preservation."""
        from agents.journaling_agent.journaling_agent import setup_before_agent_call
        
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
        
        # Call setup function
        setup_before_agent_call(self.mock_callback_context)
        
        # Verify existing data was preserved
        session = self.mock_callback_context.state["journal_session"]
        assert session["raw_text"] == "Existing journal text"
        assert session["standardized_entry"]["reflection"] == "Existing reflection"
        assert session["insights"]["pattern"] == "existing_pattern"
        assert session["created_at"] == "2025-01-01T00:00:00"
        assert session["status"] == "processing"
        
        # Verify missing keys were added
        assert "reflection_question" in session
        assert "embedding_id" in session
    
    def test_setup_before_agent_call_partial_existing_session(self):
        """Test setup with partially complete existing session."""
        from agents.journaling_agent.journaling_agent import setup_before_agent_call
        
        # Set up partial existing state
        partial_session_data = {
            "raw_text": "Partial journal text",
            "created_at": "2025-01-01T12:00:00"
            # Missing other required keys
        }
        self.mock_callback_context.state = {
            "journal_session": partial_session_data
        }
        
        # Call setup function  
        setup_before_agent_call(self.mock_callback_context)
        
        # Verify existing data was preserved and missing keys were added
        session = self.mock_callback_context.state["journal_session"]
        assert session["raw_text"] == "Partial journal text"
        assert session["created_at"] == "2025-01-01T12:00:00"
        
        # Verify missing keys were added with defaults
        assert session["standardized_entry"] == {}
        assert session["insights"] == {}
        assert session["reflection_question"] == ""
        assert session["embedding_id"] == ""
        assert session["status"] == "active"  # Default status 