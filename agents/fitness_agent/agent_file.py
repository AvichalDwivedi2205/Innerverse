import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from google.adk import Agent, AgentConfig, Session
from google.genai import Client as GenAIClient

from config.api_keys import get_api_key
from shared.utils.adk_communication import adk_comm, MessageType, Priority
from config.firebase_config import firebase_config
from integrations.elevenlabs.voice_synthesis import elevenlabs_voice
from integrations.tavus.video_generation import tavus_video
from integrations.google_calendar.calendar_integration import google_calendar

class FitnessAgent(Agent):
    """Google ADK-powered fitness agent for workout planning and personal training"""
    
    def __init__(self):
        # Initialize Google ADK agent configuration
        config = AgentConfig(
            name="fitness_agent",
            description="Workout plan generator and personal trainer consultation for exercise planning and modifications",
            model="gemini-2.5-pro",
            temperature=0.5,  # Balanced creativity for workout variety
            max_tokens=2048,
            system_instructions=self._get_system_instructions()
        )
        
        super().__init__(config)
        
        # Initialize Gemini client
        self.gemini_client = GenAIClient(api_key=get_api_key('gemini_2_5_pro'))
        
        # User fitness profiles
        self.user_profiles = {}
        
        logging.info("Fitness Agent initialized with Google ADK")
    
    def _get_system_instructions(self) -> str:
        """Get system instructions for the fitness agent"""
        return """You are a Fitness Agent providing safe, practical workout planning and personal training guidance. Your role is to:

1. WORKOUT PLAN GENERATION: Create personalized weekly workout plans based on goals, fitness level, and physical limitations
2. PERSONAL TRAINING CONSULTATION: Provide exercise guidance through text, voice, and video consultations
3. PLAN MODIFICATION: Allow users to modify workout plans based on schedule, equipment, or physical changes
4. GOAL FLEXIBILITY: Enable users to change fitness goals and limitations anytime
5. GOOGLE CALENDAR INTEGRATION: Schedule workouts automatically through the scheduling agent

Key Principles:
- Always prioritize safety and respect physical limitations
- Provide clear exercise instructions with proper form guidance
- Offer modifications for injuries and equipment constraints
- Create realistic, achievable workout plans
- Focus on progressive overload and sustainable fitness habits
- Encourage consistency over intensity for beginners

Exercise Categories:
- Strength training (bodyweight, weights, resistance bands)
- Cardiovascular exercise (walking, running, cycling, HIIT)
- Flexibility and mobility (stretching, yoga, foam rolling)
- Functional movement (daily life activities, balance, coordination)

Always ask about injuries, physical limitations, and available equipment before creating plans."""

    async def generate_workout_plan(self, session: Session, plan_request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized workout plan using Gemini 2.5 Pro"""
        try:
            user_id = plan_request.get('user_id')
            fitness_goals = plan_request.get('fitness_goals', ['general_fitness'])
            current_fitness_level = plan_request.get('fitness_level', 'beginner')
            physical_limitations = plan_request.get('physical_limitations', [])
            available_equipment = plan_request.get('available_equipment', ['bodyweight'])
            time_per_session = plan_request.get('time_per_session', 30)
            sessions_per_week = plan_request.get('sessions_per_week', 3)
            
            logging.info(f"Generating workout plan for user {user_id}")
            
            # Store user fitness profile
            await self._store_user_fitness_profile(user_id, plan_request)
            
            # Generate workout plan using Gemini 2.5 Pro
            workout_plan = await self._create_workout_plan(
                session, fitness_goals, current_fitness_level, physical_limitations,
                available_equipment, time_per_session, sessions_per_week
            )
            
            # Store workout plan
            plan_id = await self._store_workout_plan(user_id, workout_plan)
            
            # Schedule workouts in Google Calendar
            calendar_events = await self._schedule_workouts(user_id, workout_plan)
            
            # Generate voice consultation if requested
            voice_consultation = None
            if plan_request.get('include_voice', False):
                voice_consultation = await self._generate_voice_consultation(workout_plan)
            
            # Generate video consultation if requested
            video_consultation = None
            if plan_request.get('include_video', False):
                video_consultation = await self._generate_video_consultation(workout_plan, plan_request)
            
            return {
                'plan_id': plan_id,
                'workout_plan': workout_plan,
                'calendar_events': calendar_events,
                'voice_consultation': voice_consultation,
                'video_consultation': video_consultation,
                'generated_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error generating workout plan: {e}")
            return {'error': str(e)}
    
    async def _store_user_fitness_profile(self, user_id: str, profile_data: Dict[str, Any]):
        """Store user fitness profile in Firebase"""
        try:
            db = firebase_config.get_firestore_client()
            
            fitness_profile = {
                'user_id': user_id,
                'fitness_goals': profile_data.get('fitness_goals', []),
                'fitness_level': profile_data.get('fitness_level', 'beginner'),
                'physical_limitations': profile_data.get('physical_limitations', []),
                'available_equipment': profile_data.get('available_equipment', []),
                'time_per_session': profile_data.get('time_per_session', 30),
                'sessions_per_week': profile_data.get('sessions_per_week', 3),
                'updated_at': datetime.now()
            }
            
            db.collection('fitness_profiles').document(user_id).set(fitness_profile)
            
        except Exception as e:
            logging.error(f"Error storing fitness profile: {e}")
    
    async def _create_workout_plan(self, session: Session, fitness_goals: List[str],
                                 fitness_level: str, physical_limitations: List[str],
                                 available_equipment: List[str], time_per_session: int,
                                 sessions_per_week: int) -> Dict[str, Any]:
        """Create workout plan using Gemini 2.5 Pro"""
        try:
            # Import prompts
            from .prompt_file import FitnessPrompts
            
            workout_plan_prompt = FitnessPrompts.get_workout_plan_generation_prompt(
                fitness_goals, fitness_level, physical_limitations, available_equipment,
                time_per_session, sessions_per_week
            )
            
            workout_plan_response = await session.send_message(workout_plan_prompt)
            
            # Parse workout plan (simplified for demo)
            workout_plan = {
                'weekly_schedule': self._parse_weekly_schedule(workout_plan_response.text, sessions_per_week),
                'exercise_library': self._generate_exercise_library(available_equipment, physical_limitations),
                'progression_plan': self._create_progression_plan(fitness_level, fitness_goals),
                'safety_guidelines': self._generate_safety_guidelines(physical_limitations),
                'equipment_needed': available_equipment,
                'generated_plan': workout_plan_response.text
            }
            
            return workout_plan
            
        except Exception as e:
            logging.error(f"Error creating workout plan: {e}")
            return {}
    
    def _parse_weekly_schedule(self, plan_text: str, sessions_per_week: int) -> Dict[str, Dict[str, Any]]:
        """Parse weekly workout schedule from text"""
        # Simplified parsing - would use more sophisticated parsing in production
        weekly_schedule = {}
        
        workout_types = ['upper_body', 'lower_body', 'cardio', 'full_body', 'flexibility']
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        # Distribute workouts across the week
        workout_days = days[:sessions_per_week]
        
        for i, day in enumerate(workout_days):
            workout_type = workout_types[i % len(workout_types)]
            weekly_schedule[day] = {
                'workout_type': workout_type,
                'exercises': self._get_sample_exercises(workout_type),
                'duration_minutes': 30,
                'intensity': 'moderate'
            }
        
        # Add rest days
        for day in days[sessions_per_week:]:
            weekly_schedule[day] = {
                'workout_type': 'rest',
                'activity': 'Active recovery or complete rest',
                'duration_minutes': 0
            }
        
        return weekly_schedule
    
    def _get_sample_exercises(self, workout_type: str) -> List[Dict[str, Any]]:
        """Get sample exercises for workout type"""
        exercise_library = {
            'upper_body': [
                {'name': 'Push-ups', 'sets': 3, 'reps': '8-12', 'rest': '60s'},
                {'name': 'Pull-ups/Assisted Pull-ups', 'sets': 3, 'reps': '5-10', 'rest': '60s'},
                {'name': 'Shoulder Press', 'sets': 3, 'reps': '8-12', 'rest': '60s'}
            ],
            'lower_body': [
                {'name': 'Squats', 'sets': 3, 'reps': '10-15', 'rest': '60s'},
                {'name': 'Lunges', 'sets': 3, 'reps': '8-12 each leg', 'rest': '60s'},
                {'name': 'Glute Bridges', 'sets': 3, 'reps': '12-15', 'rest': '45s'}
            ],
            'cardio': [
                {'name': 'Brisk Walking', 'duration': '20-30 minutes', 'intensity': 'moderate'},
                {'name': 'Jumping Jacks', 'sets': 3, 'duration': '30s', 'rest': '30s'},
                {'name': 'High Knees', 'sets': 3, 'duration': '30s', 'rest': '30s'}
            ],
            'full_body': [
                {'name': 'Burpees', 'sets': 3, 'reps': '5-8', 'rest': '90s'},
                {'name': 'Mountain Climbers', 'sets': 3, 'duration': '30s', 'rest': '60s'},
                {'name': 'Plank', 'sets': 3, 'duration': '30-60s', 'rest': '60s'}
            ],
            'flexibility': [
                {'name': 'Forward Fold', 'duration': '30s', 'sets': 2},
                {'name': 'Cat-Cow Stretch', 'duration': '60s', 'sets': 1},
                {'name': 'Child\'s Pose', 'duration': '60s', 'sets': 1}
            ]
        }
        
        return exercise_library.get(workout_type, [])
    
    def _generate_exercise_library(self, available_equipment: List[str], 
                                 physical_limitations: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Generate exercise library based on equipment and limitations"""
        # Simplified exercise library
        base_library = {
            'bodyweight': [
                {'name': 'Push-ups', 'muscle_groups': ['chest', 'shoulders', 'triceps']},
                {'name': 'Squats', 'muscle_groups': ['quadriceps', 'glutes', 'hamstrings']},
                {'name': 'Plank', 'muscle_groups': ['core', 'shoulders']},
                {'name': 'Lunges', 'muscle_groups': ['quadriceps', 'glutes', 'hamstrings']}
            ],
            'dumbbells': [
                {'name': 'Dumbbell Press', 'muscle_groups': ['chest', 'shoulders', 'triceps']},
                {'name': 'Dumbbell Rows', 'muscle_groups': ['back', 'biceps']},
                {'name': 'Dumbbell Squats', 'muscle_groups': ['quadriceps', 'glutes']}
            ]
        }
        
        # Filter based on available equipment
        filtered_library = {}
        for equipment in available_equipment:
            if equipment in base_library:
                filtered_library[equipment] = base_library[equipment]
        
        return filtered_library
    
    def _create_progression_plan(self, fitness_level: str, fitness_goals: List[str]) -> Dict[str, Any]:
        """Create progression plan based on fitness level and goals"""
        progression_plans = {
            'beginner': {
                'week_1_2': 'Focus on form and movement patterns',
                'week_3_4': 'Increase repetitions by 2-3',
                'week_5_6': 'Add additional set to main exercises',
                'week_7_8': 'Increase intensity or add new exercises'
            },
            'intermediate': {
                'week_1_2': 'Establish baseline with current routine',
                'week_3_4': 'Increase weight/resistance by 5-10%',
                'week_5_6': 'Add advanced exercise variations',
                'week_7_8': 'Implement periodization techniques'
            },
            'advanced': {
                'week_1_2': 'Focus on weak points and imbalances',
                'week_3_4': 'Implement advanced training techniques',
                'week_5_6': 'Peak intensity phase',
                'week_7_8': 'Deload and recovery week'
            }
        }
        
        return progression_plans.get(fitness_level, progression_plans['beginner'])
    
    def _generate_safety_guidelines(self, physical_limitations: List[str]) -> List[str]:
        """Generate safety guidelines based on physical limitations"""
        general_guidelines = [
            'Always warm up before exercising',
            'Stop if you feel pain (not to be confused with muscle fatigue)',
            'Stay hydrated throughout your workout',
            'Cool down and stretch after exercising'
        ]
        
        # Add specific guidelines for limitations
        limitation_guidelines = {
            'knee_issues': 'Avoid high-impact exercises; focus on low-impact alternatives',
            'back_problems': 'Maintain neutral spine; avoid heavy lifting without proper form',
            'shoulder_injury': 'Limit overhead movements; focus on pain-free range of motion',
            'heart_condition': 'Monitor heart rate; stay within prescribed zones'
        }
        
        for limitation in physical_limitations:
            if limitation in limitation_guidelines:
                general_guidelines.append(limitation_guidelines[limitation])
        
        return general_guidelines
    
    async def _store_workout_plan(self, user_id: str, workout_plan: Dict[str, Any]) -> str:
        """Store workout plan in Firebase"""
        try:
            db = firebase_config.get_firestore_client()
            
            plan_doc = {
                'user_id': user_id,
                'workout_plan': workout_plan,
                'created_at': datetime.now(),
                'active': True
            }
            
            doc_ref = db.collection('workout_plans').add(plan_doc)
            plan_id = doc_ref[1].id
            
            logging.info(f"Stored workout plan {plan_id} for user {user_id}")
            return plan_id
            
        except Exception as e:
            logging.error(f"Error storing workout plan: {e}")
            return f"error_{datetime.now().timestamp()}"
    
    async def _schedule_workouts(self, user_id: str, workout_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Schedule workouts in Google Calendar"""
        try:
            weekly_schedule = workout_plan.get('weekly_schedule', {})
            calendar_events = []
            
            for day, workout in weekly_schedule.items():
                if workout.get('workout_type') != 'rest':
                    # Calculate next occurrence of this day
                    next_workout_date = self._get_next_day_date(day)
                    
                    workout_data = {
                        'workout_name': f"{workout['workout_type'].replace('_', ' ').title()} Workout",
                        'scheduled_time': next_workout_date.isoformat(),
                        'duration_minutes': workout.get('duration_minutes', 30),
                        'workout_type': workout['workout_type'],
                        'exercises': workout.get('exercises', []),
                        'location': 'Home Workout'
                    }
                    
                    calendar_result = await google_calendar.schedule_workout_session(workout_data)
                    
                    if calendar_result:
                        calendar_events.append(calendar_result)
            
            return calendar_events
            
        except Exception as e:
            logging.error(f"Error scheduling workouts: {e}")
            return []
    
    def _get_next_day_date(self, day_name: str) -> datetime:
        """Get next occurrence of specified day"""
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        target_day = days.index(day_name.lower())
        
        today = datetime.now()
        current_day = today.weekday()
        
        days_ahead = target_day - current_day
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        
        target_date = today + timedelta(days=days_ahead)
        # Set to 9 AM for workout time
        return target_date.replace(hour=9, minute=0, second=0, microsecond=0)
    
    async def _generate_voice_consultation(self, workout_plan: Dict[str, Any]) -> Optional[bytes]:
        """Generate voice consultation using ElevenLabs"""
        try:
            consultation_text = f"""
            Welcome to your personalized fitness consultation!
            
            I've created a workout plan that includes {len([d for d in workout_plan.get('weekly_schedule', {}).values() if d.get('workout_type') != 'rest'])} workout sessions per week.
            
            Your plan focuses on safe, effective exercises that respect your physical limitations and available equipment.
            
            Remember to always warm up before exercising and cool down afterward.
            Listen to your body and modify exercises as needed.
            
            Consistency is more important than intensity, especially when starting out.
            You've got this!
            """
            
            voice_consultation = await elevenlabs_voice.synthesize_fitness_coaching_audio(
                consultation_text, {'workout_type': 'general', 'consultation_type': 'plan_overview'}
            )
            
            return voice_consultation
            
        except Exception as e:
            logging.error(f"Error generating voice consultation: {e}")
            return None
    
    async def _generate_video_consultation(self, workout_plan: Dict[str, Any], 
                                         plan_request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate video consultation using Tavus"""
        try:
            video_data = {
                'user_id': plan_request.get('user_id'),
                'workout_type': 'personalized_plan',
                'fitness_goals': plan_request.get('fitness_goals', []),
                'physical_limitations': plan_request.get('physical_limitations', []),
                'sessions_per_week': len([d for d in workout_plan.get('weekly_schedule', {}).values() if d.get('workout_type') != 'rest'])
            }
            
            video_result = await tavus_video.create_personal_trainer_video(video_data)
            
            return video_result
            
        except Exception as e:
            logging.error(f"Error generating video consultation: {e}")
            return None

# Global fitness agent instance
fitness_agent = FitnessAgent()
