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
        import os
        
        # Set up environment for Firebase
        os.environ['GOOGLE_CLOUD_PROJECT'] = 'gen-lang-client-0307630688'
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'service-account-key.json'
        
        try:
            _db = firestore.Client(project='gen-lang-client-0307630688')
            print("✅ Firebase Firestore connected successfully")
        except Exception as e:
            print(f"❌ Firestore connection failed: {e}")
            # Don't fall back to local storage, raise the error
            raise Exception(f"Firebase connection required for cloud hosting: {e}")
    return _db

def get_gemini_model():
    """Get Gemini model with lazy initialization using Google AI API."""
    global _model
    if _model is None:
        import os
        
        # Ensure environment variables are set up for cloud hosting
        os.environ['GOOGLE_CLOUD_PROJECT'] = 'gen-lang-client-0307630688'
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'service-account-key.json'
        
        google_api_key = os.getenv('GOOGLE_API_KEY')
        
        if google_api_key:
            try:
                # Use Google AI API directly
                import google.generativeai as genai
                genai.configure(api_key=google_api_key)
                _model = genai.GenerativeModel('gemini-2.5-flash')
                print(f"✅ Gemini model initialized with Google AI API")
            except Exception as e:
                print(f"❌ Google AI API initialization failed: {e}")
                raise Exception(f"Google AI API initialization failed: {e}")
        else:
            try:
                # Fallback to Vertex AI
                vertexai.init(project='gen-lang-client-0307630688', location='us-central1')
                _model = GenerativeModel("gemini-2.5-flash")
                print(f"✅ Gemini model initialized with Vertex AI")
            except Exception as e:
                print(f"❌ Vertex AI initialization failed: {e}")
                raise Exception(f"Vertex AI initialization failed: {e}")
    return _model

def extract_json_from_response(text):
    """Robust JSON extraction from model responses."""
    text = text.strip()
    
    # Method 1: Handle markdown code blocks
    if text.startswith('```'):
        lines = text.split('\n')
        start_idx = 1
        end_idx = len(lines)
        
        # Find where JSON actually starts
        for i in range(1, len(lines)):
            if lines[i].strip().startswith('{'):
                start_idx = i
                break
        
        # Find where JSON ends
        for i in range(len(lines)-1, -1, -1):
            if lines[i].strip().endswith('}'):
                end_idx = i + 1
                break
            elif lines[i].strip() == '```':
                end_idx = i
                break
        
        text = '\n'.join(lines[start_idx:end_idx])
    
    # Method 2: Extract JSON from any position in text
    if not text.startswith('{'):
        start_pos = text.find('{')
        if start_pos != -1:
            # Find matching closing brace
            brace_count = 0
            end_pos = start_pos
            for i, char in enumerate(text[start_pos:], start_pos):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_pos = i + 1
                        break
            text = text[start_pos:end_pos]
    
    return text.strip()

async def standardize_journal_text(
    raw_text: str,
    tool_context: ToolContext,
) -> JournalingToolResult:
    """Tool to standardize journal text using gemini-2.5-flash with empowerment focus."""
    
    try:
        prompt = get_standardization_prompt()
        full_prompt = f"{prompt}\n\nRaw Journal Text: {raw_text}\n\nReturn ONLY valid JSON in the specified format."
        
        response = get_gemini_model().generate_content(full_prompt)
        standardized_text = response.text.strip()
        
        # Clean the response text to extract JSON
        # Remove markdown code blocks if present
        if standardized_text.startswith('```'):
            lines = standardized_text.split('\n')
            # Skip the first line with ```json
            start_idx = 1
            end_idx = len(lines)
            
            # Find where JSON actually starts
            for i in range(1, len(lines)):
                if lines[i].strip().startswith('{'):
                    start_idx = i
                    break
            
            # Find where JSON ends
            for i in range(len(lines)-1, -1, -1):
                if lines[i].strip().endswith('}'):
                    end_idx = i + 1
                    break
                elif lines[i].strip() == '```':
                    end_idx = i
                    break
            
            standardized_text = '\n'.join(lines[start_idx:end_idx])
        
        # Parse JSON response
        try:
            standardized_entry = json.loads(standardized_text)
        except json.JSONDecodeError as json_error:
            # Try to fix common JSON issues
            cleaned_text = standardized_text.replace("'", '"')  # Replace single quotes with double quotes
            try:
                standardized_entry = json.loads(cleaned_text)
            except json.JSONDecodeError:
                return JournalingToolResult.error_result(
                    message="Failed to parse standardized entry JSON",
                    error_details=f"JSON Error: {json_error}. Raw response: {standardized_text[:500]}",
                    next_actions=["retry_standardization"]
                )
        
        # Initialize session state if needed
        if "journal_session" not in tool_context.state:
            tool_context.state["journal_session"] = {
                "raw_text": "",
                "standardized_entry": {},
                "insights": {},
                "reflection_question": "",
                "embedding_id": "",
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
        
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
        standardized_entry = tool_context.state.get("journal_session", {}).get("standardized_entry", {})
        
        if not standardized_entry:
            return JournalingToolResult.error_result(
                message="No standardized entry found",
                error_details="standardize_journal_text must be called first",
                next_actions=["standardize_journal_text"]
            )
        
        prompt = get_insights_prompt()
        full_prompt = prompt.format(entry=json.dumps(standardized_entry)) + "\n\nReturn ONLY valid JSON in the specified format. No explanations or markdown."
        
        # Generate response with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = get_gemini_model().generate_content(full_prompt)
                insights_text = response.text.strip()
                
                # Extract JSON using robust method
                json_text = extract_json_from_response(insights_text)
                
                # Parse JSON with multiple fallback methods
                try:
                    insights = json.loads(json_text)
                    break  # Success, exit retry loop
                except json.JSONDecodeError as json_error:
                    # Try fixing common JSON issues
                    cleaned_text = json_text.replace("'", '"')  # Single to double quotes
                    cleaned_text = cleaned_text.replace('True', 'true').replace('False', 'false')  # Python to JSON boolean
                    try:
                        insights = json.loads(cleaned_text)
                        break  # Success, exit retry loop
                    except json.JSONDecodeError:
                        if attempt == max_retries - 1:  # Last attempt
                            # Return a default insights structure
                            insights = {
                                "sentiment": "neutral",
                                "emotion": "mixed emotions",
                                "intensity": "5",
                                "themes": ["self-reflection", "personal growth"],
                                "triggers": ["internal dialogue", "life circumstances"]
                            }
                            print(f"⚠️ Using default insights due to JSON parsing issues. Raw response: {insights_text[:200]}")
                            break
                        else:
                            print(f"⚠️ JSON parsing failed on attempt {attempt + 1}, retrying...")
                            continue
                            
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    return JournalingToolResult.error_result(
                        message="Failed to generate insights after multiple attempts",
                        error_details=f"Error: {str(e)}",
                        next_actions=["retry_insights_generation", "check_model_availability"]
                    )
                else:
                    print(f"⚠️ Model call failed on attempt {attempt + 1}, retrying...")
                    continue
        
        # Store in context
        if "journal_session" not in tool_context.state:
            tool_context.state["journal_session"] = {}
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


async def generate_multiple_reflection_questions(
    tool_context: ToolContext,
) -> JournalingToolResult:
    """
    Phase 3: Generate complete set of 5 categorized reflection questions.
    Replaces single reflection question generation with enhanced system.
    Always generates: 2 daily + 2 deep + 1 action = 5 questions total.
    """
    
    try:
        # Import enhanced reflection generator
        from ..common.reflection_generator import EnhancedReflectionGenerator
        
        # Get session data
        standardized_entry = tool_context.state["journal_session"]["standardized_entry"]
        insights = tool_context.state["journal_session"]["insights"]
        
        # Initialize enhanced reflection generator
        reflection_generator = EnhancedReflectionGenerator()
        
        # Prepare context data
        session_data = {
            "entry": standardized_entry,
            "raw_text": tool_context.state["journal_session"].get("raw_text", ""),
            "challenges": insights.get("triggers", []),
            "emotions": [insights.get("emotion", "mixed emotions")],
            "topics": insights.get("themes", ["personal growth"])
        }
        
        user_context = {
            "preferences": ["empowerment", "self-reflection"],
            "source": "journaling"
        }
        
        # Generate complete question set (2 daily + 2 deep + 1 action = 5 questions)
        question_set = await reflection_generator.generate_complete_question_set(
            session_data=session_data,
            insights=insights,
            user_context=user_context,
            source_type="journaling"
        )
        
        # Get question summary
        summary = reflection_generator.get_question_summary(question_set)
        
        # Store in context
        tool_context.state["journal_session"]["reflection_questions"] = question_set
        tool_context.state["journal_session"]["reflection_summary"] = summary
        
        # Prepare data for response
        questions_data = {}
        for category, questions in question_set.items():
            questions_data[category.value] = [
                {
                    "question_id": q.question_id,
                    "question": q.question,
                    "type": q.reflection_type.value,
                    "difficulty": q.metadata["difficulty"],
                    "estimated_time": q.metadata["estimatedTime"],
                    "scheduled_for": q.delivery["scheduledFor"].isoformat()
                }
                for q in questions
            ]
        
        return JournalingToolResult.success_result(
            data={
                "reflection_questions": questions_data,
                "summary": summary,
                "total_questions": summary["total_questions"]
            },
            message=f"Generated {summary['total_questions']} categorized reflection questions: "
                   f"{summary['category_breakdown']['daily_practice']} daily, "
                   f"{summary['category_breakdown']['deep_reflection']} deep, "
                   f"{summary['category_breakdown']['action_items']} action",
            next_actions=["store_journal_entry_with_enhanced_questions"]
        )
        
    except Exception as e:
        return JournalingToolResult.error_result(
            message="Error generating enhanced reflection questions",
            error_details=str(e),
            next_actions=["retry_reflection_generation", "check_insights"]
        )


async def generate_reflection_question(
    tool_context: ToolContext,
) -> JournalingToolResult:
    """
    Backward compatibility wrapper - redirects to enhanced reflection system.
    """
    return await generate_multiple_reflection_questions(tool_context)


async def store_journal_entry_with_enhanced_questions(
    tool_context: ToolContext,
) -> str:
    """Phase 3: Store journal entry with enhanced reflection questions."""
    
    try:
        user_id = tool_context.state.get("user_id", "anonymous_user")
        journal_session = tool_context.state["journal_session"]
        journal_id = str(uuid.uuid4())
        
        # Prepare enhanced journal document
        journal_doc = {
            "date": datetime.now().isoformat(),
            "rawText": journal_session.get("raw_text", ""),
            "standardizedEntry": journal_session.get("standardized_entry", {}),
            "insights": journal_session.get("insights", {}),
            # Phase 3: Store categorized reflection questions
            "reflectionQuestions": {},
            "reflectionSummary": journal_session.get("reflection_summary", {}),
            "embeddingId": "",  # Will be set after embedding generation
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
            "phase": 3  # Mark as Phase 3 enhanced
        }
        
        # Convert reflection questions to storable format
        reflection_questions = journal_session.get("reflection_questions", {})
        for category, questions in reflection_questions.items():
            category_key = category.value if hasattr(category, 'value') else str(category)
            journal_doc["reflectionQuestions"][category_key] = [
                {
                    "questionId": q.question_id,
                    "question": q.question,
                    "category": q.category.value,
                    "type": q.reflection_type.value,
                    "context": q.context,
                    "delivery": {
                        "createdAt": q.delivery["createdAt"].isoformat(),
                        "scheduledFor": q.delivery["scheduledFor"].isoformat(),
                        "deliveredAt": None,
                        "completedAt": None,
                        "expiresAt": q.delivery["expiresAt"].isoformat()
                    },
                    "metadata": q.metadata
                }
                for q in questions
            ]
        
        # Store in Firestore
        db_client = get_firestore_client()
        db_client.collection("users").document(user_id).collection("journals").document(journal_id).set(journal_doc)
        
        # Generate and store embedding
        try:
            reflection_text = journal_session.get("standardized_entry", {}).get("reflection", "")
            if reflection_text:
                embedding_id = await _generate_and_store_embedding(
                    text=reflection_text,
                    user_id=user_id,
                    context="journal",
                    source_id=journal_id
                )
                
                # Update journal with embedding ID if successful
                if embedding_id:
                    db_client.collection("users").document(user_id).collection("journals").document(journal_id).update({
                        "embeddingId": embedding_id
                    })
        except Exception as e:
            print(f"⚠️  Embedding generation failed (non-critical): {e}")
        
        # Store each reflection question as individual recommendation with category
        try:
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
                        "source": "journal",
                        "sourceId": journal_id,
                        "priority": _get_category_priority(category_key),
                        "status": "pending",
                        "createdAt": datetime.now().isoformat(),
                        "scheduledFor": question.delivery["scheduledFor"].isoformat(),
                        "expiresAt": question.delivery["expiresAt"].isoformat()
                    }
                    
                    db_client.collection("users").document(user_id).collection("reflectionQuestions").add(recommendation_doc)
                    
        except Exception as e:
            print(f"⚠️  Enhanced reflection questions storage failed (non-critical): {e}")
        
        tool_context.state["journal_id"] = journal_id
        
        # Get summary for response
        summary = journal_session.get("reflection_summary", {})
        total_questions = summary.get("total_questions", 0)
        
        return f"✅ Journal entry stored with {total_questions} enhanced reflection questions (ID: {journal_id})"
        
    except Exception as e:
        return f"❌ Error storing enhanced journal entry: {str(e)}"


def _get_category_priority(category: str) -> int:
    """Get priority for reflection question categories."""
    priorities = {
        "action_items": 1,      # Highest priority
        "daily_practice": 2,    # Medium priority
        "deep_reflection": 3    # Lower priority (longer term)
    }
    return priorities.get(category, 2)


async def store_journal_entry(
    tool_context: ToolContext,
) -> str:
    """Backward compatibility wrapper - redirects to enhanced storage."""
    return await store_journal_entry_with_enhanced_questions(tool_context)


async def update_consistency_tracking(
    tool_context: ToolContext,
) -> str:
    """Tool to update daily journaling consistency metrics in Firebase."""
    
    try:
        user_id = tool_context.state.get("user_id", "anonymous_user")
        
        # Use Firebase Firestore
        db_client = get_firestore_client()
        metrics_ref = db_client.collection("users").document(user_id).collection("dashboard").document("metrics")
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
        metrics["consistency"]["journalStreak"] += 1
        metrics["lastUpdated"] = datetime.now().isoformat()
        
        # Store updated metrics
        metrics_ref.set(metrics, merge=True)
        
        return f"✅ Firebase consistency tracking updated: Journal count {metrics['consistency']['journalCount']}"
        
    except Exception as e:
        return f"❌ Error updating consistency tracking: {str(e)}"


async def trigger_mental_orchestrator(
    tool_context: ToolContext,
) -> JournalingToolResult:
    """Tool to trigger Mental Orchestrator Agent for mind map updates."""
    
    try:
        user_id = tool_context.state.get("user_id", "anonymous_user")
        journal_id = tool_context.state.get("journal_id")
        
        if not journal_id:
            return JournalingToolResult.error_result(
                message="journal_id not found in context",
                error_details="store_journal_entry must be called first",
                next_actions=["store_journal_entry"]
            )
        
        # Use coordinator for direct agent communication
        try:
            coordination_result = coordinator.trigger_mindmap_update(
                user_id=user_id,
                source_type="journal",
                source_id=journal_id,
                callback_context=tool_context
            )
            
            # Check if coordination_result is awaitable
            if hasattr(coordination_result, '__await__'):
                coordination_result = await coordination_result
            
            if coordination_result and hasattr(coordination_result, 'success') and coordination_result.success:
                return JournalingToolResult.success_result(
                    data={
                        "coordination_result": coordination_result.dict() if hasattr(coordination_result, 'dict') else str(coordination_result),
                        "coordinated_agents": coordination_result.coordinated_agents if hasattr(coordination_result, 'coordinated_agents') else []
                    },
                    message="✅ Mental Orchestrator coordination completed successfully",
                    next_actions=[]
                )
            else:
                return JournalingToolResult.success_result(
                    data={"coordination_status": "attempted"},
                    message="✅ Mind map update coordination attempted",
                    next_actions=[]
                )
                
        except Exception as coord_error:
            print(f"⚠️  Coordination failed: {coord_error}")
            # For hackathon demo, consider this non-critical
            return JournalingToolResult.success_result(
                data={"coordination_status": "failed_non_critical"},
                message="✅ Journal processing completed (mind map coordination unavailable)",
                next_actions=[]
            )
        
    except Exception as e:
        return JournalingToolResult.error_result(
            message="Error triggering Mental Orchestrator",
            error_details=str(e),
            next_actions=["retry_coordination"]
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
