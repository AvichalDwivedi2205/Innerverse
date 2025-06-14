import os
from typing import Optional, Dict
from dataclasses import dataclass

@dataclass
class APIKeyConfig:
    """Configuration for API keys with validation"""
    key_name: str
    env_var: str
    required: bool = True
    description: str = ""

class APIKeysManager:
    """Centralized API keys management for wellness AI platform"""
    
    # Define all API keys used in the platform
    API_CONFIGS = {
        'google_adk': APIKeyConfig(
            key_name='google_adk',
            env_var='GOOGLE_ADK_API_KEY',
            required=True,
            description='Google Agent Development Kit API key'
        ),
        'gemini_2_5_pro': APIKeyConfig(
            key_name='gemini_2_5_pro',
            env_var='GEMINI_2_5_PRO_API_KEY',
            required=True,
            description='Gemini 2.5 Pro API key for advanced reasoning'
        ),
        'gemini_embedding': APIKeyConfig(
            key_name='gemini_embedding',
            env_var='GEMINI_EMBEDDING_API_KEY',
            required=True,
            description='Gemini Embedding model API key'
        ),
        'elevenlabs': APIKeyConfig(
            key_name='elevenlabs',
            env_var='ELEVENLABS_API_KEY',
            required=True,
            description='ElevenLabs voice synthesis API key'
        ),
        'tavus': APIKeyConfig(
            key_name='tavus',
            env_var='TAVUS_API_KEY',
            required=True,
            description='Tavus video generation API key'
        ),
        'google_speech': APIKeyConfig(
            key_name='google_speech',
            env_var='GOOGLE_SPEECH_API_KEY',
            required=True,
            description='Google Speech-to-Text API key'
        ),
        'google_calendar': APIKeyConfig(
            key_name='google_calendar',
            env_var='GOOGLE_CALENDAR_API_KEY',
            required=False,
            description='Google Calendar API key'
        ),
        'gmail_api': APIKeyConfig(
            key_name='gmail_api',
            env_var='GMAIL_API_KEY',
            required=False,
            description='Gmail API key for reminders'
        ),
        'pinecone': APIKeyConfig(
            key_name='pinecone',
            env_var='PINECONE_API_KEY',
            required=True,
            description='Pinecone vector database API key'
        )
    }
    
    def __init__(self):
        self.api_keys = {}
        self._load_api_keys()
        self._validate_required_keys()
    
    def _load_api_keys(self):
        """Load all API keys from environment variables"""
        for key_name, config in self.API_CONFIGS.items():
            api_key = os.getenv(config.env_var)
            if api_key:
                self.api_keys[key_name] = api_key
            elif config.required:
                print(f"Warning: Required API key {config.env_var} not found")
    
    def _validate_required_keys(self):
        """Validate that all required API keys are present"""
        missing_keys = []
        for key_name, config in self.API_CONFIGS.items():
            if config.required and key_name not in self.api_keys:
                missing_keys.append(config.env_var)
        
        if missing_keys:
            raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")
    
    def get_api_key(self, service_name: str) -> Optional[str]:
        """Get API key for specified service"""
        return self.api_keys.get(service_name)
    
    def get_all_keys(self) -> Dict[str, str]:
        """Get all loaded API keys"""
        return self.api_keys.copy()
    
    def is_service_available(self, service_name: str) -> bool:
        """Check if API key is available for service"""
        return service_name in self.api_keys
    
    def get_headers_for_service(self, service_name: str) -> Dict[str, str]:
        """Get authentication headers for specific service"""
        api_key = self.get_api_key(service_name)
        if not api_key:
            return {}
        
        # Service-specific header formats
        header_formats = {
            'google_adk': {'Authorization': f'Bearer {api_key}'},
            'gemini_2_5_pro': {'Authorization': f'Bearer {api_key}'},
            'gemini_embedding': {'Authorization': f'Bearer {api_key}'},
            'elevenlabs': {'xi-api-key': api_key},
            'tavus': {'x-api-key': api_key},
            'google_speech': {'Authorization': f'Bearer {api_key}'},
            'google_calendar': {'Authorization': f'Bearer {api_key}'},
            'gmail_api': {'Authorization': f'Bearer {api_key}'}
        }
        
        return header_formats.get(service_name, {'Authorization': f'Bearer {api_key}'})

# Global API keys manager
api_keys_manager = APIKeysManager()

# Convenience functions for backward compatibility
def get_api_key(service_name: str) -> Optional[str]:
    """Get API key for specified service"""
    return api_keys_manager.get_api_key(service_name)

def get_headers_for_service(service_name: str) -> Dict[str, str]:
    """Get authentication headers for specific service"""
    return api_keys_manager.get_headers_for_service(service_name)
