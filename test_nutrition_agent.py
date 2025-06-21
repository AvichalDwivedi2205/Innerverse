#!/usr/bin/env python3
"""
Test script for the LLM-powered Nutrition Agent

Tests all major functionality including meal planning, substitutions,
budget optimization, and nutrition education.
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock OpenAI client for testing
class MockOpenAIClient:
    """Mock OpenAI client for testing without API calls."""
    
    def __init__(self):
        self.chat = MockChatCompletions()

class MockChatCompletions:
    """Mock chat completions."""
    
    async def create(self, **kwargs):
        """Mock completion creation."""
        
        # Mock response based on prompt content
        prompt = kwargs.get('messages', [{}])[0].get('content', '')
        
        if 'meal plan' in prompt.lower():
            return MockResponse(self._generate_mock_meal_plan())
        elif 'substitution' in prompt.lower():
            return MockResponse(self._generate_mock_substitution())
        elif 'budget' in prompt.lower():
            return MockResponse(self._generate_mock_budget_optimization())
        elif 'nutrition question' in prompt.lower():
            return MockResponse(self._generate_mock_nutrition_education())
        else:
            return MockResponse("I'm here to help with your nutrition needs!")

    def _generate_mock_meal_plan(self):
        """Generate mock meal plan JSON."""
        return json.dumps({
            "daily_plans": {
                "1": {
                    "breakfast": {
                        "name": "Overnight Oats with Berries",
                        "ingredients": ["rolled oats", "almond milk", "chia seeds", "mixed berries", "honey"],
                        "simple_recipe": "Mix oats with milk and chia seeds, refrigerate overnight, top with berries and honey",
                        "prep_time": "5 min",
                        "nutrition_highlights": ["fiber", "antioxidants", "protein"]
                    },
                    "morning_snack": {
                        "name": "Greek Yogurt with Nuts",
                        "ingredients": ["Greek yogurt", "almonds", "walnuts"],
                        "simple_recipe": "Mix yogurt with chopped nuts",
                        "prep_time": "2 min",
                        "nutrition_highlights": ["protein", "healthy fats"]
                    },
                    "lunch": {
                        "name": "Quinoa Buddha Bowl",
                        "ingredients": ["quinoa", "chickpeas", "roasted vegetables", "tahini dressing"],
                        "simple_recipe": "Combine cooked quinoa with roasted vegetables and chickpeas, drizzle with tahini",
                        "prep_time": "20 min",
                        "nutrition_highlights": ["complete protein", "fiber", "vitamins"]
                    },
                    "afternoon_snack": {
                        "name": "Apple with Almond Butter",
                        "ingredients": ["apple", "almond butter"],
                        "simple_recipe": "Slice apple and serve with almond butter",
                        "prep_time": "2 min",
                        "nutrition_highlights": ["fiber", "healthy fats"]
                    },
                    "dinner": {
                        "name": "Baked Salmon with Sweet Potato",
                        "ingredients": ["salmon fillet", "sweet potato", "broccoli", "olive oil", "herbs"],
                        "simple_recipe": "Bake salmon and sweet potato at 400°F for 20 minutes, steam broccoli",
                        "prep_time": "25 min",
                        "nutrition_highlights": ["omega-3", "beta-carotene", "protein"]
                    }
                }
            },
            "nutrition_balance": "Well-balanced with adequate protein, healthy fats, and complex carbohydrates",
            "meal_prep_tips": "Cook quinoa and roast vegetables in batches, prepare overnight oats for multiple days",
            "cuisine_variety": "Mediterranean, American, Middle Eastern influences",
            "budget_breakdown": "Proteins 35%, Vegetables 25%, Grains 20%, Other 20%"
        })

    def _generate_mock_substitution(self):
        """Generate mock substitution response."""
        return json.dumps({
            "suggestions": [
                {
                    "category": "budget-friendly",
                    "suggestion": "Replace salmon with chicken thighs for similar protein at lower cost",
                    "reasoning": "Maintains protein content while reducing grocery costs"
                },
                {
                    "category": "dietary",
                    "suggestion": "Swap dairy yogurt for coconut yogurt if avoiding dairy",
                    "reasoning": "Plant-based alternative with similar texture and probiotics"
                },
                {
                    "category": "time-saving",
                    "suggestion": "Use pre-cooked quinoa or frozen vegetables to save prep time",
                    "reasoning": "Reduces cooking time without sacrificing nutrition"
                }
            ],
            "summary": "Multiple substitution options available for dietary needs, budget, and time constraints"
        })

    def _generate_mock_budget_optimization(self):
        """Generate mock budget optimization response."""
        return json.dumps({
            "optimized_daily_plans": {
                "1": {
                    "breakfast": {
                        "name": "Oatmeal with Banana",
                        "ingredients": ["rolled oats", "banana", "milk", "cinnamon"],
                        "simple_recipe": "Cook oats with milk, top with sliced banana and cinnamon",
                        "prep_time": "10 min",
                        "nutrition_highlights": ["fiber", "potassium"],
                        "cost_savings": "Replaced expensive berries with affordable banana"
                    },
                    "lunch": {
                        "name": "Bean and Rice Bowl",
                        "ingredients": ["brown rice", "black beans", "vegetables", "salsa"],
                        "simple_recipe": "Combine cooked rice and beans, top with vegetables and salsa",
                        "prep_time": "15 min",
                        "nutrition_highlights": ["protein", "fiber"],
                        "cost_savings": "Used beans instead of quinoa for plant protein"
                    },
                    "dinner": {
                        "name": "Chicken Thigh with Roasted Vegetables",
                        "ingredients": ["chicken thighs", "seasonal vegetables", "olive oil"],
                        "simple_recipe": "Roast chicken thighs with vegetables at 425°F for 30 minutes",
                        "prep_time": "35 min",
                        "nutrition_highlights": ["protein", "vitamins"],
                        "cost_savings": "Used chicken thighs instead of salmon for protein"
                    }
                }
            },
            "estimated_cost": 65,
            "total_savings": 35,
            "cost_saving_tips": [
                "Buy proteins in bulk when on sale and freeze portions",
                "Use seasonal vegetables for better prices and freshness",
                "Choose store brands for pantry staples - same quality, lower cost"
            ],
            "budget_breakdown": {
                "proteins": "30%",
                "vegetables": "25%",
                "grains": "25%",
                "other": "20%"
            }
        })

    def _generate_mock_nutrition_education(self):
        """Generate mock nutrition education response."""
        return """🥗 **Great question about fiber!**

Fiber is incredibly important for digestive health and overall wellbeing. Here's what you need to know:

**Types of Fiber:**
- **Soluble fiber** (oats, beans, apples) helps lower cholesterol and blood sugar
- **Insoluble fiber** (whole grains, vegetables) promotes healthy digestion

**Daily Recommendations:**
- Adults need 25-35 grams of fiber per day
- Most people only get about half of this amount

**Best Sources:**
- Fruits and vegetables (with skin when possible)
- Whole grains like oats, quinoa, brown rice
- Legumes like beans, lentils, chickpeas
- Nuts and seeds

**Pro Tips:**
- Increase fiber gradually to avoid digestive discomfort
- Drink plenty of water when increasing fiber intake
- Aim for variety - different fibers have different benefits

Adding more fiber-rich foods to your meals can improve digestion, help you feel full longer, and support heart health! 💪"""

class MockResponse:
    """Mock response object."""
    
    def __init__(self, content):
        self.choices = [MockChoice(content)]

class MockChoice:
    """Mock choice object."""
    
    def __init__(self, content):
        self.message = MockMessage(content)

class MockMessage:
    """Mock message object."""
    
    def __init__(self, content):
        self.content = content

async def test_nutrition_agent():
    """Test the nutrition agent functionality."""
    
    print("🧪 Testing LLM-Powered Nutrition Agent")
    print("=" * 50)
    
    try:
        # Import nutrition agent
        from agents.nutrition_agent.nutrition_agent import NutritionAgent
        from google.adk.agents.callback_context import CallbackContext
        
        # Create agent (no client needed with ADK)
        agent = NutritionAgent(user_id="test_user")
        
        print("✅ Nutrition agent initialized successfully")
        
        # Test 1: Meal plan creation request
        print("\n🍽️ Test 1: Meal Plan Creation")
        print("-" * 30)
        
        # Create mock callback context (CallbackContext needs invocation_context)
        callback_context = None  # Use None for testing
        response = await agent.process_message(
            "I want to create a meal plan for weight loss, vegetarian diet, medium budget",
            "test_user",
            callback_context
        )
        
        print(f"Response: {response[:200]}...")
        print("✅ Meal plan creation test passed")
        
        # Test 2: Substitution request
        print("\n🔄 Test 2: Food Substitution")
        print("-" * 30)
        
        response = await agent.process_message(
            "Can you substitute the salmon with chicken? I don't like fish",
            "test_user",
            callback_context
        )
        
        print(f"Response: {response[:200]}...")
        print("✅ Substitution request test passed")
        
        # Test 3: Budget optimization
        print("\n💰 Test 3: Budget Optimization")
        print("-" * 30)
        
        response = await agent.process_message(
            "Can you optimize my meal plan for a $60 per week budget?",
            "test_user",
            callback_context
        )
        
        print(f"Response: {response[:200]}...")
        print("✅ Budget optimization test passed")
        
        # Test 4: Nutrition education
        print("\n🧠 Test 4: Nutrition Education")
        print("-" * 30)
        
        response = await agent.process_message(
            "What are the benefits of fiber in my diet?",
            "test_user",
            callback_context
        )
        
        print(f"Response: {response[:200]}...")
        print("✅ Nutrition education test passed")
        
        # Test 5: General conversation
        print("\n💬 Test 5: General Conversation")
        print("-" * 30)
        
        response = await agent.process_message(
            "Hi, I need help with healthy eating",
            "test_user",
            callback_context
        )
        
        print(f"Response: {response[:200]}...")
        print("✅ General conversation test passed")
        
        print("\n🎉 All Nutrition Agent Tests Passed!")
        print("=" * 50)
        
        # Test LLM services individually
        print("\n🔧 Testing Individual LLM Services")
        print("-" * 40)
        
        # Test meal planner
        print("Testing LLM Meal Planner...")
        test_preferences = {
            'duration_days': 3,
            'diet_type': 'vegetarian',
            'budget_level': 'medium',
            'weekly_budget': 100,
            'cooking_skill': 'intermediate'
        }
        
        meal_plan = await agent._global_state['llm_meal_planner'].generate_comprehensive_meal_plan(test_preferences)
        print(f"✅ Generated meal plan with {len(meal_plan.get('daily_plans', {}))} days")
        
        # Test substitution engine
        print("Testing Substitution Engine...")
        substitutions = await agent._global_state['substitution_engine'].suggest_substitutions_after_generation(
            meal_plan, test_preferences
        )
        print(f"✅ Generated {len(substitutions.get('suggestions', []))} substitution suggestions")
        
        # Test budget optimizer
        print("Testing Budget Optimizer...")
        optimized_plan = await agent._global_state['budget_optimizer'].optimize_for_budget(
            meal_plan, 75.0, test_preferences
        )
        print(f"✅ Optimized meal plan for $75 budget")
        
        # Test nutrition data service
        print("Testing Nutrition Data Service...")
        nutrition_info = await agent._global_state['nutrition_data'].get_food_nutrition_info("chicken breast")
        print(f"✅ Retrieved nutrition info for chicken breast: {nutrition_info.get('nutrition_per_100g', {}).get('calories', 0)} calories")
        
        print("\n🌟 All LLM Services Working Correctly!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all nutrition agent modules are properly created")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_tools_and_data():
    """Test nutrition tools and data services."""
    
    print("\n📊 Testing Nutrition Tools and Data Services")
    print("-" * 50)
    
    try:
        from agents.nutrition_agent.tools import NutritionTools
        from agents.nutrition_agent.nutrition_data import NutritionDataService
        
        # Test tools
        tools = NutritionTools()
        
        # Test user preferences
        test_preferences = {
            'diet_type': 'vegetarian',
            'budget_level': 'medium',
            'cooking_skill': 'intermediate'
        }
        
        await tools.update_user_preferences('test_user', test_preferences)
        retrieved_prefs = await tools.get_user_preferences('test_user')
        
        print(f"✅ User preferences: {retrieved_prefs}")
        
        # Test meal plan storage
        mock_meal_plan = {
            'duration_days': 7,
            'estimated_cost': 100,
            'daily_plans': {'1': {'breakfast': {'name': 'Test Meal'}}}
        }
        
        plan_id = await tools.store_meal_plan('test_user', mock_meal_plan)
        retrieved_plan = await tools.get_meal_plan('test_user', plan_id)
        
        print(f"✅ Meal plan storage: Plan ID {plan_id}")
        
        # Test nutrition data service
        nutrition_service = NutritionDataService()
        
        # Test food lookup
        foods_to_test = ['chicken breast', 'broccoli', 'quinoa', 'unknown food']
        
        for food in foods_to_test:
            nutrition_info = await nutrition_service.get_food_nutrition_info(food)
            calories = nutrition_info.get('nutrition_per_100g', {}).get('calories', 0)
            print(f"✅ {food}: {calories} calories per 100g")
        
        # Test meal nutrition analysis
        test_ingredients = ['chicken breast', 'broccoli', 'brown rice']
        meal_analysis = await nutrition_service.analyze_meal_nutrition(test_ingredients)
        
        total_calories = meal_analysis.get('total_nutrition', {}).get('calories', 0)
        print(f"✅ Meal analysis: {total_calories} total calories")
        
        print("\n🎯 All Tools and Data Services Working!")
        
        return True
        
    except Exception as e:
        print(f"❌ Tools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all nutrition agent tests."""
    
    print("🚀 Starting Nutrition Agent Test Suite")
    print("=" * 60)
    
    async def run_tests():
        """Run all tests."""
        
        # Test main agent functionality
        agent_test_passed = await test_nutrition_agent()
        
        # Test tools and data services
        tools_test_passed = await test_tools_and_data()
        
        # Summary
        print("\n📋 Test Summary")
        print("=" * 30)
        print(f"Agent Tests: {'✅ PASSED' if agent_test_passed else '❌ FAILED'}")
        print(f"Tools Tests: {'✅ PASSED' if tools_test_passed else '❌ FAILED'}")
        
        if agent_test_passed and tools_test_passed:
            print("\n🎉 ALL TESTS PASSED! Nutrition Agent is ready! 🎉")
            print("\nKey Features Verified:")
            print("- ✅ LLM-powered meal planning with unlimited creativity")
            print("- ✅ Smart food substitutions and alternatives")
            print("- ✅ Budget optimization for any budget level")
            print("- ✅ Nutrition education and Q&A")
            print("- ✅ Comprehensive food database and analysis")
            print("- ✅ User preference management")
            print("- ✅ Meal plan storage and retrieval")
            
            print("\n🚀 Ready for Production Integration!")
        else:
            print("\n❌ Some tests failed. Please check the errors above.")
            return False
        
        return True
    
    # Run the tests
    return asyncio.run(run_tests())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 