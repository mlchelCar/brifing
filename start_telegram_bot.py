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

        # Log environment info
        logger.info(f"🐍 Python version: {sys.version}")
        logger.info(f"🌐 Environment: {os.getenv('ENVIRONMENT', 'unknown')}")
        logger.info(f"🔧 Service type: {os.getenv('RENDER_SERVICE_TYPE', 'unknown')}")

        # Check required environment variables
        required_vars = ['TELEGRAM_BOT_TOKEN', 'OPENAI_API_KEY', 'NEWS_API_KEY', 'DATABASE_URL']
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {missing_vars}")
            return False

        logger.info("✅ All required environment variables are set")

        # Log token info (safely)
        token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        if token:
            logger.info(f"🤖 Bot token configured: {token[:10]}...{token[-4:]}")
        else:
            logger.error("❌ No bot token found")

        # Import required modules
        from app.config import settings
        from app.database import init_database
        from app.services.telegram_bot import telegram_bot_service
        from app.services.scheduler import start_background_scheduler

        # Validate settings
        if not settings.validate_settings():
            logger.error("❌ Invalid configuration. Please check your environment variables.")
            return False
        # Sync user briefing schedules
        logger.info("📅 Syncing user briefing schedules...")
        from app.services.scheduler import scheduler_service
        scheduled_count = await scheduler_service.sync_user_briefing_schedules()
        logger.info(f"✅ Synced {scheduled_count} user briefing schedules")

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

        # Start polling with the modern python-telegram-bot API
        application = telegram_bot_service.application

        try:
            logger.info("🔄 Starting bot with compatible API...")

            # Use the async context manager approach for better compatibility
            async with application:
                # Initialize and start the application
                await application.start()

                # Now set up commands after the application is started
                logger.info("🔧 Setting up bot commands...")
                await telegram_bot_service._setup_commands()

                # Start polling with the updater
                logger.info("🚀 Starting polling...")
                await application.updater.start_polling(drop_pending_updates=True)

                # Keep running until interrupted
                try:
                    logger.info("♾️ Bot is now running indefinitely...")
                    # This will run forever until KeyboardInterrupt
                    await asyncio.Event().wait()
                except (asyncio.CancelledError, KeyboardInterrupt):
                    logger.info("🛑 Received interrupt signal")
                finally:
                    # Clean shutdown
                    logger.info("🔄 Stopping polling...")
                    await application.updater.stop()

        except Exception as polling_error:
            logger.error(f"❌ Polling error: {polling_error}")

            # Fallback to manual polling setup
            logger.info("🔄 Trying manual polling setup...")
            try:
                # Initialize the application
                await application.initialize()
                await application.start()

                # Start polling manually
                logger.info("🔄 Starting manual polling...")
                await application.updater.start_polling(drop_pending_updates=True)

                # Keep running until interrupted
                try:
                    logger.info("♾️ Bot is now running indefinitely...")
                    # This will run forever until KeyboardInterrupt
                    await asyncio.Event().wait()
                except (asyncio.CancelledError, KeyboardInterrupt):
                    logger.info("🛑 Received interrupt signal")
                finally:
                    # Clean shutdown
                    logger.info("🔄 Stopping polling...")
                    await application.updater.stop()
                    await application.stop()
                    await application.shutdown()

            except Exception as manual_error:
                logger.error(f"❌ Manual polling also failed: {manual_error}")
                raise

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

        # Check if we're in a deployment environment
        is_render = os.getenv('RENDER_SERVICE_TYPE') == 'worker'
        if is_render:
            logger.info("🌐 Running on Render deployment environment")
        else:
            logger.info("💻 Running in local/development environment")

        # Create a new event loop for this process
        try:
            # Close any existing event loop
            try:
                existing_loop = asyncio.get_running_loop()
                logger.info("⚠️ Found existing event loop, will create new one")
            except RuntimeError:
                logger.info("✅ No existing event loop found")

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            logger.info("✅ Created new event loop successfully")

            # Run the bot
            logger.info("🚀 Starting bot service...")
            result = loop.run_until_complete(run_bot_service())

            if result:
                logger.info("✅ Bot service completed successfully")
            else:
                logger.error("❌ Bot service failed")
                sys.exit(1)

        except Exception as loop_error:
            logger.error(f"❌ Event loop error: {loop_error}")
            import traceback
            traceback.print_exc()

            # Fallback: try with asyncio.run
            logger.info("🔄 Trying fallback method with asyncio.run...")
            try:
                asyncio.run(run_bot_service())
            except Exception as fallback_error:
                logger.error(f"❌ Fallback method also failed: {fallback_error}")
                sys.exit(1)

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
