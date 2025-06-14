"""
Mental Orchestration Agent Module
Google ADK-powered central coordinator for mental health data integration
"""

from .agent_file import mental_orchestration_agent, MentalOrchestrationAgent
from .prompt_file import orchestration_prompts, OrchestrationPrompts
from .tool_file import (
    vector_clustering_tool,
    pattern_identification_tool,
    progress_tracking_tool
)

def validate_mental_orchestration_agent():
    """Validate mental orchestration agent configuration"""
    print("Validating mental orchestration agent...")
    
    # Check agent initialization
    if mental_orchestration_agent.gemini_client:
        print("✓ Mental orchestration agent initialized with Google ADK")
        print(f"  - Context window: {mental_orchestration_agent.context_window:,} tokens")
    else:
        print("✗ Mental orchestration agent initialization failed")
    
    # Check tools
    if vector_clustering_tool.gemini_client:
        print("✓ Vector clustering tool configured")
    else:
        print("✗ Vector clustering tool failed")
    
    if pattern_identification_tool.gemini_client:
        print("✓ Pattern identification tool configured")
    else:
        print("✗ Pattern identification tool failed")
    
    if progress_tracking_tool.firebase_db:
        print("✓ Progress tracking tool configured")
    else:
        print("✗ Progress tracking tool failed")
    
    print("Mental orchestration agent validation complete!")

# Auto-validate on import
validate_mental_orchestration_agent()

__all__ = [
    'mental_orchestration_agent',
    'MentalOrchestrationAgent',
    'orchestration_prompts',
    'OrchestrationPrompts',
    'vector_clustering_tool',
    'pattern_identification_tool',
    'progress_tracking_tool'
]
