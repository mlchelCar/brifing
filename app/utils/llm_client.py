"""
MorningBrief - News Briefing Application
Copyright (c) 2025 Michel Car

Abstract base class for LLM clients (OpenAI, OpenRouter, Mock).
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    async def select_top_articles(
        self, 
        articles: List[Dict[str, Any]], 
        category: str, 
        top_count: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Select the top articles from a list using AI.
        
        Args:
            articles: List of article dictionaries
            category: News category
            top_count: Number of top articles to select
            
        Returns:
            List of selected article dictionaries
        """
        pass
    
    @abstractmethod
    async def summarize_article(
        self, 
        title: str, 
        description: str, 
        url: str, 
        category: str
    ) -> str:
        """
        Generate a summary for an article.
        
        Args:
            title: Article title
            description: Article description
            url: Article URL
            category: Article category
            
        Returns:
            Generated summary string
        """
        pass
    
    @abstractmethod
    async def _make_request(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Make a request to the LLM API.
        
        Args:
            messages: List of message dictionaries
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        pass

