import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from google.adk import Agent, AgentConfig, Session
from google.genai import Client as GenAIClient

from config.api_keys import get_api_key
from shared.utils.adk_communication import adk_comm, MessageType, Priority
from config.firebase_config import firebase_config
from integrations.elevenlabs.voice_synthesis import elevenlabs_voice
from integrations.tavus.video_generation import tavus_video
from integrations.google_vision_mock.food_recognition import mock_google_vision

class NutritionAgent(Agent):
    """Google ADK-powered nutrition agent for meal planning and calorie tracking"""
    
    def __init__(self):
        # Initialize Google ADK agent configuration
        config = AgentConfig(
            name="nutrition_agent",
            description="Simple meal plan generator and nutritional consultation for calorie tracking and plan modifications",
            model="gemini-2.5-pro",
            temperature=0.6,  # Moderate creativity for meal variety
            max_tokens=2048,
            system_instructions=self._get_system_instructions()
        )
        
        super().__init__(config)
        
        # Initialize Gemini client
        self.gemini_client = GenAIClient(api_key=get_api_key('gemini_2_5_pro'))
        
        # User dietary profiles
        self.user_profiles = {}
        
        logging.info("Nutrition Agent initialized with Google ADK")
    
    def _get_system_instructions(self) -> str:
        """Get system instructions for the nutrition agent"""
        return """You are a Nutrition Agent providing simple, practical meal planning and nutritional guidance. Your role is to:

1. MEAL PLAN GENERATION: Create basic weekly meal plans based on user's physical goals (weight loss, muscle gain, maintenance) and dietary preferences
2. CALORIE TRACKING: Help users track calories through food recognition and USDA database lookups
3. NUTRITIONAL CONSULTATION: Provide conversational nutrition advice through text, voice, and video
4. PLAN MODIFICATION: Allow users to modify meal plans based on preferences and availability
5. GOAL FLEXIBILITY: Enable users to change dietary goals and preferences anytime

Key Principles:
- Keep nutritional advice simple and actionable
- Focus on practical meal solutions users can actually implement
- Provide clear calorie information for foods
- Offer straightforward food substitutions
- Respect dietary restrictions and preferences
- Allow flexibility in goal changes

Avoid complex nutritional science - focus on practical, everyday nutrition guidance."""

    async def generate_meal_plan(self, session: Session, plan_request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized meal plan using Gemini 2.5 Pro"""
        try:
            user_id = plan_request.get('user_id')
            physical_goals = plan_request.get('physical_goals', ['maintenance'])
            dietary_preferences = plan_request.get('dietary_preferences', [])
            dietary_restrictions = plan_request.get('dietary_restrictions', [])
            target_calories = plan_request.get('target_calories', 2000)
            
            logging.info(f"Generating meal plan for user {user_id}")
            
            # Store user preferences
            await self._store_user_preferences(user_id, plan_request)
            
            # Generate meal plan using Gemini 2.5 Pro
            meal_plan = await self._create_meal_plan(
                session, physical_goals, dietary_preferences, dietary_restrictions, target_calories
            )
            
            # Store meal plan
            plan_id = await self._store_meal_plan(user_id, meal_plan)
            
            # Generate voice consultation if requested
            voice_consultation = None
            if plan_request.get('include_voice', False):
                voice_consultation = await self._generate_voice_consultation(meal_plan)
            
            # Generate video consultation if requested
            video_consultation = None
            if plan_request.get('include_video', False):
                video_consultation = await self._generate_video_consultation(meal_plan, plan_request)
            
            return {
                'plan_id': plan_id,
                'meal_plan': meal_plan,
                'voice_consultation': voice_consultation,
                'video_consultation': video_consultation,
                'generated_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error generating meal plan: {e}")
            return {'error': str(e)}
    
    async def _store_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """Store user dietary preferences in Firebase"""
        try:
            db = firebase_config.get_firestore_client()
            
            user_nutrition_profile = {
                'user_id': user_id,
                'physical_goals': preferences.get('physical_goals', []),
                'dietary_preferences': preferences.get('dietary_preferences', []),
                'dietary_restrictions': preferences.get('dietary_restrictions', []),
                'target_calories': preferences.get('target_calories', 2000),
                'allergies': preferences.get('allergies', []),
                'updated_at': datetime.now()
            }
            
            db.collection('nutrition_profiles').document(user_id).set(user_nutrition_profile)
            
        except Exception as e:
            logging.error(f"Error storing user preferences: {e}")
    
    async def _create_meal_plan(self, session: Session, physical_goals: List[str], 
                              dietary_preferences: List[str], dietary_restrictions: List[str],
                              target_calories: int) -> Dict[str, Any]:
        """Create meal plan using Gemini 2.5 Pro"""
        try:
            # Import prompts
            from .prompt_file import NutritionPrompts
            
            meal_plan_prompt = NutritionPrompts.get_meal_plan_generation_prompt(
                physical_goals, dietary_preferences, dietary_restrictions, target_calories
            )
            
            meal_plan_response = await session.send_message(meal_plan_prompt)
            
            # Parse meal plan (simplified for demo)
            meal_plan = {
                'weekly_plan': self._parse_weekly_plan(meal_plan_response.text),
                'daily_calorie_target': target_calories,
                'macronutrient_breakdown': self._calculate_macro_breakdown(physical_goals),
                'shopping_list': self._generate_shopping_list(meal_plan_response.text),
                'meal_prep_tips': self._extract_meal_prep_tips(meal_plan_response.text),
                'generated_plan': meal_plan_response.text
            }
            
            return meal_plan
            
        except Exception as e:
            logging.error(f"Error creating meal plan: {e}")
            return {}
    
    def _parse_weekly_plan(self, plan_text: str) -> Dict[str, Dict[str, str]]:
        """Parse weekly meal plan from text"""
        # Simplified parsing - would use more sophisticated parsing in production
        weekly_plan = {}
        
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        for day in days:
            weekly_plan[day] = {
                'breakfast': f'Healthy breakfast option for {day}',
                'lunch': f'Balanced lunch for {day}',
                'dinner': f'Nutritious dinner for {day}',
                'snacks': f'Healthy snacks for {day}'
            }
        
        return weekly_plan
    
    def _calculate_macro_breakdown(self, physical_goals: List[str]) -> Dict[str, int]:
        """Calculate macronutrient breakdown based on goals"""
        if 'weight_loss' in physical_goals:
            return {'protein': 30, 'carbs': 35, 'fat': 35}
        elif 'muscle_gain' in physical_goals:
            return {'protein': 35, 'carbs': 40, 'fat': 25}
        else:  # maintenance
            return {'protein': 25, 'carbs': 45, 'fat': 30}
    
    def _generate_shopping_list(self, plan_text: str) -> List[str]:
        """Generate shopping list from meal plan"""
        # Simplified shopping list generation
        basic_items = [
            'Chicken breast', 'Brown rice', 'Broccoli', 'Sweet potatoes',
            'Greek yogurt', 'Eggs', 'Spinach', 'Salmon', 'Quinoa', 'Avocado'
        ]
        return basic_items
    
    def _extract_meal_prep_tips(self, plan_text: str) -> List[str]:
        """Extract meal prep tips from plan"""
        tips = [
            'Prepare proteins in bulk on Sunday',
            'Wash and chop vegetables ahead of time',
            'Cook grains in large batches',
            'Use meal prep containers for portion control'
        ]
        return tips
    
    async def _store_meal_plan(self, user_id: str, meal_plan: Dict[str, Any]) -> str:
        """Store meal plan in Firebase"""
        try:
            db = firebase_config.get_firestore_client()
            
            plan_doc = {
                'user_id': user_id,
                'meal_plan': meal_plan,
                'created_at': datetime.now(),
                'active': True
            }
            
            doc_ref = db.collection('meal_plans').add(plan_doc)
            plan_id = doc_ref[1].id
            
            logging.info(f"Stored meal plan {plan_id} for user {user_id}")
            return plan_id
            
        except Exception as e:
            logging.error(f"Error storing meal plan: {e}")
            return f"error_{datetime.now().timestamp()}"
    
    async def _generate_voice_consultation(self, meal_plan: Dict[str, Any]) -> Optional[bytes]:
        """Generate voice consultation using ElevenLabs"""
        try:
            consultation_text = f"""
            Here's your personalized meal plan overview. 
            Your daily calorie target is {meal_plan.get('daily_calorie_target', 2000)} calories.
            Your macronutrient breakdown is {meal_plan.get('macronutrient_breakdown', {}).get('protein', 25)}% protein, 
            {meal_plan.get('macronutrient_breakdown', {}).get('carbs', 45)}% carbohydrates, 
            and {meal_plan.get('macronutrient_breakdown', {}).get('fat', 30)}% healthy fats.
            
            I've created a balanced weekly meal plan that includes variety and nutrition.
            Remember to stay hydrated and listen to your body's hunger cues.
            You can always ask me to modify any meals based on your preferences.
            """
            
            voice_consultation = await elevenlabs_voice.synthesize_nutrition_consultation_audio(
                consultation_text, {'consultation_type': 'meal_plan_overview'}
            )
            
            return voice_consultation
            
        except Exception as e:
            logging.error(f"Error generating voice consultation: {e}")
            return None
    
    async def _generate_video_consultation(self, meal_plan: Dict[str, Any], 
                                         plan_request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate video consultation using Tavus"""
        try:
            video_data = {
                'user_id': plan_request.get('user_id'),
                'consultation_type': 'nutrition_plan',
                'daily_calories': meal_plan.get('daily_calorie_target', 2000),
                'physical_goals': plan_request.get('physical_goals', []),
                'meal_plan_summary': meal_plan.get('generated_plan', '')[:500]  # First 500 chars
            }
            
            video_result = await tavus_video.create_nutrition_consultation_video(video_data)
            
            return video_result
            
        except Exception as e:
            logging.error(f"Error generating video consultation: {e}")
            return None
    
    async def analyze_food_image(self, image_data: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze food image using mock Google Vision API"""
        try:
            # Use mock Google Vision API for food recognition
            recognition_result = await mock_google_vision.recognize_food_from_image(
                image_data, user_context
            )
            
            # Get nutritional suggestions
            suggestions = await mock_google_vision.get_food_suggestions(
                recognition_result.get('total_nutrition', {}),
                user_context.get('dietary_goals', {})
            )
            
            return {
                'recognition_result': recognition_result,
                'nutritional_suggestions': suggestions,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error analyzing food image: {e}")
            return {'error': str(e)}
    
    async def modify_meal_plan(self, session: Session, modification_request: Dict[str, Any]) -> Dict[str, Any]:
        """Modify existing meal plan based on user request"""
        try:
            user_id = modification_request.get('user_id')
            plan_id = modification_request.get('plan_id')
            modifications = modification_request.get('modifications', '')
            
            # Get current meal plan
            current_plan = await self._get_current_meal_plan(user_id, plan_id)
            
            # Generate modifications using Gemini 2.5 Pro
            from .prompt_file import NutritionPrompts
            
            modification_prompt = NutritionPrompts.get_meal_plan_modification_prompt(
                current_plan, modifications
            )
            
            modification_response = await session.send_message(modification_prompt)
            
            # Update meal plan
            updated_plan = await self._update_meal_plan(plan_id, modification_response.text)
            
            return {
                'plan_id': plan_id,
                'updated_plan': updated_plan,
                'modifications_applied': modifications,
                'update_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error modifying meal plan: {e}")
            return {'error': str(e)}
    
    async def _get_current_meal_plan(self, user_id: str, plan_id: str) -> Dict[str, Any]:
        """Get current meal plan from Firebase"""
        try:
            db = firebase_config.get_firestore_client()
            plan_doc = db.collection('meal_plans').document(plan_id).get()
            
            if plan_doc.exists:
                return plan_doc.to_dict().get('meal_plan', {})
            else:
                return {}
                
        except Exception as e:
            logging.error(f"Error getting current meal plan: {e}")
            return {}
    
    async def _update_meal_plan(self, plan_id: str, updated_content: str) -> Dict[str, Any]:
        """Update meal plan in Firebase"""
        try:
            db = firebase_config.get_firestore_client()
            
            # Parse updated content (simplified)
            updated_plan = {
                'updated_content': updated_content,
                'last_modified': datetime.now()
            }
            
            db.collection('meal_plans').document(plan_id).update({
                'meal_plan': updated_plan,
                'updated_at': datetime.now()
            })
            
            return updated_plan
            
        except Exception as e:
            logging.error(f"Error updating meal plan: {e}")
            return {}

# Global nutrition agent instance
nutrition_agent = NutritionAgent()
