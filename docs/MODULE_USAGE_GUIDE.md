# Module Usage Guide

This guide provides comprehensive information on how to use the Clinical Metabolomics Oracle Web Search Agent as an imported module in your Python applications.

## Quick Start

### Basic Usage

```python
import asyncio
from search_agent.config import Configuration, SearchConfig, LLMConfig
from search_agent.answer_orchestrator import orchestrate_answer_generation

async def get_answer(question: str):
    """Get a comprehensive answer to a question using web search."""
    
    config = Configuration(
        query=question,
        search=SearchConfig(
            provider="selenium",  # Use Selenium for reliable results
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
    
    return result

# Usage
result = asyncio.run(get_answer("What is machine learning?"))
print(f"Answer: {result['synthesized_answer']['answer']}")
print(f"Sources: {result['source_urls']}")
print(f"Execution time: {result['execution_time_seconds']:.2f}s")
```

### Synchronous Wrapper

```python
def get_answer_sync(question: str):
    """Synchronous wrapper for getting answers."""
    
    config = Configuration(
        query=question,
        search=SearchConfig(provider="selenium"),
        llm=LLMConfig(provider="openrouter", model="openrouter/cypher-alpha:free")
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

## Available Search Providers

The system supports multiple search providers, each with different characteristics:

| Provider | Type | Speed | Reliability | API Key Required |
|----------|------|-------|-------------|------------------|
| `selenium` | Browser automation | Medium | High | No |
| `playwright` | Browser automation | Fast | High | No |
| `brave` | API | Very Fast | High | Yes |
| `google_cse` | API | Fast | High | Yes |
| `httpx` | HTTP scraping | Very Fast | Medium | No |
| `scrapy` | Framework | Fast | High | No |

### Provider Selection Examples

```python
# Use only Selenium (reliable, no API key needed)
config = Configuration(
    query="What is AI?",
    search=SearchConfig(provider="selenium")
)

# Use multiple providers for comprehensive results
config = Configuration(
    query="What is AI?",
    search=SearchConfig(provider="selenium,brave")
)

# Use all available providers (slowest but most comprehensive)
config = Configuration(
    query="What is AI?",
    search=SearchConfig(provider="all")
)
```

## Configuration Options

### Search Configuration

```python
from search_agent.config import SearchConfig

search_config = SearchConfig(
    provider="selenium",        # Search provider(s) to use
    max_results=10,            # Maximum search results to collect
    max_urls=3,               # Maximum URLs to extract content from
    timeout=30,               # Timeout for operations (seconds)
    cache=True,               # Enable caching of search results
    force_refresh=False       # Force refresh of cached results
)
```

### LLM Configuration

```python
from search_agent.config import LLMConfig

llm_config = LLMConfig(
    provider="openrouter",           # LLM API provider
    model="openrouter/cypher-alpha:free",  # Model to use
    temperature=0.1,                # Creativity (0.0-2.0)
    max_tokens=1024,               # Maximum response length
    evaluation=True                 # Enable quality evaluation
)
```

### Complete Configuration

```python
from search_agent.config import Configuration, SearchConfig, LLMConfig

config = Configuration(
    query="What is machine learning?",
    search=SearchConfig(
        provider="selenium",
        max_results=10,
        max_urls=3,
        timeout=30
    ),
    llm=LLMConfig(
        provider="openrouter",
        model="openrouter/cypher-alpha:free",
        temperature=0.1,
        max_tokens=1024,
        evaluation=True
    )
)
```

## Advanced Usage Patterns

### Batch Processing

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
                search=SearchConfig(provider="selenium"),
                llm=LLMConfig(provider="openrouter", model="openrouter/cypher-alpha:free")
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

results = asyncio.run(process_questions(questions))
for result in results:
    print(f"Q: {result['question']}")
    print(f"A: {result['answer'][:100]}...")
    print(f"Time: {result['execution_time']:.2f}s")
    print("-" * 50)
```

### Error Handling and Fallbacks

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

### Caching for Performance

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

## Web Application Integration

### Flask Integration

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

### Django Integration

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

## Direct Module Usage

### Using Individual Search Modules

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

### Using the LLM Client Directly

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

## Configuration Management

### Loading from YAML File

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

### Environment-Based Configuration

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

## Performance Considerations

### Provider Performance Comparison

| Provider | Average Time | Reliability | Resource Usage |
|----------|--------------|-------------|----------------|
| `selenium` | 10-15s | High | Medium |
| `playwright` | 8-12s | High | Medium |
| `brave` | 3-5s | High | Low |
| `google_cse` | 2-4s | High | Low |
| `httpx` | 2-3s | Medium | Low |
| `all` | 20-40s | Very High | High |

### Optimization Tips

1. **Choose the right provider**: Use `selenium` for reliability, `brave` for speed
2. **Implement caching**: Cache results for repeated queries
3. **Use batch processing**: Process multiple questions together
4. **Implement fallbacks**: Use multiple providers with fallback logic
5. **Monitor performance**: Track execution times and success rates

## Error Handling

### Common Exceptions

```python
from search_agent.core.exceptions import ScrapingError, NoResultsError, ConfigurationError

try:
    result = await orchestrate_answer_generation(query, config)
except NoResultsError:
    print("No results found for this query")
except ScrapingError as e:
    print(f"Search failed: {e}")
except ConfigurationError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Best Practices

1. **Always wrap in try-catch**: Handle exceptions gracefully
2. **Implement fallbacks**: Use multiple providers
3. **Log errors**: Track and monitor error patterns
4. **Validate input**: Check query and configuration before processing
5. **Set timeouts**: Prevent hanging operations

## API Keys and Configuration

### Required API Keys

Some providers require API keys:

- **Brave API**: `BRAVE_API_KEY`
- **Google CSE**: `GOOGLE_API_KEY` and `GOOGLE_CSE_ID`
- **OpenAI**: `OPENAI_API_KEY`
- **OpenRouter**: `OPENROUTER_API_KEY`

### Setting API Keys

```python
import os

# Set API keys
os.environ["BRAVE_API_KEY"] = "your_brave_api_key"
os.environ["OPENROUTER_API_KEY"] = "your_openrouter_api_key"
```

## Best Practices Summary

1. **Provider Selection**: Choose based on your needs (speed vs. reliability)
2. **Error Handling**: Always implement proper error handling
3. **Caching**: Cache results for better performance
4. **Configuration**: Use configuration files for different environments
5. **Async/Await**: Use proper async patterns
6. **Resource Management**: Be mindful of API limits and resource usage
7. **Monitoring**: Log execution times and success rates
8. **Testing**: Test with various query types and configurations

## Examples

See the `example_usage.py` file in the project root for a complete working example of module usage. 