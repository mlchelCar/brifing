"""Simple News API test without dependencies."""

import requests
import json
from datetime import datetime, timedelta
import os

# Load API key from environment or .env file
NEWS_API_KEY = "cda3c946119a4588875b1a376fd262c2"  # Your API key from .env

def test_news_api():
    """Test News API with different endpoints."""
    
    print("🔧 Simple News API Test")
    print("=" * 40)
    print(f"API Key: {NEWS_API_KEY[:10]}...{NEWS_API_KEY[-5:]}")
    
    # Test 1: Top Headlines (simpler endpoint)
    print("\n🔍 Test 1: Top Headlines")
    url1 = "https://newsapi.org/v2/top-headlines"
    params1 = {
        'apiKey': NEWS_API_KEY,
        'language': 'en',
        'country': 'us',
        'pageSize': 5
    }
    
    try:
        response1 = requests.get(url1, params=params1, timeout=10)
        print(f"Status: {response1.status_code}")
        
        if response1.status_code == 200:
            data1 = response1.json()
            articles1 = data1.get('articles', [])
            print(f"✅ Success! Found {len(articles1)} articles")
            if articles1:
                print(f"Sample: {articles1[0]['title'][:50]}...")
        else:
            print(f"❌ Failed: {response1.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Everything endpoint with technology
    print("\n🔍 Test 2: Everything - Technology")
    url2 = "https://newsapi.org/v2/everything"
    params2 = {
        'q': 'technology',
        'apiKey': NEWS_API_KEY,
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': 5
    }
    
    try:
        response2 = requests.get(url2, params=params2, timeout=10)
        print(f"Status: {response2.status_code}")
        
        if response2.status_code == 200:
            data2 = response2.json()
            articles2 = data2.get('articles', [])
            print(f"✅ Success! Found {len(articles2)} articles")
            if articles2:
                print(f"Sample: {articles2[0]['title'][:50]}...")
        else:
            print(f"❌ Failed: {response2.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Everything endpoint with date range
    print("\n🔍 Test 3: Everything - With Date Range")
    to_date = datetime.utcnow()
    from_date = to_date - timedelta(days=1)
    
    url3 = "https://newsapi.org/v2/everything"
    params3 = {
        'q': 'technology',
        'apiKey': NEWS_API_KEY,
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': 5,
        'from': from_date.strftime('%Y-%m-%d'),
        'to': to_date.strftime('%Y-%m-%d')
    }
    
    try:
        response3 = requests.get(url3, params=params3, timeout=10)
        print(f"Status: {response3.status_code}")
        print(f"Date range: {params3['from']} to {params3['to']}")
        
        if response3.status_code == 200:
            data3 = response3.json()
            articles3 = data3.get('articles', [])
            print(f"✅ Success! Found {len(articles3)} articles")
            if articles3:
                print(f"Sample: {articles3[0]['title'][:50]}...")
        else:
            print(f"❌ Failed: {response3.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Simple query without date restrictions
    print("\n🔍 Test 4: Simple Query - No Date Restrictions")
    url4 = "https://newsapi.org/v2/everything"
    params4 = {
        'q': 'AI OR artificial intelligence',
        'apiKey': NEWS_API_KEY,
        'language': 'en',
        'sortBy': 'popularity',
        'pageSize': 5
    }
    
    try:
        response4 = requests.get(url4, params=params4, timeout=10)
        print(f"Status: {response4.status_code}")
        
        if response4.status_code == 200:
            data4 = response4.json()
            articles4 = data4.get('articles', [])
            print(f"✅ Success! Found {len(articles4)} articles")
            if articles4:
                for i, article in enumerate(articles4[:3], 1):
                    print(f"  {i}. {article['title'][:60]}...")
        else:
            print(f"❌ Failed: {response4.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_news_api()
