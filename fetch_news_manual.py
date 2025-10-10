#!/usr/bin/env python3
"""Manual script to fetch news articles and populate the database."""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import init_database
from app.services.scheduler import scheduler_service
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to fetch news articles."""
    try:
        logger.info("🗞️  Starting manual news fetch...")
        
        # Initialize database
        logger.info("📊 Initializing database...")
        await init_database()
        
        # Trigger manual news refresh
        logger.info("🔄 Fetching latest news articles...")
        await scheduler_service.trigger_manual_refresh()
        
        logger.info("✅ News fetch completed successfully!")
        logger.info("🤖 Your Telegram bot now has fresh articles for briefings!")
        
    except Exception as e:
        logger.error(f"❌ Error during news fetch: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
