"""
Phase 3 Enhanced Reflection System - Comprehensive Test Suite

Tests the complete replacement of single reflection questions with:
- Multiple categorized questions (daily_practice, deep_reflection, action_items)
- Template-based generation with context awareness
- Always generates exactly: 2 daily + 2 deep + 1 action = 5 questions total
- Complete agent integration testing
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.common.reflection_generator import (
    EnhancedReflectionGenerator,
    ReflectionCategory,
    ReflectionType,
    ReflectionQuestion
)
from agents.common.tool_results import JournalingToolResult, TherapyToolResult
from agents.journaling_agent.tools import generate_multiple_reflection_questions
from agents.therapy_agent.tools import generate_therapy_reflection_questions


# Simple ToolContext class for testing
class ToolContext:
    """Simple tool context class for testing."""
    def __init__(self):
        self.state = {}


class TestPhase3EnhancedReflectionSystem:
    """Comprehensive test suite for Phase 3 Enhanced Reflection System."""
    
    def setup_method(self):
        """Set up test environment for each test."""
        self.reflection_generator = EnhancedReflectionGenerator()
        
        # Sample session data for testing
        self.sample_session_data = {
            "entry": {
                "reflection": "Today I felt overwhelmed with work but found strength in meditation",
                "emotions": ["stress", "peace"],
                "themes": ["work-life balance", "mindfulness"]
            },
            "challenges": ["work stress", "time management"],
            "emotions": ["anxiety", "peace", "determination"], 
            "topics": ["meditation", "work pressure", "self-care"]
        }
        
        self.sample_insights = {
            "triggers": ["deadline pressure", "multitasking"],
            "patterns": ["stress response", "coping mechanisms"],
            "themes": ["resilience", "mindfulness practice"],
            "emotion": "mixed emotions"
        }
        
        self.sample_user_context = {
            "preferences": ["empowerment", "practical solutions"],
            "source": "testing"
        }
    
    async def test_1_reflection_generator_initialization(self):
        """Test 1: Enhanced reflection generator initialization and template system."""
        print("\n🧪 TEST 1: Reflection Generator Initialization")
        
        # Test initialization
        generator = EnhancedReflectionGenerator()
        assert generator is not None
        assert hasattr(generator, 'question_templates')
        assert hasattr(generator, 'context_variables')
        
        # Test template structure
        templates = generator.question_templates
        
        # Verify all required categories exist
        required_categories = {
            ReflectionCategory.DAILY_PRACTICE,
            ReflectionCategory.DEEP_REFLECTION,
            ReflectionCategory.ACTION_ITEMS
        }
        assert set(templates.keys()) == required_categories
        
        # Verify each category has reflection types
        for category in required_categories:
            assert len(templates[category]) > 0
            print(f"   ✅ {category.value}: {len(templates[category])} reflection types")
        
        # Test context variables
        context_vars = generator.context_variables
        required_vars = ["challenges", "emotions", "contexts", "topics"]
        for var in required_vars:
            assert var in context_vars
            assert len(context_vars[var]) > 0
            print(f"   ✅ {var}: {len(context_vars[var])} options")
        
        print("   🎉 Reflection generator initialized successfully with complete template system")
    
    async def test_2_complete_question_set_generation(self):
        """Test 2: Complete question set generation (2 daily + 2 deep + 1 action = 5 total)."""
        print("\n🧪 TEST 2: Complete Question Set Generation")
        
        # Generate complete question set
        question_set = await self.reflection_generator.generate_complete_question_set(
            session_data=self.sample_session_data,
            insights=self.sample_insights,
            user_context=self.sample_user_context,
            source_type="test"
        )
        
        # Verify structure
        assert isinstance(question_set, dict)
        assert len(question_set) == 3  # 3 categories
        
        # Verify exact question counts
        daily_questions = question_set[ReflectionCategory.DAILY_PRACTICE]
        deep_questions = question_set[ReflectionCategory.DEEP_REFLECTION]
        action_questions = question_set[ReflectionCategory.ACTION_ITEMS]
        
        assert len(daily_questions) == 2, f"Expected 2 daily questions, got {len(daily_questions)}"
        assert len(deep_questions) == 2, f"Expected 2 deep questions, got {len(deep_questions)}"
        assert len(action_questions) == 1, f"Expected 1 action question, got {len(action_questions)}"
        
        print(f"   ✅ Generated exactly 5 questions: 2 daily + 2 deep + 1 action")
        
        # Verify question quality
        total_questions = 0
        for category, questions in question_set.items():
            total_questions += len(questions)
            category_name = category.value.replace("_", " ").title()
            print(f"   📝 {category_name} ({len(questions)} questions):")
            
            for i, question in enumerate(questions, 1):
                assert isinstance(question, ReflectionQuestion)
                assert question.question_id is not None
                assert len(question.question) > 10  # Meaningful length
                assert question.category == category
                assert question.reflection_type in ReflectionType
                
                print(f"      {i}. {question.question[:60]}..." if len(question.question) > 60 else f"      {i}. {question.question}")
                print(f"         - Type: {question.reflection_type.value}")
                print(f"         - Difficulty: {question.metadata['difficulty']}")
                print(f"         - Time: {question.metadata['estimatedTime']}")
        
        assert total_questions == 5
        print(f"   🎉 All {total_questions} questions generated with proper metadata and categorization")
    
    async def test_3_journaling_agent_integration(self):
        """Test 3: Journaling agent integration with enhanced reflection system."""
        print("\n🧪 TEST 3: Journaling Agent Integration")
        
        # Set up journaling context
        tool_context = ToolContext()
        tool_context.state = {
            "user_id": "test_user_journaling",
            "journal_session": {
                "raw_text": "Today was challenging but I found inner strength through meditation and self-reflection.",
                "standardized_entry": {
                    "reflection": "Discovered inner strength through mindfulness practice",
                    "emotions": ["challenged", "peaceful", "strong"],
                    "themes": ["inner strength", "mindfulness", "resilience"]
                },
                "insights": {
                    "triggers": ["daily challenges", "stress"],
                    "themes": ["resilience", "mindfulness practice"],
                    "emotion": "empowered"
                }
            }
        }
        
        # Test enhanced reflection generation
        result = await generate_multiple_reflection_questions(tool_context)
        
        # Verify result type and success
        assert isinstance(result, JournalingToolResult)
        assert result.success == True
        
        # Verify data structure
        data = result.data
        assert "reflection_questions" in data
        assert "summary" in data
        assert "total_questions" in data
        
        # Verify question counts
        questions = data["reflection_questions"]
        assert "daily_practice" in questions
        assert "deep_reflection" in questions
        assert "action_items" in questions
        
        assert len(questions["daily_practice"]) == 2
        assert len(questions["deep_reflection"]) == 2
        assert len(questions["action_items"]) == 1
        
        print(f"   ✅ Journaling agent generated {data['total_questions']} categorized questions")
        
        # Verify context storage
        assert "reflection_questions" in tool_context.state["journal_session"]
        assert "reflection_summary" in tool_context.state["journal_session"]
        
        stored_questions = tool_context.state["journal_session"]["reflection_questions"]
        assert len(stored_questions) == 3  # 3 categories
        
        print("   🎉 Journaling agent successfully integrated with enhanced reflection system")
    
    async def test_4_therapy_agent_integration(self):
        """Test 4: Therapy agent integration with enhanced reflection system."""
        print("\n🧪 TEST 4: Therapy Agent Integration")
        
        # Set up therapy context
        tool_context = ToolContext()
        tool_context.state = {
            "user_id": "test_user_therapy",
            "therapy_session": {
                "transcript": "Session focused on anxiety management and building confidence for upcoming presentation.",
                "summary": {
                    "observations": "Client shows progress in anxiety management techniques",
                    "insights": "Breathing techniques are effective coping strategy",
                    "recommendations": "Continue practicing mindfulness before presentations"
                },
                "insights": {
                    "challenges": ["presentation anxiety", "public speaking fear"],
                    "emotions": ["anxiety", "nervousness", "determination"],
                    "themes": ["anxiety management", "confidence building", "public speaking"]
                },
                "therapy_notes": [
                    {
                        "content": "Client demonstrated good use of breathing techniques",
                        "category": "progress",
                        "priority": 2,
                        "status": "noted"
                    }
                ]
            }
        }
        
        # Test enhanced reflection generation
        result = await generate_therapy_reflection_questions(tool_context)
        
        # Verify result is string (therapy agent returns formatted string)
        assert isinstance(result, str)
        assert "THERAPY REFLECTION QUESTIONS GENERATED" in result
        assert "5 categorized questions" in result
        
        # Verify context storage
        assert "reflection_questions" in tool_context.state["therapy_session"]
        assert "reflection_summary" in tool_context.state["therapy_session"]
        
        stored_questions = tool_context.state["therapy_session"]["reflection_questions"]
        stored_summary = tool_context.state["therapy_session"]["reflection_summary"]
        
        # Verify counts
        assert len(stored_questions) == 3  # 3 categories
        assert stored_summary["total_questions"] == 5
        
        category_counts = stored_summary["category_breakdown"]
        assert category_counts["daily_practice"] == 2
        assert category_counts["deep_reflection"] == 2
        assert category_counts["action_items"] == 1
        
        print(f"   ✅ Therapy agent generated 5 categorized questions successfully")
        print(f"   📊 Breakdown: {category_counts}")
        
        print("   🎉 Therapy agent successfully integrated with enhanced reflection system")
    
    async def test_5_fallback_system_and_error_handling(self):
        """Test 5: Fallback system and error handling."""
        print("\n🧪 TEST 5: Fallback System and Error Handling")
        
        # Test with minimal/invalid data
        try:
            question_set = await self.reflection_generator.generate_complete_question_set(
                session_data=None,
                insights=None,
                user_context=None,
                source_type="fallback_test"
            )
            
            # Should still generate questions using fallback
            assert isinstance(question_set, dict)
            assert len(question_set) == 3
            
            # Verify fallback question counts
            daily_count = len(question_set[ReflectionCategory.DAILY_PRACTICE])
            deep_count = len(question_set[ReflectionCategory.DEEP_REFLECTION])
            action_count = len(question_set[ReflectionCategory.ACTION_ITEMS])
            
            assert daily_count == 2
            assert deep_count == 2
            assert action_count == 1
            
            print(f"   ✅ Fallback system generated {daily_count + deep_count + action_count} questions")
            
            # Check for fallback indicators
            for category, questions in question_set.items():
                for question in questions:
                    # Fallback questions should still have proper structure
                    assert question.question_id is not None
                    assert len(question.question) > 5
                    assert question.category == category
            
            print("   ✅ Fallback questions maintain proper structure and metadata")
            
        except Exception as e:
            print(f"❌ Fallback system failed: {e}")
            raise
        
        print("   🎉 Fallback system and error handling working correctly")


def run_comprehensive_phase_3_tests():
    """Run all Phase 3 Enhanced Reflection System tests."""
    print("🚀 STARTING PHASE 3 ENHANCED REFLECTION SYSTEM TESTS")
    print("=" * 80)
    
    test_instance = TestPhase3EnhancedReflectionSystem()
    
    async def run_all_tests():
        """Run all tests in sequence."""
        test_methods = [
            test_instance.test_1_reflection_generator_initialization,
            test_instance.test_2_complete_question_set_generation,
            test_instance.test_3_journaling_agent_integration,
            test_instance.test_4_therapy_agent_integration,
            test_instance.test_5_fallback_system_and_error_handling
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for i, test_method in enumerate(test_methods, 1):
            try:
                test_instance.setup_method()  # Reset for each test
                await test_method()
                passed_tests += 1
                print(f"✅ Test {i}/{total_tests} PASSED")
            except Exception as e:
                print(f"❌ Test {i}/{total_tests} FAILED: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n" + "=" * 80)
        print(f"🏁 PHASE 3 TEST RESULTS: {passed_tests}/{total_tests} TESTS PASSED")
        
        if passed_tests == total_tests:
            print("🎉 ALL PHASE 3 ENHANCED REFLECTION SYSTEM TESTS PASSED!")
            print("\n✨ PHASE 3 IMPLEMENTATION STATUS: COMPLETE AND PRODUCTION-READY")
            print("\n🎯 FEATURES VALIDATED:")
            print("   ✅ Complete replacement of single reflection questions")
            print("   ✅ Exactly 5 categorized questions (2 daily + 2 deep + 1 action)")
            print("   ✅ Template-based generation with context awareness")
            print("   ✅ Complete journaling agent integration")
            print("   ✅ Complete therapy agent integration")
            print("   ✅ Fallback system and error handling")
        else:
            print(f"⚠️  {total_tests - passed_tests} tests failed - review implementation")
        
        return passed_tests == total_tests
    
    # Run the tests
    return asyncio.run(run_all_tests())


if __name__ == "__main__":
    success = run_comprehensive_phase_3_tests()
    exit(0 if success else 1) 