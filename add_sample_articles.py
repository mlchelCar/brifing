#!/usr/bin/env python3
"""Script to add sample news articles directly to the database for testing."""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import AsyncSessionLocal, init_database
from app.models import NewsArticle
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sample articles for testing
SAMPLE_ARTICLES = [
    {
        "category": "technology",
        "title": "Apple Unveils Revolutionary AI Chip for Next-Gen Devices",
        "url": "https://example.com/apple-ai-chip",
        "description": "Apple announces breakthrough AI processing chip that promises 10x performance improvement for machine learning tasks.",
        "summary": "Apple has unveiled its latest AI chip, designed to revolutionize machine learning performance in consumer devices. The new chip offers unprecedented processing power while maintaining energy efficiency."
    },
    {
        "category": "technology", 
        "title": "Google's Quantum Computer Achieves New Milestone",
        "url": "https://example.com/google-quantum",
        "description": "Google's quantum computer successfully solves complex problems in record time, marking a significant advancement in quantum computing.",
        "summary": "Google's quantum computing team has achieved a new milestone, demonstrating the ability to solve previously intractable problems in minutes rather than years."
    },
    {
        "category": "business",
        "title": "Tesla Reports Record Quarterly Profits",
        "url": "https://example.com/tesla-profits",
        "description": "Tesla announces its highest quarterly profits ever, driven by strong electric vehicle sales and energy storage business growth.",
        "summary": "Tesla has reported record-breaking quarterly profits, with electric vehicle deliveries exceeding expectations and the energy storage division showing remarkable growth."
    },
    {
        "category": "business",
        "title": "Amazon Expands Drone Delivery Service Nationwide",
        "url": "https://example.com/amazon-drones",
        "description": "Amazon announces nationwide expansion of its drone delivery service, promising 30-minute deliveries for millions of customers.",
        "summary": "Amazon is expanding its drone delivery service across the United States, aiming to provide ultra-fast delivery for a wide range of products to millions of customers."
    },
    {
        "category": "world",
        "title": "International Climate Summit Reaches Historic Agreement",
        "url": "https://example.com/climate-summit",
        "description": "World leaders agree on ambitious new climate targets and funding mechanisms to combat global warming.",
        "summary": "The latest international climate summit has concluded with a historic agreement on carbon reduction targets and a substantial funding commitment for developing nations."
    },
    {
        "category": "world",
        "title": "European Union Announces New Digital Rights Framework",
        "url": "https://example.com/eu-digital-rights",
        "description": "The EU introduces comprehensive digital rights legislation to protect citizens' privacy and data in the digital age.",
        "summary": "The European Union has unveiled a groundbreaking digital rights framework that establishes new standards for data protection and digital privacy across member states."
    },
    {
        "category": "finance",
        "title": "Bitcoin Reaches New All-Time High Amid Institutional Adoption",
        "url": "https://example.com/bitcoin-high",
        "description": "Bitcoin surges to unprecedented levels as major financial institutions announce cryptocurrency investment strategies.",
        "summary": "Bitcoin has reached a new all-time high, driven by increasing institutional adoption and growing acceptance of cryptocurrency as a legitimate asset class."
    },
    {
        "category": "finance",
        "title": "Federal Reserve Announces Interest Rate Decision",
        "url": "https://example.com/fed-rates",
        "description": "The Federal Reserve maintains current interest rates while signaling potential changes in monetary policy for the coming year.",
        "summary": "The Federal Reserve has decided to maintain current interest rates, citing economic stability while indicating flexibility for future policy adjustments."
    },
    {
        "category": "entertainment",
        "title": "Streaming Wars Heat Up with New Platform Launches",
        "url": "https://example.com/streaming-wars",
        "description": "Multiple new streaming platforms enter the market, intensifying competition for viewer attention and content creators.",
        "summary": "The streaming entertainment landscape is becoming increasingly competitive as new platforms launch with exclusive content and innovative features."
    },
    {
        "category": "entertainment",
        "title": "Hollywood Studios Embrace AI in Film Production",
        "url": "https://example.com/hollywood-ai",
        "description": "Major film studios begin integrating artificial intelligence tools into movie production workflows for enhanced efficiency.",
        "summary": "Hollywood is embracing AI technology to streamline film production, from script analysis to visual effects, promising faster and more cost-effective moviemaking."
    }
]

async def add_sample_articles():
    """Add sample articles to the database."""
    try:
        logger.info("🗞️  Adding sample news articles to database...")
        
        # Initialize database
        await init_database()
        
        async with AsyncSessionLocal() as session:
            articles_added = 0
            
            for article_data in SAMPLE_ARTICLES:
                # Create new article
                article = NewsArticle(
                    category=article_data["category"],
                    title=article_data["title"],
                    url=article_data["url"],
                    description=article_data["description"],
                    summary=article_data["summary"],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    is_active=True
                )
                
                session.add(article)
                articles_added += 1
                logger.info(f"Added article: {article_data['title'][:50]}...")
            
            await session.commit()
            
            logger.info(f"✅ Successfully added {articles_added} sample articles!")
            logger.info("🤖 Your Telegram bot now has articles for testing!")
            logger.info("📱 Try the /briefing command in your bot!")
            
    except Exception as e:
        logger.error(f"❌ Error adding sample articles: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(add_sample_articles())
