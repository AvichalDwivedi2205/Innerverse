import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from google.adk import Agent, AgentConfig, Session
from google.genai import Client as GenAIClient

from config.api_keys import get_api_key
from shared.models.therapy_models import MentalExercise, TherapeuticFramework
from shared.utils.adk_communication import adk_comm, MessageType, Priority
from vector_db.schemas.mental_health_schemas import MentalExerciseVector, VectorType
from vector_db.utils.vector_operations import vector_ops
from vector_db.embeddings.gemini_embeddings import gemini_embeddings
from integrations.elevenlabs.voice_synthesis import elevenlabs_voice
from config.firebase_config import firebase_config

class MentalExerciseAgent(Agent):
    """Google ADK-powered agent for personalized mental health exercises"""
    
    def __init__(self):
        # Initialize Google ADK agent configuration
        config = AgentConfig(
            name="mental_exercise_agent",
            description="Personalized mental health exercise delivery using CBT, mindfulness, emotional regulation, and behavioral activation",
            model="gemini-2.5-pro",
            temperature=0.4,  # Moderate creativity for exercise adaptation
            max_tokens=3072,
            system_instructions=self._get_system_instructions()
        )
        
        super().__init__(config)
        
        # Initialize Gemini client
        self.gemini_client = GenAIClient(api_key=get_api_key('gemini_2_5_pro'))
        
        # Exercise library
        self.exercise_library = self._initialize_exercise_library()
        
        # User exercise history
        self.user_exercise_history = {}
        
        logging.info("Mental Exercise Agent initialized with Google ADK")
    
    def _get_system_instructions(self) -> str:
        """Get system instructions for the mental exercise agent"""
        return """You are the Mental Exercise Agent, specialized in delivering personalized mental health exercises. Your role is to:

1. EXERCISE RECOMMENDATION: Use vector similarity matching to recommend personalized mental exercises based on user's current mental state and therapeutic needs
2. GUIDED DELIVERY: Provide clear, step-by-step instructions for CBT, mindfulness, emotional regulation, and behavioral activation exercises
3. VOICE GUIDANCE: Integrate with ElevenLabs for voice-guided exercise sessions when requested
4. PROGRESS TRACKING: Monitor exercise completion and effectiveness based on user feedback
5. THERAPEUTIC INTEGRATION: Align exercises with ongoing therapy goals and frameworks

Exercise Categories:
- CBT: Cognitive restructuring, thought challenging, behavioral experiments
- Mindfulness: Present-moment awareness, breathing exercises, body scans
- Emotional Regulation: Emotion identification, distress tolerance, self-soothing
- Behavioral Activation: Activity scheduling, goal setting, mastery activities

Key Principles:
- Personalize exercises based on user's mental state and preferences
- Provide clear, actionable instructions with therapeutic rationale
- Encourage consistent practice while respecting user's capacity
- Track effectiveness and adapt recommendations accordingly
- Maintain therapeutic focus while being accessible and engaging"""

    def _initialize_exercise_library(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize the mental health exercise library"""
        return {
            'CBT': [
                {
                    'id': 'cbt_thought_record',
                    'name': 'Thought Record Exercise',
                    'description': 'Identify and challenge negative thought patterns',
                    'duration_minutes': 10,
                    'difficulty': 'beginner',
                    'instructions': [
                        'Identify a situation that triggered difficult emotions',
                        'Write down the automatic thoughts that came to mind',
                        'Rate the intensity of emotions (0-10)',
                        'Examine evidence for and against the thought',
                        'Create a more balanced, realistic thought',
                        'Re-rate emotional intensity after balanced thinking'
                    ],
                    'therapeutic_rationale': 'Helps identify cognitive distortions and develop balanced thinking patterns'
                }
            ],
            'mindfulness': [
                {
                    'id': 'mindfulness_breathing',
                    'name': '5-Minute Mindful Breathing',
                    'description': 'Simple breathing exercise for present-moment awareness',
                    'duration_minutes': 5,
                    'difficulty': 'beginner',
                    'instructions': [
                        'Find a comfortable seated position',
                        'Close your eyes or soften your gaze',
                        'Notice your natural breathing rhythm',
                        'Count breaths from 1 to 10, then start over',
                        'When mind wanders, gently return to counting',
                        'End with intention setting for your day'
                    ],
                    'therapeutic_rationale': 'Develops present-moment awareness and reduces anxiety through focused attention'
                }
            ],
            'emotional_regulation': [
                {
                    'id': 'emotion_surfing',
                    'name': 'Emotion Surfing Technique',
                    'description': 'Learn to ride emotional waves without being overwhelmed',
                    'duration_minutes': 8,
                    'difficulty': 'intermediate',
                    'instructions': [
                        'Notice and name the emotion you\'re experiencing',
                        'Observe where you feel it in your body',
                        'Breathe deeply and imagine the emotion as a wave',
                        'Remind yourself: "This feeling will pass"',
                        'Stay present with the emotion without fighting it',
                        'Notice as the intensity naturally decreases'
                    ],
                    'therapeutic_rationale': 'Teaches distress tolerance and emotional acceptance without avoidance'
                }
            ],
            'behavioral_activation': [
                {
                    'id': 'activity_scheduling',
                    'name': 'Meaningful Activity Planning',
                    'description': 'Schedule activities that bring pleasure and mastery',
                    'duration_minutes': 15,
                    'difficulty': 'beginner',
                    'instructions': [
                        'List 3 activities you used to enjoy',
                        'List 3 activities that give you a sense of accomplishment',
                        'Choose one from each list for this week',
                        'Schedule specific times for these activities',
                        'Rate anticipated pleasure/mastery (0-10)',
                        'Plan how to overcome potential obstacles'
                    ],
                    'therapeutic_rationale': 'Combats depression by increasing engagement in meaningful activities'
                }
            ]
        }
    
    async def recommend_personalized_exercise(self, session: Session, 
                                            recommendation_request: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend personalized mental exercise using vector similarity matching"""
        try:
            user_id = recommendation_request.get('user_id')
            current_mental_state = recommendation_request.get('mental_state', {})
            therapeutic_context = recommendation_request.get('therapeutic_context', {})
            preferred_duration = recommendation_request.get('preferred_duration', 10)
            
            logging.info(f"Generating exercise recommendation for user {user_id}")
            
            # Get user's exercise history and preferences
            user_context = await self._get_user_exercise_context(user_id)
            
            # Perform vector similarity matching
            similar_exercises = await self._find_similar_exercises(
                current_mental_state, therapeutic_context, user_context
            )
            
            # Select optimal exercise
            recommended_exercise = await self._select_optimal_exercise(
                session, similar_exercises, current_mental_state, therapeutic_context, preferred_duration
            )
            
            # Personalize exercise instructions
            personalized_exercise = await self._personalize_exercise(
                session, recommended_exercise, current_mental_state, user_context
            )
            
            # Generate voice guidance if requested
            voice_guidance = None
            if recommendation_request.get('include_voice', False):
                voice_guidance = await self._generate_voice_guidance(personalized_exercise)
            
            # Store exercise recommendation
            exercise_vector = await self._create_exercise_vector(
                user_id, personalized_exercise, current_mental_state
            )
            
            return {
                'exercise_id': personalized_exercise['id'],
                'exercise': personalized_exercise,
                'voice_guidance': voice_guidance,
                'vector_id': exercise_vector.id if exercise_vector else None,
                'recommendation_timestamp': datetime.now().isoformat(),
                'estimated_effectiveness': self._estimate_effectiveness(
                    personalized_exercise, current_mental_state
                )
            }
            
        except Exception as e:
            logging.error(f"Error recommending personalized exercise: {e}")
            return {'error': str(e)}
    
    async def _get_user_exercise_context(self, user_id: str) -> Dict[str, Any]:
        """Get user's exercise history and preferences"""
        try:
            # Get recent exercise completions
            recent_exercises = await vector_ops.semantic_search(
                query_vector=[0.0] * 384,  # Dummy vector for recent exercises
                vector_type=VectorType.MENTAL_EXERCISE,
                user_id=user_id,
                top_k=10
            )
            
            # Get user preferences from Firebase
            db = firebase_config.get_firestore_client()
            user_doc = db.collection('users').document(user_id).get()
            user_profile = user_doc.to_dict() if user_doc.exists else {}
            
            return {
                'recent_exercises': recent_exercises,
                'preferred_frameworks': user_profile.get('preferred_therapeutic_frameworks', ['CBT']),
                'exercise_preferences': user_profile.get('exercise_preferences', {}),
                'completed_exercises': len(recent_exercises),
                'preferred_duration': user_profile.get('preferred_exercise_duration', 10)
            }
            
        except Exception as e:
            logging.error(f"Error getting user exercise context: {e}")
            return {}
    
    async def _find_similar_exercises(self, mental_state: Dict[str, Any], 
                                    therapeutic_context: Dict[str, Any],
                                    user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find similar exercises using vector similarity matching"""
        try:
            # Import similarity matching tool
            from .tool_file import vector_similarity_tool
            
            similar_exercises = await vector_similarity_tool.find_similar_exercises(
                mental_state, therapeutic_context, user_context
            )
            
            return similar_exercises
            
        except Exception as e:
            logging.error(f"Error finding similar exercises: {e}")
            return []
    
    async def _select_optimal_exercise(self, session: Session, similar_exercises: List[Dict[str, Any]], 
                                     mental_state: Dict[str, Any], therapeutic_context: Dict[str, Any],
                                     preferred_duration: int) -> Dict[str, Any]:
        """Select optimal exercise using Gemini 2.5 Pro reasoning"""
        try:
            # Import prompts
            from .prompt_file import ExercisePrompts
            
            selection_prompt = ExercisePrompts.get_exercise_selection_prompt(
                similar_exercises, mental_state, therapeutic_context, preferred_duration
            )
            
            selection_response = await session.send_message(selection_prompt)
            
            # Parse selection (simplified for demo)
            selected_exercise_id = self._parse_exercise_selection(selection_response.text)
            
            # Find the selected exercise
            for exercise in similar_exercises:
                if exercise.get('id') == selected_exercise_id:
                    return exercise
            
            # Fallback to first exercise or default
            if similar_exercises:
                return similar_exercises[0]
            else:
                return self._get_default_exercise(mental_state)
            
        except Exception as e:
            logging.error(f"Error selecting optimal exercise: {e}")
            return self._get_default_exercise(mental_state)
    
    def _parse_exercise_selection(self, selection_text: str) -> str:
        """Parse exercise selection from Gemini response"""
        # Simplified parsing - would use more sophisticated parsing in production
        if 'thought_record' in selection_text.lower():
            return 'cbt_thought_record'
        elif 'breathing' in selection_text.lower():
            return 'mindfulness_breathing'
        elif 'emotion' in selection_text.lower():
            return 'emotion_surfing'
        elif 'activity' in selection_text.lower():
            return 'activity_scheduling'
        else:
            return 'mindfulness_breathing'  # Default
    
    def _get_default_exercise(self, mental_state: Dict[str, Any]) -> Dict[str, Any]:
        """Get default exercise based on mental state"""
        anxiety_level = mental_state.get('anxiety_level', 0.0)
        depression_level = mental_state.get('depression_level', 0.0)
        
        if anxiety_level > 0.6:
            return self.exercise_library['mindfulness'][0]
        elif depression_level > 0.6:
            return self.exercise_library['behavioral_activation'][0]
        else:
            return self.exercise_library['CBT'][0]
    
    async def _personalize_exercise(self, session: Session, exercise: Dict[str, Any], 
                                  mental_state: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Personalize exercise instructions for the user"""
        try:
            # Import prompts
            from .prompt_file import ExercisePrompts
            
            personalization_prompt = ExercisePrompts.get_exercise_personalization_prompt(
                exercise, mental_state, user_context
            )
            
            personalization_response = await session.send_message(personalization_prompt)
            
            # Create personalized exercise
            personalized_exercise = exercise.copy()
            personalized_exercise['personalized_instructions'] = personalization_response.text
            personalized_exercise['personalization_timestamp'] = datetime.now().isoformat()
            
            return personalized_exercise
            
        except Exception as e:
            logging.error(f"Error personalizing exercise: {e}")
            return exercise
    
    async def _generate_voice_guidance(self, exercise: Dict[str, Any]) -> Optional[bytes]:
        """Generate voice guidance for exercise using ElevenLabs"""
        try:
            # Prepare voice guidance text
            guidance_text = self._prepare_voice_guidance_text(exercise)
            
            # Generate voice guidance
            voice_guidance = await elevenlabs_voice.synthesize_mental_exercise_audio(
                guidance_text, exercise.get('category', 'mindfulness')
            )
            
            if voice_guidance:
                logging.info(f"Generated voice guidance for exercise {exercise['id']}")
                return voice_guidance
            
            return None
            
        except Exception as e:
            logging.error(f"Error generating voice guidance: {e}")
            return None
    
    def _prepare_voice_guidance_text(self, exercise: Dict[str, Any]) -> str:
        """Prepare text for voice guidance"""
        guidance_parts = [
            f"Welcome to the {exercise['name']} exercise.",
            f"This exercise will take approximately {exercise['duration_minutes']} minutes.",
            f"The purpose of this exercise is: {exercise.get('therapeutic_rationale', 'to support your mental wellness')}.",
            "Let's begin."
        ]
        
        # Add personalized instructions if available
        if 'personalized_instructions' in exercise:
            guidance_parts.append("Here are your personalized instructions:")
            guidance_parts.append(exercise['personalized_instructions'])
        else:
            # Add standard instructions
            guidance_parts.append("Follow these steps:")
            for i, instruction in enumerate(
            exercise.get('instructions', []), 1):
                guidance_parts.append(f"Step {i}: {instruction}")
        
        guidance_parts.extend([
            "Take your time with each step.",
            "Remember, there's no right or wrong way to do this exercise.",
            "When you're finished, take a moment to notice how you feel.",
            "Great job completing this exercise!"
        ])
        
        return " ".join(guidance_parts)
    
    async def _create_exercise_vector(self, user_id: str, exercise: Dict[str, Any], 
                                    mental_state: Dict[str, Any]) -> Optional[MentalExerciseVector]:
        """Create exercise vector for storage and similarity matching"""
        try:
            # Prepare text for embedding
            embedding_text = f"""
            Exercise: {exercise['name']}
            Category: {exercise.get('category', 'general')}
            Description: {exercise['description']}
            Therapeutic Rationale: {exercise.get('therapeutic_rationale', '')}
            Mental State Context: Anxiety {mental_state.get('anxiety_level', 0)}, Depression {mental_state.get('depression_level', 0)}
            """
            
            # Generate embedding
            embedding = await gemini_embeddings.generate_exercise_embedding(embedding_text)
            
            # Create exercise vector
            exercise_vector = MentalExerciseVector(
                id=f"exercise_{user_id}_{datetime.now().timestamp()}",
                user_id=user_id,
                vector=embedding,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                exercise_type=exercise.get('category', 'general'),
                difficulty_level=exercise.get('difficulty', 'beginner'),
                estimated_duration=exercise.get('duration_minutes', 10),
                effectiveness_score=0.0,  # Will be updated based on user feedback
                completion_rate=0.0,
                user_rating=0.0,
                tags=[exercise.get('category', 'general'), exercise.get('difficulty', 'beginner')],
                metadata={
                    'exercise_name': exercise['name'],
                    'therapeutic_rationale': exercise.get('therapeutic_rationale', ''),
                    'mental_state_context': mental_state,
                    'recommendation_timestamp': datetime.now().isoformat()
                }
            )
            
            # Store vector
            await vector_ops.upsert_mental_health_vector(exercise_vector)
            
            return exercise_vector
            
        except Exception as e:
            logging.error(f"Error creating exercise vector: {e}")
            return None
    
    def _estimate_effectiveness(self, exercise: Dict[str, Any], mental_state: Dict[str, Any]) -> float:
        """Estimate exercise effectiveness based on mental state"""
        anxiety_level = mental_state.get('anxiety_level', 0.0)
        depression_level = mental_state.get('depression_level', 0.0)
        stress_level = mental_state.get('stress_level', 0.0)
        
        exercise_type = exercise.get('category', 'general')
        
        # Simple effectiveness estimation
        if exercise_type == 'mindfulness' and anxiety_level > 0.6:
            return 0.8
        elif exercise_type == 'behavioral_activation' and depression_level > 0.6:
            return 0.9
        elif exercise_type == 'CBT' and stress_level > 0.6:
            return 0.7
        else:
            return 0.6  # Default moderate effectiveness
    
    async def track_exercise_completion(self, completion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track exercise completion and update effectiveness"""
        try:
            user_id = completion_data.get('user_id')
            exercise_id = completion_data.get('exercise_id')
            completed = completion_data.get('completed', False)
            user_rating = completion_data.get('user_rating', 0.0)
            feedback = completion_data.get('feedback', '')
            
            # Update exercise effectiveness
            await self._update_exercise_effectiveness(exercise_id, user_rating, completed)
            
            # Store completion data
            await self._store_completion_data(user_id, completion_data)
            
            # Send completion update to orchestration agent
            await self._send_completion_update(user_id, completion_data)
            
            return {
                'completion_tracked': True,
                'exercise_id': exercise_id,
                'updated_effectiveness': user_rating,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error tracking exercise completion: {e}")
            return {'error': str(e)}
    
    async def _update_exercise_effectiveness(self, exercise_id: str, user_rating: float, completed: bool):
        """Update exercise effectiveness based on user feedback"""
        try:
            # This would update the vector in Pinecone with new effectiveness data
            # Simplified for demo
            logging.info(f"Updated effectiveness for exercise {exercise_id}: rating {user_rating}, completed {completed}")
            
        except Exception as e:
            logging.error(f"Error updating exercise effectiveness: {e}")
    
    async def _store_completion_data(self, user_id: str, completion_data: Dict[str, Any]):
        """Store exercise completion data in Firebase"""
        try:
            db = firebase_config.get_firestore_client()
            
            completion_doc = {
                'user_id': user_id,
                'exercise_id': completion_data.get('exercise_id'),
                'completed': completion_data.get('completed', False),
                'user_rating': completion_data.get('user_rating', 0.0),
                'feedback': completion_data.get('feedback', ''),
                'completion_time': datetime.now(),
                'duration_actual': completion_data.get('duration_actual', 0)
            }
            
            db.collection('exercise_completions').add(completion_doc)
            
        except Exception as e:
            logging.error(f"Error storing completion data: {e}")
    
    async def _send_completion_update(self, user_id: str, completion_data: Dict[str, Any]):
        """Send completion update to orchestration agent"""
        try:
            completion_message = ADKMessage(
                message_id=f"exercise_completion_{user_id}_{datetime.now().timestamp()}",
                message_type=MessageType.EXERCISE_RECOMMENDATION,
                sender_agent="mental_exercise_agent",
                recipient_agent="mental_orchestration_agent",
                priority=Priority.NORMAL,
                timestamp=datetime.now(),
                payload={
                    'update_type': 'exercise_completion',
                    'user_id': user_id,
                    'completion_data': completion_data
                }
            )
            
            await adk_comm.send_message(completion_message)
            
        except Exception as e:
            logging.error(f"Error sending completion update: {e}")

# Global mental exercise agent instance
mental_exercise_agent = MentalExerciseAgent()
