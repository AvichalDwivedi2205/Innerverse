"""
Nutrition Agent Tools

Comprehensive tools for meal plan management, user preferences,
nutrition data, and CRUD operations.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid

logger = logging.getLogger(__name__)

class NutritionTools:
    """Tools for nutrition agent data management and operations."""
    
    def __init__(self):
        """Initialize nutrition tools."""
        # Mock storage for development - replace with Firestore in production
        self.user_preferences = {}
        self.meal_plans = {}
        self.nutrition_cache = {}
        
        logger.info("NutritionTools initialized")

    # User Preferences Management
    async def get_user_preferences(self, user_id: str) -> Optional[Dict]:
        """Get user's nutrition preferences."""
        try:
            return self.user_preferences.get(user_id)
        except Exception as e:
            logger.error(f"Error getting user preferences: {str(e)}")
            return None

    async def update_user_preferences(self, user_id: str, preferences: Dict) -> bool:
        """Update user's nutrition preferences."""
        try:
            if user_id not in self.user_preferences:
                self.user_preferences[user_id] = {}
            
            # Merge new preferences with existing ones
            self.user_preferences[user_id].update(preferences)
            
            logger.info(f"Updated preferences for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating user preferences: {str(e)}")
            return False

    async def set_complete_user_preferences(self, user_id: str, preferences: Dict) -> bool:
        """Set complete user preferences (overwrite existing)."""
        try:
            self.user_preferences[user_id] = preferences
            logger.info(f"Set complete preferences for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting user preferences: {str(e)}")
            return False

    # Meal Plan Management
    async def store_meal_plan(self, user_id: str, meal_plan: Dict) -> str:
        """Store a new meal plan for user."""
        try:
            plan_id = str(uuid.uuid4())
            
            meal_plan_data = {
                'plan_id': plan_id,
                'user_id': user_id,
                'meal_plan': meal_plan,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'is_active': True
            }
            
            if user_id not in self.meal_plans:
                self.meal_plans[user_id] = {}
            
            self.meal_plans[user_id][plan_id] = meal_plan_data
            
            logger.info(f"Stored meal plan {plan_id} for user {user_id}")
            return plan_id
        except Exception as e:
            logger.error(f"Error storing meal plan: {str(e)}")
            raise

    async def get_meal_plan(self, user_id: str, plan_id: str) -> Optional[Dict]:
        """Get specific meal plan by ID."""
        try:
            user_plans = self.meal_plans.get(user_id, {})
            plan_data = user_plans.get(plan_id)
            
            if plan_data:
                return plan_data['meal_plan']
            return None
        except Exception as e:
            logger.error(f"Error getting meal plan: {str(e)}")
            return None

    async def update_meal_plan(self, user_id: str, plan_id: str, updated_plan: Dict) -> bool:
        """Update existing meal plan."""
        try:
            if user_id in self.meal_plans and plan_id in self.meal_plans[user_id]:
                self.meal_plans[user_id][plan_id]['meal_plan'] = updated_plan
                self.meal_plans[user_id][plan_id]['updated_at'] = datetime.now().isoformat()
                
                logger.info(f"Updated meal plan {plan_id} for user {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating meal plan: {str(e)}")
            return False

    async def get_user_meal_plans(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get user's meal plans (most recent first)."""
        try:
            user_plans = self.meal_plans.get(user_id, {})
            
            plans = []
            for plan_id, plan_data in user_plans.items():
                plans.append({
                    'plan_id': plan_id,
                    'created_at': plan_data['created_at'],
                    'updated_at': plan_data['updated_at'],
                    'is_active': plan_data['is_active'],
                    'duration_days': plan_data['meal_plan'].get('duration_days', 7),
                    'estimated_cost': plan_data['meal_plan'].get('estimated_cost', 0)
                })
            
            # Sort by creation date (most recent first)
            plans.sort(key=lambda x: x['created_at'], reverse=True)
            
            return plans[:limit]
        except Exception as e:
            logger.error(f"Error getting user meal plans: {str(e)}")
            return []

    async def delete_meal_plan(self, user_id: str, plan_id: str) -> bool:
        """Delete meal plan."""
        try:
            if user_id in self.meal_plans and plan_id in self.meal_plans[user_id]:
                del self.meal_plans[user_id][plan_id]
                logger.info(f"Deleted meal plan {plan_id} for user {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting meal plan: {str(e)}")
            return False

    # Nutrition Data Operations
    async def get_food_nutrition_info(self, food_name: str) -> Dict:
        """Get nutrition information for a specific food."""
        try:
            # Check cache first
            if food_name.lower() in self.nutrition_cache:
                return self.nutrition_cache[food_name.lower()]
            
            # Mock nutrition data - replace with USDA API in production
            mock_nutrition = await self._get_mock_nutrition_data(food_name)
            
            # Cache the result
            self.nutrition_cache[food_name.lower()] = mock_nutrition
            
            return mock_nutrition
        except Exception as e:
            logger.error(f"Error getting nutrition info for {food_name}: {str(e)}")
            return self._get_default_nutrition_data(food_name)

    async def _get_mock_nutrition_data(self, food_name: str) -> Dict:
        """Get mock nutrition data for development."""
        
        # Common foods with approximate nutrition per 100g
        nutrition_db = {
            'chicken breast': {
                'calories': 165,
                'protein': 31,
                'carbs': 0,
                'fat': 3.6,
                'fiber': 0,
                'sugar': 0,
                'sodium': 74,
                'key_nutrients': ['protein', 'niacin', 'phosphorus']
            },
            'salmon': {
                'calories': 208,
                'protein': 22,
                'carbs': 0,
                'fat': 12,
                'fiber': 0,
                'sugar': 0,
                'sodium': 93,
                'key_nutrients': ['omega-3', 'protein', 'vitamin D']
            },
            'broccoli': {
                'calories': 34,
                'protein': 2.8,
                'carbs': 7,
                'fat': 0.4,
                'fiber': 2.6,
                'sugar': 1.5,
                'sodium': 33,
                'key_nutrients': ['vitamin C', 'vitamin K', 'folate']
            },
            'quinoa': {
                'calories': 368,
                'protein': 14,
                'carbs': 64,
                'fat': 6,
                'fiber': 7,
                'sugar': 0,
                'sodium': 5,
                'key_nutrients': ['complete protein', 'fiber', 'iron']
            },
            'avocado': {
                'calories': 160,
                'protein': 2,
                'carbs': 9,
                'fat': 15,
                'fiber': 7,
                'sugar': 0.7,
                'sodium': 7,
                'key_nutrients': ['healthy fats', 'fiber', 'potassium']
            }
        }
        
        # Try to find exact match or similar food
        food_lower = food_name.lower()
        for key, data in nutrition_db.items():
            if key in food_lower or food_lower in key:
                return {
                    'food_name': food_name,
                    'serving_size': '100g',
                    'nutrition': data,
                    'source': 'mock_database'
                }
        
        # Return generic nutrition data if not found
        return self._get_default_nutrition_data(food_name)

    def _get_default_nutrition_data(self, food_name: str) -> Dict:
        """Get default nutrition data for unknown foods."""
        return {
            'food_name': food_name,
            'serving_size': '100g',
            'nutrition': {
                'calories': 150,
                'protein': 5,
                'carbs': 20,
                'fat': 5,
                'fiber': 3,
                'sugar': 5,
                'sodium': 100,
                'key_nutrients': ['varies']
            },
            'source': 'estimated',
            'note': 'Estimated values - actual nutrition may vary'
        }

    async def analyze_daily_nutrition(self, user_id: str, plan_id: str, day_number: int) -> Dict:
        """Analyze nutrition for a specific day in meal plan."""
        try:
            meal_plan = await self.get_meal_plan(user_id, plan_id)
            if not meal_plan:
                return {}
            
            daily_plans = meal_plan.get('daily_plans', {})
            day_data = daily_plans.get(str(day_number), {})
            
            if not day_data:
                return {}
            
            # Calculate total nutrition for the day
            total_nutrition = {
                'calories': 0,
                'protein': 0,
                'carbs': 0,
                'fat': 0,
                'fiber': 0,
                'sugar': 0,
                'sodium': 0
            }
            
            meals = ['breakfast', 'morning_snack', 'lunch', 'afternoon_snack', 'dinner']
            meal_breakdown = {}
            
            for meal in meals:
                if meal in day_data:
                    meal_data = day_data[meal]
                    # Mock nutrition calculation - in production, sum up ingredient nutrition
                    meal_nutrition = await self._estimate_meal_nutrition(meal_data)
                    meal_breakdown[meal] = meal_nutrition
                    
                    # Add to daily totals
                    for nutrient in total_nutrition:
                        total_nutrition[nutrient] += meal_nutrition.get(nutrient, 0)
            
            return {
                'day_number': day_number,
                'total_nutrition': total_nutrition,
                'meal_breakdown': meal_breakdown,
                'nutrition_goals_met': self._check_nutrition_goals(total_nutrition),
                'recommendations': self._generate_nutrition_recommendations(total_nutrition)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing daily nutrition: {str(e)}")
            return {}

    async def _estimate_meal_nutrition(self, meal_data: Dict) -> Dict:
        """Estimate nutrition for a meal based on ingredients."""
        
        # Mock estimation - in production, sum up all ingredient nutrition
        meal_name = meal_data.get('name', '').lower()
        
        # Basic estimates based on meal type
        if 'salad' in meal_name:
            return {'calories': 200, 'protein': 8, 'carbs': 15, 'fat': 12, 'fiber': 6, 'sugar': 8, 'sodium': 300}
        elif 'chicken' in meal_name:
            return {'calories': 350, 'protein': 35, 'carbs': 10, 'fat': 15, 'fiber': 2, 'sugar': 3, 'sodium': 400}
        elif 'pasta' in meal_name:
            return {'calories': 400, 'protein': 15, 'carbs': 60, 'fat': 12, 'fiber': 4, 'sugar': 5, 'sodium': 500}
        elif 'smoothie' in meal_name:
            return {'calories': 250, 'protein': 10, 'carbs': 35, 'fat': 8, 'fiber': 5, 'sugar': 25, 'sodium': 100}
        else:
            return {'calories': 300, 'protein': 15, 'carbs': 30, 'fat': 12, 'fiber': 4, 'sugar': 8, 'sodium': 350}

    def _check_nutrition_goals(self, total_nutrition: Dict) -> Dict:
        """Check if daily nutrition meets general goals."""
        
        # General daily targets for average adult
        targets = {
            'calories': 2000,
            'protein': 50,  # grams
            'fiber': 25,    # grams
            'sodium': 2300  # mg (max)
        }
        
        goals_met = {}
        for nutrient, target in targets.items():
            actual = total_nutrition.get(nutrient, 0)
            if nutrient == 'sodium':
                goals_met[nutrient] = actual <= target
            else:
                goals_met[nutrient] = actual >= target * 0.8  # 80% of target is good
        
        return goals_met

    def _generate_nutrition_recommendations(self, total_nutrition: Dict) -> List[str]:
        """Generate nutrition recommendations based on daily totals."""
        
        recommendations = []
        
        if total_nutrition.get('protein', 0) < 40:
            recommendations.append("Consider adding more protein-rich foods like lean meats, beans, or Greek yogurt")
        
        if total_nutrition.get('fiber', 0) < 20:
            recommendations.append("Increase fiber intake with more vegetables, fruits, and whole grains")
        
        if total_nutrition.get('sodium', 0) > 2500:
            recommendations.append("Try to reduce sodium by using herbs and spices instead of salt")
        
        if total_nutrition.get('calories', 0) < 1500:
            recommendations.append("Consider adding healthy snacks to meet your energy needs")
        
        if not recommendations:
            recommendations.append("Great job! Your nutrition looks well-balanced for today")
        
        return recommendations

    # Recipe and Meal Management
    async def get_recipe_details(self, user_id: str, plan_id: str, meal_name: str) -> Dict:
        """Get detailed recipe for a specific meal."""
        try:
            meal_plan = await self.get_meal_plan(user_id, plan_id)
            if not meal_plan:
                return {}
            
            # Search through all days for the meal
            daily_plans = meal_plan.get('daily_plans', {})
            
            for day_num, day_data in daily_plans.items():
                for meal_type, meal_data in day_data.items():
                    if meal_data.get('name', '').lower() == meal_name.lower():
                        return {
                            'meal_name': meal_data.get('name'),
                            'ingredients': meal_data.get('ingredients', []),
                            'recipe': meal_data.get('simple_recipe', 'Recipe not available'),
                            'prep_time': meal_data.get('prep_time', '15 min'),
                            'nutrition_highlights': meal_data.get('nutrition_highlights', []),
                            'day': day_num,
                            'meal_type': meal_type
                        }
            
            return {}
        except Exception as e:
            logger.error(f"Error getting recipe details: {str(e)}")
            return {}

    async def save_favorite_meal(self, user_id: str, meal_data: Dict) -> bool:
        """Save a meal as user's favorite."""
        try:
            # Mock implementation - in production, save to user's favorites
            logger.info(f"Saved favorite meal for user {user_id}: {meal_data.get('name')}")
            return True
        except Exception as e:
            logger.error(f"Error saving favorite meal: {str(e)}")
            return False

    async def get_user_favorites(self, user_id: str) -> List[Dict]:
        """Get user's favorite meals."""
        try:
            # Mock implementation - return empty list for now
            return []
        except Exception as e:
            logger.error(f"Error getting user favorites: {str(e)}")
            return []

    # Utility Methods
    async def calculate_estimated_cost(self, meal_plan: Dict, budget_level: str) -> float:
        """Calculate estimated cost for meal plan."""
        try:
            # Mock cost calculation based on budget level
            duration_days = meal_plan.get('duration_days', 7)
            
            cost_per_day = {
                'low': 7.0,      # $50/week ÷ 7 days
                'medium': 14.0,  # $100/week ÷ 7 days  
                'high': 28.0     # $200/week ÷ 7 days
            }
            
            daily_cost = cost_per_day.get(budget_level, 14.0)
            total_cost = daily_cost * duration_days
            
            return round(total_cost, 2)
        except Exception as e:
            logger.error(f"Error calculating estimated cost: {str(e)}")
            return 0.0

    async def generate_shopping_list(self, user_id: str, plan_id: str) -> Dict:
        """Generate shopping list for meal plan."""
        try:
            meal_plan = await self.get_meal_plan(user_id, plan_id)
            if not meal_plan:
                return {}
            
            # Mock shopping list generation
            shopping_list = {
                'proteins': ['chicken breast (2 lbs)', 'salmon fillet (1 lb)', 'eggs (1 dozen)'],
                'vegetables': ['broccoli (2 heads)', 'spinach (1 bag)', 'bell peppers (3)'],
                'grains': ['quinoa (1 bag)', 'brown rice (1 bag)', 'whole wheat bread (1 loaf)'],
                'dairy': ['Greek yogurt (1 container)', 'cheese (1 block)', 'milk (1 gallon)'],
                'pantry': ['olive oil', 'garlic', 'onions', 'herbs & spices'],
                'estimated_total': meal_plan.get('estimated_cost', 100)
            }
            
            return shopping_list
        except Exception as e:
            logger.error(f"Error generating shopping list: {str(e)}")
            return {} 