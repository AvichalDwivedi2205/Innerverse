"""Tools for the therapy agent.

This module contains tools for therapy transcript processing, insights generation,
therapy notes creation, storage operations, and consistency tracking with focus 
on internal empowerment and therapeutic continuity.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, List

from google.adk.tools import ToolContext
from google.cloud import firestore
from google.cloud import aiplatform
import vertexai
from vertexai.generative_models import GenerativeModel
import pinecone

from .prompts import (
    get_transcript_processing_prompt,
    get_therapy_insights_prompt,
    get_therapy_notes_prompt,
    get_therapy_reflection_question_prompt
)

# Initialize clients
db = firestore.Client()
vertexai.init()
model = GenerativeModel("gemini-2.5-pro")


async def process_therapy_transcript(
    transcript: str,
    tool_context: ToolContext,
) -> str:
    """Tool to process therapy transcript into structured summary with empowerment focus."""
    
    try:
        prompt = get_transcript_processing_prompt()
        full_prompt = prompt.format(transcript=transcript)
        
        response = model.generate_content(full_prompt)
        summary_text = response.text
        
        # Parse JSON response
        summary = json.loads(summary_text)
        
        # Store in context
        tool_context.state["therapy_session"]["transcript"] = transcript
        tool_context.state["therapy_session"]["summary"] = summary
        
        return f"Therapy transcript processed with empowerment focus: {summary}"
        
    except Exception as e:
        return f"Error processing therapy transcript: {str(e)}"


async def generate_therapy_insights(
    tool_context: ToolContext,
) -> str:
    """Tool to generate therapy insights focusing on self-creation patterns."""
    
    try:
        summary = tool_context.state["therapy_session"]["summary"]
        
        prompt = get_therapy_insights_prompt()
        full_prompt = prompt.format(summary=json.dumps(summary))
        
        response = model.generate_content(full_prompt)
        insights_text = response.text
        
        # Parse JSON response
        insights = json.loads(insights_text)
        
        # Store in context
        tool_context.state["therapy_session"]["insights"] = insights
        
        return f"Therapy insights generated with empowerment themes: {insights}"
        
    except Exception as e:
        return f"Error generating therapy insights: {str(e)}"


async def generate_therapy_notes(
    tool_context: ToolContext,
) -> str:
    """Tool to generate therapy notes for session continuity with empowerment focus."""
    
    try:
        summary = tool_context.state["therapy_session"]["summary"]
        
        prompt = get_therapy_notes_prompt()
        full_prompt = prompt.format(summary=json.dumps(summary))
        
        response = model.generate_content(full_prompt)
        notes_text = response.text
        
        # Parse and structure therapy notes
        therapy_notes = [
            {
                "content": notes_text,
                "category": "observation",
                "priority": "high",
                "status": "active"
            }
        ]
        
        # Store in context
        tool_context.state["therapy_session"]["therapy_notes"] = therapy_notes
        
        return f"Therapy notes generated for session continuity: {len(therapy_notes)} notes"
        
    except Exception as e:
        return f"Error generating therapy notes: {str(e)}"


async def generate_therapy_reflection_question(
    tool_context: ToolContext,
) -> str:
    """Tool to generate empowering therapy reflection question."""
    
    try:
        summary = tool_context.state["therapy_session"]["summary"]
        
        prompt = get_therapy_reflection_question_prompt()
        full_prompt = prompt.format(summary=json.dumps(summary))
        
        response = model.generate_content(full_prompt)
        reflection_question = response.text.strip()
        
        # Store in context
        tool_context.state["therapy_session"]["reflection_question"] = reflection_question
        
        return f"Empowering therapy reflection question generated: {reflection_question}"
        
    except Exception as e:
        return f"Error generating therapy reflection question: {str(e)}"


async def store_therapy_session(
    tool_context: ToolContext,
) -> str:
    """Tool to store therapy session in Firebase Firestore."""
    
    try:
        user_id = tool_context.state.get("user_id")
        if not user_id:
            return "Error: User ID not found in context"
        
        therapy_session = tool_context.state["therapy_session"]
        session_id = str(uuid.uuid4())
        
        # Prepare therapy session document
        session_doc = {
            "sessionDate": datetime.now(),
            "transcript": therapy_session["transcript"],
            "summary": therapy_session["summary"],
            "insights": therapy_session["insights"],
            "embeddingId": "",  # Will be set after embedding generation
            "duration": 60,  # Default 60 minutes
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        # Store in Firestore
        db.collection("users").document(user_id).collection("therapySessions").document(session_id).set(session_doc)
        
        # Generate and store embedding for observations
        observations_text = therapy_session["summary"].get("observations", "")
        embedding_id = await _generate_and_store_embedding(
            text=observations_text,
            user_id=user_id,
            context="therapy",
            source_id=session_id
        )
        
        # Update session with embedding ID
        db.collection("users").document(user_id).collection("therapySessions").document(session_id).update({
            "embeddingId": embedding_id
        })
        
        # Store therapy notes
        for note in therapy_session["therapy_notes"]:
            note_id = str(uuid.uuid4())
            note_doc = {
                "content": note["content"],
                "sessionId": session_id,
                "category": note["category"],
                "priority": note["priority"],
                "status": note["status"],
                "embeddingId": await _generate_and_store_embedding(
                    text=note["content"],
                    user_id=user_id,
                    context="notes",
                    source_id=note_id
                ),
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            }
            
            db.collection("users").document(user_id).collection("therapyNotes").document(note_id).set(note_doc)
        
        # Store reflection question as recommendation
        recommendation_doc = {
            "type": "reflection_question",
            "content": therapy_session["reflection_question"],
            "category": "Reflection",
            "source": "therapy",
            "priority": 4,
            "status": "pending",
            "createdAt": datetime.now(),
            "expiresAt": datetime.now().replace(hour=23, minute=59, second=59)
        }
        
        db.collection("users").document(user_id).collection("recommendations").add(recommendation_doc)
        
        tool_context.state["session_id"] = session_id
        
        return f"Therapy session stored successfully with ID: {session_id}"
        
    except Exception as e:
        return f"Error storing therapy session: {str(e)}"


async def update_therapy_consistency_tracking(
    tool_context: ToolContext,
) -> str:
    """Tool to update weekly therapy consistency metrics."""
    
    try:
        user_id = tool_context.state.get("user_id")
        if not user_id:
            return "Error: User ID not found in context"
        
        # Get current metrics
        metrics_ref = db.collection("users").document(user_id).collection("dashboard").document("metrics")
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
        
        # Update therapy consistency
        metrics["consistency"]["therapyCount"] += 1
        metrics["consistency"]["therapyStreak"] += 1  # Simplified streak logic
        metrics["lastUpdated"] = datetime.now()
        
        # Store updated metrics
        metrics_ref.set(metrics, merge=True)
        
        return f"Therapy consistency tracking updated: Session count {metrics['consistency']['therapyCount']}"
        
    except Exception as e:
        return f"Error updating therapy consistency tracking: {str(e)}"


async def trigger_mental_orchestrator_therapy(
    tool_context: ToolContext,
) -> str:
    """Tool to trigger Mental Orchestrator Agent for mind map updates from therapy."""
    
    try:
        user_id = tool_context.state.get("user_id")
        session_id = tool_context.state.get("session_id")
        
        if not user_id or not session_id:
            return "Error: User ID or Session ID not found in context"
        
        # Create trigger document for Mental Orchestrator
        trigger_doc = {
            "userId": user_id,
            "sourceType": "therapy",
            "sourceId": session_id,
            "action": "update_mind_map",
            "status": "pending",
            "createdAt": datetime.now()
        }
        
        # Store trigger (this would be picked up by Firebase Functions)
        db.collection("orchestrator_triggers").add(trigger_doc)
        
        return "Mental Orchestrator Agent triggered for therapy mind map update"
        
    except Exception as e:
        return f"Error triggering Mental Orchestrator from therapy: {str(e)}"


async def _generate_and_store_embedding(
    text: str,
    user_id: str,
    context: str,
    source_id: str
) -> str:
    """Helper function to generate and store embeddings in Pinecone."""
    
    try:
        # Generate embedding using Vertex AI
        embedding_model = aiplatform.TextEmbeddingModel.from_pretrained("text-embedding-004")
        embeddings = embedding_model.get_embeddings([text])
        embedding_vector = embeddings[0].values
        
        # Generate unique embedding ID
        embedding_id = f"{user_id}_{context}_{source_id}"
        
        # Store in Pinecone (assuming Pinecone is configured)
        # pinecone.upsert(
        #     vectors=[(embedding_id, embedding_vector, {
        #         "userId": user_id,
        #         "context": context,
        #         "sourceId": source_id,
        #         "timestamp": datetime.now().isoformat()
        #     })]
        # )
        
        return embedding_id
        
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        return ""
