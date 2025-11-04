"""Article summarization service using ChatGPT-4o-mini.

This service is kept for backward compatibility but now uses SummarizationProcessor
and StorageProcessor internally. New code should use PipelineService directly.
"""

from datetime import timedelta
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import NewsArticle
from app.services.processors.summarization import SummarizationProcessor
from app.services.processors.storage import StorageProcessor
from app.schemas import SelectedArticle, ProcessedArticle
from app.database import get_async_session
import logging

logger = logging.getLogger(__name__)

class SummarizerService:
    """Service for summarizing news articles using AI (backward compatibility wrapper)."""
    
    def __init__(self):
        """Initialize the summarizer service using processors."""
        self.summarization_processor = SummarizationProcessor(max_concurrent=5)
    
    async def summarize_article(self, article_data: Dict[str, Any]) -> str:
        """Generate a summary for a single article (backward compatibility)."""
        # Convert dict to SelectedArticle
        try:
            selected_article = SelectedArticle(
                title=article_data.get('title', ''),
                description=article_data.get('description'),
                url=article_data.get('url', ''),
                publishedAt=article_data.get('publishedAt'),
                source=article_data.get('source', 'Unknown'),
                category=article_data.get('category', '')
            )
            processed_articles = await self.summarization_processor.process([selected_article])
            if processed_articles and processed_articles[0].ai_summary:
                return processed_articles[0].ai_summary
            return article_data.get('description', '') or f"News article: {article_data.get('title', '')}"
        except Exception as e:
            logger.error(f"Failed to summarize article: {e}")
            return article_data.get('description', '') or f"News article: {article_data.get('title', '')}"
    
    async def summarize_articles_batch(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Summarize multiple articles concurrently with rate limiting (backward compatibility)."""
        if not articles:
            return []
        
        # Convert dicts to SelectedArticle
        selected_articles = [
            SelectedArticle(
                title=article.get('title', ''),
                description=article.get('description'),
                url=article.get('url', ''),
                publishedAt=article.get('publishedAt'),
                source=article.get('source', 'Unknown'),
                category=article.get('category', '')
            )
            for article in articles
        ]
        
        # Process through summarization processor
        processed_articles = await self.summarization_processor.process(selected_articles)
        
        # Convert back to dict for backward compatibility
        return [
            {
                **articles[i],
                'summary': processed_articles[i].ai_summary or articles[i].get('description', '')
            }
            for i in range(len(processed_articles))
        ]
    
    async def save_articles_to_database(self, articles: List[Dict[str, Any]], 
                                      session: AsyncSession) -> List[NewsArticle]:
        """Save summarized articles to the database (backward compatibility)."""
        # Convert dicts to ProcessedArticle
        processed_articles = [
            ProcessedArticle(
                title=article.get('title', ''),
                description=article.get('description'),
                url=article.get('url', ''),
                publishedAt=article.get('publishedAt'),
                source=article.get('source', 'Unknown'),
                category=article.get('category', ''),
                ai_summary=article.get('summary', '')  # Map 'summary' to 'ai_summary'
            )
            for article in articles
        ]
        
        # Use StorageProcessor
        storage_processor = StorageProcessor(session=session)
        return await storage_processor.process(processed_articles)
    
    async def process_and_save_articles(self, category_articles: Dict[str, List[Dict[str, Any]]]) -> List[NewsArticle]:
        """Process articles by summarizing and saving to database (backward compatibility)."""
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
        """Get recent articles from database for specified categories (backward compatibility)."""
        storage_processor = StorageProcessor(session=session)
        return await storage_processor.get_recent_articles(categories, hours)

# Global summarizer service instance
summarizer_service = SummarizerService()
