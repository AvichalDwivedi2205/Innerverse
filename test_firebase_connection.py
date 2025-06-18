#!/usr/bin/env python3
"""Test Firebase connection for cloud hosting."""

import os
import sys
from datetime import datetime

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env")
except ImportError:
    print("⚠️  python-dotenv not available, using system environment")

# Set up environment
os.environ['GOOGLE_CLOUD_PROJECT'] = 'gen-lang-client-0307630688'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'service-account-key.json'

def test_firebase_connection():
    """Test Firebase Firestore connection."""
    try:
        from google.cloud import firestore
        
        # Initialize client
        db = firestore.Client(project='gen-lang-client-0307630688')
        print("✅ Firebase client initialized")
        
        # Test connection by writing a test document
        test_doc = {
            "test": True,
            "timestamp": datetime.now().isoformat(),
            "message": "Firebase connection test for hackathon"
        }
        
        # Write test document
        doc_ref = db.collection("test").document("connection_test")
        doc_ref.set(test_doc)
        print("✅ Test document written to Firebase")
        
        # Read it back
        doc = doc_ref.get()
        if doc.exists:
            print("✅ Test document read successfully")
            print(f"   Data: {doc.to_dict()}")
        else:
            print("❌ Test document not found")
            
        # Clean up
        doc_ref.delete()
        print("✅ Test document cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Firebase connection failed: {e}")
        return False

def test_google_ai():
    """Test Google AI API."""
    try:
        import google.generativeai as genai
        
        # Configure with API key
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("❌ GOOGLE_API_KEY not found")
            return False
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        response = model.generate_content("Say hello for hackathon test")
        print(f"✅ Google AI API working: {response.text[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ Google AI API failed: {e}")
        return False

if __name__ == "__main__":
    print("🔬 Testing Cloud Services for Hackathon")
    print("=" * 50)
    
    firebase_ok = test_firebase_connection()
    ai_ok = test_google_ai()
    
    print("\n📊 Test Results:")
    print(f"   Firebase: {'✅' if firebase_ok else '❌'}")
    print(f"   Google AI: {'✅' if ai_ok else '❌'}")
    
    if firebase_ok and ai_ok:
        print("\n🎉 All cloud services ready for hackathon!")
    else:
        print("\n⚠️  Some services need fixing before hosting") 