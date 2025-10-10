#!/usr/bin/env python3
"""
Debug script to check environment variables and database connectivity.
"""

import os
import sys

def main():
    print("🔍 Environment Variables Debug")
    print("=" * 50)
    
    # Check required environment variables
    required_vars = [
        'DATABASE_URL',
        'TELEGRAM_BOT_TOKEN', 
        'OPENAI_API_KEY',
        'NEWS_API_KEY',
        'PORT'
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'TOKEN' in var or 'KEY' in var:
                masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET")
    
    print("\n🐍 Python Information")
    print("=" * 50)
    print(f"Python Version: {sys.version}")
    print(f"Python Path: {sys.executable}")
    
    print("\n📁 Current Directory")
    print("=" * 50)
    print(f"Working Directory: {os.getcwd()}")
    print(f"Script Location: {__file__}")
    
    # Test database URL parsing
    print("\n🗄️ Database URL Test")
    print("=" * 50)
    db_url = os.getenv('DATABASE_URL', '')
    if db_url:
        try:
            from sqlalchemy import create_engine
            from sqlalchemy.engine.url import make_url
            
            parsed_url = make_url(db_url)
            print(f"✅ Database URL is valid")
            print(f"   Driver: {parsed_url.drivername}")
            print(f"   Host: {parsed_url.host}")
            print(f"   Database: {parsed_url.database}")
        except Exception as e:
            print(f"❌ Database URL parsing failed: {e}")
    else:
        print("⚠️ DATABASE_URL is empty or not set")

if __name__ == "__main__":
    main()
