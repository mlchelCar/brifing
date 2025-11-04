"""
MorningBrief - News Briefing Application
Copyright (c) 2025 Michel Car

LLM provider factory for creating appropriate LLM clients.
"""

from typing import Optional
from app.config import settings
from app.utils.llm_client import LLMClient
from app.utils.openai_client import OpenAIClient
from app.utils.openrouter_client import OpenRouterClient
from app.utils.mock_client import MockLLMClient
import logging

logger = logging.getLogger(__name__)

# Global LLM client instance (lazy initialization)
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """
    Get the appropriate LLM client based on configuration.
    
    Priority:
    1. USE_MOCK=True -> MockLLMClient
    2. LLM_PROVIDER="openrouter" -> OpenRouterClient
    3. Default -> OpenAIClient
    
    Returns:
        LLMClient instance
    """
    global _llm_client
    
    if _llm_client is not None:
        return _llm_client
    
    # Check if mock mode is enabled
    if settings.USE_MOCK:
        logger.info("Using Mock LLM client for testing")
        _llm_client = MockLLMClient()
        return _llm_client
    
    # Check provider selection
    provider = settings.LLM_PROVIDER.lower() if hasattr(settings, 'LLM_PROVIDER') else "openai"
    
    if provider == "openrouter":
        # Check if OpenRouter API key is available
        if hasattr(settings, 'OPENROUTER_API_KEY') and settings.OPENROUTER_API_KEY:
            logger.info("Using OpenRouter LLM client")
            _llm_client = OpenRouterClient()
            return _llm_client
        else:
            logger.warning("OpenRouter API key not found, falling back to OpenAI")
            provider = "openai"
    
    # Default to OpenAI
    if provider == "openai":
        # Check if OpenAI API key is available
        if settings.OPENAI_API_KEY:
            logger.info("Using OpenAI LLM client")
            _llm_client = OpenAIClient()
            return _llm_client
        else:
            logger.warning("OpenAI API key not found, falling back to Mock")
            _llm_client = MockLLMClient()
            return _llm_client
    
    # Fallback to mock if no provider matches
    logger.warning(f"Unknown provider '{provider}', falling back to Mock")
    _llm_client = MockLLMClient()
    return _llm_client


def reset_llm_client():
    """Reset the global LLM client (useful for testing)."""
    global _llm_client
    _llm_client = None


# Note: openai_client is exported from openai_client.py for backward compatibility

