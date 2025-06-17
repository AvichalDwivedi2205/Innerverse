"""Tests for Pinecone service."""

import pytest
import os
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from agents.common.pinecone_service import PineconeService, pinecone_service


class TestPineconeService:
    """Test cases for PineconeService class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create a fresh service instance for testing
        self.service = PineconeService()
        self.test_user_id = "test_user_123"
        self.test_text = "I feel empowered when I realize I create my own experiences."
        self.test_context = "journal"
        self.test_source_id = "journal_456"
    
    @pytest.mark.asyncio
    @patch('agents.common.pinecone_service.TextEmbeddingModel')
    async def test_generate_embedding_success(self, mock_embedding_model):
        """Test successful embedding generation."""
        # Mock the embedding model response
        mock_model_instance = Mock()
        mock_embedding = Mock()
        mock_embedding.values = [0.1, 0.2, 0.3] * 256  # 768 dimensions
        mock_model_instance.get_embeddings.return_value = [mock_embedding]
        mock_embedding_model.from_pretrained.return_value = mock_model_instance
        
        # Update service with mock model
        self.service.embedding_model = mock_model_instance
        
        # Test embedding generation
        result = await self.service.generate_embedding(self.test_text)
        
        assert result is not None
        assert len(result) == 768  # Expected embedding dimension
        assert isinstance(result, list)
        mock_model_instance.get_embeddings.assert_called_once_with([self.test_text])
    
    @pytest.mark.asyncio
    async def test_generate_embedding_fallback(self):
        """Test embedding generation fallback when model not available."""
        # Set model to None to trigger fallback
        self.service.embedding_model = None
        
        result = await self.service.generate_embedding(self.test_text)
        
        assert result is not None
        assert len(result) == self.service.dimension
        assert isinstance(result, list)
        # Should be random values between 0 and 1
        assert all(0 <= val <= 1 for val in result)
    
    @pytest.mark.asyncio
    @patch('agents.common.pinecone_service.pinecone')
    async def test_store_embedding_with_pinecone(self, mock_pinecone_module):
        """Test storing embedding when Pinecone is available."""
        # Mock Pinecone index
        mock_index = Mock()
        self.service.index = mock_index
        
        # Mock embedding generation
        with patch.object(self.service, 'generate_embedding') as mock_generate:
            mock_generate.return_value = [0.1] * 768
            
            # Test storing embedding
            result = await self.service.store_embedding(
                embedding_id="test_embedding_123",
                text=self.test_text,
                user_id=self.test_user_id,
                context=self.test_context,
                source_id=self.test_source_id
            )
            
            assert result is True
            mock_index.upsert.assert_called_once()
            
            # Verify upsert was called with correct structure
            call_args = mock_index.upsert.call_args[1]["vectors"]
            embedding_data = call_args[0]
            assert embedding_data[0] == "test_embedding_123"  # ID
            assert len(embedding_data[1]) == 768  # Vector
            assert embedding_data[2]["userId"] == self.test_user_id  # Metadata
    
    @pytest.mark.asyncio
    async def test_store_embedding_without_pinecone(self):
        """Test storing embedding when Pinecone is not available."""
        # Set index to None to simulate unavailable Pinecone
        self.service.index = None
        
        # Mock embedding generation
        with patch.object(self.service, 'generate_embedding') as mock_generate:
            mock_generate.return_value = [0.1] * 768
            
            # Test storing embedding (should succeed with simulation)
            result = await self.service.store_embedding(
                embedding_id="test_embedding_123",
                text=self.test_text,
                user_id=self.test_user_id,
                context=self.test_context,
                source_id=self.test_source_id
            )
            
            assert result is True  # Should succeed even without Pinecone
    
    @pytest.mark.asyncio
    async def test_store_embedding_generation_failure(self):
        """Test storing embedding when embedding generation fails."""
        # Mock embedding generation failure
        with patch.object(self.service, 'generate_embedding') as mock_generate:
            mock_generate.return_value = None
            
            # Test storing embedding
            result = await self.service.store_embedding(
                embedding_id="test_embedding_123",
                text=self.test_text,
                user_id=self.test_user_id,
                context=self.test_context,
                source_id=self.test_source_id
            )
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_retrieve_user_embeddings_with_pinecone(self):
        """Test retrieving embeddings when Pinecone is available."""
        # Mock Pinecone index and response
        mock_index = Mock()
        mock_match1 = Mock()
        mock_match1.id = f"{self.test_user_id}_journal_001"
        mock_match1.values = [0.1] * 768
        mock_match1.metadata = {"userId": self.test_user_id, "context": "journal"}
        mock_match1.score = 0.95
        
        mock_match2 = Mock()
        mock_match2.id = f"{self.test_user_id}_therapy_001"
        mock_match2.values = [0.2] * 768
        mock_match2.metadata = {"userId": self.test_user_id, "context": "therapy"}
        mock_match2.score = 0.87
        
        mock_response = Mock()
        mock_response.matches = [mock_match1, mock_match2]
        mock_index.query.return_value = mock_response
        
        self.service.index = mock_index
        
        # Test retrieving embeddings
        result = await self.service.retrieve_user_embeddings(self.test_user_id)
        
        assert len(result) == 2
        assert result[0]["id"] == f"{self.test_user_id}_journal_001"
        assert result[1]["id"] == f"{self.test_user_id}_therapy_001"
        assert all("metadata" in emb for emb in result)
        assert all("vector" in emb for emb in result)
        assert all("score" in emb for emb in result)
    
    @pytest.mark.asyncio
    async def test_retrieve_user_embeddings_without_pinecone(self):
        """Test retrieving embeddings when Pinecone is not available."""
        # Set index to None
        self.service.index = None
        
        # Test retrieving embeddings (should return sample data)
        result = await self.service.retrieve_user_embeddings(self.test_user_id)
        
        assert len(result) > 0
        assert all("id" in emb for emb in result)
        assert all("vector" in emb for emb in result)
        assert all("metadata" in emb for emb in result)
        assert all(emb["metadata"]["userId"] == self.test_user_id for emb in result)
    
    @pytest.mark.asyncio
    async def test_retrieve_user_embeddings_with_context_filter(self):
        """Test retrieving embeddings with context filter."""
        # Set index to None to use sample data
        self.service.index = None
        
        # Test with context filter
        result = await self.service.retrieve_user_embeddings(
            self.test_user_id,
            context_filter="journal"
        )
        
        assert len(result) > 0
        assert all(emb["metadata"]["context"] == "journal" for emb in result)
    
    @pytest.mark.asyncio
    async def test_search_similar_embeddings(self):
        """Test searching for similar embeddings."""
        # Set index to None (will return empty results but test the flow)
        self.service.index = None
        
        # Mock embedding generation
        with patch.object(self.service, 'generate_embedding') as mock_generate:
            mock_generate.return_value = [0.1] * 768
            
            # Test similarity search
            result = await self.service.search_similar_embeddings(
                query_text="I feel stressed about work",
                user_id=self.test_user_id,
                context_filter="journal",
                top_k=5
            )
            
            # Without real Pinecone, should return empty
            assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_delete_user_embeddings(self):
        """Test deleting user embeddings."""
        # Mock the retrieval and deletion
        with patch.object(self.service, 'retrieve_user_embeddings') as mock_retrieve:
            mock_retrieve.return_value = [
                {"id": f"{self.test_user_id}_journal_001"},
                {"id": f"{self.test_user_id}_therapy_001"}
            ]
            
            # Mock Pinecone index
            mock_index = Mock()
            self.service.index = mock_index
            
            # Test deletion
            result = await self.service.delete_user_embeddings(self.test_user_id)
            
            assert result is True
            mock_index.delete.assert_called_once()
    
    def test_get_index_stats_unavailable(self):
        """Test getting index stats when Pinecone is unavailable."""
        self.service.index = None
        
        stats = self.service.get_index_stats()
        
        assert stats["status"] == "unavailable"
        assert "reason" in stats
    
    def test_get_index_stats_available(self):
        """Test getting index stats when Pinecone is available."""
        # Mock Pinecone index with stats
        mock_index = Mock()
        mock_stats = Mock()
        mock_stats.total_vector_count = 1000
        mock_stats.dimension = 768
        mock_stats.index_fullness = 0.5
        mock_index.describe_index_stats.return_value = mock_stats
        
        self.service.index = mock_index
        
        stats = self.service.get_index_stats()
        
        assert stats["status"] == "available"
        assert stats["total_vector_count"] == 1000
        assert stats["dimension"] == 768
        assert stats["index_fullness"] == 0.5
    
    def test_generate_sample_embeddings(self):
        """Test sample embedding generation."""
        embeddings = self.service._generate_sample_embeddings(
            user_id=self.test_user_id,
            context_filter="journal",
            limit=5
        )
        
        assert len(embeddings) <= 5
        assert all(emb["metadata"]["userId"] == self.test_user_id for emb in embeddings)
        assert all(emb["metadata"]["context"] == "journal" for emb in embeddings)
        assert all(len(emb["vector"]) == self.service.dimension for emb in embeddings)


class TestGlobalPineconeService:
    """Test cases for global Pinecone service instance."""
    
    def test_global_service_exists(self):
        """Test that global Pinecone service exists."""
        assert pinecone_service is not None
        assert isinstance(pinecone_service, PineconeService)
    
    def test_global_service_initialized(self):
        """Test that global service has proper configuration."""
        assert hasattr(pinecone_service, 'dimension')
        assert pinecone_service.dimension > 0
        assert hasattr(pinecone_service, 'index')
        assert hasattr(pinecone_service, 'embedding_model')


class TestPineconeIntegration:
    """Integration tests for Pinecone service with trend analysis."""
    
    @pytest.mark.asyncio
    async def test_trend_analysis_workflow(self):
        """Test complete workflow for trend analysis."""
        service = PineconeService()
        service.index = None  # Use simulation mode
        
        # Simulate storing multiple journal entries over time
        user_id = "trend_test_user"
        journal_entries = [
            "Today I felt anxious about my presentation at work.",
            "I realized my anxiety comes from my need for perfection.",
            "I'm practicing self-compassion and it's helping with anxiety.",
            "Work stress is decreasing as I set better boundaries.",
            "I feel more confident and in control of my responses."
        ]
        
        # Store embeddings for each entry
        embedding_ids = []
        for i, entry in enumerate(journal_entries):
            embedding_id = f"{user_id}_journal_{i:03d}"
            success = await service.store_embedding(
                embedding_id=embedding_id,
                text=entry,
                user_id=user_id,
                context="journal",
                source_id=f"journal_{i:03d}",
                additional_metadata={"entry_number": i, "trend_test": True}
            )
            assert success
            embedding_ids.append(embedding_id)
        
        # Retrieve all embeddings for trend analysis
        all_embeddings = await service.retrieve_user_embeddings(user_id)
        assert len(all_embeddings) >= len(journal_entries)
        
        # Test context-specific retrieval (crucial for web app)
        journal_embeddings = await service.retrieve_user_embeddings(
            user_id, 
            context_filter="journal"
        )
        assert len(journal_embeddings) >= len(journal_entries)
        
        # Test similarity search (for finding patterns)
        similar = await service.search_similar_embeddings(
            query_text="anxiety and stress management",
            user_id=user_id,
            context_filter="journal",
            top_k=3
        )
        assert isinstance(similar, list)  # Will be empty in simulation mode
        
        # Clean up
        cleanup_success = await service.delete_user_embeddings(user_id)
        assert cleanup_success 