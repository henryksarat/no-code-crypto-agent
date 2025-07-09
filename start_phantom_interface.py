#!/usr/bin/env python3
"""
Solana No-code Agent - Phantom Integration Startup Script

This script starts the web interface with Phantom wallet integration.
No private keys needed - all operations are performed through Phantom wallet.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_phantom_environment():
    """Check if the environment is properly set up for Phantom integration"""
    issues = []
    
    # Check if .env file exists (only OpenAI key needed for Phantom version)
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("📝 For Phantom integration, you need an AI API key:")
        print("   Option 1 (FREE): DEEPSEEK_API_KEY=your_key")
        print("   Option 2 (Paid): OPENAI_API_KEY=your_key")
        print("   (No wallet private keys needed!)")
        print()
        issues.append("❌ .env file not found")
    else:
        print("✅ .env file found")
        
        # Check AI API keys
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            model_provider = os.getenv('AI_MODEL_PROVIDER', 'openai').lower()
            deepseek_key = os.getenv('DEEPSEEK_API_KEY')
            openai_key = os.getenv('OPENAI_API_KEY')
            
            if model_provider == 'deepseek':
                if deepseek_key:
                    print("✅ DeepSeek API key configured (FREE)")
                elif openai_key:
                    print("✅ OpenAI API key found, will use as fallback")
                else:
                    issues.append("❌ No AI API key found")
                    print("❌ No DEEPSEEK_API_KEY or OPENAI_API_KEY found")
            else:
                if openai_key:
                    print("✅ OpenAI API key configured")
                elif deepseek_key:
                    print("✅ DeepSeek API key found, consider setting AI_MODEL_PROVIDER=deepseek for free usage")
                else:
                    issues.append("❌ No AI API key found")
                    print("❌ No OPENAI_API_KEY or DEEPSEEK_API_KEY found")
                    
        except ImportError:
            print("⚠️  python-dotenv not installed, cannot verify .env contents")
    
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
        print("📝 Please install dependencies:")
        print("   pip install -r requirements.txt")
        print()
    
    try:
        import requests
        print("✅ Requests library available")
    except ImportError:
        issues.append("❌ Requests library not installed")
        print("📝 Please install requests:")
        print("   pip install requests")
        print()
    
    return len(issues) == 0, issues

def print_phantom_info():
    """Print information about Phantom wallet integration"""
    print("\n" + "=" * 60)
    print("👻 PHANTOM WALLET INTEGRATION")
    print("=" * 60)
    print("🔒 Secure: Your private keys never leave your browser")
    print("🌐 Easy: Connect with one click through Phantom extension")
    print("✅ Safe: All transactions signed through your wallet")
    print("📱 Compatible: Works with Phantom browser extension")
    print()
    print("📋 REQUIRED:")
    print("   • Phantom wallet browser extension installed")
    print("   • AI API key (DeepSeek FREE or OpenAI)")
    print()
    print("💰 AI MODEL OPTIONS:")
    print("   • DeepSeek: FREE, get key at platform.deepseek.com")
    print("   • OpenAI: Paid, get key at platform.openai.com")
    print()
    print("🚫 NOT REQUIRED:")
    print("   • Private keys in .env file")
    print("   • Funding wallet setup")
    print("   • Manual key management")
    print("=" * 60)

def main():
    """Main function to start the Phantom wallet interface"""
    print("👻 Starting Solana No-code Agent - Phantom Integration")
    print_phantom_info()
    
    # Check environment
    env_ok, issues = check_phantom_environment()
    
    if not env_ok:
        print("\n❌ Environment setup issues detected:")
        for issue in issues:
            print(f"   {issue}")
        print("\n🔧 Please resolve these issues before starting.")
        print("📖 Note: Phantom version only requires OpenAI API key!")
        return 1
    
    print("\n✅ Environment setup looks good!")
    print("🌐 Starting Phantom wallet interface...")
    print("📍 Web interface will be available at: http://localhost:5001")
    print("👻 Make sure Phantom wallet extension is installed!")
    print("🔄 Press Ctrl+C to stop the server")
    print("-" * 60)
    
    try:
        # Start the Flask app for Phantom integration
        os.system('python app_phantom.py')
    except KeyboardInterrupt:
        print("\n🛑 Phantom wallet interface stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Error starting Phantom interface: {e}")
        return 1

def print_usage_guide():
    """Print usage guide for Phantom integration"""
    print("\n📖 PHANTOM WALLET USAGE GUIDE")
    print("=" * 40)
    print("1. 🌐 Open http://localhost:5001 in your browser")
    print("2. 👻 Click 'Connect Phantom' button")
    print("3. ✅ Approve connection in Phantom popup")
    print("4. 💬 Type natural language commands")
    print("5. 🔒 Sign transactions in Phantom when needed")
    print()
    print("Example commands:")
    print("• 'Check my wallet balance'")
    print("• 'Show my wallet information'")
    print("• 'Send 0.1 SOL to [address]'")
    print("• 'View my transaction history'")
    print("=" * 40)

if __name__ == "__main__":
    try:
        result = main()
        if result == 0:  # Success or clean exit
            print_usage_guide()
        sys.exit(result)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)