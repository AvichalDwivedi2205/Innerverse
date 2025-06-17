"""Tools for the journaling agent.

This module contains tools for journal text processing, insights generation,
storage operations, and consistency tracking with focus on internal empowerment.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any

from google.adk.tools import ToolContext
from google.cloud import firestore
from google.cloud import aiplatform
import vertexai
from vertexai.generative_models import GenerativeModel
# Pinecone functionality is now handled by the pinecone_service

from .prompts import (
    get_standardization_prompt,
    get_insights_prompt,
    get_reflection_question_prompt
)
from ..common import JournalingToolResult, coordinator
from ..common.pinecone_service import pinecone_service

# Initialize clients lazily to avoid import-time errors
_db = None
_model = None

def get_firestore_client():
    """Get Firestore client with lazy initialization."""
    global _db
    if _db is None:
        _db = firestore.Client()
    return _db

def get_gemini_model():
    """Get Gemini model with lazy initialization."""
    global _model
    if _model is None:
        vertexai.init()
        _model = GenerativeModel("gemini-2.5-pro")
    return _model


async def standardize_journal_text(
    raw_text: str,
    tool_context: ToolContext,
) -> JournalingToolResult:
    """Tool to standardize journal text using Gemini-2.5-Pro with empowerment focus."""
    
    try:
        prompt = get_standardization_prompt()
        full_prompt = f"{prompt}\n\nRaw Journal Text: {raw_text}"
        
        response = get_gemini_model().generate_content(full_prompt)
        standardized_text = response.text
        
        # Parse JSON response
        standardized_entry = json.loads(standardized_text)
        
        # Store in context
        tool_context.state["journal_session"]["raw_text"] = raw_text
        tool_context.state["journal_session"]["standardized_entry"] = standardized_entry
        
        return JournalingToolResult.success_result(
            data={"standardized_entry": standardized_entry},
            message="Journal text standardized with empowerment focus",
            next_actions=["generate_journal_insights"]
        )
        
    except Exception as e:
        return JournalingToolResult.error_result(
            message="Error standardizing journal text",
            error_details=str(e),
            next_actions=["retry_standardization", "check_input_format"]
        )


async def generate_journal_insights(
    tool_context: ToolContext,
) -> JournalingToolResult:
    """Tool to generate journal insights focusing on internal empowerment."""
    
    try:
        standardized_entry = tool_context.state["journal_session"]["standardized_entry"]
        
        if not standardized_entry:
            return JournalingToolResult.error_result(
                message="No standardized entry found",
                error_details="standardize_journal_text must be called first",
                next_actions=["standardize_journal_text"]
            )
        
        prompt = get_insights_prompt()
        full_prompt = prompt.format(entry=json.dumps(standardized_entry))
        
        response = get_gemini_model().generate_content(full_prompt)
        insights_text = response.text
        
        # Parse JSON response
        insights = json.loads(insights_text)
        
        # Store in context
        tool_context.state["journal_session"]["insights"] = insights
        
        return JournalingToolResult.success_result(
            data={"insights": insights},
            message="Journal insights generated with empowerment themes",
            next_actions=["generate_reflection_question"]
        )
        
    except Exception as e:
        return JournalingToolResult.error_result(
            message="Error generating journal insights",
            error_details=str(e),
            next_actions=["retry_insights_generation", "check_standardized_entry"]
        )


async def generate_reflection_question(
    tool_context: ToolContext,
) -> str:
    """Tool to generate empowering reflection question."""
    
    try:
        standardized_entry = tool_context.state["journal_session"]["standardized_entry"]
        insights = tool_context.state["journal_session"]["insights"]
        
        entry_with_insights = {
            "entry": standardized_entry,
            "insights": insights
        }
        
        prompt = get_reflection_question_prompt()
        full_prompt = prompt.format(entry_with_insights=json.dumps(entry_with_insights))
        
        response = get_gemini_model().generate_content(full_prompt)
        reflection_question = response.text.strip()
        
        # Store in context
        tool_context.state["journal_session"]["reflection_question"] = reflection_question
        
        return f"Empowering reflection question generated: {reflection_question}"
        
    except Exception as e:
        return f"Error generating reflection question: {str(e)}"


async def store_journal_entry(
    tool_context: ToolContext,
) -> str:
    """Tool to store journal entry in Firebase Firestore."""
    
    try:
        user_id = tool_context.state.get("user_id")
        if not user_id:
            return "Error: User ID not found in context"
        
        journal_session = tool_context.state["journal_session"]
        journal_id = str(uuid.uuid4())
        
        # Prepare journal document
        journal_doc = {
            "date": datetime.now(),
            "rawText": journal_session["raw_text"],
            "standardizedEntry": journal_session["standardized_entry"],
            "insights": journal_session["insights"],
            "embeddingId": "",  # Will be set after embedding generation
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        # Store in Firestore
        get_firestore_client().collection("users").document(user_id).collection("journals").document(journal_id).set(journal_doc)
        
        # Generate and store embedding
        reflection_text = journal_session["standardized_entry"].get("reflection", "")
        embedding_id = await _generate_and_store_embedding(
            text=reflection_text,
            user_id=user_id,
            context="journal",
            source_id=journal_id
        )
        
        # Update journal with embedding ID
        get_firestore_client().collection("users").document(user_id).collection("journals").document(journal_id).update({
            "embeddingId": embedding_id
        })
        
        # Store reflection question as recommendation
        recommendation_doc = {
            "type": "reflection_question",
            "content": journal_session["reflection_question"],
            "category": "Reflection",
            "source": "journal",
            "priority": 3,
            "status": "pending",
            "createdAt": datetime.now(),
            "expiresAt": datetime.now().replace(hour=23, minute=59, second=59)
        }
        
        get_firestore_client().collection("users").document(user_id).collection("recommendations").add(recommendation_doc)
        
        tool_context.state["journal_id"] = journal_id
        
        return f"Journal entry stored successfully with ID: {journal_id}"
        
    except Exception as e:
        return f"Error storing journal entry: {str(e)}"


async def update_consistency_tracking(
    tool_context: ToolContext,
) -> str:
    """Tool to update daily journaling consistency metrics."""
    
    try:
        user_id = tool_context.state.get("user_id")
        if not user_id:
            return "Error: User ID not found in context"
        
        # Get current metrics
        metrics_ref = get_firestore_client().collection("users").document(user_id).collection("dashboard").document("metrics")
        metrics_doc = metrics_ref.get()
        
        if metrics_doc.exists:
            metrics = metrics_doc.to_dict()
        else:
            metrics = {
                "consistency": {
                    "journalCount": 0,
                    "journalStreak": 0,
                    "therapyCount": 0,
                    "therapyStreak": 0
                }
            }
        
        # Update journal consistency
        metrics["consistency"]["journalCount"] += 1
        metrics["consistency"]["journalStreak"] += 1  # Simplified streak logic
        metrics["lastUpdated"] = datetime.now()
        
        # Store updated metrics
        metrics_ref.set(metrics, merge=True)
        
        return f"Consistency tracking updated: Journal count {metrics['consistency']['journalCount']}"
        
    except Exception as e:
        return f"Error updating consistency tracking: {str(e)}"


async def trigger_mental_orchestrator(
    tool_context: ToolContext,
) -> JournalingToolResult:
    """Tool to trigger Mental Orchestrator Agent for mind map updates."""
    
    try:
        user_id = tool_context.state.get("user_id")
        journal_id = tool_context.state.get("journal_id")
        
        if not user_id or not journal_id:
            return JournalingToolResult.error_result(
                message="Missing required context data",
                error_details="User ID or Journal ID not found in context",
                next_actions=["ensure_journal_stored", "verify_user_context"]
            )
        
        # Use coordinator for direct agent communication instead of Firebase triggers
        coordination_result = await coordinator.trigger_mindmap_update(
            user_id=user_id,
            source_type="journal",
            source_id=journal_id,
            callback_context=tool_context
        )
        
        if coordination_result.success:
            return JournalingToolResult.success_result(
                data={
                    "coordination_result": coordination_result.dict(),
                    "coordinated_agents": coordination_result.coordinated_agents
                },
                message="Mental Orchestrator Agent coordination completed successfully",
                next_actions=[]
            )
        else:
            return JournalingToolResult.error_result(
                message="Failed to coordinate with Mental Orchestrator",
                error_details="; ".join(coordination_result.errors),
                next_actions=["retry_coordination", "check_agent_registry"]
            )
        
    except Exception as e:
        return JournalingToolResult.error_result(
            message="Error triggering Mental Orchestrator",
            error_details=str(e),
            next_actions=["retry_coordination", "check_coordinator_setup"]
        )


async def _generate_and_store_embedding(
    text: str,
    user_id: str,
    context: str,
    source_id: str
) -> str:
    """Helper function to generate and store embeddings in Pinecone."""
    
    try:
        # Generate unique embedding ID
        embedding_id = f"{user_id}_{context}_{source_id}"
        
        # Store in Pinecone using the service
        success = await pinecone_service.store_embedding(
            embedding_id=embedding_id,
            text=text,
            user_id=user_id,
            context=context,
            source_id=source_id,
            additional_metadata={
                "agent": "journaling_agent",
                "version": "1.0"
            }
        )
        
        if success:
            return embedding_id
        else:
            print(f"Failed to store embedding: {embedding_id}")
            return ""
        
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        return ""
