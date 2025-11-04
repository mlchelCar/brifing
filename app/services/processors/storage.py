"""
MorningBrief - News Briefing Application
Copyright (c) 2025 Michel Car

Storage processor for database persistence.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.services.processors.base import Processor, ProcessingError
from app.schemas import ProcessedArticle
from app.models import NewsArticle
import logging

logger = logging.getLogger(__name__)


class StorageProcessor(Processor[List[ProcessedArticle], List[NewsArticle]]):
    """Processor for storing articles in the database."""
    
    def __init__(self, session: AsyncSession):
        """
        Initialize storage processor.
        
        Args:
            session: Database session for persistence
        """
        super().__init__("StorageProcessor")
        self.session = session
    
    async def process(self, input_data: List[ProcessedArticle]) -> List[NewsArticle]:
        """
        Process articles and save them to the database.
        
        Args:
            input_data: List of processed articles to save
            
        Returns:
            List of saved NewsArticle database objects
            
        Raises:
            ProcessingError: If storage fails
        """
        if not self.is_enabled():
            logger.warning(f"{self.name} is disabled, skipping database save")
            return []
        
        if not input_data:
            return []
        
        saved_articles = []
        
        try:
            for article_data in input_data:
                try:
                    # Check if article already exists
                    stmt = select(NewsArticle).where(NewsArticle.url == str(article_data.url))
                    result = await self.session.execute(stmt)
                    existing_article = result.scalar_one_or_none()
                    
                    if existing_article:
                        # Update existing article
                        existing_article.summary = article_data.ai_summary or article_data.description
                        existing_article.ai_summary = article_data.ai_summary
                        existing_article.description = article_data.description
                        existing_article.updated_at = datetime.utcnow()
                        existing_article.is_active = True
                        saved_articles.append(existing_article)
                        logger.info(f"Updated existing article: {existing_article.title[:50]}...")
                    else:
                        # Create new article
                        new_article = NewsArticle(
                            category=article_data.category,
                            title=article_data.title,
                            url=str(article_data.url),
                            description=article_data.description or '',
                            summary=article_data.ai_summary or article_data.description or '',
                            ai_summary=article_data.ai_summary,
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow(),
                            is_active=True
                        )
                        self.session.add(new_article)
                        saved_articles.append(new_article)
                        logger.info(f"Created new article: {new_article.title[:50]}...")
                    
                except Exception as e:
                    logger.error(f"Error saving article to database: {e}")
                    continue
            
            # Commit all changes
            await self.session.commit()
            logger.info(f"{self.name} successfully saved {len(saved_articles)} articles to database")
            return saved_articles
            
        except Exception as e:
            logger.error(f"{self.name} failed to save articles: {e}")
            await self.session.rollback()
            raise ProcessingError(
                f"Failed to save articles to database: {str(e)}",
                self.name,
                original_error=e
            )
    
    async def get_recent_articles(self, categories: List[str], hours: int = 24) -> List[NewsArticle]:
        """
        Get recent articles from database for specified categories.
        
        Args:
            categories: List of categories to retrieve
            hours: Number of hours to look back
            
        Returns:
            List of recent NewsArticle objects
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        stmt = select(NewsArticle).where(
            NewsArticle.category.in_(categories),
            NewsArticle.created_at >= cutoff_time,
            NewsArticle.is_active == True
        ).order_by(NewsArticle.created_at.desc())
        
        result = await self.session.execute(stmt)
        articles = result.scalars().all()
        
        logger.info(f"Retrieved {len(articles)} recent articles from database")
        return articles
    
    async def get_fresh_articles_by_category(
        self,
        categories: List[str],
        category_freshness_windows: Optional[Dict[str, int]] = None
    ) -> Dict[str, List[NewsArticle]]:
        """
        Get fresh articles grouped by category with category-specific freshness windows.
        
        Args:
            categories: List of categories to retrieve
            category_freshness_windows: Optional dict mapping category to freshness window in hours
            
        Returns:
            Dictionary mapping category to list of fresh NewsArticle objects
        """
        from app.services.freshness import freshness_scorer
        
        articles_by_category: Dict[str, List[NewsArticle]] = {}
        
        for category in categories:
            # Get freshness window for this category
            if category_freshness_windows and category in category_freshness_windows:
                freshness_window = category_freshness_windows[category]
            else:
                freshness_window = freshness_scorer.get_freshness_window(category)
            
            # Calculate cutoff time
            cutoff_time = datetime.utcnow() - timedelta(hours=freshness_window)
            
            # Query articles for this category
            stmt = select(NewsArticle).where(
                NewsArticle.category == category,
                NewsArticle.created_at >= cutoff_time,
                NewsArticle.is_active == True
            ).order_by(NewsArticle.created_at.desc())
            
            result = await self.session.execute(stmt)
            articles = result.scalars().all()
            
            articles_by_category[category] = articles
            logger.info(
                f"Retrieved {len(articles)} fresh articles for category '{category}' "
                f"(freshness_window={freshness_window}h)"
            )
        
        return articles_by_category

