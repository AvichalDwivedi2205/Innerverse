"""
LLM-Powered Meal Planner

Advanced meal planning engine using LLM for unlimited creativity,
personalization, and intelligent meal plan generation.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class LLMMealPlanner:
    """LLM-powered meal planning with unlimited creativity and personalization."""
    
    def __init__(self, agent):
        """Initialize LLM meal planner."""
        self.agent = agent
        logger.info("LLMMealPlanner initialized")

    async def generate_comprehensive_meal_plan(self, user_preferences: Dict) -> Dict:
        """Generate complete meal plan with recipes using LLM."""
        
        try:
            # Extract key preferences
            duration = user_preferences.get('duration_days', 7)
            budget_level = user_preferences.get('budget_level', 'medium')
            weekly_budget = user_preferences.get('weekly_budget', self._get_default_budget(budget_level))
            
            meal_plan_prompt = self._build_meal_plan_prompt(user_preferences, duration, weekly_budget)
            
            # Generate meal plan with LLM
            # Mock meal plan response - in production this would use Agent conversation flow
            raw_response = self._get_mock_meal_plan_response(user_preferences)
            meal_plan = await self._parse_meal_plan_response(raw_response, user_preferences)
            
            # Add metadata
            meal_plan['duration_days'] = duration
            meal_plan['estimated_cost'] = weekly_budget if duration == 7 else (weekly_budget * duration / 7)
            meal_plan['generated_at'] = datetime.now().isoformat()
            meal_plan['user_preferences'] = user_preferences
            
            logger.info(f"Generated {duration}-day meal plan with estimated cost ${meal_plan['estimated_cost']}")
            return meal_plan
            
        except Exception as e:
            logger.error(f"Error generating meal plan: {str(e)}")
            return self._get_fallback_meal_plan(user_preferences)

    def _build_meal_plan_prompt(self, preferences: Dict, duration: int, budget: float) -> str:
        """Build comprehensive meal planning prompt."""
        
        prompt = f"""Create a comprehensive {duration}-day meal plan for this user:

**USER PROFILE:**
- Age: {preferences.get('age', 'Adult')}
- Gender: {preferences.get('gender', 'Not specified')}
- Activity Level: {preferences.get('activity_level', 'Moderately active')}
- Primary Goal: {preferences.get('primary_goal', 'General health')}
- Timeline: {preferences.get('timeline', 'Ongoing')}
- Mental Health Focus: {preferences.get('mental_health_goals', 'General wellbeing')}

**DIETARY REQUIREMENTS:**
- Diet Type: {preferences.get('diet_type', 'Omnivore')}
- Allergies/Intolerances: {preferences.get('allergies', 'None specified')}
- Foods to Avoid: {preferences.get('dislikes', 'None specified')}
- Cultural Preferences: {preferences.get('cultural_preferences', 'Varied cuisines')}
- Cooking Level: {preferences.get('cooking_skill', 'Intermediate')}

**LIFESTYLE CONSTRAINTS:**
- Budget: ${budget}/week
- Cooking Time: {preferences.get('cooking_time', '30 minutes')} per day
- Meal Prep Preference: {preferences.get('meal_prep_preference', 'Sometimes')}
- Eating Schedule: {preferences.get('eating_schedule', 'Regular meal times')}

**MEAL STRUCTURE REQUIREMENTS:**
- 3 main meals (breakfast, lunch, dinner) + 2 healthy snacks per day
- Include simple, clear recipes for each meal
- Vary cuisines and flavors throughout the week
- Balance macronutrients (protein, carbs, healthy fats)
- Stay within budget while maximizing nutrition
- Consider meal prep opportunities where appropriate
- Include foods that support mental health and energy

**CREATIVITY GUIDELINES:**
- Mix different cuisines (Mediterranean, Asian, Mexican, etc.)
- Use seasonal ingredients when possible
- Include both familiar and new foods
- Balance quick meals with more elaborate ones
- Consider batch cooking opportunities
- Include mood-boosting foods (omega-3s, complex carbs, etc.)

**FORMAT REQUIREMENTS:**
Return as valid JSON with this exact structure:
{{
  "daily_plans": {{
    "1": {{
      "breakfast": {{
        "name": "Meal name",
        "ingredients": ["ingredient 1", "ingredient 2"],
        "simple_recipe": "Step-by-step instructions",
        "prep_time": "15 min",
        "nutrition_highlights": ["protein", "fiber"]
      }},
      "morning_snack": {{ ... }},
      "lunch": {{ ... }},
      "afternoon_snack": {{ ... }},
      "dinner": {{ ... }}
    }},
    "2": {{ ... }}
  }},
  "nutrition_balance": "Brief description of overall nutrition balance",
  "meal_prep_tips": "3-4 practical meal prep suggestions",
  "cuisine_variety": "List of cuisines featured",
  "budget_breakdown": "How the budget is allocated"
}}

Be creative with flavors, practical with preparation, and mindful of the budget!"""
        
        return prompt

    async def _parse_meal_plan_response(self, raw_response: str, preferences: Dict) -> Dict:
        """Parse LLM meal plan response into structured format."""
        
        try:
            # Try to extract JSON from response
            json_start = raw_response.find('{')
            json_end = raw_response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = raw_response[json_start:json_end]
                meal_plan = json.loads(json_str)
                
                # Validate structure
                if self._validate_meal_plan_structure(meal_plan):
                    return meal_plan
            
            # If JSON parsing fails, use LLM to fix it
            return await self._fix_meal_plan_format(raw_response, preferences)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            return await self._fix_meal_plan_format(raw_response, preferences)
        except Exception as e:
            logger.error(f"Error parsing meal plan: {str(e)}")
            return self._get_fallback_meal_plan(preferences)

    async def _fix_meal_plan_format(self, raw_response: str, preferences: Dict) -> Dict:
        """Use LLM to fix meal plan format."""
        
        try:
            fix_prompt = f"""
            Fix this meal plan response to be valid JSON with the correct structure:
            
            Original response: {raw_response}
            
            Required JSON structure:
            {{
              "daily_plans": {{
                "1": {{
                  "breakfast": {{"name": "...", "ingredients": [...], "simple_recipe": "...", "prep_time": "...", "nutrition_highlights": [...]}},
                  "morning_snack": {{ ... }},
                  "lunch": {{ ... }},
                  "afternoon_snack": {{ ... }},
                  "dinner": {{ ... }}
                }},
                "2": {{ ... }}
              }},
              "nutrition_balance": "...",
              "meal_prep_tips": "...",
              "cuisine_variety": "...",
              "budget_breakdown": "..."
            }}
            
            Return ONLY valid JSON, no additional text.
            """
            
            fixed_response = await self.agent.generate(fix_prompt)
            return json.loads(fixed_response)
            
        except Exception as e:
            logger.error(f"Error fixing meal plan format: {str(e)}")
            return self._get_fallback_meal_plan(preferences)

    def _validate_meal_plan_structure(self, meal_plan: Dict) -> bool:
        """Validate meal plan has correct structure."""
        
        required_keys = ['daily_plans']
        if not all(key in meal_plan for key in required_keys):
            return False
        
        daily_plans = meal_plan.get('daily_plans', {})
        if not daily_plans:
            return False
        
        # Check at least one day exists
        for day_num, day_data in daily_plans.items():
            required_meals = ['breakfast', 'lunch', 'dinner']
            if not all(meal in day_data for meal in required_meals):
                return False
            
            # Check meal structure
            for meal_name, meal_data in day_data.items():
                if not isinstance(meal_data, dict) or 'name' not in meal_data:
                    return False
        
        return True

    async def generate_recipe_details(self, meal_name: str, dietary_restrictions: List[str], cooking_skill: str = 'intermediate') -> Dict:
        """Generate detailed recipe for a specific meal."""
        
        try:
            recipe_prompt = f"""
            Create a detailed recipe for: {meal_name}
            
            Dietary Restrictions: {dietary_restrictions if dietary_restrictions else 'None'}
            Cooking Skill Level: {cooking_skill}
            
            Include:
            - Complete ingredient list with specific quantities
            - Step-by-step cooking instructions (numbered)
            - Prep time and cook time
            - Serving size
            - Nutrition highlights (key nutrients)
            - Tips for meal prep or storage
            - 2-3 possible ingredient substitutions
            - Equipment needed
            
            Keep instructions clear and appropriate for {cooking_skill} level.
            
            Format as JSON:
            {{
              "recipe_name": "...",
              "ingredients": [
                {{"item": "ingredient name", "quantity": "amount", "notes": "optional notes"}}
              ],
              "instructions": [
                "Step 1: ...",
                "Step 2: ..."
              ],
              "prep_time": "X minutes",
              "cook_time": "X minutes", 
              "total_time": "X minutes",
              "servings": X,
              "nutrition_highlights": ["nutrient 1", "nutrient 2"],
              "meal_prep_tips": "Storage and prep advice",
              "substitutions": [
                {{"original": "ingredient", "substitute": "alternative", "reason": "why"}}
              ],
              "equipment": ["tool 1", "tool 2"],
              "difficulty": "easy/medium/hard"
            }}
            """
            
            recipe_text = await self.agent.generate(recipe_prompt)
            
            # Parse JSON response
            json_start = recipe_text.find('{')
            json_end = recipe_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = recipe_text[json_start:json_end]
                return json.loads(json_str)
            
            # Fallback if JSON parsing fails
            return {
                'recipe_name': meal_name,
                'ingredients': [],
                'instructions': ['Recipe generation failed, please try again'],
                'prep_time': '15 minutes',
                'cook_time': '15 minutes',
                'total_time': '30 minutes',
                'servings': 2,
                'nutrition_highlights': ['varies'],
                'meal_prep_tips': 'Store in refrigerator',
                'substitutions': [],
                'equipment': ['basic kitchen tools'],
                'difficulty': 'medium'
            }
            
        except Exception as e:
            logger.error(f"Error generating recipe details: {str(e)}")
            return self._get_fallback_recipe(meal_name)

    async def generate_meal_variations(self, base_meal: Dict, preferences: Dict, variation_count: int = 3) -> List[Dict]:
        """Generate variations of a base meal."""
        
        try:
            variation_prompt = f"""
            Create {variation_count} variations of this meal:
            
            Base meal: {base_meal}
            User preferences: {preferences}
            
            Generate variations by:
            - Changing cooking method (grilled vs baked vs sautéed)
            - Using different spices/seasonings
            - Swapping similar ingredients
            - Changing cuisine style (Italian → Mexican → Asian)
            - Adjusting for different dietary needs
            
            Keep the same basic nutrition profile and cooking difficulty.
            
            Format as JSON array:
            [
              {{
                "name": "Variation name",
                "ingredients": ["ingredient 1", "ingredient 2"],
                "simple_recipe": "Brief cooking instructions",
                "prep_time": "X min",
                "nutrition_highlights": ["nutrient 1", "nutrient 2"],
                "cuisine_style": "cuisine type",
                "variation_notes": "What makes this different from the original"
              }}
            ]
            """
            
            variations_text = await self.agent.generate(variation_prompt)
            
            # Parse JSON response
            json_start = variations_text.find('[')
            json_end = variations_text.rfind(']') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = variations_text[json_start:json_end]
                return json.loads(json_str)
            
            return []
            
        except Exception as e:
            logger.error(f"Error generating meal variations: {str(e)}")
            return []

    def _get_default_budget(self, budget_level: str) -> float:
        """Get default budget based on level."""
        
        budget_map = {
            'low': 50.0,
            'medium': 100.0,
            'high': 200.0
        }
        
        return budget_map.get(budget_level, 100.0)

    def _get_fallback_meal_plan(self, preferences: Dict) -> Dict:
        """Get fallback meal plan if LLM generation fails."""
        
        duration = preferences.get('duration_days', 7)
        diet_type = preferences.get('diet_type', 'omnivore')
        
        # Simple fallback meal plan
        fallback_plan = {
            'daily_plans': {},
            'nutrition_balance': 'Balanced macronutrients with variety',
            'meal_prep_tips': 'Prepare proteins in advance, wash vegetables ahead of time',
            'cuisine_variety': 'Mixed international cuisines',
            'budget_breakdown': 'Economical ingredient choices'
        }
        
        # Generate simple days
        for day in range(1, duration + 1):
            fallback_plan['daily_plans'][str(day)] = self._get_fallback_day_plan(diet_type, day)
        
        return fallback_plan

    def _get_fallback_day_plan(self, diet_type: str, day_num: int) -> Dict:
        """Get fallback day plan."""
        
        if diet_type.lower() == 'vegetarian':
            return {
                'breakfast': {
                    'name': 'Vegetarian Scrambled Eggs with Toast',
                    'ingredients': ['eggs', 'whole grain bread', 'spinach', 'cheese'],
                    'simple_recipe': 'Scramble eggs with spinach, serve with toast',
                    'prep_time': '10 min',
                    'nutrition_highlights': ['protein', 'fiber']
                },
                'morning_snack': {
                    'name': 'Greek Yogurt with Berries',
                    'ingredients': ['Greek yogurt', 'mixed berries', 'honey'],
                    'simple_recipe': 'Mix yogurt with berries and drizzle honey',
                    'prep_time': '2 min',
                    'nutrition_highlights': ['protein', 'probiotics']
                },
                'lunch': {
                    'name': 'Quinoa Buddha Bowl',
                    'ingredients': ['quinoa', 'chickpeas', 'vegetables', 'tahini dressing'],
                    'simple_recipe': 'Combine cooked quinoa with roasted vegetables and chickpeas',
                    'prep_time': '20 min',
                    'nutrition_highlights': ['complete protein', 'fiber']
                },
                'afternoon_snack': {
                    'name': 'Hummus with Vegetables',
                    'ingredients': ['hummus', 'carrots', 'bell peppers', 'cucumber'],
                    'simple_recipe': 'Slice vegetables and serve with hummus',
                    'prep_time': '5 min',
                    'nutrition_highlights': ['fiber', 'healthy fats']
                },
                'dinner': {
                    'name': 'Vegetarian Pasta Primavera',
                    'ingredients': ['whole wheat pasta', 'seasonal vegetables', 'olive oil', 'parmesan'],
                    'simple_recipe': 'Sauté vegetables, toss with cooked pasta and olive oil',
                    'prep_time': '25 min',
                    'nutrition_highlights': ['complex carbs', 'vegetables']
                }
            }
        else:
            return {
                'breakfast': {
                    'name': 'Overnight Oats with Fruit',
                    'ingredients': ['rolled oats', 'milk', 'banana', 'chia seeds'],
                    'simple_recipe': 'Mix ingredients, refrigerate overnight',
                    'prep_time': '5 min',
                    'nutrition_highlights': ['fiber', 'healthy fats']
                },
                'morning_snack': {
                    'name': 'Apple with Almond Butter',
                    'ingredients': ['apple', 'almond butter'],
                    'simple_recipe': 'Slice apple and serve with almond butter',
                    'prep_time': '2 min',
                    'nutrition_highlights': ['fiber', 'healthy fats']
                },
                'lunch': {
                    'name': 'Grilled Chicken Salad',
                    'ingredients': ['chicken breast', 'mixed greens', 'vegetables', 'olive oil dressing'],
                    'simple_recipe': 'Grill chicken, serve over salad with dressing',
                    'prep_time': '15 min',
                    'nutrition_highlights': ['lean protein', 'vitamins']
                },
                'afternoon_snack': {
                    'name': 'Trail Mix',
                    'ingredients': ['nuts', 'seeds', 'dried fruit'],
                    'simple_recipe': 'Mix ingredients together',
                    'prep_time': '1 min',
                    'nutrition_highlights': ['healthy fats', 'protein']
                },
                'dinner': {
                    'name': 'Baked Salmon with Vegetables',
                    'ingredients': ['salmon fillet', 'broccoli', 'sweet potato', 'herbs'],
                    'simple_recipe': 'Bake salmon and vegetables with herbs',
                    'prep_time': '25 min',
                    'nutrition_highlights': ['omega-3', 'vitamins']
                }
            }

    def _get_fallback_recipe(self, meal_name: str) -> Dict:
        """Get fallback recipe if generation fails."""
        
        return {
            'recipe_name': meal_name,
            'ingredients': [
                {'item': 'main ingredient', 'quantity': '1 portion', 'notes': 'adjust to taste'},
                {'item': 'seasonings', 'quantity': 'to taste', 'notes': 'salt, pepper, herbs'}
            ],
            'instructions': [
                'Prepare ingredients according to recipe requirements',
                'Cook using appropriate method for ingredients',
                'Season to taste and serve'
            ],
            'prep_time': '15 minutes',
            'cook_time': '20 minutes',
            'total_time': '35 minutes',
            'servings': 2,
            'nutrition_highlights': ['varies based on ingredients'],
            'meal_prep_tips': 'Store leftovers in refrigerator for up to 3 days',
            'substitutions': [],
            'equipment': ['basic kitchen tools'],
            'difficulty': 'medium'
        }

    def _get_mock_meal_plan_response(self, user_preferences: Dict) -> str:
        """Generate mock meal plan response for testing."""
        return """{
            "duration_days": 7,
            "estimated_cost": 85.50,
            "nutrition_balance": "Well-balanced macronutrients with adequate protein, healthy fats, and complex carbs",
            "meal_prep_tips": "Prepare grains and proteins in batches on Sunday",
            "daily_plans": {
                "1": {
                    "breakfast": {"name": "Vegetarian Scramble with Toast", "prep_time": "10 min"},
                    "morning_snack": {"name": "Greek Yogurt with Berries", "prep_time": "2 min"},
                    "lunch": {"name": "Quinoa Buddha Bowl", "prep_time": "15 min"},
                    "afternoon_snack": {"name": "Hummus with Veggies", "prep_time": "3 min"},
                    "dinner": {"name": "Lentil Curry with Rice", "prep_time": "25 min"}
                },
                "2": {
                    "breakfast": {"name": "Overnight Oats with Fruit", "prep_time": "5 min"},
                    "morning_snack": {"name": "Handful of Nuts", "prep_time": "1 min"},
                    "lunch": {"name": "Chickpea Salad Sandwich", "prep_time": "10 min"},
                    "afternoon_snack": {"name": "Apple with Peanut Butter", "prep_time": "2 min"},
                    "dinner": {"name": "Vegetable Stir-fry with Tofu", "prep_time": "20 min"}
                },
                "3": {
                    "breakfast": {"name": "Smoothie Bowl", "prep_time": "8 min"},
                    "morning_snack": {"name": "Granola Bar", "prep_time": "1 min"},
                    "lunch": {"name": "Black Bean Quesadilla", "prep_time": "12 min"},
                    "afternoon_snack": {"name": "Trail Mix", "prep_time": "1 min"},
                    "dinner": {"name": "Pasta with Marinara and Vegetables", "prep_time": "18 min"}
                }
            }
        }""" 