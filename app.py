#!/usr/bin/env python3
"""
Production startup script for Innerverse Multi-Agent System

This script uses the ADK CLI to start the multi-agent web interface
in production mode.
"""

import os
import sys
import subprocess
from pathlib import Path

# Set up environment variables for production
os.environ.setdefault('GOOGLE_GENAI_USE_VERTEXAI', 'False')  # Use Google AI API, not Vertex AI
os.environ.setdefault('ENVIRONMENT', 'production')
os.environ.setdefault('USER_TIMEZONE', 'America/New_York')

def main():
    # Get port from environment or default to 8080
    port = int(os.environ.get("PORT", 8080))
    
    print(f"🚀 Starting Innerverse Multi-Agent System on port {port}")
    print("🌟 Available agents:")
    
    # List available agents
    agents_dir = Path("agents")
    if agents_dir.exists():
        for agent_dir in agents_dir.iterdir():
            if agent_dir.is_dir() and (agent_dir / "__init__.py").exists():
                print(f"   • {agent_dir.name}")
    
    # Build ADK command
    cmd = [
        "adk", "web", "agents/",
        "--port", str(port),
        "--host", "0.0.0.0"
    ]
    
    print(f"🔧 ADK Command: {' '.join(cmd)}")
    
    try:
        # Start ADK web interface
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ ADK web interface failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 