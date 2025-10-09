"""Integration test script for Daily Briefing MVP."""

import asyncio
import os
import sys
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.config import settings
from app.database import init_database_sync, get_sync_session, get_async_session
from app.services.selection import news_selection_service
from app.services.summarizer import summarizer_service
from app.utils.openai_client import openai_client
from app.models import NewsArticle

async def test_openai_connection():
    """Test OpenAI API connection."""
    print("🔍 Testing OpenAI connection...")
    
    try:
        # Test with a simple summarization
        summary = await openai_client.summarize_article(
            title="Test Article",
            description="This is a test article to verify OpenAI connectivity.",
            url="https://example.com",
            category="technology"
        )
        print(f"✅ OpenAI connection successful!")
        print(f"   Sample summary: {summary[:100]}...")
        return True
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
        return False

async def test_news_api_connection():
    """Test News API connection."""
    print("\n🔍 Testing News API connection...")
    
    try:
        # Test fetching news for a single category
        articles = await news_selection_service.fetch_news_for_category("technology")
        
        if articles:
            print(f"✅ News API connection successful!")
            print(f"   Fetched {len(articles)} articles for 'technology' category")
            print(f"   Sample article: {articles[0]['title'][:50]}...")
            return True
        else:
            print("⚠️  News API connected but no articles returned")
            return False
            
    except Exception as e:
        print(f"❌ News API connection failed: {e}")
        return False

async def test_article_selection():
    """Test AI-powered article selection."""
    print("\n🔍 Testing article selection...")
    
    try:
        # Get articles for technology category
        selected_articles = await news_selection_service.select_top_articles_for_category("technology")
        
        if selected_articles:
            print(f"✅ Article selection successful!")
            print(f"   Selected {len(selected_articles)} top articles")
            for i, article in enumerate(selected_articles, 1):
                print(f"   {i}. {article['title'][:50]}...")
            return True
        else:
            print("⚠️  Article selection completed but no articles returned")
            return False
            
    except Exception as e:
        print(f"❌ Article selection failed: {e}")
        return False

async def test_article_summarization():
    """Test article summarization."""
    print("\n🔍 Testing article summarization...")
    
    try:
        # Create a test article
        test_article = {
            'title': 'AI Breakthrough in Healthcare Technology',
            'description': 'Researchers have developed a new artificial intelligence system that can diagnose diseases with unprecedented accuracy.',
            'url': 'https://example.com/ai-healthcare',
            'category': 'technology'
        }
        
        summary = await summarizer_service.summarize_article(test_article)
        
        print(f"✅ Article summarization successful!")
        print(f"   Original: {test_article['description']}")
        print(f"   Summary: {summary}")
        return True
        
    except Exception as e:
        print(f"❌ Article summarization failed: {e}")
        return False

def test_database_connection():
    """Test database connection and operations."""
    print("\n🔍 Testing database connection...")
    
    try:
        # Initialize database
        init_database_sync()
        
        # Test database session
        session = get_sync_session()
        
        # Try to query articles (should work even if empty)
        articles = session.query(NewsArticle).limit(5).all()
        session.close()
        
        print(f"✅ Database connection successful!")
        print(f"   Found {len(articles)} existing articles in database")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def test_end_to_end_workflow():
    """Test the complete end-to-end workflow."""
    print("\n🔍 Testing end-to-end workflow...")
    
    try:
        # Test categories
        test_categories = ["technology", "business"]
        
        print(f"   Testing with categories: {test_categories}")
        
        # Step 1: Fetch and select articles
        category_articles = await news_selection_service.select_articles_for_categories(test_categories)
        
        if not category_articles:
            print("⚠️  No articles fetched for test categories")
            return False
        
        print(f"   ✓ Fetched articles for {len(category_articles)} categories")
        
        # Step 2: Summarize and save articles
        saved_articles = await summarizer_service.process_and_save_articles(category_articles)
        
        print(f"   ✓ Processed and saved {len(saved_articles)} articles")
        
        # Step 3: Verify articles in database
        async for session in get_async_session():
            recent_articles = await summarizer_service.get_recent_articles(
                categories=test_categories,
                session=session,
                hours=1
            )
            break
        
        print(f"   ✓ Retrieved {len(recent_articles)} recent articles from database")
        
        print("✅ End-to-end workflow successful!")
        return True
        
    except Exception as e:
        print(f"❌ End-to-end workflow failed: {e}")
        return False

def check_environment():
    """Check environment configuration."""
    print("🔍 Checking environment configuration...")
    
    issues = []
    
    # Check required environment variables
    if not settings.OPENAI_API_KEY:
        issues.append("OPENAI_API_KEY is not set")
    
    if not settings.NEWS_API_KEY:
        issues.append("NEWS_API_KEY is not set")
    
    # Check API keys format (basic validation)
    if settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith('sk-'):
        issues.append("OPENAI_API_KEY format appears invalid (should start with 'sk-')")
    
    if issues:
        print("❌ Environment configuration issues:")
        for issue in issues:
            print(f"   • {issue}")
        return False
    else:
        print("✅ Environment configuration looks good!")
        return True

async def main():
    """Run all integration tests."""
    print("🚀 Daily Briefing Integration Tests")
    print("=" * 50)
    
    # Track test results
    test_results = []
    
    # Environment check
    env_ok = check_environment()
    test_results.append(("Environment", env_ok))
    
    if not env_ok:
        print("\n❌ Environment issues detected. Please fix configuration before running other tests.")
        return
    
    # Database test
    db_ok = test_database_connection()
    test_results.append(("Database", db_ok))
    
    # API connection tests
    openai_ok = await test_openai_connection()
    test_results.append(("OpenAI API", openai_ok))
    
    news_api_ok = await test_news_api_connection()
    test_results.append(("News API", news_api_ok))
    
    # Component tests
    if openai_ok and news_api_ok:
        selection_ok = await test_article_selection()
        test_results.append(("Article Selection", selection_ok))
        
        summarization_ok = await test_article_summarization()
        test_results.append(("Article Summarization", summarization_ok))
        
        # End-to-end test
        if db_ok and selection_ok and summarization_ok:
            e2e_ok = await test_end_to_end_workflow()
            test_results.append(("End-to-End Workflow", e2e_ok))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Daily Briefing MVP is ready to use.")
    else:
        print("⚠️  Some tests failed. Please check the configuration and try again.")

if __name__ == "__main__":
    asyncio.run(main())
