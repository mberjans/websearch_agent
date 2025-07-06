"""Core data models for the web search agent system.

This module defines the standardized data structures used throughout the system
to ensure consistent JSON I/O and type safety.
"""

from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, HttpUrl


class SearchResult(BaseModel):
    """Represents a single search result item."""
    
    title: str = Field(..., description="The title of the search result.")
    url: HttpUrl = Field(..., description="The URL of the search result.")
    snippet: str = Field(..., description="A descriptive snippet of the result content.")


class SearchModuleOutput(BaseModel):
    """Defines the standardized output structure for all search modules."""
    
    source_name: str = Field(..., description="The name of the module that generated the result (e.g., 'selenium_search').")
    query: str = Field(..., description="The original search query.")
    timestamp_utc: datetime = Field(..., description="The UTC timestamp of when the search was completed.")
    execution_time_seconds: float = Field(..., description="The total execution time for the search module in seconds.")
    results: List[SearchResult] = Field(..., description="A list of search result items.")