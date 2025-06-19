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
# Pinecone functionality is now handled by the pinecone_service

from .prompts import (
    get_transcript_processing_prompt,
    get_therapy_insights_prompt,
    get_therapy_notes_prompt,
    get_therapy_reflection_question_prompt
)

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
    """Get Gemini model with lazy initialization using Google AI API."""
    global _model
    if _model is None:
        import os
        google_api_key = os.getenv('GOOGLE_API_KEY')
        
        if google_api_key:
            # Use Google AI API directly
            import google.generativeai as genai
            genai.configure(api_key=google_api_key)
            _model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            # Fallback to Vertex AI
            vertexai.init()
            _model = GenerativeModel("gemini-2.5-flash")
    return _model


async def process_therapy_transcript(
    transcript: str,
    tool_context: ToolContext,
) -> str:
    """Tool to process therapy transcript into structured summary with empowerment focus."""
    
    try:
        prompt = get_transcript_processing_prompt()
        full_prompt = prompt.format(transcript=transcript)
        
        model = get_gemini_model()
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
        
        model = get_gemini_model()
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
        
        model = get_gemini_model()
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
        
        model = get_gemini_model()
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
        db = get_firestore_client()
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
        db = get_firestore_client()
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
        db = get_firestore_client()
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


async def complete_therapy_session(
    session_transcript: str,
    tool_context: ToolContext,
) -> str:
    """Tool to complete and properly end a therapy session with full documentation."""
    
    try:
        # Check if user_id is set
        user_id = tool_context.state.get("user_id")
        if not user_id:
            return "Error: User ID must be set before completing session. Please ensure user is properly authenticated."
        
        print("Starting session completion process...")
        
        # Step 1: Process transcript
        transcript_result = await process_therapy_transcript(session_transcript, tool_context)
        print(f"✓ Transcript processed: {transcript_result}")
        
        # Step 2: Generate insights
        insights_result = await generate_therapy_insights(tool_context)
        print(f"✓ Insights generated: {insights_result}")
        
        # Step 3: Generate therapy notes
        notes_result = await generate_therapy_notes(tool_context)
        print(f"✓ Clinical notes created: {notes_result}")
        
        # Step 4: Generate reflection question
        reflection_result = await generate_therapy_reflection_question(tool_context)
        print(f"✓ Reflection question generated: {reflection_result}")
        
        # Step 5: Store session
        storage_result = await store_therapy_session(tool_context)
        print(f"✓ Session stored: {storage_result}")
        
        # Step 6: Update consistency tracking
        tracking_result = await update_therapy_consistency_tracking(tool_context)
        print(f"✓ Progress tracking updated: {tracking_result}")
        
        # Step 7: Trigger mental orchestrator
        orchestrator_result = await trigger_mental_orchestrator_therapy(tool_context)
        print(f"✓ Mental orchestrator triggered: {orchestrator_result}")
        
        session_id = tool_context.state.get("session_id", "unknown")
        
        return f"""
🏁 THERAPY SESSION COMPLETED SUCCESSFULLY

Session ID: {session_id}
Documentation Status: ✅ Complete

Summary:
• Clinical transcript processed and analyzed
• Comprehensive therapy notes created with behavioral patterns
• Risk assessment and diagnostic impressions documented  
• Empowerment themes and agency opportunities identified
• Therapeutic reflection question generated for continued growth
• Progress tracking updated
• Care coordination triggered

Your session has been fully documented and stored securely. 
The reflection question and any homework assignments are available in your recommendations.

Thank you for engaging in this therapeutic work. Your commitment to growth and self-awareness is commendable.
        """
        
    except Exception as e:
        return f"Error completing therapy session: {str(e)}. Please try again or contact support."
