"""
MorningBrief - News Briefing Application
Copyright (c) 2025 Michel Car

OpenRouter API client for LLM integration.
"""

import json
import asyncio
import httpx
from typing import List, Dict, Any, Optional
from app.utils.llm_client import LLMClient
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class OpenRouterClient(LLMClient):
    """OpenRouter API client wrapper with error handling and rate limiting."""
    
    def __init__(self):
        """Initialize OpenRouter client."""
        self.api_key = settings.OPENROUTER_API_KEY
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = settings.OPENROUTER_MODEL or "openai/gpt-4o-mini"
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        self.timeout = 30  # seconds
    
    async def _make_request(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Make a request to OpenRouter API with retry logic."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://morningbrief.app",  # Optional: for tracking
            "X-Title": "MorningBrief",  # Optional: for tracking
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        self.api_url,
                        headers=headers,
                        json=payload
                    )
                    response.raise_for_status()
                    
                    data = response.json()
                    return data["choices"][0]["message"]["content"].strip()
            
            except httpx.HTTPError as e:
                logger.warning(f"OpenRouter request attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    logger.error(f"OpenRouter request failed after {self.max_retries} attempts")
                    raise e
            except Exception as e:
                logger.warning(f"OpenRouter request attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    logger.error(f"OpenRouter request failed after {self.max_retries} attempts")
                    raise e
    
    async def select_top_articles(
        self, 
        articles: List[Dict[str, Any]], 
        category: str, 
        top_count: int = 3
    ) -> List[Dict[str, Any]]:
        """Use OpenRouter to select the most important articles from a list."""
        
        if len(articles) <= top_count:
            return articles
        
        # Prepare articles for AI selection
        articles_text = ""
        for i, article in enumerate(articles, 1):
            articles_text += f"{i}. Title: {article.get('title', 'N/A')}\n"
            articles_text += f"   Description: {article.get('description', 'N/A')}\n"
            articles_text += f"   URL: {article.get('url', 'N/A')}\n\n"
        
        prompt = f"""
You are a news curator. From the following {len(articles)} {category} news articles, 
select the {top_count} most important, newsworthy, and recent articles.

Consider:
- Breaking news and recent developments
- Impact and significance
- Relevance to the {category} category
- Credibility of the source

Articles:
{articles_text}

Respond with ONLY a JSON array containing the numbers of the selected articles.
Example: [1, 3, 7]
"""
        
        messages = [
            {"role": "system", "content": "You are a professional news curator who selects the most important and relevant news articles."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self._make_request(messages, temperature=0.3)
            
            # Parse the response to get selected article indices
            selected_indices = json.loads(response)
            
            # Validate and convert to 0-based indices
            selected_articles = []
            for idx in selected_indices:
                if 1 <= idx <= len(articles):
                    selected_articles.append(articles[idx - 1])
                    if len(selected_articles) >= top_count:
                        break
            
            return selected_articles[:top_count]
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse OpenRouter selection response: {e}")
            # Fallback: return first N articles
            return articles[:top_count]
    
    async def summarize_article(
        self, 
        title: str, 
        description: str, 
        url: str, 
        category: str
    ) -> str:
        """Generate a 2-3 sentence summary of an article."""
        
        prompt = f"""
Summarize this {category} news article in exactly 2-3 concise sentences.
Focus on the key facts, impact, and significance.

Title: {title}
Description: {description}
URL: {url}

Provide a clear, informative summary that captures the essence of the article.
"""
        
        messages = [
            {"role": "system", "content": "You are a professional news summarizer who creates concise, informative summaries."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            summary = await self._make_request(messages, temperature=0.5, max_tokens=150)
            return summary
        except Exception as e:
            logger.error(f"Failed to generate summary for article: {title}. Error: {e}")
            # Fallback to description or title
            return description if description else f"News article: {title}"

