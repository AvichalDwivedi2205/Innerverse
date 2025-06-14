import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from google.genai import Client as GenAIClient
from config.api_keys import get_api_key
from vector_db.utils.vector_operations import vector_ops
from vector_db.schemas.mental_health_schemas import VectorType
from vector_db.embeddings.gemini_embeddings import gemini_embeddings
from integrations.elevenlabs.voice_synthesis import elevenlabs_voice
from config.firebase_config import firebase_config

class VectorSimilarityTool:
    """Tool for vector similarity matching of mental health exercises"""
    
    def __init__(self):
        self.vector_ops = vector_ops
        self.embeddings = gemini_embeddings
    
    async def find_similar_exercises(self, mental_state: Dict[str, Any], 
                                   therapeutic_context: Dict[str, Any],
                                   user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find similar exercises using vector similarity matching"""
        try:
            # Create query vector from mental state and context
            query_text = self._create_query_text(mental_state, therapeutic_context)
            
            # Generate query embedding
            query_embedding = await self.embeddings.generate_exercise_embedding(query_text)
            
            # Perform semantic search
            similar_exercises = await self.vector_ops.semantic_search(
                query_vector=query_embedding,
                vector_type=VectorType.MENTAL_EXERCISE,
                user_id=user_context.get('user_id'),
                top_k=5
            )
            
            # Enhance with exercise library data
            enhanced_exercises = await self._enhance_with_library_data(similar_exercises)
            
            return enhanced_exercises
            
        except Exception as e:
            logging.error(f"Error finding similar exercises: {e}")
            return self._get_fallback_exercises(mental_state)
    
    def _create_query_text(self, mental_state: Dict[str, Any], 
                          therapeutic_context: Dict[str, Any]) -> str:
        """Create query text for vector similarity search"""
        query_parts = []
        
        # Add mental state information
        anxiety_level = mental_state.get('anxiety_level', 0.0)
        depression_level = mental_state.get('depression_level', 0.0)
        stress_level = mental_state.get('stress_level', 0.0)
        
        if anxiety_level > 0.6:
            query_parts.append("anxiety relief mindfulness breathing calming")
        if depression_level > 0.6:
            query_parts.append("depression behavioral activation mood lifting")
        if stress_level > 0.6:
            query_parts.append("stress management CBT cognitive restructuring")
        
        # Add therapeutic context
        framework = therapeutic_context.get('framework', '')
        if framework:
            query_parts.append(framework)
        
        session_goals = therapeutic_context.get('session_goals', [])
        if session_goals:
            query_parts.extend(session_goals)
        
        return " ".join(query_parts)
    
    async def _enhance_with_library_data(self, similar_exercises: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance search results with exercise library data"""
        enhanced = []
        
        # Exercise library (simplified)
        exercise_library = {
            'mindfulness_breathing': {
                'id': 'mindfulness_breathing',
                'name': '5-Minute Mindful Breathing',
                'category': 'mindfulness',
                'duration_minutes': 5,
                'difficulty': 'beginner',
                'instructions': [
                    'Find a comfortable seated position',
                    'Close your eyes or soften your gaze',
                    'Notice your natural breathing rhythm',
                    'Count breaths from 1 to 10, then start over',
                    'When mind wanders, gently return to counting',
                    'End with intention setting for your day'
                ]
            },
            'cbt_thought_record': {
                'id': 'cbt_thought_record',
                'name': 'Thought Record Exercise',
                'category': 'CBT',
                'duration_minutes': 10,
                'difficulty': 'beginner',
                'instructions': [
                    'Identify a situation that triggered difficult emotions',
                    'Write down the automatic thoughts that came to mind',
                    'Rate the intensity of emotions (0-10)',
                    'Examine evidence for and against the thought',
                    'Create a more balanced, realistic thought',
                    'Re-rate emotional intensity after balanced thinking'
                ]
            }
        }
        
        for exercise in similar_exercises:
            exercise_id = exercise.get('id', 'mindfulness_breathing')
            library_data = exercise_library.get(exercise_id, exercise_library['mindfulness_breathing'])
            
            enhanced_exercise = {
                **library_data,
                'similarity_score': exercise.get('score', 0.8),
                'metadata': exercise.get('metadata', {})
            }
            enhanced.append(enhanced_exercise)
        
        return enhanced
    
    def _get_fallback_exercises(self, mental_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get fallback exercises when vector search fails"""
        anxiety_level = mental_state.get('anxiety_level', 0.0)
        depression_level = mental_state.get('depression_level', 0.0)
        
        if anxiety_level > 0.6:
            return [{
                'id': 'mindfulness_breathing',
                'name': '5-Minute Mindful Breathing',
                'category': 'mindfulness',
                'duration_minutes': 5,
                'difficulty': 'beginner'
            }]
        elif depression_level > 0.6:
            return [{
                'id': 'activity_scheduling',
                'name': 'Meaningful Activity Planning',
                'category': 'behavioral_activation',
                'duration_minutes': 15,
                'difficulty': 'beginner'
            }]
        else:
            return [{
                'id': 'cbt_thought_record',
                'name': 'Thought Record Exercise',
                'category': 'CBT',
                'duration_minutes': 10,
                'difficulty': 'beginner'
            }]

class VoiceGuidanceTool:
    """Tool for generating voice guidance using ElevenLabs"""
    
    def __init__(self):
        self.elevenlabs = elevenlabs_voice
    
    async def generate_exercise_guidance(self, exercise: Dict[str, Any], 
                                       personalization_context: Dict[str, Any]) -> Optional[bytes]:
        """Generate voice guidance for mental health exercise"""
        try:
            # Prepare guidance script
            guidance_script = self._prepare_guidance_script(exercise, personalization_context)
            
            # Generate voice guidance
            voice_guidance = await self.elevenlabs.synthesize_mental_exercise_audio(
                guidance_script, exercise.get('category', 'mindfulness')
            )
            
            if voice_guidance:
                logging.info(f"Generated voice guidance for exercise {exercise.get('id')}")
                return voice_guidance
            
            return None
            
        except Exception as e:
            logging.error(f"Error generating voice guidance: {e}")
            return None
    
    def _prepare_guidance_script(self, exercise: Dict[str, Any], 
                               context: Dict[str, Any]) -> str:
        """Prepare voice guidance script"""
        script_parts = [
            f"Welcome to the {exercise.get('name', 'mental health exercise')}.",
            f"This exercise will take about {exercise.get('duration_minutes', 10)} minutes.",
            "Find a comfortable position where you won't be disturbed.",
            "Let's begin."
        ]
        
        # Add personalized instructions
        if 'personalized_instructions' in exercise:
            script_parts.append("Here are your personalized instructions:")
            script_parts.append(exercise['personalized_instructions'])
        else:
            # Add standard instructions with pauses
            instructions = exercise.get('instructions', [])
            for i, instruction in enumerate(instructions, 1):
                script_parts.append(f"Step {i}: {instruction}")
                if i < len(instructions):
                    script_parts.append("Take a moment to complete this step.")
        
        script_parts.extend([
            "You're doing great.",
            "Take a moment to notice how you feel after completing this exercise.",
            "Remember, regular practice helps build these skills.",
            "Thank you for taking time for your mental health."
        ])
        
        return " ".join(script_parts)

class ExerciseTrackingTool:
    """Tool for tracking exercise completion and effectiveness"""
    
    def __init__(self):
        self.firebase_db = firebase_config.get_firestore_client()
    
    async def track_exercise_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track exercise session completion and feedback"""
        try:
            # Store session data
            session_doc = {
                'user_id': session_data.get('user_id'),
                'exercise_id': session_data.get('exercise_id'),
                'started_at': session_data.get('started_at', datetime.now()),
                'completed_at': session_data.get('completed_at'),
                'duration_actual': session_data.get('duration_actual', 0),
                'completed': session_data.get('completed', False),
                'user_rating': session_data.get('user_rating', 0.0),
                'feedback': session_data.get('feedback', ''),
                'mood_before': session_data.get('mood_before', 0.0),
                'mood_after': session_data.get('mood_after', 0.0),
                'created_at': datetime.now()
            }
            
            doc_ref = self.firebase_db.collection('exercise_sessions').add(session_doc)
            
            # Calculate effectiveness
            effectiveness = self._calculate_effectiveness(session_data)
            
            return {
                'session_id': doc_ref[1].id,
                'effectiveness_score': effectiveness,
                'mood_improvement': session_data.get('mood_after', 0.0) - session_data.get('mood_before', 0.0),
                'tracked_successfully': True
            }
            
        except Exception as e:
            logging.error(f"Error tracking exercise session: {e}")
            return {'error': str(e)}
    
    def _calculate_effectiveness(self, session_data: Dict[str, Any]) -> float:
        """Calculate exercise effectiveness score"""
        factors = []
        
        # Completion factor
        if session_data.get('completed', False):
            factors.append(0.4)
        
        # User rating factor
        user_rating = session_data.get('user_rating', 0.0)
        factors.append(user_rating / 5.0 * 0.3)  # Normalize to 0-1 scale
        
        # Mood improvement factor
        mood_before = session_data.get('mood_before', 0.0)
        mood_after = session_data.get('mood_after', 0.0)
        mood_improvement = max(0, mood_after - mood_before)
        factors.append(mood_improvement * 0.3)
        
        return sum(factors)
    
    async def get_exercise_history(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get user's exercise history"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            sessions_query = (self.firebase_db.collection('exercise_sessions')
                            .where('user_id', '==', user_id)
                            .where('created_at', '>=', start_date)
                            .where('created_at', '<=', end_date)
                            .order_by('created_at', direction='DESCENDING'))
            
            sessions = []
            docs = await asyncio.to_thread(sessions_query.get)
            
            for doc in docs:
                session_data = doc.to_dict()
                session_data['session_id'] = doc.id
                sessions.append(session_data)
            
            return sessions
            
        except Exception as e:
            logging.error(f"Error getting exercise history: {e}")
            return []

# Initialize tool instances
vector_similarity_tool = VectorSimilarityTool()
voice_guidance_tool = VoiceGuidanceTool()
exercise_tracking_tool = ExerciseTrackingTool()
