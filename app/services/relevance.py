"""
MorningBrief - News Briefing Application
Copyright (c) 2025 Michel Car

Relevance validation service for article quality and deduplication.
"""

from typing import List, Dict, Set, Optional
from difflib import SequenceMatcher
from app.models import NewsArticle
import logging

logger = logging.getLogger(__name__)


class RelevanceValidator:
    """Service for validating article relevance and quality."""
    
    def __init__(self):
        """Initialize relevance validator."""
        # Minimum quality requirements
        self.min_title_length = 10
        self.min_description_length = 20
        self.min_summary_length = 30
        
        # Similarity threshold for deduplication (0.0 to 1.0)
        self.similarity_threshold = 0.85
    
    def calculate_relevance_score(self, article: NewsArticle) -> float:
        """
        Calculate relevance score for an article based on quality metrics.
        
        Args:
            article: NewsArticle object
            
        Returns:
            Relevance score between 0.0 and 1.0
        """
        score = 0.0
        
        # Title quality (30% weight)
        if article.title:
            title_length = len(article.title.strip())
            if title_length >= self.min_title_length:
                title_score = min(1.0, title_length / 100.0)  # Normalize to 100 chars
                score += title_score * 0.3
            else:
                logger.debug(f"Article {article.id} has short title: {title_length} chars")
        
        # Description quality (20% weight)
        if article.description:
            desc_length = len(article.description.strip())
            if desc_length >= self.min_description_length:
                desc_score = min(1.0, desc_length / 200.0)  # Normalize to 200 chars
                score += desc_score * 0.2
            else:
                logger.debug(f"Article {article.id} has short description: {desc_length} chars")
        
        # AI Summary quality (30% weight) - AI summaries are more valuable
        if article.ai_summary:
            summary_length = len(article.ai_summary.strip())
            if summary_length >= self.min_summary_length:
                summary_score = min(1.0, summary_length / 150.0)  # Normalize to 150 chars
                score += summary_score * 0.3
            else:
                logger.debug(f"Article {article.id} has short AI summary: {summary_length} chars")
        elif article.summary:
            # Fallback to regular summary if AI summary not available
            summary_length = len(article.summary.strip())
            if summary_length >= self.min_summary_length:
                summary_score = min(1.0, summary_length / 150.0) * 0.8  # Lower weight for non-AI summary
                score += summary_score * 0.3
        
        # URL validity (10% weight)
        if article.url and article.url.startswith(('http://', 'https://')):
            score += 0.1
        
        # Active status (10% weight)
        if article.is_active:
            score += 0.1
        
        return round(min(1.0, score), 4)
    
    def is_relevant(self, article: NewsArticle, min_score: float = 0.5) -> bool:
        """
        Check if an article meets minimum relevance requirements.
        
        Args:
            article: NewsArticle object
            min_score: Minimum relevance score required
            
        Returns:
            True if article is relevant, False otherwise
        """
        score = self.calculate_relevance_score(article)
        return score >= min_score
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts using SequenceMatcher.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not text1 or not text2:
            return 0.0
        
        # Normalize texts (lowercase, strip)
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()
        
        if text1 == text2:
            return 1.0
        
        return SequenceMatcher(None, text1, text2).ratio()
    
    def find_duplicates(self, articles: List[NewsArticle]) -> List[Set[int]]:
        """
        Find duplicate or very similar articles.
        
        Args:
            articles: List of NewsArticle objects
            
        Returns:
            List of sets containing IDs of duplicate articles
        """
        duplicates = []
        processed = set()
        
        for i, article1 in enumerate(articles):
            if article1.id in processed:
                continue
            
            duplicate_group = {article1.id}
            
            for j, article2 in enumerate(articles[i+1:], start=i+1):
                if article2.id in processed:
                    continue
                
                # Check title similarity
                title_similarity = self.calculate_similarity(
                    article1.title or "",
                    article2.title or ""
                )
                
                # Check URL similarity (exact match)
                url_match = article1.url == article2.url
                
                # Check description similarity
                desc_similarity = self.calculate_similarity(
                    article1.description or "",
                    article2.description or ""
                )
                
                # Consider duplicates if:
                # 1. Same URL (exact duplicate)
                # 2. Very similar title (> threshold)
                # 3. Similar title AND similar description
                if url_match:
                    duplicate_group.add(article2.id)
                    processed.add(article2.id)
                elif title_similarity >= self.similarity_threshold:
                    duplicate_group.add(article2.id)
                    processed.add(article2.id)
                elif title_similarity >= 0.7 and desc_similarity >= 0.7:
                    duplicate_group.add(article2.id)
                    processed.add(article2.id)
            
            if len(duplicate_group) > 1:
                duplicates.append(duplicate_group)
                processed.add(article1.id)
        
        return duplicates
    
    def deduplicate_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """
        Remove duplicate articles, keeping the most relevant one from each group.
        
        Args:
            articles: List of NewsArticle objects
            
        Returns:
            Deduplicated list of articles
        """
        if len(articles) <= 1:
            return articles
        
        duplicates = self.find_duplicates(articles)
        
        if not duplicates:
            return articles
        
        # Create article lookup by ID
        article_map = {article.id: article for article in articles}
        to_remove = set()
        
        # For each duplicate group, keep the most relevant article
        for duplicate_group in duplicates:
            group_articles = [article_map[article_id] for article_id in duplicate_group]
            
            # Sort by relevance score (descending)
            group_articles.sort(
                key=lambda a: self.calculate_relevance_score(a),
                reverse=True
            )
            
            # Keep the first (most relevant), mark others for removal
            to_keep = group_articles[0]
            for article in group_articles[1:]:
                to_remove.add(article.id)
                logger.debug(
                    f"Removing duplicate article {article.id} "
                    f"(keeping {to_keep.id}): {article.title[:50]}"
                )
        
        # Filter out duplicates
        deduplicated = [article for article in articles if article.id not in to_remove]
        
        logger.info(f"Deduplicated {len(articles)} articles to {len(deduplicated)} articles")
        return deduplicated
    
    def filter_by_relevance(
        self, 
        articles: List[NewsArticle], 
        min_score: float = 0.5
    ) -> List[NewsArticle]:
        """
        Filter articles by minimum relevance score.
        
        Args:
            articles: List of NewsArticle objects
            min_score: Minimum relevance score required
            
        Returns:
            Filtered list of relevant articles
        """
        relevant = [article for article in articles if self.is_relevant(article, min_score)]
        
        if len(relevant) < len(articles):
            logger.info(
                f"Filtered {len(articles)} articles to {len(relevant)} relevant articles "
                f"(min_score={min_score})"
            )
        
        return relevant


# Global relevance validator instance
relevance_validator = RelevanceValidator()

