"""ADK Agent entry point for Mental Orchestrator Agent.

This file exposes the root_agent that the ADK web interface expects to find.
"""

import os
import sys
from datetime import date

# Ensure the workspace root is in Python path
workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

# Now we can import with both relative and absolute paths
try:
    # Try relative import first (when loaded as part of package)
    from .mental_orchestrator_agent import mental_orchestrator_agent
    root_agent = mental_orchestrator_agent
except ImportError:
    # Fall back to absolute import (when loaded directly by ADK)
    try:
        from agents.mental_orchestrator_agent.mental_orchestrator_agent import mental_orchestrator_agent
        root_agent = mental_orchestrator_agent
    except ImportError as e:
        # Fallback: create a minimal agent inline if imports fail
        from google.adk.agents import Agent
        from google.genai import types
        
        def simple_orchestrator_response(trigger_data: str) -> str:
            """Simple orchestrator response when full agent can't load."""
            return f"Mental orchestration triggered. Processing data: {trigger_data[:100]}... Analyzing patterns for empowerment insights and mind map updates."
        
        root_agent = Agent(
            model="gemini-2.5-flash",
            name="mental_orchestrator_agent_fallback",
            instruction=f"""
            You are a mental orchestrator agent focused on empowerment and self-creation.
            Today's date: {date.today()}
            
            Analyze patterns and provide insights for user empowerment.
            Focus on internal awareness and personal growth.
            """,
            tools=[simple_orchestrator_response],
            generate_content_config=types.GenerateContentConfig(temperature=0.2),
        )

# Alternative export names that ADK might search for
agent = root_agent
main_agent = root_agent 