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
from app.services.selection import news_selection_service
from app.services.summarizer import summarizer_service
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
        # First, try to get recent articles from database
        recent_articles = await summarizer_service.get_recent_articles(
            categories=request.categories,
            session=session,
            hours=24
        )
        
        # If we have recent articles, return them
        if recent_articles:
            logger.info(f"Returning {len(recent_articles)} recent articles from database")
            
            article_responses = [
                ArticleResponse(
                    title=article.title,
                    url=article.url,
                    description=article.description,
                    summary=article.summary,
                    category=article.category,
                    created_at=article.created_at
                )
                for article in recent_articles
            ]
            
            return BriefingResponse(
                categories=request.categories,
                articles=article_responses,
                total_articles=len(article_responses),
                generated_at=datetime.utcnow()
            )
        
        # If no recent articles, fetch new ones
        logger.info(f"No recent articles found, fetching new articles for categories: {request.categories}")
        
        # Add background task to fetch and process new articles
        background_tasks.add_task(
            fetch_and_process_articles_background,
            request.categories
        )
        
        # Return empty response with message
        return BriefingResponse(
            categories=request.categories,
            articles=[],
            total_articles=0,
            generated_at=datetime.utcnow()
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
    
    # Get recent articles count
    recent_articles = await summarizer_service.get_recent_articles(
        categories=category_list,
        session=session,
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
        
        # Fetch articles for all categories
        category_articles = await news_selection_service.select_articles_for_categories(categories)
        
        # Process and save articles
        if category_articles:
            saved_articles = await summarizer_service.process_and_save_articles(category_articles)
            logger.info(f"Background task completed: processed {len(saved_articles)} articles")
        else:
            logger.warning("No articles found in background task")
            
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
