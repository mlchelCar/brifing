"""
MorningBrief - News Briefing Application
Copyright (c) 2025 Michel Car

Pipeline service for orchestrating decoupled processors.
"""

import time
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.processors.base import Processor, ProcessingError
from app.services.processors.selection import SelectionProcessor
from app.services.processors.summarization import SummarizationProcessor
from app.services.processors.storage import StorageProcessor
from app.schemas import RawArticle, SelectedArticle, ProcessedArticle, ProcessingResult
from app.models import NewsArticle
import logging

logger = logging.getLogger(__name__)


class PipelineService:
    """Service for orchestrating the news processing pipeline."""
    
    def __init__(
        self,
        selection_processor: Optional[SelectionProcessor] = None,
        summarization_processor: Optional[SummarizationProcessor] = None,
        storage_processor: Optional[StorageProcessor] = None
    ):
        """
        Initialize pipeline service.
        
        Args:
            selection_processor: Processor for article selection (defaults to new instance)
            summarization_processor: Processor for article summarization (defaults to new instance)
            storage_processor: Processor for database storage (must be provided with session)
        """
        self.selection_processor = selection_processor or SelectionProcessor()
        self.summarization_processor = summarization_processor or SummarizationProcessor()
        self.storage_processor = storage_processor
    
    async def process_categories(
        self,
        categories: List[str],
        enable_selection: bool = True,
        enable_summarization: bool = True,
        enable_storage: bool = True
    ) -> ProcessingResult:
        """
        Process articles for multiple categories through the pipeline.
        
        Args:
            categories: List of categories to process
            enable_selection: Whether to enable selection processor
            enable_summarization: Whether to enable summarization processor
            enable_storage: Whether to enable storage processor
            
        Returns:
            ProcessingResult with processed articles and statistics
        """
        start_time = time.time()
        
        # Configure processors
        if enable_selection:
            self.selection_processor.enable()
        else:
            self.selection_processor.disable()
        
        if enable_summarization:
            self.summarization_processor.enable()
        else:
            self.summarization_processor.disable()
        
        if enable_storage and self.storage_processor:
            self.storage_processor.enable()
        elif self.storage_processor:
            self.storage_processor.disable()
        
        try:
            # Step 1: Fetch and select articles
            logger.info(f"Starting pipeline processing for categories: {categories}")
            category_articles = await self.selection_processor.select_articles_for_categories(categories)
            
            # Flatten all articles from all categories
            all_selected_articles: List[SelectedArticle] = []
            for category, articles in category_articles.items():
                all_selected_articles.extend(articles)
            
            if not all_selected_articles:
                logger.warning("No articles selected for processing")
                return ProcessingResult(
                    articles=[],
                    total_count=0,
                    success_count=0,
                    error_count=0,
                    processing_time=time.time() - start_time
                )
            
            # Step 2: Summarize articles
            processed_articles = await self.summarization_processor.process(all_selected_articles)
            
            # Step 3: Save to database (if enabled and processor available)
            saved_articles: List[NewsArticle] = []
            if enable_storage and self.storage_processor:
                saved_articles = await self.storage_processor.process(processed_articles)
            
            # Count successes and errors
            success_count = len([a for a in processed_articles if a.ai_summary])
            error_count = len(processed_articles) - success_count
            
            processing_time = time.time() - start_time
            
            logger.info(
                f"Pipeline completed: {len(processed_articles)} articles processed "
                f"({success_count} successful, {error_count} errors) in {processing_time:.2f}s"
            )
            
            return ProcessingResult(
                articles=processed_articles,
                total_count=len(processed_articles),
                success_count=success_count,
                error_count=error_count,
                processing_time=processing_time
            )
            
        except ProcessingError as e:
            logger.error(f"Pipeline processing error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected pipeline error: {e}")
            raise ProcessingError(
                f"Pipeline processing failed: {str(e)}",
                "PipelineService",
                original_error=e
            )
    
    async def process_articles(
        self,
        raw_articles: List[RawArticle],
        enable_selection: bool = True,
        enable_summarization: bool = True,
        enable_storage: bool = True
    ) -> ProcessingResult:
        """
        Process a list of raw articles through the pipeline.
        
        Args:
            raw_articles: List of raw articles to process
            enable_selection: Whether to enable selection processor
            enable_summarization: Whether to enable summarization processor
            enable_storage: Whether to enable storage processor
            
        Returns:
            ProcessingResult with processed articles and statistics
        """
        start_time = time.time()
        
        # Configure processors
        if enable_selection:
            self.selection_processor.enable()
        else:
            self.selection_processor.disable()
        
        if enable_summarization:
            self.summarization_processor.enable()
        else:
            self.summarization_processor.disable()
        
        if enable_storage and self.storage_processor:
            self.storage_processor.enable()
        elif self.storage_processor:
            self.storage_processor.disable()
        
        try:
            # Step 1: Select articles
            selected_articles = await self.selection_processor.process(raw_articles)
            
            # Step 2: Summarize articles
            processed_articles = await self.summarization_processor.process(selected_articles)
            
            # Step 3: Save to database (if enabled and processor available)
            saved_articles: List[NewsArticle] = []
            if enable_storage and self.storage_processor:
                saved_articles = await self.storage_processor.process(processed_articles)
            
            # Count successes and errors
            success_count = len([a for a in processed_articles if a.ai_summary])
            error_count = len(processed_articles) - success_count
            
            processing_time = time.time() - start_time
            
            logger.info(
                f"Pipeline completed: {len(processed_articles)} articles processed "
                f"({success_count} successful, {error_count} errors) in {processing_time:.2f}s"
            )
            
            return ProcessingResult(
                articles=processed_articles,
                total_count=len(processed_articles),
                success_count=success_count,
                error_count=error_count,
                processing_time=processing_time
            )
            
        except ProcessingError as e:
            logger.error(f"Pipeline processing error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected pipeline error: {e}")
            raise ProcessingError(
                f"Pipeline processing failed: {str(e)}",
                "PipelineService",
                original_error=e
            )
    
    async def get_recent_articles(
        self,
        categories: List[str],
        hours: int = 24
    ) -> List[NewsArticle]:
        """
        Get recent articles from database.
        
        Args:
            categories: List of categories to retrieve
            hours: Number of hours to look back
            
        Returns:
            List of recent NewsArticle objects
        """
        if not self.storage_processor:
            raise ValueError("Storage processor not available")
        
        return await self.storage_processor.get_recent_articles(categories, hours)

