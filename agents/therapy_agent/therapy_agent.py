"""Therapy Agent for mental health empowerment.

Conducts weekly therapy sessions focusing on internal empowerment and self-creation, 
generates therapy notes for continuity, and provides Reflection Questions that 
reinforce the user's role as creator of their experience.
"""
import os
from datetime import date

from google.genai import types

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext

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

date_today = date.today()


def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the therapy agent."""
    
    # Initialize user context if not exists
    if "user_id" not in callback_context.state:
        callback_context.state["user_id"] = None
    
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


therapy_agent = Agent(
    model=os.getenv("THERAPY_AGENT_MODEL", "gemini-2.5-pro"),
    name="therapy_agent",
    instruction=return_instructions_therapy(),
    global_instruction=(
        f"""
        You are an Empowerment-Focused Therapy Agent for mental health.
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
)
