"""Article summarization service using ChatGPT-4o-mini."""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models import NewsArticle
from app.utils.openai_client import openai_client
from app.database import get_async_session
import logging

logger = logging.getLogger(__name__)

class SummarizerService:
    """Service for summarizing news articles using AI."""
    
    def __init__(self):
        self.max_concurrent_summaries = 5  # Limit concurrent API calls
    
    async def summarize_article(self, article_data: Dict[str, Any]) -> str:
        """Generate a summary for a single article."""
        
        title = article_data.get('title', '')
        description = article_data.get('description', '')
        url = article_data.get('url', '')
        category = article_data.get('category', '')
        
        try:
            summary = await openai_client.summarize_article(
                title=title,
                description=description,
                url=url,
                category=category
            )
            
            logger.info(f"Generated summary for article: {title[:50]}...")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to summarize article '{title}': {e}")
            # Fallback to description
            return description if description else f"News article about {category}: {title}"
    
    async def summarize_articles_batch(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Summarize multiple articles concurrently with rate limiting."""
        
        if not articles:
            return []
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.max_concurrent_summaries)
        
        async def summarize_with_semaphore(article):
            async with semaphore:
                summary = await self.summarize_article(article)
                return {**article, 'summary': summary}
        
        # Process articles concurrently
        tasks = [summarize_with_semaphore(article) for article in articles]
        summarized_articles = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return successful results
        results = []
        for i, result in enumerate(summarized_articles):
            if isinstance(result, Exception):
                logger.error(f"Error summarizing article {i}: {result}")
                # Add article without summary as fallback
                article = articles[i]
                article['summary'] = article.get('description', article.get('title', ''))
                results.append(article)
            else:
                results.append(result)
        
        return results
    
    async def save_articles_to_database(self, articles: List[Dict[str, Any]], 
                                      session: AsyncSession) -> List[NewsArticle]:
        """Save summarized articles to the database."""
        
        saved_articles = []
        
        for article_data in articles:
            try:
                # Check if article already exists
                stmt = select(NewsArticle).where(NewsArticle.url == article_data['url'])
                result = await session.execute(stmt)
                existing_article = result.scalar_one_or_none()
                
                if existing_article:
                    # Update existing article
                    existing_article.summary = article_data.get('summary', '')
                    existing_article.updated_at = datetime.utcnow()
                    existing_article.is_active = True
                    saved_articles.append(existing_article)
                    logger.info(f"Updated existing article: {existing_article.title[:50]}...")
                else:
                    # Create new article
                    new_article = NewsArticle(
                        category=article_data['category'],
                        title=article_data['title'],
                        url=article_data['url'],
                        description=article_data.get('description', ''),
                        summary=article_data.get('summary', ''),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                        is_active=True
                    )
                    session.add(new_article)
                    saved_articles.append(new_article)
                    logger.info(f"Created new article: {new_article.title[:50]}...")
                
            except Exception as e:
                logger.error(f"Error saving article to database: {e}")
                continue
        
        try:
            await session.commit()
            logger.info(f"Successfully saved {len(saved_articles)} articles to database")
        except Exception as e:
            logger.error(f"Error committing articles to database: {e}")
            await session.rollback()
            raise e
        
        return saved_articles
    
    async def process_and_save_articles(self, category_articles: Dict[str, List[Dict[str, Any]]]) -> List[NewsArticle]:
        """Process articles by summarizing and saving to database."""
        
        # Flatten all articles from all categories
        all_articles = []
        for category, articles in category_articles.items():
            for article in articles:
                article['category'] = category  # Ensure category is set
                all_articles.append(article)
        
        if not all_articles:
            logger.warning("No articles to process")
            return []
        
        # Summarize all articles
        logger.info(f"Starting summarization of {len(all_articles)} articles")
        summarized_articles = await self.summarize_articles_batch(all_articles)
        
        # Save to database
        async for session in get_async_session():
            try:
                saved_articles = await self.save_articles_to_database(summarized_articles, session)
                return saved_articles
            except Exception as e:
                logger.error(f"Error in process_and_save_articles: {e}")
                raise e
    
    async def get_recent_articles(self, categories: List[str], 
                                session: AsyncSession, 
                                hours: int = 24) -> List[NewsArticle]:
        """Get recent articles from database for specified categories."""
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        stmt = select(NewsArticle).where(
            NewsArticle.category.in_(categories),
            NewsArticle.created_at >= cutoff_time,
            NewsArticle.is_active == True
        ).order_by(NewsArticle.created_at.desc())
        
        result = await session.execute(stmt)
        articles = result.scalars().all()
        
        logger.info(f"Retrieved {len(articles)} recent articles from database")
        return articles

# Global summarizer service instance
summarizer_service = SummarizerService()
