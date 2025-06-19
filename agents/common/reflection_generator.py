"""
Enhanced Reflection Generator for Phase 3 - Complete Replacement System

This module provides comprehensive reflection question generation with:
- Multiple categorized questions (daily_practice, deep_reflection, action_items)
- Template-based generation with context awareness
- Always generates exactly: 2 daily + 2 deep + 1 action = 5 questions total
- Complete replacement of single reflection question system
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import random

from .tool_results import JournalingToolResult, TherapyToolResult


class ReflectionCategory(Enum):
    """Enum for reflection question categories."""
    DAILY_PRACTICE = "daily_practice"     # Immediate, actionable (2 questions)
    DEEP_REFLECTION = "deep_reflection"   # Weekly review, patterns (2 questions)
    ACTION_ITEMS = "action_items"         # Practical implementation (1 question)


class ReflectionType(Enum):
    """Enum for reflection question types."""
    EMPOWERMENT = "empowerment"           # Creator consciousness
    PATTERN_RECOGNITION = "pattern"       # Behavioral insights  
    EMOTIONAL_AWARENESS = "emotional"     # Feeling processing
    GOAL_SETTING = "goal_setting"         # Future-focused
    GRATITUDE = "gratitude"               # Appreciation practice


@dataclass
class ReflectionQuestion:
    """Enhanced reflection question with metadata."""
    question_id: str
    category: ReflectionCategory
    reflection_type: ReflectionType
    question: str
    context: Dict[str, Any]
    delivery: Dict[str, Any]
    metadata: Dict[str, Any]


class EnhancedReflectionGenerator:
    """
    Enhanced reflection generator with template-based, context-aware question generation.
    Always generates exactly 5 questions: 2 daily + 2 deep + 1 action.
    """
    
    def __init__(self):
        """Initialize the enhanced reflection generator."""
        self.logger = logging.getLogger(__name__)
        
        # Template system for context-aware question generation
        self.question_templates = {
            ReflectionCategory.DAILY_PRACTICE: {
                ReflectionType.EMPOWERMENT: [
                    "How did I choose to respond to {challenge} today, and what does this reveal about my inner strength?",
                    "What thought pattern served me well today, and how can I consciously amplify it?",
                    "In what way did I create my experience of {emotion} today through my choices?",
                    "How did I demonstrate my ability to shape my reality in {context} today?",
                    "What moment today showed me that I am the author of my own experience?"
                ],
                ReflectionType.GRATITUDE: [
                    "What small victory or positive moment can I appreciate from today?",
                    "Who or what supported my growth today, and how can I acknowledge this?",
                    "What challenge today actually served as a gift for my development?",
                    "How did my environment reflect back something beautiful about myself today?",
                    "What aspect of my {context} experience today deserves celebration?"
                ],
                ReflectionType.EMOTIONAL_AWARENESS: [
                    "What emotion arose most strongly today, and what was it trying to tell me?",
                    "How did my feelings about {topic} guide me toward what I truly need?",
                    "What emotional pattern did I notice today that I want to explore further?",
                    "In what moment today did I feel most aligned with my authentic self?",
                    "How did honoring my emotional truth today create positive change?"
                ]
            },
            
            ReflectionCategory.DEEP_REFLECTION: {
                ReflectionType.PATTERN_RECOGNITION: [
                    "What recurring theme from this week reveals a pattern I'm ready to transform?",
                    "How has my relationship with {topic} evolved over the past week?",
                    "What belief about myself was challenged this week, and how am I growing beyond it?",
                    "What pattern of thinking or behavior this week no longer serves who I'm becoming?",
                    "How has my response to {challenge_type} changed compared to previous weeks?"
                ],
                ReflectionType.EMPOWERMENT: [
                    "What evidence from this week proves that I am actively creating my desired reality?",
                    "How did I demonstrate leadership in my own life this week, even in small ways?",
                    "What choice this week reflected my deepest values and highest potential?",
                    "In what way did I step into greater personal power this week?",
                    "How has my inner dialogue shifted this week to support my empowerment?"
                ],
                ReflectionType.GOAL_SETTING: [
                    "What insight from this week clarifies my vision for the next month?",
                    "How can the lesson I learned about {topic} this week shape my future choices?",
                    "What new capability or strength did I discover this week that I want to develop?",
                    "Based on this week's experiences, what boundary do I need to set or adjust?",
                    "What theme from this week is calling me to take a specific action next week?"
                ]
            },
            
            ReflectionCategory.ACTION_ITEMS: {
                ReflectionType.GOAL_SETTING: [
                    "What one specific action will I take tomorrow to honor the insight about {insight_topic}?",
                    "How will I implement the lesson about {lesson} in a concrete way this week?",
                    "What boundary or commitment will I establish based on today's reflection?",
                    "What daily practice will I begin to support my growth in {growth_area}?",
                    "How will I celebrate and reinforce the progress I made in {progress_area}?"
                ],
                ReflectionType.EMPOWERMENT: [
                    "What bold step will I take this week to create more of what I truly want?",
                    "How will I actively design my environment to support my {goal} this week?",
                    "What limiting belief will I challenge through a specific action this week?",
                    "How will I demonstrate faith in my capabilities in a new way this week?",
                    "What creative solution will I implement to transform {challenge_area}?"
                ]
            }
        }
        
        # Context variables for template personalization
        self.context_variables = {
            "challenges": ["stress", "conflict", "uncertainty", "change", "decision-making"],
            "emotions": ["joy", "frustration", "peace", "excitement", "clarity"],
            "contexts": ["work", "relationships", "health", "creativity", "spirituality"],
            "topics": ["communication", "boundaries", "self-care", "growth", "purpose"],
            "challenge_types": ["interpersonal conflicts", "work pressures", "self-doubt", "time management"],
            "growth_areas": ["emotional intelligence", "confidence", "communication", "self-compassion"],
            "progress_areas": ["mindfulness", "relationships", "career", "health", "creativity"]
        }
        
        self.logger.info("Enhanced Reflection Generator initialized with template-based system")
    
    async def generate_complete_question_set(
        self, 
        session_data: Dict[str, Any] = None,
        insights: Dict[str, Any] = None,
        user_context: Dict[str, Any] = None,
        source_type: str = "therapy"
    ) -> Dict[ReflectionCategory, List[ReflectionQuestion]]:
        """
        Generate complete set of 5 categorized reflection questions.
        Always generates: 2 daily + 2 deep + 1 action = 5 questions total.
        
        Args:
            session_data: Session context for personalization
            insights: Extracted insights for context awareness
            user_context: User preferences and history
            source_type: Source generating questions (therapy, journaling)
            
        Returns:
            Dictionary with categorized reflection questions
        """
        try:
            # Extract context for personalization
            context_data = self._extract_context(session_data, insights, user_context)
            
            # Generate exactly 2 daily practice questions
            daily_questions = await self._generate_category_questions(
                category=ReflectionCategory.DAILY_PRACTICE,
                count=2,
                context_data=context_data,
                source_type=source_type
            )
            
            # Generate exactly 2 deep reflection questions
            deep_questions = await self._generate_category_questions(
                category=ReflectionCategory.DEEP_REFLECTION,
                count=2,
                context_data=context_data,
                source_type=source_type
            )
            
            # Generate exactly 1 action item question
            action_questions = await self._generate_category_questions(
                category=ReflectionCategory.ACTION_ITEMS,
                count=1,
                context_data=context_data,
                source_type=source_type
            )
            
            # Organize by category
            question_set = {
                ReflectionCategory.DAILY_PRACTICE: daily_questions,
                ReflectionCategory.DEEP_REFLECTION: deep_questions,
                ReflectionCategory.ACTION_ITEMS: action_questions
            }
            
            # Log generation summary
            total_questions = sum(len(questions) for questions in question_set.values())
            self.logger.info(f"Generated complete question set: {total_questions} questions "
                           f"(Daily: {len(daily_questions)}, Deep: {len(deep_questions)}, "
                           f"Action: {len(action_questions)})")
            
            return question_set
            
        except Exception as e:
            self.logger.error(f"Error generating complete question set: {e}")
            return await self._generate_fallback_questions(source_type)
    
    async def _generate_category_questions(
        self,
        category: ReflectionCategory,
        count: int,
        context_data: Dict[str, Any],
        source_type: str
    ) -> List[ReflectionQuestion]:
        """Generate questions for a specific category."""
        questions = []
        
        # Get available types for this category
        available_types = list(self.question_templates[category].keys())
        
        # Select diverse types for multiple questions
        selected_types = self._select_diverse_types(available_types, count)
        
        for i, reflection_type in enumerate(selected_types):
            question = await self._create_personalized_question(
                category=category,
                reflection_type=reflection_type,
                context_data=context_data,
                source_type=source_type
            )
            questions.append(question)
        
        return questions
    
    def _select_diverse_types(self, available_types: List[ReflectionType], count: int) -> List[ReflectionType]:
        """Select diverse reflection types to avoid repetition."""
        if count >= len(available_types):
            # If we need more questions than types, include all types
            selected = available_types.copy()
            # Add random additional types to reach count
            while len(selected) < count:
                selected.append(random.choice(available_types))
        else:
            # Randomly select without replacement
            selected = random.sample(available_types, count)
        
        return selected
    
    async def _create_personalized_question(
        self,
        category: ReflectionCategory,
        reflection_type: ReflectionType,
        context_data: Dict[str, Any],
        source_type: str
    ) -> ReflectionQuestion:
        """Create a personalized reflection question."""
        
        # Get template pool for this category/type
        templates = self.question_templates[category][reflection_type]
        
        # Select random template
        template = random.choice(templates)
        
        # Personalize template with context
        personalized_question = self._personalize_template(template, context_data)
        
        # Create question metadata
        question_id = str(uuid.uuid4())
        current_time = datetime.now()
        
        # Schedule delivery based on category
        scheduled_time = self._calculate_delivery_time(category, current_time)
        
        question = ReflectionQuestion(
            question_id=question_id,
            category=category,
            reflection_type=reflection_type,
            question=personalized_question,
            context={
                "sourceType": source_type,
                "sessionData": context_data.get("session_summary", {}),
                "triggerInsights": context_data.get("insights", []),
                "personalization": context_data.get("personalization_tags", [])
            },
            delivery={
                "createdAt": current_time,
                "scheduledFor": scheduled_time,
                "deliveredAt": None,
                "completedAt": None,
                "expiresAt": current_time + timedelta(days=7)  # Questions expire after 1 week
            },
            metadata={
                "difficulty": self._assess_difficulty(template, context_data),
                "estimatedTime": self._estimate_time(category),
                "template": template,
                "contextVariables": self._extract_used_variables(template)
            }
        )
        
        return question
    
    def _extract_context(self, session_data: Dict, insights: Dict, user_context: Dict) -> Dict[str, Any]:
        """Extract context data for question personalization."""
        context = {
            "session_summary": {},
            "insights": [],
            "personalization_tags": [],
            "emotional_themes": [],
            "challenge_areas": [],
            "growth_areas": []
        }
        
        # Extract from session data
        if session_data:
            context["session_summary"] = session_data
            
            # Extract emotional themes
            if "emotions" in session_data:
                context["emotional_themes"] = session_data["emotions"]
            
            # Extract challenges mentioned
            if "challenges" in session_data:
                context["challenge_areas"] = session_data["challenges"]
        
        # Extract from insights
        if insights:
            context["insights"] = insights
            
            # Extract growth areas from insights
            if "patterns" in insights:
                context["growth_areas"] = insights["patterns"]
        
        # Extract user preferences
        if user_context:
            context["personalization_tags"] = user_context.get("preferences", [])
        
        return context
    
    def _personalize_template(self, template: str, context_data: Dict[str, Any]) -> str:
        """Personalize question template with context variables."""
        personalized = template
        
        # Find placeholder variables in template
        import re
        placeholders = re.findall(r'\{(\w+)\}', template)
        
        for placeholder in placeholders:
            # Get context-aware replacement
            replacement = self._get_context_replacement(placeholder, context_data)
            personalized = personalized.replace(f"{{{placeholder}}}", replacement)
        
        return personalized
    
    def _get_context_replacement(self, placeholder: str, context_data: Dict[str, Any]) -> str:
        """Get context-aware replacement for template placeholder."""
        
        # Try to use session-specific context first
        if placeholder in ["challenge", "emotion", "topic"]:
            session_data = context_data.get("session_summary", {})
            
            if placeholder == "challenge" and "challenges" in session_data:
                return random.choice(session_data["challenges"])
            elif placeholder == "emotion" and "emotions" in session_data:
                return random.choice(session_data["emotions"])
            elif placeholder == "topic" and "topics" in session_data:
                return random.choice(session_data["topics"])
        
        # Fall back to general context variables
        if placeholder in self.context_variables:
            return random.choice(self.context_variables[placeholder])
        
        # Default replacements for common placeholders
        defaults = {
            "challenge": "today's experiences",
            "emotion": "feelings",
            "context": "life situation",
            "topic": "personal growth",
            "insight_topic": "today's learning",
            "lesson": "this experience",
            "growth_area": "personal development",
            "progress_area": "self-awareness",
            "goal": "intentions",
            "challenge_area": "areas of growth",
            "challenge_type": "life challenges"
        }
        
        return defaults.get(placeholder, "your experience")
    
    def _calculate_delivery_time(self, category: ReflectionCategory, current_time: datetime) -> datetime:
        """Calculate appropriate delivery time based on category."""
        
        if category == ReflectionCategory.DAILY_PRACTICE:
            # Daily questions delivered next morning at 8 AM
            next_day = current_time + timedelta(days=1)
            return next_day.replace(hour=8, minute=0, second=0, microsecond=0)
        
        elif category == ReflectionCategory.DEEP_REFLECTION:
            # Deep reflection delivered on Sunday evenings for weekly review
            days_until_sunday = (6 - current_time.weekday()) % 7
            if days_until_sunday == 0:  # Today is Sunday
                days_until_sunday = 7  # Next Sunday
            sunday = current_time + timedelta(days=days_until_sunday)
            return sunday.replace(hour=19, minute=0, second=0, microsecond=0)
        
        elif category == ReflectionCategory.ACTION_ITEMS:
            # Action items delivered within 2 hours for immediate implementation
            return current_time + timedelta(hours=2)
        
        return current_time + timedelta(hours=1)  # Default: 1 hour
    
    def _assess_difficulty(self, template: str, context_data: Dict[str, Any]) -> str:
        """Assess question difficulty based on complexity and context."""
        
        # Simple heuristics for difficulty assessment
        complexity_indicators = ["pattern", "belief", "transform", "leadership", "vision"]
        emotional_indicators = ["emotion", "feeling", "inner", "authentic"]
        
        complexity_score = sum(1 for indicator in complexity_indicators if indicator in template.lower())
        emotional_score = sum(1 for indicator in emotional_indicators if indicator in template.lower())
        
        total_score = complexity_score + emotional_score
        
        if total_score >= 3:
            return "high"
        elif total_score >= 1:
            return "medium"
        else:
            return "easy"
    
    def _estimate_time(self, category: ReflectionCategory) -> str:
        """Estimate time needed for different question categories."""
        
        time_estimates = {
            ReflectionCategory.DAILY_PRACTICE: "3-5 minutes",
            ReflectionCategory.DEEP_REFLECTION: "10-15 minutes",
            ReflectionCategory.ACTION_ITEMS: "5-8 minutes"
        }
        
        return time_estimates.get(category, "5-10 minutes")
    
    def _extract_used_variables(self, template: str) -> List[str]:
        """Extract variables used in template for tracking."""
        import re
        return re.findall(r'\{(\w+)\}', template)
    
    async def _generate_fallback_questions(self, source_type: str) -> Dict[ReflectionCategory, List[ReflectionQuestion]]:
        """Generate fallback questions if main generation fails."""
        
        fallback_questions = {
            ReflectionCategory.DAILY_PRACTICE: [
                "What moment today am I most grateful for?",
                "How did I demonstrate strength or resilience today?"
            ],
            ReflectionCategory.DEEP_REFLECTION: [
                "What pattern in my life this week deserves my attention?",
                "How has my perspective shifted through recent experiences?"
            ],
            ReflectionCategory.ACTION_ITEMS: [
                "What one action will I take tomorrow to support my wellbeing?"
            ]
        }
        
        result = {}
        for category, questions in fallback_questions.items():
            question_objects = []
            for i, q_text in enumerate(questions):
                question = ReflectionQuestion(
                    question_id=str(uuid.uuid4()),
                    category=category,
                    reflection_type=ReflectionType.EMPOWERMENT,
                    question=q_text,
                    context={"sourceType": source_type, "fallback": True},
                    delivery={
                        "createdAt": datetime.now(),
                        "scheduledFor": datetime.now() + timedelta(hours=1),
                        "deliveredAt": None,
                        "completedAt": None,
                        "expiresAt": datetime.now() + timedelta(days=7)
                    },
                    metadata={
                        "difficulty": "easy",
                        "estimatedTime": "3-5 minutes",
                        "template": "fallback",
                        "contextVariables": []
                    }
                )
                question_objects.append(question)
            result[category] = question_objects
        
        self.logger.warning("Used fallback questions due to generation error")
        return result
    
    def get_question_summary(self, question_set: Dict[ReflectionCategory, List[ReflectionQuestion]]) -> Dict[str, Any]:
        """Get summary of generated question set."""
        
        total_questions = sum(len(questions) for questions in question_set.values())
        
        category_counts = {
            category.value: len(questions) 
            for category, questions in question_set.items()
        }
        
        reflection_types = {}
        for category, questions in question_set.items():
            types_in_category = [q.reflection_type.value for q in questions]
            reflection_types[category.value] = types_in_category
        
        return {
            "total_questions": total_questions,
            "category_breakdown": category_counts,
            "reflection_types": reflection_types,
            "generation_timestamp": datetime.now().isoformat(),
            "delivery_schedule": {
                category.value: [q.delivery["scheduledFor"].isoformat() for q in questions]
                for category, questions in question_set.items()
            }
        }


# Export main class and enums
__all__ = [
    "EnhancedReflectionGenerator",
    "ReflectionCategory", 
    "ReflectionType",
    "ReflectionQuestion"
] 