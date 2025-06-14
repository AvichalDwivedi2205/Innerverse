"""
Journaling Agent Module
Google ADK-powered agent for emotional state tracking and journal processing
"""

from .agent_file import journaling_agent, JournalingAgent
from .prompt_file import JournalingPrompts
from .tool_file import (
    speech_to_text_tool,
    firebase_storage_tool,
    vector_database_tool,
    gemini_analysis_tool
)

def validate_journaling_agent():
    """Validate journaling agent configuration"""
    print("Validating journaling agent...")
    
    # Check agent initialization
    if journaling_agent.gemini_client:
        print("✓ Journaling agent initialized with Google ADK")
    else:
        print("✗ Journaling agent initialization failed")
    
    # Check tools
    if speech_to_text_tool.client or speech_to_text_tool.api_key:
        print("✓ Speech-to-Text tool configured")
    else:
        print("⚠ Speech-to-Text using mock responses")
    
    if firebase_storage_tool.db:
        print("✓ Firebase storage tool configured")
    else:
        print("✗ Firebase storage tool failed")
    
    if vector_database_tool.vector_ops:
        print("✓ Vector database tool configured")
    else:
        print("✗ Vector database tool failed")
    
    if gemini_analysis_tool.client:
        print("✓ Gemini analysis tool configured")
    else:
        print("✗ Gemini analysis tool failed")
    
    print("Journaling agent validation complete!")

# Auto-validate on import
validate_journaling_agent()

__all__ = [
    'journaling_agent',
    'JournalingAgent',
    'JournalingPrompts',
    'speech_to_text_tool',
    'firebase_storage_tool',
    'vector_database_tool',
    'gemini_analysis_tool'
]
