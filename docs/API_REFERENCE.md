# API Reference

This document provides detailed API reference for the Modular Web Search Agent System.

## Module Usage

The websearch agent can be imported and used as a module in other Python scripts. This section provides comprehensive examples and best practices for integrating the agent into your applications.

### Basic Module Usage

#### Simple Question Answering

```python
import asyncio
from search_agent.config import Configuration, SearchConfig, LLMConfig
from search_agent.answer_orchestrator import orchestrate_answer_generation

async def get_answer(question: str):
    """Get a comprehensive answer to a question using web search."""
    
    # Create configuration
    config = Configuration(
        query=question,
        search=SearchConfig(
            provider="selenium",  # Use only Selenium for speed
            max_results=10,
            max_urls=3
        ),
        llm=LLMConfig(
            provider="openrouter",
            model="openrouter/cypher-alpha:free"
        )
    )
    
    # Run the search and answer generation
    result = await orchestrate_answer_generation(
        query=config.query,
        num_links_to_parse=config.search.max_urls,
        config=config
    )
    
    return result

# Usage
async def main():
    result = await get_answer("What is machine learning?")
    print(f"Answer: {result['synthesized_answer']['answer']}")
    print(f"Sources: {result['source_urls']}")
    print(f"Execution time: {result['execution_time_seconds']:.2f}s")

# Run the async function
asyncio.run(main())
```

#### Synchronous Wrapper

```python
import asyncio
from search_agent.config import Configuration, SearchConfig, LLMConfig
from search_agent.answer_orchestrator import orchestrate_answer_generation

def get_answer_sync(question: str, max_sources: int = 3):
    """Synchronous wrapper for getting answers."""
    
    config = Configuration(
        query=question,
        search=SearchConfig(
            provider="selenium",
            max_results=10,
            max_urls=max_sources
        ),
        llm=LLMConfig(
            provider="openrouter",
            model="openrouter/cypher-alpha:free"
        )
    )
    
    return asyncio.run(orchestrate_answer_generation(
        query=config.query,
        num_links_to_parse=config.search.max_urls,
        config=config
    ))

# Usage
result = get_answer_sync("What is climate change?")
print(result['synthesized_answer']['answer'])
```

### Advanced Configuration

#### Multiple Search Providers

```python
from search_agent.config import Configuration, SearchConfig, LLMConfig

# Use multiple providers for comprehensive results
config = Configuration(
    query="What is artificial intelligence?",
    search=SearchConfig(
        provider="selenium,brave",  # Use Selenium and Brave API
        max_results=15,
        max_urls=5,
        timeout=45
    ),
    llm=LLMConfig(
        provider="openrouter",
        model="openrouter/cypher-alpha:free",
        temperature=0.1,
        max_tokens=1024
    )
)
```

#### Custom LLM Configuration

```python
from search_agent.config import Configuration, SearchConfig, LLMConfig

# Use different LLM providers
config = Configuration(
    query="Explain quantum computing",
    search=SearchConfig(provider="all"),  # Use all available providers
    llm=LLMConfig(
        provider="openai",  # Use OpenAI instead of OpenRouter
        model="gpt-4o-mini",
        temperature=0.0,  # More deterministic
        max_tokens=2048,  # Longer responses
        evaluation=True  # Enable quality evaluation
    )
)
```

### Batch Processing

#### Process Multiple Questions

```python
import asyncio
from typing import List, Dict, Any
from search_agent.config import Configuration, SearchConfig, LLMConfig
from search_agent.answer_orchestrator import orchestrate_answer_generation

async def process_questions(questions: List[str]) -> List[Dict[str, Any]]:
    """Process multiple questions and return results."""
    
    results = []
    
    for question in questions:
        try:
            config = Configuration(
                query=question,
                search=SearchConfig(
                    provider="selenium",
                    max_results=10,
                    max_urls=3
                ),
                llm=LLMConfig(
                    provider="openrouter",
                    model="openrouter/cypher-alpha:free"
                )
            )
            
            result = await orchestrate_answer_generation(
                query=config.query,
                num_links_to_parse=config.search.max_urls,
                config=config
            )
            
            results.append({
                'question': question,
                'answer': result['synthesized_answer']['answer'],
                'sources': result['source_urls'],
                'execution_time': result['execution_time_seconds'],
                'quality_scores': result.get('evaluation_results', {})
            })
            
        except Exception as e:
            results.append({
                'question': question,
                'error': str(e),
                'answer': None,
                'sources': [],
                'execution_time': 0,
                'quality_scores': {}
            })
    
    return results

# Usage
questions = [
    "What is machine learning?",
    "How do vaccines work?",
    "What is renewable energy?"
]

async def main():
    results = await process_questions(questions)
    
    for result in results:
        print(f"Question: {result['question']}")
        if result['answer']:
            print(f"Answer: {result['answer'][:200]}...")
            print(f"Time: {result['execution_time']:.2f}s")
        else:
            print(f"Error: {result['error']}")
        print("-" * 50)

asyncio.run(main())
```

### Direct Module Usage

#### Using Individual Search Modules

```python
import asyncio
from search_agent.modules.selenium_search import search as selenium_search
from search_agent.modules.brave_api_search import search as brave_search
from search_agent.modules.web_content_extractor import extract_content

async def custom_search_pipeline(query: str):
    """Custom search pipeline using individual modules."""
    
    # Get search results from multiple sources
    selenium_results = await asyncio.to_thread(selenium_search, query)
    brave_results = await brave_search(query)
    
    # Extract content from top results
    all_urls = []
    for result in selenium_results.results[:3]:
        all_urls.append(str(result.url))
    for result in brave_results.results[:2]:
        all_urls.append(str(result.url))
    
    # Extract content from URLs
    content_results = []
    for url in all_urls:
        try:
            content = await extract_content(url)
            content_results.append(content)
        except Exception as e:
            print(f"Failed to extract content from {url}: {e}")
    
    return {
        'selenium_results': selenium_results,
        'brave_results': brave_results,
        'extracted_content': content_results
    }

# Usage
result = asyncio.run(custom_search_pipeline("Python programming"))
print(f"Selenium found {len(result['selenium_results'].results)} results")
print(f"Brave found {len(result['brave_results'].results)} results")
```

#### Using the LLM Client Directly

```python
from search_agent.utils.llm_client import LLMClient
from search_agent.config import LLMConfig

async def use_llm_directly():
    """Use the LLM client directly for custom processing."""
    
    # Create LLM configuration
    llm_config = LLMConfig(
        provider="openrouter",
        model="openrouter/cypher-alpha:free",
        temperature=0.1,
        max_tokens=1024
    )
    
    # Initialize LLM client
    llm_client = LLMClient(llm_config)
    
    # Use the client directly
    response = await llm_client.generate_response(
        prompt="Explain the concept of machine learning in simple terms.",
        system_prompt="You are a helpful AI assistant that explains complex topics simply."
    )
    
    return response

# Usage
response = asyncio.run(use_llm_directly())
print(response)
```

### Error Handling and Robustness

#### Comprehensive Error Handling

```python
import asyncio
from typing import Optional, Dict, Any
from search_agent.config import Configuration, SearchConfig, LLMConfig
from search_agent.answer_orchestrator import orchestrate_answer_generation
from search_agent.core.exceptions import ScrapingError, NoResultsError

async def robust_answer_generation(
    question: str,
    fallback_providers: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Robust answer generation with fallback providers."""
    
    if fallback_providers is None:
        fallback_providers = ["selenium", "brave", "httpx"]
    
    for provider in fallback_providers:
        try:
            config = Configuration(
                query=question,
                search=SearchConfig(
                    provider=provider,
                    max_results=10,
                    max_urls=3,
                    timeout=30
                ),
                llm=LLMConfig(
                    provider="openrouter",
                    model="openrouter/cypher-alpha:free"
                )
            )
            
            result = await orchestrate_answer_generation(
                query=config.query,
                num_links_to_parse=config.search.max_urls,
                config=config
            )
            
            return {
                'success': True,
                'provider_used': provider,
                'result': result
            }
            
        except (ScrapingError, NoResultsError) as e:
            print(f"Provider {provider} failed: {e}")
            continue
        except Exception as e:
            print(f"Unexpected error with {provider}: {e}")
            continue
    
    return {
        'success': False,
        'error': 'All providers failed',
        'result': None
    }

# Usage
result = asyncio.run(robust_answer_generation("What is blockchain?"))
if result['success']:
    print(f"Answer using {result['provider_used']}: {result['result']['synthesized_answer']['answer']}")
else:
    print(f"Failed to get answer: {result['error']}")
```

### Configuration Management

#### Loading Configuration from File

```python
from search_agent.config import Configuration

# Load configuration from YAML file
config = Configuration.from_file("config/my_config.yaml", query="What is AI?")

# Use the configuration
result = asyncio.run(orchestrate_answer_generation(
    query=config.query,
    num_links_to_parse=config.search.max_urls,
    config=config
))
```

#### Environment-Based Configuration

```python
import os
from search_agent.config import Configuration

# Set environment variables
os.environ["SEARCH_PROVIDER"] = "selenium"
os.environ["LLM_PROVIDER"] = "openrouter"
os.environ["DEFAULT_LLM_MODEL"] = "openrouter/cypher-alpha:free"

# Create configuration from environment
config = Configuration.from_env("What is machine learning?")

# Use the configuration
result = asyncio.run(orchestrate_answer_generation(
    query=config.query,
    num_links_to_parse=config.search.max_urls,
    config=config
))
```

### Performance Optimization

#### Caching Results

```python
import asyncio
import json
import hashlib
from pathlib import Path
from search_agent.config import Configuration, SearchConfig, LLMConfig
from search_agent.answer_orchestrator import orchestrate_answer_generation

class CachedAnswerGenerator:
    def __init__(self, cache_dir: str = "./cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_cache_key(self, question: str, config: Configuration) -> str:
        """Generate a cache key based on question and configuration."""
        config_str = json.dumps(config.to_dict(), sort_keys=True)
        combined = f"{question}:{config_str}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    async def get_answer(self, question: str, config: Configuration, use_cache: bool = True):
        """Get answer with optional caching."""
        
        if use_cache:
            cache_key = self._get_cache_key(question, config)
            cache_file = self.cache_dir / f"{cache_key}.json"
            
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    return json.load(f)
        
        # Generate new answer
        result = await orchestrate_answer_generation(
            query=config.query,
            num_links_to_parse=config.search.max_urls,
            config=config
        )
        
        # Cache the result
        if use_cache:
            cache_key = self._get_cache_key(question, config)
            cache_file = self.cache_dir / f"{cache_key}.json"
            with open(cache_file, 'w') as f:
                json.dump(result, f, indent=2)
        
        return result

# Usage
generator = CachedAnswerGenerator()

config = Configuration(
    query="What is machine learning?",
    search=SearchConfig(provider="selenium"),
    llm=LLMConfig(provider="openrouter", model="openrouter/cypher-alpha:free")
)

# First call will cache the result
result1 = asyncio.run(generator.get_answer("What is AI?", config))

# Second call will use cached result (much faster)
result2 = asyncio.run(generator.get_answer("What is AI?", config))
```

### Integration Examples

#### Flask Web Application

```python
from flask import Flask, request, jsonify
import asyncio
from search_agent.config import Configuration, SearchConfig, LLMConfig
from search_agent.answer_orchestrator import orchestrate_answer_generation

app = Flask(__name__)

@app.route('/ask', methods=['POST'])
def ask_question():
    """API endpoint for asking questions."""
    
    data = request.get_json()
    question = data.get('question', '')
    
    if not question:
        return jsonify({'error': 'Question is required'}), 400
    
    try:
        config = Configuration(
            query=question,
            search=SearchConfig(
                provider="selenium",
                max_results=10,
                max_urls=3
            ),
            llm=LLMConfig(
                provider="openrouter",
                model="openrouter/cypher-alpha:free"
            )
        )
        
        result = asyncio.run(orchestrate_answer_generation(
            query=config.query,
            num_links_to_parse=config.search.max_urls,
            config=config
        ))
        
        return jsonify({
            'answer': result['synthesized_answer']['answer'],
            'sources': result['source_urls'],
            'execution_time': result['execution_time_seconds'],
            'quality_scores': result.get('evaluation_results', {})
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

#### Django Integration

```python
# views.py
import asyncio
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from search_agent.config import Configuration, SearchConfig, LLMConfig
from search_agent.answer_orchestrator import orchestrate_answer_generation

@csrf_exempt
@require_http_methods(["POST"])
def ask_question(request):
    """Django view for handling question requests."""
    
    try:
        data = json.loads(request.body)
        question = data.get('question', '')
        
        if not question:
            return JsonResponse({'error': 'Question is required'}, status=400)
        
        config = Configuration(
            query=question,
            search=SearchConfig(
                provider="selenium",
                max_results=10,
                max_urls=3
            ),
            llm=LLMConfig(
                provider="openrouter",
                model="openrouter/cypher-alpha:free"
            )
        )
        
        result = asyncio.run(orchestrate_answer_generation(
            query=config.query,
            num_links_to_parse=config.search.max_urls,
            config=config
        ))
        
        return JsonResponse({
            'answer': result['synthesized_answer']['answer'],
            'sources': result['source_urls'],
            'execution_time': result['execution_time_seconds'],
            'quality_scores': result.get('evaluation_results', {})
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

### Best Practices

1. **Provider Selection**: Choose providers based on your needs:
   - `"selenium"` for reliable, comprehensive results
   - `"brave"` for fast API-based results
   - `"all"` for maximum coverage (slower)
   - Multiple providers like `"selenium,brave"` for balance

2. **Error Handling**: Always wrap calls in try-catch blocks and implement fallback strategies.

3. **Caching**: Implement caching for repeated queries to improve performance.

4. **Configuration Management**: Use configuration files for different environments (development, production).

5. **Async/Await**: Use proper async/await patterns when calling async functions.

6. **Resource Management**: Be mindful of API rate limits and resource usage.

7. **Monitoring**: Log execution times and success rates for monitoring.

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