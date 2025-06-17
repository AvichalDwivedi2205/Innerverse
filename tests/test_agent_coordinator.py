"""Tests for agent coordinator."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from agents.common.agent_coordinator import AgentCoordinator, coordinator
from agents.common.tool_results import CoordinationResult
from google.adk.agents.callback_context import CallbackContext


class TestAgentCoordinator:
    """Test cases for AgentCoordinator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.coordinator = AgentCoordinator()
        self.mock_context = Mock(spec=CallbackContext)
        self.mock_context.state = {}
    
    def test_coordinator_initialization(self):
        """Test that coordinator initializes with proper workflows."""
        assert isinstance(self.coordinator.agent_registry, dict)
        assert isinstance(self.coordinator.workflow_definitions, dict)
        
        # Check that standard workflows are defined
        assert "journal_to_mindmap" in self.coordinator.workflow_definitions
        assert "therapy_to_mindmap" in self.coordinator.workflow_definitions
        assert "comprehensive_analysis" in self.coordinator.workflow_definitions
    
    def test_register_agent(self):
        """Test agent registration."""
        mock_agent = Mock()
        self.coordinator.register_agent("test_agent", mock_agent)
        
        assert "test_agent" in self.coordinator.agent_registry
        assert self.coordinator.agent_registry["test_agent"] == mock_agent
    
    @pytest.mark.asyncio
    async def test_coordinate_workflow_unknown_workflow(self):
        """Test coordination with unknown workflow name."""
        result = await self.coordinator.coordinate_workflow(
            "unknown_workflow",
            {"user_id": "test_user"},
            self.mock_context
        )
        
        assert isinstance(result, CoordinationResult)
        assert result.success is False
        assert "Unknown workflow" in result.message
        assert "unknown_workflow" in str(result.errors)
    
    @pytest.mark.asyncio
    async def test_coordinate_workflow_missing_data(self):
        """Test coordination with missing required data."""
        result = await self.coordinator.coordinate_workflow(
            "journal_to_mindmap",
            {"user_id": "test_user"},  # Missing raw_text
            self.mock_context
        )
        
        assert isinstance(result, CoordinationResult)
        assert result.success is False
        assert "Missing required data" in result.message
        assert any("raw_text" in error for error in result.errors)
    
    @pytest.mark.asyncio
    async def test_coordinate_workflow_success(self):
        """Test successful workflow coordination."""
        with patch.object(self.coordinator, '_execute_agent_action', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {
                "agent": "test_agent",
                "action": "test_action",
                "success": True,
                "data": {"result": "test_result"}
            }
            
            result = await self.coordinator.coordinate_workflow(
                "journal_to_mindmap",
                {
                    "user_id": "test_user",
                    "raw_text": "test journal entry"
                },
                self.mock_context
            )
            
            assert isinstance(result, CoordinationResult)
            assert result.success is True
            assert "completed successfully" in result.message
            assert len(result.coordinated_agents) > 0
            assert len(result.results) == 2  # Two steps in journal_to_mindmap
    
    @pytest.mark.asyncio
    async def test_coordinate_workflow_exception(self):
        """Test workflow coordination with exception."""
        with patch.object(self.coordinator, '_execute_agent_action', new_callable=AsyncMock) as mock_execute:
            mock_execute.side_effect = Exception("Test exception")
            
            result = await self.coordinator.coordinate_workflow(
                "journal_to_mindmap",
                {
                    "user_id": "test_user",
                    "raw_text": "test journal entry"
                },
                self.mock_context
            )
            
            assert isinstance(result, CoordinationResult)
            assert result.success is False
            assert "Workflow execution failed" in result.message
            assert "Test exception" in str(result.errors)
    
    @pytest.mark.asyncio
    async def test_execute_agent_action(self):
        """Test agent action execution."""
        test_data = {"user_id": "test_user", "test_key": "test_value"}
        
        result = await self.coordinator._execute_agent_action(
            "test_agent",
            "test_action",
            test_data,
            self.mock_context
        )
        
        assert isinstance(result, dict)
        assert result["agent"] == "test_agent"
        assert result["action"] == "test_action"
        assert result["success"] is True
        assert "timestamp" in result
        
        # Verify context was updated
        # Note: In real implementation, this would update the actual context
    
    @pytest.mark.asyncio
    async def test_trigger_mindmap_update_journal(self):
        """Test triggering mind map update for journal source."""
        with patch.object(self.coordinator, 'coordinate_workflow', new_callable=AsyncMock) as mock_coordinate:
            mock_coordinate.return_value = CoordinationResult(
                success=True,
                coordinated_agents=["journaling_agent", "mental_orchestrator_agent"],
                results={"step1": "completed"},
                message="Workflow completed"
            )
            
            result = await self.coordinator.trigger_mindmap_update(
                user_id="test_user",
                source_type="journal",
                source_id="journal_123",
                callback_context=self.mock_context
            )
            
            assert isinstance(result, CoordinationResult)
            assert result.success is True
            
            # Verify coordinate_workflow was called with correct parameters
            mock_coordinate.assert_called_once()
            args, kwargs = mock_coordinate.call_args
            assert args[0] == "journal_to_mindmap"
            assert args[1]["user_id"] == "test_user"
            assert args[1]["journal_id"] == "journal_123"
    
    @pytest.mark.asyncio
    async def test_trigger_mindmap_update_therapy(self):
        """Test triggering mind map update for therapy source."""
        with patch.object(self.coordinator, 'coordinate_workflow', new_callable=AsyncMock) as mock_coordinate:
            mock_coordinate.return_value = CoordinationResult(
                success=True,
                coordinated_agents=["therapy_agent", "mental_orchestrator_agent"],
                results={"step1": "completed"},
                message="Workflow completed"
            )
            
            result = await self.coordinator.trigger_mindmap_update(
                user_id="test_user",
                source_type="therapy",
                source_id="therapy_456",
                callback_context=self.mock_context
            )
            
            assert isinstance(result, CoordinationResult)
            assert result.success is True
            
            # Verify coordinate_workflow was called with correct parameters
            mock_coordinate.assert_called_once()
            args, kwargs = mock_coordinate.call_args
            assert args[0] == "therapy_to_mindmap"
            assert args[1]["user_id"] == "test_user"
            assert args[1]["therapy_id"] == "therapy_456"
    
    @pytest.mark.asyncio
    async def test_trigger_mindmap_update_unknown_source(self):
        """Test triggering mind map update with unknown source type."""
        result = await self.coordinator.trigger_mindmap_update(
            user_id="test_user",
            source_type="unknown_source",
            source_id="unknown_123",
            callback_context=self.mock_context
        )
        
        assert isinstance(result, CoordinationResult)
        assert result.success is False
        assert "No workflow defined" in result.message
        assert "unknown_source" in str(result.errors)
    
    @pytest.mark.asyncio
    async def test_trigger_mindmap_update_exception(self):
        """Test triggering mind map update with exception."""
        with patch.object(self.coordinator, 'coordinate_workflow', new_callable=AsyncMock) as mock_coordinate:
            mock_coordinate.side_effect = Exception("Coordination failed")
            
            result = await self.coordinator.trigger_mindmap_update(
                user_id="test_user",
                source_type="journal",
                source_id="journal_123",
                callback_context=self.mock_context
            )
            
            assert isinstance(result, CoordinationResult)
            assert result.success is False
            assert "Mind map update failed" in result.message
            assert "Coordination failed" in str(result.errors)


class TestGlobalCoordinator:
    """Test cases for global coordinator instance."""
    
    def test_global_coordinator_exists(self):
        """Test that global coordinator instance exists."""
        assert coordinator is not None
        assert isinstance(coordinator, AgentCoordinator)
    
    def test_global_coordinator_has_workflows(self):
        """Test that global coordinator has predefined workflows."""
        assert len(coordinator.workflow_definitions) > 0
        assert "journal_to_mindmap" in coordinator.workflow_definitions 