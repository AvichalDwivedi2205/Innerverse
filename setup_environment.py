#!/usr/bin/env python3
"""
Modern setup script for Innerverse Agent System.
This script ensures all dependencies are installed with the latest compatible versions.
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and handle errors."""
    print(f"🔧 {description}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"   Details: {e.stderr.strip()}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ is required for optimal compatibility")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True


def setup_virtual_environment():
    """Create and activate virtual environment."""
    venv_path = Path("venv")
    
    if not venv_path.exists():
        print("🌟 Creating virtual environment...")
        if not run_command("python3 -m venv venv", "Creating virtual environment"):
            return False
    else:
        print("✅ Virtual environment already exists")
    
    # Check if we're in a virtual environment
    if not os.environ.get('VIRTUAL_ENV'):
        print("⚠️  Please activate the virtual environment first:")
        print("   source venv/bin/activate  # On Linux/Mac")
        print("   venv\\Scripts\\activate     # On Windows")
        return False
    
    print("✅ Virtual environment is active")
    return True


def install_modern_dependencies():
    """Install the latest compatible versions of all dependencies."""
    print("📦 Installing modern dependencies...")
    
    # Modern requirements with specific versions for stability
    modern_requirements = {
        # Google Cloud & AI
        "google-cloud-firestore": ">=2.15.0",
        "google-cloud-aiplatform": ">=1.43.0", 
        "google-genai": ">=1.2.0",
        "google-adk": ">=1.3.0",
        "vertexai": ">=1.43.0",
        
        # Vector database (NEW Pinecone)
        "pinecone": ">=7.0.0",  # Latest version
        
        # Data processing
        "numpy": ">=1.24.0",
        "scikit-learn": ">=1.4.0",
        "pandas": ">=2.0.0",
        
        # API & Web
        "pydantic": ">=2.5.0",
        "fastapi": ">=0.108.0",
        "uvicorn[standard]": ">=0.25.0",
        "aiohttp": ">=3.9.0",
        
        # Utilities
        "python-dotenv": ">=1.0.0",
        "requests": ">=2.31.0",
        
        # Testing
        "pytest": ">=7.4.0",
        "pytest-asyncio": ">=0.23.0",
        "pytest-mock": ">=3.12.0",
        "pytest-cov": ">=4.1.0",
        
        # Development
        "black": ">=23.12.0",
        "flake8": ">=7.0.0",
        "mypy": ">=1.8.0",
    }
    
    # Install packages
    for package, version in modern_requirements.items():
        cmd = f"pip install '{package}{version}'"
        if not run_command(cmd, f"Installing {package}"):
            print(f"⚠️  Failed to install {package}, continuing...")
    
    return True


def update_requirements_file():
    """Update requirements.txt with modern versions."""
    print("📝 Updating requirements.txt...")
    
    modern_requirements = [
        "# Google Cloud & AI Platform",
        "google-cloud-firestore>=2.15.0",
        "google-cloud-aiplatform>=1.43.0", 
        "google-genai>=1.2.0",
        "google-adk>=1.3.0",
        "vertexai>=1.43.0",
        "",
        "# Vector Database (Latest Pinecone)",
        "pinecone>=7.0.0",
        "",
        "# Data Processing",
        "numpy>=1.24.0",
        "scikit-learn>=1.4.0",
        "pandas>=2.0.0",
        "",
        "# API & Web Framework",
        "pydantic>=2.5.0",
        "fastapi>=0.108.0",
        "uvicorn[standard]>=0.25.0",
        "aiohttp>=3.9.0",
        "",
        "# Utilities",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "",
        "# Testing Framework",
        "pytest>=7.4.0",
        "pytest-asyncio>=0.23.0",
        "pytest-mock>=3.12.0",
        "pytest-cov>=4.1.0",
        "",
        "# Development Tools",
        "black>=23.12.0",
        "flake8>=7.0.0",
        "mypy>=1.8.0",
    ]
    
    with open("requirements.txt", "w") as f:
        f.write("\n".join(modern_requirements))
    
    print("✅ requirements.txt updated with modern versions")
    return True


def verify_pinecone_installation():
    """Verify Pinecone installation and version."""
    print("🌲 Verifying Pinecone installation...")
    
    try:
        import pinecone
        print(f"✅ Pinecone version: {pinecone.__version__}")
        
        # Check if it's the new API
        from pinecone import Pinecone, ServerlessSpec
        print("✅ New Pinecone API detected")
        return True
    except ImportError as e:
        print(f"❌ Pinecone import failed: {e}")
        return False
    except Exception as e:
        print(f"⚠️  Pinecone verification issue: {e}")
        return False


def check_environment_file():
    """Check if .env file exists and has required variables."""
    print("🔐 Checking environment configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("   Please copy env-example.txt to .env and fill in your values")
        return False
    
    required_vars = [
        "PINECONE_API_KEY",
        "PINECONE_INDEX_NAME", 
        "PINECONE_HOST"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ Environment configuration looks good")
    return True


def run_quick_test():
    """Run a quick test to verify everything works."""
    print("🧪 Running quick verification test...")
    
    cmd = "python -c \"from agents.common.pinecone_service import pinecone_service; print('✅ Pinecone service loads successfully')\""
    return run_command(cmd, "Testing Pinecone service import")


def main():
    """Main setup function."""
    print("🚀 Innerverse Agent System - Modern Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Setup virtual environment
    if not setup_virtual_environment():
        sys.exit(1)
    
    # Update requirements file
    update_requirements_file()
    
    # Install dependencies
    if not install_modern_dependencies():
        print("⚠️  Some dependencies failed to install, but continuing...")
    
    # Verify Pinecone
    if not verify_pinecone_installation():
        print("❌ Pinecone verification failed")
        sys.exit(1)
    
    # Check environment
    check_environment_file()
    
    # Run quick test
    if run_quick_test():
        print("\n🎉 Setup completed successfully!")
        print("Next steps:")
        print("1. Make sure your .env file is configured")
        print("2. Run tests: python run_tests.py")
        print("3. Start ADK web: python run_adk_web.py")
    else:
        print("\n⚠️  Setup completed but verification failed")
        print("Please check your configuration and try again")


if __name__ == "__main__":
    main() 