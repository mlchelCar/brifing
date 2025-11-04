"""
MorningBrief - News Briefing Application
Copyright (c) 2025 Michel Car

Smart serving service for orchestrating freshness, relevance, and ranking.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import NewsArticle
from app.services.freshness import freshness_scorer
from app.services.relevance import relevance_validator
from app.services.ranking import article_ranker
from app.services.processors.storage import StorageProcessor
from app.services.pipeline import PipelineService
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class SmartServingService:
    """Service for smart article serving with freshness and relevance guarantees."""
    
    def __init__(self, storage_processor: StorageProcessor, pipeline_service: Optional[PipelineService] = None):
        """
        Initialize smart serving service.
        
        Args:
            storage_processor: Storage processor for database queries
            pipeline_service: Optional pipeline service for refreshing articles
        """
        self.storage_processor = storage_processor
        self.pipeline_service = pipeline_service
    
    async def get_fresh_articles(
        self,
        categories: List[str],
        min_articles_per_category: int = 3,
        auto_refresh: bool = True
    ) -> Tuple[List[NewsArticle], Dict[str, any]]:
        """
        Get fresh and relevant articles for specified categories.
        
        Args:
            categories: List of categories to retrieve
            min_articles_per_category: Minimum articles per category
            auto_refresh: Whether to automatically refresh stale articles
            
        Returns:
            Tuple of (articles, metadata) where metadata contains freshness info
        """
        metadata = {
            "categories": categories,
            "articles_found": {},
            "freshness_scores": {},
            "refresh_triggered": False,
            "timestamp": datetime.utcnow()
        }
        
        # Get fresh articles by category with category-specific windows
        category_articles = await self.storage_processor.get_fresh_articles_by_category(categories)
        
        # Process each category
        all_articles = []
        needs_refresh = []
        
        for category in categories:
            articles = category_articles.get(category, [])
            metadata["articles_found"][category] = len(articles)
            
            if not articles:
                logger.warning(f"No fresh articles found for category: {category}")
                needs_refresh.append(category)
                continue
            
            # Calculate freshness scores
            freshness_scores = []
            for article in articles:
                score = freshness_scorer.calculate_freshness_score(article.created_at, category)
                freshness_scores.append(score)
            
            avg_freshness = sum(freshness_scores) / len(freshness_scores) if freshness_scores else 0.0
            metadata["freshness_scores"][category] = {
                "average": round(avg_freshness, 4),
                "min": round(min(freshness_scores), 4) if freshness_scores else 0.0,
                "max": round(max(freshness_scores), 4) if freshness_scores else 0.0
            }
            
            # Check if refresh is needed
            if avg_freshness < settings.AUTO_REFRESH_FRESHNESS_THRESHOLD:
                logger.info(
                    f"Category '{category}' has low freshness score ({avg_freshness:.2f}), "
                    f"marking for refresh"
                )
                needs_refresh.append(category)
            
            # Check if we have minimum articles
            if len(articles) < min_articles_per_category:
                logger.info(
                    f"Category '{category}' has only {len(articles)} articles "
                    f"(min: {min_articles_per_category}), marking for refresh"
                )
                needs_refresh.append(category)
            
            all_articles.extend(articles)
        
        # Trigger refresh if needed and enabled
        if auto_refresh and needs_refresh and self.pipeline_service:
            logger.info(f"Triggering refresh for categories: {needs_refresh}")
            metadata["refresh_triggered"] = True
            metadata["refresh_categories"] = needs_refresh
            
            # Trigger background refresh (don't await to avoid blocking)
            try:
                # Note: In a real implementation, you might want to use a background task
                # For now, we'll just log that refresh is needed
                # The actual refresh can be handled by the API route
                pass
            except Exception as e:
                logger.error(f"Failed to trigger refresh: {e}")
        
        # Deduplicate articles
        all_articles = relevance_validator.deduplicate_articles(all_articles)
        
        # Filter by relevance
        all_articles = relevance_validator.filter_by_relevance(
            all_articles,
            min_score=settings.MIN_RELEVANCE_SCORE
        )
        
        # Rank articles
        ranked_articles = article_ranker.rank_articles(all_articles)
        
        # Ensure minimum articles per category
        final_articles = self._ensure_minimum_per_category(
            ranked_articles,
            categories,
            min_articles_per_category
        )
        
        metadata["total_articles"] = len(final_articles)
        metadata["articles_after_filtering"] = {
            "before_dedup": len(all_articles),
            "after_dedup": len(ranked_articles),
            "final": len(final_articles)
        }
        
        return final_articles, metadata
    
    def _ensure_minimum_per_category(
        self,
        articles: List[NewsArticle],
        categories: List[str],
        min_articles: int
    ) -> List[NewsArticle]:
        """
        Ensure minimum articles per category, filling with lower-ranked if needed.
        
        Args:
            articles: Ranked articles
            categories: Categories to ensure
            min_articles: Minimum articles per category
            
        Returns:
            Articles with minimum per category guaranteed
        """
        articles_by_category: Dict[str, List[NewsArticle]] = {}
        for article in articles:
            category = article.category
            if category not in articles_by_category:
                articles_by_category[category] = []
            articles_by_category[category].append(article)
        
        final_articles = []
        for category in categories:
            category_articles = articles_by_category.get(category, [])
            
            # Take top N articles for this category
            selected = category_articles[:min_articles] if len(category_articles) >= min_articles else category_articles
            
            final_articles.extend(selected)
            
            if len(selected) < min_articles:
                logger.warning(
                    f"Category '{category}' has only {len(selected)} articles "
                    f"(requested: {min_articles})"
                )
        
        return final_articles
    
    async def should_refresh_category(self, category: str) -> Tuple[bool, str]:
        """
        Determine if a category should be refreshed.
        
        Args:
            category: Category to check
            
        Returns:
            Tuple of (should_refresh, reason)
        """
        category_articles = await self.storage_processor.get_fresh_articles_by_category([category])
        articles = category_articles.get(category, [])
        
        if not articles:
            return True, "no_articles"
        
        # Check freshness scores
        freshness_scores = [
            freshness_scorer.calculate_freshness_score(article.created_at, category)
            for article in articles
        ]
        
        if not freshness_scores:
            return True, "no_freshness_data"
        
        avg_freshness = sum(freshness_scores) / len(freshness_scores)
        
        if avg_freshness < settings.AUTO_REFRESH_FRESHNESS_THRESHOLD:
            return True, f"low_freshness_score_{avg_freshness:.2f}"
        
        if len(articles) < settings.MIN_ARTICLES_PER_CATEGORY:
            return True, f"insufficient_articles_{len(articles)}"
        
        return False, "ok"
    
    async def get_article_metadata(self, article: NewsArticle) -> Dict[str, any]:
        """
        Get metadata for an article including freshness and relevance scores.
        
        Args:
            article: NewsArticle object
            
        Returns:
            Dictionary with metadata
        """
        freshness_score = freshness_scorer.calculate_freshness_score(
            article.created_at,
            article.category
        )
        relevance_score = relevance_validator.calculate_relevance_score(article)
        composite_score = article_ranker.calculate_composite_score(
            article,
            freshness_score=freshness_score,
            relevance_score=relevance_score
        )
        
        return {
            "freshness_score": freshness_score,
            "freshness_tier": freshness_scorer.get_freshness_tier(freshness_score),
            "relevance_score": relevance_score,
            "composite_score": composite_score,
            "is_fresh": freshness_scorer.is_fresh(article.created_at, article.category),
            "is_relevant": relevance_validator.is_relevant(article),
            "freshness_window_hours": freshness_scorer.get_freshness_window(article.category)
        }

