#!/usr/bin/env python3
"""Script to run ADK web interface for Innerverse Agent System."""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed, environment variables from .env file won't be loaded")
    print("   Install with: pip install python-dotenv")


def check_environment():
    """Check if environment is properly configured."""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("Please copy env-example.txt to .env and fill in your values.")
        return False
    
    # Check for Google AI API key first (prioritized)
    google_api_key = os.getenv('GOOGLE_API_KEY')
    if google_api_key:
        print("✅ Google AI API configuration found!")
        print(f"   Using Google AI API with key: {google_api_key[:10]}...{google_api_key[-4:]}")
        # Set the environment variable to use Google AI
        os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'FALSE'
        return True
    
    # Fallback to Vertex AI configuration
    required_vars = [
        "GOOGLE_CLOUD_PROJECT",
        "GOOGLE_APPLICATION_CREDENTIALS", 
        "GOOGLE_CLOUD_REGION"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ No Google AI API key found and missing Vertex AI variables: {', '.join(missing_vars)}")
        print("Please either:")
        print("1. Set GOOGLE_API_KEY in your .env file (recommended), OR")
        print("2. Configure Vertex AI with the missing variables")
        return False
    
    print("✅ Vertex AI configuration found!")
    # Set the environment variable to use Vertex AI
    os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'TRUE'
    return True


def run_adk_web(agent_path="agents/", port=8000, host="localhost"):
    """Run ADK web interface.
    
    Args:
        agent_path: Path to the agents directory
        port: Port to run the web interface on
        host: Host to bind to
    """
    try:
        # Set up environment variables
        os.environ['GOOGLE_CLOUD_PROJECT'] = 'gen-lang-client-0307630688'
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'service-account-key.json'
        
        print("🚀 Starting ADK web interface...")
        print(f"📍 Agent path: {agent_path}")
        print(f"🌐 URL: http://localhost:{port}")
        print("Press Ctrl+C to stop")
        
        # Start the ADK web interface with custom port
        result = subprocess.run([
            "adk", "web", agent_path, "--port", str(port), "--host", "0.0.0.0"
        ], check=True)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start ADK web interface: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 ADK web interface stopped by user")
        return True
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run ADK web interface for Innerverse agents")
    parser.add_argument(
        "--agent",
        default="agents/",
        help="Path to agent directory (default: agents/)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run on (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind to (default: localhost)"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check environment, don't start ADK"
    )
    
    args = parser.parse_args()
    
    print("🔧 Innerverse ADK Web Interface Launcher")
    print("=" * 50)
    
    # Check environment first
    if not check_environment():
        sys.exit(1)
    
    if args.check_only:
        print("✅ Environment check completed successfully!")
        return
    
    # Verify agent path exists
    agent_path = Path(args.agent)
    if not agent_path.exists():
        print(f"❌ Agent path does not exist: {agent_path}")
        sys.exit(1)
    
    # Run ADK web interface
    success = run_adk_web(
        agent_path=str(agent_path),
        port=args.port,
        host=args.host
    )
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main() 