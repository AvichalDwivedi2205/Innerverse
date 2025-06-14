from typing import List, Dict, Any

class FitnessPrompts:
    """Safe exercise guidance prompts respecting physical limitations"""
    
    @staticmethod
    def get_workout_plan_generation_prompt(fitness_goals: List[str], fitness_level: str,
                                         physical_limitations: List[str], available_equipment: List[str],
                                         time_per_session: int, sessions_per_week: int) -> str:
        """Generate workout plan creation prompt"""
        
        prompt = f"""
        SAFE WORKOUT PLAN GENERATION
        
        Create a personalized, safe workout plan based on these specifications:
        
        FITNESS GOALS: {', '.join(fitness_goals) if fitness_goals else 'General fitness'}
        FITNESS LEVEL: {fitness_level}
        PHYSICAL LIMITATIONS: {', '.join(physical_limitations) if physical_limitations else 'None reported'}
        AVAILABLE EQUIPMENT: {', '.join(available_equipment) if available_equipment else 'Bodyweight only'}
        TIME PER SESSION: {time_per_session} minutes
        SESSIONS PER WEEK: {sessions_per_week}
        
        SAFETY-FIRST APPROACH:
        
        1. PHYSICAL LIMITATION ACCOMMODATION:
           - NEVER include exercises that could aggravate reported limitations
           - Provide specific modifications for each limitation
           - Suggest alternative exercises that target the same muscle groups safely
           - Include warning signs to stop exercising
        
        2. FITNESS LEVEL APPROPRIATE PROGRESSION:
           - Beginner: Focus on form, basic movements, bodyweight exercises
           - Intermediate: Add resistance, increase complexity, introduce new movement patterns
           - Advanced: Include advanced techniques, higher intensity, sport-specific movements
        
        3. EQUIPMENT-BASED EXERCISE SELECTION:
           - Only use exercises that can be performed with available equipment
           - Provide equipment alternatives when possible
           - Focus on compound movements for efficiency
        
        4. GOAL-SPECIFIC PROGRAMMING:
           - Weight Loss: Include cardio, circuit training, higher rep ranges
           - Muscle Gain: Focus on progressive overload, compound movements, adequate rest
           - Strength: Lower rep ranges, heavier resistance, longer rest periods
           - Endurance: Higher volume, shorter rest, cardiovascular emphasis
           - General Fitness: Balanced approach with variety
        
        5. WEEKLY STRUCTURE:
           - Distribute workouts evenly throughout the week
           - Include adequate rest days for recovery
           - Balance different movement patterns and muscle groups
           - Consider work/life schedule constraints
        
        6. SESSION STRUCTURE (for each workout day):
           - Warm-up (5-10 minutes): Dynamic movements, light cardio
           - Main workout (15-40 minutes): Primary exercises based on goals
           - Cool-down (5-10 minutes): Static stretching, relaxation
        
        7. EXERCISE SPECIFICATIONS:
           - Exercise name and clear description
           - Sets and repetitions or duration
           - Rest periods between sets
           - Intensity level (light/moderate/vigorous)
           - Form cues and safety tips
           - Modifications for limitations
        
        8. PROGRESSION GUIDELINES:
           - Week-by-week progression plan
           - How to increase difficulty safely
           - When to add new exercises
           - Signs that indicate need to modify or rest
        
        9. SAFETY REMINDERS:
           - Always warm up and cool down
           - Stop if experiencing pain (not muscle fatigue)
           - Stay hydrated
           - Listen to your body
           - Specific precautions for reported limitations
        
        FORMAT YOUR RESPONSE:
        - Clear weekly schedule with specific workout days
        - Detailed exercise descriptions with sets/reps
        - Safety modifications for each limitation
        - Progressive plan for upcoming weeks
        - Equipment setup instructions
        - Emergency stop criteria
        
        Prioritize safety above all else. It's better to start too easy and progress gradually than to risk injury.
        """
        
        return prompt
    
    @staticmethod
    def get_exercise_modification_prompt(exercise_name: str, physical_limitations: List[str],
                                       available_equipment: List[str]) -> str:
        """Generate exercise modification prompt"""
        
        prompt = f"""
        EXERCISE MODIFICATION FOR SAFETY
        
        Provide safe modifications for this exercise:
        
        EXERCISE: {exercise_name}
        PHYSICAL LIMITATIONS: {', '.join(physical_limitations) if physical_limitations else 'None'}
        AVAILABLE EQUIPMENT: {', '.join(available_equipment) if available_equipment else 'Bodyweight only'}
        
        MODIFICATION REQUIREMENTS:
        
        1. LIMITATION-SPECIFIC MODIFICATIONS:
           - Identify how the original exercise might conflict with each limitation
           - Provide specific modifications that eliminate risk
           - Suggest alternative exercises that target the same muscles safely
        
        2. EQUIPMENT ADAPTATIONS:
           - Modify the exercise to work with available equipment
           - Suggest equipment substitutions (e.g., water bottles for weights)
           - Provide bodyweight alternatives if no equipment available
        
        3. PROGRESSIVE MODIFICATIONS:
           - Beginner version (easiest, safest)
           - Intermediate version (moderate challenge)
           - Advanced version (full exercise or harder variation)
        
        4. FORM AND SAFETY CUES:
           - Critical form points to prevent injury
           - Common mistakes to avoid
           - Breathing patterns
           - Range of motion guidelines
        
        5. STOP CRITERIA:
           - Warning signs to immediately stop the exercise
           - Difference between muscle fatigue and pain
           - When to seek medical advice
        
        Provide multiple modification options so the user can choose what feels safest and most appropriate for their situation.
        """
        
        return prompt
    
    @staticmethod
    def get_personal_training_consultation_prompt(user_question: str, fitness_context: Dict[str, Any]) -> str:
        """Generate personal training consultation prompt"""
        
        prompt = f"""
        PERSONAL TRAINING CONSULTATION
        
        Provide expert fitness guidance for this question:
        
        USER QUESTION: "{user_question}"
        
        FITNESS CONTEXT:
        - Goals: {fitness_context.get('fitness_goals', 'Not specified')}
        - Current Fitness Level: {fitness_context.get('fitness_level', 'Not specified')}
        - Physical Limitations: {', '.join(fitness_context.get('physical_limitations', [])) if fitness_context.get('physical_limitations') else 'None reported'}
        - Available Equipment: {', '.join(fitness_context.get('available_equipment', [])) if fitness_context.get('available_equipment') else 'Not specified'}
        - Training Experience: {fitness_context.get('training_experience', 'Not specified')}
        - Time Availability: {fitness_context.get('time_availability', 'Not specified')}
        
        CONSULTATION APPROACH:
        
        1. ASSESS THE QUESTION:
           - Identify if it's about exercise technique, programming, nutrition, injury prevention, or general guidance
           - Determine the urgency and safety implications
           - Consider the user's fitness context in your response
        
        2. SAFETY-FIRST GUIDANCE:
           - Address any potential safety concerns immediately
           - Provide warnings if the question involves high-risk activities
           - Recommend medical consultation if needed
           - Always respect reported physical limitations
        
        3. EVIDENCE-BASED RECOMMENDATIONS:
           - Provide scientifically-backed advice
           - Explain the reasoning behind recommendations
           - Offer multiple options when appropriate
           - Include progressive approaches for skill development
        
        4. PRACTICAL IMPLEMENTATION:
           - Give specific, actionable advice
           - Consider the user's equipment and time constraints
           - Provide step-by-step instructions
           - Include form cues and common mistakes to avoid
        
        5. PERSONALIZATION:
           - Tailor advice to the user's fitness level and goals
           - Suggest modifications for limitations
           - Consider individual preferences and constraints
           - Provide alternatives for different scenarios
        
        6. FOLLOW-UP GUIDANCE:
           - Suggest what to monitor or track
           - Provide signs of progress or concern
           - Recommend when to progress or modify
           - Include resources for further learning
        
        FORMAT YOUR RESPONSE:
        - Direct answer to the specific question
        - Safety considerations and warnings
        - Step-by-step implementation guide
        - Modifications for different levels/limitations
        - Expected outcomes and timelines
        - When to seek additional help
        
        Remember: You are providing educational guidance, not medical advice. Always recommend consulting healthcare professionals for injuries or medical concerns.
        """
        
        return prompt
    
    @staticmethod
    def get_workout_modification_prompt(original_plan: Dict[str, Any], modification_request: Dict[str, Any]) -> str:
        """Generate workout plan modification prompt"""
        
        prompt = f"""
        WORKOUT PLAN MODIFICATION
        
        Modify the existing workout plan based on the following request:
        
        ORIGINAL PLAN SUMMARY:
        - Current Goals: {original_plan.get('goals', 'Not specified')}
        - Sessions per Week: {original_plan.get('sessions_per_week', 'Not specified')}
        - Time per Session: {original_plan.get('time_per_session', 'Not specified')} minutes
        - Current Equipment: {', '.join(original_plan.get('equipment', [])) if original_plan.get('equipment') else 'Not specified'}
        
        MODIFICATION REQUEST:
        - Requested Changes: {modification_request.get('changes', 'Not specified')}
        - New Limitations: {', '.join(modification_request.get('new_limitations', [])) if modification_request.get('new_limitations') else 'None'}
        - Equipment Changes: {modification_request.get('equipment_changes', 'None')}
        - Schedule Changes: {modification_request.get('schedule_changes', 'None')}
        - Goal Adjustments: {modification_request.get('goal_adjustments', 'None')}
        
        MODIFICATION GUIDELINES:
        
        1. PRESERVE WHAT WORKS:
           - Keep effective exercises that align with new requirements
           - Maintain progression principles
           - Preserve successful habit patterns
        
        2. ADAPT FOR CHANGES:
           - Modify exercises for new limitations or equipment changes
           - Adjust intensity and volume for schedule changes
           - Realign exercises with new goals
        
        3. ENSURE CONTINUITY:
           - Provide smooth transition from old to new plan
           - Maintain fitness gains where possible
           - Prevent detraining during modification period
        
        4. SAFETY CONSIDERATIONS:
           - Address any new physical limitations
           - Modify high-risk exercises if needed
           - Ensure proper warm-up and cool-down for new activities
        
        5. PROGRESSIVE IMPLEMENTATION:
           - Phase in changes gradually when possible
           - Provide timeline for full implementation
           - Include checkpoints for adjustment
        
        FORMAT YOUR RESPONSE:
        - Summary of key modifications made
        - Updated weekly schedule
        - Exercise substitutions and reasoning
        - Implementation timeline
        - Monitoring and adjustment guidelines
        """
        
        return prompt
    
    @staticmethod
    def get_progress_assessment_prompt(current_data: Dict[str, Any], historical_data: List[Dict[str, Any]]) -> str:
        """Generate progress assessment and recommendations prompt"""
        
        prompt = f"""
        FITNESS PROGRESS ASSESSMENT
        
        Analyze the user's fitness progress and provide recommendations:
        
        CURRENT STATUS:
        - Current Fitness Level: {current_data.get('fitness_level', 'Not specified')}
        - Current Goals: {', '.join(current_data.get('goals', [])) if current_data.get('goals') else 'Not specified'}
        - Recent Performance: {current_data.get('recent_performance', 'Not specified')}
        - Adherence Rate: {current_data.get('adherence_rate', 'Not specified')}%
        - Current Challenges: {current_data.get('challenges', 'Not specified')}
        
        HISTORICAL DATA:
        {FitnessPrompts._format_historical_data(historical_data)}
        
        ASSESSMENT CRITERIA:
        
        1. PROGRESS EVALUATION:
           - Analyze trends in strength, endurance, and skill development
           - Assess goal achievement and milestone completion
           - Evaluate consistency and adherence patterns
           - Identify areas of improvement and stagnation
        
        2. PERFORMANCE ANALYSIS:
           - Compare current performance to baseline measurements
           - Identify strengths and areas needing focus
           - Assess exercise technique and form improvements
           - Evaluate adaptation to training stimulus
        
        3. PROGRAM EFFECTIVENESS:
           - Determine if current program supports goals
           - Assess if modifications are needed
           - Evaluate exercise selection and progression
           - Consider recovery and overtraining signs
        
        4. BARRIER IDENTIFICATION:
           - Identify obstacles to progress
           - Assess environmental and lifestyle factors
           - Evaluate motivation and engagement levels
           - Consider time and resource constraints
        
        5. FUTURE RECOMMENDATIONS:
           - Suggest program modifications for continued progress
           - Recommend new goals or challenges
           - Provide strategies for overcoming barriers
           - Set realistic timelines for improvements
        
        FORMAT YOUR RESPONSE:
        - Overall progress summary
        - Key achievements and improvements
        - Areas needing attention
        - Specific recommendations for next phase
        - Modified goals and timeline
        - Motivational feedback
        """
        
        return prompt
    
    @staticmethod
    def get_injury_prevention_prompt(exercise_plan: Dict[str, Any], risk_factors: List[str]) -> str:
        """Generate injury prevention guidance prompt"""
        
        prompt = f"""
        INJURY PREVENTION ASSESSMENT
        
        Provide comprehensive injury prevention guidance for this exercise plan:
        
        EXERCISE PLAN OVERVIEW:
        - Workout Types: {', '.join(exercise_plan.get('workout_types', [])) if exercise_plan.get('workout_types') else 'Not specified'}
        - Intensity Level: {exercise_plan.get('intensity', 'Not specified')}
        - Frequency: {exercise_plan.get('frequency', 'Not specified')} sessions per week
        - Duration: {exercise_plan.get('duration', 'Not specified')} minutes per session
        
        IDENTIFIED RISK FACTORS:
        {', '.join(risk_factors) if risk_factors else 'None identified'}
        
        INJURY PREVENTION STRATEGIES:
        
        1. MOVEMENT PREPARATION:
           - Specific warm-up routines for each workout type
           - Dynamic stretching and mobility work
           - Activation exercises for key muscle groups
           - Progressive intensity buildup
        
        2. TECHNIQUE OPTIMIZATION:
           - Critical form points for high-risk exercises
           - Common movement errors and corrections
           - Breathing patterns and core engagement
           - Load progression guidelines
        
        3. RECOVERY PROTOCOLS:
           - Cool-down routines and static stretching
           - Recovery activities for rest days
           - Sleep and nutrition considerations
           - Stress management techniques
        
        4. LOAD MANAGEMENT:
           - Progressive overload principles
           - Deload week recommendations
           - Signs of overtraining to monitor
           - Modification strategies for fatigue
        
        5. RISK-SPECIFIC PRECAUTIONS:
           - Address each identified risk factor
           - Provide specific modifications
           - Warning signs to stop exercising
           - When to seek professional help
        
        6. EQUIPMENT SAFETY:
           - Proper equipment setup and use
           - Safety checks before exercising
           - Alternative options for equipment issues
           - Environmental safety considerations
        
        FORMAT YOUR RESPONSE:
        - Risk assessment summary
        - Pre-workout preparation checklist
        - Exercise-specific safety guidelines
        - Recovery and monitoring protocols
        - Emergency action plan
        - Professional consultation recommendations
        """
        
        return prompt
    
    @staticmethod
    def _format_historical_data(historical_data: List[Dict[str, Any]]) -> str:
        """Format historical data for prompt inclusion"""
        if not historical_data:
            return "No historical data available"
        
        formatted_data = []
        for entry in historical_data[-5:]:  # Last 5 entries
            date = entry.get('date', 'Unknown date')
            metrics = []
            if 'weight' in entry:
                metrics.append(f"Weight: {entry['weight']}")
            if 'performance_metrics' in entry:
                metrics.append(f"Performance: {entry['performance_metrics']}")
            if 'adherence' in entry:
                metrics.append(f"Adherence: {entry['adherence']}%")
            
            formatted_data.append(f"- {date}: {', '.join(metrics) if metrics else 'No metrics recorded'}")
        
        return '\n'.join(formatted_data)
