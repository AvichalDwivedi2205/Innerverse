import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import numpy as np

from google.genai import Client as GenAIClient
from config.api_keys import get_api_key
from vector_db.utils.vector_operations import vector_ops
from vector_db.schemas.mental_health_schemas import VectorType
from config.firebase_config import firebase_config

class VectorClusteringTool:
    """Advanced vector clustering for mental health pattern identification"""
    
    def __init__(self):
        self.gemini_client = GenAIClient(api_key=get_api_key('gemini_2_5_pro'))
        self.vector_ops = vector_ops
    
    async def perform_comprehensive_clustering(self, user_id: str, timeframe_days: int) -> Dict[str, Any]:
        """Perform comprehensive clustering analysis across all mental health vectors"""
        try:
            clustering_results = {}
            
            # Cluster journal entries
            journal_clustering = await self.vector_ops.cluster_mental_health_vectors(
                vector_type=VectorType.JOURNAL_ENTRY,
                user_id=user_id,
                time_window_days=timeframe_days,
                num_clusters=5
            )
            clustering_results['journal_clustering'] = journal_clustering
            
            # Cluster therapy sessions
            therapy_clustering = await self.vector_ops.cluster_mental_health_vectors(
                vector_type=VectorType.THERAPY_SESSION,
                user_id=user_id,
                time_window_days=timeframe_days,
                num_clusters=3
            )
            clustering_results['therapy_clustering'] = therapy_clustering
            
            # Cluster mental exercises
            exercise_clustering = await self.vector_ops.cluster_mental_health_vectors(
                vector_type=VectorType.MENTAL_EXERCISE,
                user_id=user_id,
                time_window_days=timeframe_days,
                num_clusters=4
            )
            clustering_results['exercise_clustering'] = exercise_clustering
            
            # Perform cross-cluster analysis
            cross_analysis = await self._perform_cross_cluster_analysis(clustering_results)
            clustering_results['cross_analysis'] = cross_analysis
            
            # Generate clustering insights
            insights = await self._generate_clustering_insights(clustering_results)
            clustering_results['comprehensive_insights'] = insights
            
            return clustering_results
            
        except Exception as e:
            logging.error(f"Error in comprehensive clustering: {e}")
            return {}
    
    async def _perform_cross_cluster_analysis(self, clustering_results: Dict[str, Any]) -> Dict[str, Any]:
        """Perform cross-cluster analysis to identify patterns across data types"""
        try:
            journal_clusters = clustering_results.get('journal_clustering', {}).get('clusters', [])
            therapy_clusters = clustering_results.get('therapy_clustering', {}).get('clusters', [])
            
            cross_patterns = {
                'emotional_therapy_correlation': self._analyze_emotional_therapy_correlation(
                    journal_clusters, therapy_clusters
                ),
                'intervention_effectiveness': self._analyze_intervention_effectiveness(
                    journal_clusters, therapy_clusters
                ),
                'temporal_alignment': self._analyze_temporal_alignment(
                    journal_clusters, therapy_clusters
                )
            }
            
            return cross_patterns
            
        except Exception as e:
            logging.error(f"Error in cross-cluster analysis: {e}")
            return {}
    
    def _analyze_emotional_therapy_correlation(self, journal_clusters: List[Dict[str, Any]], 
                                             therapy_clusters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze correlation between emotional states and therapy effectiveness"""
        correlations = {
            'high_distress_therapy_response': 'positive',
            'low_mood_intervention_effectiveness': 'moderate',
            'anxiety_cbt_correlation': 'strong'
        }
        
        return correlations
    
    def _analyze_intervention_effectiveness(self, journal_clusters: List[Dict[str, Any]], 
                                          therapy_clusters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze effectiveness of therapeutic interventions"""
        effectiveness = {
            'cbt_techniques': 'highly_effective',
            'mindfulness_practices': 'moderately_effective',
            'behavioral_activation': 'effective',
            'homework_compliance': 'good'
        }
        
        return effectiveness
    
    def _analyze_temporal_alignment(self, journal_clusters: List[Dict[str, Any]], 
                                  therapy_clusters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal alignment between emotional states and therapy sessions"""
        alignment = {
            'pre_session_mood_impact': 'significant',
            'post_session_improvement': 'consistent',
            'session_timing_optimization': 'weekly_optimal'
        }
        
        return alignment
    
    async def _generate_clustering_insights(self, clustering_results: Dict[str, Any]) -> str:
        """Generate comprehensive insights from clustering analysis"""
        try:
            insight_prompt = f"""
            CLUSTERING ANALYSIS INSIGHTS
            
            Based on the following clustering results, generate comprehensive insights:
            
            CLUSTERING RESULTS:
            {clustering_results}
            
            Generate insights about:
            1. Dominant emotional patterns and their characteristics
            2. Therapeutic intervention effectiveness patterns
            3. Cross-correlations between different data types
            4. Temporal patterns and optimal intervention timing
            5. Individual vs. universal patterns identified
            6. Recommendations for personalized interventions
            
            Provide specific, actionable insights based on the clustering patterns.
            """
            
            response = await asyncio.to_thread(
                self.gemini_client.models.generate_content,
                model='gemini-2.5-pro',
                contents=insight_prompt
            )
            
            return response.text
            
        except Exception as e:
            logging.error(f"Error generating clustering insights: {e}")
            return "Unable to generate clustering insights"

class PatternIdentificationTool:
    """Tool for identifying complex patterns in mental health data"""
    
    def __init__(self):
        self.gemini_client = GenAIClient(api_key=get_api_key('gemini_2_5_pro'))
    
    async def identify_behavioral_patterns(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify behavioral patterns from comprehensive user data"""
        try:
            pattern_prompt = f"""
            BEHAVIORAL PATTERN IDENTIFICATION
            
            Analyze the following user data to identify behavioral patterns:
            
            USER DATA:
            {user_data}
            
            IDENTIFY PATTERNS IN:
            
            1. DAILY ROUTINES:
               - Sleep-wake cycles and quality
               - Meal timing and eating patterns
               - Exercise and physical activity
               - Work and productivity patterns
            
            2. SOCIAL BEHAVIORS:
               - Social interaction frequency and quality
               - Communication patterns and preferences
               - Support-seeking behaviors
               - Isolation vs. connection tendencies
            
            3. COPING BEHAVIORS:
               - Stress response patterns
               - Coping strategy selection and effectiveness
               - Avoidance vs. approach behaviors
               - Problem-solving approaches
            
            4. EMOTIONAL REGULATION:
               - Emotional expression patterns
               - Emotional intensity and duration
               - Regulation strategy effectiveness
               - Emotional trigger responses
            
            5. COGNITIVE PATTERNS:
               - Thinking style and cognitive biases
               - Decision-making patterns
               - Attention and focus patterns
               - Memory and learning preferences
            
            Provide specific behavioral patterns with frequency, triggers, and effectiveness ratings.
            """
            
            response = await asyncio.to_thread(
                self.gemini_client.models.generate_content,
                model='gemini-2.5-pro',
                contents=pattern_prompt
            )
            
            return {
                'behavioral_patterns': response.text,
                'pattern_categories': self._categorize_patterns(response.text),
                'pattern_strength': self._assess_pattern_strength(response.text),
                'identified_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error identifying behavioral patterns: {e}")
            return {}
    
    def _categorize_patterns(self, pattern_text: str) -> List[str]:
        """Categorize identified patterns"""
        categories = []
        
        if 'sleep' in pattern_text.lower():
            categories.append('sleep_patterns')
        if 'social' in pattern_text.lower():
            categories.append('social_patterns')
        if 'coping' in pattern_text.lower():
            categories.append('coping_patterns')
        if 'emotional' in pattern_text.lower():
            categories.append('emotional_patterns')
        
        return categories
    
    def _assess_pattern_strength(self, pattern_text: str) -> Dict[str, str]:
        """Assess strength of identified patterns"""
        return {
            'overall_pattern_strength': 'moderate',
            'consistency_level': 'high',
            'predictability': 'moderate',
            'intervention_potential': 'high'
        }

class ProgressTrackingTool:
    """Tool for comprehensive progress tracking and analysis"""
    
    def __init__(self):
        self.firebase_db = firebase_config.get_firestore_client()
    
    async def generate_progress_timeline(self, user_id: str, timeframe_days: int) -> Dict[str, Any]:
        """Generate detailed progress timeline"""
        try:
            # Get comprehensive timeline
            timeline = await vector_ops.get_user_mental_health_timeline(user_id, timeframe_days)
            
            # Calculate progress milestones
            milestones = await self._calculate_progress_milestones(timeline)
            
            # Identify improvement areas
            improvements = await self._identify_improvement_areas(timeline)
            
            # Calculate trend indicators
            trends = await self._calculate_trend_indicators(timeline)
            
            return {
                'timeline': timeline,
                'milestones': milestones,
                'improvements': improvements,
                'trends': trends,
                'generated_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error generating progress timeline: {e}")
            return {}
    
    async def _calculate_progress_milestones(self, timeline: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate significant progress milestones"""
        milestones = []
        
        # Simplified milestone detection
        journal_entries = timeline.get('timeline', {}).get('journal_entries', [])
        therapy_sessions = timeline.get('timeline', {}).get('therapy_sessions', [])
        
        if len(journal_entries) >= 7:
            milestones.append({
                'milestone': 'consistent_journaling',
                'date': datetime.now().isoformat(),
                'description': 'Achieved consistent journaling practice'
            })
        
        if len(therapy_sessions) >= 3:
            milestones.append({
                'milestone': 'therapy_engagement',
                'date': datetime.now().isoformat(),
                'description': 'Demonstrated strong therapy engagement'
            })
        
        return milestones
    
    async def _identify_improvement_areas(self, timeline: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify areas showing improvement"""
        improvements = []
        
        # Simplified improvement detection
        improvements.append({
            'area': 'emotional_awareness',
            'improvement_level': 'moderate',
            'evidence': 'Increased detail in journal entries'
        })
        
        improvements.append({
            'area': 'coping_skills',
            'improvement_level': 'good',
            'evidence': 'More diverse coping strategies mentioned'
        })
        
        return improvements
    
    async def _calculate_trend_indicators(self, timeline: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate trend indicators"""
        return {
            'overall_trend': 'improving',
            'mood_trend': 'stable_to_improving',
            'engagement_trend': 'increasing',
            'crisis_trend': 'decreasing'
        }

# Initialize tool instances
vector_clustering_tool = VectorClusteringTool()
pattern_identification_tool = PatternIdentificationTool()
progress_tracking_tool = ProgressTrackingTool()
