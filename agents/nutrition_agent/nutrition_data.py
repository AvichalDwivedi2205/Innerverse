"""
Nutrition Data Service

Service for retrieving nutrition information, analyzing food data,
and providing nutritional insights for meal planning.
"""

import json
import logging
from typing import Dict, List, Optional, Any
import asyncio

logger = logging.getLogger(__name__)

class NutritionDataService:
    """Service for nutrition data retrieval and analysis."""
    
    def __init__(self):
        """Initialize nutrition data service."""
        self.nutrition_cache = {}
        self.food_database = self._initialize_food_database()
        logger.info("NutritionDataService initialized")

    def _initialize_food_database(self) -> Dict:
        """Initialize comprehensive food nutrition database."""
        
        return {
            # Proteins
            'chicken_breast': {
                'name': 'Chicken Breast (skinless)',
                'category': 'protein',
                'nutrition_per_100g': {
                    'calories': 165,
                    'protein': 31.0,
                    'carbs': 0.0,
                    'fat': 3.6,
                    'fiber': 0.0,
                    'sugar': 0.0,
                    'sodium': 74,
                    'cholesterol': 85,
                    'saturated_fat': 1.0
                },
                'key_nutrients': ['protein', 'niacin', 'phosphorus', 'selenium'],
                'health_benefits': ['lean protein', 'muscle building', 'weight management'],
                'cooking_methods': ['grilled', 'baked', 'sautéed', 'poached'],
                'cost_category': 'medium',
                'shelf_life': '2-3 days fresh, 6 months frozen'
            },
            'salmon': {
                'name': 'Atlantic Salmon',
                'category': 'protein',
                'nutrition_per_100g': {
                    'calories': 208,
                    'protein': 22.0,
                    'carbs': 0.0,
                    'fat': 12.4,
                    'fiber': 0.0,
                    'sugar': 0.0,
                    'sodium': 93,
                    'cholesterol': 55,
                    'saturated_fat': 3.1
                },
                'key_nutrients': ['omega-3 fatty acids', 'protein', 'vitamin D', 'B12'],
                'health_benefits': ['heart health', 'brain function', 'anti-inflammatory'],
                'cooking_methods': ['baked', 'grilled', 'pan-seared', 'poached'],
                'cost_category': 'high',
                'shelf_life': '1-2 days fresh, 3 months frozen'
            },
            'tofu': {
                'name': 'Firm Tofu',
                'category': 'protein',
                'nutrition_per_100g': {
                    'calories': 144,
                    'protein': 17.3,
                    'carbs': 2.8,
                    'fat': 8.7,
                    'fiber': 2.3,
                    'sugar': 0.6,
                    'sodium': 7,
                    'cholesterol': 0,
                    'saturated_fat': 1.3
                },
                'key_nutrients': ['complete protein', 'isoflavones', 'calcium', 'iron'],
                'health_benefits': ['plant protein', 'heart health', 'bone health'],
                'cooking_methods': ['stir-fried', 'baked', 'grilled', 'scrambled'],
                'cost_category': 'low',
                'shelf_life': '5-7 days opened, 3-5 days cooked'
            },
            'eggs': {
                'name': 'Large Eggs',
                'category': 'protein',
                'nutrition_per_100g': {
                    'calories': 155,
                    'protein': 13.0,
                    'carbs': 1.1,
                    'fat': 11.0,
                    'fiber': 0.0,
                    'sugar': 1.1,
                    'sodium': 124,
                    'cholesterol': 373,
                    'saturated_fat': 3.1
                },
                'key_nutrients': ['complete protein', 'choline', 'vitamin D', 'B12'],
                'health_benefits': ['brain health', 'eye health', 'muscle building'],
                'cooking_methods': ['scrambled', 'boiled', 'poached', 'baked'],
                'cost_category': 'low',
                'shelf_life': '3-5 weeks refrigerated'
            },
            
            # Vegetables
            'broccoli': {
                'name': 'Fresh Broccoli',
                'category': 'vegetable',
                'nutrition_per_100g': {
                    'calories': 34,
                    'protein': 2.8,
                    'carbs': 6.6,
                    'fat': 0.4,
                    'fiber': 2.6,
                    'sugar': 1.5,
                    'sodium': 33,
                    'cholesterol': 0,
                    'saturated_fat': 0.1
                },
                'key_nutrients': ['vitamin C', 'vitamin K', 'folate', 'fiber'],
                'health_benefits': ['immune support', 'bone health', 'antioxidants'],
                'cooking_methods': ['steamed', 'roasted', 'stir-fried', 'raw'],
                'cost_category': 'low',
                'shelf_life': '3-5 days fresh'
            },
            'spinach': {
                'name': 'Fresh Spinach',
                'category': 'vegetable',
                'nutrition_per_100g': {
                    'calories': 23,
                    'protein': 2.9,
                    'carbs': 3.6,
                    'fat': 0.4,
                    'fiber': 2.2,
                    'sugar': 0.4,
                    'sodium': 79,
                    'cholesterol': 0,
                    'saturated_fat': 0.1
                },
                'key_nutrients': ['iron', 'folate', 'vitamin K', 'vitamin A'],
                'health_benefits': ['blood health', 'eye health', 'bone health'],
                'cooking_methods': ['sautéed', 'steamed', 'raw', 'wilted'],
                'cost_category': 'low',
                'shelf_life': '5-7 days fresh'
            },
            'sweet_potato': {
                'name': 'Sweet Potato',
                'category': 'vegetable',
                'nutrition_per_100g': {
                    'calories': 86,
                    'protein': 1.6,
                    'carbs': 20.1,
                    'fat': 0.1,
                    'fiber': 3.0,
                    'sugar': 4.2,
                    'sodium': 5,
                    'cholesterol': 0,
                    'saturated_fat': 0.0
                },
                'key_nutrients': ['beta-carotene', 'vitamin A', 'fiber', 'potassium'],
                'health_benefits': ['eye health', 'immune support', 'heart health'],
                'cooking_methods': ['baked', 'roasted', 'mashed', 'steamed'],
                'cost_category': 'low',
                'shelf_life': '1-2 weeks stored properly'
            },
            
            # Grains
            'quinoa': {
                'name': 'Cooked Quinoa',
                'category': 'grain',
                'nutrition_per_100g': {
                    'calories': 120,
                    'protein': 4.4,
                    'carbs': 21.8,
                    'fat': 1.9,
                    'fiber': 2.8,
                    'sugar': 0.9,
                    'sodium': 7,
                    'cholesterol': 0,
                    'saturated_fat': 0.2
                },
                'key_nutrients': ['complete protein', 'fiber', 'iron', 'magnesium'],
                'health_benefits': ['complete amino acids', 'gluten-free', 'heart health'],
                'cooking_methods': ['boiled', 'steamed', 'pilaf', 'salad'],
                'cost_category': 'medium',
                'shelf_life': '3-5 days cooked, 2-3 years dry'
            },
            'brown_rice': {
                'name': 'Cooked Brown Rice',
                'category': 'grain',
                'nutrition_per_100g': {
                    'calories': 112,
                    'protein': 2.6,
                    'carbs': 22.9,
                    'fat': 0.9,
                    'fiber': 1.8,
                    'sugar': 0.4,
                    'sodium': 5,
                    'cholesterol': 0,
                    'saturated_fat': 0.2
                },
                'key_nutrients': ['fiber', 'manganese', 'selenium', 'magnesium'],
                'health_benefits': ['heart health', 'digestive health', 'energy'],
                'cooking_methods': ['boiled', 'steamed', 'pilaf', 'fried'],
                'cost_category': 'low',
                'shelf_life': '4-6 days cooked, 6 months dry'
            },
            'oats': {
                'name': 'Rolled Oats',
                'category': 'grain',
                'nutrition_per_100g': {
                    'calories': 389,
                    'protein': 16.9,
                    'carbs': 66.3,
                    'fat': 6.9,
                    'fiber': 10.6,
                    'sugar': 0.0,
                    'sodium': 2,
                    'cholesterol': 0,
                    'saturated_fat': 1.2
                },
                'key_nutrients': ['beta-glucan fiber', 'protein', 'manganese', 'phosphorus'],
                'health_benefits': ['cholesterol reduction', 'heart health', 'satiety'],
                'cooking_methods': ['porridge', 'overnight oats', 'baked', 'smoothies'],
                'cost_category': 'low',
                'shelf_life': '2 years dry storage'
            },
            
            # Fruits
            'banana': {
                'name': 'Medium Banana',
                'category': 'fruit',
                'nutrition_per_100g': {
                    'calories': 89,
                    'protein': 1.1,
                    'carbs': 22.8,
                    'fat': 0.3,
                    'fiber': 2.6,
                    'sugar': 12.2,
                    'sodium': 1,
                    'cholesterol': 0,
                    'saturated_fat': 0.1
                },
                'key_nutrients': ['potassium', 'vitamin B6', 'vitamin C', 'fiber'],
                'health_benefits': ['heart health', 'muscle function', 'energy'],
                'cooking_methods': ['raw', 'smoothies', 'baked', 'grilled'],
                'cost_category': 'low',
                'shelf_life': '2-7 days depending on ripeness'
            },
            'blueberries': {
                'name': 'Fresh Blueberries',
                'category': 'fruit',
                'nutrition_per_100g': {
                    'calories': 57,
                    'protein': 0.7,
                    'carbs': 14.5,
                    'fat': 0.3,
                    'fiber': 2.4,
                    'sugar': 10.0,
                    'sodium': 1,
                    'cholesterol': 0,
                    'saturated_fat': 0.1
                },
                'key_nutrients': ['antioxidants', 'vitamin C', 'vitamin K', 'manganese'],
                'health_benefits': ['brain health', 'antioxidant protection', 'heart health'],
                'cooking_methods': ['raw', 'smoothies', 'baked', 'compotes'],
                'cost_category': 'medium',
                'shelf_life': '1-2 weeks refrigerated'
            },
            'avocado': {
                'name': 'Medium Avocado',
                'category': 'fruit',
                'nutrition_per_100g': {
                    'calories': 160,
                    'protein': 2.0,
                    'carbs': 8.5,
                    'fat': 14.7,
                    'fiber': 6.7,
                    'sugar': 0.7,
                    'sodium': 7,
                    'cholesterol': 0,
                    'saturated_fat': 2.1
                },
                'key_nutrients': ['healthy fats', 'fiber', 'potassium', 'folate'],
                'health_benefits': ['heart health', 'nutrient absorption', 'satiety'],
                'cooking_methods': ['raw', 'grilled', 'baked', 'mashed'],
                'cost_category': 'medium',
                'shelf_life': '3-7 days depending on ripeness'
            },
            
            # Legumes
            'black_beans': {
                'name': 'Cooked Black Beans',
                'category': 'legume',
                'nutrition_per_100g': {
                    'calories': 132,
                    'protein': 8.9,
                    'carbs': 23.7,
                    'fat': 0.5,
                    'fiber': 8.7,
                    'sugar': 0.3,
                    'sodium': 2,
                    'cholesterol': 0,
                    'saturated_fat': 0.1
                },
                'key_nutrients': ['fiber', 'protein', 'folate', 'iron'],
                'health_benefits': ['digestive health', 'blood sugar control', 'heart health'],
                'cooking_methods': ['boiled', 'pressure cooked', 'stewed', 'salads'],
                'cost_category': 'low',
                'shelf_life': '3-5 days cooked, 2-3 years dry'
            },
            'lentils': {
                'name': 'Cooked Lentils',
                'category': 'legume',
                'nutrition_per_100g': {
                    'calories': 116,
                    'protein': 9.0,
                    'carbs': 20.1,
                    'fat': 0.4,
                    'fiber': 7.9,
                    'sugar': 1.8,
                    'sodium': 2,
                    'cholesterol': 0,
                    'saturated_fat': 0.1
                },
                'key_nutrients': ['protein', 'fiber', 'folate', 'iron'],
                'health_benefits': ['heart health', 'blood sugar control', 'digestive health'],
                'cooking_methods': ['boiled', 'stewed', 'curries', 'soups'],
                'cost_category': 'low',
                'shelf_life': '3-5 days cooked, 2-3 years dry'
            }
        }

    async def get_food_nutrition_info(self, food_name: str) -> Dict:
        """Get comprehensive nutrition information for a food."""
        
        try:
            # Normalize food name for lookup
            normalized_name = self._normalize_food_name(food_name)
            
            # Check cache first
            if normalized_name in self.nutrition_cache:
                return self.nutrition_cache[normalized_name]
            
            # Look up in database
            if normalized_name in self.food_database:
                nutrition_info = self.food_database[normalized_name].copy()
                nutrition_info['source'] = 'internal_database'
                nutrition_info['lookup_name'] = food_name
                
                # Cache the result
                self.nutrition_cache[normalized_name] = nutrition_info
                return nutrition_info
            
            # If not found, try fuzzy matching
            fuzzy_match = self._find_fuzzy_match(normalized_name)
            if fuzzy_match:
                nutrition_info = self.food_database[fuzzy_match].copy()
                nutrition_info['source'] = 'fuzzy_match'
                nutrition_info['original_query'] = food_name
                nutrition_info['matched_food'] = fuzzy_match
                
                # Cache the result
                self.nutrition_cache[normalized_name] = nutrition_info
                return nutrition_info
            
            # If still not found, return estimated data
            return await self._get_estimated_nutrition_data(food_name)
            
        except Exception as e:
            logger.error(f"Error getting nutrition info for {food_name}: {str(e)}")
            return self._get_default_nutrition_data(food_name)

    def _normalize_food_name(self, food_name: str) -> str:
        """Normalize food name for database lookup."""
        
        # Convert to lowercase and replace spaces with underscores
        normalized = food_name.lower().strip()
        normalized = normalized.replace(' ', '_')
        normalized = normalized.replace('-', '_')
        
        # Remove common descriptors
        descriptors_to_remove = [
            'fresh', 'frozen', 'canned', 'organic', 'raw', 'cooked',
            'grilled', 'baked', 'steamed', 'roasted', 'medium', 'large', 'small'
        ]
        
        for descriptor in descriptors_to_remove:
            normalized = normalized.replace(f'_{descriptor}', '')
            normalized = normalized.replace(f'{descriptor}_', '')
        
        return normalized

    def _find_fuzzy_match(self, food_name: str) -> Optional[str]:
        """Find fuzzy match for food name in database."""
        
        # Simple fuzzy matching - check if food name contains any database keys
        for db_key in self.food_database.keys():
            if food_name in db_key or db_key in food_name:
                return db_key
        
        # Check for common synonyms
        synonyms = {
            'chicken': 'chicken_breast',
            'fish': 'salmon',
            'rice': 'brown_rice',
            'beans': 'black_beans',
            'greens': 'spinach',
            'berries': 'blueberries'
        }
        
        for synonym, db_key in synonyms.items():
            if synonym in food_name:
                return db_key
        
        return None

    async def _get_estimated_nutrition_data(self, food_name: str) -> Dict:
        """Get estimated nutrition data for unknown foods."""
        
        # Categorize food and provide estimated nutrition
        category = self._categorize_unknown_food(food_name)
        
        estimated_nutrition = {
            'protein': {
                'calories': 180, 'protein': 25, 'carbs': 2, 'fat': 8,
                'fiber': 0, 'sugar': 0, 'sodium': 100
            },
            'vegetable': {
                'calories': 30, 'protein': 2, 'carbs': 6, 'fat': 0.3,
                'fiber': 3, 'sugar': 3, 'sodium': 20
            },
            'fruit': {
                'calories': 60, 'protein': 1, 'carbs': 15, 'fat': 0.2,
                'fiber': 3, 'sugar': 12, 'sodium': 2
            },
            'grain': {
                'calories': 130, 'protein': 4, 'carbs': 25, 'fat': 1.5,
                'fiber': 3, 'sugar': 1, 'sodium': 5
            },
            'dairy': {
                'calories': 120, 'protein': 8, 'carbs': 9, 'fat': 5,
                'fiber': 0, 'sugar': 9, 'sodium': 120
            }
        }
        
        nutrition = estimated_nutrition.get(category, estimated_nutrition['protein'])
        
        return {
            'name': food_name,
            'category': category,
            'nutrition_per_100g': nutrition,
            'key_nutrients': ['varies'],
            'health_benefits': ['varies based on food type'],
            'cooking_methods': ['varies'],
            'cost_category': 'medium',
            'shelf_life': 'varies',
            'source': 'estimated',
            'note': 'Estimated values - actual nutrition may vary significantly'
        }

    def _categorize_unknown_food(self, food_name: str) -> str:
        """Categorize unknown food based on name."""
        
        food_lower = food_name.lower()
        
        # Protein keywords
        protein_keywords = [
            'chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'turkey',
            'tofu', 'tempeh', 'eggs', 'cheese', 'yogurt', 'meat'
        ]
        
        # Vegetable keywords
        vegetable_keywords = [
            'broccoli', 'spinach', 'kale', 'carrot', 'pepper', 'tomato',
            'onion', 'garlic', 'lettuce', 'cucumber', 'zucchini', 'cabbage'
        ]
        
        # Fruit keywords
        fruit_keywords = [
            'apple', 'banana', 'orange', 'berry', 'grape', 'melon',
            'peach', 'pear', 'cherry', 'mango', 'pineapple', 'citrus'
        ]
        
        # Grain keywords
        grain_keywords = [
            'rice', 'quinoa', 'oats', 'wheat', 'barley', 'pasta',
            'bread', 'cereal', 'grain', 'flour'
        ]
        
        # Check categories
        for keyword in protein_keywords:
            if keyword in food_lower:
                return 'protein'
        
        for keyword in vegetable_keywords:
            if keyword in food_lower:
                return 'vegetable'
        
        for keyword in fruit_keywords:
            if keyword in food_lower:
                return 'fruit'
        
        for keyword in grain_keywords:
            if keyword in food_lower:
                return 'grain'
        
        return 'protein'  # Default to protein

    def _get_default_nutrition_data(self, food_name: str) -> Dict:
        """Get default nutrition data for fallback."""
        
        return {
            'name': food_name,
            'category': 'unknown',
            'nutrition_per_100g': {
                'calories': 150,
                'protein': 5,
                'carbs': 20,
                'fat': 5,
                'fiber': 3,
                'sugar': 5,
                'sodium': 100,
                'cholesterol': 0,
                'saturated_fat': 1
            },
            'key_nutrients': ['varies'],
            'health_benefits': ['varies'],
            'cooking_methods': ['varies'],
            'cost_category': 'medium',
            'shelf_life': 'varies',
            'source': 'default',
            'note': 'Default values used - actual nutrition may vary significantly'
        }

    async def analyze_meal_nutrition(self, meal_ingredients: List[str], serving_size: str = "1 serving") -> Dict:
        """Analyze nutrition for a complete meal."""
        
        try:
            total_nutrition = {
                'calories': 0,
                'protein': 0,
                'carbs': 0,
                'fat': 0,
                'fiber': 0,
                'sugar': 0,
                'sodium': 0
            }
            
            ingredient_breakdown = []
            
            for ingredient in meal_ingredients:
                nutrition_info = await self.get_food_nutrition_info(ingredient)
                nutrition_per_100g = nutrition_info.get('nutrition_per_100g', {})
                
                # Estimate portion size (this is simplified - in production, would need better portion estimation)
                estimated_portion = self._estimate_ingredient_portion(ingredient)
                
                # Calculate nutrition for estimated portion
                portion_nutrition = {}
                for nutrient, value in nutrition_per_100g.items():
                    if isinstance(value, (int, float)):
                        portion_nutrition[nutrient] = value * (estimated_portion / 100)
                        if nutrient in total_nutrition:
                            total_nutrition[nutrient] += portion_nutrition[nutrient]
                
                ingredient_breakdown.append({
                    'ingredient': ingredient,
                    'estimated_portion': f"{estimated_portion}g",
                    'nutrition': portion_nutrition,
                    'key_nutrients': nutrition_info.get('key_nutrients', [])
                })
            
            # Calculate nutrition density and quality scores
            nutrition_quality = self._calculate_nutrition_quality(total_nutrition)
            
            return {
                'total_nutrition': total_nutrition,
                'ingredient_breakdown': ingredient_breakdown,
                'nutrition_quality': nutrition_quality,
                'serving_size': serving_size,
                'analysis_notes': self._generate_nutrition_analysis_notes(total_nutrition)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing meal nutrition: {str(e)}")
            return {}

    def _estimate_ingredient_portion(self, ingredient: str) -> float:
        """Estimate typical portion size for ingredient in grams."""
        
        # Simplified portion estimation - in production, would use more sophisticated methods
        portion_estimates = {
            'protein': 120,  # 4 oz serving
            'vegetable': 80,  # ~1/2 cup
            'fruit': 100,    # medium fruit
            'grain': 50,     # ~1/4 cup dry weight
            'dairy': 200,    # ~1 cup
            'legume': 75     # ~1/3 cup cooked
        }
        
        # Categorize ingredient
        category = self._categorize_unknown_food(ingredient)
        return portion_estimates.get(category, 75)  # Default 75g

    def _calculate_nutrition_quality(self, nutrition: Dict) -> Dict:
        """Calculate nutrition quality metrics."""
        
        try:
            calories = nutrition.get('calories', 0)
            protein = nutrition.get('protein', 0)
            fiber = nutrition.get('fiber', 0)
            sodium = nutrition.get('sodium', 0)
            
            # Calculate quality metrics
            protein_percentage = (protein * 4) / calories * 100 if calories > 0 else 0
            fiber_density = fiber / (calories / 100) if calories > 0 else 0
            sodium_per_calorie = sodium / calories if calories > 0 else 0
            
            # Quality scoring (0-100)
            quality_score = 0
            
            # Protein quality (0-30 points)
            if protein_percentage >= 20:
                quality_score += 30
            elif protein_percentage >= 15:
                quality_score += 20
            elif protein_percentage >= 10:
                quality_score += 10
            
            # Fiber quality (0-25 points)
            if fiber >= 8:
                quality_score += 25
            elif fiber >= 5:
                quality_score += 15
            elif fiber >= 3:
                quality_score += 10
            
            # Sodium quality (0-20 points) - lower is better
            if sodium_per_calorie <= 1:
                quality_score += 20
            elif sodium_per_calorie <= 2:
                quality_score += 15
            elif sodium_per_calorie <= 3:
                quality_score += 10
            
            # Calorie density (0-25 points) - moderate density is good
            calorie_density = calories / 100  # calories per 100g
            if 100 <= calorie_density <= 200:
                quality_score += 25
            elif 80 <= calorie_density <= 250:
                quality_score += 15
            elif calorie_density <= 300:
                quality_score += 10
            
            return {
                'overall_score': min(quality_score, 100),
                'protein_percentage': round(protein_percentage, 1),
                'fiber_density': round(fiber_density, 1),
                'sodium_per_calorie': round(sodium_per_calorie, 2),
                'calorie_density': round(calorie_density, 1),
                'quality_rating': self._get_quality_rating(quality_score)
            }
            
        except Exception as e:
            logger.error(f"Error calculating nutrition quality: {str(e)}")
            return {'overall_score': 50, 'quality_rating': 'moderate'}

    def _get_quality_rating(self, score: float) -> str:
        """Get quality rating based on score."""
        
        if score >= 80:
            return 'excellent'
        elif score >= 65:
            return 'good'
        elif score >= 50:
            return 'moderate'
        elif score >= 35:
            return 'fair'
        else:
            return 'poor'

    def _generate_nutrition_analysis_notes(self, nutrition: Dict) -> List[str]:
        """Generate helpful nutrition analysis notes."""
        
        notes = []
        
        calories = nutrition.get('calories', 0)
        protein = nutrition.get('protein', 0)
        fiber = nutrition.get('fiber', 0)
        sodium = nutrition.get('sodium', 0)
        
        # Protein analysis
        if protein >= 25:
            notes.append("Excellent protein content - great for muscle building and satiety")
        elif protein >= 15:
            notes.append("Good protein content - supports muscle maintenance")
        elif protein < 10:
            notes.append("Consider adding more protein for better satiety and muscle support")
        
        # Fiber analysis
        if fiber >= 8:
            notes.append("High fiber content - excellent for digestive health")
        elif fiber >= 5:
            notes.append("Good fiber content - supports digestive health")
        elif fiber < 3:
            notes.append("Consider adding more fiber-rich foods like vegetables or whole grains")
        
        # Sodium analysis
        if sodium > 800:
            notes.append("High sodium content - consider reducing salt or processed ingredients")
        elif sodium < 300:
            notes.append("Low sodium content - good for heart health")
        
        # Calorie analysis
        if calories > 600:
            notes.append("High calorie meal - good for active individuals or main meals")
        elif calories < 200:
            notes.append("Light meal - consider adding more substantial ingredients if needed")
        
        return notes

    async def get_food_recommendations(self, nutritional_goals: Dict, dietary_restrictions: List[str] = None) -> Dict:
        """Get food recommendations based on nutritional goals."""
        
        try:
            dietary_restrictions = dietary_restrictions or []
            recommendations = {
                'high_protein': [],
                'high_fiber': [],
                'low_sodium': [],
                'nutrient_dense': [],
                'budget_friendly': []
            }
            
            # Filter foods based on dietary restrictions
            suitable_foods = {}
            for food_key, food_data in self.food_database.items():
                if self._meets_dietary_restrictions(food_data, dietary_restrictions):
                    suitable_foods[food_key] = food_data
            
            # Categorize recommendations
            for food_key, food_data in suitable_foods.items():
                nutrition = food_data.get('nutrition_per_100g', {})
                
                # High protein (>15g per 100g)
                if nutrition.get('protein', 0) >= 15:
                    recommendations['high_protein'].append({
                        'name': food_data['name'],
                        'protein': nutrition.get('protein', 0),
                        'reason': f"{nutrition.get('protein', 0)}g protein per 100g"
                    })
                
                # High fiber (>5g per 100g)
                if nutrition.get('fiber', 0) >= 5:
                    recommendations['high_fiber'].append({
                        'name': food_data['name'],
                        'fiber': nutrition.get('fiber', 0),
                        'reason': f"{nutrition.get('fiber', 0)}g fiber per 100g"
                    })
                
                # Low sodium (<100mg per 100g)
                if nutrition.get('sodium', 0) <= 100:
                    recommendations['low_sodium'].append({
                        'name': food_data['name'],
                        'sodium': nutrition.get('sodium', 0),
                        'reason': f"Only {nutrition.get('sodium', 0)}mg sodium per 100g"
                    })
                
                # Nutrient dense (high nutrients per calorie)
                calorie_density = nutrition.get('calories', 100)
                if calorie_density <= 150 and len(food_data.get('key_nutrients', [])) >= 3:
                    recommendations['nutrient_dense'].append({
                        'name': food_data['name'],
                        'calories': calorie_density,
                        'nutrients': food_data.get('key_nutrients', []),
                        'reason': f"High nutrients, only {calorie_density} calories per 100g"
                    })
                
                # Budget friendly
                if food_data.get('cost_category') == 'low':
                    recommendations['budget_friendly'].append({
                        'name': food_data['name'],
                        'cost': 'low',
                        'reason': "Affordable and nutritious option"
                    })
            
            # Limit recommendations to top 5 per category
            for category in recommendations:
                recommendations[category] = recommendations[category][:5]
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting food recommendations: {str(e)}")
            return {}

    def _meets_dietary_restrictions(self, food_data: Dict, restrictions: List[str]) -> bool:
        """Check if food meets dietary restrictions."""
        
        if not restrictions:
            return True
        
        food_name = food_data.get('name', '').lower()
        category = food_data.get('category', '').lower()
        
        for restriction in restrictions:
            restriction_lower = restriction.lower()
            
            # Vegetarian restrictions
            if restriction_lower in ['vegetarian', 'vegan']:
                if category == 'protein' and any(meat in food_name for meat in ['chicken', 'beef', 'pork', 'fish', 'salmon']):
                    return False
                if restriction_lower == 'vegan' and any(dairy in food_name for dairy in ['cheese', 'milk', 'yogurt', 'egg']):
                    return False
            
            # Gluten-free restrictions
            elif restriction_lower == 'gluten-free':
                if any(gluten in food_name for gluten in ['wheat', 'barley', 'rye', 'pasta', 'bread']):
                    return False
            
            # Dairy-free restrictions
            elif restriction_lower == 'dairy-free':
                if any(dairy in food_name for dairy in ['cheese', 'milk', 'yogurt', 'dairy']):
                    return False
        
        return True 