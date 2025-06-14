from typing import List, Dict, Any

class NutritionPrompts:
    """Practical nutritional guidance prompts for meal planning"""
    
    @staticmethod
    def get_meal_plan_generation_prompt(physical_goals: List[str], dietary_preferences: List[str],
                                      dietary_restrictions: List[str], target_calories: int) -> str:
        """Generate meal plan creation prompt"""
        
        prompt = f"""
        SIMPLE MEAL PLAN GENERATION
        
        Create a practical weekly meal plan based on these requirements:
        
        PHYSICAL GOALS: {', '.join(physical_goals) if physical_goals else 'General health maintenance'}
        DIETARY PREFERENCES: {', '.join(dietary_preferences) if dietary_preferences else 'No specific preferences'}
        DIETARY RESTRICTIONS: {', '.join(dietary_restrictions) if dietary_restrictions else 'None'}
        TARGET CALORIES: {target_calories} calories per day
        
        MEAL PLAN REQUIREMENTS:
        
        1. WEEKLY STRUCTURE:
           - 7 days of meals (Monday through Sunday)
           - Breakfast, lunch, dinner, and 2 snacks per day
           - Simple, realistic meals that people actually eat
           - Variety to prevent boredom
        
        2. CALORIE DISTRIBUTION:
           - Breakfast: ~25% of daily calories
           - Lunch: ~30% of daily calories
           - Dinner: ~35% of daily calories
           - Snacks: ~10% of daily calories (split between 2 snacks)
        
        3. GOAL-SPECIFIC GUIDANCE:
           - Weight Loss: Focus on lean proteins, vegetables, controlled portions
           - Muscle Gain: Higher protein, adequate carbs for energy
           - Maintenance: Balanced approach with variety
        
        4. PRACTICAL CONSIDERATIONS:
           - Use common, easily available ingredients
           - Include simple cooking methods
           - Suggest meal prep options
           - Provide portion size guidance
           - Include hydration reminders
        
        5. DIETARY ACCOMMODATION:
           - Respect all dietary restrictions completely
           - Incorporate preferred foods when possible
           - Suggest alternatives for restricted items
           - Ensure nutritional completeness despite restrictions
        
        6. SHOPPING AND PREP:
           - Include a basic shopping list
           - Suggest meal prep strategies
           - Recommend batch cooking options
           - Provide food storage tips
        
        FORMAT YOUR RESPONSE:
        - Clear day-by-day meal breakdown
        - Approximate calorie counts for each meal
        - Simple ingredient lists
        - Basic preparation instructions
        - Shopping list summary
        - Meal prep tips
        
        Keep everything simple, practical, and achievable for everyday people with busy lives.
        """
        
        return prompt
    
    @staticmethod
    def get_meal_plan_modification_prompt(current_plan: Dict[str, Any], modifications: str) -> str:
        """Generate meal plan modification prompt"""
        
        prompt = f"""
        MEAL PLAN MODIFICATION
        
        Modify the following meal plan based on the user's request:
        
        CURRENT MEAL PLAN:
        {current_plan}
        
        USER'S MODIFICATION REQUEST:
        "{modifications}"
        
        MODIFICATION GUIDELINES:
        
        1. UNDERSTAND THE REQUEST:
           - Identify specific meals, ingredients, or days to change
           - Determine if it's a preference change or substitution need
           - Consider if it affects overall nutritional balance
        
        2. MAINTAIN NUTRITIONAL BALANCE:
           - Keep similar calorie counts unless specifically requested to change
           - Maintain protein, carb, and fat balance appropriate for goals
           - Ensure modifications don't compromise nutritional completeness
        
        3. PRACTICAL SUBSTITUTIONS:
           - Suggest realistic alternatives that are easily available
           - Consider cooking time and complexity
           - Maintain meal prep efficiency if applicable
        
        4. ACCOMMODATION TYPES:
           - Ingredient swaps (e.g., chicken to fish, rice to quinoa)
           - Meal timing changes
           - Portion adjustments
           - Cuisine style changes
           - Cooking method modifications
        
        5. CLEAR COMMUNICATION:
           - Explain what changes were made and why
           - Provide the updated meal plan sections
           - Include any new shopping list items needed
           - Mention any nutritional impact of changes
        
        Provide specific, actionable modifications that address the user's request while maintaining a practical, healthy meal plan.
        """
        
        return prompt
    
    @staticmethod
    def get_food_analysis_prompt(food_items: List[str], nutritional_goals: Dict[str, Any]) -> str:
        """Generate food analysis prompt"""
        
        prompt = f"""
        FOOD NUTRITIONAL ANALYSIS
        
        Analyze the following food items and provide practical nutritional guidance:
        
        FOOD ITEMS: {', '.join(food_items)}
        NUTRITIONAL GOALS: {nutritional_goals}
        
        ANALYSIS REQUIREMENTS:
        
        1. CALORIE INFORMATION:
           - Approximate calories per typical serving
           - Portion size recommendations
           - Calorie density assessment (high/medium/low)
        
        2. MACRONUTRIENT BREAKDOWN:
           - Protein content and quality
           - Carbohydrate type (simple/complex)
           - Fat content and type (saturated/unsaturated)
        
        3. NUTRITIONAL VALUE:
           - Key vitamins and minerals
           - Fiber content
           - Overall nutritional density
        
        4. GOAL ALIGNMENT:
           - How well each food fits the user's goals
           - Suggestions for portion control if needed
           - Timing recommendations (pre/post workout, etc.)
        
        5. PRACTICAL GUIDANCE:
           - Best preparation methods
           - Food combinations for better nutrition
           - Storage and meal prep tips
        
        6. ALTERNATIVES AND SUBSTITUTIONS:
           - Healthier alternatives if applicable
           - Ways to enhance nutritional value
           - Portion modification suggestions
        
        Provide clear, actionable nutritional guidance that helps users make informed food choices aligned with their goals.
        """
        
        return prompt
    
    @staticmethod
    def get_calorie_tracking_prompt(daily_food_log: List[Dict[str, Any]], calorie_target: int) -> str:
        """Generate calorie tracking analysis prompt"""
        
        prompt = f"""
        DAILY CALORIE TRACKING ANALYSIS
        
        Analyze the following daily food log and provide tracking insights:
        
        DAILY FOOD LOG:
        {daily_food_log}
        
        DAILY CALORIE TARGET: {calorie_target} calories
        
        TRACKING ANALYSIS:
        
        1. CALORIE SUMMARY:
           - Total calories consumed
           - Calories remaining or over target
           - Percentage of target achieved
        
        2. MEAL DISTRIBUTION:
           - Calories per meal (breakfast, lunch, dinner, snacks)
           - Meal timing analysis
           - Portion size assessment
        
        3. MACRONUTRIENT ANALYSIS:
           - Protein, carbs, and fat distribution
           - Comparison to recommended ratios
           - Quality of macronutrient sources
        
        4. NUTRITIONAL GAPS:
           - Missing food groups
           - Micronutrient considerations
           - Hydration status if available
        
        5. RECOMMENDATIONS:
           - Adjustments for remaining meals if day isn't complete
           - Better food choices for similar calories
           - Portion size modifications
        
        6. PROGRESS INSIGHTS:
           - How today's intake supports goals
           - Patterns to maintain or change
           - Motivational feedback
        
        Provide encouraging, practical feedback that helps users stay on track with their nutritional goals.
        """
        
        return prompt

# Global nutrition prompts instance
nutrition_prompts = NutritionPrompts()
