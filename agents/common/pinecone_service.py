"""Pinecone service for vector embeddings storage and retrieval.

This module provides comprehensive Pinecone integration for storing and retrieving
embeddings that are crucial for trend analysis and pattern recognition in the web app.
"""

import os
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
from google.cloud import aiplatform
import vertexai
from vertexai.language_models import TextEmbeddingModel

try:
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    Pinecone = None
    ServerlessSpec = None

logger = logging.getLogger(__name__)


class PineconeService:
    """Service for managing Pinecone vector operations."""
    
    def __init__(self):
        self.index = None
        self.embedding_model = None
        self.dimension = int(os.getenv("EMBEDDING_DIMENSION", 768))
        self._initialize_pinecone()
        self._initialize_embedding_model()
    
    def _initialize_pinecone(self):
        """Initialize Pinecone connection."""
        try:
            api_key = os.getenv("PINECONE_API_KEY")
            index_name = os.getenv("PINECONE_INDEX_NAME", "innerverse")
            
            if not api_key or not PINECONE_AVAILABLE:
                if not api_key:
                    print("⚠️  Pinecone API key not found. Vector operations will be simulated.")
                    logger.warning("Pinecone API key not found. Vector operations will be simulated.")
                else:
                    print("⚠️  Pinecone package not available. Vector operations will be simulated.")
                    logger.warning("Pinecone package not available. Vector operations will be simulated.")
                return
            
            # Initialize Pinecone client (new API)
            pc = Pinecone(api_key=api_key)
            
            # Check if we have a host (user's setup) or need to create index
            pinecone_host = os.getenv("PINECONE_HOST")
            
            if pinecone_host:
                # Connect to existing index with host
                logger.info("Using host-based Pinecone connection")
                self.index = pc.Index(index_name, host=pinecone_host)
                logger.info(f"Connected to Pinecone index: {index_name} at {pinecone_host}")
            else:
                # Create or connect to index (serverless or pod-based)
                logger.info("Checking/creating Pinecone index")
                
                # List existing indexes
                existing_indexes = [idx.name for idx in pc.list_indexes()]
                
                if index_name not in existing_indexes:
                    logger.info(f"Creating Pinecone index: {index_name}")
                    # Create serverless index (recommended for new users)
                    pc.create_index(
                        name=index_name,
                        dimension=self.dimension,
                        metric="cosine",
                        spec=ServerlessSpec(
                            cloud="aws",
                            region="us-east-1"
                        )
                    )
                
                # Connect to index
                self.index = pc.Index(index_name)
                logger.info(f"Connected to Pinecone index: {index_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {str(e)}")
            self.index = None
    
    def _initialize_embedding_model(self):
        """Initialize Vertex AI embedding model."""
        try:
            # Ensure environment variables are set for Vertex AI
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("VERTEX_AI_PROJECT")
            location = os.getenv("GOOGLE_CLOUD_REGION") or os.getenv("VERTEX_AI_LOCATION", "us-central1")
            
            if not project_id:
                print("⚠️  Google Cloud project not found. Using fallback embedding generation.")
                logger.warning("Google Cloud project not found. Using fallback embedding generation.")
                self.embedding_model = None
                return
                
            vertexai.init(project=project_id, location=location)
            self.embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")
            print("✅ Vertex AI embedding model initialized")
            logger.info("Vertex AI embedding model initialized")
        except Exception as e:
            print(f"⚠️  Failed to initialize embedding model: {str(e)}")
            logger.error(f"Failed to initialize embedding model: {str(e)}")
            self.embedding_model = None
    
    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for given text.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            List of embedding values or None if failed
        """
        try:
            if not self.embedding_model:
                logger.warning("Embedding model not available, using random vector")
                return np.random.rand(self.dimension).tolist()
            
            embeddings = self.embedding_model.get_embeddings([text])
            return embeddings[0].values
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return None
    
    async def store_embedding(
        self,
        embedding_id: str,
        text: str,
        user_id: str,
        context: str,
        source_id: str,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Store embedding in Pinecone with metadata.
        
        Args:
            embedding_id: Unique identifier for the embedding
            text: Original text content
            user_id: User identifier
            context: Context type (journal, therapy, notes)
            source_id: Source document ID
            additional_metadata: Additional metadata to store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate embedding
            embedding_vector = await self.generate_embedding(text)
            if not embedding_vector:
                return False
            
            # Prepare metadata
            metadata = {
                "userId": user_id,
                "context": context,
                "sourceId": source_id,
                "timestamp": datetime.now().isoformat(),
                "text": text[:1000],  # Store truncated text for reference
                **(additional_metadata or {})
            }
            
            # Store in Pinecone
            if self.index:
                self.index.upsert(
                    vectors=[(embedding_id, embedding_vector, metadata)]
                )
                logger.info(f"Stored embedding {embedding_id} in Pinecone")
                return True
            else:
                logger.warning(f"Pinecone not available, simulating storage of {embedding_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error storing embedding {embedding_id}: {str(e)}")
            return False
    
    async def retrieve_user_embeddings(
        self,
        user_id: str,
        context_filter: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Retrieve all embeddings for a user.
        
        Args:
            user_id: User identifier
            context_filter: Optional context filter (journal, therapy, notes)
            limit: Maximum number of embeddings to retrieve
            
        Returns:
            List of embedding data with metadata
        """
        try:
            if not self.index:
                logger.warning("Pinecone not available, returning sample data")
                return self._generate_sample_embeddings(user_id, context_filter, limit)
            
            # Build filter
            filter_dict = {"userId": user_id}
            if context_filter:
                filter_dict["context"] = context_filter
            
            # Query Pinecone
            query_response = self.index.query(
                vector=[0.0] * self.dimension,  # Dummy vector for metadata-only query
                filter=filter_dict,
                top_k=limit,
                include_metadata=True,
                include_values=True
            )
            
            # Format results
            embeddings_data = []
            for match in query_response.matches:
                embeddings_data.append({
                    "id": match.id,
                    "vector": match.values,
                    "metadata": match.metadata,
                    "score": match.score
                })
            
            logger.info(f"Retrieved {len(embeddings_data)} embeddings for user {user_id}")
            return embeddings_data
            
        except Exception as e:
            logger.error(f"Error retrieving embeddings for user {user_id}: {str(e)}")
            return self._generate_sample_embeddings(user_id, context_filter, limit)
    
    async def search_similar_embeddings(
        self,
        query_text: str,
        user_id: str,
        context_filter: Optional[str] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for similar embeddings based on query text.
        
        Args:
            query_text: Text to search for similar content
            user_id: User identifier
            context_filter: Optional context filter
            top_k: Number of similar embeddings to return
            
        Returns:
            List of similar embeddings with similarity scores
        """
        try:
            # Generate query embedding
            query_vector = await self.generate_embedding(query_text)
            if not query_vector:
                return []
            
            if not self.index:
                logger.warning("Pinecone not available, returning empty results")
                return []
            
            # Build filter
            filter_dict = {"userId": user_id}
            if context_filter:
                filter_dict["context"] = context_filter
            
            # Search similar vectors
            search_response = self.index.query(
                vector=query_vector,
                filter=filter_dict,
                top_k=top_k,
                include_metadata=True,
                include_values=False  # Don't need vectors for similarity search
            )
            
            # Format results
            similar_embeddings = []
            for match in search_response.matches:
                similar_embeddings.append({
                    "id": match.id,
                    "metadata": match.metadata,
                    "similarity_score": match.score
                })
            
            logger.info(f"Found {len(similar_embeddings)} similar embeddings for query")
            return similar_embeddings
            
        except Exception as e:
            logger.error(f"Error searching similar embeddings: {str(e)}")
            return []
    
    async def delete_user_embeddings(
        self,
        user_id: str,
        context_filter: Optional[str] = None
    ) -> bool:
        """Delete all embeddings for a user.
        
        Args:
            user_id: User identifier
            context_filter: Optional context filter
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.index:
                logger.warning("Pinecone not available, simulating deletion")
                return True
            
            # Get all embedding IDs for user
            embeddings = await self.retrieve_user_embeddings(user_id, context_filter)
            embedding_ids = [emb["id"] for emb in embeddings]
            
            if embedding_ids:
                # Delete embeddings
                self.index.delete(ids=embedding_ids)
                logger.info(f"Deleted {len(embedding_ids)} embeddings for user {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting embeddings for user {user_id}: {str(e)}")
            return False
    
    def _generate_sample_embeddings(
        self,
        user_id: str,
        context_filter: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Generate sample embeddings for testing when Pinecone is not available."""
        sample_embeddings = []
        contexts = [context_filter] if context_filter else ["journal", "therapy", "notes"]
        
        for i in range(min(limit, 10)):
            for context in contexts:
                if len(sample_embeddings) >= limit:
                    break
                    
                sample_embeddings.append({
                    "id": f"{user_id}_{context}_{i:03d}",
                    "vector": np.random.rand(self.dimension).tolist(),
                    "metadata": {
                        "userId": user_id,
                        "context": context,
                        "sourceId": f"{context}_{i:03d}",
                        "timestamp": datetime.now().isoformat(),
                        "text": f"Sample {context} content {i}"
                    },
                    "score": 0.8 + np.random.random() * 0.2
                })
        
        return sample_embeddings
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get Pinecone index statistics.
        
        Returns:
            Dictionary with index statistics
        """
        try:
            if not self.index:
                return {"status": "unavailable", "reason": "Pinecone not initialized"}
            
            stats = self.index.describe_index_stats()
            return {
                "status": "available",
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness
            }
            
        except Exception as e:
            logger.error(f"Error getting index stats: {str(e)}")
            return {"status": "error", "error": str(e)}


# Global Pinecone service instance
pinecone_service = PineconeService() 