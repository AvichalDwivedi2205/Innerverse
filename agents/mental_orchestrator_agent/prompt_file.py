from typing import Dict, Any
from datetime import datetime

class OrchestrationPrompts:
    """Prompts for mental health orchestration and comprehensive analysis"""
    
    @staticmethod
    def get_mental_health_map_prompt(comprehensive_data: Dict[str, Any], 
                                   clustering_analysis: Dict[str, Any]) -> str:
        """Generate comprehensive mental health map prompt"""
        
        timeline = comprehensive_data.get('timeline', {})
        journal_clustering = comprehensive_data.get('journal_clustering', {})
        therapy_clustering = comprehensive_data.get('therapy_clustering', {})
        user_profile = comprehensive_data.get('user_profile', {})
        
        prompt = f"""
        COMPREHENSIVE MENTAL HEALTH MAP GENERATION
        
        Create a detailed mental health map based on the following comprehensive data analysis:
        
        USER PROFILE:
        - Mental Health Conditions: {user_profile.get('mental_health_conditions', [])}
        - Current Medications: {user_profile.get('current_medications', [])}
        - Therapeutic Goals: {user_profile.get('therapeutic_goals', [])}
        - Risk Level: {user_profile.get('risk_level', 'unknown')}
        
        TIMELINE DATA:
        - Total Data Points: {comprehensive_data.get('data_points', 0)}
        - Therapy Sessions: {comprehensive_data.get('therapy_sessions', 0)}
        - Timeline Summary: {timeline.get('summary', 'No timeline data')}
        
        JOURNAL CLUSTERING ANALYSIS:
        - Clusters Identified: {len(journal_clustering.get('clusters', []))}
        - Insights: {journal_clustering.get('insights', 'No journal insights')}
        
        THERAPY CLUSTERING ANALYSIS:
        - Clusters Identified: {len(therapy_clustering.get('clusters', []))}
        - Insights: {therapy_clustering.get('insights', 'No therapy insights')}
        
        CLUSTERING PATTERNS:
        {clustering_analysis}
        
        MENTAL HEALTH MAP REQUIREMENTS:
        
        1. EMOTIONAL PATTERNS:
           - Identify dominant emotional states and their frequency
           - Map emotional cycles and seasonal patterns
           - Analyze emotional intensity variations
           - Identify emotional triggers and their impact
        
        2. TRIGGER ANALYSIS:
           - Primary triggers (work, relationships, health, etc.)
           - Trigger intensity and frequency patterns
           - Trigger-response patterns and coping effectiveness
           - Environmental and situational trigger factors
        
        3. COPING MECHANISMS:
           - Effective coping strategies currently used
           - Underdeveloped coping areas needing attention
           - Coping strategy effectiveness ratings
           - Adaptive vs. maladaptive coping patterns
        
        4. THERAPEUTIC PROGRESS:
           - Progress in therapy sessions and frameworks
           - Skill development and insight acquisition
           - Behavioral and cognitive changes observed
           - Treatment engagement and compliance patterns
        
        5. RISK AND PROTECTIVE FACTORS:
           - Current risk factors for mental health decline
           - Protective factors supporting mental wellness
           - Resilience indicators and stress tolerance
           - Social support and relationship quality
        
        6. BEHAVIORAL PATTERNS:
           - Sleep, exercise, and self-care patterns
           - Social interaction and isolation tendencies
           - Work/life balance and productivity patterns
           - Substance use or avoidance behaviors
        
        7. RELATIONSHIP DYNAMICS:
           - Family, romantic, and friendship patterns
           - Professional and social relationship quality
           - Communication styles and conflict resolution
           - Support-seeking and help-accepting behaviors
        
        8. COGNITIVE PATTERNS:
           - Thought patterns and cognitive distortions
           - Problem-solving and decision-making styles
           - Self-talk and internal narrative themes
           - Learning and adaptation capabilities
        
        Generate a comprehensive, objective mental health map that provides actionable insights for continued care and progress. Focus on patterns, trends, and connections between different aspects of mental health.
        """
        
        return prompt
    
    @staticmethod
    def get_progress_metrics_prompt(comprehensive_data: Dict[str, Any], timeframe_days: int) -> str:
        """Generate progress metrics analysis prompt"""
        
        prompt = f"""
        OBJECTIVE PROGRESS METRICS CALCULATION
        
        Analyze the following data to calculate objective progress metrics over {timeframe_days} days:
        
        COMPREHENSIVE DATA:
        {comprehensive_data}
        
        CALCULATE THE FOLLOWING METRICS:
        
        1. OVERALL WELLNESS SCORE (0-10):
           - Aggregate mood scores from journal entries
           - Weight recent entries more heavily
           - Consider therapy session progress
           - Factor in crisis incidents (negative impact)
           - Include coping skill development
        
        2. MOOD TREND ANALYSIS:
           - Compare recent vs. earlier mood patterns
           - Identify upward, downward, or stable trends
           - Calculate rate of change and consistency
           - Note any significant mood fluctuations
        
        3. THERAPY ENGAGEMENT SCORE:
           - Session attendance and participation
           - Homework completion rates
           - Insight development and skill practice
           - Therapeutic alliance quality
        
        4. JOURNAL CONSISTENCY SCORE:
           - Frequency of journal entries
           - Quality and depth of emotional expression
           - Consistency over time period
           - Emotional awareness development
        
        5. CRISIS PREVENTION EFFECTIVENESS:
           - Number of crisis incidents
           - Crisis resolution time and methods
           - Prevention strategy effectiveness
           - Early warning sign recognition
        
        6. COPING SKILL DEVELOPMENT:
           - New coping strategies learned
           - Effectiveness of existing strategies
           - Frequency of strategy use
           - Adaptation and flexibility in coping
        
        7. SOCIAL CONNECTION QUALITY:
           - Support system engagement
           - Relationship satisfaction indicators
           - Social activity participation
           - Communication and boundary setting
        
        8. BEHAVIORAL ACTIVATION LEVEL:
           - Engagement in meaningful activities
           - Goal-directed behavior patterns
           - Energy and motivation levels
           - Daily routine consistency
        
        Provide specific numerical scores and detailed explanations for each metric. Focus on objective, measurable indicators of progress.
        """
        
        return prompt
    
    @staticmethod
    def get_actionable_insights_prompt(mental_map: Dict[str, Any], progress_metrics: Dict[str, Any], 
                                     clustering_analysis: Dict[str, Any]) -> str:
        """Generate actionable insights prompt"""
        
        prompt = f"""
        ACTIONABLE INSIGHTS GENERATION
        
        Based on the comprehensive analysis, generate specific, actionable insights:
        
        MENTAL HEALTH MAP:
        {mental_map}
        
        PROGRESS METRICS:
        {progress_metrics}
        
        CLUSTERING ANALYSIS:
        {clustering_analysis}
        
        GENERATE ACTIONABLE INSIGHTS IN THESE AREAS:
        
        1. KEY INSIGHTS:
           - Most significant patterns identified
           - Breakthrough moments and progress indicators
           - Areas of concern requiring attention
           - Unexpected findings or correlations
        
        2. IMMEDIATE RECOMMENDATIONS:
           - Actions to take in the next week
           - Skills to practice or develop
           - Behavioral changes to implement
           - Support resources to engage
        
        3. PRIORITY INTERVENTIONS:
           - Most critical areas needing intervention
           - Therapeutic focus areas for next sessions
           - Crisis prevention strategies to strengthen
           - Coping skills requiring development
        
        4. THERAPEUTIC ADJUSTMENTS:
           - Modifications to current therapeutic approach
           - Framework changes or additions needed
           - Session frequency or format adjustments
           - Homework and practice modifications
        
        5. LONG-TERM STRATEGIES:
           - Goals for next 30-90 days
           - Skill development trajectories
           - Relationship and social goals
           - Lifestyle and behavioral targets
        
        6. MONITORING RECOMMENDATIONS:
           - Metrics to track closely
           - Warning signs to watch for
           - Progress indicators to celebrate
           - Assessment timing and methods
        
        7. RESOURCE CONNECTIONS:
           - Additional support services needed
           - Educational resources to explore
           - Community connections to make
           - Professional referrals to consider
        
        8. PERSONALIZATION FACTORS:
           - Individual strengths to leverage
           - Unique challenges to address
           - Preferred learning and coping styles
           - Cultural and personal considerations
        
        Provide specific, actionable recommendations that can be implemented immediately and tracked over time. Focus on evidence-based interventions tailored to the individual's unique patterns and needs.
        """
        
        return prompt
    
    @staticmethod
    def get_trend_analysis_prompt(historical_data: Dict[str, Any]) -> str:
        """Generate trend analysis prompt for longitudinal data"""
        
        prompt = f"""
        LONGITUDINAL TREND ANALYSIS
        
        Analyze the following historical mental health data for trends and patterns:
        
        HISTORICAL DATA:
        {historical_data}
        
        TREND ANALYSIS REQUIREMENTS:
        
        1. TEMPORAL PATTERNS:
           - Daily, weekly, and monthly cycles
           - Seasonal affective patterns
           - Anniversary reactions and triggers
           - Time-of-day mood variations
        
        2. PROGRESSION ANALYSIS:
           - Overall trajectory of mental health
           - Rate of change and improvement
           - Setback patterns and recovery
           - Skill development progression
        
        3. INTERVENTION EFFECTIVENESS:
           - Impact of therapeutic interventions
           - Medication changes and effects
           - Lifestyle modification outcomes
           - Coping strategy effectiveness over time
        
        4. PREDICTIVE INDICATORS:
           - Early warning signs of decline
           - Factors predicting good days
           - Vulnerability periods identification
           - Resilience factor patterns
        
        5. CORRELATION ANALYSIS:
           - Relationships between different variables
           - Cause-and-effect patterns
           - Environmental factor impacts
           - Social and relational influences
        
        Provide detailed trend analysis with specific recommendations for future monitoring and intervention.
        """
        
        return prompt

# Global orchestration prompts instance
orchestration_prompts = OrchestrationPrompts()
