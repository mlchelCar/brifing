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
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.database import init_database
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main startup function."""
    try:
        logger.info("🚀 Starting MorningBrief Telegram Bot on Render...")
        
        # Check required environment variables
        required_vars = ['TELEGRAM_BOT_TOKEN', 'OPENAI_API_KEY', 'NEWS_API_KEY', 'DATABASE_URL']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {missing_vars}")
            sys.exit(1)
        
        logger.info("✅ All required environment variables are set")
        
        # Initialize database
        logger.info("📊 Initializing database...")
        await init_database()
        logger.info("✅ Database initialized successfully")
        
        # Import and run the bot directly in the current event loop
        logger.info("🤖 Starting Telegram bot...")

        # Import the setup and run functions separately to avoid main() wrapper
        from run_telegram_bot import setup_bot
        from app.services.telegram_bot import telegram_bot_service

        # Setup bot
        logger.info("🔧 Setting up bot...")
        setup_success = await setup_bot()
        if not setup_success:
            logger.error("❌ Bot setup failed")
            return

        # Start bot polling directly
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
                import asyncio
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                pass
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
