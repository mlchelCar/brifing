"""Configuration settings for the Daily Briefing application."""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # News API Configuration
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
    NEWS_API_URL: str = os.getenv("NEWS_API_URL", "https://newsapi.org/v2/everything")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./daily_briefing.db")
    
    # Application Configuration
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Scheduler Configuration
    SCHEDULER_TIMEZONE: str = os.getenv("SCHEDULER_TIMEZONE", "UTC")
    DAILY_REFRESH_HOUR: int = int(os.getenv("DAILY_REFRESH_HOUR", "6"))
    DAILY_REFRESH_MINUTE: int = int(os.getenv("DAILY_REFRESH_MINUTE", "0"))
    
    # News Configuration
    MAX_CATEGORIES: int = int(os.getenv("MAX_CATEGORIES", "10"))
    ARTICLES_PER_CATEGORY: int = int(os.getenv("ARTICLES_PER_CATEGORY", "10"))
    TOP_ARTICLES_PER_CATEGORY: int = int(os.getenv("TOP_ARTICLES_PER_CATEGORY", "3"))
    
    # Available news categories
    AVAILABLE_CATEGORIES: List[str] = [
        "technology",
        "business",
        "sports",
        "entertainment",
        "health",
        "science",
        "politics",
        "world",
        "finance",
        "environment"
    ]

    # Categories that work well with top-headlines endpoint
    TOP_HEADLINES_CATEGORIES: List[str] = [
        "technology",
        "business",
        "sports",
        "entertainment",
        "health",
        "science"
    ]
    
    def validate_settings(self) -> bool:
        """Validate that required settings are present."""
        required_settings = [
            self.OPENAI_API_KEY,
            self.NEWS_API_KEY
        ]
        return all(setting for setting in required_settings)

# Global settings instance
settings = Settings()
