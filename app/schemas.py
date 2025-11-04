"""
MorningBrief - News Briefing Application
Copyright (c) 2025 Michel Car

Type-safe data models using Pydantic for article processing pipeline.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl


class RawArticle(BaseModel):
    """Raw article from News API before processing."""
    
    title: str = Field(..., description="Article title")
    description: Optional[str] = Field(None, description="Article description")
    url: HttpUrl = Field(..., description="Article URL")
    publishedAt: Optional[str] = Field(None, description="Publication date/time")
    source: str = Field(default="Unknown", description="Source name")
    category: str = Field(..., description="Article category")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "AI Breakthrough in Healthcare",
                "description": "New AI system shows promise",
                "url": "https://example.com/article",
                "publishedAt": "2024-01-01T12:00:00Z",
                "source": "Tech News",
                "category": "technology"
            }
        }


class SelectedArticle(BaseModel):
    """Article after AI selection process."""
    
    title: str = Field(..., description="Article title")
    description: Optional[str] = Field(None, description="Article description")
    url: HttpUrl = Field(..., description="Article URL")
    publishedAt: Optional[str] = Field(None, description="Publication date/time")
    source: str = Field(default="Unknown", description="Source name")
    category: str = Field(..., description="Article category")
    selection_score: Optional[float] = Field(None, description="AI selection score if available")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "AI Breakthrough in Healthcare",
                "description": "New AI system shows promise",
                "url": "https://example.com/article",
                "publishedAt": "2024-01-01T12:00:00Z",
                "source": "Tech News",
                "category": "technology",
                "selection_score": 0.95
            }
        }
    
    @classmethod
    def from_raw_article(cls, raw_article: RawArticle, selection_score: Optional[float] = None) -> "SelectedArticle":
        """Create SelectedArticle from RawArticle."""
        return cls(
            title=raw_article.title,
            description=raw_article.description,
            url=raw_article.url,
            publishedAt=raw_article.publishedAt,
            source=raw_article.source,
            category=raw_article.category,
            selection_score=selection_score
        )


class ProcessedArticle(BaseModel):
    """Article after full processing (selection + summarization + metadata)."""
    
    title: str = Field(..., description="Article title")
    description: Optional[str] = Field(None, description="Article description")
    url: HttpUrl = Field(..., description="Article URL")
    publishedAt: Optional[str] = Field(None, description="Publication date/time")
    source: str = Field(default="Unknown", description="Source name")
    category: str = Field(..., description="Article category")
    ai_summary: Optional[str] = Field(None, description="AI-generated summary")
    selection_score: Optional[float] = Field(None, description="AI selection score if available")
    processed_at: datetime = Field(default_factory=datetime.utcnow, description="Processing timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "AI Breakthrough in Healthcare",
                "description": "New AI system shows promise",
                "url": "https://example.com/article",
                "publishedAt": "2024-01-01T12:00:00Z",
                "source": "Tech News",
                "category": "technology",
                "ai_summary": "Researchers have developed an AI system that can diagnose diseases with 95% accuracy.",
                "selection_score": 0.95,
                "processed_at": "2024-01-01T12:00:00Z"
            }
        }
    
    @classmethod
    def from_selected_article(cls, selected_article: SelectedArticle, ai_summary: Optional[str] = None) -> "ProcessedArticle":
        """Create ProcessedArticle from SelectedArticle."""
        return cls(
            title=selected_article.title,
            description=selected_article.description,
            url=selected_article.url,
            publishedAt=selected_article.publishedAt,
            source=selected_article.source,
            category=selected_article.category,
            selection_score=selected_article.selection_score,
            ai_summary=ai_summary
        )


class ProcessingResult(BaseModel):
    """Result of processing articles through the pipeline."""
    
    articles: List[ProcessedArticle] = Field(default_factory=list, description="Processed articles")
    total_count: int = Field(0, description="Total number of articles processed")
    success_count: int = Field(0, description="Number of successfully processed articles")
    error_count: int = Field(0, description="Number of articles that failed processing")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "articles": [],
                "total_count": 10,
                "success_count": 9,
                "error_count": 1,
                "processing_time": 2.5
            }
        }

