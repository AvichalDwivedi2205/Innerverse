from typing import Dict, Any, List

class SchedulingPrompts:
    """Flexible, encouraging scheduling prompts for wellness activities"""
    
    @staticmethod
    def get_optimal_scheduling_prompt(user_context: Dict[str, Any], preferences: Dict[str, Any],
                                    activities: List[str]) -> str:
        """Generate optimal scheduling prompt"""
        
        prompt = f"""
        INTELLIGENT WELLNESS SCHEDULING
        
        Create an optimal weekly schedule that balances all wellness activities while respecting user preferences and lifestyle:
        
        USER CONTEXT:
        - Timezone: {user_context.get('timezone', 'UTC')}
        - Preferred Times: {user_context.get('preferred_times', {})}
        - Existing Events: {len(user_context.get('existing_events', []))} events scheduled
        - Schedule History: {len(user_context.get('schedule_history', []))} previous schedules
        - Notification Preferences: {user_context.get('notification_preferences', {})}
        
        USER PREFERENCES:
        {preferences}
        
        ACTIVITIES TO SCHEDULE:
        {', '.join(activities)}
        
        SCHEDULING PRINCIPLES:
        
        1. PRIORITY-BASED SCHEDULING:
           - Critical: Therapy sessions (fixed times, highest priority)
           - High: Journaling, mental exercises (consistent daily times)
           - Medium: Workouts, meal planning (flexible within preferred windows)
           - Low: Progress reviews, wellness check-ins (weekend flexibility)
        
        2. LIFESTYLE INTEGRATION:
           - Respect work schedules and existing commitments
           - Consider energy levels throughout the day
           - Account for family and social obligations
           - Build in buffer time between activities
        
        3. CONSISTENCY BUILDING:
           - Schedule similar activities at consistent times
           - Create sustainable daily and weekly routines
           - Allow for gradual habit formation
           - Avoid overwhelming schedules
        
        4. FLEXIBILITY WINDOWS:
           - Identify times when activities can be rescheduled
           - Provide alternative time slots for each activity
           - Build in "catch-up" opportunities
           - Allow for spontaneous wellness activities
        
        5. ENERGY AND MOTIVATION OPTIMIZATION:
           - Schedule high-focus activities during peak energy times
           - Place physical activities when energy is appropriate
           - Consider motivation patterns and preferences
           - Balance challenging and enjoyable activities
        
        6. REALISTIC TIME ALLOCATION:
           - Journaling: 10-15 minutes daily
           - Mental exercises: 5-20 minutes as needed
           - Workouts: 20-60 minutes, 3-5 times per week
           - Therapy sessions: 50 minutes, weekly or bi-weekly
           - Meal planning: 30 minutes weekly
           - Progress reviews: 15 minutes every 5 days
        
        7. ACCOMMODATION STRATEGIES:
           - Provide multiple options for each time slot
           - Consider seasonal and weather factors
           - Account for travel and schedule changes
           - Build in recovery and rest periods
        
        GENERATE A WEEKLY SCHEDULE THAT:
        - Specifies exact days and times for each activity
        - Explains the rationale behind each scheduling decision
        - Identifies flexibility windows for rescheduling
        - Provides motivation for maintaining consistency
        - Suggests strategies for overcoming common obstacles
        
        Focus on creating a schedule that feels supportive and achievable rather than rigid and demanding.
        """
        
        return prompt
    
    @staticmethod
    def get_progress_report_prompt(progress_data: Dict[str, Any]) -> str:
        """Generate progress report prompt"""
        
        prompt = f"""
        5-DAY WELLNESS PROGRESS REPORT
        
        Generate an encouraging, comprehensive progress report based on the following data:
        
        PROGRESS METRICS:
        - Overall Wellness Score: {progress_data.get('overall_wellness_score', 0)}/10
        - Mood Trend: {progress_data.get('mood_trend', 'stable')}
        - Therapy Engagement: {progress_data.get('therapy_engagement', 0)*100:.0f}%
        - Journal Consistency: {progress_data.get('journal_consistency', 0)*100:.0f}%
        - Exercise Completion: {progress_data.get('exercise_completion', 0)*100:.0f}%
        - Key Achievements: {progress_data.get('key_achievements', [])}
        - Areas for Improvement: {progress_data.get('areas_for_improvement', [])}
        
        REPORT REQUIREMENTS:
        
        1. ENCOURAGING OPENING:
           - Start with genuine recognition of effort and progress
           - Acknowledge the courage it takes to prioritize mental health
           - Highlight positive trends and improvements
        
        2. ACHIEVEMENT CELEBRATION:
           - Specifically celebrate each key achievement
           - Explain why each achievement matters for overall wellness
           - Connect achievements to long-term wellness goals
           - Use specific metrics to show concrete progress
        
        3. PROGRESS ANALYSIS:
           - Analyze trends in mood, engagement, and consistency
           - Identify patterns that are working well
           - Recognize efforts even when results are still developing
           - Put progress in context of the wellness journey
        
        4. GENTLE IMPROVEMENT GUIDANCE:
           - Address areas for improvement with compassion
           - Suggest specific, small steps for enhancement
           - Provide motivation for continuing challenging areas
           - Offer alternative approaches if current methods aren't working
        
        5. FORWARD-LOOKING ENCOURAGEMENT:
           - Set realistic expectations for the next 5 days
           - Suggest focus areas that build on current strengths
           - Provide motivation for maintaining momentum
           - Remind user of their resilience and capability
        
        6. PRACTICAL RECOMMENDATIONS:
           - Offer 2-3 specific, actionable recommendations
           - Suggest schedule adjustments if needed
           - Recommend celebrating progress milestones
           - Provide strategies for overcoming identified challenges
        
        7. SUPPORTIVE CLOSING:
           - Reinforce that wellness is a journey, not a destination
           - Acknowledge that progress isn't always linear
           - Express confidence in their continued growth
           - Remind them of available support and resources
        
        TONE GUIDELINES:
        - Warm, encouraging, and genuinely supportive
        - Specific and personalized to their actual progress
        - Balanced between celebration and gentle guidance
        - Professional yet approachable
        - Motivating without being overwhelming
        
        Generate a report that makes the user feel seen, supported, and motivated to continue their wellness journey.
        """
        
        return prompt
    
    @staticmethod
    def get_rescheduling_prompt(activity: str, new_time: str, reason: str) -> str:
        """Generate rescheduling support prompt"""
        
        prompt = f"""
        SUPPORTIVE RESCHEDULING ASSISTANCE
        
        Help the user reschedule their wellness activity with understanding and encouragement:
        
        RESCHEDULING REQUEST:
        - Activity: {activity}
        - New Requested Time: {new_time}
        - Reason: {reason if reason else 'Not specified'}
        
        RESCHEDULING SUPPORT APPROACH:
        
        1. VALIDATE THE REQUEST:
           - Acknowledge that life happens and flexibility is important
           - Validate their reason for needing to reschedule
           - Emphasize that rescheduling shows commitment, not failure
           - Recognize their proactive approach to maintaining wellness
        
        2. PROVIDE REASSURANCE:
           - Remind them that consistency is about long-term patterns, not perfect adherence
           - Acknowledge that adapting schedules is part of sustainable wellness
           - Emphasize that asking for schedule changes shows self-awareness
           - Reinforce that their wellness journey is flexible and personal
        
        3. OFFER PRACTICAL SOLUTIONS:
           - Confirm the new time works with their overall schedule
           - Suggest ways to prepare for the rescheduled activity
           - Provide tips for maintaining momentum despite the change
           - Offer alternative options if the requested time doesn't work
        
        4. MAINTAIN MOTIVATION:
           - Connect the rescheduling to their overall wellness goals
           - Remind them of recent progress and achievements
           - Encourage them to view flexibility as a strength
           - Provide motivation for the upcoming rescheduled activity
        
        5. PREVENT GUILT OR SHAME:
           - Explicitly state that rescheduling is completely normal
           - Avoid any language that could induce guilt
           - Frame the change as responsible self-care
           - Emphasize that perfect schedules don't exist
        
        6. FUTURE PLANNING:
           - Suggest strategies for handling similar situations in the future
           - Offer to build more flexibility into their schedule if needed
           - Provide tips for communicating schedule needs early
           - Encourage ongoing schedule adjustments as life changes
        
        RESPONSE TONE:
        - Understanding and non-judgmental
        - Encouraging and supportive
        - Practical and solution-focused
        - Warm and personally caring
        - Confident in their ability to maintain wellness
        
        Generate a response that makes the user feel supported in their decision and motivated to continue their wellness activities at the new time.
        """
        
        return prompt
    
    @staticmethod
    def get_reminder_message_prompt(activity: str, user_context: Dict[str, Any]) -> str:
        """Generate personalized reminder message prompt"""
        
        prompt = f"""
        MOTIVATIONAL WELLNESS REMINDER
        
        Create an encouraging reminder message for this wellness activity:
        
        ACTIVITY: {activity}
        USER CONTEXT: {user_context}
        
        REMINDER MESSAGE GUIDELINES:
        
        1. POSITIVE MOTIVATION:
           - Focus on benefits and positive outcomes
           - Use encouraging, uplifting language
           - Remind them of their wellness goals
           - Acknowledge their commitment to self-care
        
        2. PERSONAL CONNECTION:
           - Reference their recent progress if available
           - Connect to their specific wellness journey
           - Use warm, personally supportive tone
           - Acknowledge their individual challenges and strengths
        
        3. GENTLE ENCOURAGEMENT:
           - Avoid pressure or guilt-inducing language
           - Provide permission to modify if needed
           - Emphasize that small steps count
           - Remind them that they're worth the investment
        
        4. PRACTICAL SUPPORT:
           - Briefly remind them what the activity involves
           - Suggest how to prepare mentally or physically
           - Provide a quick motivation boost
           - Offer flexibility if circumstances have changed
        
        5. EMPOWERMENT:
           - Remind them of their agency and choice
           - Emphasize their capability and strength
           - Connect the activity to their larger wellness vision
           - Celebrate their commitment to growth
        
        Keep the message brief, warm, and genuinely encouraging. The goal is to motivate participation while respecting their autonomy and current circumstances.
        """
        
        return prompt

# Global scheduling prompts instance
scheduling_prompts = SchedulingPrompts()
