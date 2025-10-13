"""
MorningBrief - News Briefing Application
Copyright (c) 2025 Michel Car

Licensed under the MIT License. See LICENSE file for details.

Database models for the Daily Briefing application.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, BigInteger, JSON
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from typing import List

Base = declarative_base()

class NewsArticle(Base):
    """SQLAlchemy model for news articles."""
    
    __tablename__ = "news_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class TelegramUser(Base):
    """SQLAlchemy model for Telegram users."""

    __tablename__ = "telegram_users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, nullable=False, unique=True, index=True)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    language_code = Column(String(10), nullable=True)
    is_active = Column(Boolean, default=True)
    selected_categories = Column(JSON, nullable=True)  # List of selected categories
    daily_time = Column(String(10), nullable=True)  # Time for daily briefing (HH:MM format)
    timezone = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_interaction = Column(DateTime, default=datetime.utcnow)


# Pydantic models for API requests/responses

class CategoryRequest(BaseModel):
    """Request model for category selection."""
    categories: List[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "categories": ["technology", "business", "politics"]
            }
        }

class ArticleResponse(BaseModel):
    """Response model for individual articles."""
    title: str
    url: str
    description: Optional[str] = None
    summary: Optional[str] = None
    category: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class BriefingResponse(BaseModel):
    """Response model for briefing endpoint."""
    categories: List[str]
    articles: List[ArticleResponse]
    total_articles: int
    generated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "categories": ["technology", "business"],
                "articles": [
                    {
                        "title": "AI Breakthrough in Healthcare",
                        "url": "https://example.com/ai-healthcare",
                        "description": "New AI system shows promise in medical diagnosis",
                        "summary": "Researchers have developed an AI system that can diagnose diseases with 95% accuracy. The system uses machine learning to analyze medical images and patient data.",
                        "category": "technology",
                        "created_at": "2024-01-01T12:00:00Z"
                    }
                ],
                "total_articles": 1,
                "generated_at": "2024-01-01T12:00:00Z"
            }
        }

class CategoriesResponse(BaseModel):
    """Response model for available categories."""
    categories: List[str]
    max_categories: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "categories": ["technology", "business", "politics", "sports"],
                "max_categories": 10
            }
        }
