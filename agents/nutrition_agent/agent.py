"""ADK Agent Interface for Nutrition Agent.

This file exposes the root_agent that the ADK web interface expects to find.
It wraps the NutritionAgent class to make it compatible with ADK web.
"""

import os
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext

from agents.nutrition_agent.nutrition_agent import NutritionAgent
from agents.nutrition_agent.tools import NutritionTools
from agents.nutrition_agent.prompts import NUTRITION_AGENT_SYSTEM_PROMPT

# Create the nutrition agent instance
nutrition_agent = NutritionAgent()

# Expose the root_agent for ADK web
root_agent = nutrition_agent

# Create nutrition tools instance
nutrition_tools = NutritionTools()

# Alternative configuration with ADK agent
root_agent = Agent(
    model="gemini-2.5-flash",
    name="nutrition_agent", 
    instruction=NUTRITION_AGENT_SYSTEM_PROMPT,
    tools=[]  # Tools will be accessed through the nutrition_agent instance
)

# For compatibility with different naming conventions
agent = root_agent
main_agent = root_agent 