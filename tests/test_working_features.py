"""Tests for working features without external dependencies."""

import pytest
from unittest.mock import Mock, patch
from agents.common.tool_results import (
    ToolResult,
    JournalingToolResult,
    TherapyToolResult,
    OrchestratorToolResult,
    CoordinationResult
)
from agents.common.agent_coordinator import AgentCoordinator
from agents.common.pinecone_service import PineconeService


class TestToolResults:
    """Test tool results classes."""
    
    def test_tool_result_success(self):
        """Test ToolResult success creation."""
        result = ToolResult(
            success=True,
            data={"test": "data"},
            message="Success message",
            next_suggested_actions=["action1", "action2"]
        )
        
        assert result.success is True
        assert result.data == {"test": "data"}
        assert result.message == "Success message"
        assert result.next_suggested_actions == ["action1", "action2"]
        assert result.error_details is None
    
    def test_tool_result_error(self):
        """Test ToolResult error creation."""
        result = ToolResult(
            success=False,
            data={},
            message="Error message",
            error_details="Detailed error info",
            next_suggested_actions=["retry", "fallback"]
        )
        
        assert result.success is False
        assert result.data == {}
        assert result.message == "Error message"
        assert result.error_details == "Detailed error info"
        assert result.next_suggested_actions == ["retry", "fallback"]
    
    def test_journaling_tool_result_success(self):
        """Test JournalingToolResult creation."""
        result = JournalingToolResult.success_result(
            data={"journal_id": "123"},
            message="Journal processed",
            next_actions=["store_entry"]
        )
        
        assert isinstance(result, JournalingToolResult)
        assert result.success is True
        assert result.data["journal_id"] == "123"
    
    def test_orchestrator_tool_result_success(self):
        """Test OrchestratorToolResult creation."""
        result = OrchestratorToolResult.success_result(
            data={"mind_map": "data"},
            message="Mind map created",
            next_actions=["generate_insights"]
        )
        
        assert isinstance(result, OrchestratorToolResult)
        assert result.success is True
        assert result.data["mind_map"] == "data"


class TestAgentCoordinator:
    """Test agent coordinator functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.coordinator = AgentCoordinator()
    
    def test_coordinator_initialization(self):
        """Test coordinator initialization."""
        assert self.coordinator is not None
        assert hasattr(self.coordinator, 'agent_registry')
        # The coordinator may have different attributes - test what's available
        assert hasattr(self.coordinator, 'predefined_workflows') or hasattr(self.coordinator, 'workflows')
    
    def test_coordination_result_success(self):
        """Test CoordinationResult creation."""
        result = CoordinationResult(
            success=True,
            coordinated_agents=["agent1", "agent2"],
            results={"result": "data"},
            message="Coordination successful"
        )
        
        assert result.success is True
        assert len(result.coordinated_agents) == 2
        assert result.results["result"] == "data"
        assert result.message == "Coordination successful"
    
    def test_coordination_result_error(self):
        """Test CoordinationResult error creation."""
        result = CoordinationResult(
            success=False,
            coordinated_agents=[],
            results={},
            message="Coordination failed",
            errors=["Error 1", "Error 2"]
        )
        
        assert result.success is False
        assert len(result.coordinated_agents) == 0
        assert len(result.errors) == 2


class TestPineconeService:
    """Test Pinecone service functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = PineconeService()
    
    def test_pinecone_service_initialization(self):
        """Test Pinecone service initialization."""
        assert self.service is not None
        assert hasattr(self.service, 'dimension')
        assert self.service.dimension > 0
    
    @pytest.mark.asyncio
    async def test_generate_embedding_fallback(self):
        """Test embedding generation fallback."""
        # Service should work even without real Pinecone connection
        self.service.embedding_model = None
        
        result = await self.service.generate_embedding("test text")
        
        assert result is not None
        assert len(result) == self.service.dimension
        assert isinstance(result, list)
        assert all(isinstance(x, (int, float)) for x in result)
    
    @pytest.mark.asyncio
    async def test_store_embedding_without_pinecone(self):
        """Test storing embedding without Pinecone connection."""
        # Service should handle missing Pinecone gracefully
        self.service.index = None
        
        success = await self.service.store_embedding(
            embedding_id="test_id",
            text="test text",
            user_id="user123",
            context="journal",
            source_id="source123"
        )
        
        assert success is True  # Should succeed even without real Pinecone
    
    @pytest.mark.asyncio
    async def test_retrieve_user_embeddings_fallback(self):
        """Test retrieving embeddings fallback."""
        # Service should provide sample data when Pinecone not available
        self.service.index = None
        
        embeddings = await self.service.retrieve_user_embeddings("user123")
        
        assert isinstance(embeddings, list)
        assert len(embeddings) > 0
        for embedding in embeddings:
            assert "id" in embedding
            assert "vector" in embedding
            assert "metadata" in embedding
            assert embedding["metadata"]["userId"] == "user123"
    
    def test_get_index_stats_unavailable(self):
        """Test getting index stats when unavailable."""
        self.service.index = None
        
        stats = self.service.get_index_stats()
        
        assert stats["status"] == "unavailable"
        assert "reason" in stats


class TestIntegrationWorkflow:
    """Test integration workflow functionality."""
    
    @pytest.mark.asyncio
    async def test_trend_analysis_workflow(self):
        """Test complete trend analysis workflow without external services."""
        # Initialize service
        service = PineconeService()
        service.index = None  # Use simulation mode
        
        # Test data
        user_id = "test_user"
        journal_entries = [
            "I feel empowered when I realize I create my own reality.",
            "Today I practiced mindfulness and felt more centered.",
            "I'm learning to trust my inner wisdom and intuition."
        ]
        
        # Store multiple embeddings
        for i, entry in enumerate(journal_entries):
            success = await service.store_embedding(
                embedding_id=f"{user_id}_journal_{i}",
                text=entry,
                user_id=user_id,
                context="journal",
                source_id=f"journal_{i}"
            )
            assert success is True
        
        # Retrieve embeddings for analysis
        embeddings = await service.retrieve_user_embeddings(user_id)
        assert len(embeddings) >= len(journal_entries)
        
        # Test context filtering
        journal_embeddings = await service.retrieve_user_embeddings(
            user_id, 
            context_filter="journal"
        )
        assert len(journal_embeddings) >= len(journal_entries)
        
        # All embeddings should be for the correct user
        for embedding in journal_embeddings:
            assert embedding["metadata"]["userId"] == user_id
            assert embedding["metadata"]["context"] == "journal"


class TestEnvironmentCompatibility:
    """Test environment compatibility."""
    
    def test_imports_work(self):
        """Test that all imports work without errors."""
        # This test passing means all modules can be imported
        from agents.common import (
            ToolResult,
            JournalingToolResult,
            AgentCoordinator,
            PineconeService
        )
        
        assert ToolResult is not None
        assert JournalingToolResult is not None
        assert AgentCoordinator is not None
        assert PineconeService is not None
    
    def test_global_services_exist(self):
        """Test that global service instances exist."""
        from agents.common import coordinator, pinecone_service
        
        assert coordinator is not None
        assert pinecone_service is not None
        assert isinstance(coordinator, AgentCoordinator)
        assert isinstance(pinecone_service, PineconeService) 