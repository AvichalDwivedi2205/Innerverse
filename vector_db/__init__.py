"""
Vector Database Module for Mental Health Data
Handles embedding generation, vector schemas, and advanced operations
"""

from .embeddings.gemini_embeddings import gemini_embeddings, GeminiEmbeddingGenerator
from .schemas.mental_health_schemas import (
    VectorType, 
    BaseVectorSchema,
    UserMentalProfileVector,
    JournalEntryVector,
    TherapySessionVector,
    MentalExerciseVector,
    ProgressTrackingVector,
    VectorSchemaFactory
)
from .utils.vector_operations import vector_ops, VectorOperations

# Validation function for vector database setup
def validate_vector_db_setup():
    """Validate that vector database components are properly configured"""
    print("Validating vector database setup...")
    
    # Check embedding generator
    if gemini_embeddings.client:
        print("✓ Gemini embedding generator initialized")
    else:
        print("✗ Gemini embedding generator failed to initialize")
    
    # Check Pinecone configuration
    if vector_ops.pinecone_config.indexes:
        print(f"✓ Pinecone configured with {len(vector_ops.pinecone_config.indexes)} indexes")
    else:
        print("✗ Pinecone indexes not properly configured")
    
    # Validate schema dimensions
    for vector_type in VectorType:
        expected_dims = VectorSchemaFactory.get_expected_dimensions(vector_type)
        print(f"✓ {vector_type.value}: {expected_dims} dimensions")
    
    print("Vector database validation complete!")

# Auto-validate on import
validate_vector_db_setup()

__all__ = [
    'gemini_embeddings',
    'GeminiEmbeddingGenerator',
    'VectorType',
    'BaseVectorSchema',
    'UserMentalProfileVector',
    'JournalEntryVector', 
    'TherapySessionVector',
    'MentalExerciseVector',
    'ProgressTrackingVector',
    'VectorSchemaFactory',
    'vector_ops',
    'VectorOperations'
]
