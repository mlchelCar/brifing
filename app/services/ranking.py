"""
MorningBrief - News Briefing Application
Copyright (c) 2025 Michel Car

Article ranking service for composite scoring and ranking.
"""

from typing import List, Dict, Optional
from app.models import NewsArticle
from app.services.freshness import freshness_scorer
from app.services.relevance import relevance_validator
import logging

logger = logging.getLogger(__name__)


class ArticleRanker:
    """Service for ranking articles using composite scoring."""
    
    def __init__(
        self,
        freshness_weight: float = 0.4,
        relevance_weight: float = 0.4,
        selection_weight: float = 0.2
    ):
        """
        Initialize article ranker.
        
        Args:
            freshness_weight: Weight for freshness score (default: 0.4)
            relevance_weight: Weight for relevance score (default: 0.4)
            selection_weight: Weight for AI selection score (default: 0.2)
        """
        self.freshness_weight = freshness_weight
        self.relevance_weight = relevance_weight
        self.selection_weight = selection_weight
        
        # Ensure weights sum to 1.0
        total_weight = freshness_weight + relevance_weight + selection_weight
        if total_weight != 1.0:
            logger.warning(
                f"Weights don't sum to 1.0 (sum={total_weight}), normalizing..."
            )
            self.freshness_weight /= total_weight
            self.relevance_weight /= total_weight
            self.selection_weight /= total_weight
    
    def calculate_composite_score(
        self,
        article: NewsArticle,
        freshness_score: Optional[float] = None,
        relevance_score: Optional[float] = None
    ) -> float:
        """
        Calculate composite score for an article.
        
        Formula: composite_score = (freshness * 0.4) + (relevance * 0.4) + (selection * 0.2)
        
        Args:
            article: NewsArticle object
            freshness_score: Pre-calculated freshness score (optional)
            relevance_score: Pre-calculated relevance score (optional)
            
        Returns:
            Composite score between 0.0 and 1.0
        """
        # Calculate freshness score if not provided
        if freshness_score is None:
            freshness_score = freshness_scorer.calculate_freshness_score(
                article.created_at,
                article.category
            )
        
        # Calculate relevance score if not provided
        if relevance_score is None:
            relevance_score = relevance_validator.calculate_relevance_score(article)
        
        # Selection score (we don't store this, so default to 0.5 for articles that passed selection)
        # In the future, we could store selection_score in the database
        selection_score = 0.5  # Default for articles that made it through selection
        
        # Calculate weighted composite score
        composite_score = (
            freshness_score * self.freshness_weight +
            relevance_score * self.relevance_weight +
            selection_score * self.selection_weight
        )
        
        return round(composite_score, 4)
    
    def rank_articles(
        self,
        articles: List[NewsArticle],
        limit: Optional[int] = None
    ) -> List[NewsArticle]:
        """
        Rank articles by composite score.
        
        Args:
            articles: List of NewsArticle objects
            limit: Maximum number of articles to return (None for all)
            
        Returns:
            Ranked list of articles (highest score first)
        """
        # Calculate composite scores for all articles
        scored_articles = []
        for article in articles:
            score = self.calculate_composite_score(article)
            scored_articles.append((article, score))
        
        # Sort by composite score (descending)
        scored_articles.sort(key=lambda x: x[1], reverse=True)
        
        # Extract articles
        ranked_articles = [article for article, score in scored_articles]
        
        # Apply limit if specified
        if limit is not None and limit > 0:
            ranked_articles = ranked_articles[:limit]
        
        logger.info(
            f"Ranked {len(articles)} articles, "
            f"returning top {len(ranked_articles)}"
        )
        
        return ranked_articles
    
    def rank_by_category(
        self,
        articles: List[NewsArticle],
        articles_per_category: int = 3
    ) -> Dict[str, List[NewsArticle]]:
        """
        Rank articles grouped by category, ensuring minimum articles per category.
        
        Args:
            articles: List of NewsArticle objects
            articles_per_category: Minimum articles per category
            
        Returns:
            Dictionary mapping category to ranked articles
        """
        # Group articles by category
        articles_by_category: Dict[str, List[NewsArticle]] = {}
        for article in articles:
            category = article.category
            if category not in articles_by_category:
                articles_by_category[category] = []
            articles_by_category[category].append(article)
        
        # Rank articles within each category
        ranked_by_category = {}
        for category, category_articles in articles_by_category.items():
            ranked = self.rank_articles(category_articles, limit=articles_per_category)
            ranked_by_category[category] = ranked
        
        logger.info(
            f"Ranked articles by category: "
            f"{', '.join(f'{cat}: {len(arts)}' for cat, arts in ranked_by_category.items())}"
        )
        
        return ranked_by_category
    
    def get_top_articles(
        self,
        articles: List[NewsArticle],
        limit: int = 10
    ) -> List[NewsArticle]:
        """
        Get top N articles by composite score.
        
        Args:
            articles: List of NewsArticle objects
            limit: Number of top articles to return
            
        Returns:
            Top N articles ranked by composite score
        """
        return self.rank_articles(articles, limit=limit)


# Global article ranker instance
article_ranker = ArticleRanker()

