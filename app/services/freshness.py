"""
MorningBrief - News Briefing Application
Copyright (c) 2025 Michel Car

Freshness scoring system for article freshness evaluation.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class FreshnessScorer:
    """Service for calculating article freshness scores."""
    
    def __init__(self):
        """Initialize freshness scorer with category-specific windows."""
        # Category-specific freshness windows (in hours)
        # Breaking news categories need fresher content
        self.freshness_windows = {
            # Breaking news: 6 hours
            "technology": 6,
            "politics": 6,
            "business": 6,
            # Standard news: 12 hours
            "sports": 12,
            "entertainment": 12,
            "health": 12,
            "world": 12,
            # Evergreen content: 24 hours
            "science": 24,
            "environment": 24,
            "finance": 12,  # Financial news needs timely updates
        }
        
        # Default freshness window if category not found
        self.default_freshness_window = 24
        
        # Minimum freshness score to serve (0.0 to 1.0)
        self.min_freshness_score = 0.3
    
    def get_freshness_window(self, category: str) -> int:
        """
        Get freshness window for a category.
        
        Args:
            category: News category
            
        Returns:
            Freshness window in hours
        """
        return self.freshness_windows.get(category.lower(), self.default_freshness_window)
    
    def calculate_freshness_score(self, article_created_at: datetime, category: str) -> float:
        """
        Calculate freshness score for an article.
        
        Formula: freshness_score = max(0, 1 - (age_hours / freshness_window_hours))
        
        Args:
            article_created_at: When the article was created
            category: Article category
            
        Returns:
            Freshness score between 0.0 (stale) and 1.0 (fresh)
        """
        now = datetime.utcnow()
        age = now - article_created_at
        age_hours = age.total_seconds() / 3600.0
        
        freshness_window = self.get_freshness_window(category)
        
        # Calculate freshness score with exponential decay
        if age_hours >= freshness_window:
            return 0.0
        
        # Linear decay: score decreases linearly as article ages
        freshness_score = max(0.0, 1.0 - (age_hours / freshness_window))
        
        # Apply exponential decay for older articles (makes decay more aggressive)
        if age_hours > freshness_window * 0.5:
            # Articles older than half the window get exponential penalty
            excess_age = age_hours - (freshness_window * 0.5)
            excess_ratio = excess_age / (freshness_window * 0.5)
            decay_factor = 1.0 - (excess_ratio ** 1.5)  # Exponential decay
            freshness_score = max(0.0, freshness_score * decay_factor)
        
        return round(freshness_score, 4)
    
    def is_fresh(self, article_created_at: datetime, category: str) -> bool:
        """
        Check if an article is considered fresh.
        
        Args:
            article_created_at: When the article was created
            category: Article category
            
        Returns:
            True if article is fresh, False otherwise
        """
        score = self.calculate_freshness_score(article_created_at, category)
        return score >= self.min_freshness_score
    
    def get_freshness_tier(self, freshness_score: float) -> str:
        """
        Get human-readable freshness tier.
        
        Args:
            freshness_score: Freshness score (0.0 to 1.0)
            
        Returns:
            Freshness tier string
        """
        if freshness_score >= 0.8:
            return "very_fresh"
        elif freshness_score >= 0.6:
            return "fresh"
        elif freshness_score >= 0.4:
            return "moderate"
        elif freshness_score >= 0.2:
            return "stale"
        else:
            return "very_stale"
    
    def should_refresh(self, article_created_at: datetime, category: str) -> bool:
        """
        Determine if articles for a category should be refreshed.
        
        Args:
            article_created_at: When the article was created
            category: Article category
            
        Returns:
            True if refresh is needed, False otherwise
        """
        freshness_window = self.get_freshness_window(category)
        age = datetime.utcnow() - article_created_at
        age_hours = age.total_seconds() / 3600.0
        
        # Refresh if article is older than freshness window
        return age_hours >= freshness_window


# Global freshness scorer instance
freshness_scorer = FreshnessScorer()

