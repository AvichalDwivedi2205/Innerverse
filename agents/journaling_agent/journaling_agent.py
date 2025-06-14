"""Journaling Agent for mental health empowerment.

Facilitates daily journaling to promote introspection, helping users shift focus 
from external events to internal thought patterns, recognize how their internal 
responses create their experiences, and receive tailored Reflection Questions 
to deepen self-awareness and personal empowerment.
"""
import os
from datetime import date

from google.genai import types

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext

from .prompts import return_instructions_journaling
from .tools import (
    standardize_journal_text,
    generate_journal_insights,
    generate_reflection_question,
    store_journal_entry,
    update_consistency_tracking,
    trigger_mental_orchestrator
)

date_today = date.today()


def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the journaling agent."""
    
    # Initialize user context if not exists
    if "user_id" not in callback_context.state:
        callback_context.state["user_id"] = None
    
    # Initialize journaling session state
    if "journal_session" not in callback_context.state:
        callback_context.state["journal_session"] = {
            "raw_text": "",
            "standardized_entry": {},
            "insights": {},
            "reflection_question": "",
            "embedding_id": ""
        }
    
    # Set empowerment-focused instruction context
    callback_context._invocation_context.agent.instruction = (
        return_instructions_journaling()
        + f"""
        
    --------- Current Session Context ---------
    Today's Date: {date_today}
    Focus: Internal empowerment and self-creation awareness
    Goal: Help user recognize they are the creator of their experience
    
    """
    )


journaling_agent = Agent(
    model=os.getenv("JOURNALING_AGENT_MODEL", "gemini-2.5-pro"),
    name="journaling_agent",
    instruction=return_instructions_journaling(),
    global_instruction=(
        f"""
        You are an Empowerment-Focused Journaling Agent for mental health.
        Your role is to guide users from external focus to internal empowerment.
        Today's date: {date_today}
        
        Core Mission: Help users realize they are the creators of their experience 
        through their internal thoughts, beliefs, and responses.
        """
    ),
    tools=[
        standardize_journal_text,
        generate_journal_insights,
        generate_reflection_question,
        store_journal_entry,
        update_consistency_tracking,
        trigger_mental_orchestrator,
    ],
    before_agent_callback=setup_before_agent_call,
    generate_content_config=types.GenerateContentConfig(temperature=0.3),
)
