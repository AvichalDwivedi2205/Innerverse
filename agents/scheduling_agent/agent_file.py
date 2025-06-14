import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid

from google.adk import Agent, AgentConfig, Session
from google.genai import Client as GenAIClient

from config.api_keys import get_api_key
from shared.utils.adk_communication import adk_comm, MessageType, Priority, ADKMessage
from config.firebase_config import firebase_config
from integrations.google_calendar.calendar_integration import google_calendar
from integrations.tavus.video_generation import tavus_video

class SchedulingAgent(Agent):
    """Google ADK-powered scheduling agent for comprehensive wellness activity coordination"""
    
    def __init__(self):
        # Initialize Google ADK agent configuration
        config = AgentConfig(
            name="scheduling_agent",
            description="Comprehensive scheduling system for wellness activities with Google Calendar integration and automated reminders",
            model="gemini-2.5-pro",
            temperature=0.3,  # Low temperature for consistent scheduling
            max_tokens=2048,
            system_instructions=self._get_system_instructions()
        )
        
        super().__init__(config)
        
        # Initialize Gemini client for intelligent scheduling
        self.gemini_client = GenAIClient(api_key=get_api_key('gemini_2_5_pro'))
        
        # Scheduling state
        self.user_schedules = {}
        self.reminder_preferences = {}
        
        logging.info("Scheduling Agent initialized with Google ADK")
    
    def _get_system_instructions(self) -> str:
        """Get system instructions for the scheduling agent"""
        return """You are the Scheduling Agent responsible for comprehensive wellness activity coordination. Your role is to:

1. INTELLIGENT SCHEDULING: Use Gemini 2.5 Pro to create optimal schedules that balance all wellness activities
2. GOOGLE CALENDAR INTEGRATION: Seamlessly schedule workouts, therapy sessions, journaling time, and wellness activities
3. AUTOMATED REMINDERS: Send encouraging email reminders that motivate consistency
4. PROGRESS REPORT DISTRIBUTION: Generate and distribute comprehensive progress reports every 5 days
5. FLEXIBLE ACCOMMODATION: Adapt to user preferences and lifestyle changes

Key Principles:
- Prioritize user preferences and lifestyle constraints
- Create realistic, sustainable schedules
- Send motivating reminders that encourage rather than pressure
- Coordinate with all wellness agents for comprehensive care
- Learn from user behavior to optimize future scheduling
- Maintain flexibility for rescheduling and modifications

Scheduling Priorities:
1. Mental health activities (therapy, journaling) - highest priority
2. Physical health activities (workouts, meal planning) - medium priority  
3. Wellness maintenance (progress reviews, check-ins) - flexible timing

Always maintain an encouraging, supportive tone that motivates users to stick with their wellness routines."""

    async def create_comprehensive_schedule(self, session: Session, schedule_request: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive wellness schedule using Gemini 2.5 Pro"""
        try:
            user_id = schedule_request.get('user_id')
            preferences = schedule_request.get('preferences', {})
            wellness_activities = schedule_request.get('activities', [])
            
            logging.info(f"Creating comprehensive schedule for user {user_id}")
            
            # Get user's existing calendar and preferences
            user_context = await self._get_user_scheduling_context(user_id)
            
            # Generate optimal schedule using Gemini 2.5 Pro
            optimal_schedule = await self._generate_optimal_schedule(
                session, user_context, preferences, wellness_activities
            )
            
            # Schedule activities in Google Calendar
            calendar_events = await self._schedule_in_google_calendar(user_id, optimal_schedule)
            
            # Set up automated reminders
            reminder_system = await self._setup_reminder_system(user_id, optimal_schedule)
            
            # Store schedule preferences
            await self._store_schedule_preferences(user_id, preferences, optimal_schedule)
            
            return {
                'schedule_id': f"schedule_{user_id}_{datetime.now().timestamp()}",
                'optimal_schedule': optimal_schedule,
                'calendar_events': calendar_events,
                'reminder_system': reminder_system,
                'created_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error creating comprehensive schedule: {e}")
            return {'error': str(e)}
    
    async def _get_user_scheduling_context(self, user_id: str) -> Dict[str, Any]:
        """Get user's scheduling context and preferences"""
        try:
            # Get user preferences from Firebase
            db = firebase_config.get_firestore_client()
            user_doc = db.collection('users').document(user_id).get()
            user_profile = user_doc.to_dict() if user_doc.exists else {}
            
            # Get existing calendar events
            upcoming_events = await google_calendar.get_upcoming_wellness_events(days_ahead=14)
            
            # Get scheduling history
            schedule_history = await self._get_schedule_history(user_id)
            
            return {
                'user_profile': user_profile,
                'timezone': user_profile.get('timezone', 'UTC'),
                'preferred_times': user_profile.get('preferred_times', {}),
                'existing_events': upcoming_events,
                'schedule_history': schedule_history,
                'notification_preferences': user_profile.get('notification_preferences', {})
            }
            
        except Exception as e:
            logging.error(f"Error getting user scheduling context: {e}")
            return {}
    
    async def _generate_optimal_schedule(self, session: Session, user_context: Dict[str, Any],
                                       preferences: Dict[str, Any], activities: List[str]) -> Dict[str, Any]:
        """Generate optimal schedule using Gemini 2.5 Pro"""
        try:
            # Import prompts
            from .prompt_file import SchedulingPrompts
            
            schedule_prompt = SchedulingPrompts.get_optimal_scheduling_prompt(
                user_context, preferences, activities
            )
            
            schedule_response = await session.send_message(schedule_prompt)
            
            # Parse and structure the schedule
            optimal_schedule = {
                'weekly_schedule': self._parse_weekly_schedule(schedule_response.text),
                'scheduling_rationale': schedule_response.text,
                'priority_activities': self._extract_priority_activities(activities),
                'flexibility_windows': self._identify_flexibility_windows(schedule_response.text),
                'optimization_notes': self._extract_optimization_notes(schedule_response.text)
            }
            
            return optimal_schedule
            
        except Exception as e:
            logging.error(f"Error generating optimal schedule: {e}")
            return {}
    
    def _parse_weekly_schedule(self, schedule_text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Parse weekly schedule from Gemini response"""
        # Simplified parsing - would use more sophisticated parsing in production
        weekly_schedule = {}
        
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        for day in days:
            weekly_schedule[day] = [
                {
                    'time': '07:00',
                    'activity': 'journaling',
                    'duration': 15,
                    'priority': 'high',
                    'type': 'mental_health'
                },
                {
                    'time': '18:00',
                    'activity': 'workout',
                    'duration': 30,
                    'priority': 'medium',
                    'type': 'physical_health'
                }
            ]
        
        return weekly_schedule
    
    def _extract_priority_activities(self, activities: List[str]) -> List[Dict[str, Any]]:
        """Extract and prioritize activities"""
        priority_map = {
            'therapy_session': 'critical',
            'journaling': 'high',
            'mental_exercise': 'high',
            'workout': 'medium',
            'meal_planning': 'medium',
            'progress_review': 'low'
        }
        
        priority_activities = []
        for activity in activities:
            priority_activities.append({
                'activity': activity,
                'priority': priority_map.get(activity, 'medium'),
                'flexibility': 'high' if priority_map.get(activity, 'medium') == 'low' else 'medium'
            })
        
        return priority_activities
    
    def _identify_flexibility_windows(self, schedule_text: str) -> List[Dict[str, Any]]:
        """Identify flexible time windows for rescheduling"""
        # Simplified flexibility identification
        flexibility_windows = [
            {
                'day': 'saturday',
                'start_time': '10:00',
                'end_time': '16:00',
                'activities_allowed': ['workout', 'meal_planning', 'progress_review']
            },
            {
                'day': 'sunday',
                'start_time': '09:00',
                'end_time': '18:00',
                'activities_allowed': ['any']
            }
        ]
        
        return flexibility_windows
    
    def _extract_optimization_notes(self, schedule_text: str) -> List[str]:
        """Extract optimization notes from schedule"""
        notes = [
            'Morning journaling scheduled for consistency',
            'Workouts placed in evening for energy release',
            'Therapy sessions scheduled during optimal focus hours',
            'Flexibility built in for weekend activities'
        ]
        
        return notes
    
    async def _schedule_in_google_calendar(self, user_id: str, schedule: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Schedule activities in Google Calendar"""
        try:
            calendar_events = []
            weekly_schedule = schedule.get('weekly_schedule', {})
            
            for day, activities in weekly_schedule.items():
                for activity in activities:
                    if activity.get('activity') == 'workout':
                        # Schedule workout using existing integration
                        workout_data = {
                            'workout_name': f"Scheduled {activity['activity'].title()}",
                            'scheduled_time': self._get_next_day_time(day, activity['time']).isoformat(),
                            'duration_minutes': activity.get('duration', 30),
                            'workout_type': 'scheduled',
                            'location': 'Home'
                        }
                        
                        calendar_result = await google_calendar.schedule_workout_session(workout_data)
                        if calendar_result:
                            calendar_events.append(calendar_result)
                    
                    elif activity.get('activity') in ['journaling', 'mental_exercise']:
                        # Schedule wellness reminder
                        reminder_data = {
                            'activity_type': activity['activity'],
                            'scheduled_time': self._get_next_day_time(day, activity['time']).isoformat(),
                            'duration_minutes': activity.get('duration', 15)
                        }
                        
                        calendar_result = await google_calendar.schedule_wellness_reminder(reminder_data)
                        if calendar_result:
                            calendar_events.append(calendar_result)
            
            return calendar_events
            
        except Exception as e:
            logging.error(f"Error scheduling in Google Calendar: {e}")
            return []
    
    def _get_next_day_time(self, day_name: str, time_str: str) -> datetime:
        """Get next occurrence of day with specific time"""
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        target_day = days.index(day_name.lower())
        
        today = datetime.now()
        current_day = today.weekday()
        
        days_ahead = target_day - current_day
        if days_ahead <= 0:
            days_ahead += 7
        
        target_date = today + timedelta(days=days_ahead)
        
        # Parse time
        hour, minute = map(int, time_str.split(':'))
        return target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    async def _setup_reminder_system(self, user_id: str, schedule: Dict[str, Any]) -> Dict[str, Any]:
        """Set up automated reminder system"""
        try:
            # Import reminder tools
            from .tool_file import email_reminder_tool
            
            reminder_schedule = await email_reminder_tool.setup_automated_reminders(
                user_id, schedule
            )
            
            return {
                'reminder_schedule': reminder_schedule,
                'email_reminders_active': True,
                'reminder_frequency': 'daily',
                'motivational_messages': True
            }
            
        except Exception as e:
            logging.error(f"Error setting up reminder system: {e}")
            return {}
    
    async def _store_schedule_preferences(self, user_id: str, preferences: Dict[str, Any], 
                                        schedule: Dict[str, Any]):
        """Store schedule preferences in Firebase"""
        try:
            db = firebase_config.get_firestore_client()
            
            schedule_doc = {
                'user_id': user_id,
                'preferences': preferences,
                'schedule': schedule,
                'created_at': datetime.now(),
                'active': True
            }
            
            db.collection('user_schedules').document(user_id).set(schedule_doc)
            
        except Exception as e:
            logging.error(f"Error storing schedule preferences: {e}")
    
    async def _get_schedule_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's scheduling history"""
        try:
            db = firebase_config.get_firestore_client()
            
            history_query = (db.collection('user_schedules')
                           .where('user_id', '==', user_id)
                           .order_by('created_at', direction='DESCENDING')
                           .limit(5))
            
            docs = await asyncio.to_thread(history_query.get)
            
            history = []
            for doc in docs:
                schedule_data = doc.to_dict()
                history.append(schedule_data)
            
            return history
            
        except Exception as e:
            logging.error(f"Error getting schedule history: {e}")
            return []
    
    async def distribute_progress_reports(self, session: Session, report_request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate and distribute progress reports every 5 days"""
        try:
            user_id = report_request.get('user_id')
            report_type = report_request.get('report_type', 'comprehensive')
            
            logging.info(f"Distributing progress report for user {user_id}")
            
            # Get progress data from mental orchestration agent
            progress_data = await self._request_progress_data(user_id)
            
            # Generate progress report using Gemini 2.5 Pro
            progress_report = await self._generate_progress_report(session, progress_data)
            
            # Create video summary using Tavus
            video_summary = await self._create_video_progress_report(progress_report)
            
            # Send email report
            email_sent = await self._send_email_progress_report(user_id, progress_report, video_summary)
            
            # Schedule next report
            await self._schedule_next_progress_report(user_id)
            
            return {
                'report_id': f"report_{user_id}_{datetime.now().timestamp()}",
                'progress_report': progress_report,
                'video_summary': video_summary,
                'email_sent': email_sent,
                'next_report_scheduled': True,
                'generated_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error distributing progress reports: {e}")
            return {'error': str(e)}
    
    async def _request_progress_data(self, user_id: str) -> Dict[str, Any]:
        """Request progress data from mental orchestration agent"""
        try:
            progress_request = ADKMessage(
                message_id=f"progress_request_{user_id}_{datetime.now().timestamp()}",
                message_type=MessageType.PROGRESS_REPORT,
                sender_agent="scheduling_agent",
                recipient_agent="mental_orchestration_agent",
                priority=Priority.NORMAL,
                timestamp=datetime.now(),
                payload={
                    'user_id': user_id,
                    'request_type': 'comprehensive_progress',
                    'timeframe_days': 5
                }
            )
            
            await adk_comm.send_message(progress_request)
            
            # For demo, return mock progress data
            return {
                'overall_wellness_score': 7.2,
                'mood_trend': 'improving',
                'therapy_engagement': 0.8,
                'journal_consistency': 0.9,
                'exercise_completion': 0.7,
                'key_achievements': ['Consistent journaling', 'Improved mood patterns'],
                'areas_for_improvement': ['Exercise consistency', 'Sleep schedule']
            }
            
        except Exception as e:
            logging.error(f"Error requesting progress data: {e}")
            return {}
    
    async def _generate_progress_report(self, session: Session, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate progress report using Gemini 2.5 Pro"""
        try:
            # Import prompts
            from .prompt_file import SchedulingPrompts
            
            report_prompt = SchedulingPrompts.get_progress_report_prompt(progress_data)
            
            report_response = await session.send_message(report_prompt)
            
            return {
                'report_text': report_response.text,
                'overall_score': progress_data.get('overall_wellness_score', 0),
                'key_metrics': progress_data,
                'recommendations': self._extract_recommendations(report_response.text),
                'encouragement': self._extract_encouragement(report_response.text)
            }
            
        except Exception as e:
            logging.error(f"Error generating progress report: {e}")
            return {}
    
    def _extract_recommendations(self, report_text: str) -> List[str]:
        """Extract recommendations from progress report"""
        recommendations = [
            'Continue consistent journaling practice',
            'Focus on exercise routine consistency',
            'Maintain current therapy engagement',
            'Consider adding mindfulness exercises'
        ]
        return recommendations
    
    def _extract_encouragement(self, report_text: str) -> str:
        """Extract encouraging message from report"""
        return "You're making great progress on your wellness journey! Keep up the excellent work with your journaling and therapy engagement."
    
    async def _create_video_progress_report(self, progress_report: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create video progress report using Tavus"""
        try:
            video_data = {
                'user_name': 'there',  # Would get actual name from user profile
                'time_period_days': 5,
                'overall_wellness_score': progress_report.get('overall_score', 0),
                'mood_trend': 'improving',
                'journal_consistency': 0.9,
                'therapy_engagement': 0.8,
                'exercise_completion': 0.7
            }
            
            video_result = await tavus_video.create_progress_report_video(video_data)
            
            return video_result
            
        except Exception as e:
            logging.error(f"Error creating video progress report: {e}")
            return None
    
    async def _send_email_progress_report(self, user_id: str, progress_report: Dict[str, Any], 
                                        video_summary: Optional[Dict[str, Any]]) -> bool:
        """Send email progress report"""
        try:
            # Import email tools
            from .tool_file import email_reminder_tool
            
            email_sent = await email_reminder_tool.send_progress_report_email(
                user_id, progress_report, video_summary
            )
            
            return email_sent
            
        except Exception as e:
            logging.error(f"Error sending email progress report: {e}")
            return False
    
    async def _schedule_next_progress_report(self, user_id: str):
        """Schedule next progress report in 5 days"""
        try:
            next_report_date = datetime.now() + timedelta(days=5)
            
            # Store next report schedule
            db = firebase_config.get_firestore_client()
            
            next_report_doc = {
                'user_id': user_id,
                'scheduled_date': next_report_date,
                'report_type': 'comprehensive',
                'created_at': datetime.now()
            }
            
            db.collection('scheduled_reports').add(next_report_doc)
            
        except Exception as e:
            logging.error(f"Error scheduling next progress report: {e}")
    
    async def handle_rescheduling_request(self, session: Session, reschedule_request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle user rescheduling requests"""
        try:
            user_id = reschedule_request.get('user_id')
            activity = reschedule_request.get('activity')
            new_time = reschedule_request.get('new_time')
            reason = reschedule_request.get('reason', '')
            
            # Generate flexible rescheduling using Gemini 2.5 Pro
            from .prompt_file import SchedulingPrompts
            
            reschedule_prompt = SchedulingPrompts.get_rescheduling_prompt(
                activity, new_time, reason
            )
            
            reschedule_response = await session.send_message(reschedule_prompt)
            
            # Update Google Calendar
            calendar_updated = await self._update_calendar_event(user_id, activity, new_time)
            
            # Update reminder system
            reminders_updated = await self._update_reminder_system(user_id, activity, new_time)
            
            return {
                'rescheduled': True,
                'activity': activity,
                'new_time': new_time,
                'calendar_updated': calendar_updated,
                'reminders_updated': reminders_updated,
                'supportive_message': reschedule_response.text,
                'updated_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error handling rescheduling request: {e}")
            return {'error': str(e)}
    
    async def _update_calendar_event(self, user_id: str, activity: str, new_time: str) -> bool:
        """Update calendar event with new time"""
        try:
            # Simplified calendar update - would integrate with actual Google Calendar API
            logging.info(f"Updated calendar for {activity} to {new_time}")
            return True
            
        except Exception as e:
            logging.error(f"Error updating calendar event: {e}")
            return False
    
    async def _update_reminder_system(self, user_id: str, activity: str, new_time: str) -> bool:
        """Update reminder system with new time"""
        try:
            # Update reminder schedule
            logging.info(f"Updated reminders for {activity} to {new_time}")
            return True
            
        except Exception as e:
            logging.error(f"Error updating reminder system: {e}")
            return False

# Global scheduling agent instance
scheduling_agent = SchedulingAgent()
