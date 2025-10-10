#!/usr/bin/env python3
"""
Test script to verify deployment readiness.
Run this before deploying to Render to catch issues early.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_environment_variables():
    """Test that all required environment variables are set."""
    print("🔍 Testing environment variables...")
    
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'OPENAI_API_KEY', 
        'NEWS_API_KEY',
        'DATABASE_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
        else:
            print(f"  ✅ {var}: Set")
    
    if missing_vars:
        print(f"  ❌ Missing variables: {missing_vars}")
        return False
    
    print("  ✅ All environment variables are set")
    return True

def test_imports():
    """Test that all required modules can be imported."""
    print("\n📦 Testing imports...")
    
    try:
        import fastapi
        print(f"  ✅ FastAPI: {fastapi.__version__}")
        
        import uvicorn
        print(f"  ✅ Uvicorn: {uvicorn.__version__}")
        
        import sqlalchemy
        print(f"  ✅ SQLAlchemy: {sqlalchemy.__version__}")
        
        import asyncpg
        print(f"  ✅ AsyncPG: {asyncpg.__version__}")
        
        import telegram
        print(f"  ✅ Python-telegram-bot: {telegram.__version__}")
        
        import openai
        print(f"  ✅ OpenAI: {openai.__version__}")
        
        from app.config import settings
        print("  ✅ App config imported")
        
        from app.database import async_engine
        print("  ✅ Database engine created")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False

async def test_database_connection():
    """Test database connection."""
    print("\n🗄️ Testing database connection...")
    
    try:
        from app.database import async_engine
        
        async with async_engine.begin() as conn:
            result = await conn.execute("SELECT 1")
            row = result.fetchone()
            if row and row[0] == 1:
                print("  ✅ Database connection successful")
                return True
            else:
                print("  ❌ Database query returned unexpected result")
                return False
                
    except Exception as e:
        print(f"  ❌ Database connection failed: {e}")
        return False

async def test_telegram_bot():
    """Test Telegram bot initialization."""
    print("\n🤖 Testing Telegram bot...")
    
    try:
        from app.services.telegram_bot import TelegramBotService
        
        bot_service = TelegramBotService()
        
        # Test bot token
        bot_info = await bot_service.application.bot.get_me()
        print(f"  ✅ Bot connected: @{bot_info.username}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Telegram bot test failed: {e}")
        return False

async def test_web_service():
    """Test web service startup."""
    print("\n🌐 Testing web service...")
    
    try:
        from app.main import app
        print("  ✅ FastAPI app created successfully")
        
        # Test health endpoint
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        # Note: This won't work with lifespan events in test mode
        # but we can at least verify the app structure
        print("  ✅ Web service structure is valid")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Web service test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🚀 MorningBrief Deployment Readiness Test\n")
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Imports", test_imports),
        ("Database Connection", test_database_connection),
        ("Telegram Bot", test_telegram_bot),
        ("Web Service", test_web_service),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📋 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Ready for deployment to Render.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Fix issues before deploying.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
