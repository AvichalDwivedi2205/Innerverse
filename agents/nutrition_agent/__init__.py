"""
Nutrition Agent Package

This package contains the nutrition agent implementation for the Innerverse platform.
It provides nutritional guidance, meal planning, and dietary recommendations
with integration to food databases and image recognition capabilities.

Components:
- agent_file.py: Main NutritionAgent class with Google ADK integration
- prompt_file.py: Nutrition-specific prompts for meal planning and dietary guidance
- tool_file.py: Tools for food database access, meal tracking, and nutritional analysis
"""

from .agent_file import NutritionAgent
from .prompt_file import NutritionPrompts
from .tool_file import USDAFoodDatabaseTool, FoodImageAnalysisTool, MealPlanStorageTool

__all__ = [
    'NutritionAgent',
    'NutritionPrompts',
    'USDAFoodDatabaseTool',
    'FoodImageAnalysisTool',
    'MealPlanStorageTool'
]

__version__ = '1.0.0'
__author__ = 'Innerverse Team' 