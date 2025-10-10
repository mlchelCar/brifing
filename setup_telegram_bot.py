"""Setup script for MorningBrief Telegram bot."""

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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def setup_bot():
    """Setup the Telegram bot."""
    logger.info("🤖 Setting up MorningBrief Telegram Bot...")
    
    # Check environment variables
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN not found in environment variables")
        logger.info("Please add your Telegram bot token to .env file:")
        logger.info("TELEGRAM_BOT_TOKEN=your_bot_token_here")
        return False
    
    if not settings.OPENAI_API_KEY:
        logger.error("❌ OPENAI_API_KEY not found in environment variables")
        logger.info("Please add your OpenAI API key to .env file:")
        logger.info("OPENAI_API_KEY=your_openai_key_here")
        return False
    
    if not settings.NEWS_API_KEY:
        logger.error("❌ NEWS_API_KEY not found in environment variables")
        logger.info("Please add your News API key to .env file:")
        logger.info("NEWS_API_KEY=your_news_api_key_here")
        return False
    
    try:
        # Initialize database
        logger.info("📊 Initializing database...")
        await init_database()
        logger.info("✅ Database initialized successfully")
        
        # Initialize bot
        logger.info("🤖 Initializing Telegram bot...")
        if not await telegram_bot_service.initialize():
            logger.error("❌ Failed to initialize Telegram bot")
            return False
        
        # Get bot info
        if telegram_bot_service.application:
            bot = telegram_bot_service.application.bot
            me = await bot.get_me()
            logger.info(f"✅ Bot initialized successfully!")
            logger.info(f"   Bot Name: {me.first_name}")
            logger.info(f"   Bot Username: @{me.username}")
            logger.info(f"   Bot ID: {me.id}")
            
            # Test bot commands
            logger.info("🔧 Setting up bot commands...")
            await telegram_bot_service._setup_commands()
            logger.info("✅ Bot commands configured")
            
            return True
        else:
            logger.error("❌ Bot application not created")
            return False
            
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        return False

async def test_bot():
    """Test bot functionality."""
    logger.info("🧪 Testing bot functionality...")
    
    try:
        if telegram_bot_service.application:
            bot = telegram_bot_service.application.bot
            
            # Test getting bot info
            me = await bot.get_me()
            logger.info(f"✅ Bot info retrieved: @{me.username}")
            
            # Test getting webhook info
            webhook_info = await bot.get_webhook_info()
            logger.info(f"📡 Webhook URL: {webhook_info.url or 'Not set'}")
            
            return True
        else:
            logger.error("❌ Bot not initialized")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

def print_instructions():
    """Print setup instructions."""
    print("\n" + "="*60)
    print("🤖 MorningBrief Telegram Bot Setup Complete!")
    print("="*60)
    print("\n📋 Next Steps:")
    print("\n1. 🚀 Start the bot:")
    print("   python run_telegram_bot.py")
    print("\n2. 📱 Test your bot:")
    print("   - Open Telegram")
    print("   - Search for your bot username")
    print("   - Send /start command")
    print("\n3. 🌐 Optional - Set up webhook (for production):")
    print("   - Deploy your app to a server")
    print("   - Set TELEGRAM_WEBHOOK_URL in .env")
    print("   - Use /telegram/webhook/set endpoint")
    print("\n4. ⏰ The bot will automatically:")
    print("   - Help users select news categories")
    print("   - Send daily briefings at chosen times")
    print("   - Provide on-demand briefings with /briefing")
    print("\n🔧 Available Commands:")
    print("   /start - Start using MorningBrief")
    print("   /categories - Select news categories")
    print("   /briefing - Get daily briefing now")
    print("   /settings - Manage preferences")
    print("   /help - Show help")
    print("   /stop - Stop receiving briefings")
    print("\n📚 Documentation:")
    print("   - Check README.md for detailed setup")
    print("   - API docs: http://localhost:8000/docs")
    print("   - Telegram API: /telegram/bot/info")
    print("\n" + "="*60)

async def main():
    """Main setup function."""
    print("🌅 MorningBrief Telegram Bot Setup")
    print("="*40)
    
    # Setup bot
    if await setup_bot():
        logger.info("✅ Setup completed successfully")
        
        # Test bot
        if await test_bot():
            logger.info("✅ All tests passed")
            print_instructions()
        else:
            logger.warning("⚠️ Some tests failed, but bot should still work")
            print_instructions()
    else:
        logger.error("❌ Setup failed")
        print("\n💡 Troubleshooting:")
        print("1. Check your .env file has all required variables")
        print("2. Verify your Telegram bot token is correct")
        print("3. Ensure you have internet connection")
        print("4. Check the logs above for specific errors")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Setup interrupted by user")
