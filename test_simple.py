#!/usr/bin/env python3
"""Simple test to verify core functionality."""

import sys
import os
sys.path.insert(0, '.')

def test_imports():
    """Test that core imports work."""
    try:
        from agents.journaling_agent.tools import standardize_journal_text
        from agents.common.tool_results import JournalingToolResult
        print("✅ Core imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_google_ai_model():
    """Test Google AI model access."""
    try:
        from agents.journaling_agent.tools import get_gemini_model
        model = get_gemini_model()
        print("✅ Google AI model initialized")
        return True
    except Exception as e:
        print(f"❌ Model initialization failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Running Simple Tests")
    print("=" * 30)
    
    success_count = 0
    
    if test_imports():
        success_count += 1
    
    if test_google_ai_model():
        success_count += 1
    
    print(f"\n📊 Results: {success_count}/2 tests passed")
    
    if success_count == 2:
        print("🎉 All basic tests passed!")
    else:
        print("⚠️  Some tests failed") 