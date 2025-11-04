"""News selection service for fetching and filtering news articles.

This service is kept for backward compatibility but now uses SelectionProcessor internally.
New code should use SelectionProcessor directly or PipelineService.
"""

from typing import List, Dict, Any
from app.services.processors.selection import SelectionProcessor
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class NewsSelectionService:
    """Service for fetching and selecting news articles (backward compatibility wrapper)."""
    
    def __init__(self):
        """Initialize the selection service using SelectionProcessor."""
        self.processor = SelectionProcessor(top_count=settings.TOP_ARTICLES_PER_CATEGORY)
        self.top_articles_per_category = settings.TOP_ARTICLES_PER_CATEGORY
    
    async def fetch_news_for_category(self, category: str) -> List[Dict[str, Any]]:
        """Fetch news articles for a specific category (backward compatibility)."""
        raw_articles = await self.processor.fetch_news_for_category(category)
        # Convert RawArticle to dict for backward compatibility
        return [
            {
                'title': article.title,
                'description': article.description or '',
                'url': str(article.url),
                'publishedAt': article.publishedAt or '',
                'source': article.source,
                'category': article.category
            }
            for article in raw_articles
        ]
    
    async def select_top_articles_for_category(self, category: str) -> List[Dict[str, Any]]:
        """Fetch and select top articles for a category using AI (backward compatibility)."""
        raw_articles = await self.processor.fetch_news_for_category(category)
        if not raw_articles:
            return []
        
        selected_articles = await self.processor.process(raw_articles)
        # Convert SelectedArticle to dict for backward compatibility
        return [
            {
                'title': article.title,
                'description': article.description or '',
                'url': str(article.url),
                'publishedAt': article.publishedAt or '',
                'source': article.source,
                'category': article.category
            }
            for article in selected_articles
        ]
    
    async def select_articles_for_categories(self, categories: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Select top articles for multiple categories concurrently (backward compatibility)."""
        selected_by_category = await self.processor.select_articles_for_categories(categories)
        # Convert SelectedArticle to dict for backward compatibility
        result = {}
        for category, articles in selected_by_category.items():
            result[category] = [
                {
                    'title': article.title,
                    'description': article.description or '',
                    'url': str(article.url),
                    'publishedAt': article.publishedAt or '',
                    'source': article.source,
                    'category': article.category
                }
                for article in articles
            ]
        return result

# Global news selection service instance
news_selection_service = NewsSelectionService()
