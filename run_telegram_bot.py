"""Script to run the Telegram bot."""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.config import settings
from app.database import init_database
from app.services.telegram_bot import telegram_bot_service
from app.services.scheduler import start_background_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to run the Telegram bot."""
    logger.info("🤖 Starting MorningBrief Telegram Bot...")
    
    # Validate settings
    if not settings.validate_settings():
        logger.error("❌ Invalid configuration. Please check your environment variables.")
        logger.error("Required: OPENAI_API_KEY, NEWS_API_KEY, TELEGRAM_BOT_TOKEN")
        return
    
    try:
        # Initialize database
        logger.info("📊 Initializing database...")
        await init_database()
        
        # Initialize bot
        logger.info("🤖 Initializing Telegram bot...")
        if not await telegram_bot_service.initialize():
            logger.error("❌ Failed to initialize Telegram bot")
            return
        
        # Start background scheduler for news updates
        logger.info("⏰ Starting background scheduler...")
        await start_background_scheduler()
        
        logger.info("✅ MorningBrief Telegram Bot is ready!")
        logger.info(f"   Bot Token: {settings.TELEGRAM_BOT_TOKEN[:10]}...")
        logger.info("   Press Ctrl+C to stop the bot")
        logger.info("-" * 50)
        
        # Start bot polling
        await telegram_bot_service.start_polling()
        
    except KeyboardInterrupt:
        logger.info("🛑 Received interrupt signal")
    except Exception as e:
        logger.error(f"❌ Error running bot: {e}")
    finally:
        logger.info("🔄 Shutting down...")
        await telegram_bot_service.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 MorningBrief Telegram Bot stopped")
