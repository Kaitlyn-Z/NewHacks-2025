#!/usr/bin/env python3
"""
Test script to verify Meme Stock Dashboard setup
Run this to check if all dependencies and configurations are correct
"""

import sys
import importlib

def test_module(module_name, package_name=None):
    """Test if a Python module can be imported"""
    display_name = package_name or module_name
    try:
        importlib.import_module(module_name)
        print(f"✅ {display_name}")
        return True
    except ImportError:
        print(f"❌ {display_name} - Run: pip3 install {package_name or module_name}")
        return False

def test_api_keys():
    """Test if API keys are configured"""
    try:
        import api_keys
        
        has_gemini = hasattr(api_keys, 'GEMINI_API_KEY') and \
                     api_keys.GEMINI_API_KEY != "your_gemini_api_key_here"
        
        if has_gemini:
            print("✅ Gemini API key configured")
        else:
            print("⚠️  Gemini API key not configured (sentiment analysis will be limited)")
        
        return True
    except ImportError:
        print("❌ api_keys.py not found - Copy api_keys.py.example to api_keys.py")
        return False

def test_backend_imports():
    """Test if backend modules can be imported"""
    print("\n📦 Testing Backend Imports...")
    
    try:
        sys.path.insert(0, 'backend')
        
        print("Testing integrated_backend.py...")
        import integrated_backend
        print("✅ Integrated backend imports successfully")
        
        print("Testing gemini.py...")
        import gemini
        print("✅ Gemini backend imports successfully")
        
        return True
    except Exception as e:
        print(f"❌ Backend import error: {e}")
        return False
    finally:
        sys.path.pop(0)

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Meme Stock Dashboard - Setup Test")
    print("=" * 60)
    
    print("\n📦 Testing Core Dependencies...")
    all_passed = True
    
    # Test core dependencies
    deps = [
        ('flask', 'flask'),
        ('flask_cors', 'flask-cors'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('yfinance', 'yfinance'),
        ('google.generativeai', 'google-generativeai'),
        ('dotenv', 'python-dotenv'),
    ]
    
    for module, package in deps:
        if not test_module(module, package):
            all_passed = False
    
    print("\n🔑 Testing API Keys...")
    if not test_api_keys():
        all_passed = False
    
    # Test backend imports
    if not test_backend_imports():
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed! You're ready to start the dashboard.")
        print("\nRun: ./start-all-services.sh")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  1. Install dependencies: pip3 install -r requirements.txt")
        print("  2. Setup API keys: cp api_keys.py.example api_keys.py")
        print("  3. Edit api_keys.py with your actual keys")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())


