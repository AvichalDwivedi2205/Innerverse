"""ADK Agent entry point for Therapy Agent.

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
    from agents.therapy_agent.therapy_agent import therapy_agent
    root_agent = therapy_agent
except ImportError as e:
    # Fallback: create a minimal agent inline if imports fail
    from google.adk.agents import Agent
    from google.genai import types
    
    def simple_therapy_response(transcript: str) -> str:
        """Simple therapy response when full agent can't load."""
        return f"Thank you for sharing in our therapy session. I hear your concerns about: {transcript[:100]}... Let's explore how you can take empowered action in this situation."
    
    root_agent = Agent(
        model="gemini-2.5-pro",
        name="therapy_agent_fallback",
        instruction=f"""
        You are a therapy agent focused on empowerment and self-creation.
        Today's date: {date.today()}
        
        Help users shift from victim consciousness to creator consciousness.
        Focus on internal empowerment and personal responsibility.
        """,
        tools=[simple_therapy_response],
        generate_content_config=types.GenerateContentConfig(temperature=0.3),
    )

# Alternative export names that ADK might search for
agent = root_agent
main_agent = root_agent 