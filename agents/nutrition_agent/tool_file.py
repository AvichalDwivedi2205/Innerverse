import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from config.firebase_config import firebase_config
from integrations.google_vision_mock.food_recognition import mock_google_vision

class USDAFoodDatabaseTool:
    """Mock USDA Food Database integration for nutritional information"""
    
    def __init__(self):
        # Mock USDA food database
        self.food_database = {
            'chicken_breast': {
                'name': 'Chicken Breast, Skinless',
                'calories_per_100g': 165,
                'protein': 31.0,
                'carbs': 0.0,
                'fat': 3.6,
                'fiber': 0.0,
                'category': 'Poultry'
            },
            'brown_rice': {
                'name': 'Brown Rice, Cooked',
                'calories_per_100g': 112,
                'protein': 2.6,
                'carbs': 23.0,
                'fat': 0.9,
                'fiber': 1.8,
                'category': 'Grains'
            },
            'broccoli': {
                'name': 'Broccoli, Raw',
                'calories_per_100g': 34,
                'protein': 2.8,
                'carbs': 7.0,
                'fat': 0.4,
                'fiber': 2.6,
                'category': 'Vegetables'
            },
            'salmon': {
                'name': 'Atlantic Salmon',
                'calories_per_100g': 208,
                'protein': 22.0,
                'carbs': 0.0,
                'fat': 13.0,
                'fiber': 0.0,
                'category': 'Fish'
            },
            'greek_yogurt': {
                'name': 'Greek Yogurt, Plain',
                'calories_per_100g': 59,
                'protein': 10.0,
                'carbs': 3.6,
                'fat': 0.4,
                'fiber': 0.0,
                'category': 'Dairy'
            }
        }
    
    async def search_food(self, food_name: str) -> Optional[Dict[str, Any]]:
        """Search for food in mock USDA database"""
        try:
            # Simple search - normalize food name
            normalized_name = food_name.lower().replace(' ', '_')
            
            # Direct lookup
            if normalized_name in self.food_database:
                return self.food_database[normalized_name]
            
            # Partial matching
            for key, food_data in self.food_database.items():
                if normalized_name in key or any(word in key for word in normalized_name.split('_')):
                    return food_data
            
            # Return None if not found
            return None
            
        except Exception as e:
            logging.error(f"Error searching food database: {e}")
            return None
    
    async def get_nutritional_info(self, food_name: str, serving_size_g: float = 100.0) -> Dict[str, Any]:
        """Get detailed nutritional information for a food item"""
        try:
            food_data = await self.search_food(food_name)
            
            if not food_data:
                return {'error': f'Food "{food_name}" not found in database'}
            
            # Calculate nutrition based on serving size
            serving_ratio = serving_size_g / 100.0
            
            nutritional_info = {
                'food_name': food_data['name'],
                'serving_size_g': serving_size_g,
                'calories': round(food_data['calories_per_100g'] * serving_ratio, 1),
                'macronutrients': {
                    'protein': round(food_data['protein'] * serving_ratio, 1),
                    'carbohydrates': round(food_data['carbs'] * serving_ratio, 1),
                    'fat': round(food_data['fat'] * serving_ratio, 1),
                    'fiber': round(food_data['fiber'] * serving_ratio, 1)
                },
                'category': food_data['category'],
                'per_100g_data': food_data
            }
            
            return nutritional_info
            
        except Exception as e:
            logging.error(f"Error getting nutritional info: {e}")
            return {'error': str(e)}
    
    async def calculate_meal_nutrition(self, meal_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate total nutrition for a meal"""
        try:
            total_nutrition = {
                'total_calories': 0.0,
                'total_protein': 0.0,
                'total_carbs': 0.0,
                'total_fat': 0.0,
                'total_fiber': 0.0,
                'items': []
            }
            
            for item in meal_items:
                food_name = item.get('food_name', '')
                serving_size = item.get('serving_size_g', 100.0)
                
                nutrition_info = await self.get_nutritional_info(food_name, serving_size)
                
                if 'error' not in nutrition_info:
                    total_nutrition['total_calories'] += nutrition_info['calories']
                    total_nutrition['total_protein'] += nutrition_info['macronutrients']['protein']
                    total_nutrition['total_carbs'] += nutrition_info['macronutrients']['carbohydrates']
                    total_nutrition['total_fat'] += nutrition_info['macronutrients']['fat']
                    total_nutrition['total_fiber'] += nutrition_info['macronutrients']['fiber']
                    total_nutrition['items'].append(nutrition_info)
            
            # Round totals
            for key in ['total_calories', 'total_protein', 'total_carbs', 'total_fat', 'total_fiber']:
                total_nutrition[key] = round(total_nutrition[key], 1)
            
            return total_nutrition
            
        except Exception as e:
            logging.error(f"Error calculating meal nutrition: {e}")
            return {'error': str(e)}

class FoodImageAnalysisTool:
    """Tool for analyzing food images using mock Google Vision API"""
    
    def __init__(self):
        self.vision_api = mock_google_vision
        self.usda_tool = USDAFoodDatabaseTool()
    
    async def analyze_food_image(self, image_data: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze food image and provide nutritional information"""
        try:
            # Use mock Google Vision API for food recognition
            recognition_result = await self.vision_api.recognize_food_from_image(image_data, user_context)
            
            # Enhance with USDA database information
            enhanced_results = await self._enhance_with_usda_data(recognition_result)
            
            # Generate nutritional recommendations
            recommendations = await self._generate_nutritional_recommendations(
                enhanced_results, user_context
            )
            
            return {
                'recognition_result': enhanced_results,
                'nutritional_recommendations': recommendations,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error analyzing food image: {e}")
            return {'error': str(e)}
    
    async def _enhance_with_usda_data(self, recognition_result: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance recognition results with USDA database data"""
        try:
            recognized_foods = recognition_result.get('recognized_foods', [])
            enhanced_foods = []
            
            for food in recognized_foods:
                food_name = food.get('name', '')
                serving_size = food.get('serving_size_g', 100)
                
                # Get detailed USDA data
                usda_data = await self.usda_tool.get_nutritional_info(food_name, serving_size)
                
                if 'error' not in usda_data:
                    enhanced_food = {
                        **food,
                        'detailed_nutrition': usda_data,
                        'usda_verified': True
                    }
                else:
                    enhanced_food = {
                        **food,
                        'usda_verified': False,
                        'note': 'Using estimated nutritional data'
                    }
                
                enhanced_foods.append(enhanced_food)
            
            enhanced_result = recognition_result.copy()
            enhanced_result['recognized_foods'] = enhanced_foods
            
            return enhanced_result
            
        except Exception as e:
            logging.error(f"Error enhancing with USDA data: {e}")
            return recognition_result
    
    async def _generate_nutritional_recommendations(self, analysis_result: Dict[str, Any], 
                                                  user_context: Dict[str, Any]) -> List[str]:
        """Generate nutritional recommendations based on analysis"""
        recommendations = []
        
        total_nutrition = analysis_result.get('total_nutrition', {})
        total_calories = total_nutrition.get('total_calories', 0)
        
        # Basic recommendations based on calorie content
        if total_calories > 600:
            recommendations.append("This appears to be a high-calorie meal. Consider smaller portions if weight management is a goal.")
        elif total_calories < 200:
            recommendations.append("This is a light meal. You might want to add some protein or healthy fats for satiety.")
        
        # Macronutrient recommendations
        macro_percentages = total_nutrition.get('macro_percentages', {})
        protein_percent = macro_percentages.get('protein_percent', 0)
        
        if protein_percent < 15:
            recommendations.append("Consider adding more protein to this meal for better satiety and muscle support.")
        
        return recommendations

class MealPlanStorageTool:
    """Tool for storing and retrieving meal plans from Firebase"""
    
    def __init__(self):
        self.firebase_db = firebase_config.get_firestore_client()
    
    async def store_meal_plan(self, user_id: str, meal_plan: Dict[str, Any]) -> str:
        """Store meal plan in Firebase"""
        try:
            plan_doc = {
                'user_id': user_id,
                'meal_plan': meal_plan,
                'created_at': datetime.now(),
                'active': True,
                'version': 1
            }
            
            doc_ref = self.firebase_db.collection('meal_plans').add(plan_doc)
            plan_id = doc_ref[1].id
            
            logging.info(f"Stored meal plan {plan_id} for user {user_id}")
            return plan_id
            
        except Exception as e:
            logging.error(f"Error storing meal plan: {e}")
            return f"error_{datetime.now().timestamp()}"
    
    async def get_user_meal_plans(self, user_id: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get user's meal plans from Firebase"""
        try:
            query = self.firebase_db.collection('meal_plans').where('user_id', '==', user_id)
            
            if active_only:
                query = query.where('active', '==', True)
            
            docs = await asyncio.to_thread(query.get)
            
            meal_plans = []
            for doc in docs:
                plan_data = doc.to_dict()
                plan_data['plan_id'] = doc.id
                meal_plans.append(plan_data)
            
            return meal_plans
            
        except Exception as e:
            logging.error(f"Error getting user meal plans: {e}")
            return []
    
    async def update_meal_plan(self, plan_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing meal plan"""
        try:
            update_data = {
                **updates,
                'updated_at': datetime.now(),
                'version': firestore.Increment(1)
            }
            
            self.firebase_db.collection('meal_plans').document(plan_id).update(update_data)
            
            logging.info(f"Updated meal plan {plan_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error updating meal plan: {e}")
            return False

# Initialize tool instances
usda_food_tool = USDAFoodDatabaseTool()
food_image_tool = FoodImageAnalysisTool()
meal_plan_storage_tool = MealPlanStorageTool()
