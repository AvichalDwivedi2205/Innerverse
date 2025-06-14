"""
Therapy Agent Module
Google ADK-powered agent for evidence-based therapeutic interventions
"""

from .agent_file import therapy_agent, TherapyAgent
from .prompt_file import therapy_prompts, TherapyPrompts
from .tool_file import (
    gemini_reasoning_tool,
    session_summary_tool,
    agent_coordination_tool,
    multimodal_content_tool
)

def validate_therapy_agent():
    """Validate therapy agent configuration"""
    print("Validating therapy agent...")
    
    # Check agent initialization
    if therapy_agent.gemini_client:
        print("✓ Therapy agent initialized with Google ADK")
        print(f"  - Crisis protocols: {'Active' if therapy_agent.crisis_protocols_active else 'Inactive'}")
        print(f"  - Therapeutic frameworks: {len(therapy_agent.frameworks.__dict__)} available")
    else:
        print("✗ Therapy agent initialization failed")
    
    # Check tools
    if gemini_reasoning_tool.client:
        print("✓ Gemini therapeutic reasoning tool configured")
        print(f"  - Context window: {gemini_reasoning_tool.context_window:,} tokens")
    else:
        print("✗ Gemini reasoning tool failed")
    
    if session_summary_tool.gemini_client:
        print("✓ Session summary tool configured")
    else:
        print("✗ Session summary tool failed")
    
    if agent_coordination_tool.adk_comm:
        print("✓ Agent coordination tool configured")
    else:
        print("✗ Agent coordination tool failed")
    
    # Check multi-modal capabilities
    if multimodal_content_tool.elevenlabs.api_key:
        print("✓ ElevenLabs voice synthesis available")
    else:
        print("⚠ ElevenLabs not configured - audio therapy disabled")
    
    if multimodal_content_tool.tavus.api_key:
        print("✓ Tavus video generation available")
    else:
        print("⚠ Tavus not configured - video therapy disabled")
    
    print("Therapy agent validation complete!")

# Auto-validate on import
validate_therapy_agent()

__all__ = [
    'therapy_agent',
    'TherapyAgent',
    'therapy_prompts',
    'TherapyPrompts',
    'gemini_reasoning_tool',
    'session_summary_tool',
    'agent_coordination_tool',
    'multimodal_content_tool'
]
