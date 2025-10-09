"""Debug script to test News API connectivity and responses."""

import requests
import json
from datetime import datetime, timedelta
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.config import settings

def test_news_api_basic():
    """Test basic News API connectivity."""
    print("🔍 Testing basic News API connectivity...")
    
    # Test with top headlines endpoint (simpler)
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        'apiKey': settings.NEWS_API_KEY,
        'language': 'en',
        'pageSize': 5,
        'country': 'us'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Basic API call successful!")
            print(f"Total results: {data.get('totalResults', 0)}")
            print(f"Articles returned: {len(data.get('articles', []))}")
            
            if data.get('articles'):
                print(f"Sample article: {data['articles'][0]['title'][:50]}...")
                return True
            else:
                print("⚠️  No articles in response")
                return False
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_news_api_everything():
    """Test the 'everything' endpoint that we're using."""
    print("\n🔍 Testing News API 'everything' endpoint...")
    
    # Test with current parameters
    url = settings.NEWS_API_URL
    to_date = datetime.utcnow()
    from_date = to_date - timedelta(days=1)
    
    params = {
        'q': 'technology',
        'apiKey': settings.NEWS_API_KEY,
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': 5,
        'from': from_date.isoformat(),
        'to': to_date.isoformat()
    }
    
    print(f"URL: {url}")
    print(f"Query: {params['q']}")
    print(f"From: {params['from']}")
    print(f"To: {params['to']}")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Everything endpoint successful!")
            print(f"Total results: {data.get('totalResults', 0)}")
            print(f"Articles returned: {len(data.get('articles', []))}")
            
            if data.get('articles'):
                for i, article in enumerate(data['articles'][:3], 1):
                    print(f"  {i}. {article['title'][:60]}...")
                return True
            else:
                print("⚠️  No articles in response")
                return False
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_different_queries():
    """Test with different query parameters."""
    print("\n🔍 Testing different query parameters...")
    
    queries = [
        'technology',
        'AI',
        'bitcoin',
        'apple',
        'google'
    ]
    
    url = "https://newsapi.org/v2/top-headlines"
    
    for query in queries:
        print(f"\n  Testing query: '{query}'")
        
        params = {
            'q': query,
            'apiKey': settings.NEWS_API_KEY,
            'language': 'en',
            'pageSize': 3
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                article_count = len(data.get('articles', []))
                print(f"    ✅ {article_count} articles found")
                
                if article_count > 0:
                    print(f"    Sample: {data['articles'][0]['title'][:50]}...")
            else:
                print(f"    ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")

def test_api_key_validity():
    """Test if the API key is valid."""
    print("\n🔍 Testing API key validity...")
    
    # Simple request to check API key
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        'apiKey': settings.NEWS_API_KEY,
        'country': 'us',
        'pageSize': 1
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            print("✅ API key is valid!")
            return True
        elif response.status_code == 401:
            print("❌ API key is invalid or unauthorized")
            return False
        elif response.status_code == 429:
            print("⚠️  Rate limit exceeded")
            return False
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API key: {e}")
        return False

def main():
    """Run all debug tests."""
    print("🔧 News API Debug Tests")
    print("=" * 50)
    
    print(f"API Key: {settings.NEWS_API_KEY[:10]}...{settings.NEWS_API_KEY[-5:]}")
    print(f"API URL: {settings.NEWS_API_URL}")
    
    # Test API key validity
    key_valid = test_api_key_validity()
    
    if not key_valid:
        print("\n❌ API key issue detected. Please check your News API key.")
        return
    
    # Test basic connectivity
    basic_ok = test_news_api_basic()
    
    # Test everything endpoint
    everything_ok = test_news_api_everything()
    
    # Test different queries
    test_different_queries()
    
    print("\n" + "=" * 50)
    print("📊 Debug Summary:")
    print("=" * 50)
    print(f"API Key Valid: {'✅' if key_valid else '❌'}")
    print(f"Basic Endpoint: {'✅' if basic_ok else '❌'}")
    print(f"Everything Endpoint: {'✅' if everything_ok else '❌'}")
    
    if basic_ok and not everything_ok:
        print("\n💡 Suggestion: The 'everything' endpoint might have stricter requirements.")
        print("   Consider using 'top-headlines' endpoint instead for better reliability.")

if __name__ == "__main__":
    main()
