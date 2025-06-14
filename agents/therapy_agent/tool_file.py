import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json

from google.genai import Client as GenAIClient
from config.api_keys import get_api_key
from config.firebase_config import firebase_config
from vector_db.utils.vector_operations import vector_ops
from vector_db.schemas.mental_health_schemas import VectorType
from integrations.elevenlabs.voice_synthesis import elevenlabs_voice
from integrations.tavus.video_generation import tavus_video
from shared.models.therapy_models import TherapySession, TherapeuticFramework

class GeminiTherapeuticReasoningTool:
    """Gemini 2.5 Pro integration for complex therapeutic reasoning"""
    
    def __init__(self):
        self.client = GenAIClient(api_key=get_api_key('gemini_2_5_pro'))
        self.context_window = 1000000  # 1M token context window
    
    async def analyze_therapeutic_progress(self, user_id: str, timeframe_days: int = 30) -> Dict[str, Any]:
        """Analyze therapeutic progress using Gemini 2.5 Pro's advanced reasoning"""
        try:
            # Get comprehensive user timeline
            timeline = await vector_ops.get_user_mental_health_timeline(user_id, timeframe_days)
            
            # Get therapy session history
            therapy_sessions = await self._get_therapy_session_history(user_id, timeframe_days)
            
            # Prepare comprehensive analysis prompt
            analysis_prompt = f"""
            COMPREHENSIVE THERAPEUTIC PROGRESS ANALYSIS
            
            Analyze the following therapeutic data for evidence-based progress assessment:
            
            USER TIMELINE DATA:
            {json.dumps(timeline, indent=2)}
            
            THERAPY SESSION HISTORY:
            {json.dumps(therapy_sessions, indent=2)}
            
            ANALYSIS REQUIREMENTS:
            
            1. PROGRESS INDICATORS:
               - Quantitative improvements in mood, anxiety, depression scores
               - Qualitative changes in coping strategies and resilience
               - Behavioral activation and engagement patterns
               - Cognitive restructuring effectiveness
               - Emotional regulation improvements
            
            2. THERAPEUTIC EFFECTIVENESS:
               - Which interventions showed most benefit
               - Framework effectiveness (CBT, DBT, ACT)
               - Session frequency and duration optimization
               - Homework compliance and effectiveness
            
            3. PATTERN IDENTIFICATION:
               - Recurring themes and triggers
               - Seasonal or cyclical patterns
               - Stress response patterns
               - Recovery and resilience patterns
            
            4. RISK ASSESSMENT:
               - Current risk level and trajectory
               - Protective factor development
               - Crisis prevention effectiveness
               - Safety plan utilization
            
            5. TREATMENT RECOMMENDATIONS:
               - Continued intervention priorities
               - Framework adjustments needed
               - Session frequency modifications
               - New therapeutic targets
               - Referral considerations
            
            6. PROGNOSIS AND GOALS:
               - Short-term progress expectations
               - Long-term therapeutic goals
               - Maintenance planning needs
               - Relapse prevention strategies
            
            Provide a comprehensive, evidence-based analysis suitable for clinical treatment planning.
            """
            
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model='gemini-2.5-pro',
                contents=analysis_prompt
            )
            
            return {
                'analysis': response.text,
                'progress_score': self._extract_progress_score(response.text),
                'risk_level': self._extract_risk_level(response.text),
                'recommendations': self._extract_recommendations(response.text),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error in therapeutic progress analysis: {e}")
            return {'error': str(e)}
    
    async def _get_therapy_session_history(self, user_id: str, days: int) -> List[Dict[str, Any]]:
        """Get therapy session history from Firebase"""
        try:
            db = firebase_config.get_firestore_client()
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            sessions_query = (db.collection('therapy_sessions')
                            .where('user_id', '==', user_id)
                            .where('created_at', '>=', start_date)
                            .where('created_at', '<=', end_date)
                            .order_by('created_at', direction='DESCENDING'))
            
            sessions = []
            docs = await asyncio.to_thread(sessions_query.get)
            
            for doc in docs:
                session_data = doc.to_dict()
                sessions.append(session_data)
            
            return sessions
            
        except Exception as e:
            logging.error(f"Error retrieving therapy session history: {e}")
            return []
    
    def _extract_progress_score(self, analysis_text: str) -> float:
        """Extract progress score from analysis"""
        # Simplified extraction - would use more sophisticated parsing in production
        if 'excellent progress' in analysis_text.lower():
            return 0.9
        elif 'good progress' in analysis_text.lower():
            return 0.7
        elif 'moderate progress' in analysis_text.lower():
            return 0.5
        elif 'minimal progress' in analysis_text.lower():
            return 0.3
        else:
            return 0.5  # Default moderate
    
    def _extract_risk_level(self, analysis_text: str) -> str:
        """Extract risk level from analysis"""
        text_lower = analysis_text.lower()
        if 'high risk' in text_lower or 'critical' in text_lower:
            return 'high'
        elif 'moderate risk' in text_lower:
            return 'moderate'
        else:
            return 'low'
    
    def _extract_recommendations(self, analysis_text: str) -> List[str]:
        """Extract recommendations from analysis"""
        # Simplified extraction
        recommendations = []
        
        if 'continue cbt' in analysis_text.lower():
            recommendations.append('Continue CBT interventions')
        if 'increase session frequency' in analysis_text.lower():
            recommendations.append('Increase session frequency')
        if 'medication evaluation' in analysis_text.lower():
            recommendations.append('Consider medication evaluation')
        if 'group therapy' in analysis_text.lower():
            recommendations.append('Consider group therapy')
        
        return recommendations if recommendations else ['Continue current treatment plan']
    
    async def generate_treatment_plan(self, user_context: Dict[str, Any], 
                                    assessment_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive treatment plan using Gemini 2.5 Pro"""
        try:
            treatment_prompt = f"""
            COMPREHENSIVE TREATMENT PLAN DEVELOPMENT
            
            Based on the following assessment data, develop a detailed, evidence-based treatment plan:
            
            USER CONTEXT:
            {json.dumps(user_context, indent=2)}
            
            ASSESSMENT RESULTS:
            {json.dumps(assessment_results, indent=2)}
            
            TREATMENT PLAN COMPONENTS:
            
            1. PRIMARY DIAGNOSIS AND FORMULATION:
               - Clinical presentation summary
               - Diagnostic considerations
               - Case formulation using biopsychosocial model
               - Precipitating and maintaining factors
            
            2. TREATMENT GOALS:
               - Short-term goals (1-3 months)
               - Medium-term goals (3-6 months)
               - Long-term goals (6-12 months)
               - Specific, measurable, achievable objectives
            
            3. THERAPEUTIC FRAMEWORK SELECTION:
               - Primary therapeutic approach (CBT, DBT, ACT)
               - Rationale for framework selection
               - Integration of multiple approaches if needed
               - Adaptation for individual needs
            
            4. INTERVENTION STRATEGIES:
               - Specific techniques and interventions
               - Session structure and frequency
               - Homework and between-session activities
               - Skills training components
            
            5. RISK MANAGEMENT:
               - Safety planning protocols
               - Crisis intervention procedures
               - Risk monitoring strategies
               - Emergency contact procedures
            
            6. PROGRESS MONITORING:
               - Outcome measures and assessments
               - Progress review schedule
               - Treatment adjustment criteria
               - Success indicators
            
            7. RELAPSE PREVENTION:
               - Maintenance strategies
               - Early warning sign identification
               - Coping strategy reinforcement
               - Long-term support planning
            
            Provide a comprehensive, individualized treatment plan following evidence-based practice guidelines.
            """
            
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model='gemini-2.5-pro',
                contents=treatment_prompt
            )
            
            return {
                'treatment_plan': response.text,
                'primary_framework': self._extract_primary_framework(response.text),
                'session_frequency': self._extract_session_frequency(response.text),
                'treatment_duration': self._extract_treatment_duration(response.text),
                'generated_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error generating treatment plan: {e}")
            return {'error': str(e)}
    
    def _extract_primary_framework(self, plan_text: str) -> str:
        """Extract primary therapeutic framework from treatment plan"""
        text_lower = plan_text.lower()
        if 'cbt' in text_lower or 'cognitive behavioral' in text_lower:
            return 'CBT'
        elif 'dbt' in text_lower or 'dialectical' in text_lower:
            return 'DBT'
        elif 'act' in text_lower or 'acceptance commitment' in text_lower:
            return 'ACT'
        else:
            return 'Integrative'
    
    def _extract_session_frequency(self, plan_text: str) -> str:
        """Extract recommended session frequency"""
        text_lower = plan_text.lower()
        if 'twice weekly' in text_lower or '2 times per week' in text_lower:
            return 'twice_weekly'
        elif 'weekly' in text_lower:
            return 'weekly'
        elif 'biweekly' in text_lower or 'every two weeks' in text_lower:
            return 'biweekly'
        else:
            return 'weekly'  # Default
    
    def _extract_treatment_duration(self, plan_text: str) -> str:
        """Extract estimated treatment duration"""
        text_lower = plan_text.lower()
        if '12 months' in text_lower or 'one year' in text_lower:
            return '12_months'
        elif '6 months' in text_lower:
            return '6_months'
        elif '3 months' in text_lower:
            return '3_months'
        else:
            return '6_months'  # Default

class SessionSummaryTool:
    """Tool for generating comprehensive therapy session summaries"""
    
    def __init__(self):
        self.gemini_client = GenAIClient(api_key=get_api_key('gemini_2_5_pro'))
    
    async def generate_session_summary(self, therapy_session: TherapySession, 
                                     session_content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed session summary using Gemini 2.5 Pro"""
        try:
            summary_prompt = f"""
            THERAPY SESSION DOCUMENTATION
            
            Generate a comprehensive clinical summary for this therapy session:
            
            SESSION METADATA:
            - Session ID: {therapy_session.session_id}
            - Framework: {therapy_session.therapeutic_framework.value}
            - Duration: {therapy_session.duration_minutes} minutes
            - Modality: {therapy_session.modality.value}
            - Session Type: {therapy_session.session_type.value}
            
            SESSION GOALS:
            {chr(10).join(f"• {goal}" for goal in therapy_session.session_goals)}
            
            SESSION CONTENT:
            {session_content.get('text_content', 'No content available')}
            
            TECHNIQUES USED:
            {chr(10).join(f"• {technique}" for technique in session_content.get('intervention_techniques_used', []))}
            
            CLINICAL DOCUMENTATION REQUIREMENTS:
            
            1. SESSION OVERVIEW (2-3 sentences):
               - Brief description of session focus
               - Client's presentation and engagement
               - Overall session tone and dynamics
            
            2. INTERVENTIONS AND TECHNIQUES:
               - Specific therapeutic techniques utilized
               - Client's response to interventions
               - Effectiveness of chosen approaches
               - Any modifications made during session
            
            3. THERAPEUTIC PROGRESS:
               - Observable changes in client's presentation
               - Insights gained by client
               - Skills demonstrated or practiced
               - Progress toward treatment goals
            
            4. CLIENT ENGAGEMENT AND PARTICIPATION:
               - Level of engagement and cooperation
               - Resistance or challenges encountered
               - Motivation and readiness for change
               - Therapeutic alliance quality
            
            5. HOMEWORK AND BETWEEN-SESSION TASKS:
               - Specific assignments given
               - Rationale for homework selection
               - Client's understanding and commitment
               - Anticipated challenges and solutions
            
            6. RISK ASSESSMENT AND SAFETY:
               - Current risk level and safety status
               - Any safety concerns identified
               - Safety planning updates if applicable
               - Crisis intervention needs
            
            7. CLINICAL IMPRESSIONS:
               - Diagnostic considerations
               - Treatment response patterns
               - Therapeutic relationship observations
               - Areas of strength and concern
            
            8. TREATMENT PLANNING:
               - Progress toward current goals
               - Adjustments needed in treatment approach
               - Focus areas for next session
               - Long-term treatment considerations
            
            Provide a professional, detailed summary suitable for clinical records and treatment planning.
            """
            
            response = await asyncio.to_thread(
                self.gemini_client.models.generate_content,
                model='gemini-2.5-pro',
                contents=summary_prompt
            )
            
            return {
                'clinical_summary': response.text,
                'session_effectiveness': self._assess_session_effectiveness(response.text),
                'next_session_focus': self._extract_next_focus(response.text),
                'treatment_adjustments': self._extract_treatment_adjustments(response.text),
                'summary_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error generating session summary: {e}")
            return {'error': str(e)}
    
    def _assess_session_effectiveness(self, summary_text: str) -> float:
        """Assess session effectiveness from summary"""
        effectiveness_indicators = [
            'breakthrough', 'insight', 'progress', 'improvement', 'engagement',
            'understanding', 'skill development', 'positive response'
        ]
        
        challenge_indicators = [
            'resistance', 'difficulty', 'struggle', 'setback', 'confusion',
            'poor engagement', 'limited progress'
        ]
        
        text_lower = summary_text.lower()
        positive_count = sum(1 for indicator in effectiveness_indicators if indicator in text_lower)
        negative_count = sum(1 for indicator in challenge_indicators if indicator in text_lower)
        
        # Calculate effectiveness score (0.0 to 1.0)
        if positive_count + negative_count == 0:
            return 0.7  # Default moderate effectiveness
        
        return min(1.0, max(0.0, (positive_count * 2 - negative_count) / (positive_count + negative_count + 2) + 0.5))
    
    def _extract_next_focus(self, summary_text: str) -> List[str]:
        """Extract focus areas for next session"""
        focus_areas = []
        text_lower = summary_text.lower()
        
        if 'continue' in text_lower and 'cbt' in text_lower:
            focus_areas.append('Continue CBT interventions')
        if 'mindfulness' in text_lower:
            focus_areas.append('Expand mindfulness practice')
        if 'homework' in text_lower and 'review' in text_lower:
            focus_areas.append('Review homework assignments')
        if 'crisis' in text_lower or 'safety' in text_lower:
            focus_areas.append('Safety planning and crisis prevention')
        if 'relationship' in text_lower:
            focus_areas.append('Interpersonal skills development')
        
        return focus_areas if focus_areas else ['Continue current therapeutic approach']
    
    def _extract_treatment_adjustments(self, summary_text: str) -> List[str]:
        """Extract recommended treatment adjustments"""
        adjustments = []
        text_lower = summary_text.lower()
        
        if 'increase frequency' in text_lower:
            adjustments.append('Increase session frequency')
        if 'medication' in text_lower:
            adjustments.append('Consider medication evaluation')
        if 'group therapy' in text_lower:
            adjustments.append('Explore group therapy options')
        if 'different approach' in text_lower:
            adjustments.append('Consider alternative therapeutic approach')
        
        return adjustments

class AgentCoordinationTool:
    """Tool for coordinating with other agents in the wellness platform"""
    
    def __init__(self):
        self.adk_comm = adk_comm
    
    async def coordinate_with_mental_orchestration(self, user_id: str, 
                                                 therapy_session: TherapySession,
                                                 session_summary: Dict[str, Any]) -> bool:
        """Send therapy session data to mental orchestration agent"""
        try:
            coordination_message = ADKMessage(
                message_id=f"therapy_coordination_{therapy_session.session_id}",
                message_type=MessageType.AGENT_COORDINATION,
                sender_agent="therapy_agent",
                recipient_agent="mental_orchestration_agent",
                priority=Priority.HIGH,
                timestamp=datetime.now(),
                payload={
                    'coordination_type': 'therapy_session_complete',
                    'user_id': user_id,
                    'session_data': {
                        'session_id': therapy_session.session_id,
                        'framework': therapy_session.therapeutic_framework.value,
                        'effectiveness_score': session_summary.get('session_effectiveness', 0.7),
                        'progress_indicators': session_summary.get('next_session_focus', []),
                        'safety_assessment': therapy_session.safety_assessment,
                        'homework_assigned': therapy_session.homework_assigned
                    }
                }
            )
            
            success = await self.adk_comm.send_message(coordination_message)
            if success:
                logging.info(f"Successfully coordinated therapy session {therapy_session.session_id} with mental orchestration")
            
            return success
            
        except Exception as e:
            logging.error(f"Error coordinating with mental orchestration: {e}")
            return False
    
    async def request_mental_exercises(self, user_id: str, therapy_session: TherapySession) -> bool:
        """Request personalized mental exercises based on therapy session"""
        try:
            exercise_request = ADKMessage(
                message_id=f"exercise_request_{therapy_session.session_id}",
                message_type=MessageType.EXERCISE_RECOMMENDATION,
                sender_agent="therapy_agent",
                recipient_agent="mental_exercise_agent",
                priority=Priority.NORMAL,
                timestamp=datetime.now(),
                payload={
                    'user_id': user_id,
                    'request_type': 'therapy_homework_support',
                    'therapeutic_context': {
                        'framework': therapy_session.therapeutic_framework.value,
                        'session_goals': therapy_session.session_goals,
                        'homework_assigned': therapy_session.homework_assigned,
                        'target_skills': self._extract_target_skills(therapy_session)
                    }
                }
            )
            
            success = await self.adk_comm.send_message(exercise_request)
            if success:
                logging.info(f"Successfully requested mental exercises for user {user_id}")
            
            return success
            
        except Exception as e:
            logging.error(f"Error requesting mental exercises: {e}")
            return False
    
    def _extract_target_skills(self, therapy_session: TherapySession) -> List[str]:
        """Extract target skills from therapy session"""
        framework_skills = {
            TherapeuticFramework.CBT: ['cognitive_restructuring', 'behavioral_activation', 'thought_challenging'],
            TherapeuticFramework.DBT: ['mindfulness', 'distress_tolerance', 'emotion_regulation'],
            TherapeuticFramework.ACT: ['psychological_flexibility', 'values_clarification', 'mindfulness']
        }
        
        return framework_skills.get(therapy_session.therapeutic_framework, ['general_coping_skills'])
    
    async def schedule_follow_up_session(self, user_id: str, 
                                       recommended_timeframe: str,
                                       priority_level: str) -> bool:
        """Schedule follow-up therapy session"""
        try:
            scheduling_request = ADKMessage(
                message_id=f"schedule_therapy_{user_id}_{datetime.now().timestamp()}",
                message_type=MessageType.SCHEDULING_REQUEST,
                sender_agent="therapy_agent",
                recipient_agent="scheduling_agent",
                priority=Priority.HIGH if priority_level in ['high', 'critical'] else Priority.NORMAL,
                timestamp=datetime.now(),
                payload={
                    'user_id': user_id,
                    'appointment_type': 'therapy_session',
                    'recommended_timeframe': recommended_timeframe,
                    'priority_level': priority_level,
                    'session_requirements': {
                        'duration_minutes': 50,
                        'modality_preference': 'user_choice',
                        'framework_continuation': True
                    }
                }
            )
            
            success = await self.adk_comm.send_message(scheduling_request)
            if success:
                logging.info(f"Successfully scheduled follow-up therapy session for user {user_id}")
            
            return success
            
        except Exception as e:
            logging.error(f"Error scheduling follow-up session: {e}")
            return False

class MultiModalContentTool:
    """Tool for generating multi-modal therapy content"""
    
    def __init__(self):
        self.elevenlabs = elevenlabs_voice
        self.tavus = tavus_video
    
    async def generate_session_audio(self, session_content: str, 
                                   therapy_context: Dict[str, Any]) -> Optional[bytes]:
        """Generate audio content for therapy session"""
        try:
            audio_content = await self.elevenlabs.synthesize_therapy_session_audio(
                session_content, therapy_context
            )
            
            if audio_content:
                logging.info("Successfully generated therapy session audio")
                return audio_content
            else:
                logging.warning("Failed to generate therapy session audio")
                return None
                
        except Exception as e:
            logging.error(f"Error generating session audio: {e}")
            return None
    
    async def generate_session_video(self, therapy_session: TherapySession,
                                   session_summary: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate video summary for therapy session"""
        try:
            video_data = {
                'session_id': therapy_session.session_id,
                'session_type': therapy_session.session_type.value,
                'therapeutic_framework': therapy_session.therapeutic_framework.value,
                'progress_score': session_summary.get('session_effectiveness', 0.7),
                'therapeutic_insights': session_summary.get('next_session_focus', []),
                'homework_assigned': therapy_session.homework_assigned
            }
            
            video_result = await self.tavus.create_therapy_session_video(video_data)
            
            if video_result:
                logging.info(f"Successfully initiated video generation for session {therapy_session.session_id}")
                return video_result
            else:
                logging.warning("Failed to initiate video generation")
                return None
                
        except Exception as e:
            logging.error(f"Error generating session video: {e}")
            return None
    
    async def create_therapeutic_resources(self, framework: TherapeuticFramework,
                                         homework_assignments: List[str]) -> Dict[str, Any]:
        """Create therapeutic resources and worksheets"""
        try:
            resources = {
                'worksheets': [],
                'audio_guides': [],
                'educational_materials': []
            }
            
            # Framework-specific resources
            if framework == TherapeuticFramework.CBT:
                resources['worksheets'] = [
                    {
                        'title': 'Thought Record Worksheet',
                        'description': 'Track and challenge negative thoughts',
                        'format': 'pdf',
                        'url': '/resources/cbt/thought_record.pdf'
                    },
                    {
                        'title': 'Behavioral Activation Planner',
                        'description': 'Plan meaningful activities',
                        'format': 'pdf',
                        'url': '/resources/cbt/behavioral_activation.pdf'
                    }
                ]
                
                # Generate audio guides for CBT exercises
                for assignment in homework_assignments:
                    if 'thought' in assignment.lower():
                        audio_guide = await self.elevenlabs.synthesize_mental_exercise_audio(
                            "Let's practice identifying and challenging negative thoughts. Start by noticing when you have a strong emotional reaction...",
                            'CBT'
                        )
                        if audio_guide:
                            resources['audio_guides'].append({
                                'title': 'Thought Challenging Guide',
                                'duration': '5 minutes',
                                'audio_data': audio_guide
                            })
            
            elif framework == TherapeuticFramework.DBT:
                resources['worksheets'] = [
                    {
                        'title': 'Mindfulness Practice Log',
                        'description': 'Track daily mindfulness practice',
                        'format': 'pdf',
                        'url': '/resources/dbt/mindfulness_log.pdf'
                    },
                    {
                        'title': 'Distress Tolerance Skills',
                        'description': 'Crisis survival strategies',
                        'format': 'pdf',
                        'url': '/resources/dbt/distress_tolerance.pdf'
                    }
                ]
            
            elif framework == TherapeuticFramework.ACT:
                resources['worksheets'] = [
                    {
                        'title': 'Values Clarification Exercise',
                        'description': 'Identify your core values',
                        'format': 'pdf',
                        'url': '/resources/act/values_clarification.pdf'
                    },
                    {
                        'title': 'Committed Action Plan',
                        'description': 'Plan values-based actions',
                        'format': 'pdf',
                        'url': '/resources/act/committed_action.pdf'
                    }
                ]
            
            return resources
            
        except Exception as e:
            logging.error(f"Error creating therapeutic resources: {e}")
            return {}

# Initialize tool instances
gemini_reasoning_tool = GeminiTherapeuticReasoningTool()
session_summary_tool = SessionSummaryTool()
agent_coordination_tool = AgentCoordinationTool()
multimodal_content_tool = MultiModalContentTool()
