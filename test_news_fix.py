"""Test the fixed news API implementation."""

import requests
from datetime import datetime, timedelta

# Your API key
NEWS_API_KEY = "cda3c946119a4588875b1a376fd262c2"

def test_fixed_news_fetching():
    """Test the improved news fetching logic."""

    print("🔧 Testing Fixed News API Implementation")
    print("=" * 50)

    def fetch_news_for_category_fixed(category: str):
        """Improved news fetching function."""
        
        # Use top-headlines for better categories
        top_headlines_categories = ['technology', 'business', 'sports', 'entertainment', 'health', 'science']
        
        if category in top_headlines_categories:
            # Use top-headlines endpoint
            api_url = "https://newsapi.org/v2/top-headlines"
            params = {
                'category': category,
                'apiKey': NEWS_API_KEY,
                'language': 'en',
                'pageSize': 10,
                'country': 'us'
            }
            print(f"Using top-headlines for '{category}'")
        else:
            # Use everything endpoint for other categories
            to_date = datetime.utcnow()
            from_date = to_date - timedelta(days=3)
            
            api_url = "https://newsapi.org/v2/everything"
            params = {
                'q': category,
                'apiKey': NEWS_API_KEY,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': 10,
                'from': from_date.strftime('%Y-%m-%d'),
                'to': to_date.strftime('%Y-%m-%d')
            }
            print(f"Using everything endpoint for '{category}'")
        
        try:
            response = requests.get(api_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            articles = data.get('articles', [])

            # Filter valid articles
            cleaned_articles = []
            for article in articles:
                if (article.get('title') and
                    article.get('url') and
                    article.get('description') and
                    '[removed]' not in article.get('title', '').lower() and
                    '[removed]' not in article.get('description', '').lower()):

                    cleaned_article = {
                        'title': article.get('title', '').strip(),
                        'description': article.get('description', '').strip(),
                        'url': article.get('url', '').strip(),
                        'publishedAt': article.get('publishedAt', ''),
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'category': category
                    }
                    cleaned_articles.append(cleaned_article)

            return cleaned_articles
                
        except Exception as e:
            print(f"❌ Error fetching {category}: {e}")
            return []
    
    # Test different categories
    test_categories = ['technology', 'business', 'politics', 'sports', 'health']
    
    for category in test_categories:
        print(f"\n🔍 Testing category: {category}")
        articles = fetch_news_for_category_fixed(category)
        
        if articles:
            print(f"✅ Success! Found {len(articles)} articles")
            print(f"   Sample: {articles[0]['title'][:60]}...")
            print(f"   Source: {articles[0]['source']}")
        else:
            print(f"❌ No articles found for {category}")
    
    print(f"\n{'='*50}")
    print("🎉 News API fix test completed!")

if __name__ == "__main__":
    test_fixed_news_fetching()
