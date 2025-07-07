"""Configuration management for the web search agent system.

This module provides centralized configuration management using Pydantic BaseSettings
to load settings from environment variables and .env files.
"""

from typing import Optional
from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized application configuration.
    Settings are loaded from environment variables or a .env file.
    """
    
    # API Keys and Secrets
    BRAVE_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    
    # Google Custom Search Engine
    GOOGLE_CSE_ID: Optional[str] = None
    
    # Evaluator Database
    EVALUATION_DB_PATH: str = "evaluation_log.db"
    
    # LLM Configuration
    LLM_EVALUATOR_MODEL: str = "gpt-4o-mini"
    LLM_SYNTHESIZER_MODEL: str = "gpt-4o-mini"
    
    # OpenRouter Configuration
    USE_OPENROUTER: bool = True
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_REFERER: str = "https://websearch-agent.example.com"
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'  # Ignore extra fields from .env file
    )


# Instantiate a single settings object for the entire application
settings = Settings()