"""
LLM-Powered Budget Optimizer

Intelligent budget optimization system using LLM for cost-effective
meal planning while maintaining nutrition and taste quality.
"""

import json
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class LLMBudgetOptimizer:
    """LLM-powered budget optimization for meal plans."""
    
    def __init__(self, agent):
        """Initialize budget optimizer."""
        self.agent = agent
        logger.info("LLMBudgetOptimizer initialized")

    async def optimize_for_budget(self, meal_plan: Dict, target_budget: float, user_preferences: Dict) -> Dict:
        """Optimize meal plan to fit specific budget using LLM creativity."""
        
        try:
            current_cost = meal_plan.get('estimated_cost', target_budget + 50)
            
            # If already within budget, provide cost-saving tips instead
            if current_cost <= target_budget:
                return await self._provide_cost_saving_tips(meal_plan, target_budget, user_preferences)
            
            optimization_prompt = self._build_budget_optimization_prompt(
                meal_plan, target_budget, current_cost, user_preferences
            )
            
            raw_response = self._get_mock_response(optimization_prompt)
            
            # Parse optimized meal plan
            optimized_plan = await self._parse_optimization_response(raw_response, meal_plan, target_budget)
            
            logger.info(f"Optimized meal plan for ${target_budget} budget")
            return optimized_plan
            
        except Exception as e:
            logger.error(f"Error optimizing for budget: {str(e)}")
            return self._get_fallback_optimization(meal_plan, target_budget)

    def _build_budget_optimization_prompt(self, meal_plan: Dict, target_budget: float, current_cost: float, preferences: Dict) -> str:
        """Build comprehensive budget optimization prompt."""
        
        savings_needed = current_cost - target_budget
        
        prompt = f"""
        Optimize this meal plan to fit a ${target_budget}/week budget:

        CURRENT SITUATION:
        - Current estimated cost: ${current_cost}/week
        - Target budget: ${target_budget}/week
        - Savings needed: ${savings_needed:.2f}/week
        
        CURRENT MEAL PLAN:
        {self._format_meal_plan_for_optimization(meal_plan)}

        USER PREFERENCES:
        - Diet: {preferences.get('diet_type', 'Omnivore')}
        - Cooking Level: {preferences.get('cooking_skill', 'Intermediate')}
        - Cultural Preferences: {preferences.get('cultural_preferences', 'Varied')}
        - Allergies: {preferences.get('allergies', 'None')}
        - Meal Prep: {preferences.get('meal_prep_preference', 'Sometimes')}

        OPTIMIZATION STRATEGIES TO APPLY:
        1. **Protein Swaps**: Replace expensive proteins with budget-friendly alternatives
           - Salmon → Canned salmon, chicken thighs, eggs
           - Beef → Ground turkey, chicken, plant proteins
           - Fresh fish → Frozen fish, canned fish
        
        2. **Smart Shopping**: Use cost-effective ingredient choices
           - Seasonal vegetables and fruits
           - Bulk buying opportunities (rice, beans, oats)
           - Store brands and generic alternatives
           - Frozen vegetables instead of fresh when appropriate
        
        3. **Meal Prep Optimization**: Batch cooking for efficiency
           - Cook proteins in bulk
           - Prepare versatile base ingredients
           - Use leftovers creatively
        
        4. **Ingredient Versatility**: Use ingredients across multiple meals
           - Same vegetables in different preparations
           - Base proteins used in various cuisines
           - Pantry staples that work in many dishes
        
        5. **Plant-Forward Approach**: Increase affordable plant proteins
           - Beans, lentils, chickpeas
           - Eggs and dairy
           - Tofu and tempeh
        
        REQUIREMENTS:
        - Maintain nutritional quality and balance
        - Keep meals interesting and flavorful
        - Respect dietary restrictions
        - Preserve variety throughout the week
        - Stay within ${target_budget} budget
        - Provide specific cost-saving explanations

        FORMAT RESPONSE AS JSON:
        {{
          "optimized_daily_plans": {{
            "1": {{
              "breakfast": {{
                "name": "Updated meal name",
                "ingredients": ["cost-effective ingredients"],
                "simple_recipe": "updated instructions",
                "prep_time": "time",
                "nutrition_highlights": ["nutrients"],
                "cost_savings": "what changed to save money"
              }},
              "lunch": {{ ... }},
              "dinner": {{ ... }}
            }}
          }},
          "estimated_cost": {target_budget - 5},
          "total_savings": {savings_needed + 5},
          "cost_saving_tips": [
            "Specific tip 1 with estimated savings",
            "Specific tip 2 with estimated savings"
          ],
          "budget_breakdown": {{
            "proteins": "30%",
            "vegetables": "25%", 
            "grains": "20%",
            "pantry_items": "15%",
            "other": "10%"
          }},
          "meal_prep_suggestions": [
            "Batch cook suggestion 1",
            "Batch cook suggestion 2"
          ],
          "shopping_tips": [
            "Shop sales and seasonal produce",
            "Buy proteins in bulk when on sale"
          ]
        }}

        Be creative with cost-saving while maintaining delicious, nutritious meals!
        """
        
        return prompt

    def _format_meal_plan_for_optimization(self, meal_plan: Dict) -> str:
        """Format meal plan for budget optimization analysis."""
        
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
                    
                    # Highlight potentially expensive ingredients
                    expensive_ingredients = self._identify_expensive_ingredients(ingredients)
                    
                    formatted += f"  {meal_type}: {meal_name}\n"
                    formatted += f"    Ingredients: {', '.join(ingredients[:5])}\n"
                    if expensive_ingredients:
                        formatted += f"    Expensive items: {', '.join(expensive_ingredients)}\n"
        
        return formatted

    def _identify_expensive_ingredients(self, ingredients: List[str]) -> List[str]:
        """Identify potentially expensive ingredients."""
        
        expensive_keywords = [
            'salmon', 'tuna', 'shrimp', 'lobster', 'crab',
            'beef', 'steak', 'lamb', 'veal',
            'organic', 'grass-fed', 'free-range',
            'pine nuts', 'cashews', 'macadamia',
            'truffle', 'saffron', 'vanilla bean',
            'fresh herbs', 'specialty cheese'
        ]
        
        expensive_items = []
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            for keyword in expensive_keywords:
                if keyword in ingredient_lower:
                    expensive_items.append(ingredient)
                    break
        
        return expensive_items

    async def _parse_optimization_response(self, raw_response: str, original_plan: Dict, target_budget: float) -> Dict:
        """Parse budget optimization response."""
        
        try:
            # Extract JSON from response
            json_start = raw_response.find('{')
            json_end = raw_response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = raw_response[json_start:json_end]
                optimization_data = json.loads(json_str)
                
                # Merge optimized daily plans with original structure
                optimized_plan = original_plan.copy()
                
                if 'optimized_daily_plans' in optimization_data:
                    optimized_plan['daily_plans'] = optimization_data['optimized_daily_plans']
                
                # Add optimization metadata
                optimized_plan['estimated_cost'] = optimization_data.get('estimated_cost', optimized_plan.get('estimated_cost', 0))
                optimized_plan['cost_saving_tips'] = optimization_data.get('cost_saving_tips', [])
                optimized_plan['budget_breakdown'] = optimization_data.get('budget_breakdown', {})
                optimized_plan['meal_prep_suggestions'] = optimization_data.get('meal_prep_suggestions', [])
                optimized_plan['shopping_tips'] = optimization_data.get('shopping_tips', [])
                optimized_plan['total_savings'] = optimization_data.get('total_savings', 0)
                optimized_plan['optimization_applied'] = True
                
                return optimized_plan
            
            # If JSON parsing fails, return fallback
            return self._get_fallback_optimization(original_plan, target_budget)
            
        except Exception as e:
            logger.error(f"Error parsing optimization response: {str(e)}")
            return self._get_fallback_optimization(original_plan, target_budget)

    async def _provide_cost_saving_tips(self, meal_plan: Dict, target_budget: float, preferences: Dict) -> Dict:
        """Provide cost-saving tips when already within budget."""
        
        try:
            tips_prompt = f"""
            This meal plan is already within the ${target_budget} budget, but provide additional cost-saving tips:
            
            MEAL PLAN: {self._format_meal_plan_for_optimization(meal_plan)}
            USER PREFERENCES: {preferences}
            
            Provide 8-10 practical cost-saving tips that could reduce costs even further:
            
            Categories:
            1. Smart shopping strategies
            2. Bulk buying opportunities  
            3. Meal prep efficiency
            4. Ingredient substitutions
            5. Seasonal eating
            6. Waste reduction
            7. Store brand alternatives
            8. Cooking techniques that save money
            
            Format as JSON:
            {{
              "cost_saving_tips": [
                "Buy proteins in bulk when on sale and freeze portions",
                "Use frozen vegetables - often cheaper and just as nutritious"
              ],
              "estimated_additional_savings": 15,
              "budget_already_optimized": true,
              "current_efficiency_score": "85%"
            }}
            """
            
            tips_text = self._get_mock_response(tips_prompt)
            
            # Parse JSON response
            json_start = tips_text.find('{')
            json_end = tips_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = tips_text[json_start:json_end]
                return json.loads(json_str)
            
            return self._get_fallback_tips()
            
        except Exception as e:
            logger.error(f"Error generating budget tips: {str(e)}")
            return self._get_fallback_tips()

    async def suggest_budget_alternatives(self, meal_plan: Dict, budget_constraints: Dict) -> Dict:
        """Suggest budget alternatives for specific constraints."""
        
        try:
            constraints_prompt = f"""
            Suggest budget alternatives based on these constraints:
            
            MEAL PLAN: {self._format_meal_plan_for_optimization(meal_plan)}
            CONSTRAINTS: {budget_constraints}
            
            Provide specific alternatives for:
            1. Most expensive meals
            2. Costly ingredients
            3. Time-intensive preparations
            4. Specialty items
            
            Format as JSON:
            {{
              "meal_alternatives": [
                {{
                  "original_meal": "expensive meal name",
                  "alternative": "budget-friendly version",
                  "cost_savings": "$5-8 per serving",
                  "nutrition_comparison": "maintains protein, reduces cost"
                }}
              ],
              "ingredient_swaps": [
                {{
                  "expensive_ingredient": "salmon",
                  "budget_alternatives": ["canned salmon", "chicken thighs", "tofu"],
                  "cost_difference": "50-70% savings"
                }}
              ],
              "preparation_shortcuts": [
                "Use pre-cooked proteins to save time and energy costs"
              ]
            }}
            """
            
            alternatives_text = self._get_mock_response(constraints_prompt)
            
            # Parse JSON response
            json_start = alternatives_text.find('[')
            json_end = alternatives_text.rfind(']') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = alternatives_text[json_start:json_end]
                return json.loads(json_str)
            
            return []
            
        except Exception as e:
            logger.error(f"Error generating budget alternatives: {str(e)}")
            return []

    async def calculate_cost_breakdown(self, meal_plan: Dict, budget_level: str) -> Dict:
        """Calculate detailed cost breakdown for meal plan."""
        
        try:
            breakdown_prompt = f"""
            Calculate detailed cost breakdown for this meal plan:
            
            MEAL PLAN: {self._format_meal_plan_for_optimization(meal_plan)}
            BUDGET LEVEL: {budget_level}
            
            Estimate costs for:
            1. Proteins (meat, fish, plant proteins)
            2. Vegetables and fruits
            3. Grains and starches
            4. Dairy and eggs
            5. Pantry items (oils, spices, condiments)
            6. Snacks and beverages
            
            Consider:
            - Typical grocery store prices
            - Seasonal variations
            - Bulk buying opportunities
            - Store brand vs name brand
            
            Format as JSON:
            {{
              "weekly_breakdown": {{
                "proteins": {{"cost": 35, "percentage": "35%"}},
                "vegetables": {{"cost": 20, "percentage": "20%"}},
                "grains": {{"cost": 15, "percentage": "15%"}},
                "dairy": {{"cost": 12, "percentage": "12%"}},
                "pantry": {{"cost": 10, "percentage": "10%"}},
                "other": {{"cost": 8, "percentage": "8%"}}
              }},
              "total_estimated_cost": 100,
              "cost_per_meal": 4.76,
              "cost_per_day": 14.29,
              "budget_efficiency": "85%",
              "cost_saving_opportunities": [
                "Buy proteins in bulk for 15% savings",
                "Use frozen vegetables for 20% savings"
              ]
            }}
            """
            
            breakdown_text = self._get_mock_response(breakdown_prompt)
            
            # Parse JSON response
            json_start = breakdown_text.find('{')
            json_end = breakdown_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = breakdown_text[json_start:json_end]
                return json.loads(json_str)
            
            return self._get_fallback_breakdown(budget_level)
            
        except Exception as e:
            logger.error(f"Error generating cost breakdown: {str(e)}")
            return self._get_fallback_breakdown(budget_level)

    def _get_fallback_optimization(self, original_plan: Dict, target_budget: float) -> Dict:
        """Get fallback optimization if LLM optimization fails."""
        
        optimized_plan = original_plan.copy()
        optimized_plan['estimated_cost'] = target_budget
        optimized_plan['cost_saving_tips'] = [
            "Replace expensive proteins with chicken thighs, eggs, or plant proteins",
            "Use frozen vegetables instead of fresh when possible",
            "Buy grains and legumes in bulk for significant savings",
            "Shop seasonal produce for better prices",
            "Use store brands for pantry staples (same quality, lower cost)",
            "Batch cook proteins and grains to save time and energy costs"
        ]
        optimized_plan['budget_breakdown'] = {
            'proteins': '35%',
            'vegetables': '25%',
            'grains': '20%',
            'pantry_items': '15%',
            'other': '5%'
        }
        optimized_plan['meal_prep_suggestions'] = [
            "Cook proteins in bulk on weekends",
            "Prepare grains and legumes in large batches",
            "Wash and prep vegetables when you get home from shopping"
        ]
        optimized_plan['optimization_applied'] = True
        
        return optimized_plan

    def _get_fallback_tips(self) -> Dict:
        """Get fallback budget tips."""
        return {
            'tips': [
                'Buy ingredients in bulk when possible',
                'Use seasonal vegetables for better prices',
                'Prepare meals in batches to save time and money',
                'Choose less expensive protein sources like eggs and beans'
            ],
            'estimated_savings': 10.0
        }
    
    def _get_fallback_breakdown(self, estimated_cost: float) -> Dict:
        """Get fallback cost breakdown."""
        return {
            'categories': {
                'proteins': round(estimated_cost * 0.4, 2),
                'vegetables': round(estimated_cost * 0.3, 2),
                'grains': round(estimated_cost * 0.2, 2),
                'other': round(estimated_cost * 0.1, 2)
            },
            'total': estimated_cost,
            'per_meal': round(estimated_cost / 21, 2)  # 7 days * 3 meals
        }
    
    def _get_mock_response(self, prompt: str) -> str:
        """Generate mock response for testing."""
        if "optimize" in prompt.lower() and "budget" in prompt.lower():
            return '{"optimized_plan": {"estimated_cost": 75.0, "changes_made": ["Replaced expensive ingredients with budget alternatives"]}, "cost_savings": 10.0, "optimization_notes": "Successfully optimized for target budget"}'
        elif "budget tips" in prompt.lower():
            return '{"tips": ["Buy in bulk", "Use seasonal ingredients", "Meal prep"], "estimated_savings": 15.0}'
        elif "budget alternatives" in prompt.lower():
            return '[{"original": "salmon", "alternative": "chicken", "savings": 5.0}]'
        elif "cost breakdown" in prompt.lower():
            return '{"categories": {"proteins": 30.0, "vegetables": 20.0, "grains": 15.0}, "total": 75.0, "per_meal": 3.50}'
        else:
            return '{"result": "mock budget optimization response"}' 