import os
import logging
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass

# Note: In production, install with: pip install pinecone-client
try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    print("Pinecone not installed. Install with: pip install pinecone-client")

@dataclass
class VectorConfig:
    """Configuration for different vector types in mental health system"""
    name: str
    dimension: int
    metric: str
    description: str

class PineconeConfig:
    """Pinecone vector database configuration for mental health vectors"""
    
    # Vector configurations for mental health data
    VECTOR_CONFIGS = {
        'user_mental_profiles': VectorConfig(
            name='user-mental-profiles',
            dimension=768,
            metric='cosine',
            description='Comprehensive mental health profiles'
        ),
        'journal_entries': VectorConfig(
            name='journal-entries',
            dimension=768,
            metric='cosine',
            description='Daily emotional states and life events'
        ),
        'therapy_sessions': VectorConfig(
            name='therapy-sessions',
            dimension=768,
            metric='cosine',
            description='Therapeutic insights and progress'
        ),
        'mental_exercises': VectorConfig(
            name='mental-exercises',
            dimension=384,
            metric='cosine',
            description='Exercise recommendations and effectiveness'
        ),
        'progress_tracking': VectorConfig(
            name='progress-tracking',
            dimension=384,
            metric='cosine',
            description='Longitudinal health monitoring'
        )
    }
    
    def __init__(self):
        self.api_key = os.getenv('PINECONE_API_KEY')
        self.environment = os.getenv('PINECONE_ENVIRONMENT', 'us-east1-gcp')
        self.indexes = {}
        self._initialize_pinecone()
    
    def _initialize_pinecone(self):
        """Initialize Pinecone client and create indexes"""
        if not PINECONE_AVAILABLE:
            logging.warning("Pinecone not available. Vector operations will be mocked.")
            return
            
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY environment variable not set")
        
        try:
            # Initialize Pinecone
            pinecone.init(api_key=self.api_key, environment=self.environment)
            
            # Create indexes for each vector type
            for config_name, config in self.VECTOR_CONFIGS.items():
                self._create_or_connect_index(config)
                
            logging.info("Pinecone initialized successfully")
            
        except Exception as e:
            logging.error(f"Error initializing Pinecone: {e}")
            raise
    
    def _create_or_connect_index(self, config: VectorConfig):
        """Create or connect to a Pinecone index"""
        if not PINECONE_AVAILABLE:
            return
            
        try:
            if config.name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=config.name,
                    dimension=config.dimension,
                    metric=config.metric
                )
                logging.info(f"Created index: {config.name}")
            
            # Connect to the index
            self.indexes[config.name] = pinecone.Index(config.name)
            
        except Exception as e:
            logging.error(f"Error with index {config.name}: {e}")
    
    def upsert_vectors(self, index_name: str, vectors: List[Tuple[str, List[float], Dict[str, Any]]]):
        """Upsert vectors to specified index with metadata"""
        if not PINECONE_AVAILABLE or index_name not in self.indexes:
            logging.warning(f"Index {index_name} not available")
            return False
            
        try:
            self.indexes[index_name].upsert(vectors)
            return True
        except Exception as e:
            logging.error(f"Error upserting vectors to {index_name}: {e}")
            return False
    
    def query_vectors(self, index_name: str, vector: List[float], top_k: int = 10, filter_dict: Dict = None):
        """Query vectors from specified index"""
        if not PINECONE_AVAILABLE or index_name not in self.indexes:
            logging.warning(f"Index {index_name} not available")
            return []
            
        try:
            return self.indexes[index_name].query(
                vector=vector,
                top_k=top_k,
                filter=filter_dict,
                include_metadata=True
            )
        except Exception as e:
            logging.error(f"Error querying vectors from {index_name}: {e}")
            return []
    
    def get_index_stats(self, index_name: str):
        """Get statistics for specified index"""
        if not PINECONE_AVAILABLE or index_name not in self.indexes:
            return {}
            
        try:
            return self.indexes[index_name].describe_index_stats()
        except Exception as e:
            logging.error(f"Error getting stats for {index_name}: {e}")
            return {}

# Global Pinecone instance
pinecone_config = PineconeConfig()
