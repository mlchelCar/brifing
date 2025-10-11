#!/usr/bin/env python3
"""
Test script to verify bot startup works locally.
This helps debug issues before deployment.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_bot_initialization():
    """Test bot initialization without actually starting polling."""
    try:
        logger.info("🧪 Testing bot initialization...")
        
        # Set dummy environment variables for testing
        os.environ['TELEGRAM_BOT_TOKEN'] = 'dummy_token_for_testing'
        os.environ['OPENAI_API_KEY'] = 'dummy_key_for_testing'
        os.environ['NEWS_API_KEY'] = 'dummy_key_for_testing'
        os.environ['DATABASE_URL'] = 'sqlite:///test_bot.db'
        
        # Import required modules
        from app.config import settings
        from app.database import init_database
        
        logger.info("✅ Imports successful")
        
        # Test database initialization
        logger.info("📊 Testing database initialization...")
        await init_database()
        logger.info("✅ Database initialization successful")
        
        # Test bot service import (but don't initialize with dummy token)
        from app.services.telegram_bot import TelegramBotService
        logger.info("✅ Bot service import successful")
        
        # Test scheduler import
        from app.services.scheduler import SchedulerService
        logger.info("✅ Scheduler service import successful")
        
        logger.info("🎉 All tests passed! Bot should start successfully on deployment.")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the test."""
    try:
        logger.info("🚀 Starting bot initialization test...")
        
        # Create a new event loop for testing
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the test
        success = loop.run_until_complete(test_bot_initialization())
        
        if success:
            logger.info("✅ Test completed successfully!")
            sys.exit(0)
        else:
            logger.error("❌ Test failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Test error: {e}")
        sys.exit(1)
    finally:
        logger.info("🔄 Test cleanup complete")

if __name__ == "__main__":
    main()
