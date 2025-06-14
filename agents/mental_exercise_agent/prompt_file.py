from typing import Dict, Any, List

class ExercisePrompts:
    """Clear therapeutic instruction prompts for mental health exercises"""
    
    @staticmethod
    def get_exercise_selection_prompt(similar_exercises: List[Dict[str, Any]], 
                                    mental_state: Dict[str, Any],
                                    therapeutic_context: Dict[str, Any],
                                    preferred_duration: int) -> str:
        """Generate exercise selection prompt"""
        
        prompt = f"""
        MENTAL HEALTH EXERCISE SELECTION
        
        Select the most appropriate exercise based on the user's current mental state and therapeutic context:
        
        CURRENT MENTAL STATE:
        - Anxiety Level: {mental_state.get('anxiety_level', 0.0)} (0-1 scale)
        - Depression Level: {mental_state.get('depression_level', 0.0)} (0-1 scale)
        - Stress Level: {mental_state.get('stress_level', 0.0)} (0-1 scale)
        - Mood Score: {mental_state.get('mood_score', 0.0)} (-1 to 1 scale)
        - Energy Level: {mental_state.get('energy_level', 0.5)} (0-1 scale)
        
        THERAPEUTIC CONTEXT:
        - Framework: {therapeutic_context.get('framework', 'general')}
        - Session Goals: {therapeutic_context.get('session_goals', [])}
        - Homework Focus: {therapeutic_context.get('homework_focus', [])}
        
        USER PREFERENCES:
        - Preferred Duration: {preferred_duration} minutes
        
        AVAILABLE EXERCISES:
        {chr(10).join(f"• {ex.get('name', 'Unknown')}: {ex.get('description', 'No description')} ({ex.get('duration_minutes', 0)} min)" for ex in similar_exercises)}
        
        SELECTION CRITERIA:
        
        1. MENTAL STATE ALIGNMENT:
           - High anxiety (>0.6): Prioritize mindfulness and breathing exercises
           - High depression (>0.6): Prioritize behavioral activation and mood-lifting exercises
           - High stress (>0.6): Prioritize CBT and cognitive restructuring exercises
           - Low energy (<0.4): Choose shorter, gentler exercises
        
        2. THERAPEUTIC INTEGRATION:
           - Align with current therapeutic framework (CBT, DBT, ACT)
           - Support ongoing therapy goals and homework assignments
           - Build on previously learned skills and techniques
        
        3. PRACTICAL CONSIDERATIONS:
           - Match user's preferred duration (+/- 5 minutes acceptable)
           - Consider user's current capacity and energy level
           - Select exercises appropriate for current emotional state
        
        4. EFFECTIVENESS FACTORS:
           - Choose exercises with proven effectiveness for current symptoms
           - Consider user's previous exercise completion and feedback
           - Balance challenge with achievability
        
        Select the single most appropriate exercise and explain your reasoning. Respond with the exercise ID and a brief explanation.
        """
        
        return prompt
    
    @staticmethod
    def get_exercise_personalization_prompt(exercise: Dict[str, Any], 
                                          mental_state: Dict[str, Any],
                                          user_context: Dict[str, Any]) -> str:
        """Generate exercise personalization prompt"""
        
        prompt = f"""
        EXERCISE PERSONALIZATION
        
        Personalize the following mental health exercise for this specific user:
        
        BASE EXERCISE:
        - Name: {exercise.get('name', 'Unknown Exercise')}
        - Description: {exercise.get('description', 'No description')}
        - Duration: {exercise.get('duration_minutes', 10)} minutes
        - Difficulty: {exercise.get('difficulty', 'beginner')}
        - Category: {exercise.get('category', 'general')}
        
        STANDARD INSTRUCTIONS:
        {chr(10).join(f"{i+1}. {instruction}" for i, instruction in enumerate(exercise.get('instructions', [])))}
        
        THERAPEUTIC RATIONALE:
        {exercise.get('therapeutic_rationale', 'General mental health support')}
        
        USER'S CURRENT MENTAL STATE:
        - Anxiety Level: {mental_state.get('anxiety_level', 0.0)}
        - Depression Level: {mental_state.get('depression_level', 0.0)}
        - Stress Level: {mental_state.get('stress_level', 0.0)}
        - Energy Level: {mental_state.get('energy_level', 0.5)}
        - Mood Score: {mental_state.get('mood_score', 0.0)}
        
        USER CONTEXT:
        - Completed Exercises: {user_context.get('completed_exercises', 0)}
        - Preferred Frameworks: {user_context.get('preferred_frameworks', ['CBT'])}
        - Exercise Preferences: {user_context.get('exercise_preferences', {})}
        - Preferred Duration: {user_context.get('preferred_duration', 10)} minutes
        
        PERSONALIZATION REQUIREMENTS:
        
        1. INSTRUCTION ADAPTATION:
           - Modify language to match user's current emotional state
           - Adjust complexity based on user's experience level
           - Add specific examples relevant to user's situation
           - Include encouraging statements tailored to current mood
        
        2. DURATION ADJUSTMENT:
           - Adapt timing based on user's energy level and preferences
           - Suggest shorter versions if energy is low
           - Offer extension options if user is engaged
        
        3. THERAPEUTIC CUSTOMIZATION:
           - Emphasize aspects most relevant to current mental state
           - Connect exercise to user's ongoing therapeutic goals
           - Reference previous exercises or progress when appropriate
        
        4. MOTIVATIONAL ELEMENTS:
           - Include personalized encouragement based on mood
           - Acknowledge current challenges without overwhelming
           - Highlight benefits specific to user's current needs
           - Provide gentle reminders about self-compassion
        
        5. ACCESSIBILITY CONSIDERATIONS:
           - Adjust for current energy and concentration levels
           - Provide alternatives for different physical positions
           - Offer modifications for varying attention spans
        
        Generate personalized, step-by-step instructions that feel specifically tailored to this user's current state and needs. Use warm, encouraging language that validates their experience while gently guiding them through the exercise.
        """
        
        return prompt
    
    @staticmethod
    def get_cbt_exercise_prompt(user_situation: str, thought_pattern: str) -> str:
        """Generate CBT-specific exercise prompt"""
        
        prompt = f"""
        CBT THOUGHT CHALLENGING EXERCISE
        
        Guide the user through a cognitive restructuring exercise:
        
        USER'S SITUATION: {user_situation}
        IDENTIFIED THOUGHT PATTERN: {thought_pattern}
        
        EXERCISE STRUCTURE:
        
        1. THOUGHT IDENTIFICATION:
           "Let's examine the thought: '{thought_pattern}'"
           "Notice how this thought makes you feel emotionally and physically."
        
        2. EVIDENCE EXAMINATION:
           "What evidence supports this thought?"
           "What evidence challenges or contradicts this thought?"
           "Are there alternative explanations for this situation?"
        
        3. COGNITIVE DISTORTION CHECK:
           "Does this thought involve any of these patterns:
           - All-or-nothing thinking
           - Catastrophizing
           - Mind reading
           - Fortune telling
           - Emotional reasoning"
        
        4. BALANCED THINKING:
           "Based on the evidence, what would be a more balanced, realistic thought?"
           "How does this new thought change how you feel?"
        
        5. ACTION PLANNING:
           "What small action could you take based on this more balanced perspective?"
        
        Provide specific, gentle guidance for each step with examples relevant to their situation.
        """
        
        return prompt
    
    @staticmethod
    def get_mindfulness_exercise_prompt(anxiety_level: float, duration_minutes: int) -> str:
        """Generate mindfulness exercise prompt"""
        
        prompt = f"""
        PERSONALIZED MINDFULNESS EXERCISE
        
        Create a {duration_minutes}-minute mindfulness exercise for someone with anxiety level {anxiety_level}:
        
        ANXIETY LEVEL CONSIDERATIONS:
        - High anxiety (>0.7): Focus on grounding and calming techniques
        - Moderate anxiety (0.4-0.7): Balance awareness with gentle calming
        - Low anxiety (<0.4): Emphasize present-moment awareness and clarity
        
        EXERCISE COMPONENTS:
        
        1. SETTLING IN (1-2 minutes):
           - Comfortable position guidance
           - Initial breath awareness
           - Gentle transition from daily activities
        
        2. MAIN PRACTICE ({duration_minutes-3} minutes):
           - Breath-focused attention or body awareness
           - Gentle guidance for when mind wanders
           - Anxiety-specific modifications if needed
        
        3. CLOSING (1-2 minutes):
           - Gradual transition back to daily awareness
           - Intention setting or gratitude practice
           - Gentle movement preparation
        
        LANGUAGE GUIDELINES:
        - Use calm, soothing tone
        - Provide clear but not rigid instructions
        - Include permission for imperfection
        - Offer gentle redirections for anxious minds
        
        Create specific, step-by-step guidance with appropriate pacing for the anxiety level and duration.
        """
        
        return prompt
    
    @staticmethod
    def get_behavioral_activation_prompt(depression_level: float, energy_level: float) -> str:
        """Generate behavioral activation exercise prompt"""
        
        prompt = f"""
        BEHAVIORAL ACTIVATION EXERCISE
        
        Create a behavioral activation exercise for someone with:
        - Depression Level: {depression_level} (0-1 scale)
        - Energy Level: {energy_level} (0-1 scale)
        
        ENERGY-ADAPTED APPROACH:
        - High energy (>0.7): Include multiple activities and goal-setting
        - Moderate energy (0.4-0.7): Focus on one meaningful activity
        - Low energy (<0.4): Start with very small, achievable actions
        
        EXERCISE STRUCTURE:
        
        1. ACTIVITY IDENTIFICATION:
           - Help identify activities that previously brought pleasure or mastery
           - Consider current energy level and capacity
           - Focus on small, achievable steps
        
        2. PLEASURE vs MASTERY:
           - Pleasure activities: Things that bring joy or satisfaction
           - Mastery activities: Things that provide sense of accomplishment
           - Balance both types based on current needs
        
        3. SCHEDULING AND PLANNING:
           - Choose specific times and days
           - Break large activities into smaller steps
           - Plan for obstacles and solutions
        
        4. COMMITMENT AND FOLLOW-THROUGH:
           - Make realistic commitments
           - Plan accountability measures
           - Prepare for motivation fluctuations
        
        5. REFLECTION AND ADJUSTMENT:
           - Plan to notice mood changes
           - Adjust activities based on what works
           - Celebrate small victories
        
        Provide specific guidance that respects the person's current depression and energy levels while gently encouraging engagement.
        """
        
        return prompt

# Global exercise prompts instance
exercise_prompts = ExercisePrompts()
