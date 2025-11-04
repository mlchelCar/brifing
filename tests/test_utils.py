"""
MorningBrief - News Briefing Application
Copyright (c) 2025 Michel Car

Test utilities and helpers for E2E tests.
"""

import asyncio
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import init_database, get_async_session_factory
from app.models import NewsArticle
from app.schemas import RawArticle, SelectedArticle, ProcessedArticle
from app.services.processors.storage import StorageProcessor
from app.services.freshness import freshness_scorer
from app.services.relevance import relevance_validator
from app.services.ranking import article_ranker
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class TestUtils:
    """Utility class for test helpers."""
    
    @staticmethod
    async def setup_test_database():
        """Initialize test database."""
        await init_database()
        logger.info("Test database initialized")
    
    @staticmethod
    async def cleanup_test_articles(categories: Optional[List[str]] = None):
        """Clean up test articles from database."""
        async for session in get_async_session_factory():
            try:
                from sqlalchemy import delete
                
                if categories:
                    stmt = delete(NewsArticle).where(
                        NewsArticle.category.in_(categories)
                    )
                else:
                    stmt = delete(NewsArticle)
                
                await session.execute(stmt)
                await session.commit()
                logger.info(f"Cleaned up test articles for categories: {categories or 'all'}")
                break
            except Exception as e:
                logger.error(f"Error cleaning up test articles: {e}")
                await session.rollback()
    
    @staticmethod
    def create_test_raw_article(
        title: str,
        category: str = "technology",
        description: Optional[str] = None,
        url: Optional[str] = None,
        source: str = "Test Source"
    ) -> RawArticle:
        """Create a test RawArticle."""
        return RawArticle(
            title=title,
            description=description or f"Test description for {title}",
            url=url or f"https://example.com/article/{title.lower().replace(' ', '-')}",
            publishedAt=datetime.utcnow().isoformat(),
            source=source,
            category=category
        )
    
    @staticmethod
    def create_test_articles(count: int = 5, category: str = "technology") -> List[RawArticle]:
        """Create multiple test articles."""
        articles = []
        for i in range(count):
            articles.append(
                TestUtils.create_test_raw_article(
                    title=f"Test Article {i+1} - {category.title()}",
                    category=category,
                    description=f"This is test article {i+1} about {category} with detailed information about the topic.",
                    url=f"https://example.com/{category}/article-{i+1}"
                )
            )
        return articles
    
    @staticmethod
    async def save_test_articles(articles: List[ProcessedArticle]) -> List[NewsArticle]:
        """Save test articles to database."""
        async for session in get_async_session_factory():
            try:
                storage_processor = StorageProcessor(session=session)
                saved = await storage_processor.process(articles)
                logger.info(f"Saved {len(saved)} test articles to database")
                return saved
            except Exception as e:
                logger.error(f"Error saving test articles: {e}")
                await session.rollback()
                raise
    
    @staticmethod
    def create_test_news_article(
        title: str,
        category: str = "technology",
        created_hours_ago: int = 1,
        has_ai_summary: bool = True
    ) -> NewsArticle:
        """Create a test NewsArticle object."""
        created_at = datetime.utcnow() - timedelta(hours=created_hours_ago)
        
        article = NewsArticle(
            id=hash(f"{title}{category}") % 1000000,  # Simple ID generation
            category=category,
            title=title,
            url=f"https://example.com/{category}/{title.lower().replace(' ', '-')}",
            description=f"Test description for {title}",
            summary=f"Test summary for {title}",
            ai_summary=f"AI-generated summary for {title} with key insights and important information." if has_ai_summary else None,
            created_at=created_at,
            updated_at=created_at,
            is_active=True
        )
        return article
    
    @staticmethod
    async def get_test_session() -> AsyncSession:
        """Get a test database session."""
        session_factory = get_async_session_factory()
        async for session in session_factory():
            return session
    
    @staticmethod
    def calculate_freshness_for_article(article: NewsArticle) -> float:
        """Calculate freshness score for a test article."""
        return freshness_scorer.calculate_freshness_score(article.created_at, article.category)
    
    @staticmethod
    def calculate_relevance_for_article(article: NewsArticle) -> float:
        """Calculate relevance score for a test article."""
        return relevance_validator.calculate_relevance_score(article)
    
    @staticmethod
    def calculate_composite_for_article(article: NewsArticle) -> float:
        """Calculate composite score for a test article."""
        freshness = TestUtils.calculate_freshness_for_article(article)
        relevance = TestUtils.calculate_relevance_for_article(article)
        return article_ranker.calculate_composite_score(
            article,
            freshness_score=freshness,
            relevance_score=relevance
        )
    
    @staticmethod
    def setup_mock_mode():
        """Set up mock mode for testing."""
        os.environ["USE_MOCK"] = "True"
        os.environ["LLM_PROVIDER"] = "mock"
        # Reset LLM client to pick up new settings
        from app.utils.llm_provider import reset_llm_client
        reset_llm_client()
    
    @staticmethod
    def setup_openrouter_mode():
        """Set up OpenRouter mode for testing."""
        os.environ["USE_MOCK"] = "False"
        os.environ["LLM_PROVIDER"] = "openrouter"
        # Reset LLM client to pick up new settings
        from app.utils.llm_provider import reset_llm_client
        reset_llm_client()
    
    @staticmethod
    def setup_openai_mode():
        """Set up OpenAI mode for testing."""
        os.environ["USE_MOCK"] = "False"
        os.environ["LLM_PROVIDER"] = "openai"
        # Reset LLM client to pick up new settings
        from app.utils.llm_provider import reset_llm_client
        reset_llm_client()

