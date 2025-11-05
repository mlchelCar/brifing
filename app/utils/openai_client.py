"""OpenAI client utility for ChatGPT-4o-mini integration."""

import json
import asyncio
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from app.config import settings
from app.utils.llm_client import LLMClient
import logging

logger = logging.getLogger(__name__)

class OpenAIClient(LLMClient):
    """OpenAI client wrapper with error handling and rate limiting."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: Optional API key. If not provided, uses settings.OPENAI_API_KEY
        """
        api_key = api_key or settings.OPENAI_API_KEY
        # Allow initialization without API key (will fail on first request)
        if api_key:
            self.client = AsyncOpenAI(api_key=api_key)
        else:
            self.client = None
        self.model = settings.OPENAI_MODEL
        self.max_retries = 3
        self.retry_delay = 1  # seconds
    
    async def _make_request(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Make a request to OpenAI with retry logic."""
        if not self.client:
            raise ValueError("OpenAI client not initialized. API key is required.")
        
        for attempt in range(self.max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content.strip()
            
            except Exception as e:
                logger.warning(f"OpenAI request attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    logger.error(f"OpenAI request failed after {self.max_retries} attempts")
                    raise e
    
    async def select_top_articles(
        self, 
        articles: List[Dict[str, Any]], 
        category: str, 
        top_count: int = 3
    ) -> List[Dict[str, Any]]:
        """Use ChatGPT to select the most important articles from a list."""
        
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
            logger.error(f"Failed to parse AI selection response: {e}")
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

# For backward compatibility, export openai_client
# Note: This is instantiated at module level, which should be fine
# as long as we don't import from llm_provider here
# New code should use get_llm_client() from llm_provider for provider flexibility
try:
    openai_client = OpenAIClient()
except Exception as e:
    logger.warning(f"Failed to initialize OpenAI client at module level: {e}")
    # Set to None - will be handled by provider factory
    openai_client = None
