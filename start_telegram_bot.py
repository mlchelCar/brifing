#!/usr/bin/env python3
"""
MorningBrief - News Briefing Application
Copyright (c) 2025 Michel Car. All rights reserved.

This software is proprietary and confidential. Unauthorized use, reproduction,
or distribution is strictly prohibited.

Startup script for the Telegram bot on Render.
Handles database initialization and starts the bot.
"""

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

def main():
    """Main entry point - use the existing run_telegram_bot.py directly."""
    try:
        logger.info("🚀 Starting MorningBrief Telegram Bot on Render...")

        # Check required environment variables
        required_vars = ['TELEGRAM_BOT_TOKEN', 'OPENAI_API_KEY', 'NEWS_API_KEY', 'DATABASE_URL']
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {missing_vars}")
            sys.exit(1)

        logger.info("✅ All required environment variables are set")

        # Import and run the existing bot main function directly
        logger.info("🔄 Delegating to run_telegram_bot.main()...")
        from run_telegram_bot import main as bot_main

        # Call the bot main function directly - it handles all the async setup
        bot_main()

    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
