import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from config.firebase_config import firebase_config

class ExerciseDatabaseTool:
    """Comprehensive exercise database with modifications for physical limitations"""
    
    def __init__(self):
        # Comprehensive exercise database
        self.exercise_database = {
            'push_ups': {
                'name': 'Push-ups',
                'category': 'Upper Body Strength',
                'primary_muscles': ['Chest', 'Shoulders', 'Triceps'],
                'secondary_muscles': ['Core'],
                'equipment': ['Bodyweight'],
                'difficulty': 'Beginner to Advanced',
                'modifications': {
                    'knee_push_ups': 'Perform on knees instead of toes',
                    'wall_push_ups': 'Stand arm\'s length from wall, push against wall',
                    'incline_push_ups': 'Hands elevated on bench or step'
                },
                'contraindications': ['Wrist injury', 'Shoulder impingement']
            },
            'squats': {
                'name': 'Squats',
                'category': 'Lower Body Strength',
                'primary_muscles': ['Quadriceps', 'Glutes'],
                'secondary_muscles': ['Hamstrings', 'Calves', 'Core'],
                'equipment': ['Bodyweight', 'Dumbbells', 'Barbell'],
                'difficulty': 'Beginner to Advanced',
                'modifications': {
                    'chair_squats': 'Sit down and stand up from chair',
                    'wall_squats': 'Back against wall for support',
                    'partial_squats': 'Reduce range of motion'
                },
                'contraindications': ['Knee injury', 'Hip injury', 'Lower back injury']
            },
            'planks': {
                'name': 'Planks',
                'category': 'Core Stability',
                'primary_muscles': ['Core', 'Abdominals'],
                'secondary_muscles': ['Shoulders', 'Glutes'],
                'equipment': ['Bodyweight'],
                'difficulty': 'Beginner to Advanced',
                'modifications': {
                    'knee_planks': 'Drop knees to ground',
                    'wall_planks': 'Standing plank against wall',
                    'incline_planks': 'Hands elevated on bench'
                },
                'contraindications': ['Wrist injury', 'Lower back injury']
            }
        }
    
    async def search_exercises(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search exercises based on criteria"""
        try:
            muscle_groups = criteria.get('muscle_groups', [])
            equipment = criteria.get('equipment', [])
            physical_limitations = criteria.get('physical_limitations', [])
            
            matching_exercises = []
            
            for exercise_id, exercise_data in self.exercise_database.items():
                matches = True
                
                # Filter by muscle groups
                if muscle_groups:
                    exercise_muscles = exercise_data['primary_muscles'] + exercise_data['secondary_muscles']
                    if not any(muscle in exercise_muscles for muscle in muscle_groups):
                        matches = False
                
                # Filter by equipment
                if equipment:
                    if not any(equip in exercise_data['equipment'] for equip in equipment):
                        matches = False
                
                # Check contraindications
                if physical_limitations:
                    contraindications = exercise_data.get('contraindications', [])
                    if any(limitation.lower() in [c.lower() for c in contraindications] for limitation in physical_limitations):
                        matches = False
                
                if matches:
                    exercise_result = {
                        'exercise_id': exercise_id,
                        **exercise_data
                    }
                    matching_exercises.append(exercise_result)
            
            return matching_exercises
            
        except Exception as e:
            logging.error(f"Error searching exercises: {e}")
            return []
    
    async def get_exercise_modifications(self, exercise_id: str, physical_limitations: List[str]) -> Dict[str, Any]:
        """Get exercise modifications for specific limitations"""
        try:
            if exercise_id not in self.exercise_database:
                return {'error': 'Exercise not found'}
            
            exercise = self.exercise_database[exercise_id]
            modifications = exercise.get('modifications', {})
            contraindications = exercise.get('contraindications', [])
            
            return {
                'exercise': exercise['name'],
                'contraindications': contraindications,
                'safe_modifications': modifications,
                'recommendations': self._generate_modification_recommendations(physical_limitations, exercise)
            }
            
        except Exception as e:
            logging.error(f"Error getting exercise modifications: {e}")
            return {'error': str(e)}
    
    def _generate_modification_recommendations(self, limitations: List[str], exercise: Dict[str, Any]) -> List[str]:
        """Generate specific modification recommendations"""
        recommendations = []
        
        for limitation in limitations:
            limitation_lower = limitation.lower()
            
            if 'knee' in limitation_lower and 'squats' in exercise['name'].lower():
                recommendations.append("Consider chair squats or wall squats to reduce knee stress")
            elif 'back' in limitation_lower and 'deadlift' in exercise['name'].lower():
                recommendations.append("Try glute bridges or Romanian deadlifts with lighter weight")
            elif 'wrist' in limitation_lower and 'push' in exercise['name'].lower():
                recommendations.append("Perform on fists or use push-up handles to reduce wrist stress")
        
        if not recommendations:
            recommendations.append("Consult with a healthcare provider for exercise modifications")
        
        return recommendations

class WorkoutTrackingTool:
    """Tool for tracking workout sessions and progress"""
    
    def __init__(self):
        self.firebase_db = firebase_config.get_firestore_client()
    
    async def log_workout_session(self, user_id: str, workout_data: Dict[str, Any]) -> str:
        """Log a completed workout session"""
        try:
            session_data = {
                'user_id': user_id,
                'workout_date': workout_data.get('date', datetime.now()),
                'workout_type': workout_data.get('workout_type', 'General'),
                'duration_minutes': workout_data.get('duration_minutes', 0),
                'exercises': workout_data.get('exercises', []),
                'perceived_exertion': workout_data.get('perceived_exertion', 5),
                'notes': workout_data.get('notes', ''),
                'completed': workout_data.get('completed', True),
                'created_at': datetime.now()
            }
            
            doc_ref = self.firebase_db.collection('workout_sessions').document()
            doc_ref.set(session_data)
            
            return doc_ref.id
            
        except Exception as e:
            logging.error(f"Error logging workout session: {e}")
            return None
    
    async def get_workout_history(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get user's workout history"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            query = (self.firebase_db.collection('workout_sessions')
                    .where('user_id', '==', user_id)
                    .where('workout_date', '>=', start_date)
                    .where('workout_date', '<=', end_date)
                    .order_by('workout_date', direction='DESCENDING'))
            
            docs = query.stream()
            
            workout_history = []
            for doc in docs:
                workout_data = doc.to_dict()
                workout_data['session_id'] = doc.id
                workout_history.append(workout_data)
            
            return workout_history
            
        except Exception as e:
            logging.error(f"Error getting workout history: {e}")
            return []
    
    async def get_progress_metrics(self, user_id: str) -> Dict[str, Any]:
        """Calculate user's fitness progress metrics"""
        try:
            recent_workouts = await self.get_workout_history(user_id, days=90)
            
            if not recent_workouts:
                return {'error': 'No workout data available'}
            
            total_workouts = len(recent_workouts)
            total_minutes = sum(workout.get('duration_minutes', 0) for workout in recent_workouts)
            avg_duration = total_minutes / total_workouts if total_workouts > 0 else 0
            
            weeks = 90 / 7
            workouts_per_week = total_workouts / weeks
            
            workout_types = [workout.get('workout_type', 'General') for workout in recent_workouts]
            most_common_type = max(set(workout_types), key=workout_types.count) if workout_types else 'N/A'
            
            return {
                'total_workouts_90_days': total_workouts,
                'total_minutes_90_days': total_minutes,
                'average_workout_duration': round(avg_duration, 1),
                'workouts_per_week': round(workouts_per_week, 1),
                'most_common_workout_type': most_common_type,
                'last_workout_date': recent_workouts[0].get('workout_date') if recent_workouts else None
            }
            
        except Exception as e:
            logging.error(f"Error calculating progress metrics: {e}")
            return {'error': str(e)}

class WorkoutPlanStorageTool:
    """Tool for storing and managing workout plans"""
    
    def __init__(self):
        self.firebase_db = firebase_config.get_firestore_client()
    
    async def store_workout_plan(self, user_id: str, plan_data: Dict[str, Any]) -> str:
        """Store a workout plan in Firebase"""
        try:
            plan = {
                'user_id': user_id,
                'plan_name': plan_data.get('plan_name', 'Custom Workout Plan'),
                'weekly_schedule': plan_data.get('weekly_schedule', {}),
                'exercise_library': plan_data.get('exercise_library', {}),
                'progression_plan': plan_data.get('progression_plan', {}),
                'safety_guidelines': plan_data.get('safety_guidelines', []),
                'equipment_needed': plan_data.get('equipment_needed', []),
                'fitness_goals': plan_data.get('fitness_goals', []),
                'physical_limitations': plan_data.get('physical_limitations', []),
                'created_at': datetime.now(),
                'active': True
            }
            
            doc_ref = self.firebase_db.collection('workout_plans').document()
            doc_ref.set(plan)
            
            return doc_ref.id
            
        except Exception as e:
            logging.error(f"Error storing workout plan: {e}")
            return None
    
    async def get_user_workout_plans(self, user_id: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """Retrieve user's workout plans"""
        try:
            query = self.firebase_db.collection('workout_plans').where('user_id', '==', user_id)
            
            if active_only:
                query = query.where('active', '==', True)
            
            docs = query.order_by('created_at', direction='DESCENDING').stream()
            
            plans = []
            for doc in docs:
                plan_data = doc.to_dict()
                plan_data['plan_id'] = doc.id
                plans.append(plan_data)
            
            return plans
            
        except Exception as e:
            logging.error(f"Error retrieving workout plans: {e}")
            return []
    
    async def update_workout_plan(self, plan_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing workout plan"""
        try:
            plan_ref = self.firebase_db.collection('workout_plans').document(plan_id)
            updates['updated_at'] = datetime.now()
            plan_ref.update(updates)
            return True
            
        except Exception as e:
            logging.error(f"Error updating workout plan: {e}")
            return False 