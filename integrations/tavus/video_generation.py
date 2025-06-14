import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
import requests
from datetime import datetime

from config.api_keys import get_api_key, get_headers_for_service

class TavusVideoGeneration:
    """Tavus video generation for wellness platform"""
    
    BASE_URL = "https://tavusapi.com/v2"
    
    # Video templates for different wellness contexts
    VIDEO_TEMPLATES = {
        'therapy_session': {
            'background': 'therapy_office',
            'aspect_ratio': '16:9',
            'resolution': '1080p',
            'duration_limit': 600  # 10 minutes max
        },
        'progress_report': {
            'background': 'professional_clean',
            'aspect_ratio': '16:9',
            'resolution': '1080p',
            'duration_limit': 300  # 5 minutes max
        },
        'personal_trainer': {
            'background': 'gym_environment',
            'aspect_ratio': '16:9',
            'resolution': '1080p',
            'duration_limit': 900  # 15 minutes max
        },
        'nutrition_consultation': {
            'background': 'kitchen_clean',
            'aspect_ratio': '16:9',
            'resolution': '1080p',
            'duration_limit': 480  # 8 minutes max
        }
    }
    
    def __init__(self):
        self.api_key = get_api_key('tavus')
        self.headers = get_headers_for_service('tavus')
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        if not self.api_key:
            logging.warning("Tavus API key not found. Video generation will be disabled.")
    
    async def create_therapy_session_video(self, session_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate video for therapy session summary"""
        try:
            script = self._generate_therapy_session_script(session_data)
            
            video_request = {
                'replica_id': await self._get_or_create_therapist_replica(),
                'script': script,
                'background': self.VIDEO_TEMPLATES['therapy_session']['background'],
                'video_name': f"therapy_session_{session_data.get('session_id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'callback_url': None  # For hackathon, we'll poll for completion
            }
            
            return await self._generate_video(video_request, 'therapy_session')
            
        except Exception as e:
            logging.error(f"Error creating therapy session video: {e}")
            return None
    
    def _generate_therapy_session_script(self, session_data: Dict[str, Any]) -> str:
        """Generate script for therapy session video"""
        session_type = session_data.get('session_type', 'individual')
        framework = session_data.get('therapeutic_framework', 'CBT')
        progress_score = session_data.get('progress_score', 0.0)
        insights = session_data.get('therapeutic_insights', [])
        
        script_parts = [
            f"Hello, this is a summary of your {framework} {session_type} therapy session.",
            f"During our session today, we focused on several key areas."
        ]
        
        if insights:
            script_parts.append("Here are the main insights from our discussion:")
            for i, insight in enumerate(insights[:3], 1):  # Limit to top 3 insights
                script_parts.append(f"{i}. {insight}")
        
        if progress_score > 0.7:
            script_parts.append("I'm pleased to see the positive progress you're making. Keep up the excellent work.")
        elif progress_score > 0.4:
            script_parts.append("You're making steady progress. Remember that healing is a journey, and you're moving in the right direction.")
        else:
            script_parts.append("Remember that progress takes time. Be patient with yourself as you work through these challenges.")
        
        homework = session_data.get('homework_assigned', [])
        if homework:
            script_parts.append("For this week, I'd like you to focus on:")
            for task in homework[:2]:  # Limit to 2 homework items
                script_parts.append(f"- {task}")
        
        script_parts.append("I look forward to our next session. Take care of yourself.")
        
        return " ".join(script_parts)
    
    async def create_progress_report_video(self, progress_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate AI-powered video progress report"""
        try:
            script = self._generate_progress_report_script(progress_data)
            
            video_request = {
                'replica_id': await self._get_or_create_wellness_coach_replica(),
                'script': script,
                'background': self.VIDEO_TEMPLATES['progress_report']['background'],
                'video_name': f"progress_report_{progress_data.get('user_id', 'unknown')}_{datetime.now().strftime('%Y%m%d')}",
                'callback_url': None
            }
            
            return await self._generate_video(video_request, 'progress_report')
            
        except Exception as e:
            logging.error(f"Error creating progress report video: {e}")
            return None
    
    def _generate_progress_report_script(self, progress_data: Dict[str, Any]) -> str:
        """Generate script for progress report video"""
        user_name = progress_data.get('user_name', 'there')
        time_period = progress_data.get('time_period_days', 30)
        overall_score = progress_data.get('overall_wellness_score', 0.0)
        mood_trend = progress_data.get('mood_trend', 'stable')
        journal_consistency = progress_data.get('journal_consistency', 0.0)
        therapy_engagement = progress_data.get('therapy_engagement', 0.0)
        exercise_completion = progress_data.get('exercise_completion', 0.0)
        
        script_parts = [
            f"Hello {user_name}, this is your {time_period}-day wellness progress report.",
            f"Your overall wellness score is {overall_score:.1f} out of 10."
        ]
        
        # Mood trend analysis
        if mood_trend == 'improving':
            script_parts.append("I'm happy to report that your mood has been trending upward. This is a great sign of progress.")
        elif mood_trend == 'stable':
            script_parts.append("Your mood has remained stable, which shows consistency in your emotional well-being.")
        else:
            script_parts.append("Your mood has been fluctuating. This is normal, and we'll work together to identify patterns and coping strategies.")
        
        # Journal consistency
        if journal_consistency > 0.8:
            script_parts.append("Your journaling consistency has been excellent. This regular reflection is contributing significantly to your progress.")
        elif journal_consistency > 0.5:
            script_parts.append("You've been fairly consistent with journaling. Try to maintain this habit as it's helping you process your emotions.")
        else:
            script_parts.append("Consider increasing your journaling frequency. Regular reflection can help you better understand your emotional patterns.")
        
        # Therapy engagement
        if therapy_engagement > 0.7:
            script_parts.append("Your engagement with therapy sessions has been outstanding. You're actively participating in your healing journey.")
        elif therapy_engagement > 0.4:
            script_parts.append("Your therapy engagement is good. Continue to be open and honest in your sessions for maximum benefit.")
        
        # Exercise completion
        if exercise_completion > 0.7:
            script_parts.append("You've been consistently completing your mental health exercises. This dedication is paying off.")
        elif exercise_completion > 0.4:
            script_parts.append("You're doing well with your mental health exercises. Try to maintain this routine.")
        else:
            script_parts.append("Consider dedicating more time to your mental health exercises. They're designed to support your overall well-being.")
        
        script_parts.append("Remember, progress isn't always linear. Celebrate your achievements and be kind to yourself during challenging times.")
        script_parts.append("Keep up the great work, and I'll see you in your next progress report.")
        
        return " ".join(script_parts)
    
    async def create_personal_trainer_video(self, workout_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate personal trainer consultation video"""
        try:
            script = self._generate_trainer_script(workout_data)
            
            video_request = {
                'replica_id': await self._get_or_create_trainer_replica(),
                'script': script,
                'background': self.VIDEO_TEMPLATES['personal_trainer']['background'],
                'video_name': f"trainer_session_{workout_data.get('user_id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'callback_url': None
            }
            
            return await self._generate_video(video_request, 'personal_trainer')
            
        except Exception as e:
            logging.error(f"Error creating personal trainer video: {e}")
            return None
    
    def _generate_trainer_script(self, workout_data: Dict[str, Any]) -> str:
        """Generate script for personal trainer video"""
        workout_type = workout_data.get('workout_type', 'general')
        fitness_goals = workout_data.get('fitness_goals', [])
        physical_limitations = workout_data.get('physical_limitations', [])
        
        script_parts = [
            "Hey there! Ready for an awesome workout session?",
            f"Today we're focusing on {workout_type} training."
        ]
        
        if fitness_goals:
            script_parts.append(f"Remember, we're working towards your goals of {', '.join(fitness_goals[:2])}.")
        
        if physical_limitations:
            script_parts.append(f"I've modified today's exercises to accommodate your {', '.join(physical_limitations[:2])}.")
        
        script_parts.extend([
            "Let's start with a proper warm-up to prepare your body.",
            "Remember to listen to your body and modify any exercise if needed.",
            "You've got this! Let's make today count!"
        ])
        
        return " ".join(script_parts)
    
    async def _generate_video(self, video_request: Dict[str, Any], video_type: str) -> Optional[Dict[str, Any]]:
        """Internal method to generate video using Tavus API"""
        if not self.api_key:
            logging.warning("Tavus API key not available")
            return None
        
        url = f"{self.BASE_URL}/videos"
        
        try:
            response = await asyncio.to_thread(
                self.session.post,
                url,
                json=video_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                logging.info(f"Successfully initiated {video_type} video generation")
                return {
                    'video_id': result.get('video_id'),
                    'status': 'processing',
                    'video_type': video_type,
                    'created_at': datetime.now().isoformat(),
                    'estimated_completion': 'Processing time: 6-9 hours'
                }
            else:
                logging.error(f"Tavus API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Error calling Tavus API: {e}")
            return None
    
    async def _get_or_create_therapist_replica(self) -> str:
        """Get or create therapist replica ID"""
        # For hackathon demo, return a mock replica ID
        # In production, this would create/retrieve actual replicas
        return "therapist_replica_demo_id"
    
    async def _get_or_create_wellness_coach_replica(self) -> str:
        """Get or create wellness coach replica ID"""
        return "wellness_coach_replica_demo_id"
    
    async def _get_or_create_trainer_replica(self) -> str:
        """Get or create personal trainer replica ID"""
        return "trainer_replica_demo_id"
    
    async def get_video_status(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Check video generation status"""
        if not self.api_key:
            return None
        
        url = f"{self.BASE_URL}/videos/{video_id}"
        
        try:
            response = await asyncio.to_thread(self.session.get, url)
            
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"Error checking video status: {response.status_code}")
                return None
                
        except Exception as e:
            logging.error(f"Error checking video status: {e}")
            return None

# Global Tavus instance
tavus_video = TavusVideoGeneration()
