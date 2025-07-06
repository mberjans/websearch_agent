# API Reference

This document provides detailed API reference for the Modular Web Search Agent System.

## Core Models

### SearchResult

Represents a single search result item.

```python
class SearchResult(BaseModel):
    title: str = Field(..., description="The title of the search result.")
    url: HttpUrl = Field(..., description="The URL of the search result.")
    snippet: str = Field(..., description="A descriptive snippet of the result content.")
```

**Example:**
```python
result = SearchResult(
    title="Python Programming Tutorial",
    url="https://example.com/python-tutorial",
    snippet="Learn Python programming with examples and exercises."
)
```

### SearchModuleOutput

Defines the standardized output structure for all search modules.

```python
class SearchModuleOutput(BaseModel):
    source_name: str = Field(..., description="The name of the module that generated the result.")
    query: str = Field(..., description="The original search query.")
    timestamp_utc: datetime = Field(..., description="The UTC timestamp of when the search was completed.")
    execution_time_seconds: float = Field(..., description="The total execution time for the search module in seconds.")
    results: List[SearchResult] = Field(..., description="A list of search result items.")
```

**Example:**
```python
output = SearchModuleOutput(
    source_name="selenium_search",
    query="python programming",
    timestamp_utc=datetime.now(timezone.utc),
    execution_time_seconds=2.45,
    results=[result1, result2, result3]
)
```

## Search Modules

All search modules implement the same interface pattern:

### Standard Interface

```python
async def search(query: str) -> SearchModuleOutput:
    """
    Perform a search and return standardized results.
    
    Args:
        query: The search query string
        
    Returns:
        SearchModuleOutput containing results and metadata
        
    Raises:
        ScrapingError: When search execution fails
        NoResultsError: When no results are found
        ConfigurationError: When required configuration is missing
    """
```

### Module-Specific APIs

#### selenium_search

```python
from search_agent.modules.selenium_search import search

# Synchronous function
result = search("python programming")
```

**Features:**
- Traditional browser automation
- Chrome WebDriver with headless mode
- Robust element waiting and error handling
- DuckDuckGo search target

#### playwright_search

```python
from search_agent.modules.playwright_search import search
import asyncio

# Asynchronous function
result = await search("python programming")
# or
result = asyncio.run(search("python programming"))
```

**Features:**
- Modern browser automation
- Native async support
- Anti-detection measures
- Fast execution

#### brave_api_search

```python
from search_agent.modules.brave_api_search import search
import asyncio

# Requires BRAVE_API_KEY environment variable
result = await search("python programming")
```

**Configuration:**
```bash
BRAVE_API_KEY=your_api_key_here
```

**Features:**
- Commercial API access
- High-quality results
- Rate limiting handling
- JSON response parsing

#### google_cse_search

```python
from search_agent.modules.google_cse_search import search
import asyncio

# Requires GOOGLE_API_KEY and GOOGLE_CSE_ID
result = await search("python programming")
```

**Configuration:**
```bash
GOOGLE_API_KEY=your_api_key_here
GOOGLE_CSE_ID=your_cse_id_here
```

**Features:**
- Google Custom Search Engine
- Comprehensive error handling
- Quota management
- High relevance results

#### httpx_search

```python
from search_agent.modules.httpx_search import search
import asyncio

# Lightweight HTTP scraping
result = await search("python programming")
```

**Features:**
- Fast HTTP requests with httpx
- BeautifulSoup HTML parsing
- CSS selector-based extraction
- Minimal resource usage

#### scrapy_search

```python
from search_agent.modules.scrapy_search import search
import asyncio

# Framework-based scraping
result = await search("python programming")
```

**Features:**
- Full Scrapy framework integration
- Advanced scraping capabilities
- Built-in throttling and politeness
- Complex data extraction pipelines

## Orchestrator

### run_orchestration

```python
async def run_orchestration(query: str) -> SearchModuleOutput:
    """
    Orchestrates the concurrent execution of multiple search modules.
    
    Args:
        query: The search query to execute across all modules
        
    Returns:
        SearchModuleOutput containing merged and ranked results from all modules
        
    Raises:
        RuntimeError: When no search modules could be loaded or all modules fail
    """
```

**Example:**
```python
from search_agent.orchestrator import run_orchestration
import asyncio

result = await run_orchestration("machine learning")
print(f"Found {len(result.results)} unique results from {result.source_name}")
```

### merge_and_deduplicate

```python
def merge_and_deduplicate(module_outputs: List[SearchModuleOutput]) -> List[SearchResult]:
    """
    Merges results from multiple modules and de-duplicates them based on URL.
    
    Args:
        module_outputs: List of SearchModuleOutput objects from different modules
        
    Returns:
        List of unique SearchResult objects
    """
```

### rerank_results

```python
def rerank_results(results: List[SearchResult]) -> List[SearchResult]:
    """
    Re-ranks results using an initial heuristic strategy.
    
    Args:
        results: List of SearchResult objects to re-rank
        
    Returns:
        Re-ranked list of SearchResult objects
    """
```

## Evaluator

### Speed Evaluation

```python
def measure_speed(module_name: str, query: str) -> float:
    """
    Measure the execution time of a search module.
    
    Args:
        module_name: Name of the search module (e.g., 'selenium_search')
        query: The search query to execute
        
    Returns:
        The execution time in seconds
        
    Raises:
        ImportError: If the module cannot be imported
        AttributeError: If the module doesn't have a search function
    """
```

**Example:**
```python
from search_agent.evaluator import measure_speed

execution_time = measure_speed("selenium_search", "test query")
print(f"Execution time: {execution_time:.3f} seconds")
```

### Quality Evaluation

#### LLM-based Evaluation

```python
def evaluate_quality_llm(search_output: SearchModuleOutput) -> int:
    """
    Evaluate the quality and relevance of search results using an LLM.
    
    Args:
        search_output: The SearchModuleOutput object containing search results
        
    Returns:
        An integer score from 1-10 representing the quality/relevance of results
        
    Raises:
        ValueError: If API key is not configured or LLM response is invalid
        Exception: If API call fails
    """
```

**Configuration:**
```bash
OPENAI_API_KEY=your_openai_api_key_here
LLM_EVALUATOR_MODEL=gpt-4o-mini
```

**Example:**
```python
from search_agent.evaluator import evaluate_quality_llm

score = evaluate_quality_llm(search_output)
print(f"LLM Quality Score: {score}/10")
```

#### NLP-based Evaluation

```python
def evaluate_quality_nlp(search_output: SearchModuleOutput) -> float:
    """
    Evaluate the quality and relevance of search results using NLP similarity.
    
    Args:
        search_output: The SearchModuleOutput object containing search results
        
    Returns:
        A float score between 0 and 1 representing semantic similarity
        
    Raises:
        OSError: If the spaCy model is not installed
        ValueError: If no results are provided or model lacks vectors
    """
```

**Prerequisites:**
```bash
python -m spacy download en_core_web_md
```

**Example:**
```python
from search_agent.evaluator import evaluate_quality_nlp

similarity = evaluate_quality_nlp(search_output)
print(f"NLP Similarity Score: {similarity:.3f}")
```

### Database Operations

#### setup_database

```python
def setup_database() -> None:
    """
    Initialize the SQLite database for storing evaluation results.
    Creates the evaluation_log table if it doesn't exist.
    """
```

#### log_evaluation

```python
def log_evaluation(
    module_name: str,
    query: str,
    execution_time_seconds: float,
    result_count: int,
    was_successful: bool,
    llm_quality_score: Optional[int] = None,
    nlp_similarity_score: Optional[float] = None,
    error_message: Optional[str] = None,
    raw_output_json: Optional[str] = None
) -> None:
    """
    Log evaluation results to the SQLite database.
    
    Args:
        module_name: Name of the search module
        query: The search query that was executed
        execution_time_seconds: Time taken to execute the search
        result_count: Number of results returned
        was_successful: Whether the search completed without errors
        llm_quality_score: Optional LLM-based quality score (1-10)
        nlp_similarity_score: Optional NLP-based similarity score (0-1)
        error_message: Optional error message if search failed
        raw_output_json: Optional raw JSON output from the search module
    """
```

## Configuration

### Settings Class

```python
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
    
    # Google Custom Search Engine
    GOOGLE_CSE_ID: Optional[str] = None
    
    # Evaluator Database
    EVALUATION_DB_PATH: str = "evaluation_log.db"
    
    # LLM Configuration
    LLM_EVALUATOR_MODEL: str = "gpt-4o-mini"
    LLM_EVALUATOR_ENDPOINT: Optional[HttpUrl] = None
```

**Usage:**
```python
from search_agent.config import settings

print(f"Database path: {settings.EVALUATION_DB_PATH}")
print(f"Brave API configured: {bool(settings.BRAVE_API_KEY)}")
```

## Exceptions

### Custom Exception Hierarchy

```python
class SearchAgentError(Exception):
    """Base exception for the search agent system."""
    pass

class ScrapingError(SearchAgentError):
    """Raised when an error occurs during the scraping process."""
    pass

class NoResultsError(SearchAgentError):
    """Raised when a search successfully completes but yields no results."""
    pass

class ConfigurationError(SearchAgentError):
    """Raised when a required configuration (e.g., API key) is missing."""
    pass
```

**Usage:**
```python
from search_agent.core.exceptions import ScrapingError, NoResultsError

try:
    result = await search("test query")
except NoResultsError:
    print("No results found for this query")
except ScrapingError as e:
    print(f"Search failed: {e}")
```

## CLI Commands

### Orchestrator Commands

```bash
# Run orchestrated search
python -m search_agent.orchestrator search "query" [--output FILE]

# List available modules
python -m search_agent.orchestrator list-modules
```

### Individual Module Commands

```bash
# All modules support the same CLI pattern
python -m search_agent.modules.MODULE_NAME --query "search query"

# Examples:
python -m search_agent.modules.selenium_search --query "python"
python -m search_agent.modules.playwright_search --query "javascript"
python -m search_agent.modules.brave_api_search --query "api search"
```

### Evaluator Commands

```bash
# Initialize database
python -m search_agent.evaluator init-db

# Evaluate module speed
python -m search_agent.evaluator evaluate-speed MODULE_NAME "query"
```

## Type Hints

The entire codebase uses comprehensive type hints for better IDE support and code clarity:

```python
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from pydantic import HttpUrl

# Function signatures include full type information
async def search(query: str) -> SearchModuleOutput: ...
def merge_results(outputs: List[SearchModuleOutput]) -> List[SearchResult]: ...
def evaluate_quality(output: SearchModuleOutput) -> Optional[float]: ...
```

## Error Handling Patterns

### Module-Level Error Handling

```python
try:
    # Search operation
    results = perform_search(query)
except TimeoutException:
    raise ScrapingError("Search request timed out")
except ConnectionError as e:
    raise ScrapingError(f"Network connection failed: {e}")
except Exception as e:
    raise ScrapingError(f"Unexpected error: {e}")
finally:
    # Cleanup resources (browser, connections, etc.)
    cleanup_resources()
```

### Orchestrator Error Handling

```python
# Graceful degradation - continue with partial results
results = await asyncio.gather(*tasks, return_exceptions=True)
successful_results = [r for r in results if not isinstance(r, Exception)]
failed_count = len(results) - len(successful_results)

if not successful_results:
    raise RuntimeError("All search modules failed")
```

This API reference provides comprehensive documentation for all public interfaces in the system. Each function includes type hints, parameter descriptions, return values, and potential exceptions for complete clarity.