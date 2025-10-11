#!/usr/bin/env python3
"""
Test script for personalized briefing features.
Tests the enhanced MorningBrief Telegram bot with personalization.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime, time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.database import init_database, get_async_session_factory
from app.models import TelegramUser, NewsArticle
from app.services.telegram_bot import TelegramBotService
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PersonalizationTester:
    """Test class for personalized briefing features."""
    
    def __init__(self):
        self.bot_service = TelegramBotService()
        self.test_users = []
    
    async def setup_test_environment(self):
        """Set up the test environment with sample users and articles."""
        logger.info("🔧 Setting up test environment...")
        
        # Initialize database
        await init_database()
        
        # Create test users
        await self.create_test_users()
        
        # Create sample articles
        await self.create_sample_articles()
        
        logger.info("✅ Test environment setup complete")
    
    async def create_test_users(self):
        """Create test users with different delivery times."""
        session_factory = get_async_session_factory()
        async with session_factory() as session:
            # Clear existing test users
            await session.execute(
                delete(TelegramUser).where(TelegramUser.telegram_id.in_([111111, 222222, 333333]))
            )
            await session.commit()
            
            # Test User 1: Morning person
            user1 = TelegramUser(
                telegram_id=111111,
                username="alice_test",
                first_name="Alice",
                last_name="Johnson",
                selected_categories=["technology", "business"],
                daily_time="07:00",
                timezone="UTC",
                is_active=True
            )
            
            # Test User 2: Late riser
            user2 = TelegramUser(
                telegram_id=222222,
                username="bob_test",
                first_name="Bob",
                last_name="Smith",
                selected_categories=["sports", "entertainment"],
                daily_time="09:30",
                timezone="UTC",
                is_active=True
            )
            
            # Test User 3: Evening person
            user3 = TelegramUser(
                telegram_id=333333,
                username="charlie_test",
                first_name="Charlie",
                last_name="Brown",
                selected_categories=["health", "science"],
                daily_time="18:00",
                timezone="UTC",
                is_active=True
            )
            
            session.add_all([user1, user2, user3])
            await session.commit()
            
            self.test_users = [user1, user2, user3]
            logger.info(f"✅ Created {len(self.test_users)} test users")
    
    async def create_sample_articles(self):
        """Create sample articles for testing."""
        session_factory = get_async_session_factory()
        async with session_factory() as session:
            # Clear existing test articles
            await session.execute(
                delete(NewsArticle).where(NewsArticle.title.like("TEST:%"))
            )
            await session.commit()
            
            # Sample articles for different categories
            articles = [
                NewsArticle(
                    title="TEST: Revolutionary AI Breakthrough",
                    url="https://example.com/ai-breakthrough",
                    description="Scientists develop new AI technology that could change everything.",
                    summary="A groundbreaking AI system has been developed that shows unprecedented capabilities in reasoning and problem-solving.",
                    category="technology",
                    is_active=True,
                    created_at=datetime.utcnow()
                ),
                NewsArticle(
                    title="TEST: Stock Market Reaches New Heights",
                    url="https://example.com/stock-market",
                    description="Major indices hit record highs amid positive economic indicators.",
                    summary="The stock market continues its upward trajectory with technology and healthcare sectors leading the gains.",
                    category="business",
                    is_active=True,
                    created_at=datetime.utcnow()
                ),
                NewsArticle(
                    title="TEST: Championship Game Tonight",
                    url="https://example.com/championship",
                    description="Two top teams face off in tonight's championship match.",
                    summary="The highly anticipated championship game promises to be an exciting showdown between two evenly matched teams.",
                    category="sports",
                    is_active=True,
                    created_at=datetime.utcnow()
                ),
                NewsArticle(
                    title="TEST: New Health Study Results",
                    url="https://example.com/health-study",
                    description="Researchers publish findings on nutrition and longevity.",
                    summary="A comprehensive study reveals new insights into the relationship between diet and healthy aging.",
                    category="health",
                    is_active=True,
                    created_at=datetime.utcnow()
                )
            ]
            
            session.add_all(articles)
            await session.commit()
            logger.info(f"✅ Created {len(articles)} sample articles")
    
    async def test_personalized_briefings(self):
        """Test personalized briefing generation for each user."""
        logger.info("🧪 Testing personalized briefing generation...")
        
        session_factory = get_async_session_factory()
        async with session_factory() as session:
            for user in self.test_users:
                logger.info(f"\n📝 Testing briefing for {user.first_name} ({user.username})")
                logger.info(f"   Categories: {user.selected_categories}")
                logger.info(f"   Delivery time: {user.daily_time}")
                
                # Test on-demand briefing
                briefing_on_demand = await self.bot_service._generate_briefing(
                    categories=user.selected_categories,
                    user_name=user.first_name,
                    is_scheduled=False
                )
                
                # Test scheduled briefing
                briefing_scheduled = await self.bot_service._generate_briefing(
                    categories=user.selected_categories,
                    user_name=user.first_name,
                    is_scheduled=True
                )
                
                logger.info("📰 ON-DEMAND BRIEFING:")
                logger.info(briefing_on_demand[:200] + "..." if briefing_on_demand else "None")
                
                logger.info("📅 SCHEDULED BRIEFING:")
                logger.info(briefing_scheduled[:200] + "..." if briefing_scheduled else "None")
                
                # Verify personalization
                if briefing_on_demand and user.first_name in briefing_on_demand:
                    logger.info(f"✅ User name '{user.first_name}' found in on-demand briefing")
                else:
                    logger.error(f"❌ User name '{user.first_name}' NOT found in on-demand briefing")
                
                if briefing_scheduled and user.first_name in briefing_scheduled:
                    logger.info(f"✅ User name '{user.first_name}' found in scheduled briefing")
                else:
                    logger.error(f"❌ User name '{user.first_name}' NOT found in scheduled briefing")
                
                # Check for time-based greeting
                current_hour = datetime.utcnow().hour
                expected_greeting = "Good morning" if current_hour < 12 else "Good afternoon" if current_hour < 17 else "Good evening"
                
                if briefing_on_demand and expected_greeting in briefing_on_demand:
                    logger.info(f"✅ Time-based greeting '{expected_greeting}' found")
                else:
                    logger.error(f"❌ Time-based greeting '{expected_greeting}' NOT found")
                
                print("-" * 80)
    
    async def test_scheduled_delivery_simulation(self):
        """Simulate scheduled delivery for all users."""
        logger.info("📅 Testing scheduled delivery simulation...")
        
        # Simulate sending briefings to all users
        await self.bot_service.send_daily_briefings()
        
        logger.info("✅ Scheduled delivery simulation complete")
    
    async def cleanup_test_data(self):
        """Clean up test data."""
        logger.info("🧹 Cleaning up test data...")
        
        session_factory = get_async_session_factory()
        async with session_factory() as session:
            # Remove test users
            await session.execute(
                delete(TelegramUser).where(TelegramUser.telegram_id.in_([111111, 222222, 333333]))
            )
            
            # Remove test articles
            await session.execute(
                delete(NewsArticle).where(NewsArticle.title.like("TEST:%"))
            )
            
            await session.commit()
            logger.info("✅ Test data cleanup complete")

async def main():
    """Main test function."""
    logger.info("🚀 Starting MorningBrief Personalization Tests")
    logger.info("=" * 60)
    
    tester = PersonalizationTester()
    
    try:
        # Setup test environment
        await tester.setup_test_environment()
        
        # Test personalized briefings
        await tester.test_personalized_briefings()
        
        # Test scheduled delivery simulation
        await tester.test_scheduled_delivery_simulation()
        
        logger.info("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        await tester.cleanup_test_data()

if __name__ == "__main__":
    asyncio.run(main())
