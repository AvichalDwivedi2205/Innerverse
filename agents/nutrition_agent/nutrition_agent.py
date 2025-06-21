"""
LLM-Powered Nutrition Agent

Main agent class for intelligent nutrition planning with unlimited creativity,
smart substitutions, budget optimization, and nutrition education.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from agents.common.tool_results import NutritionToolResult
from .tools import NutritionTools
from .llm_meal_planner import LLMMealPlanner
from .substitution_engine import LLMSubstitutionEngine
from .budget_optimizer import LLMBudgetOptimizer
from .nutrition_data import NutritionDataService
from .prompts import NUTRITION_PROMPTS

logger = logging.getLogger(__name__)

class NutritionAgent(Agent):
    """LLM-powered nutrition agent with comprehensive meal planning capabilities."""
    
    def __init__(self, user_id: str = None):
        """Initialize the nutrition agent with all LLM-powered services."""
        
        # Agent system prompt for nutrition conversations
        system_prompt = """You are an expert nutrition and meal planning assistant with deep knowledge of:
        - Nutritional science and dietary requirements
        - Meal planning and recipe creation
        - Budget-conscious food choices
        - Cultural cuisines and cooking techniques
        - Food substitutions and dietary restrictions
        - Mental health and nutrition connections
        
        Your role is to:
        1. Create personalized, creative meal plans using LLM intelligence
        2. Provide smart food substitutions and alternatives
        3. Optimize meal plans for any budget level
        4. Educate users about nutrition in an engaging way
        5. Respect all dietary restrictions and preferences
        6. Make healthy eating accessible and enjoyable
        
        Always be encouraging, practical, and creative in your responses.
        Focus on sustainable, enjoyable eating habits rather than restrictive diets."""
        
        super().__init__(
            model="gemini-2.5-flash",
            instruction=system_prompt,
            name="nutrition_agent"
        )
        
        # Use global state to store all data and services (Pydantic restriction workaround)
        if not hasattr(NutritionAgent, '_global_state'):
            NutritionAgent._global_state = {
                'conversation_state': {},
                'preference_collection_step': {},
                'current_meal_plan_id': {},
                'tools': NutritionTools(),
                'llm_meal_planner': LLMMealPlanner(self),
                'substitution_engine': LLMSubstitutionEngine(self),
                'budget_optimizer': LLMBudgetOptimizer(self),
                'nutrition_data': NutritionDataService()
            }
        
        logger.info("NutritionAgent initialized with LLM-powered services")

    async def process_message(self, message: str, user_id: str, callback_context: CallbackContext) -> str:
        """Process nutrition-related messages with LLM intelligence."""
        
        try:
            message_lower = message.lower()
            
            # Initialize user state if needed
            if user_id not in NutritionAgent._global_state['conversation_state']:
                NutritionAgent._global_state['conversation_state'][user_id] = "general"
                NutritionAgent._global_state['preference_collection_step'][user_id] = 0
                NutritionAgent._global_state['current_meal_plan_id'][user_id] = None
            
            logger.info(f"Processing nutrition message from user {user_id}: {message[:100]}...")
            
            # Determine request type and route accordingly
            if self._is_meal_plan_request(message_lower):
                return await self._handle_meal_plan_creation(message, user_id, callback_context)
            elif self._is_substitution_request(message_lower):
                return await self._handle_substitution_request(message, user_id, callback_context)
            elif self._is_nutrition_question(message_lower):
                return await self._handle_nutrition_education(message, user_id, callback_context)
            elif self._is_budget_optimization_request(message_lower):
                return await self._handle_budget_optimization(message, user_id, callback_context)
            elif self._is_preference_response(message_lower, user_id):
                return await self._handle_preference_collection(message, user_id, callback_context)
            else:
                return await self._handle_general_nutrition_conversation(message, user_id, callback_context)
                
        except Exception as e:
            logger.error(f"Error processing nutrition message: {str(e)}")
            return "I apologize, but I encountered an error while processing your nutrition request. Please try again or rephrase your question."

    def _is_meal_plan_request(self, message: str) -> bool:
        """Check if message is requesting meal plan creation."""
        meal_plan_keywords = [
            "meal plan", "weekly plan", "daily meals", "create plan", "plan my meals",
            "what should i eat", "menu planning", "weekly menu", "food plan",
            "plan meals", "meal planning", "weekly meals", "daily menu"
        ]
        return any(keyword in message for keyword in meal_plan_keywords)

    def _is_substitution_request(self, message: str) -> bool:
        """Check if message is requesting food substitutions."""
        substitution_keywords = [
            "substitute", "replace", "swap", "instead of", "alternative",
            "don't like", "allergic to", "can't eat", "change", "different",
            "swap out", "replace with", "alternative to"
        ]
        return any(keyword in message for keyword in substitution_keywords)

    def _is_nutrition_question(self, message: str) -> bool:
        """Check if message is asking nutrition education questions."""
        nutrition_keywords = [
            "nutrition", "healthy", "calories", "protein", "vitamins",
            "nutrients", "benefits", "why", "how does", "is it good",
            "nutritional value", "health benefits", "diet question"
        ]
        return any(keyword in message for keyword in nutrition_keywords)

    def _is_budget_optimization_request(self, message: str) -> bool:
        """Check if message is requesting budget optimization."""
        budget_keywords = [
            "budget", "cheap", "affordable", "save money", "cost less",
            "expensive", "lower cost", "budget friendly", "economical"
        ]
        return any(keyword in message for keyword in budget_keywords)

    def _is_preference_response(self, message: str, user_id: str) -> bool:
        """Check if message is responding to preference collection."""
        return NutritionAgent._global_state['conversation_state'].get(user_id) == "collecting_preferences"

    async def _handle_meal_plan_creation(self, message: str, user_id: str, callback_context: CallbackContext) -> str:
        """Handle meal plan creation requests."""
        
        try:
            # Check if user has provided preferences
            user_preferences = await NutritionAgent._global_state['tools'].get_user_preferences(user_id)
            
            if not user_preferences:
                # Start preference collection
                NutritionAgent._global_state['conversation_state'][user_id] = "collecting_preferences"
                NutritionAgent._global_state['preference_collection_step'][user_id] = 0
                return await self._start_preference_collection(user_id)
            else:
                # Generate comprehensive meal plan
                meal_plan = await NutritionAgent._global_state['llm_meal_planner'].generate_comprehensive_meal_plan(user_preferences)
                
                # Store meal plan
                plan_id = await NutritionAgent._global_state['tools'].store_meal_plan(user_id, meal_plan)
                NutritionAgent._global_state['current_meal_plan_id'][user_id] = plan_id
                
                # Generate proactive substitution suggestions
                substitution_suggestions = await NutritionAgent._global_state['substitution_engine'].suggest_substitutions_after_generation(
                    meal_plan, user_preferences
                )
                
                # Create tool result for coordinator
                tool_result = NutritionToolResult(
                    meal_plan_created=True,
                    plan_id=plan_id,
                    duration_days=meal_plan.get('duration_days', 7),
                    estimated_cost=meal_plan.get('estimated_cost', 0),
                    substitution_suggestions=substitution_suggestions.get('suggestions', [])
                )
                
                if callback_context and callback_context.set_tool_result:
                    callback_context.set_tool_result(tool_result)
                
                # Format comprehensive response
                return self._format_meal_plan_response(meal_plan, substitution_suggestions)
                
        except Exception as e:
            logger.error(f"Error handling meal plan creation: {str(e)}")
            return "I encountered an error while creating your meal plan. Let me try a different approach or please provide more specific preferences."

    async def _start_preference_collection(self, user_id: str) -> str:
        """Start collecting user preferences for meal planning."""
        
        NutritionAgent._global_state['conversation_state'][user_id] = "collecting_preferences"
        NutritionAgent._global_state['preference_collection_step'][user_id] = 0
        
        return """🍽️ **Let's Create Your Perfect Meal Plan!**

I'll ask you a few questions to create a personalized meal plan that fits your lifestyle, preferences, and budget.

**First, let's start with the basics:**

1. **What's your primary nutrition goal?**
   - Weight loss
   - Weight gain  
   - Muscle building
   - Maintenance/general health
   - Mental health improvement (mood, energy, sleep)

2. **What's your dietary preference?**
   - Omnivore (eat everything)
   - Vegetarian
   - Vegan
   - Pescatarian (fish but no meat)
   - Keto/Low-carb
   - Mediterranean
   - Other (please specify)

Just let me know your goal and dietary preference, and I'll ask about budget and other details next! 🎯"""

    async def _handle_preference_collection(self, message: str, user_id: str, callback_context: CallbackContext) -> str:
        """Handle preference collection conversation."""
        
        try:
            # Parse current preferences from message
            current_step = NutritionAgent._global_state['preference_collection_step'][user_id]
            current_preferences = await self._parse_preference_response(message, current_step)
            
            # Store partial preferences
            await NutritionAgent._global_state['tools'].update_user_preferences(user_id, current_preferences)
            
            # Move to next step
            NutritionAgent._global_state['preference_collection_step'][user_id] += 1
            current_step = NutritionAgent._global_state['preference_collection_step'][user_id]
            
            if current_step == 1:
                return """Great choices! Now let's talk about your lifestyle and constraints:

**3. What's your budget preference?**
   - Low budget (~$50/week) - Budget-friendly, simple ingredients
   - Medium budget (~$100/week) - Balanced quality and variety  
   - High budget (~$200/week) - Premium ingredients and variety
   - Custom amount (tell me your weekly food budget)

**4. How much time can you spend cooking daily?**
   - 15 minutes (quick & simple meals)
   - 30 minutes (moderate cooking)
   - 1 hour (enjoy cooking)
   - 2+ hours (love to cook)

**5. What's your cooking skill level?**
   - Beginner (simple recipes please!)
   - Intermediate (comfortable with most techniques)
   - Advanced (bring on the challenge!)"""
            
            elif current_step == 2:
                return """Perfect! Just a few more questions:

**6. Any food allergies or intolerances?** (e.g., nuts, dairy, gluten)

**7. Any foods you strongly dislike or want to avoid?**

**8. Do you have any cultural cuisine preferences?** (e.g., Italian, Mexican, Asian, Indian, Mediterranean)

**9. How many days would you like your meal plan for?** (3, 7, or 14 days)"""
            
            elif current_step >= 3:
                # Final step - generate meal plan
                complete_preferences = await NutritionAgent._global_state['tools'].get_user_preferences(user_id)
                
                NutritionAgent._global_state['conversation_state'][user_id] = "general"
                
                return """🎉 **Perfect! I have everything I need.**

Let me create your personalized meal plan now. This will include:
- 3 meals + 2 snacks per day
- Recipes with clear instructions
- Budget-conscious ingredient choices
- Variety of flavors and cuisines
- Nutrition-balanced meals

*Generating your custom meal plan... this may take a moment!* ⏳

Once ready, I'll also provide substitution suggestions in case you want to make any changes!"""
            
        except Exception as e:
            logger.error(f"Error in preference collection: {str(e)}")
            return "I had trouble understanding your preferences. Could you please rephrase your response?"

    async def _parse_preference_response(self, message: str, step: int) -> Dict:
        """Parse user preference responses using LLM."""
        
        # Use LLM to parse natural language preferences
        parse_prompt = f"""
        Parse this user response for nutrition preferences (step {step}):
        "{message}"
        
        Extract relevant information and return as JSON:
        {{
            "primary_goal": "extracted goal if mentioned",
            "diet_type": "extracted diet type if mentioned", 
            "budget_level": "extracted budget if mentioned",
            "weekly_budget": "extracted custom budget amount if mentioned",
            "cooking_time": "extracted cooking time if mentioned",
            "cooking_skill": "extracted skill level if mentioned",
            "allergies": ["list of allergies if mentioned"],
            "dislikes": ["list of dislikes if mentioned"],
            "cultural_preferences": ["list of cuisine preferences if mentioned"],
            "duration_days": "number of days if mentioned"
        }}
        
        Only include fields that are clearly mentioned. Return valid JSON.
        """
        
        try:
            # For now, return a mock parsed response since direct LLM calls aren't available
            # In production, this would be handled by the Agent's conversation flow
            mock_response = '{"diet_type": "vegetarian", "primary_goal": "weight loss", "budget_level": "medium"}'
            parsed_data = json.loads(mock_response)
            return {k: v for k, v in parsed_data.items() if v}  # Remove empty values
            
        except Exception as e:
            logger.error(f"Error parsing preferences: {str(e)}")
            return {}

    async def _handle_substitution_request(self, message: str, user_id: str, callback_context: CallbackContext) -> str:
        """Handle food substitution requests."""
        
        try:
            # Get current meal plan
            current_plan_id = NutritionAgent._global_state['current_meal_plan_id'].get(user_id)
            if not current_plan_id:
                meal_plans = await NutritionAgent._global_state['tools'].get_user_meal_plans(user_id)
                if not meal_plans:
                    return "I don't have a current meal plan for you. Would you like me to create one first?"
                current_plan_id = meal_plans[0]['plan_id']
                NutritionAgent._global_state['current_meal_plan_id'][user_id] = current_plan_id
            
            meal_plan = await NutritionAgent._global_state['tools'].get_meal_plan(user_id, current_plan_id)
            user_preferences = await NutritionAgent._global_state['tools'].get_user_preferences(user_id)
            
            # Process substitution request with LLM
            updated_plan = await NutritionAgent._global_state['substitution_engine'].process_user_substitution_request(
                meal_plan, message, user_preferences
            )
            
            # Update stored meal plan
            await NutritionAgent._global_state['tools'].update_meal_plan(user_id, current_plan_id, updated_plan)
            
            # Create tool result
            tool_result = NutritionToolResult(
                substitution_made=True,
                plan_id=current_plan_id,
                substitution_details=updated_plan.get('changes_made', [])
            )
            
            if callback_context and callback_context.set_tool_result:
                callback_context.set_tool_result(tool_result)
            
            return self._format_substitution_response(updated_plan)
            
        except Exception as e:
            logger.error(f"Error handling substitution: {str(e)}")
            return "I had trouble processing your substitution request. Could you be more specific about what you'd like to change?"

    async def _handle_nutrition_education(self, message: str, user_id: str, callback_context: CallbackContext) -> str:
        """Handle nutrition education questions."""
        
        try:
            # Use LLM to provide comprehensive nutrition education
            education_prompt = f"""
            User nutrition question: "{message}"
            
            Provide a comprehensive, educational response that:
            1. Directly answers their question
            2. Explains the science/reasoning behind it
            3. Gives practical tips or applications
            4. Mentions any relevant health benefits
            5. Suggests related foods or nutrients
            6. Keeps the tone encouraging and accessible
            
            Make it informative but not overwhelming. Include emojis for engagement.
            """
            
            # Mock education response - in production this would be handled by Agent conversation
            education_response = "Fiber is essential for digestive health, helps regulate blood sugar, and supports heart health. Aim for 25-35g daily from fruits, vegetables, whole grains, and legumes."
            
            # Create tool result
            tool_result = NutritionToolResult(
                nutrition_education_provided=True,
                topic=message[:50] + "..." if len(message) > 50 else message
            )
            
            if callback_context and callback_context.set_tool_result:
                callback_context.set_tool_result(tool_result)
            
            return f"🧠 **Nutrition Education**\n\n{education_response}\n\n💡 **Want to know more?** Feel free to ask follow-up questions!"
            
        except Exception as e:
            logger.error(f"Error handling nutrition education: {str(e)}")
            return "I'd be happy to help with nutrition information! Could you rephrase your question?"

    async def _handle_budget_optimization(self, message: str, user_id: str, callback_context: CallbackContext) -> str:
        """Handle budget optimization requests."""
        
        try:
            # Extract target budget from message
            target_budget = await self._extract_budget_from_message(message)
            
            current_plan_id = NutritionAgent._global_state['current_meal_plan_id'].get(user_id)
            if not current_plan_id:
                return "I don't have a current meal plan to optimize. Would you like me to create a budget-friendly meal plan for you?"
            
            meal_plan = await NutritionAgent._global_state['tools'].get_meal_plan(user_id, current_plan_id)
            user_preferences = await NutritionAgent._global_state['tools'].get_user_preferences(user_id)
            
            # Optimize with LLM
            optimized_plan = await NutritionAgent._global_state['budget_optimizer'].optimize_for_budget(
                meal_plan, target_budget, user_preferences
            )
            
            # Update meal plan
            await NutritionAgent._global_state['tools'].update_meal_plan(user_id, current_plan_id, optimized_plan)
            
            # Create tool result
            tool_result = NutritionToolResult(
                budget_optimization_applied=True,
                plan_id=current_plan_id,
                target_budget=target_budget,
                estimated_savings=meal_plan.get('estimated_cost', 0) - optimized_plan.get('estimated_cost', 0)
            )
            
            if callback_context and callback_context.set_tool_result:
                callback_context.set_tool_result(tool_result)
            
            return self._format_budget_optimization_response(optimized_plan, target_budget)
            
        except Exception as e:
            logger.error(f"Error handling budget optimization: {str(e)}")
            return "I had trouble optimizing your meal plan for budget. Could you specify your target weekly budget amount?"

    async def _handle_general_nutrition_conversation(self, message: str, user_id: str, callback_context: CallbackContext) -> str:
        """Handle general nutrition conversation."""
        
        try:
            # Use LLM for general nutrition conversation
            conversation_prompt = f"""
            User message: "{message}"
            
            Respond as a friendly, knowledgeable nutrition assistant. 
            - Be encouraging and supportive
            - Offer helpful suggestions
            - Ask clarifying questions if needed
            - Mention relevant nutrition services you can provide
            - Keep response conversational and engaging
            
            Available services you can offer:
            - Create personalized meal plans
            - Provide food substitutions
            - Answer nutrition questions
            - Optimize meals for budget
            - Generate recipes
            """
            
            # Mock general conversation response - in production this would be handled by Agent conversation
            return "I'm here to help with all your nutrition needs! I can create personalized meal plans, suggest food substitutions, answer nutrition questions, and help optimize your meals for any budget. What would you like to explore first?"
            
        except Exception as e:
            logger.error(f"Error in general nutrition conversation: {str(e)}")
            return "I'm here to help with all your nutrition needs! I can create meal plans, suggest substitutions, answer nutrition questions, and help optimize your meals for any budget. What would you like to explore?"

    def _format_meal_plan_response(self, meal_plan: Dict, substitution_suggestions: Dict) -> str:
        """Format comprehensive meal plan response."""
        
        try:
            duration = meal_plan.get('duration_days', 7)
            estimated_cost = meal_plan.get('estimated_cost', 0)
            
            response = f"""🍽️ **Your Personalized {duration}-Day Meal Plan**

{self._format_daily_meals(meal_plan)}

📊 **Weekly Summary:**
- 💰 Estimated Cost: ${estimated_cost}/week
- 🥗 Nutrition Balance: {meal_plan.get('nutrition_balance', 'Well-balanced macronutrients')}
- 🍳 Meal Prep Tips: {meal_plan.get('meal_prep_tips', 'Prepare ingredients in advance for easier cooking')}

🔄 **Want to make changes?** Here are some substitution ideas:
{self._format_substitution_suggestions(substitution_suggestions)}

**Just tell me what you'd like to substitute and I'll update your plan!** 

Need recipes for any specific meal? Want to optimize for a different budget? Just ask! 🎯"""
            
            return response
            
        except Exception as e:
            logger.error(f"Error formatting meal plan response: {str(e)}")
            return "I've created your meal plan! There was a formatting issue, but your plan is ready. Ask me about specific meals or substitutions!"

    def _format_daily_meals(self, meal_plan: Dict) -> str:
        """Format daily meals section."""
        
        try:
            daily_meals = ""
            days = meal_plan.get('daily_plans', {})
            
            for day_num in sorted(days.keys()):
                day_data = days[day_num]
                daily_meals += f"\n**Day {day_num}:**\n"
                
                meals = ['breakfast', 'morning_snack', 'lunch', 'afternoon_snack', 'dinner']
                meal_emojis = {'breakfast': '🌅', 'morning_snack': '🍎', 'lunch': '🌞', 'afternoon_snack': '🥨', 'dinner': '🌙'}
                
                for meal in meals:
                    if meal in day_data:
                        meal_info = day_data[meal]
                        emoji = meal_emojis.get(meal, '🍽️')
                        meal_name = meal_info.get('name', 'Meal')
                        prep_time = meal_info.get('prep_time', '15 min')
                        
                        daily_meals += f"  {emoji} **{meal.replace('_', ' ').title()}:** {meal_name} ({prep_time})\n"
                
                daily_meals += "\n"
            
            return daily_meals
            
        except Exception as e:
            logger.error(f"Error formatting daily meals: {str(e)}")
            return "Daily meal breakdown available - ask me about specific days or meals!"

    def _format_substitution_suggestions(self, substitution_suggestions: Dict) -> str:
        """Format substitution suggestions."""
        
        try:
            suggestions = substitution_suggestions.get('suggestions', [])
            if not suggestions:
                return "- No specific suggestions right now, but I can help with any substitutions you need!"
            
            formatted = ""
            for suggestion in suggestions[:6]:  # Limit to 6 suggestions
                formatted += f"- {suggestion}\n"
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting substitution suggestions: {str(e)}")
            return "- I can help with any substitutions you need - just ask!"

    def _format_substitution_response(self, updated_plan: Dict) -> str:
        """Format substitution response."""
        
        changes_made = updated_plan.get('changes_made', [])
        explanation = updated_plan.get('explanation', 'I\'ve updated your meal plan with your requested substitutions.')
        
        response = f"""✅ **Substitution Complete!**

{explanation}

**Changes Made:**
"""
        
        for change in changes_made:
            response += f"- {change}\n"
        
        response += "\n🍽️ Your updated meal plan is ready! Need any other changes or want to see specific recipes?"
        
        return response

    def _format_budget_optimization_response(self, optimized_plan: Dict, target_budget: float) -> str:
        """Format budget optimization response."""
        
        new_cost = optimized_plan.get('estimated_cost', target_budget)
        savings_tips = optimized_plan.get('cost_saving_tips', [])
        
        response = f"""💰 **Budget Optimization Complete!**

🎯 **Target Budget:** ${target_budget}/week
💵 **New Estimated Cost:** ${new_cost}/week

**Money-Saving Changes Made:**
"""
        
        for tip in savings_tips:
            response += f"- {tip}\n"
        
        response += "\n✨ Your optimized meal plan maintains great nutrition while fitting your budget! Want to see the updated meals?"
        
        return response

    async def _extract_budget_from_message(self, message: str) -> float:
        """Extract budget amount from user message."""
        
        try:
            # Use LLM to extract budget
            extract_prompt = f"""
            Extract the budget amount from this message: "{message}"
            
            Look for:
            - Dollar amounts ($50, $100, etc.)
            - Numbers followed by budget keywords (50 dollars, 100 per week)
            - Budget level keywords (low = 50, medium = 100, high = 200)
            
            Return just the weekly budget number (e.g., 75.0) or 0 if no budget found.
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": extract_prompt}],
                temperature=0.1
            )
            
            budget_str = response.choices[0].message.content.strip()
            return float(budget_str) if budget_str.replace('.', '').isdigit() else 100.0
            
        except Exception as e:
            logger.error(f"Error extracting budget: {str(e)}")
            return 100.0  # Default budget 