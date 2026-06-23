#!/usr/bin/env python3
"""
Test script to verify all dependencies and configuration are set up correctly
"""

import sys
import os
from pathlib import Path

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def test_python_version():
    """Check Python version"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} - Please upgrade to 3.8+")
        return False

def test_dependencies():
    """Check if all required packages are installed"""
    print("🔍 Checking dependencies...")
    required = {
        'vaderSentiment': 'vaderSentiment',
        'youtube_comment_downloader': 'youtube-comment-downloader',
        'praw': 'praw',
        'dotenv': 'python-dotenv',
        'requests': 'requests',
        'jinja2': 'Jinja2'
    }

    all_ok = True
    for module, package_name in required.items():
        try:
            __import__(module)
            print(f"✅ {package_name} - installed")
        except ImportError:
            print(f"❌ {package_name} - NOT installed")
            print(f"   Run: pip install {package_name}")
            all_ok = False

    return all_ok

def test_config_files():
    """Check if required config files exist"""
    print("🔍 Checking configuration files...")
    required_files = {
        'config.json': 'Configuration',
        '.env.example': 'Environment template'
    }

    all_ok = True
    for filename, description in required_files.items():
        if Path(filename).exists():
            print(f"✅ {filename} ({description}) - found")
        else:
            print(f"❌ {filename} ({description}) - NOT found")
            all_ok = False

    return all_ok

def test_env_file():
    """Check if .env file exists and has values"""
    print("🔍 Checking .env file...")
    if not Path('.env').exists():
        print("⚠️  .env file not found - Reddit features won't work")
        print("   Create .env from .env.example and add your Reddit credentials")
        return False

    env_ok = True
    with open('.env', 'r') as f:
        content = f.read()
        if 'your_client_id_here' in content or 'REDDIT_CLIENT_ID=' not in content:
            print("⚠️  REDDIT_CLIENT_ID not configured")
            env_ok = False
        else:
            print("✅ REDDIT_CLIENT_ID - configured")

        if 'your_client_secret_here' in content or 'REDDIT_CLIENT_SECRET=' not in content:
            print("⚠️  REDDIT_CLIENT_SECRET not configured")
            env_ok = False
        else:
            print("✅ REDDIT_CLIENT_SECRET - configured")

    return env_ok

def test_python_files():
    """Check if all Python modules exist"""
    print("🔍 Checking Python modules...")
    required_modules = [
        'main.py',
        'config_loader.py',
        'sentiment_analyzer.py',
        'storage.py',
        'youtube_collector.py',
        'reddit_collector.py',
        'report_generator.py'
    ]

    all_ok = True
    for module in required_modules:
        if Path(module).exists():
            print(f"✅ {module} - found")
        else:
            print(f"❌ {module} - NOT found")
            all_ok = False

    return all_ok

def test_import_modules():
    """Try importing all modules to check for syntax errors"""
    print("🔍 Testing module imports...")
    modules = [
        'config_loader',
        'sentiment_analyzer',
        'storage'
    ]

    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module} - imports successfully")
        except Exception as e:
            print(f"❌ {module} - import failed: {str(e)}")
            all_ok = False

    return all_ok

def run_all_tests():
    """Run all tests"""
    print_header("SETUP VERIFICATION TEST")

    results = {
        'Python Version': test_python_version(),
        'Dependencies': test_dependencies(),
        'Config Files': test_config_files(),
        'Python Modules': test_python_files(),
        'Module Imports': test_import_modules(),
        'Environment (.env)': test_env_file(),
    }

    print_header("TEST RESULTS")
    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "⚠️  NEEDS ATTENTION"
        print(f"{status}: {test_name}")

    print(f"\n{'='*60}")
    print(f"Passed: {passed}/{total}")
    print(f"{'='*60}\n")

    if passed == total:
        print("🎉 All checks passed! You're ready to run: python main.py")
        return True
    else:
        print("⚠️  Please fix the issues above and run this test again")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
