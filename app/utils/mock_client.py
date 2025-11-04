"""
MorningBrief - News Briefing Application
Copyright (c) 2025 Michel Car

Mock LLM client for testing without API calls.
"""

import json
import asyncio
from typing import List, Dict, Any, Optional
from app.utils.llm_client import LLMClient
import logging

logger = logging.getLogger(__name__)


class MockLLMClient(LLMClient):
    """Mock LLM client for testing without API calls."""
    
    def __init__(self, simulate_delay: bool = True, delay_seconds: float = 0.1):
        """
        Initialize mock LLM client.
        
        Args:
            simulate_delay: Whether to simulate API delay
            delay_seconds: Delay in seconds to simulate
        """
        self.simulate_delay = simulate_delay
        self.delay_seconds = delay_seconds
    
    async def _make_request(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Make a mock request with simulated delay."""
        if self.simulate_delay:
            await asyncio.sleep(self.delay_seconds)
        
        # Extract the user prompt from messages
        user_message = next((msg["content"] for msg in messages if msg["role"] == "user"), "")
        
        # Generate mock response based on prompt type
        if "select" in user_message.lower() or "curator" in user_message.lower():
            # Mock article selection response
            # Extract number of articles from prompt
            import re
            match = re.search(r'(\d+)\s+.*?\s+articles', user_message)
            if match:
                total_articles = int(match.group(1))
                # Return first few indices as selected
                selected_count = min(3, total_articles)
                selected_indices = list(range(1, selected_count + 1))
                return json.dumps(selected_indices)
            else:
                # Default: select first 3
                return json.dumps([1, 2, 3])
        else:
            # Mock summary response
            return "This is a mock AI-generated summary of the article. It provides key insights and important information about the news story in 2-3 concise sentences."
    
    async def select_top_articles(
        self, 
        articles: List[Dict[str, Any]], 
        category: str, 
        top_count: int = 3
    ) -> List[Dict[str, Any]]:
        """Mock article selection - returns first N articles."""
        
        if len(articles) <= top_count:
            return articles
        
        # Simulate AI selection by returning first N articles
        # In real scenario, this would use AI to select based on importance
        selected = articles[:top_count]
        
        logger.debug(f"Mock: Selected {len(selected)} articles from {len(articles)} for category: {category}")
        return selected
    
    async def summarize_article(
        self, 
        title: str, 
        description: str, 
        url: str, 
        category: str
    ) -> str:
        """Generate a mock summary for an article."""
        
        # Generate deterministic mock summary based on title and description
        if description:
            # Use first part of description as mock summary
            words = description.split()[:30]  # First 30 words
            summary = " ".join(words)
            if len(description) > len(summary):
                summary += "..."
        else:
            summary = f"Mock summary for {category} article: {title}. This article discusses important developments in the field."
        
        logger.debug(f"Mock: Generated summary for article: {title[:50]}...")
        return summary

