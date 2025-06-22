"""ADK Agent entry point for Mental Orchestrator Agent.

This file exposes the root_agent that the ADK web interface expects to find.
"""

import os
import sys
from datetime import date

# Ensure the workspace root is in Python path - try multiple approaches
workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

# Also add the agents directory to path
agents_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if agents_dir not in sys.path:
    sys.path.insert(0, agents_dir)

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Now we can import with both relative and absolute paths
try:
    # Try relative import first (when loaded as part of package)
    from .mental_orchestrator_agent import mental_orchestrator_agent
    root_agent = mental_orchestrator_agent
except ImportError:
    try:
        # Fall back to absolute import (when loaded directly by ADK)
        from agents.mental_orchestrator_agent.mental_orchestrator_agent import mental_orchestrator_agent
        root_agent = mental_orchestrator_agent
    except ImportError:
        try:
            # Try direct import from current directory
            from mental_orchestrator_agent import mental_orchestrator_agent
            root_agent = mental_orchestrator_agent
        except ImportError as e:
            # Final fallback: create a minimal agent inline if imports fail
            print(f"Warning: Could not import mental_orchestrator_agent: {e}")
            print("Creating fallback agent...")
            
            try:
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
            except ImportError as adk_error:
                print(f"Error: Could not even create fallback agent: {adk_error}")
                # Create a minimal response function
                def minimal_agent_response(input_text: str) -> str:
                    return f"Mental Orchestrator Agent (minimal mode): Received '{input_text}'. Please check your ADK installation and agent configuration."
                
                root_agent = minimal_agent_response

# Alternative export names that ADK might search for
agent = root_agent
main_agent = root_agent
mental_orchestrator_agent = root_agent 