"""Therapy Agent for mental health empowerment.

Conducts weekly therapy sessions focusing on internal empowerment and self-creation, 
generates therapy notes for continuity, and provides Reflection Questions that 
reinforce the user's role as creator of their experience.
"""
import os
import uuid
from datetime import date

from google.genai import types

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext

try:
    # Try relative imports first (when loaded as part of package)
    from .prompts import return_instructions_therapy
    from .tools import (
        process_therapy_transcript,
        generate_therapy_insights,
        generate_therapy_notes,
        generate_therapy_reflection_question,
        store_therapy_session,
        update_therapy_consistency_tracking,
        trigger_mental_orchestrator_therapy
    )
except ImportError:
    # Fall back to absolute imports (when loaded directly by ADK)
    from agents.therapy_agent.prompts import return_instructions_therapy
    from agents.therapy_agent.tools import (
        process_therapy_transcript,
        generate_therapy_insights,
        generate_therapy_notes,
        generate_therapy_reflection_question,
        store_therapy_session,
        update_therapy_consistency_tracking,
        trigger_mental_orchestrator_therapy
    )

date_today = date.today()


def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the therapy agent."""
    
    # Initialize user context if not exists
    if "user_id" not in callback_context.state:
        # Set user context in state - use dynamic user ID from session or fallback
        # Get session_id from callback_context.state or generate one
        session_id = getattr(callback_context, 'session_id', None) or callback_context.state.get('session_id', str(uuid.uuid4()))
        session_user_id = session_id.split('_')[0] if '_' in session_id else session_id
        callback_context.state["session_id"] = session_id
        callback_context.state["user_id"] = os.getenv("DEV_USER_ID", session_user_id or "default_user")
    
    # Initialize therapy session state
    if "therapy_session" not in callback_context.state:
        callback_context.state["therapy_session"] = {
            "transcript": "",
            "summary": {},
            "insights": {},
            "therapy_notes": [],
            "reflection_question": "",
            "embedding_id": ""
        }
    
    # Retrieve previous therapy notes for context
    if "previous_therapy_notes" not in callback_context.state:
        callback_context.state["previous_therapy_notes"] = []
    
    # Set empowerment-focused instruction context
    callback_context._invocation_context.agent.instruction = (
        return_instructions_therapy()
        + f"""
        
    --------- Current Session Context ---------
    Today's Date: {date_today}
    Focus: Internal empowerment and self-creation awareness
    Goal: Help user recognize they are the creator of their experience
    Previous Notes Available: {len(callback_context.state["previous_therapy_notes"])} notes
    
    """
    )


# Configure model with proper API settings
def get_therapy_model_config():
    """Get the proper model configuration based on available credentials."""
    google_api_key = os.getenv('GOOGLE_API_KEY')
    vertex_project = os.getenv('GOOGLE_CLOUD_PROJECT') or os.getenv('VERTEX_AI_PROJECT')
    vertex_location = os.getenv('GOOGLE_CLOUD_REGION') or os.getenv('VERTEX_AI_LOCATION', 'us-central1')
    
    if google_api_key:
        # Use Google AI API - set environment variables for ADK
        os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'FALSE'
        return {
            "model": os.getenv("THERAPY_AGENT_MODEL", "gemini-2.5-flash")
        }
    elif vertex_project:
        # Use working Vertex AI models only (fallback)
        os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'TRUE'
        model_name = os.getenv("THERAPY_AGENT_MODEL", "gemini-2.5-flash")
        return {
            "model": f"vertexai/{vertex_project}/{vertex_location}/{model_name}"
        }
    else:
        # Final fallback - use stable Gemini model
        return {
            "model": os.getenv("THERAPY_AGENT_MODEL", "gemini-2.5-flash")
        }

therapy_model_config = get_therapy_model_config()

therapy_agent = Agent(
    name="therapy_agent",
    instruction=return_instructions_therapy(),
    global_instruction=(
        f"""
        You are a Therapy Agent for mental health.
        Your role is to conduct therapy sessions that shift users from victim consciousness to creator consciousness.
        Today's date: {date_today}
        
        Core Mission: Help users realize they create their experience through their internal 
        thoughts, beliefs, and responses during therapeutic conversations.
        """
    ),
    tools=[
        process_therapy_transcript,
        generate_therapy_insights,
        generate_therapy_notes,
        generate_therapy_reflection_question,
        store_therapy_session,
        update_therapy_consistency_tracking,
        trigger_mental_orchestrator_therapy,
    ],
    before_agent_callback=setup_before_agent_call,
    generate_content_config=types.GenerateContentConfig(temperature=0.3),
    **therapy_model_config
)
