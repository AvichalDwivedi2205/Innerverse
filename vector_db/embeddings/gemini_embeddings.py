import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from google import genai
from google.genai.types import EmbedContentConfig

from config.api_keys import get_api_key

@dataclass
class EmbeddingRequest:
    """Request structure for embedding generation"""
    text: str
    task_type: str = "RETRIEVAL_DOCUMENT"
    title: Optional[str] = None
    metadata: Dict[str, Any] = None

class GeminiEmbeddingGenerator:
    """Gemini-powered embedding generation for mental health data"""
    
    # Model configurations for different mental health data types
    MODEL_CONFIGS = {
        'mental_health_768': {
            'model': 'gemini-embedding-exp-03-07',
            'dimension': 768,
            'task_type': 'RETRIEVAL_DOCUMENT'
        },
        'mental_exercises_384': {
            'model': 'text-embedding-004',
            'dimension': 384,
            'task_type': 'CLASSIFICATION'
        }
    }
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Gemini client with API key"""
        try:
            api_key = get_api_key('gemini_embedding')
            if not api_key:
                raise ValueError("Gemini Embedding API key not found")
            
            self.client = genai.Client(api_key=api_key)
            logging.info("Gemini embedding client initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to initialize Gemini client: {e}")
            raise
    
    async def generate_mental_health_embedding(self, text: str, title: str = None) -> List[float]:
        """Generate 768-dimensional embedding for mental health content"""
        return await self._generate_embedding(
            text=text,
            config_key='mental_health_768',
            title=title
        )
    
    async def generate_exercise_embedding(self, text: str, title: str = None) -> List[float]:
        """Generate 384-dimensional embedding for mental exercises"""
        return await self._generate_embedding(
            text=text,
            config_key='mental_exercises_384',
            title=title
        )
    
    async def _generate_embedding(self, text: str, config_key: str, title: str = None) -> List[float]:
        """Internal method to generate embeddings with specific configuration"""
        if not self.client:
            raise RuntimeError("Gemini client not initialized")
        
        config = self.MODEL_CONFIGS[config_key]
        
        try:
            response = await asyncio.to_thread(
                self.client.models.embed_content,
                model=config['model'],
                contents=text,
                config=EmbedContentConfig(
                    task_type=config['task_type'],
                    output_dimensionality=config['dimension'],
                    title=title
                )
            )
            
            if response.embeddings and len(response.embeddings) > 0:
                return response.embeddings[0].values
            else:
                raise ValueError("No embeddings returned from Gemini API")
                
        except Exception as e:
            logging.error(f"Error generating embedding: {e}")
            raise
    
    async def batch_generate_embeddings(self, requests: List[EmbeddingRequest], config_key: str) -> List[List[float]]:
        """Generate embeddings for multiple texts in batch"""
        tasks = []
        for request in requests:
            task = self._generate_embedding(
                text=request.text,
                config_key=config_key,
                title=request.title
            )
            tasks.append(task)
        
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    def preprocess_journal_entry(self, entry: Dict[str, Any]) -> str:
        """Preprocess journal entry for optimal embedding generation"""
        components = []
        
        # Add emotional context
        if 'mood' in entry:
            components.append(f"Mood: {entry['mood']}")
        
        # Add main content
        if 'content' in entry:
            components.append(f"Journal Entry: {entry['content']}")
        
        # Add triggers if present
        if 'triggers' in entry and entry['triggers']:
            components.append(f"Triggers: {', '.join(entry['triggers'])}")
        
        # Add coping mechanisms
        if 'coping_mechanisms' in entry and entry['coping_mechanisms']:
            components.append(f"Coping: {', '.join(entry['coping_mechanisms'])}")
        
        return " | ".join(components)
    
    def preprocess_therapy_session(self, session: Dict[str, Any]) -> str:
        """Preprocess therapy session for optimal embedding generation"""
        components = []
        
        # Add session type
        if 'session_type' in session:
            components.append(f"Session Type: {session['session_type']}")
        
        # Add therapeutic framework
        if 'framework' in session:
            components.append(f"Framework: {session['framework']}")
        
        # Add key insights
        if 'insights' in session:
            components.append(f"Insights: {session['insights']}")
        
        # Add progress notes
        if 'progress_notes' in session:
            components.append(f"Progress: {session['progress_notes']}")
        
        # Add homework assignments
        if 'homework' in session and session['homework']:
            components.append(f"Homework: {', '.join(session['homework'])}")
        
        return " | ".join(components)
    
    def preprocess_mental_profile(self, profile: Dict[str, Any]) -> str:
        """Preprocess mental health profile for comprehensive embedding"""
        components = []
        
        # Add current mental state
        if 'current_state' in profile:
            components.append(f"Current State: {profile['current_state']}")
        
        # Add diagnosed conditions
        if 'conditions' in profile and profile['conditions']:
            components.append(f"Conditions: {', '.join(profile['conditions'])}")
        
        # Add therapeutic goals
        if 'goals' in profile and profile['goals']:
            components.append(f"Goals: {', '.join(profile['goals'])}")
        
        # Add preferred coping strategies
        if 'preferred_coping' in profile and profile['preferred_coping']:
            components.append(f"Preferred Coping: {', '.join(profile['preferred_coping'])}")
        
        # Add risk factors
        if 'risk_factors' in profile and profile['risk_factors']:
            components.append(f"Risk Factors: {', '.join(profile['risk_factors'])}")
        
        return " | ".join(components)

# Global embedding generator instance
gemini_embeddings = GeminiEmbeddingGenerator()
