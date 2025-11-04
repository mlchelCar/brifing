"""
MorningBrief - News Briefing Application
Copyright (c) 2025 Michel Car

Summarization processor for AI-based article summarization.
"""

import asyncio
from typing import List
from app.services.processors.base import Processor, ProcessingError
from app.schemas import SelectedArticle, ProcessedArticle
from app.utils.llm_provider import get_llm_client
import logging

logger = logging.getLogger(__name__)


class SummarizationProcessor(Processor[List[SelectedArticle], List[ProcessedArticle]]):
    """Processor for generating AI summaries of articles."""
    
    def __init__(self, max_concurrent: int = 5):
        """
        Initialize summarization processor.
        
        Args:
            max_concurrent: Maximum number of concurrent summarization requests
        """
        super().__init__("SummarizationProcessor")
        self.max_concurrent = max_concurrent
    
    async def process(self, input_data: List[SelectedArticle]) -> List[ProcessedArticle]:
        """
        Process selected articles and generate summaries.
        
        Args:
            input_data: List of selected articles to summarize
            
        Returns:
            List of processed articles with AI summaries
            
        Raises:
            ProcessingError: If summarization fails
        """
        if not self.is_enabled():
            logger.warning(f"{self.name} is disabled, returning articles without summaries")
            return [
                ProcessedArticle.from_selected_article(article, ai_summary=None)
                for article in input_data
            ]
        
        if not input_data:
            return []
        
        try:
            # Create semaphore to limit concurrent requests
            semaphore = asyncio.Semaphore(self.max_concurrent)
            
            async def summarize_with_semaphore(article: SelectedArticle) -> ProcessedArticle:
                async with semaphore:
                    try:
                        llm_client = get_llm_client()
                        summary = await llm_client.summarize_article(
                            title=article.title,
                            description=article.description or '',
                            url=str(article.url),
                            category=article.category
                        )
                        logger.info(f"Generated summary for article: {article.title[:50]}...")
                        return ProcessedArticle.from_selected_article(article, ai_summary=summary)
                    except Exception as e:
                        logger.error(f"Failed to summarize article '{article.title}': {e}")
                        # Fallback: return article without summary
                        return ProcessedArticle.from_selected_article(article, ai_summary=None)
            
            # Process articles concurrently
            tasks = [summarize_with_semaphore(article) for article in input_data]
            processed_articles = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and return successful results
            results = []
            for i, result in enumerate(processed_articles):
                if isinstance(result, Exception):
                    logger.error(f"Error summarizing article {i}: {result}")
                    # Add article without summary as fallback
                    article = input_data[i]
                    results.append(
                        ProcessedArticle.from_selected_article(article, ai_summary=None)
                    )
                else:
                    results.append(result)
            
            logger.info(f"{self.name} processed {len(results)} articles")
            return results
            
        except Exception as e:
            logger.error(f"{self.name} failed to process articles: {e}")
            raise ProcessingError(
                f"Failed to summarize articles: {str(e)}",
                self.name,
                original_error=e
            )

