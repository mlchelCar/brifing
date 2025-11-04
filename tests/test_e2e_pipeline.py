"""
MorningBrief - News Briefing Application
Copyright (c) 2025 Michel Car

Comprehensive end-to-end tests for the decoupled pipeline with freshness and relevance.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import init_database, get_async_session_factory
from app.models import NewsArticle
from app.services.pipeline import PipelineService
from app.services.processors.storage import StorageProcessor
from app.services.processors.selection import SelectionProcessor
from app.services.processors.summarization import SummarizationProcessor
from app.services.serving import SmartServingService
from app.services.freshness import freshness_scorer
from app.services.relevance import relevance_validator
from app.services.ranking import article_ranker
from app.schemas import ProcessedArticle
from app.config import settings
from tests.test_utils import TestUtils
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class E2EPipelineTester:
    """E2E test class for the decoupled pipeline."""
    
    def __init__(self):
        """Initialize E2E tester."""
        self.test_categories = ["technology", "business"]
        self.test_results = []
    
    async def setup(self):
        """Set up test environment."""
        logger.info("Setting up E2E test environment...")
        
        # Set up mock mode for testing
        TestUtils.setup_mock_mode()
        
        # Initialize database
        await TestUtils.setup_test_database()
        
        # Clean up any existing test articles
        await TestUtils.cleanup_test_articles(self.test_categories)
        
        logger.info("E2E test environment ready")
    
    async def cleanup(self):
        """Clean up test environment."""
        logger.info("Cleaning up E2E test environment...")
        await TestUtils.cleanup_test_articles(self.test_categories)
        logger.info("E2E test environment cleaned up")
    
    async def test_full_pipeline(self) -> bool:
        """Test the complete pipeline: Selection → Summarization → Storage."""
        logger.info("=" * 70)
        logger.info("Test 1: Full Pipeline Test")
        logger.info("=" * 70)
        
        try:
            # Create test articles
            test_articles = []
            for category in self.test_categories:
                category_articles = TestUtils.create_test_articles(count=5, category=category)
                test_articles.extend(category_articles)
            
            logger.info(f"Created {len(test_articles)} test articles")
            
            # Create pipeline service
            async for session in get_async_session_factory():
                storage_processor = StorageProcessor(session=session)
                pipeline_service = PipelineService(storage_processor=storage_processor)
                
                # Process articles through pipeline
                result = await pipeline_service.process_articles(
                    raw_articles=test_articles,
                    enable_selection=True,
                    enable_summarization=True,
                    enable_storage=True
                )
                
                logger.info(f"Pipeline processed {result.total_count} articles")
                logger.info(f"Success: {result.success_count}, Errors: {result.error_count}")
                
                # Verify articles were saved
                saved_articles = await storage_processor.get_recent_articles(
                    categories=self.test_categories,
                    hours=1
                )
                
                assert len(saved_articles) > 0, "No articles were saved to database"
                assert result.success_count > 0, "No articles were successfully processed"
                
                logger.info(f"✅ Full pipeline test passed: {len(saved_articles)} articles saved")
                return True
                
        except Exception as e:
            logger.error(f"❌ Full pipeline test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_freshness_scoring(self) -> bool:
        """Test freshness scoring with category-specific windows."""
        logger.info("=" * 70)
        logger.info("Test 2: Freshness Scoring Test")
        logger.info("=" * 70)
        
        try:
            # Create articles with different ages
            test_articles = []
            
            # Fresh article (1 hour ago)
            article_fresh = TestUtils.create_test_news_article(
                title="Fresh Technology Article",
                category="technology",
                created_hours_ago=1
            )
            test_articles.append(article_fresh)
            
            # Stale article (12 hours ago - beyond technology freshness window)
            article_stale = TestUtils.create_test_news_article(
                title="Stale Technology Article",
                category="technology",
                created_hours_ago=12
            )
            test_articles.append(article_stale)
            
            # Calculate freshness scores
            fresh_score = freshness_scorer.calculate_freshness_score(
                article_fresh.created_at,
                article_fresh.category
            )
            stale_score = freshness_scorer.calculate_freshness_score(
                article_stale.created_at,
                article_stale.category
            )
            
            logger.info(f"Fresh article score: {fresh_score:.4f}")
            logger.info(f"Stale article score: {stale_score:.4f}")
            
            # Verify freshness scoring
            assert fresh_score > stale_score, "Fresh article should have higher score"
            assert fresh_score > 0.5, "Fresh article should have good freshness score"
            assert stale_score < 0.3, "Stale article should have low freshness score"
            
            # Test category-specific windows
            tech_window = freshness_scorer.get_freshness_window("technology")
            science_window = freshness_scorer.get_freshness_window("science")
            
            logger.info(f"Technology freshness window: {tech_window}h")
            logger.info(f"Science freshness window: {science_window}h")
            
            assert tech_window < science_window, "Technology should have shorter freshness window"
            
            logger.info("✅ Freshness scoring test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Freshness scoring test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_relevance_validation(self) -> bool:
        """Test relevance validation and deduplication."""
        logger.info("=" * 70)
        logger.info("Test 3: Relevance Validation Test")
        logger.info("=" * 70)
        
        try:
            # Create test articles with different quality levels
            high_quality = TestUtils.create_test_news_article(
                title="High Quality Article with Detailed Information",
                category="technology",
                has_ai_summary=True
            )
            high_quality.description = "This is a comprehensive article with detailed information about the topic and extensive coverage of the subject matter."
            high_quality.ai_summary = "This article provides in-depth analysis of the topic with key insights and important information for readers."
            
            low_quality = TestUtils.create_test_news_article(
                title="Low Quality",
                category="technology",
                has_ai_summary=False
            )
            low_quality.description = "Short"
            
            # Calculate relevance scores
            high_score = relevance_validator.calculate_relevance_score(high_quality)
            low_score = relevance_validator.calculate_relevance_score(low_quality)
            
            logger.info(f"High quality article score: {high_score:.4f}")
            logger.info(f"Low quality article score: {low_score:.4f}")
            
            # Verify relevance scoring
            assert high_score > low_score, "High quality article should have higher relevance score"
            assert high_score >= settings.MIN_RELEVANCE_SCORE, "High quality article should meet minimum relevance"
            
            # Test deduplication
            duplicate1 = TestUtils.create_test_news_article(
                title="Duplicate Article Title",
                category="technology"
            )
            duplicate2 = TestUtils.create_test_news_article(
                title="Duplicate Article Title",
                category="technology"
            )
            duplicate2.url = duplicate1.url  # Same URL = exact duplicate
            
            articles = [duplicate1, duplicate2, high_quality]
            deduplicated = relevance_validator.deduplicate_articles(articles)
            
            logger.info(f"Original articles: {len(articles)}, Deduplicated: {len(deduplicated)}")
            
            assert len(deduplicated) < len(articles), "Deduplication should remove duplicates"
            
            logger.info("✅ Relevance validation test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Relevance validation test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_ranking_algorithm(self) -> bool:
        """Test composite ranking algorithm."""
        logger.info("=" * 70)
        logger.info("Test 4: Ranking Algorithm Test")
        logger.info("=" * 70)
        
        try:
            # Create articles with different scores
            fresh_high_quality = TestUtils.create_test_news_article(
                title="Fresh High Quality Article",
                category="technology",
                created_hours_ago=1,
                has_ai_summary=True
            )
            fresh_high_quality.description = "Comprehensive article with detailed information"
            fresh_high_quality.ai_summary = "Detailed AI summary with key insights"
            
            stale_low_quality = TestUtils.create_test_news_article(
                title="Stale Low Quality Article",
                category="technology",
                created_hours_ago=12,
                has_ai_summary=False
            )
            stale_low_quality.description = "Short"
            
            articles = [stale_low_quality, fresh_high_quality]
            
            # Rank articles
            ranked = article_ranker.rank_articles(articles)
            
            logger.info(f"Ranked {len(ranked)} articles")
            
            # Verify ranking
            assert ranked[0].title == fresh_high_quality.title, "Fresh high quality article should rank first"
            
            # Verify composite scores
            top_score = article_ranker.calculate_composite_score(ranked[0])
            bottom_score = article_ranker.calculate_composite_score(ranked[-1])
            
            logger.info(f"Top article composite score: {top_score:.4f}")
            logger.info(f"Bottom article composite score: {bottom_score:.4f}")
            
            assert top_score > bottom_score, "Top article should have higher composite score"
            
            logger.info("✅ Ranking algorithm test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ranking algorithm test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_smart_serving(self) -> bool:
        """Test smart serving with freshness checks and auto-refresh triggers."""
        logger.info("=" * 70)
        logger.info("Test 5: Smart Serving Test")
        logger.info("=" * 70)
        
        try:
            async for session in get_async_session_factory():
                # Create and save test articles
                test_articles = []
                for category in self.test_categories:
                    for i in range(3):
                        article = TestUtils.create_test_news_article(
                            title=f"Test {category} Article {i+1}",
                            category=category,
                            created_hours_ago=i+1,  # Different ages
                            has_ai_summary=True
                        )
                        test_articles.append(article)
                
                # Save articles to database using SQLAlchemy
                from sqlalchemy import select
                for article in test_articles:
                    # Check if article exists
                    stmt = select(NewsArticle).where(NewsArticle.url == article.url)
                    result = await session.execute(stmt)
                    existing = result.scalar_one_or_none()
                    
                    if not existing:
                        session.add(article)
                await session.commit()
                
                # Create smart serving service
                pipeline_service = PipelineService(storage_processor=storage_processor)
                serving_service = SmartServingService(
                    storage_processor=storage_processor,
                    pipeline_service=pipeline_service
                )
                
                # Get fresh articles
                articles, metadata = await serving_service.get_fresh_articles(
                    categories=self.test_categories,
                    min_articles_per_category=2,
                    auto_refresh=False  # Disable auto-refresh for testing
                )
                
                logger.info(f"Retrieved {len(articles)} fresh articles")
                logger.info(f"Metadata: {metadata}")
                
                # Verify we got articles
                assert len(articles) > 0, "Should retrieve fresh articles"
                
                # Verify freshness metadata
                assert "freshness_scores" in metadata, "Metadata should contain freshness scores"
                
                # Verify articles have freshness scores
                for article in articles:
                    article_metadata = await serving_service.get_article_metadata(article)
                    assert "freshness_score" in article_metadata, "Article should have freshness score"
                    assert article_metadata["freshness_score"] > 0, "Freshness score should be positive"
                
                logger.info("✅ Smart serving test passed")
                return True
                
        except Exception as e:
            logger.error(f"❌ Smart serving test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_api_endpoint(self) -> bool:
        """Test API endpoint with freshness metadata."""
        logger.info("=" * 70)
        logger.info("Test 6: API Endpoint Test")
        logger.info("=" * 70)
        
        try:
            # This would require FastAPI TestClient
            # For now, we'll test the serving logic directly
            async for session in get_async_session_factory():
                # Create test articles
                test_articles = []
                for category in self.test_categories:
                    article = TestUtils.create_test_news_article(
                        title=f"API Test {category} Article",
                        category=category,
                        created_hours_ago=1,
                        has_ai_summary=True
                    )
                    test_articles.append(article)
                
                # Save articles using SQLAlchemy
                for article in test_articles:
                    # Check if article exists
                    from sqlalchemy import select
                    stmt = select(NewsArticle).where(NewsArticle.url == article.url)
                    result = await session.execute(stmt)
                    existing = result.scalar_one_or_none()
                    
                    if not existing:
                        session.add(article)
                await session.commit()
                
                # Test serving service (simulates API endpoint logic)
                pipeline_service = PipelineService(storage_processor=storage_processor)
                serving_service = SmartServingService(
                    storage_processor=storage_processor,
                    pipeline_service=pipeline_service
                )
                
                articles, metadata = await serving_service.get_fresh_articles(
                    categories=self.test_categories,
                    min_articles_per_category=1
                )
                
                # Verify response structure
                assert len(articles) > 0, "Should return articles"
                assert "freshness_scores" in metadata, "Should include freshness metadata"
                
                # Verify article metadata
                for article in articles:
                    article_metadata = await serving_service.get_article_metadata(article)
                    assert "freshness_score" in article_metadata, "Article should have freshness score"
                    assert "relevance_score" in article_metadata, "Article should have relevance score"
                    assert "composite_score" in article_metadata, "Article should have composite score"
                
                logger.info("✅ API endpoint test passed")
                return True
                
        except Exception as e:
            logger.error(f"❌ API endpoint test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def run_all_tests(self):
        """Run all E2E tests."""
        logger.info("🚀 Starting E2E Pipeline Tests")
        logger.info("=" * 70)
        
        try:
            # Setup
            await self.setup()
            
            # Run tests
            tests = [
                ("Full Pipeline", self.test_full_pipeline),
                ("Freshness Scoring", self.test_freshness_scoring),
                ("Relevance Validation", self.test_relevance_validation),
                ("Ranking Algorithm", self.test_ranking_algorithm),
                ("Smart Serving", self.test_smart_serving),
                ("API Endpoint", self.test_api_endpoint),
            ]
            
            passed = 0
            total = len(tests)
            
            for test_name, test_func in tests:
                logger.info(f"\nRunning: {test_name}")
                result = await test_func()
                self.test_results.append((test_name, result))
                if result:
                    passed += 1
                    logger.info(f"✅ {test_name}: PASSED")
                else:
                    logger.error(f"❌ {test_name}: FAILED")
            
            # Summary
            logger.info("\n" + "=" * 70)
            logger.info("📊 E2E Test Results Summary")
            logger.info("=" * 70)
            
            for test_name, result in self.test_results:
                status = "✅ PASS" if result else "❌ FAIL"
                logger.info(f"{test_name:<30} {status}")
            
            logger.info(f"\nOverall: {passed}/{total} tests passed")
            
            if passed == total:
                logger.info("🎉 All E2E tests passed!")
            else:
                logger.warning(f"⚠️  {total - passed} test(s) failed")
            
        finally:
            # Cleanup
            await self.cleanup()


async def main():
    """Main test function."""
    tester = E2EPipelineTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())

