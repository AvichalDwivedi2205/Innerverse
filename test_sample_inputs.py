#!/usr/bin/env python3
"""Sample inputs for testing agents in ADK web interface."""

print("🧪 ADK Web Interface Test Inputs")
print("=" * 50)

print("\n🔧 1. JOURNALING AGENT - Empowerment Focus")
print("-" * 40)
print("📝 Input to paste in ADK web:")
print('"I had a really challenging day at work today. My manager criticized my presentation in front of the whole team, and I felt embarrassed and frustrated. But then I realized that maybe I\'m creating this stress by taking things too personally. I wonder if I can learn to see criticism as feedback rather than attacks. I want to feel more empowered in these situations."')
print("\n✅ Expected: Structured journal processing with empowerment themes, insights, and reflection questions")

print("\n🔧 2. THERAPY AGENT - Relationship Patterns")  
print("-" * 40)
print("📝 Input to paste in ADK web:")
print('"I keep having the same argument with my partner about household chores. Every time we discuss it, I get defensive and feel like they\'re attacking me personally. I know this pattern isn\'t healthy, but I can\'t seem to break out of it. How can I approach this differently and take more responsibility for my reactions?"')
print("\n✅ Expected: Therapeutic insights with empowerment-focused guidance and practical suggestions")

print("\n🔧 3. MENTAL ORCHESTRATOR AGENT - Mind Map Update")
print("-" * 40)
print("📝 Input to paste in ADK web (JSON format):")
print('''{
  "user_id": "test_user_123",
  "source_type": "journal", 
  "source_id": "journal_456",
  "trigger_type": "mindmap_update",
  "context": {
    "journal_entry": {
      "reflection": "I create my own stress through negative thinking patterns",
      "empowerment_theme": "self_creation",
      "insights": ["pattern_recognition", "thought_awareness"]
    }
  }
}''')
print("\n✅ Expected: Mind map updates with pattern recognition and trend analysis")

print("\n🚀 HOW TO USE:")
print("1. Copy the input text above (including quotes)")
print("2. Paste into the ADK web interface message field")  
print("3. Click 'Send' or press Enter")
print("4. Check that you get structured responses (JournalingToolResult, etc.)")

print("\n💡 PRO TIP: The agents now return structured results instead of plain strings!")
print("Look for 'success', 'data', 'message', and 'next_suggested_actions' in responses.")

print("\n🔍 TROUBLESHOOTING:")
print("- If agents don't respond, check the 'Trace' tab for errors")
print("- If you see Google Cloud errors, those are expected (agents work in simulation mode)")
print("- Pinecone operations will use fallback data when API unavailable") 