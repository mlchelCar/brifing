"""Briefing API routes."""

from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_session
from app.models import (
    CategoryRequest, 
    BriefingResponse, 
    CategoriesResponse, 
    ArticleResponse,
    NewsArticle
)
from app.config import settings
from app.services.pipeline import PipelineService
from app.services.processors.storage import StorageProcessor
from app.services.serving import SmartServingService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/categories", response_model=CategoriesResponse)
async def get_categories():
    """Get available news categories."""
    return CategoriesResponse(
        categories=settings.AVAILABLE_CATEGORIES,
        max_categories=settings.MAX_CATEGORIES
    )

@router.post("/briefing", response_model=BriefingResponse)
async def generate_briefing(
    request: CategoryRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session)
):
    """Generate a personalized news briefing for selected categories."""
    
    # Validate request
    if not request.categories:
        raise HTTPException(status_code=400, detail="At least one category must be provided")
    
    if len(request.categories) > settings.MAX_CATEGORIES:
        raise HTTPException(
            status_code=400, 
            detail=f"Maximum {settings.MAX_CATEGORIES} categories allowed"
        )
    
    # Validate categories
    invalid_categories = [cat for cat in request.categories if cat not in settings.AVAILABLE_CATEGORIES]
    if invalid_categories:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid categories: {invalid_categories}. Available categories: {settings.AVAILABLE_CATEGORIES}"
        )
    
    try:
        # Create services
        storage_processor = StorageProcessor(session=session)
        pipeline_service = PipelineService(storage_processor=storage_processor)
        serving_service = SmartServingService(
            storage_processor=storage_processor,
            pipeline_service=pipeline_service
        )
        
        # Get fresh and relevant articles using smart serving
        articles, metadata = await serving_service.get_fresh_articles(
            categories=request.categories,
            min_articles_per_category=settings.MIN_ARTICLES_PER_CATEGORY,
            auto_refresh=True
        )
        
        # If refresh was triggered, add background task
        if metadata.get("refresh_triggered") and metadata.get("refresh_categories"):
            logger.info(f"Triggering background refresh for categories: {metadata['refresh_categories']}")
            background_tasks.add_task(
                fetch_and_process_articles_background,
                metadata["refresh_categories"]
            )
        
        # Build article responses with freshness metadata
        article_responses = []
        for article in articles:
            # Get article metadata (freshness, relevance scores)
            article_metadata = await serving_service.get_article_metadata(article)
            
            article_responses.append(
                ArticleResponse(
                    title=article.title,
                    url=article.url,
                    description=article.description,
                    summary=article.summary,  # Backward compatibility
                    ai_summary=article.ai_summary,  # AI-generated summary
                    category=article.category,
                    created_at=article.created_at,
                    freshness_score=article_metadata.get("freshness_score"),
                    freshness_tier=article_metadata.get("freshness_tier"),
                    relevance_score=article_metadata.get("relevance_score"),
                    composite_score=article_metadata.get("composite_score")
                )
            )
        
        # If no articles found, trigger background refresh
        if not articles:
            logger.info(f"No fresh articles found, triggering background refresh for categories: {request.categories}")
            background_tasks.add_task(
                fetch_and_process_articles_background,
                request.categories
            )
        
        return BriefingResponse(
            categories=request.categories,
            articles=article_responses,
            total_articles=len(article_responses),
            generated_at=datetime.utcnow(),
            freshness_metadata=metadata.get("freshness_scores"),
            refresh_triggered=metadata.get("refresh_triggered", False)
        )
        
    except Exception as e:
        logger.error(f"Error generating briefing: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while generating briefing")

@router.get("/briefing/status/{categories}")
async def get_briefing_status(
    categories: str,
    session: AsyncSession = Depends(get_async_session)
):
    """Check the status of briefing generation for given categories."""
    
    category_list = categories.split(",")
    
    # Create pipeline service with storage processor
    storage_processor = StorageProcessor(session=session)
    pipeline_service = PipelineService(storage_processor=storage_processor)
    
    # Get recent articles count
    recent_articles = await pipeline_service.get_recent_articles(
        categories=category_list,
        hours=24
    )
    
    return {
        "categories": category_list,
        "articles_available": len(recent_articles),
        "last_updated": max([article.created_at for article in recent_articles]) if recent_articles else None,
        "status": "ready" if recent_articles else "processing"
    }

async def fetch_and_process_articles_background(categories: List[str]):
    """Background task to fetch and process articles."""
    try:
        logger.info(f"Starting background task to fetch articles for categories: {categories}")
        
        # Create pipeline service with database session
        async for session in get_async_session():
            storage_processor = StorageProcessor(session=session)
            pipeline_service = PipelineService(storage_processor=storage_processor)
            
            # Process articles through the pipeline
            result = await pipeline_service.process_categories(
                categories=categories,
                enable_selection=True,
                enable_summarization=True,
                enable_storage=True
            )
            
            logger.info(
                f"Background task completed: processed {result.total_count} articles "
                f"({result.success_count} successful, {result.error_count} errors)"
            )
            break
            
    except Exception as e:
        logger.error(f"Error in background task: {e}")

@router.get("/briefing/refresh")
async def refresh_briefing(background_tasks: BackgroundTasks):
    """Manually trigger a refresh of all news categories."""
    
    logger.info("Manual refresh triggered for all categories")
    
    # Add background task to refresh all categories
    background_tasks.add_task(
        fetch_and_process_articles_background,
        settings.AVAILABLE_CATEGORIES
    )
    
    return {
        "message": "Refresh started for all categories",
        "categories": settings.AVAILABLE_CATEGORIES,
        "status": "processing"
    }
