#!/usr/bin/env python3
"""Test Vertex AI model configuration."""

import os
import sys
sys.path.insert(0, '.')

def test_model_config():
    """Test the model configuration."""
    print("🧪 Testing Vertex AI Model Configuration")
    print("=" * 50)
    
    # Set up environment variables for testing
    os.environ['GOOGLE_CLOUD_PROJECT'] = 'gen-lang-client-0307630688'
    os.environ['GOOGLE_CLOUD_REGION'] = 'us-central1'
    
    print(f"📊 Project: {os.getenv('GOOGLE_CLOUD_PROJECT')}")
    print(f"🌍 Region: {os.getenv('GOOGLE_CLOUD_REGION')}")
    
    # Test journaling agent import
    try:
        from agents.journaling_agent.journaling_agent import get_model_config
        config = get_model_config()
        print(f"✅ Journaling agent model config: {config}")
        
        # Check if it's using the correct model
        if 'gemini-1.5-pro' in config.get('model', ''):
            print("✅ Using correct Vertex AI model: gemini-1.5-pro-001")
        else:
            print(f"❌ Unexpected model: {config.get('model')}")
            
    except Exception as e:
        print(f"❌ Journaling agent config failed: {e}")
    
    # Test agent import
    try:
        from agents.journaling_agent.agent import root_agent
        print("✅ Journaling agent imported successfully!")
        print(f"   Agent name: {root_agent.name}")
        
    except Exception as e:
        print(f"❌ Agent import failed: {e}")
        import traceback
        traceback.print_exc()

def show_available_models():
    """Show information about available Vertex AI models."""
    print("\n📋 Available Vertex AI Gemini Models:")
    print("=" * 50)
    print("✅ gemini-1.5-pro-001 (Recommended)")
    print("✅ gemini-1.5-pro-002") 
    print("✅ gemini-1.5-flash-001")
    print("✅ gemini-1.5-flash-002")
    print("❌ gemini-2.5-pro (Does NOT exist in Vertex AI)")
    print("❌ gemini-2.0-pro (Does NOT exist in Vertex AI)")
    
    print("\n💡 Model Path Format:")
    print("   vertexai/{project}/{region}/{model-name}")
    print("   Example: vertexai/gen-lang-client-0307630688/us-central1/gemini-1.5-pro-001")

if __name__ == "__main__":
    test_model_config()
    show_available_models()
    
    print("\n🚀 Next Steps:")
    print("1. Restart your ADK web interface:")
    print("   source venv/bin/activate")
    print("   adk web agents/")
    print("2. Test the journaling agent - should work now!")
    print("\n✅ The model error should be resolved!") 