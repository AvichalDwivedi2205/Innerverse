from typing import Dict, Any
from datetime import datetime

class JournalingPrompts:
    """Empathetic prompts for journaling agent interactions"""
    
    @staticmethod
    def get_general_response_prompt(context: Dict[str, Any]) -> str:
        """Generate general empathetic response prompt"""
        entry_text = context.get('entry_text', '')
        mood_score = context.get('mood_score', 0.0)
        dominant_emotion = context.get('dominant_emotion', 'neutral')
        triggers = context.get('triggers', [])
        coping_mechanisms = context.get('coping_mechanisms', [])
        
        prompt = f"""
        The user has shared a journal entry with you. Here's what they wrote:
        
        "{entry_text}"
        
        Context:
        - Current mood score: {mood_score:.2f} (range: -1 to 1)
        - Dominant emotion: {dominant_emotion}
        - Identified triggers: {', '.join(triggers) if triggers else 'None identified'}
        - Coping mechanisms used: {', '.join(coping_mechanisms) if coping_mechanisms else 'None mentioned'}
        
        Respond with empathy and understanding. Your response should:
        1. Acknowledge and validate their feelings
        2. Reflect back what you heard to show understanding
        3. Ask ONE thoughtful follow-up question to encourage deeper reflection
        4. Offer gentle encouragement or a positive reframe if appropriate
        
        Keep your response warm, supportive, and conversational (2-3 sentences plus one question).
        """
        
        return prompt
    
    @staticmethod
    def get_low_mood_response_prompt(context: Dict[str, Any]) -> str:
        """Generate response for low mood entries"""
        entry_text = context.get('entry_text', '')
        triggers = context.get('triggers', [])
        coping_mechanisms = context.get('coping_mechanisms', [])
        
        prompt = f"""
        The user is experiencing a difficult time and shared this with you:
        
        "{entry_text}"
        
        Context:
        - They're experiencing low mood/depression
        - Triggers identified: {', '.join(triggers) if triggers else 'None clear'}
        - Coping strategies mentioned: {', '.join(coping_mechanisms) if coping_mechanisms else 'None mentioned'}
        
        Your response should be especially gentle and supportive. Focus on:
        1. Validating their struggle without minimizing it
        2. Acknowledging their strength in sharing these feelings
        3. Gently exploring what might help them feel a bit better right now
        4. Reminding them that difficult feelings are temporary
        
        Be extra compassionate and avoid toxic positivity. Ask about small, manageable steps they might take.
        """
        
        return prompt
    
    @staticmethod
    def get_anxiety_response_prompt(context: Dict[str, Any]) -> str:
        """Generate response for high anxiety entries"""
        entry_text = context.get('entry_text', '')
        triggers = context.get('triggers', [])
        anxiety_level = context.get('emotional_intensity', 0.0)
        
        prompt = f"""
        The user is experiencing significant anxiety and shared:
        
        "{entry_text}"
        
        Context:
        - High anxiety level detected ({anxiety_level:.2f})
        - Anxiety triggers: {', '.join(triggers) if triggers else 'Not clearly identified'}
        
        Your response should be calming and grounding. Focus on:
        1. Acknowledging their anxiety with understanding
        2. Validating that anxiety is a normal human experience
        3. Gently suggesting grounding techniques if appropriate
        4. Asking about what usually helps them when they feel this way
        
        Use calm, reassuring language and avoid adding to their worry. Consider mentioning breathing or mindfulness if it fits naturally.
        """
        
        return prompt
    
    @staticmethod
    def get_crisis_response_prompt(context: Dict[str, Any]) -> str:
        """Generate response for crisis situations"""
        entry_text = context.get('entry_text', '')
        
        prompt = f"""
        CRISIS RESPONSE NEEDED: The user has shared concerning content that indicates they may be in emotional crisis:
        
        "{entry_text}"
        
        Your immediate response should:
        1. Express genuine concern and care for their wellbeing
        2. Acknowledge their pain without judgment
        3. Gently remind them that they're not alone
        4. Let them know that professional help is being arranged
        5. Encourage them to reach out to crisis resources if they feel unsafe
        
        Be direct but compassionate. This is not the time for questions - focus on immediate support and safety.
        Include: "I'm concerned about you and want to make sure you get the support you need. A therapy session is being arranged for you."
        """
        
        return prompt
    
    @staticmethod
    def get_follow_up_prompts() -> Dict[str, str]:
        """Get follow-up prompts for deeper exploration"""
        return {
            'emotional_exploration': "What emotions are you noticing right now as you reflect on this?",
            'trigger_identification': "Can you think of what might have contributed to feeling this way today?",
            'coping_exploration': "What has helped you through similar situations in the past?",
            'gratitude_shift': "Is there anything, even something small, that brought you a moment of peace today?",
            'future_focus': "What's one small thing you're looking forward to, even if it's just later today?",
            'support_system': "Who in your life makes you feel understood and supported?",
            'self_compassion': "If a close friend was going through exactly what you're experiencing, what would you tell them?",
            'progress_recognition': "Looking back at your recent entries, what positive changes do you notice in yourself?",
            'goal_setting': "What's one small step you could take tomorrow to care for your mental health?",
            'mindfulness': "What are you noticing in your body right now as we talk about this?"
        }
    
    @staticmethod
    def get_encouragement_phrases() -> Dict[str, List[str]]:
        """Get encouraging phrases for different situations"""
        return {
            'validation': [
                "Your feelings are completely valid.",
                "It makes sense that you'd feel this way given what you're going through.",
                "Thank you for trusting me with these feelings.",
                "It takes courage to be this honest about your emotions."
            ],
            'strength_recognition': [
                "I can see how much strength it took to share this.",
                "You're showing real resilience by working through these feelings.",
                "The fact that you're reflecting on this shows your commitment to growth.",
                "You're taking important steps by being aware of your emotional patterns."
            ],
            'hope_building': [
                "Difficult feelings are temporary, even when they feel overwhelming.",
                "You've gotten through hard times before, and you have that strength within you now.",
                "Small steps forward are still progress.",
                "Healing isn't linear, and that's completely normal."
            ],
            'gentle_challenge': [
                "I wonder if there might be another way to look at this situation?",
                "What would you tell a friend who was experiencing exactly what you're going through?",
                "Sometimes our thoughts can be harsher than reality - what do you think?",
                "Is this thought helping you or making things harder right now?"
            ]
        }
    
    @staticmethod
    def get_crisis_resources_text() -> str:
        """Get crisis resources information"""
        return """
        If you're having thoughts of self-harm or suicide, please reach out for immediate help:
        
        🇺🇸 National Suicide Prevention Lifeline: 988
        🇺🇸 Crisis Text Line: Text HOME to 741741
        🇺🇸 Emergency Services: 911
        
        🌍 International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/
        
        You are not alone, and there are people who want to help you through this difficult time.
        """
    
    @staticmethod
    def get_welcome_message() -> str:
        """Get welcome message for new users"""
        return """
        Welcome to your personal journaling space! I'm here to listen and support you as you explore your thoughts and feelings.
        
        This is a safe space where you can:
        ✨ Share your daily experiences and emotions
        🌱 Reflect on your personal growth
        💭 Process difficult feelings
        🎯 Identify patterns and triggers
        🛠️ Discover effective coping strategies
        
        You can write to me in text or speak your thoughts aloud - whatever feels most natural to you. I'm here to listen without judgment and help you gain insights into your emotional well-being.
        
        What's on your mind today?
        """
