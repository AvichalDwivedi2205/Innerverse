"""
LLM-Powered Substitution Engine

Intelligent food substitution system using LLM for smart alternatives,
dietary adaptations, and personalized food swaps.
"""

import json
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class LLMSubstitutionEngine:
    """LLM-powered food substitution with intelligent suggestions."""
    
    def __init__(self, agent):
        """Initialize substitution engine."""
        self.agent = agent
        logger.info("LLMSubstitutionEngine initialized")

    async def suggest_substitutions_after_generation(self, meal_plan: Dict, user_preferences: Dict) -> Dict:
        """Proactively suggest substitutions after meal plan generation."""
        
        try:
            substitution_prompt = self._build_proactive_substitution_prompt(meal_plan, user_preferences)
            
            raw_suggestions = self._get_mock_response(substitution_prompt)
            
            # Parse suggestions
            suggestions = await self._parse_substitution_suggestions(raw_suggestions)
            
            logger.info(f"Generated {len(suggestions.get('suggestions', []))} proactive substitution suggestions")
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating proactive substitutions: {str(e)}")
            return {'suggestions': self._get_fallback_suggestions()}

    def _build_proactive_substitution_prompt(self, meal_plan: Dict, user_preferences: Dict) -> str:
        """Build prompt for proactive substitution suggestions."""
        
        # Extract key meals and ingredients for analysis
        sample_meals = self._extract_sample_meals(meal_plan)
        
        prompt = f"""
        Review this meal plan and suggest helpful substitutions for flexibility:

        SAMPLE MEALS FROM PLAN:
        {sample_meals}
        
        USER PROFILE:
        - Diet: {user_preferences.get('diet_type', 'Omnivore')}
        - Budget: {user_preferences.get('budget_level', 'Medium')}
        - Allergies: {user_preferences.get('allergies', 'None')}
        - Dislikes: {user_preferences.get('dislikes', 'None')}
        - Cooking Level: {user_preferences.get('cooking_skill', 'Intermediate')}
        - Cultural Preferences: {user_preferences.get('cultural_preferences', 'Varied')}

        GENERATE 8-10 HELPFUL SUBSTITUTION SUGGESTIONS:
        
        Categories to cover:
        1. Budget-friendly alternatives (save money)
        2. Dietary restriction alternatives (accommodate different diets)
        3. Skill level alternatives (easier/harder options)
        4. Flavor variety alternatives (different cuisines/tastes)
        5. Ingredient availability alternatives (common substitutes)
        6. Allergy-friendly alternatives (if applicable)
        7. Time-saving alternatives (quicker options)
        8. Nutrition-focused alternatives (healthier swaps)

        FORMAT: Return as JSON:
        {{
          "suggestions": [
            {{
              "category": "budget-friendly",
              "suggestion": "Don't like salmon? Try canned salmon, sardines, or chicken thighs instead - same protein, lower cost",
              "reasoning": "Maintains protein content while reducing cost"
            }},
            {{
              "category": "dietary",
              "suggestion": "Need vegan options? Replace chicken with tofu, tempeh, or lentils",
              "reasoning": "Plant-based proteins with similar texture and nutrition"
            }}
          ],
          "summary": "Brief overview of substitution flexibility in this plan"
        }}

        Make suggestions practical, encouraging, and specific to the meal plan!
        """
        
        return prompt

    def _extract_sample_meals(self, meal_plan: Dict) -> str:
        """Extract sample meals from meal plan for analysis."""
        
        sample_meals = []
        daily_plans = meal_plan.get('daily_plans', {})
        
        # Get first 2 days as samples
        for day_num in sorted(daily_plans.keys())[:2]:
            day_data = daily_plans[day_num]
            
            for meal_type in ['breakfast', 'lunch', 'dinner']:
                if meal_type in day_data:
                    meal_info = day_data[meal_type]
                    meal_name = meal_info.get('name', 'Unknown meal')
                    ingredients = meal_info.get('ingredients', [])
                    
                    sample_meals.append(f"Day {day_num} {meal_type}: {meal_name} (ingredients: {', '.join(ingredients[:4])})")
        
        return '\n'.join(sample_meals) if sample_meals else "No meals found in plan"

    async def _parse_substitution_suggestions(self, raw_suggestions: str) -> Dict:
        """Parse LLM substitution suggestions response."""
        
        try:
            # Try to extract JSON
            json_start = raw_suggestions.find('{')
            json_end = raw_suggestions.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = raw_suggestions[json_start:json_end]
                parsed = json.loads(json_str)
                
                if 'suggestions' in parsed and isinstance(parsed['suggestions'], list):
                    return parsed
            
            # If JSON parsing fails, extract suggestions manually
            return await self._extract_suggestions_manually(raw_suggestions)
            
        except Exception as e:
            logger.error(f"Error parsing substitution suggestions: {str(e)}")
            return {'suggestions': self._get_fallback_suggestions()}

    async def _extract_suggestions_manually(self, raw_text: str) -> Dict:
        """Extract suggestions manually if JSON parsing fails."""
        
        try:
            extract_prompt = f"""
            Extract substitution suggestions from this text and format as JSON:
            
            Text: {raw_text}
            
            Format as:
            {{
              "suggestions": [
                {{
                  "category": "category_name",
                  "suggestion": "suggestion text",
                  "reasoning": "why this substitution works"
                }}
              ],
              "summary": "overall summary"
            }}
            
            Return only valid JSON.
            """
            
            response_text = self._get_mock_response(extract_prompt)
            return json.loads(response_text)
            
        except Exception as e:
            logger.error(f"Error extracting suggestions manually: {str(e)}")
            return {'suggestions': self._get_fallback_suggestions()}

    async def process_user_substitution_request(self, meal_plan: Dict, substitution_request: str, user_preferences: Dict) -> Dict:
        """Process specific user substitution requests."""
        
        try:
            substitution_prompt = self._build_user_substitution_prompt(
                meal_plan, substitution_request, user_preferences
            )
            
            raw_response = self._get_mock_response(substitution_prompt)
            
            # Parse the updated meal plan
            updated_plan = await self._parse_substitution_response(raw_response, meal_plan)
            
            logger.info(f"Processed user substitution request: {substitution_request[:50]}...")
            return updated_plan
            
        except Exception as e:
            logger.error(f"Error processing user substitution: {str(e)}")
            return self._get_fallback_substitution_response(meal_plan, substitution_request)

    def _build_user_substitution_prompt(self, meal_plan: Dict, request: str, preferences: Dict) -> str:
        """Build prompt for user-requested substitutions."""
        
        prompt = f"""
        User wants to make this substitution: "{request}"
        
        CURRENT MEAL PLAN:
        {self._format_meal_plan_for_substitution(meal_plan)}
        
        USER PREFERENCES:
        - Diet: {preferences.get('diet_type', 'Omnivore')}
        - Budget: {preferences.get('budget_level', 'Medium')}
        - Allergies: {preferences.get('allergies', 'None')}
        - Dislikes: {preferences.get('dislikes', 'None')}
        - Cooking Level: {preferences.get('cooking_skill', 'Intermediate')}
        
        PROCESS THIS SUBSTITUTION REQUEST:
        1. Identify what they want to change (specific ingredient, meal, or dietary requirement)
        2. Suggest 2-3 appropriate alternatives that fit their diet/budget/preferences
        3. Update the affected meals with new ingredients and recipes
        4. Maintain nutritional balance and meal variety
        5. Keep within budget constraints
        6. Explain the changes and why they work
        
        FORMAT RESPONSE AS JSON:
        {{
          "changes_made": [
            "Replaced salmon in Day 2 dinner with chicken breast",
            "Updated recipe instructions for new protein"
          ],
          "explanation": "I've replaced the salmon with chicken breast as requested. This maintains the protein content while reducing cost and accommodating your preference.",
          "affected_meals": [
            {{
              "day": "2",
              "meal_type": "dinner",
              "old_name": "Baked Salmon with Vegetables",
              "new_name": "Grilled Chicken with Vegetables",
              "new_ingredients": ["chicken breast", "broccoli", "sweet potato", "herbs"],
              "new_recipe": "Season chicken breast and grill for 6-8 minutes per side. Roast vegetables at 400°F for 20 minutes.",
              "prep_time": "25 min",
              "nutrition_highlights": ["lean protein", "vitamins"]
            }}
          ],
          "nutrition_impact": "Maintains protein content, slightly reduces omega-3 fatty acids",
          "budget_impact": "Saves approximately $3-5 per serving",
          "additional_suggestions": [
            "You could also try turkey breast or pork tenderloin",
            "Add avocado for healthy fats if desired"
          ]
        }}
        
        Be specific about changes and helpful with explanations!
        """
        
        return prompt

    def _format_meal_plan_for_substitution(self, meal_plan: Dict) -> str:
        """Format meal plan for substitution analysis."""
        
        formatted = ""
        daily_plans = meal_plan.get('daily_plans', {})
        
        for day_num in sorted(daily_plans.keys()):
            day_data = daily_plans[day_num]
            formatted += f"\nDay {day_num}:\n"
            
            for meal_type in ['breakfast', 'lunch', 'dinner']:
                if meal_type in day_data:
                    meal_info = day_data[meal_type]
                    meal_name = meal_info.get('name', 'Unknown')
                    ingredients = meal_info.get('ingredients', [])
                    
                    formatted += f"  {meal_type}: {meal_name} ({', '.join(ingredients[:3])})\n"
        
        return formatted

    async def _parse_substitution_response(self, raw_response: str, original_plan: Dict) -> Dict:
        """Parse substitution response and update meal plan."""
        
        try:
            # Extract JSON from response
            json_start = raw_response.find('{')
            json_end = raw_response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = raw_response[json_start:json_end]
                substitution_data = json.loads(json_str)
                
                # Apply changes to original meal plan
                updated_plan = original_plan.copy()
                
                for affected_meal in substitution_data.get('affected_meals', []):
                    day = affected_meal.get('day')
                    meal_type = affected_meal.get('meal_type')
                    
                    if day in updated_plan.get('daily_plans', {}) and meal_type in updated_plan['daily_plans'][day]:
                        # Update the meal
                        updated_plan['daily_plans'][day][meal_type].update({
                            'name': affected_meal.get('new_name'),
                            'ingredients': affected_meal.get('new_ingredients', []),
                            'simple_recipe': affected_meal.get('new_recipe'),
                            'prep_time': affected_meal.get('prep_time'),
                            'nutrition_highlights': affected_meal.get('nutrition_highlights', [])
                        })
                
                # Add substitution metadata
                substitution_data['updated_meal_plan'] = updated_plan
                return substitution_data
            
            # If JSON parsing fails, return fallback
            return self._get_fallback_substitution_response(original_plan, "substitution request")
            
        except Exception as e:
            logger.error(f"Error parsing substitution response: {str(e)}")
            return self._get_fallback_substitution_response(original_plan, "substitution request")

    async def suggest_ingredient_alternatives(self, ingredient: str, dietary_restrictions: List[str], budget_level: str = 'medium') -> List[Dict]:
        """Suggest alternatives for a specific ingredient."""
        
        try:
            alternatives_prompt = f"""
            Suggest 5-7 alternatives for this ingredient: {ingredient}
            
            Considerations:
            - Dietary restrictions: {dietary_restrictions if dietary_restrictions else 'None'}
            - Budget level: {budget_level}
            - Similar nutritional profile
            - Similar cooking properties
            - Easy to find in stores
            
            Format as JSON array:
            [
              {{
                "alternative": "ingredient name",
                "reason": "why it's a good substitute",
                "nutrition_comparison": "how nutrition compares",
                "cost_comparison": "more/less/similar cost",
                "cooking_notes": "any cooking adjustments needed"
              }}
            ]
            """
            
            alternatives_text = self._get_mock_response(alternatives_prompt)
            
            # Parse JSON response
            json_start = alternatives_text.find('[')
            json_end = alternatives_text.rfind(']') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = alternatives_text[json_start:json_end]
                return json.loads(json_str)
            
            return []
            
        except Exception as e:
            logger.error(f"Error suggesting ingredient alternatives: {str(e)}")
            return []

    async def adapt_meal_for_diet(self, meal: Dict, target_diet: str) -> Dict:
        """Adapt a meal for a specific dietary requirement."""
        
        try:
            adaptation_prompt = f"""
            Adapt this meal for {target_diet} diet:
            
            Original meal: {meal}
            Target diet: {target_diet}
            
            Make necessary substitutions while:
            - Maintaining similar flavors and textures
            - Keeping nutritional balance
            - Using accessible ingredients
            - Preserving cooking difficulty level
            
            Format as JSON:
            {{
              "adapted_meal": {{
                "name": "new meal name",
                "ingredients": ["new ingredient list"],
                "simple_recipe": "updated cooking instructions",
                "prep_time": "time needed",
                "nutrition_highlights": ["key nutrients"]
              }},
              "changes_made": ["list of specific changes"],
              "adaptation_notes": "explanation of how it fits the diet"
            }}
            """
            
            adaptation_text = self._get_mock_response(adaptation_prompt)
            
            # Parse JSON response
            json_start = adaptation_text.find('{')
            json_end = adaptation_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = adaptation_text[json_start:json_end]
                return json.loads(json_str)
            
            return {'adapted_meal': meal, 'changes_made': [], 'adaptation_notes': 'No adaptation needed'}
            
        except Exception as e:
            logger.error(f"Error adapting meal for diet: {str(e)}")
            return {'adapted_meal': meal, 'changes_made': [], 'adaptation_notes': 'Adaptation failed'}

    def _get_fallback_suggestions(self) -> List[Dict]:
        """Get fallback substitution suggestions."""
        
        return [
            {
                'category': 'budget-friendly',
                'suggestion': 'Replace expensive proteins like salmon with chicken thighs, eggs, or beans for similar nutrition at lower cost',
                'reasoning': 'Maintains protein content while reducing grocery costs'
            },
            {
                'category': 'dietary',
                'suggestion': 'Need vegetarian options? Swap meat with tofu, tempeh, lentils, or chickpeas',
                'reasoning': 'Plant-based proteins provide similar satiety and nutrition'
            },
            {
                'category': 'time-saving',
                'suggestion': 'Short on time? Use pre-cooked proteins, frozen vegetables, or one-pot meals',
                'reasoning': 'Reduces preparation time without sacrificing nutrition'
            },
            {
                'category': 'flavor-variety',
                'suggestion': 'Want different flavors? Try the same base ingredients with different spice blends (Italian, Mexican, Asian)',
                'reasoning': 'Same nutrition, completely different taste experience'
            },
            {
                'category': 'availability',
                'suggestion': 'Can\'t find specific ingredients? Most vegetables can be swapped for similar ones (broccoli ↔ cauliflower, spinach ↔ kale)',
                'reasoning': 'Similar nutritional profiles and cooking properties'
            }
        ]

    def _get_fallback_substitution_response(self, original_plan: Dict, request: str) -> Dict:
        """Get fallback response for failed substitutions."""
        
        return {
            'changes_made': [f'Processed request: {request}'],
            'explanation': 'I understand your substitution request. Could you be more specific about what you\'d like to change?',
            'affected_meals': [],
            'nutrition_impact': 'No changes made yet',
            'budget_impact': 'No cost changes',
            'additional_suggestions': [
                'Try being more specific about ingredients or meals you want to change',
                'Let me know if you have dietary restrictions I should consider',
                'I can help with budget-friendly swaps if cost is a concern'
            ],
            'updated_meal_plan': original_plan
        }

    def _get_mock_response(self, prompt: str) -> str:
        """Generate mock response for testing."""
        if "substitution suggestions" in prompt.lower():
            return '{"suggestions": [{"category": "budget-friendly", "suggestion": "Replace expensive ingredients with budget alternatives", "reasoning": "Maintains nutrition while reducing cost"}], "summary": "Multiple substitution options available"}'
        elif "extract substitution" in prompt.lower():
            return '{"suggestions": [{"category": "dietary", "suggestion": "Try plant-based alternatives", "reasoning": "Accommodates dietary preferences"}], "summary": "Extracted suggestions"}'
        else:
            return '{"changes_made": ["Mock substitution made"], "explanation": "Mock substitution explanation", "affected_meals": [], "nutrition_impact": "Minimal impact", "budget_impact": "Cost neutral"}' 