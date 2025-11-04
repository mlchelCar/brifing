"""Configuration settings for the Daily Briefing application."""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""
    
    # LLM Provider Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")  # openai, openrouter, mock
    USE_MOCK: bool = os.getenv("USE_MOCK", "False").lower() == "true"
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # OpenRouter Configuration
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    
    # News API Configuration
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
    NEWS_API_URL: str = os.getenv("NEWS_API_URL", "https://newsapi.org/v2/everything")

    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_WEBHOOK_URL: str = os.getenv("TELEGRAM_WEBHOOK_URL", "")
    TELEGRAM_WEBHOOK_SECRET: str = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")

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
    
    # Freshness Configuration
    MIN_FRESHNESS_SCORE: float = float(os.getenv("MIN_FRESHNESS_SCORE", "0.3"))
    MIN_RELEVANCE_SCORE: float = float(os.getenv("MIN_RELEVANCE_SCORE", "0.5"))
    MIN_ARTICLES_PER_CATEGORY: int = int(os.getenv("MIN_ARTICLES_PER_CATEGORY", "3"))
    AUTO_REFRESH_FRESHNESS_THRESHOLD: float = float(os.getenv("AUTO_REFRESH_FRESHNESS_THRESHOLD", "0.4"))
    
    # Ranking weights
    FRESHNESS_WEIGHT: float = float(os.getenv("FRESHNESS_WEIGHT", "0.4"))
    RELEVANCE_WEIGHT: float = float(os.getenv("RELEVANCE_WEIGHT", "0.4"))
    SELECTION_WEIGHT: float = float(os.getenv("SELECTION_WEIGHT", "0.2"))
    
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
            self.NEWS_API_KEY,
            self.TELEGRAM_BOT_TOKEN
        ]
        return all(setting for setting in required_settings)

# Global settings instance
settings = Settings()
