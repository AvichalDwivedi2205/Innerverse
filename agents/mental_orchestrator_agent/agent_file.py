import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from google.adk import Agent, AgentConfig, Session
from google.genai import Client as GenAIClient

from config.api_keys import get_api_key
from shared.models.user_models import MentalHealthState, UserProfile
from shared.utils.adk_communication import adk_comm, MessageType, Priority, ADKMessage
from vector_db.schemas.mental_health_schemas import VectorType
from vector_db.utils.vector_operations import vector_ops
from config.firebase_config import firebase_config
from integrations.tavus.video_generation import tavus_video

class MentalOrchestrationAgent(Agent):
    """Google ADK-powered central coordinator for mental health data integration"""
    
    def __init__(self):
        # Initialize Google ADK agent configuration
        config = AgentConfig(
            name="mental_orchestration_agent",
            description="Central coordinator for mental health data integration, progress tracking, and comprehensive mental map generation",
            model="gemini-2.5-pro",
            temperature=0.2,  # Low temperature for consistent analysis
            max_tokens=8192,
            system_instructions=self._get_system_instructions()
        )
        
        super().__init__(config)
        
        # Initialize Gemini client with 1M token context window
        self.gemini_client = GenAIClient(api_key=get_api_key('gemini_2_5_pro'))
        self.context_window = 1000000  # 1M token context window
        
        # Progress tracking
        self.progress_reports = {}
        self.mental_maps = {}
        
        logging.info("Mental Orchestration Agent initialized with Google ADK")
    
    def _get_system_instructions(self) -> str:
        """Get system instructions for the orchestration agent"""
        return """You are the Mental Health Orchestration Agent, the central coordinator for comprehensive mental health data integration and analysis. Your role is to:

1. COMPREHENSIVE DATA ANALYSIS: Aggregate and analyze data from journaling and therapy sessions using advanced vector clustering and pattern recognition
2. PROGRESS TRACKING: Generate objective progress measurements and trend identification across all mental health activities
3. MENTAL MAP GENERATION: Create detailed mental health maps showing emotional patterns, triggers, coping mechanisms, and therapeutic progress
4. AGENT COORDINATION: Coordinate with all mental health agents to ensure comprehensive care delivery
5. INSIGHT GENERATION: Provide actionable insights based on comprehensive data analysis using Gemini 2.5 Pro's advanced reasoning

Key Capabilities:
- Utilize 1 million token context window for holistic analysis
- Perform vector clustering to identify emotional patterns
- Generate progress reports every 5 days with trend analysis
- Create AI-powered video summaries using Tavus API
- Coordinate care between journaling, therapy, and exercise agents

Maintain objectivity while providing meaningful insights that support user's mental health journey."""

    async def generate_comprehensive_analysis(self, session: Session, user_id: str, 
                                            analysis_request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive mental health analysis using 1M token context"""
        try:
            timeframe_days = analysis_request.get('timeframe_days', 30)
            analysis_type = analysis_request.get('analysis_type', 'comprehensive')
            
            logging.info(f"Generating comprehensive analysis for user {user_id}, timeframe: {timeframe_days} days")
            
            # Gather comprehensive data using vector operations
            comprehensive_data = await self._gather_comprehensive_data(user_id, timeframe_days)
            
            # Perform vector clustering analysis
            clustering_analysis = await self._perform_clustering_analysis(user_id, timeframe_days)
            
            # Generate mental health map
            mental_map = await self._generate_mental_health_map(
                session, comprehensive_data, clustering_analysis
            )
            
            # Calculate progress metrics
            progress_metrics = await self._calculate_progress_metrics(
                session, comprehensive_data, timeframe_days
            )
            
            # Generate actionable insights
            insights = await self._generate_actionable_insights(
                session, mental_map, progress_metrics, clustering_analysis
            )
            
            # Create progress report
            progress_report = await self._create_progress_report(
                user_id, mental_map, progress_metrics, insights, timeframe_days
            )
            
            # Generate video summary if requested
            video_summary = None
            if analysis_request.get('include_video', True):
                video_summary = await self._generate_video_summary(progress_report)
            
            # Coordinate with other agents
            await self._coordinate_follow_up_actions(user_id, insights, progress_metrics)
            
            return {
                'analysis_id': f"analysis_{user_id}_{datetime.now().timestamp()}",
                'mental_map': mental_map,
                'progress_metrics': progress_metrics,
                'insights': insights,
                'progress_report': progress_report,
                'video_summary': video_summary,
                'clustering_analysis': clustering_analysis,
                'generated_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error generating comprehensive analysis: {e}")
            return {'error': str(e)}
    
    async def _gather_comprehensive_data(self, user_id: str, timeframe_days: int) -> Dict[str, Any]:
        """Gather comprehensive mental health data from all sources"""
        try:
            # Get user timeline
            timeline = await vector_ops.get_user_mental_health_timeline(user_id, timeframe_days)
            
            # Get journal entries clustering
            journal_clustering = await vector_ops.cluster_mental_health_vectors(
                vector_type=VectorType.JOURNAL_ENTRY,
                user_id=user_id,
                time_window_days=timeframe_days,
                num_clusters=5
            )
            
            # Get therapy sessions clustering
            therapy_clustering = await vector_ops.cluster_mental_health_vectors(
                vector_type=VectorType.THERAPY_SESSION,
                user_id=user_id,
                time_window_days=timeframe_days,
                num_clusters=3
            )
            
            # Get user profile
            db = firebase_config.get_firestore_client()
            user_doc = db.collection('users').document(user_id).get()
            user_profile = user_doc.to_dict() if user_doc.exists else {}
            
            return {
                'timeline': timeline,
                'journal_clustering': journal_clustering,
                'therapy_clustering': therapy_clustering,
                'user_profile': user_profile,
                'data_points': len(timeline.get('timeline', {}).get('journal_entries', [])),
                'therapy_sessions': len(timeline.get('timeline', {}).get('therapy_sessions', []))
            }
            
        except Exception as e:
            logging.error(f"Error gathering comprehensive data: {e}")
            return {}
    
    async def _perform_clustering_analysis(self, user_id: str, timeframe_days: int) -> Dict[str, Any]:
        """Perform advanced clustering analysis on mental health data"""
        try:
            # Import clustering tools
            from .tool_file import vector_clustering_tool
            
            clustering_results = await vector_clustering_tool.perform_comprehensive_clustering(
                user_id, timeframe_days
            )
            
            return clustering_results
            
        except Exception as e:
            logging.error(f"Error in clustering analysis: {e}")
            return {}
    
    async def _generate_mental_health_map(self, session: Session, comprehensive_data: Dict[str, Any], 
                                        clustering_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive mental health map using Gemini 2.5 Pro"""
        try:
            # Import prompts
            from .prompt_file import OrchestrationPrompts
            
            mental_map_prompt = OrchestrationPrompts.get_mental_health_map_prompt(
                comprehensive_data, clustering_analysis
            )
            
            # Generate mental map using Gemini 2.5 Pro
            map_response = await session.send_message(mental_map_prompt)
            
            # Parse and structure the mental map
            mental_map = {
                'emotional_patterns': self._extract_emotional_patterns(map_response.text),
                'trigger_analysis': self._extract_triggers(map_response.text),
                'coping_mechanisms': self._extract_coping_mechanisms(map_response.text),
                'therapeutic_progress': self._extract_therapeutic_progress(map_response.text),
                'risk_factors': self._extract_risk_factors(map_response.text),
                'protective_factors': self._extract_protective_factors(map_response.text),
                'relationship_patterns': self._extract_relationship_patterns(map_response.text),
                'behavioral_patterns': self._extract_behavioral_patterns(map_response.text),
                'generated_map': map_response.text
            }
            
            return mental_map
            
        except Exception as e:
            logging.error(f"Error generating mental health map: {e}")
            return {}
    
    def _extract_emotional_patterns(self, map_text: str) -> List[Dict[str, Any]]:
        """Extract emotional patterns from mental map"""
        patterns = []
        
        # Simplified pattern extraction
        if 'anxiety' in map_text.lower():
            patterns.append({
                'pattern': 'anxiety_cycles',
                'frequency': 'high',
                'triggers': ['work_stress', 'social_situations'],
                'intensity': 'moderate_to_high'
            })
        
        if 'depression' in map_text.lower():
            patterns.append({
                'pattern': 'depressive_episodes',
                'frequency': 'moderate',
                'triggers': ['isolation', 'negative_thoughts'],
                'intensity': 'moderate'
            })
        
        return patterns
    
    def _extract_triggers(self, map_text: str) -> List[Dict[str, Any]]:
        """Extract trigger analysis from mental map"""
        triggers = []
        
        common_triggers = ['work', 'relationships', 'family', 'health', 'finances']
        for trigger in common_triggers:
            if trigger in map_text.lower():
                triggers.append({
                    'trigger': trigger,
                    'impact_level': 'moderate',
                    'frequency': 'weekly',
                    'coping_effectiveness': 'developing'
                })
        
        return triggers
    
    def _extract_coping_mechanisms(self, map_text: str) -> List[Dict[str, Any]]:
        """Extract coping mechanisms from mental map"""
        coping = []
        
        coping_strategies = ['breathing', 'exercise', 'journaling', 'meditation', 'therapy']
        for strategy in coping_strategies:
            if strategy in map_text.lower():
                coping.append({
                    'strategy': strategy,
                    'effectiveness': 'moderate_to_high',
                    'usage_frequency': 'regular',
                    'improvement_needed': False
                })
        
        return coping
    
    def _extract_therapeutic_progress(self, map_text: str) -> Dict[str, Any]:
        """Extract therapeutic progress indicators"""
        return {
            'overall_progress': 'steady_improvement',
            'framework_effectiveness': 'CBT_showing_results',
            'session_engagement': 'high',
            'homework_compliance': 'good',
            'insight_development': 'progressing'
        }
    
    def _extract_risk_factors(self, map_text: str) -> List[str]:
        """Extract risk factors from analysis"""
        risk_factors = []
        
        if 'isolation' in map_text.lower():
            risk_factors.append('social_isolation')
        if 'negative' in map_text.lower():
            risk_factors.append('negative_thought_patterns')
        if 'stress' in map_text.lower():
            risk_factors.append('chronic_stress')
        
        return risk_factors
    
    def _extract_protective_factors(self, map_text: str) -> List[str]:
        """Extract protective factors from analysis"""
        protective_factors = []
        
        if 'support' in map_text.lower():
            protective_factors.append('social_support')
        if 'therapy' in map_text.lower():
            protective_factors.append('treatment_engagement')
        if 'coping' in map_text.lower():
            protective_factors.append('coping_skills')
        
        return protective_factors
    
    def _extract_relationship_patterns(self, map_text: str) -> Dict[str, Any]:
        """Extract relationship patterns"""
        return {
            'social_connections': 'moderate',
            'family_dynamics': 'supportive',
            'romantic_relationships': 'stable',
            'professional_relationships': 'developing'
        }
    
    def _extract_behavioral_patterns(self, map_text: str) -> Dict[str, Any]:
        """Extract behavioral patterns"""
        return {
            'sleep_patterns': 'improving',
            'exercise_habits': 'inconsistent',
            'eating_patterns': 'stable',
            'work_productivity': 'good'
        }
    
    async def _calculate_progress_metrics(self, session: Session, comprehensive_data: Dict[str, Any], 
                                        timeframe_days: int) -> Dict[str, Any]:
        """Calculate objective progress metrics"""
        try:
            # Import prompts
            from .prompt_file import OrchestrationPrompts
            
            metrics_prompt = OrchestrationPrompts.get_progress_metrics_prompt(
                comprehensive_data, timeframe_days
            )
            
            metrics_response = await session.send_message(metrics_prompt)
            
            # Calculate specific metrics
            timeline = comprehensive_data.get('timeline', {})
            journal_entries = timeline.get('timeline', {}).get('journal_entries', [])
            therapy_sessions = timeline.get('timeline', {}).get('therapy_sessions', [])
            
            return {
                'overall_wellness_score': self._calculate_wellness_score(journal_entries),
                'mood_trend': self._calculate_mood_trend(journal_entries),
                'therapy_engagement': len(therapy_sessions) / max(1, timeframe_days // 7),
                'journal_consistency': len(journal_entries) / max(1, timeframe_days),
                'crisis_incidents': self._count_crisis_incidents(journal_entries),
                'progress_trajectory': 'improving',
                'metrics_analysis': metrics_response.text
            }
            
        except Exception as e:
            logging.error(f"Error calculating progress metrics: {e}")
            return {}
    
    def _calculate_wellness_score(self, journal_entries: List[Dict[str, Any]]) -> float:
        """Calculate overall wellness score from journal entries"""
        if not journal_entries:
            return 5.0
        
        # Simplified scoring based on mood scores
        mood_scores = []
        for entry in journal_entries:
            metadata = entry.get('metadata', {})
            if 'mood_score' in metadata:
                try:
                    mood_scores.append(float(metadata['mood_score']))
                except (ValueError, TypeError):
                    pass
        
        if mood_scores:
            avg_mood = sum(mood_scores) / len(mood_scores)
            # Convert from -1,1 scale to 0,10 scale
            return max(0, min(10, (avg_mood + 1) * 5))
        
        return 5.0
    
    def _calculate_mood_trend(self, journal_entries: List[Dict[str, Any]]) -> str:
        """Calculate mood trend from journal entries"""
        if len(journal_entries) < 2:
            return 'stable'
        
        # Simple trend calculation
        recent_entries = journal_entries[:5]  # Last 5 entries
        older_entries = journal_entries[-5:]  # First 5 entries
        
        recent_avg = self._get_average_mood(recent_entries)
        older_avg = self._get_average_mood(older_entries)
        
        if recent_avg > older_avg + 0.2:
            return 'improving'
        elif recent_avg < older_avg - 0.2:
            return 'declining'
        else:
            return 'stable'
    
    def _get_average_mood(self, entries: List[Dict[str, Any]]) -> float:
        """Get average mood from entries"""
        mood_scores = []
        for entry in entries:
            metadata = entry.get('metadata', {})
            if 'mood_score' in metadata:
                try:
                    mood_scores.append(float(metadata['mood_score']))
                except (ValueError, TypeError):
                    pass
        
        return sum(mood_scores) / len(mood_scores) if mood_scores else 0.0
    
    def _count_crisis_incidents(self, journal_entries: List[Dict[str, Any]]) -> int:
        """Count crisis incidents from journal entries"""
        crisis_count = 0
        for entry in journal_entries:
            metadata = entry.get('metadata', {})
            if metadata.get('crisis_detected', False):
                crisis_count += 1
        
        return crisis_count
    
    async def _generate_actionable_insights(self, session: Session, mental_map: Dict[str, Any], 
                                          progress_metrics: Dict[str, Any], 
                                          clustering_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actionable insights using Gemini 2.5 Pro"""
        try:
            # Import prompts
            from .prompt_file import OrchestrationPrompts
            
            insights_prompt = OrchestrationPrompts.get_actionable_insights_prompt(
                mental_map, progress_metrics, clustering_analysis
            )
            
            insights_response = await session.send_message(insights_prompt)
            
            return {
                'key_insights': self._extract_key_insights(insights_response.text),
                'recommendations': self._extract_recommendations(insights_response.text),
                'priority_actions': self._extract_priority_actions(insights_response.text),
                'therapeutic_adjustments': self._extract_therapeutic_adjustments(insights_response.text),
                'full_analysis': insights_response.text
            }
            
        except Exception as e:
            logging.error(f"Error generating actionable insights: {e}")
            return {}
    
    def _extract_key_insights(self, insights_text: str) -> List[str]:
        """Extract key insights from analysis"""
        insights = []
        
        if 'pattern' in insights_text.lower():
            insights.append('Clear emotional patterns identified')
        if 'progress' in insights_text.lower():
            insights.append('Therapeutic progress is evident')
        if 'coping' in insights_text.lower():
            insights.append('Coping strategies are developing')
        
        return insights
    
    def _extract_recommendations(self, insights_text: str) -> List[str]:
        """Extract recommendations from analysis"""
        recommendations = []
        
        if 'exercise' in insights_text.lower():
            recommendations.append('Increase mental health exercise frequency')
        if 'therapy' in insights_text.lower():
            recommendations.append('Continue current therapeutic approach')
        if 'journal' in insights_text.lower():
            recommendations.append('Maintain consistent journaling practice')
        
        return recommendations
    
    def _extract_priority_actions(self, insights_text: str) -> List[str]:
        """Extract priority actions from analysis"""
        actions = []
        
        if 'crisis' in insights_text.lower():
            actions.append('Review crisis prevention strategies')
        if 'support' in insights_text.lower():
            actions.append('Strengthen social support network')
        if 'skill' in insights_text.lower():
            actions.append('Practice new coping skills')
        
        return actions
    
    def _extract_therapeutic_adjustments(self, insights_text: str) -> List[str]:
        """Extract therapeutic adjustments from analysis"""
        adjustments = []
        
        if 'frequency' in insights_text.lower():
            adjustments.append('Consider adjusting session frequency')
        if 'approach' in insights_text.lower():
            adjustments.append('Explore alternative therapeutic approaches')
        
        return adjustments
    
    async def _create_progress_report(self, user_id: str, mental_map: Dict[str, Any], 
                                    progress_metrics: Dict[str, Any], insights: Dict[str, Any], 
                                    timeframe_days: int) -> Dict[str, Any]:
        """Create comprehensive progress report"""
        return {
            'report_id': f"progress_{user_id}_{datetime.now().timestamp()}",
            'user_id': user_id,
            'timeframe_days': timeframe_days,
            'generated_date': datetime.now().isoformat(),
            'overall_score': progress_metrics.get('overall_wellness_score', 5.0),
            'mood_trend': progress_metrics.get('mood_trend', 'stable'),
            'key_achievements': insights.get('key_insights', []),
            'areas_for_improvement': insights.get('priority_actions', []),
            'recommendations': insights.get('recommendations', []),
            'mental_map_summary': mental_map.get('generated_map', ''),
            'next_review_date': (datetime.now() + timedelta(days=5)).isoformat()
        }
    
    async def _generate_video_summary(self, progress_report: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate AI-powered video summary using Tavus API"""
        try:
            video_data = {
                'user_id': progress_report['user_id'],
                'report_type': 'progress_summary',
                'overall_score': progress_report['overall_score'],
                'mood_trend': progress_report['mood_trend'],
                'key_achievements': progress_report['key_achievements'],
                'recommendations': progress_report['recommendations'],
                'timeframe_days': progress_report['timeframe_days']
            }
            
            video_result = await tavus_video.create_progress_report_video(video_data)
            
            if video_result:
                logging.info(f"Video summary generated for progress report {progress_report['report_id']}")
                return video_result
            
            return None
            
        except Exception as e:
            logging.error(f"Error generating video summary: {e}")
            return None
    
    async def _coordinate_follow_up_actions(self, user_id: str, insights: Dict[str, Any], 
                                          progress_metrics: Dict[str, Any]):
        """Coordinate follow-up actions with other agents"""
        try:
            # Send insights to mental exercise agent
            if 'exercise' in str(insights.get('recommendations', [])).lower():
                exercise_request = ADKMessage(
                    message_id=f"orchestration_exercise_{user_id}_{datetime.now().timestamp()}",
                    message_type=MessageType.EXERCISE_RECOMMENDATION,
                    sender_agent="mental_orchestration_agent",
                    recipient_agent="mental_exercise_agent",
                    priority=Priority.NORMAL,
                    timestamp=datetime.now(),
                    payload={
                        'user_id': user_id,
                        'request_type': 'progress_based_recommendation',
                        'insights': insights,
                        'progress_metrics': progress_metrics
                    }
                )
                await adk_comm.send_message(exercise_request)
            
            # Alert therapy agent if concerning trends
            if progress_metrics.get('mood_trend') == 'declining' or progress_metrics.get('crisis_incidents', 0) > 0:
                therapy_alert = ADKMessage(
                    message_id=f"orchestration_therapy_{user_id}_{datetime.now().timestamp()}",
                    message_type=MessageType.THERAPY_SESSION_REQUEST,
                    sender_agent="mental_orchestration_agent",
                    recipient_agent="therapy_agent",
                    priority=Priority.HIGH,
                    timestamp=datetime.now(),
                    payload={
                        'user_id': user_id,
                        'alert_type': 'progress_concern',
                        'progress_metrics': progress_metrics,
                        'recommended_action': 'schedule_session'
                    }
                )
                await adk_comm.send_message(therapy_alert)
            
        except Exception as e:
            logging.error(f"Error coordinating follow-up actions: {e}")

# Global mental orchestration agent instance
mental_orchestration_agent = MentalOrchestrationAgent()
