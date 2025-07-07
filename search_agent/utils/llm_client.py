"""Utility functions for LLM client configuration.

This module provides functions to create and configure LLM clients
based on application settings.
"""

import logging
from typing import Optional, Dict, Any

from openai import AsyncOpenAI

from search_agent.config import settings
from search_agent.core.exceptions import SearchAgentError

# Configure logging
logger = logging.getLogger(__name__)

def get_llm_client() -> AsyncOpenAI:
    """
    Returns an appropriately configured LLM client based on application settings.
    
    If USE_OPENROUTER is True and OPENROUTER_API_KEY is available, configures the client
    to use OpenRouter. Otherwise, falls back to using OPENAI_API_KEY directly.
    
    Returns:
        AsyncOpenAI: Configured OpenAI client
        
    Raises:
        SearchAgentError: If no valid API key is available
    """
    # Check if we should use OpenRouter
    if settings.USE_OPENROUTER and settings.OPENROUTER_API_KEY:
        logger.info("Using OpenRouter for LLM API calls")
        return AsyncOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
            default_headers={
                "HTTP-Referer": settings.OPENROUTER_REFERER,  # Required for OpenRouter
            }
        )
    
    # Fall back to direct OpenAI API
    elif settings.OPENAI_API_KEY:
        logger.info("Using OpenAI API directly for LLM API calls")
        return AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    # No valid API key available
    else:
        raise SearchAgentError("No valid API key found. Please set either OPENROUTER_API_KEY or OPENAI_API_KEY in your .env file.")


def get_model_name(default_model: str) -> str:
    """
    Returns the appropriate model name based on whether we're using OpenRouter or not.
    
    Args:
        default_model: The default model name to use (e.g., "gpt-4o-mini")
        
    Returns:
        str: The model name to use with the configured client
    """
    # For OpenRouter, we can use the same model names as OpenAI
    # If specific OpenRouter model mapping is needed, it can be added here
    return default_model