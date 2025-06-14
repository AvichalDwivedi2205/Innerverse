"""
Fitness Agent Package

This package contains the fitness agent implementation for the Innerverse platform.
It provides safe exercise guidance, workout planning, and personal training consultation
with a focus on respecting physical limitations and providing modifications.

Components:
- agent_file.py: Main FitnessAgent class with Google ADK integration
- prompt_file.py: Fitness-specific prompts for workout planning and consultation
- tool_file.py: Tools for exercise database, workout tracking, and progress monitoring
"""

from .agent_file import FitnessAgent
from .prompt_file import FitnessPrompts
from .tool_file import ExerciseDatabaseTool, WorkoutTrackingTool, WorkoutPlanStorageTool

__all__ = [
    'FitnessAgent',
    'FitnessPrompts',
    'ExerciseDatabaseTool',
    'WorkoutTrackingTool',
    'WorkoutPlanStorageTool'
]

__version__ = '1.0.0'
__author__ = 'Innerverse Team' 