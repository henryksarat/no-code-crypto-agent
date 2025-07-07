#!/usr/bin/env python3
"""
Solana Wallet Agent Web Interface Startup Script

This script starts the web interface for the Solana Wallet Agent.
It checks for required dependencies and environment setup before starting the Flask server.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """Check if the environment is properly set up"""
    issues = []
    
    # Check if .env file exists
    env_file = Path('.env')
    if not env_file.exists():
        issues.append("❌ .env file not found")
        print("📝 Please create a .env file with the following variables:")
        print("   OPENAI_API_KEY=your_openai_api_key")
        print("   FUNDING_WALLET_PRIVATE_KEY=your_funding_wallet_private_key")
        print("   FUNDING_WALLET_PUBLIC_KEY=your_funding_wallet_public_key")
        print()
    else:
        print("✅ .env file found")
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        issues.append("❌ Virtual environment not activated")
        print("📝 Please activate your virtual environment:")
        print("   source venv/bin/activate  # On macOS/Linux")
        print("   venv\\Scripts\\activate     # On Windows")
        print()
    else:
        print("✅ Virtual environment activated")
    
    # Check if required packages are installed
    try:
        import flask
        import flask_cors
        print("✅ Flask dependencies installed")
    except ImportError:
        issues.append("❌ Flask dependencies not installed")
        print("📝 Please install Flask dependencies:")
        print("   pip install flask flask-cors")
        print()
    
    try:
        import dspy
        print("✅ DSPy dependency available")
    except ImportError:
        issues.append("❌ DSPy not installed")
        print("📝 Please install all dependencies:")
        print("   pip install -r requirements.txt")
        print()
    
    return len(issues) == 0, issues

def main():
    """Main function to start the web interface"""
    print("🚀 Starting Solana Wallet Agent Web Interface")
    print("=" * 50)
    
    # Check environment
    env_ok, issues = check_environment()
    
    if not env_ok:
        print("\n❌ Environment setup issues detected:")
        for issue in issues:
            print(f"   {issue}")
        print("\n🔧 Please resolve these issues before starting the web interface.")
        print("📖 See README.md for detailed setup instructions.")
        return 1
    
    print("\n✅ Environment setup looks good!")
    print("🌐 Starting web server...")
    print("📍 Web interface will be available at: http://localhost:5000")
    print("🔄 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Start the Flask app
        os.system('python app.py')
    except KeyboardInterrupt:
        print("\n🛑 Web interface stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Error starting web interface: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())