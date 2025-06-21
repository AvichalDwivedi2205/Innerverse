"""Mental Orchestrator Agent for mental health empowerment.

Analyzes embeddings to create a mental mind map focused on internal patterns, 
generates insights for self-empowerment, recommends exercises that build internal 
awareness, tracks growth toward self-responsibility, and detects crises while 
maintaining focus on personal power and self-creation.
"""
import os
from datetime import date

from google.genai import types

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext

from agents.mental_orchestrator_agent.prompts import return_instructions_orchestrator
from agents.mental_orchestrator_agent.tools import (
    retrieve_user_embeddings,
    cluster_internal_patterns,
    build_mental_mind_map,
    generate_empowerment_insights,
    recommend_awareness_exercises,
    calculate_dashboard_metrics,
    detect_crisis_with_empowerment,
    store_orchestrator_results
)

date_today = date.today()


def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the mental orchestrator agent."""
    
    # Initialize user context if not exists
    if "user_id" not in callback_context.state:
        callback_context.state["user_id"] = os.getenv("DEV_USER_ID", "avichal_dev_user")
    
    # Initialize orchestrator state
    if "orchestrator_state" not in callback_context.state:
        callback_context.state["orchestrator_state"] = {
            "embeddings_data": [],
            "clusters": {},
            "mind_map": {},
            "insights": [],
            "exercise_recommendations": [],
            "dashboard_metrics": {},
            "crisis_alerts": []
        }
    
    # Initialize trigger context
    if "trigger_data" not in callback_context.state:
        callback_context.state["trigger_data"] = {
            "source_type": "",
            "source_id": "",
            "action": ""
        }
    
    # Set empowerment-focused instruction context
    callback_context._invocation_context.agent.instruction = (
        return_instructions_orchestrator()
        + f"""
        
    --------- Current Orchestration Context ---------
    Today's Date: {date_today}
    Focus: Internal pattern analysis and empowerment orchestration
    Goal: Coordinate insights and recommendations for user self-empowerment
    Available Data Sources: Journal entries, therapy sessions, therapy notes
    
    """
    )


# Configure model with proper API settings
def get_orchestrator_model_config():
    """Get the proper model configuration based on available credentials."""
    google_api_key = os.getenv('GOOGLE_API_KEY')
    vertex_project = os.getenv('GOOGLE_CLOUD_PROJECT') or os.getenv('VERTEX_AI_PROJECT')
    vertex_location = os.getenv('GOOGLE_CLOUD_REGION') or os.getenv('VERTEX_AI_LOCATION', 'us-central1')
    
    if google_api_key:
        # Use Google AI API - set environment variables for ADK
        os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'FALSE'
        return {
            "model": os.getenv("ORCHESTRATOR_AGENT_MODEL", "gemini-2.5-flash")
        }
    elif vertex_project:
        # Use working Vertex AI models only (fallback)
        os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'TRUE'
        model_name = os.getenv("ORCHESTRATOR_AGENT_MODEL", "gemini-2.5-flash")
        return {
            "model": f"vertexai/{vertex_project}/{vertex_location}/{model_name}"
        }
    else:
        # Final fallback - use stable Gemini model
        return {
            "model": os.getenv("ORCHESTRATOR_AGENT_MODEL", "gemini-2.5-flash")
        }

orchestrator_model_config = get_orchestrator_model_config()

mental_orchestrator_agent = Agent(
    name="mental_orchestrator_agent",
    instruction=return_instructions_orchestrator(),
    global_instruction=(
        f"""
        You are an Empowerment-Focused Mental Orchestrator Agent for mental health.
        Your role is to coordinate insights and recommendations that shift users toward creator consciousness.
        Today's date: {date_today}
        
        Core Mission: Analyze internal patterns from journal and therapy data to generate 
        empowering insights and recommendations that help users recognize their role as 
        creators of their experience.
        """
    ),
    tools=[
        retrieve_user_embeddings,
        cluster_internal_patterns,
        build_mental_mind_map,
        generate_empowerment_insights,
        recommend_awareness_exercises,
        calculate_dashboard_metrics,
        detect_crisis_with_empowerment,
        store_orchestrator_results,
    ],
    before_agent_callback=setup_before_agent_call,
    generate_content_config=types.GenerateContentConfig(temperature=0.2),
    **orchestrator_model_config
)
