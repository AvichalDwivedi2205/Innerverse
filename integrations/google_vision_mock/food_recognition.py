import asyncio
import logging
import random
from typing import Dict, Any, Optional, List
import base64
from datetime import datetime

class MockGoogleVisionAPI:
    """Mock Google Vision API for food recognition demonstration"""
    
    # Mock food database with nutritional information
    FOOD_DATABASE = {
        'apple': {
            'name': 'Apple',
            'category': 'fruit',
            'calories_per_100g': 52,
            'macros': {'carbs': 14, 'protein': 0.3, 'fat': 0.2},
            'confidence': 0.95,
            'typical_serving_g': 150
        },
        'banana': {
            'name': 'Banana',
            'category': 'fruit',
            'calories_per_100g': 89,
            'macros': {'carbs': 23, 'protein': 1.1, 'fat': 0.3},
            'confidence': 0.92,
            'typical_serving_g': 120
        },
        'chicken_breast': {
            'name': 'Chicken Breast',
            'category': 'protein',
            'calories_per_100g': 165,
            'macros': {'carbs': 0, 'protein': 31, 'fat': 3.6},
            'confidence': 0.88,
            'typical_serving_g': 150
        },
        'rice': {
            'name': 'White Rice',
            'category': 'grain',
            'calories_per_100g': 130,
            'macros': {'carbs': 28, 'protein': 2.7, 'fat': 0.3},
            'confidence': 0.85,
            'typical_serving_g': 200
        },
        'broccoli': {
            'name': 'Broccoli',
            'category': 'vegetable',
            'calories_per_100g': 34,
            'macros': {'carbs': 7, 'protein': 2.8, 'fat': 0.4},
            'confidence': 0.90,
            'typical_serving_g': 100
        },
        'salmon': {
            'name': 'Salmon',
            'category': 'protein',
            'calories_per_100g': 208,
            'macros': {'carbs': 0, 'protein': 22, 'fat': 13},
            'confidence': 0.87,
            'typical_serving_g': 150
        },
        'pasta': {
            'name': 'Pasta',
            'category': 'grain',
            'calories_per_100g': 131,
            'macros': {'carbs': 25, 'protein': 5, 'fat': 1.1},
            'confidence': 0.83,
            'typical_serving_g': 200
        },
        'salad': {
            'name': 'Mixed Salad',
            'category': 'vegetable',
            'calories_per_100g': 20,
            'macros': {'carbs': 4, 'protein': 1.5, 'fat': 0.2},
            'confidence': 0.78,
            'typical_serving_g': 150
        }
    }
    
    def __init__(self):
        self.api_calls_count = 0
        logging.info("Mock Google Vision API initialized for food recognition demo")
    
    async def recognize_food_from_image(self, image_data: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Mock food recognition from base64 image data"""
        try:
            self.api_calls_count += 1
            
            # Simulate API processing delay
            await asyncio.sleep(random.uniform(1.0, 2.5))
            
            # Mock recognition - randomly select 1-3 foods for demonstration
            recognized_foods = self._mock_food_recognition()
            
            # Calculate total nutritional information
            total_nutrition = self._calculate_total_nutrition(recognized_foods)
            
            result = {
                'recognition_id': f"mock_recognition_{self.api_calls_count}_{datetime.now().timestamp()}",
                'timestamp': datetime.now().isoformat(),
                'recognized_foods': recognized_foods,
                'total_nutrition': total_nutrition,
                'confidence_score': sum(food['confidence'] for food in recognized_foods) / len(recognized_foods),
                'api_calls_used': self.api_calls_count,
                'processing_time_ms': random.randint(800, 2000)
            }
            
            logging.info(f"Mock food recognition completed: {len(recognized_foods)} items detected")
            return result
            
        except Exception as e:
            logging.error(f"Error in mock food recognition: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _mock_food_recognition(self) -> List[Dict[str, Any]]:
        """Generate mock food recognition results"""
        # Randomly select 1-3 foods for demonstration
        num_foods = random.randint(1, 3)
        selected_foods = random.sample(list(self.FOOD_DATABASE.keys()), num_foods)
        
        recognized_foods = []
        for food_key in selected_foods:
            food_data = self.FOOD_DATABASE[food_key].copy()
            
            # Add some randomness to serving size
            base_serving = food_data['typical_serving_g']
            actual_serving = random.randint(int(base_serving * 0.7), int(base_serving * 1.3))
            
            # Calculate actual nutrition based on serving size
            calories = (food_data['calories_per_100g'] * actual_serving) / 100
            actual_macros = {
                macro: (value * actual_serving) / 100 
                for macro, value in food_data['macros'].items()
            }
            
            recognized_food = {
                'food_id': food_key,
                'name': food_data['name'],
                'category': food_data['category'],
                'confidence': food_data['confidence'] + random.uniform(-0.05, 0.05),  # Add slight variation
                'serving_size_g': actual_serving,
                'calories': round(calories, 1),
                'macros': {k: round(v, 1) for k, v in actual_macros.items()},
                'bounding_box': self._generate_mock_bounding_box()
            }
            
            recognized_foods.append(recognized_food)
        
        return recognized_foods
    
    def _generate_mock_bounding_box(self) -> Dict[str, float]:
        """Generate mock bounding box coordinates"""
        x = random.uniform(0.1, 0.6)
        y = random.uniform(0.1, 0.6)
        width = random.uniform(0.2, 0.4)
        height = random.uniform(0.2, 0.4)
        
        return {
            'x': round(x, 3),
            'y': round(y, 3),
            'width': round(width, 3),
            'height': round(height, 3)
        }
    
    def _calculate_total_nutrition(self, recognized_foods: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate total nutritional information for all recognized foods"""
        total_calories = sum(food['calories'] for food in recognized_foods)
        total_macros = {
            'carbs': sum(food['macros']['carbs'] for food in recognized_foods),
            'protein': sum(food['macros']['protein'] for food in recognized_foods),
            'fat': sum(food['macros']['fat'] for food in recognized_foods)
        }
        
        return {
            'total_calories': round(total_calories, 1),
            'total_macros': {k: round(v, 1) for k, v in total_macros.items()},
            'macro_percentages': {
                'carbs_percent': round((total_macros['carbs'] * 4 / total_calories) * 100, 1) if total_calories > 0 else 0,
                'protein_percent': round((total_macros['protein'] * 4 / total_calories) * 100, 1) if total_calories > 0 else 0,
                'fat_percent': round((total_macros['fat'] * 9 / total_calories) * 100, 1) if total_calories > 0 else 0
            },
            'meal_category': self._determine_meal_category(recognized_foods)
        }
    
    def _determine_meal_category(self, recognized_foods: List[Dict[str, Any]]) -> str:
        """Determine meal category based on recognized foods"""
        categories = [food['category'] for food in recognized_foods]
        
        if 'protein' in categories and 'grain' in categories:
            return 'balanced_meal'
        elif 'fruit' in categories and len(categories) == 1:
            return 'snack'
        elif 'vegetable' in categories and 'protein' in categories:
            return 'healthy_meal'
        else:
            return 'mixed_meal'
    
    async def get_food_suggestions(self, current_nutrition: Dict[str, Any], dietary_goals: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get food suggestions based on current nutrition and goals"""
        try:
            current_calories = current_nutrition.get('total_calories', 0)
            target_calories = dietary_goals.get('target_calories', 2000)
            remaining_calories = target_calories - current_calories
            
            suggestions = []
            
            if remaining_calories > 300:
                suggestions.append({
                    'suggestion': 'Add a protein-rich meal',
                    'foods': ['chicken_breast', 'salmon'],
                    'reason': f'You have {remaining_calories:.0f} calories remaining for the day'
                })
            elif remaining_calories > 100:
                suggestions.append({
                    'suggestion': 'Consider a healthy snack',
                    'foods': ['apple', 'banana'],
                    'reason': 'A light snack would help you reach your calorie goal'
                })
            else:
                suggestions.append({
                    'suggestion': 'You\'re close to your calorie goal',
                    'foods': [],
                    'reason': 'Consider light vegetables if still hungry'
                })
            
            return suggestions
            
        except Exception as e:
            logging.error(f"Error generating food suggestions: {e}")
            return []

# Global mock Google Vision instance
mock_google_vision = MockGoogleVisionAPI()
