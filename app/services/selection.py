"""News selection service for fetching and filtering news articles."""

import asyncio
import httpx
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from app.config import settings
from app.utils.openai_client import openai_client
import logging

logger = logging.getLogger(__name__)

class NewsSelectionService:
    """Service for fetching and selecting news articles."""
    
    def __init__(self):
        self.api_key = settings.NEWS_API_KEY
        self.api_url = settings.NEWS_API_URL
        self.articles_per_category = settings.ARTICLES_PER_CATEGORY
        self.top_articles_per_category = settings.TOP_ARTICLES_PER_CATEGORY
        self.timeout = 30  # seconds
    
    async def fetch_news_for_category(self, category: str) -> List[Dict[str, Any]]:
        """Fetch news articles for a specific category."""

        # Try multiple approaches for better results
        # First try: Use top-headlines for more reliable results
        if category in settings.TOP_HEADLINES_CATEGORIES:
            # Use top-headlines endpoint for better categories
            api_url = "https://newsapi.org/v2/top-headlines"
            params = {
                'category': category,
                'apiKey': self.api_key,
                'language': 'en',
                'pageSize': self.articles_per_category,
                'country': 'us'
            }
        else:
            # Use everything endpoint for other categories
            # Calculate date range (last 3 days for better results)
            to_date = datetime.utcnow()
            from_date = to_date - timedelta(days=3)

            params = {
                'q': category,
                'apiKey': self.api_key,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': self.articles_per_category,
                'from': from_date.strftime('%Y-%m-%d'),
                'to': to_date.strftime('%Y-%m-%d')
            }
            api_url = self.api_url
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(api_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                articles = data.get('articles', [])
                
                # Filter and clean articles
                cleaned_articles = []
                for article in articles:
                    if self._is_valid_article(article):
                        cleaned_article = {
                            'title': article.get('title', '').strip(),
                            'description': article.get('description', '').strip(),
                            'url': article.get('url', '').strip(),
                            'publishedAt': article.get('publishedAt', ''),
                            'source': article.get('source', {}).get('name', 'Unknown'),
                            'category': category
                        }
                        cleaned_articles.append(cleaned_article)
                
                logger.info(f"Fetched {len(cleaned_articles)} articles for category: {category}")
                return cleaned_articles
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching news for {category}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching news for {category}: {e}")
            return []
    
    def _is_valid_article(self, article: Dict[str, Any]) -> bool:
        """Check if an article is valid and complete."""
        required_fields = ['title', 'url']
        
        # Check required fields
        for field in required_fields:
            if not article.get(field):
                return False
        
        # Filter out removed articles
        title = article.get('title', '').lower()
        if '[removed]' in title or 'removed' == title:
            return False
        
        # Filter out articles without description
        description = article.get('description', '')
        if not description or description.lower() in ['[removed]', 'removed']:
            return False
        
        return True
    
    async def select_top_articles_for_category(self, category: str) -> List[Dict[str, Any]]:
        """Fetch and select top articles for a category using AI."""
        
        # Fetch all articles for the category
        all_articles = await self.fetch_news_for_category(category)
        
        if not all_articles:
            logger.warning(f"No articles found for category: {category}")
            return []
        
        # Use AI to select top articles
        try:
            selected_articles = await openai_client.select_top_articles(
                articles=all_articles,
                category=category,
                top_count=self.top_articles_per_category
            )
            
            logger.info(f"Selected {len(selected_articles)} top articles for category: {category}")
            return selected_articles
            
        except Exception as e:
            logger.error(f"Error selecting top articles for {category}: {e}")
            # Fallback: return first N articles
            return all_articles[:self.top_articles_per_category]
    
    async def select_articles_for_categories(self, categories: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Select top articles for multiple categories concurrently."""
        
        # Validate categories
        valid_categories = [cat for cat in categories if cat in settings.AVAILABLE_CATEGORIES]
        
        if not valid_categories:
            logger.warning("No valid categories provided")
            return {}
        
        # Fetch articles for all categories concurrently
        tasks = [
            self.select_top_articles_for_category(category)
            for category in valid_categories
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        category_articles = {}
        for category, result in zip(valid_categories, results):
            if isinstance(result, Exception):
                logger.error(f"Error processing category {category}: {result}")
                category_articles[category] = []
            else:
                category_articles[category] = result
        
        return category_articles

# Global news selection service instance
news_selection_service = NewsSelectionService()
