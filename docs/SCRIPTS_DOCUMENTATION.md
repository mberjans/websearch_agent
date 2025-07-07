# Python Scripts Documentation

This document provides comprehensive documentation for all Python scripts in the Clinical Metabolomics Oracle Web Search Agent repository.

## Table of Contents

1. [Main Scripts](#main-scripts)
   - [websearch_agent.py](#websearch_agentpy)
   - [example_usage.py](#example_usagepy)

2. [Test Scripts](#test-scripts)
   - [test_answer_generation.py](#test_answer_generationpy)
   - [test_config_compatibility.py](#test_config_compatibilitypy)
   - [test_module_import.py](#test_module_importpy)

3. [Module Scripts](#module-scripts)
   - [search_agent/cli.py](#search_agentclipy)
   - [search_agent/orchestrator.py](#search_agentorchestratorpy)
   - [search_agent/answer_orchestrator.py](#search_agentanswer_orchestratorpy)
   - [search_agent/answer_synthesizer.py](#search_agentanswer_synthesizerpy)
   - [search_agent/answer_evaluator.py](#search_agentanswer_evaluatorpy)
   - [search_agent/evaluator.py](#search_agentevaluatorpy)
   - [search_agent/output_manager.py](#search_agentoutput_managerpy)

4. [Search Module Scripts](#search-module-scripts)
   - [search_agent/modules/selenium_search.py](#search_agentmodulesselenium_searchpy)
   - [search_agent/modules/playwright_search.py](#search_agentmodulesplaywright_searchpy)
   - [search_agent/modules/brave_api_search.py](#search_agentmodulesbrave_api_searchpy)
   - [search_agent/modules/google_cse_search.py](#search_agentmodulesgoogle_cse_searchpy)
   - [search_agent/modules/httpx_search.py](#search_agentmoduleshttpx_searchpy)
   - [search_agent/modules/scrapy_search.py](#search_agentmodulesscrapy_searchpy)
   - [search_agent/modules/web_content_extractor.py](#search_agentmodulesweb_content_extractorpy)

5. [Utility Scripts](#utility-scripts)
   - [search_agent/utils/llm_client.py](#search_agentutilsllm_clientpy)
   - [search_agent/config.py](#search_agentconfigpy)
   - [search_agent/core/models.py](#search_agentcoremodelspy)
   - [search_agent/core/exceptions.py](#search_agentcoreexceptionspy)

6. [Test Scripts](#test-scripts-1)
   - [tests/test_playwright_search.py](#teststest_playwright_searchpy)
   - [tests/test_selenium_search.py](#teststest_selenium_searchpy)
   - [tests/test_web_content_extractor.py](#teststest_web_content_extractorpy)
   - [tests/test_cli_argument_parsing.py](#teststest_cli_argument_parsingpy)
   - [tests/test_config_file_loading.py](#teststest_config_file_loadingpy)
   - [tests/test_config_merging.py](#teststest_config_mergingpy)
   - [tests/test_output_manager.py](#teststest_output_managerpy)

---

## Main Scripts

### websearch_agent.py

**Purpose**: Main command-line interface for the web search agent system.

**Description**: This is the primary entry point for the web search agent. It provides a comprehensive CLI with extensive configuration options for searching the web and generating answers to queries.

**Key Features**:
- Command-line interface using Typer
- Comprehensive argument validation
- Configuration management (file, environment, CLI)
- Logging configuration
- Output management
- Error handling

**Usage**:
```bash
# Basic usage
python websearch_agent.py search "What is machine learning?"

# With custom configuration
python websearch_agent.py search "What is AI?" --search-provider selenium --max-urls 3

# With output configuration
python websearch_agent.py search "What is Python?" --output-dir ./results --project-name my_project

# With LLM configuration
python websearch_agent.py search "What is quantum computing?" --llm-provider openrouter --llm-model openrouter/cypher-alpha:free

# With configuration file
python websearch_agent.py search "What is blockchain?" --config-file config/my_config.yaml

# Verbose logging
python websearch_agent.py search "What is climate change?" --verbose

# Debug mode
python websearch_agent.py search "What is DNA?" --debug
```

**Command Options**:
- `query`: The question to search for (required)
- `--output-dir`: Directory to save results
- `--output-file`: Base name for output files
- `--output-path`: Absolute path for output file
- `--project-name`: Project name for organizing results
- `--search-provider`: Search provider(s) to use
- `--max-results`: Maximum search results
- `--max-urls`: Maximum URLs to extract
- `--timeout`: Timeout for operations (seconds)
- `--no-cache`: Disable caching of search results
- `--force-refresh`: Force refresh of cached results
- `--llm-provider`: LLM API provider to use
- `--llm-model`: LLM model to use
- `--temperature`: Temperature parameter for LLM
- `--max-tokens`: Maximum tokens for LLM response
- `--no-evaluation`: Skip answer quality evaluation
- `--config-file`: Path to custom configuration file
- `--proxy`: Proxy URL for web requests
- `--user-agent`: Custom user agent for web requests
- `--retry-count`: Number of retries for failed operations
- `--extract-images`: Extract and include images in results
- `--save-html`: Save raw HTML of extracted pages
- `--verbose`: Enable verbose logging
- `--quiet`: Suppress all output except errors
- `--debug`: Enable debug mode

**Example Configuration File**:
```yaml
query: "What is machine learning?"
search:
  provider: "selenium"
  max_results: 10
  max_urls: 3
  timeout: 30
llm:
  provider: "openrouter"
  model: "openrouter/cypher-alpha:free"
  temperature: 0.1
  max_tokens: 1024
output:
  directory: "./output"
  project_name: "ml_research"
advanced:
  debug: false
```

### example_usage.py

**Purpose**: Simple example demonstrating how to use the websearch agent as a module.

**Description**: This script shows the most common use case of asking a question and getting a comprehensive answer with sources. It's designed to be easy to understand and modify.

**Key Features**:
- Simple module import example
- Basic configuration setup
- Error handling
- Result display
- Multiple example questions

**Usage**:
```bash
python example_usage.py
```

**Example Output**:
```
🔍 WebSearch Agent - Example Usage
==================================================

📝 Question 1: What is the impact of climate change on biodiversity?
--------------------------------------------------
✅ Answer generated in 16.75 seconds
📚 Sources used: 3
📊 Quality scores:
   - Factual Consistency: 0.95
   - Relevance: 0.90
   - Completeness: 0.85
   - Conciseness: 0.80

💡 Answer:
Climate change has significant impacts on biodiversity, including...

🔗 Sources:
   - https://example.com/climate-biodiversity
   - https://example.com/ecosystem-changes
   - https://example.com/conservation-efforts
```

**Code Example**:
```python
import asyncio
from search_agent.config import Configuration, SearchConfig, LLMConfig
from search_agent.answer_orchestrator import orchestrate_answer_generation

async def get_answer(question: str, max_sources: int = 3):
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
    
    result = await orchestrate_answer_generation(
        query=config.query,
        num_links_to_parse=config.search.max_urls,
        config=config
    )
    
    return result
```

---

## Test Scripts

### test_answer_generation.py

**Purpose**: Test script for answer generation from web search using only Selenium as the source.

**Description**: This script tests the complete answer generation pipeline with mock LLM functions for testing purposes. It can be configured to use real LLM functions or mock functions.

**Key Features**:
- Mock LLM functions for testing
- Selenium-only search configuration
- Comprehensive result display
- JSON result saving
- Error handling and logging

**Usage**:
```bash
python test_answer_generation.py
```

**Mock Functions**:
- `mock_synthesize_answer()`: Generates mock answers based on query patterns
- `mock_evaluate_answer_quality()`: Returns mock evaluation scores

**Configuration**:
```python
# Enable mock functions (uncomment to use)
# search_agent.answer_synthesizer.synthesize_answer = mock_synthesize_answer
# search_agent.answer_evaluator.evaluate_answer_quality = mock_evaluate_answer_quality
```

**Output Format**:
- Query and synthesized answer
- Source URLs
- Extracted content preview
- Evaluation results
- Metadata (timing, counts, errors)
- Full JSON result saved to file

### test_config_compatibility.py

**Purpose**: Test script to verify configuration system compatibility with existing code.

**Description**: This script runs a comprehensive test suite to ensure the new configuration system works correctly with existing functionality.

**Test Cases**:
1. Configuration creation from environment variables
2. Configuration loading from custom environment variables
3. Configuration loading from YAML file
4. Configuration export to environment variables
5. Directory creation functionality
6. Orchestration integration

**Usage**:
```bash
python test_config_compatibility.py
```

**Test Functions**:
- `test_configuration_creation()`: Tests basic configuration creation
- `test_configuration_from_env_vars()`: Tests environment variable loading
- `test_configuration_file_loading()`: Tests YAML file loading
- `test_configuration_env_var_export()`: Tests environment variable export
- `test_directory_creation()`: Tests output directory creation
- `test_orchestration_with_config()`: Tests orchestration integration

**Example Output**:
```
Running Configuration System Compatibility Tests
============================================================
Testing Configuration creation from environment variables...
✓ Configuration creation from environment variables works
Testing Configuration loading from custom environment variables...
✓ Configuration loading from environment variables works
Testing Configuration loading from YAML file...
✓ Configuration loading from YAML file works
Testing Configuration export to environment variables...
✓ Configuration export to environment variables works
Testing output directory creation...
✓ Directory creation works

Testing async orchestration...
✓ orchestrate_answer_generation works with configuration

============================================================
Configuration System Compatibility Tests Summary:
✓ Configuration creation: PASSED
✓ Environment variable loading: PASSED
✓ YAML file loading: PASSED
✓ Environment variable export: PASSED
✓ Directory creation: PASSED
✓ Orchestration integration: PASSED

🎉 All core configuration tests passed!
```

### test_module_import.py

**Purpose**: Test script demonstrating how to import and use the websearch agent as a module.

**Description**: This script shows different ways to use the websearch agent as an imported module in other Python applications.

**Test Scenarios**:
1. Basic usage with the main orchestration function
2. Direct module usage without orchestrator
3. Custom configuration with specific settings
4. Batch processing multiple queries
5. Error handling and robustness
6. Save and load results

**Usage**:
```bash
python test_module_import.py
```

**Test Functions**:
- `test_basic_usage()`: Tests basic orchestration
- `test_direct_module_usage()`: Tests direct module imports
- `test_custom_configuration()`: Tests custom configuration
- `test_batch_processing()`: Tests batch processing
- `test_error_handling()`: Tests error handling
- `test_save_and_load_results()`: Tests result persistence

**Example Output**:
```
============================================================
TEST 1: Basic Usage with Main Orchestration
============================================================
✅ Success! Answer generated:
Query: What is artificial intelligence?
Answer: Artificial intelligence (AI) is a branch of computer science...
Sources: 2 URLs
Execution time: 12.45 seconds

============================================================
TEST 2: Direct Module Usage
============================================================
✅ Direct search module test:
Query: What is machine learning?
Found 10 search results
First result: Machine Learning Tutorial
First URL: https://example.com/ml-tutorial
✅ Content extraction successful:
Extracted 15420 characters
Preview: Machine learning is a subset of artificial intelligence...
```

---

## Module Scripts

### search_agent/cli.py

**Purpose**: Command-line interface module for the search agent.

**Description**: Provides CLI functionality for individual search modules and orchestrator commands.

**Commands**:
- `search`: Run orchestrated search
- `list-modules`: List available search modules
- Individual module commands (selenium, playwright, brave, etc.)

**Usage**:
```bash
# Run orchestrated search
python -m search_agent.cli search "query"

# List available modules
python -m search_agent.cli list-modules

# Run individual module
python -m search_agent.cli selenium "query"
```

### search_agent/orchestrator.py

**Purpose**: Central orchestrator for managing concurrent search module execution.

**Description**: Coordinates multiple search modules, aggregates results, and applies intelligent ranking.

**Key Functions**:
- `run_orchestration()`: Main orchestration function
- `merge_and_deduplicate()`: Merge and deduplicate results
- `rerank_results()`: Re-rank results using heuristics

**Features**:
- Concurrent module execution
- Result deduplication
- Intelligent ranking
- Error handling
- Performance monitoring

### search_agent/answer_orchestrator.py

**Purpose**: Orchestrates the complete answer generation pipeline.

**Description**: Coordinates search, content extraction, answer synthesis, and evaluation.

**Key Functions**:
- `orchestrate_answer_generation()`: Main orchestration function
- `extract_content_from_urls()`: Extract content from URLs
- `synthesize_answer()`: Generate answer from content
- `evaluate_answer_quality()`: Evaluate answer quality

**Pipeline Steps**:
1. Web search using specified providers
2. Content extraction from top results
3. Answer synthesis using LLM
4. Quality evaluation
5. Result formatting and output

### search_agent/answer_synthesizer.py

**Purpose**: Synthesizes answers from extracted content using LLM.

**Description**: Uses language models to generate comprehensive answers from web content.

**Key Functions**:
- `synthesize_answer()`: Main synthesis function
- `prepare_synthesis_prompt()`: Prepare LLM prompt
- `call_llm_api()`: Call LLM API

**Features**:
- Multiple LLM provider support
- Retry logic
- Error handling
- Prompt optimization

### search_agent/answer_evaluator.py

**Purpose**: Evaluates the quality of generated answers.

**Description**: Uses LLM and NLP techniques to assess answer quality.

**Key Functions**:
- `evaluate_answer_quality()`: Main evaluation function
- `evaluate_factual_consistency()`: Check factual accuracy
- `evaluate_relevance()`: Check relevance to query
- `evaluate_completeness()`: Check answer completeness
- `evaluate_conciseness()`: Check answer conciseness

**Evaluation Metrics**:
- Factual consistency (0-1)
- Relevance (0-1)
- Completeness (0-1)
- Conciseness (0-1)
- LLM feedback (text)

### search_agent/evaluator.py

**Purpose**: Evaluates search module performance and quality.

**Description**: Provides tools for evaluating search modules, measuring speed, and assessing result quality.

**Key Functions**:
- `measure_speed()`: Measure module execution time
- `evaluate_quality_llm()`: LLM-based quality evaluation
- `evaluate_quality_nlp()`: NLP-based quality evaluation
- `setup_database()`: Initialize evaluation database
- `log_evaluation()`: Log evaluation results

**Features**:
- Speed measurement
- Quality evaluation
- Database logging
- Performance tracking

### search_agent/output_manager.py

**Purpose**: Manages output formatting and file operations.

**Description**: Handles result formatting, file saving, and output organization.

**Key Functions**:
- `save_results()`: Save results to file
- `format_results()`: Format results for display
- `create_output_directory()`: Create output directory structure
- `generate_filename()`: Generate timestamped filenames

**Features**:
- Multiple output formats (JSON, YAML, TXT)
- Timestamped filenames
- Directory organization
- Error handling

---

## Search Module Scripts

### search_agent/modules/selenium_search.py

**Purpose**: Web search using Selenium browser automation.

**Description**: Uses Selenium WebDriver to perform web searches and extract results.

**Key Features**:
- Chrome WebDriver automation
- DuckDuckGo search target
- Robust element waiting
- Error handling
- Headless mode support

**Usage**:
```python
from search_agent.modules.selenium_search import search

# Synchronous usage
result = search("python programming")

# Async usage
result = await asyncio.to_thread(search, "python programming")
```

**Configuration**:
- Browser options
- Timeout settings
- User agent
- Proxy support

### search_agent/modules/playwright_search.py

**Purpose**: Web search using Playwright browser automation.

**Description**: Uses Playwright for modern browser automation with anti-detection measures.

**Key Features**:
- Native async support
- Anti-detection measures
- Fast execution
- Multiple browser support
- Screenshot capability

**Usage**:
```python
from search_agent.modules.playwright_search import search

# Async usage
result = await search("python programming")
```

### search_agent/modules/brave_api_search.py

**Purpose**: Web search using Brave Search API.

**Description**: Uses Brave's commercial API for high-quality search results.

**Key Features**:
- Commercial API access
- High-quality results
- Rate limiting handling
- JSON response parsing
- Error handling

**Requirements**:
- `BRAVE_API_KEY` environment variable

**Usage**:
```python
from search_agent.modules.brave_api_search import search

# Async usage
result = await search("python programming")
```

### search_agent/modules/google_cse_search.py

**Purpose**: Web search using Google Custom Search Engine API.

**Description**: Uses Google's Custom Search Engine for comprehensive search results.

**Key Features**:
- Google Custom Search Engine
- Comprehensive error handling
- Quota management
- High relevance results
- Multiple search types

**Requirements**:
- `GOOGLE_API_KEY` environment variable
- `GOOGLE_CSE_ID` environment variable

**Usage**:
```python
from search_agent.modules.google_cse_search import search

# Async usage
result = await search("python programming")
```

### search_agent/modules/httpx_search.py

**Purpose**: Lightweight HTTP-based web search.

**Description**: Uses httpx for fast HTTP requests and BeautifulSoup for HTML parsing.

**Key Features**:
- Fast HTTP requests with httpx
- BeautifulSoup HTML parsing
- CSS selector-based extraction
- Minimal resource usage
- No browser dependencies

**Usage**:
```python
from search_agent.modules.httpx_search import search

# Async usage
result = await search("python programming")
```

### search_agent/modules/scrapy_search.py

**Purpose**: Web search using Scrapy framework.

**Description**: Uses Scrapy for advanced web scraping with built-in throttling and politeness.

**Key Features**:
- Full Scrapy framework integration
- Advanced scraping capabilities
- Built-in throttling and politeness
- Complex data extraction pipelines
- Spider management

**Usage**:
```python
from search_agent.modules.scrapy_search import search

# Async usage
result = await search("python programming")
```

### search_agent/modules/web_content_extractor.py

**Purpose**: Extracts main content from web pages.

**Description**: Uses advanced techniques to extract clean, readable content from web pages.

**Key Features**:
- Main content extraction
- HTML cleaning
- Text normalization
- Image extraction (optional)
- Metadata extraction

**Usage**:
```python
from search_agent.modules.web_content_extractor import extract_main_content

# Async usage
content = await extract_main_content("https://example.com")
```

---

## Utility Scripts

### search_agent/utils/llm_client.py

**Purpose**: LLM client for making API calls to various language models.

**Description**: Provides a unified interface for calling different LLM providers (OpenAI, Anthropic, OpenRouter, etc.).

**Key Features**:
- Multiple provider support
- Retry logic
- Error handling
- Response formatting
- Token management

**Usage**:
```python
from search_agent.utils.llm_client import LLMClient
from search_agent.config import LLMConfig

llm_config = LLMConfig(
    provider="openrouter",
    model="openrouter/cypher-alpha:free"
)

llm_client = LLMClient(llm_config)
response = await llm_client.generate_response("Your prompt here")
```

### search_agent/config.py

**Purpose**: Configuration management for the web search agent system.

**Description**: Provides centralized configuration management using Pydantic BaseSettings.

**Key Classes**:
- `Settings`: Centralized application configuration
- `SearchConfig`: Search-related parameters
- `LLMConfig`: LLM-related parameters
- `OutputConfig`: Output-related parameters
- `AdvancedConfig`: Advanced options
- `Configuration`: Main configuration class

**Features**:
- Environment variable loading
- YAML file loading
- Configuration validation
- Default values
- Type safety

**Usage**:
```python
from search_agent.config import Configuration

# From environment
config = Configuration.from_env("What is AI?")

# From file
config = Configuration.from_file("config.yaml", "What is AI?")

# Direct creation
config = Configuration(
    query="What is AI?",
    search=SearchConfig(provider="selenium"),
    llm=LLMConfig(provider="openrouter")
)
```

### search_agent/core/models.py

**Purpose**: Core data models for the search agent system.

**Description**: Defines the data structures used throughout the system.

**Key Models**:
- `SearchResult`: Single search result item
- `SearchModuleOutput`: Standardized output for search modules
- `ContentExtractionResult`: Content extraction result
- `AnswerSynthesisResult`: Answer synthesis result
- `EvaluationResult`: Quality evaluation result

**Usage**:
```python
from search_agent.core.models import SearchResult, SearchModuleOutput

result = SearchResult(
    title="Example Result",
    url="https://example.com",
    snippet="This is an example search result."
)

output = SearchModuleOutput(
    source_name="selenium_search",
    query="python programming",
    results=[result]
)
```

### search_agent/core/exceptions.py

**Purpose**: Custom exception hierarchy for the search agent system.

**Description**: Defines custom exceptions for different error scenarios.

**Key Exceptions**:
- `SearchAgentError`: Base exception
- `ScrapingError`: Scraping process errors
- `NoResultsError`: No results found
- `ConfigurationError`: Configuration errors
- `LLMError`: LLM API errors

**Usage**:
```python
from search_agent.core.exceptions import ScrapingError, NoResultsError

try:
    result = await search("query")
except NoResultsError:
    print("No results found")
except ScrapingError as e:
    print(f"Search failed: {e}")
```

---

## Test Scripts

### tests/test_playwright_search.py

**Purpose**: Unit tests for the Playwright search module.

**Description**: Tests the Playwright search functionality, including browser automation and result extraction.

**Test Cases**:
- Basic search functionality
- Error handling
- Result formatting
- Browser management
- Timeout handling

### tests/test_selenium_search.py

**Purpose**: Unit tests for the Selenium search module.

**Description**: Tests the Selenium search functionality, including WebDriver management and result extraction.

**Test Cases**:
- Basic search functionality
- WebDriver initialization
- Result extraction
- Error handling
- Browser cleanup

### tests/test_web_content_extractor.py

**Purpose**: Unit tests for the web content extractor module.

**Description**: Tests content extraction functionality, including HTML parsing and text cleaning.

**Test Cases**:
- Content extraction accuracy
- HTML cleaning
- Text normalization
- Error handling
- Performance testing

### tests/test_cli_argument_parsing.py

**Purpose**: Unit tests for CLI argument parsing.

**Description**: Tests the command-line interface argument parsing and validation.

**Test Cases**:
- Argument validation
- Option parsing
- Error handling
- Help text generation
- Completion support

### tests/test_config_file_loading.py

**Purpose**: Unit tests for configuration file loading.

**Description**: Tests YAML configuration file loading and validation.

**Test Cases**:
- YAML file parsing
- Configuration validation
- Default value handling
- Error handling
- Environment variable integration

### tests/test_config_merging.py

**Purpose**: Unit tests for configuration merging functionality.

**Description**: Tests the merging of multiple configuration sources.

**Test Cases**:
- Configuration merging logic
- Priority handling
- Conflict resolution
- Validation after merging
- Error handling

### tests/test_output_manager.py

**Purpose**: Unit tests for the output manager module.

**Description**: Tests output formatting, file saving, and directory management.

**Test Cases**:
- File saving functionality
- Directory creation
- Format conversion
- Error handling
- Performance testing

---

## Running Tests

### Individual Test Scripts

```bash
# Run main test scripts
python test_answer_generation.py
python test_config_compatibility.py
python test_module_import.py

# Run unit tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_selenium_search.py

# Run with verbose output
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=search_agent
```

### Test Configuration

**Environment Variables for Testing**:
```bash
# API Keys (optional for testing)
export BRAVE_API_KEY="your_brave_api_key"
export GOOGLE_API_KEY="your_google_api_key"
export OPENAI_API_KEY="your_openai_api_key"
export OPENROUTER_API_KEY="your_openrouter_api_key"

# Test Configuration
export TEST_MODE="true"
export DEBUG="true"
```

**Mock Configuration**:
```python
# Enable mock functions for testing
search_agent.answer_synthesizer.synthesize_answer = mock_synthesize_answer
search_agent.answer_evaluator.evaluate_answer_quality = mock_evaluate_answer_quality
```

---

## Best Practices

### Script Development

1. **Error Handling**: Always implement comprehensive error handling
2. **Logging**: Use appropriate logging levels and formats
3. **Configuration**: Use the centralized configuration system
4. **Testing**: Write unit tests for all functionality
5. **Documentation**: Document all functions and classes
6. **Type Hints**: Use type hints for better code clarity

### Script Usage

1. **Environment Setup**: Set up required environment variables
2. **Configuration**: Use configuration files for complex setups
3. **Logging**: Enable appropriate logging levels
4. **Error Handling**: Handle exceptions gracefully
5. **Resource Management**: Clean up resources properly
6. **Performance**: Monitor execution times and resource usage

### Integration

1. **Module Import**: Import modules correctly
2. **Configuration**: Use the Configuration class
3. **Async/Await**: Use proper async patterns
4. **Error Handling**: Implement fallback strategies
5. **Caching**: Implement caching for performance
6. **Monitoring**: Log execution times and success rates

---

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **API Key Errors**: Check environment variable configuration
3. **Timeout Errors**: Increase timeout values or check network
4. **Memory Errors**: Reduce max_results or max_urls
5. **Browser Errors**: Check browser driver installation
6. **SSL Errors**: Configure proxy or disable SSL verification

### Debug Mode

```bash
# Enable debug logging
python websearch_agent.py search "query" --debug

# Enable verbose logging
python websearch_agent.py search "query" --verbose

# Check configuration
python test_config_compatibility.py
```

### Performance Optimization

1. **Provider Selection**: Choose appropriate search providers
2. **Caching**: Enable result caching
3. **Parallel Processing**: Use multiple providers concurrently
4. **Resource Limits**: Set appropriate limits for your environment
5. **Timeout Configuration**: Adjust timeouts based on network conditions

---

This documentation provides comprehensive information about all Python scripts in the repository. Each script is documented with its purpose, usage examples, configuration options, and best practices for development and usage. 