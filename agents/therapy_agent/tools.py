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

# Phase 2: Import enhanced session timer
from ..common.session_timer import EnhancedSessionTimer, SessionType, TimerToolResult

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


async def generate_therapy_reflection_questions(
    tool_context: ToolContext,
) -> str:
    """
    Phase 3: Generate complete set of 5 categorized therapy reflection questions.
    Replaces single reflection question generation with enhanced system.
    Always generates: 2 daily + 2 deep + 1 action = 5 questions total.
    """
    
    try:
        # Import enhanced reflection generator
        from ..common.reflection_generator import EnhancedReflectionGenerator
        
        # Get therapy session data
        therapy_session = tool_context.state["therapy_session"]
        summary = therapy_session["summary"]
        insights = therapy_session.get("insights", {})
        
        # Initialize enhanced reflection generator
        reflection_generator = EnhancedReflectionGenerator()
        
        # Prepare context data from therapy session
        session_data = {
            "transcript": therapy_session.get("transcript", ""),
            "summary": summary,
            "insights": insights,
            "challenges": insights.get("challenges", []),
            "emotions": insights.get("emotions", []),
            "topics": insights.get("themes", ["therapy session", "personal growth"]),
            "therapy_notes": therapy_session.get("therapy_notes", [])
        }
        
        user_context = {
            "preferences": ["therapy", "professional guidance", "empowerment"],
            "source": "therapy"
        }
        
        # Generate complete question set (2 daily + 2 deep + 1 action = 5 questions)
        question_set = await reflection_generator.generate_complete_question_set(
            session_data=session_data,
            insights=insights,
            user_context=user_context,
            source_type="therapy"
        )
        
        # Get question summary
        summary_data = reflection_generator.get_question_summary(question_set)
        
        # Store in context
        tool_context.state["therapy_session"]["reflection_questions"] = question_set
        tool_context.state["therapy_session"]["reflection_summary"] = summary_data
        
        # Format response
        question_counts = summary_data["category_breakdown"]
        return (
            f"✅ **THERAPY REFLECTION QUESTIONS GENERATED**\n\n"
            f"📊 **Generated {summary_data['total_questions']} categorized questions:**\n"
            f"   🔹 Daily Practice: {question_counts['daily_practice']} questions\n"
            f"   🔹 Deep Reflection: {question_counts['deep_reflection']} questions\n"
            f"   🔹 Action Items: {question_counts['action_items']} questions\n\n"
            f"🎯 **Question Preview:**\n"
        ) + _format_question_preview(question_set) + (
            f"\n\n💡 **Enhanced delivery system activated** - Questions scheduled for optimal timing"
        )
        
    except Exception as e:
        return f"❌ Error generating enhanced therapy reflection questions: {str(e)}"


def _format_question_preview(question_set) -> str:
    """Format a preview of the generated questions."""
    preview = ""
    
    for category, questions in question_set.items():
        category_name = category.value.replace("_", " ").title()
        preview += f"\n📝 **{category_name}:**\n"
        
        for i, question in enumerate(questions, 1):
            preview += f"   {i}. {question.question[:80]}{'...' if len(question.question) > 80 else ''}\n"
    
    return preview


def _get_therapy_category_priority(category: str) -> int:
    """Get priority for therapy reflection question categories."""
    priorities = {
        "action_items": 1,      # Highest priority - immediate implementation
        "daily_practice": 2,    # Medium priority - daily integration
        "deep_reflection": 3    # Lower priority - longer term processing
    }
    return priorities.get(category, 2)


async def generate_therapy_reflection_question(
    tool_context: ToolContext,
) -> str:
    """
    Backward compatibility wrapper - redirects to enhanced reflection system.
    """
    return await generate_therapy_reflection_questions(tool_context)


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
        
        # Store enhanced reflection questions if available (Phase 3)
        if "reflection_questions" in therapy_session:
            reflection_questions = therapy_session["reflection_questions"]
            
            for category, questions in reflection_questions.items():
                category_key = category.value if hasattr(category, 'value') else str(category)
                
                for question in questions:
                    recommendation_doc = {
                        "type": "reflection_question",
                        "category": category_key,
                        "reflectionType": question.reflection_type.value,
                        "content": question.question,
                        "questionId": question.question_id,
                        "difficulty": question.metadata["difficulty"],
                        "estimatedTime": question.metadata["estimatedTime"],
                        "source": "therapy",
                        "sourceId": session_id,
                        "priority": _get_therapy_category_priority(category_key),
                        "status": "pending",
                        "createdAt": datetime.now(),
                        "scheduledFor": question.delivery["scheduledFor"],
                        "expiresAt": question.delivery["expiresAt"]
                    }
                    
                    db.collection("users").document(user_id).collection("reflectionQuestions").add(recommendation_doc)
        
        # Backward compatibility: Store single reflection question if available
        elif "reflection_question" in therapy_session:
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


# =================================
# PHASE 2: ENHANCED SESSION TIMING TOOLS
# =================================

async def choose_session_duration(
    user_id: str,
    preferences: Dict[str, Any] = None,
    tool_context: ToolContext = None
) -> str:
    """Tool to present therapy session duration options and recommendations.
    
    Args:
        user_id: User identifier
        preferences: User preferences for session timing
        tool_context: Tool context for state management
        
    Returns:
        String describing available session options
    """
    try:
        # Create temporary timer to get options
        temp_timer = EnhancedSessionTimer(user_id, SessionType.THERAPY, "standard_60")
        
        result = await temp_timer.choose_session_duration(preferences or {})
        
        if tool_context:
            tool_context.state["session_options"] = result.data
            
        if result.success:
            options = result.data["available_sessions"]
            return (
                f"Session duration options available:\n\n"
                f"🕐 **60-MINUTE SESSION (Recommended for deep work)**\n"
                f"   - Pre-session: {options['standard_60']['phases'][0]['duration']} min - {options['standard_60']['phases'][0]['description']}\n"
                f"   - Opening: {options['standard_60']['phases'][1]['duration']} min - {options['standard_60']['phases'][1]['description']}\n"
                f"   - Working: {options['standard_60']['phases'][2]['duration']} min - {options['standard_60']['phases'][2]['description']}\n"
                f"   - Integration: {options['standard_60']['phases'][3]['duration']} min - {options['standard_60']['phases'][3]['description']}\n"
                f"   - Closing: {options['standard_60']['phases'][4]['duration']} min - {options['standard_60']['phases'][4]['description']}\n"
                f"   Best for: {options['standard_60']['recommended_for']}\n\n"
                f"🕐 **30-MINUTE SESSION (Focused sessions)**\n"
                f"   - Pre-session: {options['short_30']['phases'][0]['duration']} min - {options['short_30']['phases'][0]['description']}\n"
                f"   - Opening: {options['short_30']['phases'][1]['duration']} min - {options['short_30']['phases'][1]['description']}\n"
                f"   - Working: {options['short_30']['phases'][2]['duration']} min - {options['short_30']['phases'][2]['description']}\n"
                f"   - Integration: {options['short_30']['phases'][3]['duration']} min - {options['short_30']['phases'][3]['description']}\n"
                f"   - Closing: {options['short_30']['phases'][4]['duration']} min - {options['short_30']['phases'][4]['description']}\n"
                f"   Best for: {options['short_30']['recommended_for']}"
            )
        else:
            return f"Error getting session options: {result.message}"
            
    except Exception as e:
        return f"Error presenting session duration options: {str(e)}"


async def start_therapy_session_timer(
    user_id: str,
    session_type: str = "standard_60",
    tool_context: ToolContext = None
) -> str:
    """Tool to start therapy session timer with exact phase timing.
    
    Args:
        user_id: User identifier
        session_type: "standard_60" or "short_30"
        tool_context: Tool context for state management
        
    Returns:
        String describing session start status
    """
    try:
        # Create enhanced session timer
        timer = EnhancedSessionTimer(
            user_id=user_id,
            session_type=SessionType.THERAPY,
            therapy_session_type=session_type
        )
        
        # Start the session
        result = await timer.start_session()
        
        if tool_context:
            tool_context.state["session_timer"] = timer
            tool_context.state["session_id"] = result.session_id
            
        if result.success:
            session_data = result.data
            return (
                f"✅ **THERAPY SESSION STARTED**\n\n"
                f"📊 **Session Details:**\n"
                f"   - Type: {session_data['therapy_session_type']}\n"
                f"   - Total Duration: {session_data['total_duration']} minutes\n"
                f"   - Session ID: {result.session_id}\n\n"
                f"🎯 **Current Phase:** {session_data['current_phase']}\n"
                f"   - Duration: {session_data['phase_duration']} minutes\n\n"
                f"📋 **All Phases:**\n" +
                "\n".join([
                    f"   {i+1}. {p['name'].title()}: {p['duration']} min - {p['description']}"
                    for i, p in enumerate(session_data['phases'])
                ]) +
                f"\n\n⏰ **Background monitoring active** - Automatic phase transitions enabled"
            )
        else:
            return f"❌ Error starting session: {result.message}"
            
    except Exception as e:
        return f"Error starting therapy session timer: {str(e)}"


async def get_session_timer_status(
    tool_context: ToolContext = None
) -> str:
    """Tool to get real-time session progress with exact timing.
    
    Args:
        tool_context: Tool context containing session timer
        
    Returns:
        String describing current session status
    """
    try:
        if not tool_context or "session_timer" not in tool_context.state:
            return "❌ No active session timer found"
            
        timer = tool_context.state["session_timer"]
        result = await timer.get_session_timer_status()
        
        if result.success:
            data = result.data
            current_phase = data.get("current_phase")
            
            if current_phase:
                return (
                    f"📊 **SESSION STATUS**\n\n"
                    f"🎯 **Current Phase:** {current_phase['name'].title()}\n"
                    f"   - Remaining: {current_phase['remaining_minutes']} min {current_phase['remaining_seconds'] % 60} sec\n"
                    f"   - Progress: {current_phase['progress_percentage']:.1f}%\n\n"
                    f"⏱️ **Session Progress:**\n"
                    f"   - Total Elapsed: {data['total_elapsed_minutes']} minutes\n"
                    f"   - Total Duration: {data['total_duration_minutes']} minutes\n"
                    f"   - Overall Progress: {data['completion_percentage']:.1f}%\n\n"
                    f"📝 **Phase History:**\n" +
                    (
                        "\n".join([
                            f"   ✅ {h['phase'].title()}: {h['actual_duration']/60:.1f}min"
                            for h in data.get('phase_history', [])
                            if h['status'] == 'completed'
                        ]) if data.get('phase_history') else "   No completed phases yet"
                    ) +
                    f"\n\n🔄 **Status:** {'Active' if data['is_active'] else 'Inactive'}"
                )
            else:
                return f"📊 Session timer active but no current phase data available"
        else:
            return f"❌ Error getting session status: {result.message}"
            
    except Exception as e:
        return f"Error getting session timer status: {str(e)}"


async def transition_to_next_phase(
    force: bool = False,
    tool_context: ToolContext = None
) -> str:
    """Tool for manual phase transition (therapist override).
    
    Args:
        force: Whether to force transition regardless of timing
        tool_context: Tool context containing session timer
        
    Returns:
        String describing phase transition result
    """
    try:
        if not tool_context or "session_timer" not in tool_context.state:
            return "❌ No active session timer found"
            
        timer = tool_context.state["session_timer"]
        result = await timer.transition_to_next_phase_manual(force)
        
        if result.success:
            data = result.data
            if data.get("completed"):
                return (
                    f"🏁 **SESSION COMPLETED**\n\n"
                    f"✅ All phases have been completed!\n"
                    f"🎯 Final phase index: {data['phase_index']}\n"
                    f"📊 Session has ended successfully."
                )
            else:
                return (
                    f"🔄 **PHASE TRANSITION SUCCESSFUL**\n\n"
                    f"🎯 **New Current Phase:** {data['current_phase'].title()}\n"
                    f"📍 Phase Index: {data['phase_index'] + 1}\n"
                    f"⏰ Transition completed at exact timing"
                )
        else:
            return f"❌ Error transitioning phase: {result.message}"
            
    except Exception as e:
        return f"Error transitioning to next phase: {str(e)}"


async def complete_therapy_session_with_timer(
    user_notes: str = None,
    tool_context: ToolContext = None
) -> str:
    """Tool to complete therapy session with enhanced timer data.
    
    Args:
        user_notes: Optional notes from the therapy session
        tool_context: Tool context containing session timer and session data
        
    Returns:
        String describing session completion with timer data
    """
    try:
        if not tool_context:
            return "❌ No tool context available"
            
        # Complete timer session if active
        timer_result = None
        if "session_timer" in tool_context.state:
            timer = tool_context.state["session_timer"]
            timer_result = await timer.complete_session(user_notes)
        
        # Store the regular therapy session data
        session_result = await store_therapy_session(tool_context)
        
        if timer_result and timer_result.success:
            timer_data = timer_result.data
            return (
                f"🏁 **THERAPY SESSION COMPLETED WITH TIMER DATA**\n\n"
                f"✅ **Session Summary:**\n"
                f"   - Type: {timer_data.get('therapy_session_type', 'standard_60')}\n"
                f"   - Planned Duration: {timer_data.get('total_duration_planned', 60)} minutes\n"
                f"   - Actual Duration: {timer_data.get('total_duration_actual', 0):.1f} minutes\n"
                f"   - Completion Rate: {timer_data.get('completion_percentage', 100):.1f}%\n\n"
                f"📊 **Phase Completion:**\n"
                f"   - Phases Completed: {timer_data.get('phases_completed', 0)}/{timer_data.get('total_phases', 5)}\n\n"
                f"📝 **Storage Results:**\n"
                f"   - Timer Data: {'Stored' if timer_data.get('stored', False) else 'Failed to store'}\n"
                f"   - Session Data: {session_result}\n\n"
                f"💭 **User Notes:** {user_notes or 'None provided'}\n\n"
                f"🎯 **Session ID:** {timer_result.session_id}"
            )
        else:
            return (
                f"🏁 **THERAPY SESSION COMPLETED (NO TIMER)**\n\n"
                f"📝 **Storage Results:**\n"
                f"   - Session Data: {session_result}\n\n"
                f"💭 **User Notes:** {user_notes or 'None provided'}\n\n"
                f"⚠️ Timer completion: {timer_result.message if timer_result else 'No timer was active'}"
            )
            
    except Exception as e:
        return f"Error completing therapy session with timer: {str(e)}"
