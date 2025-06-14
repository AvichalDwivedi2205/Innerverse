"""
Configuration module for wellness AI platform
Initializes Firebase, Pinecone, and API keys management
"""

from .firebase_config import firebase_config
from .vector_db_config import pinecone_config
from .api_keys import api_keys_manager, get_api_key, get_headers_for_service

# Validate configuration on import
def validate_configuration():
    """Validate that all essential services are properly configured"""
    print("Validating wellness AI platform configuration...")
    
    # Check Firebase
    if firebase_config.db is not None:
        print("✓ Firebase configured successfully")
    else:
        print("✗ Firebase configuration failed")
    
    # Check Pinecone
    if pinecone_config.indexes:
        print(f"✓ Pinecone configured with {len(pinecone_config.indexes)} indexes")
    else:
        print("✗ Pinecone configuration incomplete")
    
    # Check API keys
    available_keys = len(api_keys_manager.get_all_keys())
    print(f"✓ {available_keys} API keys loaded")
    
    print("Configuration validation complete!")

# Auto-validate on import
validate_configuration()

__all__ = [
    'firebase_config',
    'pinecone_config', 
    'api_keys_manager',
    'get_api_key',
    'get_headers_for_service'
]
