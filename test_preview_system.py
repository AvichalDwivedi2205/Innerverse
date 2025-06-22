#!/usr/bin/env python3
"""
Test script for the Mental Health Preview System.
This script tests the preview generation and storage functionality.
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

try:
    from agents.mental_orchestrator_agent.tools import create_dashboard_preview, preview_storage
    print("✅ Successfully imported preview tools")
    
    # Create a simple ToolContext mock since we don't need the full ADK for testing
    class ToolContext:
        def __init__(self):
            self.state = {}
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

async def test_preview_generation():
    """Test preview generation functionality"""
    print("\n🧪 Testing Preview Generation...")
    
    # Create a mock tool context
    class MockToolContext:
        def __init__(self):
            self.state = {
                "user_id": "test_user_avichal",
                "preview_base_url": "http://localhost:8003"
            }
    
    tool_context = MockToolContext()
    
    try:
        # Generate a preview
        result = await create_dashboard_preview(tool_context)
        print("📊 Preview generation result:")
        print(result)
        
        # Check storage stats
        stats = preview_storage.get_stats()
        print(f"\n📈 Storage stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Preview generation failed: {e}")
        return False

def test_storage_system():
    """Test the preview storage system"""
    print("\n🗄️ Testing Storage System...")
    
    try:
        # Store a test preview
        test_html = """
        <html>
        <head><title>Test Preview</title></head>
        <body>
            <h1>Test Mental Health Dashboard</h1>
            <p>This is a test preview for Avichal Dwivedi</p>
        </body>
        </html>
        """
        
        preview_id = preview_storage.store_preview(test_html, "Test Dashboard")
        print(f"✅ Stored preview with ID: {preview_id}")
        
        # Retrieve the preview
        retrieved_html = preview_storage.get_preview(preview_id)
        if retrieved_html:
            print("✅ Successfully retrieved preview")
            print(f"📝 Preview length: {len(retrieved_html)} characters")
        else:
            print("❌ Failed to retrieve preview")
        
        # Get stats
        stats = preview_storage.get_stats()
        print(f"📊 Storage stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Storage test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🧠 Mental Health Preview System Test")
    print("=" * 50)
    
    # Test storage system
    storage_ok = test_storage_system()
    
    # Test preview generation
    preview_ok = await test_preview_generation()
    
    print("\n" + "=" * 50)
    if storage_ok and preview_ok:
        print("🎉 All tests passed! Preview system is working correctly.")
        print("\n🚀 Next steps:")
        print("1. Start the preview server: python preview_server.py")
        print("2. Start ADK: adk web")
        print("3. Test with: 'Create a dashboard preview for my mental health insights'")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
    
    return storage_ok and preview_ok

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 