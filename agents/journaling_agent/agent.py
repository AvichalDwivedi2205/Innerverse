"""ADK Agent entry point for Journaling Agent.

This file exposes the root_agent that the ADK web interface expects to find.
"""

import os
import sys
from datetime import date

# Ensure the workspace root is in Python path
workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

# Now we can import with absolute paths
try:
    from agents.journaling_agent.journaling_agent import journaling_agent
    root_agent = journaling_agent
except ImportError as e:
    # Fallback: create a minimal agent inline if imports fail
    from google.adk.agents import Agent
    from google.genai import types
    
    def simple_journal_response(raw_text: str) -> str:
        """Simple journaling response when full agent can't load."""
        return f"Thank you for sharing your journal entry. I've received: {raw_text[:100]}... Your reflection shows self-awareness and growth mindset."
    
    # Configure model with proper API settings
    import os
    
    # Try to get Google AI API key first (simpler for local development)
    google_api_key = os.getenv('GOOGLE_API_KEY')
    vertex_project = os.getenv('GOOGLE_CLOUD_PROJECT') or os.getenv('VERTEX_AI_PROJECT')
    vertex_location = os.getenv('GOOGLE_CLOUD_REGION') or os.getenv('VERTEX_AI_LOCATION', 'us-central1')
    
    if google_api_key:
        # Use Google AI API with latest Gemini 2.5 Pro
        model_config = {
            "model": "gemini-2.5-pro",
            "api_key": google_api_key
        }
    elif vertex_project:
        # Use Vertex AI with latest Gemini 2.5 Pro model
        model_config = {
            "model": f"vertexai/{vertex_project}/{vertex_location}/gemini-2.5-pro"
        }
    else:
        # Fallback to latest Gemini model configuration
        model_config = {
            "model": "gemini-2.5-pro"
        }
    
    root_agent = Agent(
        name="journaling_agent_fallback",
        instruction=f"""
        You are a journaling agent focused on empowerment and self-creation.
        Today's date: {date.today()}
        
        Help users recognize they are creators of their experience through their thoughts and responses.
        Focus on internal empowerment rather than external circumstances.
        """,
        tools=[simple_journal_response],
        generate_content_config=types.GenerateContentConfig(temperature=0.3),
        **model_config
    )

# Alternative export names that ADK might search for
agent = root_agent
main_agent = root_agent 