import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid

from google.adk import Agent, AgentConfig, Session
from google.genai import Client as GenAIClient

from config.api_keys import get_api_key
from shared.models.therapy_models import TherapySession, TherapeuticFramework, SessionType, SessionModality
from shared.models.user_models import MentalHealthState, RiskLevel
from shared.utils.adk_communication import adk_comm, MessageType, Priority, ADKMessage
from shared.constants.therapeutic_constants import TherapeuticFrameworks, RISK_ASSESSMENT_THRESHOLDS
from vector_db.schemas.mental_health_schemas import TherapySessionVector, VectorType
from vector_db.utils.vector_operations import vector_ops
from vector_db.embeddings.gemini_embeddings import gemini_embeddings
from config.firebase_config import firebase_config
from integrations.elevenlabs.voice_synthesis import elevenlabs_voice
from integrations.tavus.video_generation import tavus_video

class TherapyAgent(Agent):
    """Google ADK-powered therapy agent for evidence-based therapeutic interventions"""
    
    def __init__(self):
        # Initialize Google ADK agent configuration
        config = AgentConfig(
            name="therapy_agent",
            description="AI-powered therapy agent providing evidence-based therapeutic interventions using CBT, DBT, and ACT frameworks",
            model="gemini-2.5-pro",
            temperature=0.3,  # Lower temperature for more consistent therapeutic responses
            max_tokens=4096,
            system_instructions=self._get_system_instructions()
        )
        
        super().__init__(config)
        
        # Initialize Gemini client for advanced therapeutic reasoning
        self.gemini_client = GenAIClient(api_key=get_api_key('gemini_2_5_pro'))
        
        # Therapeutic frameworks
        self.frameworks = TherapeuticFrameworks()
        
        # Active therapy sessions
        self.active_sessions = {}
        self.session_history = {}
        
        # Crisis intervention settings
        self.crisis_protocols_active = True
        self.emergency_contacts = {}
        
        logging.info("Therapy Agent initialized with Google ADK")
    
    def _get_system_instructions(self) -> str:
        """Get comprehensive system instructions for the therapy agent"""
        return """You are a professional AI therapy agent trained in evidence-based therapeutic interventions. Your role encompasses:

CORE THERAPEUTIC COMPETENCIES:
1. EVIDENCE-BASED PRACTICE: Implement CBT, DBT, and ACT methodologies with clinical precision
2. CRISIS INTERVENTION: Immediately identify and respond to mental health crises with appropriate safety protocols
3. THERAPEUTIC ALLIANCE: Build trust, rapport, and collaborative therapeutic relationships
4. ASSESSMENT: Conduct ongoing mental health assessments and risk evaluations
5. TREATMENT PLANNING: Develop personalized therapeutic interventions based on user needs

THERAPEUTIC FRAMEWORKS:
- CBT (Cognitive Behavioral Therapy): Focus on thought-behavior connections, cognitive restructuring, behavioral activation
- DBT (Dialectical Behavior Therapy): Emphasize mindfulness, distress tolerance, emotion regulation, interpersonal effectiveness
- ACT (Acceptance and Commitment Therapy): Promote psychological flexibility, values-based living, mindfulness

SAFETY PROTOCOLS:
- ALWAYS conduct safety assessments when crisis indicators are present
- Immediately escalate suicidal ideation, self-harm, or psychosis
- Maintain professional boundaries while providing empathetic support
- Document all safety concerns and interventions

THERAPEUTIC PROCESS:
1. Assessment and rapport building
2. Collaborative goal setting
3. Intervention implementation
4. Progress monitoring
5. Relapse prevention planning

COMMUNICATION GUIDELINES:
- Use professional yet warm and empathetic language
- Validate emotions while challenging maladaptive thoughts
- Provide psychoeducation about mental health conditions
- Encourage active participation in the therapeutic process
- Maintain hope while being realistic about challenges

Remember: You are providing therapeutic support, not replacing professional human therapy. Always encourage users to seek additional professional help when appropriate."""

    async def conduct_therapy_session(self, session: Session, session_request: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct comprehensive therapy session with multi-modal capabilities"""
        try:
            user_id = session_request.get('user_id')
            session_type = SessionType(session_request.get('session_type', 'individual'))
            framework = TherapeuticFramework(session_request.get('framework', 'CBT'))
            modality = SessionModality(session_request.get('modality', 'text'))
            crisis_alert = session_request.get('crisis_alert', False)
            
            logging.info(f"Starting {framework.value} therapy session for user {user_id}")
            
            # Create therapy session object
            therapy_session = self._create_therapy_session(
                user_id, session_type, framework, modality, crisis_alert
            )
            
            # Retrieve user's mental health context
            user_context = await self._get_user_mental_health_context(user_id)
            
            # Conduct safety assessment
            safety_assessment = await self._conduct_safety_assessment(
                session, user_context, crisis_alert
            )
            
            # Select therapeutic intervention based on framework and context
            intervention_plan = await self._select_therapeutic_intervention(
                framework, user_context, safety_assessment
            )
            
            # Conduct therapy session based on modality
            session_content = await self._conduct_session_by_modality(
                session, therapy_session, intervention_plan, modality
            )
            
            # Generate session summary and insights
            session_summary = await self._generate_session_summary(
                session, therapy_session, session_content, intervention_plan
            )
            
            # Create and store therapy session vector
            session_vector = await self._create_therapy_session_vector(
                therapy_session, session_content, session_summary
            )
            
            # Store session data
            await self._store_therapy_session(therapy_session, session_summary)
            
            # Handle post-session communications
            await self._handle_post_session_communications(
                user_id, therapy_session, session_summary, safety_assessment
            )
            
            # Generate multi-modal session materials
            session_materials = await self._generate_session_materials(
                therapy_session, session_summary, modality
            )
            
            return {
                'session_id': therapy_session.session_id,
                'session_summary': session_summary,
                'safety_assessment': safety_assessment,
                'homework_assigned': therapy_session.homework_assigned,
                'session_materials': session_materials,
                'next_session_recommended': self._recommend_next_session(safety_assessment),
                'crisis_intervention_needed': safety_assessment.get('crisis_level') == 'critical',
                'processing_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error conducting therapy session: {e}")
            return {
                'error': str(e),
                'crisis_support_message': self._get_crisis_support_message()
            }
    
    def _create_therapy_session(self, user_id: str, session_type: SessionType, 
                               framework: TherapeuticFramework, modality: SessionModality, 
                               crisis_alert: bool) -> TherapySession:
        """Create therapy session object"""
        session_id = f"therapy_{user_id}_{datetime.now().timestamp()}"
        
        return TherapySession(
            session_id=session_id,
            user_id=user_id,
            therapist_agent_id="therapy_agent",
            session_type=session_type,
            therapeutic_framework=framework,
            modality=modality,
            scheduled_start=datetime.now(),
            actual_start=datetime.now(),
            duration_minutes=50,
            session_goals=self._get_default_session_goals(framework, crisis_alert),
            safety_assessment={'crisis_alert': crisis_alert},
            crisis_indicators=[] if not crisis_alert else ['crisis_alert_received']
        )
    
    def _get_default_session_goals(self, framework: TherapeuticFramework, crisis_alert: bool) -> List[str]:
        """Get default session goals based on framework"""
        if crisis_alert:
            return [
                "Ensure immediate safety and stability",
                "Assess suicide risk and self-harm potential",
                "Develop crisis safety plan",
                "Connect with emergency resources if needed"
            ]
        
        framework_goals = {
            TherapeuticFramework.CBT: [
                "Identify and challenge negative thought patterns",
                "Explore thought-behavior-emotion connections",
                "Develop cognitive restructuring skills",
                "Assign behavioral activation homework"
            ],
            TherapeuticFramework.DBT: [
                "Practice mindfulness and present-moment awareness",
                "Develop distress tolerance skills",
                "Improve emotion regulation strategies",
                "Enhance interpersonal effectiveness"
            ],
            TherapeuticFramework.ACT: [
                "Increase psychological flexibility",
                "Clarify personal values and goals",
                "Practice acceptance of difficult emotions",
                "Commit to values-based actions"
            ]
        }
        
        return framework_goals.get(framework, framework_goals[TherapeuticFramework.CBT])
    
    async def _get_user_mental_health_context(self, user_id: str) -> Dict[str, Any]:
        """Retrieve comprehensive mental health context for user"""
        try:
            # Get recent mental health timeline
            timeline = await vector_ops.get_user_mental_health_timeline(user_id, days=14)
            
            # Get user profile from Firebase
            db = firebase_config.get_firestore_client()
            user_doc = db.collection('users').document(user_id).get()
            user_profile = user_doc.to_dict() if user_doc.exists else {}
            
            # Get recent journal entries for context
            recent_journals = await vector_ops.semantic_search(
                query_vector=[0.0] * 768,  # Dummy vector for recent entries
                vector_type=VectorType.JOURNAL_ENTRY,
                user_id=user_id,
                top_k=5
            )
            
            return {
                'user_profile': user_profile,
                'timeline': timeline,
                'recent_journals': recent_journals,
                'mental_health_conditions': user_profile.get('mental_health_conditions', []),
                'current_medications': user_profile.get('current_medications', []),
                'therapeutic_goals': user_profile.get('therapeutic_goals', []),
                'risk_level': user_profile.get('risk_level', 'low')
            }
            
        except Exception as e:
            logging.error(f"Error retrieving user context: {e}")
            return {}
    
    async def _conduct_safety_assessment(self, session: Session, user_context: Dict[str, Any], 
                                       crisis_alert: bool) -> Dict[str, Any]:
        """Conduct comprehensive safety assessment"""
        try:
            # Import safety assessment prompts
            from .prompt_file import TherapyPrompts
            
            safety_prompt = TherapyPrompts.get_safety_assessment_prompt(user_context, crisis_alert)
            
            # Conduct safety assessment using Gemini 2.5 Pro
            safety_response = await session.send_message(safety_prompt)
            
            # Parse safety assessment (simplified for demo)
            safety_level = self._parse_safety_level(safety_response.text)
            risk_factors = self._extract_risk_factors(safety_response.text)
            protective_factors = self._extract_protective_factors(safety_response.text)
            
            safety_assessment = {
                'assessment_timestamp': datetime.now().isoformat(),
                'crisis_level': safety_level,
                'risk_factors': risk_factors,
                'protective_factors': protective_factors,
                'immediate_intervention_needed': safety_level in ['high', 'critical'],
                'safety_plan_required': safety_level in ['moderate', 'high', 'critical'],
                'emergency_contacts_needed': safety_level == 'critical',
                'assessment_details': safety_response.text
            }
            
            return safety_assessment
            
        except Exception as e:
            logging.error(f"Error in safety assessment: {e}")
            return {'crisis_level': 'moderate', 'error': str(e)}
    
    def _parse_safety_level(self, assessment_text: str) -> str:
        """Parse safety level from assessment text"""
        text_lower = assessment_text.lower()
        if any(word in text_lower for word in ['critical', 'imminent', 'immediate danger']):
            return 'critical'
        elif any(word in text_lower for word in ['high risk', 'significant concern']):
            return 'high'
        elif any(word in text_lower for word in ['moderate', 'some concern']):
            return 'moderate'
        else:
            return 'low'
    
    def _extract_risk_factors(self, assessment_text: str) -> List[str]:
        """Extract risk factors from assessment"""
        risk_factors = []
        text_lower = assessment_text.lower()
        
        risk_keywords = {
            'suicidal_ideation': ['suicide', 'kill myself', 'end my life'],
            'self_harm': ['self harm', 'cut myself', 'hurt myself'],
            'substance_abuse': ['drinking', 'drugs', 'alcohol'],
            'social_isolation': ['alone', 'isolated', 'no friends'],
            'hopelessness': ['hopeless', 'no future', 'pointless'],
            'severe_depression': ['severe depression', 'can\'t function'],
            'psychosis': ['voices', 'hallucinations', 'paranoid']
        }
        
        for factor, keywords in risk_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                risk_factors.append(factor)
        
        return risk_factors
    
    def _extract_protective_factors(self, assessment_text: str) -> List[str]:
        """Extract protective factors from assessment"""
        protective_factors = []
        text_lower = assessment_text.lower()
        
        protective_keywords = {
            'social_support': ['family', 'friends', 'support'],
            'coping_skills': ['coping', 'strategies', 'techniques'],
            'treatment_engagement': ['therapy', 'medication', 'treatment'],
            'future_orientation': ['goals', 'plans', 'future'],
            'spiritual_beliefs': ['faith', 'spiritual', 'religious'],
            'responsibility_to_others': ['children', 'pets', 'responsibilities']
        }
        
        for factor, keywords in protective_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                protective_factors.append(factor)
        
        return protective_factors
    
    async def _select_therapeutic_intervention(self, framework: TherapeuticFramework, 
                                             user_context: Dict[str, Any], 
                                             safety_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Select appropriate therapeutic intervention"""
        
        # Crisis intervention takes priority
        if safety_assessment.get('crisis_level') in ['high', 'critical']:
            return {
                'intervention_type': 'crisis_intervention',
                'primary_techniques': ['safety_planning', 'crisis_stabilization', 'resource_connection'],
                'session_structure': 'crisis_focused',
                'homework': ['safety_plan_review', 'emergency_contact_practice']
            }
        
        # Framework-specific interventions
        framework_interventions = {
            TherapeuticFramework.CBT: {
                'intervention_type': 'cognitive_behavioral',
                'primary_techniques': ['cognitive_restructuring', 'behavioral_activation', 'thought_challenging'],
                'session_structure': 'structured_cbt',
                'homework': ['thought_record', 'behavioral_experiment', 'activity_scheduling']
            },
            TherapeuticFramework.DBT: {
                'intervention_type': 'dialectical_behavioral',
                'primary_techniques': ['mindfulness', 'distress_tolerance', 'emotion_regulation'],
                'session_structure': 'skills_focused',
                'homework': ['mindfulness_practice', 'distress_tolerance_skills', 'emotion_diary']
            },
            TherapeuticFramework.ACT: {
                'intervention_type': 'acceptance_commitment',
                'primary_techniques': ['values_clarification', 'psychological_flexibility', 'mindfulness'],
                'session_structure': 'values_based',
                'homework': ['values_exercise', 'mindfulness_practice', 'committed_action_plan']
            }
        }
        
        return framework_interventions.get(framework, framework_interventions[TherapeuticFramework.CBT])
    
    async def _conduct_session_by_modality(self, session: Session, therapy_session: TherapySession, 
                                         intervention_plan: Dict[str, Any], 
                                         modality: SessionModality) -> Dict[str, Any]:
        """Conduct therapy session based on selected modality"""
        
        # Import therapeutic prompts
        from .prompt_file import TherapyPrompts
        
        # Generate session prompt based on intervention plan
        session_prompt = TherapyPrompts.get_session_prompt(
            therapy_session.therapeutic_framework,
            intervention_plan,
            therapy_session.session_goals
        )
        
        # Conduct text-based session
        text_response = await session.send_message(session_prompt)
        
        session_content = {
            'text_content': text_response.text,
            'intervention_techniques_used': intervention_plan['primary_techniques'],
            'session_structure': intervention_plan['session_structure']
        }
        
        # Generate audio content if requested
        if modality in [SessionModality.VOICE, SessionModality.MIXED]:
            audio_content = await elevenlabs_voice.synthesize_therapy_session_audio(
                text_response.text,
                {
                    'therapeutic_framework': therapy_session.therapeutic_framework.value,
                    'user_mood_score': 0.0,  # Would be retrieved from context
                    'session_type': therapy_session.session_type.value
                }
            )
            session_content['audio_content'] = audio_content
        
        # Generate video content if requested
        if modality in [SessionModality.VIDEO, SessionModality.MIXED]:
            video_request = await tavus_video.create_therapy_session_video({
                'session_id': therapy_session.session_id,
                'session_type': therapy_session.session_type.value,
                'therapeutic_framework': therapy_session.therapeutic_framework.value,
                'progress_score': 0.7,  # Would be calculated from user progress
                'therapeutic_insights': therapy_session.therapeutic_insights,
                'homework_assigned': intervention_plan.get('homework', [])
            })
            session_content['video_content'] = video_request
        
        return session_content
    
    async def _generate_session_summary(self, session: Session, therapy_session: TherapySession, 
                                       session_content: Dict[str, Any], 
                                       intervention_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive session summary"""
        try:
            # Import summary prompts
            from .prompt_file import TherapyPrompts
            
            summary_prompt = TherapyPrompts.get_session_summary_prompt(
                therapy_session,
                session_content,
                intervention_plan
            )
            
            summary_response = await session.send_message(summary_prompt)
            
            return {
                'session_id': therapy_session.session_id,
                'summary_text': summary_response.text,
                'therapeutic_framework': therapy_session.therapeutic_framework.value,
                'techniques_used': intervention_plan['primary_techniques'],
                'goals_addressed': therapy_session.session_goals,
                'homework_assigned': intervention_plan.get('homework', []),
                'progress_indicators': self._extract_progress_indicators(summary_response.text),
                'next_session_focus': self._extract_next_session_focus(summary_response.text),
                'therapist_notes': summary_response.text,
                'session_rating': self._calculate_session_effectiveness(summary_response.text)
            }
            
        except Exception as e:
            logging.error(f"Error generating session summary: {e}")
            return {'error': str(e)}
    
    def _extract_progress_indicators(self, summary_text: str) -> List[str]:
        """Extract progress indicators from session summary"""
        indicators = []
        text_lower = summary_text.lower()
        
        progress_keywords = {
            'insight_gained': ['insight', 'understanding', 'awareness'],
            'skill_development': ['skill', 'technique', 'strategy'],
            'behavioral_change': ['behavior', 'action', 'change'],
            'emotional_regulation': ['emotion', 'feeling', 'mood'],
            'cognitive_shift': ['thought', 'thinking', 'perspective']
        }
        
        for indicator, keywords in progress_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                indicators.append(indicator)
        
        return indicators
    
    def _extract_next_session_focus(self, summary_text: str) -> List[str]:
        """Extract focus areas for next session"""
        # Simplified extraction - would use more sophisticated NLP in production
        if 'continue' in summary_text.lower():
            return ['continue_current_interventions']
        elif 'new' in summary_text.lower():
            return ['introduce_new_techniques']
        else:
            return ['review_progress', 'adjust_treatment_plan']
    
    def _calculate_session_effectiveness(self, summary_text: str) -> float:
        """Calculate session effectiveness score"""
        # Simplified scoring based on positive indicators
        positive_indicators = ['progress', 'improvement', 'insight', 'breakthrough', 'success']
        negative_indicators = ['resistance', 'difficulty', 'struggle', 'setback']
        
        text_lower = summary_text.lower()
        positive_count = sum(1 for indicator in positive_indicators if indicator in text_lower)
        negative_count = sum(1 for indicator in negative_indicators if indicator in text_lower)
        
        # Calculate score (0.0 to 1.0)
        total_indicators = positive_count + negative_count
        if total_indicators == 0:
            return 0.7  # Default moderate effectiveness
        
        return min(1.0, max(0.0, (positive_count - negative_count * 0.5) / total_indicators + 0.5))
    
    async def _create_therapy_session_vector(self, therapy_session: TherapySession, 
                                           session_content: Dict[str, Any], 
                                           session_summary: Dict[str, Any]) -> TherapySessionVector:
        """Create therapy session vector for semantic storage"""
        
        # Prepare comprehensive text for embedding
        embedding_text = f"""
        Therapy Session Summary:
        Framework: {therapy_session.therapeutic_framework.value}
        Session Type: {therapy_session.session_type.value}
        Goals: {', '.join(therapy_session.session_goals)}
        Techniques Used: {', '.join(session_content.get('intervention_techniques_used', []))}
        Summary: {session_summary.get('summary_text', '')}
        Progress: {', '.join(session_summary.get('progress_indicators', []))}
        """
        
        # Generate embedding
        embedding = await gemini_embeddings.generate_mental_health_embedding(
            embedding_text,
            title=f"Therapy Session - {therapy_session.therapeutic_framework.value}"
        )
        
        # Create therapy session vector
        session_vector = TherapySessionVector(
            id=therapy_session.session_id,
            user_id=therapy_session.user_id,
            vector=embedding,
            created_at=therapy_session.actual_start or datetime.now(),
            updated_at=datetime.now(),
            session_type=therapy_session.session_type.value,
            therapeutic_framework=therapy_session.therapeutic_framework.value,
            progress_score=session_summary.get('session_rating', 0.7),
            insights=session_summary.get('progress_indicators', []),
            homework_assigned=session_summary.get('homework_assigned', []),
            therapist_notes=session_summary.get('summary_text', ''),
            session_duration=therapy_session.duration_minutes,
            metadata={
                'techniques_used': session_content.get('intervention_techniques_used', []),
                'session_effectiveness': session_summary.get('session_rating', 0.7),
                'safety_assessment': therapy_session.safety_assessment,
                'crisis_indicators': therapy_session.crisis_indicators
            }
        )
        
        # Store vector in database
        await vector_ops.upsert_mental_health_vector(session_vector)
        
        return session_vector
    
    async def _store_therapy_session(self, therapy_session: TherapySession, 
                                   session_summary: Dict[str, Any]):
        """Store therapy session in Firebase"""
        try:
            db = firebase_config.get_firestore_client()
            
            session_doc = {
                'session_id': therapy_session.session_id,
                'user_id': therapy_session.user_id,
                'therapeutic_framework': therapy_session.therapeutic_framework.value,
                'session_type': therapy_session.session_type.value,
                'modality': therapy_session.modality.value,
                'scheduled_start': therapy_session.scheduled_start,
                'actual_start': therapy_session.actual_start,
                'actual_end': therapy_session.actual_end or datetime.now(),
                'duration_minutes': therapy_session.duration_minutes,
                'session_goals': therapy_session.session_goals,
                'homework_assigned': therapy_session.homework_assigned,
                'safety_assessment': therapy_session.safety_assessment,
                'crisis_indicators': therapy_session.crisis_indicators,
                'session_summary': session_summary,
                'processed_by': 'therapy_agent',
                'created_at': datetime.now()
            }
            
            db.collection('therapy_sessions').document(therapy_session.session_id).set(session_doc)
            
        except Exception as e:
            logging.error(f"Error storing therapy session: {e}")
    
    async def _handle_post_session_communications(self, user_id: str, therapy_session: TherapySession, 
                                                session_summary: Dict[str, Any], 
                                                safety_assessment: Dict[str, Any]):
        """Handle communications with other agents after session"""
        
        # Send session update to mental orchestration agent
        session_update = ADKMessage(
            message_id=f"therapy_update_{therapy_session.session_id}",
            message_type=MessageType.THERAPY_SESSION_REQUEST,
            sender_agent="therapy_agent",
            recipient_agent="mental_orchestration_agent",
            priority=Priority.HIGH if safety_assessment.get('crisis_level') == 'critical' else Priority.NORMAL,
            timestamp=datetime.now(),
            payload={
                'user_id': user_id,
                'session_id': therapy_session.session_id,
                'session_summary': session_summary,
                'safety_assessment': safety_assessment,
                'homework_assigned': therapy_session.homework_assigned
            }
        )
        
        await adk_comm.send_message(session_update)
        
        # Request mental exercises if homework assigned
        if therapy_session.homework_assigned:
            exercise_request = adk_comm.create_exercise_recommendation_request(
                user_id=user_id,
                mental_state={'homework_focus': therapy_session.homework_assigned},
                sender_agent="therapy_agent"
            )
            await adk_comm.send_message(exercise_request)
        
        # Schedule follow-up if needed
        if self._recommend_next_session(safety_assessment):
            scheduling_request = ADKMessage(
                message_id=f"schedule_followup_{user_id}_{datetime.now().timestamp()}",
                message_type=MessageType.SCHEDULING_REQUEST,
                sender_agent="therapy_agent",
                recipient_agent="scheduling_agent",
                priority=Priority.HIGH,
                timestamp=datetime.now(),
                payload={
                    'user_id': user_id,
                    'session_type': 'therapy_followup',
                    'recommended_timeframe': '1_week',
                    'priority_level': safety_assessment.get('crisis_level', 'low')
                }
            )
            await adk_comm.send_message(scheduling_request)
    
    def _recommend_next_session(self, safety_assessment: Dict[str, Any]) -> bool:
        """Determine if next session should be recommended"""
        crisis_level = safety_assessment.get('crisis_level', 'low')
        return crisis_level in ['moderate', 'high', 'critical']
    
    async def _generate_session_materials(self, therapy_session: TherapySession, 
                                        session_summary: Dict[str, Any], 
                                        modality: SessionModality) -> Dict[str, Any]:
        """Generate additional session materials"""
        materials = {
            'session_transcript': session_summary.get('summary_text', ''),
            'homework_instructions': therapy_session.homework_assigned,
            'resource_links': self._get_therapeutic_resources(therapy_session.therapeutic_framework)
        }
        
        # Add modality-specific materials
        if modality in [SessionModality.VOICE, SessionModality.MIXED]:
            materials['audio_summary_available'] = True
        
        if modality in [SessionModality.VIDEO, SessionModality.MIXED]:
            materials['video_summary_available'] = True
        
        return materials
    
    def _get_therapeutic_resources(self, framework: TherapeuticFramework) -> List[Dict[str, str]]:
        """Get therapeutic resources based on framework"""
        resources = {
            TherapeuticFramework.CBT: [
                {'title': 'Thought Record Worksheet', 'type': 'worksheet'},
                {'title': 'Cognitive Distortions Guide', 'type': 'educational'},
                {'title': 'Behavioral Activation Planning', 'type': 'worksheet'}
            ],
            TherapeuticFramework.DBT: [
                {'title': 'Mindfulness Exercises', 'type': 'practice'},
                {'title': 'Distress Tolerance Skills', 'type': 'educational'},
                {'title': 'Emotion Regulation Diary', 'type': 'worksheet'}
            ],
            TherapeuticFramework.ACT: [
                {'title': 'Values Clarification Exercise', 'type': 'worksheet'},
                {'title': 'Mindfulness Practices', 'type': 'practice'},
                {'title': 'Committed Action Planning', 'type': 'worksheet'}
            ]
        }
        
        return resources.get(framework, resources[TherapeuticFramework.CBT])
    
    def _get_crisis_support_message(self) -> str:
        """Get crisis support message"""
        return """If you're experiencing a mental health crisis, please reach out for immediate help:
        
        🇺🇸 National Suicide Prevention Lifeline: 988
        🇺🇸 Crisis Text Line: Text HOME to 741741
        🇺🇸 Emergency Services: 911
        
        You are not alone, and professional help is available 24/7."""

# Global therapy agent instance
therapy_agent = TherapyAgent()
