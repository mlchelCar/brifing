#!/usr/bin/env python3
"""
MorningBrief - News Briefing Application
Copyright (c) 2025 Michel Car. All rights reserved.

This software is proprietary and confidential. Unauthorized use, reproduction,
or distribution is strictly prohibited.

Startup script for the Telegram bot on Render.
Handles database initialization and starts the bot.
"""

import asyncio
import logging
import os
import sys
import signal
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

async def run_bot_service():
    """Run the bot service with proper async handling."""
    try:
        logger.info("🚀 Starting MorningBrief Telegram Bot on Render...")

        # Check required environment variables
        required_vars = ['TELEGRAM_BOT_TOKEN', 'OPENAI_API_KEY', 'NEWS_API_KEY', 'DATABASE_URL']
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {missing_vars}")
            return False

        logger.info("✅ All required environment variables are set")

        # Import required modules
        from app.config import settings
        from app.database import init_database
        from app.services.telegram_bot import telegram_bot_service
        from app.services.scheduler import start_background_scheduler

        # Validate settings
        if not settings.validate_settings():
            logger.error("❌ Invalid configuration. Please check your environment variables.")
            return False

        # Initialize database
        logger.info("📊 Initializing database...")
        await init_database()
        logger.info("✅ Database initialized successfully")

        # Initialize bot
        logger.info("🤖 Initializing Telegram bot...")
        if not await telegram_bot_service.initialize():
            logger.error("❌ Failed to initialize Telegram bot")
            return False

        # Start background scheduler for news updates
        logger.info("⏰ Starting background scheduler...")
        await start_background_scheduler()

        logger.info("✅ MorningBrief Telegram Bot is ready!")
        logger.info(f"   Bot Token: {settings.TELEGRAM_BOT_TOKEN[:10]}...")
        logger.info("   Press Ctrl+C to stop the bot")
        logger.info("-" * 50)

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
            except (asyncio.CancelledError, KeyboardInterrupt):
                logger.info("🛑 Received interrupt signal")

        return True

    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        import traceback
        traceback.print_exc()
        return False

def handle_signal(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"🛑 Received signal {signum}, shutting down...")
    sys.exit(0)

def main():
    """Main entry point with proper signal handling."""
    # Set up signal handlers
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    try:
        logger.info("📍 Starting bot with new event loop")
        # Create a new event loop for this process
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Run the bot
        loop.run_until_complete(run_bot_service())

    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        logger.info("🔄 Cleaning up...")

if __name__ == "__main__":
    main()
