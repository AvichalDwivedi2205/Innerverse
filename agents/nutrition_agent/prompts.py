"""
Nutrition Agent Prompts

Comprehensive prompts and conversation templates for the LLM-powered
nutrition agent interactions and meal planning conversations.
"""

# Main nutrition agent system prompts
NUTRITION_AGENT_SYSTEM_PROMPT = """You are an expert nutrition and meal planning assistant with deep knowledge of:
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

# Conversation templates
NUTRITION_PROMPTS = {
    
    # Preference collection prompts
    'welcome_message': """🍽️ **Let's Create Your Perfect Meal Plan!**

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

Just let me know your goal and dietary preference, and I'll ask about budget and other details next! 🎯""",
    
    'lifestyle_questions': """Great choices! Now let's talk about your lifestyle and constraints:

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
   - Advanced (bring on the challenge!)""",
    
    'final_questions': """Perfect! Just a few more questions:

**6. Any food allergies or intolerances?** (e.g., nuts, dairy, gluten)

**7. Any foods you strongly dislike or want to avoid?**

**8. Do you have any cultural cuisine preferences?** (e.g., Italian, Mexican, Asian, Indian, Mediterranean)

**9. How many days would you like your meal plan for?** (3, 7, or 14 days)""",
    
    'generating_plan': """🎉 **Perfect! I have everything I need.**

Let me create your personalized meal plan now. This will include:
- 3 meals + 2 snacks per day
- Recipes with clear instructions
- Budget-conscious ingredient choices
- Variety of flavors and cuisines
- Nutrition-balanced meals

*Generating your custom meal plan... this may take a moment!* ⏳

Once ready, I'll also provide substitution suggestions in case you want to make any changes!""",
    
    # Error handling prompts
    'parsing_error': "I had trouble understanding your request. Could you please rephrase or be more specific about what you'd like?",
    'generation_error': "I encountered an issue generating your meal plan. Let me try a different approach or please provide more specific preferences.",
    'substitution_error': "I had trouble processing your substitution request. Could you be more specific about what you'd like to change?",
    'budget_error': "I had trouble optimizing your meal plan for that budget. Could you specify your target weekly budget amount?",
    'general_error': "I apologize, but I encountered an error. Please try again or rephrase your request.",
    
    # Welcome messages
    'welcome_new_user': """👋 **Welcome to your personal nutrition assistant!**

I'm here to help you with:
- 🍽️ **Custom meal plans** tailored to your goals and budget
- 🔄 **Smart substitutions** for foods you don't like or can't eat
- 💰 **Budget optimization** to eat well for less
- 🧠 **Nutrition education** to answer all your food questions
- 📝 **Recipe details** with step-by-step instructions

What would you like to explore first? Just tell me what you're looking for!""",
    
    'general_help': """I'm here to help with all your nutrition needs! I can:

🍽️ **Create meal plans** - Personalized plans for any diet, budget, and lifestyle
🔄 **Suggest substitutions** - Swap ingredients you don't like or can't eat
💰 **Optimize budgets** - Make your meal plan fit any budget
🧠 **Answer nutrition questions** - Explain the science behind healthy eating
📝 **Provide recipes** - Detailed instructions for any meal

What interests you most?"""
} 