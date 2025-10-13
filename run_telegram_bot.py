"""
MorningBrief - News Briefing Application
Copyright (c) 2025 Michel Car

Licensed under the MIT License. See LICENSE file for details.

Script to run the Telegram bot.
"""

import asyncio
import logging
import sys
import os
import signal
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

async def setup_bot():
    """Setup the bot and dependencies."""
    logger.info("🤖 Starting MorningBrief Telegram Bot...")

    # Validate settings
    if not settings.validate_settings():
        logger.error("❌ Invalid configuration. Please check your environment variables.")
        logger.error("Required: OPENAI_API_KEY, NEWS_API_KEY, TELEGRAM_BOT_TOKEN")
        return False

    try:
        # Initialize database
        logger.info("📊 Initializing database...")
        await init_database()

        # Initialize bot
        logger.info("🤖 Initializing Telegram bot...")
        if not await telegram_bot_service.initialize():
            logger.error("❌ Failed to initialize Telegram bot")
            return False

        # Start background scheduler for news updates
        logger.info("⏰ Starting background scheduler...")
        await start_background_scheduler()
        # Sync user briefing schedules
        logger.info("📅 Syncing user briefing schedules...")
        from app.services.scheduler import scheduler_service
        scheduled_count = await scheduler_service.sync_user_briefing_schedules()
        logger.info(f"✅ Synced {scheduled_count} user briefing schedules")

        logger.info("✅ MorningBrief Telegram Bot is ready!")
        logger.info(f"   Bot Token: {settings.TELEGRAM_BOT_TOKEN[:10]}...")
        logger.info("   Press Ctrl+C to stop the bot")
        logger.info("-" * 50)

        return True

    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        return False

async def run_bot():
    """Run the bot with proper async handling."""
    try:
        # Setup bot
        setup_success = await setup_bot()
        if not setup_success:
            return

        # Start bot polling
        logger.info("🚀 Starting bot polling...")
        logger.info("✅ Bot is now running and listening for messages...")
        logger.info("📱 Send /start to your bot to test it!")

        # Start polling - this will run until interrupted
        async with telegram_bot_service.application:
            await telegram_bot_service.application.start()
            await telegram_bot_service.application.updater.start_polling(drop_pending_updates=True)

            # Keep running until interrupted
            try:
                # This will run forever until KeyboardInterrupt
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                pass

    except KeyboardInterrupt:
        logger.info("🛑 Received interrupt signal")
    except Exception as e:
        logger.error(f"❌ Error running bot: {e}")
    finally:
        logger.info("🔄 Shutting down...")
        logger.info("👋 MorningBrief Telegram Bot stopped")

def main():
    """Main entry point."""
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")

if __name__ == "__main__":
    main()
