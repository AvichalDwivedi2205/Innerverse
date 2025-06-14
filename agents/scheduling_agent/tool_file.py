import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config.api_keys import get_api_key
from config.firebase_config import firebase_config
from integrations.tavus.video_generation import tavus_video

class EmailReminderTool:
    """Gmail API integration for email reminders and progress reports"""
    
    def __init__(self):
        self.gmail_api_key = get_api_key('gmail_api')
        self.smtp_configured = False
        
        # For demo purposes, we'll use mock email sending
        if not self.gmail_api_key:
            logging.warning("Gmail API key not found. Using mock email system.")
    
    async def setup_automated_reminders(self, user_id: str, schedule: Dict[str, Any]) -> Dict[str, Any]:
        """Set up automated reminder system for user"""
        try:
            weekly_schedule = schedule.get('weekly_schedule', {})
            reminder_schedule = {}
            
            for day, activities in weekly_schedule.items():
                day_reminders = []
                
                for activity in activities:
                    if activity.get('activity') != 'rest':
                        reminder_time = self._calculate_reminder_time(activity)
                        
                        reminder = {
                            'activity': activity['activity'],
                            'reminder_time': reminder_time,
                            'activity_time': activity['time'],
                            'message_type': 'motivational',
                            'enabled': True
                        }
                        
                        day_reminders.append(reminder)
                
                reminder_schedule[day] = day_reminders
            
            # Store reminder schedule
            await self._store_reminder_schedule(user_id, reminder_schedule)
            
            return {
                'reminder_schedule': reminder_schedule,
                'total_reminders': sum(len(reminders) for reminders in reminder_schedule.values()),
                'setup_successful': True
            }
            
        except Exception as e:
            logging.error(f"Error setting up automated reminders: {e}")
            return {'error': str(e)}
    
    def _calculate_reminder_time(self, activity: Dict[str, Any]) -> str:
        """Calculate optimal reminder time for activity"""
        activity_time = activity.get('time', '09:00')
        hour, minute = map(int, activity_time.split(':'))
        
        # Send reminder 30 minutes before activity
        reminder_hour = hour
        reminder_minute = minute - 30
        
        if reminder_minute < 0:
            reminder_minute += 60
            reminder_hour -= 1
        
        if reminder_hour < 0:
            reminder_hour += 24
        
        return f"{reminder_hour:02d}:{reminder_minute:02d}"
    
    async def _store_reminder_schedule(self, user_id: str, reminder_schedule: Dict[str, Any]):
        """Store reminder schedule in Firebase"""
        try:
            db = firebase_config.get_firestore_client()
            
            reminder_doc = {
                'user_id': user_id,
                'reminder_schedule': reminder_schedule,
                'created_at': datetime.now(),
                'active': True
            }
            
            db.collection('reminder_schedules').document(user_id).set(reminder_doc)
            
        except Exception as e:
            logging.error(f"Error storing reminder schedule: {e}")
    
    async def send_activity_reminder(self, user_id: str, activity: str, 
                                   reminder_context: Dict[str, Any]) -> bool:
        """Send activity reminder email"""
        try:
            # Get user email
            user_email = await self._get_user_email(user_id)
            if not user_email:
                return False
            
            # Generate personalized reminder message
            reminder_message = await self._generate_reminder_message(activity, reminder_context)
            
            # Send email (mock implementation)
            email_sent = await self._send_email(
                user_email,
                f"Gentle Reminder: Your {activity.replace('_', ' ').title()} Time",
                reminder_message
            )
            
            # Log reminder sent
            await self._log_reminder_sent(user_id, activity, email_sent)
            
            return email_sent
            
        except Exception as e:
            logging.error(f"Error sending activity reminder: {e}")
            return False
    
    async def _get_user_email(self, user_id: str) -> Optional[str]:
        """Get user email from Firebase"""
        try:
            db = firebase_config.get_firestore_client()
            user_doc = db.collection('users').document(user_id).get()
            
            if user_doc.exists:
                return user_doc.to_dict().get('email')
            
            return None
            
        except Exception as e:
            logging.error(f"Error getting user email: {e}")
            return None
    
    async def _generate_reminder_message(self, activity: str, context: Dict[str, Any]) -> str:
        """Generate personalized reminder message"""
        activity_messages = {
            'journaling': """
                Hi there! 📝
                
                It's time for your daily journaling session. Taking a few minutes to reflect on your thoughts and feelings is a wonderful way to check in with yourself.
                
                Remember, there's no right or wrong way to journal. Just let your thoughts flow and be kind to yourself.
                
                You've got this! 💙
                
                Your Wellness Team
            """,
            'workout': """
                Hey! 💪
                
                Your workout is coming up! Whether it's a full session or just a few minutes of movement, your body will thank you.
                
                Remember to listen to your body and modify as needed. Every bit of movement counts toward your wellness goals.
                
                Let's do this! 🌟
                
                Your Wellness Team
            """,
            'mental_exercise': """
                Hello! 🧠
                
                Time for your mental health exercise. These practices are building your emotional resilience and coping skills.
                
                Take your time, be patient with yourself, and remember that every practice session is valuable.
                
                You're investing in your mental wellness! ✨
                
                Your Wellness Team
            """,
            'therapy_session': """
                Hi! 🌱
                
                Your therapy session is coming up. This is your dedicated time for growth, healing, and self-discovery.
                
                Remember to be open, honest, and gentle with yourself during this important time.
                
                We're proud of your commitment to your mental health! 💚
                
                Your Wellness Team
            """
        }
        
        return activity_messages.get(activity, f"""
            Hi! 
            
            This is a gentle reminder about your upcoming {activity.replace('_', ' ')} activity.
            
            Taking time for your wellness is an act of self-care and self-respect. You're worth this investment!
            
            Your Wellness Team
        """)
    
    async def _send_email(self, to_email: str, subject: str, message: str) -> bool:
        """Send email (mock implementation for demo)"""
        try:
            # Mock email sending for demo
            logging.info(f"Mock email sent to {to_email}: {subject}")
            
            # In production, this would use Gmail API
            # gmail_service = build('gmail', 'v1', credentials=creds)
            # message = create_message(to_email, subject, message)
            # send_message(gmail_service, 'me', message)
            
            return True
            
        except Exception as e:
            logging.error(f"Error sending email: {e}")
            return False
    
    async def _log_reminder_sent(self, user_id: str, activity: str, success: bool):
        """Log reminder sent to Firebase"""
        try:
            db = firebase_config.get_firestore_client()
            
            log_doc = {
                'user_id': user_id,
                'activity': activity,
                'sent_at': datetime.now(),
                'success': success,
                'reminder_type': 'activity_reminder'
            }
            
            db.collection('reminder_logs').add(log_doc)
            
        except Exception as e:
            logging.error(f"Error logging reminder: {e}")
    
    async def send_progress_report_email(self, user_id: str, progress_report: Dict[str, Any],
                                       video_summary: Optional[Dict[str, Any]]) -> bool:
        """Send progress report email with optional video"""
        try:
            user_email = await self._get_user_email(user_id)
            if not user_email:
                return False
            
            # Generate progress report email
            email_content = self._generate_progress_report_email(progress_report, video_summary)
            
            # Send email
            email_sent = await self._send_email(
                user_email,
                "Your 5-Day Wellness Progress Report 📊",
                email_content
            )
            
            # Log progress report sent
            await self._log_progress_report_sent(user_id, email_sent)
            
            return email_sent
            
        except Exception as e:
            logging.error(f"Error sending progress report email: {e}")
            return False
    
    def _generate_progress_report_email(self, progress_report: Dict[str, Any],
                                      video_summary: Optional[Dict[str, Any]]) -> str:
        """Generate progress report email content"""
        overall_score = progress_report.get('overall_score', 0)
        recommendations = progress_report.get('recommendations', [])
        encouragement = progress_report.get('encouragement', '')
        
        email_content = f"""
        Hi there! 🌟
        
        Your 5-day wellness progress report is ready! Here's how you're doing:
        
        📊 Overall Wellness Score: {overall_score}/10
        
        {encouragement}
        
        🎯 Recommendations for the next 5 days:
        {chr(10).join(f"• {rec}" for rec in recommendations[:3])}
        
        """
        
        if video_summary:
            email_content += f"""
        🎥 We've also created a personalized video summary for you! 
        Watch it here: [Video will be available once processing completes]
        
        """
        
        email_content += """
        Remember, progress isn't always linear, and every step forward matters. You're doing great!
        
        Keep up the amazing work! 💙
        
        Your Wellness Team
        """
        
        return email_content
    
    async def _log_progress_report_sent(self, user_id: str, success: bool):
        """Log progress report sent to Firebase"""
        try:
            db = firebase_config.get_firestore_client()
            
            log_doc = {
                'user_id': user_id,
                'sent_at': datetime.now(),
                'success': success,
                'report_type': 'progress_report'
            }
            
            db.collection('progress_report_logs').add(log_doc)
            
        except Exception as e:
            logging.error(f"Error logging progress report: {e}")

class FirebaseCloudFunctionsTool:
    """Firebase Cloud Functions for automated wellness activity coordination"""
    
    def __init__(self):
        self.firebase_db = firebase_config.get_firestore_client()
    
    async def setup_automated_coordination(self, user_id: str, coordination_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Set up automated coordination rules"""
        try:
            coordination_config = {
                'user_id': user_id,
                'rules': coordination_rules,
                'created_at': datetime.now(),
                'active': True
            }
            
            # Store coordination rules
            doc_ref = self.firebase_db.collection('coordination_rules').add(coordination_config)
            
            return {
                'coordination_id': doc_ref[1].id,
                'rules_active': True,
                'setup_successful': True
            }
            
        except Exception as e:
            logging.error(f"Error setting up automated coordination: {e}")
            return {'error': str(e)}
    
    async def trigger_agent_coordination(self, coordination_event: Dict[str, Any]) -> bool:
        """Trigger coordination between agents"""
        try:
            # Log coordination event
            event_doc = {
                'event_type': coordination_event.get('event_type'),
                'user_id': coordination_event.get('user_id'),
                'trigger_data': coordination_event.get('trigger_data', {}),
                'triggered_at': datetime.now(),
                'processed': False
            }
            
            self.firebase_db.collection('coordination_events').add(event_doc)
            
            # In production, this would trigger actual Cloud Functions
            logging.info(f"Coordination event triggered: {coordination_event.get('event_type')}")
            
            return True
            
        except Exception as e:
            logging.error(f"Error triggering agent coordination: {e}")
            return False
    
    async def process_wellness_activity_completion(self, completion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process wellness activity completion and trigger follow-up actions"""
        try:
            user_id = completion_data.get('user_id')
            activity = completion_data.get('activity')
            completion_status = completion_data.get('completed', False)
            
            # Store completion data
            completion_doc = {
                'user_id': user_id,
                'activity': activity,
                'completed': completion_status,
                'completion_time': datetime.now(),
                'metadata': completion_data.get('metadata', {})
            }
            
            self.firebase_db.collection('activity_completions').add(completion_doc)
            
            # Trigger follow-up actions based on completion
            follow_up_actions = []
            
            if completion_status:
                # Successful completion - send encouragement
                follow_up_actions.append('send_encouragement')
                
                # Check for streaks or milestones
                if await self._check_completion_streak(user_id, activity):
                    follow_up_actions.append('celebrate_streak')
            else:
                # Missed activity - send supportive reminder
                follow_up_actions.append('send_supportive_followup')
            
            return {
                'completion_processed': True,
                'follow_up_actions': follow_up_actions,
                'processing_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error processing wellness activity completion: {e}")
            return {'error': str(e)}
    
    async def _check_completion_streak(self, user_id: str, activity: str) -> bool:
        """Check if user has a completion streak for activity"""
        try:
            # Query recent completions for this activity
            recent_completions = (self.firebase_db.collection('activity_completions')
                                .where('user_id', '==', user_id)
                                .where('activity', '==', activity)
                                .where('completed', '==', True)
                                .order_by('completion_time', direction='DESCENDING')
                                .limit(7))
            
            docs = await asyncio.to_thread(recent_completions.get)
            
            # Check for 7-day streak
            if len(docs) >= 7:
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"Error checking completion streak: {e}")
            return False

# Initialize tool instances
email_reminder_tool = EmailReminderTool()
firebase_coordination_tool = FirebaseCloudFunctionsTool()
