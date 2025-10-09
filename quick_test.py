#!/usr/bin/env python3
"""Quick test script to verify the News API fixes."""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    import asyncio
    from app.services.selection import news_selection_service
    
    async def quick_test():
        print("🔧 Quick News API Test")
        print("=" * 30)
        
        # Test a single category
        print("Testing 'technology' category...")
        articles = await news_selection_service.fetch_news_for_category("technology")
        
        if articles:
            print(f"✅ Success! Found {len(articles)} articles")
            print(f"Sample: {articles[0]['title'][:50]}...")
        else:
            print("❌ No articles found")
        
        # Test article selection
        print("\nTesting article selection...")
        selected = await news_selection_service.select_top_articles_for_category("technology")
        
        if selected:
            print(f"✅ Selection successful! Got {len(selected)} top articles")
            for i, article in enumerate(selected, 1):
                print(f"  {i}. {article['title'][:50]}...")
        else:
            print("❌ Article selection failed")
    
    if __name__ == "__main__":
        asyncio.run(quick_test())
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the virtual environment:")
    print("  cd daily_briefing")
    print("  source ../venv/bin/activate")
    print("  python quick_test.py")
except Exception as e:
    print(f"❌ Error: {e}")
