"""
MorningBrief - News Briefing Application
Copyright (c) 2025 Michel Car

Selection processor for AI-based article selection.
"""

import asyncio
import httpx
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from app.services.processors.base import Processor, ProcessingError
from app.schemas import RawArticle, SelectedArticle
from app.config import settings
from app.utils.llm_provider import get_llm_client
import logging

logger = logging.getLogger(__name__)


class SelectionProcessor(Processor[List[RawArticle], List[SelectedArticle]]):
    """Processor for selecting top articles using AI."""
    
    def __init__(self, top_count: int = 3):
        """
        Initialize selection processor.
        
        Args:
            top_count: Number of top articles to select
        """
        super().__init__("SelectionProcessor")
        self.top_count = top_count
        self.timeout = 30  # seconds
    
    async def process(self, input_data: List[RawArticle]) -> List[SelectedArticle]:
        """
        Process raw articles and return selected articles.
        
        Args:
            input_data: List of raw articles to select from
            
        Returns:
            List of selected articles
            
        Raises:
            ProcessingError: If selection fails
        """
        if not self.is_enabled():
            logger.warning(f"{self.name} is disabled, returning all articles")
            return [
                SelectedArticle.from_raw_article(article)
                for article in input_data[:self.top_count]
            ]
        
        if not input_data:
            return []
        
        if len(input_data) <= self.top_count:
            # Return all articles if we have fewer than top_count
            return [
                SelectedArticle.from_raw_article(article)
                for article in input_data
            ]
        
        try:
            # Convert RawArticle to dict format for OpenAI client (backward compatibility)
            articles_dict = [
                {
                    'title': article.title,
                    'description': article.description or '',
                    'url': str(article.url),
                    'publishedAt': article.publishedAt or '',
                    'source': article.source,
                    'category': article.category
                }
                for article in input_data
            ]
            
            # Use LLM to select top articles
            category = input_data[0].category if input_data else "general"
            llm_client = get_llm_client()
            selected_dicts = await llm_client.select_top_articles(
                articles=articles_dict,
                category=category,
                top_count=self.top_count
            )
            
            # Convert back to SelectedArticle
            selected_articles = []
            for selected_dict in selected_dicts:
                # Find matching RawArticle
                matching_raw = next(
                    (raw for raw in input_data if str(raw.url) == selected_dict.get('url', '')),
                    None
                )
                if matching_raw:
                    selected_articles.append(
                        SelectedArticle.from_raw_article(matching_raw)
                    )
            
            logger.info(f"{self.name} selected {len(selected_articles)} articles from {len(input_data)} candidates")
            return selected_articles[:self.top_count]
            
        except Exception as e:
            logger.error(f"{self.name} failed to process articles: {e}")
            raise ProcessingError(
                f"Failed to select articles: {str(e)}",
                self.name,
                original_error=e
            )
    
    async def fetch_news_for_category(self, category: str) -> List[RawArticle]:
        """
        Fetch raw news articles for a specific category.
        
        Args:
            category: News category to fetch
            
        Returns:
            List of raw articles
        """
        # Try multiple approaches for better results
        if category in settings.TOP_HEADLINES_CATEGORIES:
            api_url = "https://newsapi.org/v2/top-headlines"
            params = {
                'category': category,
                'apiKey': settings.NEWS_API_KEY,
                'language': 'en',
                'pageSize': settings.ARTICLES_PER_CATEGORY,
                'country': 'us'
            }
        else:
            # Use everything endpoint for other categories
            to_date = datetime.utcnow()
            from_date = to_date - timedelta(days=3)
            
            params = {
                'q': category,
                'apiKey': settings.NEWS_API_KEY,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': settings.ARTICLES_PER_CATEGORY,
                'from': from_date.strftime('%Y-%m-%d'),
                'to': to_date.strftime('%Y-%m-%d')
            }
            api_url = settings.NEWS_API_URL
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(api_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                articles = data.get('articles', [])
                
                # Filter and convert to RawArticle
                raw_articles = []
                for article in articles:
                    if self._is_valid_article(article):
                        try:
                            raw_article = RawArticle(
                                title=article.get('title', '').strip(),
                                description=article.get('description', '').strip() or None,
                                url=article.get('url', '').strip(),
                                publishedAt=article.get('publishedAt', ''),
                                source=article.get('source', {}).get('name', 'Unknown'),
                                category=category
                            )
                            raw_articles.append(raw_article)
                        except Exception as e:
                            logger.warning(f"Failed to create RawArticle: {e}")
                            continue
                
                logger.info(f"Fetched {len(raw_articles)} articles for category: {category}")
                return raw_articles
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching news for {category}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching news for {category}: {e}")
            return []
    
    def _is_valid_article(self, article: Dict) -> bool:
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
    
    async def select_articles_for_categories(self, categories: List[str]) -> Dict[str, List[SelectedArticle]]:
        """
        Select top articles for multiple categories concurrently.
        
        Args:
            categories: List of categories to process
            
        Returns:
            Dictionary mapping category to list of selected articles
        """
        # Validate categories
        valid_categories = [cat for cat in categories if cat in settings.AVAILABLE_CATEGORIES]
        
        if not valid_categories:
            logger.warning("No valid categories provided")
            return {}
        
        # Fetch and select articles for all categories concurrently
        async def process_category(category: str) -> tuple[str, List[SelectedArticle]]:
            raw_articles = await self.fetch_news_for_category(category)
            if not raw_articles:
                return category, []
            selected_articles = await self.process(raw_articles)
            return category, selected_articles
        
        tasks = [process_category(category) for category in valid_categories]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        category_articles = {}
        for category, result in zip(valid_categories, results):
            if isinstance(result, Exception):
                logger.error(f"Error processing category {category}: {result}")
                category_articles[category] = []
            elif isinstance(result, tuple):
                cat, articles = result
                category_articles[cat] = articles
        
        return category_articles

